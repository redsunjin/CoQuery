# CoQuery iOS Training Runtime Contract

Date: 2026-07-08

Goal:

```text
Launch Goal 3: iOS Training Runtime Contract
```

## Purpose

This contract defines the minimum Training Mode runtime that the iOS app must implement without starting the current Python local server.

The Python implementation remains the reference behavior, but iOS must be able to run the training app locally:

```text
iOS Training App
  -> Capacitor WebView shell
  -> Training Runtime adapter
  -> bundled practice packs
  -> local SELECT-only query executor
  -> local attempt storage
  -> bilingual help catalog
```

## Scope

In scope for the first iOS runtime:

- `practice_list`
- `practice_schema`
- `practice_query`
- `practice_grade`
- `practice_attempts`
- `help_catalog`
- `command_explain`
- `term_explain`

Out of scope for the first iOS runtime:

- production DB connection
- `natural`
- provider setup and provider tests
- cloud LLM feedback
- local LLM inference
- SQL generation for operational databases
- write commands
- multi-user sync

## Runtime Decision

The first iOS Training Runtime should use a TypeScript adapter behind the same command shape as the current local Command API.

Recommended implementation sequence:

1. Create `training_runtime` as a portable TypeScript module.
2. Load practice packs from bundled JSON files.
3. Execute practice SQL through a local SQLite-compatible runtime in the app.
4. Store attempts locally on device.
5. Keep the current Python `sql_cli.command_api.run_command` as the reference test oracle.

Preferred first query execution strategy:

```text
Capacitor WebView
  -> TypeScript Training Runtime
  -> bundled sql_basics JSON
  -> SQLite-compatible JS/WASM executor
```

Reason:

- avoids embedding a Python server in the iOS app
- keeps the existing HTML/JS terminal shell reusable
- keeps the first TestFlight build focused on Training Mode
- allows later replacement with native SQLite if performance or App Store review needs it

Fallback strategy:

```text
Capacitor native plugin
  -> iOS SQLite
  -> TypeScript bridge
```

Use the fallback only if the JS/WASM executor cannot run reliably in WKWebView.

## Command Envelope

Every training command should use this envelope:

```json
{
  "command": "practice_list",
  "args": {},
  "context": {
    "lang": "ko"
  }
}
```

Every command result should use this envelope:

```json
{
  "ok": true,
  "command": "practice_list",
  "block_type": "practice_list",
  "cli_equivalent": "python main.py --command practice_list --format json",
  "actions": ["copy", "start_practice", "show_schema"],
  "data": {},
  "error": null
}
```

Failure envelope:

```json
{
  "ok": false,
  "command": "practice_query",
  "block_type": "practice_query_result",
  "cli_equivalent": "python main.py --command practice_query --sql \"SELECT ...\" --format json",
  "actions": ["copy", "grade", "save_attempt"],
  "data": {},
  "error": {
    "code": "practice_sql_error",
    "message": "error text",
    "details": {}
  }
}
```

The iOS shell may keep `cli_equivalent` as a trust hint even though iOS will not execute Python.

## Block Types And Actions

| Command | block_type | actions |
| --- | --- | --- |
| `practice_list` | `practice_list` | `copy`, `start_practice`, `show_schema` |
| `practice_schema` | `practice_schema` | `copy`, `insert_template`, `start_practice` |
| `practice_query` | `practice_query_result` | `copy`, `grade`, `save_attempt` |
| `practice_grade` | `practice_grade` | `copy`, `retry`, `save_wrong_note` |
| `practice_attempts` | `practice_attempts` | `copy`, `review_wrong_notes` |
| `help_catalog` | `help_catalog` | `copy`, `explain_command`, `explain_term` |
| `command_explain` | `command_help` | `copy`, `insert_example`, `show_terms` |
| `term_explain` | `term_help` | `copy`, `show_related_commands` |

## Practice Pack Contract

Practice packs are bundled JSON files under:

```text
practice_packs/*.json
```

Required pack shape:

```json
{
  "id": "sql_basics",
  "title": "SQL Basics Practice Pack",
  "description": "text",
  "dataset": {
    "id": "commerce_support",
    "title": "Commerce Support Sample",
    "tables": []
  },
  "examples": [],
  "problems": []
}
```

Required table shape:

```json
{
  "name": "customers",
  "description": "text",
  "columns": [
    {"name": "id", "type": "INTEGER", "description": "Customer primary key"}
  ],
  "primary_key": ["id"],
  "foreign_keys": [
    {"column": "customer_id", "references_table": "customers", "references_column": "id"}
  ],
  "rows": [
    {"id": 1, "name": "Aster Foods"}
  ]
}
```

