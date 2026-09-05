# CoQuery Deterministic Explain Implementation

Date: 2026-09-02
Status: implemented on active PR #18; branch CI verification required before merge

## Product role

CoQuery's result-understanding surface is:

`Table | Visual | Flow | Explain`

Explain is not an AI summary. The first implementation is deterministic and uses only evidence already present in the successful `practice_query` result:

- recognized SQL `flow_steps`
- `ResultShape`
- classifier-provided dimensions/measures
- recommended view/visual
- returned row count

It must remain useful without an external provider.

## Explain questions

The visible Explain block answers four questions:

1. **What did the SQL do?** — shows only recognized SQL transformation fragments.
2. **What does each row represent?** — uses a conservative template for the proven result shape.
3. **Why this view?** — explains why Bar/Line/etc. is recommended, or why Table remains preferred.
4. **What is the boundary?** — states that business causality, hidden meaning, and physical execution plans are not inferred.

## Truthfulness boundary

Explain must not:

- invent SQL clauses not present in `flow_steps`
- accept physical execution-plan nodes as Query Graph/Explain evidence
- infer business causes or intent
- infer hidden semantics for generic tabular records
- turn missing/null values into zero
- mutate `columns`, `rows`, `row_count`, or classifier metadata
- require an LLM/provider

Unsupported or ambiguous result shapes use conservative Table-oriented wording.

## Implementation

Files:

- `app_shell/terminal_shell_prototype/practice-result-explain.js`
- `app_shell/terminal_shell_prototype/practice-result-explain.css`
- `app_shell/terminal_shell_prototype/practice_result_explain_smoke.js`

Asset wiring:

- `app_shell/terminal_shell_prototype/onboarding.js`
- `app_shell/terminal_shell_prototype/service-worker.js`

Regression gates:

- `.github/workflows/baseline.yml`
- `app_shell/terminal_shell_prototype/practice_focus_smoke.py`
- `app_shell/terminal_shell_prototype/pwa_serverless_smoke.py`

## Result-shape row semantics

Supported deterministic wording covers:

- `category_measure`
- `time_series`
- `part_to_whole`
- `numeric_relationship`
- `stage_funnel`
- `source_target_flow`
- `single_metric`
- `tabular`
- `unknown`

The wording describes the returned structure, not the business reason behind it.

## Localization

The Explain surface provides Korean and English copy in the frontend and updates when the existing language selector changes.

This does not yet replace the separate backend-English `result_intelligence.reason` string shown in the recommendation area; completing that KR/EN recommendation copy remains a separate task.

## PWA cache

The app-shell cache is bumped to `coquery-pwa-v3` and includes:

- `practice-result-explain.js`
- `practice-result-explain.css`

`/api/*` remains outside the service-worker cache path.

## Acceptance

1. Same successful result metadata produces the same Explain model.
2. Failed/non-query results do not render Explain.
3. Unsupported flow kinds are filtered rather than interpreted.
4. Row semantics are conservative for ambiguous/tabular results.
5. No business causality or physical execution-plan claim is made.
6. Canonical query evidence is not mutated.
7. Korean/English copy is available without an AI call.
8. Baseline and PostgreSQL smoke remain green before merge.

## Next gate

After this Explain slice is green, the next planned Result Visual is the deterministic Line renderer for safely ordered `time_series` results.
