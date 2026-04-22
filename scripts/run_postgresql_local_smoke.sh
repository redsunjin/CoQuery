#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="${ROOT_DIR}/.tmp"
VENV_DIR="${TMP_DIR}/pg-venv"
DATA_DIR="${TMP_DIR}/pg-smoke"
LOG_FILE="${TMP_DIR}/pg-smoke.log"
SOCKET_ROOT="${COQUERY_PG_SOCKET_ROOT:-${TMP_DIR}}"
PORT="${COQUERY_PG_PORT:-}"
DEFAULT_PORT="${COQUERY_PG_DEFAULT_PORT:-49251}"
DB_NAME="${COQUERY_PG_DB:-coquery_probe}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
POSTGRES_BIN_DIR="${POSTGRES_BIN_DIR:-}"
EXTERNAL_DB_URI="${COQUERY_PG_DB_URI:-}"
PSQL_URI="${COQUERY_PSQL_URI:-${EXTERNAL_DB_URI}}"
INITDB_LOCALE="${COQUERY_PG_INITDB_LOCALE:-}"
START_TIMEOUT="${COQUERY_PG_START_TIMEOUT:-30}"
RESET_CLUSTER="${COQUERY_PG_RESET:-0}"
KEEP_SOCKET_DIR="${COQUERY_PG_KEEP_SOCKET_DIR:-0}"
SOCKET_DIR=""
LOCAL_CLUSTER_STARTED=0

detect_initdb_locale() {
  if [[ -n "${INITDB_LOCALE}" ]]; then
    printf '%s\n' "${INITDB_LOCALE}"
    return
  fi
  if locale -a 2>/dev/null | grep -Eiq '^en_US\.(UTF-8|utf8)$'; then
    printf '%s\n' "en_US.UTF-8"
    return
  fi
  if locale -a 2>/dev/null | grep -Eiq '^C\.(UTF-8|utf8)$'; then
    printf '%s\n' "C.UTF-8"
    return
  fi
}

detect_port() {
  if [[ -n "${PORT}" ]]; then
    printf '%s\n' "${PORT}"
    return
  fi

  "${PYTHON_BIN}" - "${DEFAULT_PORT}" <<'PY'
import socket
import sys

preferred = int(sys.argv[1])


def is_free(port: int) -> bool:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", port))
    except OSError:
        return False
    finally:
        sock.close()
    return True


if is_free(preferred):
    print(preferred)
else:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
    sock.close()
PY
}

make_socket_dir() {
  mkdir -p "${SOCKET_ROOT}"
  mktemp -d "${SOCKET_ROOT}/pg-socket.XXXXXX"
}

require_binary() {
  local binary_path="$1"
  local description="$2"

  if [[ ! -x "${binary_path}" ]]; then
    echo "${description} not found at '${binary_path}'." >&2
    echo "Add PostgreSQL binaries to PATH or set POSTGRES_BIN_DIR." >&2
    exit 1
  fi
}

show_failure_context() {
  local exit_code=$?

  echo "" >&2
  echo "PostgreSQL smoke failed with exit code ${exit_code}." >&2
  if [[ -n "${EXTERNAL_DB_URI}" ]]; then
    echo "Mode: external DB URI" >&2
    echo "PSQL_URI: ${PSQL_URI}" >&2
  else
    echo "Mode: local cluster" >&2
    echo "Data dir: ${DATA_DIR}" >&2
    echo "Socket dir: ${SOCKET_DIR}" >&2
    echo "Port: ${PORT}" >&2
  fi
  echo "Log file: ${LOG_FILE}" >&2
  if [[ -f "${LOG_FILE}" ]]; then
    echo "--- PostgreSQL log tail ---" >&2
    tail -n 40 "${LOG_FILE}" >&2 || true
    echo "--- End log tail ---" >&2
  fi

  return "${exit_code}"
}

if [[ -n "${EXTERNAL_DB_URI}" ]]; then
  if [[ -z "${POSTGRES_BIN_DIR}" ]] && command -v psql >/dev/null 2>&1; then
    POSTGRES_BIN_DIR="$(cd "$(dirname "$(command -v psql)")" && pwd)"
  fi
