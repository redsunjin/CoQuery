# CoQuery Todo List

Version: product baseline 2026-09-02
Last Updated: 2026-09-02

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

Product principle:

**SQL as Visual Data Transformation**

Three visual layers:

1. **Query Graph** — recognized SQL transformation structure; core learning experience.
2. **Result Visual** — BI view derived from exact returned rows.
3. **Execution Graph** — actual database plan evidence; later slice and never inferred from SQL text alone.

Product surface:

`Table | Visual | Flow | Explain`

Current boundary:

`practice_query result -> classify -> Table | Result Visual recommendation | Query Graph/Flow | Explain`

Classifier baseline completed on active PR #18:

- `sql_cli/result_intelligence.py`
- `sql_cli/tests/test_result_intelligence.py`
- baseline CI executes the classifier contracts

Hosted integration completed on active PR #18:

- `sql_cli/result_integration.py` attaches additive `result_intelligence` metadata without mutating raw result data
- `cloudflare_worker.py` enriches successful hosted `practice_query` responses
- focused practice UI replaces visible JSON-string preview with a real column/row table
- all returned rows from the current query response are rendered
- `NULL` remains `NULL`; numeric zero remains `0`
- recommendation metadata is shown above the canonical Table result
- mobile table overflow is handled without React
- `sql_cli/tests/test_practice_query_regression.py` protects existing learner/query/grading contracts

Tasks:

- [x] define `ResultShape` contract
- [x] add deterministic classifier tests
- [x] classify category + measure results
- [x] classify time-series candidates
- [x] classify source/target/value only when explicit
- [x] fall back to `tabular`/Table for ambiguous results
- [x] cover single metric, part-to-whole, numeric relationship, ordered stage, zero/null, category-count guardrails, and deterministic/non-mutating behavior
- [x] derive conservative SQL flow steps from explicitly recognized clauses
- [x] wire ResultShape metadata into hosted `practice_query` output
- [x] replace JSON-string row preview with a real column/row Table renderer in focused practice
- [x] add recommendation reason to the result block
- [x] keep zero/null handling truthful in the Table renderer
- [x] verify no external AI/provider call is required in the rendered result flow
- [x] document `SQL as Visual Data Transformation` product principle
- [x] explicitly separate Query Graph / Result Visual / Execution Graph
- [x] make Query Graph/Flow a first-class learning view in the roadmap
- [ ] add first lightweight Bar Result Visual without React migration
- [ ] add visible Query Graph/Flow renderer from recognized `flow_steps`
- [ ] label Query Graph clearly so it cannot be mistaken for an execution plan
- [ ] add textual alternative for Query Graph accessibility
- [ ] add deterministic Explain copy connecting SQL transformation + row meaning + visual recommendation
- [ ] keep exact raw result available in the detail panel as an explicit regression check
- [ ] complete KR/EN result-intelligence copy instead of backend-English reason text
- [ ] add keyboard/accessibility baseline for view tabs
- [ ] decide whether the local/advanced command runtime should attach the same additive metadata before the BI slice closes

Acceptance:

- same rows/SQL => same classification
- ambiguous result => Table
- chart recommendation always explains why
- Query Graph contains only recognized SQL structure
- Query Graph is never presented as physical runtime order/execution plan
- Execution Graph is never shown without actual planner/executor evidence
- Table remains canonical evidence
- BI enrichment does not mutate `columns`, `rows`, or `row_count`
- existing practice catalog/query/grading/non-SELECT contracts remain green
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

### Query Graph / Execution Graph expansion

Only after the first Query Graph renderer is proven:

- [ ] support nested Query Graph structures for subqueries/CTEs only with explicit parser contracts
- [ ] add window/set-operation graph semantics only with deterministic coverage
- [ ] research provider-specific `EXPLAIN` contracts
- [ ] define Execution Graph evidence schema
- [ ] ensure Execution Graph is labeled separately from Query Graph

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

**Add the first lightweight Bar Result Visual for proven `category_measure` results while Table remains canonical; then implement the Query Graph/Flow renderer as the next core learning view.**