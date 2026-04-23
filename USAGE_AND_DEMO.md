# CoQuery Usage and Demo

Date: 2026-04-23

## Current Saved Result

- Repository: `redsunjin/CoQuery`
- Repository URL: `https://github.com/redsunjin/CoQuery`
- Visibility: `PUBLIC` as verified through GitHub on 2026-04-23
- Current saved commit: `4be8a3d Add PostgreSQL write safety smoke proof`
- Current branch: `main`
- Latest observed GitHub Actions result: `baseline` and `postgresql-smoke` succeeded on 2026-04-22 UTC for commit `4be8a3d36f9c30f922f2ce30d21e4056cdd7bb57`

The project state is stored in the repository, not only in chat context. The main context and result files are:

- `HANDOFF.md`
- `STAGE_STATUS.md`
- `PROJECT_SUMMARY.md`
- `README_COQ.md`
- `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`
- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`
- `POSTGRESQL_SCOPE_LOCK_2026-04-07.md`
- `skills/coquery-cli/`

## Local Use

From the repository root:

```bash
python3 main.py --help
python3 sql_cli/tests/test_core.py
```

Inspect SQLite schema and data:

```bash
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command query --db example.db --sql "SELECT * FROM users LIMIT 10" --format json
```

Generate SQL:

```bash
python3 main.py --command generate --db example.db \
  --skill select_simple \
  --params '{"table":"users","cols":["id","name"]}' \
  --format json
```

Preview a write without committing:

```bash
python3 main.py --command insert --db example.db --write --dry-run \
  --sql "INSERT INTO users (name, age) VALUES ('preview', 20)" \
  --format json
```

Use the agent wrapper:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py describe
python3 skills/coquery-cli/scripts/coquery_agent.py verify
python3 skills/coquery-cli/scripts/coquery_agent.py demo
```

## GitHub Demo

CoQuery is currently a CLI project, not a hosted browser app. GitHub can still run a practical log-based demo through Actions.

Run the baseline demo:

1. Open `https://github.com/redsunjin/CoQuery`
2. Go to `Actions`
3. Select `baseline`
4. Select `Run workflow`
5. Read the run log for `coquery_agent.py verify` and `coquery_agent.py demo`

Run the PostgreSQL proof:

1. Open `Actions`
2. Select `postgresql-smoke`
3. Select `Run workflow`
4. Read the run log for the PostgreSQL schema/query/generate/write-safety smoke proof

## Current Boundary

- SQLite is the working baseline.
- PostgreSQL is experimental and limited to the documented smoke-proven paths.
- MySQL remains a stub.
- JPA support is source introspection only.
- GitHub Pages or a hosted web UI has not been added yet.
