# CoQuery Recommendation Reason Localization — 2026-09-02

Status: implemented on PR #18

## Goal

Remove the remaining backend-English `result_intelligence.reason` text from the learner-facing recommendation line while keeping classification and recommendation decisions unchanged.

The UI now derives its recommendation explanation deterministically from the already-proven result metadata:

- `shape`
- `recommended_view`
- `recommended_visual`
- dimensions/measures

The backend reason string is no longer reused as learner-facing Korean copy.

## Product rule

Localization is presentation, not re-classification.

`same ResultShape metadata -> same recommendation decision -> localized explanation`

No LLM/provider call is introduced.

## Implemented boundary

Current deterministic KR/EN reason coverage includes:

- `unknown`
- `source_target_flow`
- `single_metric`
- ordered `time_series -> line`
- unsafe-order `time_series -> table`
- `part_to_whole -> ring`
- `stage_funnel -> funnel`
- `category_measure -> bar`
- `numeric_relationship -> scatter`
- `tabular -> table`

Unknown future shapes use a conservative generic localized explanation instead of exposing backend-English reason text.

## Truthfulness rules

- localization never changes `shape`, `recommended_view`, or `recommended_visual`
- Korean copy never falls back to the backend-English reason string
- Table remains canonical exact-value evidence
- unsafe time-series remains Table and explicitly says the returned order is not safely chartable
- single metric does not imply Gauge without target/range
- no business causality, intent, or hidden meaning is added
- no physical execution-plan meaning is added

## Implementation

Files:

- `app_shell/terminal_shell_prototype/practice-result-explain.js`
- `app_shell/terminal_shell_prototype/practice_result_explain_smoke.js`

Implementation commit:

- `49cc8ea3e1892db4bab78575baa7883507a5b7e5` — `Localize result recommendation reasons`

## Regression proof

The implementation commit passed:

- `baseline` ✅
- `postgresql-smoke` ✅

The executable Explain smoke now also verifies:

- deterministic Korean and English recommendation copy
- Korean copy does not reuse backend-English `reason`
- Bar recommendation copy
- safely ordered Line recommendation copy
- unsafe time-series Table copy
- single-metric no-Gauge explanation
- Flow/Sankey explanation
- tabular fallback explanation
- same input + language => same localized output

## Next gate

Define keyboard/accessibility behavior for future `Table | Visual | Flow | Explain` view switching before adding more chart types.
