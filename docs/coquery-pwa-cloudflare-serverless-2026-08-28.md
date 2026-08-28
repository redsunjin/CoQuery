# CoQuery PWA + Cloudflare Serverless Deployment

Date: 2026-08-28
Status: temporary hosted HTTP/API proof complete; permanent-account and device/browser QA pending

## Decision

CoQuery's canonical product surface is one installable PWA/web application that can later be wrapped for iPhone and Android.

The hosted learning MVP uses:

- Cloudflare Static Assets for the existing HTML/CSS/JS shell
- a Cloudflare Python Worker for the command API
- the existing `sql_cli.command_api.run_command()` implementation for practice execution/grading
- browser `localStorage` for learner attempt/progress persistence

No new application server or database is required for the first hosted learning MVP.

## Verified Cloudflare Result

A real authentication-free Cloudflare temporary Worker deployment succeeded on 2026-08-28.

The successful GitHub Actions proof verified remotely:

- Worker deployment and startup
- `GET /api/health`
- PWA HTML shell delivery
- `manifest.webmanifest`
- all 24 practice problems through `practice_list`
- real `practice_query` execution
- correct `practice_grade` result

Evidence:

- `docs/coquery-cloudflare-temporary-deploy-proof-2026-08-28.md`
- workflow: `.github/workflows/cloudflare-temporary-deploy.yml`

This is a hosted runtime proof, not a permanent production deployment.

## Important Cloudflare Constraint

Cloudflare Python Workers use an ephemeral in-memory filesystem. File writes are not durable learner storage.

The hosted learning MVP therefore must not depend on these local file-backed stores:

- `.coquery/practice_attempts.jsonl`
- LLM provider registry files
- Production Assist profile/review/audit files

The Worker forces `practice_grade.no_record=true`. The browser PWA stores learner attempts/progress in `localStorage`.

Future multi-device/login synchronization can move progress to D1 or another durable store only when the product requires it.

## Hosted MVP Command Boundary

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

Provider configuration, Production Assist, external database access, and other advanced/local commands remain unavailable from the public practice-first PWA.

## PWA Behavior

The PWA provides:

- web app manifest
- standalone display mode
- application icon/theme metadata
- service-worker registration
- app-shell caching
- browser-local learner progress

Offline boundary:

- the application shell can reopen from cache by design
- SQL execution and grading require network access to the Worker

Actual offline reopening on target browsers/devices has not yet been verified and must not be claimed as complete.

## Deployment Packaging Rule

Do **not** deploy the repository root as the Worker module tree.

A real deployment attempt proved that repository-wide additional-module scanning pulls in local environments/tooling and can create a grossly oversized Worker bundle.

Canonical preparation:

```bash
python3 scripts/prepare_cloudflare_bundle.py
```

This creates an isolated generated bundle under `.cloudflare-build/` containing only:

- Worker entrypoint
- required `sql_cli` Python modules
- `practice_packs`
- `knowledge` JSON
- PWA static assets

It also creates Cloudflare's generated config redirect under `.wrangler/deploy/config.json`.

Both generated directories are ignored by Git.

## Temporary Deployment Proof

Install/update local tooling:

```bash
uv sync
npm install --no-save wrangler@latest
```

Prepare the bundle:

```bash
python3 scripts/prepare_cloudflare_bundle.py
```

Create an authentication-free temporary Cloudflare preview:

```bash
uv run pywrangler deploy --temporary
```

The repository workflow automates the same process and verifies remote endpoints:

```text
.github/workflows/cloudflare-temporary-deploy.yml
```

The temporary URL is evidence only and should not be used as the final public product URL.

## Permanent Deployment Path

After authenticating the target Cloudflare account:

```bash
python3 scripts/prepare_cloudflare_bundle.py
uv run pywrangler deploy
```

Permanent deployment is not yet recorded as verified.

Before attaching a custom domain, verify the durable `workers.dev` deployment and target-device PWA behavior.

## Static Assets Routing

The proven deployment pattern uses Worker-first routing for the staged application:

1. Python Worker receives the request.
2. `/api/*` is handled explicitly by the Worker.
3. non-API requests are delegated to the `ASSETS` binding.

Worker fallback:

```python
return await self.env.ASSETS.fetch(request)
```

This was chosen after real temporary deployment exposed unreliable behavior in the earlier selective-routing proof path.

## Files

Source deployment/runtime files:

- `cloudflare_worker.py`
- `wrangler.jsonc`
- `pyproject.toml`
- `scripts/prepare_cloudflare_bundle.py`

PWA files:

- `app_shell/terminal_shell_prototype/manifest.webmanifest`
- `app_shell/terminal_shell_prototype/coquery-icon.svg`
- `app_shell/terminal_shell_prototype/service-worker.js`
- `app_shell/terminal_shell_prototype/pwa-runtime.js`
- `app_shell/terminal_shell_prototype/.assetsignore`

Verification:

- `app_shell/terminal_shell_prototype/pwa_serverless_smoke.py`
- `.github/workflows/cloudflare-temporary-deploy.yml`
- `docs/coquery-cloudflare-temporary-deploy-proof-2026-08-28.md`

## Verified vs Pending

Verified remotely:

- Worker bundle/deploy/startup
- health endpoint
- PWA shell delivery
- PWA manifest delivery
- 24-problem listing
- SQL execution
- grading

Pending real browser/device verification:

- Home -> problem bank -> solve -> grade -> next problem visual flow
- learner progress across browser refresh
- service-worker offline shell reopening
- actual PWA installation
- iOS target behavior
- Android target behavior

Pending infrastructure:

- target Cloudflare account authentication
- durable `workers.dev` deployment
- custom domain decision

## Next Deployment Gate

1. merge the deployment-proof/harness PR after CI and explicit approval
2. deploy to the target Cloudflare account
3. perform browser/device PWA QA
4. record the durable hosted URL and exact verified behavior
5. proceed to AI Context-to-Prompt Handoff implementation

## Official references

- Cloudflare Python Workers: https://developers.cloudflare.com/workers/languages/python/
- Python Workers standard library / filesystem: https://developers.cloudflare.com/workers/languages/python/stdlib/
- Static Assets: https://developers.cloudflare.com/workers/static-assets/
- Static Assets binding/routing: https://developers.cloudflare.com/workers/static-assets/binding/
- Wrangler configuration: https://developers.cloudflare.com/workers/wrangler/configuration/
