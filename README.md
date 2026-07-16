# PixelCopy

> Copy text from anything you can see.

PixelCopy is a privacy-first Windows desktop application for extracting editable text from images, screenshots, clipboard images, screen selections, and scanned PDFs. Processing is designed to remain local: no generative AI, cloud correction, analytics, or telemetry.

## Current status

PixelCopy is in pre-alpha. Milestones 1 and 2 provide the typed application foundation, polished PySide6 shell, themes and settings, and content-validated image import through a file picker, drag and drop, or clipboard. Imported PNG, JPEG, BMP, TIFF, and WebP sources have a zoomable, pannable preview and metadata. OCR, preprocessing, capture, PDFs, history, export, and packaging are planned for later milestones and are not yet implemented.

## Requirements

- Windows 10 or Windows 11
- Python 3.12 or newer for development

## Development setup

```powershell
git clone https://github.com/wekalop/PixelCopy.git
cd PixelCopy
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pixelcopy
```

The current runtime installs PySide6 and Pillow. Heavy OCR and document dependencies will be introduced with the milestones that use them; CI will continue to avoid model downloads.

## Verification

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src
```

For headless environments, set `QT_QPA_PLATFORM=offscreen` before running UI tests.

## Architecture

PixelCopy uses a typed `src` layout with presentation, configuration, domain, services, infrastructure adapters, and workers kept separate as those layers are introduced. Qt widgets remain presentation-focused; expensive work will use cancellable background workers and signals.

The approved product stack is Python 3.12+, PySide6, PaddleOCR, optional Tesseract, OpenCV, Pillow, PyMuPDF, SQLite, pytest, Ruff, mypy, PyInstaller, and GitHub Actions. See [Architecture](docs/ARCHITECTURE.md) and [Product specification](docs/PRODUCT_SPEC.md).

## Privacy

PixelCopy does not upload source content or extracted text. Milestone 1 stores only a local settings JSON file and rotating technical logs; logs must never contain OCR content. Optional extraction history will default off. See [Privacy](docs/PRIVACY.md) and [Security policy](SECURITY.md).

## Contributing

Read [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md) before making changes. Work is organized as focused, tested Conventional Commits.

## License

PixelCopy is available under the [MIT License](LICENSE).
