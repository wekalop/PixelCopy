# PixelCopy Repository Instructions

## Product purpose

PixelCopy is a privacy-first Windows desktop application that copies editable text from images, screen captures, clipboard images, and scanned PDFs. All recognition and document processing must remain local. Never add generative AI, cloud OCR, analytics, telemetry, or content-uploading services.

## Approved stack

- Python 3.12+
- PySide6 for the desktop UI
- PaddleOCR as the primary OCR engine and optional Tesseract fallback
- OpenCV, Pillow, and PyMuPDF for image and document processing
- SQLite for optional local history
- pytest and pytest-qt for tests
- Ruff for linting and formatting, mypy for typing, PyInstaller for Windows packaging
- GitHub Actions for CI

Add a dependency only when its milestone needs it. Do not silently replace an approved technology.

## Architecture boundaries

Use a `src` layout. Keep domain models independent of frameworks. Put orchestration in services, infrastructure adapters in their dedicated packages, background work in workers, and presentation in `ui`. Qt widgets must not contain business logic. OCR engines and exporters must implement shared typed interfaces. Long-running OCR, PDF, preprocessing, and database operations must never block the GUI thread. Avoid global mutable state and hidden singletons; inject dependencies where it improves testing.

## Repository structure

- `src/pixelcopy/`: application code
- `tests/unit/`, `tests/integration/`, `tests/ui/`: deterministic offline tests
- `docs/`: product and engineering documentation
- `assets/`: packaged visual resources and non-private samples
- `scripts/`: build and release tooling
- `.github/workflows/`: CI and, when stable, release automation

## Coding conventions

Use complete type annotations in production code, explicit dataclasses or enums for domain data, `pathlib` for paths, and actionable exception messages. Preserve original inputs. Never use `shell=True` with imported data. Do not swallow exceptions or log OCR content. Keep files focused, use deterministic behavior, and do not leave TODO placeholders in completed features.

## Verification commands

Run the smallest relevant test set during development and the full suite at milestone completion:

```powershell
python -m pytest
ruff check .
ruff format --check .
mypy src
```

Use `QT_QPA_PLATFORM=offscreen` for headless UI tests where required. Tests must not need network access or large OCR model downloads.

## Git rules

Read this file and check `git status`, the active branch, recent commits, and relevant docs before every task. Preserve all user changes. Never run destructive Git operations, rewrite published history, amend pushed commits, or force-push. Keep independently complete features in focused Conventional Commits and push each successful commit to `origin`. Stage only files belonging to that feature. Never commit secrets, local settings, OCR model caches, extraction history, private screenshots, logs, temporary files, build output, or installer output.

## Privacy and security

Process user content locally. Store OCR text and thumbnails only when history is explicitly enabled. Validate untrusted images, PDFs, and paths; use safe temporary files; delete temporary page images; avoid exposing source paths; and log technical metadata without document content. Application data belongs in the OS application-data directory, never the install directory.

## Documentation and completion

Update README, architecture, testing, privacy, UI, OCR pipeline, and Windows build documentation whenever behavior changes. A feature is complete only when scope, error handling, tests, lint, types, documentation, application usability, focused commit, and push have been verified. Report exact verification summaries, commit hashes, push results, limitations, and remaining work. Do not claim unrun checks or unsupported behavior.

## Prohibited shortcuts

Do not build a one-file prototype, perform unrelated refactors, weaken tests, skip errors silently, fabricate uncertain OCR text, hardcode user paths, add cloud correction, or implement a later milestone early. Never delete or reset user work to make implementation easier.
