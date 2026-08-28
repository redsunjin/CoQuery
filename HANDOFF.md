# CoQuery Handoff

Date: 2026-08-28
Status: Learning-first/PWA baseline merged through PR #13; real Cloudflare temporary hosted HTTP/API proof completed on `ops/cloudflare-temporary-deploy`

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
- PR #13: installable PWA + Cloudflare serverless scaffold + roadmap/harness currentization

Latest merged distribution baseline:

- PR #13 merge commit: `834b1eaf988b2b1c5fea2a7d9e69500d0918a61a`

Verified learner-flow contract:

`Home -> choose/continue problem -> focused SQL editor -> execute/grade -> feedback -> next incomplete problem / learning path`

Baseline CI includes dedicated static/contract smokes for:

- focused practice
- learning path
- expanded curriculum
- user-flow QA
- PWA/serverless scaffold

## Cloudflare Hosted Proof — Completed

Active proof branch:

- `ops/cloudflare-temporary-deploy`

A real authentication-free Cloudflare temporary Worker was successfully deployed and remotely verified.

Successful proof workflow:

- `cloudflare-temporary-deploy`
- successful run ID: `33148714909`
- proof head: `e09bd59b8ff891cab3a00918ec67659759e8dfc2`

Verified over the public temporary Worker URL:

- Worker deployment
- Python Worker startup
- `GET /api/health` HTTP 200
- PWA HTML shell delivery
- valid standalone manifest delivery
- 24-problem `practice_list`
- real `practice_query` SQL execution
- correct `practice_grade` result

The successful deployment uses an isolated generated bundle prepared by:

- `scripts/prepare_cloudflare_bundle.py`

The generated tree contains only:

- required Worker Python runtime
- `sql_cli`
- `practice_packs`
- `knowledge`
- PWA static assets

Generated deployment artifacts are not source and are ignored by Git.

Reference:

- `docs/coquery-cloudflare-temporary-deploy-proof-2026-08-28.md`
- `docs/coquery-pwa-cloudflare-serverless-2026-08-28.md`

## Deployment Lessons Preserved

Real temporary deployment exposed three issues that are now captured by the harness:

1. repository-wide additional-module scanning created an approximately 16.5 MiB bundle by including virtual environments and Node/local tooling
2. over-restricting module discovery then removed `sql_cli`
3. selective Static Assets routing resulted in API 404s even after the Worker bundle itself deployed successfully

The proven pattern is now:

- explicit staged runtime bundle
- Worker-first deployed routing
- Python handles `/api/*`
- non-API requests delegate to `self.env.ASSETS.fetch(request)`
- remote deployment workflow checks actual health/PWA/practice behavior

Do not regress to repository-wide Worker module discovery.

## What Hosted Proof Does and Does Not Mean

Verified:

- Cloudflare Python Worker can host the practice-first CoQuery runtime
- PWA shell and manifest can be delivered with the Worker
- current practice problem loading, SQL execution, and grading work remotely

Not yet verified:

- durable target-account deployment
- interactive browser visual-flow QA
- browser-local progress persistence across a real refresh
- service-worker offline reopening on a target browser/device
- actual PWA install completion
- iOS device/simulator wrapper
- Android device/emulator wrapper

Do not describe the temporary proof as completed production/mobile QA.

## AI Direction — Approved, Not Yet Implemented

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

First implementation slice after the durable hosted/browser baseline:

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

After real hosted PWA browser/device proof, create thin iOS/Android wrappers around the same canonical application.

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

- durable Cloudflare target-account deployment
- interactive browser QA on the durable public URL
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

Finish the deployment-proof/harness branch and durable PWA publication baseline:

1. confirm branch CI
2. open Draft PR
3. explicit merge approval
4. merge deployment proof/harness
5. authenticate/connect target Cloudflare account
6. durable `workers.dev` deploy
7. browser/PWA/device QA
8. record durable hosted verification

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

**Open and review the `ops/cloudflare-temporary-deploy` deployment-proof/harness Draft PR.**

After merge, connect the target Cloudflare account and perform durable browser/PWA QA before the AI Handoff implementation branch, unless an explicit new priority decision changes this order.

Execution history remains linear:

`learning UX -> PWA/serverless scaffold -> hosted deployment proof -> durable PWA QA -> AI validation handoff -> iOS/Android wrappers`

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
- `docs/coquery-cloudflare-temporary-deploy-proof-2026-08-28.md`
- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

Last Updated: 2026-08-28
