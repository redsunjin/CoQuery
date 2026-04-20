# CoQuery Stage Status Report

Version: v0.7.0
Last Update: 2026-04-20

## Current Status

```text
SQLite-first baseline verified
Explicit write contract frozen
Shared DB URI contract implemented
Doctor diagnostics implemented and verified
PostgreSQL schema, schema_detail, query, insert, update, and delete smoke proved
PostgreSQL direct join generation smoke proved for `generate join_inner` and `generate join_left` slices
Codex skill package added for agent-side reuse
JPA entity source introspection added as an ORM/model track
Schema-detail direct join generation proved for built-in join skills
GitHub Actions `baseline` and `postgresql-smoke` succeeded on 2026-04-12
Phase 5 remains narrow and experimental
```

## Phase Overview

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0 | Complete | CLI recovery and command routing are working |
| Phase 1 | Complete enough | `schema` and `query` work on SQLite |
| Phase 2 | Complete enough | structured SQL generation works for built-in skills |
| Phase 3 | Baseline stabilized | explicit `--write` plus explicit SQL is enforced |
| Phase 4 | In stabilization | natural-language path is heuristic by default and can optionally use a registered provider |
| Phase 5 | Early experimental | PostgreSQL `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`, and direct `generate join_inner` / `generate join_left` smoke slices succeeded; broader backend support is not proven |

## Verified Commands

- `schema`
- `schema_detail`
- `doctor`
- `query`
- `generate`
- `insert`
- `update`
- `delete`
- `natural`
- `jpa_schema`
- `db_knowledge`
- `provider_add`
- `provider_list`
- `provider_remove`
- `provider_test`

Write-command baseline:

- `insert`, `update`, and `delete` require `--write` and explicit SQL
- `insert`, `update`, `delete`, and write-mode `query` support `--dry-run` preview with rollback
- `insert`, `update`, `delete`, and write-mode `query` support `--max-affected-rows` rollback guards
- full-table `update`, `delete`, and write-mode `query` statements fail closed unless `--allow-full-table-write` is provided

## Backend Support

| Backend | Status | Notes |
|---------|--------|-------|
| SQLite | Working | current verified runtime path |
| PostgreSQL | Experimental (narrow read + write) | local smoke proof succeeded for `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete`, plus direct `generate join_inner` / `generate join_left` slices; broader backend support is still not proven |
| MySQL | Stub | URI contract exists; runtime returns structured placeholder error |

CI note:

- GitHub Actions workflow files now exist for baseline and PostgreSQL smoke automation
- the first observed runs for `baseline` and `postgresql-smoke` both succeeded on 2026-04-12

ORM/model support:

| Track | Status | Notes |
|-------|--------|-------|
| JPA | Experimental source introspection | `jpa_schema` scans annotation-based entity source; JPQL runtime execution is not implemented |

Natural-language note:

- heuristic by default
- registered-provider routing exists as a secondary experimental track

Doctor note:

- readiness checks include parsed target, driver availability, connection probe, and schema probe where applicable
- PostgreSQL diagnostics classify common failure modes such as `auth_failed`, `database_not_found`, `host_unreachable`, `connection_refused`, `timeout`, and `ssl_error`

## Verification Commands

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 main.py --command doctor --db example.db --format json
python3 sql_cli/tests/test_core.py
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
bash scripts/run_postgresql_local_smoke.sh
```

## Active Loop

1. keep the GitHub Actions `baseline` and `postgresql-smoke` workflows green
2. align docs to executable behavior
3. keep the PostgreSQL smoke runner repeatable and repo-managed
4. keep `skills/coquery-cli` aligned with runnable CLI behavior
5. keep JPA labelled as ORM/model support until JPQL runtime proof exists
6. do not broaden join-generation claims beyond direct schema-detail foreign-key inference without a new proof slice

Last Updated: 2026-04-20
Phase Status: SQLite-first baseline verified with `doctor`, PostgreSQL schema, schema_detail, query, insert, update, delete, and direct `generate join_inner` / `generate join_left` smoke proof plus agent skill packaging, JPA source introspection, explicit write safety guards, direct schema-detail join inference, and verified GitHub Actions baseline / PostgreSQL smoke workflows