else
  if [[ -z "${POSTGRES_BIN_DIR}" ]]; then
    if command -v pg_ctl >/dev/null 2>&1; then
      POSTGRES_BIN_DIR="$(cd "$(dirname "$(command -v pg_ctl)")" && pwd)"
    elif [[ -d "/Users/Agent/homebrew/opt/postgresql@18/bin" ]]; then
      POSTGRES_BIN_DIR="/Users/Agent/homebrew/opt/postgresql@18/bin"
    elif [[ -d "/opt/homebrew/opt/postgresql@18/bin" ]]; then
      POSTGRES_BIN_DIR="/opt/homebrew/opt/postgresql@18/bin"
    fi
  fi
fi

mkdir -p "${TMP_DIR}"

if [[ -n "${EXTERNAL_DB_URI}" ]]; then
  require_binary "${POSTGRES_BIN_DIR}/psql" "PostgreSQL client binary"
else
  require_binary "${POSTGRES_BIN_DIR}/pg_ctl" "pg_ctl"
  require_binary "${POSTGRES_BIN_DIR}/psql" "psql"
  require_binary "${POSTGRES_BIN_DIR}/initdb" "initdb"
  require_binary "${POSTGRES_BIN_DIR}/createdb" "createdb"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

if ! "${VENV_DIR}/bin/python" -c "import psycopg" >/dev/null 2>&1; then
  "${VENV_DIR}/bin/python" -m pip install "psycopg[binary]" >/dev/null
fi

psql_exec() {
  local sql="$1"
  if [[ -n "${EXTERNAL_DB_URI}" ]]; then
    "${POSTGRES_BIN_DIR}/psql" "${PSQL_URI}" -v ON_ERROR_STOP=1 -c "${sql}" >/dev/null
  else
    "${POSTGRES_BIN_DIR}/psql" \
      -h "${SOCKET_DIR}" \
      -p "${PORT}" \
      -d "${DB_NAME}" \
      -v ON_ERROR_STOP=1 \
      -c "${sql}" >/dev/null
  fi
}

cleanup() {
  if [[ "${LOCAL_CLUSTER_STARTED}" == "1" && -f "${DATA_DIR}/postmaster.pid" ]]; then
    "${POSTGRES_BIN_DIR}/pg_ctl" -D "${DATA_DIR}" stop -m fast >/dev/null || true
  fi
  if [[ -n "${SOCKET_DIR}" && "${KEEP_SOCKET_DIR}" != "1" ]]; then
    rm -rf "${SOCKET_DIR}" || true
  fi
}
trap show_failure_context ERR
trap cleanup EXIT

if [[ -z "${EXTERNAL_DB_URI}" ]]; then
  PORT="$(detect_port)"
  SOCKET_DIR="$(make_socket_dir)"

  if [[ "${RESET_CLUSTER}" == "1" ]]; then
    rm -rf "${DATA_DIR}"
  fi

  if [[ ! -f "${DATA_DIR}/PG_VERSION" ]]; then
    INITDB_LOCALE="$(detect_initdb_locale)"
    rm -rf "${DATA_DIR}"
    mkdir -p "${DATA_DIR}"
    if [[ -n "${INITDB_LOCALE}" ]]; then
      LC_ALL="${INITDB_LOCALE}" "${POSTGRES_BIN_DIR}/initdb" -D "${DATA_DIR}" >/dev/null
    else
      "${POSTGRES_BIN_DIR}/initdb" -D "${DATA_DIR}" >/dev/null
    fi
  fi

  "${POSTGRES_BIN_DIR}/pg_ctl" \
    -D "${DATA_DIR}" \
    -l "${LOG_FILE}" \
    -o "-k ${SOCKET_DIR} -p ${PORT}" \
    -w \
    -t "${START_TIMEOUT}" \
    start >/dev/null
  LOCAL_CLUSTER_STARTED=1

  DB_EXISTS="$(
    "${POSTGRES_BIN_DIR}/psql" \
      -h "${SOCKET_DIR}" \
      -p "${PORT}" \
      -d postgres \
      -Atqc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'"
  )"

  if [[ "${DB_EXISTS}" != "1" ]]; then
    "${POSTGRES_BIN_DIR}/createdb" -h "${SOCKET_DIR}" -p "${PORT}" "${DB_NAME}"
  fi

  DB_URI="postgresql://localhost/${DB_NAME}?host=${SOCKET_DIR}&port=${PORT}"
