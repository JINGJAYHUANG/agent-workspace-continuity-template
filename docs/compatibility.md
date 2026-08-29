# Compatibility

**Last checked:** 2026-08-29

## Python

| Version | Status |
|---|---|
| 3.11 | Declared and covered by CI matrix |
| 3.12 | Declared and covered by CI matrix |
| 3.13 | Locally verified and covered by CI matrix |

The package has no runtime dependencies outside the Python standard library.

## Operating systems

The core CLI uses `pathlib`, atomic file replacement, and subprocess calls to Git when available. It is intended for Windows, macOS, Linux, and WSL. Local release verification was performed on Linux; the repository includes PowerShell usage examples, but this release does not claim a completed native-Windows execution test.

## Agent tools

| Tool | Integration level | Boundary |
|---|---|---|
| Codex | Native `AGENTS.md` guidance | Contextual guidance, not enforcement |
| Claude Code | `CLAUDE.md` imports `AGENTS.md`; optional lifecycle hooks | Hook configuration must be reviewed and activated by the user |
| Other coding agents | Can read Markdown continuity files | Auto-discovery behavior varies by tool |

OpenAI documents `AGENTS.md` as a repository guidance mechanism for navigation, test commands, and project conventions. Claude Code documents project `CLAUDE.md`, file imports, and lifecycle hooks. Product behavior can change, so re-check official documentation before relying on exact hook schemas in a future release.

## Git

Git is optional for basic continuity. Snapshot output reports `is_repository: false` when the root is not a repository. When Git is present, only aggregate change counts, branch, and a short commit hash are captured.
