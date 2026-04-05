# CoQuery PostgreSQL Local Smoke

Date: 2026-04-05

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## Purpose

Record one repeatable local PostgreSQL smoke path that proves CoQuery can run `schema`, `query`, and one write-safe `insert` against a real non-SQLite backend.

This is a narrow probe environment, not the default baseline runtime.

## Environment used

- PostgreSQL binaries: `/Users/Agent/homebrew/opt/postgresql@18/bin`
- temporary Python venv: `/Users/Agent/ps-workspace/CoQuery/.tmp/pg-venv`
- temporary cluster dir: `/Users/Agent/ps-workspace/CoQuery/.tmp/pg-smoke`
- temporary socket dir: `/Users/Agent/ps-workspace/CoQuery/.tmp/pg-socket`
- port: `49251`
- database: `coquery_probe`

## Recommended runner

Use:

```bash
bash scripts/run_postgresql_local_smoke.sh
```

This script:

- checks `PATH` for PostgreSQL binaries first
- falls back to known Homebrew paths when needed
- creates the probe virtualenv if needed
- installs `psycopg[binary]`
- initializes a temporary local PostgreSQL cluster
- starts PostgreSQL on a non-default port
- seeds a `users` table
- runs CoQuery `schema`, `query`, and `insert`
- stops the cluster when finished

## Observed commands and results

### Schema proof

```bash
/Users/Agent/ps-workspace/CoQuery/.tmp/pg-venv/bin/python main.py \
  --command schema \
  --db-uri "postgresql://localhost/coquery_probe?host=/Users/Agent/ps-workspace/CoQuery/.tmp/pg-socket&port=49251" \
  --format json
```

Observed output:

```json
{
  "ok": true,
  "command": "schema",
  "data": {
    "tables": [
      "users"
    ]
  },
  "error": null
}
```

### Query proof

```bash
/Users/Agent/ps-workspace/CoQuery/.tmp/pg-venv/bin/python main.py \
  --command query \
  --db-uri "postgresql://localhost/coquery_probe?host=/Users/Agent/ps-workspace/CoQuery/.tmp/pg-socket&port=49251" \
  --sql "SELECT name, age FROM users ORDER BY id LIMIT 5" \
  --format json
```

Observed output:

```json
{
  "ok": true,
  "command": "query",
  "data": {
    "rows": [
      [
        "probe_user",
        34
      ]
    ]
  },
  "error": null
}
```

### Insert proof

```bash
/Users/Agent/ps-workspace/CoQuery/.tmp/pg-venv/bin/python main.py \
  --command insert \
  --db-uri "postgresql://localhost/coquery_probe?host=/Users/Agent/ps-workspace/CoQuery/.tmp/pg-socket&port=49251" \
  --write \
  --sql "INSERT INTO users (name, age) VALUES ('insert_probe_user', 45)" \
  --format json
```

Observed output:

```json
{
  "ok": true,
  "command": "insert",
  "data": {
    "affected_rows": 1,
    "warnings": [],
    "safety_level": "low"
  },
  "error": null
}
```

## Interpretation

What is proven:

- PostgreSQL URI handling works with a real target
- PostgreSQL connection succeeds when `psycopg[binary]` is available
- `schema` works against a real PostgreSQL database
- `query` works against a real PostgreSQL database
- `insert` works against a real PostgreSQL database with the baseline write contract

What is not proven yet:

- PostgreSQL `update` and `delete`
- PostgreSQL natural-language flows
- CI-backed PostgreSQL automation
- stable one-command bootstrap inside the default developer baseline

## Current status effect

This supports:

- PostgreSQL status: `experimental`
- proven scope: `schema`, `query`, and `insert`

This does not justify claiming broad multi-DB completion.
