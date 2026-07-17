"""Shared page layout helpers."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class Page(QWidget):
    """Base page with consistent heading and content spacing."""

    def __init__(self, title: str, description: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(f"{title.lower()}Page")
        self.page_layout = QVBoxLayout(self)
        self.page_layout.setContentsMargins(24, 20, 24, 18)
        self.page_layout.setSpacing(10)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        heading.setAccessibleName(f"{title} page")
        summary = QLabel(description)
        summary.setObjectName("pageDescription")
        summary.setWordWrap(True)
        self.page_layout.addWidget(heading)
        self.page_layout.addWidget(summary)
