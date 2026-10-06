from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, field_validator
from typing import Optional
from contextlib import asynccontextmanager
from collections import defaultdict
from pathlib import Path
import shutil, os, tempfile, threading, time

from src.auth import get_login_credentials, is_authorized
from src.context import case_context_prefix
from src.session_manager import SessionManager

vectorstore = None
session_manager = None
_rate_limit_store: dict = defaultdict(list)

MAX_FILE_SIZE_MB = 20
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 60

# Built React app (produced by `npm run build` in frontend/, or by the Dockerfile).
# When it exists, the backend serves it so the UI and API share one origin.
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


def _check_rate_limit(client_ip: str):
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    _rate_limit_store[client_ip] = [t for t in _rate_limit_store[client_ip] if t > window_start]
    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait before trying again.")
    _rate_limit_store[client_ip].append(now)


_vectorstore_lock = threading.Lock()


def _load_vectorstore():
    global vectorstore
    if vectorstore is not None:
        return vectorstore
    # The lock stops the startup warm-up and an early request from loading the model twice.
    with _vectorstore_lock:
        if vectorstore is not None:
            return vectorstore
        try:
            from src.vector_store import VectorStore, get_global_model_and_tokenizer
            get_global_model_and_tokenizer()
            vectorstore = VectorStore().load_index()
            print("[OK] Vector store loaded")
        except Exception as e:
            print(f"[ERROR] Vector store failed: {e}")
            vectorstore = None
    return vectorstore


@asynccontextmanager
async def lifespan(app: FastAPI):
    global session_manager
    from src.config import config
    config.validate()
    session_manager = SessionManager(timeout_minutes=30)
    print("[OK] Session manager ready")
    # Load the embedding model in the background so the first user does not wait for it.
    threading.Thread(target=_load_vectorstore, name="vectorstore-warmup", daemon=True).start()
    yield


app = FastAPI(title="Juriscope API", version="1.0.0", lifespan=lifespan)

# Origins allowed to call the API from a browser. Set ALLOWED_ORIGINS (comma-separated)
# when the frontend is hosted somewhere other than localhost.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def require_login(request: Request, call_next):
    # Login is only enforced when JURISCOPE_USERNAME and JURISCOPE_PASSWORD are set.
    # The health check and CORS preflight requests stay open. The web page itself
    # is protected, so the browser shows the login prompt before the app loads.
    credentials = get_login_credentials()
    is_public = (request.method == "GET" and request.url.path == "/api/health") or request.method == "OPTIONS"
    if credentials is None or is_public:
        return await call_next(request)

    if not is_authorized(request.headers.get("authorization"), *credentials):
        return JSONResponse(
            status_code=401,
            content={"detail": "Login required"},
            headers={"WWW-Authenticate": 'Basic realm="Juriscope"'},
        )
    return await call_next(request)


class Query(BaseModel):
    text: str
    session_id: Optional[str] = None

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Query text cannot be empty")
        if len(v.strip()) < 3:
            raise ValueError("Query too short — please ask a complete question")
        if len(v) > 2000:
            raise ValueError("Query too long — maximum 2000 characters")
        return v.strip()


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: list[dict] = []


def get_vectorstore():
    vs = _load_vectorstore()
    if vs is None:
        raise HTTPException(status_code=503, detail="Vector store unavailable. Check Pinecone and embedding model configuration.")
    return vs


def get_session_manager():
    if session_manager is None:
        raise HTTPException(status_code=503, detail="Session manager unavailable.")
    return session_manager


def create_chatbot():
    from src.chatbot import LegalDocumentAssistant
    return LegalDocumentAssistant(get_vectorstore())


@app.get("/api/health")
async def health():
    from src.config import config
    return {"status": "ok", "message": "Juriscope API is running", "version": "1.0.0", "model": config.GROQ_MODEL}


@app.post("/chat", response_model=ChatResponse)
async def chat(query: Query, request: Request, sm: SessionManager = Depends(get_session_manager)):
    _check_rate_limit(request.client.host)
    try:
        session_id, bot = sm.get_or_create_session(create_chatbot, query.session_id)
        response, sources = bot.chat(query.text)
        return ChatResponse(response=response, session_id=session_id, sources=sources)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/upload")
async def upload_document(request: Request, file: UploadFile = File(...)):
    _check_rate_limit(request.client.host)

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".txt"]:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")

    # Read file content and check size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large ({size_mb:.1f}MB). Maximum allowed size is {MAX_FILE_SIZE_MB}MB.")

    vs = get_vectorstore()

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if ext == ".pdf":
            from pypdf import PdfReader
            from src.pdf_check import readable_text
            pages = PdfReader(tmp_path).pages
            text = readable_text([p.extract_text() or "" for p in pages])
            if not text:
                raise HTTPException(status_code=400, detail="This PDF has no readable text. It looks scanned or image-based, and scanned PDFs are not supported. Please upload a text-based PDF or a .txt file.")
        else:
            with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
    finally:
        os.unlink(tmp_path)

    if not text.strip():
        raise HTTPException(status_code=400, detail="File appears to be empty or unreadable.")

    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document

    # Prepend the case header and closing section to every chunk, so party names,
    # the bench, the date and the final order are present whichever chunk is retrieved
    header_prefix = case_context_prefix(text)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
    chunks = splitter.split_text(text)

    if not chunks:
        raise HTTPException(status_code=400, detail="Could not split document into chunks.")

    docs = [
        Document(
            page_content=header_prefix + chunk,
            metadata={"source": file.filename, "chunk": i, "total_chunks": len(chunks)}
        )
        for i, chunk in enumerate(chunks)
    ]

    try:
        vs.add_documents(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")

    return {
        "message": f"Successfully indexed '{file.filename}'",
        "chunks": len(docs),
        "size_mb": round(size_mb, 2),
        "pages": len(pages) if ext == ".pdf" else None
    }


@app.delete("/session/{session_id}")
async def end_session(session_id: str, sm: SessionManager = Depends(get_session_manager)):
    if sm.end_session(session_id):
        return {"message": f"Session {session_id} ended"}
    raise HTTPException(status_code=404, detail="Session not found")


@app.post("/session/reset/{session_id}")
async def reset_session(session_id: str, sm: SessionManager = Depends(get_session_manager)):
    session = sm.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    msg = session["chatbot"].reset_conversation()
    return {"message": msg, "session_id": session_id}


@app.get("/sessions/count")
async def session_count(sm: SessionManager = Depends(get_session_manager)):
    return {"active_sessions": sm.get_active_session_count()}


@app.get("/sources/{session_id}")
async def get_sources(session_id: str, sm: SessionManager = Depends(get_session_manager)):
    session = sm.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    chatbot = session["chatbot"]
    history = getattr(chatbot, "sources_history", [])
    unique = {s["source"]: s for s in history}
    return {"session_id": session_id, "document_references": list(unique.values())}


def _frontend_response(full_path: str):
    """Serve a file from the built frontend, or index.html for client-side routes."""
    if not FRONTEND_DIST.is_dir():
        raise HTTPException(status_code=404, detail="Frontend is not built.")

    root = FRONTEND_DIST.resolve()
    candidate = (root / full_path).resolve()
    if full_path and candidate.is_file() and candidate.is_relative_to(root):
        return FileResponse(candidate)

    index = root / "index.html"
    if index.is_file():
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="Frontend is not built.")


# Registered last so every API route above takes priority over these catch-alls.
@app.get("/", include_in_schema=False)
async def frontend_root():
    return _frontend_response("")


@app.get("/{full_path:path}", include_in_schema=False)
async def frontend_files(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    return _frontend_response(full_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
