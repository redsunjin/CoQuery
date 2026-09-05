# CoQuery Handoff

Date: 2026-09-05
Status: Production PWA beta redeployed with the merged BI result-understanding slice; iOS shell is synchronized to the same deterministic result contract. Interactive PWA/device and Apple-signing gates remain.

## Product Definition

CoQuery is a learning-first SQL product:

`Learn -> Practice -> Apply -> Assist`

Canonical product distribution:

- Web/PWA
- iPhone app wrapper
- Android app wrapper

The shared Web/PWA product logic remains canonical. Native wrappers must stay thin.

Product principle:

**SQL as Visual Data Transformation**

Approved result-understanding surface:

`Table | Visual | Flow | Explain`

Three visual layers remain separate:

1. **Query Graph** — logical transformation explicitly described by recognized SQL structure.
2. **Result Visual** — BI interpretation derived only from exact returned rows.
3. **Execution Graph** — actual database planner/executor evidence; requires real `EXPLAIN`-style output and is never inferred from SQL text alone.

Table remains canonical evidence.

## Current Main / Branch State

Current `main` at deployment:

- `efd351e8b82c4352cdac8eae7a7773b088160a3e`

Important main changes since the original PR #18 base:

- PR #19 merged SQL Dialect Learning Phase A (`6fe26c83cd97bf3498ca5be1ef986f07668ec19b`)
- Korean privacy-policy update (`1b329e23b167fe53a54c8afbec70e3f1ef604d0e`)
- PR #18 — BI Result Intelligence (`efd351e8b82c4352cdac8eae7a7773b088160a3e`)

## Merged Product History

- PR #8 — first-run learning Home
- PR #9 — focused SQL practice
- PR #10 — learning path/progress
- PR #11 — 24-problem curriculum
- PR #12 — learner-flow QA and next-problem navigation
- PR #13 — installable PWA + Cloudflare Python Worker scaffold
- PR #14 — isolated deployment bundle + real temporary Cloudflare hosted proof
- PR #15 — durable production deployment workflow + PWA QA harness
- PR #16 — hardened production hosted-API verification
- PR #18 — BI Result Intelligence
- PR #19 — SQL Dialect Learning Phase A

## Durable Cloudflare Production Baseline

Durable Worker:

- `https://coquery-pwa.edu-public-app.workers.dev`

Successful production workflow:

