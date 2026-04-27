# CoQuery v0.7.0 Stabilization Snapshot

## Release Information

**Version**: v0.7.0  
**Date**: 2026-04-23
**Status**: Stabilized CLI baseline

## Features

### Verified CLI Commands

```text
schema
schema_detail
doctor
query
generate
insert
update
delete
natural
jpa_schema
db_knowledge
provider_add
provider_list
provider_remove
provider_test
```

### New in v0.7.0

**SQLite-first CLI baseline:**
- `main.py` routes through `sql_cli/cli.py`
- SQLite schema, query, generation, natural-language, and explicit write paths are verified
- `schema_detail` exposes normalized schema metadata
- write commands require `--write` and explicit SQL
- `--dry-run`, `--max-affected-rows`, and full-table write rejection are verified

**Experimental PostgreSQL proof:**
- `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` smoke paths are verified
- schema-detail-validated `generate select_simple` and `generate count_simple` are verified with generated SQL execution
- direct `generate join_inner` and `generate join_left` are verified
- write-safety guards are verified against a real PostgreSQL target

**Agent and automation support:**
- Codex skill package lives under `skills/coquery-cli`
- `coquery_agent.py` supports `describe`, `verify`, `demo`, `run`, and `install-skill`
- GitHub Actions `baseline` and `postgresql-smoke` are verified

## Installation

```bash
git clone https://github.com/redsunjin/CoQuery.git
cd CoQuery
python3 main.py --command schema --db example.db
```

## Commands

```bash
# List tables
python3 main.py --command schema --db example.db

# Execute query
python3 main.py --command query --db example.db --sql "SELECT * FROM users"

# Generate SQL
python3 main.py --command generate --db example.db --skill select_simple

# Insert data
python3 main.py --command insert --db example.db --write --sql "INSERT INTO users (name, age) VALUES ('a', 20)"

# Update data
python3 main.py --command update --db example.db --write --sql "UPDATE users SET age = 21 WHERE id = 1"

# Delete data
python3 main.py --command delete --db example.db --write --sql "DELETE FROM users WHERE id = 1"

# Natural language
python3 main.py --command natural --sql "count users"
```

## Test Results

| Test Suite | Status |
|------------|--------|
| Baseline tests | 96/96 passing |
| Agent wrapper verify | passing |
| Local PostgreSQL smoke | passing |
| GitHub Actions baseline | success on 2026-04-23 UTC for `022d89f` |
| GitHub Actions postgresql-smoke | success on 2026-04-23 UTC for `022d89f` |

## Release Notes

### v0.7.0 stabilization snapshot (2026-04-23)
- SQLite-first CLI baseline is verified
- PostgreSQL remains experimental and smoke-proven only for documented slices
- MySQL remains a stub
- JPA support is source introspection only
- Public repository usage and GitHub Actions log demo path are documented in `USAGE_AND_DEMO.md`

## Next Release

**v0.8.0 Planned**:
- decide the next PostgreSQL verification slice before widening claims
- keep GitHub Actions `baseline` and `postgresql-smoke` green
- consider a hosted or browser-facing demo only after CLI proof remains stable
- keep docs aligned with observed proof

## Credits

**Repository**: [redsunjin/CoQuery](https://github.com/redsunjin/CoQuery)  
**License**: MIT  
**Status**: v0.7.0 stabilized CLI baseline
