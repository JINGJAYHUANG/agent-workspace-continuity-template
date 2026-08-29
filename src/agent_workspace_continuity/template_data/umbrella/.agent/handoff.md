<!-- awc:state=handoff schema=1 -->
# Handoff

**Last updated:** ${GENERATED_AT}

## Current objective

Establish safe umbrella routing without scanning every child workspace.

## Last verified state

- The umbrella continuity scaffold exists.
- No child-project claims have been verified yet.

## Changes made

- Added the minimum umbrella coordination files.

## Blockers

- The primary active child workspace is not yet identified.

## Next exact action

- List only first-level candidate child directories, choose the relevant one, and audit it separately.

## Validation

- Run `awc doctor . --strict` after umbrella-specific edits.
