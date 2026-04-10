# CoQuery Status Reference

Current truthful product state:

- Version line: v0.7.x stabilization.
- SQLite-first CLI baseline is verified.
- Baseline tests pass with 52 executable tests.
- Explicit write contract is frozen: `insert`, `update`, and `delete` require `--write` and explicit SQL.
- `--db-uri` is the preferred multi-backend connection contract.
- PostgreSQL is experimental for a narrow `schema`, `query`, `insert`, `update`, and `delete` smoke slice.
- MySQL is a stub with a structured placeholder error.
- Natural-language mode is heuristic by default.
- Provider-backed natural routing exists, but remains secondary and experimental.
- JPA entity source introspection exists through `jpa_schema`.
- A compact DB knowledge seed exists at `references/db-knowledge.md`.
- Structured DB/JPA rules exist under `knowledge/` and are queryable through `db_knowledge`.

Avoid overclaims:

- Do not call CoQuery a complete multi-database product.
- Do not claim MySQL runtime support.
- Do not claim production-grade natural-language SQL quality.
- Do not broaden PostgreSQL status beyond the smoke-proven command set without a fresh verification result.
- Do not claim JPQL runtime execution or Spring Data JPA integration.
- Do not claim the local DB knowledge seed is a complete offline SQL/JPA knowledge base.

Recommended readiness checks:

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 sql_cli/tests/test_core.py
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
python3 main.py --command db_knowledge --dialect sqlite --topic schema
bash scripts/run_postgresql_local_smoke.sh
```
