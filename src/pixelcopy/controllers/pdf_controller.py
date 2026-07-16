"""Scanned PDF UI and worker coordination."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Slot

from pixelcopy.domain.ocr import OCROptions
from pixelcopy.domain.pdf import PDFBatchResult, PDFDocumentInfo
from pixelcopy.services.ocr_service import OCRService
from pixelcopy.services.pdf_service import PDFError, PDFService, parse_page_range
from pixelcopy.ui.pages.pdf import PDFPage
from pixelcopy.workers.pdf_worker import PDFThumbnailWorker, PDFWorker


class PDFController(QObject):
    def __init__(self, page: PDFPage, pdf_service: PDFService, ocr_service: OCRService) -> None:
        super().__init__(page)
        self._page = page
        self._pdf_service = pdf_service
        self._ocr_service = ocr_service
        self._info: PDFDocumentInfo | None = None
        self._thread: QThread | None = None
        self._worker: PDFWorker | None = None
        self._thumbnail_thread: QThread | None = None
        self._thumbnail_worker: PDFThumbnailWorker | None = None
        self._failed_pages: tuple[int, ...] = ()
        page.file_selected.connect(self.open_pdf)
        page.extract_requested.connect(self.extract)
        page.cancel_requested.connect(self.cancel)
        page.retry_requested.connect(self.retry_failed)

    def open_pdf(self, path: Path) -> None:
        try:
            info = self._pdf_service.inspect(path)
        except PDFError as error:
            self._page.display_error(str(error))
            return
        self._info = info
        self._page.display_info(info)
        self._start_thumbnails(info)

    @Slot(str, int, str)
    def extract(self, range_value: str, dpi: int, language: str) -> None:
        if self._info is None or self._thread is not None:
            return
        try:
            pages = parse_page_range(range_value, self._info.page_count)
        except PDFError as error:
            self._page.display_error(str(error))
            return
        self._start_worker(pages, dpi, language)

    def _start_worker(self, pages: tuple[int, ...], dpi: int, language: str) -> None:
        if self._info is None:
            return
        thread = QThread(self)
        worker = PDFWorker(
            self._pdf_service,
            self._ocr_service,
            self._info.path,
            pages,
            dpi,
            OCROptions(language=language),
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._page.set_progress)
        worker.page_failed.connect(self._page.add_failure)
        worker.completed.connect(self._completed)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._finished)
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        self._worker = worker
        self._page.failures.clear()
        self._page.failures.setVisible(False)
        self._page.set_busy(True)
        thread.start()

    def _start_thumbnails(self, info: PDFDocumentInfo) -> None:
        if self._thumbnail_worker is not None:
            self._thumbnail_worker.cancel()
        thread = QThread(self)
        worker = PDFThumbnailWorker(self._pdf_service, info.path, info.page_count)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.thumbnail_ready.connect(self._page.display_thumbnail)
        worker.failed.connect(self._page.display_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda: self._clear_thumbnails(thread))
        thread.finished.connect(thread.deleteLater)
        self._thumbnail_thread = thread
        self._thumbnail_worker = worker
        thread.start()

    @Slot()
    def cancel(self) -> None:
        if self._worker is not None:
            self._worker.cancel()

    @Slot()
    def retry_failed(self) -> None:
        if self._failed_pages:
            self._start_worker(self._failed_pages, self._page.dpi.value(), "en")

    @Slot(object)
    def _completed(self, value: object) -> None:
        if isinstance(value, PDFBatchResult):
            self._failed_pages = tuple(failure.page_number - 1 for failure in value.failures)
            self._page.display_result(value)

    @Slot()
    def _finished(self) -> None:
        self._thread = None
        self._worker = None
        self._page.set_busy(False)

    def _clear_thumbnails(self, thread: QThread) -> None:
        if self._thumbnail_thread is thread:
            self._thumbnail_thread = None
            self._thumbnail_worker = None
