#!/usr/bin/env python3
"""Static checks for the learning-path problem bank layer."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(path: Path, *needles: str) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise AssertionError(f"{path.name} missing: {', '.join(missing)}")


def main() -> int:
    require(
        ROOT / "onboarding.js",
        "loadLearningPathAssets",
        "learning-path.css",
        "learning-path.js",
        "nextPracticeProblem",
        'postCommand("practice_attempts"',
        "attempt.correct === true",
    )
    require(
        ROOT / "learning-path.js",
        "learningPathUnits",
        "buildLearningPathSnapshot",
        "completedCount",
        "attemptedCount",
        "nextProblem",
        "data-learning-filter",
        "data-learning-problem",
        "practice_attempts",
        "practice_grade",
        "startProblemFromLearningPath",
        "updateLearningHomeProgress",
    )
    require(
        ROOT / "learning-path.css",
        'data-learning-path="true"',
        ".learning-path-block",
        ".learning-unit",
        ".learning-problem-card",
        ".learning-home-progress",
        "@media (max-width: 760px)",
    )
    print("learning path static smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
