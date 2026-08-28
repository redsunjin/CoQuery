#!/usr/bin/env python3
"""Static QA checks for the learning-first CoQuery user flow."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(path: Path, *needles: str) -> None:
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise AssertionError(f"{path.name} missing expected user-flow contract: {needle}")


def main() -> int:
    focus_js = ROOT / "practice-focus.js"
    focus_css = ROOT / "practice-focus.css"
    learning_js = ROOT / "learning-path.js"

    require(
        focus_js,
        'nextProblem: "다음 문제"',
        'reviewPath: "학습경로 보기"',
        "async function openPracticeLearningPath()",
        'setLearningPathMode(true)',
        "async function startNextPracticeProblem(currentProblemId)",
        '"practice_schema", "practice_attempts", "practice_feedback"',
        "addPracticeGradeNavigation(block)",
        'result.data?.correct !== true',
    )
    require(
        focus_css,
        '.terminal-block:not(.practice-focus-block):not(.practice-feedback-block)',
    )
    require(
        learning_js,
        "function setLearningPathMode(enabled)",
        "async function refreshLearningPath()",
        "function startProblemFromLearningPath(problem, packId)",
    )

    print("user-flow QA smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
