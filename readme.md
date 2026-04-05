# CoQuery CLI

CoQuery currently provides a verified SQLite-first CLI baseline.
Phase 5 multi-DB support is now early experimental and is not complete.

## Available Commands

```bash
python3 main.py --command schema --db example.db
python3 main.py --command schema --db-uri sqlite:///Users/Agent/ps-workspace/CoQuery/example.db
python3 main.py --command query --db example.db --sql "SELECT * FROM users"
python3 main.py --command generate --db example.db --skill select_simple
python3 main.py --command insert --db example.db --write --sql "INSERT INTO users (name, age) VALUES ('a', 20)"
python3 main.py --command update --db example.db --write --sql "UPDATE users SET age = 21 WHERE id = 1"
python3 main.py --command delete --db example.db --write --sql "DELETE FROM users WHERE id = 1"
python3 main.py --command natural --db example.db --sql "show users"
```

## Verified Baseline

- `main.py` routes to the package handlers in `sql_cli/cli.py`
- `python3 sql_cli/tests/test_core.py` passes with 32 tests
- SQLite is the working backend
- `--db-uri` is the preferred multi-backend connection contract
- `query` is read-only unless `--write` is provided
- `insert`, `update`, and `delete` require both `--write` and explicit SQL

## Current Limits

- PostgreSQL is experimental for the documented `schema` and `query` probe paths only
- MySQL is a stub with a structured placeholder error
- write commands do not yet have dry-run or transaction support
- natural-language support is lightweight and heuristic

## Recommended Verification

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 sql_cli/tests/test_core.py
bash scripts/run_postgresql_local_smoke.sh
```

Version: v0.7.0
Last Updated: 2026-04-05
Status: SQLite-first baseline verified with experimental PostgreSQL schema and query proof
