# CoQuery Handoff v0.7.1

Date: 2026-07-09

## Current Handoff State

CoQuery is no longer in emergency repair.
The verified state is now a working SQLite-first CLI baseline.
The reduced cleanup PR was closed unmerged; current `main` remains the active line with DB/JPA knowledge retained.
The last recorded GitHub Actions proof is merge commit `20e5d8f` on `origin/main`.
The GitHub repository `redsunjin/CoQuery` is public as verified on 2026-04-23.

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
- PostgreSQL write-safety smoke verifies `--dry-run`, `--max-affected-rows`, and full-table write rejection against a real target
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
- real PostgreSQL smoke proof for write-safety rollback and guard paths
- repo-local GitHub Actions workflows for baseline and PostgreSQL smoke automation
- Last recorded GitHub Actions `baseline` and `postgresql-smoke` proof succeeded on 2026-07-09 UTC for `main` commit `20e5d8f`
- structured write results with `affected_rows`, `warnings`, and `safety_level`
- GitHub Actions can be used as a log-based demo through manual `workflow_dispatch` runs of `baseline` and `postgresql-smoke`

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
- Training/Production Assist mode separation is implemented at the Command API and terminal-shell level
- Production Assist Safety Gate is implemented with read-only profiles, reviewed SQL approval, SELECT-only execution, and JSONL audit logging
- Release Candidate Hardening is implemented with `npm run rc:verify` as the one-command launch check
- non-iOS local packaging is local web app first, with `python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765` as the stable start command
- PostgreSQL is proven only for narrow `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` paths, write-safety guard slices, `generate select_simple`, `generate count_simple`, and direct `generate join_inner` / `generate join_left` slices through local smoke runs
- `doctor` classifies common PostgreSQL failures such as `auth_failed`, `database_not_found`, `host_unreachable`, `connection_refused`, `timeout`, and `ssl_error`
- MySQL URIs return a structured `unsupported_backend` placeholder error
- JPA support is source introspection only and does not execute JPQL
- GitHub Actions proof has only been observed for the committed `baseline` and `postgresql-smoke` workflows so far
- no GitHub Pages, hosted browser demo, Tauri wrapper, or Electron wrapper exists yet

## Post-Merge Release Checkpoint

- PR #4 (`Harden CoQuery release candidate shell`) was merged into `main` on 2026-07-09.
- Merge commit: `20e5d8f77eaee455755060a4428dc32a98950723`.
- Local release-candidate verification passed with `npm run rc:verify` after the merge.
- GitHub Actions `baseline` and `postgresql-smoke` both succeeded on `main` for merge commit `20e5d8f`.

## Official Next Work

1. Prepare the `v0.8.0` release tag and release notes if publication is requested.
2. Keep the GitHub Actions `baseline` and `postgresql-smoke` workflows green.
3. Keep top-level docs aligned with the verified baseline and post-merge release checkpoint.
4. Use the verification matrix and scope lock to gate any broader Phase 5 claim changes.
5. Do not broaden join-generation claims beyond direct schema-detail foreign-key inference without a new proof slice.
6. If feature work resumes before release tagging, choose the next PostgreSQL verification slice first.

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
- `USAGE_AND_DEMO.md`
- `SCOPE_DECISION_2026-04-10.md`
- `docs/desktop-local-packaging-decision.md`
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
python3 tests/rc_hardening_smoke.py
npm run rc:verify
python3 tests/local_packaging_decision_smoke.py
bash scripts/run_postgresql_local_smoke.sh
```

Last Updated: 2026-07-09
Status: SQLite-first baseline verified with `doctor`, PostgreSQL schema, schema_detail, query, insert, update, delete, write-safety guard, schema-detail-validated `generate select_simple` / `generate count_simple`, and direct `generate join_inner` / `generate join_left` smoke proof, local DB knowledge-first planning, schema-detail-aware identifier validation, explicit write safety guards, direct schema-detail join inference, Training/Production Assist mode separation, Desktop/Local Packaging Decision, Production Assist Safety Gate, Release Candidate Hardening, and verified GitHub Actions baseline / PostgreSQL smoke workflows
Next: prepare the `v0.8.0` release tag/notes or choose the next PostgreSQL verification slice
