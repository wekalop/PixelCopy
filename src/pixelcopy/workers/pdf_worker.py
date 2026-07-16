"""Background thumbnail rendering and scanned PDF OCR."""

from __future__ import annotations

import threading
from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from pixelcopy.domain.ocr import OCROptions, OCRRequest, OCRResult
from pixelcopy.domain.pdf import PDFBatchResult, PDFPageFailure
from pixelcopy.services.ocr_service import OCRService
from pixelcopy.services.pdf_service import PDFService


class PDFThumbnailWorker(QObject):
    thumbnail_ready = Signal(int, object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, service: PDFService, path: Path, page_count: int) -> None:
        super().__init__()
        self._service = service
        self._path = path
        self._page_count = page_count
        self._cancel = threading.Event()

    @Slot()
    def run(self) -> None:
        try:
            for page_index in range(self._page_count):
                if self._cancel.is_set():
                    return
                self.thumbnail_ready.emit(
                    page_index,
                    self._service.render_thumbnail(self._path, page_index),
                )
        except Exception as error:
            self.failed.emit(f"Could not render PDF thumbnails: {error}")
        finally:
            self.finished.emit()

    @Slot()
    def cancel(self) -> None:
        self._cancel.set()


class PDFWorker(QObject):
    progress = Signal(int, int)
    page_failed = Signal(object)
    completed = Signal(object)
    cancelled = Signal()
    finished = Signal()

    def __init__(
        self,
        pdf_service: PDFService,
        ocr_service: OCRService,
        path: Path,
        pages: tuple[int, ...],
        dpi: int,
        options: OCROptions,
    ) -> None:
        super().__init__()
        self._pdf_service = pdf_service
        self._ocr_service = ocr_service
        self._path = path
        self._pages = pages
        self._dpi = dpi
        self._options = options
        self._cancel = threading.Event()

    @Slot()
    def run(self) -> None:
        results: list[OCRResult] = []
        failures: list[PDFPageFailure] = []
        try:
            for position, page_index in enumerate(self._pages, start=1):
                if self._cancel.is_set():
                    self.cancelled.emit()
                    return
                self.progress.emit(position - 1, len(self._pages))
                try:
                    image = self._pdf_service.render_page(self._path, page_index, self._dpi)
                    raw = self._ocr_service.recognize(OCRRequest(image, self._options))
                    page_number = page_index + 1
                    blocks = tuple(replace(block, page_number=page_number) for block in raw.blocks)
                    results.append(replace(raw, blocks=blocks, page_number=page_number))
                except Exception as error:
                    failure = PDFPageFailure(page_index + 1, str(error))
                    failures.append(failure)
                    self.page_failed.emit(failure)
                self.progress.emit(position, len(self._pages))
            combined = self._combined_text(results, failures)
            self.completed.emit(PDFBatchResult(tuple(results), tuple(failures), combined))
        finally:
            self.finished.emit()

    @Slot()
    def cancel(self) -> None:
        self._cancel.set()

    @staticmethod
    def _combined_text(results: list[OCRResult], failures: list[PDFPageFailure]) -> str:
        content: dict[int, str] = {result.page_number or 0: result.full_text for result in results}
        content.update(
            {failure.page_number: f"[Page failed: {failure.message}]" for failure in failures}
        )
        return "\n\n".join(f"--- Page {page} ---\n{text}" for page, text in sorted(content.items()))
