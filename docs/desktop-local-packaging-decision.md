# CoQuery Desktop/Local Packaging Decision

Date: 2026-07-08

Selected launch target: local web app first.

CoQuery's non-iOS launch package is a local Python HTTP server plus the responsive terminal shell opened in a browser.
Do not ship a Tauri or Electron wrapper for the first local release.
The desktop wrapper remains a later packaging option after the local web shell and release checks stabilize.

## Launch Target

Selected:

```text
Local web app first: Python local server + browser
```

Deferred:

- Tauri desktop wrapper
- Electron desktop wrapper
- hosted production web service
- packaged production DB assistant

This keeps the first local release aligned with the current verified runtime: `sql_cli.command_api.run_command` served by `app_shell/terminal_shell_prototype/server.py`.

## Stable Start Command

Run from the repository root:

```bash
python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

The wrapper delegates to `app_shell/terminal_shell_prototype/server.py`, so existing server flags remain stable:

- `--host`: defaults to `127.0.0.1`
- `--port`: defaults to `8765`

The direct server command still works, but the wrapper is the documented local packaging entrypoint.

## Runtime Storage Paths

Provider registry:

```text
app_shell/terminal_shell_prototype/.runtime/llm_providers.json
```

Override with:

```text
COQUERY_LLM_REGISTRY_PATH
```

Practice attempt log:

```text
.coquery/practice_attempts.jsonl
```

Override with:

```text
COQUERY_PRACTICE_ATTEMPT_LOG
```

Production Assist safety gate:

```text
.coquery/production_profiles.json
.coquery/production_reviews.json
.coquery/production_audit.jsonl
```

Override with:

```text
COQUERY_PRODUCTION_PROFILE_PATH
COQUERY_PRODUCTION_REVIEW_PATH
COQUERY_PRODUCTION_AUDIT_LOG
```

Generated iOS shell assets:

```text
dist/ios-shell/
```

This directory is build output and is ignored by git.

No API key secret values are stored by CoQuery. Provider profiles store the environment variable name, such as `GEMINI_API_KEY`, not the key value. Production Assist profiles should use `db_uri_env` for real production targets so DB secrets stay in the environment.

## Update Path

Update path for the local release:

1. Pull or checkout the newer repository revision.
2. Run `python3 sql_cli/tests/test_core.py`.
3. Run `python3 app_shell/terminal_shell_prototype/smoke.py`.
4. Run `python3 tests/local_packaging_decision_smoke.py`.
5. Start the local shell with `python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765`.

Local runtime files are intentionally outside the committed release surface. Updating code should not delete `.runtime/llm_providers.json`, `.coquery/practice_attempts.jsonl`, or `.coquery/production_*.json*`.

## Rollback Path

Rollback path:

1. Stop the local shell process.
2. Checkout the previous known-good commit or release tag.
3. Start again with `python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765`.
4. If a provider profile causes local startup or provider testing issues, move `app_shell/terminal_shell_prototype/.runtime/llm_providers.json` aside and restart.
5. If practice attempt display is the problem, move `.coquery/practice_attempts.jsonl` aside and restart.
6. If Production Assist state causes local review issues, move `.coquery/production_profiles.json`, `.coquery/production_reviews.json`, or `.coquery/production_audit.jsonl` aside and restart.

Rollback should not require deleting the repository, reinstalling Python packages, or resetting user secrets.

## First Local Release Boundary

Included:

- local responsive terminal shell
- Command API backed by current Python handlers
- Training Mode sample-dataset practice flow
- provider setup, selection, test, and removal UI
- Training/Production Assist mode indicator and provider policy guard

Excluded:

- packaged production DB assistant claim
- desktop installer
- background auto-update agent
- bundled Python runtime
- hosted account or multi-user service

Goal 9 adds the local reviewed read-only SELECT gate. A packaged production DB assistant still needs release-candidate hardening and real credential validation before broader positioning.
