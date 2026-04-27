# CoQuery Baseline Verification

Date: 2026-04-23

## Result

```text
96/96 executable baseline tests pass
SQLite-first CLI verified
Explicit write contract verified
Shared DB URI contract verified
Doctor command verified
PostgreSQL schema, schema_detail, query, insert, update, and delete smoke verified
PostgreSQL select/count generation smoke verified
PostgreSQL direct join-generation smoke verified
PostgreSQL write-safety guard smoke verified
Local PostgreSQL smoke runner re-verified on 2026-04-22
Local DB/JPA knowledge-first generation planning verified
Schema-detail knowledge command verified
Schema-detail-aware generation and natural identifier validation verified
Schema-detail-aware direct join generation verified
Dry-run preview and max-affected-row rollback guards verified
Full-table write guard verified
PostgreSQL doctor classification verified for common connection failures
GitHub Actions baseline and PostgreSQL smoke workflows last recorded as verified on 2026-04-23 UTC for `main` commit `022d89f`
Public GitHub repository verified
```

Scope decision:

- current `main` is retained as the active line
- reduced cleanup PR `#1` was closed unmerged
- DB/JPA knowledge, JPA source introspection, and Codex skill packaging stay in scope as retained experimental tracks

## Verified Commands

- `schema`
- `schema_detail`
- `doctor`
- `query`
- `generate`
- `insert`
- `update`
- `delete`
- `natural`
- `jpa_schema`
- `db_knowledge`
- `provider_add`
- `provider_list`
- `provider_remove`
- `provider_test`

## Support Matrix

| Area | Status | Notes |
|------|--------|-------|
| SQLite CLI path | Working | current verified runtime |
| PostgreSQL | Experimental (narrow read + write + limited generate) | local smoke proof succeeded for `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`, write-safety guards, schema-detail-validated `generate select_simple` / `generate count_simple`, and direct join generation; latest local runner pass on 2026-04-22 |
| MySQL | Stub | returns structured placeholder error |
| Write contract | Working baseline | `--write` plus explicit SQL is enforced |
| Dry-run preview | Working baseline | `insert`, `update`, `delete`, and write-mode `query` can return affected rows without committing changes |
| Affected-row guard | Working baseline | `--max-affected-rows` rolls back writes that touch more rows than expected |
| Full-table write guard | Working baseline | `update`, `delete`, and write-mode `query` without `WHERE` fail closed unless `--allow-full-table-write` is provided |
| DB URI contract | Working baseline | `--db-uri` is available and validated |
| Doctor diagnostics | Working baseline | `doctor` reports readiness plus classified PostgreSQL connection failures |
| Phase 5 verification matrix | Working baseline | backend promotion is now proof-gated |
| PostgreSQL schema smoke | Working baseline | initial local proof recorded on 2026-04-05; latest runner pass on 2026-04-22 |
| PostgreSQL select/count generation smoke | Working baseline | local proof recorded on 2026-04-22 for schema-detail-validated `generate select_simple` and `generate count_simple` plus generated SQL execution |
| PostgreSQL direct join generation smoke | Working baseline | initial local proof recorded on 2026-04-11 for direct `generate join_inner` and `generate join_left` slices; latest runner pass on 2026-04-22 |
| PostgreSQL query smoke | Working baseline | initial local proof recorded on 2026-04-05; latest runner pass on 2026-04-22 |
| PostgreSQL insert smoke | Working baseline | initial local proof recorded on 2026-04-05; latest runner pass on 2026-04-22 |
| PostgreSQL update smoke | Working baseline | initial local proof recorded on 2026-04-07; latest runner pass on 2026-04-22 |
| PostgreSQL delete smoke | Working baseline | initial local proof recorded on 2026-04-08; latest runner pass on 2026-04-22 |
| PostgreSQL write-safety smoke | Working baseline | local proof recorded on 2026-04-22 for dry-run rollback, max-affected rollback, and full-table write rejection |
| Docs example smoke | Working baseline | key documented CLI examples are exercised in tests |
| Natural language | Baseline only | simple covered requests use local knowledge first; optional provider path remains fallback |
| JPA | Source introspection only | `jpa_schema` scans annotation-based entity source; JPQL runtime execution is not implemented |
| DB knowledge planner | Seed | generation, natural, and write planning attach local dialect/safety context |
| Schema detail knowledge | Seed | `schema_detail` exposes normalized columns, keys, indexes, constraints, and SQLite create SQL for verified paths |
| Schema validation | Seed | `generate` and simple `natural` requests validate table and simple column identifiers against `schema_detail` |
| Direct join generation | Working baseline | `generate` can infer one-step join `ON` clauses from schema-detail foreign keys; no-path and ambiguous joins fail closed |
| CI automation | Working baseline | GitHub Actions `baseline` and `postgresql-smoke` last recorded successfully on 2026-04-23 UTC for `main` commit `022d89f` |
| GitHub log demo | Available | public repository can run `baseline` and `postgresql-smoke` manually from GitHub Actions |

