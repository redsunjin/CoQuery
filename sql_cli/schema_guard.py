#!/usr/bin/env python3
"""Schema-detail-backed identifier validation."""

from __future__ import annotations

import re
from typing import Any, Optional

from sql_cli.db_new import CoQueryDB, CoQueryDBError


IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TABLE_VERBS_RE = re.compile(r"\b(?:show|find|select|count)\s+(?:all\s+)?([A-Za-z_][A-Za-z0-9_]*)\b", re.IGNORECASE)
NATURAL_TABLE_SKIP_WORDS = {"all", "me", "the", "rows", "records", "data", "table", "tables"}


def _case_key(value: str) -> str:
    return value.casefold()


def _clean_identifier(value: Any) -> Optional[str]:
    if value is None:
        return None

    token = str(value).strip()
    if not token or token == "*":
        return None

    token = token.strip('"`[]')
    if "." in token:
        token = token.rsplit(".", 1)[-1].strip('"`[]')

    if not IDENTIFIER_RE.match(token):
        return None
    return token


def _unique_identifiers(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    identifiers: list[str] = []
    for value in values:
        identifier = _clean_identifier(value)
        if not identifier:
            continue
        key = _case_key(identifier)
        if key in seen:
            continue
        seen.add(key)
        identifiers.append(identifier)
    return identifiers


def _extract_column_references(value: Any, default_table: str) -> dict[str, list[str]]:
    if value is None or value == "*":
        return {}

    raw_parts = value if isinstance(value, list) else str(value).split(",")
    references: dict[str, list[str]] = {}

    for raw_part in raw_parts:
        part = str(raw_part).strip()
        if not part or part == "*":
            continue

        # Keep this intentionally narrow. Complex expressions stay unvalidated
        # until the generator has a real SQL parser.
        part = re.split(r"\s+", part, maxsplit=1)[0]
        if part == "*":
            continue

        table = default_table
        column_token = part
        if "." in part:
            table_token, column_token = part.rsplit(".", 1)
            cleaned_table = _clean_identifier(table_token)
            if cleaned_table:
                table = cleaned_table

        column = _clean_identifier(column_token)
        if not column:
            continue

        references.setdefault(table, [])
        if _case_key(column) not in {_case_key(existing) for existing in references[table]}:
            references[table].append(column)

    return references


def _merge_column_references(target: dict[str, list[str]], source: dict[str, list[str]]) -> None:
    for table, columns in source.items():
        target.setdefault(table, [])
        existing = {_case_key(column) for column in target[table]}
        for column in columns:
            key = _case_key(column)
            if key not in existing:
                existing.add(key)
                target[table].append(column)


def generation_schema_requirements(skill_id: str | None, params: Optional[dict[str, Any]]) -> dict[str, Any]:
    normalized_params = params or {}
    normalized_skill = (skill_id or "select_simple").strip().lower()
    table = _clean_identifier(normalized_params.get("table")) or "users"

    if "join" in normalized_skill:
        table1 = _clean_identifier(normalized_params.get("table1")) or table
        table2 = _clean_identifier(normalized_params.get("table2")) or "orders"
        tables = _unique_identifiers([table1, table2])
        default_column_table = table1
    else:
        tables = [table]
        default_column_table = table

    columns_by_table: dict[str, list[str]] = {}
    for key in ("cols", "group", "sort"):
        _merge_column_references(
            columns_by_table,
            _extract_column_references(normalized_params.get(key), default_column_table),
        )

    return {
        "tables": tables,
        "columns_by_table": columns_by_table,
    }


def _load_schema_detail(db_target: str | None) -> tuple[Optional[dict[str, Any]], Optional[CoQueryDBError]]:
    try:
        with CoQueryDB(db_target or "example.db") as conn:
            return conn.get_schema_detail(), None
    except CoQueryDBError as exc:
        return None, exc


def validate_schema_identifiers(
    db_target: str | None,
    tables: Optional[list[str]] = None,
    columns_by_table: Optional[dict[str, list[str]]] = None,
) -> dict[str, Any]:
    requested_tables = _unique_identifiers(tables or [])
    requested_columns = columns_by_table or {}
    for table in requested_columns:
        cleaned_table = _clean_identifier(table)
        if cleaned_table and _case_key(cleaned_table) not in {_case_key(existing) for existing in requested_tables}:
            requested_tables.append(cleaned_table)

    schema_detail, error = _load_schema_detail(db_target)
    if error:
        return {
            "source": "schema_detail",
            "status": "unavailable",
            "backend": None,
            "checked_tables": requested_tables,
            "checked_columns": requested_columns,
            "available_tables": [],
            "errors": [],
            "warnings": [
                {
                    "code": error.code,
                    "message": error.message,
                }
            ],
        }

    assert schema_detail is not None
    table_details = schema_detail.get("tables", [])
    table_map = {_case_key(table["name"]): table for table in table_details}
    available_tables = [table["name"] for table in table_details]
    errors: list[dict[str, Any]] = []
    validated_columns: list[dict[str, Any]] = []

    for table in requested_tables:
        table_key = _case_key(table)
        table_detail = table_map.get(table_key)
        if not table_detail:
            errors.append(
                {
                    "code": "unknown_table",
                    "table": table,
                    "message": f"Table not found in schema_detail: {table}.",
                }
            )
            continue

        available_columns = {
            _case_key(column["name"]): column["name"]
            for column in table_detail.get("columns", [])
        }
        checked_columns = requested_columns.get(table, [])
        for column in checked_columns:
            if _case_key(column) not in available_columns:
                errors.append(
                    {
                        "code": "unknown_column",
                        "table": table_detail["name"],
                        "column": column,
                        "message": f"Column not found in schema_detail: {table_detail['name']}.{column}.",
                    }
                )
                continue
            validated_columns.append({"table": table_detail["name"], "column": available_columns[_case_key(column)]})

    return {
        "source": "schema_detail",
        "status": "invalid" if errors else "validated",
        "backend": schema_detail.get("backend"),
        "checked_tables": requested_tables,
        "checked_columns": requested_columns,
        "validated_columns": validated_columns,
        "available_tables": available_tables,
        "errors": errors,
        "warnings": [],
    }


def schema_validation_failed(validation: dict[str, Any]) -> bool:
    return validation.get("status") == "invalid"


def schema_validation_message(validation: dict[str, Any]) -> str:
    errors = validation.get("errors") or []
    if not errors:
        return "Schema validation failed."
    return " ".join(error.get("message", "Schema validation failed.") for error in errors)


def infer_table_from_natural_text(db_target: str | None, text: str, default_table: str = "users") -> dict[str, Any]:
    schema_detail, error = _load_schema_detail(db_target)
    if error:
        return {
            "source": "schema_detail",
            "status": "unavailable",
            "table": default_table,
            "matched": False,
            "warnings": [{"code": error.code, "message": error.message}],
        }

    assert schema_detail is not None
    table_names = [table["name"] for table in schema_detail.get("tables", [])]
    lowered_text = text.casefold()
    for table_name in table_names:
        if re.search(rf"\b{re.escape(table_name.casefold())}\b", lowered_text):
            return {
                "source": "schema_detail",
                "status": "matched",
                "table": table_name,
                "matched": True,
                "available_tables": table_names,
                "warnings": [],
            }

    candidate = None
    match = TABLE_VERBS_RE.search(text)
    if match:
        raw_candidate = match.group(1)
        if raw_candidate.casefold() not in NATURAL_TABLE_SKIP_WORDS:
            candidate = raw_candidate

    return {
        "source": "schema_detail",
        "status": "candidate" if candidate else "default",
        "table": candidate or default_table,
        "matched": False,
        "available_tables": table_names,
        "warnings": [],
    }
