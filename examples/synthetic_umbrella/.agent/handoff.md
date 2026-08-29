<!-- awc:state=handoff schema=1 -->
# Handoff

**Last updated:** 2026-08-29T00:00:00Z

## Current objective

Select one child workspace based on the next task.

## Last verified state

- The umbrella has exactly two synthetic first-level workspaces.

## Changes made

- Added fictional child directories without importing deep state.

## Blockers

- The next user task has not selected a child workspace.

## Next exact action

- Match the next task to `analytics-lab` or `docs-site`, then inspect only that child.

## Validation

- `awc doctor . --strict`
