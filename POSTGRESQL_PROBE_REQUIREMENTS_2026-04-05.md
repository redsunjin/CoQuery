# CoQuery PostgreSQL Probe Requirements

Date: 2026-04-05

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Define the dependency, error, and verification rules for the first real PostgreSQL probe.

This document exists because CoQuery chose PostgreSQL as the first non-SQLite backend target, and the runtime now has both structured PostgreSQL error handling and one verified local smoke path.

## 2. Current truthful state

Observed in the current codebase:

- `sql_cli/db_new.py` detects `postgresql://` URIs
- `sql_cli/db_new.py` returns structured `driver_not_installed` or `connection_failed` errors for PostgreSQL URIs
- `schema` works against a real PostgreSQL database
- `query` works against a real PostgreSQL database
- PostgreSQL is `experimental` for the narrow `schema` and `query` probe paths

## 3. Dependency declaration

The current PostgreSQL probe uses one explicit driver path only:

- Python package: `psycopg[binary]`

Reason:

- modern PostgreSQL driver
- simple local CLI install story
- avoids documenting multiple interchangeable drivers too early

## 4. Installation expectation

Probe environment install:

```bash
python3 -m pip install "psycopg[binary]"
```

Repo smoke runner:

```bash
bash scripts/run_postgresql_local_smoke.sh
```

This is probe infrastructure, not proof of broad production readiness.

## 5. Missing-driver behavior

If the user passes a PostgreSQL URI but the driver is not installed, CoQuery should not crash with a raw traceback.

The public error contract is:

```json
{
  "ok": false,
  "command": "schema",
  "data": {},
  "error": {
    "code": "driver_not_installed",
    "message": "PostgreSQL support requires psycopg[binary]. Install it before using postgresql:// URIs."
  }
}
```

## 6. Connection-failure behavior

If the driver is installed but the database cannot be reached, the command should fail with:

```json
{
  "ok": false,
  "command": "schema",
  "data": {},
  "error": {
    "code": "connection_failed",
    "message": "Failed to connect to the PostgreSQL database."
  }
}
```

Do not expose raw credentials or large tracebacks in the public message.

## 7. Proven probe scope

Currently proven on PostgreSQL:

- `schema`
- `query`

Not proven:

- `insert`
- `update`
- `delete`
- natural-language PostgreSQL behavior
- broader multi-command parity

## 8. Verified smoke command

The current repeatable proof is recorded in:

- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`

Runner:

```bash
bash scripts/run_postgresql_local_smoke.sh
```

## 9. Backend status rule

Use these labels for PostgreSQL:

- `planned`: driver not declared, no runtime path
- `stub`: URI detection exists, but connection is not implemented
- `experimental`: one or more real commands work and at least one verification path is documented
- `working`: multiple commands work with repeatable tests and docs alignment in a less ad hoc environment

Current truthful label:

`experimental`

This is appropriate because real `schema` and `query` commands now succeed, but the environment and coverage are still narrow.

## 10. MySQL policy for now

MySQL should not advance in parallel with PostgreSQL expansion.

Use this temporary policy:

- keep MySQL as `stub` or `planned`
- do not add MySQL dependency instructions yet unless a dedicated slice starts
- do not split effort across both backends before PostgreSQL stabilizes further

## 11. Persona checkpoint

This decision matches the persona review:

- Planner: one backend family is enough to validate real need
- Developer: one driver path keeps implementation pressure smaller
- Manager: two proven commands are still not broad support
- QA: proof is clearer when tied to one smoke runner

## 12. Next follow-up

The next stabilization slice after this document should be:

1. make the PostgreSQL smoke environment less ad hoc
2. decide MySQL status more explicitly
3. only then consider widening PostgreSQL beyond read-oriented probes
