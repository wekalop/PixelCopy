"""Shared exporter protocol and destination checks."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from pixelcopy.domain.exceptions import PixelCopyError
from pixelcopy.domain.export import ExportPayload


class ExportError(PixelCopyError):
    pass


class Exporter(Protocol):
    def export(self, payload: ExportPayload, destination: Path) -> None: ...


def validate_destination(destination: Path) -> None:
    if destination.exists():
        raise ExportError(f"'{destination.name}' already exists. Choose a new filename.")
    if not destination.parent.is_dir():
        raise ExportError("The selected export folder does not exist.")
