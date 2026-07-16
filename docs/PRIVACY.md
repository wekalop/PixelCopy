# Privacy

PixelCopy is designed to process visual content locally. It must not upload images, PDFs, screenshots, clipboard content, or extracted text. It includes no analytics, telemetry, cloud correction, generative AI, or remote crash reporting.

## Milestone 1 stored data

PixelCopy stores a JSON settings file under the user's roaming application-data directory and rotating technical logs under the user's local application-data directory. Settings include preferences such as theme and future workflow defaults. Logs record startup and technical failures; they must never contain extracted text, document content, clipboard content, or full source paths by default.

No source content, thumbnails, OCR text, PDF pages, or extraction history are stored in Milestone 1.

## Future optional history

History will be disabled by default. While disabled, PixelCopy will not save OCR text, thumbnails, or source content. When enabled, documentation and UI will identify fields and local locations. Deleting an item will also safely delete its associated local thumbnail. Clearing history will require an explicit user action.

## Temporary data

Future PDF rendering and preprocessing may require temporary images. They will use application-owned temporary locations, avoid predictable unsafe names, and be removed after completion, cancellation, or handled failure. Imported documents remain unmodified.

## User control

Users can reset preferences by deleting or resetting the settings file. Future history controls will support per-item deletion, multi-delete, and clear-all. Uninstall behavior depends on the Windows installer milestone and will be documented before release.