else
  DB_URI="${EXTERNAL_DB_URI}"
fi

psql_exec "SELECT current_database();"
psql_exec "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT, age INTEGER);"
psql_exec "CREATE TABLE IF NOT EXISTS orgs (id SERIAL PRIMARY KEY, name TEXT NOT NULL UNIQUE);"
psql_exec "CREATE TABLE IF NOT EXISTS members (id SERIAL PRIMARY KEY, org_id INTEGER NOT NULL REFERENCES orgs(id) ON DELETE CASCADE, email TEXT NOT NULL UNIQUE);"
psql_exec "INSERT INTO users (name, age) SELECT 'probe_user', 34 WHERE NOT EXISTS (SELECT 1 FROM users WHERE name = 'probe_user');"
psql_exec "DELETE FROM users WHERE name = 'insert_probe_user';"
psql_exec "DELETE FROM users WHERE name = 'update_probe_user';"
psql_exec "DELETE FROM users WHERE name = 'delete_probe_user';"
psql_exec "DELETE FROM users WHERE name = 'dry_run_probe_user';"
psql_exec "DELETE FROM users WHERE name IN ('max_guard_probe_user_1', 'max_guard_probe_user_2');"
psql_exec "DELETE FROM users WHERE name = 'full_table_guard_user';"
psql_exec "DELETE FROM members WHERE email = 'join_probe_member@example.com';"
psql_exec "DELETE FROM orgs WHERE name = 'join_probe_org';"
psql_exec "INSERT INTO orgs (name) SELECT 'join_probe_org' WHERE NOT EXISTS (SELECT 1 FROM orgs WHERE name = 'join_probe_org');"
psql_exec "INSERT INTO members (org_id, email) SELECT id, 'join_probe_member@example.com' FROM orgs WHERE name = 'join_probe_org' AND NOT EXISTS (SELECT 1 FROM members WHERE email = 'join_probe_member@example.com');"

echo "== PostgreSQL schema smoke =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command schema \
  --db-uri "${DB_URI}" \
  --format json

echo ""
echo "== PostgreSQL schema detail smoke =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command schema_detail \
  --db-uri "${DB_URI}" \
  --table users \
  --format json

echo ""
echo "== PostgreSQL query smoke =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "SELECT name, age FROM users ORDER BY id LIMIT 5" \
  --format json

echo ""
echo "== PostgreSQL select_simple generation smoke =="
SELECT_GENERATE_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command generate \
  --db-uri "${DB_URI}" \
  --skill select_simple \
  --params '{"table":"users","cols":["id","name"]}' \
  --format json)"
printf '%s\n' "${SELECT_GENERATE_OUTPUT}"

SELECT_SQL="$(printf '%s\n' "${SELECT_GENERATE_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; assert payload.get("schema_validation", {}).get("status") == "validated", payload; print(payload["sql"])')"

echo ""
echo "== PostgreSQL select_simple generated query smoke =="
SELECT_VERIFY_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "${SELECT_SQL}" \
  --format json)"
printf '%s\n' "${SELECT_VERIFY_OUTPUT}"
printf '%s\n' "${SELECT_VERIFY_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; rows = payload.get("data", {}).get("rows", []); assert rows, payload; assert len(rows[0]) == 2, payload'

echo ""
echo "== PostgreSQL count_simple generation smoke =="
COUNT_GENERATE_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command generate \
  --db-uri "${DB_URI}" \
  --skill count_simple \
  --params '{"table":"users"}' \
  --format json)"
printf '%s\n' "${COUNT_GENERATE_OUTPUT}"

