# CoQuery Stage Status Report

Version: v0.7.2
Last Update: 2026-07-09

## Current Status

```text
SQLite-first baseline verified
Explicit write contract frozen
Shared DB URI contract implemented
Doctor diagnostics implemented and verified
PostgreSQL schema, schema_detail, query, insert, update, and delete smoke proved
PostgreSQL schema-detail-validated `generate select_simple` and `generate count_simple` smoke proved
PostgreSQL direct join generation smoke proved for `generate join_inner` and `generate join_left` slices
PostgreSQL write-safety guard smoke proved for dry-run rollback, max-affected rollback, and full-table rejection
Local PostgreSQL smoke re-run succeeded on 2026-04-22
Codex skill package added for agent-side reuse
JPA entity source introspection added as an ORM/model track
Schema-detail direct join generation proved for built-in join skills
Provider presets added for OpenAI, Groq, OpenRouter, Gemini, and DeepSeek-style API registration
Command API Adapter added for mobile/web shell reuse of existing handlers
Responsive Terminal Shell Prototype added as a local mobile/tablet/desktop app shell over the Command API
Provider Preset Mobile Flow added to the dark-mode terminal shell
Practice Dataset Sandbox added for DB-free SQL learning over built-in sample data
Bilingual beginner help added for Korean/English command and SQL term guidance
iOS TestFlight Shell Skeleton added with Capacitor SPM packaging and local `practice_list` runtime proof
Training/Production Assist mode separation added with Command API provider policy guard
Desktop/Local Packaging Decision added for local web app first launch
Production Assist Safety Gate added with read-only profiles, reviewed SQL approval, SELECT-only enforcement, and JSONL audit logging
Release Candidate Hardening added with `npm run rc:verify` as the one-command launch check
PR #4 (`Harden CoQuery release candidate shell`) merged into `main` at commit `20e5d8f`
Last recorded GitHub Actions `baseline` and `postgresql-smoke` proof succeeded on 2026-07-09 UTC for `main` commit `20e5d8f`
GitHub repository `redsunjin/CoQuery` is public
Phase 5 remains narrow and experimental
```

## Phase Overview

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0 | Complete | CLI recovery and command routing are working |
| Phase 1 | Complete enough | `schema` and `query` work on SQLite |
| Phase 2 | Complete enough | structured SQL generation works for built-in skills |
| Phase 3 | Baseline stabilized | explicit `--write` plus explicit SQL is enforced |
| Phase 4 | In stabilization | natural-language path is heuristic by default and can optionally use a registered provider |
| Phase 5 | Early experimental | PostgreSQL `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`, write-safety guard, `generate select_simple`, `generate count_simple`, and direct `generate join_inner` / `generate join_left` smoke slices succeeded; broader backend support is not proven |

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
- `practice_feedback`
- `production_profile_add`
- `production_profile_list`
- `production_review`
- `production_approve`
- `production_execute`

Write-command baseline:

- `insert`, `update`, and `delete` require `--write` and explicit SQL
- `insert`, `update`, `delete`, and write-mode `query` support `--dry-run` preview with rollback
- `insert`, `update`, `delete`, and write-mode `query` support `--max-affected-rows` rollback guards
- full-table `update`, `delete`, and write-mode `query` statements fail closed unless `--allow-full-table-write` is provided

## Backend Support

| Backend | Status | Notes |
|---------|--------|-------|
| SQLite | Working | current verified runtime path |
| PostgreSQL | Experimental (narrow read + write + limited generate) | local smoke proof succeeded for `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`, write-safety guards, `generate select_simple`, `generate count_simple`, plus direct `generate join_inner` / `generate join_left` slices; broader backend support is still not proven |
| MySQL | Stub | URI contract exists; runtime returns structured placeholder error |

CI note:

- GitHub Actions workflow files now exist for baseline and PostgreSQL smoke automation
- the latest local PostgreSQL smoke re-run succeeded on 2026-04-22
- the first observed runs for `baseline` and `postgresql-smoke` both succeeded on 2026-04-12
- the last recorded `main` runs for `baseline` and `postgresql-smoke` both succeeded on 2026-07-09 UTC for commit `20e5d8f`
- the public GitHub repository can run a log-based demo through manual `workflow_dispatch`

ORM/model support:

| Track | Status | Notes |
|-------|--------|-------|
| JPA | Experimental source introspection | `jpa_schema` scans annotation-based entity source; JPQL runtime execution is not implemented |

Natural-language note:

