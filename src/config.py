import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"
SUPPORTED_GROQ_MODELS = {
    "qwen/qwen3.8-27b",
    "groq/compound",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
}


def resolve_groq_model(requested_model: str | None = None) -> str:
    candidate = (requested_model or os.getenv("GROQ_MODEL") or DEFAULT_GROQ_MODEL).strip()
    if candidate in SUPPORTED_GROQ_MODELS:
        return candidate
    if candidate == "llama-3.3-70b-versatile":
        return DEFAULT_GROQ_MODEL
    if candidate == "llama-3.1-8b-instant":
        return DEFAULT_GROQ_MODEL
    return DEFAULT_GROQ_MODEL


@dataclass
class Config:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = resolve_groq_model(os.getenv("GROQ_MODEL"))
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
    PINECONE_REGION: str = os.getenv("PINECONE_REGION", "us-east-1")
    CHUNK_SIZE: int = 350
    CHUNK_OVERLAP: int = 50
    INDEX_NAME: str = "legal-rag"

    def validate(self):
        if not all([self.GROQ_API_KEY, self.PINECONE_API_KEY]):
            raise ValueError("Missing required environment variables. Please check your .env file.")

config = Config()