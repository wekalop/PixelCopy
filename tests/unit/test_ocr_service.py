from __future__ import annotations

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCROptions, OCRRequest, OCRResult
from pixelcopy.ocr.fake_engine import FakeOCREngine
from pixelcopy.services.ocr_service import OCRService


def image() -> ImageDocument:
    return ImageDocument("test.png", "PNG", 2, 2, "RGB", bytes(16))


def test_service_filters_confidence_and_reconstructs_text() -> None:
    raw = OCRResult(
        "engine order ignored",
        (
            OCRBlock("low", BoundingBox(0, 30, 10, 40), 0.2),
            OCRBlock("world", BoundingBox(20, 0, 40, 10), 0.9),
            OCRBlock("hello", BoundingBox(0, 0, 15, 10), 0.8),
        ),
        "en",
        0.1,
        "Fake OCR",
        2,
        2,
    )
    engine = FakeOCREngine(raw)

    result = OCRService(engine).recognize(OCRRequest(image(), OCROptions(confidence_threshold=0.5)))

    assert result.full_text == "hello world"
    assert len(result.blocks) == 2
    assert result.warnings == ("1 low-confidence region(s) were excluded.",)
    assert len(engine.requests) == 1
