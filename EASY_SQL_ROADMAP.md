# CoQuery Roadmap

Version: product baseline 2026-08-30
Last Updated: 2026-08-30

## Product Definition

CoQuery is a learning-first SQL product:

`Learn -> Practice -> Apply -> Assist`

The canonical product surface is one shared Web/PWA codebase distributed as:

- Web/PWA
- iPhone app wrapper
- Android app wrapper

Native applications must reuse the shared product logic instead of forking the learning flow.

A SQL result is not limited to an Excel-like grid. The approved result-intelligence direction is:

`Table -> Visual -> Flow -> Explain`

Table remains the canonical evidence view; Visual/Flow/Explain are derived, explainable views.

## Current Verified Position

### Product UX

Verified and merged:

- learning-first Home
- focused SQL practice workspace
- learning path/progress
- 24-problem curriculum
- next-incomplete-problem navigation
- user-flow regression smoke

Current result-view gap:

- `practice_query` still presents a limited JSON-row preview
- no deterministic BI/visual interpretation layer yet

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
- PR #15: durable Cloudflare production deployment workflow + PWA QA contract
- PR #16: hardened post-deploy practice API verification

Durable production Worker:

- `https://coquery-pwa.edu-public-app.workers.dev`

Successful production workflow proof:

- run `33160202910`
- deployment: success
- `/api/health`: success
- PWA shell/manifest: success
- hosted practice API: success

PR #16 merge commit:

- `5752cd24142da60496e42b66e35d1a546e4a0c06`

Browser/device installation QA remains separate and is not implied by the automated deployment proof.

## Active Priority Stack

### P0-A. Browser/device PWA QA — release evidence

Durable hosted deployment is complete. Remaining release evidence:

- browser learner flow: Home -> problem -> execute/grade -> next problem
- progress across reload/relaunch
- explicit offline-shell/network-required behavior
- service-worker API cache boundary
- desktop PWA install where supported
- iOS Safari Add to Home Screen
- Android Chrome install/add-to-home-screen

Reference:

- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`

This evidence remains required before native wrapper release claims.

### P0-B. BI Result Intelligence — active product slice

Priority was explicitly moved forward after durable production deployment.

Approved surface:

`Table | Visual | Flow | Explain`

First implementation boundary:

`practice_query result -> classify -> Table | Visual recommendation | SQL Flow | Explain`

Core rules:

- deterministic first; no LLM required
- Table is always available and remains the evidence baseline
- high-confidence result shapes may recommend a chart
- ambiguous shapes fall back to Table
- SQL Flow contains only recognized query clauses
- visualization recommendation explains why it was selected
- no React migration in the first slice

Bklit UI is a design/component reference for chart patterns such as Bar, Line, Funnel, Sankey, Gauge, and Choropleth. Current CoQuery is plain HTML/CSS/JS, so direct React registry adoption is deferred until a deliberate frontend architecture decision.

Reference:

- `docs/coquery-bi-result-intelligence-2026-08-30.md`

Implementation order:

1. ResultShape classifier + contract tests
2. real Table renderer
3. Bar renderer for category + measure
4. SQL clause Flow renderer
5. deterministic Explain copy
6. Line/time-series support

### P0-C. AI Context-to-Prompt Handoff — first slice

Starts after the BI result-intelligence first slice unless an explicit priority decision changes the gate.

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

### P0-D. iOS / Android wrapper baseline

After hosted PWA behavior and browser/device evidence are stable:

- validate the minimal wrapper choice
- keep shared Web/PWA source canonical
- create thin iOS and Android wrappers
- prove simulator/emulator flows
- map clipboard/share through platform adapters where necessary
- prepare store assets and metadata separately

Preferred direction remains a thin Capacitor-style wrapper, subject to implementation-time toolchain/store validation.

### P1

- additional BI visuals only when ResultShape rules justify them
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
- PR #15 — durable production deployment workflow and PWA QA gate
- PR #16 — production API verification hardening, proven by successful production deploy

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
- durable production workflow
- post-deploy health/PWA/practice API checks

BI result intelligence must add deterministic classifier/fallback regression coverage before merge.

## Scope Locks

Do not silently:

- split the canonical PWA into separate native product implementations
- make external AI mandatory for SQL generation or result interpretation
- automatically send data to an AI
- expose Production Assist data through AI handoff before ExportPolicy proof
- describe automated HTTP proof as completed browser/device/install QA
- broaden PostgreSQL/MySQL support claims without new proof
- turn the BI result slice into an undeclared React migration
- reuse or redistribute Bklit Studio; only the upstream MIT chart-component boundary is eligible for later technical evaluation
- invent chart dimensions, targets, flow edges, geographic meaning, or stage order

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

Immediate implementation gate:

**prove the deterministic BI ResultShape classifier and Table fallback before adding chart rendering.**

Execution direction:

`learning UX -> hosted PWA -> durable deploy -> BI result intelligence -> AI validation handoff -> iOS/Android wrappers`

Browser/device PWA QA remains an open release-evidence track in parallel.
