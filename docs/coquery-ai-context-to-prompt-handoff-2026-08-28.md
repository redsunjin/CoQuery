# CoQuery AI Context-to-Prompt Handoff

Date: 2026-08-28
Status: Approved product direction; implementation not yet started

## One-line definition

CoQuery turns the current SQL question, generated SQL, schema evidence, execution/grading result, timestamps, and known limitations into a reviewable plain-text prompt that the user can copy or share to an external AI for validation, alternative interpretations, counter-evidence, and follow-up questions.

## Why this exists

Rule-based and local-knowledge-first SQL generation remains valuable for deterministic baseline behavior, but it cannot fully resolve the meaning of open-ended user questions.

The product should therefore separate two responsibilities:

1. CoQuery structures the question, SQL, evidence, and safety boundary.
2. The user may ask an external AI to critique that package.

This is not a built-in chatbot and not automated external AI control.

## First valid application point

P0 target: the result of `natural` immediately after SQL generation.

Initial user intents:

- Validate whether this SQL answers my question.
- Find another reasonable interpretation.
- Identify missing conditions or assumptions.
- Suggest the next question or evidence to check.

Second targets after the first slice is verified:

- `practice_grade`
- `practice_query`
- read-only Production Assist review, only after export policy is proven

## Product flow

Current result -> choose question purpose -> ContextAdapter snapshot -> ExportPolicy filtering -> QuestionPolicy -> PromptComposer -> PromptPreview -> user edits/excludes -> copy/share/open destination -> user sends externally.

Copy is the universal baseline. System share and destination opening are optional platform adapters.

## Boundary modules

### ContextAdapter

Normalizes:

- selected target
- user question
- generated/submitted SQL
- schema context
- execution result summary
- grading result
- evidence sources
- `dataAsOf`
- `capturedAt`
- missing/stale/sample limitations
- external-sharing permission state

### ExportPolicy

Allowlist-first extraction. Default excludes:

- API keys, tokens, passwords, secrets
- provider credentials
- connection strings / DB URI
- raw production records
- personal information
- audit log raw text
- fields whose external-sharing permission is unknown

Displaying a field inside CoQuery does not imply permission to send it to an external AI.

### QuestionPolicy

Question behavior changes by evidence quality:

- sufficient: ask meaning, alternatives, counter-evidence, next observation
- limited: ask assumptions, generalization limits, counterexamples, extra samples
- stale: include reference time and ask what should be refreshed
- insufficient: ask what must be learned before concluding

### PromptComposer

Pure deterministic function. No LLM call or API key is required to create the prompt.

Same normalized input + purpose + language + template version produces the same body.

Output contract:

- title
- reason
- body
- warnings
- excludedFields
- templateVersion
- snapshotId
- revision

Body order:

`[Purpose] -> [Confirmed context] -> [Data limitations] -> [User questions] -> [Requested answer format] -> [Caution]`

The requested AI response should distinguish:

- confirmed facts
- interpretation / assumptions
- counter-evidence / risk
- additional verification questions

### PromptPreview

Owns:

- exact outgoing body
- user edits
- excluded evidence
- revision
- reviewed state
- source-data change detection

Changing the body invalidates previous review state. New source data must not silently overwrite user edits.

### HandoffAdapter

Side effects only after an explicit user action:

- copy
- system share
- open approved external URL

Do not implement automatic paste/send, DOM injection, login delegation, automatic answer retrieval, or execution of an AI response.

## PWA / iOS / Android architecture

Core modules stay platform-neutral:

- ContextAdapter
- ExportPolicy
- QuestionPolicy
- PromptComposer
- PromptPreview state

Only HandoffAdapter differs:

- PWA: Clipboard API, Web Share API when supported
- iOS/Android wrapper: native clipboard/share sheet through the chosen wrapper layer

This keeps one product behavior across Web, iOS, and Android.

## First implementation slice

Keep the first implementation deliberately small:

`natural result -> Build AI validation prompt -> Preview -> Copy`

No provider SDK, destination deep link, system share, or Production Assist export in the first slice.

## Acceptance criteria for first slice

- No side effect before explicit user action.
- Prompt creation is deterministic.
- Exact outgoing text is previewed first.
- Sensitive/unknown-permission fields are excluded by default.
- Generated SQL, question, selected schema evidence, timestamps, and limitations are distinguishable.
- User can edit the prompt before copying.
- Preview revision equals copied revision.
- Data changes do not overwrite user edits.
- Missing values remain unknown; zero is not invented.
- No claim is made that an external AI actually received the prompt.

## Test plan

RED -> minimal implementation -> GREEN.

Cover:

- deterministic output
- null / zero / units / timestamps / sources
- sufficient / limited / stale / insufficient evidence
- target/evidence mismatch
- sensitive-field exclusion
- malicious note treated as data, not instruction
- long prompt handling without silent truncation
- preview/copy revision equality
- source change with user edits
- clipboard failure
- unsupported share/open behavior in later slices
- no side effects without explicit user action

## Non-goals

- replacing the current local-rule SQL engine
- making provider-backed natural the only generation path
- automatically sharing production data
- building a new server for this feature
- coupling the prompt format to one AI vendor

## Roadmap placement

Priority after the current PWA/serverless publication baseline is merged and verified.

P0 next product slice:

`Natural SQL result -> deterministic external-AI validation prompt -> preview -> copy`

P1 after proof:

- practice result handoff
- system share
- configurable external AI destination

P2 only after export-policy evidence:

- constrained Production Assist handoff
- optional cross-device prompt/history sync
