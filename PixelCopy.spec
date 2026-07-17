# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller onedir configuration for the portable Windows application."""

from importlib.util import find_spec
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


ROOT = Path(SPECPATH).resolve()
datas = [(str(ROOT / "assets"), "assets")]
binaries = []
hiddenimports = []

# OCR packages load pipeline modules and native libraries dynamically. Build
# environments with the `ocr` extra installed collect those packages in full;
# lightweight packaging smoke builds intentionally omit them.
for package in ("paddle", "paddleocr", "paddlex"):
    if find_spec(package) is not None:
        package_datas, package_binaries, package_hidden = collect_all(package)
        datas += package_datas
        binaries += package_binaries
        hiddenimports += package_hidden

a = Analysis(
    [str(ROOT / "src" / "pixelcopy" / "__main__.py")],
    pathex=[str(ROOT / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "mypy",
        "ruff",
        "PyQt5",
        "PyQt6",
        "PySide2",
    ],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PixelCopy",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(ROOT / "assets" / "icons" / "pixelcopy.ico"),
    version=str(ROOT / "packaging" / "windows_version_info.txt"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="PixelCopy",
)
