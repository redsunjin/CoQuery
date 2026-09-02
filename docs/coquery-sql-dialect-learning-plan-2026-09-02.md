# CoQuery SQL Dialect Learning Plan

Date: 2026-09-02
Status: Proposed implementation slice
Branch: `feat/sql-dialect-learning`

## 1. Why this exists

CoQuery teaches SQL before it teaches a specific database product. Learners should first understand the portable concepts — `SELECT`, `WHERE`, `JOIN`, `GROUP BY`, `ORDER BY` — and then learn that real database engines sometimes express the same intent differently.

The feature goal is:

> Learn common SQL first, then reveal database-specific differences only when they help the learner.

This is not a PostgreSQL course, a MySQL course, or a compatibility promise.

## 2. Product model

Add an optional **DB differences** layer to practice and result views.

Default learner flow:

`Problem -> Write SQL -> Run/Grade -> Feedback`

Optional expansion:

`DB differences -> PostgreSQL | MySQL | SQLite`

The beginner path stays uncluttered. Database-specific material is secondary and opened explicitly by the learner.

Suggested labels:

- Korean: `DB별 차이 보기`
- English: `Compare DB syntax`

## 3. Learning outcomes

A learner should be able to understand:

1. which parts of a query are broadly portable SQL,
2. which parts are database-specific syntax or behavior,
3. how the same intent can be expressed in PostgreSQL, MySQL, and SQLite,
4. whether an example is only a reference comparison or actually verified against an engine.

## 4. Initial dialect scope

### PostgreSQL

Use as the first real-world comparison target because CoQuery already has a narrow PostgreSQL smoke path.

### MySQL

Include as a **reference comparison** in the first slice. Do not claim runtime compatibility until a MySQL execution baseline exists.

### SQLite

Treat as the current practice baseline and use it to explain why a learner's practice query may differ from a production database.

## 5. Truthfulness levels

Every dialect example must carry one of these states:

- `common` — portable SQL concept with no material dialect difference in the example
- `reference` — documented syntax comparison, not executed by CoQuery against that engine
- `verified` — executed by a CoQuery test/smoke environment against that engine

Never show `verified` for MySQL until a MySQL test environment is added.

## 6. First comparison topics

The first content pack should focus on high-value differences rather than cataloging every database feature.

| Intent | PostgreSQL | MySQL | SQLite | Priority |
| --- | --- | --- | --- | --- |
| String concatenation | `||` | `CONCAT()` | `||` | P0 |
| Current date/time | PostgreSQL functions | MySQL functions | SQLite date/time functions | P0 |
| Date arithmetic | interval expressions | `DATE_ADD` / `DATE_SUB` | date modifiers | P0 |
| Limit rows | `LIMIT` | `LIMIT` | `LIMIT` | P0, commonality lesson |
| Boolean representation | native boolean | boolean aliases / numeric behavior | integer-oriented behavior | P1 |
| Upsert | `ON CONFLICT` | `ON DUPLICATE KEY UPDATE` | `ON CONFLICT` variants | P1 |
| Auto-generated IDs | identity/serial family | auto increment | integer primary key behavior | P1 |
| Case-insensitive matching | `ILIKE` | collation-dependent patterns | collation / `LIKE` behavior | P1 |

The examples must explain **intent first**, then syntax.

## 7. UX design

### Practice feedback

After grading, show a small secondary action:

`DB별 차이 보기`

Expanded view:

- **Common idea** — what the SQL is trying to do
- **SQLite** — current practice form
- **PostgreSQL** — equivalent or notable difference
- **MySQL** — equivalent or notable difference
- **Why it differs** — one short explanation
- **Verification badge** — Common / Reference / Verified

### Example

Intent: join first and last name.

```sql
-- PostgreSQL / SQLite
SELECT first_name || ' ' || last_name AS full_name
FROM users;
```

```sql
-- MySQL
SELECT CONCAT(first_name, ' ', last_name) AS full_name
FROM users;
```

Explanation: the SQL concept is the same; the string-concatenation function/operator differs by engine.

## 8. Architecture

The first slice should be deterministic and content-driven. No LLM is required.

Suggested model:

```text
DialectLesson
  id
  concept
  intent
  commonExplanation
  variants[]
    engine
    sql
    explanation
    verificationState
  relatedProblemIds[]
```

Suggested modules:

- `DialectCatalog` — versioned learning content
- `DialectMatcher` — maps curriculum concepts/problems to relevant comparisons
- `DialectComparisonView` — renders optional comparison UI
- `DialectVerificationState` — makes proof level explicit

Do not build a SQL transpiler in this slice.

## 9. Relationship to BI/result interpretation

This feature answers **"Would this SQL look different in another database?"**

The separate result-intelligence direction answers **"What does this result mean?"** through Table / Chart / Flow / Explain.

The two features can meet later, but they should stay separate in the first implementation so the learner can distinguish syntax learning from data interpretation.

## 10. Delivery phases

### Phase A — learning contract and content baseline

- add the dialect-learning data model
- add 4 P0 comparison topics
- add KR/EN copy
- expose `DB별 차이 보기` only where a comparison exists
- show verification state explicitly
- add deterministic tests for the catalog and problem mapping

### Phase B — curriculum integration

- map relevant problems to dialect lessons
- add comparison cards to practice feedback
- track whether learners open comparisons only if product evidence later requires analytics

### Phase C — engine-backed verification

- expand PostgreSQL verified examples where smoke coverage can prove behavior
- create a MySQL test baseline before any `verified` MySQL badge
- record engine/version assumptions for behavior-sensitive examples

## 11. Acceptance criteria for first implementation

- beginner flow is unchanged until the learner opens `DB별 차이 보기`
- at least 4 deterministic comparison lessons exist
- PostgreSQL/MySQL/SQLite variants are clearly labeled
- MySQL examples are not presented as runtime-verified
- unsupported or uncertain behavior is not guessed
- comparison content is available in Korean and English
- baseline CI remains green
- PostgreSQL smoke remains truthful and independent

## 12. Non-goals

Not in this slice:

- full SQL dialect transpilation
- automatic conversion of arbitrary SQL between engines
- full PostgreSQL compatibility certification
- working MySQL runtime support
- replacing SQLite as the practice baseline
- making dialect knowledge mandatory for beginners

## 13. Proposed roadmap position

This should enter the roadmap as **P1 Learning Quality / SQL Dialect Learning**, after the stable learning/PWA baseline and without blocking AI handoff or mobile packaging.

A small Phase A implementation can proceed independently because it is local, deterministic, and does not require a new backend.