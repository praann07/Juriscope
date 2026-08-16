# Juriscope — PPT Content
### 22AIE305 · Introduction to Cloud Computing

---

## SLIDE 1 — Title

**Juriscope**
*AI-Powered Legal Document Assistant using Cloud-Native RAG Architecture*

22AIE305 · Introduction to Cloud Computing

GROUP — [Your Group Number] | AIE - [Your Section]
[Roll Number] — [Your Name]

---

## SLIDE 2 — Table of Contents

1. Problem Statement
2. Existing Systems
3. Objectives & Scope
4. Why Cloud
5. System Architecture
6. Cloud Services & Tech Stack
7. Modules Implemented
8. API Endpoints
9. One Codebase, Two Environments
10. Demo Screenshots
11. RAG Pipeline (How it works)
12. Challenges & Next Steps
13. References

---

## SLIDE 3 — Problem Statement

Legal research is slow, expensive, and inaccessible to most people.

- Lawyers and students spend **hours manually reading** lengthy court judgments to find specific rulings
- Existing tools like Westlaw and LexisNexis are **proprietary and expensive** — not accessible to students or citizens
- Court PDFs are **unstructured** — no way to ask a plain English question and get a direct answer
- No open, cloud-native tool lets you **upload any legal document and query it conversationally**
- A 48-page Supreme Court judgment like *Rajnesh vs. Neha (2020)* contains dozens of rulings — finding the maintenance amount manually takes 20+ minutes

> **The gap:** No open, cloud-native system combines legal document upload, semantic search, and conversational AI in one place.

---

## SLIDE 4 — Existing Systems Comparison

| System | Scope | AI Q&A | Upload Own Docs | Cloud-Native | Open |
|---|---|---|---|---|---|
| Westlaw | Full legal DB | No | No | No — proprietary | No |
| LexisNexis | Full legal DB | Partial | No | No — proprietary | No |
| ChatGPT | General purpose | Yes | No grounding | No | No |
| Google NotebookLM | General docs | Yes | Yes | Yes | No |
| **This project** | Legal documents | **Yes — RAG** | **Yes — PDF/TXT** | **Yes — Azure** | **Yes** |

**Gap:** No open system combines legal-domain focus, PDF upload, grounded AI answers, and cloud deployment.

---

## SLIDE 5 — Objectives & Scope

### Objectives
- Build a system where users upload legal PDFs and query them in plain English
- Use **Retrieval-Augmented Generation (RAG)** to ground every answer in the actual document
- Store uploaded PDFs in **cloud object storage (Azure Blob)**
- Deploy the full system on **Microsoft Azure** using PaaS services
- Support **session-based multi-user** querying with conversation history

### Scope
- Accepts PDF and TXT legal documents
- Answers questions grounded strictly in indexed documents — no hallucination
- Two indexed documents for demo: *Smith v. Johnson (US)* and *Rajnesh vs. Neha, Supreme Court India (2020)*
- Demonstrator with real documents — not a production legal platform

### Out of Scope
- Real-time court database integration
- OCR for scanned/image-based PDFs
- Mobile application
- Multi-language support

---

## SLIDE 6 — Why Cloud

### Why this needs a cloud architecture

**The workload demands it:**
- Embedding model (`all-mpnet-base-v2`, 768D) is CPU-heavy — running it locally on every query is slow
- Vector similarity search across thousands of chunks needs a managed, scalable index — not a local file
- LLM inference (Llama 3.3 70B) requires GPU — impossible on a laptop, trivial via Groq Cloud API
- PDF storage grows indefinitely — unsuited to app-server disk

### Cloud Models Applied
- **Delivery model:** PaaS — Azure App Service runs the container, no VM or OS management
- **Deployment model:** Public cloud — Microsoft Azure + external managed APIs
- **Storage:** Azure Blob Storage decoupled from compute — each scales independently

### Course Units Covered
- Unit 1 — Cloud delivery & deployment models (PaaS, Public Cloud)
- Unit 2 — Cloud compute & object storage (App Service, Blob Storage)
- Unit 3 — Containerisation (Docker, Azure Container Registry)

---

