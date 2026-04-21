# CoQuery Todo List

Version: v0.7.x stabilization
Last Updated: 2026-04-21

## Official Next Tasks

These tasks reflect the current stabilization loop.
Do not treat old recovery steps as active work anymore.

Scope decision:

- `main` remains active after closing the reduced cleanup PR unmerged.
- DB/JPA knowledge, JPA source introspection, and Codex skill packaging are retained experimental tracks.
- Provider-backed natural remains secondary and experimental.

### 1. Shared backend selector and DB URI contract

Goal:

- define one connection contract that can describe SQLite, PostgreSQL, and MySQL without overstating support

Open tasks:

- [x] choose the backend selector field or flag
- [x] define the DB URI shape or equivalent connection fields
- [x] define invalid-backend and invalid-URI errors

Current output:

- `BACKEND_CONNECTION_CONTRACT_2026-04-05.md`
- runtime implementation in `main.py` and `sql_cli/db_new.py`

### 2. Driver dependency declaration

Goal:

- document what PostgreSQL and MySQL require before they can be called experimental

Open tasks:

- [x] declare PostgreSQL driver expectations
- [x] declare MySQL driver expectations
- [x] define missing-driver error wording
- [x] define connection-failure error wording

Current output:

- `POSTGRESQL_PROBE_REQUIREMENTS_2026-04-05.md`
- `MYSQL_PROBE_REQUIREMENTS_2026-04-09.md`

### 3. Phase 5 backend status policy

Goal:

- prevent placeholder code from being described as real support

Open tasks:

- [x] define when a backend is `planned`
- [x] define when a backend is `stub`
- [x] define when a backend is `experimental`
- [x] define when a backend is `working`

Current outputs:

- `MULTI_DB_ENTRY_CRITERIA_2026-04-05.md`
- `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`

### 4. First real Phase 5 verification slice

Goal:

- prove one non-SQLite backend path with one real command and one real verification step

Open tasks:

- [x] pick PostgreSQL as the first probe
- [x] add one documented local smoke path
- [x] prove PostgreSQL `schema`
- [x] prove PostgreSQL `schema_detail`
- [x] prove PostgreSQL `query`
- [x] prove PostgreSQL `insert`
- [x] prove PostgreSQL `update`
- [x] prove PostgreSQL `delete`
- [x] prove PostgreSQL direct `generate join_inner`
- [x] prove PostgreSQL direct `generate join_left`

Current output:

- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`
- `scripts/run_postgresql_local_smoke.sh`

Current next step:

- keep GitHub Actions PostgreSQL smoke green and keep the runner portable before broadening any PostgreSQL claim
- keep docs explicit about PostgreSQL driver requirements in the active Python environment
- latest local PostgreSQL smoke re-run succeeded on 2026-04-21
- latest observed `main` runs for `baseline` and `postgresql-smoke` succeeded on 2026-04-20 UTC for commit `e9c98be`

### 5. Verification-gated backend promotion

Goal:

- ensure backend labels change only after proof exists

Open tasks:

- [x] publish the initial Phase 5 verification matrix
- [x] promote PostgreSQL from `stub` to `experimental` only after real proof
- [x] decide whether MySQL remains `stub` or drops to `planned`

Current output:

- `MYSQL_STATUS_DECISION_2026-04-05.md`

### 6. PostgreSQL scope lock

Goal:

- freeze the current truthful PostgreSQL claim before any broader Phase 5 work begins

Open tasks:

- [x] state the currently proven PostgreSQL command set explicitly
- [x] state what is still out of scope
- [x] require a fresh verification slice before broadening PostgreSQL claims

Current output:

- `POSTGRESQL_SCOPE_LOCK_2026-04-07.md`

### 7. Provider registry direction decision

Goal:

- decide whether provider-backed natural remains a sidecar experiment or enters the official active loop

Open tasks:

- [x] decide whether the provider registry is an official roadmap track
- [x] label provider-backed natural as primary or secondary relative to the PostgreSQL track
- [x] truth-align official docs with that decision

Current output:

- `LLM_PROVIDER_REGISTRY_2026-04-07.md`
- `PROVIDER_TRACK_DECISION_2026-04-09.md`
- `STATE_REVIEW_2026-04-09.md`

### 8. Agent reuse package

Goal:

- make the verified CoQuery CLI usable by other Codex sessions as an agent skill

Open tasks:

- [x] create repo-local `skills/coquery-cli` skill package
- [x] add a JSON-oriented agent wrapper for `verify`, `demo`, and single-command `run`
- [x] validate the skill package
- [x] install the skill under `~/.codex/skills/coquery-cli`

Current output:

- `skills/coquery-cli/SKILL.md`
- `skills/coquery-cli/scripts/coquery_agent.py`
- `skills/coquery-cli/references/status.md`
- `skills/coquery-cli/references/commands.md`

### 9. JPA ORM/model support

Goal:

- support Java/JPA projects without pretending JPA is a direct database backend

Open tasks:

- [x] define JPA as an ORM/model track
- [x] add annotation-based source introspection through `jpa_schema`
- [x] keep JPQL runtime execution out of scope until a Java runner proof exists

Current output:

- `JPA_SUPPORT_PLAN_2026-04-10.md`
- `sql_cli/jpa.py`
- `python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json`

### 10. Offline DB knowledge base

Goal:

- reduce LLM/provider calls by keeping local SQL, dialect, and JPA reference knowledge

Open tasks:

- [x] audit whether current DB knowledge is sufficient
- [x] add a compact source-linked DB knowledge seed
- [x] add structured machine-readable dialect rules
- [x] add a deterministic `db_knowledge` lookup command
- [x] add first type/operator/join/constraint knowledge topics
- [x] add an inspectable coverage and gap report
- [x] wire local knowledge lookup into generation before provider calls
- [x] add schema-detail knowledge for columns, indexes, foreign keys, and constraints
- [x] wire schema-detail output into generation and natural-language identifier validation
- [x] use schema-detail relationships and constraints for safer join generation

Current output:

- `DB_KNOWLEDGE_AUDIT_2026-04-10.md`
- `skills/coquery-cli/references/db-knowledge.md`
- `knowledge/dialects/sqlite.json`
- `knowledge/dialects/postgresql.json`
- `knowledge/dialects/mysql.json`
- `knowledge/dialects/jpql.json`
- `knowledge/safety/write_rules.json`
- `knowledge/coverage.json`
- `sql_cli/knowledge_planner.py`
- `python3 main.py --command schema_detail --db example.db --table users --format json`
- `python3 main.py --command generate --db example.db --skill select_simple --params '{"table":"users","cols":["id","name"]}' --format json`
- `python3 main.py --command generate --db /tmp/join-test.db --skill join_inner --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' --format json`
- `python3 main.py --command generate --db /tmp/join-test.db --skill join_left --params '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}' --format json`
- `python3 main.py --command db_knowledge --topic coverage`

