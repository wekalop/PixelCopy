from __future__ import annotations

from pathlib import Path

from pixelcopy.database.connection import connect_database
from pixelcopy.database.repositories import HistoryRepository
from pixelcopy.database.schema import migrate


def repository(tmp_path: Path) -> HistoryRepository:
    connection = connect_database(tmp_path / "history.sqlite3")
    migrate(connection)
    return HistoryRepository(connection, tmp_path / "thumbs")


def test_add_search_favorite_rename_and_delete_thumbnail(tmp_path: Path) -> None:
    thumbnails = tmp_path / "thumbs"
    thumbnails.mkdir()
    thumbnail = thumbnails / "one.png"
    thumbnail.write_bytes(b"thumbnail")
    repo = repository(tmp_path)
    item = repo.add(
        "Receipt",
        "image",
        "receipt.png",
        "coffee total",
        "{}",
        "en",
        "Fake",
        0.9,
        0.1,
        thumbnail_path=thumbnail,
    )

    assert repo.list("coffee")[0].id == item.id
    repo.rename(item.id, "Cafe receipt")
    repo.set_favorite(item.id, True)
    assert repo.list(favorites_only=True)[0].title == "Cafe receipt"

    repo.delete((item.id,))
    assert repo.list() == ()
    assert not thumbnail.exists()


def test_delete_never_removes_thumbnail_outside_owned_directory(tmp_path: Path) -> None:
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"keep")
    repo = repository(tmp_path)
    item = repo.add(
        "Title", "image", "x.png", "text", "{}", "en", "Fake", 1, 0, thumbnail_path=outside
    )

    repo.delete((item.id,))

    assert outside.exists()
