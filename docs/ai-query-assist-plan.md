# CoQuery AI Query Assist — planning and session handoff

Date: 2026-10-26 (KST)
Status: proposal recorded; implementation NOT started in this branch
Repository: redsunjin/CoQuery
Branch: docs/ai-query-assist-handoff-2026-10-26
Base main commit at branch creation: 3ff318eeb630bf9a74de5b5a176913a39ca66c1b

## Decision

Extend existing CoQuery SQL education and assistance into **AI Query Assist**, without replacing deterministic SQL generation or weakening Production Assist safety controls. First user-facing slice belongs in Training/Practice, not live production.

Three user actions:
1. **Generate SQL** from a natural-language request.
2. **Fix SQL** using user's SQL, actual error text and approved schema context.
3. **Explain SQL** in accessible Korean/English, clearly separating SQL semantics from business assumptions.

Initial MVP: natural-language question → AI SQL draft → explanation and assumptions → deterministic validation → preview → explicit **Apply to editor**; user initiates execution separately. Fix/Explain are follow-up slices with shared contracts.

## Existing building blocks verified at planning time

- `sql_cli/nl_core.py`: `NaturalLanguageEngine` combines local intent heuristics, inferred tables, knowledge planner and optional provider invocation.
- `sql_cli/llm_registry.py`: `LLMProviderRegistry` / `LLMProviderClient` support Ollama and OpenAI-compatible providers. Present structured generation takes natural-language text only.
- `sql_cli/schema_guard.py`: schema-detail-backed table/column and FK/join checks; currently limited for complex SQL, not a complete SQL AST policy.
- `sql_cli/mode_policy.py`: Training vs Production Assist and external provider policy.
- `sql_cli/production_assist.py`: read-only profiles, review/approve/execute workflow, audit. Existing SELECT-prefix check alone must NOT be treated as a complete SQL safety parser.
- `sql_cli/command_api.py`: app-facing `natural` command and action metadata.
- `docs/coquery-ai-context-to-prompt-handoff-2026-08-28.md`: previously approved, distinct **external AI prompt preview/copy** product direction. Keep it separate from embedded provider calls; do not mistake design for shipped functionality.
- `app_shell/terminal_shell_prototype/` and `app_shell/ios_training_shell/`: UI surfaces and parity targets.

These file references demonstrate available foundations, not end-to-end AI Assist readiness or deployed behavior.

## Current gaps requiring tests and code inspection

1. Provider SQL-generation prompt does not receive a bounded, approved schema snapshot or explicit SQL dialect; hallucinated tables/columns/joins are plausible.
2. Existing natural engine performs preliminary schema validation for heuristic table inference but does not demonstrably validate **provider-produced SQL identifiers** before returning them.
3. Provider-reported `confidence` is not calibrated proof of SQL correctness.
4. Regex/first-keyword checks and single-statement checks are insufficient for production security. Add dialect-aware AST parsing or a proven equivalent policy layer, and enforce read-only DB credentials/transaction settings and query limits server-side.
5. UI integration, secrets boundary, input/output privacy, error redaction, cache behavior and iOS/PWA parity require explicit review.
6. External sharing is different from displaying within CoQuery; enforce explicit allowlists and consent.

## Proposed user flow

```text
Question or current SQL
  → ContextAdapter (request, dialect, approved schema, relationship evidence, current SQL, safe error text)
  → Privacy/ExportPolicy (deny unknown or sensitive fields by default)
  → ProviderAdapter (configurable local/API provider, bounded request)
  → Structured draft {sql, explanation, assumptions, referenced_tables, warnings, confidence}
  → deterministic Schema & SQL Policy Gate
  → Preview (evidence, warnings, unverified assumptions, provider/source, no auto-execution)
  → user: Apply to editor
  → existing user-controlled query execution workflow
```

Always preserve local rule-based generation when AI is unavailable; make provider use explicit, never silently fall back to a provider. Do not silently imply that a generated SELECT necessarily answers the business question.

## Safety and data contracts

