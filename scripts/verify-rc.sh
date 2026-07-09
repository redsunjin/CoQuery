#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

run_step() {
  local label="$1"
  shift
  echo "[rc] ${label}"
  "$@"
}

run_step "release candidate contract" python3 tests/rc_hardening_smoke.py
run_step "core CLI and Command API tests" python3 sql_cli/tests/test_core.py
run_step "terminal shell app smoke" python3 app_shell/terminal_shell_prototype/smoke.py
run_step "desktop/local packaging smoke" python3 tests/local_packaging_decision_smoke.py
run_step "iOS shell package smoke" npm run ios:shell:test
run_step "diff whitespace check" git diff --check

echo "[rc] release candidate checks passed"
