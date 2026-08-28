# CoQuery Handoff

Date: 2026-08-28
Status: Learning-first product baseline verified through PR #12; PWA/Cloudflare publication scaffold active in Draft PR #13

## Product Definition

CoQuery is a learning-first SQL product:

`Learn -> Practice -> Apply -> Assist`

The canonical product is one shared PWA/web application intended for three distributions:

- Web/PWA
- iPhone app wrapper
- Android app wrapper

Do not fork the learning flow into separate native product implementations.

## Current Verified Product Baseline

Merged August 2026 product work:

- PR #8: first-run learning Home
- PR #9: focused practice workspace
- PR #10: learning path and progress
- PR #11: 24-problem SQL curriculum
- PR #12: user-flow QA fixes and next-problem navigation

Verified learner flow on the committed code contract:

`Home -> choose/continue problem -> focused SQL editor -> execute/grade -> feedback -> next incomplete problem / learning path`

Baseline CI includes dedicated static/contract smokes for:

- focused practice
- learning path
- expanded curriculum
- user-flow QA

## Active Draft Distribution Baseline

Draft PR #13: `Add installable PWA and Cloudflare serverless scaffold`

Branch:

- `feat/pwa-cloudflare-serverless`

Prepared on the branch:

- PWA manifest
- app icon
- service worker application-shell cache
- browser PWA runtime
- learner attempt persistence in browser `localStorage` for hosted mode
- Cloudflare Python Worker adapter
- Cloudflare Static Assets configuration
- worker-first `/api/*` routing
- hosted command allowlist focused on learning/practice
- `practice_grade` forced to no server-file recording in hosted mode
- PWA/serverless regression smoke in baseline CI

Important boundary:

- code/config readiness is not the same as real deployment proof
- no `workers.dev` hosted QA has been recorded yet
- SQL execution/grading remains network dependent even if the PWA shell is cached
- Cloudflare Python Workers are a deployment choice for the hosted MVP, not a reason to rewrite the core command API

Reference:

- `docs/coquery-pwa-cloudflare-serverless-2026-08-28.md`

## AI Direction — Newly Approved

Rule-based/local-knowledge SQL generation remains the deterministic baseline, but it cannot fully determine the intent of open-ended user questions.

The approved next AI product pattern is **Context-to-Prompt Handoff**.

Purpose:

- take the user's question
- generated/submitted SQL
- selected schema evidence
- execution/grading result
- source/timestamps
- known limitations

and compose a deterministic, reviewable plain-text prompt that the user can give to an external AI for:

- SQL validation
- alternative interpretations
- missing assumptions/conditions
- counter-evidence
- next questions to investigate

This is not a built-in chatbot and does not automatically control ChatGPT/Gemini/Claude.

First implementation slice after hosted/PWA baseline:

`natural result -> Build AI validation prompt -> Preview -> Copy`

Core architecture:

- ContextAdapter
- ExportPolicy
- QuestionPolicy
- PromptComposer
- PromptPreview
- HandoffAdapter

Copy is the first universal handoff. System share/external destination opening come later.

Reference:

- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

## AI Safety / Data Boundary

The Handoff design must keep these rules:

- visible in CoQuery does not mean permitted for external AI sharing
- allowlist/minimal extraction first
- API keys, secrets, tokens, passwords, credentials, DB URIs, personal information, and unknown-permission production fields are excluded by default
- exact outgoing body must be shown before copy/share/open
- no clipboard/share/open side effect without explicit user action
- no automatic paste/send, DOM injection, login delegation, answer retrieval, or AI-generated SQL auto-execution
- Production Assist external handoff remains OFF until ExportPolicy is separately proven

## Mobile Distribution Direction

After real hosted PWA proof, create thin iOS/Android wrappers around the same canonical application.

Preferred current direction:

- Capacitor-style thin wrapper, to be validated against the current toolchain and store rules when that implementation slice starts

Native-specific concerns should stay limited to:

- app packaging
- icons/splash
- clipboard/share adapters
- required permissions
- App Store / Play Store metadata

## Existing Engineering Baseline Retained

The earlier infrastructure remains valid:

- SQLite-first working baseline
- shared `--db-uri` contract
- write safety guards
- PostgreSQL narrow experimental smoke proof
- provider registry
- DB/JPA local knowledge
- JPA source introspection
- schema-detail validation
- direct foreign-key join inference
- Production Assist read-only review/approval boundary
- Codex agent reuse package

Do not broaden PostgreSQL/MySQL/JPA claims without new verification evidence.

## What Is Not Yet Verified

- real Cloudflare hosted deployment
- browser QA on a public `workers.dev` URL
- actual PWA install QA on target devices
- iOS wrapper
- Android wrapper
- AI Context-to-Prompt implementation
- external AI copy/share/open behavior
- constrained Production Assist AI handoff
- cross-device learner progress sync
- broad PostgreSQL parity
- MySQL working support
- JPQL runtime

## Active Priority Order

### P0-1

Finish PR #13 and hosted publication proof:

1. confirm PR CI
2. explicit merge approval
3. merge
4. deploy to `workers.dev`
5. browser/PWA QA
6. record hosted verification

### P0-2

Implement AI Context-to-Prompt Handoff first slice:

`natural result -> validation prompt -> preview -> copy`

Use RED -> minimal implementation -> GREEN.

### P0-3

Prove shared-code mobile wrappers:

- iOS
- Android

### P1

- Practice-result AI handoff
- system share / selectable AI destination
- My Data bridge
- learner feedback-driven curriculum refinement

### P2

- constrained Production Assist handoff only after export-rights policy proof
- optional cross-device progress sync

## Official Harness / Working Rules

1. Work on a branch and Draft PR.
2. Do not implement directly on `main`.
3. Preserve current command/data contracts unless the slice explicitly changes them.
4. Add a failing/contract test before behavior changes where practical.
5. Make the smallest valid implementation.
6. Keep baseline CI green.
7. Keep PostgreSQL smoke truthful and green when it is part of the gate.
8. Record what was actually verified and what was not.
9. Merge only after explicit approval.
10. Currentize `EASY_SQL_ROADMAP.md`, `EASY_SQL_TODO.md`, and `HANDOFF.md` whenever product direction or verified baseline materially changes.

## Immediate Next Gate

**PR #13 must be finished/merged before starting the AI Handoff implementation branch**, unless an explicit stacked-branch decision is made.

This keeps the execution history linear:

`learning UX -> PWA/serverless publication -> AI validation handoff -> iOS/Android wrappers`

## Key Current Documents

- `EASY_SQL_ROADMAP.md`
- `EASY_SQL_TODO.md`
- `HANDOFF.md`
- `docs/coquery-ux-first-run-direction-2026-08-28.md`
- `docs/coquery-practice-focus-ux-2026-08-28.md`
- `docs/coquery-learning-path-problem-bank-2026-08-28.md`
- `docs/coquery-expanded-sql-curriculum-2026-08-28.md`
- `docs/coquery-user-flow-qa-2026-08-28.md`
- `docs/coquery-pwa-cloudflare-serverless-2026-08-28.md`
- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

Last Updated: 2026-08-28
