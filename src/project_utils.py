"""Utility helpers for project presentation and input cleanup."""

from __future__ import annotations


def clean_user_query(query: str) -> str:
    """Normalize user input for chat and demo usage."""
    if query is None:
        return ""
    return " ".join(str(query).strip().split())


def build_project_summary() -> str:
    """Return a project overview suitable for course reviews and demos."""
    return (
        "Juriscope is a Retrieval-Augmented Generation project for legal document analysis. "
        "It combines FastAPI, vector search, and a language model to retrieve relevant legal "
        "context and answer user queries with grounded, document-based reasoning."
    )


def get_project_highlights() -> list[str]:
    """Return a short list of showcase-ready project strengths."""
    return [
        "Retrieval-Augmented Generation for legal document analysis",
        "FastAPI backend with session-based conversational flow",
        "Vector database search using Pinecone for document retrieval",
        "Llama via Groq for legal Q&A generation",
        "Streamlit demo interface for easy showcase and testing",
    ]
