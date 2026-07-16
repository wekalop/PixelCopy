"""Ordered and cancellable OpenCV image preprocessing."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import cv2
import numpy as np
from numpy.typing import NDArray

from pixelcopy.domain.exceptions import PixelCopyError
from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.preprocessing import PreprocessingOptions, ThresholdMode

PixelArray = NDArray[np.uint8]


class ProcessingCancelled(PixelCopyError):
    """Preprocessing stopped at a safe stage boundary."""


def enabled_stage_names(options: PreprocessingOptions) -> tuple[str, ...]:
    """Expose the exact deterministic pipeline order for UI and tests."""
    stages: list[str] = []
    if options.rotation_degrees:
        stages.append("rotation")
    if options.grayscale:
        stages.append("grayscale")
    if options.contrast != 1.0 or options.brightness:
        stages.append("contrast_brightness")
    if options.denoise:
        stages.append("denoise")
    if options.sharpen:
        stages.append("sharpen")
    if options.threshold is not ThresholdMode.NONE:
        stages.append("threshold")
    if options.invert:
        stages.append("invert")
    if options.deskew:
        stages.append("deskew")
    if options.upscale_factor != 1.0:
        stages.append("upscale")
    return tuple(stages)


class PreprocessingPipeline:
    """Transform an immutable source into a new immutable preview document."""

    def process(
        self,
        document: ImageDocument,
        options: PreprocessingOptions,
        is_cancelled: Callable[[], bool] | None = None,
        on_progress: Callable[[int], None] | None = None,
    ) -> ImageDocument:
        cancelled = is_cancelled or (lambda: False)
        progress = on_progress or (lambda value: None)
        image = (
            np.frombuffer(document.rgba_pixels, dtype=np.uint8)
            .reshape(document.height, document.width, 4)
            .copy()
        )
        stages = enabled_stage_names(options)
        if not stages:
            return document

        operations: dict[str, Callable[[PixelArray], PixelArray]] = {
            "rotation": lambda value: self._rotate(value, options.rotation_degrees),
            "grayscale": self._grayscale,
            "contrast_brightness": lambda value: cast(
                PixelArray,
                cv2.convertScaleAbs(value, alpha=options.contrast, beta=options.brightness),
            ),
            "denoise": self._denoise,
            "sharpen": self._sharpen,
            "threshold": lambda value: self._threshold(value, options.threshold),
            "invert": lambda value: cast(PixelArray, cv2.bitwise_not(value)),
            "deskew": self._deskew,
            "upscale": lambda value: cast(
                PixelArray,
                cv2.resize(
                    value,
                    None,
                    fx=options.upscale_factor,
                    fy=options.upscale_factor,
                    interpolation=cv2.INTER_CUBIC,
                ),
            ),
        }
        for index, stage in enumerate(stages, start=1):
            if cancelled():
                raise ProcessingCancelled("Image processing was cancelled.")
            image = operations[stage](image)
            progress(round(index / len(stages) * 100))

        rgba = self._to_rgba(image)
        height, width = rgba.shape[:2]
        return ImageDocument(
            source_name=f"Processed · {document.source_name}",
            image_format="RGBA",
            width=int(width),
            height=int(height),
            color_mode="RGBA",
            rgba_pixels=rgba.tobytes(),
            original_path=document.original_path,
        )

    @staticmethod
    def _rotate(image: PixelArray, degrees: int) -> PixelArray:
        rotations = {
            90: cv2.ROTATE_90_CLOCKWISE,
            180: cv2.ROTATE_180,
            270: cv2.ROTATE_90_COUNTERCLOCKWISE,
        }
        return cast(PixelArray, cv2.rotate(image, rotations[degrees]))

    @staticmethod
    def _grayscale(image: PixelArray) -> PixelArray:
        if image.ndim == 2:
            return image
        conversion = cv2.COLOR_RGBA2GRAY if image.shape[2] == 4 else cv2.COLOR_RGB2GRAY
        return cast(PixelArray, cv2.cvtColor(image, conversion))

    @classmethod
    def _denoise(cls, image: PixelArray) -> PixelArray:
        if image.ndim == 2:
            return cast(PixelArray, cv2.fastNlMeansDenoising(image, None, 7, 7, 21))
        rgb = cv2.cvtColor(cls._to_rgba(image), cv2.COLOR_RGBA2RGB)
        denoised = cv2.fastNlMeansDenoisingColored(rgb, None, 5, 5, 7, 21)
        return cast(PixelArray, cv2.cvtColor(denoised, cv2.COLOR_RGB2RGBA))

    @staticmethod
    def _sharpen(image: PixelArray) -> PixelArray:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        return cast(PixelArray, cv2.filter2D(image, -1, kernel))

    @classmethod
    def _threshold(cls, image: PixelArray, mode: ThresholdMode) -> PixelArray:
        gray = cls._grayscale(image)
        if mode is ThresholdMode.ADAPTIVE:
            return cast(
                PixelArray,
                cv2.adaptiveThreshold(
                    gray,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    31,
                    11,
                ),
            )
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cast(PixelArray, binary)

    @classmethod
    def _deskew(cls, image: PixelArray) -> PixelArray:
        gray = cls._grayscale(image)
        _, foreground = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coordinates = cv2.findNonZero(foreground)
        if coordinates is None or len(coordinates) < 10:
            return image
        angle = float(cv2.minAreaRect(coordinates)[-1])
        angle = -(90 + angle) if angle < -45 else -angle
        if abs(angle) < 0.1 or abs(angle) > 15:
            return image
        height, width = image.shape[:2]
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
        return cast(
            PixelArray,
            cv2.warpAffine(
                image,
                matrix,
                (width, height),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            ),
        )

    @staticmethod
    def _to_rgba(image: PixelArray) -> PixelArray:
        if image.ndim == 2:
            return cast(PixelArray, cv2.cvtColor(image, cv2.COLOR_GRAY2RGBA))
        if image.shape[2] == 3:
            return cast(PixelArray, cv2.cvtColor(image, cv2.COLOR_RGB2RGBA))
        return image
