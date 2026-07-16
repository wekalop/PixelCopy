from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from pixelcopy.config.settings import ApplicationSettings, SettingsStore


def test_missing_settings_use_privacy_conscious_defaults(tmp_path: Path) -> None:
    settings = SettingsStore(tmp_path / "settings.json").load()

    assert settings.theme == "light"
    assert settings.save_history is False
    assert settings.save_thumbnails is False


def test_malformed_settings_recover_without_overwriting_source(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    malformed = "{not-json"
    path.write_text(malformed, encoding="utf-8")

    settings = SettingsStore(path).load()

    assert settings == ApplicationSettings()
    assert path.read_text(encoding="utf-8") == malformed


def test_invalid_fields_fall_back_independently(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "theme": "dark",
                "confidence_threshold": 4,
                "pdf_render_resolution": "high",
                "save_history": True,
            }
        ),
        encoding="utf-8",
    )

    settings = SettingsStore(path).load()

    assert settings.theme == "dark"
    assert settings.confidence_threshold == 0.5
    assert settings.pdf_render_resolution == 300
    assert settings.save_history is True


def test_settings_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    expected = replace(ApplicationSettings(), theme="dark", auto_copy=True)

    store.save(expected)

    assert store.load() == expected
    assert not path.with_suffix(".json.tmp").exists()
