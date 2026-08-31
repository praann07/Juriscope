from src.project_utils import clean_user_query, build_project_summary
from src.config import resolve_groq_model


def test_clean_user_query_trims_and_normalizes():
    raw = "   What is the liability clause?   "
    cleaned = clean_user_query(raw)

    assert cleaned == "What is the liability clause?"


def test_build_project_summary_mentions_core_capabilities():
    summary = build_project_summary()

    assert "Retrieval-Augmented Generation" in summary
    assert "legal document analysis" in summary.lower()
    assert "FastAPI" in summary


def test_resolve_groq_model_falls_back_for_invalid_default():
    assert resolve_groq_model("llama-3.3-70b-versatile") == "qwen/qwen3.8-27b"
    assert resolve_groq_model("qwen/qwen3.8-27b") == "qwen/qwen3.8-27b"
