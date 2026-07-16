# Contributing to PixelCopy

PixelCopy welcomes focused improvements that preserve its local-first privacy model and Windows quality.

## Before starting

Read `AGENTS.md`, the relevant documents under `docs/`, the current branch and recent commits, and `git status`. Preserve all uncommitted work. Discuss changes that alter the approved stack or privacy model before implementation.

## Local workflow

1. Use Python 3.12 or newer and install `.[dev]` in a virtual environment.
2. Implement the smallest complete vertical slice without pulling later milestones into scope.
3. Keep domain, services, persistence, workers, and Qt presentation separated.
4. Add deterministic offline tests; prefer fakes over OCR model downloads.
5. Run the relevant tests, Ruff lint and formatting checks, and strict mypy.
6. Update behavior and architecture documentation.
7. Review the full diff and stage only related files.
8. Create a focused Conventional Commit and push without rewriting history.

## Commit messages

Use forms such as `feat(ui): add sidebar navigation`, `fix(settings): recover malformed theme`, `test(ui): cover keyboard navigation`, or `docs: clarify privacy storage`. Do not use vague messages such as `update`, `progress`, or `fixes`.

## Pull requests

Explain behavior, privacy implications, checks run with their exact summaries, screenshots for intentional UI changes, and known limitations. Never include private source files, OCR text, local settings, logs, downloaded models, build artifacts, or secrets.

## Quality bar

Features must handle errors clearly, remain responsive, use complete production type annotations, preserve original inputs, avoid logging content, and keep accessible keyboard and focus behavior. Do not weaken tests or conceal failures.
