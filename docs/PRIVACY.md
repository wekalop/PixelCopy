# Privacy

PixelCopy is designed to process visual content locally. It must not upload images, PDFs, screenshots, clipboard content, or extracted text. It includes no analytics, telemetry, cloud correction, generative AI, or remote crash reporting.

## Milestone 1 stored data

PixelCopy stores a JSON settings file under the user's roaming application-data directory and rotating technical logs under the user's local application-data directory. Settings include preferences such as theme and future workflow defaults. Logs record startup and technical failures; they must never contain extracted text, document content, clipboard content, or full source paths by default.

Imported image files are decoded locally and remain unmodified. The current image is retained only in application memory for display and is released when replaced, cleared, or the process exits. No source copies, thumbnails, OCR text, PDF pages, or extraction history are written to storage.
Scanned PDFs are opened locally and pages are rendered incrementally in memory. Current thumbnail and page images are not written to persistent storage, and failed pages are reported rather than uploaded or silently omitted.

## Future optional history

History is disabled by default. While disabled, PixelCopy does not save OCR text, thumbnails, or source content. When enabled, only an explicit Save action writes the currently edited text and structured metadata to `%LOCALAPPDATA%\PixelCopy\history.sqlite3`. Deleting an item also removes an associated thumbnail only from the application-owned thumbnail directory. Multi-delete and clear-all are explicit user actions.

## Temporary data

Future PDF rendering and preprocessing may require temporary images. They will use application-owned temporary locations, avoid predictable unsafe names, and be removed after completion, cancellation, or handled failure. Imported documents remain unmodified.

## User control

Users can reset preferences by deleting or resetting the settings file. Future history controls will support per-item deletion, multi-delete, and clear-all. Uninstall behavior depends on the Windows installer milestone and will be documented before release.
