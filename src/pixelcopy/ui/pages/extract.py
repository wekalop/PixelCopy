"""Image import and OCR result workspace."""

from __future__ import annotations

from itertools import pairwise
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QTextOption
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import OCRMode, OCRResult
from pixelcopy.services.image_import_service import IMAGE_FILE_FILTER
from pixelcopy.ui.dialogs.find_replace import FindReplaceDialog
from pixelcopy.ui.pages.base import Page
from pixelcopy.ui.widgets.image_preview import ImagePreview
from pixelcopy.ui.widgets.preprocessing_panel import PreprocessingPanel


class ExtractPage(Page):
    """Source import and editable OCR result workspace."""

    file_selected = Signal(Path)
    paste_requested = Signal()
    source_cleared = Signal()
    capture_requested = Signal()
    extract_requested = Signal(str, str, float)
    cancel_requested = Signal()
    copy_requested = Signal()
    save_requested = Signal()
    export_requested = Signal()
    cleanup_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Extract",
            "Import an image and recognize editable text privately on this device.",
            parent,
        )
        self.setAcceptDrops(True)
        self._has_source = False
        self._ocr_busy = False
        self._find_dialog: FindReplaceDialog | None = None

        columns = QHBoxLayout()
        columns.setSpacing(18)
        self.page_layout.addLayout(columns, 1)
        columns.addWidget(self._build_source_card(), 1)
        columns.addWidget(self._build_result_card(), 1)
        self._configure_tab_order()
        self._update_controls()
        self.preprocessing_panel.set_source_available(False)

    def _build_source_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addWidget(self._title("Source preview"))

        self.preview_tabs = QTabWidget()
        self.preview = ImagePreview()
        self.processed_preview = ImagePreview()
        self.preview_tabs.addTab(self.preview, "Original")
        self.preview_tabs.addTab(self.processed_preview, "Processed")
        self.preview_tabs.setTabEnabled(1, False)
        layout.addWidget(self.preview_tabs, 1)
        self.source_status = QLabel(
            "Drop an image here, open a file, or paste an image from the clipboard."
        )
        self.source_status.setObjectName("mutedLabel")
        self.source_status.setWordWrap(True)
        layout.addWidget(self.source_status)
        self.metadata = QLabel("No source selected")
        self.metadata.setObjectName("mutedLabel")
        layout.addWidget(self.metadata)
        self.preprocessing_panel = PreprocessingPanel()
        layout.addWidget(self.preprocessing_panel)

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
        self.open_button.setShortcut("Ctrl+O")
        self.open_button.clicked.connect(self._choose_image)
        self.paste_button = QPushButton("Paste")
        self.paste_button.setShortcut("Ctrl+V")
        self.paste_button.clicked.connect(self.paste_requested)
        self.capture_button = QPushButton("Capture")
        self.capture_button.setToolTip("Select a screen region (Ctrl+Shift+X)")
        self.capture_button.clicked.connect(self.capture_requested)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.source_cleared)
        for button in (
            self.open_button,
            self.paste_button,
            self.capture_button,
            self.clear_button,
        ):
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

        options = QGridLayout()
        options.setHorizontalSpacing(10)
        options.setVerticalSpacing(6)
        self.language_selector = QComboBox()
        self.language_selector.setAccessibleName("Recognition language")
        self.language_selector.addItem("English", "en")
        self.language_selector.addItem("Arabic", "ar")
        self.language_selector.addItem("English + Arabic", "en_ar")
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
        options.addWidget(QLabel("Language"), 0, 0)
        options.addWidget(self.language_selector, 1, 0)
        options.addWidget(QLabel("Reading mode"), 2, 0)
        options.addWidget(self.mode_selector, 3, 0)
        options.addWidget(QLabel("Minimum confidence"), 4, 0)
        options.addWidget(self.confidence_selector, 5, 0)
        options.setColumnStretch(0, 1)
        layout.addLayout(options)

        self.result_editor = QPlainTextEdit()
        self.result_editor.setPlaceholderText("Recognized text will appear here.")
        self.result_editor.setAccessibleName("Recognized text editor")
        self.result_editor.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        layout.addWidget(self.result_editor, 1)

        self.result_status = QLabel("Ready for a source image")
        self.result_status.setObjectName("mutedLabel")
        self.result_status.setAccessibleName("Recognition status")
        self.result_status.setWordWrap(True)
        layout.addWidget(self.result_status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setAccessibleName("Recognition progress")
        self.progress.setFormat("Recognizing text locally: %p%")
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        edit_actions = QGridLayout()
        self.undo_button = QPushButton("Undo")
        self.undo_button.setShortcut("Ctrl+Z")
        self.undo_button.clicked.connect(self.result_editor.undo)
        self.redo_button = QPushButton("Redo")
        self.redo_button.setShortcut("Ctrl+Y")
        self.redo_button.clicked.connect(self.result_editor.redo)
        self.find_button = QPushButton("Find / replace")
        self.find_button.setShortcut("Ctrl+F")
        self.find_button.clicked.connect(self._show_find_replace)
        self.wrap_button = QPushButton("Wrap lines")
        self.wrap_button.setCheckable(True)
        self.wrap_button.setChecked(True)
        self.wrap_button.clicked.connect(self._toggle_line_wrap)
        self.cleanup_button = QPushButton("Clean up")
        cleanup_menu = QMenu(self.cleanup_button)
        for label, action_name in (
            ("Normalize whitespace", "normalize_whitespace"),
            ("Remove duplicate blank lines", "remove_duplicate_blank_lines"),
            ("Join hyphenated line breaks", "join_hyphenated_linebreaks"),
        ):
            action = QAction(label, cleanup_menu)
            action.triggered.connect(
                lambda checked=False, name=action_name: self.cleanup_requested.emit(name)
            )
            cleanup_menu.addAction(action)
        self.cleanup_button.setMenu(cleanup_menu)
        edit_actions.addWidget(self.undo_button, 0, 0)
        edit_actions.addWidget(self.redo_button, 0, 1)
        edit_actions.addWidget(self.find_button, 1, 0, 1, 2)
        edit_actions.addWidget(self.wrap_button, 2, 0)
        edit_actions.addWidget(self.cleanup_button, 2, 1)
        for column in range(2):
            edit_actions.setColumnStretch(column, 1)
        layout.addLayout(edit_actions)

        actions = QGridLayout()
        self.copy_button = QPushButton("Copy text")
        self.copy_button.setAccessibleName("Copy recognized text")
        self.copy_button.setToolTip("Copy the currently edited recognized text")
        self.copy_button.setShortcut("Ctrl+Shift+C")
        self.copy_button.clicked.connect(self.copy_requested)
        self.select_all_button = QPushButton("Select all")
        self.select_all_button.clicked.connect(self.result_editor.selectAll)
        self.clear_result_button = QPushButton("Clear text")
        self.clear_result_button.clicked.connect(self.result_editor.clear)
        self.save_button = QPushButton("Save")
        self.save_button.setShortcut("Ctrl+S")
        self.save_button.clicked.connect(self.save_requested)
        self.export_button = QPushButton("Export")
        self.export_button.setShortcut("Ctrl+Shift+S")
        self.export_button.clicked.connect(self.export_requested)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_requested)
        self.extract_button = QPushButton("Extract text")
        self.extract_button.setObjectName("primaryButton")
        self.extract_button.setShortcut("Ctrl+Return")
        self.extract_button.clicked.connect(self._request_extraction)
        actions.addWidget(self.copy_button, 0, 0)
        actions.addWidget(self.extract_button, 0, 1)
        actions.addWidget(self.select_all_button, 1, 0)
        actions.addWidget(self.clear_result_button, 1, 1)
        actions.addWidget(self.save_button, 2, 0)
        actions.addWidget(self.export_button, 2, 1)
        actions.addWidget(self.cancel_button, 3, 0, 1, 2)
        for column in range(2):
            actions.setColumnStretch(column, 1)
        layout.addLayout(actions)
        self.result_editor.textChanged.connect(self._update_controls)
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
        self.clear_processed_document()
        self._refresh_label_styles(self.source_status)
        self._update_controls()

    def set_source_available(self, available: bool) -> None:
        self._has_source = available
        self.preprocessing_panel.set_source_available(available)
        self._update_controls()

    def display_processed_document(self, document: ImageDocument) -> None:
        """Show a derived preview while retaining the original tab."""
        self.processed_preview.set_document(document)
        self.preview_tabs.setTabEnabled(1, True)
        self.preview_tabs.setCurrentIndex(1)

    def clear_processed_document(self) -> None:
        """Discard only derived pixels and return to the original preview."""
        self.processed_preview.clear_document()
        self.preview_tabs.setCurrentIndex(0)
        self.preview_tabs.setTabEnabled(1, False)

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
        direction = (
            Qt.LayoutDirection.RightToLeft
            if result.recognition_language in {"ar", "en_ar"}
            else Qt.LayoutDirection.LeftToRight
        )
        self.result_editor.setLayoutDirection(direction)
        text_options = self.result_editor.document().defaultTextOption()
        text_options.setTextDirection(direction)
        self.result_editor.document().setDefaultTextOption(text_options)
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

    def set_capture_shortcut(self, shortcut: str) -> None:
        """Show the active global capture shortcut beside the capture action."""
        self.capture_button.setToolTip(f"Select a screen region ({shortcut})")

    def _show_find_replace(self) -> None:
        if self._find_dialog is None:
            self._find_dialog = FindReplaceDialog(self.result_editor, self)
        selected = self.result_editor.textCursor().selectedText()
        if selected:
            self._find_dialog.find_editor.setText(selected)
        self._find_dialog.show()
        self._find_dialog.raise_()
        self._find_dialog.activateWindow()
        self._find_dialog.find_editor.setFocus()

    def _toggle_line_wrap(self, enabled: bool) -> None:
        mode = (
            QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere
            if enabled
            else QTextOption.WrapMode.NoWrap
        )
        self.result_editor.setWordWrapMode(mode)

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
        self.capture_button.setEnabled(not self._ocr_busy)
        self.extract_button.setEnabled(self._has_source and not self._ocr_busy)
        self.cancel_button.setEnabled(self._ocr_busy)
        self.copy_button.setEnabled(bool(self.result_editor.toPlainText()) and not self._ocr_busy)
        self.select_all_button.setEnabled(bool(self.result_editor.toPlainText()))
        self.clear_result_button.setEnabled(
            bool(self.result_editor.toPlainText()) and not self._ocr_busy
        )
        self.save_button.setEnabled(bool(self.result_editor.toPlainText()) and not self._ocr_busy)
        self.export_button.setEnabled(bool(self.result_editor.toPlainText()) and not self._ocr_busy)
        self.find_button.setEnabled(bool(self.result_editor.toPlainText()))
        self.cleanup_button.setEnabled(
            bool(self.result_editor.toPlainText()) and not self._ocr_busy
        )
        self.undo_button.setEnabled(self.result_editor.document().isUndoAvailable())
        self.redo_button.setEnabled(self.result_editor.document().isRedoAvailable())
        self.language_selector.setEnabled(not self._ocr_busy)
        self.mode_selector.setEnabled(not self._ocr_busy)
        self.confidence_selector.setEnabled(not self._ocr_busy)

    def _configure_tab_order(self) -> None:
        controls = (
            self.open_button,
            self.paste_button,
            self.capture_button,
            self.clear_button,
            self.preview_tabs,
            self.language_selector,
            self.mode_selector,
            self.confidence_selector,
            self.result_editor,
            self.undo_button,
            self.redo_button,
            self.find_button,
            self.wrap_button,
            self.cleanup_button,
            self.copy_button,
            self.select_all_button,
            self.clear_result_button,
            self.save_button,
            self.export_button,
            self.cancel_button,
            self.extract_button,
        )
        for current, following in pairwise(controls):
            QWidget.setTabOrder(current, following)

    @staticmethod
    def _refresh_label_styles(label: QLabel) -> None:
        label.style().unpolish(label)
        label.style().polish(label)

    @staticmethod
    def _title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("cardTitle")
        return label