Required problem shape:

```json
{
  "id": "basic_select_customers",
  "title": "List all customers",
  "difficulty": "beginner",
  "prompt": "Return each customer id, name, and region ordered by id.",
  "concepts": ["select", "order_by"],
  "hint": "Start from the customers table.",
  "expected_sql": "SELECT id, name, region FROM customers ORDER BY id"
}
```

The first iOS runtime must bundle at least `practice_packs/sql_basics.json`.

## Command Contracts

### practice_list

Input:

```json
{
  "command": "practice_list",
  "args": {"pack": "sql_basics"},
  "context": {}
}
```

`pack` is optional. Default is `sql_basics`.

Output `data`:

Rows below are abbreviated for documentation; the runtime returns the complete result rows matching `row_count`.

```json
{
  "packs": [
    {
      "id": "sql_basics",
      "title": "SQL Basics Practice Pack",
      "description": "text",
      "dataset_id": "commerce_support",
      "table_count": 3,
      "problem_count": 5,
      "path": "practice_packs/sql_basics.json"
    }
  ],
  "selected_pack": "sql_basics",
  "problems": [
    {
      "id": "basic_select_customers",
      "title": "List all customers",
      "difficulty": "beginner",
      "prompt": "Return each customer id, name, and region ordered by id.",
      "concepts": ["select", "order_by"],
      "hint": "Start from the customers table."
    }
  ],
  "examples": [
    {"title": "Show paid orders", "sql": "SELECT ..."}
  ]
}
```

### practice_schema

Input:

```json
{
  "command": "practice_schema",
  "args": {"pack": "sql_basics", "table": "orders"},
  "context": {}
}
```

`pack` and `table` are optional.

Output `data`:

Rows below are abbreviated for documentation; the runtime returns the complete result rows in `actual.rows` and `expected.rows`.

```json
{
  "pack_id": "sql_basics",
  "dataset_id": "commerce_support",
  "dataset_title": "Commerce Support Sample",
  "table_count": 1,
  "tables": [
    {
      "name": "orders",
      "description": "Order facts for filtering, joining, and aggregation practice.",
      "columns": [],
      "primary_key": ["id"],
      "foreign_keys": [],
      "row_count": 6
    }
  ]
}
```

### practice_query

Input:

```json
{
  "command": "practice_query",
  "args": {
    "pack": "sql_basics",
    "sql": "SELECT id, name, region FROM customers ORDER BY id",
    "limit": 20
  },
  "context": {}
}
```

Required:

- `sql`

Rules:

- SQL must be non-empty.
- First token must be `SELECT`, case-insensitive.
- Writes and DDL must be rejected.
- `limit` defaults to `50`.
- `limit` must be zero or greater.

Output `data`:

```json
{
  "pack_id": "sql_basics",
  "dataset_id": "commerce_support",
  "sql": "SELECT id, name, region FROM customers ORDER BY id",
  "limit": 20,
  "columns": ["id", "name", "region"],
  "rows": [
    {"id": 1, "name": "Aster Foods", "region": "Seoul"}
  ],
  "row_count": 4
}
```

### practice_grade

Input:

```json
{
  "command": "practice_grade",
  "args": {
    "pack": "sql_basics",
    "problem_id": "basic_select_customers",
    "sql": "SELECT id, name, region FROM customers ORDER BY id",
    "no_record": false
  },
  "context": {}
}
```

Required:

- `problem_id`
- `sql`

Rules:

- Execute submitted SQL with no row limit.
- Execute the problem's `expected_sql` with no row limit.
- Grade by exact column order and exact row values in returned order.
- Record an attempt unless `no_record` is true.

Output `data`:

```json
{
  "pack_id": "sql_basics",
  "dataset_id": "commerce_support",
  "problem": {
    "id": "basic_select_customers",
    "title": "List all customers",
    "difficulty": "beginner",
    "prompt": "Return each customer id, name, and region ordered by id.",
    "concepts": ["select", "order_by"],
    "hint": "Start from the customers table."
  },
  "correct": true,
  "feedback": "Correct. Result columns and rows match the expected answer.",
  "actual": {
    "columns": ["id", "name", "region"],
    "rows": [],
    "row_count": 4
  },
  "expected": {
    "columns": ["id", "name", "region"],
    "rows": [],
    "row_count": 4
  },
  "expected_sql": "SELECT id, name, region FROM customers ORDER BY id",
  "attempt_recorded": true,
  "attempt_log_path": "local://coquery/practice_attempts"
}
```

### practice_attempts

Input:

```json
{
  "command": "practice_attempts",
  "args": {
    "pack": "sql_basics",
    "problem_id": "basic_select_customers",
    "limit": 20
  },
  "context": {}
}
```

