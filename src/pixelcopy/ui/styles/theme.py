"""Central light and dark application themes."""

from __future__ import annotations

from enum import StrEnum

from PySide6.QtWidgets import QApplication


class Theme(StrEnum):
    """Supported application color schemes."""

    LIGHT = "light"
    DARK = "dark"


_PALETTES: dict[Theme, dict[str, str]] = {
    Theme.LIGHT: {
        "background": "#F4F7FB",
        "surface": "#FFFFFF",
        "surface_alt": "#EDF3FA",
        "text": "#172033",
        "muted": "#667085",
        "border": "#D8E1EC",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "accent_soft": "#E8F0FF",
        "danger": "#DC2626",
    },
    Theme.DARK: {
        "background": "#101521",
        "surface": "#181F2D",
        "surface_alt": "#202A3A",
        "text": "#F2F5FA",
        "muted": "#AAB5C5",
        "border": "#334155",
        "accent": "#60A5FA",
        "accent_hover": "#3B82F6",
        "accent_soft": "#1D3557",
        "danger": "#F87171",
    },
}


def stylesheet(theme: Theme) -> str:
    """Build the complete stylesheet for a theme."""
    color = _PALETTES[theme]
    return f"""
        * {{ font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 14px; }}
        QMainWindow, QWidget#appRoot {{ background: {color["background"]}; color: {color["text"]}; }}
        QLabel {{ color: {color["text"]}; background: transparent; }}
        QLabel#mutedLabel, QLabel#pageDescription, QLabel#eyebrow {{ color: {color["muted"]}; }}
        QLabel#errorLabel {{ color: {color["danger"]}; font-weight: 600; }}
        QLabel#pageTitle {{ font-size: 28px; font-weight: 700; }}
        QLabel#cardTitle {{ font-size: 17px; font-weight: 650; }}
        QLabel#brandName {{ font-size: 20px; font-weight: 700; color: white; }}
        QLabel#brandTagline {{ font-size: 12px; color: #C9DAFF; }}
        QWidget#sidebar {{ background: #12306B; border: none; }}
        QFrame#card {{ background: {color["surface"]}; border: 1px solid {color["border"]}; border-radius: 14px; }}
        QFrame#emptyState {{ background: {color["surface_alt"]}; border: 1px dashed {color["border"]}; border-radius: 12px; }}
        QPushButton {{ background: {color["surface"]}; color: {color["text"]}; border: 1px solid {color["border"]}; border-radius: 8px; padding: 9px 14px; font-weight: 600; }}
        QPushButton:hover {{ border-color: {color["accent"]}; background: {color["accent_soft"]}; }}
        QPushButton:focus {{ border: 2px solid {color["accent"]}; }}
        QPushButton:disabled {{ color: {color["muted"]}; background: {color["surface_alt"]}; }}
        QPushButton#primaryButton {{ background: {color["accent"]}; color: white; border-color: {color["accent"]}; }}
        QPushButton#primaryButton:hover {{ background: {color["accent_hover"]}; }}
        QPushButton#navButton {{ color: #DDE8FF; background: transparent; border: none; border-radius: 8px; padding: 11px 14px; text-align: left; font-weight: 600; }}
        QPushButton#navButton:hover {{ background: rgba(255, 255, 255, 0.10); color: white; }}
        QPushButton#navButton:checked {{ background: #FFFFFF; color: #173B7A; }}
        QPlainTextEdit, QLineEdit, QComboBox {{ background: {color["surface"]}; color: {color["text"]}; border: 1px solid {color["border"]}; border-radius: 8px; padding: 8px; selection-background-color: {color["accent"]}; }}
        QGraphicsView#imagePreview {{ background: {color["surface_alt"]}; border: 1px dashed {color["border"]}; border-radius: 10px; }}
        QPlainTextEdit:focus, QLineEdit:focus, QComboBox:focus {{ border: 2px solid {color["accent"]}; }}
        QStatusBar {{ background: {color["surface"]}; color: {color["muted"]}; border-top: 1px solid {color["border"]}; }}
        QToolTip {{ background: {color["surface"]}; color: {color["text"]}; border: 1px solid {color["border"]}; padding: 5px; }}
    """


def apply_theme(application: QApplication, theme: Theme) -> None:
    """Apply a named theme to the full application."""
    application.setProperty("pixelcopyTheme", theme.value)
    application.setStyleSheet(stylesheet(theme))
