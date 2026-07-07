# CoQuery Mobile CLI UX Plan

Date: 2026-06-30

## Direction

CoQuery should remain CLI-first, but the CLI can be wrapped by a mobile app shell.

The product should feel like a terminal, not a dashboard:

- command input stays primary
- results are shown as terminal blocks
- AI help appears as optional adjacent context
- history, shortcuts, explanations, and plans expand only when the screen has room

Reference mood:

- Warp-like clean terminal workspace
- session list on wide screens
- centered terminal flow on medium screens
- side detail panel for plans, explainers, or review output
- compact mobile mode that behaves like a calculator: fast input, clear output, no heavy navigation

This is not a clone of Warp. The reference is the interaction model: terminal blocks plus adaptive side panels.

## Screen Model

### Phone Portrait

Phone portrait should be the simple calculator mode.

Layout:

```text
┌─────────────────────────┐
│ CoQuery        provider │
├─────────────────────────┤
│ session / db context    │
├─────────────────────────┤
│ terminal output blocks  │
│                         │
│ > schema users          │
│ result...               │
│                         │
├─────────────────────────┤
│ command input           │
│ [run] [templates] [?]   │
└─────────────────────────┘
```

Primary actions:

- run command
- insert common template
- switch provider
- open command history
- copy result
- save note

Hidden by default:

- long session list
- full command reference
- long explanations
- multi-pane review

### Phone Landscape

Phone landscape should expose a compact side strip.

Layout:

```text
┌───────────────┬────────────────────────┐
│ shortcuts     │ terminal               │
│ history       │ command/result blocks  │
└───────────────┴────────────────────────┘
```

Use this mode for:

- repeated practice queries
- quick review of recent commands
- copy/paste between generated SQL and user SQL

### Tablet

Tablet should behave like the engineering calculator mode.

Layout:

```text
┌──────────────┬────────────────┬─────────────────┐
│ sessions     │ terminal       │ detail panel    │
│ history      │ input/results  │ explain/review  │
│ saved packs  │                │ shortcuts       │
└──────────────┴────────────────┴─────────────────┘
```

The terminal remains central. Side panels assist; they do not replace the CLI.

### Desktop / Wide Web

Wide mode can follow the Warp reference most closely.

Layout:

```text
┌──────────────┬──────────────────────────────┬────────────────────┐
│ sessions     │ active terminal conversation │ plan / review doc  │
│ search       │ command blocks               │ schema/help        │
│ db contexts  │ approvals                    │ wrong-note detail  │
└──────────────┴──────────────────────────────┴────────────────────┘
```

Useful right-panel modes:

- command explanation
- generated SQL review
- schema detail
- provider/cost status
- practice problem
- wrong-note summary
- lesson material

## Core Interaction

Commands should be represented as structured blocks:

```text
> provider_list_presets
ok
presets: openai, groq, openrouter, gemini, deepseek

> natural "join users and orders" --provider fast_groq
mode: provider
sql: SELECT ...
```

Each block can expose actions:

- copy SQL
- run again
- explain
- review
- save as practice
- add to wrong note
- export result

The app should not force users to remember every CLI option. It should provide command builders that still emit the exact CLI equivalent.

Example:

```text
UI action: Add Groq provider
CLI shown: provider_add_preset --preset groq --provider-name fast_groq --model-name ...
```

## Architecture

The app should not rewrite CoQuery logic in the UI layer.

Recommended layers:

```text
Mobile/Web Shell
  ↓
CoQuery Command API
  ↓
Existing CLI handlers
  ↓
SQLite / schema files / practice packs / provider APIs
```

The current CLI handlers should remain the source of truth:

- `provider_list_presets`
- `provider_add_preset`
- `schema`
- `schema_detail`
- `generate`
- `natural`
- future `query_review`
- future `practice_grade`
- future `wrongnote_*`
- future `lesson_build`

The UI should call an app-facing API that wraps these handlers, not shell out blindly from mobile clients.

Current implementation:

- `sql_cli.command_api.run_command`
- reuses existing handlers directly
- adds `cli_equivalent`, `block_type`, and `actions`
- covered for provider presets, provider registration, provider list, schema detail, natural requests, and unknown-command errors

## Mobile API Shape

Minimum backend API:

```text
POST /commands/run
GET  /sessions
POST /sessions
GET  /sessions/{id}/blocks
GET  /providers/presets
POST /providers
GET  /practice/packs
POST /practice/grade
GET  /wrongnotes
```

Command run payload:

```json
{
  "session_id": "local-001",
  "command": "provider_list_presets",
  "args": {},
  "context": {
    "db": "example.db",
    "provider_name": "fast_groq"
  }
}
```

Command result payload:

```json
{
  "ok": true,
  "command": "provider_list_presets",
  "block_type": "provider_presets",
  "cli_equivalent": "python main.py --command provider_list_presets --format json",
  "data": {},
  "actions": ["copy", "insert_template", "add_provider"]
}
```

## UX Principles

1. Preserve terminal trust.
   Always show the CLI equivalent for important UI actions.

