# OCR Pipeline

The OCR foundation is implemented. Image preprocessing, multilingual model setup, and PDF orchestration are added in their later milestones.

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

Planned profiles are Original, Automatic, Scanned document, Low contrast, Small text, Dark background, and Custom. Stages may include rotation, cropping, grayscale, contrast, brightness, denoise, sharpen, adaptive or binary threshold, inversion, deskew, upscale, and safe border removal. Order will be explicit and regression-tested.

## Engines and languages

PaddleOCR 3.x is the primary local adapter and is installed through the optional `ocr` dependency group. Its runtime and models are loaded only when recognition begins. A fake engine keeps tests offline. Typed modes cover paragraph, single line, sparse text, and practical table-oriented extraction. Tesseract fallback and Arabic/mixed model setup remain later work.

## Integrity rules

The pipeline never invents uncertain text, silently drops failed pages, uploads content, or sends text to correction services. Confidence thresholds filter or warn deterministically. Logs contain technical events, not extracted documents.
