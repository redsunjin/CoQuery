---
name: coquery-cli
description: Run, verify, demo, and extend the CoQuery SQL CLI. Use when Codex needs to inspect CoQuery status, demonstrate schema/query/generate/natural/write/JPA entity-schema workflows, run the SQLite baseline tests, run the PostgreSQL smoke proof, or call CoQuery as an agent-side SQL helper against SQLite, annotation-based JPA source, or the documented experimental PostgreSQL path.
---

# CoQuery CLI

Use this skill to operate CoQuery as an agent-side SQL helper without re-discovering the project commands.

## Quick Start

Prefer the bundled wrapper for repeatable agent use:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py verify
python3 skills/coquery-cli/scripts/coquery_agent.py demo
python3 skills/coquery-cli/scripts/coquery_agent.py run --command schema --db example.db
python3 skills/coquery-cli/scripts/coquery_agent.py run --command query --db example.db --sql "SELECT * FROM users"
python3 skills/coquery-cli/scripts/coquery_agent.py run --command jpa_schema --jpa-project /path/to/java-project
python3 skills/coquery-cli/scripts/coquery_agent.py run --command db_knowledge --dialect sqlite --topic schema
python3 skills/coquery-cli/scripts/coquery_agent.py run --command db_knowledge --topic coverage
```

If the skill has been installed outside the repository, pass `--repo /path/to/CoQuery` or set `COQUERY_REPO=/path/to/CoQuery`.

## Operating Rules

- Treat SQLite as the working backend.
- Treat PostgreSQL as experimental and limited to the documented `schema`, `query`, `insert`, `update`, and `delete` smoke paths.
- Treat MySQL as a stub unless the repository status documents have been updated with a real verification slice.
- Treat JPA as ORM/model source introspection unless a Java runtime proof exists.
- Use explicit SQL plus `--write` for `insert`, `update`, and `delete`.
- Use `natural` as an assistive drafting path; do not describe provider-backed natural output as production-grade unless a provider smoke has passed in the current environment.
- Prefer JSON output for agent consumption.

## Common Tasks

Check readiness:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py verify
```

Include PostgreSQL smoke when local PostgreSQL binaries are available:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py verify --postgres
```

In sandboxed environments, this may need permission to start a local PostgreSQL process because the server uses shared memory.

Run a safe SQLite demo on a temporary database copy:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py demo
```

Call one CoQuery command:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py run --command natural --db example.db --sql "show users"
```

Inspect JPA entity source:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py run --command jpa_schema --jpa-project /path/to/java-project
```

Look up local DB/JPA knowledge before using an LLM:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py run --command db_knowledge --dialect postgresql --topic pagination
python3 skills/coquery-cli/scripts/coquery_agent.py run --command db_knowledge --topic write_safety
python3 skills/coquery-cli/scripts/coquery_agent.py run --command db_knowledge --topic coverage
```

Call a write command only when the user has intentionally requested a state-changing operation:

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py run \
  --command insert \
  --db /tmp/demo.db \
  --write \
  --sql "INSERT INTO users (name, age) VALUES ('agent_user', 30)"
```

## References

- Read `references/status.md` for the current truthful capability boundaries.
- Read `references/commands.md` for command examples and demo flow.
- Read `references/db-knowledge.md` before asking an LLM for common SQL, dialect, or JPA rules.
- Use `knowledge/dialects/*.json` and `knowledge/safety/write_rules.json` through `db_knowledge` for deterministic lookup.