## SLIDE 7 — System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Microsoft Azure                       │
│                                                          │
│  ┌──────────────────┐      ┌────────────────────────┐   │
│  │ Azure Static     │      │  Azure App Service     │   │
│  │ Web Apps         │─────▶│  FastAPI (Docker)      │   │
│  │ React Frontend   │HTTPS │  Port 8000             │   │
│  └──────────────────┘      └───────┬────────────────┘   │
│                                    │                     │
│              ┌─────────────────────┼──────────────┐     │
│              ▼                     ▼              ▼     │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────┐ │
│  │ Azure Blob       │  │ Pinecone        │  │ Groq   │ │
│  │ Storage          │  │ Serverless      │  │ Cloud  │ │
│  │ (PDF files)      │  │ Vector DB       │  │ API    │ │
│  │                  │  │ (text chunks)   │  │Llama3.3│ │
│  └──────────────────┘  └─────────────────┘  └────────┘ │
└─────────────────────────────────────────────────────────┘

GitHub Actions → Azure Container Registry → App Service (CI/CD)
```

**Data flow:**
1. User uploads PDF → stored in Azure Blob Storage
2. Text extracted → chunked → embedded → stored in Pinecone
3. User asks question → multi-query retrieval from Pinecone
4. Retrieved chunks + question → Groq (Llama 3.3) → answer returned

---

## SLIDE 8 — Cloud Services & Tech Stack

| Layer | Service | Provider | Status |
|---|---|---|---|
| Frontend hosting | Azure Static Web Apps | Azure | Planned |
| Backend compute | Azure App Service (Docker) | Azure | Planned |
| PDF storage | Azure Blob Storage | Azure | Planned |
| Container registry | Azure Container Registry | Azure | Planned |
| CI/CD | GitHub Actions + ACR webhook | GitHub + Azure | Planned |
| Vector database | Pinecone Serverless (AWS us-east-1) | Pinecone | ✅ Live |
| LLM inference | Groq Cloud — Llama 3.3 70B | Groq | ✅ Live |
| Embeddings | HuggingFace all-mpnet-base-v2 (768D) | HuggingFace | ✅ Live |
| Secrets | Azure App Configuration / .env | Azure | Planned |

**Stack (built):**
Python 3.12 · FastAPI · LangChain · React 19 · Tailwind CSS · Vite · Docker

---

## SLIDE 9 — Modules Implemented

### Backend Modules

- **Document Upload** — accepts PDF/TXT, extracts text via `pypdf`, chunks with `RecursiveCharacterTextSplitter` (1500 chars, 300 overlap), embeds and stores in Pinecone
- **RAG Pipeline** — multi-query retrieval (3 query variants per question), MMR search (k=6, fetch_k=20), deduplication, context assembly
- **LLM Answering** — Llama 3.3 70B via Groq, grounded strictly in retrieved context, temperature=0.1 for factual accuracy
- **Session Management** — UUID-based sessions, 30-minute timeout, conversation history (last 10 exchanges)
- **Rate Limiting** — 20 requests/minute per IP, enforced at API layer
- **Input Validation** — query length 3–2000 chars, file size max 20MB, PDF/TXT only

### Frontend Modules

- **Chat Interface** — real-time Q&A with markdown rendering, typing indicator, auto-scroll
- **Document Upload Modal** — drag & drop PDF/TXT upload with progress feedback
- **Indexed Documents Sidebar** — live list of uploaded documents
- **Backend Health Monitor** — polls `/` every 5 seconds, shows online/offline status
- **Session Tracking** — displays active session ID, supports reset

---

## SLIDE 10 — API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | None | Health check |
| POST | `/chat` | Session | Query documents with RAG |
| POST | `/upload` | None | Upload and index PDF/TXT |
| DELETE | `/session/{id}` | None | End a session |
| POST | `/session/reset/{id}` | None | Reset conversation history |
| GET | `/sessions/count` | None | Active session count |
| GET | `/sources/{id}` | None | Get session document references |

### Chat Request/Response
```json
// POST /chat
{ "text": "Who are the parties in Rajnesh vs Neha?", "session_id": "abc123" }

