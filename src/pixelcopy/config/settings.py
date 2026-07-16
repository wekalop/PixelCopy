"""Validated, local application settings persistence."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ApplicationSettings:
    """User preferences with privacy-conscious defaults."""

    theme: str = "light"
    default_ocr_language: str = "en"
    ocr_engine: str = "paddle"
    confidence_threshold: float = 0.5
    automatic_enhancement: bool = True
    preprocessing_profile: str = "automatic"
    auto_copy: bool = False
    save_history: bool = False
    save_thumbnails: bool = False
    default_export_directory: str = ""
    global_shortcut: str = "Ctrl+Shift+X"
    pdf_render_resolution: int = 300
    start_minimized: bool = False
    logging_level: str = "INFO"

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> ApplicationSettings:
        """Recover valid values while replacing malformed fields with defaults."""
        defaults = cls()
        return cls(
            theme=_choice(values.get("theme"), {"light", "dark"}, defaults.theme),
            default_ocr_language=_choice(
                values.get("default_ocr_language"),
                {"en", "ar", "en_ar"},
                defaults.default_ocr_language,
            ),
            ocr_engine=_choice(
                values.get("ocr_engine"), {"paddle", "tesseract"}, defaults.ocr_engine
            ),
            confidence_threshold=_float_range(
                values.get("confidence_threshold"), 0.0, 1.0, defaults.confidence_threshold
            ),
            automatic_enhancement=_boolean(
                values.get("automatic_enhancement"), defaults.automatic_enhancement
            ),
            preprocessing_profile=_choice(
                values.get("preprocessing_profile"),
                {
                    "original",
                    "automatic",
                    "scanned_document",
                    "low_contrast",
                    "small_text",
                    "dark_background",
                    "custom",
                },
                defaults.preprocessing_profile,
            ),
            auto_copy=_boolean(values.get("auto_copy"), defaults.auto_copy),
            save_history=_boolean(values.get("save_history"), defaults.save_history),
            save_thumbnails=_boolean(values.get("save_thumbnails"), defaults.save_thumbnails),
            default_export_directory=_string(
                values.get("default_export_directory"), defaults.default_export_directory
            ),
            global_shortcut=_nonempty_string(
                values.get("global_shortcut"), defaults.global_shortcut
            ),
            pdf_render_resolution=_integer_range(
                values.get("pdf_render_resolution"), 72, 600, defaults.pdf_render_resolution
            ),
            start_minimized=_boolean(values.get("start_minimized"), defaults.start_minimized),
            logging_level=_choice(
                values.get("logging_level"),
                {"DEBUG", "INFO", "WARNING", "ERROR"},
                defaults.logging_level,
            ),
        )


class SettingsStore:
    """Read and atomically write a JSON settings document."""

    def __init__(self, path: Path, logger: logging.Logger | None = None) -> None:
        self._path = path
        self._logger = logger or logging.getLogger("pixelcopy.settings")

    def load(self) -> ApplicationSettings:
        """Load settings, recovering safely from missing or malformed content."""
        try:
            content = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ApplicationSettings()
        except OSError as error:
            self._logger.warning("Could not read settings; defaults will be used: %s", error)
            return ApplicationSettings()

        try:
            values = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            self._logger.warning("Malformed settings ignored: %s", error)
            return ApplicationSettings()

        if not isinstance(values, dict):
            self._logger.warning("Malformed settings ignored: root must be an object")
            return ApplicationSettings()
        return ApplicationSettings.from_mapping(values)

    def save(self, settings: ApplicationSettings) -> None:
        """Persist settings without exposing a partially written target file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._path.with_suffix(f"{self._path.suffix}.tmp")
        serialized = json.dumps(asdict(settings), indent=2, sort_keys=True) + "\n"
        temporary_path.write_text(serialized, encoding="utf-8")
        temporary_path.replace(self._path)


def _choice(value: Any, allowed: set[str], default: str) -> str:
    return value if isinstance(value, str) and value in allowed else default


def _string(value: Any, default: str) -> str:
    return value if isinstance(value, str) else default


def _nonempty_string(value: Any, default: str) -> str:
    return value if isinstance(value, str) and value.strip() else default


def _boolean(value: Any, default: bool) -> bool:
    return value if isinstance(value, bool) else default


def _float_range(value: Any, minimum: float, maximum: float, default: float) -> float:
    if isinstance(value, int | float) and not isinstance(value, bool):
        number = float(value)
        if minimum <= number <= maximum:
            return number
    return default


def _integer_range(value: Any, minimum: int, maximum: int, default: int) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and minimum <= value <= maximum:
        return value
    return default
