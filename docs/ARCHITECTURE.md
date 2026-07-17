# Architecture

## Goals

PixelCopy separates desktop presentation from local document-processing logic so expensive tasks remain cancellable, testable, and independent of Qt widgets. The application targets Windows first while keeping platform-specific services behind narrow interfaces.

## Layers

- `config`: validated preferences, stable metadata, and operating-system application paths.
- `domain`: framework-independent typed OCR, document, history, and export models and protocols.
- `services`: use-case orchestration for import, OCR, preprocessing, capture, PDF, export, and history.
- `ocr`, `preprocessing`, `database`, and `export`: implementation adapters behind shared interfaces.
- `workers`: Qt-aware background execution with progress, cancellation, success, and error signals.
- `ui`: presentation-only windows, pages, widgets, overlays, and styles.
- `utils`: small shared infrastructure utilities that do not contain product workflows.

Dependencies flow toward domain contracts. Qt widgets do not perform OCR, disk-heavy work, or database operations. Platform and engine adapters do not reach into UI state.

## Milestone 1 runtime

`pixelcopy.main` discovers and creates per-user directories, configures privacy-conscious logging, creates the Qt application, and constructs `ApplicationController`. The controller loads immutable validated settings, applies the selected theme, coordinates persistence when the settings page emits a theme change, and owns the main window for the event-loop lifetime.

`MainWindow` owns navigation and a stacked set of pages. It does not own settings persistence or processing logic.

Presentation styling is centralized in immutable semantic `DesignTokens`, shared spacing and typography constants, and one generated application stylesheet. Control minimum height is derived from the active application font rather than duplicated as fixed page geometry. `Page` provides shell spacing, while workflow pages own responsive layouts. The Extract workspace uses a non-collapsible `QSplitter`; `PreprocessingPanel` contains a bounded `QScrollArea` for advanced settings so adding options cannot collapse the preview or result editor.

## Image import

`ImageImportService` reads encoded bytes, detects the actual format through Pillow, verifies the content, applies non-destructive EXIF display orientation, and returns an immutable framework-independent RGBA `ImageDocument`. The original file is never modified. `ImageImportController` coordinates file, drop, and clipboard sources and translates expected failures into Extract-page messages. The Qt page owns only dialogs, signals, presentation state, and the zoomable `ImagePreview`.

## OCR foundation

Framework-independent `OCRRequest`, `OCROptions`, `OCRBlock`, `BoundingBox`, and `OCRResult` models retain recognition evidence and metadata. Engines implement `OCREngine`; `FakeOCREngine` keeps tests deterministic, while `PaddleOCREngine` lazily loads the official local PaddleOCR 3.x pipeline and normalizes `rec_texts`, `rec_scores`, and `rec_boxes`. Missing local dependencies or models produce setup guidance rather than a startup failure.

`OCRService` applies shared confidence filtering and direction-aware reading order. `OCRController` creates one `OCRWorker` and `QThread` per request. The worker signals progress, success, cancellation, understandable errors, and terminal cleanup. Source replacement and clearing remain synchronized through controller signals.

## Preprocessing

Immutable `PreprocessingOptions` and named profiles feed `PreprocessingPipeline`. The OpenCV pipeline exposes and enforces a stable stage order, checks cancellation between expensive stages, and returns a new RGBA `ImageDocument` without modifying the source. `PreprocessingController` owns a dedicated worker thread, updates the processed preview, and hands only successful derived documents to the OCR controller. Reset restores the retained original document.

## Windows capture and multilingual results

`WindowsGlobalShortcut` owns `RegisterHotKey` on a dedicated Windows message-loop thread, emits its Qt signal safely across the thread boundary, and always unregisters during application shutdown. This keeps capture active when the main window is minimized. `ScreenCaptureOverlay` spans the union of monitor geometries; `ScreenshotService` intersects the selection per screen and maps logical coordinates to physical pixels using each display scale. `CaptureController` returns the local image to the ordinary validated import path, restores a minimized main window, and requests foreground focus.

The OCR options and Paddle adapter accept English, Arabic, and mixed language modes. Shared reading order reverses horizontal ordering for RTL results while preserving visual lines, and the editor applies an RTL text direction for Arabic or mixed output.

## Scanned PDFs

`PDFService` opens a document only long enough to inspect it or render one requested page or thumbnail through PyMuPDF. `PDFThumbnailWorker` and `PDFWorker` run outside the GUI thread. The OCR worker continues after individual page errors, annotates blocks and results with page numbers, includes every failure in the combined text, reports progress, supports cancellation, and retains failed indexes for explicit retry.

## Local history

`HistoryRepository` uses a versioned SQLite schema and FTS5 index with transactional triggers. `HistoryController` receives completed OCR evidence but writes the currently edited text only after an explicit Save action and only while history is enabled. Deletion accepts multiple IDs and removes thumbnails only when their resolved parent is the application-owned thumbnail directory.

## Export

`ExportService` selects a typed exporter behind one protocol. Text and Markdown use the edited result; JSON retains structured OCR evidence; CSV emits one row per compatible block; and searchable PDF places the source image and an invisible positioned text layer on each page. Destination validation rejects missing folders and existing files before writing.

## Data locations

On Windows, roaming configuration lives under `%APPDATA%\PixelCopy`; history, thumbnails, caches, and logs live under `%LOCALAPPDATA%\PixelCopy`. Non-Windows development uses the corresponding XDG locations. Packaged resources are read separately from writable application data.

## Windows packaging

`PixelCopy.spec` creates a windowed PyInstaller onedir application. It collects installed Paddle, PaddleOCR, and PaddleX dynamic modules for production builds, explicitly excludes alternate Qt bindings, embeds Windows version metadata and the application icon, and copies only checked-in read-only assets. `resource_path` separates frozen `_MEIPASS` assets from repository development assets and rejects traversal. Build and verification scripts use argument lists without a shell; the release verifier isolates writable user directories and imports the packaged OCR runtime.

## Background work

OCR, preprocessing, PDF rendering, and PDF OCR run outside the GUI thread. Workers expose typed inputs and Qt signals for progress, cooperative cancellation, completion, and understandable failures. PDF pages are rendered incrementally rather than accumulated, and partial failures remain visible per page. Image preview scaling is bounded; source and processed images are retained only for the active workflow. The release review found no network paths or OCR-content logging. History queries use local SQLite FTS5; a future very-large-history benchmark may justify moving bulk maintenance to a worker, but ordinary explicit item operations remain short transactions.

## Extension boundaries

PaddleOCR will be the primary engine, with optional Tesseract and deterministic fake adapters sharing one protocol. Export formats will share another protocol. Screen capture and global shortcut registration will remain Windows-specific services until another platform receives a tested implementation.
