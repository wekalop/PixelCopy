# Building on Windows

## Development

Use a supported 64-bit Windows 10 or Windows 11 environment with Python 3.12 or newer:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pixelcopy
```

Run the complete verification commands in `docs/TESTING.md` before sharing changes.

## Packaging status

Standalone Windows packaging belongs to Milestone 11 and is not implemented yet. PyInstaller is declared as the approved build dependency, but no production `.spec`, icon metadata, model setup flow, portable bundle, or installer-ready output is claimed in Milestone 1.

The packaging milestone must bundle Qt and application resources, handle PaddleOCR dependencies and local model setup, preserve `%APPDATA%` and `%LOCALAPPDATA%` storage, provide version metadata and an application icon, and verify launch on a clean supported machine without Python installed. Build and installer outputs remain untracked.

## Resource rules

Packaged read-only resources and writable user data must resolve through separate helpers. Never write beside the executable or bundle personal files, tests, settings, logs, downloaded models, extraction history, or developer caches into release output.