COUNT_SQL="$(printf '%s\n' "${COUNT_GENERATE_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; assert payload.get("schema_validation", {}).get("status") == "validated", payload; print(payload["sql"])')"

echo ""
echo "== PostgreSQL count_simple generated query smoke =="
COUNT_VERIFY_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "${COUNT_SQL}" \
  --format json)"
printf '%s\n' "${COUNT_VERIFY_OUTPUT}"
printf '%s\n' "${COUNT_VERIFY_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; rows = payload.get("data", {}).get("rows", []); assert rows and rows[0][0] >= 1, payload'

echo ""
echo "== PostgreSQL insert smoke =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command insert \
  --db-uri "${DB_URI}" \
  --write \
  --sql "INSERT INTO users (name, age) VALUES ('insert_probe_user', 45)" \
  --format json

echo ""
echo "== PostgreSQL insert verification query =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "SELECT name, age FROM users WHERE name = 'insert_probe_user' ORDER BY id DESC LIMIT 1" \
  --format json

echo ""
echo "== PostgreSQL insert dry-run rollback smoke =="
INSERT_DRY_RUN_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command insert \
  --db-uri "${DB_URI}" \
  --write \
  --dry-run \
  --sql "INSERT INTO users (name, age) VALUES ('dry_run_probe_user', 48)" \
  --format json)"
printf '%s\n' "${INSERT_DRY_RUN_OUTPUT}"
printf '%s\n' "${INSERT_DRY_RUN_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; data = payload.get("data", {}); assert data.get("dry_run") is True, payload; assert data.get("committed") is False, payload'

echo ""
echo "== PostgreSQL insert dry-run verification query =="
INSERT_DRY_RUN_VERIFY_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "SELECT COUNT(*) FROM users WHERE name = 'dry_run_probe_user'" \
  --format json)"
printf '%s\n' "${INSERT_DRY_RUN_VERIFY_OUTPUT}"
printf '%s\n' "${INSERT_DRY_RUN_VERIFY_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; assert payload.get("data", {}).get("rows") == [[0]], payload'

echo ""
echo "== PostgreSQL update smoke =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command insert \
  --db-uri "${DB_URI}" \
  --write \
  --sql "INSERT INTO users (name, age) VALUES ('update_probe_user', 41)" \
  --format json >/dev/null

"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command update \
  --db-uri "${DB_URI}" \
  --write \
  --sql "UPDATE users SET age = 52 WHERE name = 'update_probe_user'" \
  --format json

echo ""
echo "== PostgreSQL update verification query =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "SELECT name, age FROM users WHERE name = 'update_probe_user' ORDER BY id DESC LIMIT 1" \
  --format json

echo ""
echo "== PostgreSQL delete smoke =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command insert \
  --db-uri "${DB_URI}" \
  --write \
  --sql "INSERT INTO users (name, age) VALUES ('delete_probe_user', 27)" \
  --format json >/dev/null

"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command delete \
  --db-uri "${DB_URI}" \
  --write \
  --sql "DELETE FROM users WHERE name = 'delete_probe_user'" \
  --format json

echo ""
echo "== PostgreSQL delete verification query =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "SELECT COUNT(*) FROM users WHERE name = 'delete_probe_user'" \
  --format json

echo ""
echo "== PostgreSQL max affected rows guard smoke =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command insert \
  --db-uri "${DB_URI}" \
  --write \
  --sql "INSERT INTO users (name, age) VALUES ('max_guard_probe_user_1', 31)" \
  --format json >/dev/null

"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command insert \
  --db-uri "${DB_URI}" \
  --write \
  --sql "INSERT INTO users (name, age) VALUES ('max_guard_probe_user_2', 32)" \
  --format json >/dev/null

if MAX_GUARD_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command delete \
  --db-uri "${DB_URI}" \
  --write \
  --max-affected-rows 1 \
  --sql "DELETE FROM users WHERE name IN ('max_guard_probe_user_1', 'max_guard_probe_user_2')" \
  --format json)"; then
  echo "Expected max affected rows guard to fail." >&2
  printf '%s\n' "${MAX_GUARD_OUTPUT}" >&2
  exit 1
