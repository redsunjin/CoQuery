# CoQuery CLI

CoQuery currently provides a verified SQLite-first CLI baseline.
Phase 5 multi-DB support is now early experimental and is not complete.

Repository: `https://github.com/redsunjin/CoQuery`
Visibility: `PUBLIC` as verified on 2026-04-23.
Recorded proof commit: `7e677fe Clarify recorded CI proof status`.

Service launch roadmap: `SERVICE_LAUNCH_PLAN_2026-07-07.md`
Next recommended `/goal`: `Launch Goal 1: Query Practice Flow UI`

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
python3 main.py --command help_catalog --lang ko --format json
python3 main.py --command command_explain --topic natural --lang ko --format json
python3 main.py --command term_explain --topic join --lang en --format json
python3 main.py --command provider_list_presets
python3 main.py --command provider_add_preset --preset groq --provider-name fast_groq --model-name llama-3.1-8b-instant --api-key-env GROQ_API_KEY
python3 main.py --command provider_add_preset --preset gemini --provider-name gemini_flash --api-key-env GEMINI_API_KEY
python3 main.py --command provider_list
python3 main.py --command provider_test --provider-name local_ollama
python3 main.py --command practice_list --format json
python3 main.py --command practice_schema --table orders --format json
python3 main.py --command practice_query --sql "SELECT id, name FROM customers ORDER BY id" --format json
python3 main.py --command practice_grade --problem-id basic_select_customers --sql "SELECT id, name, region FROM customers ORDER BY id" --no-record --format json
python3 main.py --command practice_attempts --limit 5 --format json
```

## Provider Presets

CoQuery can register local or API-backed LLM providers for optional `natural` fallback routing.
The preset path stores provider-specific chat-completions endpoints directly, so OpenAI-compatible APIs with non-standard base paths can be used without guessing URL layout.

Available presets:

- `openai`: OpenAI Chat Completions endpoint, requires a model name and `OPENAI_API_KEY` by default
- `groq`: Groq OpenAI-compatible endpoint, requires a model name and `GROQ_API_KEY` by default
- `openrouter`: OpenRouter OpenAI-compatible endpoint, requires a model name and `OPENROUTER_API_KEY` by default
- `gemini`: Gemini OpenAI-compatible endpoint, defaults to `gemini-3.5-flash` and `GEMINI_API_KEY`
- `deepseek`: DeepSeek chat-completions endpoint, defaults to `deepseek-v4-flash` and `DEEPSEEK_API_KEY`

Examples:

```bash
python3 main.py --command provider_list_presets --format json
python3 main.py --command provider_add_preset \
  --preset groq \
  --provider-name fast_groq \
  --model-name llama-3.1-8b-instant \
  --api-key-env GROQ_API_KEY
python3 main.py --command provider_add_preset \
  --preset gemini \
  --provider-name gemini_flash \
  --api-key-env GEMINI_API_KEY
python3 main.py --command provider_test --provider-name fast_groq
python3 main.py --command natural --db example.db --sql "join users and orders" --provider-name fast_groq
```

Manual endpoint override remains available for providers that expose an OpenAI-style payload but use custom paths:

```bash
python3 main.py --command provider_add \
  --provider-name custom_compat \
  --provider-kind openai_compatible \
  --model-name small-model \
  --base-url https://provider.example \
  --chat-completions-url https://provider.example/custom/chat/completions \
  --models-url https://provider.example/custom/models \
  --api-key-env CUSTOM_API_KEY
```

## Verified Baseline

- `main.py` routes to the package handlers in `sql_cli/cli.py`
- `python3 sql_cli/tests/test_core.py` passes with 119 tests
- SQLite is the working backend
- `--db-uri` is the preferred multi-backend connection contract
- `doctor` reports masked targets, readiness checks, and classified PostgreSQL connection failures
- direct PostgreSQL `doctor` or runtime use requires `psycopg[binary]` in the active Python environment
- `query` is read-only unless `--write` is provided
- `insert`, `update`, and `delete` require both `--write` and explicit SQL
- `update` and `delete` without `WHERE` require `--allow-full-table-write`
- provider registry commands are available for optional `natural` fallback routing
- provider presets are available for OpenAI, Groq, OpenRouter, Gemini, and DeepSeek-style API registration
- `practice_*` commands provide a DB-free SQL learning sandbox over built-in sample data
- `jpa_schema` can inspect annotation-based JPA entity source as an ORM/model context
- `db_knowledge` can retrieve local SQL/JPA dialect and write-safety rules before using an LLM/provider
- `help_catalog`, `command_explain`, and `term_explain` provide Korean/English beginner guidance for commands and SQL terms
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

## Mobile CLI UX Direction

The mobile/wide-screen app direction lives in `MOBILE_CLI_UX_PLAN_2026-06-30.md`.
The plan keeps CoQuery CLI-first while defining a responsive app shell:

- phone portrait: compact calculator-like terminal
- phone landscape: terminal plus shortcut/history strip
- tablet: terminal plus explain/review panel
- desktop/wide: Warp-inspired session rail, terminal blocks, and detail panel

The planned app shell should call CoQuery handlers through a command API instead of replacing the CLI core.

## Command API Adapter

Mobile, tablet, and web shells can call the existing handlers without shelling out through `sql_cli.command_api.run_command`.
The adapter preserves handler output and adds app-shell metadata:

- `cli_equivalent`: exact CLI command to show for trust and reproducibility
- `block_type`: UI rendering hint such as `provider_presets`, `schema_detail`, or `natural_sql`
- `actions`: suggested block actions such as copy, add provider, run query, or review

Example:

```python
from sql_cli.command_api import run_command

