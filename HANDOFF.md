# CoQuery Handoff

Date: 2026-09-02
Status: Durable Cloudflare production deployment proven; PR #18 now has ResultShape classification + hosted metadata integration + canonical practice Table; first Bar renderer is next

## Product Definition

CoQuery is a learning-first SQL product:

`Learn -> Practice -> Apply -> Assist`

Canonical product distribution:

- Web/PWA
- iPhone app wrapper
- Android app wrapper

The shared Web/PWA product logic remains canonical. Native wrappers must stay thin.

Approved result-understanding direction:

`Table -> Visual -> Flow -> Explain`

Table remains the canonical evidence view. Visual/Flow/Explain are derived, explainable views of the same query result and SQL structure.

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

## Verified Learner/Product Baseline

Verified learner-flow contract:

`Home -> choose/continue problem -> focused SQL editor -> execute/grade -> feedback -> next incomplete problem / learning path`

Baseline CI contains dedicated checks for:

- CLI/core
- deterministic BI ResultShape contracts
- practice-query regression gate
- practice focus including canonical Table markers
- learning path
- curriculum
- user-flow QA
- PWA/serverless contract including hosted BI wiring
- PostgreSQL smoke as a separate narrow experimental proof

## Durable Cloudflare Production — Completed Automated Proof

Durable Worker:

- `https://coquery-pwa.edu-public-app.workers.dev`

Successful workflow run:

- `33160202910`

Verified automatically on the durable Worker:

- Worker deployment/startup
- `/api/health`
- PWA HTML shell
- standalone manifest
- hosted practice listing
- hosted practice grading

The production workflow uses GitHub `production` environment-scoped Cloudflare credentials. Credential values are not in the repository and must never be committed.

PR #16 hardened the post-deploy API check so a short 404/5xx/transport propagation window can be retried while non-retryable responses still fail.

This automated HTTP proof is **not** browser/device/install QA.

The new PR #18 BI integration is branch-CI proven but has not yet been merged/redeployed to this durable Worker.

Reference:

