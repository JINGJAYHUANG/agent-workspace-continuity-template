<!-- awc:state=decisions schema=1 -->
# Decision Log

**Last updated:** 2026-08-28T22:57:52Z

Record only durable decisions. Use one section per decision and preserve superseded entries.

## Decision 001 — Adopt local evidence-labeled continuity

- **Status:** accepted
- **Date:** 2026-08-28
- **Context:** Coding-agent sessions need recoverable project context without treating chat history as proof.
- **Decision:** Use concise tracked rules plus `.agent/` state files; keep local event metadata ignored by Git.
- **Consequences:** State updates require explicit evidence labels and regular handoffs.
- **Supersedes:** none
