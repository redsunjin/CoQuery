# CoQuery State Review

Date: 2026-04-09

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Review the current product state after:

- SQLite baseline stabilization
- PostgreSQL narrow proof expansion
- local LLM provider registry introduction

This review exists to answer three questions:

1. what is actually working now
2. how far the current project has progressed against its honest goal
3. what the next product direction should be

## 2. Current truthful state

What is clearly proven:

- SQLite-first CLI baseline is working
- explicit write contract is working
- shared DB URI contract is working
- PostgreSQL `schema`, `query`, `insert`, `update`, and `delete` have local smoke proof
- local/provider-backed `natural` routing exists through the provider registry path
- baseline test file currently passes with `39` tests

What is not yet broadly proven:

- broad PostgreSQL support beyond the narrow smoke slice
- MySQL runtime support
- production-grade natural-language SQL quality
- remote provider production readiness
- CI-backed multi-environment repeatability

## 3. Progress estimate

Using the current honest project goal:

- `stable SQLite-first AI-assisted SQL CLI`
- `narrow experimental PostgreSQL`
- `experimental provider-backed natural command`

the project is roughly at:

- baseline stabilization: `90%`
- PostgreSQL experimental track: `80%`
- provider-backed natural track: `45%`
- overall honest product maturity: `75%`

Interpretation:

- the baseline foundation is strong enough to use and extend
- the PostgreSQL path is no longer just a stub, but it is still bounded proof, not broad support
- the provider registry is a promising new direction, but still in an early experimental stage

## 4. Persona review

### Planner

The product direction is now more coherent than before.

The project is no longer claiming vague "AI SQL" completion.
It now has:

- a reliable SQLite baseline
- a bounded PostgreSQL experiment
- an optional provider-backed natural path

The main product risk is not missing features.
The main product risk is splitting attention between:

- backend expansion
- LLM/provider expansion
- contract stability

### Developer

The structure is still manageable.

Good signs:

- CLI entry stays small
- DB wrapper remains narrow
- write contract remains explicit
- provider registry is separated from the DB layer

Main technical caution:

- the provider registry has entered the repo faster than the control-plane docs have fully absorbed it
- if provider work keeps growing without a dedicated official track, the roadmap will drift again

### Manager

The project is now much more honest than it was during the earlier overclaimed stages.

That said, one new management risk exists:

- the repository now contains two meaningful experimental directions at once
  - PostgreSQL expansion
  - provider-backed natural command

This is acceptable only if one remains primary and the other is clearly labelled secondary.

### QA

The quality bar has improved substantially.

Strong points:

- narrow backend claims are tied to smoke proof
- tests exercise contract paths
- repeatable PostgreSQL runner exists

Current QA gap:

- provider registry and provider-backed natural behavior have smoke/test proof, but they are not yet integrated into the same control-plane language as the backend proof track

## 5. Direction judgment

The current direction is good, with one condition:

- do not broaden PostgreSQL and provider-backed natural at the same time without choosing a primary active loop

Recommended interpretation:

- SQLite baseline: primary working product
- PostgreSQL proof track: primary experimental extension
- provider registry: secondary experimental assistive track

This keeps the product understandable.

## 6. Recommended next decisions

The next decisions should be:

1. decide whether provider registry becomes an official roadmap track or remains a sidecar experiment
2. keep PostgreSQL scope frozen at the current narrow proof unless a new explicit verification slice is opened
3. avoid adding more backend breadth until the provider-track decision is written down

## 7. Current recommendation

The next immediate slice should not be another raw feature.

The next immediate slice should be:

1. truth-align the official roadmap and TODO with the new provider registry reality
2. explicitly mark provider-backed natural as experimental and secondary
3. then choose one primary next loop:
   - PostgreSQL parity work
   - or provider-backed natural refinement

Outcome note:

- this recommendation is now recorded in `PROVIDER_TRACK_DECISION_2026-04-09.md`
