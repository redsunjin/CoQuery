#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="${ROOT_DIR}/.tmp"
VENV_DIR="${TMP_DIR}/pg-venv"
DATA_DIR="${TMP_DIR}/pg-smoke"
LOG_FILE="${TMP_DIR}/pg-smoke.log"
SOCKET_DIR="${TMP_DIR}/pg-socket"
PORT="${COQUERY_PG_PORT:-49251}"
DB_NAME="${COQUERY_PG_DB:-coquery_probe}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
POSTGRES_BIN_DIR="${POSTGRES_BIN_DIR:-}"

if [[ -z "${POSTGRES_BIN_DIR}" ]]; then
  if command -v pg_ctl >/dev/null 2>&1; then
    POSTGRES_BIN_DIR="$(cd "$(dirname "$(command -v pg_ctl)")" && pwd)"
  elif [[ -d "/Users/Agent/homebrew/opt/postgresql@18/bin" ]]; then
    POSTGRES_BIN_DIR="/Users/Agent/homebrew/opt/postgresql@18/bin"
  elif [[ -d "/opt/homebrew/opt/postgresql@18/bin" ]]; then
    POSTGRES_BIN_DIR="/opt/homebrew/opt/postgresql@18/bin"
  fi
fi

mkdir -p "${TMP_DIR}" "${SOCKET_DIR}"

if [[ ! -x "${POSTGRES_BIN_DIR}/pg_ctl" || ! -x "${POSTGRES_BIN_DIR}/psql" || ! -x "${POSTGRES_BIN_DIR}/initdb" ]]; then
  echo "PostgreSQL binaries not found. Add them to PATH or set POSTGRES_BIN_DIR." >&2
  echo "Current PATH lookup failed; tried POSTGRES_BIN_DIR='${POSTGRES_BIN_DIR}'." >&2
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

if ! "${VENV_DIR}/bin/python" -c "import psycopg" >/dev/null 2>&1; then
  "${VENV_DIR}/bin/python" -m pip install "psycopg[binary]" >/dev/null
fi

if [[ ! -f "${DATA_DIR}/PG_VERSION" ]]; then
  rm -rf "${DATA_DIR}"
  mkdir -p "${DATA_DIR}"
  LC_ALL=en_US.UTF-8 "${POSTGRES_BIN_DIR}/initdb" -D "${DATA_DIR}" >/dev/null
fi

cleanup() {
  if [[ -f "${DATA_DIR}/postmaster.pid" ]]; then
    "${POSTGRES_BIN_DIR}/pg_ctl" -D "${DATA_DIR}" stop -m fast >/dev/null || true
  fi
}
trap cleanup EXIT

"${POSTGRES_BIN_DIR}/pg_ctl" \
  -D "${DATA_DIR}" \
  -l "${LOG_FILE}" \
  -o "-k ${SOCKET_DIR} -p ${PORT}" \
  start >/dev/null

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

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT, age INTEGER);" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "CREATE TABLE IF NOT EXISTS orgs (id SERIAL PRIMARY KEY, name TEXT NOT NULL UNIQUE);" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "CREATE TABLE IF NOT EXISTS members (id SERIAL PRIMARY KEY, org_id INTEGER NOT NULL REFERENCES orgs(id) ON DELETE CASCADE, email TEXT NOT NULL UNIQUE);" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "INSERT INTO users (name, age) SELECT 'probe_user', 34 WHERE NOT EXISTS (SELECT 1 FROM users WHERE name = 'probe_user');" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "DELETE FROM users WHERE name = 'insert_probe_user';" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "DELETE FROM users WHERE name = 'update_probe_user';" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "DELETE FROM users WHERE name = 'delete_probe_user';" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "DELETE FROM members WHERE email = 'join_probe_member@example.com';" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "DELETE FROM orgs WHERE name = 'join_probe_org';" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "INSERT INTO orgs (name) SELECT 'join_probe_org' WHERE NOT EXISTS (SELECT 1 FROM orgs WHERE name = 'join_probe_org');" >/dev/null

"${POSTGRES_BIN_DIR}/psql" \
  -h "${SOCKET_DIR}" \
  -p "${PORT}" \
  -d "${DB_NAME}" \
  -c "INSERT INTO members (org_id, email) SELECT id, 'join_probe_member@example.com' FROM orgs WHERE name = 'join_probe_org' AND NOT EXISTS (SELECT 1 FROM members WHERE email = 'join_probe_member@example.com');" >/dev/null

DB_URI="postgresql://localhost/${DB_NAME}?host=${SOCKET_DIR}&port=${PORT}"

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
