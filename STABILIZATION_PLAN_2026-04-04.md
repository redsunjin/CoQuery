# CoQuery Stabilization Plan

Date: 2026-04-04

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Why this plan exists

The repository is in a better state than the earlier 2026-04-01 audit.

As of this plan:

- `main.py` command routing works again
- the package import path works in the current environment
- the executable baseline test file passes
- the project has a usable SQLite-first command surface

However, the repository is still not in a "broadly complete" state.

The main remaining problem is not total breakage.
It is over-expansion and document drift.

This plan exists to keep the next work focused on stabilization instead of claiming more scope than the code currently supports.

## 2. Current verified baseline

The following were verified directly in the current workspace:

- `python3 main.py --help`
- `python3 main.py --command schema --db example.db --format json`
- `python3 sql_cli/tests/test_core.py`
- `python3 -c "import sql_cli.cli, sql_cli.core, sql_cli.db_new"`

Interpretation:

- SQLite-first runtime is working
- package modules are importable
- baseline tests are executable
- command spine is restored

## 3. Current truthful project status

Use this wording going forward unless the codebase changes again.

### What is complete enough to rely on

- SQLite-first CLI baseline
- `schema`
- `query`
- `generate`
- baseline write command path
- baseline natural-language path
- package-based runtime routing
- executable baseline tests

### What is not yet complete

- trustworthy project status docs
- clearly bounded write contracts
- real PostgreSQL integration
- real MySQL integration
- production-grade NL reasoning
- stable multi-DB contract

## 4. Official active loop

Until explicitly changed, the official active loop should be:

1. stabilize runtime truth
2. align status docs to observed behavior
3. define real Phase 5 scope before adding more code

Do not treat "more features" as the active loop right now.

## 5. Guardrails

- Do not claim PostgreSQL/MySQL support until commands run against real fixtures.
- Do not merge new feature docs that outrun executable behavior.
- Do not widen write capability without explicit safety rules and tests.
- Do not maintain parallel command implementations in both `main.py` and package modules.
- Do not add new AI/NL complexity until existing command contracts are frozen.

## 6. Recommended next slices

### Slice 1. Truth-align status documents

Goal:

- make all top-level docs describe the current verified baseline instead of the aspirational one

Files likely affected:

- `HANDOFF.md`
- `STAGE_STATUS.md`
- `PROJECT_SUMMARY.md`
- `README_COQ.md`

Acceptance:

- no document claims unsupported completion
- SQLite-first baseline is described accurately
- Phase 5 is described as planned, not complete

### Slice 2. Freeze write-command contract

Goal:

- decide whether write commands are permanently raw-SQL based, structured, or hybrid

Questions to answer:

- must `insert/update/delete` require structured params
- is raw SQL still allowed for writes
- what must `--write` mean exactly
- how are affected rows, warnings, and dry-run behavior reported

Acceptance:

- one written contract
- one command shape
- tests reflect that contract

Current output:

- `WRITE_COMMAND_CONTRACT_2026-04-05.md`

### Slice 3. Define real multi-DB entry criteria

Goal:

- stop treating Phase 5 as complete until there is a real gate

Entry criteria should include:

- actual dependency declaration
- one real PostgreSQL test path
- one real MySQL test path or explicit stub declaration
- shared DB URI contract
- error behavior for unavailable drivers

Acceptance:

- a written phase boundary
- no more placeholder completion claims

Current output:

- `MULTI_DB_ENTRY_CRITERIA_2026-04-05.md`

### Slice 4. Freeze shared backend connection contract

Goal:

- choose one primary database input format before Phase 5 implementation begins

Acceptance:

- one written connection contract
- one primary public input shape
- one chosen first backend probe

Current output:

- `BACKEND_CONNECTION_CONTRACT_2026-04-05.md`

### Slice 5. Freeze PostgreSQL probe requirements

Goal:

- choose one PostgreSQL driver path, one bounded error surface, and one first verification command

Acceptance:

- one written PostgreSQL dependency declaration
- one missing-driver message
- one connection-failure message
- one first probe command

Current output:

- `POSTGRESQL_PROBE_REQUIREMENTS_2026-04-05.md`

### Slice 6. Publish Phase 5 verification matrix

Goal:

- define the proof table that will gate backend status claims

Acceptance:

- one written matrix
- explicit backend labels
- one promotion rule for PostgreSQL

Current output:

- `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`

## 7. Suggested phase interpretation

Use this interpretation unless new verification proves more.

### Phase 0-2

Operationally complete enough for local development.

### Phase 3

Partially present, but still needs contract clarification.

### Phase 4

Baseline NL exists, but should be described as assistive and lightweight, not advanced or complete.

### Phase 5

Not complete.
At best, this is an exploratory scaffold toward multi-DB.

## 8. Delivery harness for CoQuery

Use this 4-stage loop for every non-trivial change.

### Plan

- pick one slice only
- define the exact commands that will prove success
- define which status docs must change

### Review

- confirm command ownership stays in package handlers
- confirm whether the slice changes runtime contract, docs, or both
- confirm whether the slice is stabilization or expansion

### Execute

- implement only the selected slice
- keep command routing singular
- keep docs and runtime together

### Verify

Minimum baseline:

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 sql_cli/tests/test_core.py
python3 -c "import sql_cli.cli, sql_cli.core, sql_cli.db_new"
```

Slice-specific verification should add only what changed.

## 9. Recommended order of work

The safest order is:

1. document truth alignment
2. write-command contract decision
3. Phase 5 scope definition
4. then only one real multi-DB implementation slice

Do not jump straight from "SQLite baseline works" to "multi-DB complete."

## 10. Persona review checkpoint

At appropriate phase boundaries, run a short product review through these personas:

- product planner
- developer
- manager
- QA

The first structured review output is:

- `PERSONA_REVIEW_2026-04-05.md`

## 11. Final recommendation

CoQuery no longer needs emergency recovery.

It now needs disciplined stabilization.

The next success condition is not "more capability."
It is:

- truthful docs
- stable command contracts
- one explicit next phase

That is the shortest path to a credible `v0.8` or later release.
