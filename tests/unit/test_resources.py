from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pixelcopy.utils.resources import resource_path, resource_root


def test_source_resource_path_finds_packaged_icon() -> None:
    assert resource_path("icons/pixelcopy.png").is_file()


def test_frozen_resource_path_uses_bundle_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", "C:/bundle", raising=False)
    assert resource_root() == Path("C:/bundle/assets")


def test_resource_path_rejects_traversal() -> None:
    with pytest.raises(ValueError, match="must stay inside"):
        resource_path("../private.txt")
