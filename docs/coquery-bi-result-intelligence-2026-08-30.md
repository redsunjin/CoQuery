# CoQuery BI Result Intelligence

Date: 2026-08-30
Status: product/UX direction approved; implementation not yet started

## Product Goal

CoQuery should not stop at an Excel-like result grid.

The query result surface should teach the user how to **read data**, not only how to write SQL.

Target result experience:

`Query -> Result Intelligence -> Table | Visual | Flow | Explain`

This keeps the table as the source-of-truth view while adding BI-style interpretation and SQL-learning context.

## Four Result Views

### 1. Table

Purpose:

- preserve exact rows/columns returned by SQL
- support correctness checks
- remain the canonical raw-result representation

The table is never removed just because a chart is available.

### 2. Visual

Purpose:

- turn compatible result shapes into an immediately readable chart
- teach when a chart is appropriate for a given SQL result

Initial deterministic recommendation rules:

| Result shape / SQL signal | Preferred visual | Learning intent |
| --- | --- | --- |
| category + numeric aggregate | Bar | compare groups |
| ordered date/time + numeric measure | Line / Area | understand trend |
| small category set + additive share | Pie / Ring | understand composition |
| two numeric measures per row | Scatter | understand relationship |
| stage + count/rate | Funnel | understand conversion stages |
| source + target + numeric weight | Sankey | understand movement/flow |
| one bounded KPI + target/range | Gauge | understand status against a reference |
| geographic key + measure | Choropleth | understand spatial distribution |

If the result shape does not clearly support a truthful visual, CoQuery must stay on Table instead of forcing a chart.

## 3. Flow

`Flow` has two different learning uses.

### Data flow

For compatible datasets, show movement such as:

`source -> intermediate -> destination`

Sankey-style rendering is appropriate when the query result explicitly contains weighted source/target relationships.

### SQL transformation flow

For SQL learning, visualize how the query transforms data:

`FROM customers -> WHERE active = 1 -> GROUP BY region -> COUNT(*) -> result`

This is not a replacement for an execution plan. It is a beginner-facing semantic explanation of the SQL structure.

The first implementation should support simple clauses only:

- FROM
- JOIN
- WHERE
- GROUP BY
- aggregate expressions
- ORDER BY
- LIMIT

Unsupported or ambiguous SQL should fall back to textual explanation instead of inventing a flow.

## 4. Explain

Explain should answer three questions:

1. **What did this SQL do?**
2. **What does the returned data mean?**
3. **Why is this visual appropriate or not appropriate?**

The first baseline should be deterministic/rule-first and derived from the SQL structure + result metadata.

AI-generated interpretation may be added later through the existing Context-to-Prompt Handoff direction. It must not become a prerequisite for basic result explanation.

## Result Intelligence Pipeline

Recommended architecture:

1. `ResultShapeAnalyzer`
   - inspect column names/types/result cardinality
   - infer category/time/numeric/share/source-target candidates
2. `SqlStructureAnalyzer`
   - identify supported SQL clauses without executing new SQL
3. `VisualizationPolicy`
   - return `recommended`, `alternative`, or `table_only`
   - include a reason and confidence
4. `ResultViewModel`
   - normalize data for Table / Visual / Flow / Explain
5. renderer adapters
   - keep the view model independent from a specific chart library

The policy layer should be testable without a browser or chart package.

## Bklit UI Reference

Reference repository:

- `bklit/bklit-ui`

Useful reference components include:

- Area
- Bar
- Line
- Pie / Ring
- Scatter
- Funnel
- Sankey
- Gauge
- Choropleth
- Composed charts

Bklit UI's chart components are MIT licensed, but its Studio is proprietary. CoQuery may reference or use compatible chart components according to their license, but must not copy/repackage the proprietary Studio.

Important implementation constraint:

- current CoQuery PWA is static HTML/CSS/JavaScript
- Bklit UI chart components are React-oriented

Therefore the first slice should **not** migrate CoQuery to React only to gain charts.

The first implementation decision should compare:

A. small native/SVG/Canvas chart renderer for the current PWA
B. a lightweight framework-agnostic chart dependency
C. isolated React chart island only if the integration cost is justified

The visualization policy and result model must remain renderer-agnostic so this choice can change later.

## MVP Slice

The first implementation should be intentionally small:

`practice_query result -> Table | Visual | Explain`

Supported automatic visuals:

- Bar
- Line

Supported explain behavior:

- describe selected columns
- describe filters/grouping/aggregation when detectable
- explain why Bar or Line was recommended

Flow/Sankey/Pie/Scatter/Gauge/Map remain documented follow-up work until the first two visual types are proven usable.

## UX Rules

- Table is always available.
- Never silently replace rows with a visualization.
- Show why a visualization was selected.
- Allow the learner to switch views manually.
- Do not infer business meaning that is not present in column names/SQL/result metadata.
- Never imply correlation, causation, significance, or anomaly without evidence.
- Zero is data, not missing data.
- Missing/null values must remain visible in explanation and visualization handling.
- Large result sets should be summarized only when the aggregation rule is explicit and visible.

## Acceptance for the First Implementation Slice

A result is ready for release when:

- the same result shape produces the same recommendation deterministically
- Table remains unchanged and authoritative
- Bar/Line rendering uses only returned query data
- unsupported shapes fall back to Table without error
- Explain states the SQL transformation without inventing business facts
- view switching works on desktop and mobile PWA layouts
- baseline learner-flow tests stay green

## Product Positioning

This creates a stronger product loop:

`Learn SQL -> Query data -> See the shape -> Understand the meaning -> Improve the next query`

CoQuery therefore becomes more than an SQL editor or spreadsheet-like result viewer. It becomes a **learning-first data interpretation workspace** that connects SQL syntax, query results, BI visualization, and explanation in one flow.
