from pathlib import Path

import pytest
from pypdf import PdfWriter

from pruning_slides import cli


def test_manual_prune_keeps_the_input_file(tmp_path: Path) -> None:
    input_path = tmp_path / "deck.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with input_path.open("wb") as stream:
        writer.write(stream)

    output_path = tmp_path / "out.pdf"
    removed = cli.prune(input_path, output_path, mode="manual", keep="1")

    assert removed == 0
    assert input_path.exists()
    assert output_path.exists()


def test_auto_prune_cleans_up_the_repaired_temp_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_path = tmp_path / "deck.pdf"
    temp_path = tmp_path / "deck.repaired.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    for path in (input_path, temp_path):
        with path.open("wb") as stream:
            writer.write(stream)

    monkeypatch.setattr(cli, "_repair", lambda path: temp_path)
    removed = cli.prune(input_path, tmp_path / "out.pdf", mode="auto")

    assert removed == 0
    assert not temp_path.exists()
    assert input_path.exists()


def test_prune_folder_writes_one_pruned_pdf_per_input(tmp_path: Path) -> None:
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()
    output_dir.mkdir()
    for name in ("a", "b"):
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        with (input_dir / f"{name}.pdf").open("wb") as stream:
            writer.write(stream)

    removed = cli.prune_folder(input_dir, output_dir, mode="manual", keep="1")

    assert removed == 0
    assert (output_dir / "a-pruned.pdf").exists()
    assert (output_dir / "b-pruned.pdf").exists()
    assert (input_dir / "a.pdf").exists()
    assert (input_dir / "b.pdf").exists()
