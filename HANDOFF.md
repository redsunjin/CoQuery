# CoQuery Handoff

Date: 2026-09-02
Status: Production PWA deployed; SQL Dialect Learning planning/implementation slice active on `feat/sql-dialect-learning`

## Product Definition

CoQuery is a learning-first SQL product:

`Learn -> Practice -> Apply -> Assist`

Canonical product distribution:

- Web/PWA
- iPhone app wrapper
- Android app wrapper

The shared Web/PWA product logic remains canonical. Native wrappers must stay thin.

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

Latest `main` before this branch:

- `5752cd24142da60496e42b66e35d1a546e4a0c06`

## Production PWA Baseline

Durable Worker:

- `https://coquery-pwa.edu-public-app.workers.dev`

Automated production workflow has verified:

- Worker deployment/startup
- `/api/health`
- PWA HTML shell
- standalone manifest
- 24-problem practice listing
- SQL execution
- grading

The production verification retry handles short deployment-propagation delay for the hosted practice API.

Interactive browser/device evidence remains a separate QA gate.

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

## SQL Dialect Learning — Active Slice

Branch:

- `feat/sql-dialect-learning`

Reference:

- `docs/coquery-sql-dialect-learning-plan-2026-09-02.md`

Approved product principle:

> Teach common SQL first, then reveal database-specific differences only when they help the learner.

Proposed learner flow:

`Problem -> Write SQL -> Run/Grade -> DB별 차이 보기 -> PostgreSQL | MySQL | SQLite`

The comparison layer is optional. It must not add database-specific complexity to the default beginner path.

### Truthfulness states

Each comparison must declare one of:

- `common` — no material dialect difference for the lesson
- `reference` — documented comparison, not executed by CoQuery against that engine
- `verified` — behavior proven by an actual CoQuery test/smoke environment

Current engine boundary:

- SQLite — working practice baseline
- PostgreSQL — narrow experimental/runtime smoke path
- MySQL — reference-only for this slice; no working runtime baseline

Do not mark MySQL examples as `verified` until a real MySQL environment exists.

### Phase A implementation target

- deterministic `DialectLesson` data model
- `DialectCatalog`
- first four comparison topics
  - string concatenation
  - current date/time
  - date arithmetic
  - row limiting/commonality
- PostgreSQL/MySQL/SQLite variants
- KR/EN copy
- optional `DB별 차이 보기` surface only when a relevant lesson exists
- explicit verification-state badge
- curriculum/problem mapping
- deterministic catalog/mapping tests

Not in Phase A:

- general SQL transpiler
- automatic conversion of arbitrary SQL between engines
- broad PostgreSQL/MySQL compatibility claims
- replacing SQLite as practice baseline

## Result Intelligence / BI Direction

Separate but complementary product direction:

`Table | Chart | Flow | Explain`

SQL Dialect Learning answers:

**"Would the SQL syntax/behavior differ in another database?"**

Result Intelligence answers:

**"What does this result mean and how should it be interpreted?"**

Keep these concerns separate in their first implementations.

## Browser/PWA QA Still Required

Required interactive checks:

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

The app builds a deterministic, reviewable prompt from the current SQL/evidence/limitations. The user controls what is copied or later shared to an external AI.

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

Interactive browser/device PWA QA.

### P0-2

AI Context-to-Prompt Handoff first implementation:

`natural result -> validation prompt -> preview -> copy`

### P0-3

Shared-code mobile wrappers:

- iOS
- Android

### P1-1 — Active parallel learning-quality slice

SQL Dialect Learning:

`common SQL -> optional DB comparison -> PostgreSQL | MySQL | SQLite`

### P1-2

Result Intelligence:

`Table | Chart | Flow | Explain`

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

On `feat/sql-dialect-learning`:

**Implement Phase A with a deterministic dialect catalog, four comparison lessons, curriculum mapping, and an optional comparison surface that leaves the default beginner flow unchanged.**

## Key Documents

- `EASY_SQL_ROADMAP.md`
- `EASY_SQL_TODO.md`
- `HANDOFF.md`
- `docs/coquery-sql-dialect-learning-plan-2026-09-02.md`
- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`
- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`
