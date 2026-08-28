#!/usr/bin/env python3
"""Smoke checks for the expanded built-in SQL curriculum."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sql_cli.practice import practice_grade_handler  # noqa: E402

PACK_PATH = ROOT / "practice_packs" / "sql_basics.json"


def main() -> int:
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    problems = pack.get("problems", [])
    problem_ids = [problem.get("id") for problem in problems]

    assert len(problems) == 24, f"expected 24 curriculum problems, got {len(problems)}"
    assert len(problem_ids) == len(set(problem_ids)), "problem ids must be unique"

    original_ids = {
        "basic_select_customers",
        "paid_large_orders",
        "paid_order_customers",
        "paid_orders_by_region",
        "open_high_tickets",
    }
    assert original_ids.issubset(set(problem_ids)), "original practice problems must remain available"

    business = [problem for problem in problems if "business" in problem.get("concepts", [])]
    assert len(business) == 3, f"expected 3 business scenario problems, got {len(business)}"
    assert {problem["id"] for problem in business} == {
        "monthly_paid_sales",
        "high_value_paid_customers",
        "open_support_load_by_region",
    }

    expected_concepts = {
        "select",
        "where",
        "or",
        "in",
        "like",
        "join",
        "group_by",
        "count",
        "sum",
        "having",
        "limit",
        "date",
        "business",
    }
    concepts = {concept for problem in problems for concept in problem.get("concepts", [])}
    missing = expected_concepts - concepts
    assert not missing, f"missing curriculum concepts: {sorted(missing)}"

    for problem in problems:
        result = practice_grade_handler(
            problem_id=problem["id"],
            sql=problem["expected_sql"],
            pack="sql_basics",
            record=False,
        )
        assert result["ok"] is True, f"expected SQL failed for {problem['id']}: {result}"
        assert result["data"]["correct"] is True, f"expected SQL did not grade correct for {problem['id']}"

    curriculum_asset = (ROOT / "app_shell" / "terminal_shell_prototype" / "curriculum-expansion.js").read_text(encoding="utf-8")
    assert 'id: "business"' in curriculum_asset
    assert "업무 질문 해결하기" in curriculum_asset

    onboarding = (ROOT / "app_shell" / "terminal_shell_prototype" / "onboarding.js").read_text(encoding="utf-8")
    assert "loadExpandedCurriculumAsset" in onboarding
    assert "curriculum-expansion.js" in onboarding

    print("expanded curriculum smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