- heuristic by default
- registered-provider routing exists as a secondary experimental track, with provider presets for common OpenAI-compatible APIs
- `sql_cli.command_api.run_command` exposes app-shell metadata around existing handlers without replacing the CLI
- `app_shell/terminal_shell_prototype` is a dark-mode local responsive terminal prototype, not a packaged mobile app or production web service
- `Setup AI` can save a provider profile through `provider_add_preset`
- saved providers can be selected, tested, and removed from the shell, and provider readiness is visible near the command input
- mode-aware Command API responses include `mode_context`
- Production Assist Mode blocks saved external providers by default unless `allow_external_provider=true` is explicitly supplied
- Production Assist execution requires a read-only profile, a generated SQL review, explicit approval, a SELECT-only statement, and an audit record

iOS shell note:

- `ios/` is a Capacitor SPM TestFlight skeleton for Training Mode
- `app_shell/ios_training_shell/src/trainingRuntime.ts` currently handles local `practice_list`, `practice_schema`, `practice_attempts`, and static `practice_feedback`
- the skeleton intentionally does not embed or start the Python local server

Practice sandbox note:

- `practice_packs/sql_basics.json` is the current built-in pack
- `practice_query` and `practice_grade` run against in-memory SQLite, not production data
- `practice_attempts` reads local attempt records for review and wrong-note flows
- `practice_feedback` returns static feedback without a provider; provider-backed feedback is Training Mode only and labeled as AI-generated
- Training Mode is the only launch mode for sample-dataset practice; Production Assist is policy-gated and limited to reviewed read-only SELECT support

Mode boundary note:

- `docs/mode-security-boundary.md` documents the Training vs Production Assist trust boundary
- `docs/production-assist-safety-gate.md` documents the read-only review/approval/audit gate
- external OpenAI-compatible providers are allowed for Training Mode sample-data learning flows
- external providers are blocked for Production Assist natural/provider payloads unless an explicit policy override is supplied
- Goal 9 is implemented for read-only production connection profiles, SQL approval state, SELECT-only guard, audit logging, and redaction; broader production DB support is still not claimed

Desktop/local packaging note:

- non-iOS local launch target is local web app first: Python local server plus browser
- stable start command is `python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765`
- `docs/desktop-local-packaging-decision.md` documents runtime storage, update path, and rollback path
- Tauri/Electron wrappers are deferred until the local shell and release checks stabilize

Doctor note:

- readiness checks include parsed target, driver availability, connection probe, and schema probe where applicable
- PostgreSQL diagnostics classify common failure modes such as `auth_failed`, `database_not_found`, `host_unreachable`, `connection_refused`, `timeout`, and `ssl_error`

## Verification Commands

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 main.py --command doctor --db example.db --format json
python3 sql_cli/tests/test_core.py
python3 app_shell/terminal_shell_prototype/smoke.py
python3 tests/local_packaging_decision_smoke.py
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
bash scripts/run_postgresql_local_smoke.sh
```

## Active Loop

1. keep the GitHub Actions `baseline` and `postgresql-smoke` workflows green
2. align docs to executable behavior
3. keep the PostgreSQL smoke runner repeatable and repo-managed
4. keep `skills/coquery-cli` aligned with runnable CLI behavior
5. keep JPA labelled as ORM/model support until JPQL runtime proof exists
6. keep the terminal shell prototype aligned with Command API behavior
7. keep bilingual help guidance local and curated until an adaptive tutor/LLM feedback flow is explicitly implemented
8. keep provider setup UI honest about model/API key env configuration before any provider call
9. expand practice packs and feedback only after keeping the DB-free baseline green
10. do not broaden join-generation claims beyond direct schema-detail foreign-key inference without a new proof slice
11. use `npm run rc:verify` as the local release-candidate gate before publication

Last Updated: 2026-07-08
Phase Status: SQLite-first baseline verified with `doctor`, PostgreSQL schema, schema_detail, query, insert, update, delete, write-safety guard, schema-detail-validated `generate select_simple` / `generate count_simple`, and direct `generate join_inner` / `generate join_left` smoke proof plus agent skill packaging, JPA source introspection, provider presets, Command API Adapter, dark-mode responsive terminal shell prototype, Provider Preset Mobile Flow, Practice Dataset Sandbox, bilingual beginner help, Training/Production Assist mode separation, Desktop/Local Packaging Decision, Production Assist Safety Gate, Release Candidate Hardening, explicit write safety guards, direct schema-detail join inference, and verified GitHub Actions baseline / PostgreSQL smoke workflows
