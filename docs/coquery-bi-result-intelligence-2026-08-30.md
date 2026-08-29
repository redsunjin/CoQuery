# CoQuery BI Result Intelligence

Date: 2026-08-30
Status: product/UX baseline plus proven deterministic ResultShape classifier

## Product decision

CoQuery should not treat a SQL result as only an Excel-like grid.

The result surface becomes:

`Table -> Visual -> Flow -> Explain`

The table remains the evidence baseline. Visuals and explanations are derived views of the exact returned result and SQL structure.

This keeps CoQuery aligned with its product journey:

`Learn -> Practice -> Apply -> Assist`

The goal is not to become a general-purpose BI dashboard. The goal is to help a learner or operator understand what the query result means, what shape the data has, and how the SQL produced it.

## Current gap

The current hosted practice result renders `practice_query` rows as JSON strings and truncates the visible preview to five rows.

That is sufficient for execution proof but weak for data understanding.

The deterministic classification layer is now implemented and regression-tested, but it is not yet wired into `practice_query` output or the visible PWA result block.

## Result view contract

Every supported query result may expose four views:

1. **Table** — exact rows/columns returned by the query.
2. **Visual** — a recommended chart only when the result shape makes the recommendation defensible.
3. **Flow** — the SQL transformation path, and later data-flow visuals such as Sankey when the returned schema explicitly represents source/target/value.
4. **Explain** — plain-language explanation of the SQL operation and the result pattern.

Fallback rule:

**When the result shape is ambiguous, default to Table and explain why no chart was selected.**

The user must always be able to return to the exact Table evidence.

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

Supported/proven shapes in the current classifier:

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

## SQL transformation Flow

Flow has two meanings and they remain distinct.

### A. SQL reasoning flow — classifier metadata implemented

Example:

`customers -> WHERE active = 1 -> GROUP BY region -> COUNT(*) -> ORDER BY count DESC -> result`

The current conservative parser records only explicitly recognized fragments:

- FROM
- JOIN
- WHERE
- GROUP BY
- aggregate expressions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`)
- HAVING
- ORDER BY
- LIMIT

Unsupported syntax is not assigned invented meaning.

The visible Flow renderer remains a later step in this PR slice.

### B. Returned-data flow — renderer later

If the result itself has an exact `source`, `target`, `value` contract, the classifier returns `source_target_flow` and recommends Sankey/Flow.

The actual Sankey renderer is deferred until the first Table/Bar result surface is stable.

Do not confuse this with the SQL reasoning flow.

## Explain contract

Explain should answer four compact questions:

1. What did this SQL do?
2. What does each result row represent?
3. Why was this visual selected or not selected?
4. What should the learner inspect next?

The deterministic first slice can explain common clauses and result shapes. AI augmentation may come later, but the base explanation must remain useful without a provider.

## Bklit UI reference decision

Reference repository:

- `bklit/bklit-ui`

Useful visual patterns include Bar, Line, Area, Pie/Ring, Scatter, Funnel, Gauge, Choropleth, and Sankey.

Licensing boundary from the upstream repository:

- chart components are MIT-licensed
- Bklit Studio is proprietary and must not be reused or redistributed as part of CoQuery

Architecture boundary:

- current CoQuery PWA is plain HTML/CSS/JavaScript
- Bklit chart components are React-based and rely on React/visx-style dependencies

Therefore the first slice **does not add React or directly install the Bklit component registry**.

Use Bklit as a design/reference library first. After the result-intelligence contract is proven, evaluate either:

1. lightweight native SVG/Canvas rendering for the small chart subset CoQuery needs, or
2. a deliberate frontend architecture change that can host selected MIT chart components without forking the product.

A React migration must not be smuggled into a chart feature.

## First implementation slice

Boundary:

`practice_query result -> classify -> Table | Visual recommendation | SQL Flow | Explain`

Completed proof:

- deterministic ResultShape module
- category+measure -> Bar recommendation
- ambiguous result -> Table fallback
- ordered time-series -> Line recommendation; unsafe order -> Table
- explicit part-to-whole, numeric relationship, stage funnel, and source/target/value classification
- single metric does not infer Gauge
- zero/null/category-count guardrails
- deterministic/non-mutating classifier behavior
- conservative SQL flow-step extraction
- classifier contracts run in baseline CI
- no external AI call
- no React dependency

Still required for the first visible result slice:

- wire ResultShape metadata into `practice_query`
- Table view renders real columns/rows instead of JSON-string rows
- recommendation reason appears in the result block
- exact raw result remains inspectable
- first chart renderer may be limited to Bar
- visible SQL Flow and deterministic Explain follow after Table/Bar contract is stable

## Suggested UI placement

Inside the existing result block:

`Table | Visual | Flow | Explain`

Default selection policy:

- raw/detail-heavy record result -> Table
- high-confidence aggregate/time result -> Visual
- learning task focused on SQL construction -> Table or Flow, with recommendation badge

The interface should show a small label such as:

`Recommended: Bar · region is a category and count is numeric`

This makes the visualization choice teachable rather than magical.

## Safety and truthfulness

- visualization is derived from the returned result only
- never fabricate missing measures, targets, geography, stage order, or flow edges
- zero is a valid value, not missing data
- null/missing values remain visible in Table and must not be silently converted to zero
- chart sampling/truncation must be explicit
- Table remains the canonical evidence view
- no automatic external data sharing
- Production Assist data remains subject to its existing safety/export boundary

## Accessibility baseline

- Table is always available
- chart has a textual summary
- recommendations are not communicated by color alone
- keyboard-accessible view tabs
- reduced-motion safe by default

## Acceptance criteria for this product slice

1. Same rows/SQL produce the same classification and recommendation.
2. Unsupported/ambiguous shapes fall back to Table.
3. The chart recommendation includes a plain-language reason.
4. SQL Flow contains only clauses explicitly recognized from the query.
5. Table data is not altered by Visual/Flow/Explain.
6. No new AI/provider requirement is introduced.
7. No React migration is introduced by this slice.
8. Regression coverage protects the classifier and fallback behavior.

## Current implementation order

1. [done] `ResultShape` classifier + contract tests
2. wire classifier metadata into `practice_query`
3. real Table renderer
4. Bar renderer for `category_measure`
5. SQL clause Flow renderer
6. deterministic Explain copy
7. Line/time-series support
8. evaluate additional Bklit-inspired visuals only when result-shape rules require them
