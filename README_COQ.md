# CoQuery Baseline Verification

Date: 2026-04-05

## Result

```text
35/35 executable baseline tests pass
SQLite-first CLI verified
Explicit write contract verified
Shared DB URI contract verified
PostgreSQL schema, query, insert, update, and delete smoke verified
```

## Verified Commands

- `schema`
- `query`
- `generate`
- `insert`
- `update`
- `delete`
- `natural`

## Support Matrix

| Area | Status | Notes |
|------|--------|-------|
| SQLite CLI path | Working | current verified runtime |
| PostgreSQL | Experimental (narrow read + write) | local smoke proof succeeded for `schema`, `query`, `insert`, `update`, and `delete` |
| MySQL | Stub | returns structured placeholder error |
| Write contract | Working baseline | `--write` plus explicit SQL is enforced |
| DB URI contract | Working baseline | `--db-uri` is available and validated |
| Phase 5 verification matrix | Working baseline | backend promotion is now proof-gated |
| PostgreSQL schema smoke | Working baseline | local proof recorded on 2026-04-05 |
| PostgreSQL query smoke | Working baseline | local proof recorded on 2026-04-05 |
| PostgreSQL insert smoke | Working baseline | local proof recorded on 2026-04-05 |
| PostgreSQL update smoke | Working baseline | local proof recorded on 2026-04-07 |
| PostgreSQL delete smoke | Working baseline | local proof recorded on 2026-04-08 |
| Docs example smoke | Working baseline | key documented CLI examples are exercised in tests |
| Natural language | Baseline only | heuristic intent mapping |

## Verification Commands

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema --db-uri sqlite:///Users/Agent/ps-workspace/CoQuery/example.db --format json
python3 sql_cli/tests/test_core.py
bash scripts/run_postgresql_local_smoke.sh
```

## Notes

- `query` is read-only unless `--write` is set
- dedicated `insert`, `update`, and `delete` handlers require `--write` and explicit SQL
- full-table `update` and `delete` return a high-risk warning
- `--db-uri` is preferred for future multi-backend commands
- `natural` currently emits simple fixed SQL patterns
- the PostgreSQL smoke runner checks `PATH` for PostgreSQL binaries before falling back to known Homebrew paths

Version: v0.7.0
Last Updated: 2026-04-10
Status: Baseline verified with experimental PostgreSQL schema, query, insert, update, and delete proof
Reference: `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`
Smoke Result: `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`
