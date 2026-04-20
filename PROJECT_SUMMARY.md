# CoQuery - Project Summary v0.7.0

**AI-assisted SQL CLI baseline**
**Current focus: stabilization after CLI repair**

---

## Current Status

```text
Verified on 2026-04-20
- 96 executable baseline tests pass
- SQLite-first command surface works
- package handlers are the canonical runtime path
- explicit write contract is enforced
- shared DB URI contract is implemented
- doctor diagnostics are implemented and verified
- dry-run preview, max-affected-row rollback guards, and full-table write rejection are verified
- PostgreSQL schema, schema_detail, query, insert, update, and delete smoke have succeeded
- PostgreSQL direct `generate join_inner` and `generate join_left` smoke have succeeded against real schema-detail paths
- schema-detail knowledge command is verified for SQLite and the PostgreSQL proof path
- schema-detail-aware identifier validation is verified for generate and simple natural paths
- schema-detail-aware direct join generation is verified for built-in join skills
- GitHub Actions `baseline` and `postgresql-smoke` succeeded on 2026-04-12
```

Scope decision:

- `main` remains the active line.
- PR `#1` for the reduced cleanup branch was closed unmerged.
- DB/JPA knowledge, JPA source introspection, and Codex skill packaging are retained experimental tracks.

---

## Current Harness

- Delivery harness: `Plan -> Review -> Execute -> Verify` in `STABILIZATION_PLAN_2026-04-04.md`
- Runtime harness: `main.py` routes one command into `sql_cli/cli.py`, which fans into `sql_cli/db_new.py`, `sql_cli/core.py`, or `sql_cli/nl_core.py`
- Verification harness: baseline CLI checks, `python3 sql_cli/tests/test_core.py`, `bash scripts/run_postgresql_local_smoke.sh`, and GitHub Actions workflows under `.github/workflows/`

---

## Project Structure

```text
/Users/Agent/ps-workspace/CoQuery/
├── main.py                     # CLI entry point
├── HANDOFF.md                  # Current handoff status
├── PROJECT_SUMMARY.md          # This summary
├── README_COQ.md               # Baseline verification notes
├── STATUS_AUDIT_2026-04-04.md  # Audit of the repaired baseline
├── STABILIZATION_PLAN_2026-04-04.md
└── sql_cli/
    ├── cli.py                  # Canonical command handlers
    ├── core.py                 # SQL generation and validation
    ├── db_new.py               # SQLite-first DB wrapper
    ├── llm_registry.py         # Repo-local provider registry and lightweight clients
    ├── knowledge_planner.py    # Local-knowledge-first planning context
    ├── jpa.py                  # Annotation-based JPA entity source scanner
    ├── nl_core.py              # Lightweight NL processing
    └── tests/test_core.py      # Executable baseline tests
```

---

## Verified Command Surface

- `schema`: list SQLite tables
- `schema_detail`: expose normalized columns, primary keys, foreign keys, indexes, constraints, and SQLite create SQL
- `doctor`: probe readiness and classify common PostgreSQL connection failures without exposing raw secrets
- `query`: execute `SELECT` statements by default; non-`SELECT` requires `--write`
- `generate`: build SQL from built-in skill IDs
- `insert`: requires explicit `INSERT` SQL and `--write`; supports `--dry-run` and `--max-affected-rows`
- `update`: requires explicit `UPDATE` SQL and `--write`; supports `--dry-run` and `--max-affected-rows`
- `delete`: requires explicit `DELETE` SQL and `--write`; supports `--dry-run` and `--max-affected-rows`
- `natural`: uses heuristic intent mapping with local knowledge first and can optionally fall back to a registered provider
- `db_knowledge`: inspect local DB/JPA rules, safety guidance, schema detail, and coverage metadata
- `provider_add`: add or update one repo-local LLM provider profile
- `provider_list`: list registered provider profiles
- `provider_remove`: remove one provider profile
- `provider_test`: test one provider connection
- `jpa_schema`: inspect annotation-based JPA entity source as ORM/model context
- `--db-uri`: preferred shared connection input for non-SQLite backends

---

## Tests

Current executable baseline:

```bash
python3 sql_cli/tests/test_core.py
```

This passes 96 baseline tests covering:

