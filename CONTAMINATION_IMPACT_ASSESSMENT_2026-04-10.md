# CoQuery Contamination Impact Assessment

Date: 2026-04-10

Reference report:

- `CONTAMINATION_SCOPE_REPORT_2026-04-10.md`

## 1. Current Observation

The contamination report is accurate in its main classification:

- the current problem is committed scope drift on `main`
- the working tree is not carrying code drift, but the source report itself was untracked when this assessment was prepared
- the expansion range is concentrated from `cce3bfe` through `b8d3fb6`

Current `main` is synchronized with `origin/main`.

## 2. Impact Summary

The contamination is bounded but meaningful.

Low-risk committed work:

- SQLite baseline stabilization remains useful.
- Explicit write-command safety remains useful.
- PostgreSQL narrow proof work remains aligned with the earlier CoQuery stabilization direction.
- Repository hygiene changes are safe to keep.

Higher-risk scope expansion:

- provider registry and provider-backed natural routing
- JPA source introspection
- Codex skill packaging
- local DB/JPA knowledge lookup, coverage, and local-knowledge-first planning

These tracks are not necessarily bad work. The issue is that they broaden product scope while the intended active repository may have been `rfs-cli`, so they should be treated as optional CoQuery experiments until reviewed.

## 3. Entanglement Assessment

### Provider Track

Primary range:

- `cce3bfe`
- `32372b2`

Impact:

- adds provider registry CLI commands
- changes `natural` behavior
- adds `sql_cli/llm_registry.py`
- adds Ollama smoke script and provider docs

Cleanup complexity: medium.

Reason:

- `cce3bfe` mixes provider work with PostgreSQL smoke expansion, so a blunt revert would also risk removing useful PostgreSQL proof updates.

### JPA Track

Primary range:

- `4da3f97`

Impact:

- adds `jpa_schema`
- adds `sql_cli/jpa.py`
- expands CLI command surface and tests
- adds the first skill package

Cleanup complexity: medium.

Reason:

- code is mostly separable, but command docs and tests are now aligned around the larger surface.

### Agent Skill Track

Primary range:

- `4da3f97`
- later documentation updates through `b8d3fb6`

Impact:

- adds `skills/coquery-cli`
- syncs current CoQuery behavior into a reusable Codex skill

Cleanup complexity: low to medium.

Reason:

- files are mostly isolated under `skills/coquery-cli`, but status references mention provider, JPA, and DB knowledge tracks.

### DB Knowledge Track

Primary range:

- `aaec350`
- `8b46432`
- `b8d3fb6`

Impact:

- adds structured dialect JSON rules
- adds `db_knowledge`
- adds coverage reporting
- wires generation, natural, and write planning to local knowledge context

Cleanup complexity: medium.

Reason:

- new files are isolated under `knowledge/` and `sql_cli/dialect_rules.py`, but `main.py`, `sql_cli/cli.py`, `sql_cli/nl_core.py`, tests, and docs now reference the track.

## 4. Recommended Cleanup Strategy

Do not rewrite `main` immediately.

Use a branch-preserving cleanup path:

1. Preserve current `main` as an expansion branch:
   - suggested branch: `archive/coquery-expansion-2026-04-10`
2. Create a cleanup branch from the desired baseline:
   - smallest repaired baseline: `9181642`
   - stabilization plus PostgreSQL smoke harness: `fb835c8`
   - PostgreSQL narrow proof through update: `178c823`
3. Re-apply only reviewed commits or partial patches:
   - keep PostgreSQL proof updates that are still in scope
   - keep repo hygiene changes
   - keep provider/JPA/skill/knowledge tracks only if explicitly accepted as CoQuery roadmap items
4. Update status docs to match the chosen product boundary.
5. Run the baseline verification suite before replacing or merging any branch.

## 5. Recommended Decision Matrix

If the goal is a minimal honest SQL CLI:

- baseline: `fb835c8`
- keep: SQLite baseline, write safety, PostgreSQL smoke harness
- exclude by default: provider, JPA, skill package, DB knowledge layer

If the goal is current CoQuery with optional experiments:

- baseline: `b8d3fb6`
- keep all current code
- relabel provider/JPA/skill/knowledge as optional experimental tracks
- add a roadmap note that these tracks came from post-stabilization expansion

If the goal is practical cleanup without losing useful work:

- branch current `main`
- create a new `main` cleanup branch from `178c823`
- cherry-pick or manually re-apply PostgreSQL delete proof and MySQL status docs
- leave provider/JPA/skill/knowledge on the archive branch until accepted

## 6. Immediate Safe Actions

Safe to do now:

- track this assessment and the source contamination report
- do not revert any commits yet
- do not delete generated branches or remote history
- run current tests to prove the present head is at least internally consistent

Unsafe without explicit decision:

- `git reset --hard`
- force-pushing `main`
- reverting `cce3bfe` directly
- deleting provider/JPA/knowledge files piecemeal from current `main`

## 7. Verification Needed Before Any Cleanup Merge

For current head:

```bash
python3 sql_cli/tests/test_core.py
python3 skills/coquery-cli/scripts/coquery_agent.py verify
```

For a reduced baseline:

```bash
python3 main.py --help
python3 main.py --command schema --db example.db --format json
python3 sql_cli/tests/test_core.py
bash scripts/run_postgresql_local_smoke.sh
```

## 8. Recommendation

The best next cleanup move is not deletion. It is branch separation.

Recommended next action:

1. Commit this assessment and the source contamination report.
2. Create and push `archive/coquery-expansion-2026-04-10` at current HEAD.
3. Create a review branch from `178c823`.
4. Decide which post-`178c823` tracks are CoQuery roadmap items versus misplaced `rfs-cli` work.

This keeps all work recoverable while giving reviewers a clean place to rebuild the intended CoQuery boundary.

## 9. Follow-Up Decision

After review, the reduced cleanup PR was closed unmerged:

- PR: `#1` `Review reduced CoQuery core stabilization branch`
- branch: `cleanup/core-stabilization-2026-04-10`
- result: closed, not merged

The current active direction is to keep `main` as the active CoQuery line and preserve the DB/JPA knowledge layer, JPA source introspection, and Codex skill packaging.

Provider-backed natural remains secondary and experimental.

The reduced cleanup branch remains useful as a comparison point, but it is not the active direction unless a future explicit decision reverses this one.

Decision record:

- `SCOPE_DECISION_2026-04-10.md`
