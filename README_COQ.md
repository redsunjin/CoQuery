# CoQuery Baseline Verification

Date: 2026-06-30

## Result

```text
119/119 executable baseline tests pass
SQLite-first CLI verified
Explicit write contract verified
Shared DB URI contract verified
Doctor command verified
PostgreSQL schema, schema_detail, query, insert, update, and delete smoke verified
PostgreSQL select/count generation smoke verified
PostgreSQL direct join-generation smoke verified
PostgreSQL write-safety guard smoke verified
Local PostgreSQL smoke runner re-verified on 2026-04-22
Local DB/JPA knowledge-first generation planning verified
Schema-detail knowledge command verified
Schema-detail-aware generation and natural identifier validation verified
Schema-detail-aware direct join generation verified
Dry-run preview and max-affected-row rollback guards verified
Full-table write guard verified
PostgreSQL doctor classification verified for common connection failures
Provider preset registration and OpenAI-compatible endpoint override verified
Command API Adapter verified for app-shell handler reuse
Responsive Terminal Shell Prototype verified as a local Command API app shell
Provider Preset Mobile Flow verified in the dark-mode terminal shell prototype
Practice Dataset Sandbox verified for DB-free sample schema, query, grading, attempts, CLI, and Command API paths
Query Practice Flow UI verified for problem start, schema view, SQL submit, grading, and local attempt review
Bilingual beginner help verified for Korean/English command and SQL term guidance
GitHub Actions baseline and PostgreSQL smoke workflows last recorded as verified on 2026-04-27 UTC for `main` commit `7e677fe`
Public GitHub repository verified
```

Service launch plan:

- `SERVICE_LAUNCH_PLAN_2026-07-07.md`
- Next recommended `/goal`: `Launch Goal 2: Wrong Note And Feedback`

Scope decision:

- current `main` is retained as the active line
- reduced cleanup PR `#1` was closed unmerged
- DB/JPA knowledge, JPA source introspection, and Codex skill packaging stay in scope as retained experimental tracks

## Verified Commands

- `schema`
- `schema_detail`
- `doctor`
- `query`
- `generate`
- `insert`
- `update`
- `delete`
- `natural`
- `jpa_schema`
- `db_knowledge`
- `help_catalog`
- `command_explain`
- `term_explain`
- `provider_add`
- `provider_list_presets`
- `provider_add_preset`
- `provider_list`
- `provider_remove`
- `provider_test`
- `practice_list`
- `practice_schema`
- `practice_query`
- `practice_grade`
- `practice_attempts`

## Support Matrix

