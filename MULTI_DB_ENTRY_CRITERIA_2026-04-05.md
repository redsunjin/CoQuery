# CoQuery Multi-DB Entry Criteria

Date: 2026-04-05

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Define the real gate for entering Phase 5.

This document exists to stop CoQuery from describing multi-database support as "ready" before there is runtime proof.

The goal of this slice is not to implement PostgreSQL or MySQL.
The goal is to define what must be true before Phase 5 can honestly begin.

## 2. Current truthful state

As of this document:

- SQLite is the only broadly verified backend
- PostgreSQL has narrow experimental `schema` and `query` probes
- PostgreSQL is not implemented as a broad working runtime path
- MySQL is not implemented as a working runtime path
- multi-DB remains an early experimental phase, not a complete capability

## 3. Phase language

Use these words consistently:

- `working`: command executes in the current environment
- `experimental`: code path exists, but verification is partial
- `planned`: no verified runtime path yet
- `complete`: runtime, tests, and docs all agree

For Phase 5 today, the correct label is:

`early experimental`

## 4. Phase 5 may start only when all entry criteria are defined

Before Phase 5 implementation begins, the project must define all of the following:

### Dependency declaration

- the required PostgreSQL driver
- the required MySQL driver
- installation expectations for local development
- failure behavior when a driver is missing

### Shared connection contract

- one backend selector contract
- one database URI or equivalent connection contract
- one rule for choosing SQLite vs PostgreSQL vs MySQL

### Backend status model

Each backend must be marked as one of:

- `working`
- `experimental`
- `stub`
- `not implemented`

Do not collapse these into a single "supported" label.

### Error model

The runtime must define structured errors for:

- unavailable driver
- invalid backend selection
- invalid connection string
- unsupported command/backend combination
- connection failure

### Test path

Before a backend can move beyond `planned`, there must be:

- at least one real command path
- at least one real test or smoke command
- at least one documented verification command

## 5. Minimum implementation gate for Phase 5

Phase 5 implementation may begin only when the repository has:

1. one written dependency declaration
2. one written backend selection contract
3. one written multi-DB error contract
4. one written verification matrix

Without those four items, Phase 5 is still pre-entry planning.

## 6. Minimum evidence required to claim progress inside Phase 5

### PostgreSQL

To describe PostgreSQL as `experimental`, all of the following must be true:

- dependency is declared
- one connection path runs
- `schema` or `query` works against a real PostgreSQL target
- one verification command is documented

### MySQL

To describe MySQL as `experimental`, all of the following must be true:

- dependency is declared
- one connection path runs
- `schema` or `query` works against a real MySQL target
- one verification command is documented

If those conditions are not met, use:

- `stub` if placeholders exist
- `planned` if no meaningful runtime path exists

## 7. Verification matrix requirement

The first real multi-DB slice must publish a simple matrix like this:

| Backend | Command | Runtime proof | Test proof | Status |
|---------|---------|---------------|------------|--------|
| SQLite | `schema` | yes | yes | working |
| PostgreSQL | `schema` | no/yes | no/yes | planned/experimental |
| MySQL | `schema` | no/yes | no/yes | planned/experimental |

This matrix should be updated only from real verification, not intention.

## 8. Non-goals

This slice does not require:

- a unified optimizer
- natural-language multi-DB support
- write support across all backends
- cross-backend parity
- production deployment claims

## 9. Persona checkpoint

At the Phase 5 boundary, apply the four persona questions:

- Planner: does multi-DB serve the real product now, or only ambition?
- Developer: is the backend contract simpler than the implementation pressure?
- Manager: are we calling a scaffold "support" too early?
- QA: what exact command proves each backend works?

The answer should be conservative unless runtime evidence exists.

## 10. Next follow-up

The next stabilization slice after this document should be:

1. define the shared backend selection and DB URI contract
2. document dependency expectations for PostgreSQL and MySQL
3. decide whether MySQL begins as `stub` or `planned`
