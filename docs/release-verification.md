# Release Verification

**Release:** `v0.1.0`  
**Verification date:** 2026-08-29  
**Local interpreter:** CPython 3.13.5  
**Local platform:** Linux container

## Result

The local public-release gate passed. The release is labeled **public-ready alpha**, not production-enforced security software.

## Source validation

| Check | Result |
|---|---|
| Automated regression tests | 37 passed |
| Public text privacy scan | 89 files, 0 findings |
| Root `project` profile doctor | healthy, 0 warnings |
| Synthetic project doctor | healthy, 0 warnings |
| Synthetic umbrella doctor | healthy, 0 warnings |
| Synthetic Orbit Notes tests | 2 passed |
| Python compile check | passed |
| Claude settings JSON | valid; expected four lifecycle events |
| Required public documentation | complete |
| Runtime dependency declaration | empty |

Primary command:

```bash
PYTHONPATH=src python scripts/validate_release.py
```

The machine-readable result is generated locally under `.agent/local/release-validation.json` and intentionally excluded from version control.

## Distribution validation

### Wheel

- Built as `agent_workspace_continuity-0.1.0-py3-none-any.whl`.
- Installed offline with `--no-index --no-deps` into a fresh virtual environment.
- Installed CLI reported `awc 0.1.0`.
- Project profile, optional files, and Claude hook examples installed successfully.
- `awc doctor --strict` and `awc privacy --continuity-only` passed.
- Two recovery runs were byte-identical.
- SessionStart hook returned bounded `additionalContext` and did not store the raw synthetic session identifier.
- Archive contained 36 entries and no `__pycache__` or `.pyc` files.

### Source distribution

- Built as `agent_workspace_continuity-0.1.0.tar.gz`.
- Installed without dependency resolution into an isolated target.
- Installed CLI generated and validated an umbrella profile.
- Extracted source ran all 37 regression tests successfully.
- Archive contained 122 entries and no `__pycache__` or `.pyc` files.

## Reproducible build

`scripts/build_release.py` performs two clean builds with a fixed `SOURCE_DATE_EPOCH`, normalizes Wheel ZIP metadata and source-tar ownership, modes, ordering, timestamps, and gzip headers, then compares SHA-256 hashes before copying artifacts to `dist/`.

Both artifacts were byte-identical across the paired local builds. Final artifact hashes are recorded in the release package’s `SHA256SUMS.txt`, rather than duplicated here.

## Boundaries not yet independently verified

- GitHub Actions cannot run until a new GitHub repository exists.
- Python 3.11 and 3.12 are included in the CI matrix but were not available in the local container.
- Native Windows, macOS, and WSL execution were not run in this release environment.
- Claude Code lifecycle behavior was validated against current official schemas and simulated hook input; a live Claude Code session was not launched inside the container.
- Markdown rules guide agent behavior but are not a hard security or policy-enforcement mechanism.
