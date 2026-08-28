# CoQuery Cloudflare Temporary Deployment Proof

Date: 2026-08-28

## Result

CoQuery's learning-first PWA was successfully deployed to a real Cloudflare temporary Worker and verified over the public network.

Successful proof run:

- GitHub Actions workflow: `cloudflare-temporary-deploy`
- run ID: `33148714909`
- head: `e09bd59b8ff891cab3a00918ec67659759e8dfc2`
- temporary Worker URL at proof time: `https://coquery-pwa.unleashed-printer.workers.dev`
- deployment type: authentication-free temporary Cloudflare account
- status: all deployment and remote HTTP/API checks passed

The temporary URL is evidence only. It is not a production URL and should not be treated as durable product hosting.

## What Was Actually Verified

The workflow performed these checks against the deployed Worker, not against localhost:

1. Worker bundle preparation completed.
2. Cloudflare upload/deployment completed.
3. Worker startup completed.
4. `GET /api/health` returned HTTP 200 and:
   - `ok: true`
   - `service: coquery-pwa-worker`
   - `runtime: cloudflare-python-worker`
   - `hosted_mode: practice-first`
   - `progress_storage: browser-localStorage`
5. `/` served the PWA HTML shell.
6. `/manifest.webmanifest` returned valid JSON with `display: standalone`.
7. `practice_list` returned at least 24 problems through the hosted command API.
8. `practice_query` successfully executed:
   `SELECT id, name, region FROM customers ORDER BY id`
9. `practice_grade` successfully graded the same SQL for `basic_select_customers` as correct.

This proves that the existing Python command/practice path can run behind Cloudflare Workers for the hosted practice MVP.

## Deployment Harness

The successful path does not deploy the whole repository directly.

`scripts/prepare_cloudflare_bundle.py` creates an isolated staging tree:

- `.cloudflare-build/src/cloudflare_worker.py`
- `.cloudflare-build/src/sql_cli/`
- `.cloudflare-build/src/practice_packs/`
- `.cloudflare-build/src/knowledge/`
- `.cloudflare-build/assets/`

It also writes Cloudflare's generated deployment config redirect under `.wrangler/deploy/config.json` so Pywrangler deploys only the staged runtime.

Generated deployment artifacts are ignored by Git.

## Problems Found During Real Deployment

### 1. Repository-wide module scan created an oversized Worker

Initial result:

- upload size: about 16.5 MiB
- cause: `find_additional_modules` scanned the repository root and pulled in virtual environments, Node modules, docs, and local tooling
- Cloudflare temporary-account limit rejected the Worker

Resolution:

- build an explicit isolated deployment tree
- stop using repository-wide discovery

### 2. Over-restricting the scan removed `sql_cli`

After narrowing the scan to only practice-pack files:

- upload size dropped to about 117 KiB
- deployment then failed with `ModuleNotFoundError: sql_cli`

Resolution:

- stage the actual Python runtime package and data resources together

### 3. Selective Static Assets routing produced API 404s

With the complete staged bundle:

- Worker upload succeeded
- Python Worker startup succeeded
- Static Assets upload succeeded
- immediate `/api/health` still returned 404

Resolution:

- make the Worker run first for the deployed application
- handle `/api/*` explicitly in Python
- delegate all non-API requests to `self.env.ASSETS.fetch(request)`

This produced the first fully successful remote run.

## Current Boundary

Verified:

- remote Cloudflare deployment
- Python Worker startup
- PWA shell/manifest delivery
- hosted practice problem listing
- hosted SQL execution
- hosted grading

Not yet verified:

- interactive visual/browser layout QA
- actual install prompt/install completion on desktop, iOS, or Android
- service-worker offline reopening on a real device/browser
- browser-local progress persistence through a real browser refresh
- permanent Cloudflare account deployment
- custom domain

Do not describe these untested items as complete.

## Next Gate

1. merge the deployment-proof/harness PR after CI and explicit approval
2. connect or authenticate the target Cloudflare account for a durable `workers.dev` deployment
3. perform real browser/device PWA QA
4. record the durable hosted URL only after that verification
5. then start the AI Context-to-Prompt Handoff implementation slice
