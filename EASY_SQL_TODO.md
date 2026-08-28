# CoQuery Todo List

Version: product baseline 2026-08-28
Last Updated: 2026-08-28

## Active Priorities

### P0-1. Durable PWA + Cloudflare publication baseline

Completed:

- [x] PR #13 PWA/serverless scaffold merged
- [x] PR #14 temporary hosted proof + isolated deployment harness merged
- [x] PWA manifest / service worker / browser-local progress
- [x] Cloudflare Python Worker practice API
- [x] real temporary Worker deploy/startup proof
- [x] remote `/api/health` proof
- [x] remote PWA shell/manifest proof
- [x] remote 24-problem listing
- [x] remote SQL execution
- [x] remote grading
- [x] isolated deployment bundle prevents repository-wide over-bundling
- [x] add manual production deployment workflow
- [x] require GitHub `production` environment
- [x] require `CLOUDFLARE_ACCOUNT_ID`
- [x] require `CLOUDFLARE_API_TOKEN`
- [x] add production health/PWA/practice post-deploy checks
- [x] add production deployment regression contract to PWA smoke
- [x] document browser/device installation QA gate

Active branch:

- `ops/cloudflare-production-deploy`

Current blocker / next actions:

- [ ] add GitHub Actions secret `CLOUDFLARE_ACCOUNT_ID`
- [ ] add GitHub Actions secret `CLOUDFLARE_API_TOKEN`
- [ ] run `cloudflare-production-deploy` manually
- [ ] record durable `workers.dev` URL
- [ ] record production workflow run ID and deployment head SHA
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

Acceptance:

- same input/version/language => same body
- unknown stays unknown
- zero is not treated as missing
- source/timestamps/limitations remain explicit
- sensitive or unknown-permission fields are excluded
- copied revision equals reviewed preview revision
- clipboard side effect requires explicit user action
- CoQuery never claims an external AI received the prompt

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

## P1

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

**Configure the two Cloudflare GitHub Actions secrets, then manually run `cloudflare-production-deploy`.**
