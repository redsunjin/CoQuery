# CoQuery CLI

CoQuery currently provides a verified SQLite-first CLI baseline.
Phase 5 multi-DB support is now early experimental and is not complete.

Repository: `https://github.com/redsunjin/CoQuery`
Visibility: `PUBLIC` as verified on 2026-04-23.
Recorded proof commit: `7e677fe Clarify recorded CI proof status`.

## Available Commands

```bash
python3 main.py --command schema --db example.db
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command doctor --db example.db --format json
# requires psycopg[binary] in the Python environment running main.py
python3 main.py --command doctor --db-uri postgresql://doctor:secret@localhost:5432/appdb --format json
python3 main.py --command schema --db-uri sqlite:///Users/Agent/ps-workspace/CoQuery/example.db
python3 main.py --command query --db example.db --sql "SELECT * FROM users"
python3 main.py --command generate --db example.db --skill select_simple
python3 main.py --command insert --db example.db --write --sql "INSERT INTO users (name, age) VALUES ('a', 20)"
python3 main.py --command update --db example.db --write --sql "UPDATE users SET age = 21 WHERE id = 1"
python3 main.py --command delete --db example.db --write --sql "DELETE FROM users WHERE id = 1"
python3 main.py --command insert --db example.db --write --dry-run --sql "INSERT INTO users (name, age) VALUES ('preview', 20)"
python3 main.py --command delete --db example.db --write --max-affected-rows 1 --sql "DELETE FROM users WHERE id = 1"
python3 main.py --command update --db example.db --write --allow-full-table-write --dry-run --sql "UPDATE users SET age = age + 1"
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
- `python3 sql_cli/tests/test_core.py` passes with 96 tests
- SQLite is the working backend
- `--db-uri` is the preferred multi-backend connection contract
- `doctor` reports masked targets, readiness checks, and classified PostgreSQL connection failures
- direct PostgreSQL `doctor` or runtime use requires `psycopg[binary]` in the active Python environment
- `query` is read-only unless `--write` is provided
- `insert`, `update`, and `delete` require both `--write` and explicit SQL
- `update` and `delete` without `WHERE` require `--allow-full-table-write`
- provider registry commands are available for optional `natural` fallback routing
- `jpa_schema` can inspect annotation-based JPA entity source as an ORM/model context
- `db_knowledge` can retrieve local SQL/JPA dialect and write-safety rules before using an LLM/provider
- `schema_detail` exposes normalized columns, keys, indexes, constraints, and SQLite create SQL for agent-side knowledge use
- `generate` and simple `natural` requests validate table and simple column identifiers against `schema_detail`
- generation, natural-language, and write-planning paths attach local DB/JPA knowledge context first
- PostgreSQL `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`, write-safety guards, select/count generation, and direct join generation are smoke-proven on the documented experimental path
- GitHub Actions `baseline` and `postgresql-smoke` were last recorded successful on 2026-04-27 UTC for commit `7e677fe`

## GitHub Demo

CoQuery is currently a CLI project, not a hosted browser app. The public GitHub repository can still run a log-based demo:

1. open `https://github.com/redsunjin/CoQuery`
2. go to `Actions`
3. run the `baseline` workflow manually to execute `verify` and `demo`
4. run the `postgresql-smoke` workflow manually to execute the PostgreSQL proof

Detailed usage and demo steps live in `USAGE_AND_DEMO.md`.

## Agent Skill

CoQuery can now be used as a Codex skill through `skills/coquery-cli`.

```bash
bash scripts/install_coquery_skill.sh
python3 skills/coquery-cli/scripts/coquery_agent.py describe
python3 skills/coquery-cli/scripts/coquery_agent.py verify
python3 skills/coquery-cli/scripts/coquery_agent.py demo
python3 skills/coquery-cli/scripts/coquery_agent.py run --command schema --db example.db
python3 skills/coquery-cli/scripts/coquery_agent.py run --command schema_detail --db example.db --table users
python3 skills/coquery-cli/scripts/coquery_agent.py run --command db_knowledge --dialect jpql --topic parameters
python3 skills/coquery-cli/scripts/coquery_agent.py install-skill
```

The skill is also installable under `~/.codex/skills/coquery-cli` for `$coquery-cli` discovery in future Codex sessions.
`describe` emits machine-readable capability metadata, and `install-skill` copies the skill package into another Codex skills directory.
`scripts/install_coquery_skill.sh` is the shortest shell-first install path.

The skill includes a compact DB knowledge seed at `skills/coquery-cli/references/db-knowledge.md`.
Structured machine-readable rules and coverage metadata now live under `knowledge/`.
Machine-readable agent capability metadata now also lives at `skills/coquery-cli/references/capabilities.json`.
Practical install/call guidance now lives in `AGENT_INTEGRATION.md`.
This is enough for basic SQL/JPA boundary decisions, deterministic lookup, normalized schema-detail lookup, simple identifier validation, and simple local-first planning, but not a complete offline SQL dialect knowledge base.

## Current Limits

- PostgreSQL is experimental for the documented `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`, write-safety guard, select/count generation, and direct join generation smoke paths only
- `doctor` can classify common PostgreSQL connection failures such as `auth_failed`, `database_not_found`, `host_unreachable`, `connection_refused`, `timeout`, and `ssl_error`
- if `psycopg[binary]` is not installed, PostgreSQL `doctor` and PostgreSQL runtime commands fail with `driver_not_installed`
- MySQL is a stub with a structured placeholder error
- write commands support `--dry-run` and `--max-affected-rows`, but a broader transaction control layer does not exist yet
- natural-language support is lightweight by default; provider-backed quality is not broadly proven
- provider-backed natural is currently a secondary experimental track
- generated SQL templates validate basic identifiers and direct joins, but are not yet multi-hop relationship-aware, alias-aware, or expression-aware
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

- `scripts/run_postgresql_local_smoke.sh` prefers PostgreSQL binaries from `PATH`, uses a per-run socket directory, and auto-selects a free port when the preferred smoke port is unavailable
- the smoke runner bootstraps `.tmp/pg-venv` and installs `psycopg[binary]` there if needed, so it remains the repeatable PostgreSQL proof path even when the default `python3` environment lacks the driver

Version: v0.7.1
Last Updated: 2026-04-28
Status: SQLite-first baseline verified with `doctor`, explicit write safety guards, experimental PostgreSQL schema, schema_detail, query, insert, update, delete, write-safety guard, schema-detail-validated select/count generation, direct join generation proof, public GitHub repository, and verified GitHub Actions baseline / PostgreSQL smoke workflows
