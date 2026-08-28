# CoQuery Roadmap

Version: product baseline 2026-08-28
Last Updated: 2026-08-28

## Product Definition

CoQuery is a learning-first SQL product:

`Learn -> Practice -> Apply -> Assist`

The canonical product surface is one shared Web/PWA codebase distributed as:

- Web/PWA
- iPhone app wrapper
- Android app wrapper

Native applications must reuse the shared product logic instead of forking the learning flow.

## Current Verified Position

### Product UX

Verified and merged:

- learning-first Home
- focused SQL practice workspace
- learning path/progress
- 24-problem curriculum
- next-incomplete-problem navigation
- user-flow regression smoke

### SQL / data engine

- SQLite remains the working baseline
- built-in practice sandbox is working
- natural-language SQL remains assistive and local/rule-first where covered
- optional provider infrastructure remains available
- PostgreSQL remains a narrow experimental track with smoke proof
- MySQL is not part of the working baseline

### Product distribution

Merged distribution work:

- PR #13: installable PWA + Cloudflare Python Worker scaffold
- PR #14: isolated Worker bundle + real temporary Cloudflare deployment proof

PR #14 merge commit:

- `2f06ba761eb869c65f91a03f7588ec2d363e1173`

Verified against a real public temporary Cloudflare Worker:

- Worker deployment/startup
- `/api/health`
- PWA shell and standalone manifest
- 24-problem `practice_list`
- SQL execution
- correct grading

The temporary deployment proof is documented in:

- `docs/coquery-cloudflare-temporary-deploy-proof-2026-08-28.md`

## Active Priority Stack

### P0-A. Durable Cloudflare + PWA release baseline

Active branch:

- `ops/cloudflare-production-deploy`

Prepared on the branch:

- manual production deployment workflow
- GitHub `production` environment gate
- `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` secret contract
- reuse of the proven isolated Worker bundle
- post-deploy health/PWA/practice API verification
- production deployment contract regression checks
- manual browser/device PWA QA checklist

Reference:

- `.github/workflows/cloudflare-production-deploy.yml`
- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`

Remaining release gate:

1. configure `CLOUDFLARE_ACCOUNT_ID` in GitHub Actions secrets
2. configure `CLOUDFLARE_API_TOKEN` in GitHub Actions secrets
3. manually run `cloudflare-production-deploy`
4. record the durable `workers.dev` URL and workflow run ID
5. execute browser learner-flow QA
6. verify browser-local progress across reload/relaunch
7. verify service-worker offline shell behavior
8. verify PWA installation on supported desktop/iOS/Android browsers

Cloudflare's official CI/CD guidance requires the account ID and API token for non-interactive deployment. Do not commit either credential to the repository.

### P0-B. AI Context-to-Prompt Handoff — first slice

Starts after the durable hosted/browser baseline is recorded unless an explicit priority decision changes the gate.

First implementation boundary:

`natural result -> Build AI validation prompt -> Preview -> Copy`

Core modules:

- ContextAdapter
- ExportPolicy
- QuestionPolicy
- PromptComposer
- PromptPreview
- HandoffAdapter

No new backend is required for the first slice.

Reference:

- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

### P0-C. iOS / Android wrapper baseline

After hosted PWA behavior is stable:

- validate the minimal wrapper choice
- keep shared Web/PWA source canonical
- create thin iOS and Android wrappers
- prove simulator/emulator flows
- map clipboard/share through platform adapters where necessary
- prepare store assets and metadata separately

Preferred direction remains a thin Capacitor-style wrapper, subject to implementation-time toolchain/store validation.

### P1

- Practice-result AI handoff
- system share / selectable external AI destination
- My Data bridge
- learner-feedback-driven curriculum refinement

### P2

- constrained Production Assist external handoff only after export-rights policy proof
- optional cross-device progress sync

## Completed Product History — August 2026

- PR #8 — first-run learning Home
- PR #9 — focused practice workspace
- PR #10 — learning path/progress
- PR #11 — curriculum expansion to 24 problems
- PR #12 — learner-flow QA and next-problem navigation
- PR #13 — PWA + Cloudflare serverless scaffold
- PR #14 — real temporary Cloudflare deployment proof and isolated deployment harness

## Verification Baseline

Core CI:

- CLI/core verification
- practice focus smoke
- learning path smoke
- curriculum smoke
- user-flow QA smoke
- PWA/serverless smoke
- separate PostgreSQL smoke

Deployment verification:

- temporary Cloudflare remote proof workflow
- production deployment workflow contract checks

## Scope Locks

Do not silently:

- split the canonical PWA into separate native product implementations
- make external AI mandatory for SQL generation
- automatically send data to an AI
- expose Production Assist data through AI handoff before ExportPolicy proof
- describe temporary Cloudflare proof as durable production deployment
- describe HTTP proof as completed browser/device/install QA
- broaden PostgreSQL/MySQL support claims without new proof

## Official Execution Loop

For each slice:

1. confirm current `main`
2. create a branch
3. document the scope and proof boundary
4. add regression/contract tests where practical
5. implement the smallest valid change
6. keep baseline CI green
7. keep PostgreSQL smoke truthful when relevant
8. record exactly what was verified and skipped
9. merge only after explicit approval
10. currentize `EASY_SQL_ROADMAP.md`, `EASY_SQL_TODO.md`, and `HANDOFF.md`

## Next Decision Gate

Immediate gate:

**configure the two Cloudflare GitHub Actions secrets and execute the manual durable production workflow.**

Execution order remains:

`learning UX -> PWA/serverless -> hosted proof -> durable PWA QA -> AI validation handoff -> iOS/Android wrappers`
