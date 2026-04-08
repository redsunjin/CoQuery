#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="${ROOT_DIR}/.tmp"
REGISTRY_PATH="${TMP_DIR}/ollama_registry.json"
BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PROVIDER_NAME="${COQUERY_OLLAMA_PROVIDER_NAME:-local_ollama}"
MODEL_NAME="${COQUERY_OLLAMA_MODEL:-}"

mkdir -p "${TMP_DIR}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama command not found in PATH." >&2
  exit 1
fi

if [[ -z "${MODEL_NAME}" ]]; then
  MODEL_NAME="$(ollama list | awk 'NR==2 {print $1}')"
fi

if [[ -z "${MODEL_NAME}" ]]; then
  echo "No Ollama models found. Set COQUERY_OLLAMA_MODEL or install one first." >&2
  exit 1
fi

export COQUERY_LLM_REGISTRY_PATH="${REGISTRY_PATH}"

echo "== Register Ollama provider =="
"${PYTHON_BIN}" "${ROOT_DIR}/main.py" \
  --command provider_add \
  --provider-name "${PROVIDER_NAME}" \
  --provider-kind ollama \
  --base-url "${BASE_URL}" \
  --model-name "${MODEL_NAME}" \
  --format json

echo ""
echo "== List registered providers =="
"${PYTHON_BIN}" "${ROOT_DIR}/main.py" \
  --command provider_list \
  --format json

echo ""
echo "== Provider connectivity test =="
"${PYTHON_BIN}" "${ROOT_DIR}/main.py" \
  --command provider_test \
  --provider-name "${PROVIDER_NAME}" \
  --format json

echo ""
echo "== Natural command with registered Ollama provider =="
"${PYTHON_BIN}" "${ROOT_DIR}/main.py" \
  --command natural \
  --provider-name "${PROVIDER_NAME}" \
  --sql "count users" \
  --format json
