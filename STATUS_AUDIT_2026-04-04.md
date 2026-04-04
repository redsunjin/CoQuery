# CoQuery Status Audit

Date: 2026-04-04
Workspace: `/Users/Agent/ps-workspace/CoQuery`

## Summary

Initial audit found that the repository documents claimed Phase 4 and Phase 5 were complete while the codebase was only partially aligned with that state.

That baseline has now been repaired:

1. `main.py` delegates to `sql_cli/*` package handlers
2. `sql_cli/db_new.py` accepts SQLite paths correctly
3. the canonical test command passes

Remaining caution:

- docs still overstate overall maturity
- PostgreSQL/MySQL are still placeholders, not working integrations

## Working Tree

Uncommitted changes already present before this audit:

- `ANALYSIS_REPORT_2026-04-01.md`
- `PROJECT_SUMMARY.md`
- `sql_cli/tests/fixtures/sample.db`

## What Was Verified

### `main.py` commands

Verified directly:

- `schema` works against `example.db`
- `query` works for a basic `SELECT`
- `generate` returns SQL
- `insert` works against a copied SQLite DB
- `update` works against a copied SQLite DB
- `delete` works against a copied SQLite DB
- `natural` returns intent + SQL

Notes:

- `main.py` now routes through package handlers.
- write commands accept raw SQL and still fall back to simple defaults when SQL is omitted.
- `generate` now emits normalized SQL such as `SELECT * FROM USERS`.

### Tests

Current behavior after repair:

- `python3 -m sql_cli.tests.test_core` passes
- `python3 sql_cli/tests/test_core.py` also passes

Issues that were repaired:

- test import path assumptions
- `count_simple` vs `count`
- `CoQueryDB("example.db")` constructor mismatch

## Code-Level Findings

### 1. `sql_cli/db_new.py` constructor contract was broken for current callers

Current signature:

```python
CoQueryDB(db_type='sqlite', db_uri=None)
```

Current callers use:

```python
CoQueryDB("example.db")
```

That sets:

- `type = "example.db"`
- `uri = None`

This has been fixed so SQLite file paths now connect correctly.

### 2. `sql_cli/cli.py` is now the canonical runtime path

`main.py` now delegates to package handlers instead of maintaining a second implementation.

### 3. `main.py` and `sql_cli/cli.py` were divergent implementations

`main.py`:

- now acts as a thin CLI entry point
- delegates to package handlers

`sql_cli/cli.py`:

- uses `CoQueryDB`
- reflects the intended multi-DB direction
- provides the current working command handlers

This has been standardized on the package handler path.

### 4. `sql_cli/tests/test_core.py` has been aligned with implementation

The baseline tests now validate:

- SQL generation
- SQL validation
- DB connection and schema access
- package command handlers
- NL processing

### 5. `sql_cli/nl_core.py` printed on import

Import side effect:

```python
print("✅ NL Processing Clean Created")
```

This has been removed.

### 6. Documentation is ahead of reality

These files currently overstate completion:

- `PROJECT_SUMMARY.md`
- `STAGE_STATUS.md`
- `HANDOFF.md`
- `README_COQ.md`

They should not be treated as authoritative until runtime and tests are reconciled.

## Practical Current Status

If work resumes now, the safest interpretation is:

- SQLite-only CLI baseline is working
- package handlers are the real runtime path
- automated baseline tests are passing
- docs are still not reliable indicators of Phase 5 completeness

## Recommended Next Work Order

1. Update the remaining status docs to match the repaired baseline
2. Decide whether write operations should remain raw-SQL based or become structured contracts
3. Define the actual Phase 5 scope before claiming multi-DB support
4. Implement PostgreSQL/MySQL only after tests and interfaces are specified

## Suggested Baseline Goal

Baseline now reached:

- `python3 -m sql_cli.tests.test_core` passes
- `main.py` and package handlers share the same logic path
- one working command set matches observed behavior
