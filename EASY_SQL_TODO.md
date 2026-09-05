# CoQuery Todo List

Version: product baseline 2026-09-03
Last Updated: 2026-09-03

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
- [x] production hosted practice API proof
- [x] isolated deployment bundle
- [x] production post-deploy health/PWA/practice checks
- [x] deployment-propagation retry for hosted practice verification

Durable URL:

- `https://coquery-pwa.edu-public-app.workers.dev`

Remaining interactive QA:

- [ ] Home -> problem bank -> solve -> grade -> next problem
- [ ] verify progress across browser reload/relaunch
- [ ] verify `/api/*` is not served from stale service-worker cache
- [ ] verify offline shell reopening and explicit network-required execution failure
- [ ] verify desktop PWA installation where supported
- [ ] verify iOS Safari Add to Home Screen baseline
- [ ] verify Android Chrome install/add-to-home-screen baseline
- [ ] record actual browser/device evidence

Reference:

- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`

### P0-2. BI Result Intelligence — active Draft PR #18

References:

- `docs/coquery-bi-result-intelligence-2026-08-30.md`
- `docs/coquery-query-graph-implementation-2026-09-02.md`
- `docs/coquery-deterministic-explain-implementation-2026-09-02.md`
- `docs/coquery-line-result-visual-implementation-2026-09-02.md`
- `docs/coquery-recommendation-reason-localization-2026-09-02.md`

Product principle:

**SQL as Visual Data Transformation**

Product surface:

`Table | Visual | Flow | Explain`

Three visual layers:

1. Query Graph — recognized logical SQL transformation structure.
2. Result Visual — BI view derived from exact returned rows.
3. Execution Graph — actual database plan evidence only; never inferred from SQL text.

Implemented on PR #18:

- [x] deterministic ResultShape classifier + regression contracts
- [x] conservative SQL `flow_steps`
- [x] hosted `practice_query` additive result-intelligence metadata
- [x] real column/row Table renderer
- [x] preserve `NULL` and zero truthfully
- [x] Bar Result Visual only for proven `category_measure`
- [x] Line Result Visual only for safely ordered `time_series`
- [x] Line preserves exact returned order and does not infer elapsed-time spacing
- [x] visible Query Graph/Flow from recognized SQL steps only
- [x] explicit Query Graph boundary against execution-plan semantics
- [x] deterministic Explain
- [x] Explain boundary against business causality/hidden meaning/physical execution inference
- [x] deterministic KR/EN recommendation-reason localization
- [x] Korean UI no longer reuses backend-English `reason` as learner-facing copy
- [x] executable Bar/Line, Query Graph, Explain/localization smokes
- [x] no React migration
- [x] no external AI requirement
- [x] synchronize PR #18 with current main, retaining merged SQL Dialect Learning and privacy-policy work
- [x] combined PWA cache contract includes BI assets + `dialect-learning.js`

Next BI tasks:

- [ ] define keyboard/focus semantics for future `Table | Visual | Flow | Explain` switching
- [ ] define tab vs arrow-key behavior and selected-state semantics
- [ ] keep no-JS/no-chart Table fallback usable
- [ ] add accessibility regression smoke for view switching before exposing tabs
- [ ] keep exact raw result available as explicit evidence regression check
- [ ] decide whether local/advanced command runtime should attach the same additive metadata before closing the first BI slice

Acceptance:

- same rows/SQL => same classification
- ambiguous result => Table
- chart recommendation always explains why
- localization does not alter classification decisions
- Bar renders only proven category + measure results
- Line renders only safely ordered time-series results
- Line does not sort returned rows or infer elapsed-time distance
- Query Graph contains only recognized SQL structure
- Query Graph is never presented as physical runtime order/execution plan
- Execution Graph is never shown without actual planner/executor evidence
- Explain never invents business causality or hidden semantics
- Table remains canonical evidence
- BI enrichment does not mutate `columns`, `rows`, or `row_count`
- existing practice catalog/query/grading/non-SELECT contracts remain green

### P0-3. AI Context-to-Prompt Handoff — first implementation slice

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

Acceptance:

- same input/version/language => same body
- unknown stays unknown
- zero is not treated as missing
- sensitive or unknown-permission fields are excluded
- clipboard/share side effect requires explicit user action
- CoQuery never claims an external AI received the prompt

### P0-4. iOS / Android wrapper baseline

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

### P1-1. SQL Dialect Learning — Phase A merged in PR #19

Reference:

- `docs/coquery-sql-dialect-learning-plan-2026-09-02.md`

Product rule:

`common SQL first -> optional DB별 차이 보기 -> PostgreSQL | MySQL | SQLite`

Phase A:

- [x] deterministic `DialectLesson` / `DialectCatalog`
- [x] string concatenation comparison
- [x] current date/time comparison
- [x] date arithmetic comparison
- [x] row limiting/commonality lesson
- [x] PostgreSQL/MySQL/SQLite variants
- [x] KR/EN copy
- [x] optional default-closed comparison UI only for mapped problems
- [x] `common` / `reference` / `verified` state labels
- [x] deterministic catalog/problem-mapping regression tests
- [x] SQLite execution proof for examples labeled `verified`
- [x] MySQL stays `reference`; no runtime-support claim
- [x] PR #19 merged into main

Future dialect tasks:

- [ ] expand comparison coverage only from demonstrated learner gaps
- [ ] add additional lessons only where useful
- [ ] expand PostgreSQL `verified` coverage only with executed proof
- [ ] establish a MySQL runtime/test baseline before any MySQL `verified` badge

Explicit non-goals:

- [ ] no general SQL transpiler
- [ ] no arbitrary SQL automatic cross-engine conversion
- [ ] no claim of broad PostgreSQL/MySQL compatibility
- [ ] no replacement of SQLite as the practice baseline

### P1-2. Query Graph / Execution Graph expansion

- [ ] nested Query Graph for subqueries/CTEs only after explicit parser contracts
- [ ] window/set-operation graph semantics only with deterministic coverage
- [ ] research provider-specific `EXPLAIN` contracts
- [ ] define Execution Graph evidence schema
- [ ] keep Execution Graph labeled separately from Query Graph

### P1-3. Additional BI visuals

Only when ResultShape rules justify them:

- [ ] Ring/Pie for explicit part-to-whole results
- [ ] Scatter for true numeric observation pairs
- [ ] Funnel for explicit ordered stages
- [ ] Sankey for explicit source/target/value results
- [ ] Gauge only with explicit target/range
- [ ] Choropleth only with a supported geography contract

### Other P1

- [ ] Practice-result AI handoff
- [ ] system share / selectable external AI destination
- [ ] My Data bridge
- [ ] learner-feedback-driven curriculum refinement

## P2

### Constrained Production Assist AI handoff

Default OFF until:

- [ ] external-sharing ExportPolicy is proven
- [ ] display permission is separated from external-provision permission
- [ ] explicitly allowed schema/aggregate/non-sensitive context is defined
- [ ] sensitive-field blocking is tested

### Cross-device learner sync

- [ ] decide D1/KV/account requirement only when product evidence requires it
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
2. synchronize with current `main` before continuing when the base has moved materially
3. no direct `main` implementation commits from the active slice
4. preserve existing contracts unless the slice explicitly changes them
5. RED -> minimum implementation -> GREEN where practical
6. baseline CI stays green
7. PostgreSQL smoke stays truthful when part of the gate
8. record skipped and completed validation explicitly
9. merge only after explicit approval
10. currentize roadmap/TODO/HANDOFF after material baseline changes
11. prefer one cohesive implementation commit per logical slice; documentation-only currentization may follow after verified CI

## Current Next Action

**Implement the keyboard/accessibility baseline for future `Table | Visual | Flow | Explain` view switching before adding more BI chart types.**
