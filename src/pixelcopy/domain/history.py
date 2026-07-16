"""Local extraction history models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class HistoryItem:
    id: str
    title: str
    source_type: str
    source_name: str
    text: str
    metadata_json: str
    created_at: datetime
    updated_at: datetime
    language: str
    engine: str
    average_confidence: float
    duration_seconds: float
    thumbnail_path: Path | None
    favorite: bool
    page_count: int
