from __future__ import annotations

from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from pixelcopy.domain.ocr import BoundingBox, OCRBlock, OCRResult
from pixelcopy.ui.pages.extract import ExtractPage


def test_arabic_result_uses_rtl_editor_direction(qtbot: QtBot) -> None:
    page = ExtractPage()
    qtbot.addWidget(page)
    result = OCRResult(
        "مرحبا بالعالم",
        (OCRBlock("مرحبا بالعالم", BoundingBox(0, 0, 100, 20), 0.9),),
        "ar",
        0.1,
        "Fake OCR",
        100,
        20,
    )

    page.display_ocr_result(result)

    assert page.result_editor.layoutDirection() is Qt.LayoutDirection.RightToLeft
    assert page.result_editor.toPlainText() == "مرحبا بالعالم"


def test_language_selector_offers_english_arabic_and_mixed(qtbot: QtBot) -> None:
    page = ExtractPage()
    qtbot.addWidget(page)

    assert [page.language_selector.itemData(index) for index in range(3)] == [
        "en",
        "ar",
        "en_ar",
    ]
