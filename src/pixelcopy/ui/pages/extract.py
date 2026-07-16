"""Image import and OCR result workspace."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QTextOption
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import OCRMode, OCRResult
from pixelcopy.services.image_import_service import IMAGE_FILE_FILTER
from pixelcopy.ui.pages.base import Page
from pixelcopy.ui.widgets.image_preview import ImagePreview


class ExtractPage(Page):
    """Source import and editable OCR result workspace."""

    file_selected = Signal(Path)
    paste_requested = Signal()
    source_cleared = Signal()
    extract_requested = Signal(str, str, float)
    cancel_requested = Signal()
    copy_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Extract",
            "Import an image and recognize editable text privately on this device.",
            parent,
        )
        self.setAcceptDrops(True)
        self._has_source = False
        self._ocr_busy = False

        columns = QHBoxLayout()
        columns.setSpacing(18)
        self.page_layout.addLayout(columns, 1)
        columns.addWidget(self._build_source_card(), 1)
        columns.addWidget(self._build_result_card(), 1)
        self._update_controls()

    def _build_source_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addWidget(self._title("Source preview"))

        self.preview = ImagePreview()
        layout.addWidget(self.preview, 1)
        self.source_status = QLabel(
            "Drop an image here, open a file, or paste an image from the clipboard."
        )
        self.source_status.setObjectName("mutedLabel")
        self.source_status.setWordWrap(True)
        layout.addWidget(self.source_status)
        self.metadata = QLabel("No source selected")
        self.metadata.setObjectName("mutedLabel")
        layout.addWidget(self.metadata)

        zoom_actions = QHBoxLayout()
        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setAccessibleName("Zoom out")
        self.zoom_out_button.clicked.connect(self.preview.zoom_out)
        self.zoom_reset_button = QPushButton("Fit")
        self.zoom_reset_button.clicked.connect(self.preview.reset_zoom)
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setAccessibleName("Zoom in")
        self.zoom_in_button.clicked.connect(self.preview.zoom_in)
        for button in (self.zoom_out_button, self.zoom_reset_button, self.zoom_in_button):
            zoom_actions.addWidget(button)
        zoom_actions.addStretch(1)
        layout.addLayout(zoom_actions)

        import_actions = QHBoxLayout()
        self.open_button = QPushButton("Open image")
        self.open_button.setObjectName("primaryButton")
        self.open_button.clicked.connect(self._choose_image)
        self.paste_button = QPushButton("Paste")
        self.paste_button.setShortcut("Ctrl+V")
        self.paste_button.clicked.connect(self.paste_requested)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.source_cleared)
        for button in (self.open_button, self.paste_button, self.clear_button):
            import_actions.addWidget(button)
        layout.addLayout(import_actions)
        return card

    def _build_result_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addWidget(self._title("Recognized text"))

        options = QHBoxLayout()
        self.language_selector = QComboBox()
        self.language_selector.setAccessibleName("Recognition language")
        self.language_selector.addItem("English", "en")
        self.mode_selector = QComboBox()
        self.mode_selector.setAccessibleName("OCR mode")
        self.mode_selector.addItem("Paragraph", OCRMode.PARAGRAPH.value)
        self.mode_selector.addItem("Single line", OCRMode.SINGLE_LINE.value)
        self.mode_selector.addItem("Sparse text", OCRMode.SPARSE_TEXT.value)
        self.mode_selector.addItem("Table", OCRMode.TABLE.value)
        self.confidence_selector = QDoubleSpinBox()
        self.confidence_selector.setAccessibleName("Minimum confidence")
        self.confidence_selector.setRange(0.0, 1.0)
        self.confidence_selector.setSingleStep(0.05)
        self.confidence_selector.setValue(0.5)
        options.addWidget(self.language_selector)
        options.addWidget(self.mode_selector)
        options.addWidget(self.confidence_selector)
        layout.addLayout(options)

        self.result_editor = QPlainTextEdit()
        self.result_editor.setPlaceholderText("Recognized text will appear here.")
        self.result_editor.setAccessibleName("Recognized text editor")
        self.result_editor.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        layout.addWidget(self.result_editor, 1)

        self.result_status = QLabel("Ready for a source image")
        self.result_status.setObjectName("mutedLabel")
        self.result_status.setWordWrap(True)
        layout.addWidget(self.result_status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        actions = QHBoxLayout()
        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_requested)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_requested)
        self.extract_button = QPushButton("Extract text")
        self.extract_button.setObjectName("primaryButton")
        self.extract_button.clicked.connect(self._request_extraction)
        actions.addStretch(1)
        actions.addWidget(self.copy_button)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.extract_button)
        layout.addLayout(actions)
        return card

    def display_document(self, document: ImageDocument) -> None:
        self.preview.set_document(document)
        self._has_source = True
        self.source_status.setText(document.source_name)
        self.source_status.setObjectName("mutedLabel")
        self.metadata.setText(
            f"{document.image_format} · {document.dimensions_label} · {document.color_mode}"
        )
        self._refresh_label_styles(self.source_status)
        self._update_controls()

    def display_error(self, message: str) -> None:
        self.source_status.setText(message)
        self.source_status.setObjectName("errorLabel")
        self._refresh_label_styles(self.source_status)

    def clear_source(self) -> None:
        self.preview.clear_document()
        self._has_source = False
        self.source_status.setText(
            "Drop an image here, open a file, or paste an image from the clipboard."
        )
        self.source_status.setObjectName("mutedLabel")
        self.metadata.setText("No source selected")
        self._refresh_label_styles(self.source_status)
        self._update_controls()

    def set_source_available(self, available: bool) -> None:
        self._has_source = available
        self._update_controls()

    def set_ocr_busy(self, busy: bool) -> None:
        self._ocr_busy = busy
        self.progress.setVisible(busy)
        if busy:
            self.progress.setValue(0)
            self.result_status.setText("Recognizing text locally...")
        self._update_controls()

    def set_ocr_progress(self, value: int) -> None:
        self.progress.setValue(value)

    def display_ocr_result(self, result: OCRResult) -> None:
        self.result_editor.setPlainText(result.full_text)
        self.result_status.setObjectName("mutedLabel")
        self.result_status.setText(
            f"{len(result.full_text.split())} words · {len(result.full_text)} characters · "
            f"{result.duration_seconds:.2f} s · {result.average_confidence:.0%} confidence · "
            f"{result.engine_name} · {result.recognition_language} · "
            f"{len(result.warnings)} warning(s)"
        )
        self._refresh_label_styles(self.result_status)
        self._update_controls()

    def display_ocr_error(self, message: str) -> None:
        self.result_status.setText(message)
        self.result_status.setObjectName("errorLabel")
        self._refresh_label_styles(self.result_status)

    def display_ocr_cancelled(self) -> None:
        self.result_status.setText("Text recognition was cancelled.")
        self.result_status.setObjectName("mutedLabel")
        self._refresh_label_styles(self.result_status)

    def _request_extraction(self) -> None:
        language = self.language_selector.currentData()
        mode = self.mode_selector.currentData()
        if isinstance(language, str) and isinstance(mode, str):
            self.extract_requested.emit(language, mode, self.confidence_selector.value())

    def _choose_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open image", "", IMAGE_FILE_FILTER)
        if path:
            self.file_selected.emit(Path(path))

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].isLocalFile():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].isLocalFile():
            self.file_selected.emit(Path(urls[0].toLocalFile()))
            event.acceptProposedAction()
        else:
            event.ignore()

    def _update_controls(self) -> None:
        for control in (
            self.clear_button,
            self.zoom_out_button,
            self.zoom_reset_button,
            self.zoom_in_button,
        ):
            control.setEnabled(self._has_source and not self._ocr_busy)
        self.open_button.setEnabled(not self._ocr_busy)
        self.paste_button.setEnabled(not self._ocr_busy)
        self.extract_button.setEnabled(self._has_source and not self._ocr_busy)
        self.cancel_button.setEnabled(self._ocr_busy)
        self.copy_button.setEnabled(bool(self.result_editor.toPlainText()) and not self._ocr_busy)
        self.language_selector.setEnabled(not self._ocr_busy)
        self.mode_selector.setEnabled(not self._ocr_busy)
        self.confidence_selector.setEnabled(not self._ocr_busy)

    @staticmethod
    def _refresh_label_styles(label: QLabel) -> None:
        label.style().unpolish(label)
        label.style().polish(label)

    @staticmethod
    def _title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("cardTitle")
        return label
