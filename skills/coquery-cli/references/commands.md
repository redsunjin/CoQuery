# CoQuery Command Reference

Baseline commands:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py describe
python3 skills/coquery-cli/scripts/coquery_agent.py install-skill
python3 skills/coquery-cli/scripts/coquery_agent.py install-skill --target-root /tmp/codex-skills
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command doctor --db example.db --format json
# requires psycopg[binary] in the active Python environment
python3 main.py --command doctor --db-uri postgresql://doctor:secret@localhost:5432/appdb --format json
python3 main.py --command query --db example.db --sql "SELECT * FROM users" --format json
python3 main.py --command generate --db example.db --skill select_simple --format json
python3 main.py --command generate --db example.db --skill select_simple --params '{"table":"users","cols":["id","name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_inner --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_left --params '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}' --format json
python3 main.py --command natural --db example.db --sql "show users" --format json
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
python3 main.py --command db_knowledge --dialect sqlite --topic schema
python3 main.py --command db_knowledge --topic write_safety
python3 main.py --command db_knowledge --topic coverage
python3 main.py --command help_catalog --lang ko --format json
python3 main.py --command command_explain --topic natural --lang ko --format json
python3 main.py --command term_explain --topic join --lang en --format json
python3 main.py --command provider_list_presets --format json
python3 main.py --command practice_list --format json
python3 main.py --command practice_schema --table orders --format json
python3 main.py --command practice_query --sql "SELECT id, name FROM customers ORDER BY id" --format json
python3 main.py --command practice_grade --problem-id basic_select_customers --sql "SELECT id, name, region FROM customers ORDER BY id" --no-record --format json
```

SQLite URI example:

```bash
python3 main.py --command schema --db-uri sqlite:///absolute/path/to/example.db --format json
python3 main.py --command schema_detail --db-uri sqlite:///absolute/path/to/example.db --table users --format json
```

Doctor output now includes readiness checks plus classified PostgreSQL connection failures such as `auth_failed`, `database_not_found`, `host_unreachable`, `connection_refused`, `timeout`, and `ssl_error`.
If `psycopg[binary]` is not installed in the active Python environment, PostgreSQL doctor calls fail closed with `driver_not_installed`.

Agent package notes:

- `describe` prints machine-readable capability metadata and install guidance.
- `install-skill` copies the current skill package into another Codex skills directory.
- installed skill copies should use `--repo /path/to/CoQuery` or `COQUERY_REPO=/path/to/CoQuery` when the repository lives elsewhere.

Write examples:

```bash
python3 main.py --command insert --db /tmp/demo.db --write --sql "INSERT INTO users (name, age) VALUES ('a', 20)"
python3 main.py --command update --db /tmp/demo.db --write --sql "UPDATE users SET age = 21 WHERE name = 'a'"
python3 main.py --command delete --db /tmp/demo.db --write --sql "DELETE FROM users WHERE name = 'a'"
python3 main.py --command insert --db /tmp/demo.db --write --dry-run --sql "INSERT INTO users (name, age) VALUES ('preview', 20)"
python3 main.py --command delete --db /tmp/demo.db --write --max-affected-rows 1 --sql "DELETE FROM users WHERE name = 'a'"
python3 main.py --command update --db /tmp/demo.db --write --allow-full-table-write --dry-run --sql "UPDATE users SET age = age + 1"
python3 skills/coquery-cli/scripts/coquery_agent.py run --command insert --db /tmp/demo.db --write --dry-run --sql "INSERT INTO users (name, age) VALUES ('preview', 20)"
python3 skills/coquery-cli/scripts/coquery_agent.py run --command delete --db /tmp/demo.db --write --max-affected-rows 1 --sql "DELETE FROM users WHERE name = 'a'"
python3 skills/coquery-cli/scripts/coquery_agent.py run --command update --db /tmp/demo.db --write --allow-full-table-write --dry-run --sql "UPDATE users SET age = age + 1"
```

Direct join generation example:

```bash
python3 main.py --command generate --db /tmp/join-test.db --skill join_inner \
  --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_left \
  --params '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}' --format json
