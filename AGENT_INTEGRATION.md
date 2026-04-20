# CoQuery Agent Integration

This project is designed to be invoked from the shell first.

The two primary entry points are:

- `python3 main.py ...` for direct CoQuery CLI calls
- `python3 skills/coquery-cli/scripts/coquery_agent.py ...` for agent-oriented wrapper calls

## Recommended Paths

### 1. Same repository session

Use this when the agent or CLI process is already running inside the repository.

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py describe
python3 skills/coquery-cli/scripts/coquery_agent.py verify
python3 skills/coquery-cli/scripts/coquery_agent.py run --command schema --db example.db
```

Why this is the best default:

- no installation step
- machine-readable JSON output
- stable `describe`, `verify`, `run` wrapper surface
- repository auto-detection already works

### 2. Installed skill in another Codex session

Use this when another Codex session should discover and reuse the skill package.

```bash
bash scripts/install_coquery_skill.sh
python3 ~/.codex/skills/coquery-cli/scripts/coquery_agent.py describe --repo /path/to/CoQuery
python3 ~/.codex/skills/coquery-cli/scripts/coquery_agent.py verify --repo /path/to/CoQuery
```

If the repository is not in the current working directory, pass `--repo /path/to/CoQuery` or set:

```bash
export COQUERY_REPO=/path/to/CoQuery
```

### 3. Generic CLI or automation integration

Use this when Bash, Python, Node.js, or another tool needs to invoke CoQuery.

```bash
python3 skills/coquery-cli/scripts/coquery_agent.py run \
  --repo /path/to/CoQuery \
  --command schema_detail \
  --db /path/to/example.db
```

Why this is effective:

- stdout carries JSON payloads
- exit code `0/1` is enough for automation
- the wrapper exposes a narrower, easier contract than the full CLI
- `describe` can be called first to discover capability boundaries

## Best Invocation Pattern

For other agents, this is the recommended order:

1. call `describe`
2. if needed, call `verify`
3. call `run` for actual work

This is better than asking another agent to rediscover the project because:

- capability boundaries are explicit
- backend support is explicit
- driver requirements are explicit
- installation guidance is explicit

## Effective Install Strategy

The most effective default is:

- keep CoQuery as the source repository
- install only the skill package into `~/.codex/skills/coquery-cli`
- point the installed skill back at the repository with `--repo` or `COQUERY_REPO`

This avoids:

- duplicating the whole repository into each agent environment
- stale copies of project code
- confusing drift between installed skill files and repository files

## Backend Notes

- SQLite is the primary working path.
- PostgreSQL is narrow experimental support only.
- direct PostgreSQL runtime calls require `psycopg[binary]` in the active Python environment.
- `scripts/run_postgresql_local_smoke.sh` remains the repeatable PostgreSQL proof path because it bootstraps its own virtual environment when needed.
- Oracle is not in scope.

## Practical Recommendation

Use these defaults unless there is a strong reason not to:

- humans: `python3 main.py ...` for direct manual use
- agents in-repo: `python3 skills/coquery-cli/scripts/coquery_agent.py ...`
- agents out-of-repo: `bash scripts/install_coquery_skill.sh` then installed wrapper with `--repo`
- automation: prefer wrapper JSON output over parsing human-readable text
