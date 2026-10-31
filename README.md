# pruning-slides

Command-line tool that removes intermediate slides from a PDF deck, keeping standalone and final/complete slides.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv sync
```

## Automatic mode

Removes intermediate slides. An evolution run is a sequence of pages that
repeat the same slide header; the final page is kept as the complete version.

```bash
uv run prune-slides auto deck.pdf -o deck-pruned.pdf
```

No `X/X` slide counter is required.

If same-header pages are actually separate completed slides, force them to stay:

```bash
uv run prune-slides auto deck.pdf --keep 2,3 -o deck-pruned.pdf
```

Page numbers are 1-based.

Automatic mode repairs the input with Ghostscript before parsing when
available; otherwise it uses the original file.

This is intentionally conservative: image-only slides and slides whose text
cannot be extracted are kept.

## Manual mode

Keep only the pages you choose.

```bash
uv run prune-slides manual deck.pdf --keep 1,4,7-9 -o deck-selected.pdf
```

## Folder mode

Process every PDF directly inside a folder, writing `<name>-pruned.pdf` per file
to a separate output folder. Originals are not changed.

```bash
uv run prune-slides auto decks/ -o pruned-decks/
```

The same `manual` command works with a folder, applying the page selection to
each PDF.

## Development

Run the tests with:

```bash
uv run pytest
```

## License

MIT — see [LICENSE](LICENSE).
