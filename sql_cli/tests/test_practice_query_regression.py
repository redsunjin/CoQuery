#!/usr/bin/env python3
"""Regression gate for the existing CoQuery practice-query learner flow.

This test intentionally protects the behavior that BI Result Intelligence must not break:
- practice catalog remains available
- practice_query preserves columns/rows/row_count and app-facing metadata
- BI metadata is additive and does not mutate canonical result evidence
- correct grading still succeeds without recording a learner attempt
- invalid/non-SELECT SQL still fails through the existing structured error contract
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sql_cli.command_api import run_command
from sql_cli.result_integration import enrich_practice_query_result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    catalog = run_command("practice_list", {}, {"mode": "training"})
    require(catalog["ok"] is True, "practice_list must remain available")
    require(catalog["block_type"] == "practice_list", "practice_list block type changed")
    problems = catalog["data"].get("problems") or []
    require(len(problems) >= 24, "24-problem learner baseline regressed")
    require(any(problem.get("id") == "basic_select_customers" for problem in problems), "first practice problem missing")

    sql = "SELECT region, COUNT(*) AS customer_count FROM customers GROUP BY region ORDER BY region"
    query = run_command("practice_query", {"sql": sql, "pack": "sql_basics", "limit": 50}, {"mode": "training"})
    require(query["ok"] is True, "practice_query must succeed for a valid SELECT")
    require(query["block_type"] == "practice_query_result", "practice_query block type changed")
    require(query["actions"] == ["copy", "grade", "save_attempt"], "practice_query actions changed")
    require(query["data"]["columns"] == ["region", "customer_count"], "practice_query columns changed")
    require(
        query["data"]["rows"]
        == [
            {"region": "Busan", "customer_count": 1},
            {"region": "Incheon", "customer_count": 1},
            {"region": "Seoul", "customer_count": 2},
        ],
        "practice_query rows changed",
    )
    require(query["data"]["row_count"] == 3, "practice_query row_count changed")
    require(query["data"]["sql"] == sql, "practice_query must preserve submitted SQL")
    require(query["data"]["mode_context"]["mode"] == "training", "training mode context changed")

    raw_columns = list(query["data"]["columns"])
    raw_rows = [dict(row) for row in query["data"]["rows"]]
    raw_row_count = query["data"]["row_count"]
    enriched = enrich_practice_query_result(query, {"sql": sql})
    intelligence = enriched["data"].get("result_intelligence") or {}
    require(intelligence.get("shape") == "category_measure", "category + measure classification changed")
    require(intelligence.get("recommended_view") == "visual", "category + measure should recommend Visual")
    require(intelligence.get("recommended_visual") == "bar", "category + measure should recommend Bar")
    require(intelligence.get("dimensions") == ["region"], "dimension classification changed")
    require(intelligence.get("measures") == ["customer_count"], "measure classification changed")
    require("result_intelligence" not in query["data"], "BI enrichment must not mutate the raw result data mapping")
    require(enriched["data"]["columns"] == raw_columns, "BI enrichment altered canonical columns")
    require(enriched["data"]["rows"] == raw_rows, "BI enrichment altered canonical rows")
    require(enriched["data"]["row_count"] == raw_row_count, "BI enrichment altered canonical row_count")

    grade_sql = "SELECT id, name, region FROM customers ORDER BY id"
    grade = run_command(
        "practice_grade",
        {"problem_id": "basic_select_customers", "sql": grade_sql, "pack": "sql_basics", "no_record": True},
        {"mode": "training"},
    )
    require(grade["ok"] is True, "practice_grade must remain callable")
    require(grade["data"]["correct"] is True, "known-correct learner answer no longer grades correctly")
    require(grade["data"]["attempt_recorded"] is False, "no_record regression: test must not write learner history")
    require(grade["data"]["actual"]["columns"] == ["id", "name", "region"], "grading result columns changed")
    require(grade["data"]["actual"]["row_count"] == 4, "grading result row count changed")

    invalid = run_command("practice_query", {"sql": "DELETE FROM customers"}, {"mode": "training"})
    require(invalid["ok"] is False, "non-SELECT practice SQL must remain blocked")
    require(invalid["error"]["code"] == "practice_sql_not_select", "structured non-SELECT error contract changed")
    require(invalid["block_type"] == "practice_query_result", "failed practice_query block type changed")
    require(enrich_practice_query_result(invalid, {"sql": "DELETE FROM customers"}) is invalid, "failed results must not be rewritten")

    print("practice-query regression gate: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
