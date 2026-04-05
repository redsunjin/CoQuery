# CoQuery Todo List

Version: v0.7.x stabilization
Last Updated: 2026-04-05

## Official Next Tasks

These tasks reflect the current stabilization loop.
Do not treat old recovery steps as active work anymore.

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
- [ ] declare MySQL driver expectations
- [x] define missing-driver error wording
- [x] define connection-failure error wording

Current output:

- `POSTGRESQL_PROBE_REQUIREMENTS_2026-04-05.md`

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
- [x] prove PostgreSQL `query`

Current output:

- `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`
- `scripts/run_postgresql_local_smoke.sh`

Current next step:

- reduce local-environment setup friction for the PostgreSQL probe

### 5. Verification-gated backend promotion

Goal:

- ensure backend labels change only after proof exists

Open tasks:

- [x] publish the initial Phase 5 verification matrix
- [x] promote PostgreSQL from `stub` to `experimental` only after real proof
- [ ] decide whether MySQL remains `stub` or drops to `planned`

## Recently Closed Stabilization Slices

- [x] truth-align top-level status docs
- [x] freeze write-command contract
- [x] define Phase 5 entry criteria
- [x] implement shared DB URI validation and structured backend errors
- [x] define verification matrix and backend status policy
- [x] add docs-example smoke coverage to the baseline test file
- [x] add persona review checkpoint
- [x] add first real PostgreSQL `schema` and `query` smoke

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

## Verification Baseline

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 sql_cli/tests/test_core.py
python3 -c "import sql_cli.cli, sql_cli.core, sql_cli.db_new"
```

## Current Direction

Current work is about stabilization and honest phase boundaries.

It is not about:

- broad new feature count
- claiming multi-DB support early
- expanding AI behavior before the current contracts are stable
