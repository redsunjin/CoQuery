# CoQuery Handoff

Date: 2026-09-02
Status: Durable Cloudflare production deployment proven; PR #18 now has ResultShape classification + canonical Table + Bar + Line Result Visuals + Query Graph + deterministic Explain; recommendation-reason localization is next

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

Approved result-understanding direction:

`Table -> Visual -> Flow -> Explain`

Three visual layers are separate:

1. **Query Graph** — logical transformation explicitly described by recognized SQL structure.
2. **Result Visual** — BI interpretation derived only from exact returned rows.
3. **Execution Graph** — actual database planner/executor evidence; requires real `EXPLAIN`-style output and is never inferred from SQL text alone.

Table remains canonical evidence.

## Merged Product History

- PR #8 — first-run learning Home
- PR #9 — focused SQL practice
- PR #10 — learning path/progress
- PR #11 — 24-problem curriculum
- PR #12 — learner-flow QA and next-problem navigation
- PR #13 — installable PWA + Cloudflare Python Worker scaffold
- PR #14 — isolated deployment bundle + real temporary Cloudflare hosted proof
- PR #15 — durable production deployment workflow + PWA QA contract
- PR #16 — post-deploy practice API verification hardening

Latest verified merge after PR #16:

- `5752cd24142da60496e42b66e35d1a546e4a0c06`

PR #18 remains Draft and unmerged.

## Durable Cloudflare Production — Completed Automated Proof

Durable Worker:

- `https://coquery-pwa.edu-public-app.workers.dev`

Successful workflow run:

- `33160202910`

Verified automatically on durable Worker:

- Worker deployment/startup
- `/api/health`
- PWA HTML shell
- standalone manifest
- hosted practice listing
- hosted practice grading

The production workflow uses GitHub `production` environment-scoped Cloudflare credentials. Credential values are not in the repository and must never be committed.

The PR #18 BI/Query Graph/Explain/Line integration is branch-CI proven but has not yet been merged/redeployed to the durable Worker.

## Browser/PWA QA — Still Required

Required interactive evidence:

1. open public URL without login
2. Home -> first problem -> SQL -> grade -> next problem
3. complete a problem and refresh
4. verify progress persists
5. close/reopen browser/PWA and verify progress remains
6. test offline cached-shell reopening
7. verify SQL execution clearly requires network while offline
8. verify `/api/*` does not use stale service-worker cache
9. verify install/add-to-home-screen behavior where supported

Target evidence:

- desktop PWA-capable browser
- iOS Safari/Add to Home Screen
- Android Chrome/install flow

## BI Result Intelligence — Active PR #18

### ResultShape classifier — implemented and tested

Files:

- `sql_cli/result_intelligence.py`
- `sql_cli/tests/test_result_intelligence.py`

Proven deterministic behavior:

- category + numeric measure -> Bar recommendation when category labels are stable and bounded
- temporal + numeric measure -> Line only when returned temporal sequence is safely ordered
- explicit share/percentage forming complete total -> Ring recommendation
- two non-identifier numeric observation fields -> Scatter recommendation
- explicit stage + numeric value + SQL `ORDER BY` -> Funnel recommendation
- exact `source`, `target`, `value` contract -> Sankey/Flow recommendation
- one numeric metric does not infer Gauge without target/range
- null/ambiguous/too-wide/too-many-category results fall back to Table
- zero remains valid numeric value
- SQL flow extraction includes only explicitly recognized FROM/JOIN/WHERE/GROUP BY/aggregate/HAVING/ORDER BY/LIMIT fragments

### Hosted `practice_query` integration — implemented and tested

Files:

- `sql_cli/result_integration.py`
- `cloudflare_worker.py`
- `sql_cli/tests/test_practice_query_regression.py`

Behavior:

- successful hosted `practice_query` responses receive additive `data.result_intelligence`
- `columns`, `rows`, `row_count`, actions, mode context, grading behavior, and structured non-SELECT errors remain protected
- failed practice-query results are not rewritten

### Canonical focused-practice Table — implemented and tested

Files:

- `app_shell/terminal_shell_prototype/practice-focus.js`
- `app_shell/terminal_shell_prototype/practice-focus.css`

Behavior:

- visible JSON-string preview is hidden in focused practice
- real HTML table renders returned columns and all rows in current response
- Table remains canonical result evidence
- `NULL` stays `NULL`; zero stays `0`
- mobile widths use horizontal scrolling

### Bar Result Visual — implemented and tested

Files:

- `app_shell/terminal_shell_prototype/practice-result-visual.js`
- `app_shell/terminal_shell_prototype/practice-result-visual.css`
- `app_shell/terminal_shell_prototype/practice_result_visual_smoke.js`

Behavior:

- only proven `category_measure + recommended_visual=bar` renders
- exact returned row order is preserved
- negative and positive values use truthful zero baseline
- zero remains zero-width rather than missing
- null/non-numeric/ambiguous results refuse chart rendering
- returned rows are not mutated

### Line Result Visual — implemented and tested

Files:

- `app_shell/terminal_shell_prototype/practice-result-visual.js`
- `app_shell/terminal_shell_prototype/practice-result-visual.css`
- `app_shell/terminal_shell_prototype/practice_result_visual_smoke.js`
- `docs/coquery-line-result-visual-implementation-2026-09-02.md`

Behavior:

- only proven `time_series + recommended_visual=line` is eligible
- frontend repeats the safe temporal-key/order check instead of trusting stale metadata blindly
- exact returned row order is preserved; no sorting or sampling
- ascending and descending safe temporal order are both accepted and preserved
- null/non-numeric/unparseable/unordered temporal results refuse Line rendering
- vertical geometry uses exact returned min/max
- horizontal geometry represents returned temporal sequence only; elapsed-time distance is not inferred
- first/last temporal labels and min/max measure labels are visible
- exact values remain in canonical Table
- returned rows are not mutated

