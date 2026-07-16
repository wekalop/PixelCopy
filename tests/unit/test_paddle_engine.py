from __future__ import annotations

from collections.abc import Iterable

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import OCROptions, OCRRequest
from pixelcopy.ocr.paddle_engine import PaddleOCREngine


class Result:
    @property
    def json(self) -> dict[str, object]:
        return {
            "res": {
                "rec_texts": ["world", "ignored", "hello"],
                "rec_scores": [0.91, 0.2, 0.95],
                "rec_boxes": [[30, 0, 60, 10], [0, 20, 20, 30], [0, 0, 25, 10]],
            }
        }


class Pipeline:
    def predict(self, input: object) -> Iterable[Result]:
        del input
        return [Result()]


def test_paddle_v3_result_is_normalized_without_models() -> None:
    engine = PaddleOCREngine(lambda **kwargs: Pipeline())
    image = ImageDocument("test.png", "PNG", 2, 2, "RGB", bytes(16))

    result = engine.recognize(OCRRequest(image, OCROptions(confidence_threshold=0.5)))

    assert result.full_text == "hello world"
    assert [block.text for block in result.blocks] == ["hello", "world"]
    assert result.engine_name == "PaddleOCR"
