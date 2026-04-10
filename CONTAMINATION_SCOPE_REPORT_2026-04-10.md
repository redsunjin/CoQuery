# CoQuery Contamination Scope Report

Date: 2026-04-10

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Record the current contamination scope caused by work continuing in `CoQuery` while the intended active repository should have been `rfs-cli`.

This report is descriptive only.
It does not revert, reset, or change the repository state.

## 2. Current Repository State

Observed at reporting time:

- branch: `main`
- remote tracking: `origin/main`
- working tree: `clean`
- note: the concern is not uncommitted drift now, but committed scope drift already landed on `main`

## 3. Confirmed Committed Range

Recent commits now present on `main`:

1. `b8d3fb6` `Use local DB knowledge before provider calls`
2. `8b46432` `Add DB knowledge coverage report`
3. `aaec350` `Add structured DB knowledge lookup`
4. `4da3f97` `Add JPA schema support and CoQuery skill package`
5. `32372b2` `Align docs with provider track decision`
6. `cce3bfe` `Add provider registry and extend PostgreSQL smoke coverage`
7. `178c823` `Expand PostgreSQL proof to update`
8. `9a94c54` `Remove tracked Python bytecode cache`
9. `72edd40` `Prove PostgreSQL insert smoke path`
10. `572f5eb` `Document MySQL stub status decision`

Reference pre-range baseline still visible in history:

- `fb835c8` `Stabilize contracts and add PostgreSQL smoke harness`
- `9181642` `Repair CLI baseline and align tests`

## 4. Risk Classification

### A. Core stabilization line

These commits still fit the original CoQuery stabilization direction reasonably well:

- `572f5eb` `Document MySQL stub status decision`
- `72edd40` `Prove PostgreSQL insert smoke path`
- `9a94c54` `Remove tracked Python bytecode cache`
- `178c823` `Expand PostgreSQL proof to update`

Why:

- they stay close to SQLite baseline hardening
- they stay close to PostgreSQL narrow proof
- they improve repo hygiene or truthful status language

### B. Scope expansion with contamination risk

These commits are the main contamination candidates:

- `cce3bfe` `Add provider registry and extend PostgreSQL smoke coverage`
- `32372b2` `Align docs with provider track decision`
- `4da3f97` `Add JPA schema support and CoQuery skill package`
- `aaec350` `Add structured DB knowledge lookup`
- `8b46432` `Add DB knowledge coverage report`
- `b8d3fb6` `Use local DB knowledge before provider calls`

Why these are higher risk:

- they broadened product scope while the operator believed work should be happening in another repository
- they introduced new tracks beyond the original stabilization focus
- they landed directly on `main`
- they mixed multiple experimental directions:
  - provider-backed natural
  - JPA source introspection
  - Codex skill packaging
  - local DB knowledge lookup/coverage

## 5. File-Level Contamination Surface

### A. Provider / natural track

Main files:

- [main.py](/Users/Agent/ps-workspace/CoQuery/main.py)
- [sql_cli/cli.py](/Users/Agent/ps-workspace/CoQuery/sql_cli/cli.py)
- [sql_cli/nl_core.py](/Users/Agent/ps-workspace/CoQuery/sql_cli/nl_core.py)
- [sql_cli/llm_registry.py](/Users/Agent/ps-workspace/CoQuery/sql_cli/llm_registry.py)
- [scripts/run_ollama_local_smoke.sh](/Users/Agent/ps-workspace/CoQuery/scripts/run_ollama_local_smoke.sh)
- [LLM_PROVIDER_REGISTRY_2026-04-07.md](/Users/Agent/ps-workspace/CoQuery/LLM_PROVIDER_REGISTRY_2026-04-07.md)
- [PROVIDER_TRACK_DECISION_2026-04-09.md](/Users/Agent/ps-workspace/CoQuery/PROVIDER_TRACK_DECISION_2026-04-09.md)

### B. JPA track

Main files:

- [sql_cli/jpa.py](/Users/Agent/ps-workspace/CoQuery/sql_cli/jpa.py)
- [main.py](/Users/Agent/ps-workspace/CoQuery/main.py)
- [sql_cli/cli.py](/Users/Agent/ps-workspace/CoQuery/sql_cli/cli.py)
- [JPA_SUPPORT_PLAN_2026-04-10.md](/Users/Agent/ps-workspace/CoQuery/JPA_SUPPORT_PLAN_2026-04-10.md)

### C. Agent skill packaging track

Main files:

