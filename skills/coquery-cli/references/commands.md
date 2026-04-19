# CoQuery Command Reference

Baseline commands:

```bash
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command doctor --db example.db --format json
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
```

SQLite URI example:

```bash
python3 main.py --command schema --db-uri sqlite:///absolute/path/to/example.db --format json
python3 main.py --command schema_detail --db-uri sqlite:///absolute/path/to/example.db --table users --format json
```

Doctor output now includes readiness checks plus classified PostgreSQL connection failures such as `auth_failed`, `database_not_found`, `host_unreachable`, `connection_refused`, `timeout`, and `ssl_error`.

Write examples:

```bash
python3 main.py --command insert --db /tmp/demo.db --write --sql "INSERT INTO users (name, age) VALUES ('a', 20)"
python3 main.py --command update --db /tmp/demo.db --write --sql "UPDATE users SET age = 21 WHERE name = 'a'"
python3 main.py --command delete --db /tmp/demo.db --write --sql "DELETE FROM users WHERE name = 'a'"
python3 main.py --command insert --db /tmp/demo.db --write --dry-run --sql "INSERT INTO users (name, age) VALUES ('preview', 20)"
python3 main.py --command delete --db /tmp/demo.db --write --max-affected-rows 1 --sql "DELETE FROM users WHERE name = 'a'"
python3 main.py --command update --db /tmp/demo.db --write --allow-full-table-write --dry-run --sql "UPDATE users SET age = age + 1"
```

Direct join generation example:

```bash
python3 main.py --command generate --db /tmp/join-test.db --skill join_inner \
  --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_left \
  --params '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}' --format json
```

This generates a direct `ON` clause from `schema_detail` foreign-key metadata when the two tables have exactly one direct join path. Missing or ambiguous join paths fail closed.

Provider registry examples:

```bash
python3 main.py --command provider_add --provider-name local_ollama --provider-kind ollama --model-name qwen3.5:4b-nvfp4 --base-url http://127.0.0.1:11434
python3 main.py --command provider_list --format json
python3 main.py --command provider_test --provider-name local_ollama
python3 main.py --command natural --db example.db --sql "show users" --provider-name local_ollama --format json
```

For simple covered natural-language requests, `natural --provider-name ...` returns `mode: local_knowledge` and `provider_skipped: true`. More complex requests can still fall back to provider mode.

PostgreSQL smoke:

```bash
bash scripts/run_postgresql_local_smoke.sh
COQUERY_PG_RESET=1 bash scripts/run_postgresql_local_smoke.sh
COQUERY_PG_DB_URI=postgresql://user:pass@host:5432/dbname bash scripts/run_postgresql_local_smoke.sh
```

The runner prefers PostgreSQL binaries from `PATH`, falls back to known Homebrew paths, creates a per-run socket directory, and auto-selects a free port when the preferred smoke port is already in use.
