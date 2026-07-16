"""Preprocessing preview workflow coordination."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal, Slot

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.preprocessing import PreprocessingOptions
from pixelcopy.preprocessing.pipeline import PreprocessingPipeline
from pixelcopy.ui.pages.extract import ExtractPage
from pixelcopy.workers.preprocessing_worker import PreprocessingWorker


class PreprocessingController(QObject):
    document_processed = Signal(object)
    original_restored = Signal(object)

    def __init__(self, page: ExtractPage, pipeline: PreprocessingPipeline) -> None:
        super().__init__(page)
        self._page = page
        self._pipeline = pipeline
        self._original: ImageDocument | None = None
        self._thread: QThread | None = None
        self._worker: PreprocessingWorker | None = None
        page.preprocessing_panel.process_requested.connect(self.process)
        page.preprocessing_panel.cancel_requested.connect(self.cancel)
        page.preprocessing_panel.reset_requested.connect(self.reset)

    def set_document(self, document: ImageDocument) -> None:
        self.cancel()
        self._original = document
        self._page.clear_processed_document()
        self._page.preprocessing_panel.set_source_available(True)

    def clear_document(self) -> None:
        self.cancel()
        self._original = None
        self._page.clear_processed_document()
        self._page.preprocessing_panel.set_source_available(False)

    @Slot(object)
    def process(self, value: object) -> None:
        if self._original is None or self._thread is not None:
            return
        if not isinstance(value, PreprocessingOptions):
            return
        thread = QThread(self)
        worker = PreprocessingWorker(self._pipeline, self._original, value)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._page.preprocessing_panel.set_progress)
        worker.succeeded.connect(self._succeeded)
        worker.failed.connect(self._page.display_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._finished)
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        self._worker = worker
        self._page.preprocessing_panel.set_busy(True)
        thread.start()

    @Slot()
    def cancel(self) -> None:
        if self._worker is not None:
            self._worker.cancel()

    @Slot()
    def reset(self) -> None:
        self.cancel()
        self._page.clear_processed_document()
        if self._original is not None:
            self.original_restored.emit(self._original)

    @Slot(ImageDocument)
    def _succeeded(self, document: ImageDocument) -> None:
        self._page.display_processed_document(document)
        self.document_processed.emit(document)

    @Slot()
    def _finished(self) -> None:
        self._thread = None
        self._worker = None
        self._page.preprocessing_panel.set_busy(False)
