"""Lazy local PaddleOCR 3.x adapter."""

from __future__ import annotations

import importlib
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Protocol, cast

from PIL import Image

from pixelcopy.domain.exceptions import PixelCopyError
from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCRRequest, OCRResult
from pixelcopy.ocr.reading_order import sort_reading_order, text_from_blocks


class OCRSetupError(PixelCopyError):
    """Local PaddleOCR dependencies or models are unavailable."""


class _PaddleResult(Protocol):
    @property
    def json(self) -> Mapping[str, object]: ...


class _PaddlePipeline(Protocol):
    def predict(self, input: object) -> Iterable[_PaddleResult]: ...


class PaddleOCREngine:
    """Run the official local PaddleOCR pipeline and normalize its evidence."""

    def __init__(self, pipeline_factory: Callable[..., _PaddlePipeline] | None = None) -> None:
        self._pipeline_factory = pipeline_factory
        self._pipelines: dict[str, _PaddlePipeline] = {}

    @property
    def name(self) -> str:
        return "PaddleOCR"

    def recognize(self, request: OCRRequest) -> OCRResult:
        started = time.perf_counter()
        pipeline = self._pipeline_for(request.options.language)
        image = Image.frombytes(
            "RGBA",
            (request.image.width, request.image.height),
            request.image.rgba_pixels,
        ).convert("RGB")
        try:
            numpy_module = importlib.import_module("numpy")
            asarray = cast(Callable[[object], object], numpy_module.asarray)
            raw_results = pipeline.predict(asarray(image))
            blocks = self._parse_results(raw_results, request.options.confidence_threshold)
        except OCRSetupError:
            raise
        except Exception as error:
            raise PixelCopyError(f"PaddleOCR could not recognize this image: {error}") from error

        rtl = request.options.language in {"ar", "en_ar"}
        ordered = sort_reading_order(blocks, right_to_left=rtl)
        return OCRResult(
            full_text=text_from_blocks(ordered, right_to_left=rtl),
            blocks=ordered,
            recognition_language=request.options.language,
            duration_seconds=time.perf_counter() - started,
            engine_name=self.name,
            image_width=request.image.width,
            image_height=request.image.height,
        )

    def _pipeline_for(self, language: str) -> _PaddlePipeline:
        cached = self._pipelines.get(language)
        if cached is not None:
            return cached
        factory = self._pipeline_factory or self._load_factory()
        paddle_language = "ar" if language in {"ar", "en_ar"} else "en"
        try:
            pipeline = factory(
                lang=paddle_language,
                use_doc_orientation_classify=True,
                use_doc_unwarping=False,
                use_textline_orientation=True,
                device="cpu",
                enable_mkldnn=False,
            )
        except Exception as error:
            raise OCRSetupError(
                "PaddleOCR could not initialize its local models. Install the OCR extras "
                "and complete local model setup."
            ) from error
        self._pipelines[language] = pipeline
        return pipeline

    @staticmethod
    def _load_factory() -> Callable[..., _PaddlePipeline]:
        try:
            module = importlib.import_module("paddleocr")
        except ImportError as error:
            raise OCRSetupError(
                "PaddleOCR is not installed. Install PixelCopy with the 'ocr' extra."
            ) from error
        return cast(Callable[..., _PaddlePipeline], module.PaddleOCR)

    @classmethod
    def _parse_results(
        cls,
        results: Iterable[_PaddleResult],
        confidence_threshold: float,
    ) -> tuple[OCRBlock, ...]:
        blocks: list[OCRBlock] = []
        for result in results:
            payload = result.json.get("res", result.json)
            if not isinstance(payload, Mapping):
                continue
            texts = cls._sequence(payload.get("rec_texts"))
            scores = cls._sequence(payload.get("rec_scores"))
            boxes = cls._sequence(payload.get("rec_boxes"))
            for text, score, box in zip(texts, scores, boxes, strict=False):
                if not isinstance(text, str) or not isinstance(score, int | float):
                    continue
                confidence = float(score)
                bounds = cls._bounds(box)
                if text and bounds is not None and confidence >= confidence_threshold:
                    blocks.append(OCRBlock(text, bounds, confidence))
        return tuple(blocks)

    @staticmethod
    def _sequence(value: object) -> Sequence[object]:
        if isinstance(value, Sequence) and not isinstance(value, str | bytes):
            return value
        tolist = getattr(value, "tolist", None)
        if callable(tolist):
            converted = tolist()
            if isinstance(converted, Sequence):
                return cast(Sequence[object], converted)
        return ()

    @classmethod
    def _bounds(cls, value: object) -> BoundingBox | None:
        coordinates = cls._sequence(value)
        if len(coordinates) != 4 or not all(isinstance(item, int | float) for item in coordinates):
            return None
        left, top, right, bottom = (float(cast(int | float, item)) for item in coordinates)
        return BoundingBox(left, top, right, bottom)
