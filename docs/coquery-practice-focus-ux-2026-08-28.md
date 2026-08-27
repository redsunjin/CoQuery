# CoQuery Practice Focus UX

Date: 2026-08-28

## Decision

Phase 2 simplifies the practice workspace without changing the SQL practice engine.

The learner-facing sequence is:

**Problem -> Write SQL -> Run and check -> Feedback**

Everything else is secondary.

## Problem observed after Phase 1

The first-run Home is now simpler, but opening a problem still exposes too much implementation detail at once:

- terminal command header
- CLI-equivalent command
- schema button
- attempt history button
- hint content
- terminal action chips
- surrounding session / provider / command UI

These are useful capabilities, but they compete with the actual learning task.

## Phase 2 UX rules

### 1. Enter a focused workspace when a problem opens

While a `practice_start` flow is active:

- hide the session rail
- hide the detail panel
- hide the bottom command bar
- hide command-menu and detail controls
- keep Home and language controls available

### 2. Keep the problem and editor visible first

Primary visual order:

1. problem title and prompt
2. SQL editor
3. primary `Run and check` action
4. secondary learning tools
5. status / feedback

### 3. Progressive disclosure for learning aids

Hint is hidden by default and exposed through `Show hint`.

Schema, attempt history, and problem list remain available as secondary actions.

### 4. Hide implementation details, not capabilities

The CLI-equivalent command and terminal block chrome are hidden only in focused practice mode. They are still available in the advanced terminal workspace.

### 5. Keep results compact

`practice_query` and `practice_grade` outputs remain visible after submission, but their generic terminal header, action chips, and CLI-equivalent line are hidden while practice focus is active.

## Implementation boundary

This phase is implemented as an additive presentation layer:

- `practice-focus.css`
- `practice-focus.js`
- loader hook in `onboarding.js`

No changes are required to:

- `practice_list`
- `practice_query`
- `practice_grade`
- `practice_attempts`
- Command API contracts
- SQL grading
- provider handling
- Production Assist safety

## Acceptance criteria

- Opening a practice problem enters focused mode.
- Problem prompt and SQL editor dominate the screen.
- Hint is hidden until requested.
- Schema, attempts, and problem list remain reachable.
- CLI-equivalent output is not shown in focused mode.
- Query and grading feedback remain visible after submit.
- Home exits focused mode.
- KR/EN changes update the focused-workspace control copy without duplicating controls.
- Existing advanced terminal functionality remains unchanged outside focused mode.

## Next product step

After browser QA, Phase 3 should improve the problem bank itself:

- concept / difficulty grouping
- progress and completion state
- continue-learning entry point
- scenario-based business problem packs
- bridge from sample data to `My Data`
