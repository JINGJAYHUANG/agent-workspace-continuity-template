# Evidence Model

Continuity fails when repeated statements are mistaken for verified facts. AWC therefore treats evidence status as a first-class field.

## Three states

### Verified this session

A claim belongs here only when the current session checked it against an authoritative source, such as:

- a file that was actually read;
- a command whose output was observed;
- a test that ran and completed;
- an official document inspected on a recorded date;
- a human confirmation explicitly given in the current task.

A useful entry includes the evidence location or validation command.

### Existing, not re-verified

This section holds inherited state that may still be useful but was not checked now. Examples include an earlier handoff, an old report, a prior agent summary, or an unconfirmed branch status.

The wording is intentional: inherited state is not automatically false, but it is not safe to present as current truth.

### Unknowns and risks

Use this section for missing evidence, conflicting sources, assumptions, stale timestamps, unresolved permissions, and protected boundaries.

## Promotion rule

A claim moves from inherited to verified only after a current check. Copying it into a new file, repeating it in chat, or having two agents agree does not count as verification.

## Demotion rule

A formerly verified claim should be moved back to inherited or risk status when:

- its source is no longer available;
- the relevant system may have changed;
- a later observation conflicts with it;
- its verification date is outside the task’s freshness requirement.

## Handoff contract

A handoff should answer six questions:

1. What is the current objective?
2. What was actually verified?
3. What changed?
4. What is blocked?
5. What is the next exact action?
6. What validation was run?

It should not become a full transcript or a personal memory store.
