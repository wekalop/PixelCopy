from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.app import ApplicationController
from pixelcopy.config.settings import SettingsStore
from pixelcopy.database.connection import connect_database
from pixelcopy.database.repositories import HistoryRepository
from pixelcopy.database.schema import migrate
from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCRResult
from pixelcopy.ocr.fake_engine import FakeOCREngine


def test_history_requires_opt_in_then_supports_search_copy_and_delete(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    connection = connect_database(tmp_path / "history.sqlite3")
    migrate(connection)
    repository = HistoryRepository(connection, tmp_path / "thumbs")
    controller = ApplicationController(
        qapp,
        SettingsStore(tmp_path / "settings.json"),
        FakeOCREngine(),
        repository,
    )
    qtbot.addWidget(controller.window)
    result = OCRResult(
        "private receipt text",
        (OCRBlock("private receipt text", BoundingBox(0, 0, 50, 10), 0.9),),
        "en",
        0.1,
        "Fake OCR",
        2,
        2,
    )
    image = ImageDocument("receipt.png", "PNG", 2, 2, "RGBA", bytes(16))
    controller.window.extract_page.display_ocr_result(result)
    assert controller.history_controller is not None
    controller.history_controller.set_latest((result, image))

    controller.history_controller.save_latest()
    assert repository.list() == ()

    controller.change_history(True)
    controller.history_controller.save_latest()
    assert len(repository.list()) == 1

    controller.window.history_page.search.setText("receipt")
    assert controller.window.history_page.items.count() == 1
    controller.history_controller.copy()
    assert qapp.clipboard().text() == "private receipt text"
    controller.history_controller.delete_selected()
    assert repository.list() == ()
