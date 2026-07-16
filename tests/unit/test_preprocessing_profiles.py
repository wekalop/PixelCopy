from __future__ import annotations

from pixelcopy.domain.preprocessing import PreprocessingProfile, ThresholdMode
from pixelcopy.preprocessing.profiles import options_for_profile


def test_every_profile_has_deterministic_options() -> None:
    profiles = {profile: options_for_profile(profile) for profile in PreprocessingProfile}

    assert profiles[PreprocessingProfile.ORIGINAL].grayscale is False
    assert profiles[PreprocessingProfile.SCANNED_DOCUMENT].threshold is ThresholdMode.ADAPTIVE
    assert profiles[PreprocessingProfile.SMALL_TEXT].upscale_factor == 2.0
    assert profiles[PreprocessingProfile.DARK_BACKGROUND].invert is True
