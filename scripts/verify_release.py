"""Validate a portable PixelCopy distribution and launch smoke test."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify_distribution(
    distribution: Path, *, launch: bool = True, verify_ocr: bool = True
) -> None:
    """Validate required files and optionally execute a bounded startup test."""
    executable = distribution.resolve() / "PixelCopy.exe"
    required = (
        executable,
        distribution.resolve() / "_internal" / "assets" / "icons" / "pixelcopy.png",
    )
    missing = tuple(path for path in required if not path.is_file())
    if missing:
        rendered = ", ".join(str(path) for path in missing)
        raise RuntimeError(f"Release is missing required files: {rendered}")
    if launch:
        with tempfile.TemporaryDirectory(prefix="pixelcopy-release-") as temporary:
            environment = os.environ.copy()
            environment["APPDATA"] = temporary
            environment["LOCALAPPDATA"] = temporary
            environment.setdefault("QT_QPA_PLATFORM", "offscreen")
            smoke_argument = "--smoke-test-ocr" if verify_ocr else "--smoke-test"
            completed = subprocess.run(
                [str(executable), smoke_argument],
                cwd=distribution,
                env=environment,
                check=False,
                timeout=60,
            )
        if completed.returncode != 0:
            raise RuntimeError(
                f"Packaged startup smoke test exited with code {completed.returncode}."
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "distribution",
        type=Path,
        nargs="?",
        default=ROOT / "dist" / "PixelCopy",
    )
    parser.add_argument("--no-launch", action="store_true")
    parser.add_argument(
        "--without-ocr",
        action="store_true",
        help="Verify a lightweight CI-only bundle without importing PaddleOCR",
    )
    options = parser.parse_args()
    verify_distribution(
        options.distribution,
        launch=not options.no_launch,
        verify_ocr=not options.without_ocr,
    )
    print(f"Release verification passed: {options.distribution.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
