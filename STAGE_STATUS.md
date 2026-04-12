# CoQuery Stage Status Report

Version: v0.7.0
Last Update: 2026-04-12

## Current Status

```text
SQLite-first baseline verified
Explicit write contract frozen
Shared DB URI contract implemented
PostgreSQL schema, schema_detail, query, insert, update, and delete smoke proved
PostgreSQL direct join generation smoke proved for `generate join_inner` and `generate join_left` slices
Codex skill package added for agent-side reuse
JPA entity source introspection added as an ORM/model track
Schema-detail direct join generation proved for built-in join skills
GitHub Actions workflow files added for baseline and PostgreSQL smoke automation
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
- `query`
- `generate`
- `insert`
- `update`
- `delete`
- `natural`
- `jpa_schema`
- `provider_add`
- `provider_list`
- `provider_remove`
- `provider_test`

Write-command baseline:

- `insert`, `update`, and `delete` require `--write` and explicit SQL
- full-table `update` and `delete` return a high-risk warning

## Backend Support

| Backend | Status | Notes |
|---------|--------|-------|
| SQLite | Working | current verified runtime path |
| PostgreSQL | Experimental (narrow read + write) | local smoke proof succeeded for `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete`, plus direct `generate join_inner` / `generate join_left` slices; broader backend support is still not proven |
| MySQL | Stub | URI contract exists; runtime returns structured placeholder error |

CI note:

- GitHub Actions workflow files now exist for baseline and PostgreSQL smoke automation
- this session did not observe a live GitHub runner result yet

ORM/model support:

| Track | Status | Notes |
|-------|--------|-------|
| JPA | Experimental source introspection | `jpa_schema` scans annotation-based entity source; JPQL runtime execution is not implemented |

Natural-language note:

- heuristic by default
- registered-provider routing exists as a secondary experimental track

## Verification Commands

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 sql_cli/tests/test_core.py
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
bash scripts/run_postgresql_local_smoke.sh
```

## Active Loop

1. observe the first GitHub Actions baseline and PostgreSQL smoke runs and fix runner drift if needed
2. align docs to executable behavior
3. keep the PostgreSQL smoke runner repeatable and repo-managed
4. keep `skills/coquery-cli` aligned with runnable CLI behavior
5. keep JPA labelled as ORM/model support until JPQL runtime proof exists
6. do not broaden join-generation claims beyond direct schema-detail foreign-key inference without a new proof slice

Last Updated: 2026-04-12
Phase Status: SQLite-first baseline verified with PostgreSQL schema, schema_detail, query, insert, update, delete, and direct `generate join_inner` / `generate join_left` smoke proof plus agent skill packaging, JPA source introspection, direct schema-detail join inference, and added GitHub Actions baseline / PostgreSQL smoke workflows
