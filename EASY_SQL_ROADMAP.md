# CoQuery Roadmap

Version: product baseline 2026-09-02
Last Updated: 2026-09-02

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

- SQLite remains the working practice baseline
- built-in practice sandbox is working
- natural-language SQL remains assistive and local/rule-first where covered
- optional provider infrastructure remains available
- PostgreSQL remains a narrow experimental/runtime-smoke track
- MySQL does not yet have a working runtime baseline

### Product distribution

Merged:

- PR #13 — installable PWA + Cloudflare Python Worker scaffold
- PR #14 — isolated Worker bundle + real temporary Cloudflare deployment proof
- PR #15 — durable production deployment workflow + PWA QA harness
- PR #16 — production API verification hardened for deployment propagation delay

Latest merged baseline before this branch:

- `5752cd24142da60496e42b66e35d1a546e4a0c06`

Durable public Worker:

- `https://coquery-pwa.edu-public-app.workers.dev`

Verified by production workflow:

- Worker deployment/startup
- `/api/health`
- PWA shell and manifest
- 24-problem practice listing
- SQL execution
- grading

Interactive browser/device installation QA is still separate from the automated HTTP proof.

## Active Priority Stack

### P0-A. Browser/device PWA release QA

Automated production deployment is proven. Remaining release-quality evidence:

1. Home -> problem bank -> solve -> grade -> next problem
2. progress persistence across reload/relaunch
3. offline cached-shell behavior
4. explicit network-required behavior for SQL execution
5. `/api/*` not served from stale service-worker cache
6. desktop PWA installation where supported
7. iOS Safari Add to Home Screen baseline
8. Android Chrome install/add-to-home-screen baseline

Reference:

- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`

### P0-B. AI Context-to-Prompt Handoff — first slice

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

## P1 — Learning Quality Expansion

### P1-A. SQL Dialect Learning — approved parallel slice

Purpose:

**teach common SQL first, then reveal PostgreSQL/MySQL/SQLite differences only when useful.**

Learner surface:

`Problem -> Run/Grade -> DB별 차이 보기 -> PostgreSQL | MySQL | SQLite`

Rules:

- do not turn the beginner curriculum into a PostgreSQL/MySQL course
- explain intent before syntax
- label examples as `common`, `reference`, or `verified`
- MySQL remains `reference` until a real MySQL runtime/test baseline exists
- do not build a general SQL transpiler in the first slice

Phase A:

- deterministic DialectCatalog
- first 4 high-value comparison topics
- PostgreSQL/MySQL/SQLite variants
- KR/EN content
- optional comparison card in practice feedback
- catalog/problem-mapping tests

Reference:

- `docs/coquery-sql-dialect-learning-plan-2026-09-02.md`

### P1-B. Result Intelligence / BI interpretation

Direction under product design:

`Table | Chart | Flow | Explain`

This answers what a query result means, while SQL Dialect Learning answers how equivalent SQL can differ by database engine. Keep the two concepts separate in the first implementation.

### Other P1 items

- Practice-result AI handoff
- system share / selectable external AI destination
- My Data bridge
- learner-feedback-driven curriculum refinement

## P2

- constrained Production Assist external handoff only after export-rights policy proof
- optional cross-device progress sync
- broader engine-backed dialect verification only when runtime environments justify it

## Completed Product History — August 2026

- PR #8 — first-run learning Home
- PR #9 — focused practice workspace
- PR #10 — learning path/progress
- PR #11 — curriculum expansion to 24 problems
- PR #12 — learner-flow QA and next-problem navigation
- PR #13 — PWA + Cloudflare serverless scaffold
- PR #14 — real temporary Cloudflare deployment proof and isolated deployment harness
- PR #15 — production deployment + PWA QA harness
- PR #16 — hardened production API verification

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
- production Cloudflare workflow
- post-deploy health/PWA/practice API checks

## Scope Locks

Do not silently:

- split the canonical PWA into separate native product implementations
- make external AI mandatory for SQL generation
- automatically send data to an AI
- expose Production Assist data through AI handoff before ExportPolicy proof
- describe HTTP proof as completed browser/device/install QA
- broaden PostgreSQL/MySQL support claims without new proof
- present reference dialect examples as engine-verified
- make DB-specific syntax mandatory in beginner lessons

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

## Current Decision Gate

Active parallel work is allowed when it does not destabilize P0 release work.

Current execution tracks:

`PWA QA -> AI validation handoff -> mobile wrappers`

and

`SQL learning quality -> dialect comparison -> result intelligence`
