<!-- awc:profile=project schema=1 -->
# Workspace Brief

**Workspace:** synthetic_project
**Profile:** project
**Generated:** 2026-08-28

## Purpose

Maintain a recoverable, evidence-labeled working context for this project without depending on chat history or cloud memory.

## In scope

- Project code, tests, documentation, data contracts, and tracked decisions.
- The minimum context needed to resume work safely.
- Commands and evidence required to verify material project state.

## Out of scope

- Personal profiles or long-term personal memory.
- Credentials, tokens, customer records, private communications, and unrelated projects.
- Global machine configuration unless the project explicitly owns it.

## Constraints

- Local-first and tool-agnostic.
- Existing project files are never overwritten by the scaffold without explicit human action.
- Inherited facts remain unverified until checked in the current session.
- Tracked state must remain portable and free of absolute user paths.

## Acceptance criteria

- A new session can identify the objective, verified state, blockers, risks, and next action from the continuity files.
- `awc doctor` reports no structural or privacy errors.
- Re-running the installer is idempotent and preserves edited AWC-managed state.
