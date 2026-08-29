# Contributing

Contributions should improve portability, evidence discipline, privacy, or recovery quality without turning the project into a general memory database.

## Development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m pytest -q
python scripts/validate_release.py
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`.

## Change requirements

- Add or update tests for behavior changes.
- Preserve preview-first and non-destructive installation semantics.
- Do not add runtime dependencies without a documented necessity.
- Do not commit personal paths, credentials, raw model transcripts, or private project state.
- Label unverified compatibility claims as unverified.

## Pull requests

Explain the problem, the threat or failure mode addressed, the validation run, and any migration impact.