## Verification Commands

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command doctor --db example.db --format json
python3 main.py --command generate --db example.db --skill select_simple --params '{"table":"users","cols":["id","name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_inner --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' --format json
python3 main.py --command schema --db-uri sqlite:///Users/Agent/ps-workspace/CoQuery/example.db --format json
python3 sql_cli/tests/test_core.py
bash scripts/run_postgresql_local_smoke.sh
```

## Notes

- `query` is read-only unless `--write` is set
- dedicated `insert`, `update`, and `delete` handlers require `--write` and explicit SQL
- `insert`, `update`, `delete`, and write-mode `query` accept `--dry-run` to roll back after execution
- `insert`, `update`, `delete`, and write-mode `query` accept `--max-affected-rows` to fail closed on unexpected row counts
- full-table `update`, `delete`, and write-mode `query` statements fail closed unless `--allow-full-table-write` is provided
- `--db-uri` is preferred for future multi-backend commands
- `doctor` exposes masked targets, readiness checks, and structured connection failure codes
- `schema_detail` provides normalized schema metadata for agent-side DB knowledge use
- `generate` and simple `natural` requests can reject unknown tables before returning local SQL
- the local PostgreSQL smoke runner now proves schema-detail-validated `generate select_simple` and `generate count_simple`, then executes the generated SQL
- `generate` can auto-build direct join `ON` clauses from schema detail when both tables are inspectable
- the local PostgreSQL smoke runner now proves direct `generate join_inner` and `generate join_left` slices against a real PostgreSQL schema
- the local PostgreSQL smoke runner now proves `--dry-run`, `--max-affected-rows`, and full-table write rejection against a real PostgreSQL target
- the local PostgreSQL smoke runner was re-run successfully on 2026-04-22
- explicit join `ON` clauses are still allowed, but qualified table/column references are validated against schema detail when available
- `natural` defaults to simple fixed SQL patterns
- `natural --provider-name ...` skips provider calls for simple covered requests and can route complex requests through a registered provider
- provider-backed natural is experimental and secondary to the PostgreSQL proof track
- `jpa_schema --jpa-project ...` can provide entity model context for Java/JPA projects
- the PostgreSQL smoke runner checks `PATH` for PostgreSQL binaries before falling back to known Homebrew paths
- `doctor` can classify common PostgreSQL connection failures such as `auth_failed`, `database_not_found`, `host_unreachable`, `connection_refused`, `timeout`, and `ssl_error`
- GitHub Actions workflow files exist at `.github/workflows/baseline.yml` and `.github/workflows/postgresql-smoke.yml`
- the PostgreSQL smoke workflow uses an external PostgreSQL service URI, while the local smoke runner still supports managed local startup
- GitHub Actions `baseline` and `postgresql-smoke` first succeeded on 2026-04-12 in PR `#3`
- GitHub Actions `baseline` and `postgresql-smoke` were last recorded successful on 2026-04-23 UTC for `main` commit `022d89f`
- use `USAGE_AND_DEMO.md` for local CLI usage and GitHub Actions demo steps

Version: v0.7.0
Last Updated: 2026-04-23
Status: Baseline verified with `doctor`, explicit write safety guards, experimental PostgreSQL schema, schema_detail, query, insert, update, delete, write-safety guard, schema-detail-validated `generate select_simple` / `generate count_simple`, and direct `generate join_inner` / `generate join_left` proof, local DB knowledge-first planning, schema-detail-aware identifier validation, direct schema-detail join inference, and verified GitHub Actions baseline / PostgreSQL smoke workflows
Reference: `PHASE5_VERIFICATION_MATRIX_2026-04-05.md`
Smoke Result: `POSTGRESQL_LOCAL_SMOKE_2026-04-05.md`
