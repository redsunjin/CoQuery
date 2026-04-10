# CoQuery Scope Decision

Date: 2026-04-10

## Decision

Keep current `main` as the active CoQuery line.

Do not merge the reduced cleanup PR:

- PR: `#1` `Review reduced CoQuery core stabilization branch`
- Branch: `cleanup/core-stabilization-2026-04-10`
- Outcome: closed unmerged

## Reason

The reduced cleanup branch is useful as a comparison point, but adopting it would remove work that is now considered important to preserve:

- DB/JPA knowledge lookup and coverage
- local-knowledge-first planning
- JPA source introspection
- Codex skill packaging

The project direction is therefore:

- keep the current SQLite-first baseline
- keep the narrow PostgreSQL proof track
- keep the DB/JPA knowledge layer
- keep JPA and skill packaging as experimental but retained tracks
- keep provider-backed natural as secondary and experimental

## Branch Roles

`main`:

- active line
- includes current baseline plus retained experimental tracks

`coquery-expansion-2026-04-10`:

- archive/reference branch for the current expanded state

`cleanup/core-stabilization-2026-04-10`:

- reduced-core comparison branch
- not the active direction unless a future decision reverses this one

## Guardrails

Do not remove these tracks from `main` without a new explicit decision:

- `knowledge/`
- `sql_cli/dialect_rules.py`
- `sql_cli/knowledge_planner.py`
- `sql_cli/jpa.py`
- `skills/coquery-cli/`

Do not broaden claims beyond current proof:

- PostgreSQL remains experimental and limited to the smoke-proven `schema`, `query`, `insert`, `update`, and `delete` paths.
- MySQL remains a stub.
- JPA remains source introspection only.
- DB knowledge remains a local seed and planning layer, not a complete offline SQL/JPA knowledge base.
- Provider-backed natural remains secondary and experimental.

## Next Work

The next useful implementation step is schema-detail knowledge:

- normalized columns
- indexes
- foreign keys
- constraints
- generation checks that use this schema detail before provider fallback
