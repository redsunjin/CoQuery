#!/usr/bin/env python3
"""Deterministic BI/result-shape interpretation for CoQuery query results.

This module intentionally avoids external AI and renderer dependencies.  It
classifies only what can be defended from the returned columns/values and the
submitted SQL.  Table is the canonical fallback when evidence is ambiguous.
"""

from __future__ import annotations

import math
import re
from typing import Any, Iterable


AGGREGATE_RE = re.compile(r"\b(COUNT|SUM|AVG|MIN|MAX)\s*\([^)]*\)(?:\s+AS\s+[A-Za-z_][A-Za-z0-9_]*)?", re.IGNORECASE)
TEMPORAL_NAMES = {
    "date",
    "day",
    "datetime",
    "month",
    "quarter",
    "time",
    "timestamp",
    "week",
    "year",
}
PART_TO_WHOLE_NAMES = {"pct", "percent", "percentage", "ratio", "share"}
STAGE_NAMES = {"phase", "stage", "step"}
FLOW_COLUMNS = {"source", "target", "value"}
MAX_BAR_CATEGORIES = 20
MAX_PARTS = 6


def _normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def _name_tokens(name: str) -> set[str]:
    normalized = _normalize_name(name)
    return {token for token in normalized.split("_") if token}


def _is_identifier_name(name: str) -> bool:
    normalized = _normalize_name(name)
    return normalized == "id" or normalized.endswith("_id")


def _is_temporal_name(name: str) -> bool:
    tokens = _name_tokens(name)
    return bool(tokens & TEMPORAL_NAMES)


def _is_part_to_whole_name(name: str) -> bool:
    tokens = _name_tokens(name)
    return bool(tokens & PART_TO_WHOLE_NAMES)


def _is_stage_name(name: str) -> bool:
    return bool(_name_tokens(name) & STAGE_NAMES)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _non_null_values(rows: Iterable[dict[str, Any]], column: str) -> list[Any]:
    return [row.get(column) for row in rows if row.get(column) is not None]


def _temporal_key(value: Any) -> tuple[Any, ...] | None:
    if _is_number(value):
        return (float(value),)
    text = str(value).strip()
    if re.fullmatch(r"\d{4}", text):
        return (int(text),)
    match = re.fullmatch(r"(\d{4})-(\d{1,2})(?:-(\d{1,2}))?", text)
    if match:
        return tuple(int(part or 0) for part in match.groups())
    match = re.fullmatch(r"(\d{4})[./](\d{1,2})(?:[./](\d{1,2}))?", text)
    if match:
        return tuple(int(part or 0) for part in match.groups())
    return None


def _is_ordered_temporal(values: list[Any]) -> bool:
    keys = [_temporal_key(value) for value in values]
    if not keys or any(key is None for key in keys):
        return False
    concrete = [key for key in keys if key is not None]
    return concrete == sorted(concrete) or concrete == sorted(concrete, reverse=True)


