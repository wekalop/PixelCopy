# Testing

## Tooling

PixelCopy uses pytest for unit and integration tests, pytest-qt for Qt behavior, Ruff for linting and formatting, and strict mypy for production types. Tests must remain deterministic, offline, and free of private content.

## Commands

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src
```

Set `$env:QT_QPA_PLATFORM = "offscreen"` before pytest in headless Windows environments. CI sets this automatically.

## Organization

- `tests/unit`: framework-independent models, settings, paths, cleanup, algorithms, and adapters with isolated dependencies.
- `tests/integration`: multiple local components working together without external services.
- `tests/ui`: navigation, workers, critical workflows, focus, theme, and direction behavior using pytest-qt.
- `tests/fixtures`: small synthetic, non-private images and documents introduced only when needed.

## Milestone 1 coverage

Current tests cover application-data directory creation, rotating log setup, required page navigation, theme stylesheet identity and focus rules, settings defaults, malformed settings recovery, field validation, settings round trips, and live theme persistence. Image tests cover every supported encoding, content-versus-extension detection, corrupt and unsupported input, file presentation and clearing, clipboard import, metadata, and actionable errors.

OCR tests cover model invariants, average confidence, left-to-right and right-to-left reading order, shared filtering, fake engine requests, PaddleOCR 3.x result normalization through an injected model-free pipeline, worker success and cancellation, background UI completion, editable results, statistics, and clipboard copy.

Preprocessing tests lock the stage order, profile values, source immutability, rotation and upscale dimensions, original passthrough, cancellation, processed-preview creation, reset, and image/OCR workflow regressions.

Capture tests cover shortcut parsing, conflicts represented as typed errors, negative monitor origins, and logical-to-physical DPI mapping. Multilingual tests cover language choices, RTL editor direction, Unicode preservation, and right-to-left reading order without downloading models.

PDF tests create small synthetic documents and cover range validation, metadata, incremental rendering, thumbnails, background extraction, page annotations, visible per-page failures, separators, retry state, and navigation without model downloads.

History tests cover migrations, FTS search, opt-in enforcement, edited-text saving, favorites, rename, preview, copy, multi-ID deletion, clear behavior, and protection against deleting thumbnail paths outside the owned directory.

Future OCR tests will use a fake engine by default. CI must not download large OCR models. Windows coordinate and DPI calculations, page failures, cancellation, reading order, RTL behavior, exporters, history, and packaging verification will be added with their implementation milestones.
