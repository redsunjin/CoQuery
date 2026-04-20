# CoQuery Status Reference

Current truthful product state:

- Version line: v0.7.x stabilization.
- SQLite-first CLI baseline is verified.
- Baseline tests pass with 96 executable tests.
- Explicit write contract is frozen: `insert`, `update`, and `delete` require `--write` and explicit SQL.
- `doctor` reports masked targets, readiness checks, and classified PostgreSQL connection failures.
- `--dry-run`, `--max-affected-rows`, and `--allow-full-table-write` are part of the verified write-safety surface.
- `--db-uri` is the preferred multi-backend connection contract.
- PostgreSQL is experimental for a narrow `schema`, `schema_detail`, `query`, `insert`, `update`, and `delete` smoke slice plus direct `generate join_inner` / `generate join_left` proof.
- MySQL is a stub with a structured placeholder error.
- Natural-language mode is heuristic by default.
- Provider-backed natural routing exists, but remains secondary and experimental.
- JPA entity source introspection exists through `jpa_schema`.
- A compact DB knowledge seed exists at `references/db-knowledge.md`.
- Structured DB/JPA rules exist under `knowledge/` and are queryable through `db_knowledge`.
- DB knowledge coverage and gaps are queryable through `db_knowledge --topic coverage`.
- Normalized schema detail is queryable through `schema_detail`.
- The skill package exposes machine-readable metadata through `references/capabilities.json` and `coquery_agent.py describe`.
- Generate and simple natural-language paths validate basic identifiers against `schema_detail`.
- Built-in join generation can infer one-step join conditions from `schema_detail` foreign keys and constraints when exactly one direct path exists.
- Generation, natural-language, and write-planning paths attach local DB/JPA knowledge context before provider use.

Avoid overclaims:

- Do not call CoQuery a complete multi-database product.
- Do not claim MySQL runtime support.
- Do not claim production-grade natural-language SQL quality.
- Do not broaden PostgreSQL status beyond the smoke-proven command set without a fresh verification result.
- Do not claim JPQL runtime execution or Spring Data JPA integration.
- Do not claim the local DB knowledge seed is a complete offline SQL/JPA knowledge base.
- Do not claim generated SQL is multi-hop relationship-aware, alias-aware, or expression-aware yet.

Recommended readiness checks:

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command doctor --db example.db --format json
python3 main.py --command generate --db example.db --skill select_simple --params '{"table":"users","cols":["id","name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_inner --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' --format json
python3 main.py --command generate --db /tmp/join-test.db --skill join_left --params '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}' --format json
python3 sql_cli/tests/test_core.py
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
python3 main.py --command db_knowledge --dialect sqlite --topic schema
python3 main.py --command db_knowledge --topic coverage
bash scripts/run_postgresql_local_smoke.sh
```
