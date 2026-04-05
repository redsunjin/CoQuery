# CoQuery Stage Status Report

Version: v0.7.0
Last Update: 2026-04-05

## Current Status

```text
SQLite-first baseline verified
Explicit write contract frozen
Shared DB URI contract implemented
PostgreSQL schema, query, and insert smoke proved
Phase 5 remains narrow and experimental
```

## Phase Overview

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0 | Complete | CLI recovery and command routing are working |
| Phase 1 | Complete enough | `schema` and `query` work on SQLite |
| Phase 2 | Complete enough | structured SQL generation works for built-in skills |
| Phase 3 | Baseline stabilized | explicit `--write` plus explicit SQL is enforced |
| Phase 4 | In stabilization | natural-language path exists, but it is heuristic only |
| Phase 5 | Early experimental | PostgreSQL `schema`, `query`, and `insert` smoke succeeded; broader backend support is not proven |

## Verified Commands

- `schema`
- `query`
- `generate`
- `insert`
- `update`
- `delete`
- `natural`

Write-command baseline:

- `insert`, `update`, and `delete` require `--write` and explicit SQL
- full-table `update` and `delete` return a high-risk warning

## Backend Support

| Backend | Status | Notes |
|---------|--------|-------|
| SQLite | Working | current verified runtime path |
| PostgreSQL | Experimental (narrow read + insert) | local smoke proof succeeded for `schema`, `query`, and `insert`; broader write coverage is not proven |
| MySQL | Stub | URI contract exists; runtime returns structured placeholder error |

## Verification Commands

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 sql_cli/tests/test_core.py
bash scripts/run_postgresql_local_smoke.sh
```

## Active Loop

1. align docs to executable behavior
2. keep the PostgreSQL smoke runner repeatable and repo-managed
3. use the verification matrix before changing any broader multi-DB status claim

Last Updated: 2026-04-05
Phase Status: SQLite-first baseline verified with PostgreSQL schema, query, and insert smoke proof
