# Changelog

All notable changes will be documented here. The project follows Keep a Changelog conventions and intends to use Semantic Versioning after the first stable release.

## Unreleased

### Added

- Python 3.12+ `src`-layout project foundation.
- PySide6 application shell with Extract, PDF, History, Settings, and About navigation.
- Accessible light and dark visual themes.
- Validated local settings persistence with safe malformed-file recovery.
- Privacy-conscious rotating technical logging.
- Offline unit and UI test foundations.
- Windows and Linux GitHub Actions verification.
- Product, architecture, OCR pipeline, UI, testing, Windows build, and privacy documentation.
- Content-based validation and decoding for PNG, JPEG, BMP, TIFF, and WebP images.
- File picker, drag-and-drop, and clipboard image import.
- Aspect-preserving source preview with bounded zoom, panning, metadata, replace, and clear behavior.
- Actionable image import errors that preserve an already valid source.
- Typed OCR requests, blocks, bounds, results, modes, warnings, and confidence statistics.
- Shared OCR protocol, deterministic fake engine, and lazy local PaddleOCR 3.x adapter.
- Direction-aware geometric reading order and confidence filtering.
- Cancellable background OCR worker with progress, errors, editable result text, and copy action.
- Immutable OpenCV preprocessing pipeline with explicit, tested stage order.
- Original, Automatic, Scanned document, Low contrast, Small text, Dark background, and Custom profiles.
- Rotation, grayscale, contrast, brightness, denoise, sharpen, threshold, invert, deskew, and upscale controls.
- Cancellable background processed preview with original reset and OCR handoff.
- Configurable native Windows capture shortcut with conflict reporting and clean unregister.
- Multi-monitor capture overlay with negative-coordinate and per-monitor DPI mapping.
- Escape cancellation, minimum selection validation, capture import, and focus restoration.
- English, Arabic, and mixed-language selection with direction-aware ordering and RTL results.
- Validated scanned PDF inspection, page counts, ranges, and incremental PyMuPDF rendering.
- Background page thumbnails and memory-conscious multi-page OCR.
- Per-page progress, cancellation, visible failures, page separators, and failed-page retry.
- Versioned SQLite and FTS5 history repository with search, favorites, rename, and deletion.
- Privacy-gated local history UI with preview, copy, multi-delete, clear, and safe thumbnail cleanup.

### Not yet implemented

- Export and Windows packaging.
