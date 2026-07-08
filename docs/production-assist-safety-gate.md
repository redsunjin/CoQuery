# Production Assist Safety Gate

Date: 2026-07-08

Goal 9 adds a conservative Production Assist path. It prepares reviewed read-only support without claiming broad production DB automation.

## What Exists

- Read-only production connection profiles via `production_profile_add`.
- Generated SQL review records via `production_review`.
- Approval-required execution via `production_approve` and `production_execute`.
- A SELECT-only guard for every Production Assist review and execution.
- JSONL audit logging for profile, review, approval, block, and execution events.

## Commands

```bash
python3 main.py --command production_profile_add \
  --profile-name prod_readonly \
  --db-uri-env COQUERY_PROD_READONLY_DB_URI

python3 main.py --command production_review \
  --profile-name prod_readonly \
  --sql "SELECT COUNT(*) FROM users" \
  --request-text "count users"

python3 main.py --command production_approve --review-id prodrev_...
python3 main.py --command production_execute --review-id prodrev_...
```

For local smoke use only, `--db-uri example.db` is accepted. For real production targets, prefer `--db-uri-env` so secrets stay in the environment and not in the profile file.

## Runtime Files

Defaults:

```text
.coquery/production_profiles.json
.coquery/production_reviews.json
.coquery/production_audit.jsonl
```

Environment overrides:

```text
COQUERY_PRODUCTION_PROFILE_PATH
COQUERY_PRODUCTION_REVIEW_PATH
COQUERY_PRODUCTION_AUDIT_LOG
```

## Guardrails

- Profiles are rejected unless they are read-only.
- Profiles reject DB URIs that embed a password; use `db_uri_env` for secrets.
- Reviews reject non-`SELECT` SQL and multiple statements.
- Execution is blocked until a review is approved.
- Execution rechecks the SELECT-only guard before connecting.
- Audit records are appended for accepted profiles, rejected profiles, created reviews, rejected reviews, blocked executions, approvals, and completed executions.

## Non-Claims

- This is not write access to production data.
- This is not a replacement for a database-level read-only user.
- This does not make the iOS Training App a production DB client.
- Broader production DB support still needs release hardening and real credential/device validation.
