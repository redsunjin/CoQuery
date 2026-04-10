# DB Knowledge Seed

This is a compact offline reference for CoQuery agents. Use it before asking an LLM for common SQL/JPA decisions.

## Coverage Label

Current level: `schema_detail_seed`

This file is enough for basic routing, safety decisions, deterministic lookup, normalized schema-detail lookup, and simple local-first planning. It is not enough for full SQL dialect generation, query optimization, or JPQL runtime execution.

For a machine-readable status, run:

```bash
python3 main.py --command db_knowledge --topic coverage
```

## Official Sources

- SQLite SQL language reference: https://www.sqlite.org/lang.html
- PostgreSQL current SQL commands reference: https://www.postgresql.org/docs/current/sql-commands.html
- MySQL 8.4 SQL statements reference: https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html
- Jakarta Persistence 3.2 specification: https://jakarta.ee/specifications/persistence/3.2/jakarta-persistence-spec-3.2

## General SQL Safety Rules

- Treat `SELECT` as read-only unless it includes dialect-specific side effects or non-query wrappers.
- Treat `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `MERGE`, `CALL`, and DDL/DCL/TCL commands as write or administrative operations.
- Require explicit user intent and `--write` for state-changing commands.
- Flag `UPDATE` without `WHERE` as high risk.
- Flag `DELETE` without `WHERE` as high risk.
- Prefer explicit columns over `SELECT *` for generated queries.
- Prefer parameterized values over literal interpolation.
- Never use natural-language output directly for writes without explicit SQL review.

## CoQuery Runtime Boundaries

SQLite:

- Status: working baseline.
- Connection forms: file path or `sqlite://...`.
- Current schema query: `SELECT name FROM sqlite_master WHERE type='table' ORDER BY name`.
- Current schema-detail query path: `schema_detail` combines PRAGMA table, foreign-key, index, and `sqlite_master` metadata.
- Current command coverage: `schema`, `schema_detail`, `query`, `generate`, `insert`, `update`, `delete`, `natural`.

PostgreSQL:

- Status: experimental narrow smoke.
- Connection form: `postgresql://...`.
- Driver path: `psycopg`.
- Current schema query uses `information_schema.tables` for `public` base tables.
- Current schema-detail query path uses `information_schema` plus `pg_catalog` metadata.
- Current proven commands: `schema`, `schema_detail`, `query`, `insert`, `update`, `delete`.
- Do not claim broad PostgreSQL support beyond the smoke-proven commands.

MySQL:

- Status: stub.
- Connection form recognition exists for `mysql://...`.
- Runtime execution is not implemented.
- Use official MySQL SQL statement docs for future planning only.

JPA:

- Status: experimental source introspection.
- Current command: `jpa_schema`.
- JPA is an ORM/model layer, not a direct database backend.
- JPQL operates over entity names and persistent attributes, not raw table/column names.
- JPQL statement types are select, update, and delete; entity inserts normally go through persistence operations, not JPQL insert.
- Field access and property access depend on where mapping annotations are placed.
- Do not claim JPQL execution, Criteria execution, Spring Data JPA support, or Java persistence-unit runtime support.

## Dialect Decision Matrix

| Concern | SQLite | PostgreSQL | MySQL | JPA/JPQL |
|---------|--------|------------|-------|----------|
| CoQuery status | working | experimental | stub | source introspection |
| Runtime target | DB file | DB server | planned DB server | Java persistence unit |
| Query language | SQL | SQL | SQL | JPQL/Criteria |
| Main model names | tables/columns | tables/columns | tables/columns | entities/attributes |
| Current schema source | `sqlite_master`, PRAGMA detail | `information_schema`, `pg_catalog` | not implemented | Java annotations |
| Current write gate | `--write` | `--write` | not supported | not supported |

## Retrieval Guidance For Agents

Use this order:

1. Read `status.md` to avoid overclaims.
2. Read `commands.md` for exact runnable command shapes.
3. Read this file for dialect/JPA boundaries.
4. Use an LLM/provider only if the needed rule is absent, the request is complex, or the user asks for generative help.

Useful deterministic lookup topics:

```bash
python3 main.py --command db_knowledge --dialect sqlite --topic schema
python3 main.py --command db_knowledge --dialect sqlite --topic schema_detail
python3 main.py --command schema_detail --db example.db --table users --format json
python3 main.py --command db_knowledge --dialect postgresql --topic types
python3 main.py --command db_knowledge --dialect mysql --topic constraints
python3 main.py --command db_knowledge --dialect jpql --topic joins
python3 main.py --command db_knowledge --topic write_safety
python3 main.py --command db_knowledge --topic coverage
```

## Missing Knowledge Still Needed

- schema-detail-aware generated SQL and identifier validation
- deeper dialect-specific generation templates
- per-dialect syntax snippets for common commands
- per-dialect placeholder conventions by Python driver
- date/time function matrix
- string function matrix
- pagination and limit/offset differences
- upsert/merge differences
- transaction and isolation rules
- identifier quoting rules with examples
- deeper schema introspection for views, composite constraints, generated columns, and backend-specific metadata
- JPQL generation patterns
- Criteria API generation patterns
- Spring Data repository method-name parsing rules
