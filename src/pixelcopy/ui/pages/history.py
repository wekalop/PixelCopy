"""Searchable local extraction history page."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QWidget,
)

from pixelcopy.domain.history import HistoryItem
from pixelcopy.ui.pages.base import Page


class HistoryPage(Page):
    search_changed = Signal(str)
    copy_requested = Signal()
    favorite_requested = Signal()
    delete_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("History", "Search and manage optional local extractions.", parent)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search extracted text and titles")
        self.search.textChanged.connect(self.search_changed)
        self.page_layout.addWidget(self.search)

        content = QHBoxLayout()
        self.items = QListWidget()
        self.items.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.items.currentItemChanged.connect(self._selection_changed)
        content.addWidget(self.items, 1)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        content.addWidget(self.preview, 2)
        self.page_layout.addLayout(content, 1)

        actions = QHBoxLayout()
        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_requested)
        self.favorite_button = QPushButton("Toggle favorite")
        self.favorite_button.clicked.connect(self.favorite_requested)
        self.delete_button = QPushButton("Delete selected")
        self.delete_button.clicked.connect(self.delete_requested)
        self.clear_button = QPushButton("Clear history")
        self.clear_button.clicked.connect(self.clear_requested)
        for button in (
            self.copy_button,
            self.favorite_button,
            self.delete_button,
            self.clear_button,
        ):
            actions.addWidget(button)
        actions.addStretch(1)
        self.page_layout.addLayout(actions)
        self._records: dict[str, HistoryItem] = {}

    def display_items(self, records: tuple[HistoryItem, ...]) -> None:
        self._records = {record.id: record for record in records}
        self.items.clear()
        for record in records:
            marker = "★ " if record.favorite else ""
            item = QListWidgetItem(f"{marker}{record.title}\n{record.source_name}")
            item.setData(Qt.ItemDataRole.UserRole, record.id)
            self.items.addItem(item)
        if records:
            self.items.setCurrentRow(0)
        else:
            self.preview.clear()

    def selected_ids(self) -> tuple[str, ...]:
        return tuple(
            str(item.data(Qt.ItemDataRole.UserRole)) for item in self.items.selectedItems()
        )

    def current_record(self) -> HistoryItem | None:
        item = self.items.currentItem()
        if item is None:
            return None
        return self._records.get(str(item.data(Qt.ItemDataRole.UserRole)))

    def _selection_changed(self, current: QListWidgetItem | None) -> None:
        if current is None:
            self.preview.clear()
            return
        record = self._records.get(str(current.data(Qt.ItemDataRole.UserRole)))
        self.preview.setPlainText(record.text if record else "")
