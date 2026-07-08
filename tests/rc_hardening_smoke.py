#!/usr/bin/env python3
"""Smoke checks for the release-candidate hardening contract."""

from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFY_RC = ROOT / "scripts" / "verify-rc.sh"
README = ROOT / "readme.md"
RELEASE = ROOT / "RELEASE.md"
SERVICE_PLAN = ROOT / "SERVICE_LAUNCH_PLAN_2026-07-07.md"


def assert_contains(path: Path, expected: str) -> None:
    text = path.read_text(encoding="utf-8")
    if expected not in text:
        raise AssertionError(f"{path.relative_to(ROOT)} does not contain expected text: {expected}")


def main() -> int:
    if not VERIFY_RC.exists():
        raise AssertionError("scripts/verify-rc.sh should exist as the one-command RC verifier")
    if not os.access(VERIFY_RC, os.X_OK):
        raise AssertionError("scripts/verify-rc.sh should be executable")

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    if scripts.get("rc:verify") != "./scripts/verify-rc.sh":
        raise AssertionError('package.json should expose "rc:verify": "./scripts/verify-rc.sh"')

    verify_text = VERIFY_RC.read_text(encoding="utf-8")
    required_steps = [
        "python3 tests/rc_hardening_smoke.py",
        "python3 sql_cli/tests/test_core.py",
        "python3 app_shell/terminal_shell_prototype/smoke.py",
        "python3 tests/local_packaging_decision_smoke.py",
        "npm run ios:shell:test",
    ]
    for step in required_steps:
        if step not in verify_text:
            raise AssertionError(f"scripts/verify-rc.sh should run: {step}")

    assert_contains(README, "## Launch Quickstart")
    assert_contains(README, "npm run rc:verify")
    assert_contains(README, "npm run local:shell")
    assert_contains(README, "http://127.0.0.1:8765")
    assert_contains(README, "CLI, Command API, app shell smoke, practice flow, provider setup, bilingual help")
    assert_contains(README, "Supported launch claims")
    assert_contains(README, "Unsupported launch claims")

    assert_contains(RELEASE, "## Exact Release Claims")
    assert_contains(RELEASE, "Supported claims")
    assert_contains(RELEASE, "Unsupported claims")
    assert_contains(RELEASE, "Production Assist Safety Gate")
    assert_contains(RELEASE, "packaged production DB assistant")

    assert_contains(SERVICE_PLAN, "Launch Goal 10: Release Candidate Hardening")
    assert_contains(SERVICE_PLAN, "One command runs all launch checks")
    assert_contains(SERVICE_PLAN, "Release Candidate Hardening.")

    print("release candidate hardening smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
