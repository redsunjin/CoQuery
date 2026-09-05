# CoQuery BI Result Intelligence

Date: 2026-09-02
Status: active PR #18 baseline with Table + Bar Result Visual + Query Graph implemented

## Product decision

CoQuery should not treat a SQL result as only an Excel-like grid.

The product principle is:

**SQL as Visual Data Transformation**

SQL is treated as a declarative relational/data transformation expression that can be understood visually. The mathematical-formula analogy is useful at the level of a compact symbolic statement producing a transformation/result, but SQL is not reduced to a simple numeric function.

The result surface is:

`Table -> Visual -> Flow -> Explain`

The table remains canonical evidence. Visuals, Query Graph, and explanations are derived views of the exact returned result and recognized SQL structure.

This keeps CoQuery aligned with its product journey:

`Learn -> Practice -> Apply -> Assist`

The goal is not to become a general-purpose BI dashboard. The goal is to help a learner or operator understand what a query transforms, what the returned data means, and why a particular visual fits.

## Three visual layers

1. **Query Graph** — logical transformation explicitly described by recognized SQL structure. This is a core learning experience.
2. **Result Visual** — BI-style visual derived only from the exact returned rows.
3. **Execution Graph** — actual database planner/executor evidence. This requires real `EXPLAIN`-style output and is never inferred from SQL text alone.

Query Graph must never be presented as a physical execution plan.

## Result view contract

Every supported query result may expose four views:

1. **Table** — exact rows/columns returned by the query.
2. **Visual** — a recommended chart only when the result shape makes the recommendation defensible.
3. **Flow** — the Query Graph based on explicitly recognized SQL transformation steps; later, returned-data flows such as Sankey remain separate.
4. **Explain** — deterministic plain-language explanation of the recognized SQL transformation, result shape, and visual recommendation.

Fallback rule:

**When the result shape is ambiguous, default to Table and explain why no chart was selected.**

The user must always be able to return to exact Table evidence.

## Deterministic ResultShape classifier

Implemented in:

- `sql_cli/result_intelligence.py`

Executable contract coverage:

- `sql_cli/tests/test_result_intelligence.py`

The classifier does not require an LLM or chart runtime.

Inputs:

- returned column names
- returned values/types
- row count
- submitted SQL text
- practice problem metadata when available (reserved for later deterministic teaching hints)

Outputs:

- `shape`
- `recommended_view`
- `recommended_visual`
- `confidence`
- `reason`
- `dimensions`
- `measures`
- `column_profiles`
- `flow_steps`

Supported/proven shapes:

- `single_metric`
- `category_measure`
- `time_series`
- `part_to_whole`
- `numeric_relationship`
- `stage_funnel`
- `source_target_flow`
- `tabular`
- `unknown`

`geographic_measure` remains deferred until a supported geography contract exists.

## Current recommendation rules

| Result shape | Default view | Visual | Guardrail |
| --- | --- | --- | --- |
| one stable category + one numeric measure | Visual | Bar | max 20 categories, no missing category/measure values |
| time/date + numeric measure | Visual | Line | returned temporal sequence must be safely ordered |
| small explicit percentage/share set forming a complete total | Visual | Ring | max 6 parts; total must be approximately 100 or 1.0 |
| two non-identifier numeric fields per observation | Visual | Scatter | no aggregate/GROUP BY; identifier-like numeric columns are excluded |
| explicit stage + numeric value | Visual | Funnel | stage-like column plus SQL `ORDER BY` required |
| exact `source` + `target` + numeric `value` columns | Flow | Sankey | exact three-column contract required |
| single current numeric value | Table | none | Gauge is not inferred without an explicit target/range |
| mixed/raw/incomplete/too-wide result | Table | none | Table is the truthful default |

No chart is selected solely because numeric values exist.

Zero remains a valid numeric value. Null values are not silently converted to zero; ambiguous/incomplete chart candidates fall back to Table.

## Canonical Table — implemented

Focused practice now renders a real HTML table from the exact returned `columns` and `rows` instead of the visible JSON-string preview.

Rules:

- all rows in the current response are rendered
- `NULL` remains `NULL`
- numeric zero remains `0`
- mobile uses horizontal scrolling rather than dropping columns
- Table remains canonical evidence even when a visual is recommended

## Bar Result Visual — implemented

The first lightweight chart renders only when the classifier returns:

- `shape = category_measure`
- `recommended_visual = bar`
- exactly one dimension and one measure
- all category values are present
- all measure values are finite numbers

Truthfulness rules:

- returned row order is preserved; no hidden sorting
- no sampling/truncation
- negative values remain negative around a truthful zero baseline
- zero remains zero-width rather than missing
- null/non-numeric/ambiguous results refuse the chart
- the visual does not mutate canonical rows

Implementation:

