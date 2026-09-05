# CoQuery Query Graph Implementation

Date: 2026-09-02
Status: implemented and merged in PR #18; implementation CI verified and deployed to the durable PWA Worker

## Product principle

CoQuery treats SQL as **Visual Data Transformation**.

The visible learning model keeps three layers separate:

1. **Query Graph** — the logical transformation explicitly described by recognized SQL clauses.
2. **Result Visual** — a BI-style visual derived only from the exact returned rows.
3. **Execution Graph** — an actual database planner/executor view that requires real `EXPLAIN`-style evidence and is not inferred from SQL text.

`Table | Visual | Flow | Explain`

Table remains canonical evidence.

## Implemented Query Graph boundary

The hosted practice result already receives deterministic `result_intelligence.flow_steps` from the Python classifier. The first visible Query Graph renders only those recognized steps.

Recognized kinds:

- `from`
- `join`
- `where`
- `group_by`
- `aggregate`
- `having`
- `order_by`
- `limit`

The UI preserves the exact recognized SQL fragment text and its order. Unsupported step kinds are ignored rather than interpreted.

A final **Result** node is derived only from actual returned `row_count`/rows so the learner can see the transformation ending in concrete output.

## Truthfulness rules

- Query Graph is labeled as a logical SQL transformation view, not database execution order.
- No physical nodes such as scans, hash joins, indexes, costs, or planner estimates are invented.
- Empty/failed query results do not invent a graph.
- Unsupported step kinds are not rendered.
- The graph does not mutate `columns`, `rows`, `row_count`, or classifier metadata.
- Table remains available as canonical evidence.
- No LLM/provider is required.
- No React migration or chart dependency is introduced.

## UI implementation

Files:

- `app_shell/terminal_shell_prototype/practice-query-flow.js`
- `app_shell/terminal_shell_prototype/practice-query-flow.css`
- `app_shell/terminal_shell_prototype/practice_query_flow_smoke.js`

The graph is rendered as an accessible ordered list of step cards connected left-to-right. Small screens use horizontal scrolling instead of dropping or sampling steps. The visual uses explicit step labels in addition to styling, and reduced-motion behavior is safe by default.

The onboarding loader includes Query Graph assets alongside Bar Result Visual assets.

The PWA app shell cache was bumped to `coquery-pwa-v2` and explicitly includes:

- `practice-result-visual.js/css`
- `practice-query-flow.js/css`

`/api/*` remains outside service-worker caching.

## Regression proof

The implementation is protected by:

- existing core tests
- ResultShape classifier contracts
- practice-query regression gate
- Bar Result Visual smoke
- executable Query Graph model smoke invoked by `practice_focus_smoke.py`
- focused-practice asset/static smoke
- PWA/serverless smoke including shell-cache assertions
- separate PostgreSQL smoke

Verified on implementation head `d30ce9f888db7b6bc2626ff2626fcf8eef0093c8`:

- `baseline` — success
- `postgresql-smoke` — success

The following project state files were currentized after the implementation proof:

- `docs/coquery-bi-result-intelligence-2026-08-30.md`
- `EASY_SQL_ROADMAP.md`
- `EASY_SQL_TODO.md`
- `HANDOFF.md`

Documentation-only heads must remain green before merge.

## Next implementation gate

**Deterministic Explain** should connect three things without inventing business meaning:

1. what recognized SQL transformations occurred,
2. what each returned row represents when deterministically knowable,
3. why a Result Visual was or was not recommended.

Line/time-series and other additional BI visuals remain after this explanatory layer unless explicitly reprioritized.
