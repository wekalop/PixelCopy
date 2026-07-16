from __future__ import annotations

from PySide6.QtTest import QSignalSpy

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import OCROptions, OCRRequest, OCRResult
from pixelcopy.ocr.fake_engine import FakeOCREngine
from pixelcopy.services.ocr_service import OCRService
from pixelcopy.workers.ocr_worker import OCRWorker


def request() -> OCRRequest:
    image = ImageDocument("test.png", "PNG", 1, 1, "RGB", bytes(4))
    return OCRRequest(image, OCROptions())


def test_worker_emits_success_and_completion() -> None:
    result = OCRResult("hello", (), "en", 0.1, "Fake OCR", 1, 1)
    worker = OCRWorker(OCRService(FakeOCREngine(result)), request())
    succeeded = QSignalSpy(worker.succeeded)
    finished = QSignalSpy(worker.finished)

    worker.run()

    assert succeeded.count() == 1
    assert finished.count() == 1


def test_worker_honors_cancellation_before_start() -> None:
    worker = OCRWorker(OCRService(FakeOCREngine()), request())
    cancelled = QSignalSpy(worker.cancelled)

    worker.cancel()
    worker.run()

    assert cancelled.count() == 1
