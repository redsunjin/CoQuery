# CoQuery MySQL Status Decision

Date: 2026-04-05

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## Purpose

Freeze the truthful status label for MySQL after PostgreSQL became the first real non-SQLite proof track.

## Decision

Keep MySQL labelled as:

`stub`

Do not downgrade it to `planned`.

## Why `stub` is more accurate than `planned`

Current code already includes:

- `mysql://` URI recognition
- shared backend validation through `--db-uri`
- a bounded `unsupported_backend` response path

That means MySQL is not merely an idea.
It has a placeholder runtime boundary, even though it is not implemented as a working backend.

## What `stub` means here

For CoQuery, `stub` means:

- the backend is recognized by the command surface
- the CLI can identify it and respond predictably
- real execution is not implemented yet

This is the current MySQL state.

## What MySQL does not have

MySQL still lacks:

- real connection implementation
- structured missing-driver and connection-failure behavior
- schema proof
- query proof
- write proof

So `stub` does not mean supported.
It only means the placeholder boundary exists.

## Product interpretation

This decision keeps product language honest:

- PostgreSQL is the first real non-SQLite backend
- MySQL remains intentionally behind it
- MySQL should not receive feature claims or roadmap weight beyond placeholder status

## Persona checkpoint

- Planner: keeps focus on one backend at a time
- Developer: avoids deleting useful placeholder boundaries just to simplify wording
- Manager: prevents overstating MySQL while still describing the code truthfully
- QA: preserves a stable negative-path expectation for MySQL URIs

## Next follow-up

The next MySQL-related slice should only happen if one of these becomes true:

1. PostgreSQL still justifies keeping MySQL behind the current narrow proof track
2. a dedicated MySQL implementation slice is intentionally opened
3. a real MySQL smoke path is ready to gate any status promotion