fi
printf '%s\n' "${MAX_GUARD_OUTPUT}"
printf '%s\n' "${MAX_GUARD_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok") is False, payload; assert payload.get("error", {}).get("code") == "affected_rows_exceeded", payload; data = payload.get("data", {}); assert data.get("affected_rows") == 2, payload; assert data.get("max_affected_rows") == 1, payload; assert data.get("committed") is False, payload'

echo ""
echo "== PostgreSQL max affected rows verification query =="
MAX_GUARD_VERIFY_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "SELECT COUNT(*) FROM users WHERE name IN ('max_guard_probe_user_1', 'max_guard_probe_user_2')" \
  --format json)"
printf '%s\n' "${MAX_GUARD_VERIFY_OUTPUT}"
printf '%s\n' "${MAX_GUARD_VERIFY_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; assert payload.get("data", {}).get("rows") == [[2]], payload'
psql_exec "DELETE FROM users WHERE name IN ('max_guard_probe_user_1', 'max_guard_probe_user_2');"

echo ""
echo "== PostgreSQL full-table write guard smoke =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command insert \
  --db-uri "${DB_URI}" \
  --write \
  --sql "INSERT INTO users (name, age) VALUES ('full_table_guard_user', 33)" \
  --format json >/dev/null

if FULL_TABLE_GUARD_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command delete \
  --db-uri "${DB_URI}" \
  --write \
  --sql "DELETE FROM users" \
  --format json)"; then
  echo "Expected full-table write guard to fail." >&2
  printf '%s\n' "${FULL_TABLE_GUARD_OUTPUT}" >&2
  exit 1
fi
printf '%s\n' "${FULL_TABLE_GUARD_OUTPUT}"
printf '%s\n' "${FULL_TABLE_GUARD_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok") is False, payload; assert payload.get("error", {}).get("code") == "full_table_write_requires_flag", payload; data = payload.get("data", {}); assert data.get("committed") is False, payload; assert data.get("safety_level") == "high", payload'

echo ""
echo "== PostgreSQL full-table write guard verification query =="
FULL_TABLE_GUARD_VERIFY_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "SELECT COUNT(*) FROM users WHERE name = 'full_table_guard_user'" \
  --format json)"
printf '%s\n' "${FULL_TABLE_GUARD_VERIFY_OUTPUT}"
printf '%s\n' "${FULL_TABLE_GUARD_VERIFY_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; assert payload.get("data", {}).get("rows") == [[1]], payload'
psql_exec "DELETE FROM users WHERE name = 'full_table_guard_user';"

echo ""
echo "== PostgreSQL direct join generation smoke =="
JOIN_GENERATE_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command generate \
  --db-uri "${DB_URI}" \
  --skill join_inner \
  --params '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}' \
  --format json)"
printf '%s\n' "${JOIN_GENERATE_OUTPUT}"

JOIN_SQL="$(printf '%s\n' "${JOIN_GENERATE_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; print(payload["sql"])')"

echo ""
echo "== PostgreSQL direct join verification query =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "${JOIN_SQL}" \
  --format json

echo ""
echo "== PostgreSQL direct left join generation smoke =="
JOIN_LEFT_GENERATE_OUTPUT="$("${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command generate \
  --db-uri "${DB_URI}" \
  --skill join_left \
  --params '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}' \
  --format json)"
printf '%s\n' "${JOIN_LEFT_GENERATE_OUTPUT}"

JOIN_LEFT_SQL="$(printf '%s\n' "${JOIN_LEFT_GENERATE_OUTPUT}" | "${VENV_DIR}/bin/python" -c 'import json, sys; payload = json.load(sys.stdin); assert payload.get("ok"), payload; print(payload["sql"])')"

echo ""
echo "== PostgreSQL direct left join verification query =="
"${VENV_DIR}/bin/python" "${ROOT_DIR}/main.py" \
  --command query \
  --db-uri "${DB_URI}" \
  --sql "${JOIN_LEFT_SQL}" \
  --format json
