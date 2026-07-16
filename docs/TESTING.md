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

Current tests cover application-data directory creation, rotating log setup, required page navigation, theme stylesheet identity and focus rules, settings defaults, malformed settings recovery, field validation, settings round trips, and live theme persistence.

Future OCR tests will use a fake engine by default. CI must not download large OCR models. Windows coordinate and DPI calculations, page failures, cancellation, reading order, RTL behavior, exporters, history, and packaging verification will be added with their implementation milestones.
