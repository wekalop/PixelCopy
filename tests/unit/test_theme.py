from __future__ import annotations

from pixelcopy.ui.styles.theme import Theme, stylesheet


def test_themes_have_distinct_accessible_application_styles() -> None:
    light = stylesheet(Theme.LIGHT)
    dark = stylesheet(Theme.DARK)

    assert light != dark
    assert "#2563EB" in light
    assert "#101521" in dark
    assert "QPushButton:focus" in light
