"""Milestone-scoped placeholder pages."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from pixelcopy.config.constants import APP_TAGLINE, APP_VERSION
from pixelcopy.ui.pages.base import Page


class PlaceholderPage(Page):
    """An honest empty state for a future milestone."""

    def __init__(
        self,
        title: str,
        description: str,
        milestone: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, description, parent)
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.addStretch(1)
        status = QLabel(f"Planned for {milestone}")
        status.setObjectName("cardTitle")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        explanation = QLabel(
            "This foundation page is ready for its focused implementation milestone."
        )
        explanation.setObjectName("mutedLabel")
        explanation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        explanation.setWordWrap(True)
        card_layout.addWidget(status)
        card_layout.addWidget(explanation)
        card_layout.addStretch(1)
        self.page_layout.addWidget(card, 1)


class AboutPage(Page):
    """Product identity and privacy summary."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("About", "A private, local-first Windows OCR workspace.", parent)
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        title = QLabel("PixelCopy")
        title.setObjectName("pageTitle")
        tagline = QLabel(APP_TAGLINE)
        tagline.setObjectName("cardTitle")
        details = QLabel(
            f"Version {APP_VERSION}\n\nPixelCopy processes visual content locally. "
            "It does not upload documents, send telemetry, or use generative AI."
        )
        details.setObjectName("mutedLabel")
        details.setWordWrap(True)
        card_layout.addWidget(title)
        card_layout.addWidget(tagline)
        card_layout.addSpacing(16)
        card_layout.addWidget(details)
        card_layout.addStretch(1)
        self.page_layout.addWidget(card, 1)