def _column_profile(column: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    values = _non_null_values(rows, column)
    null_count = len(rows) - len(values)
    identifier = _is_identifier_name(column)

    if values and all(_is_number(value) for value in values):
        kind = "temporal" if _is_temporal_name(column) else "numeric"
    elif values and _is_temporal_name(column) and all(_temporal_key(value) is not None for value in values):
        kind = "temporal"
    elif values:
        kind = "categorical"
    else:
        kind = "unknown"

    distinct = {repr(value) for value in values}
    return {
        "name": column,
        "kind": kind,
        "identifier": identifier,
        "null_count": null_count,
        "distinct_count": len(distinct),
    }


def _base_result(
    *,
    shape: str,
    recommended_view: str,
    recommended_visual: str | None,
    confidence: float,
    reason: str,
    dimensions: list[str],
    measures: list[str],
    profiles: list[dict[str, Any]],
    flow_steps: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "shape": shape,
        "recommended_view": recommended_view,
        "recommended_visual": recommended_visual,
        "confidence": confidence,
        "reason": reason,
        "dimensions": dimensions,
        "measures": measures,
        "column_profiles": profiles,
        "flow_steps": flow_steps,
    }


def _extract_clause(text: str, clause: str, stop_clauses: list[str]) -> str | None:
    stops = "|".join(re.escape(item) for item in stop_clauses)
    pattern = rf"\b{re.escape(clause)}\b\s+(.+?)(?=\b(?:{stops})\b|$)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return f"{clause.upper()} {match.group(1).strip()}"


def extract_sql_flow_steps(sql: str | None) -> list[dict[str, str]]:
    """Return explicit, conservative SQL transformation steps.

    The parser is deliberately small. Unsupported/nested syntax is not
    interpreted beyond clause fragments that are explicitly recognized.
    """

    text = re.sub(r"\s+", " ", str(sql or "").strip()).rstrip(";")
    if not text:
        return []

    steps: list[dict[str, str]] = []

    from_match = re.search(
        r"\bFROM\b\s+(.+?)(?=\b(?:LEFT\s+JOIN|RIGHT\s+JOIN|FULL\s+JOIN|INNER\s+JOIN|CROSS\s+JOIN|JOIN|WHERE|GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT)\b|$)",
        text,
        flags=re.IGNORECASE,
    )
    if from_match:
        steps.append({"kind": "from", "text": f"FROM {from_match.group(1).strip()}"})

    join_pattern = re.compile(
        r"\b((?:LEFT|RIGHT|FULL|INNER|CROSS)\s+JOIN|JOIN)\b\s+(.+?)(?=\b(?:LEFT\s+JOIN|RIGHT\s+JOIN|FULL\s+JOIN|INNER\s+JOIN|CROSS\s+JOIN|JOIN|WHERE|GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT)\b|$)",
        flags=re.IGNORECASE,
    )
    for match in join_pattern.finditer(text):
        steps.append({"kind": "join", "text": f"{match.group(1).upper()} {match.group(2).strip()}"})

    clause_specs = [
        ("WHERE", ["GROUP BY", "HAVING", "ORDER BY", "LIMIT"], "where"),
        ("GROUP BY", ["HAVING", "ORDER BY", "LIMIT"], "group_by"),
    ]
    for clause, stops, kind in clause_specs:
        fragment = _extract_clause(text, clause, stops)
        if fragment:
            steps.append({"kind": kind, "text": fragment})

    select_match = re.search(r"\bSELECT\b\s+(.+?)\s+\bFROM\b", text, flags=re.IGNORECASE)
    if select_match:
        for aggregate in AGGREGATE_RE.finditer(select_match.group(1)):
            steps.append({"kind": "aggregate", "text": aggregate.group(0).strip()})

    for clause, stops, kind in [
        ("HAVING", ["ORDER BY", "LIMIT"], "having"),
        ("ORDER BY", ["LIMIT"], "order_by"),
        ("LIMIT", [], "limit"),
    ]:
        if stops:
            fragment = _extract_clause(text, clause, stops)
        else:
            match = re.search(rf"\b{re.escape(clause)}\b\s+(.+)$", text, flags=re.IGNORECASE)
            fragment = f"{clause} {match.group(1).strip()}" if match else None
        if fragment:
            steps.append({"kind": kind, "text": fragment})

    return steps


def classify_result(
    columns: Iterable[str],
    rows: Iterable[dict[str, Any]],
    sql: str | None = None,
    problem_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify a returned SQL result into a truthful BI/result shape."""

    del problem_metadata  # Reserved for later deterministic teaching hints.

    column_list = [str(column) for column in columns]
    row_list = [dict(row) for row in rows]
    profiles = [_column_profile(column, row_list) for column in column_list]
    flow_steps = extract_sql_flow_steps(sql)

    if not column_list:
        return _base_result(
            shape="unknown",
            recommended_view="table",
            recommended_visual=None,
            confidence=1.0,
            reason="No returned columns are available to classify.",
            dimensions=[],
            measures=[],
            profiles=profiles,
            flow_steps=flow_steps,
        )

    profile_by_name = {profile["name"]: profile for profile in profiles}
    numeric = [
        column
        for column in column_list
        if profile_by_name[column]["kind"] == "numeric" and not profile_by_name[column]["identifier"]
    ]
    temporal = [column for column in column_list if profile_by_name[column]["kind"] == "temporal"]
    categorical = [column for column in column_list if profile_by_name[column]["kind"] == "categorical"]
    normalized_columns = {_normalize_name(column): column for column in column_list}
    sql_text = str(sql or "")
    has_grouping = bool(re.search(r"\bGROUP\s+BY\b", sql_text, flags=re.IGNORECASE))
    has_aggregate = bool(AGGREGATE_RE.search(sql_text))
    has_order = bool(re.search(r"\bORDER\s+BY\b", sql_text, flags=re.IGNORECASE))

    if set(normalized_columns) == FLOW_COLUMNS:
        value_column = normalized_columns["value"]
        if profile_by_name[value_column]["kind"] == "numeric":
            return _base_result(
                shape="source_target_flow",
                recommended_view="flow",
                recommended_visual="sankey",
                confidence=0.99,
                reason="The result exposes exact source, target, and numeric value columns.",
                dimensions=[normalized_columns["source"], normalized_columns["target"]],
                measures=[value_column],
                profiles=profiles,
                flow_steps=flow_steps,
            )

    if len(column_list) == 1 and len(row_list) == 1 and numeric:
        return _base_result(
            shape="single_metric",
            recommended_view="table",
            recommended_visual=None,
            confidence=0.99,
            reason="The result is one numeric metric; no target or range was provided for a gauge.",
            dimensions=[],
            measures=[numeric[0]],
            profiles=profiles,
            flow_steps=flow_steps,
        )

    if len(column_list) == 2 and len(row_list) >= 2:
        measure_candidates = [column for column in column_list if column in numeric]
        dimension_candidates = [column for column in column_list if column not in measure_candidates]

        if len(temporal) == 1 and len(measure_candidates) == 1:
            time_column = temporal[0]
            measure_column = measure_candidates[0]
            time_values = _non_null_values(row_list, time_column)
            complete = (
                len(time_values) == len(row_list)
                and len(_non_null_values(row_list, measure_column)) == len(row_list)
            )
            ordered = complete and _is_ordered_temporal(time_values)
            return _base_result(
                shape="time_series",
                recommended_view="visual" if ordered else "table",
                recommended_visual="line" if ordered else None,
                confidence=0.96 if ordered else 0.75,
                reason=(
                    "A temporal dimension and numeric measure are returned in chronological order."
                    if ordered
                    else "A temporal dimension and numeric measure are present, but the returned time order is not safely chartable."
                ),
                dimensions=[time_column],
                measures=[measure_column],
                profiles=profiles,
                flow_steps=flow_steps,
            )

        if len(measure_candidates) == 1 and len(dimension_candidates) == 1:
            dimension = dimension_candidates[0]
            measure = measure_candidates[0]
            dimension_profile = profile_by_name[dimension]
            measure_values = _non_null_values(row_list, measure)
            dimension_values = _non_null_values(row_list, dimension)
            complete = len(measure_values) == len(row_list) and len(dimension_values) == len(row_list)

            if (
                complete
                and len(row_list) <= MAX_PARTS
                and _is_part_to_whole_name(measure)
                and measure_values
                and (
                    math.isclose(sum(float(value) for value in measure_values), 100.0, abs_tol=0.5)
                    or math.isclose(sum(float(value) for value in measure_values), 1.0, abs_tol=0.01)
                )
            ):
                return _base_result(
                    shape="part_to_whole",
                    recommended_view="visual",
                    recommended_visual="ring",
                    confidence=0.98,
                    reason="The measure is explicitly a share/percentage and the returned parts form a complete total.",
                    dimensions=[dimension],
                    measures=[measure],
                    profiles=profiles,
                    flow_steps=flow_steps,
                )

            if complete and _is_stage_name(dimension) and has_order:
                return _base_result(
                    shape="stage_funnel",
                    recommended_view="visual",
                    recommended_visual="funnel",
                    confidence=0.95,
                    reason="The result has an explicit stage dimension, numeric measure, and SQL ORDER BY.",
                    dimensions=[dimension],
                    measures=[measure],
                    profiles=profiles,
                    flow_steps=flow_steps,
                )

            stable_category = (
                dimension_profile["kind"] == "categorical"
                and complete
                and dimension_profile["distinct_count"] == len(row_list)
                and len(row_list) <= MAX_BAR_CATEGORIES
            )
            if stable_category:
                return _base_result(
                    shape="category_measure",
                    recommended_view="visual",
                    recommended_visual="bar",
                    confidence=0.94,
                    reason="The result has one stable category dimension and one numeric measure.",
                    dimensions=[dimension],
                    measures=[measure],
                    profiles=profiles,
                    flow_steps=flow_steps,
                )

        if len(numeric) == 2 and not has_grouping and not has_aggregate:
            complete = all(len(_non_null_values(row_list, column)) == len(row_list) for column in numeric)
            if complete:
                return _base_result(
                    shape="numeric_relationship",
                    recommended_view="visual",
                    recommended_visual="scatter",
                    confidence=0.92,
                    reason="Two non-identifier numeric fields are returned for row-level observations.",
                    dimensions=[numeric[0]],
                    measures=[numeric[1]],
                    profiles=profiles,
                    flow_steps=flow_steps,
                )

    return _base_result(
        shape="tabular",
        recommended_view="table",
        recommended_visual=None,
        confidence=1.0,
        reason="The returned result is mixed, incomplete, too wide, or otherwise ambiguous; Table is the truthful default.",
        dimensions=[],
        measures=numeric,
        profiles=profiles,
        flow_steps=flow_steps,
    )