// Response
{ "response": "The parties are Rajnesh (appellant/husband) and Neha...", "session_id": "abc123" }
```

---

## SLIDE 11 — One Codebase, Two Environments

| If env var is set | The app uses | Otherwise (local) |
|---|---|---|
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage for PDFs | Local temp file (deleted after indexing) |
| `PINECONE_API_KEY` | Pinecone Serverless (cloud) | ❌ Required — no local fallback |
| `GROQ_API_KEY` | Groq Cloud LLM | ❌ Required — no local fallback |
| `PORT` | Dynamic Azure port | Port 8000 |

### Why it matters
- Same code, same Docker container — cloud binding is configuration, not a rewrite
- Runs locally with `.env` file for development — doesn't burn Azure credits
- Moving to Azure is an App Service environment variable change, not a code change

---

## SLIDE 12 — RAG Pipeline — How It Works

```
User Question
      │
      ▼
┌─────────────────────────────────┐
│  Multi-Query Generation         │
│  Original + 2 variants          │
│  (factual angle + legal angle)  │
└──────────────┬──────────────────┘
               │ 3 queries
               ▼
┌─────────────────────────────────┐
│  Pinecone MMR Retrieval         │
│  k=6 per query, fetch_k=20      │
│  Deduplication of results       │
└──────────────┬──────────────────┘
               │ ~12 unique chunks
               ▼
┌─────────────────────────────────┐
│  Context Assembly               │
│  Each chunk has [CASE HEADER]   │
│  prepended (party names, case   │
│  number always present)         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Groq — Llama 3.3 70B           │
│  Strict grounding prompt        │
│  temperature=0.1                │
│  max_tokens=2048                │
└──────────────┬──────────────────┘
               │
               ▼
         Grounded Answer
```

**Key design decision:** Case header (first 1200 chars of document) is prepended to every chunk — so party names and case metadata are always in context regardless of which chunk is retrieved.

---

## SLIDE 13 — Demo Screenshots

*(Insert screenshots of your running app here)*

- Screenshot 1: Home screen with sample questions
- Screenshot 2: Uploading `2024072220.pdf` (Rajnesh vs Neha)
- Screenshot 3: Question — *"Who are the parties and what maintenance was awarded?"*
- Screenshot 4: Question — *"From what date should maintenance be paid?"*
- Screenshot 5: Sidebar showing indexed documents

---

## SLIDE 14 — Challenges & Next Steps

### Challenges Faced

- **LangChain breaking changes** — `langchain-community` Pinecone integration was sunset mid-project; migrated to `langchain-pinecone` standalone package
- **Package rename** — `pinecone-client` renamed to `pinecone`; caused import failures until resolved
- **Cross-case contamination** — retriever was mixing Smith v. Johnson chunks into Rajnesh vs. Neha answers; fixed with MMR search + case header injection
- **Scanned PDF limitation** — `pypdf` cannot extract text from image-based PDFs; documented as known limitation
- **Dependency conflicts** — `sentence-transformers` missing from system Python; resolved by explicit install

### Next Steps

- Deploy backend to **Azure App Service** via Docker + ACR
- Deploy frontend to **Azure Static Web Apps**
- Add **Azure Blob Storage** for persistent PDF storage
- Set up **GitHub Actions CI/CD** pipeline
- Add **Azure Application Insights** for monitoring and telemetry
- Add OCR support for scanned PDFs using **Azure AI Document Intelligence**

---

## SLIDE 15 — References

1. Microsoft Azure Documentation — App Service, Blob Storage, Static Web Apps, Container Registry
2. Pinecone Documentation — Serverless Index, Python SDK — pinecone.io/docs
3. Groq Documentation — Llama 3.3 70B Inference API — console.groq.com
4. LangChain Documentation — RAG, Retrieval Chains — python.langchain.com
5. HuggingFace — `sentence-transformers/all-mpnet-base-v2` model card
6. Supreme Court of India — *Rajnesh vs. Neha and Ors.* — MANU/SC/0833/2020 (04.11.2020)
7. Course guidelines — 22AIE305 Introduction to Cloud Computing

---

## SLIDE 16 — Thank You

**Juriscope**
*Making legal knowledge accessible through cloud-native AI*

[Your Name] · [Roll Number]
22AIE305 · Introduction to Cloud Computing
