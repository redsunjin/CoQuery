# CoQuery Write Command Contract

Date: 2026-04-05

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Freeze the baseline contract for write-capable commands before widening the product surface.

This document exists because CoQuery currently has working write handlers, but the behavior is still under-specified.

The goal is not to maximize flexibility yet.
The goal is to make write behavior understandable, reviewable, and testable.

## 2. Current baseline write surface

Current command names:

- `insert`
- `update`
- `delete`
- `query` with non-`SELECT` SQL and explicit `--write`

Current runtime shape after implementation:

- commands can accept raw SQL
- default write SQL fallbacks have been removed
- write behavior now uses one stable baseline envelope

## 3. Contract decision

The baseline write contract is:

### Mode

Raw-SQL baseline, but narrow:

- raw SQL remains allowed for the current baseline
- parameter binding is allowed only as a JSON array of SQL parameters
- implicit default write SQL is not allowed

### Safety requirement

Every write-capable command must require explicit write intent.

That means:

- `--write` is mandatory for any state-changing operation
- without `--write`, the command must fail with a structured error
- read-looking commands must never trigger writes implicitly

### Output envelope

Every write command should return one consistent envelope:

```json
{
  "ok": true,
  "command": "insert",
  "data": {
    "affected_rows": 1,
    "warnings": [],
    "safety_level": "medium"
  },
  "error": null
}
```

Failure:

```json
{
  "ok": false,
  "command": "delete",
  "data": {},
  "error": {
    "code": "write_flag_required",
    "message": "DELETE requires explicit --write confirmation."
  }
}
```

## 4. Required command behavior

### `insert`

Allowed:

- explicit insert SQL
- explicit parameter list when supported by the handler

Required:

- `--write`
- explicit `INSERT` SQL
- structured affected-row reporting

### `update`

Allowed:

- explicit update SQL

Required:

- `--write`
- explicit `UPDATE` SQL
- affected-row reporting
- warning when no `WHERE` clause exists
- elevated safety level for full-table updates

### `delete`

Allowed:

- explicit delete SQL

Required:

- `--write`
- explicit `DELETE` SQL
- affected-row reporting
- warning when no `WHERE` clause exists
- elevated safety level for full-table deletes

## 5. Safety levels

Use these baseline levels:

- `low`: explicitly targeted change with a clear filter
- `medium`: explicit write with some ambiguity
- `high`: full-table or destructive-looking write without a clear narrowing condition

This does not block all high-risk writes yet, but it must surface them clearly.

## 6. Structured error codes

Use these first error codes:

- `write_flag_required`
- `invalid_write_sql`
- `execution_error`
- `unsupported_write_mode`
- `database_connection_failed`

Avoid returning raw exception text as the only failure surface.

## 7. Implemented behavior snapshot

The implemented baseline now does the following:

- `insert`, `update`, and `delete` fail without `--write`
- `insert`, `update`, and `delete` fail without explicit SQL
- handler and SQL verb mismatch fails with `invalid_write_sql`
- full-table `update` and `delete` return a warning and `high` safety level
- success returns `affected_rows`, `warnings`, and `safety_level`

## 8. Non-goals for this slice

- no transaction orchestration yet
- no rollback preview system yet
- no dry-run planner yet
- no cross-database write abstraction yet
- no natural-language writes by default

## 9. Testing requirements

Completed in the current baseline:

- one insert success test
- one update success test
- one delete success test
- one missing `--write` failure test
- one full-table warning test
- one query write-flag failure test
- one handler and SQL mismatch failure test

The tests should run against disposable SQLite fixtures, not the main sample DB only.

## 10. Product interpretation

This contract means:

- CoQuery supports baseline write operations
- but only as explicit, bounded, test-backed commands
- and not yet as a polished end-user automation flow

## 11. Next follow-up

The next implementation slice after this document should be:

1. define unsupported-driver behavior for PostgreSQL/MySQL placeholders
2. add docs-example smoke coverage
3. define real Phase 5 entry criteria
