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

### Product principle: SQL as Visual Data Transformation

CoQuery treats SQL as a declarative relational/data transformation expression that can be understood visually.

This is analogous to a mathematical expression only at the level of a compact symbolic statement producing a structured transformation/result. SQL is **not** reduced to a simple numeric function.

The approved result-understanding surface remains:

`Table -> Visual -> Flow -> Explain`

Three visual layers are explicitly separated:

1. **Query Graph** — what transformation the SQL describes; core learning experience.
2. **Result Visual** — what shape the exact returned data has; BI interpretation.
3. **Execution Graph** — how a database actually plans/executes the query; requires real `EXPLAIN`-style evidence and is a later slice.

Table remains canonical evidence. Query Graph must not be presented as a physical execution plan.

Reference:

- `docs/coquery-bi-result-intelligence-2026-08-30.md`

## Current Verified Position

### Product UX

Verified and merged:

- learning-first Home
- focused SQL practice workspace
- learning path/progress
- 24-problem curriculum
- next-incomplete-problem navigation
- user-flow regression smoke

Active PR #18 result-view baseline now includes:

- deterministic ResultShape classification
- additive hosted `practice_query` result-intelligence metadata
- a real column/row Table in focused practice instead of the visible JSON-string row preview
- visible recommendation metadata while Table remains the evidence baseline
- truthful `NULL` and numeric-zero rendering
- mobile horizontal overflow handling without a React migration

This branch work is not yet merged or deployed to the durable production Worker.

### SQL / data engine

- SQLite remains the working baseline
- built-in practice sandbox is working
- natural-language SQL remains assistive and local/rule-first where covered
- optional provider infrastructure remains available
- PostgreSQL remains a narrow experimental track with smoke proof
- MySQL is not part of the working baseline
- `sql_cli/result_intelligence.py` provides the deterministic classifier and conservative Query Graph `flow_steps`
- `sql_cli/result_integration.py` attaches derived metadata without mutating canonical result fields

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

Approved surface:

`Table | Visual | Flow | Explain`

Product model:

`SQL text -> Query Graph -> returned rows -> Result Visual -> Explain`

Later, separately:

`database plan evidence -> Execution Graph`

Core rules:

- deterministic first; no LLM required
- Table is always available and remains the evidence baseline
- Query Graph/Flow is a first-class learning view
- high-confidence result shapes may recommend a chart
- ambiguous shapes fall back to Table
- Query Graph contains only recognized SQL structure
- Query Graph is not an execution-plan claim
- Execution Graph requires real database plan evidence
- visualization recommendation explains why it was selected
- no React migration in the first slice

Bklit UI remains a design/component reference for chart patterns such as Bar, Line, Funnel, Sankey, Gauge, and Choropleth. Current CoQuery is plain HTML/CSS/JS, so direct React registry adoption is deferred until a deliberate frontend architecture decision.

Proven on active PR #18:

- deterministic `ResultShape` module: `sql_cli/result_intelligence.py`
- executable contract coverage: `sql_cli/tests/test_result_intelligence.py`
- conservative recognized SQL `flow_steps`
- additive integration helper: `sql_cli/result_integration.py`
- hosted Worker wiring for successful `practice_query` responses
- real Table renderer in `practice-focus.js`/`practice-focus.css`
- practice-query regression gate protecting catalog/query/grading/error contracts
- practice-focus and PWA/serverless smoke coverage protecting the visible Table and hosted wiring
- baseline CI and separate PostgreSQL smoke green on the implementation head

Implementation order:

1. [done] ResultShape classifier + contract tests
2. [done] hosted `practice_query` metadata integration
3. [done] real Table renderer in focused practice
4. lightweight Bar Result Visual for proven category + measure
5. **Query Graph/Flow renderer as a core learning view**
6. deterministic Explain copy
7. Line/time-series Result Visual
8. nested Query Graph support only after explicit parser contracts
9. Execution Graph only with real `EXPLAIN`-style evidence
10. additional BI visuals only when ResultShape rules justify them

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

- nested Query Graph support for subqueries/CTEs/window constructs after parser contracts exist
- Execution Graph research and provider-specific `EXPLAIN` contracts
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
- deterministic BI ResultShape contract tests
- practice-query regression gate
- practice focus smoke including canonical Table markers
- learning path smoke
- curriculum smoke
- user-flow QA smoke
- PWA/serverless smoke including hosted result-intelligence wiring
- separate PostgreSQL smoke

Deployment verification:

- temporary Cloudflare remote proof workflow
- durable production workflow
- post-deploy health/PWA/practice API checks

The active BI integration is currently verified by branch CI, not yet by a new durable production deployment.

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
- invent chart dimensions, targets, flow edges, geographic meaning, stage order, or execution nodes
- replace or mutate canonical `columns`, `rows`, or `row_count` when adding derived BI metadata
- teach Query Graph as if it were the database's physical execution plan
- show Execution Graph without real planner/executor evidence

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

**add the first lightweight Bar Result Visual for proven `category_measure` results while keeping Table canonical; then implement the Query Graph/Flow renderer as the next core learning view.**

Execution direction:

`learning UX -> hosted PWA -> durable deploy -> BI result intelligence -> AI validation handoff -> iOS/Android wrappers`

Browser/device PWA QA remains an open release-evidence track in parallel.