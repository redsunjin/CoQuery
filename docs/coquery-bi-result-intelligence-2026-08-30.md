# CoQuery BI Result Intelligence

Date: 2026-09-02
Status: product/UX baseline plus proven deterministic ResultShape/Table integration

## Product principle

CoQuery adopts the product principle:

**SQL as Visual Data Transformation**

SQL can be taught as a declarative data-transformation expression: a user describes what data should be selected, filtered, related, grouped, aggregated, ordered, and returned. This is analogous to a mathematical expression in the sense that a compact symbolic statement produces a structured transformation and result.

The analogy has a strict boundary:

- SQL is **not** treated as a simple numeric function such as `y = f(x)`.
- CoQuery treats SQL as a **relational/data transformation expression**.
- Visualizations must represent evidence that can be defended from the SQL structure, returned rows, or an actual database execution plan.

The product goal is therefore broader than an Excel-like result viewer:

`SQL -> transformation understanding -> result understanding -> evidence`

This keeps CoQuery aligned with:

`Learn -> Practice -> Apply -> Assist`

## Three visual layers

CoQuery separates three different kinds of graph. They must never be presented as if they are the same thing.

### 1. Query Graph — core learning experience

Purpose: explain **what transformation the SQL describes**.

Example:

`customers -> WHERE active = 1 -> GROUP BY region -> COUNT(*) -> ORDER BY count DESC -> result`

Initial nodes/steps may include only explicitly recognized SQL structure:

