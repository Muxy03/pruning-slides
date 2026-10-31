from pathlib import Path

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