```

This generates a direct `ON` clause from `schema_detail` foreign-key metadata when the two tables have exactly one direct join path. Missing or ambiguous join paths fail closed.

Command API adapter example:

```bash
python3 -c "from sql_cli.command_api import run_command; print(run_command('provider_list_presets')['cli_equivalent'])"
```

Use `sql_cli.command_api.run_command` for mobile/web app shells that need to reuse CoQuery handlers without shelling out. Adapter responses keep the handler result and add `cli_equivalent`, `block_type`, and `actions`.

Practice dataset sandbox examples:

```bash
python3 main.py --command practice_list --format json
python3 main.py --command practice_schema --table orders --format json
python3 main.py --command practice_query --sql "SELECT id, customer_id, total_amount FROM orders WHERE status = 'paid'" --format json
python3 main.py --command practice_grade \
  --problem-id basic_select_customers \
  --sql "SELECT id, name, region FROM customers ORDER BY id" \
  --no-record \
  --format json
python3 main.py --command practice_attempts --limit 5 --format json
```

Practice commands use `practice_packs/sql_basics.json` and in-memory SQLite, so they do not require a user DB connection.
Attempt records default to `.coquery/practice_attempts.jsonl`; set `COQUERY_PRACTICE_ATTEMPT_LOG` to override the path.

Bilingual help examples:

```bash
python3 main.py --command help_catalog --lang ko --format json
python3 main.py --command help_catalog --lang en --format json
python3 main.py --command command_explain --topic practice_grade --lang ko --format json
python3 main.py --command term_explain --topic join --lang ko --format json
```

`help_catalog`, `command_explain`, and `term_explain` provide beginner-friendly command and SQL term guidance for both the CLI and responsive app shell.

Provider registry examples:

```bash
python3 main.py --command provider_list_presets --format json
python3 main.py --command provider_add --provider-name local_ollama --provider-kind ollama --model-name qwen3.5:4b-nvfp4 --base-url http://127.0.0.1:11434
python3 main.py --command provider_add_preset --preset groq --provider-name fast_groq --model-name llama-3.1-8b-instant --api-key-env GROQ_API_KEY
python3 main.py --command provider_add_preset --preset gemini --provider-name gemini_flash --api-key-env GEMINI_API_KEY
python3 main.py --command provider_list --format json
python3 main.py --command provider_test --provider-name local_ollama
python3 main.py --command natural --db example.db --sql "show users" --provider-name local_ollama --format json
```

Available provider presets are `openai`, `groq`, `openrouter`, `gemini`, and `deepseek`.
Preset registration stores the provider's concrete chat-completions endpoint so OpenAI-compatible services with custom URL paths can be used without changing CoQuery code.
Use `--model-name` for presets that do not carry a default model, and run `provider_test` before depending on any provider/model pair.

Manual OpenAI-compatible endpoint override:

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

For simple covered natural-language requests, `natural --provider-name ...` returns `mode: local_knowledge` and `provider_skipped: true`. More complex requests can still fall back to provider mode.

PostgreSQL smoke:

```bash
bash scripts/run_postgresql_local_smoke.sh
COQUERY_PG_RESET=1 bash scripts/run_postgresql_local_smoke.sh
COQUERY_PG_DB_URI=postgresql://user:pass@host:5432/dbname bash scripts/run_postgresql_local_smoke.sh
```

The smoke runner verifies `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`, write-safety guard paths for `--dry-run`, `--max-affected-rows`, and full-table write rejection, schema-detail-validated `generate select_simple` / `generate count_simple`, and direct `generate join_inner` / `generate join_left` slices against PostgreSQL.

The runner prefers PostgreSQL binaries from `PATH`, falls back to known Homebrew paths, creates a per-run socket directory, and auto-selects a free port when the preferred smoke port is already in use.
It also bootstraps `.tmp/pg-venv` and installs `psycopg[binary]` there when needed.
