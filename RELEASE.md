# CoQuery v0.7.1 Stabilization Snapshot

## Release Information

**Version**: v0.7.1
**Date**: 2026-04-28
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
help_catalog
command_explain
term_explain
provider_add
provider_list_presets
provider_add_preset
provider_list
provider_remove
provider_test
practice_list
practice_schema
practice_query
practice_grade
practice_attempts
```

### Stabilized in v0.7.1

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
| Baseline tests | 119/119 passing |
| Terminal shell prototype smoke | passing |
| Agent wrapper verify | passing |
| Local PostgreSQL smoke | passing |
| GitHub Actions baseline | success on 2026-04-27 UTC for `7e677fe` |
| GitHub Actions postgresql-smoke | success on 2026-04-27 UTC for `7e677fe` |

## Release Notes

### Current provider preset update (2026-06-30)
- Provider preset registration is available for OpenAI, Groq, OpenRouter, Gemini, and DeepSeek-style APIs
- OpenAI-compatible providers can store direct chat-completions and models endpoint overrides
- Provider preset and endpoint override behavior is covered by the executable baseline tests

### Current command API update (2026-06-30)
- `sql_cli.command_api.run_command` exposes existing CLI handlers to mobile/web app shells without shelling out
- Command API responses include `cli_equivalent`, `block_type`, and `actions` metadata
- Provider preset, provider list, schema detail, natural request, and unknown-command adapter paths are covered by executable tests

### Current responsive terminal shell update (2026-06-30)
- `app_shell/terminal_shell_prototype` provides a local mobile/tablet/desktop terminal UI over the Command API
- The shell keeps command blocks, CLI equivalents, and structured detail output visible without replacing the CLI core
- The prototype is covered by `app_shell/terminal_shell_prototype/smoke.py` and browser snapshots for desktop, tablet, and phone widths

### Current provider preset mobile flow update (2026-07-01)
- Terminal shell now defaults to dark mode
- `Setup AI` opens a provider preset form for mobile/tablet/desktop use
- Users can choose a preset, edit provider name/model/API key env, preview the CLI equivalent, and save through `provider_add_preset`
- `app_shell/terminal_shell_prototype/smoke.py` verifies provider preset saving through the local Command API

### Current practice dataset update (2026-07-01)
- `practice_packs/sql_basics.json` adds a built-in sample dataset and five SQL practice problems
- `practice_list`, `practice_schema`, `practice_query`, `practice_grade`, and `practice_attempts` work without connecting to a user DB
- Practice execution uses in-memory SQLite, read-only query enforcement, result-set grading, and local attempt records
- Practice commands are available through both the CLI and `sql_cli.command_api.run_command`

### Current bilingual help update (2026-07-06)
- `help_catalog`, `command_explain`, and `term_explain` add Korean/English beginner guidance for commands and SQL/DB terms
- The responsive terminal shell includes a KR/EN toggle, help/terms chips, and a beginner guide panel
- Help commands are available through both the CLI and `sql_cli.command_api.run_command`

### v0.7.1 stabilization snapshot (2026-04-28)
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
**Status**: v0.7.1 stabilized CLI baseline
