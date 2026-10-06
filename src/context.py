HEADER_CHARS = 1200
FOOTER_CHARS = 600


def case_context_prefix(text: str) -> str:
    """Return the context block prepended to every chunk of a document.

    The start of a judgment names the parties and court, and the end names the bench,
    the date and the final order. Both are added to every chunk, so a passage from the
    middle still carries them when it is retrieved.
    """
    header = text[:HEADER_CHARS].strip()
    parts = [f"[CASE HEADER]\n{header}"]
    if len(text) > HEADER_CHARS + FOOTER_CHARS:
        footer = text[-FOOTER_CHARS:].strip()
        parts.append(f"[CASE END]\n{footer}")
    return "\n\n".join(parts) + "\n\n[CONTENT]\n"
