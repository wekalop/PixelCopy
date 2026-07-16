"""Milestone 1 appearance settings page."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from pixelcopy.ui.pages.base import Page


class SettingsPage(Page):
    """User preferences available in the foundation milestone."""

    theme_changed = Signal(str)
    shortcut_changed = Signal(str)
    history_changed = Signal(bool)

    def __init__(
        self,
        theme: str,
        shortcut: str = "Ctrl+Shift+X",
        save_history: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            "Settings",
            "Choose the application appearance. OCR and workflow preferences "
            "arrive with their features.",
            parent,
        )
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        title = QLabel("Appearance")
        title.setObjectName("cardTitle")
        description = QLabel("Theme changes apply immediately and persist for your next launch.")
        description.setObjectName("mutedLabel")
        description.setWordWrap(True)
        card_layout.addWidget(title)
        card_layout.addWidget(description)

        form = QFormLayout()
        form.setSpacing(14)
        self.theme_selector = QComboBox()
        self.theme_selector.setObjectName("themeSelector")
        self.theme_selector.setAccessibleName("Application theme")
        self.theme_selector.addItem("Light", "light")
        self.theme_selector.addItem("Dark", "dark")
        index = self.theme_selector.findData(theme)
        self.theme_selector.setCurrentIndex(max(0, index))
        self.theme_selector.currentIndexChanged.connect(self._emit_theme)
        form.addRow("Theme", self.theme_selector)
        self.shortcut_editor = QLineEdit(shortcut)
        self.shortcut_editor.setAccessibleName("Global capture shortcut")
        self.shortcut_editor.setToolTip("Example: Ctrl+Shift+X")
        self.shortcut_editor.editingFinished.connect(self._emit_shortcut)
        form.addRow("Capture shortcut", self.shortcut_editor)
        self.history_checkbox = QCheckBox("Save extraction history locally")
        self.history_checkbox.setChecked(save_history)
        self.history_checkbox.toggled.connect(self.history_changed)
        form.addRow("History", self.history_checkbox)
        card_layout.addLayout(form)
        card_layout.addStretch(1)
        self.page_layout.addWidget(card, 1)

    def _emit_theme(self) -> None:
        theme = self.theme_selector.currentData()
        if isinstance(theme, str):
            self.theme_changed.emit(theme)

    def _emit_shortcut(self) -> None:
        self.shortcut_changed.emit(self.shortcut_editor.text().strip())
