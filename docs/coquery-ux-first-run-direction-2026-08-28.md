# CoQuery First-Run UX Direction

Date: 2026-08-28
Status: Phase 1 implementation baseline

## Product Position

CoQuery should not present itself first as a terminal, provider configuration surface, or natural-language SQL generator.

The primary product path is:

**Learn -> Practice -> Apply -> Assist**

- **Learn**: understand SQL concepts through a concrete question.
- **Practice**: run SQL against the built-in practice dataset and receive grading/feedback.
- **Apply**: connect the same concepts to the user's own database.
- **Assist**: use natural-language, provider, schema-inspection, and Production Assist features when needed.

The existing CLI, Command API, provider, PostgreSQL, and Production Assist capabilities stay in scope. This UX change only changes when those capabilities are exposed.

## Problem

The current terminal shell exposes too many internal concepts on first entry:

- sessions
- command menu
- provider presets and setup
- schema inspection
- natural-language query
- practice
- production review
- Training / Assist mode
- provider readiness
- command input
- detail panel

This makes the user learn CoQuery's architecture before experiencing its value.

The practice system already provides the right beginner foundation: a built-in dataset, problems, hints, schema inspection, SQL execution, grading, attempts, wrong notes, and optional AI feedback. The first-run UX should promote this existing path rather than add another learning engine.

## Phase 1 UX Goal

A new user should be able to start a real SQL problem in less than 30 seconds without configuring a database or AI provider.

The home surface therefore exposes only three decisions:

1. **Start first problem** — open the first built-in practice problem immediately.
2. **Choose a problem** — open the existing practice problem bank.
3. **Advanced features** — enter the existing terminal/assist workspace without removing any capability.

## Home Surface

### Primary message

> 데이터로 직접 확인하며 SQL을 배워보세요.
>
> 별도 DB 연결이나 AI 설정 없이 샘플 데이터로 바로 시작할 수 있습니다.

### Primary action

`첫 문제 시작하기`

### Secondary actions

- `문제 선택`
- `고급 기능`

### What is hidden on Home

- session rail
- terminal command history
- command bar
- Training / Assist switch
- provider readiness
- detail panel
- command popover

These elements are not deleted. They reappear when the user enters the workbench.

## Workbench

After the user starts practice or chooses Advanced:

- the current terminal shell returns intact;
- practice blocks continue to use the existing Command API;
- schema inspection, grading, wrong-note review, providers, and Production Assist keep their existing contracts;
- a `Home` action returns to the simplified learning home without discarding the current session DOM state.

## Problem Bank Direction

The existing `practice_packs/sql_basics.json` is the canonical base. Expand it rather than creating a second question system.

Recommended progression:

### Level 1 — Find data
- SELECT
- requested columns
- ORDER BY

### Level 2 — Filter data
- WHERE
- AND / OR
- LIKE / IN
- date conditions

### Level 3 — Connect data
- JOIN
- foreign keys
- multi-table questions

### Level 4 — Summarize data
- COUNT
- SUM
- AVG
- GROUP BY

### Level 5 — Work scenarios
- high-value paid orders
- unresolved support requests
- regional sales summaries
- recent-customer activity

### Level 6 — My Data bridge
Repeat a learned task against a user-selected database/schema. This is the transition from learning product to practical data assistant.

## Phase 1 Implementation

This slice deliberately avoids backend changes.

- Add a learning-first Home panel to the existing shell.
- Default the initial Command API command to `practice_list` when no runtime command is supplied.
- Keep the generated practice list hidden while Home is active.
- `Start first problem` fetches the existing practice list and opens the first problem through the current `practiceStartResult` flow.
- `Choose a problem` reveals the existing practice list.
- `Advanced features` reveals the existing workbench.
- Add a `Home` control to return to the simplified entry surface.

## Non-Goals

Phase 1 does not:

- replace the terminal shell;
- redesign the practice engine;
- add a second problem-bank format;
- modify SQL grading rules;
- modify provider contracts;
- broaden PostgreSQL support;
- change Production Assist safety policy.

## Success Criteria

1. First launch does not require knowledge of Provider, CLI, DB URI, schema detail, or Production Assist.
2. A user can reach an editable SQL answer field from the first screen with one primary action.
3. Existing advanced capabilities remain reachable without data-model or backend migration.
4. Existing terminal shell smoke contracts remain valid.
5. Future UI additions must answer: **Does this need to be visible before the user's first successful practice query?** If not, keep it out of Home.

## Next UX Slices

After Phase 1 is validated:

1. learning progress / resume state;
2. problem categories and difficulty navigation;
3. clearer schema/data preview inside the problem workspace;
4. feedback hierarchy for correct / incorrect / hint / explanation;
5. My Data bridge;
6. only then revisit provider/natural-query onboarding.
