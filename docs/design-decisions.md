# Design Decisions

## ADR-001 — Markdown is the canonical state format

**Status:** accepted

Markdown is readable by humans, Claude Code, Codex, IDEs, and Git without a service dependency. The trade-off is weaker schema enforcement, addressed by `awc doctor`.

## ADR-002 — Rules and state are separate

**Status:** accepted

`AGENTS.md` contains stable operating rules. `.agent/` contains changing project state. Mixing them would make every task rewrite the instruction file and increase drift.

## ADR-003 — CLAUDE.md imports AGENTS.md

**Status:** accepted

A thin adapter prevents duplicated cross-agent rules. Claude-specific notes may follow the import. This is also more portable on Windows than requiring a symlink.

## ADR-004 — The installer is preview-first

**Status:** accepted

A scaffold that overwrites existing project instructions creates more risk than it removes. `--apply` is required, and conflict proposals are written under ignored local state.

## ADR-005 — Optional files remain optional

**Status:** accepted

Empty `plan.md` and `decisions.md` create false ceremony. They are generated only when requested and should exist only while they carry useful state.

## ADR-006 — Recovery is bounded and deterministic

**Status:** accepted

The same source files produce the same recovery brief, excluding explicit state edits. A character bound prevents continuity context from consuming an unbounded portion of the model context window.

## ADR-007 — Hook logs are content-free

**Status:** accepted

Lengths and hash prefixes support operational checks without storing raw prompts or responses. A user who needs full observability should choose a separate, explicitly governed telemetry system.

## ADR-008 — Runtime has zero third-party dependencies

**Status:** accepted

The core uses only the Python standard library. This reduces installation friction and supply-chain exposure for a tool designed to run inside many projects.

## ADR-009 — Project and umbrella profiles are distinct

**Status:** accepted

A project root grants a narrow working scope. An umbrella root is only a router to independent children. Switching profiles requires manual review because silently changing this boundary could broaden agent access.
