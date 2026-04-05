# CoQuery Backend Connection Contract

Date: 2026-04-05

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## 1. Purpose

Define one shared input contract for database selection before multi-DB implementation begins.

This slice exists to prevent CoQuery from growing separate connection rules for each backend.

## 2. Contract decision

The baseline multi-backend input should use one primary field:

`--db-uri`

Do not use backend-specific top-level command shapes as the primary contract.

That means these should not become the main design:

- `--backend sqlite --db file.db`
- `--backend postgres --host ... --port ...`
- separate command families per backend

## 3. Why this contract

`--db-uri` is the simplest shared boundary because:

- the backend can be inferred from the URI scheme
- one command surface can serve SQLite, PostgreSQL, and MySQL
- future validation can stay in one parser and one error model
- documentation stays smaller than backend-specific flag sets

## 4. Accepted URI shapes

### SQLite

Use:

- `sqlite:///absolute/path/to/file.db`
- `sqlite:///Users/Agent/ps-workspace/CoQuery/example.db`

Relative shorthand may remain for current legacy local usage, but it should be treated as SQLite-only compatibility mode, not the long-term multi-DB contract.

### PostgreSQL

Use:

- `postgresql://user:password@host:5432/dbname`

PostgreSQL is the first non-SQLite backend probe.
That means the first real Phase 5 implementation slice should target PostgreSQL, not MySQL.

### MySQL

Use:

- `mysql://user:password@host:3306/dbname`

MySQL remains a later backend after the first PostgreSQL probe.

## 5. Backend resolution rules

Backend should be determined from the URI scheme:

- `sqlite` -> SQLite
- `postgresql` -> PostgreSQL
- `mysql` -> MySQL

If the scheme is unknown, the command must fail with a structured error.

## 6. Legacy compatibility

The current SQLite-first baseline may continue accepting:

- `--db example.db`

But this should be interpreted as a legacy local convenience path.

Rules:

- `--db` remains valid for SQLite baseline commands during stabilization
- new multi-DB work should be documented against `--db-uri`
- once PostgreSQL probe support exists, docs should prefer `--db-uri` as the primary public contract

## 7. Required structured errors

The first connection-contract error set should include:

- `invalid_db_uri`
- `unsupported_backend`
- `missing_db_uri`
- `driver_not_installed`
- `connection_failed`

Do not use backend-specific raw tracebacks as the public contract.

## 8. First PostgreSQL probe decision

The first Phase 5 verification slice should target PostgreSQL.

Reason:

- it is the user's chosen first backend
- it gives the project one clear direction instead of splitting effort
- one real PostgreSQL probe is more valuable than two placeholder backends

## 9. Implemented baseline

The current runtime now implements:

- `--db-uri` in the CLI
- URI-scheme backend resolution for SQLite, PostgreSQL, and MySQL
- structured `invalid_db_uri`, `unsupported_backend`, and `missing_db_uri` errors
- legacy SQLite compatibility through `--db`

This does not mean PostgreSQL or MySQL are working backends yet.
It means the shared connection boundary is now executable.

## 10. Non-goals

This slice still does not require:

- validating real credentials yet
- adding write support for PostgreSQL
- claiming PostgreSQL support today
- removing legacy SQLite `--db` input immediately

## 11. Next follow-up

The next stabilization slice after this document should be:

1. add one PostgreSQL probe smoke path or documented environment target
2. define the verification matrix for backend status claims
3. decide when MySQL remains `stub` versus `planned`
