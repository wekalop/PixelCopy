"""Privacy-gated extraction history coordination."""

from __future__ import annotations

import json
from dataclasses import asdict

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication

from pixelcopy.database.repositories import HistoryRepository
from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import OCRResult
from pixelcopy.ui.pages.extract import ExtractPage
from pixelcopy.ui.pages.history import HistoryPage


class HistoryController(QObject):
    def __init__(
        self,
        application: QApplication,
        history_page: HistoryPage,
        extract_page: ExtractPage,
        repository: HistoryRepository,
        enabled: bool,
    ) -> None:
        super().__init__(history_page)
        self._application = application
        self._page = history_page
        self._extract_page = extract_page
        self._repository = repository
        self._enabled = enabled
        self._latest: tuple[OCRResult, ImageDocument] | None = None
        history_page.search_changed.connect(self.refresh)
        history_page.copy_requested.connect(self.copy)
        history_page.favorite_requested.connect(self.toggle_favorite)
        history_page.delete_requested.connect(self.delete_selected)
        history_page.clear_requested.connect(self.clear)
        extract_page.save_requested.connect(self.save_latest)
        self.refresh()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    @Slot(object)
    def set_latest(self, value: object) -> None:
        if (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], OCRResult)
            and isinstance(value[1], ImageDocument)
        ):
            self._latest = (value[0], value[1])

    @Slot(str)
    def refresh(self, query: str = "") -> None:
        self._page.display_items(self._repository.list(query))

    @Slot()
    def save_latest(self) -> None:
        if not self._enabled:
            self._extract_page.display_ocr_error(
                "History is disabled. Enable it in Settings to save extracted text."
            )
            return
        if self._latest is None:
            return
        result, image = self._latest
        edited_text = self._extract_page.result_editor.toPlainText()
        metadata = json.dumps(
            {"blocks": [asdict(block) for block in result.blocks], "warnings": result.warnings},
            ensure_ascii=False,
        )
        self._repository.add(
            image.source_name,
            "image",
            image.source_name,
            edited_text,
            metadata,
            result.recognition_language,
            result.engine_name,
            result.average_confidence,
            result.duration_seconds,
        )
        self.refresh()

    @Slot()
    def copy(self) -> None:
        record = self._page.current_record()
        if record is not None:
            self._application.clipboard().setText(record.text)

    @Slot()
    def toggle_favorite(self) -> None:
        record = self._page.current_record()
        if record is not None:
            self._repository.set_favorite(record.id, not record.favorite)
            self.refresh(self._page.search.text())

    @Slot()
    def delete_selected(self) -> None:
        self._repository.delete(self._page.selected_ids())
        self.refresh(self._page.search.text())

    @Slot()
    def clear(self) -> None:
        self._repository.clear()
        self.refresh()
