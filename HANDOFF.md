# CoQuery Handoff

Date: 2026-08-30
Status: Durable Cloudflare production deployment proven; BI Result Intelligence is the active product slice

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

## Verified Learner/Product Baseline

Verified learner-flow contract:

`Home -> choose/continue problem -> focused SQL editor -> execute/grade -> feedback -> next incomplete problem / learning path`

Baseline CI contains dedicated checks for:

- practice focus
- learning path
- curriculum
- user-flow QA
- PWA/serverless contract
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

## BI Result Intelligence — Active

The immediate product direction was reprioritized after durable deployment.

Problem:

- current `practice_query` output still renders a limited JSON-string row preview
- this proves SQL execution but teaches little about the returned data shape

Approved result surface:

`Table | Visual | Flow | Explain`

First boundary:

`practice_query result -> classify -> Table | Visual recommendation | SQL Flow | Explain`

First implementation sequence:

1. deterministic `ResultShape` classifier + contract tests
2. real Table renderer
3. lightweight Bar renderer for clear category + measure results
4. SQL clause Flow renderer
5. deterministic Explain copy
6. Line/time-series support after the contract is stable

Truthfulness rules:

- Table is always available
- ambiguous results fall back to Table
- recommendation must state why it was selected
- no target/geography/stage order/flow edge may be inferred when not explicit
- zero is data, not missingness
- null remains null unless a transformation is explicit
- no external AI/provider is required for the first slice
- no undeclared React migration

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

**Implement and test the deterministic `ResultShape` classifier before chart rendering.**

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
