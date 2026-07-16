"""Milestone 1 Extract page shell."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pixelcopy.ui.pages.base import Page


class ExtractPage(Page):
    """Foundation layout for the future extraction workflow."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Extract",
            "Bring visual content into PixelCopy and turn it into editable text locally.",
            parent,
        )

        columns = QHBoxLayout()
        columns.setSpacing(18)
        self.page_layout.addLayout(columns, 1)

        source_card = QFrame()
        source_card.setObjectName("card")
        source_layout = QVBoxLayout(source_card)
        source_layout.setContentsMargins(20, 20, 20, 20)
        source_layout.setSpacing(14)
        source_layout.addWidget(self._title("Source preview"))
        empty = QFrame()
        empty.setObjectName("emptyState")
        empty_layout = QVBoxLayout(empty)
        empty_layout.setContentsMargins(24, 24, 24, 24)
        empty_layout.addStretch(1)
        prompt = QLabel("No source selected")
        prompt.setObjectName("cardTitle")
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detail = QLabel(
            "Image import, clipboard paste, and screen capture arrive in later milestones."
        )
        detail.setObjectName("mutedLabel")
        detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detail.setWordWrap(True)
        empty_layout.addWidget(prompt)
        empty_layout.addWidget(detail)
        empty_layout.addStretch(1)
        source_layout.addWidget(empty, 1)
        open_button = QPushButton("Open image")
        open_button.setObjectName("primaryButton")
        open_button.setEnabled(False)
        open_button.setToolTip("Image import is planned for Milestone 2")
        source_layout.addWidget(open_button)

        result_card = QFrame()
        result_card.setObjectName("card")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(20, 20, 20, 20)
        result_layout.setSpacing(14)
        result_layout.addWidget(self._title("Recognized text"))
        editor = QPlainTextEdit()
        editor.setPlaceholderText("Extracted text will appear here.")
        editor.setAccessibleName("Recognized text editor")
        editor.setReadOnly(True)
        result_layout.addWidget(editor, 1)
        actions = QHBoxLayout()
        extract_button = QPushButton("Extract text")
        extract_button.setObjectName("primaryButton")
        extract_button.setEnabled(False)
        copy_button = QPushButton("Copy")
        copy_button.setEnabled(False)
        actions.addStretch(1)
        actions.addWidget(copy_button)
        actions.addWidget(extract_button)
        result_layout.addLayout(actions)

        columns.addWidget(source_card, 1)
        columns.addWidget(result_card, 1)

    @staticmethod
    def _title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("cardTitle")
        return label
