# CoQuery User Flow QA — 2026-08-28

## Scope

Review the learning-first user journey after the first-run, focused-practice, learning-path, and 24-problem curriculum changes.

Primary journey:

`Home -> Learning path -> Problem -> Run/grade -> Next problem or learning path`

## Findings fixed in this phase

### P0 — Problem-list return did not reliably restore the learning path

The focused practice screen had its own `Problem list` button. It exited practice focus, but did not explicitly restore `data-learning-path=true`. Because learning-path CSS only exposes the learning-path block when that mode is active, users could fall back into the terminal-oriented surface instead of the intended curriculum view.

Fix: route the practice `Problem list` action through `openPracticeLearningPath()`, which exits focus mode, enables learning-path mode, refreshes progress, and scrolls to the learning-path block.

### P0 — Correct answer had no direct continuation

After a correct grade, the user had to manually leave the problem and find the next incomplete problem.

Fix: add a primary `Next problem` action to successful grade results. It reads the existing `practice_attempts` history and opens the next incomplete problem. When all problems are complete, it returns to the learning path.

### P0 — Schema and attempt results were hidden in focus mode

The focused-practice CSS hides terminal blocks unless they are marked as the active practice or feedback block. `practice_schema`, `practice_attempts`, and `practice_feedback` were not classified as visible focus-mode results, so their buttons could execute successfully while the result remained invisible.

Fix: classify these commands as `practice-feedback-block practice-support-result` while focus mode is active.

## Behavior preserved

- SQL grading and expected-answer comparison
- 24-problem curriculum and existing problem IDs
- attempt history and progress calculation
- Training / Production Assist boundary
- provider configuration
- advanced terminal workspace
- PostgreSQL smoke scope

## Acceptance criteria

- Home can enter or resume learning.
- Problem bank opens the learning-path view, not a raw terminal list.
- Focused practice keeps schema, attempts, and feedback visible when requested.
- Correct answers expose a direct Next problem action.
- Next problem skips already-completed problems.
- Completing the final incomplete problem returns to the learning path.
- KR/EN labels update for the new navigation actions.
- Existing advanced functionality remains available outside learning focus.

## Verification

`user_flow_qa_smoke.py` locks the navigation contracts into baseline CI alongside the existing practice-focus, learning-path, and curriculum smokes.

This phase is static/contract QA through the remote GitHub execution surface. Full pointer/keyboard/browser visual QA should still be done against a running local shell before treating the interface as release-polished.
