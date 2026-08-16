from src.project_utils import clean_user_query, build_project_summary


def test_clean_user_query_trims_and_normalizes():
    raw = "   What is the liability clause?   "
    cleaned = clean_user_query(raw)

    assert cleaned == "What is the liability clause?"


def test_build_project_summary_mentions_core_capabilities():
    summary = build_project_summary()

    assert "Retrieval-Augmented Generation" in summary
    assert "legal document analysis" in summary.lower()
    assert "FastAPI" in summary
