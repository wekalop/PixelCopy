from __future__ import annotations

from pathlib import Path

import fitz
from PySide6.QtTest import QSignalSpy

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCROptions, OCRResult
from pixelcopy.ocr.fake_engine import FakeOCREngine
from pixelcopy.services.ocr_service import OCRService
from pixelcopy.services.pdf_service import PDFError, PDFService
from pixelcopy.workers.pdf_worker import PDFWorker


class FailingPageService(PDFService):
    def render_page(self, path: Path, page_index: int, dpi: int = 300) -> ImageDocument:
        if page_index == 1:
            raise PDFError("synthetic page failure")
        return super().render_page(path, page_index, dpi)


def test_worker_reports_failed_page_and_keeps_separator(tmp_path: Path) -> None:
    path = tmp_path / "two-pages.pdf"
    document = fitz.open()
    document.new_page(width=50, height=50)
    document.new_page(width=50, height=50)
    document.save(path)
    document.close()
    raw = OCRResult(
        "ok",
        (OCRBlock("ok", BoundingBox(0, 0, 10, 10), 0.9),),
        "en",
        0.1,
        "Fake OCR",
        50,
        50,
    )
    worker = PDFWorker(
        FailingPageService(),
        OCRService(FakeOCREngine(raw)),
        path,
        (0, 1),
        72,
        OCROptions(),
    )
    completed = QSignalSpy(worker.completed)

    worker.run()

    result = completed.at(0)[0]
    assert "--- Page 1 ---" in result.combined_text
    assert "--- Page 2 ---" in result.combined_text
    assert "synthetic page failure" in result.combined_text
    assert result.failures[0].page_number == 2
