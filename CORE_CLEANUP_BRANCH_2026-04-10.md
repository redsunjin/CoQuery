# CoQuery Core Cleanup Branch

Date: 2026-04-10

Branch:

- `cleanup/core-stabilization-2026-04-10`

Base:

- `178c823` `Expand PostgreSQL proof to update`

## Purpose

This branch is a reduced CoQuery core line for reviewing the contamination scope documented on `main`.

It intentionally keeps the repaired SQLite-first CLI baseline and the narrow PostgreSQL proof track, while excluding later optional expansion tracks.

## Kept In Scope

- SQLite-first CLI baseline
- explicit write contract for `insert`, `update`, and `delete`
- shared `--db-uri` contract
- MySQL placeholder/stub behavior
- PostgreSQL narrow proof for:
  - `schema`
  - `query`
  - `insert`
  - `update`
  - `delete`
- baseline docs and verification matrix aligned to that scope

## Excluded From This Cleanup Branch

- provider registry
- provider-backed natural-language routing
- JPA source introspection
- Codex skill packaging
- DB knowledge lookup and coverage layer
- local-knowledge-first planner

These excluded tracks are preserved on:

- `main`
- `coquery-expansion-2026-04-10`

## Verification

Current reduced baseline:

```bash
python3 sql_cli/tests/test_core.py
```

Expected result:

```text
35/35 executable baseline tests pass
```

Optional local PostgreSQL proof:

```bash
bash scripts/run_postgresql_local_smoke.sh
```

## Review Use

Use this branch to decide whether the intended CoQuery product boundary should stay small:

- core SQLite CLI
- explicit write safety
- narrow PostgreSQL proof

If provider, JPA, skill packaging, or DB knowledge should become official CoQuery roadmap items, re-apply those tracks from `coquery-expansion-2026-04-10` after explicit review.
