# Migration Guide

## From chat-only handoffs

1. Run `awc init` in preview mode.
2. Review the proposed scope and protected boundaries.
3. Apply the scaffold.
4. Move only current, evidence-backed facts into `status.md`.
5. Put inherited claims under “Existing, not re-verified”.
6. Write one exact next action in `handoff.md`.
7. Do not paste the full conversation into the repository.

## From an existing AGENTS.md

The installer will not replace it. A proposal is written under `.agent/local/proposals/`.

Recommended merge:

- retain existing build, test, code-style, and architecture rules;
- add the startup protocol and evidence discipline;
- remove personal preferences that belong in user-level configuration;
- keep the merged file concise;
- retain the AWC profile marker only after accepting the scaffold’s profile boundary.

## From an existing CLAUDE.md

Do not discard Claude-specific rules. Add `@AGENTS.md` outside code blocks, then keep truly Claude-specific instructions below it. Remove duplicated cross-agent rules after comparison.

## From a large memory folder

Do not bulk-import it. Triage each item:

| Existing item | Destination |
|---|---|
| Stable project rule | `AGENTS.md` |
| Current verified fact | `.agent/status.md` verified section |
| Old or uncertain fact | `.agent/status.md` inherited section |
| Immediate next action | `.agent/handoff.md` |
| Active multi-step execution | optional `.agent/plan.md` |
| Durable architecture choice | optional `.agent/decisions.md` |
| Personal preference | user-level tool configuration, not this repository |
| Transcript or raw log | do not import by default |

## From project to umbrella

Do not switch in place automatically. Project and umbrella profiles grant different scope. Create a separate preview, compare the rules, and manually decide which root should coordinate child projects.
