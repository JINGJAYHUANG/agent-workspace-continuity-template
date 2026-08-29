# Claude Code Hooks

**Compatibility checked:** 2026-08-29 against the current Claude Code memory and hook references.

The hook example is optional. AWC works without it because the tracked files remain the source of truth.

## Why the adapter is thin

Claude Code loads `CLAUDE.md` as persistent project context and supports importing `AGENTS.md` with `@AGENTS.md`. The tracked instructions are context rather than hard enforcement, so the adapter keeps them concise and leaves security enforcement to settings, permissions, sandboxing, or dedicated blocking hooks.

Official references:

- Memory and instruction loading: https://code.claude.com/docs/en/memory
- Hook lifecycle and schemas: https://code.claude.com/docs/en/hooks

## Events used

| Event | AWC behavior | Raw content stored? | Decision control? |
|---|---|---:|---:|
| `SessionStart` | Inject a recovery summary through `additionalContext` | No event content | No |
| `PostCompact` | Store summary length and hash prefix | No | None supported |
| `Stop` | Store final-message length/hash and `stop_hook_active` | No | Deliberately omitted |
| `SessionEnd` | Store a sanitized reason enum | No | None supported |

The current official SessionStart sources include `startup`, `resume`, `clear`, `compact`, and `fork`. PostCompact triggers are `manual` and `auto`. The settings example includes these values.

## Activation

`awc init --with-claude-hooks --apply` creates:

```text
.claude/hooks/continuity_hook.py
.claude/continuity.settings.example.json
```

The settings file is an example and is not activated automatically. Review it, then merge the `hooks` object into the appropriate trusted Claude settings file.

## Privacy behavior

The event log is stored at:

```text
.agent/local/hook-events.jsonl
```

This path is ignored by the scaffold. Rows may contain:

- event type;
- UTC timestamp;
- hash prefix of a session identifier;
- content length and hash prefix;
- controlled source/reason values;
- a boolean indicating whether a Stop hook was already active.

Rows never contain the prompt, compact summary, final assistant message, transcript path, working directory, model output, or environment values.

## Loop prevention

Claude Stop hooks can ask Claude to continue. The AWC hook does not return `decision: block`, a `reason`, or Stop `additionalContext`; it emits an empty JSON object. This makes the Stop event observational only.

## Fail-open boundary

Every hook invocation catches its own exceptions and exits successfully. A failed continuity log should not prevent a developer from starting or ending a coding session.
