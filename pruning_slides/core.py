"""The text-based pruning rules for PDF slide decks."""

def slide_key(text: str) -> str:
    """Use the first extracted line as the slide/evolution identity."""
    for line in text.splitlines():
        line = " ".join(line.split())
        if line:
            return line.casefold()
    return ""


def intermediate_pages(texts: list[str]) -> set[int]:
    """Return all but the final page in each contiguous evolution run.

    Generated presentation PDFs commonly repeat the slide title while adding
    content over several pages. The repeated first extracted line identifies
    that run; the final page is the complete version. Pages without text are
    left alone because they cannot be classified safely.
    """
    result: set[int] = set()
    index = 0
    while index < len(texts):
        key = slide_key(texts[index])
        end = index + 1
        while key and end < len(texts) and slide_key(texts[end]) == key:
            end += 1
        if key and end - index > 1:
            result.update(range(index, end - 1))
        index = end
    return result


def parse_pages(value: str, page_count: int) -> list[int]:
    """Parse 1-based page numbers and ranges into sorted zero-based indexes."""
    selected: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            raise ValueError("empty page selection")
        bounds = part.split("-")
        if len(bounds) > 2 or not all(item.strip().isdigit() for item in bounds):
            raise ValueError(f"invalid page selection: {part!r}")
        start = int(bounds[0])
        end = int(bounds[-1])
        if start < 1 or end < start or end > page_count:
            raise ValueError(f"page selection outside 1-{page_count}: {part!r}")
        selected.update(page - 1 for page in range(start, end + 1))
    return sorted(selected)
