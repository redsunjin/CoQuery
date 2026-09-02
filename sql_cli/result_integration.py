#!/usr/bin/env python3
"""Additive integration helpers for CoQuery result intelligence.

The raw query result remains canonical evidence. This module only adds derived
metadata and deliberately does not alter returned columns, rows, or row_count.
"""

from __future__ import annotations

from typing import Any

from sql_cli.result_intelligence import classify_result


def enrich_practice_query_result(result: dict[str, Any], args: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a practice_query result with deterministic BI metadata attached.

    Non-practice or failed results are returned unchanged. For a successful
    practice_query, the top-level result and data mapping are copied before the
    additive `result_intelligence` field is attached so callers can keep the raw
    evidence object if needed.
    """

    if not result.get("ok") or result.get("command") != "practice_query":
        return result

    source_data = result.get("data")
    if not isinstance(source_data, dict):
        return result

    enriched = dict(result)
    data = dict(source_data)
    enriched["data"] = data

    safe_args = dict(args or {})
    columns = data.get("columns") or []
    rows = data.get("rows") or []
    sql = data.get("sql") or safe_args.get("sql")
    data["result_intelligence"] = classify_result(columns, rows, sql=sql)
    return enriched
