# CoQuery Phase 5 Verification Matrix

Date: 2026-04-22

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Define one conservative verification matrix for multi-DB progress claims.

This document exists so CoQuery can describe backend status from proof, not from intent.

## 2. Status labels

Use these meanings consistently:

- `working`: real runtime path verified and repeatable
- `experimental`: one real backend command works, but coverage is still narrow
- `stub`: contract or placeholder path exists, but real backend execution is not yet proven
- `planned`: backend work is intended, but no meaningful path is available yet

## 3. Current matrix

| Backend | Command | Runtime proof | Test proof | Status | Notes |
|---------|---------|---------------|------------|--------|-------|
| SQLite | `schema` | yes | yes | working | `python3 main.py --command schema --db example.db --format json` |
| SQLite | `query` | yes | yes | working | baseline read query path verified |
| SQLite | `insert/update/delete` | yes | yes | working | explicit `--write`, warnings, and `affected_rows` verified |
| SQLite | `natural` | yes | yes | working baseline | heuristic by default; optional registered provider path exists |
| PostgreSQL | URI detection | yes | yes | stub | `postgresql://` URIs are parsed and validated |
| PostgreSQL | missing driver error | yes | yes | stub | returns `driver_not_installed` when `psycopg` is unavailable |
| PostgreSQL | connection failure error | yes | yes | stub | returns `connection_failed` on connect failure |
| PostgreSQL | `schema` against real DB | yes | yes | experimental | verified in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| PostgreSQL | `schema_detail` against real DB | yes | yes | experimental | verified in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| PostgreSQL | `query` against real DB | yes | yes | experimental | verified in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| PostgreSQL | `insert` against real DB | yes | yes | experimental | verified in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| PostgreSQL | `update` against real DB | yes | yes | experimental | verified in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| PostgreSQL | `delete` against real DB | yes | yes | experimental | verified in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| PostgreSQL | `generate select_simple` against real DB schema detail | yes | yes | experimental | generated SQL is executed in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| PostgreSQL | `generate count_simple` against real DB schema detail | yes | yes | experimental | generated SQL is executed in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| PostgreSQL | direct `generate join_inner` / `generate join_left` against real DB schema detail | yes | yes | experimental | generated SQL is executed in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| MySQL | URI detection | yes | yes | stub | `mysql://` scheme is recognized and validated |
| MySQL | runtime execution | no | yes | stub | returns structured `unsupported_backend` placeholder |

## 4. Current interpretation

What this matrix means today:

- SQLite is the only backend with broad proof across multiple command types
- PostgreSQL is `experimental` for the narrow `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` paths plus `generate select_simple`, `generate count_simple`, and direct join generation slices
- MySQL is still a placeholder backend and should not be described as supported
- broader PostgreSQL support is still unproven beyond the documented smoke

## 5. PostgreSQL promotion rule

PostgreSQL moved from `stub` to `experimental` because all of the following are true:

1. `psycopg[binary]` dependency path is documented
2. one PostgreSQL target is available for local verification
3. `schema` succeeds through `--db-uri postgresql://...`
4. one verification command is recorded in this matrix
5. at least one repeatable smoke note exists

The next promotion beyond this should require more than one command family and a less ad hoc probe path.

## 6. MySQL policy

MySQL should remain behind PostgreSQL in priority.

Use these rules:

- do not claim MySQL support before PostgreSQL has broader working proof
- MySQL-specific docs may define dependency expectations, but must not imply runtime support without proof
- keep MySQL labelled `stub` or `planned` until real proof exists

Current decision:

- MySQL stays `stub`
- reason: URI recognition and structured placeholder behavior already exist

## 7. Verified PostgreSQL smoke runner

The current repeatable local proof is:

```bash
bash scripts/run_postgresql_local_smoke.sh
```

This runner proves:

- `schema`
- `schema_detail`
- `query`
- `insert`
- `update`
- `delete`
- schema-detail-validated `generate select_simple` and `generate count_simple`, with generated SQL execution
- direct `generate join_inner` and `generate join_left`, with generated SQL execution

against a real local PostgreSQL target.

Runner behavior:

- checks `PATH` for PostgreSQL binaries first
- falls back to known Homebrew paths when needed
- still allows `POSTGRES_BIN_DIR` as an explicit override

## 8. Current status note

The first real PostgreSQL smoke result is recorded in:

- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`

Current limits:

- the proof still uses a dedicated local probe environment
- only selected generation slices are proven
- the probe still depends on local PostgreSQL binaries outside the repo

## 9. Persona checkpoint

This matrix supports the four persona views:

- Planner: keeps product ambition smaller than proof
- Developer: narrows backend growth to one proven slice at a time
- Manager: avoids overstating maturity
- QA: turns backend claims into explicit verification rows

## 10. Next follow-up

The next slice after this matrix should be:

1. make the PostgreSQL probe environment less ad hoc
2. keep MySQL at `stub` until a dedicated proof track exists
3. decide whether the current PostgreSQL proof set is enough before broadening further

The current scope freeze is recorded in:

- `POSTGRESQL_SCOPE_LOCK_2026-04-07.md`