| Area | Status | Notes |
|------|--------|-------|
| SQLite CLI path | Working | current verified runtime |
| PostgreSQL | Experimental (narrow read + write + limited generate) | local smoke proof succeeded for `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`, write-safety guards, schema-detail-validated `generate select_simple` / `generate count_simple`, and direct join generation; latest local runner pass on 2026-04-22 |
| MySQL | Stub | returns structured placeholder error |
| Write contract | Working baseline | `--write` plus explicit SQL is enforced |
| Dry-run preview | Working baseline | `insert`, `update`, `delete`, and write-mode `query` can return affected rows without committing changes |
| Affected-row guard | Working baseline | `--max-affected-rows` rolls back writes that touch more rows than expected |
| Full-table write guard | Working baseline | `update`, `delete`, and write-mode `query` without `WHERE` fail closed unless `--allow-full-table-write` is provided |
| DB URI contract | Working baseline | `--db-uri` is available and validated |
| Doctor diagnostics | Working baseline | `doctor` reports readiness plus classified PostgreSQL connection failures |
| Phase 5 verification matrix | Working baseline | backend promotion is now proof-gated |
| PostgreSQL schema smoke | Working baseline | initial local proof recorded on 2026-04-05; latest runner pass on 2026-04-22 |
| PostgreSQL select/count generation smoke | Working baseline | local proof recorded on 2026-04-22 for schema-detail-validated `generate select_simple` and `generate count_simple` plus generated SQL execution |
| PostgreSQL direct join generation smoke | Working baseline | initial local proof recorded on 2026-04-11 for direct `generate join_inner` and `generate join_left` slices; latest runner pass on 2026-04-22 |
| PostgreSQL query smoke | Working baseline | initial local proof recorded on 2026-04-05; latest runner pass on 2026-04-22 |
| PostgreSQL insert smoke | Working baseline | initial local proof recorded on 2026-04-05; latest runner pass on 2026-04-22 |
| PostgreSQL update smoke | Working baseline | initial local proof recorded on 2026-04-07; latest runner pass on 2026-04-22 |
| PostgreSQL delete smoke | Working baseline | initial local proof recorded on 2026-04-08; latest runner pass on 2026-04-22 |
| PostgreSQL write-safety smoke | Working baseline | local proof recorded on 2026-04-22 for dry-run rollback, max-affected rollback, and full-table write rejection |
| Docs example smoke | Working baseline | key documented CLI examples are exercised in tests |
| Natural language | Baseline only | simple covered requests use local knowledge first; optional provider path remains fallback |
| Provider presets | Experimental secondary track | presets exist for OpenAI, Groq, OpenRouter, Gemini, and DeepSeek-style APIs; run `provider_test` to verify selected model availability |
| Command API Adapter | Working baseline | `sql_cli.command_api.run_command` reuses existing handlers and adds `cli_equivalent`, `block_type`, and `actions` for mobile/web shells |
| Responsive terminal shell | Local prototype | `app_shell/terminal_shell_prototype` serves a dark-mode mobile/tablet/desktop terminal UI over the Command API; not a packaged mobile app |
| Provider Preset Mobile Flow | Local prototype | setup form can choose preset, edit provider/model/env, preview CLI, and save through `provider_add_preset` |
| Practice Dataset Sandbox | Working baseline | built-in `sql_basics` pack runs in-memory SQLite for DB-free SQL learning, query checks, grading, and attempts |
| Bilingual beginner help | Working baseline | `help_catalog`, `command_explain`, and `term_explain` expose Korean/English command and SQL term explanations through CLI, Command API, and terminal shell |
| JPA | Source introspection only | `jpa_schema` scans annotation-based entity source; JPQL runtime execution is not implemented |
| DB knowledge planner | Seed | generation, natural, and write planning attach local dialect/safety context |
| Schema detail knowledge | Seed | `schema_detail` exposes normalized columns, keys, indexes, constraints, and SQLite create SQL for verified paths |
| Schema validation | Seed | `generate` and simple `natural` requests validate table and simple column identifiers against `schema_detail` |
| Direct join generation | Working baseline | `generate` can infer one-step join `ON` clauses from schema-detail foreign keys; no-path and ambiguous joins fail closed |
| CI automation | Working baseline | GitHub Actions `baseline` and `postgresql-smoke` last recorded successfully on 2026-04-27 UTC for `main` commit `7e677fe` |
| GitHub log demo | Available | public repository can run `baseline` and `postgresql-smoke` manually from GitHub Actions |

