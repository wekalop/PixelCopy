# Security Policy

## Supported versions

PixelCopy is pre-alpha. Security fixes are applied to the latest `main` branch; there are no supported release binaries yet.

## Reporting a vulnerability

Do not open a public issue containing exploit details, private documents, extracted text, credentials, or machine paths. Use GitHub's private vulnerability reporting for `wekalop/PixelCopy` when available. Include affected revision, reproducible steps using non-private fixtures, impact, and suggested mitigations.

## Security principles

PixelCopy treats imported images and PDFs as untrusted. It must not execute document content, upload source data, log extracted text, invoke shells with imported values, or traverse outside an explicitly selected export destination. Temporary content must be scoped and deleted. Dependencies must be constrained and reviewed before use.

The application is intended to process content locally without telemetry, analytics, or cloud text services. See `docs/PRIVACY.md` for stored data.
