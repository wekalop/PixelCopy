# Product Specification

## Purpose

PixelCopy is a modern Windows desktop OCR application for copying editable text from visual sources where ordinary copy and paste is unavailable. Its tagline is “Copy text from anything you can see.” Windows 10 and 11 are the first-class targets; architecture should permit later macOS and Linux work without reducing Windows quality.

## Principles

- All recognition and processing remain local.
- Never use generative AI, LLMs, cloud correction, guessing, rewriting, summarization, or translation.
- Preserve original sources and uncertain OCR output.
- Keep the interface responsive, keyboard-friendly, accessible, and clear about errors.
- Make history optional and disabled by default.

## Planned workflows

The staged product will import validated PNG, JPEG, BMP, TIFF, and WebP content through a file picker, drag and drop, clipboard paste, and a configurable screen-region shortcut. It will recognize English, Arabic, and mixed content with structured blocks, confidence, geometry, warnings, language, engine, duration, and page metadata.

Preprocessing will provide explicit, previewable profiles and stages without changing the original. Scanned PDFs will render and OCR selected pages incrementally with cancellation, progress, and per-page errors. Editable results will support deterministic cleanup, statistics, optional local history, and TXT, Markdown, JSON, compatible CSV, and searchable PDF export.

## User interface

The five top-level pages are Extract, PDF, History, Settings, and About. The design uses a left sidebar, restrained blue accent, rounded cards, consistent spacing, accessible light and dark themes, clear empty/loading/error/success states, and native keyboard behavior.

## Milestone 1 scope

Milestone 1 includes the project foundation, PySide6 entry point and application shell, sidebar and placeholder pages, visual theme foundation, settings and logging foundations, tests, CI, repository instructions, and documentation. It explicitly excludes image import, OCR, preprocessing, screen capture, PDF processing, SQLite history, export, and packaging implementation.

## Roadmap

1. Foundation
2. Image import
3. OCR foundation
4. Preprocessing
5. Screen capture
6. Arabic and multilingual OCR
7. PDF processing
8. History
9. Export
10. Polish and accessibility
11. Windows packaging