## Verification Commands

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command doctor --db example.db --format json
python3 main.py --command generate --db example.db --skill select_simple --params '{"table":"users","cols":["id","name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_inner --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' --format json
python3 main.py --command schema --db-uri sqlite:///Users/Agent/ps-workspace/CoQuery/example.db --format json
python3 main.py --command provider_list_presets --format json
python3 -c "from sql_cli.command_api import run_command; print(run_command('provider_list_presets')['block_type'])"
python3 main.py --command help_catalog --lang ko --format json
python3 main.py --command command_explain --topic natural --lang ko --format json
python3 main.py --command term_explain --topic join --lang en --format json
python3 main.py --command practice_list --format json
python3 main.py --command practice_grade --problem-id basic_select_customers --sql "SELECT id, name, region FROM customers ORDER BY id" --no-record --format json
python app_shell/terminal_shell_prototype/smoke.py
python3 sql_cli/tests/test_core.py
bash scripts/run_postgresql_local_smoke.sh
```

## Notes

- `query` is read-only unless `--write` is set
- dedicated `insert`, `update`, and `delete` handlers require `--write` and explicit SQL
- `insert`, `update`, `delete`, and write-mode `query` accept `--dry-run` to roll back after execution
- `insert`, `update`, `delete`, and write-mode `query` accept `--max-affected-rows` to fail closed on unexpected row counts
- full-table `update`, `delete`, and write-mode `query` statements fail closed unless `--allow-full-table-write` is provided
- `--db-uri` is preferred for future multi-backend commands
- `doctor` exposes masked targets, readiness checks, and structured connection failure codes
- `schema_detail` provides normalized schema metadata for agent-side DB knowledge use
- `generate` and simple `natural` requests can reject unknown tables before returning local SQL
- the local PostgreSQL smoke runner now proves schema-detail-validated `generate select_simple` and `generate count_simple`, then executes the generated SQL
- `generate` can auto-build direct join `ON` clauses from schema detail when both tables are inspectable
- the local PostgreSQL smoke runner now proves direct `generate join_inner` and `generate join_left` slices against a real PostgreSQL schema
- the local PostgreSQL smoke runner now proves `--dry-run`, `--max-affected-rows`, and full-table write rejection against a real PostgreSQL target
- the local PostgreSQL smoke runner was re-run successfully on 2026-04-22
- explicit join `ON` clauses are still allowed, but qualified table/column references are validated against schema detail when available
- `natural` defaults to simple fixed SQL patterns
- `natural --provider-name ...` skips provider calls for simple covered requests and can route complex requests through a registered provider
- provider-backed natural is experimental and secondary to the PostgreSQL proof track
- `provider_add_preset` can register OpenAI, Groq, OpenRouter, Gemini, and DeepSeek-style API providers with provider-specific chat-completions endpoints
- `provider_add` also accepts direct `--chat-completions-url` and `--models-url` overrides for custom OpenAI-compatible services
- `sql_cli.command_api.run_command` is the app-facing adapter for mobile/web shells; it is not an HTTP server yet
- `app_shell/terminal_shell_prototype/server.py` is a local prototype HTTP shell over that adapter for responsive UI verification
- `practice_packs/sql_basics.json` is the built-in sample pack for SQL learning without a user DB connection
- `jpa_schema --jpa-project ...` can provide entity model context for Java/JPA projects
- the PostgreSQL smoke runner checks `PATH` for PostgreSQL binaries before falling back to known Homebrew paths
- `doctor` can classify common PostgreSQL connection failures such as `auth_failed`, `database_not_found`, `host_unreachable`, `connection_refused`, `timeout`, and `ssl_error`
- GitHub Actions workflow files exist at `.github/workflows/baseline.yml` and `.github/workflows/postgresql-smoke.yml`
- the PostgreSQL smoke workflow uses an external PostgreSQL service URI, while the local smoke runner still supports managed local startup
- GitHub Actions `baseline` and `postgresql-smoke` first succeeded on 2026-04-12 in PR `#3`
- GitHub Actions `baseline` and `postgresql-smoke` were last recorded successful on 2026-04-27 UTC for `main` commit `7e677fe`
- use `USAGE_AND_DEMO.md` for local CLI usage and GitHub Actions demo steps

Version: v0.7.1
Last Updated: 2026-07-06
Status: Baseline verified with `doctor`, explicit write safety guards, experimental PostgreSQL schema, schema_detail, query, insert, update, delete, write-safety guard, schema-detail-validated `generate select_simple` / `generate count_simple`, and direct `generate join_inner` / `generate join_left` proof, local DB knowledge-first planning, schema-detail-aware identifier validation, direct schema-detail join inference, provider preset registration, OpenAI-compatible endpoint override, Command API Adapter metadata, dark-mode terminal shell, Provider Preset Mobile Flow, Practice Dataset Sandbox, bilingual beginner help, and verified GitHub Actions baseline / PostgreSQL smoke workflows
Reference: `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`
Smoke Result: `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`
