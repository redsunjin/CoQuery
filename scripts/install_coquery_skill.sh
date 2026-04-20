#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_ROOT="${1:-${COQUERY_SKILL_TARGET_ROOT:-$HOME/.codex/skills}}"

python3 "${ROOT_DIR}/skills/coquery-cli/scripts/coquery_agent.py" install-skill \
  --repo "${ROOT_DIR}" \
  --target-root "${TARGET_ROOT}"
