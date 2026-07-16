from __future__ import annotations

from pathlib import Path

from pixelcopy.config.paths import AppPaths


def test_ensure_directories_creates_each_owned_directory(tmp_path: Path) -> None:
    paths = AppPaths(
        data_dir=tmp_path / "data",
        config_dir=tmp_path / "config",
        cache_dir=tmp_path / "cache",
        log_dir=tmp_path / "logs",
    )

    paths.ensure_directories()

    assert all(
        path.is_dir() for path in (paths.data_dir, paths.config_dir, paths.cache_dir, paths.log_dir)
    )
