<!-- awc:profile=project schema=1 -->
# Agent Workspace Rules

## Workspace identity

This directory is the authoritative root for **synthetic_project**. Treat it as one scoped project, not as a general machine-level memory store.

## Startup protocol

Before new work:

1. Read this file and `CLAUDE.md` when the current agent uses it.
2. Read `.agent/brief.md`, `.agent/status.md`, and `.agent/handoff.md`.
3. Read `.agent/plan.md` and `.agent/decisions.md` only when they exist and are relevant.
4. Inspect the current repository or workspace state before trusting inherited claims.
5. Return the current objective, verified state, unresolved risks, and next concrete action before broad changes.

## Evidence discipline

- Do not rely on chat history alone.
- Keep **verified this session**, **existing but not re-verified**, and **unknown** claims separate.
- Never promote an inherited claim to verified without checking an authoritative source.
- Record commands, tests, dates, and source locations that support material claims.
- Mark estimates, assumptions, and planned work explicitly.

## Scope and safety

- Work inside this project unless the task explicitly requires another location.
- Do not scan parent directories, home folders, credentials, caches, or unrelated projects by default.
- Do not store secrets, personal memory, account tokens, customer data, or machine-specific paths in tracked continuity files.
- Treat `.agent/local/`, `.agent/logs/`, `.agent/backups/`, and `.agent/runtime-snapshot.json` as local state.
- Preserve existing files. For conflicting scaffolds, create a proposal instead of overwriting.

## State update protocol

- Update `.agent/status.md` when verified facts or known risks change.
- Update `.agent/handoff.md` before ending substantial work.
- Create or update `.agent/plan.md` only for an active multi-step plan.
- Record durable architectural choices in `.agent/decisions.md`; do not use it as a diary.
- Keep state concise enough that a new session can recover without reading the entire repository.
