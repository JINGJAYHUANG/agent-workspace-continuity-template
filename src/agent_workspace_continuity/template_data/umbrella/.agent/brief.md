<!-- awc:profile=umbrella schema=1 -->
# Workspace Brief

**Workspace:** ${WORKSPACE_NAME}
**Profile:** umbrella
**Generated:** ${GENERATED_DATE}

## Purpose

Coordinate continuity across several child workspaces while preserving their independent scope, instructions, evidence, and history.

## In scope

- Umbrella-level routing, protected boundaries, and identification of active child workspaces.
- Cross-project dependencies and durable coordination decisions.
- The minimum context needed to choose where deeper work belongs.

## Out of scope

- Recursive inventory of every descendant.
- Deep implementation details, data, strategies, or blockers owned by one child workspace.
- Personal memory, credentials, runtime configuration, archives, and unrelated subsystems.

## Constraints

- Local-first and tool-agnostic.
- Start broad only long enough to choose a child workspace; then narrow scope.
- Do not assume deep agents automatically inherit umbrella instructions.
- Existing files are never overwritten by the scaffold without explicit human action.

## Acceptance criteria

- A new session can identify the umbrella purpose and the next child workspace to inspect.
- Deep project state is not copied into umbrella status by default.
- `awc doctor` reports no structural or privacy errors.
