# CoQuery Mode Security Boundary

Date: 2026-07-08

CoQuery has two app modes with different trust assumptions.

## Training Mode

Training Mode is for learning, practice, and feedback.

Allowed by default:

- built-in sample datasets such as `practice_packs/sql_basics.json`
- `practice_list`, `practice_schema`, `practice_query`, `practice_grade`, `practice_attempts`, and static `practice_feedback`
- low-cost or commercial OpenAI-compatible providers for education and practice feedback

Training Mode must not be treated as production DB assistance. It can use provider-backed feedback because the expected payload is sample data, submitted practice SQL, and learning context.

## Production Assist Mode

Production Assist Mode is for controlled real database query assistance.

Default boundary:

- external AI providers are blocked for commands that can send natural-language query intent or practice feedback payloads
- local/internal providers such as Ollama-style profiles are allowed by policy
- external provider use requires an explicit `allow_external_provider=true` policy override
- the Command API returns `production_external_provider_blocked` when a saved external provider is used without that override

This boundary exists because production assist can include live schema, table names, business terms, and user query intent. Those values must not be sent to commercial providers accidentally.

## Command API Contract

Mode context is passed through `context` or `args`:

```json
{
  "mode": "production_assist",
  "allow_external_provider": false,
  "provider_policy": "default"
}
```

Example blocked request:

```json
{
  "command": "natural",
  "args": { "sql": "show users" },
  "context": {
    "db": "example.db",
    "provider_name": "gemini_prod",
    "mode": "production_assist"
  }
}
```

Expected error code:

```text
production_external_provider_blocked
```

Example explicit override:

```json
{
  "command": "natural",
  "args": { "sql": "show users" },
  "context": {
    "db": "example.db",
    "provider_name": "gemini_prod",
    "mode": "production_assist",
    "allow_external_provider": true,
    "provider_policy": "approved-enterprise-ai"
  }
}
```

The override is a policy assertion, not a safety review. The Production Assist safety gate is separate and requires a read-only profile, generated SQL review, approval state, SELECT-only guard, audit log, and redaction.

## UI Contract

The terminal shell shows a `Training` / `Assist` segmented control in the command bar.

- `Training` sends sample-dataset practice commands as Training context.
- `Assist` sends natural-language commands as `production_assist` context.
- The provider readiness indicator repeats the current mode and warns that external providers are blocked in Production Assist unless policy overrides them.

The iOS TestFlight shell remains Training-first. Production Assist stays out of the first iOS release until a separate iOS production-assist validation goal exists.