- [run 33948547355](https://github.com/redsunjin/CoQuery/actions/runs/33948547355) on `efd351e8b82c4352cdac8eae7a7773b088160a3e`

Verified automatically on the durable Worker:

- Worker deployment/startup
- `/api/health`
- PWA HTML shell
- standalone manifest
- hosted practice listing
- SQL execution
- grading

PR #18 BI changes are merged and included in this durable Worker deployment.

Interactive browser/device evidence remains a separate QA gate.

## SQL Dialect Learning — Merged Phase A

Reference:

- `docs/coquery-sql-dialect-learning-plan-2026-09-02.md`

Approved principle:

**Teach common SQL first, then reveal database-specific differences only when they help the learner.**

Learner flow:

`Problem -> Write SQL -> Run/Grade -> DB별 차이 보기 -> PostgreSQL | MySQL | SQLite`

Merged PR #19 provides:

- deterministic `DialectLesson` / versioned `DialectCatalog`
- string concatenation, current date/time, date arithmetic, and `LIMIT` commonality comparisons
- PostgreSQL/MySQL/SQLite variants with KR/EN explanations
- optional `DB별 차이 보기` surface only for mapped problems; closed by default
- visible `common` / `reference` / `verified` badges
- deterministic problem mapping and regression coverage
- SQLite execution for examples marked `verified`

Truthfulness boundary:

- SQLite — working practice baseline
- PostgreSQL — narrow experimental/runtime-smoke path; comparison content does not imply broad parity
- MySQL — reference-only until a real runtime/test baseline exists
- no general SQL transpiler
- no arbitrary automatic cross-engine conversion

## BI Result Intelligence — Merged PR #18

References:

- `docs/coquery-bi-result-intelligence-2026-08-30.md`
- `docs/coquery-query-graph-implementation-2026-09-02.md`
- `docs/coquery-deterministic-explain-implementation-2026-09-02.md`
- `docs/coquery-line-result-visual-implementation-2026-09-02.md`
- `docs/coquery-recommendation-reason-localization-2026-09-02.md`

### ResultShape classifier

Files:

- `sql_cli/result_intelligence.py`
- `sql_cli/tests/test_result_intelligence.py`

Deterministic behavior includes:

- category + numeric measure -> Bar when bounded/stable
- ordered temporal + numeric measure -> Line
- explicit complete share -> Ring recommendation
- two numeric observation fields -> Scatter recommendation
- explicit stage + numeric value + SQL ordering -> Funnel recommendation
- exact `source`, `target`, `value` -> Sankey/Flow recommendation
- one metric does not infer Gauge without target/range
- null/ambiguous/too-wide results fall back to Table
- zero remains a valid numeric value
- SQL flow extraction contains only recognized explicit clauses

### Hosted integration

Files:

- `sql_cli/result_integration.py`
- `cloudflare_worker.py`
- `sql_cli/tests/test_practice_query_regression.py`

Behavior:

- successful hosted `practice_query` responses receive additive `data.result_intelligence`
- canonical `columns`, `rows`, `row_count`, grading and structured-error behavior remain protected

### Canonical Table

Files:

- `app_shell/terminal_shell_prototype/practice-focus.js`
- `app_shell/terminal_shell_prototype/practice-focus.css`

Behavior:

- real HTML table renders returned columns/rows
- Table is canonical exact-value evidence
- `NULL` stays `NULL`; zero stays `0`
- mobile widths use horizontal scrolling

### Bar + Line Result Visuals

Files:

- `app_shell/terminal_shell_prototype/practice-result-visual.js`
- `app_shell/terminal_shell_prototype/practice-result-visual.css`
- `app_shell/terminal_shell_prototype/practice_result_visual_smoke.js`

Bar:

- only proven `category_measure + recommended_visual=bar`
- exact returned order preserved
- signed zero baseline remains truthful
- null/non-numeric/ambiguous inputs refuse chart rendering

Line:

- only proven `time_series + recommended_visual=line`
- frontend repeats safe temporal-order validation
- exact returned row order preserved; no sorting or sampling
- null/non-numeric/unparseable/unordered inputs refuse Line rendering
- horizontal geometry means returned sequence only; no elapsed-time distance is inferred
- exact values remain in Table

### Query Graph

Files:

- `app_shell/terminal_shell_prototype/practice-query-flow.js`
- `app_shell/terminal_shell_prototype/practice-query-flow.css`
- `app_shell/terminal_shell_prototype/practice_query_flow_smoke.js`

Behavior:

- recognized steps only: `from`, `join`, `where`, `group_by`, `aggregate`, `having`, `order_by`, `limit`
- preserves recognized SQL fragment text/order
- unsupported step kinds are ignored rather than interpreted
- explicitly labeled as logical SQL transformation, not physical database execution order

### Deterministic Explain + recommendation localization

Files:

- `app_shell/terminal_shell_prototype/practice-result-explain.js`
- `app_shell/terminal_shell_prototype/practice-result-explain.css`
- `app_shell/terminal_shell_prototype/practice_result_explain_smoke.js`

Behavior:

- no LLM/provider call
- uses only recognized SQL/result metadata
- explains: SQL transformation / row meaning / why this view / explanation boundary
- does not infer business causality, hidden meaning, or physical execution-plan semantics
- Korean/English recommendation explanations are deterministic from ResultShape metadata
- Korean learner UI no longer exposes backend-English `reason` as fallback copy

## Combined PWA Shell After Synchronization

The branch synchronization combines the main SQL Dialect Learning asset and the PR #18 BI assets.

`service-worker.js` now uses:

- `coquery-pwa-v5`

App-shell coverage includes:

- `practice-result-visual.js/css`
- `practice-query-flow.js/css`
- `practice-result-explain.js/css`
- `dialect-learning.js`

`/api/*` remains outside service-worker caching.

The combined baseline workflow runs both the BI regression suite and `dialect_learning_smoke.py`.

## Verification Required After Synchronization

The synchronization gate is complete only when the new combined head passes:

- baseline CI
- separate PostgreSQL smoke
- PR mergeability check against current main

The combined baseline includes:

- core CLI tests
- deterministic ResultShape contracts
- practice-query regression gate
- Bar + Line executable smoke
- Query Graph executable smoke
- deterministic Explain/localization smoke
- practice-focus wiring checks
- learning path/curriculum checks
- SQL dialect learning smoke
- user-flow QA
- PWA/serverless smoke for the combined cache/assets

## Browser/PWA QA — Still Required

1. open public URL without login
2. Home -> first problem -> SQL -> grade -> next problem
3. complete a problem and refresh
4. verify progress persists
5. close/reopen browser/PWA and verify progress remains
6. test offline cached-shell reopening
7. verify SQL execution clearly requires network while offline
8. verify `/api/*` does not use stale service-worker cache
9. verify install/add-to-home-screen behavior where supported

Target PWA evidence:

- desktop PWA-capable browser
- iOS Safari/Add to Home Screen
- Android Chrome/install flow

## AI Direction — Approved, Not Yet Implemented

Approved pattern:

**Context-to-Prompt Handoff**

First slice:

`natural result -> Build AI validation prompt -> Preview -> Copy`

Responsibilities:

- ContextAdapter
- ExportPolicy
- QuestionPolicy
- PromptComposer
- PromptPreview
- HandoffAdapter

Do not turn this into automatic external AI sending or automatic SQL execution.

Reference:

- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

## AI Safety / Data Boundary

- data visible in CoQuery is not automatically approved for external AI sharing
- allowlist/minimum extraction first
- API keys, secrets, tokens, passwords, credentials, DB URIs, personal information, and unknown-permission production data are excluded by default
- show the exact outgoing body before clipboard/share/open side effects
- require explicit user action for every handoff side effect
- Production Assist handoff remains OFF until ExportPolicy/external-sharing rights are separately proven

## Mobile Distribution Direction

After durable PWA/browser proof:

- validate a thin Capacitor-style wrapper against current toolchain/store rules
- create iOS and Android wrappers without duplicating learning/business logic
- keep native-specific work limited to packaging, icons/splash, clipboard/share adapters, permissions, and store metadata

## Active Priority Order

### P0-1

Interactive browser/device PWA QA remains open in parallel.

### P0-2

BI Result Intelligence:

`practice_query -> ResultShape -> Table | Result Visual | Query Graph | Explain`

Next implementation after synchronization:

**keyboard/accessibility baseline for future `Table | Visual | Flow | Explain` switching.**

### P0-3

AI Context-to-Prompt Handoff:

`natural result -> validation prompt -> preview -> copy`

### P0-4

Shared-code mobile wrappers:

- iOS
- Android

### P1

- dialect comparison expansion only from demonstrated learner gaps
- additional BI visuals only after the first result-understanding slice is closed
- nested Query Graph only with explicit parser contracts
- Execution Graph only with real provider-specific `EXPLAIN` evidence
- Practice-result AI handoff
- My Data bridge
- learner-feedback-driven curriculum refinement

## Official Harness Rules

1. branch + Draft PR
2. synchronize with current main when the base moves materially
3. no direct implementation commits to `main` from the active slice
4. preserve command/data contracts unless the slice explicitly changes them
5. RED -> minimum implementation -> GREEN where practical
6. keep baseline CI green
7. keep PostgreSQL smoke truthful when it is part of the gate
8. record verified and skipped evidence separately
9. merge PRs to main only after explicit approval
10. currentize roadmap/TODO/HANDOFF after material baseline changes
11. prefer one cohesive implementation commit per logical slice; documentation-only currentization may follow after verified CI

## Immediate Next Gate

**After the synchronization head is green and conflict-free, implement the keyboard/accessibility baseline for future `Table | Visual | Flow | Explain` view switching.**

## Key Documents

- `EASY_SQL_ROADMAP.md`
- `EASY_SQL_TODO.md`
- `HANDOFF.md`
- `docs/coquery-sql-dialect-learning-plan-2026-09-02.md`
- `docs/coquery-bi-result-intelligence-2026-08-30.md`
- `docs/coquery-query-graph-implementation-2026-09-02.md`
- `docs/coquery-deterministic-explain-implementation-2026-09-02.md`
- `docs/coquery-line-result-visual-implementation-2026-09-02.md`
- `docs/coquery-recommendation-reason-localization-2026-09-02.md`
- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`
- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`
