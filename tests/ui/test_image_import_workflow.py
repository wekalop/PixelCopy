from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from pixelcopy.app import ApplicationController
from pixelcopy.config.settings import SettingsStore


def write_test_image(path: Path) -> None:
    buffer = io.BytesIO()
    Image.new("RGB", (12, 7), "blue").save(buffer, format="PNG")
    path.write_bytes(buffer.getvalue())


def test_file_import_displays_preview_metadata_and_clear(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    path = tmp_path / "sample.data"
    write_test_image(path)
    controller = ApplicationController(qapp, SettingsStore(tmp_path / "settings.json"))
    qtbot.addWidget(controller.window)

    controller.image_import_controller.import_file(path)

    page = controller.window.extract_page
    assert page.source_status.text() == "sample.data"
    assert "PNG · 12 x 7 px" in page.metadata.text()
    assert page.clear_button.isEnabled()

    qtbot.mouseClick(page.clear_button, Qt.MouseButton.LeftButton)

    assert page.metadata.text() == "No source selected"
    assert not page.clear_button.isEnabled()


def test_clipboard_image_uses_same_import_workflow(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    controller = ApplicationController(qapp, SettingsStore(tmp_path / "settings.json"))
    qtbot.addWidget(controller.window)
    image = QImage(9, 6, QImage.Format.Format_RGB32)
    image.fill(QColor("red"))
    qapp.clipboard().setImage(image)

    controller.image_import_controller.import_clipboard()

    page = controller.window.extract_page
    assert page.source_status.text() == "Clipboard image"
    assert "9 x 6 px" in page.metadata.text()


def test_invalid_import_shows_error_without_crashing(
    qtbot: QtBot, qapp: QApplication, tmp_path: Path
) -> None:
    invalid = tmp_path / "broken.png"
    invalid.write_bytes(b"broken")
    controller = ApplicationController(qapp, SettingsStore(tmp_path / "settings.json"))
    qtbot.addWidget(controller.window)

    controller.image_import_controller.import_file(invalid)

    assert "could not open" in controller.window.extract_page.source_status.text()
    assert controller.window.extract_page.source_status.objectName() == "errorLabel"
