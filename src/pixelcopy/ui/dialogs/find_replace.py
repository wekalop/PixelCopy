"""Keyboard-friendly find and replace dialog for the results editor."""

from __future__ import annotations

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class FindReplaceDialog(QDialog):
    """Find or replace literal text in an associated plain-text editor."""

    def __init__(self, editor: QPlainTextEdit, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._editor = editor
        self.setWindowTitle("Find and replace")
        self.setModal(False)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.find_editor = QLineEdit()
        self.find_editor.setAccessibleName("Text to find")
        self.find_editor.setClearButtonEnabled(True)
        self.replace_editor = QLineEdit()
        self.replace_editor.setAccessibleName("Replacement text")
        self.replace_editor.setClearButtonEnabled(True)
        form.addRow("Find", self.find_editor)
        form.addRow("Replace with", self.replace_editor)
        layout.addLayout(form)

        self.status = QLabel("Enter text to search the current result.")
        self.status.setWordWrap(True)
        self.status.setAccessibleName("Find status")
        layout.addWidget(self.status)

        actions = QHBoxLayout()
        self.find_button = QPushButton("Find next")
        self.find_button.setDefault(True)
        self.find_button.clicked.connect(self.find_next)
        self.replace_button = QPushButton("Replace")
        self.replace_button.clicked.connect(self.replace_current)
        self.replace_all_button = QPushButton("Replace all")
        self.replace_all_button.clicked.connect(self.replace_all)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        for button in (
            self.find_button,
            self.replace_button,
            self.replace_all_button,
            close_button,
        ):
            actions.addWidget(button)
        layout.addLayout(actions)

    def find_next(self) -> bool:
        """Select the next literal match, wrapping once at the document end."""
        needle = self.find_editor.text()
        if not needle:
            self.status.setText("Enter text to find.")
            return False
        if not self._editor.find(needle):
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self._editor.setTextCursor(cursor)
            if not self._editor.find(needle):
                self.status.setText("No matches found.")
                return False
        self.status.setText("Match selected.")
        return True

    def replace_current(self) -> None:
        """Replace the current matching selection and move to the next match."""
        cursor = self._editor.textCursor()
        if cursor.selectedText() != self.find_editor.text() and not self.find_next():
            return
        cursor = self._editor.textCursor()
        cursor.insertText(self.replace_editor.text())
        self.find_next()

    def replace_all(self) -> int:
        """Replace every literal match as one undoable edit block."""
        needle = self.find_editor.text()
        if not needle:
            self.status.setText("Enter text to find.")
            return 0
        text = self._editor.toPlainText()
        count = text.count(needle)
        if count:
            cursor = self._editor.textCursor()
            cursor.beginEditBlock()
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.insertText(text.replace(needle, self.replace_editor.text()))
            cursor.endEditBlock()
        self.status.setText(f"Replaced {count} match(es).")
        return count
