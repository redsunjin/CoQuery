# CoQuery Roadmap

Version: v0.7.x stabilization
Last Updated: 2026-04-05

## Current Position

CoQuery currently has a verified SQLite-first baseline.

The roadmap should be read conservatively:

- SQLite baseline: working
- write path: baseline stabilized
- natural-language path: assistive, lightweight
- multi-DB: early experimental

## Phase Overview

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0 | Complete | CLI recovery and baseline routing are working |
| Phase 1 | Complete enough | `schema` and `query` are usable on SQLite |
| Phase 2 | Complete enough | built-in SQL generation works for baseline skills |
| Phase 3 | Baseline stabilized | explicit write contract is enforced |
| Phase 4 | In stabilization | NL path exists but is heuristic and not advanced |
| Phase 5 | Early experimental | PostgreSQL `schema` and `query` have local smoke proof; broader backend support is not complete |

## Official Active Loop

The current roadmap priority is:

1. keep docs aligned with executable behavior
2. keep PostgreSQL claims limited to what the smoke result actually proves
3. keep the PostgreSQL smoke runner repeatable before widening backend claims

## Current Stabilization Outputs

- `STATUS_AUDIT_2026-04-04.md`
- `STABILIZATION_PLAN_2026-04-04.md`
- `WRITE_COMMAND_CONTRACT_2026-04-05.md`
- `PERSONA_REVIEW_2026-04-05.md`
- `MULTI_DB_ENTRY_CRITERIA_2026-04-05.md`
- `BACKEND_CONNECTION_CONTRACT_2026-04-05.md`
- `POSTGRESQL_PROBE_REQUIREMENTS_2026-04-05.md`
- `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`
- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`

## Next Roadmap Slices

### Slice A. Shared backend contract

Goal:

- define one backend selector and one DB URI contract for SQLite, PostgreSQL, and MySQL

Current decision:

- use `--db-uri` as the primary future multi-DB contract
- keep `--db` only as legacy SQLite compatibility during stabilization
- use PostgreSQL as the first non-SQLite probe
- runtime validation for `--db-uri` and structured backend errors is now implemented

### Slice B. Driver dependency declaration

Goal:

- document required packages and failure behavior when PostgreSQL/MySQL drivers are unavailable

Current decision:

- PostgreSQL is the first driver path to document
- first probe uses `psycopg[binary]`
- MySQL stays later and should not split the first probe
- PostgreSQL missing-driver and connection-failure wording is now implemented

### Slice C. First real Phase 5 probe

Goal:

- implement one backend path and prove it with one real command and one real verification step

Current decision:

- PostgreSQL is the first probe target
- first proof command should be PostgreSQL `schema` via `--db-uri`
- a local smoke path is now documented
- the first successful PostgreSQL `schema` smoke is now recorded

### Slice D. PostgreSQL query proof

Goal:

- extend PostgreSQL evidence from `schema` to one real `query` path

Current result:

- the first PostgreSQL `query` smoke is now recorded
- the repo-managed smoke runner now exercises both `schema` and `query`

### Slice E. Verification-gated backend promotion

Goal:

- move backend labels only when the verification matrix justifies it

## Multi-DB Phase Boundary

Phase 5 should not be described as active implementation until:

- backend selection contract exists
- dependency expectations are written
- unavailable-driver errors are defined
- one verification matrix exists

Phase 5 should still be treated as narrow and experimental until more than the current PostgreSQL read path is proven.
