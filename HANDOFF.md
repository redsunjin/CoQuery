# CoQuery Handoff v0.7.0

Date: 2026-04-22

## Current Handoff State

CoQuery is no longer in emergency repair.
The verified state is now a working SQLite-first CLI baseline.
The reduced cleanup PR was closed unmerged; current `main` remains the active line with DB/JPA knowledge retained.

## Verified Baseline

- `main.py` is a thin entry point that routes to `sql_cli/cli.py`
- the executable command set is `schema`, `schema_detail`, `doctor`, `query`, `generate`, `insert`, `update`, `delete`, `natural`, `jpa_schema`, `db_knowledge`, `provider_add`, `provider_list`, `provider_remove`, and `provider_test`
- `python3 sql_cli/tests/test_core.py` passes with 96 baseline tests
- `python3 main.py --help` works in the current environment
- `CoQueryDB` works for SQLite file paths and `sqlite://` URIs
- `--db-uri` is now the shared multi-backend connection contract
- `doctor` reports masked targets, readiness checks, and classified PostgreSQL connection failures
- write commands require explicit `--write` confirmation and explicit SQL
- PostgreSQL `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` have verified local smoke results
- PostgreSQL `generate select_simple` and `generate count_simple` have verified local smoke results with generated SQL execution
- PostgreSQL direct `generate join_inner` and `generate join_left` inference have verified local smoke results with generated SQL execution
- Latest local PostgreSQL smoke re-run succeeded on 2026-04-22
- `schema_detail` exposes normalized columns, keys, indexes, constraints, and SQLite create SQL
- `generate` and simple `natural` requests validate basic identifiers against `schema_detail`
- `generate` can infer one-step join conditions from `schema_detail` foreign keys and constraints when both tables are inspectable

## What You Can Rely On

- SQLite schema inspection
- SQLite schema-detail inspection
- SQLite query execution
- shared DB URI parsing with structured backend errors
- masked connection diagnostics through `doctor`
- SQL generation from the built-in skill set
- explicit write handlers for `insert`, `update`, and `delete`, with optional `--dry-run` preview and `--max-affected-rows` guard
- full-table write rejection for `update`, `delete`, and write-mode `query` unless `--allow-full-table-write` is provided
- repo-local LLM provider registration and connectivity checks
- lightweight natural-language intent-to-SQL conversion with local knowledge first and optional registered provider fallback
- JPA annotation-based entity source introspection through `jpa_schema`
- inspectable SQL/JPA knowledge coverage through `db_knowledge --topic coverage`
- inspectable schema-detail topic through `db_knowledge --topic schema_detail`
- local DB/JPA knowledge context attached to generation, natural, and write planning
- schema-detail-backed table and simple column validation for covered generation and natural requests
- schema-detail-backed direct join inference for `join_inner` and `join_left`
- schema-detail-backed validation of qualified columns in explicit join `ON` clauses
- real PostgreSQL smoke proof for schema-detail-validated `generate select_simple` and `generate count_simple` slices
- real PostgreSQL smoke proof for direct `generate join_inner` and `generate join_left` slices
- repo-local GitHub Actions workflows for baseline and PostgreSQL smoke automation
- GitHub Actions `baseline` and `postgresql-smoke` succeeded on 2026-04-20 UTC for `main` commit `e9c98be`
- structured write results with `affected_rows`, `warnings`, and `safety_level`

## What Is Not Complete

- broad PostgreSQL support
- MySQL support
- production-grade natural-language behavior
- provider-backed natural as a primary product track
- JPQL runtime execution or Spring Data JPA integration
- a stable multi-DB interface
- relationship-aware SQL generation beyond direct foreign-key joins

## Important Cautions

- `query` blocks non-`SELECT` SQL unless `--write` is provided
- `insert`, `update`, and `delete` require both `--write` and explicit SQL
- `insert`, `update`, and `delete` can run with `--dry-run` to preview affected rows without committing changes
- `insert`, `update`, `delete`, and write-mode `query` can fail closed with `--max-affected-rows`
- `update`, `delete`, and write-mode `query` statements without `WHERE` fail closed unless `--allow-full-table-write` is provided
- `natural` is heuristic by default, skips provider calls for simple covered requests, and can optionally route complex requests through a registered provider
- provider-backed natural is currently a secondary experimental track, not the primary loop
- PostgreSQL is proven only for narrow `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` paths plus `generate select_simple`, `generate count_simple`, and direct `generate join_inner` / `generate join_left` slices through local smoke runs
- `doctor` classifies common PostgreSQL failures such as `auth_failed`, `database_not_found`, `host_unreachable`, `connection_refused`, `timeout`, and `ssl_error`
- MySQL URIs return a structured `unsupported_backend` placeholder error
- JPA support is source introspection only and does not execute JPQL
- GitHub Actions proof has only been observed for the committed `baseline` and `postgresql-smoke` workflows so far

## Official Next Work

1. Keep the GitHub Actions `baseline` and `postgresql-smoke` workflows green
2. Keep top-level docs aligned with the verified baseline
3. Use the verification matrix and scope lock to gate any broader Phase 5 claim changes
4. Do not broaden join-generation claims beyond direct schema-detail foreign-key inference without a new proof slice

Current runner note:

- `bash scripts/run_postgresql_local_smoke.sh` now checks `PATH` for PostgreSQL binaries before falling back to Homebrew-specific paths

## Key Files

- `main.py`
- `sql_cli/cli.py`
- `sql_cli/db_new.py`
- `sql_cli/core.py`
- `sql_cli/nl_core.py`
- `sql_cli/knowledge_planner.py`
- `sql_cli/tests/test_core.py`
- `STATUS_AUDIT_2026-04-04.md`
- `STABILIZATION_PLAN_2026-04-04.md`
- `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`
- `MYSQL_PROBE_REQUIREMENTS_2026-04-09.md`
- `PROVIDER_TRACK_DECISION_2026-04-09.md`
- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`
- `POSTGRESQL_SCOPE_LOCK_2026-04-07.md`
- `SCOPE_DECISION_2026-04-10.md`
- `.github/workflows/baseline.yml`
- `.github/workflows/postgresql-smoke.yml`

## Recommended Verification

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command doctor --db example.db --format json
python3 main.py --command generate --db example.db --skill select_simple --params '{"table":"users","cols":["id","name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_inner --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' --format json
python3 sql_cli/tests/test_core.py
python3 -c "import sql_cli.cli, sql_cli.core, sql_cli.db_new"
python3 main.py --command db_knowledge --topic coverage
bash scripts/run_postgresql_local_smoke.sh
```

Last Updated: 2026-04-22
Status: SQLite-first baseline verified with `doctor`, PostgreSQL schema, schema_detail, query, insert, update, delete, schema-detail-validated `generate select_simple` / `generate count_simple`, and direct `generate join_inner` / `generate join_left` smoke proof, local DB knowledge-first planning, schema-detail-aware identifier validation, explicit write safety guards, direct schema-detail join inference, and verified GitHub Actions baseline / PostgreSQL smoke workflows
Next: keep workflows green, keep docs aligned, and avoid broadening join-generation claims beyond direct schema-detail foreign-key inference
