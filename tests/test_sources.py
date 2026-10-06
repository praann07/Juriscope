from langchain_core.documents import Document

from src.chatbot import MAX_SOURCES, extract_sources


def _doc(source, chunk, body, header="[CASE HEADER]\nCase Title: X\n\n[CONTENT]\n"):
    return Document(
        page_content=header + body,
        metadata={"source": source, "chunk": chunk, "total_chunks": 5},
    )


def test_excerpt_is_the_passage_without_the_case_header():
    sources = extract_sources([_doc("a.pdf", 0, "The court ruled for the plaintiff.")])

    assert sources[0]["excerpt"] == "The court ruled for the plaintiff."
    assert "CASE HEADER" not in sources[0]["excerpt"]


def test_one_citation_per_passage_not_per_file():
    docs = [
        _doc("a.pdf", 0, "first passage"),
        _doc("a.pdf", 1, "second passage"),
        _doc("a.pdf", 1, "second passage"),  # same passage retrieved twice
    ]

    sources = extract_sources(docs)

    assert [(s["source"], s["chunk"]) for s in sources] == [("a.pdf", 0), ("a.pdf", 1)]


def test_same_chunk_number_in_different_files_is_kept_twice():
    docs = [_doc("a.pdf", 0, "from a"), _doc("b.pdf", 0, "from b")]

    sources = extract_sources(docs)

    assert [s["source"] for s in sources] == ["a.pdf", "b.pdf"]


def test_citation_keeps_chunk_metadata_for_the_ui():
    sources = extract_sources([_doc("a.pdf", 2, "text")])

    assert sources[0]["chunk"] == 2
    assert sources[0]["total_chunks"] == 5


def test_passage_without_content_marker_is_used_as_is():
    doc = Document(page_content="plain stored text", metadata={"source": "old.pdf", "chunk": 0})

    sources = extract_sources([doc])

    assert sources[0]["excerpt"] == "plain stored text"


def test_number_of_citations_is_capped():
    docs = [_doc("a.pdf", i, f"passage {i}") for i in range(MAX_SOURCES + 5)]

    assert len(extract_sources(docs)) == MAX_SOURCES
