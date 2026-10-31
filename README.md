# pruning-slides

Command-line tool for removing intermediate build slides from a PDF deck.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

## Install with uv

```bash
uv sync
```

## Automatic content progression

Keeps standalone slides and the final slide in each evolution run. An
evolution run is a contiguous sequence whose extracted slide/header line is
the same; the final page is treated as the complete version. A `X/X` slide
counter is not required.

```bash
uv run prune-slides auto deck.pdf -o deck-pruned.pdf
```

If two same-header pages are separate completed slides, force them to remain:

```bash
uv run prune-slides auto deck.pdf --keep 2,3 -o deck-pruned.pdf
```

This is useful when the PDF has no metadata distinguishing separate slides
from animation overlays. Page numbers are 1-based.

To process every PDF directly inside a folder, use a separate output folder:

```bash
uv run prune-slides auto decks/ -o pruned-decks/
```

Each result is named `<original-name>-pruned.pdf`; originals are not changed.

This is intentionally conservative: image-only slides and slides whose text
cannot be extracted are kept.

Automatic mode repairs the input with Ghostscript before parsing when
available, reducing malformed PDF warnings. If Ghostscript is missing, it uses
the original file.

## Manual selection

Page numbers are 1-based. Use comma-separated pages and ranges:

```bash
uv run prune-slides manual deck.pdf --keep 1,4,7-9 -o deck-selected.pdf
```

The same `manual` command works with a folder, applying the page selection to
each PDF.
