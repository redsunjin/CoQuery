# CoQuery MySQL Probe Requirements

Date: 2026-04-09

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Define the dependency and promotion rules for the first future MySQL probe without overstating current runtime support.

This document exists because CoQuery already recognizes `mysql://` URIs, but still returns a bounded placeholder error instead of a real MySQL connection path.

## 2. Current truthful state

Observed in the current codebase:

- `sql_cli/db_new.py` detects `mysql://` URIs
- shared `--db-uri` validation works for MySQL-shaped URIs
- runtime execution still returns `unsupported_backend`
- no real MySQL `schema`, `query`, or write commands are implemented
- MySQL remains `stub`

## 3. Dependency declaration

If a dedicated MySQL implementation slice is opened, the first driver path should be:

- Python package: `PyMySQL`

Reason:

- pure-Python install story
- lower bootstrap friction for a small CLI probe
- one explicit driver path keeps the first MySQL slice narrow

This is a dependency declaration only.
The current runtime does not import or require `PyMySQL` yet.

## 4. Installation expectation

Future probe environment install:

```bash
python3 -m pip install PyMySQL
```

This does not imply current MySQL support.
It only records the first dependency path CoQuery should use if a real MySQL probe begins.

## 5. Current public runtime behavior

Today, a MySQL URI should fail with the existing placeholder contract:

```json
{
  "ok": false,
  "command": "schema",
  "data": {},
  "error": {
    "code": "unsupported_backend",
    "message": "MySQL support is not implemented yet."
  }
}
```

This is truthful for the current code because no MySQL driver path is wired into runtime execution yet.

## 6. Required behavior before MySQL can become experimental

Before MySQL can move beyond `stub`, all of the following must be true:

1. `connect_mysql()` uses one declared driver path
2. missing-driver failures return a structured `driver_not_installed` error
3. unreachable targets return a structured `connection_failed` error
4. at least one real command works against a real MySQL target
5. one repeatable smoke path is documented in the repo

## 7. Not proven

The following are still unproven for MySQL:

- connection success
- schema inspection
- query execution
- insert, update, and delete execution
- natural-language behavior
- smoke automation

## 8. Backend status rule

Use these labels for MySQL:

- `planned`: no meaningful runtime boundary exists
- `stub`: URI validation or placeholder runtime behavior exists, but real execution does not
- `experimental`: at least one real command works and one verification path is documented
- `working`: multiple commands work with repeatable proof and aligned docs

Current truthful label:

`stub`

That remains correct because CoQuery can recognize MySQL and fail predictably, but cannot connect to a real MySQL target yet.

## 9. Persona checkpoint

This decision matches the persona review:

- Planner: keeps MySQL behind the already-proven PostgreSQL slice
- Developer: chooses one future driver path instead of multiple interchangeable options
- Manager: avoids implying MySQL support before proof exists
- QA: preserves a stable placeholder error until a real proof track starts

## 10. Next follow-up

The next MySQL slice should be:

1. implement `connect_mysql()` with the declared driver path
2. add structured missing-driver and connection-failure errors
3. add one repo-managed MySQL smoke path before any status promotion
