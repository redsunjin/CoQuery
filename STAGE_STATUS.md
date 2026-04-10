# CoQuery Stage Status Report

Version: v0.7.0
Last Update: 2026-04-10

## Current Status

```text
SQLite-first baseline verified
Explicit write contract frozen
Shared DB URI contract implemented
PostgreSQL schema, query, insert, update, and delete smoke proved
Codex skill package added for agent-side reuse
JPA entity source introspection added as an ORM/model track
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
| Phase 5 | Early experimental | PostgreSQL `schema`, `query`, `insert`, `update`, and `delete` smoke succeeded; broader backend support is not proven |

## Verified Commands

- `schema`
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
| PostgreSQL | Experimental (narrow read + write) | local smoke proof succeeded for `schema`, `query`, `insert`, `update`, and `delete`; broader backend support is still not proven |
| MySQL | Stub | URI contract exists; runtime returns structured placeholder error |

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

1. align docs to executable behavior
2. keep the PostgreSQL smoke runner repeatable and repo-managed
3. keep `skills/coquery-cli` aligned with runnable CLI behavior
4. keep JPA labelled as ORM/model support until JPQL runtime proof exists
5. use the verification matrix before changing any broader multi-DB status claim

Last Updated: 2026-04-10
Phase Status: SQLite-first baseline verified with PostgreSQL schema, query, insert, update, and delete smoke proof plus agent skill packaging and JPA source introspection
