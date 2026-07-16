from __future__ import annotations

import pytest

from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCRResult


def test_result_average_confidence_retains_evidence() -> None:
    blocks = (
        OCRBlock("first", BoundingBox(0, 0, 20, 10), 0.8),
        OCRBlock("second", BoundingBox(22, 0, 50, 10), 0.6),
    )
    result = OCRResult("first second", blocks, "en", 0.2, "Fake", 100, 50)

    assert result.average_confidence == pytest.approx(0.7)
    assert result.blocks == blocks


def test_invalid_confidence_is_rejected() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        OCRBlock("unsafe", BoundingBox(0, 0, 1, 1), 1.2)


def test_empty_result_confidence_is_zero() -> None:
    result = OCRResult("", (), "en", 0.0, "Fake", 10, 10)

    assert result.average_confidence == 0.0
