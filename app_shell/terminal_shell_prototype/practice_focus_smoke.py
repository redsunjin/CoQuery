#!/usr/bin/env python3
"""Static and executable smoke checks for the focused SQL practice workspace."""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent


def assert_contains(path: Path, text: str) -> None:
    content = path.read_text(encoding="utf-8")
    if text not in content:
        raise AssertionError(f"{path.name} missing expected text: {text}")


def main() -> int:
    onboarding = ROOT / "onboarding.js"
    focus_js = ROOT / "practice-focus.js"
    focus_css = ROOT / "practice-focus.css"
    visual_js = ROOT / "practice-result-visual.js"
    visual_css = ROOT / "practice-result-visual.css"
    flow_js = ROOT / "practice-query-flow.js"
    flow_css = ROOT / "practice-query-flow.css"
    flow_smoke = ROOT / "practice_query_flow_smoke.js"

    for path in (onboarding, focus_js, focus_css, visual_js, visual_css, flow_js, flow_css, flow_smoke):
        if not path.exists():
            raise AssertionError(f"missing practice focus asset: {path.name}")

    assert_contains(onboarding, "practice-focus.css")
    assert_contains(onboarding, "practice-focus.js")
    assert_contains(onboarding, "practice-result-visual.css")
    assert_contains(onboarding, "practice-result-visual.js")
    assert_contains(onboarding, "practice-query-flow.css")
    assert_contains(onboarding, "practice-query-flow.js")
    assert_contains(onboarding, 'script.addEventListener("load", loadPracticeResultIntelligenceAssets')
    assert_contains(focus_js, 'appShell.dataset.practiceFocus = enabled ? "true" : "false"')
    assert_contains(focus_js, "MutationObserver")
    assert_contains(focus_js, "practice-hint-toggle")
    assert_contains(focus_js, "practice-bank-button")
    assert_contains(focus_js, "practice_query")
    assert_contains(focus_js, "practice_grade")
    assert_contains(focus_js, "enhancePracticeQueryTable")
    assert_contains(focus_js, 'table.className = "practice-result-table"')
    assert_contains(focus_js, 'td.textContent = practiceResultCellText(value)')
    assert_contains(focus_js, 'value === null')
    assert_contains(focus_js, 'result.data?.result_intelligence')
    assert_contains(visual_js, "buildPracticeBarModel")
    assert_contains(visual_js, 'intelligence.shape !== "category_measure"')
    assert_contains(visual_js, 'intelligence.recommended_visual !== "bar"')
    assert_contains(visual_js, 'tableWrap.querySelector(".practice-result-table-scroll")')
    assert_contains(visual_js, 'point.value < 0')
    assert_contains(visual_js, 'width_percent: width')
    assert_contains(flow_js, "buildPracticeQueryFlowModel")
    assert_contains(flow_js, "RECOGNIZED_KINDS")
    assert_contains(flow_js, 'step.text.trim()')
    assert_contains(flow_js, 'figure.className = "practice-query-flow"')
    assert_contains(flow_js, "This is not the database execution order")
    assert_contains(focus_css, '.app-shell[data-practice-focus="true"]')
    assert_contains(focus_css, ".practice-focus-block")
    assert_contains(focus_css, ".practice-support-actions")
    assert_contains(focus_css, ".practice-result-table-scroll")
    assert_contains(focus_css, ".practice-result-table td.is-null")
    assert_contains(visual_css, ".practice-result-bar-visual")
    assert_contains(visual_css, ".practice-result-bar-zero")
    assert_contains(visual_css, ".practice-result-bar-fill.is-negative")
    assert_contains(visual_css, "@media (prefers-reduced-motion: reduce)")
    assert_contains(flow_css, ".practice-query-flow-track")
    assert_contains(flow_css, ".practice-query-flow-node:not(:last-child)::after")
    assert_contains(flow_css, "@media (prefers-reduced-motion: reduce)")
    assert_contains(focus_css, "@media (max-width: 760px)")

    subprocess.run(["node", str(flow_smoke)], cwd=ROOT, check=True)

    print("practice focus smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
