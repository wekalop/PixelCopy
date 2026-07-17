# Building on Windows

## Supported build environment

Build the release on 64-bit Windows 10 or Windows 11 with Python 3.12. PyInstaller produces a Windows-specific onedir bundle; do not cross-compile it. Create a clean virtual environment so unrelated packages cannot expand or destabilize collection:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,build,ocr]"
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src
```

## Local OCR model setup

The production bundle contains PaddlePaddle, PaddleOCR, and their native libraries, but not downloaded model caches. This keeps generated third-party weights out of Git and lets English/Arabic models be updated independently. Preload the official models on a connected build/test machine with:

```powershell
python scripts/download_ocr_models.py --languages en ar
```

This command initializes no user document and processes no OCR content. PaddleOCR stores model weights in its per-user cache. On a clean end-user machine, the first recognition for a language may download its official model; subsequent recognition is local. A failed or unavailable download is surfaced as setup guidance instead of crashing at startup.

## Production portable build

```powershell
python scripts/build_windows.py --archive
python scripts/verify_release.py
```

`build_windows.py` refuses a production build unless `paddle` and `paddleocr` are installed. It executes `PixelCopy.spec`, embeds the multi-resolution icon and Windows version resource, bundles read-only assets, and writes the onedir application to `dist\PixelCopy`. `--archive` also creates `dist\PixelCopy-portable.zip` for installer input or portable distribution.

`verify_release.py` checks required resources and launches `PixelCopy.exe --smoke-test-ocr` with isolated temporary `%APPDATA%` and `%LOCALAPPDATA%` directories. The smoke test initializes the cached English and Arabic pipelines, proving that the packaged application starts, imports its bundled Paddle runtime, exposes PaddleX OCR-core dependency metadata, and can load local models without a system Python installation. It does not process user content. Run `download_ocr_models.py` first so verification does not need a model download.

The verified development build on Python 3.13 contained 14,029 files and 1,080,161,350 bytes before ZIP compression. Release size varies with supported dependency versions; review `build\PixelCopy\warn-PixelCopy.txt` and the final size for every release. Missing optional TensorRT or PaddleX serving plugins are acceptable because PixelCopy uses local CPU inference, not TensorRT or a serving process.

## Lightweight CI build

Normal CI must not download the large OCR runtime or models. Its Windows packaging job uses:

```powershell
python -m pip install ".[build]"
python scripts/build_windows.py --without-ocr
python scripts/verify_release.py --without-ocr
```

This validates PyInstaller configuration, the executable, Qt startup, version/icon resources, and bundled assets. The `--without-ocr` output is explicitly not releasable.

## Resource and data boundaries

The checked-in `PixelCopy.spec` follows the official [PyInstaller spec-file guidance](https://pyinstaller.org/en/stable/spec-files.html). Frozen read-only resources resolve below the bundle’s `_internal\assets` directory. Settings, logs, opted-in history, thumbnails, and model caches remain under the current user’s `%APPDATA%` or `%LOCALAPPDATA%`; PixelCopy never writes beside the executable.

Never commit `build\`, `dist\`, ZIPs, downloaded models, application data, test data, or private documents. Code signing and an installer wrapper are release-policy concerns and are not configured for this pre-alpha portable build.
