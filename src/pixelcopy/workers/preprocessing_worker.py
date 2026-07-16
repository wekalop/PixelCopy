"""Background preprocessing worker."""

from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal, Slot

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.preprocessing import PreprocessingOptions
from pixelcopy.preprocessing.pipeline import PreprocessingPipeline, ProcessingCancelled


class PreprocessingWorker(QObject):
    progress = Signal(int)
    succeeded = Signal(ImageDocument)
    failed = Signal(str)
    cancelled = Signal()
    finished = Signal()

    def __init__(
        self,
        pipeline: PreprocessingPipeline,
        document: ImageDocument,
        options: PreprocessingOptions,
    ) -> None:
        super().__init__()
        self._pipeline = pipeline
        self._document = document
        self._options = options
        self._cancel_event = threading.Event()

    @Slot()
    def run(self) -> None:
        try:
            result = self._pipeline.process(
                self._document,
                self._options,
                self._cancel_event.is_set,
                self.progress.emit,
            )
            if self._cancel_event.is_set():
                self.cancelled.emit()
            else:
                self.succeeded.emit(result)
        except ProcessingCancelled:
            self.cancelled.emit()
        except Exception:
            self.failed.emit("Image processing failed unexpectedly. Check the technical log.")
        finally:
            self.finished.emit()

    @Slot()
    def cancel(self) -> None:
        self._cancel_event.set()
