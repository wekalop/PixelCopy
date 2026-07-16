"""Sidebar navigation widget."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from pixelcopy.config.constants import APP_NAME, APP_TAGLINE


@dataclass(frozen=True, slots=True)
class NavigationItem:
    """A stable page identifier and user-facing label."""

    key: str
    label: str
    shortcut: str


NAVIGATION_ITEMS = (
    NavigationItem("extract", "Extract", "Alt+1"),
    NavigationItem("pdf", "PDF", "Alt+2"),
    NavigationItem("history", "History", "Alt+3"),
    NavigationItem("settings", "Settings", "Alt+4"),
    NavigationItem("about", "About", "Alt+5"),
)


class NavigationSidebar(QWidget):
    """Accessible, exclusive page navigation."""

    page_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self._buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 26, 20, 20)
        layout.setSpacing(8)

        brand = QLabel(APP_NAME)
        brand.setObjectName("brandName")
        tagline = QLabel(APP_TAGLINE)
        tagline.setObjectName("brandTagline")
        tagline.setWordWrap(True)
        layout.addWidget(brand)
        layout.addWidget(tagline)
        layout.addSpacing(26)

        group = QButtonGroup(self)
        group.setExclusive(True)
        for item in NAVIGATION_ITEMS:
            button = QPushButton(item.label)
            button.setObjectName("navButton")
            button.setProperty("pageKey", item.key)
            button.setAccessibleName(f"Open {item.label} page")
            button.setToolTip(f"Open {item.label} ({item.shortcut})")
            button.setShortcut(item.shortcut)
            button.setCheckable(True)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(
                lambda checked=False, key=item.key: self.page_requested.emit(key)
            )
            group.addButton(button)
            layout.addWidget(button)
            self._buttons[item.key] = button

        layout.addStretch(1)
        privacy = QLabel("Local processing\nNo uploads or telemetry")
        privacy.setObjectName("brandTagline")
        privacy.setWordWrap(True)
        layout.addWidget(privacy)
        self.select("extract")

    def select(self, key: str) -> None:
        """Update the visible selected navigation item."""
        button = self._buttons.get(key)
        if button is not None:
            button.setChecked(True)

    def button_for(self, key: str) -> QPushButton:
        """Return a navigation button for testing and focus management."""
        return self._buttons[key]
