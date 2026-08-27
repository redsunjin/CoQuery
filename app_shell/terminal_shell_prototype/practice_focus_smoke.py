#!/usr/bin/env python3
"""Static smoke checks for the focused SQL practice workspace."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def assert_contains(path: Path, text: str) -> None:
    content = path.read_text(encoding="utf-8")
    if text not in content:
        raise AssertionError(f"{path.name} missing expected text: {text}")


def main() -> int:
    onboarding = ROOT / "onboarding.js"
    focus_js = ROOT / "practice-focus.js"
    focus_css = ROOT / "practice-focus.css"

    for path in (onboarding, focus_js, focus_css):
        if not path.exists():
            raise AssertionError(f"missing practice focus asset: {path.name}")

    assert_contains(onboarding, "practice-focus.css")
    assert_contains(onboarding, "practice-focus.js")
    assert_contains(focus_js, 'appShell.dataset.practiceFocus = enabled ? "true" : "false"')
    assert_contains(focus_js, "MutationObserver")
    assert_contains(focus_js, "practice-hint-toggle")
    assert_contains(focus_js, "practice-bank-button")
    assert_contains(focus_js, "practice_query")
    assert_contains(focus_js, "practice_grade")
    assert_contains(focus_css, '.app-shell[data-practice-focus="true"]')
    assert_contains(focus_css, ".practice-focus-block")
    assert_contains(focus_css, ".practice-support-actions")
    assert_contains(focus_css, "@media (max-width: 760px)")

    print("practice focus smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