- FROM
- JOIN
- WHERE
- GROUP BY
- aggregate expressions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`)
- HAVING
- ORDER BY
- LIMIT

Rules:

- Query Graph is a semantic/learning representation, not a claim about physical database execution.
- Unsupported clauses, nested queries, CTEs, window functions, or ambiguous syntax must not receive invented meaning.
- Complex SQL may use nested/sub-graphs later; until supported, show the recognized portion and mark the rest unsupported/unknown.
- Query Graph is a first-class learning surface, not merely decorative BI output.

### 2. Result Visual — BI interpretation of returned data

Purpose: explain **what shape the returned data has**.

Examples:

- category + measure -> Bar
- ordered time + measure -> Line
- explicit part-to-whole -> Ring/Pie
- two row-level numeric measures -> Scatter
- explicit ordered stage + value -> Funnel
- exact source/target/value -> Sankey

Rules:

- Result Visual is derived from the exact returned rows/columns.
- Table remains canonical evidence.
- A chart is recommended only when `ResultShape` can defend the mapping.
- No chart is selected merely because numeric values exist.

### 3. Execution Graph — database execution evidence

Purpose: explain **how a specific database actually planned/executed the query**.

Examples may later include provider-specific plan nodes such as scans, joins, aggregates, and sorts.

Rules:

- Execution Graph must be backed by an actual plan source such as `EXPLAIN`/equivalent evidence.
- Never infer an execution graph from SQL text alone.
- Query Graph and Execution Graph may look similar but answer different questions and must use different labels.
- Execution Graph is a later product slice; it is not part of the current first BI implementation.

## Ordering/meaning boundary

CoQuery must keep these concepts distinct:

1. **SQL text/surface** — the statement the learner wrote.
2. **Query Graph** — CoQuery's recognized logical transformation representation for learning.
3. **Execution Graph** — the database's actual planner/executor evidence.

Do not teach a Query Graph as if it were the physical runtime order. Do not label an inferred sequence as an execution plan.

## Result surface contract

The result surface remains:

`Table | Visual | Flow | Explain`

Definitions:

1. **Table** — exact rows/columns returned by the query; canonical evidence.
2. **Visual** — Result Visual selected only for a defensible result shape.
3. **Flow** — Query Graph first; returned-data flow such as Sankey when the result explicitly exposes source/target/value.
4. **Explain** — plain-language explanation connecting SQL structure, row meaning, and recommendation reason.

Flow is promoted to a **core learning experience**. It should help a learner see SQL as a transformation rather than memorize syntax in isolation.

Fallback rule:

**When a result shape or SQL structure is ambiguous, prefer Table and/or a partial recognized Query Graph, and state what is unknown.**

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

Zero remains a valid numeric value. Null values are not silently converted to zero; ambiguous/incomplete chart candidates fall back to Table.

## Query Graph contract

The current classifier already derives conservative `flow_steps`. The visible Query Graph renderer will use those exact recognized steps as its first contract.

Initial renderer rules:

- render one node/step only when the parser recognized it
- preserve the original recognized clause text for inspectability
- visually distinguish source (`FROM`/`JOIN`), filter, grouping/aggregation, ordering/limit, and result without inventing hidden operations
- provide a textual alternative for accessibility
- allow the learner to return to the original SQL and Table evidence
- label the view **Query Flow/Query Graph**, not Execution Plan

Later extensions may support nested structures for:

- subqueries
- CTEs
- set operations
- window functions

These are not to be simulated before explicit parser support exists.

## Returned-data flow contract

If the result itself has an exact `source`, `target`, `value` contract, the classifier returns `source_target_flow` and may recommend Sankey/Flow.

This is a Result Visual/data-flow view and must not be confused with Query Graph.

## Explain contract

Explain answers four compact questions:

1. What transformation did this SQL describe?
2. What does each result row represent?
3. Why was this visual/flow selected or not selected?
4. What should the learner inspect next?

The deterministic baseline must remain useful without an AI provider. AI augmentation may come later but cannot replace the evidence-backed explanation contract.

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

Therefore the current slice does **not** add React or directly install the Bklit component registry.

Use Bklit as a visual/product reference first. After the contract is proven, evaluate either:

1. lightweight native SVG/Canvas rendering for the small chart subset CoQuery needs, or
2. a deliberate frontend architecture change that can host selected MIT chart components without forking the product.

A React migration must not be smuggled into a chart feature.

## Current implementation status

Completed on active PR #18:

- deterministic `ResultShape` classifier + tests
- conservative SQL `flow_steps` extraction
- additive hosted `practice_query` result-intelligence metadata
- real column/row Table renderer in focused practice
- truthful `NULL`/zero handling
- recommendation name/reason above the Table
- practice/query/grading/non-SELECT regression gate
- practice-focus/PWA smoke protection
- baseline and PostgreSQL smoke green on the implementation head

Not yet implemented:

- lightweight Bar renderer
- visible Query Graph/Flow renderer
- deterministic Explain view
- Line/time-series renderer
- Execution Graph backed by database plan evidence

## Implementation order

The order balances fast visible value with the new core learning principle:

1. [done] `ResultShape` classifier + contract tests
2. [done] hosted `practice_query` metadata integration
3. [done] real Table renderer
4. lightweight Bar renderer for proven `category_measure`
5. **Query Graph/Flow renderer as a core learning view**
6. deterministic Explain copy
7. Line/time-series Result Visual
8. nested Query Graph support only when parser contracts are added
9. Execution Graph research/implementation only with real `EXPLAIN`-style evidence
10. evaluate additional Bklit-inspired visuals only when result-shape rules require them

## Safety and truthfulness

- Table is always available as canonical result evidence
- Result Visual is derived only from returned data
- Query Graph is derived only from explicitly recognized SQL structure
- Execution Graph requires actual database plan evidence
- never fabricate missing measures, targets, geography, stage order, flow edges, or execution nodes
- zero is valid data, not missingness
- null/missing values remain visible and are never silently converted to zero
- chart sampling/truncation must be explicit
- unsupported SQL structure stays unsupported/unknown
- no automatic external data sharing
- Production Assist remains subject to existing safety/export boundaries

## Accessibility baseline

- Table is always available
- charts and graphs have textual summaries
- recommendations are not communicated by color alone
- future view tabs are keyboard-accessible
- Query Graph nodes have readable text equivalents
- reduced-motion safe by default

## Acceptance criteria

1. Same rows/SQL produce the same classification and recommendation.
2. Unsupported/ambiguous result shapes fall back to Table.
3. The chart recommendation includes a plain-language reason.
4. Query Graph contains only explicitly recognized SQL structure.
5. Query Graph is never labeled as a physical execution plan.
6. Execution Graph is not shown without real planner/executor evidence.
7. Table data is not altered by Visual/Flow/Explain.
8. Zero/null semantics remain truthful.
9. No new AI/provider requirement is introduced.
10. No React migration is introduced by this slice.
11. Regression coverage protects existing practice/query/grading behavior.
12. Learners can distinguish SQL text, Query Graph, Result Visual, and later Execution Graph.