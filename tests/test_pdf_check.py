from src.pdf_check import MIN_READABLE_CHARS, readable_text

BANNER = "SCC Online Web Edition, 2023 EBC Publishing\nPrinted For: Delhi Judicial Academy"


def test_scanned_pdf_with_only_repeated_banner_and_page_numbers_is_rejected():
    # What the scanned judgment looks like to pypdf: the same banner on every page, plus a page number.
    pages = [f"{BANNER}\nPage {n} Wednesday, November 22, 2023" for n in range(1, 11)]

    assert readable_text(pages) == ""


def test_real_text_pdf_is_accepted():
    # Each page has different wording, as a real judgment does.
    bodies = [
        "The appellant was arrested without a reasoned order of the magistrate.",
        "Bail was refused by the trial court without recording any reasons.",
        "The police did not file the charge sheet within the statutory period.",
    ]
    pages = [f"{BANNER}\n{body} " * 4 for body in bodies]

    text = readable_text(pages)

    assert len(text) >= MIN_READABLE_CHARS
    assert "appellant was arrested" in text


def test_repeated_banner_is_removed_from_the_kept_text():
    body = "Judgment paragraph one has enough words to count as real text for indexing purposes. " * 4
    pages = [f"{BANNER}\n{body}", f"{BANNER}\nAnother page of real content, different from the first one. " * 4]

    text = readable_text(pages)

    assert "Printed For" not in text
    assert "Judgment paragraph one" in text


def test_single_page_with_little_text_is_rejected():
    assert readable_text(["short"]) == ""
