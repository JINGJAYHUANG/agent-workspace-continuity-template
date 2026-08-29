<!-- awc:profile=umbrella schema=1 -->
# Agent Workspace Rules

## Workspace identity

This directory is the coordination root for **synthetic_umbrella**. It is an umbrella workspace, not a monorepo and not permission to inspect every descendant.

## Startup protocol

Before new work:

1. Read this file and `CLAUDE.md` when the current agent uses it.
2. Read `.agent/brief.md`, `.agent/status.md`, and `.agent/handoff.md`.
3. Identify the smallest relevant child workspace before opening files or running commands.
4. Read `.agent/plan.md` and `.agent/decisions.md` only when they exist and apply at umbrella scope.
5. Verify child-project state from that child workspace; do not infer it from umbrella notes.

## Evidence discipline

- Do not rely on chat history alone.
- Keep **verified this session**, **existing but not re-verified**, and **unknown** claims separate.
- Umbrella status may name an active child directory, but deep technical details belong in that child workspace.
- Never promote inherited child-project claims to verified without checking their authoritative files.

## Scope and safety

- Do not recursively scan the umbrella root by default.
- Narrow every task to an explicitly relevant child directory.
- Do not assume instruction inheritance into deep child directories; add child-local rules only when needed.
- Do not store secrets, personal memory, account tokens, customer data, or machine-specific paths in tracked continuity files.
- Treat `.agent/local/`, `.agent/logs/`, `.agent/backups/`, and `.agent/runtime-snapshot.json` as local state.
- Preserve existing files. For conflicting scaffolds, create a proposal instead of overwriting.

## State update protocol

- Keep `.agent/status.md` limited to umbrella coordination facts.
- Update `.agent/handoff.md` before ending substantial umbrella-level work.
- Use `.agent/plan.md` only for a real cross-project plan.
- Use `.agent/decisions.md` only for durable umbrella architecture or governance choices.
- Move deep blockers, implementation notes, and test evidence into the relevant child workspace.
