"""Idempotent history schema migration."""

from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 1


def migrate(connection: sqlite3.Connection) -> None:
    """Create or upgrade the local schema transactionally."""
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS history (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_name TEXT NOT NULL,
            text TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            language TEXT NOT NULL,
            engine TEXT NOT NULL,
            average_confidence REAL NOT NULL,
            duration_seconds REAL NOT NULL,
            thumbnail_path TEXT,
            favorite INTEGER NOT NULL DEFAULT 0 CHECK (favorite IN (0, 1)),
            page_count INTEGER NOT NULL DEFAULT 1
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS history_fts USING fts5(
            title, text, content='history', content_rowid='rowid'
        );
        CREATE TRIGGER IF NOT EXISTS history_ai AFTER INSERT ON history BEGIN
            INSERT INTO history_fts(rowid, title, text) VALUES (new.rowid, new.title, new.text);
        END;
        CREATE TRIGGER IF NOT EXISTS history_ad AFTER DELETE ON history BEGIN
            INSERT INTO history_fts(history_fts, rowid, title, text)
            VALUES ('delete', old.rowid, old.title, old.text);
        END;
        CREATE TRIGGER IF NOT EXISTS history_au AFTER UPDATE ON history BEGIN
            INSERT INTO history_fts(history_fts, rowid, title, text)
            VALUES ('delete', old.rowid, old.title, old.text);
            INSERT INTO history_fts(rowid, title, text) VALUES (new.rowid, new.title, new.text);
        END;
        """
    )
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    connection.commit()