- [skills/coquery-cli/SKILL.md](/Users/Agent/ps-workspace/CoQuery/skills/coquery-cli/SKILL.md)
- [skills/coquery-cli/scripts/coquery_agent.py](/Users/Agent/ps-workspace/CoQuery/skills/coquery-cli/scripts/coquery_agent.py)
- [skills/coquery-cli/references/commands.md](/Users/Agent/ps-workspace/CoQuery/skills/coquery-cli/references/commands.md)
- [skills/coquery-cli/references/status.md](/Users/Agent/ps-workspace/CoQuery/skills/coquery-cli/references/status.md)
- [skills/coquery-cli/references/db-knowledge.md](/Users/Agent/ps-workspace/CoQuery/skills/coquery-cli/references/db-knowledge.md)
- [skills/coquery-cli/agents/openai.yaml](/Users/Agent/ps-workspace/CoQuery/skills/coquery-cli/agents/openai.yaml)

### D. DB knowledge track

Main files:

- [sql_cli/knowledge_planner.py](/Users/Agent/ps-workspace/CoQuery/sql_cli/knowledge_planner.py)
- [sql_cli/dialect_rules.py](/Users/Agent/ps-workspace/CoQuery/sql_cli/dialect_rules.py)
- [knowledge/dialects/sqlite.json](/Users/Agent/ps-workspace/CoQuery/knowledge/dialects/sqlite.json)
- [knowledge/dialects/postgresql.json](/Users/Agent/ps-workspace/CoQuery/knowledge/dialects/postgresql.json)
- [knowledge/dialects/mysql.json](/Users/Agent/ps-workspace/CoQuery/knowledge/dialects/mysql.json)
- [knowledge/dialects/jpql.json](/Users/Agent/ps-workspace/CoQuery/knowledge/dialects/jpql.json)
- [knowledge/safety/write_rules.json](/Users/Agent/ps-workspace/CoQuery/knowledge/safety/write_rules.json)
- [knowledge/coverage.json](/Users/Agent/ps-workspace/CoQuery/knowledge/coverage.json)
- [DB_KNOWLEDGE_AUDIT_2026-04-10.md](/Users/Agent/ps-workspace/CoQuery/DB_KNOWLEDGE_AUDIT_2026-04-10.md)

### E. Control-plane and status docs touched by the expansion

- [EASY_SQL_TODO.md](/Users/Agent/ps-workspace/CoQuery/EASY_SQL_TODO.md)
- [EASY_SQL_ROADMAP.md](/Users/Agent/ps-workspace/CoQuery/EASY_SQL_ROADMAP.md)
- [HANDOFF.md](/Users/Agent/ps-workspace/CoQuery/HANDOFF.md)
- [PROJECT_SUMMARY.md](/Users/Agent/ps-workspace/CoQuery/PROJECT_SUMMARY.md)
- [README_COQ.md](/Users/Agent/ps-workspace/CoQuery/README_COQ.md)
- [STAGE_STATUS.md](/Users/Agent/ps-workspace/CoQuery/STAGE_STATUS.md)
- [readme.md](/Users/Agent/ps-workspace/CoQuery/readme.md)

## 6. Practical Interpretation

The repository is not currently dirty, but `main` has absorbed multiple experiments that may not belong to the intended CoQuery core loop.

The contamination is therefore:

- primarily **scope contamination**
- not primarily **working-tree contamination**

In plain terms:

- the repo is currently orderly
- but the product boundary may have drifted
- and the drift is already recorded in committed history on `main`

## 7. Most Likely Decision Boundaries

If CoQuery is reviewed later, the most likely split points are:

### Keep with core stabilization

Likely keep:

- SQLite baseline stabilization
- explicit write contract
- PostgreSQL narrow proof
- repo hygiene changes

### Re-evaluate as optional or branch-only tracks

Likely re-evaluate:

- provider registry
- provider-backed natural routing
- JPA source introspection
- Codex skill packaging
- DB knowledge lookup/coverage

## 8. Safe Baseline Candidates For Future Review

Candidate baseline points for later human review:

1. `9181642`
   - earliest repaired CLI baseline
2. `fb835c8`
   - stabilization + PostgreSQL smoke harness
3. `178c823`
   - PostgreSQL narrow proof through update
4. `b8d3fb6`
   - current head with all expansion tracks included

Interpretation:

- if the goal is "recover the smallest honest SQL CLI baseline", inspect around `9181642` or `fb835c8`
- if the goal is "keep PostgreSQL narrow proof but remove later expansion", inspect around `178c823`
- if the goal is "keep all recent experiments and just reclassify them", inspect from `cce3bfe` onward

## 9. Reporting Conclusion

The contamination scope is real.

However, it is bounded and understandable:

- the repo is clean
- the risk is concentrated in committed scope expansion on `main`
- the highest-risk contamination zone is the range:
  - `cce3bfe` through `b8d3fb6`

That range should be the first review target if CoQuery is later triaged for cleanup or branch separation.
