# CoQuery CLI

CoQuery currently provides a verified SQLite-first CLI baseline.
Phase 5 multi-DB support is now early experimental and is not complete.

## Available Commands

```bash
python3 main.py --command schema --db example.db
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command schema --db-uri sqlite:///Users/Agent/ps-workspace/CoQuery/example.db
python3 main.py --command query --db example.db --sql "SELECT * FROM users"
python3 main.py --command generate --db example.db --skill select_simple
python3 main.py --command insert --db example.db --write --sql "INSERT INTO users (name, age) VALUES ('a', 20)"
python3 main.py --command update --db example.db --write --sql "UPDATE users SET age = 21 WHERE id = 1"
python3 main.py --command delete --db example.db --write --sql "DELETE FROM users WHERE id = 1"
python3 main.py --command natural --db example.db --sql "show users"
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
python3 main.py --command db_knowledge --dialect sqlite --topic schema
python3 main.py --command db_knowledge --topic write_safety
python3 main.py --command db_knowledge --topic coverage
python3 main.py --command provider_list
python3 main.py --command provider_test --provider-name local_ollama
```

## Verified Baseline

- `main.py` routes to the package handlers in `sql_cli/cli.py`
- `python3 sql_cli/tests/test_core.py` passes with 67 tests
- SQLite is the working backend
- `--db-uri` is the preferred multi-backend connection contract
- `query` is read-only unless `--write` is provided
- `insert`, `update`, and `delete` require both `--write` and explicit SQL
- provider registry commands are available for optional `natural` fallback routing
- `jpa_schema` can inspect annotation-based JPA entity source as an ORM/model context
- `db_knowledge` can retrieve local SQL/JPA dialect and write-safety rules before using an LLM/provider
- `schema_detail` exposes normalized columns, keys, indexes, constraints, and SQLite create SQL for agent-side knowledge use
- `generate` and simple `natural` requests validate table and simple column identifiers against `schema_detail`
- generation, natural-language, and write-planning paths attach local DB/JPA knowledge context first

## Agent Skill

CoQuery can now be used as a Codex skill through `skills/coquery-cli`.

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py verify
python3 skills/coquery-cli/scripts/coquery_agent.py demo
python3 skills/coquery-cli/scripts/coquery_agent.py run --command schema --db example.db
python3 skills/coquery-cli/scripts/coquery_agent.py run --command schema_detail --db example.db --table users
python3 skills/coquery-cli/scripts/coquery_agent.py run --command db_knowledge --dialect jpql --topic parameters
```

The skill is also installable under `~/.codex/skills/coquery-cli` for `$coquery-cli` discovery in future Codex sessions.

The skill includes a compact DB knowledge seed at `skills/coquery-cli/references/db-knowledge.md`.
Structured machine-readable rules and coverage metadata now live under `knowledge/`.
This is enough for basic SQL/JPA boundary decisions, deterministic lookup, normalized schema-detail lookup, simple identifier validation, and simple local-first planning, but not a complete offline SQL dialect knowledge base.

## Current Limits

- PostgreSQL is experimental for the documented `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` probe paths only
- MySQL is a stub with a structured placeholder error
- write commands do not yet have dry-run or transaction support
- natural-language support is lightweight by default; provider-backed quality is not broadly proven
- provider-backed natural is currently a secondary experimental track
- generated SQL templates validate basic identifiers, but are not yet relationship-aware, join-aware, or expression-aware
- JPA support is source introspection only; it does not execute JPQL or run a Java persistence unit
- DB reference knowledge is currently a seed pack, not a complete local replacement for SQL/JPA documentation

## Recommended Verification

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command generate --db example.db --skill select_simple --params '{"table":"users","cols":["id","name"]}' --format json
python3 sql_cli/tests/test_core.py
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
python3 main.py --command db_knowledge --dialect postgresql --topic pagination
python3 main.py --command db_knowledge --topic coverage
bash scripts/run_postgresql_local_smoke.sh
```

Runner note:

- `scripts/run_postgresql_local_smoke.sh` checks `PATH` for PostgreSQL binaries before falling back to known Homebrew paths

Version: v0.7.0
Last Updated: 2026-04-10
Status: SQLite-first baseline verified with experimental PostgreSQL schema, schema_detail, query, insert, update, delete proof, and schema-detail-aware identifier validation