Implementation commit:

- `6e0802ef35d7e376d7e2f7580cad1af5a4d3b9fa`
- baseline: success
- PostgreSQL smoke: success

### Query Graph — implemented and tested

Files:

- `app_shell/terminal_shell_prototype/practice-query-flow.js`
- `app_shell/terminal_shell_prototype/practice-query-flow.css`
- `app_shell/terminal_shell_prototype/practice_query_flow_smoke.js`
- `docs/coquery-query-graph-implementation-2026-09-02.md`

Behavior:

- renders only recognized `flow_steps`: `from`, `join`, `where`, `group_by`, `aggregate`, `having`, `order_by`, `limit`
- preserves recognized SQL fragment text and order
- ignores unsupported step kinds rather than interpreting them
- final Result node uses actual returned row count
- explicitly labeled as logical SQL transformation, not physical database execution order
- semantic ordered-list markup + textual description
- mobile uses horizontal scrolling rather than dropping steps
- no mutation of canonical query result

### Deterministic Explain — implemented and tested

Files:

- `app_shell/terminal_shell_prototype/practice-result-explain.js`
- `app_shell/terminal_shell_prototype/practice-result-explain.css`
- `app_shell/terminal_shell_prototype/practice_result_explain_smoke.js`
- `docs/coquery-deterministic-explain-implementation-2026-09-02.md`

Behavior:

- no LLM/provider call is required
- uses only recognized `flow_steps`, ResultShape, dimensions/measures, visual recommendation, and row count
- answers: what the SQL did / what each row represents / why this view / explanation boundary
- conservative row-semantics templates cover the currently proven result shapes
- unsupported flow kinds are filtered instead of interpreted
- business causality, hidden meaning, and physical execution-plan meaning are explicitly not inferred
- Korean and English copy follows the existing language selector
- no mutation of canonical query evidence

### PWA shell cache — updated

`service-worker.js` now uses `coquery-pwa-v4` and caches the current result-understanding assets:

- `practice-result-visual.js/css` — Bar + Line
- `practice-query-flow.js/css`
- `practice-result-explain.js/css`

`/api/*` remains uncached.

## Regression proof

Line implementation commit `6e0802ef35d7e376d7e2f7580cad1af5a4d3b9fa` passed:

- baseline: success
- PostgreSQL smoke: success

Baseline includes:

- core CLI tests
- deterministic ResultShape contracts
- practice-query regression gate
- Bar + Line Result Visual executable smoke
- Query Graph executable smoke
- deterministic Explain executable smoke
- focused-practice asset checks
- learning path/curriculum/user-flow/PWA smoke

Documentation currentization commits must also remain green before merge.

## Bklit UI Reference Boundary

Reference repository:

- `bklit/bklit-ui`

Useful patterns:

- Bar
- Line/Area
- Ring/Pie
- Scatter
- Funnel
- Gauge
- Sankey
- Choropleth

Upstream boundary:

- chart components are MIT-licensed
- Bklit Studio is proprietary and must not be reused or redistributed

Current CoQuery remains plain HTML/CSS/JavaScript. No React migration is introduced in PR #18.

## AI Direction — Approved, Deferred Behind BI First Slice

Approved pattern:

**Context-to-Prompt Handoff**

First slice:

`natural result -> Build AI validation prompt -> Preview -> Copy`

Production Assist external handoff remains OFF until ExportPolicy/external-sharing rights are separately proven.

## Mobile Distribution Direction

After durable PWA/browser proof:

- validate thin Capacitor-style wrapper against current toolchain/store rules
- create iOS and Android wrappers without duplicating learning/business logic
- keep native-specific work limited to packaging, icons/splash, clipboard/share adapters, permissions, and store metadata

## Active Priority Order

### P0-1

Browser/device PWA QA evidence remains open in parallel.

### P0-2

BI Result Intelligence:

`practice_query -> ResultShape -> Table | Result Visual | Query Graph | Explain`

Immediate implementation:

**localize the remaining backend-English result-intelligence recommendation reason into deterministic Korean/English UI copy without changing classifier decisions.**

### P0-3

AI Context-to-Prompt Handoff:

`natural result -> validation prompt -> preview -> copy`

### P0-4

Shared-code mobile wrappers:

- iOS
- Android

### P1

- additional BI visuals only after the first BI result-understanding slice is closed
- nested Query Graph only with explicit parser contracts
- Execution Graph only with real provider-specific `EXPLAIN` evidence
- Practice-result AI handoff
- system share / selectable AI destination
- My Data bridge
- learner-feedback-driven curriculum refinement

## Official Harness Rules

1. branch + Draft PR
2. no direct implementation commits to `main`
3. preserve command/data contracts unless the slice explicitly changes them
4. RED -> minimum implementation -> GREEN where practical
5. keep baseline CI green
6. keep PostgreSQL smoke truthful when it is part of the gate
7. record verified and skipped evidence separately
8. merge only after explicit approval
9. currentize roadmap/TODO/HANDOFF after material baseline changes
10. prefer one cohesive implementation commit per logical slice; documentation-only currentization may be separate after verified CI

## Immediate Next Gate

**Localize deterministic result-intelligence recommendation reasons without changing ResultShape decisions.**

## Key Documents

- `EASY_SQL_ROADMAP.md`
- `EASY_SQL_TODO.md`
- `HANDOFF.md`
- `docs/coquery-bi-result-intelligence-2026-08-30.md`
- `docs/coquery-query-graph-implementation-2026-09-02.md`
- `docs/coquery-deterministic-explain-implementation-2026-09-02.md`
- `docs/coquery-line-result-visual-implementation-2026-09-02.md`
- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`
- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`