- `.github/workflows/cloudflare-production-deploy.yml`
- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`

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

This remains a release-evidence track and must be completed before native wrapper release claims.

## BI Result Intelligence — Active PR #18

Approved result surface:

`Table | Visual | Flow | Explain`

First boundary:

`practice_query result -> classify -> Table | Visual recommendation | SQL Flow | Explain`

### ResultShape classifier — implemented and tested

Files:

- `sql_cli/result_intelligence.py`
- `sql_cli/tests/test_result_intelligence.py`

Proven deterministic behavior:

- category + numeric measure -> Bar recommendation when category labels are stable and bounded
- temporal + numeric measure -> Line only when the returned temporal sequence is safely ordered
- explicit share/percentage forming a complete total -> Ring recommendation
- two non-identifier numeric observation fields -> Scatter recommendation
- explicit stage + numeric value + SQL `ORDER BY` -> Funnel recommendation
- exact `source`, `target`, `value` contract -> Sankey/Flow recommendation
- one numeric metric does not infer Gauge without a target/range
- null/ambiguous/too-wide/too-many-category results fall back to Table
- zero remains a valid numeric value
- classifier output is deterministic and does not mutate returned rows
- SQL flow extraction includes only explicitly recognized FROM/JOIN/WHERE/GROUP BY/aggregate/HAVING/ORDER BY/LIMIT fragments

### Hosted `practice_query` integration — implemented and tested

Files:

- `sql_cli/result_integration.py`
- `cloudflare_worker.py`
- `sql_cli/tests/test_practice_query_regression.py`

Behavior:

- successful hosted `practice_query` responses receive additive `data.result_intelligence`
- `columns`, `rows`, `row_count`, actions, mode context, grading behavior, and structured non-SELECT errors remain protected
- the integration helper copies the result/data mapping before attaching metadata, so the raw result object is not mutated
- failed practice-query results are not rewritten

### Canonical focused-practice Table — implemented and tested

Files:

- `app_shell/terminal_shell_prototype/practice-focus.js`
- `app_shell/terminal_shell_prototype/practice-focus.css`
- `app_shell/terminal_shell_prototype/practice_focus_smoke.py`
- `app_shell/terminal_shell_prototype/pwa_serverless_smoke.py`

Behavior:

- the visible five-row JSON-string preview is hidden in focused practice
- a real HTML table renders the returned columns and all rows in the current response
- Table remains the canonical result evidence even when `result_intelligence` recommends Bar/Line/etc.
- recommendation name/reason is shown above the Table
- `NULL` is rendered as `NULL`; zero remains `0`
- numeric cells use tabular alignment and mobile widths use horizontal scrolling
- no React dependency or external AI/provider call is introduced

Latest implementation verification before document-only currentization:

- baseline: success
- PostgreSQL smoke: success

The documentation commits trigger CI again; merge remains blocked until the latest branch head is green.

First implementation sequence:

1. [done] deterministic `ResultShape` classifier + contract tests
2. [done] hosted `practice_query` metadata integration
3. [done] real focused-practice Table renderer
4. lightweight Bar renderer for clear category + measure results
5. SQL clause Flow renderer
6. deterministic Explain copy
7. Line/time-series support after the contract is stable

Truthfulness rules:

- Table is always available
- ambiguous results fall back to Table
- recommendation must state why it was selected
- no target/geography/stage order/flow edge may be inferred when not explicit
- zero is data, not missingness
- null remains null unless a transformation is explicit
- no external AI/provider is required for the first slice
- no undeclared React migration
- derived BI metadata must not mutate canonical query evidence

Reference:

- `docs/coquery-bi-result-intelligence-2026-08-30.md`

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

Architecture boundary:

- current CoQuery PWA is plain HTML/CSS/JavaScript
- Bklit components are React-based and depend on React/visx-style packages

Therefore the active BI slice uses Bklit as a product/design/component reference only. Direct component adoption or React migration requires a separate explicit architecture decision.

## AI Direction — Approved, Deferred Behind BI First Slice

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

The app builds a deterministic, reviewable prompt from current SQL/evidence/limitations. The user controls what is copied or later shared to an external AI.

Do not turn this into automatic external AI sending or automatic SQL execution.

Reference:

- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

## AI Safety / Data Boundary

Keep these rules:

- data visible in CoQuery is not automatically approved for external AI sharing
- allowlist/minimum extraction first
- API keys, secrets, tokens, passwords, credentials, DB URIs, personal information, and unknown-permission production data are excluded by default
- show the exact outgoing body before any clipboard/share/open side effect
- require explicit user action for every handoff side effect
- no automatic paste/send, login delegation, answer retrieval, or AI-generated SQL auto-execution
- Production Assist handoff remains OFF until ExportPolicy/external-sharing rights are separately proven

## Mobile Distribution Direction

After durable PWA/browser proof:

- validate a thin Capacitor-style wrapper against the current toolchain and store rules
- create iOS and Android wrappers without duplicating learning/business logic
- keep native-specific work limited to packaging, icons/splash, clipboard/share adapters, permissions, and store metadata

## Existing Engineering Baseline Retained

- SQLite-first working baseline
- shared DB URI contract
- write safety gates
- PostgreSQL narrow smoke proof
- provider registry
- DB/JPA local knowledge
- JPA source introspection
- schema-detail validation
- foreign-key join inference
- Production Assist read-only review/approval boundary

Do not broaden PostgreSQL/MySQL/JPA claims without new verification evidence.

## Active Priority Order

### P0-1

Browser/device PWA QA evidence remains open in parallel.

### P0-2

BI Result Intelligence:

`practice_query -> ResultShape -> Table | Visual | Flow | Explain`

Immediate implementation:

`proven category_measure -> lightweight Bar renderer`, while Table remains canonical evidence.

### P0-3

AI Context-to-Prompt Handoff:

`natural result -> validation prompt -> preview -> copy`

### P0-4

Shared-code mobile wrappers:

- iOS
- Android

### P1

- additional BI visuals after shape rules prove the need
- Practice-result AI handoff
- system share / selectable AI destination
- My Data bridge
- learner-feedback-driven curriculum refinement

### P2

- constrained Production Assist AI handoff after export-rights proof
- optional cross-device progress sync

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

## Immediate Next Gate

**Add the first lightweight Bar renderer for high-confidence `category_measure` results, with Table retained as canonical evidence and all regression gates green.**

Execution direction:

`learning UX -> hosted PWA -> durable deploy -> BI result intelligence -> AI validation handoff -> iOS/Android wrappers`

## Key Documents

- `EASY_SQL_ROADMAP.md`
- `EASY_SQL_TODO.md`
- `HANDOFF.md`
- `docs/coquery-pwa-cloudflare-serverless-2026-08-28.md`
- `docs/coquery-cloudflare-temporary-deploy-proof-2026-08-28.md`
- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`
- `docs/coquery-bi-result-intelligence-2026-08-30.md`
- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`
