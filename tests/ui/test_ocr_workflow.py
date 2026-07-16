from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.app import ApplicationController
from pixelcopy.config.settings import SettingsStore
from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCRResult
from pixelcopy.ocr.fake_engine import FakeOCREngine


def test_extract_runs_in_background_and_result_remains_editable(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    result = OCRResult(
        "hello world",
        (OCRBlock("hello world", BoundingBox(0, 0, 50, 10), 0.9),),
        "en",
        0.25,
        "Fake OCR",
        4,
        3,
    )
    controller = ApplicationController(
        qapp,
        SettingsStore(tmp_path / "settings.json"),
        FakeOCREngine(result),
    )
    qtbot.addWidget(controller.window)
    buffer = io.BytesIO()
    Image.new("RGB", (4, 3), "white").save(buffer, "PNG")
    image_path = tmp_path / "source.png"
    image_path.write_bytes(buffer.getvalue())
    controller.image_import_controller.import_file(image_path)

    qtbot.mouseClick(controller.window.extract_page.extract_button, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(
        lambda: controller.window.extract_page.result_editor.toPlainText() == "hello world"
    )

    page = controller.window.extract_page
    assert not page.result_editor.isReadOnly()
    assert "90% confidence" in page.result_status.text()
    page.result_editor.setPlainText("edited text")
    qtbot.mouseClick(page.copy_button, Qt.MouseButton.LeftButton)
    assert qapp.clipboard().text() == "edited text"
