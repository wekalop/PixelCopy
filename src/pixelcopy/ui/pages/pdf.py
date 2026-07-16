"""Scanned PDF selection and extraction page."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.pdf import PDFBatchResult, PDFDocumentInfo, PDFPageFailure
from pixelcopy.ui.pages.base import Page


class PDFPage(Page):
    file_selected = Signal(Path)
    extract_requested = Signal(str, int, str)
    cancel_requested = Signal()
    retry_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("PDF", "Render and recognize selected scanned pages locally.", parent)
        top = QHBoxLayout()
        self.open_button = QPushButton("Open PDF")
        self.open_button.setObjectName("primaryButton")
        self.open_button.clicked.connect(self._choose_file)
        self.info = QLabel("No PDF selected")
        self.info.setObjectName("mutedLabel")
        top.addWidget(self.open_button)
        top.addWidget(self.info, 1)
        self.page_layout.addLayout(top)

        content = QHBoxLayout()
        left = QVBoxLayout()
        self.thumbnails = QListWidget()
        self.thumbnails.setIconSize(QSize(80, 110))
        left.addWidget(self.thumbnails, 1)
        selection = QHBoxLayout()
        self.range_editor = QLineEdit("all")
        self.range_editor.setPlaceholderText("Pages: all or 1-3,5")
        self.dpi = QSpinBox()
        self.dpi.setRange(72, 600)
        self.dpi.setValue(300)
        selection.addWidget(self.range_editor)
        selection.addWidget(self.dpi)
        left.addLayout(selection)
        content.addLayout(left, 1)

        right = QVBoxLayout()
        self.result_editor = QPlainTextEdit()
        self.result_editor.setPlaceholderText("Combined page text will appear here.")
        right.addWidget(self.result_editor, 1)
        self.failures = QListWidget()
        self.failures.setVisible(False)
        right.addWidget(self.failures)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        right.addWidget(self.progress)
        actions = QHBoxLayout()
        self.extract_button = QPushButton("Extract selected pages")
        self.extract_button.setObjectName("primaryButton")
        self.extract_button.clicked.connect(
            lambda: self.extract_requested.emit(self.range_editor.text(), self.dpi.value(), "en")
        )
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_requested)
        self.retry_button = QPushButton("Retry failed pages")
        self.retry_button.clicked.connect(self.retry_requested)
        actions.addWidget(self.retry_button)
        actions.addStretch(1)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.extract_button)
        right.addLayout(actions)
        content.addLayout(right, 2)
        self.page_layout.addLayout(content, 1)
        self.set_busy(False)
        self.extract_button.setEnabled(False)

    def display_info(self, info: PDFDocumentInfo) -> None:
        self.info.setText(f"{info.title} · {info.page_count} page(s)")
        self.thumbnails.clear()
        for index in range(info.page_count):
            self.thumbnails.addItem(QListWidgetItem(f"Page {index + 1}"))
        self.extract_button.setEnabled(True)

    def display_thumbnail(self, page_index: int, document: ImageDocument) -> None:
        image = QImage(
            document.rgba_pixels,
            document.width,
            document.height,
            document.width * 4,
            QImage.Format.Format_RGBA8888,
        ).copy()
        item = self.thumbnails.item(page_index)
        if item is not None:
            item.setIcon(QIcon(QPixmap.fromImage(image)))

    def set_busy(self, busy: bool) -> None:
        self.progress.setVisible(busy)
        self.cancel_button.setEnabled(busy)
        self.open_button.setEnabled(not busy)
        self.range_editor.setEnabled(not busy)
        self.dpi.setEnabled(not busy)
        if busy:
            self.progress.setValue(0)

    def set_progress(self, current: int, total: int) -> None:
        self.progress.setRange(0, max(1, total))
        self.progress.setValue(current)

    def add_failure(self, failure: PDFPageFailure) -> None:
        self.failures.setVisible(True)
        self.failures.addItem(f"Page {failure.page_number}: {failure.message}")

    def display_result(self, result: PDFBatchResult) -> None:
        self.result_editor.setPlainText(result.combined_text)
        self.retry_button.setEnabled(bool(result.failures))

    def display_error(self, message: str) -> None:
        self.info.setText(message)
        self.info.setObjectName("errorLabel")

    def _choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open scanned PDF", "", "PDF (*.pdf)")
        if path:
            self.file_selected.emit(Path(path))
