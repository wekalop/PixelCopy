from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from pixelcopy.services.pdf_service import PDFError, PDFService, parse_page_range


def create_pdf(path: Path, pages: int = 3) -> None:
    document = fitz.open()
    for page_number in range(1, pages + 1):
        page = document.new_page(width=200, height=100)
        page.insert_text((20, 50), f"Page {page_number}")
    document.set_metadata({"title": "Synthetic document"})
    document.save(path)
    document.close()


def test_page_range_supports_single_ranges_deduplication_and_all() -> None:
    assert parse_page_range("1-3,2,5", 5) == (0, 1, 2, 4)
    assert parse_page_range("all", 3) == (0, 1, 2)


@pytest.mark.parametrize("value", ["0", "3-2", "1-6", "words"])
def test_page_range_reports_invalid_input(value: str) -> None:
    with pytest.raises(PDFError, match="Enter pages"):
        parse_page_range(value, 5)


def test_inspection_rendering_and_thumbnail_are_incremental(tmp_path: Path) -> None:
    path = tmp_path / "scan.pdf"
    create_pdf(path)
    service = PDFService()

    info = service.inspect(path)
    page = service.render_page(path, 1, dpi=72)
    thumbnail = service.render_thumbnail(path, 0, width=80)

    assert info.page_count == 3
    assert info.title == "Synthetic document"
    assert (page.width, page.height) == (200, 100)
    assert thumbnail.width == 80
    assert thumbnail.height < page.height