result = run_command(
    "provider_list_presets",
    args={},
    context={},
)
```

Minimum mobile-shell commands currently covered by tests:

- `provider_list_presets`
- `provider_add_preset`
- `provider_list`
- `schema_detail`
- `natural`
- `help_catalog`
- `command_explain`
- `term_explain`
- `practice_list`
- `practice_schema`
- `practice_query`
- `practice_grade`
- `practice_attempts`

## Bilingual Help

CoQuery exposes beginner-friendly Korean/English command and SQL term guidance through the same CLI and Command API contract used by the app shell.

```bash
python3 main.py --command help_catalog --lang ko --format json
python3 main.py --command command_explain --topic practice_grade --lang ko --format json
python3 main.py --command term_explain --topic join --lang en --format json
```

## Practice Dataset Sandbox

CoQuery can now run SQL practice without connecting to a user database.
The built-in pack lives at `practice_packs/sql_basics.json` and is loaded into an in-memory SQLite sandbox per command.

Available practice commands:

- `practice_list`: list packs, problems, hints, and sample queries
- `practice_schema`: inspect sample tables, columns, keys, and row counts
- `practice_query`: run read-only `SELECT` SQL against the sample dataset
- `practice_grade`: compare a submitted answer to the expected result for a problem
- `practice_attempts`: review recorded attempts for wrong-note and learning flows

Example:

```bash
python3 main.py --command practice_list --format json
python3 main.py --command practice_schema --table orders --format json
python3 main.py --command practice_query --sql "SELECT id, total_amount FROM orders WHERE status = 'paid'" --format json
python3 main.py --command practice_grade \
  --problem-id basic_select_customers \
  --sql "SELECT id, name, region FROM customers ORDER BY id" \
  --no-record \
  --format json
```

Attempt records default to `.coquery/practice_attempts.jsonl`.
Set `COQUERY_PRACTICE_ATTEMPT_LOG` to redirect them during tests or custom local use.

## Responsive Terminal Shell Prototype

A local mobile-first terminal shell prototype now lives under `app_shell/terminal_shell_prototype`.
It defaults to dark mode and keeps the command input and CLI-equivalent output visible while adapting the surrounding panels by screen size:

- phone: terminal history, bottom command input, and a bottom detail drawer
- tablet: terminal plus detail panel
- desktop/wide: session rail, terminal blocks, and detail panel

The shell also includes a provider preset mobile flow:

- open `Setup AI`
- choose Groq, Gemini, OpenRouter, DeepSeek, or OpenAI
- enter provider name, model, and API key env label
- review the generated CLI equivalent
- save through the Command API using `provider_add_preset`

Run from the repository root:

```bash
python app_shell/terminal_shell_prototype/server.py --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

The prototype exposes `GET /api/health`, `GET /api/sessions`, and `POST /api/commands/run`.
The command endpoint calls `sql_cli.command_api.run_command`, so the UI does not duplicate CLI behavior.

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
- provider pricing, free tiers, and model availability are not hardcoded guarantees; use provider docs and `provider_test` to verify a selected model before relying on it
- practice commands use a small built-in sample dataset and result comparison; they are not a full SQL course or production grader yet
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
python3 main.py --command help_catalog --lang ko --format json
python3 main.py --command practice_list --format json
python3 main.py --command practice_grade --problem-id basic_select_customers --sql "SELECT id, name, region FROM customers ORDER BY id" --no-record --format json
bash scripts/run_postgresql_local_smoke.sh
```

Runner note:

- `scripts/run_postgresql_local_smoke.sh` prefers PostgreSQL binaries from `PATH`, uses a per-run socket directory, and auto-selects a free port when the preferred smoke port is unavailable
- the smoke runner bootstraps `.tmp/pg-venv` and installs `psycopg[binary]` there if needed, so it remains the repeatable PostgreSQL proof path even when the default `python3` environment lacks the driver

Version: v0.7.1
Last Updated: 2026-07-06
Status: SQLite-first baseline verified with `doctor`, explicit write safety guards, experimental PostgreSQL schema, schema_detail, query, insert, update, delete, write-safety guard, schema-detail-validated select/count generation, direct join generation proof, provider presets for low-cost/API-backed natural fallback, bilingual beginner help, public GitHub repository, and verified GitHub Actions baseline / PostgreSQL smoke workflows
