# CoQuery Result View Accessibility Baseline — 2026-09-03

Status: implemented on Draft PR #18

## Goal

Make the approved result surface

`Table | Visual | Flow | Explain`

usable without a mouse while preserving Table as canonical evidence and preserving safe fallbacks when a derived view is unavailable.

## Interaction contract

The result switcher follows an ARIA tab pattern:

- `role=tablist` on the result-view switcher
- one `role=tab` per available view
- one `role=tabpanel` per rendered view
- `aria-controls` / `aria-labelledby` connect each tab and panel
- exactly one tab is selected and keyboard-tabbable at a time
- the selected panel is focusable; inactive panels are hidden

Keyboard behavior:

- `ArrowRight` / `ArrowDown`: next available view, wrapping at the end
- `ArrowLeft` / `ArrowUp`: previous available view, wrapping at the start
- `Home`: first available view
- `End`: last available view
- clicking a tab activates the same view

The tabs use automatic activation because each view is already present locally and switching does not trigger network work.

## Availability and fallback

View order is deterministic:

1. Table
2. Visual
3. Flow
4. Explain

Unavailable derived views are omitted rather than disabled. Examples:

- a tabular result may have no Visual tab
- SQL without recognized flow steps may have no Flow tab
- Table remains available for every successfully rendered practice-query result

The default selected view is Table. This keeps the exact returned rows as the first evidence surface.

## No-JS / partial-JS boundary

The base Table and existing result sections are rendered independently of the switcher. CSS does not hide result sections by default.

Therefore, if the view-switching enhancement fails to load, the existing Table/Visual/Flow/Explain content remains visible rather than disappearing behind an inaccessible control.

If a chart renderer refuses an unsafe result, no Visual tab is created and Table remains usable.

## Accessibility details

- Korean and English tab labels follow the current language selector.
- `:focus-visible` provides a visible keyboard focus ring for tabs and panels.
- mobile tab rows may scroll horizontally instead of shrinking labels below usable touch targets.
- tab buttons have a minimum touch height of 40px desktop / 44px mobile.
- chart accessibility text and Query Graph textual descriptions remain inside their existing panels.
- the switcher does not alter query result data, ResultShape classification, chart recommendation, or SQL flow metadata.

## Implementation

Files:

- `app_shell/terminal_shell_prototype/practice-result-views.js`
- `app_shell/terminal_shell_prototype/practice-result-views.css`
- `app_shell/terminal_shell_prototype/practice_result_views_smoke.js`
- `app_shell/terminal_shell_prototype/pwa-runtime.js`
- `app_shell/terminal_shell_prototype/service-worker.js`
- `.github/workflows/baseline.yml`

The PWA cache moves to `coquery-pwa-v6` and includes the view-switching JS/CSS while keeping `/api/*` outside the service-worker cache path.

## Regression contract

Executable smoke coverage verifies:

- deterministic view order
- omission of unavailable views
- Table-only fallback
- Arrow key wrapping
- Home / End behavior
- unrelated keys do not move selection
- empty tab lists fail safely

The existing BI, SQL Dialect Learning, learner-flow, PWA, and PostgreSQL gates remain required.

## Out of scope

- no new BI chart type
- no Execution Graph
- no nested Query Graph semantics
- no external AI dependency
- no production deployment in this slice
- browser/device screen-reader evidence remains a separate release QA activity

## Next gate

After CI is green, review whether the BI first slice is complete enough to merge PR #18 or whether the local/advanced command runtime should receive the same additive `result_intelligence` metadata before merge.
