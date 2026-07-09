# CoQuery Responsive Terminal Shell Prototype

This prototype wraps the existing CoQuery Command API in a mobile-first terminal UI.
The shell defaults to dark mode and supports Korean/English UI labels.

Run from the repository root:

```bash
python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

The local server exposes:

- `GET /api/health`
- `GET /api/sessions`
- `POST /api/commands/run`

The UI uses `/api/commands/run`, which calls `sql_cli.command_api.run_command` directly.
The local packaging decision and rollback path are documented in `docs/desktop-local-packaging-decision.md`.

Verified prototype commands:

- `provider_list_presets`
- `provider_setup`
- `provider_add_preset`
- `schema_detail users`
- `natural show users`
- `practice_list`
- `production_profile_add prod_readonly example.db`
- `production_review prod_readonly SELECT COUNT(*) FROM users`
- `production_approve <review_id>`
- `production_execute <review_id>`
- `help_catalog`
- `command_explain natural`
- `term_explain join`

Bilingual help flow:

1. Toggle `KR` or `EN` in the header.
2. Open `Help` to list beginner-friendly command guidance.
3. Open `Terms` or run `term_explain join` to explain SQL/DB vocabulary.
4. Select any terminal block to see a beginner guide in the detail panel or mobile drawer.

Provider setup flow:

1. Open `Setup AI`.
2. Choose a preset such as Groq, Gemini, OpenRouter, DeepSeek, or OpenAI.
3. Confirm provider name, model name, and API key environment variable.
4. Review the CLI equivalent.
5. Save through `/api/commands/run`, which calls `provider_add_preset`.

Production Assist review flow:

1. Add a read-only profile with `production_profile_add`.
2. Create a review block with `production_review`.
3. Approve the generated SQL with `production_approve`.
4. Execute the approved review with `production_execute`.

Production Assist only allows reviewed read-only `SELECT` statements and writes audit events. For real production targets, use `db_uri_env` instead of storing a DB URI in the profile.

The prototype stores provider profiles under `.runtime/llm_providers.json` inside this prototype folder when provider registration is used.
Practice attempts default to `.coquery/practice_attempts.jsonl` at the repository root.
Production Assist profiles, reviews, and audit logs default to `.coquery/production_profiles.json`, `.coquery/production_reviews.json`, and `.coquery/production_audit.jsonl`.

Responsive behavior:

- desktop/wide: session rail, terminal pane, detail panel
- tablet: terminal pane plus detail panel
- phone: terminal pane plus bottom command bar and bottom detail drawer

Smoke check:

```bash
python app_shell/terminal_shell_prototype/smoke.py
```
