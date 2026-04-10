# CoQuery DB Knowledge Audit

Date: 2026-04-10

## Short Answer

Partially. CoQuery now has a structured, inspectable SQL/JPA reference seed and a local-knowledge-first planning path for covered generation, natural-language, and write-planning flows. It can skip provider calls for simple covered natural-language requests, but it is still not a complete offline SQL/JPA knowledge base.

## What Exists Now

- runnable command contracts for SQLite-first SQL work
- safety contract for write commands
- PostgreSQL narrow smoke proof
- MySQL status and dependency expectations
- JPA source introspection plan and `jpa_schema`
- a Codex skill wrapper with command/status references
- a local knowledge planner in `sql_cli/knowledge_planner.py`

## Current Gap

The repository still lacks a complete reference layer for:

- SQL statement families and safe generation rules
- dialect differences across SQLite, PostgreSQL, and MySQL
- parameter binding conventions by driver/backend
- type mapping differences
- schema introspection differences
- JPQL vs SQL differences
- JPA entity mapping rules beyond the first source scanner
- detailed normalized schema metadata for columns, indexes, foreign keys, and constraints
- dialect-specific generation templates beyond the current seed

The local planner is wired into covered generation, natural, and write-planning paths, but generated SQL is still basic and not schema-detail aware.

## Minimum Knowledge Pack Added In This Slice

The first offline reference pack now lives at:

- `skills/coquery-cli/references/db-knowledge.md`

It is intentionally compact and source-linked so an agent can consult local guidance before using an LLM.

Structured machine-readable rules now live at:

- `knowledge/dialects/sqlite.json`
- `knowledge/dialects/postgresql.json`
- `knowledge/dialects/mysql.json`
- `knowledge/dialects/jpql.json`
- `knowledge/safety/write_rules.json`
- `knowledge/coverage.json`

Lookup command:

```bash
python3 main.py --command db_knowledge --dialect sqlite --topic schema
python3 main.py --command db_knowledge --topic write_safety
python3 main.py --command db_knowledge --topic coverage
```

The current structured topics include:

- `overview`
- `statements`
- `schema`
- `pagination`
- `parameters`
- `types`
- `operators`
- `joins`
- `constraints`
- `upsert`
- `safety`
- `write_safety`
- `coverage`
- `gaps`

Coverage command:

```bash
python3 main.py --command db_knowledge --topic coverage
```

This returns:

- current coverage label
- dialect matrix for SQLite, PostgreSQL, MySQL, and JPQL
- structured topic matrix
- what can be answered locally before using an LLM/provider
- implemented gates such as `local_knowledge_first_generation`
- remaining gaps and the next proof gate

Planner behavior:

- `generate` attaches local dialect/topic context before returning SQL.
- write commands attach local dialect and write-safety context before execution.
- `natural --provider-name ...` skips provider calls for simple covered requests and only falls back to provider mode for more complex requests.

## Reference Sources

Use official primary docs first:

- SQLite SQL language reference: https://www.sqlite.org/lang.html
- PostgreSQL current SQL commands reference: https://www.postgresql.org/docs/current/sql-commands.html
- MySQL 8.4 SQL statements reference: https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html
- Jakarta Persistence 3.2 specification: https://jakarta.ee/specifications/persistence/3.2/jakarta-persistence-spec-3.2

## Next Work Required

To materially reduce LLM use further, add:

1. normalized schema-detail knowledge for columns, indexes, foreign keys, and constraints
2. a larger fixture set proving common SQL and JPQL generation paths
3. source-linked reference refresh policy and tooling gate
4. richer dialect coverage for functions, transactions, indexes, schema details, and optimizer behavior

Until then, the correct label is:

- `local knowledge first seed exists`
- not yet `sufficient offline DB knowledge base`
