# CoQuery Handoff v0.7.0

Date: 2026-04-10

## Current Handoff State

CoQuery is no longer in emergency repair.
The verified state is now a working SQLite-first CLI baseline.

## Verified Baseline

- `main.py` is a thin entry point that routes to `sql_cli/cli.py`
- the executable command set is `schema`, `query`, `generate`, `insert`, `update`, `delete`, `natural`, `jpa_schema`, `provider_add`, `provider_list`, `provider_remove`, and `provider_test`
- `python3 sql_cli/tests/test_core.py` passes with 54 baseline tests
- `python3 main.py --help` works in the current environment
- `CoQueryDB` works for SQLite file paths and `sqlite://` URIs
- `--db-uri` is now the shared multi-backend connection contract
- write commands require explicit `--write` confirmation and explicit SQL
- PostgreSQL `schema`, `query`, `insert`, `update`, and `delete` have verified local smoke results

## What You Can Rely On

- SQLite schema inspection
- SQLite query execution
- shared DB URI parsing with structured backend errors
- SQL generation from the built-in skill set
- explicit write handlers for `insert`, `update`, and `delete`
- repo-local LLM provider registration and connectivity checks
- lightweight natural-language intent-to-SQL conversion with optional registered provider routing
- JPA annotation-based entity source introspection through `jpa_schema`
- inspectable SQL/JPA knowledge coverage through `db_knowledge --topic coverage`
- structured write results with `affected_rows`, `warnings`, and `safety_level`

## What Is Not Complete

- broad PostgreSQL support
- MySQL support
- production-grade natural-language behavior
- provider-backed natural as a primary product track
- JPQL runtime execution or Spring Data JPA integration
- a stable multi-DB interface

## Important Cautions

- `query` blocks non-`SELECT` SQL unless `--write` is provided
- `insert`, `update`, and `delete` require both `--write` and explicit SQL
- `update` and `delete` surface a high-risk warning when no `WHERE` clause exists
- `natural` is heuristic by default and can optionally route through a registered provider
- provider-backed natural is currently a secondary experimental track, not the primary loop
- PostgreSQL is proven only for narrow `schema`, `query`, `insert`, `update`, and `delete` paths through local smoke runs
- MySQL URIs return a structured `unsupported_backend` placeholder error
- JPA support is source introspection only and does not execute JPQL

## Official Next Work

1. Keep top-level docs aligned with the verified baseline
2. Keep the PostgreSQL smoke runner repeatable and repo-managed
3. Use the verification matrix and scope lock to gate any broader Phase 5 claim changes

Current runner note:

- `bash scripts/run_postgresql_local_smoke.sh` now checks `PATH` for PostgreSQL binaries before falling back to Homebrew-specific paths

## Key Files

- `main.py`
- `sql_cli/cli.py`
- `sql_cli/db_new.py`
- `sql_cli/core.py`
- `sql_cli/nl_core.py`
- `sql_cli/tests/test_core.py`
- `STATUS_AUDIT_2026-04-04.md`
- `STABILIZATION_PLAN_2026-04-04.md`
- `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`
- `MYSQL_PROBE_REQUIREMENTS_2026-04-09.md`
- `PROVIDER_TRACK_DECISION_2026-04-09.md`
- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`
- `POSTGRESQL_SCOPE_LOCK_2026-04-07.md`

## Recommended Verification

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 sql_cli/tests/test_core.py
python3 -c "import sql_cli.cli, sql_cli.core, sql_cli.db_new"
python3 main.py --command db_knowledge --topic coverage
bash scripts/run_postgresql_local_smoke.sh
```

Last Updated: 2026-04-10
Status: SQLite-first baseline verified with PostgreSQL schema, query, insert, update, delete smoke proof, and DB knowledge coverage reporting
Next: keep the PostgreSQL probe harness stable and decide whether the current narrow proof set is enough before broadening further
