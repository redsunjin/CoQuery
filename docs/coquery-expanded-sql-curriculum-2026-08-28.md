# CoQuery Expanded SQL Curriculum — 2026-08-28

## Decision

Expand the built-in `sql_basics` practice pack from 5 problems to 24 problems while keeping the existing sample dataset and grading model.

The goal is not to maximize the number of SQL exercises. The goal is to create a short but coherent path from first SELECT queries to realistic business questions.

## Curriculum shape

### 1. Find data — 5 problems

Focus:
- `SELECT`
- choosing columns
- `ORDER BY`
- `LIMIT`

Problems:
1. `basic_select_customers`
2. `customer_names_segments`
3. `orders_chronological`
4. `ticket_priority_list`
5. `largest_orders`

Outcome: the learner can inspect a table and return the requested data in a predictable order.

### 2. Filter data — 7 problems

Focus:
- `WHERE`
- `AND`
- `OR`
- `IN`
- `LIKE`
- date ranges

Problems:
1. `paid_large_orders`
2. `open_high_tickets`
3. `seoul_customers`
4. `march_orders`
5. `paid_or_pending_orders`
6. `selected_regions`
7. `customer_name_contains`

Outcome: the learner can translate ordinary conditions into SQL filters.

### 3. Connect tables — 5 problems

Focus:
- foreign-key relationships
- `JOIN`
- combining customer, order, and support data

Problems:
1. `paid_order_customers`
2. `order_customer_regions`
3. `ticket_customer_names`
4. `paid_order_segments`
5. `open_tickets_customer_regions`

Outcome: the learner understands why related business facts live in different tables and how to connect them.

### 4. Summarize data — 4 problems

Focus:
- `GROUP BY`
- `COUNT`
- `SUM`
- aggregation after filtering and joining

Problems:
1. `paid_orders_by_region`
2. `order_count_by_status`
3. `paid_total_by_customer`
4. `ticket_count_by_priority`

Outcome: the learner can answer questions that require totals and grouped summaries rather than row-by-row inspection.

### 5. Solve business questions — 3 problems

These problems deliberately combine concepts instead of introducing one isolated keyword at a time.

#### `monthly_paid_sales`

Question: How much paid sales did we make each month, and how many paid orders produced that sales amount?

Concepts:
- filtering
- date transformation
- grouping
- count
- sum

#### `high_value_paid_customers`

Question: Which customers have generated at least 200,000 KRW in paid orders?

Concepts:
- join
- filtering
- grouping
- sum
- `HAVING`

#### `open_support_load_by_region`

Question: Which regions currently carry the largest open-support workload?

Concepts:
- join
- filtering
- grouping
- count
- business prioritization

Outcome: the learner practices converting an operational question into a multi-step SQL query.

## Why 24 problems

Twenty-four is intentionally small enough to finish but large enough to establish repetition across the core concepts.

The current target is:

`5 foundations + 7 filters + 5 joins + 4 summaries + 3 business scenarios = 24`

Do not expand to 50 or 100 problems simply to make the bank look large. New problems should be added only when they introduce useful variation, reinforce a weak concept, or represent a real data-work pattern.

## Existing data model remains unchanged

The practice dataset remains:

- `customers`
- `orders`
- `support_tickets`

No new database, server, account system, or paid data source is required.

This is deliberate. Early learning should test SQL reasoning rather than environment setup.

## Backward compatibility

The original five problem IDs remain available:

- `basic_select_customers`
- `paid_large_orders`
- `paid_order_customers`
- `paid_orders_by_region`
- `open_high_tickets`

Existing attempt history continues to map to the same IDs, so progress already recorded for those problems remains meaningful.

## Learning-path UI integration

The first four units continue to use the existing concept-based learning-path grouping.

Problems tagged with the `business` concept are routed to a fifth unit:

`5. 업무 질문 해결하기 / Solve business questions`

This is implemented as an additive curriculum layer so the terminal, Practice Command API, and grading engine remain unchanged.

## Verification contract

`curriculum_smoke.py` checks:

- exactly 24 problems exist
- problem IDs are unique
- the original five problem IDs remain
- exactly three business scenarios are present
- required concepts are represented
- every problem's `expected_sql` executes successfully against the built-in SQLite dataset
- every `expected_sql` is graded as correct
- the fifth business unit is connected to the learning-path UI

The smoke is included in baseline CI.

## Content quality rules for future additions

A new problem should have:

1. a concrete question with one primary learning goal
2. deterministic result ordering when row order matters
3. a concise hint that does not reveal the full answer
4. an `expected_sql` that executes on the built-in dataset
5. concepts that correctly place the problem in the learning path
6. a reason to exist beyond being a cosmetic variation of another problem

For advanced problems, prefer realistic combinations such as:

- date + aggregation
- join + aggregation
- filter + group + having
- operational prioritization questions

## Not included in this phase

- changing the grading algorithm
- adding user accounts or cloud progress storage
- replacing the sample dataset
- connecting the user's real database automatically
- AI-generated problem creation
- broad PostgreSQL/MySQL expansion

## Recommended next product step

After this curriculum is validated in actual use, the next usability step should be **content localization and the bridge from practice to the user's own data**.

The learner should eventually be able to finish a practice pattern and choose:

`이 유형을 내 데이터로 해보기`

That transition should reuse the skills learned here rather than turning into a separate SQL tool experience.
