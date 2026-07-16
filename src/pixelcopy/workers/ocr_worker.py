"""Background OCR execution with cooperative cancellation."""

from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal, Slot

from pixelcopy.domain.exceptions import PixelCopyError
from pixelcopy.domain.ocr import OCRRequest, OCRResult
from pixelcopy.services.ocr_service import OCRService


class OCRWorker(QObject):
    """Run one OCR request outside the GUI thread."""

    progress = Signal(int)
    succeeded = Signal(OCRResult)
    failed = Signal(str)
    cancelled = Signal()
    finished = Signal()

    def __init__(self, service: OCRService, request: OCRRequest) -> None:
        super().__init__()
        self._service = service
        self._request = request
        self._cancel_event = threading.Event()

    @Slot()
    def run(self) -> None:
        """Execute recognition and always signal terminal completion."""
        try:
            if self._cancel_event.is_set():
                self.cancelled.emit()
                return
            self.progress.emit(5)
            result = self._service.recognize(self._request)
            if self._cancel_event.is_set():
                self.cancelled.emit()
                return
            self.progress.emit(100)
            self.succeeded.emit(result)
        except PixelCopyError as error:
            self.failed.emit(str(error))
        except Exception:
            self.failed.emit("Text recognition failed unexpectedly. Check the technical log.")
        finally:
            self.finished.emit()

    @Slot()
    def cancel(self) -> None:
        """Request cancellation at the next safe boundary."""
        self._cancel_event.set()
