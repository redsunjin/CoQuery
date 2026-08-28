# CoQuery PWA + Cloudflare Serverless Deployment

Date: 2026-08-28

## Decision

CoQuery's public learning surface should be deployable as an installable PWA on Cloudflare Workers using:

- Cloudflare Static Assets for the existing HTML/CSS/JS shell
- a Cloudflare Python Worker for `/api/*`
- the existing `sql_cli.command_api.run_command()` implementation for practice execution/grading
- browser `localStorage` for learner attempt/progress persistence in the first hosted MVP

This preserves the current architecture and avoids adding a new application server or database just to publish the learning MVP.

## Why this fits the current project

The current local shell already separates:

- static browser UI
- `/api/health`
- `/api/sessions`
- `/api/commands/run`

Cloudflare Workers can serve static assets and route only `/api/*` through Worker code. Python Workers can execute Python application logic, so the hosted adapter can reuse the existing command layer rather than rewriting it in JavaScript.

## Important Cloudflare constraint

Cloudflare Python Workers use an ephemeral in-memory filesystem. File writes can be used temporarily but are not durable across Worker isolates.

Therefore the hosted learning MVP must not depend on these existing file-backed stores for persistence:

- `.coquery/practice_attempts.jsonl`
- LLM provider registry files
- Production Assist profile/review/audit files

For the first public PWA, learner attempts are stored in browser `localStorage`. The Worker forces `practice_grade.no_record=true`.

Future multi-device/login synchronization can move progress to D1 or another durable Cloudflare store without changing the learner-facing flow.

## Hosted MVP command boundary

The public Worker exposes only learning-safe commands:

- `practice_list`
- `practice_schema`
- `practice_query`
- `practice_grade`
- `practice_feedback` (static feedback only)
- `help_catalog`
- `command_explain`
- `term_explain`
- `db_knowledge`

Provider configuration, Production Assist, external database access, and other advanced/local commands are intentionally not exposed from the public practice PWA in this phase.

## PWA behavior

The PWA adds:

- web app manifest
- standalone display mode
- dark theme metadata
- CoQuery application icon
- service worker registration
- app-shell caching
- browser-local learner progress

Offline boundary:

- the application shell can reopen from cache
- SQL execution and grading still require network access to the Worker

Moving SQLite grading fully into the browser is explicitly outside this phase.

## Files

Root deployment files:

- `cloudflare_worker.py`
- `wrangler.jsonc`
- `pyproject.toml`

PWA files:

- `app_shell/terminal_shell_prototype/manifest.webmanifest`
- `app_shell/terminal_shell_prototype/coquery-icon.svg`
- `app_shell/terminal_shell_prototype/service-worker.js`
- `app_shell/terminal_shell_prototype/pwa-runtime.js`
- `app_shell/terminal_shell_prototype/.assetsignore`

Verification:

- `app_shell/terminal_shell_prototype/pwa_serverless_smoke.py`

## Cloudflare configuration

`wrangler.jsonc` uses:

- `python_workers` compatibility flag
- `cloudflare_worker.py` as the Worker entrypoint
- `app_shell/terminal_shell_prototype` as Static Assets
- `run_worker_first: ["/api/*"]`
- SPA fallback for static navigation
- additional module inclusion for `practice_packs/**/*.json`

## Local Cloudflare development

Prerequisites:

- Node.js
- `uv`
- Cloudflare account authentication when deploying

Install/update dependencies:

```bash
uv sync
```

Run the Worker locally:

```bash
uv run pywrangler dev
```

Deploy after account authentication:

```bash
uv run pywrangler deploy
```

Before deployment, run the existing baseline CI and confirm the Worker bundle includes the practice-pack JSON files. A Cloudflare dry-run/build check should be treated as a deployment gate because Python Workers remain beta.

## Deployment acceptance checks

1. `/api/health` returns `coquery-pwa-worker`.
2. App loads from the Worker URL without login.
3. Browser identifies the site as installable where supported.
4. `첫 문제 시작하기` opens the first incomplete problem.
5. Correct grading persists progress after browser refresh.
6. Problem bank shows saved completion state after refresh.
7. Service worker can reopen the shell after it has been visited once.
8. Grading clearly fails as offline/network-required rather than silently losing work.
9. Hosted advanced commands return `hosted_command_unavailable` rather than exposing local/production behavior.

## Next deployment step

After this branch is merged and CI passes, connect the repository to the target Cloudflare account or deploy with `pywrangler deploy`, then perform browser/PWA QA against the generated `workers.dev` URL before assigning a custom domain.

## Official references

- Cloudflare Python Workers: https://developers.cloudflare.com/workers/languages/python/
- Python Workers standard library / ephemeral filesystem: https://developers.cloudflare.com/workers/languages/python/stdlib/
- Static Assets: https://developers.cloudflare.com/workers/static-assets/
- Static Assets routing and `run_worker_first`: https://developers.cloudflare.com/workers/static-assets/binding/
- Wrangler configuration: https://developers.cloudflare.com/workers/wrangler/configuration/
