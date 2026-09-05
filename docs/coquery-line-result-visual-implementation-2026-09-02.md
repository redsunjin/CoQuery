# CoQuery deterministic Line Result Visual implementation — 2026-09-02

## Status

Implemented on active Draft PR #18 (`feat/bi-result-intelligence`).

This slice adds the first time-series visual while preserving the existing product principle:

**SQL as Visual Data Transformation**

The visible result-understanding surface remains:

`Table | Visual | Flow | Explain`

Table remains canonical evidence.

## Scope

The Line visual is rendered only when the deterministic result classifier has already proven:

- `shape == "time_series"`
- `recommended_visual == "line"`
- exactly one temporal dimension
- exactly one numeric measure
- complete returned values
- a safely ascending or descending temporal sequence

The frontend repeats the safe temporal-order check before rendering so stale or inconsistent metadata cannot force an unordered Line chart.

Supported temporal keys intentionally mirror the classifier baseline:

- finite numeric temporal values
- `YYYY`
- `YYYY-M` / `YYYY-MM`
- `YYYY-M-D` / `YYYY-MM-DD`
- the same year/month/day forms using `.` or `/`

Unknown temporal text remains Table-only.

## Rendering contract

Implementation files:

- `app_shell/terminal_shell_prototype/practice-result-visual.js`
- `app_shell/terminal_shell_prototype/practice-result-visual.css`
- `app_shell/terminal_shell_prototype/practice_result_visual_smoke.js`

The renderer:

- uses every returned row in exact returned order
- never sorts or samples the result
- connects numeric measures with a lightweight SVG path
- shows first/last temporal labels
- shows exact returned minimum and maximum measure values
- uses the returned min/max only for vertical geometry
- keeps exact cell values available in the canonical Table
- does not mutate `columns`, `rows`, or `row_count`
- does not require React, Bklit runtime code, or an external AI provider

## Time-spacing truthfulness boundary

The current classifier proves ordering, not exact elapsed-time distance for every supported temporal representation.

Therefore the horizontal point spacing deliberately represents **returned temporal sequence**, not inferred elapsed-time magnitude.

The visible evidence copy states this explicitly. CoQuery does not pretend that two adjacent points are separated by equal real-world time when that is not proven.

A future continuous-time axis requires a separate explicit temporal-distance contract.

## Refusal behavior

Line is not rendered when any of these is true:

- result is not a successful `practice_query`
- classifier does not recommend Line
- dimension/measure cardinality is not exactly one each
- fewer than two rows are returned
- temporal values cannot be parsed by the safe contract
- returned temporal sequence is neither ascending nor descending
- a temporal value is null
- a measure is null, non-numeric, boolean, or non-finite

In those cases the existing Table remains available and no chart is invented.

## Regression proof contract

`practice_result_visual_smoke.js` verifies:

- ordered time series -> Line model
- exact returned temporal order is preserved
- normalized x/y geometry is deterministic
- exact returned min/max become the vertical domain
- descending temporal order remains valid and is not resorted
- unordered temporal rows are rejected even if stale metadata says `line`
- null measures are rejected
- Bar metadata cannot create a Line
- returned rows are not mutated

Existing Bar tests remain in the same smoke so Line work cannot silently break the first Result Visual.

The focused-practice smoke also protects Line model/render/CSS markers, and the PWA shell smoke protects the cache-version boundary.

## PWA cache

The app-shell cache version advances to `coquery-pwa-v4` so existing installed PWAs do not keep the previous Bar-only `practice-result-visual.js/css` assets.

`/api/*` remains outside the service-worker cache path.

## Out of scope

This slice does not add:

- Area chart
- Ring/Pie
- Scatter
- Funnel
- Sankey
- Gauge
- Choropleth
- continuous elapsed-time x-axis inference
- Execution Graph
- React migration
- external AI interpretation

## Next gate

After this Line baseline is green, close the first BI result-understanding slice by localizing the remaining backend-English recommendation reason text and defining the accessible view-selection behavior before expanding to more chart types.
