"""Operating-system appropriate application paths."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from pixelcopy.config.constants import APP_NAME


@dataclass(frozen=True, slots=True)
class AppPaths:
    """Writable paths used by PixelCopy."""

    data_dir: Path
    config_dir: Path
    cache_dir: Path
    log_dir: Path

    @classmethod
    def discover(cls) -> AppPaths:
        """Resolve user-specific paths without writing to them."""
        if os.name == "nt":
            data_root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            config_root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
            cache_root = data_root
        else:
            data_root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
            config_root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
            cache_root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))

        return cls(
            data_dir=data_root / APP_NAME,
            config_dir=config_root / APP_NAME,
            cache_dir=cache_root / APP_NAME / "cache",
            log_dir=data_root / APP_NAME / "logs",
        )

    def ensure_directories(self) -> None:
        """Create application-owned directories when the application starts."""
        for directory in (self.data_dir, self.config_dir, self.cache_dir, self.log_dir):
            directory.mkdir(parents=True, exist_ok=True)
