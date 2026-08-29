# CoQuery Todo List

Version: product baseline 2026-08-30
Last Updated: 2026-08-30

## Active Priorities

### P0-1. Durable PWA + Cloudflare publication baseline

Completed:

- [x] PR #13 PWA/serverless scaffold merged
- [x] PR #14 temporary hosted proof + isolated deployment harness merged
- [x] PR #15 durable production workflow + PWA QA contract merged
- [x] PR #16 production API verification hardening merged
- [x] PWA manifest / service worker / browser-local progress
- [x] Cloudflare Python Worker practice API
- [x] durable production Worker created
- [x] production `/api/health` proof
- [x] production PWA shell/manifest proof
- [x] production hosted practice API proof
- [x] deployment verification tolerates short propagation windows without masking non-retryable failures

Durable Worker:

- `https://coquery-pwa.edu-public-app.workers.dev`

Successful production workflow:

- run `33160202910`

Remaining browser/device evidence:

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

### P0-2. BI Result Intelligence — active

Reference:

- `docs/coquery-bi-result-intelligence-2026-08-30.md`

Product surface:

`Table | Visual | Flow | Explain`

First boundary:

`practice_query result -> classify -> Table | Visual recommendation | SQL Flow | Explain`

Classifier baseline completed on the active branch:

- `sql_cli/result_intelligence.py`
- `sql_cli/tests/test_result_intelligence.py`
- baseline CI executes the classifier contracts

Tasks:

- [x] define `ResultShape` contract
- [x] add deterministic classifier tests
- [x] classify category + measure results
- [x] classify time-series candidates
- [x] classify source/target/value only when explicit
- [x] fall back to `tabular`/Table for ambiguous results
- [x] cover single metric, part-to-whole, numeric relationship, ordered stage, zero/null, category-count guardrails, and deterministic/non-mutating behavior
- [x] derive conservative SQL flow steps from explicitly recognized clauses
- [ ] wire ResultShape metadata into `practice_query` output
- [ ] replace JSON-string row preview with a real column/row Table renderer
- [ ] add recommendation reason to the result block
- [ ] add first lightweight Bar renderer without React migration
- [ ] add SQL clause Flow renderer for supported SELECT clauses
- [ ] add deterministic Explain copy
- [ ] keep exact raw result available in the detail panel
- [ ] add KR/EN copy
- [ ] add keyboard/accessibility baseline for view tabs
- [ ] verify no external AI/provider call is required in the rendered result flow

Acceptance:

- same rows/SQL => same classification
- ambiguous result => Table
- chart recommendation always explains why
- SQL Flow never invents an unsupported clause/meaning
- Table remains the canonical evidence view
- no React dependency is added in the first slice
- no external AI requirement is added

Bklit reference boundary:

- use `bklit/bklit-ui` as chart/BI design reference
- upstream chart components are MIT-licensed
- Bklit Studio is proprietary and is not reusable/redistributable
- direct component adoption is deferred because current CoQuery is plain HTML/CSS/JS and Bklit components are React-based

### P0-3. AI Context-to-Prompt Handoff — first implementation slice

Reference:

- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

Starts after the BI first slice unless explicitly reprioritized.

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
- source/timestamps/limitations remain explicit
- sensitive or unknown-permission fields are excluded
- copied revision equals reviewed preview revision
- clipboard side effect requires explicit user action
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

## P1

### BI expansion

Only after the first ResultShape contract is proven:

- [ ] Line/time-series renderer
- [ ] part-to-whole Ring/Pie when the total is explicit
- [ ] Scatter for true numeric observation pairs
- [ ] Funnel for explicit ordered stages
- [ ] Sankey for explicit source/target/value results
- [ ] Gauge only with an explicit target/range
- [ ] Choropleth only with a supported geography contract

### AI handoff expansion

- [ ] Practice-result handoff
- [ ] system share
- [ ] user-selectable external AI destination
- [ ] copy + open failure-safe behavior

### My Data bridge

- [ ] define sample-to-user-data transition
- [ ] preserve beginner-first surface
- [ ] preserve Production Assist safety gates

### Learning quality

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

## Completed August 2026 Product Work

- [x] PR #8 first-run learning Home
- [x] PR #9 focused practice workspace
- [x] PR #10 learning path/progress
- [x] PR #11 24-problem curriculum
- [x] PR #12 learner-flow QA
- [x] PR #13 PWA/serverless scaffold
- [x] PR #14 Cloudflare temporary hosted proof + deployment harness
- [x] PR #15 durable production deployment workflow + PWA QA gate
- [x] PR #16 production API verification hardening + successful production proof

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
- [ ] working MySQL baseline
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

**Wire `ResultShape` into `practice_query`, then replace the JSON-string preview with the canonical real Table renderer before adding any chart.**
