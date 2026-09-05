# CoQuery Durable Cloudflare + PWA QA Gate

Date: 2026-09-05
Status: durable Worker beta deployed; interactive browser/device QA and custom-domain work remain

## Purpose

This document is the release gate between the proven temporary Cloudflare Worker and the durable public PWA baseline that will later be wrapped for iOS and Android.

The canonical product remains one shared Web/PWA codebase.

## Durable deployment contract

Production deployment is executed only by:

- `.github/workflows/cloudflare-production-deploy.yml`
- manual `workflow_dispatch`
- GitHub `production` environment
- `CLOUDFLARE_ACCOUNT_ID` secret
- `CLOUDFLARE_API_TOKEN` secret

The workflow reuses the already-proven isolated bundle created by:

- `scripts/prepare_cloudflare_bundle.py`

It does not deploy directly from the repository root module scan.

## Credential boundary

Never commit these values:

- Cloudflare API token
- Cloudflare account ID when it is treated as deployment configuration for the private account workflow
- global API key

Required GitHub Actions secrets:

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

The API token should be scoped to the target account and Worker deployment permissions only.

## Automated production checks

After a successful durable deploy the production workflow must verify:

1. Worker URL is returned.
2. `GET /api/health` returns HTTP 200 and `service=coquery-pwa-worker`.
3. `/` serves the PWA shell.
4. `manifest.webmanifest` is valid and `display=standalone`.
5. `practice_list` returns at least 24 problems.
6. `practice_grade` correctly grades the known baseline problem.

A durable deploy is not called successful if deployment succeeds but any of these checks fail.

## Manual browser QA

The automated HTTP proof is necessary but not sufficient.

Run against the durable Worker URL:

### First-run learner flow

- open the public URL without login
- confirm the learning-first Home appears
- choose `첫 문제 시작하기`
- confirm the focused SQL workspace appears
- run a correct SQL answer
- confirm correct feedback appears
- use `다음 문제`
- return to the learning path

### Progress persistence

- complete at least one problem
- refresh the page
- confirm completed state remains
- fully close and reopen the browser/PWA
- confirm progress remains in the same browser profile

### Network/offline boundary

- visit once while online
- go offline
- reopen the PWA shell
- confirm the cached shell opens
- attempt SQL execution
- confirm the UI reports a network-required failure rather than losing the user's SQL silently
- return online and confirm execution works again

### Service-worker safety

- confirm `/api/*` responses are not served from stale application-shell cache
- refresh after a grading action and confirm live API behavior remains correct

## Installation QA

### Desktop browser

Where the browser supports PWA installation:

- installation entry is available
- installed app launches standalone
- app icon/name are correct
- reload retains learner progress

### iPhone / iPad

Before a native wrapper exists, verify the PWA browser baseline:

- Safari loads the full learner flow
- Add to Home Screen works where supported
- standalone launch opens the correct page
- progress remains after relaunch

This is PWA QA, not App Store/native wrapper QA.

### Android

Before the native wrapper exists, verify the PWA browser baseline:

- Chrome loads the full learner flow
- install/add-to-home-screen flow works where supported
- standalone launch opens the correct page
- progress remains after relaunch

This is PWA QA, not Play Store/native wrapper QA.

## Evidence to record

After durable deployment, update `HANDOFF.md`, `EASY_SQL_ROADMAP.md`, and `EASY_SQL_TODO.md` with:

- durable Worker URL
- production workflow run ID
- deployment head SHA
- browser/device names and versions actually tested
- installation result
- progress persistence result
- offline shell result
- any skipped validation

Do not replace missing evidence with assumptions.

## Current gate

The durable deployment completed on 2026-09-05:

- Worker: `https://coquery-pwa.edu-public-app.workers.dev`
- workflow: [run 33948547355](https://github.com/redsunjin/CoQuery/actions/runs/33948547355)
- source commit: `efd351e8b82c4352cdac8eae7a7773b088160a3e`
- automated deployment, health, shell, manifest, hosted practice listing, SQL execution, and grading checks: passed

The next release gate is interactive browser/device evidence, followed by the explicit custom-domain and install-icon decisions. Keep the existing least-privilege secrets in the protected GitHub environment; never record their values here.

## Official references

- Cloudflare GitHub Actions CI/CD: https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/
- Cloudflare CI/CD overview: https://developers.cloudflare.com/workers/ci-cd/
- Wrangler deploy: https://developers.cloudflare.com/workers/wrangler/commands/workers/
