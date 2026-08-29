<!-- awc:state=handoff schema=1 -->
# Handoff

**Last updated:** 2026-08-29T00:00:00Z

## Current objective

Publish the synthetic parser example as release evidence.

## Last verified state

- Two parser tests pass.
- The project continuity profile is structurally healthy.

## Changes made

- Added a fictional parser, fixtures, tests, and evidence-labeled state.

## Blockers

- No blockers for the synthetic example.

## Next exact action

- Run the parent repository release validator.

## Validation

- `python -m unittest discover -s tests -v`
- `awc doctor . --strict`
