from __future__ import annotations

import json
from pathlib import Path

import fitz
import pytest

from pixelcopy.domain.export import ExportFormat, ExportPayload
from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCRResult
from pixelcopy.export.base import ExportError
from pixelcopy.services.export_service import ExportService


def payload() -> ExportPayload:
    result = OCRResult(
        "original",
        (OCRBlock("edited", BoundingBox(0, 0, 40, 15), 0.9),),
        "en",
        0.1,
        "Fake",
        50,
        30,
    )
    image = ImageDocument("source.png", "PNG", 50, 30, "RGBA", bytes([255]) * 6000)
    return ExportPayload("edited text", result, (image,))


@pytest.mark.parametrize("export_format", [ExportFormat.TEXT, ExportFormat.MARKDOWN])
def test_text_formats_use_currently_edited_text(
    tmp_path: Path, export_format: ExportFormat
) -> None:
    destination = tmp_path / f"result.{export_format.value}"
    ExportService().export(payload(), destination, export_format)
    assert destination.read_text(encoding="utf-8") == "edited text"


def test_json_and_csv_include_structured_evidence(tmp_path: Path) -> None:
    json_path = tmp_path / "result.json"
    csv_path = tmp_path / "result.csv"
    service = ExportService()
    service.export(payload(), json_path, ExportFormat.JSON)
    service.export(payload(), csv_path, ExportFormat.CSV)
    assert json.loads(json_path.read_text(encoding="utf-8"))["ocr"]["blocks"][0]["text"] == "edited"
    assert "confidence" in csv_path.read_text(encoding="utf-8-sig")


def test_searchable_pdf_contains_image_and_selectable_text(tmp_path: Path) -> None:
    destination = tmp_path / "result.pdf"
    ExportService().export(payload(), destination, ExportFormat.SEARCHABLE_PDF)
    with fitz.open(destination) as document:
        assert document.page_count == 1
        assert "edited" in document[0].get_text()


def test_existing_destination_is_never_overwritten(tmp_path: Path) -> None:
    destination = tmp_path / "existing.txt"
    destination.write_text("keep", encoding="utf-8")
    with pytest.raises(ExportError, match="already exists"):
        ExportService().export(payload(), destination, ExportFormat.TEXT)
    assert destination.read_text(encoding="utf-8") == "keep"
