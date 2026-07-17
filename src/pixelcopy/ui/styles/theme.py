"""Central semantic design tokens and light/dark application themes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QApplication


class Theme(StrEnum):
    """Supported application color schemes."""

    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True, slots=True)
class DesignTokens:
    """Semantic colors shared by every PixelCopy control."""

    background: str
    surface: str
    elevated_surface: str
    surface_subtle: str
    text_primary: str
    text_secondary: str
    text_muted: str
    border: str
    border_strong: str
    accent: str
    accent_hover: str
    accent_pressed: str
    accent_soft: str
    focus_ring: str
    success: str
    warning: str
    error: str
    disabled_foreground: str
    disabled_background: str
    sidebar_background: str
    sidebar_foreground: str
    sidebar_muted: str
    navigation_selected: str


_TOKENS: dict[Theme, DesignTokens] = {
    Theme.LIGHT: DesignTokens(
        background="#F3F6FA",
        surface="#FFFFFF",
        elevated_surface="#FFFFFF",
        surface_subtle="#F7F9FC",
        text_primary="#162033",
        text_secondary="#475467",
        text_muted="#667085",
        border="#D7DFEA",
        border_strong="#B8C4D4",
        accent="#2563EB",
        accent_hover="#1D4ED8",
        accent_pressed="#1E40AF",
        accent_soft="#EAF1FF",
        focus_ring="#3B82F6",
        success="#15803D",
        warning="#B45309",
        error="#C62828",
        disabled_foreground="#8792A2",
        disabled_background="#EEF2F6",
        sidebar_background="#173A70",
        sidebar_foreground="#F8FAFF",
        sidebar_muted="#C7D7F2",
        navigation_selected="#FFFFFF",
    ),
    Theme.DARK: DesignTokens(
        background="#101521",
        surface="#171F2C",
        elevated_surface="#1B2533",
        surface_subtle="#202B3A",
        text_primary="#F3F6FA",
        text_secondary="#CDD5DF",
        text_muted="#A9B4C4",
        border="#354256",
        border_strong="#53627A",
        accent="#60A5FA",
        accent_hover="#3B82F6",
        accent_pressed="#2563EB",
        accent_soft="#203A60",
        focus_ring="#93C5FD",
        success="#4ADE80",
        warning="#FBBF24",
        error="#F87171",
        disabled_foreground="#7E8A9B",
        disabled_background="#222C3A",
        sidebar_background="#101D33",
        sidebar_foreground="#F5F8FF",
        sidebar_muted="#B8C7E0",
        navigation_selected="#EAF1FF",
    ),
}

# Layout tokens are device-independent Qt coordinates. Keep them centralized so
# layouts and QSS use one coherent scale.
SPACING = (4, 8, 12, 16, 20, 24, 32)
CARD_RADIUS = 12
CONTROL_RADIUS = 7
ICON_SIZE = 18
BODY_FONT_SIZE = 14
METADATA_FONT_SIZE = 12
CARD_TITLE_SIZE = 17
PAGE_TITLE_SIZE = 27


def tokens(theme: Theme) -> DesignTokens:
    """Return immutable semantic tokens for ``theme``."""
    return _TOKENS[theme]


def control_height(application: QApplication) -> int:
    """Derive a safe control height from the active UI font metrics."""
    return max(36, QFontMetrics(application.font()).height() + 18)


def stylesheet(theme: Theme, minimum_control_height: int | None = None) -> str:
    """Build the complete stylesheet for a theme."""
    color = tokens(theme)
    height = minimum_control_height or 36
    return f"""
        * {{
            font-family: "Segoe UI", sans-serif;
            font-size: {BODY_FONT_SIZE}px;
        }}
        QMainWindow, QWidget#appRoot, QWidget#extractPage {{
            background: {color.background};
            color: {color.text_primary};
        }}
        QLabel {{ color: {color.text_primary}; background: transparent; }}
        QLabel#mutedLabel, QLabel#pageDescription, QLabel#eyebrow {{
            color: {color.text_secondary};
        }}
        QLabel#metadataLabel {{
            color: {color.text_muted};
            font-size: {METADATA_FONT_SIZE}px;
        }}
        QLabel#errorLabel {{ color: {color.error}; font-weight: 600; }}
        QLabel#successLabel {{ color: {color.success}; font-weight: 600; }}
        QLabel#pageTitle {{ font-size: {PAGE_TITLE_SIZE}px; font-weight: 700; }}
        QLabel#cardTitle {{ font-size: {CARD_TITLE_SIZE}px; font-weight: 650; }}
        QLabel#sectionTitle {{ font-weight: 650; color: {color.text_secondary}; }}
        QLabel#brandName {{ font-size: 21px; font-weight: 700; color: {color.sidebar_foreground}; }}
        QLabel#brandTagline {{ font-size: 12px; color: {color.sidebar_muted}; }}
        QWidget#sidebar {{ background: {color.sidebar_background}; border: none; }}
        QFrame#card {{
            background: {color.surface};
            border: 1px solid {color.border};
            border-radius: {CARD_RADIUS}px;
        }}
        QFrame#emptyState, QFrame#dropZone {{
            background: {color.surface_subtle};
            border: 1px dashed {color.border_strong};
            border-radius: 10px;
        }}
        QPushButton, QToolButton {{
            min-height: {height}px;
            background: {color.surface};
            color: {color.text_primary};
            border: 1px solid {color.border};
            border-radius: {CONTROL_RADIUS}px;
            padding: 0 12px;
            font-weight: 600;
        }}
        QPushButton:hover, QToolButton:hover {{
            border-color: {color.accent};
            background: {color.accent_soft};
        }}
        QPushButton:pressed, QToolButton:pressed {{
            background: {color.accent_pressed};
            border-color: {color.accent_pressed};
            color: white;
        }}
        QPushButton:focus, QToolButton:focus {{ border: 2px solid {color.focus_ring}; }}
        QPushButton:disabled, QToolButton:disabled {{
            color: {color.disabled_foreground};
            background: {color.disabled_background};
            border-color: {color.border};
        }}
        QPushButton#primaryButton {{
            background: {color.accent};
            color: white;
            border-color: {color.accent};
        }}
        QPushButton#primaryButton:hover {{ background: {color.accent_hover}; }}
        QPushButton#primaryButton:pressed {{ background: {color.accent_pressed}; }}
        QPushButton#tertiaryButton {{ background: transparent; border-color: transparent; color: {color.text_secondary}; }}
        QPushButton#navButton {{
            min-height: 42px;
            color: {color.sidebar_foreground};
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 0 13px;
            text-align: left;
            font-weight: 600;
        }}
        QPushButton#navButton:hover {{ background: rgba(255, 255, 255, 0.12); color: white; }}
        QPushButton#navButton:focus {{ border-color: white; }}
        QPushButton#navButton:checked {{
            background: {color.navigation_selected};
            color: #173B70;
        }}
        QPlainTextEdit, QLineEdit, QKeySequenceEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            min-height: {height}px;
            background: {color.surface};
            color: {color.text_primary};
            border: 1px solid {color.border_strong};
            border-radius: {CONTROL_RADIUS}px;
            selection-background-color: {color.accent};
            selection-color: white;
        }}
        QPlainTextEdit, QLineEdit, QKeySequenceEdit {{ padding: 6px 9px; }}
        QComboBox, QSpinBox, QDoubleSpinBox {{ padding: 0 9px; padding-right: 28px; }}
        QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled,
        QLineEdit:disabled, QKeySequenceEdit:disabled {{
            color: {color.disabled_foreground};
            background: {color.disabled_background};
        }}
        QPlainTextEdit:focus, QLineEdit:focus, QKeySequenceEdit:focus,
        QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {color.focus_ring};
        }}
        QComboBox::drop-down {{ border: none; width: 26px; }}
        QComboBox::down-arrow {{ width: 8px; height: 8px; }}
        QComboBox QAbstractItemView {{
            background: {color.elevated_surface};
            color: {color.text_primary};
            border: 1px solid {color.border_strong};
            selection-background-color: {color.accent};
            selection-color: white;
            outline: 0;
            padding: 4px;
        }}
        QComboBox QAbstractItemView::item {{ min-height: 30px; padding: 3px 8px; }}
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            width: 20px;
            border: none;
            background: {color.surface_subtle};
        }}
        QCheckBox {{ color: {color.text_primary}; spacing: 8px; min-height: 28px; }}
        QCheckBox:disabled {{ color: {color.disabled_foreground}; }}
        QToolButton:checked {{ background: {color.accent_soft}; border-color: {color.accent}; }}
        QTabWidget::pane {{ border: 1px solid {color.border}; border-radius: 8px; background: {color.surface_subtle}; }}
        QTabBar::tab {{
            min-height: 34px;
            background: transparent;
            color: {color.text_secondary};
            border: none;
            padding: 0 14px;
        }}
        QTabBar::tab:selected {{ color: {color.accent}; border-bottom: 2px solid {color.accent}; font-weight: 650; }}
        QTabBar::tab:disabled {{ color: {color.disabled_foreground}; }}
        QGraphicsView#imagePreview {{ background: {color.surface_subtle}; border: none; }}
        QProgressBar {{
            min-height: 18px;
            color: {color.text_primary};
            background: {color.disabled_background};
            border: none;
            border-radius: 6px;
            text-align: center;
        }}
        QProgressBar::chunk {{ background: {color.accent}; border-radius: 6px; }}
        QScrollArea {{ background: transparent; border: none; }}
        QScrollArea > QWidget > QWidget {{ background: transparent; }}
        QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
        QScrollBar::handle:vertical {{ background: {color.border_strong}; border-radius: 4px; min-height: 28px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QMenu {{ background: {color.elevated_surface}; color: {color.text_primary}; border: 1px solid {color.border}; padding: 5px; }}
        QMenu::item {{ min-height: 28px; padding: 3px 22px 3px 9px; border-radius: 5px; }}
        QMenu::item:selected {{ background: {color.accent_soft}; color: {color.text_primary}; }}
        QToolTip {{ background: {color.elevated_surface}; color: {color.text_primary}; border: 1px solid {color.border_strong}; padding: 6px; }}
        QStatusBar {{ background: {color.surface}; color: {color.text_secondary}; border-top: 1px solid {color.border}; }}
        QSplitter::handle {{ background: transparent; width: 8px; }}
    """


def apply_theme(application: QApplication, theme: Theme) -> None:
    """Apply a named theme to the full application."""
    application.setProperty("pixelcopyTheme", theme.value)
    application.setStyleSheet(stylesheet(theme, control_height(application)))