- SQL generation
- SQL validation
- SQLite connection and execution
- CLI handlers
- natural-language processing
- provider registry handlers, local provider skipping, and provider-backed natural fallback
- JPA entity source introspection and CLI routing
- explicit write safety and warning behavior
- DB URI parsing and structured backend errors
- documented CLI example smoke coverage
- mocked PostgreSQL schema, schema_detail, query, insert, update, and delete success paths
- DB/JPA knowledge lookup and coverage reporting
- local DB/JPA knowledge context for generation, natural, and write planning
- normalized schema-detail metadata for SQLite and mocked PostgreSQL paths
- schema-detail-backed table and simple column validation for generate and natural
- schema-detail-backed direct join inference, no-path rejection, ambiguous-path rejection, and explicit join-column validation
- doctor readiness checks and PostgreSQL failure classification
- dry-run write previews, affected-row rollback guards, and full-table write protection

---

## Current Limits

- SQLite is the only broadly verified backend
- PostgreSQL is experimental for the narrow `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` paths plus direct `generate join_inner` / `generate join_left` smoke slices
- MySQL is still a stub, not a working backend
- no transaction layer exists yet; baseline write commands now support `--dry-run` and `--max-affected-rows`
- `doctor` classifies common PostgreSQL failures, but it is still a diagnostic aid rather than proof of complete backend support
- natural-language behavior is lightweight by default; provider-backed quality and backend parity are not broadly proven
- provider-backed natural is currently a secondary experimental track
- generated SQL templates validate basic identifiers and direct foreign-key joins, but are not yet multi-hop relationship-aware, alias-aware, or expression-aware
- JPA support is source introspection only; JPQL runtime execution is not implemented
- GitHub Actions proof currently covers the committed `baseline` and `postgresql-smoke` workflows, not every future runner or environment change
- older docs before the 2026-04-04 repair may overstate completion

---

## Phase Interpretation

| Phase | Status | Interpretation |
|-------|--------|----------------|
| Phase 0 | Complete | CLI baseline repaired |
| Phase 1 | Complete enough | read-oriented SQLite commands work |
| Phase 2 | Complete enough | structured generation works |
| Phase 3 | Complete enough | write contract is explicit, but still baseline-only |
| Phase 4 | Partial | NL path is intentionally lightweight, uses local knowledge first for covered simple requests, and can optionally use a registered provider as fallback |
| Phase 5 | Early experimental | first PostgreSQL `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` proofs exist, but broader support is not implemented |

---

## Quick Start

```bash
# show help
python3 main.py --help

# list schemas
python3 main.py --command schema --db example.db --format json

# inspect normalized schema detail
python3 main.py --command schema_detail --db example.db --table users --format json

# run readiness diagnostics
python3 main.py --command doctor --db example.db --format json

# generate with schema-detail validation
python3 main.py --command generate --db example.db --skill select_simple \
  --params '{"table":"users","cols":["id","name"]}' --format json

# preferred multi-backend form
python3 main.py --command schema --db-uri sqlite:///Users/Agent/ps-workspace/CoQuery/example.db --format json

# run a read query
python3 main.py --command query --db example.db \
  --sql "SELECT * FROM users LIMIT 10" --format json

# generate SQL from a skill
python3 main.py --command generate --db example.db \
  --skill select_simple --format json

# run an explicit write
python3 main.py --command insert --db example.db --write \
  --sql "INSERT INTO users (name, age) VALUES ('alice', 30)"

# preview a write without committing
python3 main.py --command insert --db example.db --write --dry-run \
  --sql "INSERT INTO users (name, age) VALUES ('preview', 20)"

# run the baseline tests
python3 sql_cli/tests/test_core.py
```

---

## Next Steps

1. keep the GitHub Actions `baseline` and `postgresql-smoke` workflows green as the repo-managed proof path
2. keep status docs aligned with observed behavior
3. use the verification matrix before changing any broader multi-DB status claim
4. do not broaden join-generation claims beyond direct schema-detail foreign-key inference without a new proof slice

Current runner improvement:

- `scripts/run_postgresql_local_smoke.sh` now prefers PostgreSQL binaries from `PATH` and only falls back to known Homebrew paths when needed

---

## References

- `main.py`
- `sql_cli/cli.py`
- `sql_cli/db_new.py`
- `sql_cli/llm_registry.py`
- `sql_cli/tests/test_core.py`
- `LLM_PROVIDER_REGISTRY_2026-04-07.md`
- `MYSQL_PROBE_REQUIREMENTS_2026-04-09.md`
- `PROVIDER_TRACK_DECISION_2026-04-09.md`
- `STATUS_AUDIT_2026-04-04.md`
- `STABILIZATION_PLAN_2026-04-04.md`
- `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`
- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`

---

Last Updated: 2026-04-20
Status: SQLite-first baseline verified with `doctor`, explicit write safety guards, experimental PostgreSQL schema, schema_detail, query, insert, update, delete, and direct `generate join_inner` / `generate join_left` proof plus direct schema-detail join inference and verified GitHub Actions baseline / PostgreSQL smoke workflows
