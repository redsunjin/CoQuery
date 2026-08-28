# CoQuery Todo List

Version: product baseline 2026-08-28
Last Updated: 2026-08-28

## Active Priorities

This file is the execution queue. Historical DB/backend stabilization work remains valid evidence, but it is not the only active product loop anymore.

### P0-1. Finish durable PWA + Cloudflare publication baseline

Merged baseline:

- [x] PR #13 PWA/serverless scaffold merged
- [x] PWA manifest
- [x] service worker application-shell cache
- [x] PWA runtime
- [x] browser-local hosted practice progress
- [x] Cloudflare Python Worker adapter
- [x] Cloudflare Static Assets configuration
- [x] hosted practice command allowlist
- [x] hosted `practice_grade` without server-file recording
- [x] PWA/serverless smoke in baseline CI

Real temporary Cloudflare proof:

- [x] create isolated deployment bundle builder
- [x] prevent repository-wide `.venv`/`node_modules` over-bundling
- [x] package `sql_cli`, practice packs, knowledge, and PWA assets explicitly
- [x] deploy a real authentication-free temporary Worker
- [x] verify `/api/health` remotely
- [x] verify PWA shell and manifest remotely
- [x] verify 24-problem `practice_list` remotely
- [x] verify `practice_query` SQL execution remotely
- [x] verify `practice_grade` correct result remotely
- [x] document deployment failures and fixes

Active branch:

- `ops/cloudflare-temporary-deploy`

Current remaining gate:

- [ ] confirm branch baseline/PostgreSQL CI after documentation updates
- [ ] create Draft PR for the deployment proof/harness
- [ ] explicit merge approval
- [ ] merge deployment-proof PR
- [ ] authenticate/connect the target Cloudflare account
- [ ] deploy to durable `workers.dev`
- [ ] browser QA: Home -> problem bank -> solve -> grade -> next problem
- [ ] verify browser-local progress across reload
- [ ] verify API responses are not service-worker cached
- [ ] verify service-worker offline shell reopening
- [ ] verify PWA installation on supported desktop/mobile browser
- [ ] record durable hosted URL and exact device/browser evidence

Reference:

- `docs/coquery-cloudflare-temporary-deploy-proof-2026-08-28.md`

### P0-2. AI Context-to-Prompt Handoff — first implementation slice

Reference:

- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

First boundary:

`natural result -> AI validation prompt -> preview -> copy`

Do not start from a full chatbot or provider SDK.

Tasks:

- [ ] add failing contract tests for deterministic prompt generation
- [ ] define normalized ContextSnapshot
- [ ] implement ExportPolicy allowlist and sensitive-field exclusion
- [ ] implement QuestionPolicy for sufficient/limited/stale/insufficient context
- [ ] implement versioned PromptComposer pure function
- [ ] implement PromptPreview revision state
- [ ] add explicit `Build AI validation prompt` action to `natural` result
- [ ] show exact outgoing body before any side effect
- [ ] implement copy-only HandoffAdapter first
- [ ] preserve user edits when source context changes
- [ ] ensure copy failure leaves selectable text
- [ ] verify no automatic external open/share/send
- [ ] add KR/EN prompt templates and tests
- [ ] document actual verified behavior after implementation

Acceptance:

- same input/version/language => same body
- unknown remains unknown; zero is not invented
- data source and timestamps remain explicit
- sensitive and unknown-permission fields are excluded
- exact preview revision equals copied revision
- user action is required before clipboard side effect
- no claim that an external AI received the prompt

### P0-3. iOS / Android wrapper baseline

Goal:

- distribute the same canonical product as Web/PWA, iPhone, and Android apps

Tasks after hosted PWA proof:

- [ ] validate current minimal wrapper choice (Capacitor-style preferred direction)
- [ ] document canonical source / generated native project boundary
- [ ] create iOS wrapper
- [ ] create Android wrapper
- [ ] prove iOS simulator flow
- [ ] prove Android emulator flow
- [ ] map PWA clipboard/share behavior to native adapter where needed
- [ ] prepare app icons/splash/store metadata separately
- [ ] record App Store / Play Store release checklist

Do not fork learning logic or SQL UI into separate native implementations.

## P1 Product Tasks

### AI handoff expansion

- [ ] add Practice result handoff
- [ ] add system share where supported
- [ ] add user-selectable external AI destination
- [ ] keep prompt out of URL query by default
- [ ] handle open failure independently from copy success
- [ ] treat share cancellation as cancellation, not success

### My Data bridge

- [ ] define smallest path from built-in sample data to user-selected data
- [ ] preserve beginner-first surface
- [ ] keep production safety gates explicit

### Learning quality

- [ ] review 24-problem progression using real learner feedback
- [ ] improve schema/data preview where needed
- [ ] add more scenario packs only after evidence of gaps

## P2 Tasks

### Constrained Production Assist AI handoff

Default OFF.

Before enabling:

- [ ] prove external-sharing ExportPolicy
- [ ] distinguish display permission from external-provision permission
- [ ] restrict to explicitly allowed schema/aggregates/non-sensitive context
- [ ] test sensitive-field blocking
- [ ] document audit/privacy boundary

### Cross-device learner sync

Only when required by product usage:

- [ ] decide D1/KV/account requirement
- [ ] keep browser-local mode usable without login

## Completed August 2026 Product Work

- [x] PR #8 first-run learning Home
- [x] PR #9 focused practice workspace
- [x] PR #10 learning path and progress
- [x] PR #11 curriculum expansion to 24 problems
- [x] PR #12 learning-flow QA fixes
- [x] PR #13 PWA/serverless scaffold + product harness currentization

## Existing Engineering Baseline — Retained

The following are not deleted from the roadmap. They remain verified/experimental infrastructure:

- [x] SQLite-first baseline
- [x] shared DB URI contract
- [x] PostgreSQL narrow experimental smoke path
- [x] PostgreSQL safety guard smoke
- [x] provider registry direction
- [x] Codex agent reuse package
- [x] JPA source introspection
- [x] offline DB/JPA knowledge base
- [x] schema-detail-backed identifier validation
- [x] direct foreign-key join inference
- [x] Production Assist safety gate

Still not complete:

- [ ] broad PostgreSQL parity
- [ ] working MySQL baseline
- [ ] JPQL runtime
- [ ] production-grade unrestricted NL-to-SQL

## Execution Rules

For active work:

1. branch + Draft PR
2. no direct `main` implementation commits
3. preserve existing contracts unless the slice explicitly changes them
4. RED -> minimal implementation -> GREEN for behavior changes where practical
5. baseline CI must stay green
6. PostgreSQL smoke must stay green when relevant to the branch gate
7. record limitations and skipped validation
8. merge only after explicit approval
9. update `EASY_SQL_ROADMAP.md`, `EASY_SQL_TODO.md`, and `HANDOFF.md` whenever the verified product baseline materially changes

## Current Next Action

**Finish the `ops/cloudflare-temporary-deploy` proof/harness PR gate.**

After it is merged, connect the durable Cloudflare account and complete browser/device PWA QA before starting the AI Handoff implementation, unless a new explicit priority decision changes that gate.
