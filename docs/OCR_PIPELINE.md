# OCR Pipeline

The OCR foundation and image preprocessing are implemented. Multilingual model setup and PDF orchestration are added in their later milestones.

## Stages

1. Validate and decode an image or incrementally render a selected PDF page.
2. Correct EXIF orientation while retaining an untouched source representation.
3. Apply the explicit preprocessing profile and ordered custom stages.
4. Correct orientation and invoke a local engine through the shared OCR protocol.
5. Normalize engine output into typed text blocks, polygons or boxes, confidence, language, page, engine, duration, image dimensions, warnings, and region metadata.
6. Reconstruct reading order with direction-aware deterministic geometry.
7. Apply only explicitly selected deterministic cleanup.
8. Present editable text and structured metadata; store nothing unless history is enabled.

## Preprocessing profiles

Implemented profiles are Original, Automatic, Scanned document, Low contrast, Small text, Dark background, and Custom. The current explicit order is rotation, grayscale, contrast/brightness, denoise, sharpen, adaptive or binary threshold, inversion, deskew, and upscale. Processing is cancellable between stages and creates a derived in-memory document; cropping and conservative border removal remain future additions.

## Engines and languages

PaddleOCR 3.x is the primary local adapter and is installed through the optional `ocr` dependency group. Its runtime and English or Arabic model are loaded only when recognition begins. A fake engine keeps tests offline. Typed modes cover paragraph, single line, sparse text, and practical table-oriented extraction. English, Arabic, and mixed selection use direction-aware reading order and RTL presentation; Tesseract fallback remains future work.

## Integrity rules

The pipeline never invents uncertain text, silently drops failed pages, uploads content, or sends text to correction services. Confidence thresholds filter or warn deterministically. Logs contain technical events, not extracted documents.

Postprocessing is opt-in and deterministic. The available operations normalize horizontal whitespace while preserving line boundaries, collapse repeated blank lines, and join only words that contain an explicit hyphen immediately before a line ending. Each operation is reversible through the editor undo stack.
