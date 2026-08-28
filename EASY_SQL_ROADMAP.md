# CoQuery Roadmap

Version: product baseline 2026-08-28
Last Updated: 2026-08-28

## Product Definition

CoQuery is a learning-first SQL product that helps a user move through:

`Learn -> Practice -> Apply -> Assist`

The canonical product surface is one shared web/PWA codebase. The distribution goal is:

- Web/PWA
- iPhone app wrapper
- Android app wrapper

Native apps should reuse the same product logic rather than fork the product into separate implementations.

## Current Verified Position

### Product UX

- learning-first Home exists
- focused SQL practice workspace exists
- learning path and progress UI exist
- built-in curriculum contains 24 verified problems
- learner progress uses existing practice-attempt history locally
- successful grading can continue directly to the next incomplete problem
- user-flow QA smoke is part of baseline CI

### SQL / data engine

- SQLite remains the working baseline
- built-in practice sandbox is working
- local knowledge-first generation remains deterministic where covered
- natural-language SQL remains assistive, heuristic/local-first, with optional provider support
- PostgreSQL remains a narrow experimental track proven by smoke tests
- MySQL remains outside the working product baseline

### Product distribution

PR #13 prepares:

- installable PWA manifest
- application-shell service worker
- Cloudflare Static Assets
- Cloudflare Python Worker API adapter
- browser-local learner progress for hosted MVP

Cloudflare deployment is not yet part of the verified production baseline until a real `workers.dev` deployment and browser QA are completed.

## Product Architecture Direction

### Shared application core

One shared product behavior should serve Web, iOS, and Android.

Platform-specific code should be limited to:

- installation/package shell
- clipboard/share integration
- store metadata/assets
- platform permissions where actually needed

### AI role

Rule/local-knowledge behavior stays the deterministic baseline, but open-ended user meaning cannot be fully resolved by rules alone.

The next AI direction is therefore two-layered:

1. CoQuery creates SQL and exposes the evidence/limitations behind it.
2. Context-to-Prompt Handoff lets the user ask an external AI to validate, challenge, reinterpret, or extend the result.

This does not require CoQuery to become a full chatbot.

Reference:

- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`

## Active Priority Stack

### P0-A. Finish PWA/serverless publication baseline

Goal:

- merge the serverless/PWA scaffold only after CI is green
- deploy to a Cloudflare `workers.dev` URL
- verify installability and the complete learner flow in a real browser

Acceptance:

- Home loads from hosted URL
- problem bank loads
- SQL executes and grades
- learner progress persists in browser storage
- next-problem flow works
- service worker does not cache API responses
- PWA can be installed where platform/browser supports it

### P0-B. AI validation handoff — first slice

Starts only after P0-A is merged/verified.

First implementation boundary:

`natural result -> Build AI validation prompt -> Preview -> Copy`

Required modules:

- ContextAdapter
- ExportPolicy
- QuestionPolicy
- PromptComposer
- PromptPreview
- HandoffAdapter(copy only in first slice)

No new backend is required.

### P0-C. Mobile wrapper baseline

After hosted PWA behavior is stable:

- choose and document the minimal iOS/Android wrapper
- keep shared web/PWA source as canonical
- prove iOS simulator/device shell
- prove Android emulator/device shell
- add store-required assets and metadata separately

Current preferred direction: a thin Capacitor-style wrapper, subject to implementation-time validation of the current toolchain and store requirements.

### P1. AI handoff expansion

After prompt-generation proof:

- Practice result handoff
- system share
- configurable external AI destination
- copy + open flow with failure-safe behavior

### P1. My Data bridge

Goal:

- transition from sample-data learning to user-selected real data without exposing production complexity at first entry

Keep Production Assist safety boundaries unchanged.

### P2. Constrained Production Assist handoff

Only after ExportPolicy and external-sharing rights are proven.

Default remains OFF for production data.

## Historical Product Slices Completed in August 2026

### UX Phase 1

PR #8 — first-run practice experience

- learning Home
- first-problem CTA
- problem-bank entry
- advanced workspace retained

### UX Phase 2

PR #9 — focused practice workspace

- problem -> SQL -> run/check -> feedback
- terminal chrome hidden during learning
- hints made secondary

### UX Phase 3

PR #10 — learning path

- progress
- completed/in-progress/not-started state
- continue learning
- concept grouping

### UX Phase 4

PR #11 — curriculum expansion

- 5 -> 24 problems
- foundations, filters, joins, aggregation, business questions
- all expected SQL automatically verified

### UX Phase 5

PR #12 — user-flow QA

- problem-list return fixed
- next-problem navigation
- schema/attempt/feedback visibility in focus mode
- user-flow regression smoke

### Distribution Phase

PR #13 — currently Draft

- PWA
- Cloudflare Python Worker scaffold
- Static Assets
- browser-local hosted progress

## Existing Engineering Tracks Kept Intact

These remain valid but are no longer the sole product roadmap:

- PostgreSQL verification-gated experimental support
- provider registry
- DB/JPA knowledge base
- JPA source introspection
- write safety gates
- Production Assist read-only review/approval boundary
- agent reuse package

Broader backend claims still require explicit verification slices.

## Official Active Loop

For every slice:

1. confirm current main/PR baseline
2. document the decision and scope boundary
3. add a failing or contract test before behavior changes where practical
4. make the smallest implementation
5. keep baseline and PostgreSQL smoke green
6. record what was actually verified
7. merge only after explicit approval
8. update roadmap/TODO/handoff when product direction or verified state changes

## Verification Baseline

Core CI remains the source of truth.

Current baseline includes:

- CLI/core verification
- practice focus smoke
- learning path smoke
- curriculum smoke
- user-flow QA smoke
- PWA/serverless smoke on PR #13
- separate PostgreSQL smoke workflow

## Scope Locks

Do not silently:

- replace the shared PWA codebase with separate native apps
- make external AI mandatory for SQL generation
- automatically send data to an AI
- broaden Production Assist external sharing
- claim Cloudflare deployment is verified before real hosted QA
- broaden PostgreSQL/MySQL claims without new proof

## Next Decision Gate

Immediate gate: **PR #13 merge approval after CI readiness**.

After merge, the active execution order is:

1. real Cloudflare hosted deployment + browser/PWA QA
2. AI validation handoff first slice
3. iOS/Android wrapper baseline
