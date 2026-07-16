"""SQLite extraction history repository."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pixelcopy.domain.history import HistoryItem


class HistoryRepository:
    def __init__(self, connection: sqlite3.Connection, thumbnail_dir: Path) -> None:
        self._connection = connection
        self._thumbnail_dir = thumbnail_dir.resolve()

    def add(
        self,
        title: str,
        source_type: str,
        source_name: str,
        text: str,
        metadata_json: str,
        language: str,
        engine: str,
        average_confidence: float,
        duration_seconds: float,
        page_count: int = 1,
        thumbnail_path: Path | None = None,
    ) -> HistoryItem:
        now = datetime.now(UTC)
        item = HistoryItem(
            str(uuid4()),
            title.strip() or "Untitled extraction",
            source_type,
            source_name,
            text,
            metadata_json,
            now,
            now,
            language,
            engine,
            average_confidence,
            duration_seconds,
            thumbnail_path,
            False,
            page_count,
        )
        self._connection.execute(
            """INSERT INTO history VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            self._values(item),
        )
        self._connection.commit()
        return item

    def list(self, query: str = "", favorites_only: bool = False) -> tuple[HistoryItem, ...]:
        parameters: list[object] = []
        if query.strip():
            sql = """SELECT h.* FROM history h JOIN history_fts f ON f.rowid=h.rowid
                     WHERE history_fts MATCH ?"""
            parameters.append(query.strip())
        else:
            sql = "SELECT h.* FROM history h WHERE 1=1"
        if favorites_only:
            sql += " AND h.favorite = 1"
        sql += " ORDER BY h.updated_at DESC"
        return tuple(self._from_row(row) for row in self._connection.execute(sql, parameters))

    def rename(self, item_id: str, title: str) -> None:
        self._connection.execute(
            "UPDATE history SET title=?, updated_at=? WHERE id=?",
            (
                title.strip() or "Untitled extraction",
                datetime.now(UTC).isoformat(),
                item_id,
            ),
        )
        self._connection.commit()

    def set_favorite(self, item_id: str, favorite: bool) -> None:
        self._connection.execute(
            "UPDATE history SET favorite=?, updated_at=? WHERE id=?",
            (int(favorite), datetime.now(UTC).isoformat(), item_id),
        )
        self._connection.commit()

    def delete(self, item_ids: tuple[str, ...]) -> None:
        for item_id in item_ids:
            row = self._connection.execute(
                "SELECT thumbnail_path FROM history WHERE id=?", (item_id,)
            ).fetchone()
            self._connection.execute("DELETE FROM history WHERE id=?", (item_id,))
            if row is not None and row["thumbnail_path"]:
                self._delete_owned_thumbnail(Path(str(row["thumbnail_path"])))
        self._connection.commit()

    def clear(self) -> None:
        self.delete(tuple(item.id for item in self.list()))

    def _delete_owned_thumbnail(self, path: Path) -> None:
        resolved = path.resolve()
        if resolved.parent == self._thumbnail_dir and resolved.is_file():
            resolved.unlink()

    @staticmethod
    def _values(item: HistoryItem) -> tuple[object, ...]:
        return (
            item.id,
            item.title,
            item.source_type,
            item.source_name,
            item.text,
            item.metadata_json,
            item.created_at.isoformat(),
            item.updated_at.isoformat(),
            item.language,
            item.engine,
            item.average_confidence,
            item.duration_seconds,
            str(item.thumbnail_path) if item.thumbnail_path else None,
            int(item.favorite),
            item.page_count,
        )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> HistoryItem:
        thumbnail = row["thumbnail_path"]
        return HistoryItem(
            str(row["id"]),
            str(row["title"]),
            str(row["source_type"]),
            str(row["source_name"]),
            str(row["text"]),
            str(row["metadata_json"]),
            datetime.fromisoformat(str(row["created_at"])),
            datetime.fromisoformat(str(row["updated_at"])),
            str(row["language"]),
            str(row["engine"]),
            float(row["average_confidence"]),
            float(row["duration_seconds"]),
            Path(str(thumbnail)) if thumbnail else None,
            bool(row["favorite"]),
            int(row["page_count"]),
        )
