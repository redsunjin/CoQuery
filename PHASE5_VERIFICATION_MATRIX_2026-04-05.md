# CoQuery Phase 5 Verification Matrix

Date: 2026-04-05

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
| SQLite | `natural` | yes | yes | working baseline | heuristic NL path only |
| PostgreSQL | URI detection | yes | yes | stub | `postgresql://` URIs are parsed and validated |
| PostgreSQL | missing driver error | yes | yes | stub | returns `driver_not_installed` when `psycopg` is unavailable |
| PostgreSQL | connection failure error | yes | yes | stub | returns `connection_failed` on connect failure |
| PostgreSQL | `schema` against real DB | yes | yes | experimental | verified in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| PostgreSQL | `query` against real DB | yes | yes | experimental | verified in `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md` |
| MySQL | URI detection | yes | yes | stub | `mysql://` scheme is recognized and validated |
| MySQL | runtime execution | no | yes | stub | returns structured `unsupported_backend` placeholder |

## 4. Current interpretation

What this matrix means today:

- SQLite is the only backend with broad proof across multiple command types
- PostgreSQL is `experimental` for the narrow `schema` and `query` paths
- MySQL is still a placeholder backend and should not be described as supported
- broader PostgreSQL support is still unproven beyond the documented smoke

## 5. PostgreSQL promotion rule

PostgreSQL moved from `stub` to `experimental` because all of the following are true:

1. `psycopg[binary]` dependency path is documented
2. one PostgreSQL target is available for local verification
3. `schema` succeeds through `--db-uri postgresql://...`
4. one verification command is recorded in this matrix
5. at least one repeatable smoke note exists

The next promotion beyond this should require more than one command family and less ad hoc setup.

## 6. MySQL policy

MySQL should remain behind PostgreSQL in priority.

Use these rules:

- do not claim MySQL support before PostgreSQL has broader working proof
- do not add MySQL-specific docs beyond placeholder status unless a dedicated slice starts
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
- `query`

against a real local PostgreSQL target.

## 8. Current status note

The first real PostgreSQL smoke result is recorded in:

- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`

Current limits:

- the proof uses a dedicated local probe environment
- writes are not proven
- the probe depends on local PostgreSQL binaries outside the repo

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
3. keep PostgreSQL scope narrow until another command family is proven
