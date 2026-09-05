#!/usr/bin/env python3
"""Executable contract tests for CoQuery BI result intelligence."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sql_cli.result_intelligence import classify_result, extract_sql_flow_steps


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def test_category_measure() -> None:
    rows = [
        {"region": "Seoul", "customer_count": 32},
        {"region": "Busan", "customer_count": 18},
        {"region": "Daejeon", "customer_count": 11},
    ]
    sql = "SELECT region, COUNT(*) AS customer_count FROM customers GROUP BY region ORDER BY customer_count DESC"
    result = classify_result(["region", "customer_count"], rows, sql)
    assert_equal(result["shape"], "category_measure", "category shape")
    assert_equal(result["recommended_view"], "visual", "category view")
    assert_equal(result["recommended_visual"], "bar", "category visual")
    assert_equal(result["dimensions"], ["region"], "category dimension")
    assert_equal(result["measures"], ["customer_count"], "category measure")
    assert_equal(
        [step["kind"] for step in result["flow_steps"]],
        ["from", "group_by", "aggregate", "order_by"],
        "category SQL flow",
    )


def test_ambiguous_rows_fall_back_to_table() -> None:
    rows = [
        {"id": 1, "name": "A", "region": "Seoul"},
        {"id": 2, "name": "B", "region": "Busan"},
    ]
    result = classify_result(["id", "name", "region"], rows, "SELECT id, name, region FROM customers")
    assert_equal(result["shape"], "tabular", "tabular shape")
    assert_equal(result["recommended_view"], "table", "tabular view")
    assert_equal(result["recommended_visual"], None, "tabular visual")


def test_time_series_requires_chartable_order() -> None:
    ordered_rows = [
        {"month": "2026-01", "revenue": 100},
        {"month": "2026-02", "revenue": 120},
        {"month": "2026-03", "revenue": 115},
    ]
    ordered = classify_result(["month", "revenue"], ordered_rows, "SELECT month, revenue FROM monthly ORDER BY month")
    assert_equal(ordered["shape"], "time_series", "time-series shape")
    assert_equal(ordered["recommended_visual"], "line", "time-series visual")

    unordered_rows = [ordered_rows[1], ordered_rows[0], ordered_rows[2]]
    unordered = classify_result(["month", "revenue"], unordered_rows, "SELECT month, revenue FROM monthly")
    assert_equal(unordered["shape"], "time_series", "unordered time-series shape")
    assert_equal(unordered["recommended_view"], "table", "unordered time-series fallback")
    assert_equal(unordered["recommended_visual"], None, "unordered time-series visual")


def test_part_to_whole_requires_explicit_total() -> None:
    rows = [
        {"segment": "A", "percentage": 50},
        {"segment": "B", "percentage": 30},
        {"segment": "C", "percentage": 20},
    ]
    result = classify_result(["segment", "percentage"], rows, "SELECT segment, percentage FROM mix")
    assert_equal(result["shape"], "part_to_whole", "part-to-whole shape")
    assert_equal(result["recommended_visual"], "ring", "part-to-whole visual")

    incomplete = copy.deepcopy(rows)
    incomplete[-1]["percentage"] = 10
    fallback = classify_result(["segment", "percentage"], incomplete, "SELECT segment, percentage FROM mix")
    assert_equal(fallback["shape"], "category_measure", "incomplete share falls back to bar")
    assert_equal(fallback["recommended_visual"], "bar", "incomplete share visual")


def test_numeric_relationship_excludes_identifier_columns() -> None:
    rows = [
        {"ad_spend": 1000, "revenue": 5000},
        {"ad_spend": 1500, "revenue": 6500},
        {"ad_spend": 2200, "revenue": 8100},
    ]
    result = classify_result(["ad_spend", "revenue"], rows, "SELECT ad_spend, revenue FROM observations")
    assert_equal(result["shape"], "numeric_relationship", "numeric relationship shape")
    assert_equal(result["recommended_visual"], "scatter", "numeric relationship visual")

    id_rows = [{"id": 1, "revenue": 5000}, {"id": 2, "revenue": 6500}]
    id_result = classify_result(["id", "revenue"], id_rows, "SELECT id, revenue FROM observations")
    assert_equal(id_result["shape"], "tabular", "identifier numeric fallback")
    assert_equal(id_result["recommended_view"], "table", "identifier numeric view")


def test_stage_and_source_target_flow() -> None:
    funnel_rows = [
        {"stage": "visit", "count": 100},
        {"stage": "signup", "count": 40},
        {"stage": "purchase", "count": 12},
    ]
    funnel = classify_result(
        ["stage", "count"],
        funnel_rows,
        "SELECT stage, count FROM funnel ORDER BY stage_order",
    )
    assert_equal(funnel["shape"], "stage_funnel", "funnel shape")
    assert_equal(funnel["recommended_visual"], "funnel", "funnel visual")

    flow_rows = [
        {"source": "visit", "target": "signup", "value": 40},
        {"source": "signup", "target": "purchase", "value": 12},
    ]
    flow = classify_result(["source", "target", "value"], flow_rows, "SELECT source, target, value FROM flow_edges")
    assert_equal(flow["shape"], "source_target_flow", "source-target shape")
    assert_equal(flow["recommended_view"], "flow", "source-target view")
    assert_equal(flow["recommended_visual"], "sankey", "source-target visual")


def test_zero_nulls_and_category_guardrail() -> None:
    rows = [{"region": "A", "count": 0}, {"region": "B", "count": 2}]
    result = classify_result(["region", "count"], rows, "SELECT region, COUNT(*) AS count FROM x GROUP BY region")
    assert_equal(result["shape"], "category_measure", "zero remains numeric")

    rows_with_null = [{"region": "A", "count": None}, {"region": "B", "count": 2}]
    null_result = classify_result(["region", "count"], rows_with_null, "SELECT region, count FROM x")
    assert_equal(null_result["recommended_view"], "table", "null measure fallback")

    many_rows = [{"category": f"C{i}", "count": i} for i in range(21)]
    many = classify_result(["category", "count"], many_rows, "SELECT category, count FROM x")
    assert_equal(many["recommended_view"], "table", "too many categories fallback")
    assert_equal(many["recommended_visual"], None, "too many categories visual")


def test_single_metric_does_not_infer_gauge() -> None:
    result = classify_result(["total"], [{"total": 42}], "SELECT COUNT(*) AS total FROM customers")
    assert_equal(result["shape"], "single_metric", "single metric shape")
    assert_equal(result["recommended_view"], "table", "single metric default")
    assert_equal(result["recommended_visual"], None, "single metric no gauge")


def test_classifier_is_deterministic_and_non_mutating() -> None:
    rows = [{"region": "A", "count": 1}, {"region": "B", "count": 2}]
    original = copy.deepcopy(rows)
    sql = "SELECT region, COUNT(*) AS count FROM customers GROUP BY region"
    first = classify_result(["region", "count"], rows, sql)
    second = classify_result(["region", "count"], rows, sql)
    assert_equal(first, second, "deterministic classification")
    assert_equal(rows, original, "rows must remain unchanged")


def test_sql_flow_only_contains_explicit_clauses() -> None:
    sql = (
        "SELECT region, COUNT(*) AS count FROM customers "
        "WHERE active = 1 GROUP BY region HAVING COUNT(*) > 1 "
        "ORDER BY count DESC LIMIT 5"
    )
    steps = extract_sql_flow_steps(sql)
    assert_equal(
        [step["kind"] for step in steps],
        ["from", "where", "group_by", "aggregate", "having", "order_by", "limit"],
        "explicit SQL flow kinds",
    )
    if any("JOIN" in step["text"] for step in steps):
        raise AssertionError("flow invented a JOIN that was not present")


def main() -> int:
    test_category_measure()
    test_ambiguous_rows_fall_back_to_table()
    test_time_series_requires_chartable_order()
    test_part_to_whole_requires_explicit_total()
    test_numeric_relationship_excludes_identifier_columns()
    test_stage_and_source_target_flow()
    test_zero_nulls_and_category_guardrail()
    test_single_metric_does_not_infer_gauge()
    test_classifier_is_deterministic_and_non_mutating()
    test_sql_flow_only_contains_explicit_clauses()
    print("result intelligence tests: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
