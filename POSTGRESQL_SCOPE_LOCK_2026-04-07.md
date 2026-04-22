# CoQuery PostgreSQL Scope Lock

Date: 2026-04-22

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Freeze the current truthful PostgreSQL boundary before widening Phase 5 further.

This document exists so the project does not drift from:

- one verified SQLite-first baseline
- one narrow PostgreSQL experimental slice
- one explicit gate before broader backend claims

## 2. Current PostgreSQL scope

As of 2026-04-22, the PostgreSQL slice is:

- status: `experimental`
- proven commands: `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`
- proven write-safety guard slices: `--dry-run` rollback, `--max-affected-rows` rollback, and full-table write rejection
- proven generation slices: schema-detail-validated `generate select_simple` and `generate count_simple`, plus direct `generate join_inner` and `generate join_left` inference when exactly one direct foreign-key path exists
- proof path: `bash scripts/run_postgresql_local_smoke.sh`
- proof note: `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`

What this means:

- PostgreSQL is no longer just a placeholder
- PostgreSQL is still not broad backend support
- the current proof is enough for a narrow experimental claim only

## 3. What is explicitly out of scope now

Do not treat these as current PostgreSQL support:

- natural-language PostgreSQL execution
- broad PostgreSQL `generate` parity beyond the proven `select_simple`, `count_simple`, `join_inner`, and `join_left` slices
- multi-hop or alias-aware join generation
- transaction handling
- parity with the SQLite baseline
- broad multi-DB completion claims

## 4. Current project rule

Until a new verification slice is opened, keep PostgreSQL language limited to:

- `experimental`
- `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` are proven
- PostgreSQL write-safety guard slices are proven for `--dry-run`, `--max-affected-rows`, and full-table write rejection
- `generate select_simple` and `generate count_simple` are proven through real schema-detail validation and generated SQL execution
- direct `generate join_inner` and `generate join_left` slices are proven through real schema-detail introspection
- broader PostgreSQL support is not proven

Do not:

- call PostgreSQL `working`
- imply full write parity
- imply full PostgreSQL generation parity
- imply multi-DB completion
- widen docs from the proven slice to generic PostgreSQL support

## 5. Unlock condition for the next PostgreSQL slice

The next widening slice may start only when all of the following are true:

1. the current smoke runner remains repeatable
2. docs still match the current narrow proof
3. the next command family is named explicitly in advance
4. the new command gets both runtime proof and recorded verification

Recommended order:

1. keep the runner easy to rerun
2. decide whether the current proof set is enough for this phase
3. only then consider broader PostgreSQL parity

## 6. Persona checkpoint

This scope lock matches the project personas:

- Planner: prevents ambition from replacing proof
- Developer: keeps Phase 5 pressure small and bounded
- Manager: avoids overstating support from one successful smoke path
- QA: preserves a clear contract for what must be re-proven before expansion

## 7. Current recommendation

The next immediate work is not broader PostgreSQL functionality.

The next immediate work is:

1. keep the PostgreSQL probe harness stable
2. keep docs aligned with the current proof boundary
3. open a new widening slice only with an explicit verification target
