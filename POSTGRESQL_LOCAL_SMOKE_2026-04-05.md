# CoQuery PostgreSQL Local Smoke

Date: 2026-04-18

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## Purpose

Record one repeatable local PostgreSQL smoke path that proves CoQuery can run `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` against a real non-SQLite backend, plus direct schema-detail `join_inner` and `join_left` generation slices.

This is a narrow probe environment, not the default baseline runtime.

## Environment used

- PostgreSQL binaries: `/Users/Agent/homebrew/opt/postgresql@18/bin`
- temporary Python venv: `/Users/Agent/ps-workspace/CoQuery/.tmp/pg-venv`
- temporary cluster dir: `/Users/Agent/ps-workspace/CoQuery/.tmp/pg-smoke`
- temporary socket dir: per-run directory under `/Users/Agent/ps-workspace/CoQuery/.tmp/pg-socket.*`
- port: prefers `49251`, but auto-selects a free port when needed unless `COQUERY_PG_PORT` is set
- database: `coquery_probe`

## Recommended runner

Use:

```bash
bash scripts/run_postgresql_local_smoke.sh
```

This script:

- prefers PostgreSQL binaries from `PATH` first
- falls back to known Homebrew paths when needed
- creates the probe virtualenv if needed
- installs `psycopg[binary]`
- initializes a temporary local PostgreSQL cluster
- creates a per-run socket directory to avoid stale-socket collisions
- starts PostgreSQL on a non-default port and auto-picks a free port when the preferred one is busy
- seeds `users`, `orgs`, and `members` probe tables
- runs CoQuery `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete`
- runs `generate join_inner` and `generate join_left` against real PostgreSQL schema detail and executes the generated join SQL
- supports `COQUERY_PG_DB_URI` for an external PostgreSQL target and `COQUERY_PG_RESET=1` to reinitialize the local probe cluster
- prints PostgreSQL log-tail diagnostics when startup or smoke execution fails
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

### Direct join-generation proof

```bash
/Users/Agent/ps-workspace/CoQuery/.tmp/pg-venv/bin/python main.py \
  --command generate \
  --db-uri "postgresql://localhost/coquery_probe?host=/Users/Agent/ps-workspace/CoQuery/.tmp/pg-socket&port=49251" \
  --skill join_inner \
  --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' \
  --format json
```

Observed output:

```json
{
  "ok": true,
  "command": "generate",
  "sql": "SELECT MEMBERS.EMAIL, ORGS.NAME FROM MEMBERS JOIN ORGS ON MEMBERS.ORG_ID = ORGS.ID",
  "schema_validation": {
    "status": "validated",
    "backend": "postgresql"
  },
  "error": null
}
```

Generated SQL verification query output:

```json
{
  "ok": true,
  "command": "query",
  "data": {
    "rows": [
      [
        "join_probe_member@example.com",
        "join_probe_org"
      ]
    ]
  },
  "error": null
}
```

### Direct left-join-generation proof

```bash
/Users/Agent/ps-workspace/CoQuery/.tmp/pg-venv/bin/python main.py \
  --command generate \
  --db-uri "postgresql://localhost/coquery_probe?host=/Users/Agent/ps-workspace/CoQuery/.tmp/pg-socket&port=49251" \
  --skill join_left \
  --params '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}' \
  --format json
```

Observed output:

```json
{
  "ok": true,
  "command": "generate",
  "sql": "SELECT ORGS.NAME, MEMBERS.EMAIL FROM ORGS LEFT JOIN MEMBERS ON MEMBERS.ORG_ID = ORGS.ID",
  "schema_validation": {
    "status": "validated",
    "backend": "postgresql"
  },
  "error": null
}
```

Generated SQL verification query output:

```json
{
  "ok": true,
  "command": "query",
  "data": {
    "rows": [
      [
        "join_probe_org",
        "join_probe_member@example.com"
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

### Update proof

```bash
/Users/Agent/ps-workspace/CoQuery/.tmp/pg-venv/bin/python main.py \
  --command update \
  --db-uri "postgresql://localhost/coquery_probe?host=/Users/Agent/ps-workspace/CoQuery/.tmp/pg-socket&port=49251" \
  --write \
  --sql "UPDATE users SET age = 52 WHERE name = 'update_probe_user'" \
  --format json
```

Observed output:

```json
{
  "ok": true,
  "command": "update",
  "data": {
    "affected_rows": 1,
    "warnings": [],
    "safety_level": "low"
  },
  "error": null
}
```

### Delete proof

```bash
/Users/Agent/ps-workspace/CoQuery/.tmp/pg-venv/bin/python main.py \
  --command delete \
  --db-uri "postgresql://localhost/coquery_probe?host=/Users/Agent/ps-workspace/CoQuery/.tmp/pg-socket&port=49251" \
  --write \
  --sql "DELETE FROM users WHERE name = 'delete_probe_user'" \
  --format json
```

Observed output:

```json
{
  "ok": true,
  "command": "delete",
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
- `schema_detail` works against a real PostgreSQL database
- `query` works against a real PostgreSQL database
- `insert` works against a real PostgreSQL database with the baseline write contract
- `update` works against a real PostgreSQL database with the baseline write contract
- `delete` works against a real PostgreSQL database with the baseline write contract
- direct `generate join_inner` and `generate join_left` inference work against real PostgreSQL schema detail when exactly one direct foreign-key path exists

What is not proven yet:

- PostgreSQL natural-language flows
- broad PostgreSQL generation parity
- multi-hop or alias-aware join generation
- stable one-command bootstrap inside the default developer baseline

Automation note:

- `.github/workflows/postgresql-smoke.yml` now exists and runs this smoke path against an external PostgreSQL service URI
- GitHub Actions `postgresql-smoke` succeeded on 2026-04-12 through PR `#3`
- this document still records the local smoke proof plus the first observed CI-backed run of the same smoke path

## Current status effect

This supports:

- PostgreSQL status: `experimental`
- proven scope: `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`, and direct `generate join_inner` / `generate join_left` slices

This does not justify claiming broad multi-DB completion.
