"""Read-only application resource lookup for source and frozen builds."""

from __future__ import annotations

import sys
from pathlib import Path


def resource_root() -> Path:
    """Return the bundled or repository resource directory without creating it."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if getattr(sys, "frozen", False) and isinstance(bundle_root, str):
        return Path(bundle_root) / "assets"
    return Path(__file__).resolve().parents[3] / "assets"


def resource_path(relative_path: str) -> Path:
    """Resolve a safe path below the read-only resource directory."""
    root = resource_root().resolve()
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Resource path must stay inside the application assets directory.")
    return candidate
