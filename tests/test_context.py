from src.context import FOOTER_CHARS, HEADER_CHARS, case_context_prefix


def test_prefix_has_header_and_closing_section_for_long_documents():
    text = "START " + "x" * 5000 + " FINAL ORDER: the appeal is allowed."

    prefix = case_context_prefix(text)

    assert prefix.startswith("[CASE HEADER]\nSTART")
    assert "[CASE END]\n" in prefix
    assert "the appeal is allowed." in prefix
    assert prefix.endswith("[CONTENT]\n")


def test_closing_section_is_the_last_characters_of_the_document():
    text = "a" * 3000 + "THE-END-MARKER"

    prefix = case_context_prefix(text)
    end_block = prefix.split("[CASE END]\n", 1)[1].split("\n\n[CONTENT]")[0]

    assert end_block.endswith("THE-END-MARKER")
    assert len(end_block) <= FOOTER_CHARS


def test_short_documents_get_only_the_header():
    text = "Short case text."

    prefix = case_context_prefix(text)

    assert "[CASE END]" not in prefix
    assert "Short case text." in prefix


def test_header_is_limited_to_its_length():
    text = "h" * (HEADER_CHARS + 500)

    header_block = case_context_prefix(text).split("\n\n[CASE END]")[0].split("\n\n[CONTENT]")[0]

    assert len(header_block) <= HEADER_CHARS + len("[CASE HEADER]\n")