- `app_shell/terminal_shell_prototype/practice-result-visual.js`
- `app_shell/terminal_shell_prototype/practice-result-visual.css`
- `app_shell/terminal_shell_prototype/practice_result_visual_smoke.js`

## Query Graph / SQL transformation Flow — implemented

Query Graph is a first-class learning view.

The deterministic classifier provides conservative `flow_steps` containing only explicitly recognized fragments:

- FROM
- JOIN
- WHERE
- GROUP BY
- aggregate expressions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`)
- HAVING
- ORDER BY
- LIMIT

The visible renderer preserves the recognized step order and exact fragment text.

A final Result node is derived only from the actual returned `row_count`/rows.

Unsupported step kinds are ignored instead of interpreted.

The graph is explicitly labeled:

**logical SQL transformation, not database execution order.**

Implementation:

- `app_shell/terminal_shell_prototype/practice-query-flow.js`
- `app_shell/terminal_shell_prototype/practice-query-flow.css`
- `app_shell/terminal_shell_prototype/practice_query_flow_smoke.js`
- `docs/coquery-query-graph-implementation-2026-09-02.md`

Nested subqueries/CTEs/window/set-operation graphs remain out of scope until explicit parser contracts exist.

## Returned-data flow remains separate

If a result itself has an exact `source`, `target`, `value` contract, the classifier may recommend Sankey/Flow.

That is a **Result Visual/data-flow view**, not the SQL Query Graph.

The actual Sankey renderer remains deferred.

## Explain contract — next implementation gate

Explain should answer four compact questions without inventing business meaning:

1. What recognized transformation did this SQL perform?
2. What does each result row represent, when deterministically knowable?
3. Why was this visual selected or not selected?
4. What should the learner inspect next?

The deterministic first slice must remain useful without an AI provider.

## Bklit UI reference decision

Reference repository:

- `bklit/bklit-ui`

Useful visual patterns include Bar, Line, Area, Pie/Ring, Scatter, Funnel, Gauge, Choropleth, and Sankey.

Licensing boundary:

- chart components are MIT-licensed upstream
- Bklit Studio is proprietary and must not be reused or redistributed as part of CoQuery

Architecture boundary:

- current CoQuery PWA is plain HTML/CSS/JavaScript
- Bklit chart components are React-based and rely on React/visx-style dependencies

Therefore this slice does not add React or directly install the Bklit component registry. Bklit remains a design/reference library until a deliberate architecture decision is made.

## PWA/offline boundary

The PWA app-shell cache is now `coquery-pwa-v2` and explicitly includes:

- `practice-result-visual.js/css`
- `practice-query-flow.js/css`

`/api/*` remains outside service-worker caching.

## Safety and truthfulness

- visualization is derived from returned result only
- Query Graph derives only from recognized SQL fragments
- Query Graph is not presented as physical execution order
- Execution Graph is never shown without real planner/executor evidence
- never fabricate missing measures, targets, geography, stage order, flow edges, or execution nodes
- zero is valid data, not missing data
- null/missing values remain visible in Table and are not silently converted to zero
- Table remains canonical evidence
- no automatic external data sharing
- Production Assist data remains subject to existing safety/export boundaries

## Accessibility baseline

- Table is always available
- Bar visual has a textual summary
- Query Graph has a textual description and uses semantic ordered-list structure
- recommendations and graph meaning are not communicated by color alone
- mobile uses scrolling rather than omitted data/steps
- reduced-motion safe by default

## Regression proof

Protected by:

- core CLI tests
- ResultShape classifier contracts
- practice-query regression gate
- executable Bar model smoke
- executable Query Graph model smoke through `practice_focus_smoke.py`
- practice-focus static/wiring smoke
- user-flow and PWA/serverless smoke
- PostgreSQL smoke as a separate narrow proof

Implementation head `d30ce9f888db7b6bc2626ff2626fcf8eef0093c8` passed:

- `baseline` — success
- `postgresql-smoke` — success

Documentation-only currentization commits must also remain green before merge.

## Acceptance criteria

1. Same rows/SQL produce the same classification and recommendation.
2. Unsupported/ambiguous shapes fall back to Table.
3. Bar renders only a proven category+measure contract.
4. Query Graph contains only recognized SQL structure.
5. Query Graph is never presented as physical database execution order.
6. Table data is not altered by Visual/Flow/Explain.
7. No new AI/provider requirement is introduced.
8. No React migration is introduced.
9. Regression coverage protects classifier, Table, Bar, Query Graph, and legacy practice behavior.

## Current implementation order

1. [done] ResultShape classifier + contract tests
2. [done] hosted `practice_query` metadata integration
3. [done] real Table renderer
4. [done] Bar Result Visual for `category_measure`
5. [done] Query Graph/Flow renderer from recognized `flow_steps`
6. deterministic Explain copy
7. Line/time-series support
8. additional Bklit-inspired visuals only when result-shape rules require them
9. Execution Graph only with real `EXPLAIN`-style evidence