2. Keep mobile focused.
   Phone portrait should not show three panels. It should show input, output, and one bottom drawer.

3. Make wide screens useful.
   Tablet and desktop should add history, help, schema, and notes without hiding the terminal.

4. Prefer progressive disclosure.
   Start from command/result. Expand into explanation, review, practice, and lesson only when requested.

5. Make AI optional.
   Local deterministic output must still work without a provider. Provider-enhanced text should be labeled.

6. Track cost visibly.
   Provider name, model, preset, and cost profile should be visible before sending an AI request.

## First Implementation Slice

Build a mobile shell prototype around existing provider and natural commands.

Scope:

- responsive terminal screen
- command input
- command block history
- provider preset picker
- CLI equivalent preview
- right panel on tablet/desktop
- bottom drawer on phone
- no production DB connection

Use existing commands:

- `provider_list_presets`
- `provider_add_preset`
- `provider_list`
- `natural`
- `schema_detail`

Do not start with:

- full SQL editor
- charting
- Excel export
- dashboard UI
- multi-user auth
- production DB connectivity

## Suggested Next Goals

### Goal A: Command API Adapter - Done

Expose existing CLI handlers through a small app-facing command API.

Done when:

- provider preset commands can be called without shelling out
- responses include `cli_equivalent`
- tests cover success and error payloads

Implemented as `sql_cli.command_api.run_command`.

### Goal B: Responsive Terminal Shell Prototype - Done

Create a mobile-first UI shell that displays command blocks and adapts to phone/tablet/desktop.

Done when:

- phone portrait shows terminal + bottom command input
- tablet shows terminal + detail panel
- desktop shows session rail + terminal + detail panel
- no text overlap at mobile widths

Implemented as `app_shell/terminal_shell_prototype`.

Current proof:

- local server exposes `GET /api/health`, `GET /api/sessions`, and `POST /api/commands/run`
- UI calls `sql_cli.command_api.run_command`
- browser snapshots verified desktop, tablet, and phone layouts on 2026-06-30
- `app_shell/terminal_shell_prototype/smoke.py` verifies API and static UI expectations

### Goal C: Provider Preset Mobile Flow - Done

Add the first real flow for low-cost AI setup.

Done when:

- user can list presets
- choose Groq/Gemini/OpenRouter/DeepSeek/OpenAI
- enter model and API key env label
- see CLI equivalent
- save provider profile through the command API

Implemented in `app_shell/terminal_shell_prototype`.

Current proof:

- terminal shell defaults to dark mode
- `Setup AI` chip opens a provider preset form on mobile/tablet/desktop
- preset selection fills provider name, model, and API key env defaults
- CLI equivalent updates from the form values before saving
- `Save provider` calls `provider_add_preset` through `/api/commands/run`
- `app_shell/terminal_shell_prototype/smoke.py` verifies provider preset save through the local Command API

### Goal D: Query Practice Flow - Done

Use the same terminal shell for SQL learning.

Done when:

- practice problem appears as a terminal block
- user can open a problem, inspect schema, type SQL, and submit
- result and grading appear as terminal blocks
- wrong answers create local attempt records
- recent attempts can be opened from the UI

Implemented in `app_shell/terminal_shell_prototype`.

Current proof:

- `practice_list` renders problem cards with start and schema actions
- `practice_start` opens a local SQL entry form while preserving the CLI equivalent
- submit calls `practice_query` and `practice_grade` through `/api/commands/run`
- wrong results open `practice_attempts` so the local attempt record is visible
- `app_shell/terminal_shell_prototype/smoke.py` verifies schema, query, wrong grading, and attempt logging

Provider-backed feedback remains intentionally deferred to the Wrong Note And Feedback launch goal.

### Goal E: Bilingual Beginner Help - Done

Make menus, feature names, command help, and SQL terms usable in both Korean and English.

Done when:

- terminal shell has a KR/EN language toggle
- context chips include help and terms
- CLI exposes `help_catalog`, `command_explain`, and `term_explain`
- selected command blocks show beginner-friendly guidance in the detail panel
- smoke checks verify help commands and static UI hooks

Implemented through `sql_cli.help_catalog`, `sql_cli.command_api.run_command`, and `app_shell/terminal_shell_prototype`.

### Goal F: iOS Launch Feasibility And Packaging Decision - Done

Decide how the mobile shell should become an iOS app.

Done when:

- iOS feasibility is documented
- packaging approach is selected
- first iOS app scope is separated from production DB support
- the current Python local server dependency is addressed
- the next `/goal` is clear

Implemented as `IOS_LAUNCH_FEASIBILITY_2026-07-07.md`.

Current decision:

- first iOS target is a TestFlight-first Training App
- Capacitor iOS shell is the selected packaging path
- the iOS app must run Training Mode without starting the Python local server
- production DB assistance remains deferred to a controlled Production Assist track

## Boundary

This plan does not change CoQuery into a BI dashboard.

The mobile app should be a CLI companion:

- command-first
- practice-friendly
- provider-aware
- explainable
- useful without live DB access