- Training/Practice first; use synthetic fixtures. No production row contents to an external model by default.
- Do not send DB URIs, credentials, keys, PII, unapproved schema descriptions, raw production records, arbitrary log text or audit data.
- Provider URL/model/credential resolution remains on the trusted side; no browser-bundled secrets. Explicit provider opt-in and per-request indication.
- Provider-generated SQL is *untrusted text*. Parse to AST for target dialect; require single safe read-only statement for any execution pathway; block DDL/DML, data-changing CTEs, dangerous functions, command execution, multi-statements and parser-unsupported constructs, failing closed. Never rely on keyword checks alone.
- Validate referenced schema identifiers/relationships, respect permissions, preserve parameterization, add timeout and row/byte caps, and require database-level read-only privileges. `EXPLAIN` is not a safety substitute.
- Never auto-execute or auto-approve. A user's **Apply** click changes editor text only; review/approve/execute gate remains independent.
- Always show model suggestions as unverified and list missing assumptions; ambiguous joins/metrics/time ranges produce clarifying prompts rather than fabricated certainty.
- Logging stores minimal metadata (provider/model, sanitized intent/hash, policy decisions, timestamps, revision); do not log raw confidential prompts/responses.
- Preserve compatibility with the approved external-AI handoff: preview exact outgoing prompt and allow manual copy only after export filtering, in a separate later slice.

## First implementation slice (MVP)

**Scope**
- Provider-neutral `sql_cli/ai_assist.py` orchestration; reuse existing registry, schema guard and mode policy.
- Define structured input/output versioned contracts and clear fail-closed error statuses.
- Add dialect/schema-aware context builder with bounded field allowlist.
- Introduce server-side SQL syntax/policy validation for a clearly scoped dialect (start with SQLite training fixture; broaden only with proven tests).
- Add `ai_query_draft` command (or an equivalently namespaced adapter) without altering existing `natural` command response semantics.
- Training/Practice UI: “AI로 SQL 만들기” → draft, rationale, assumptions, errors → “편집기에 적용”. Existing Run remains separately initiated.
- Accessible desktop/mobile/PWA/iOS wrapper interaction; preserve offline fallback and no-provider explanation.
- Document cost caps, provider timeout and service failure.

**Not in MVP**
- No production SQL AI execution, no auto-run, no DML/DDL suggestions executed, no autonomous DB exploration, no prompt submission to third-party without review, no AI chatbot requirement, no merge/deploy with this planning branch.

## Acceptance tests

1. Natural prompt + permitted fixture schema yields a well-formed draft and readable explanation; Apply changes editor only.
2. Unknown tables/columns, fabricated join conditions, dialect mismatch, unsupported syntax, ambiguous schema or missing context fail closed / request clarification.
3. SQL injection/malicious model response, prompt injection embedded in schema metadata, multi-statements, write/DDL/unsafe CTEs are rejected by policy independent of model confidence.
4. Same valid local fallback stays deterministic; no provider call when disabled/offline or not approved.
5. No API key in web bundle, outgoing prompt, logs, error strings or screenshot; production/PII/raw rows excluded.
6. Provider errors/timeouts produce actionable retry/fallback; no auto-execute on return.
7. Current SQL remains unchanged until explicit Apply; previous edits not overwritten on asynchronous/stale responses.
8. Production Assist approval and DB readonly constraints cannot be bypassed via AI path.
9. Regression suite: existing Python tests, command API, terminal shell smoke, PWA runtime and iOS training parity tests.
10. Separate product validation of Korean requests and SQL explanations, including NULL vs 0, date boundaries, COUNT DISTINCT vs COUNT and join multiplicity.

## Suggested implementation sequence

1. **Read-only audit**: inspect latest main implementation and deployment/runtime boundaries, map natural/command adapters/worker/UI; confirm existing tests and any pending PRs.
2. **Contract + tests first**: create failing fixtures for safe requests, adversarial provider output and privacy policy; select proven SQL parser compatible with supported runtime or document narrower fail-closed grammar.
3. **Backend isolated slice**: new assistant orchestration + context filtering + parser gate, retaining existing commands.
4. **UI slice**: Training/Practice draft preview and Apply; mobile/web parity and accessibility QA.
5. **Review and release**: tests, cost/privacy checks, human review, PR; merge/deploy only after explicit approval and evidence.

## Continuation / session-end status

This document is a **planning handoff**, not a completed feature. No provider API tests, builds, deployment, production DB access, main merge, or automatic SQL execution are claimed here. The branch and commit should be independently confirmed after remote write before reporting preservation complete.

Next development task: implement ONLY the safe schema-aware draft first slice on a feature branch from current main, after the read-only audit and failing test cases.
