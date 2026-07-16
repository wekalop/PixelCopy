# Privacy

PixelCopy is designed to process visual content locally. It must not upload images, PDFs, screenshots, clipboard content, or extracted text. It includes no analytics, telemetry, cloud correction, generative AI, or remote crash reporting.

## Milestone 1 stored data

PixelCopy stores a JSON settings file under the user's roaming application-data directory and rotating technical logs under the user's local application-data directory. Settings include preferences such as theme and future workflow defaults. Logs record startup and technical failures; they must never contain extracted text, document content, clipboard content, or full source paths by default.

Imported image files are decoded locally and remain unmodified. The current image is retained only in application memory for display and is released when replaced, cleared, or the process exits. No source copies, thumbnails, OCR text, PDF pages, or extraction history are written to storage.
Scanned PDFs are opened locally and pages are rendered incrementally in memory. Current thumbnail and page images are not written to persistent storage, and failed pages are reported rather than uploaded or silently omitted.

## Optional history

History is disabled by default. While disabled, PixelCopy does not save OCR text, thumbnails, or source content. When enabled, only an explicit Save action writes the currently edited text and structured metadata to `%LOCALAPPDATA%\PixelCopy\history.sqlite3`. Deleting an item also removes an associated thumbnail only from the application-owned thumbnail directory. Multi-delete and clear-all are explicit user actions.

## Temporary data

PDF rendering and preprocessing use in-memory page and image representations for current workflows. Export writes only to a destination explicitly chosen by the user. If future processing requires temporary files, they must use application-owned temporary locations, avoid predictable names, and remove content after completion, cancellation, or handled failure. Imported documents remain unmodified.

## User control

Users can reset preferences by deleting or resetting the settings file. History supports per-item deletion, multi-delete, and clear-all; associated thumbnails are removed only when they are inside the application-owned thumbnail directory. Portable-build removal does not automatically delete application data under `%APPDATA%` or `%LOCALAPPDATA%`, so users retain control of settings, logs, and opted-in history.
