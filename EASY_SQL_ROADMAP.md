# CoQuery Roadmap

Version: product baseline 2026-09-03
Last Updated: 2026-09-03

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

The mathematical-formula analogy is useful as a learning metaphor, but SQL is not reduced to a simple numeric function.

Approved result-understanding surface:

`Table | Visual | Flow | Explain`

Three visual layers are explicitly separated:

1. **Query Graph** — what transformation the SQL describes; core learning experience.
2. **Result Visual** — what shape the exact returned data has; BI interpretation.
3. **Execution Graph** — how a database actually plans/executes the query; requires real `EXPLAIN`-style evidence and is never inferred from SQL text alone.

Table remains canonical evidence. Query Graph must not be presented as a physical execution plan.

References:

- `docs/coquery-bi-result-intelligence-2026-08-30.md`
- `docs/coquery-query-graph-implementation-2026-09-02.md`
- `docs/coquery-deterministic-explain-implementation-2026-09-02.md`
- `docs/coquery-line-result-visual-implementation-2026-09-02.md`
- `docs/coquery-recommendation-reason-localization-2026-09-02.md`

## Current Verified Position

### Current main

Current `main` baseline at branch synchronization:

- `1b329e23b167fe53a54c8afbec70e3f1ef604d0e`

Main now includes:

- PR #19 — SQL Dialect Learning Phase A merged (`6fe26c83cd97bf3498ca5be1ef986f07668ec19b`)
- Korean privacy-policy update (`1b329e23b167fe53a54c8afbec70e3f1ef604d0e`)

### Product UX already merged

- learning-first Home
- focused SQL practice workspace
- learning path/progress
- 24-problem curriculum
- next-incomplete-problem navigation
- user-flow regression smoke
- SQL Dialect Learning Phase A from PR #19

### BI Result Intelligence — active Draft PR #18

PR #18 remains Draft and unmerged. Its result-understanding baseline includes:

- deterministic ResultShape classification
- additive hosted `practice_query` result-intelligence metadata
- real column/row Table instead of visible JSON-string row preview
- truthful `NULL` and numeric-zero rendering
- Bar Result Visual for proven `category_measure`
- Line Result Visual only for safely ordered `time_series`
- Line preserves exact returned temporal order and never infers elapsed-time distance from horizontal spacing
- visible Query Graph from recognized `flow_steps`
- Query Graph labeled as logical SQL transformation, not database execution order
- deterministic Explain covering recognized SQL transformation, conservative row meaning, view recommendation, and its own evidence boundary
- deterministic KR/EN recommendation-reason localization without learner-facing reuse of backend-English `reason`
- no external AI/provider dependency for result interpretation
- no React migration

The PR #18 branch is synchronized with the current main before further BI work. The combined PWA shell cache is `coquery-pwa-v5`, carrying both the merged dialect-learning asset and the active BI result-understanding assets while `/api/*` remains uncached.

### SQL / data engine

- SQLite remains the working practice baseline
- built-in practice sandbox is working
- natural-language SQL remains assistive and local/rule-first where covered
- PostgreSQL remains a narrow experimental/runtime-smoke track
- MySQL does not yet have a working runtime baseline
- `sql_cli/result_intelligence.py` provides deterministic ResultShape classification and conservative Query Graph `flow_steps`
- `sql_cli/result_integration.py` attaches derived metadata without mutating canonical result fields

### Product distribution

Merged distribution work:

- PR #13 — installable PWA + Cloudflare Python Worker scaffold
- PR #14 — isolated Worker bundle + real temporary Cloudflare deployment proof
- PR #15 — durable Cloudflare production deployment workflow + PWA QA contract
- PR #16 — hardened post-deploy practice API verification

Durable production Worker:

- `https://coquery-pwa.edu-public-app.workers.dev`

Successful durable production workflow proof remains:

- run `33160202910`
- deployment: success
- `/api/health`: success
- PWA shell/manifest: success
- hosted practice API: success

The active PR #18 changes have not yet been merged or redeployed to the durable production Worker.

## Active Priority Stack

### P0-A. Browser/device PWA QA — release evidence

Remaining release-quality evidence:

- Home -> problem -> execute/grade -> next problem
- progress persistence across reload/relaunch
- explicit offline-shell/network-required behavior
- `/api/*` not served from stale service-worker cache
- desktop PWA install where supported
- iOS Safari Add to Home Screen
- Android Chrome install/add-to-home-screen

Reference:

- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`

### P0-B. BI Result Intelligence — active product slice

Product model:

`SQL text -> Query Graph -> returned rows -> Result Visual -> Explain`

Later, separately:

`database plan evidence -> Execution Graph`

Core rules:

- deterministic first; no LLM required
- Table is always available and remains evidence baseline
- Query Graph/Flow is a first-class learning view
- high-confidence result shapes may recommend a chart
- ambiguous shapes fall back to Table
- Bar is limited to proven category + numeric measure results
- Line is limited to safely ordered temporal + numeric measure results
- Line never sorts rows or invents elapsed-time spacing semantics
- Query Graph contains only recognized SQL structure
- Query Graph is not an execution-plan claim
- Explain/localization describes only supported SQL/result metadata and never invents business causality
- Execution Graph requires real database plan evidence
- no React migration in the first slice

Proven on active PR #18:

1. [done] ResultShape classifier + contract tests
2. [done] hosted `practice_query` metadata integration
3. [done] real Table renderer in focused practice
4. [done] lightweight Bar Result Visual
5. [done] Query Graph/Flow renderer
6. [done] deterministic Explain
7. [done] Line/time-series Result Visual
8. [done] deterministic KR/EN recommendation-reason localization
9. **next: keyboard/accessibility baseline for future view switching**
10. nested Query Graph only after explicit parser contracts
11. Execution Graph only with real `EXPLAIN`-style evidence
12. additional BI visuals only when ResultShape rules justify them

### P0-C. AI Context-to-Prompt Handoff — first slice

Starts after the BI first slice unless an explicit priority decision changes the gate.

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

- validate minimal wrapper choice
- keep shared Web/PWA source canonical
- create thin iOS and Android wrappers
- prove simulator/emulator flows
- map clipboard/share through platform adapters where necessary
- prepare store assets and metadata separately

Preferred direction remains a thin Capacitor-style wrapper, subject to implementation-time toolchain/store validation.

## P1 — Learning Quality Expansion

### P1-A. SQL Dialect Learning — Phase A merged

PR #19 is merged into main.

Purpose:

**teach common SQL first, then reveal PostgreSQL/MySQL/SQLite differences only when useful.**

Learner surface:

`Problem -> Run/Grade -> DB별 차이 보기 -> PostgreSQL | MySQL | SQLite`

Merged Phase A includes:

- deterministic `DialectLesson` / `DialectCatalog`
- string concatenation, current date/time, date arithmetic, and `LIMIT` commonality lessons
- PostgreSQL/MySQL/SQLite variants with `common` / `reference` / `verified` badges
- KR/EN content
- optional default-closed comparison card only for mapped problems
- deterministic catalog/problem-mapping regression coverage
- SQLite execution proof for examples labeled `verified`
- MySQL remains reference-only; no MySQL runtime-support claim

Reference:

- `docs/coquery-sql-dialect-learning-plan-2026-09-02.md`

Future dialect work:

- expand comparison coverage only from demonstrated learner gaps
- expand PostgreSQL `verified` coverage only where the smoke environment executes the behavior
- establish a MySQL runtime/test baseline before any MySQL `verified` badge
- do not build a general SQL transpiler without a separate product decision

### P1-B. BI expansion after first slice

Only when ResultShape rules justify them:

- Ring/Pie for explicit part-to-whole results
- Scatter for true numeric observation pairs
- Funnel for explicit ordered stages
- Sankey for explicit source/target/value results
- Gauge only with explicit target/range
- Choropleth only with a supported geography contract

### Other P1

- Practice-result AI handoff
- system share / selectable external AI destination
- My Data bridge
- learner-feedback-driven curriculum refinement

## P2

- constrained Production Assist external handoff only after export-rights policy proof
- optional cross-device progress sync
- broader engine-backed dialect verification only when runtime environments justify it

## Completed Product History

- PR #8 — first-run learning Home
- PR #9 — focused practice workspace
- PR #10 — learning path/progress
- PR #11 — curriculum expansion to 24 problems
- PR #12 — learner-flow QA and next-problem navigation
- PR #13 — PWA + Cloudflare serverless scaffold
- PR #14 — real temporary Cloudflare deployment proof and isolated deployment harness
- PR #15 — durable production deployment workflow and PWA QA gate
- PR #16 — production API verification hardening
- PR #19 — SQL Dialect Learning Phase A

## Verification Baseline

Core CI after synchronizing PR #18 with main must include both tracks:

- CLI/core verification
- deterministic BI ResultShape contract tests
- practice-query regression gate
- executable Bar + Line Result Visual smoke
- executable Query Graph model smoke
- executable deterministic Explain/localization smoke
- practice-focus smoke including Table/Bar/Line/Query Graph/Explain wiring
- learning path smoke
- curriculum smoke
- SQL dialect learning smoke
- user-flow QA smoke
- PWA/serverless smoke including combined `coquery-pwa-v5` assets
- separate PostgreSQL smoke

Deployment verification remains separate:

- temporary Cloudflare remote proof workflow
- durable production workflow
- post-deploy health/PWA/practice API checks

## Scope Locks

Do not silently:

- split canonical PWA into separate native product implementations
- make external AI mandatory for SQL generation or result interpretation
- automatically send data to an AI
- expose Production Assist data through AI handoff before ExportPolicy proof
- describe automated HTTP proof as completed browser/device/install QA
- broaden PostgreSQL/MySQL support claims without new proof
- present reference dialect examples as engine-verified
- make DB-specific syntax mandatory in beginner lessons
- turn BI result work into an undeclared React migration
- reuse or redistribute Bklit Studio; only the upstream MIT chart-component boundary is eligible for later technical evaluation
- invent chart dimensions, targets, flow edges, geographic meaning, stage order, elapsed-time spacing, or execution nodes
- replace or mutate canonical `columns`, `rows`, or `row_count` when adding derived BI metadata
- teach Query Graph as if it were a database physical execution plan
- use Explain/localization to invent causality, intent, or hidden business meaning
- show Execution Graph without real planner/executor evidence

## Official Execution Loop

For each slice:

1. confirm current `main`
2. create or synchronize the working branch
3. document scope and proof boundary
4. add regression/contract tests where practical
5. implement the smallest valid change
6. keep baseline CI green
7. keep PostgreSQL smoke truthful when relevant
8. record exactly what was verified and skipped
9. merge only after explicit approval
10. currentize `EASY_SQL_ROADMAP.md`, `EASY_SQL_TODO.md`, and `HANDOFF.md`
11. prefer one cohesive implementation commit per logical slice; documentation-only currentization may follow after verified CI

## Next Decision Gate

Immediate BI gate after branch synchronization:

**define and implement the keyboard/accessibility baseline for future `Table | Visual | Flow | Explain` view switching before adding more chart types.**

Browser/device PWA QA remains an open release-evidence track in parallel.
