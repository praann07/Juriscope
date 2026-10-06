from src.config import resolve_groq_model


def test_resolve_groq_model_falls_back_for_invalid_default():
    assert resolve_groq_model("llama-3.3-70b-versatile") == "qwen/qwen3.8-27b"
    assert resolve_groq_model("qwen/qwen3.8-27b") == "qwen/qwen3.8-27b"
