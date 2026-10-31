"""Command-line interface for pruning PDF slide decks."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .core import intermediate_pages, parse_pages


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Remove intermediate slides from a PDF.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    auto = subparsers.add_parser("auto", help="remove text-progression slides")
    _add_files(auto)
    auto.add_argument("--keep", help="pages to always keep, e.g. 2,3,10-12")

    manual = subparsers.add_parser("manual", help="keep only explicitly selected pages")
    _add_files(manual)
    manual.add_argument("--keep", required=True, help="pages to keep, e.g. 1,3,5-7")
    return parser


def _add_files(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input", type=Path, help="input PDF or folder of PDFs")
    parser.add_argument("-o", "--output", type=Path, required=True, help="output PDF or folder")


def _repair(input_path: Path) -> Path:
    """Return a Ghostscript-repaired copy, or the original when unavailable."""
    temporary = input_path.with_name(f"{input_path.stem}.repaired.pdf")
    try:
        subprocess.run(
            [
                "gs",
                "-q",
                "-sDEVICE=pdfwrite",
                "-dNOPAUSE",
                "-dBATCH",
                "-sOutputFile=" + str(temporary),
                str(input_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        temporary.unlink(missing_ok=True)
        return input_path
    return temporary


def prune(input_path: Path, output_path: Path, mode: str, keep: str | None = None) -> int:
    source = _repair(input_path) if mode == "auto" else input_path
    reader = PdfReader(str(source))
    if not reader.pages:
        raise ValueError("input PDF has no pages")

    if mode == "manual":
        indexes = parse_pages(keep or "", len(reader.pages))
    else:
        texts = [page.extract_text() or "" for page in reader.pages]
        removed = intermediate_pages(texts)
        if keep:
            removed -= set(parse_pages(keep, len(reader.pages)))
        indexes = [index for index in range(len(reader.pages)) if index not in removed]

    if not indexes:
        raise ValueError("selection would produce an empty PDF")
    writer = PdfWriter()
    for index in indexes:
        writer.add_page(reader.pages[index])
    if reader.metadata:
        writer.add_metadata(dict(reader.metadata))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as stream:
        writer.write(stream)
    source.unlink(missing_ok=True)
    return len(reader.pages) - len(indexes)


def prune_folder(input_dir: Path, output_dir: Path, mode: str, keep: str | None = None) -> int:
    """Prune direct PDF files in a folder without changing the originals."""
    files = sorted(
        path for path in input_dir.glob("*.pdf") if not path.stem.endswith("-pruned")
    )
    if not files:
        raise ValueError(f"no PDF files found in {input_dir}")
    removed = 0
    for input_path in files:
        output_path = output_dir / f"{input_path.stem}-pruned.pdf"
        removed += prune(input_path, output_path, mode, keep)
        print(f"Wrote {output_path}.")
    return removed


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        keep = getattr(args, "keep", None)
        if args.input.is_dir():
            if args.output.exists() and not args.output.is_dir():
                raise ValueError("folder input requires a folder output")
            removed = prune_folder(args.input, args.output, args.mode, keep)
        else:
            removed = prune(args.input, args.output, args.mode, keep)
    except (OSError, ValueError) as error:
        print(f"prune-slides: {error}", file=sys.stderr)
        return 2
    if args.input.is_dir():
        print(f"Processed PDFs in {args.input} ({removed} slide(s) removed).")
    else:
        print(f"Wrote {args.output} ({removed} slide(s) removed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
