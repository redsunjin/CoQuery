# CoQuery Handoff

Date: 2026-08-28
Status: Learning/PWA baseline merged through PR #14; durable Cloudflare production deploy harness active on `ops/cloudflare-production-deploy`

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

Latest `main` after PR #14:

- `2f06ba761eb869c65f91a03f7588ec2d363e1173`

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

## Cloudflare Hosted Proof — Completed

A real authentication-free temporary Cloudflare Worker was deployed and verified over the public network.

Verified:

- Worker deployment/startup
- `/api/health` HTTP 200
- PWA HTML shell
- valid standalone manifest
- 24-problem `practice_list`
- SQL execution
- correct grading

Deployment uses an explicit generated bundle created by:

- `scripts/prepare_cloudflare_bundle.py`

Do not return to repository-wide Worker module discovery. The temporary proof already demonstrated that repository-wide discovery can accidentally include virtual environments and local tooling.

Reference:

- `docs/coquery-cloudflare-temporary-deploy-proof-2026-08-28.md`
- `docs/coquery-pwa-cloudflare-serverless-2026-08-28.md`

## Durable Cloudflare Production Gate — Active

Active branch:

- `ops/cloudflare-production-deploy`

Prepared:

- `.github/workflows/cloudflare-production-deploy.yml`
- manual `workflow_dispatch` only
- GitHub `production` environment
- credential presence check before deploy
- reuse of the isolated bundle builder
- durable `pywrangler deploy`
- post-deploy health verification
- post-deploy PWA shell/manifest verification
- post-deploy hosted practice verification
- regression checks that production deployment does not use the temporary-account flow
- browser/device QA checklist

Reference:

- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`

Required GitHub Actions secrets:

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

These values are not in the repository and must never be committed.

Current durable deployment blocker:

- the two Cloudflare secrets are not yet available to the GitHub workflow in this session

Once configured, manually run `cloudflare-production-deploy`. The run must return a durable Worker URL and pass all automated post-deploy checks before browser/device QA starts.

## Browser/PWA QA Required After Durable Deploy

The automated HTTP proof is not a substitute for interactive browser evidence.

Required checks:

1. open public URL without login
2. Home -> first problem -> SQL -> grade -> next problem
3. complete a problem and refresh
4. verify progress persists
5. close/reopen browser/PWA and verify progress remains
6. test offline cached-shell reopening
7. verify SQL execution clearly requires network while offline
8. verify `/api/*` does not use stale service-worker cache
9. verify install/add-to-home-screen behavior where supported

Target PWA baseline evidence should cover:

- desktop PWA-capable browser
- iOS Safari/Add to Home Screen
- Android Chrome/install flow

This is PWA evidence, not yet native App Store/Play Store wrapper evidence.

## AI Direction — Approved, Not Yet Implemented

Rule/local-knowledge behavior is still the deterministic baseline, but open-ended user meaning cannot be completely resolved by rules.

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

Durable Cloudflare/PWA release gate:

1. configure `CLOUDFLARE_ACCOUNT_ID`
2. configure `CLOUDFLARE_API_TOKEN`
3. run `cloudflare-production-deploy`
4. record durable URL/run/head
5. execute browser/device PWA QA
6. currentize roadmap/TODO/HANDOFF with actual evidence

### P0-2

AI Context-to-Prompt Handoff first implementation:

`natural result -> validation prompt -> preview -> copy`

### P0-3

Shared-code mobile wrappers:

- iOS
- Android

### P1

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

**Configure the two Cloudflare GitHub Actions secrets and run the manual production deployment workflow.**

Execution history:

`learning UX -> PWA/serverless -> hosted proof -> durable PWA QA -> AI validation handoff -> iOS/Android wrappers`

## Key Documents

- `EASY_SQL_ROADMAP.md`
- `EASY_SQL_TODO.md`
- `HANDOFF.md`
- `docs/coquery-pwa-cloudflare-serverless-2026-08-28.md`
- `docs/coquery-cloudflare-temporary-deploy-proof-2026-08-28.md`
- `docs/coquery-production-cloudflare-pwa-qa-2026-08-28.md`
- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`
