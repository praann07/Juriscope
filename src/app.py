from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional
from contextlib import asynccontextmanager
from collections import defaultdict
import shutil, os, tempfile, time

from src.session_manager import SessionManager

vectorstore = None
session_manager = None
_rate_limit_store: dict = defaultdict(list)

MAX_FILE_SIZE_MB = 20
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 60


def _check_rate_limit(client_ip: str):
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    _rate_limit_store[client_ip] = [t for t in _rate_limit_store[client_ip] if t > window_start]
    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait before trying again.")
    _rate_limit_store[client_ip].append(now)


def _load_vectorstore():
    global vectorstore
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
    yield


app = FastAPI(title="Juriscope API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/")
async def root():
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
            pages = PdfReader(tmp_path).pages
            text = "\n".join(p.extract_text() or "" for p in pages)
            if not text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from PDF. The file may be image-based or scanned without OCR.")
        else:
            with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
    finally:
        os.unlink(tmp_path)

    if not text.strip():
        raise HTTPException(status_code=400, detail="File appears to be empty or unreadable.")

    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document

    # Prepend case header to every chunk so party names and key facts
    # are always present regardless of which chunk is retrieved
    case_header = text[:1200].strip()
    header_prefix = f"[CASE HEADER]\n{case_header}\n\n[CONTENT]\n"

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
