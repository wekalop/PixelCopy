"""Image import and future OCR workspace."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pixelcopy.domain.images import ImageDocument
from pixelcopy.services.image_import_service import IMAGE_FILE_FILTER
from pixelcopy.ui.pages.base import Page
from pixelcopy.ui.widgets.image_preview import ImagePreview


class ExtractPage(Page):
    """Source import and editable-result workspace."""

    file_selected = Signal(Path)
    paste_requested = Signal()
    source_cleared = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Extract",
            "Import an image and prepare it for private, local text recognition.",
            parent,
        )
        self.setAcceptDrops(True)
        self._has_source = False

        columns = QHBoxLayout()
        columns.setSpacing(18)
        self.page_layout.addLayout(columns, 1)

        source_card = QFrame()
        source_card.setObjectName("card")
        source_layout = QVBoxLayout(source_card)
        source_layout.setContentsMargins(20, 20, 20, 20)
        source_layout.setSpacing(12)
        source_layout.addWidget(self._title("Source preview"))

        self.preview = ImagePreview()
        source_layout.addWidget(self.preview, 1)

        self.source_status = QLabel(
            "Drop an image here, open a file, or paste an image from the clipboard."
        )
        self.source_status.setObjectName("mutedLabel")
        self.source_status.setWordWrap(True)
        source_layout.addWidget(self.source_status)

        self.metadata = QLabel("No source selected")
        self.metadata.setObjectName("mutedLabel")
        self.metadata.setWordWrap(True)
        source_layout.addWidget(self.metadata)

        zoom_actions = QHBoxLayout()
        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setAccessibleName("Zoom out")
        self.zoom_out_button.setToolTip("Zoom out")
        self.zoom_out_button.clicked.connect(self.preview.zoom_out)
        self.zoom_reset_button = QPushButton("Fit")
        self.zoom_reset_button.setToolTip("Fit image to preview")
        self.zoom_reset_button.clicked.connect(self.preview.reset_zoom)
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setAccessibleName("Zoom in")
        self.zoom_in_button.setToolTip("Zoom in")
        self.zoom_in_button.clicked.connect(self.preview.zoom_in)
        zoom_actions.addWidget(self.zoom_out_button)
        zoom_actions.addWidget(self.zoom_reset_button)
        zoom_actions.addWidget(self.zoom_in_button)
        zoom_actions.addStretch(1)
        source_layout.addLayout(zoom_actions)

        import_actions = QHBoxLayout()
        self.open_button = QPushButton("Open image")
        self.open_button.setObjectName("primaryButton")
        self.open_button.clicked.connect(self._choose_image)
        self.paste_button = QPushButton("Paste")
        self.paste_button.setShortcut("Ctrl+V")
        self.paste_button.clicked.connect(self.paste_requested)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.source_cleared)
        import_actions.addWidget(self.open_button)
        import_actions.addWidget(self.paste_button)
        import_actions.addWidget(self.clear_button)
        source_layout.addLayout(import_actions)

        result_card = QFrame()
        result_card.setObjectName("card")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(20, 20, 20, 20)
        result_layout.setSpacing(14)
        result_layout.addWidget(self._title("Recognized text"))
        editor = QPlainTextEdit()
        editor.setPlaceholderText("OCR arrives in Milestone 3. Extracted text will appear here.")
        editor.setAccessibleName("Recognized text editor")
        editor.setReadOnly(True)
        result_layout.addWidget(editor, 1)
        extract_button = QPushButton("Extract text")
        extract_button.setObjectName("primaryButton")
        extract_button.setEnabled(False)
        extract_button.setToolTip("OCR is implemented in Milestone 3")
        result_layout.addWidget(extract_button)

        columns.addWidget(source_card, 1)
        columns.addWidget(result_card, 1)
        self._update_source_controls()

    def display_document(self, document: ImageDocument) -> None:
        """Present a successfully imported source and its useful metadata."""
        self.preview.set_document(document)
        self._has_source = True
        self.source_status.setText(document.source_name)
        self.source_status.setObjectName("mutedLabel")
        self.metadata.setText(
            f"{document.image_format} · {document.dimensions_label} · {document.color_mode}"
        )
        self._refresh_label_styles(self.source_status)
        self._update_source_controls()

    def display_error(self, message: str) -> None:
        """Show an actionable import error without discarding a valid current source."""
        self.source_status.setText(message)
        self.source_status.setObjectName("errorLabel")
        self._refresh_label_styles(self.source_status)

    def clear_source(self) -> None:
        """Clear the visible source and reset metadata and controls."""
        self.preview.clear_document()
        self._has_source = False
        self.source_status.setText(
            "Drop an image here, open a file, or paste an image from the clipboard."
        )
        self.source_status.setObjectName("mutedLabel")
        self.metadata.setText("No source selected")
        self._refresh_label_styles(self.source_status)
        self._update_source_controls()

    def _choose_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open image", "", IMAGE_FILE_FILTER)
        if path:
            self.file_selected.emit(Path(path))

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Accept only a single local file URL for content validation."""
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].isLocalFile():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        """Forward a dropped local path to the import controller."""
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].isLocalFile():
            self.file_selected.emit(Path(urls[0].toLocalFile()))
            event.acceptProposedAction()
        else:
            event.ignore()

    def _update_source_controls(self) -> None:
        for control in (
            self.clear_button,
            self.zoom_out_button,
            self.zoom_reset_button,
            self.zoom_in_button,
        ):
            control.setEnabled(self._has_source)

    @staticmethod
    def _refresh_label_styles(label: QLabel) -> None:
        label.style().unpolish(label)
        label.style().polish(label)

    @staticmethod
    def _title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("cardTitle")
        return label
