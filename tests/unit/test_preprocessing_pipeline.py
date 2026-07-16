from __future__ import annotations

import numpy as np
import pytest

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.preprocessing import PreprocessingOptions, ThresholdMode
from pixelcopy.preprocessing.pipeline import (
    PreprocessingPipeline,
    ProcessingCancelled,
    enabled_stage_names,
)


def document(width: int = 6, height: int = 4) -> ImageDocument:
    pixels = np.zeros((height, width, 4), dtype=np.uint8)
    pixels[:, :, :3] = 120
    pixels[:, :, 3] = 255
    return ImageDocument("source.png", "PNG", width, height, "RGBA", pixels.tobytes())


def test_stage_order_is_explicit_and_stable() -> None:
    options = PreprocessingOptions(
        rotation_degrees=90,
        grayscale=True,
        contrast=1.2,
        denoise=True,
        sharpen=True,
        threshold=ThresholdMode.BINARY,
        invert=True,
        deskew=True,
        upscale_factor=2.0,
    )

    assert enabled_stage_names(options) == (
        "rotation",
        "grayscale",
        "contrast_brightness",
        "denoise",
        "sharpen",
        "threshold",
        "invert",
        "deskew",
        "upscale",
    )


def test_rotation_and_upscale_create_new_document_without_mutating_source() -> None:
    source = document()
    original_pixels = source.rgba_pixels

    processed = PreprocessingPipeline().process(
        source,
        PreprocessingOptions(rotation_degrees=90, upscale_factor=2.0),
    )

    assert (processed.width, processed.height) == (8, 12)
    assert processed is not source
    assert source.rgba_pixels == original_pixels


def test_original_profile_returns_untouched_document() -> None:
    source = document()

    assert PreprocessingPipeline().process(source, PreprocessingOptions()) is source


def test_cancellation_is_checked_between_stages() -> None:
    with pytest.raises(ProcessingCancelled):
        PreprocessingPipeline().process(
            document(),
            PreprocessingOptions(grayscale=True),
            is_cancelled=lambda: True,
        )
