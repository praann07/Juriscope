import re
from collections import Counter

# Below this many characters of real text, a PDF is treated as having no usable text layer.
MIN_READABLE_CHARS = 200


def _header_key(line: str) -> str:
    # Page numbers change from page to page, so "Page 5 ..." and "Page 6 ..." are the same header.
    return re.sub(r"\d+", "#", line.strip())


def readable_text(page_texts: list[str]) -> str:
    """Return the document text with repeated page headers and footers removed.

    A scanned PDF can still carry a text layer made only of repeated headers (for
    example a reporter's banner and page numbers on every page). Those lines repeat on
    most pages and are dropped. If little real text is left, return "" so the upload is
    rejected instead of indexing boilerplate.
    """
    page_keys = [
        {_header_key(line) for line in page.splitlines() if line.strip()}
        for page in page_texts
    ]
    appearances = Counter(key for keys in page_keys for key in keys)

    # A header must appear on at least two pages and on at least half of them.
    repeated = set()
    if len(page_texts) > 1:
        needed = max(2, 0.5 * len(page_texts))
        repeated = {key for key, count in appearances.items() if count >= needed}

    kept = []
    for page in page_texts:
        for line in page.splitlines():
            stripped = line.strip()
            if stripped and _header_key(stripped) not in repeated:
                kept.append(stripped)

    text = "\n".join(kept)
    return text if len(text) >= MIN_READABLE_CHARS else ""
