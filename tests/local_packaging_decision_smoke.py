#!/usr/bin/env python3
"""Smoke checks for the Desktop/Local Packaging Decision."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_DOC = ROOT / "docs" / "desktop-local-packaging-decision.md"
START_SCRIPT = ROOT / "scripts" / "start_local_shell.py"


def assert_contains(path: Path, expected: str) -> None:
    text = path.read_text(encoding="utf-8")
    if expected not in text:
        raise AssertionError(f"{path.relative_to(ROOT)} does not contain expected text: {expected}")


def main() -> int:
    if not START_SCRIPT.exists():
        raise AssertionError("scripts/start_local_shell.py should exist as the stable local start command")
    if not DECISION_DOC.exists():
        raise AssertionError("docs/desktop-local-packaging-decision.md should document the selected launch path")

    help_result = subprocess.run(
        [sys.executable, str(START_SCRIPT), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if help_result.returncode != 0:
        raise AssertionError(help_result.stderr or help_result.stdout)
    if "--host" not in help_result.stdout or "--port" not in help_result.stdout:
        raise AssertionError("start command help should expose --host and --port")

    assert_contains(DECISION_DOC, "Selected launch target: local web app first")
    assert_contains(DECISION_DOC, "python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765")
    assert_contains(DECISION_DOC, "app_shell/terminal_shell_prototype/.runtime/llm_providers.json")
    assert_contains(DECISION_DOC, ".coquery/practice_attempts.jsonl")
    assert_contains(DECISION_DOC, "COQUERY_LLM_REGISTRY_PATH")
    assert_contains(DECISION_DOC, "COQUERY_PRACTICE_ATTEMPT_LOG")
    assert_contains(DECISION_DOC, "Update path")
    assert_contains(DECISION_DOC, "Rollback path")

    assert_contains(ROOT / "readme.md", "docs/desktop-local-packaging-decision.md")
    assert_contains(ROOT / "readme.md", "python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765")
    assert_contains(ROOT / "package.json", '"local:shell"')
    assert_contains(ROOT / "SERVICE_LAUNCH_PLAN_2026-07-07.md", "Launch Goal 8: Desktop/Local Packaging Decision")
    assert_contains(ROOT / "SERVICE_LAUNCH_PLAN_2026-07-07.md", "Selected launch target: local web app first")

    print("local packaging decision smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
