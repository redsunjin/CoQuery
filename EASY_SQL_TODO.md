# CoQuery Todo List

Version: product baseline 2026-09-02
Last Updated: 2026-09-02

## Active Priorities

### P0-1. Durable PWA + Cloudflare publication baseline

Completed:

- [x] PR #13 PWA/serverless scaffold merged
- [x] PR #14 temporary hosted proof + isolated deployment harness merged
- [x] PR #15 production deployment workflow + PWA QA harness merged
- [x] PR #16 production API verification hardening merged
- [x] PWA manifest / service worker / browser-local progress
- [x] Cloudflare Python Worker practice API
- [x] durable Worker deployment
- [x] production `/api/health` proof
- [x] production PWA shell/manifest proof
- [x] production 24-problem listing
- [x] production SQL execution
- [x] production grading
- [x] isolated deployment bundle prevents repository-wide over-bundling
- [x] GitHub `production` environment and Cloudflare secret contract
- [x] production post-deploy health/PWA/practice checks
- [x] deployment-propagation retry for hosted practice verification

Durable URL:

- `https://coquery-pwa.edu-public-app.workers.dev`

Remaining interactive QA:

- [ ] browser QA: Home -> problem bank -> solve -> grade -> next problem
- [ ] verify progress across browser reload/relaunch
- [ ] verify `/api/*` is not served from stale service-worker cache
- [ ] verify offline shell reopening and explicit network-required execution failure
- [ ] verify desktop PWA installation where supported
- [ ] verify iOS Safari Add to Home Screen baseline
- [ ] verify Android Chrome install/add-to-home-screen baseline
- [ ] update roadmap/TODO/HANDOFF with actual device/browser evidence

Reference:

- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`

### P0-2. AI Context-to-Prompt Handoff — first implementation slice

Reference:

- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

First boundary:

`natural result -> AI validation prompt -> preview -> copy`

Tasks:

- [ ] add deterministic prompt contract tests
- [ ] define ContextSnapshot
- [ ] implement ExportPolicy allowlist / sensitive-field exclusion
- [ ] implement QuestionPolicy quality states
- [ ] implement versioned PromptComposer pure function
- [ ] implement PromptPreview revision state
- [ ] add `Build AI validation prompt` action to natural result
- [ ] show exact outgoing body before clipboard action
- [ ] implement copy-only HandoffAdapter
- [ ] preserve user edits when source data changes
- [ ] make copy failure leave selectable text
- [ ] verify no automatic external open/share/send
- [ ] add KR/EN prompt templates and tests

### P0-3. iOS / Android wrapper baseline

After durable PWA/browser proof:

- [ ] validate minimal Capacitor-style wrapper against current toolchain/store requirements
- [ ] define canonical shared-source / generated-native boundary
- [ ] create iOS wrapper
- [ ] create Android wrapper
- [ ] prove iOS simulator/device shell
- [ ] prove Android emulator/device shell
- [ ] map clipboard/share adapters
- [ ] prepare app icons/splash/store metadata
- [ ] record App Store / Play Store release checklist

Do not fork learning/business logic into separate native implementations.

## P1 — Learning Quality

### P1-1. SQL Dialect Learning — active branch

Branch:

- `feat/sql-dialect-learning`

Reference:

- `docs/coquery-sql-dialect-learning-plan-2026-09-02.md`

Product rule:

`common SQL first -> optional DB별 차이 보기 -> PostgreSQL | MySQL | SQLite`

Phase A tasks:

- [x] define product/learning contract
- [x] define `common` / `reference` / `verified` truthfulness states
- [x] define deterministic `DialectLesson` data model
- [x] implement `DialectCatalog`
- [x] add first 4 P0 comparison topics
  - [x] string concatenation
  - [x] current date/time
  - [x] date arithmetic
  - [x] row limiting/commonality lesson
- [x] add PostgreSQL/MySQL/SQLite variants
- [x] add KR/EN copy
- [x] add `DB별 차이 보기` only when a relevant comparison exists
- [x] show verification state in the comparison UI
- [x] map comparison lessons to relevant curriculum problems
- [x] add deterministic catalog/mapping regression tests
- [x] keep MySQL examples at `reference` until a real MySQL runtime/test baseline exists
- [x] keep existing beginner flow unchanged when the comparison panel is closed

Phase A proof:

- [x] `dialect_learning_smoke.py` asserts deterministic lesson order, KR/EN content, problem mappings, state labels, and no MySQL `verified` example
- [x] the SQLite examples marked `verified` execute in the regression test
- [ ] record the completed baseline and PostgreSQL CI runs on Draft PR #19

Phase B:

- [ ] expand comparison coverage only from demonstrated learner gaps
- [ ] add boolean/upsert/generated-ID/case-insensitive matching lessons where useful

Phase C — engine-backed proof:

- [ ] expand PostgreSQL `verified` coverage only where smoke tests execute the behavior
- [ ] establish a MySQL test baseline before any MySQL `verified` badge
- [ ] record engine/version assumptions for behavior-sensitive comparisons

Explicit non-goals for the first slice:

- [ ] no general SQL transpiler
- [ ] no arbitrary SQL automatic cross-engine conversion
- [ ] no claim of broad PostgreSQL/MySQL compatibility
- [ ] no replacement of SQLite as the practice baseline

### P1-2. Result Intelligence / BI interpretation

Direction:

`Table | Chart | Flow | Explain`

- [ ] document result-intelligence UX contract
- [ ] define deterministic chart recommendation rules
- [ ] separate SQL syntax/dialect learning from result interpretation
- [ ] evaluate lightweight visualization implementation against the current static PWA architecture

### Other P1

#### AI handoff expansion

- [ ] Practice-result handoff
- [ ] system share
- [ ] user-selectable external AI destination
- [ ] copy + open failure-safe behavior

#### My Data bridge

- [ ] define sample-to-user-data transition
- [ ] preserve beginner-first surface
- [ ] preserve Production Assist safety gates

#### Learning quality

- [ ] collect real learner feedback on the 24-problem path
- [ ] improve schema/data preview based on evidence
- [ ] add scenario packs only when gaps are demonstrated

## P2

### Constrained Production Assist AI handoff

Default OFF until:

- [ ] external-sharing ExportPolicy is proven
- [ ] display permission is separated from external-provision permission
- [ ] explicitly allowed schema/aggregate/non-sensitive context is defined
- [ ] sensitive-field blocking is tested

### Cross-device learner sync

Only when product evidence requires it:

- [ ] decide D1/KV/account requirement
- [ ] keep no-login browser-local mode usable

## Existing Engineering Baseline Retained

- [x] SQLite-first working baseline
- [x] shared DB URI contract
- [x] PostgreSQL narrow experimental smoke path
- [x] write safety guard
- [x] provider registry direction
- [x] DB/JPA local knowledge
- [x] JPA source introspection
- [x] schema-detail identifier validation
- [x] direct foreign-key join inference
- [x] Production Assist safety gate

Not complete:

- [ ] broad PostgreSQL parity
- [ ] working MySQL runtime baseline
- [ ] JPQL runtime
- [ ] unrestricted production-grade NL-to-SQL

## Execution Rules

1. branch + Draft PR
2. no direct `main` implementation commits
3. preserve existing contracts unless the slice explicitly changes them
4. RED -> minimum implementation -> GREEN where practical
5. baseline CI stays green
6. PostgreSQL smoke stays truthful when part of the gate
7. record skipped and completed validation explicitly
8. merge only after explicit approval
9. currentize roadmap/TODO/HANDOFF after material baseline changes

## Current Next Action

**Implement Phase A of SQL Dialect Learning on `feat/sql-dialect-learning`: deterministic catalog + first four comparison lessons + optional comparison surface, without changing the default beginner flow.**