## Recently Closed Stabilization Slices

- [x] truth-align top-level status docs
- [x] freeze write-command contract
- [x] define Phase 5 entry criteria
- [x] implement shared DB URI validation and structured backend errors
- [x] define verification matrix and backend status policy
- [x] add docs-example smoke coverage to the baseline test file
- [x] add persona review checkpoint
- [x] add first real PostgreSQL `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` smoke
- [x] package CoQuery as an agent-usable Codex skill
- [x] add first JPA entity source introspection slice
- [x] add first DB knowledge audit and reference seed
- [x] add structured DB/JPA rules and `db_knowledge` lookup
- [x] add DB knowledge coverage reporting
- [x] add local-knowledge-first planning for generation, natural, and write flows
- [x] add normalized schema-detail knowledge for columns, indexes, foreign keys, and constraints
- [x] add schema-detail-backed identifier validation for generation and simple natural-language flows
- [x] add schema-detail-backed direct join inference for built-in join skills
- [x] prove direct PostgreSQL `generate join_inner` and `generate join_left` smoke against a real schema
- [x] re-run local PostgreSQL smoke on 2026-04-21
- [x] add GitHub Actions workflows for baseline verification and PostgreSQL smoke automation
- [x] observe first GitHub Actions `baseline` and `postgresql-smoke` success on 2026-04-12
- [x] observe latest GitHub Actions `baseline` and `postgresql-smoke` success on 2026-04-20 UTC for `main` commit `e9c98be`
- [x] add `doctor` command with masked target reporting and readiness checks
- [x] add write safety guards for `--dry-run`, `--max-affected-rows`, and `--allow-full-table-write`
- [x] add PostgreSQL doctor failure classification for common connection errors
- [x] truth-align top-level docs and skill references with the 96-test baseline and current PostgreSQL driver expectations

## Reference Documents

- `STATUS_AUDIT_2026-04-04.md`
- `STABILIZATION_PLAN_2026-04-04.md`
- `WRITE_COMMAND_CONTRACT_2026-04-05.md`
- `PERSONA_REVIEW_2026-04-05.md`
- `MULTI_DB_ENTRY_CRITERIA_2026-04-05.md`
- `BACKEND_CONNECTION_CONTRACT_2026-04-05.md`
- `POSTGRESQL_PROBE_REQUIREMENTS_2026-04-05.md`
- `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`
- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`
- `MYSQL_STATUS_DECISION_2026-04-05.md`
- `MYSQL_PROBE_REQUIREMENTS_2026-04-09.md`
- `POSTGRESQL_SCOPE_LOCK_2026-04-07.md`
- `LLM_PROVIDER_REGISTRY_2026-04-07.md`
- `PROVIDER_TRACK_DECISION_2026-04-09.md`
- `STATE_REVIEW_2026-04-09.md`

## Verification Baseline

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command generate --db example.db --skill select_simple --params '{"table":"users","cols":["id","name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_inner --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_left --params '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}' --format json
python3 sql_cli/tests/test_core.py
python3 -c "import sql_cli.cli, sql_cli.core, sql_cli.db_new"
python3 skills/coquery-cli/scripts/coquery_agent.py verify
python3 skills/coquery-cli/scripts/coquery_agent.py demo
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
python3 main.py --command db_knowledge --dialect sqlite --topic schema
bash scripts/run_postgresql_local_smoke.sh
```

## Current Direction

Current work is about stabilization and honest phase boundaries.

It is not about:

- broad new feature count
- claiming multi-DB support early
- expanding backend and provider scope in parallel unless the primary and secondary tracks stay explicit