All args are optional.

Output `data`:

```json
{
  "attempt_log_path": "local://coquery/practice_attempts",
  "pack_id": "sql_basics",
  "problem_id": "basic_select_customers",
  "limit": 20,
  "attempts": [
    {
      "timestamp": "2026-07-08T00:00:00Z",
      "pack_id": "sql_basics",
      "problem_id": "basic_select_customers",
      "correct": false,
      "sql": "SELECT id, name FROM customers ORDER BY id",
      "actual_row_count": 4,
      "expected_row_count": 4
    }
  ],
  "attempt_count": 1
}
```

### help_catalog

Input:

```json
{
  "command": "help_catalog",
  "args": {},
  "context": {"lang": "ko"}
}
```

`lang` defaults to Korean if omitted or unsupported.

Output `data`:

```json
{
  "language": "ko",
  "supported_languages": ["ko", "en"],
  "categories": [],
  "commands": [],
  "terms": []
}
```

### command_explain

Input:

```json
{
  "command": "command_explain",
  "args": {"topic": "practice_query"},
  "context": {"lang": "ko"}
}
```

Required:

- `topic`

Output `data`:

```json
{
  "language": "ko",
  "command": {},
  "related_terms": []
}
```

### term_explain

Input:

```json
{
  "command": "term_explain",
  "args": {"topic": "join"},
  "context": {"lang": "ko"}
}
```

Required:

- `topic`

Output `data`:

```json
{
  "language": "ko",
  "term": {}
}
```

## Error Codes

The iOS runtime should preserve these codes where possible:

| Code | Trigger |
| --- | --- |
| `invalid_practice_pack` | pack id is unsafe or malformed |
| `practice_pack_not_found` | requested pack does not exist |
| `practice_table_not_found` | requested practice table does not exist |
| `missing_practice_sql` | SQL is empty |
| `practice_sql_not_select` | first SQL token is not `SELECT` |
| `practice_sql_error` | local SQL executor returns an error |
| `missing_problem_id` | `practice_grade` is missing problem id |
| `practice_problem_not_found` | requested problem does not exist |
| `invalid_practice_limit` | limit is negative |
| `missing_command_topic` | `command_explain` is missing topic |
| `unknown_command_topic` | command help entry does not exist |
| `missing_term_topic` | `term_explain` is missing topic |
| `unknown_term_topic` | term help entry does not exist |

## Local Storage Contract

Practice packs:

```text
Bundle resource:
practice_packs/sql_basics.json
```

Attempt storage:

```text
Local app data:
coquery/practice_attempts.jsonl
```

For iOS, the physical storage may be SQLite, JSONL, or Capacitor Preferences, but the runtime output must preserve the attempt shape defined above.

Recommended first implementation:

- store attempts in JSON array or SQLite table
- expose `attempt_log_path` as logical URI: `local://coquery/practice_attempts`
- do not sync attempts externally
- do not include production data

## App Shell Adapter Contract

The current shell calls:

```js
postCommand(command, args, context)
```

For iOS, route this to a runtime adapter:

```js
async function postCommand(command, args = {}, context = {}) {
  if (window.CoQueryTrainingRuntime) {
    return window.CoQueryTrainingRuntime.runCommand({ command, args, context });
  }
  return fetch("/api/commands/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command, args, context }),
  }).then((response) => response.json());
}
```

This keeps the browser prototype working while allowing Capacitor to bypass the Python server.

## iOS Implementation Checklist

Done when the next implementation can prove:

- `practice_packs/sql_basics.json` is bundled into the app.
- `practice_list` returns at least five problems.
- `practice_schema` returns `customers`, `orders`, and `support_tickets`.
- `practice_query` can run `SELECT id, name, region FROM customers ORDER BY id`.
- non-SELECT SQL is rejected.
- `practice_grade` marks the canonical solution for `basic_select_customers` as correct.
- `practice_grade` records a wrong attempt by default.
- `practice_attempts` returns the wrong attempt after grading.
- `help_catalog` returns Korean and English command/term data.
- `command_explain practice_query` returns a beginner explanation.
- `term_explain join` returns a beginner explanation.
- No command starts a Python process or calls the local Python HTTP server.

## Next `/goal`

Recommended next implementation unit:

```text
Launch Goal 4: iOS TestFlight Shell Skeleton
```

Done when:

- Capacitor project files exist.
- `ios/` project exists.
- The shell can load the current terminal UI.
- `postCommand` can call a local Training Runtime adapter for at least `practice_list`.
- iPhone and iPad simulator verification instructions are documented for Mac.
