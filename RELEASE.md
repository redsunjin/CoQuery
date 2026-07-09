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
practice_feedback
production_profile_add
production_profile_list
production_review
production_approve
production_execute
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

**Launch safety additions after the stabilization snapshot:**
- Production Assist Safety Gate supports read-only profiles, reviewed SQL approval, SELECT-only execution, and JSONL audit logging.
- Boundary documentation lives at `docs/production-assist-safety-gate.md`.

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
| Baseline tests | 121/121 passing |
| Terminal shell prototype smoke | passing |
| Agent wrapper verify | passing |
| Local PostgreSQL smoke | passing |
| GitHub Actions baseline | success on 2026-04-27 UTC for `7e677fe` |
| GitHub Actions postgresql-smoke | success on 2026-04-27 UTC for `7e677fe` |

## Release Notes

## Exact Release Claims

Supported claims:

- SQLite-first CLI commands are verified by the executable baseline tests.
- Command API adapter reuses the CLI handlers and returns app-shell metadata.
- Local browser shell can be started with `npm run local:shell` or `python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765`.
- Practice flow works without connecting to a user database or provider.
- Provider setup stores provider profiles with API key environment variable names, not secret key values.
- Korean/English command help and SQL term explanations are available through CLI, Command API, and terminal shell.
- Production Assist Safety Gate supports read-only profiles, reviewed SQL approval, SELECT-only execution, and JSONL audit logging.
- iOS TestFlight shell skeleton is available for Training Mode only.
- One RC command, `npm run rc:verify`, runs the launch checks.

Unsupported claims:

- CoQuery is not a hosted public web service.
- CoQuery does not ship a Tauri or Electron desktop installer.
- CoQuery is not a packaged production DB assistant.
- The iOS shell is not a production DB client.
- Production Assist is not write access to production data.
- MySQL runtime support is not implemented beyond the structured stub.
- PostgreSQL remains experimental outside the documented smoke-proven slices.
- Provider pricing, model availability, model quality, and external API uptime are not guaranteed.

### Current iOS TestFlight shell update (2026-07-08)
- Capacitor SPM project files and `ios/` native shell are present for `app.coquery.training`
- `app_shell/ios_training_shell/src/trainingRuntime.ts` provides a Python-server-free local Training Runtime skeleton
- The packaged shell starts with `practice_list` and bundles `practice_packs/sql_basics.json`
- iPhone and iPad simulator launches were verified through XcodeBuildMCP screenshots
- TestFlight metadata checklist lives at `docs/testflight-metadata-checklist.md`

### Current mode and local packaging update (2026-07-08)
- The terminal shell exposes Training/Assist mode separation in the command bar
- Command API mode-aware responses include `mode_context`
- Production Assist blocks saved external providers unless `allow_external_provider=true` is explicitly supplied
- Non-iOS local packaging is selected as local web app first, not Tauri/Electron for the first local release
- Stable local start command is `python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765`
- Runtime storage, update path, and rollback path are documented at `docs/desktop-local-packaging-decision.md`

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
- Saved providers can be listed, selected, tested, and removed in the terminal shell with CLI equivalents shown for each action
- Provider test failures include readable next-step guidance for non-specialists
- `app_shell/terminal_shell_prototype/smoke.py` verifies provider preset saving through the local Command API

### Current practice dataset update (2026-07-01)
- `practice_packs/sql_basics.json` adds a built-in sample dataset and five SQL practice problems
- `practice_list`, `practice_schema`, `practice_query`, `practice_grade`, `practice_attempts`, and static `practice_feedback` work without connecting to a user DB or provider
- Practice execution uses in-memory SQLite, read-only query enforcement, result-set grading, local attempt records, and wrong-note metadata
- Provider-backed `practice_feedback` is gated to Training Mode and labeled as AI-generated
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
- run `npm run rc:verify` before publication
- commit and push the release-candidate branch when publication is requested
- decide the next PostgreSQL verification slice before widening claims
- keep GitHub Actions `baseline` and `postgresql-smoke` green
- consider a hosted or browser-facing demo only after CLI proof remains stable
- keep docs aligned with observed proof

## Credits

**Repository**: [redsunjin/CoQuery](https://github.com/redsunjin/CoQuery)  
**License**: MIT  
**Status**: v0.7.1 stabilized CLI baseline
