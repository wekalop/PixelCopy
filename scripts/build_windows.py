"""Build the portable PixelCopy Windows directory with PyInstaller."""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_portable(*, clean: bool = True, archive: bool = False, require_ocr: bool = True) -> Path:
    """Build and optionally zip the onedir distribution."""
    if os.name != "nt":
        raise RuntimeError("PixelCopy Windows packages must be built on Windows.")
    if require_ocr and any(
        importlib.util.find_spec(package) is None for package in ("paddle", "paddleocr")
    ):
        raise RuntimeError(
            "Production builds require the local OCR runtime. Install it with: "
            'python -m pip install -e ".[build,ocr]"'
        )
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm"]
    if clean:
        command.append("--clean")
    command.append(str(ROOT / "PixelCopy.spec"))
    subprocess.run(command, cwd=ROOT, check=True)
    distribution = ROOT / "dist" / "PixelCopy"
    executable = distribution / "PixelCopy.exe"
    if not executable.is_file():
        raise RuntimeError(f"PyInstaller completed without creating {executable}.")
    if archive:
        shutil.make_archive(str(ROOT / "dist" / "PixelCopy-portable"), "zip", distribution)
    return distribution


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-clean", action="store_true", help="Reuse PyInstaller work files")
    parser.add_argument("--archive", action="store_true", help="Create a portable ZIP")
    parser.add_argument(
        "--without-ocr",
        action="store_true",
        help="Build only for CI packaging smoke tests; not a releasable package",
    )
    options = parser.parse_args()
    distribution = build_portable(
        clean=not options.no_clean,
        archive=options.archive,
        require_ocr=not options.without_ocr,
    )
    print(f"Portable build created at {distribution}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
