# CoQuery BI Result Intelligence

Date: 2026-08-30
Status: product/UX baseline for the next result-view slice

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

The next result view should preserve the raw result while adding a deterministic interpretation layer.

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

The first slice must not require an LLM.

Inputs:

- returned column names
- returned values/types
- row count
- submitted SQL text
- practice problem metadata when available

Outputs:

- `shape`
- `recommended_view`
- `recommended_visual`
- `confidence`
- `reason`
- `dimensions`
- `measures`
- `flow_steps`

Proposed shapes:

- `single_metric`
- `category_measure`
- `time_series`
- `part_to_whole`
- `numeric_relationship`
- `stage_funnel`
- `source_target_flow`
- `geographic_measure`
- `tabular`
- `unknown`

## Initial visual recommendation rules

| Result shape | Default view | Visual | Guardrail |
| --- | --- | --- | --- |
| one category + one numeric measure | Visual | Bar | use Table when categories are too numerous or labels are unstable |
| time/date + numeric measure | Visual | Line | preserve chronological order |
| small category set representing a meaningful total | Visual | Ring/Pie | only when part-to-whole is explicit; prefer Bar otherwise |
| two numeric fields per observation | Visual | Scatter | only when rows represent observations rather than aggregates |
| ordered stage + count/value | Visual | Funnel | stage order must be explicit |
| source + target + numeric value | Flow | Sankey | exact source/target/value columns required |
| geography key/name + numeric measure | Visual | Choropleth | later slice; requires an explicit supported geography mapping |
| single current value + explicit target/range | Visual | Gauge | do not infer a target |
| mixed/raw records | Table | none | explain that a table is the truthful default |

No chart should be selected solely because numeric values exist.

## SQL transformation Flow

Flow has two meanings and they must remain distinct.

### A. SQL reasoning flow — first implementation target

Example:

`customers -> WHERE active = 1 -> GROUP BY region -> COUNT(*) -> ORDER BY count DESC -> result`

This teaches how SQL transforms data.

The first slice can derive a simple sequence from explicit clauses:

- FROM / JOIN
- WHERE
- GROUP BY
- aggregate expressions
- HAVING
- ORDER BY
- LIMIT

Unknown or unsupported syntax stays unknown; do not invent an interpretation.

### B. Returned-data flow — later visual target

If the result itself has an explicit `source`, `target`, `value` contract, CoQuery may render a Sankey-style flow.

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

Minimum proof:

- Table view renders real columns/rows instead of JSON-string rows
- deterministic classifier selects `bar` for a clear category + measure result
- ambiguous result stays `table`
- SQL Flow displays explicit clause steps for a supported SELECT/GROUP BY query
- Explain states the recommendation reason
- no external AI call
- no React dependency
- exact raw result remains inspectable

A first chart renderer may be limited to Bar. Line can follow immediately after the contract is stable.

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

## Next implementation order

1. `ResultShape` classifier + contract tests
2. real Table renderer
3. Bar renderer for `category_measure`
4. SQL clause Flow renderer
5. deterministic Explain copy
6. Line/time-series support
7. evaluate additional Bklit-inspired visuals only when result-shape rules require them

