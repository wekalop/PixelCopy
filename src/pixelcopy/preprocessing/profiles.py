"""Named preprocessing profiles."""

from __future__ import annotations

from pixelcopy.domain.preprocessing import (
    PreprocessingOptions,
    PreprocessingProfile,
    ThresholdMode,
)


def options_for_profile(profile: PreprocessingProfile) -> PreprocessingOptions:
    """Return a new immutable options value for a named profile."""
    profiles = {
        PreprocessingProfile.ORIGINAL: PreprocessingOptions(),
        PreprocessingProfile.AUTOMATIC: PreprocessingOptions(
            grayscale=True,
            contrast=1.15,
            denoise=True,
            deskew=True,
        ),
        PreprocessingProfile.SCANNED_DOCUMENT: PreprocessingOptions(
            grayscale=True,
            contrast=1.2,
            denoise=True,
            threshold=ThresholdMode.ADAPTIVE,
            deskew=True,
        ),
        PreprocessingProfile.LOW_CONTRAST: PreprocessingOptions(
            grayscale=True,
            contrast=1.65,
            threshold=ThresholdMode.ADAPTIVE,
        ),
        PreprocessingProfile.SMALL_TEXT: PreprocessingOptions(
            grayscale=True,
            contrast=1.2,
            sharpen=True,
            upscale_factor=2.0,
        ),
        PreprocessingProfile.DARK_BACKGROUND: PreprocessingOptions(
            grayscale=True,
            contrast=1.25,
            threshold=ThresholdMode.ADAPTIVE,
            invert=True,
        ),
        PreprocessingProfile.CUSTOM: PreprocessingOptions(),
    }
    return profiles[profile]
