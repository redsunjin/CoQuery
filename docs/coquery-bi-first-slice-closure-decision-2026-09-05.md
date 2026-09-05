# CoQuery BI First Slice Closure Decision — 2026-09-05

Status: closure gate passed on PR #18; merge approval still required

## Decision

The first BI Result Intelligence slice should include the same additive `result_intelligence` metadata in both web runtime adapters before merge.

Reason:

- the hosted Cloudflare PWA and the local/advanced terminal shell use the same learner-facing result UI
- without local parity, the same successful `practice_query` could show `Table | Visual | Flow | Explain` when hosted but lose derived result views when run through the local shell
- this is a runtime inconsistency, not an optional future chart feature

The parity fix is intentionally applied at the web adapter boundary rather than changing the generic `sql_cli.command_api.run_command()` contract.

## Implemented boundary

Implementation commit:

- `dca239fcc20c9d3d55892b0fd9b9806ce43c7854` — `Add local result intelligence parity`

Changes:

- `app_shell/terminal_shell_prototype/server.py`
  - successful local `practice_query` responses pass through `enrich_practice_query_result()`
  - failed/non-SELECT results remain unchanged
- `app_shell/terminal_shell_prototype/practice_local_result_intelligence_smoke.py`
  - starts the actual local HTTP shell
  - proves `category_measure -> Visual -> Bar` metadata is returned
  - proves canonical columns/rows/row_count remain intact
  - proves invalid SQL does not receive fabricated result-intelligence metadata
- `.github/workflows/baseline.yml`
  - runs the local-runtime parity smoke as part of the normal gate

The hosted Worker keeps using the same `enrich_practice_query_result()` helper. No separate classifier or rule set is introduced.

## Architecture decision

Keep the layers separated:

`raw command result -> web runtime adapter -> additive Result Intelligence -> UI`

This preserves the existing generic command/CLI contract while making the two web delivery paths behaviorally consistent.

## BI first-slice closure criteria

The first slice is now considered complete enough for merge review because it has:

- deterministic ResultShape classification
- canonical Table evidence
- Bar and safely ordered Line Result Visuals
- Query Graph/Flow with explicit non-execution-plan labeling
- deterministic Explain
- deterministic KR/EN recommendation explanations
- accessible `Table | Visual | Flow | Explain` switching
- hosted and local/advanced web-runtime metadata parity
- no React migration
- no external AI dependency
- additive/non-mutating result metadata boundary
- baseline CI and PostgreSQL smoke green after the parity change

## Not implied by closure

Closing the first BI slice does not mean:

- PR #18 has been merged
- the durable Cloudflare Worker has been redeployed with PR #18
- browser/device PWA QA is complete
- screen-reader QA is complete
- additional Ring/Pie/Scatter/Funnel/Sankey/Gauge/Choropleth renderers are approved
- Execution Graph exists without real `EXPLAIN` evidence

## Next gate

PR #18 can move to review/merge approval.

After merge, the release path is:

`merge -> durable Cloudflare deployment -> browser/device result-flow QA`

Additional BI chart types remain a later evidence-driven slice.
