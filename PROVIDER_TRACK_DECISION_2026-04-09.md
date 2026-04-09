# CoQuery Provider Track Decision

Date: 2026-04-09

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Decide how the provider registry and provider-backed `natural` command should be represented in the official product direction.

This document exists because the repository now contains both:

- a narrow PostgreSQL proof track
- a working provider registry path for optional `natural` routing

Without an explicit decision, the roadmap can drift into advancing both tracks at once.

## 2. Decision

Provider-backed `natural` is now an official secondary experimental track.

It is not the primary experimental track.

The primary experimental track remains:

- PostgreSQL proof and scope control

The secondary experimental track is:

- provider registry
- provider connectivity testing
- provider-backed `natural` routing

## 3. Why this is the right label

Current code and proof already justify treating the provider path as more than a hidden sidecar:

- provider registration exists
- provider connection testing exists
- provider-backed `natural` routing exists
- baseline tests cover provider registry handlers and provider-backed `natural`
- a local Ollama smoke path is documented

At the same time, the provider path is not ready to replace the primary roadmap focus:

- broad SQL quality is not proven
- backend parity is not proven
- remote provider production readiness is not proven
- the main experimental backend story is still PostgreSQL

## 4. Official wording rules

Top-level docs should now describe the project as:

- SQLite-first baseline: working
- PostgreSQL: primary experimental extension
- provider-backed `natural`: secondary experimental extension

Top-level docs should not:

- describe provider-backed `natural` as production-ready
- imply provider-backed behavior is broadly verified across schemas or backends
- broaden PostgreSQL and provider work in parallel without a new explicit loop decision

## 5. Product interpretation

This keeps the product understandable:

- the baseline remains the main usable product
- PostgreSQL remains the main experimental systems track
- provider-backed natural remains visible, but intentionally secondary

## 6. Next follow-up

The next loop should keep this split explicit:

1. maintain PostgreSQL scope discipline unless a new proof slice is opened
2. keep provider-backed natural labelled experimental and secondary
3. choose only one primary implementation loop before adding more breadth
