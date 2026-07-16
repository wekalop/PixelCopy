"""OCR presentation workflow coordination."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import OCRMode, OCROptions, OCRRequest, OCRResult
from pixelcopy.ocr.postprocessing import apply_cleanup
from pixelcopy.services.ocr_service import OCRService
from pixelcopy.ui.pages.extract import ExtractPage
from pixelcopy.workers.ocr_worker import OCRWorker


class OCRController(QObject):
    """Own current source state and one background recognition task."""

    def __init__(
        self,
        application: QApplication,
        page: ExtractPage,
        service: OCRService,
    ) -> None:
        super().__init__(page)
        self._application = application
        self._page = page
        self._service = service
        self._document: ImageDocument | None = None
        self._thread: QThread | None = None
        self._worker: OCRWorker | None = None
        page.extract_requested.connect(self.start_recognition)
        page.cancel_requested.connect(self.cancel)
        page.copy_requested.connect(self.copy_result)
        page.cleanup_requested.connect(self.cleanup_result)

    def set_document(self, document: ImageDocument) -> None:
        """Set the validated source used by subsequent OCR requests."""
        self._document = document
        self._page.set_source_available(True)

    def clear_document(self) -> None:
        """Forget the source after a user clear action."""
        self.cancel()
        self._document = None
        self._page.set_source_available(False)

    @Slot(str, str, float)
    def start_recognition(self, language: str, mode_value: str, threshold: float) -> None:
        """Create and start one worker thread for a validated source."""
        if self._document is None or self._thread is not None:
            return
        try:
            mode = OCRMode(mode_value)
            options = OCROptions(language, mode, threshold)
        except ValueError as error:
            self._page.display_ocr_error(str(error))
            return

        thread = QThread(self)
        worker = OCRWorker(self._service, OCRRequest(self._document, options))
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._page.set_ocr_progress)
        worker.succeeded.connect(self._recognition_succeeded)
        worker.failed.connect(self._page.display_ocr_error)
        worker.cancelled.connect(self._page.display_ocr_cancelled)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._task_finished)
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        self._worker = worker
        self._page.set_ocr_busy(True)
        thread.start()

    @Slot()
    def cancel(self) -> None:
        """Request cooperative cancellation without blocking the UI thread."""
        if self._worker is not None:
            self._worker.cancel()

    @Slot(OCRResult)
    def _recognition_succeeded(self, result: OCRResult) -> None:
        self._page.display_ocr_result(result)
        if self._document is not None:
            self.result_available.emit((result, self._document))

    @Slot()
    def _task_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._page.set_ocr_busy(False)

    @Slot()
    def copy_result(self) -> None:
        """Copy the currently edited result text to the local clipboard."""
        self._application.clipboard().setText(self._page.result_editor.toPlainText())

    @Slot(str)
    def cleanup_result(self, action: str) -> None:
        """Apply an explicitly selected deterministic cleanup operation."""
        try:
            cleaned = apply_cleanup(self._page.result_editor.toPlainText(), action)
        except ValueError as error:
            self._page.display_ocr_error(str(error))
            return
        cursor = self._page.result_editor.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(cleaned)
        cursor.endEditBlock()

    result_available = Signal(object)
