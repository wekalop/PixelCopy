from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.app import ApplicationController
from pixelcopy.config.settings import SettingsStore
from pixelcopy.domain.export import ExportFormat
from pixelcopy.domain.images import ImageDocument
from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCRResult
from pixelcopy.ocr.fake_engine import FakeOCREngine


def test_dialog_free_export_uses_edited_text(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    controller = ApplicationController(
        qapp, SettingsStore(tmp_path / "settings.json"), FakeOCREngine()
    )
    qtbot.addWidget(controller.window)
    result = OCRResult(
        "original",
        (OCRBlock("original", BoundingBox(0, 0, 20, 10), 0.9),),
        "en",
        0.1,
        "Fake",
        2,
        2,
    )
    image = ImageDocument("source.png", "PNG", 2, 2, "RGBA", bytes(16))
    controller.export_controller.set_latest((result, image))
    controller.window.extract_page.result_editor.setPlainText("edited")

    destination = tmp_path / "export.txt"
    controller.export_controller.export_to(destination, ExportFormat.TEXT)

    assert destination.read_text(encoding="utf-8") == "edited"
