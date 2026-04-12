#!/usr/bin/env python3
"""Schema-detail-backed identifier validation."""

from __future__ import annotations

import re
from typing import Any, Optional

from sql_cli.db_new import CoQueryDB, CoQueryDBError


IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TABLE_VERBS_RE = re.compile(r"\b(?:show|find|select|count)\s+(?:all\s+)?([A-Za-z_][A-Za-z0-9_]*)\b", re.IGNORECASE)
QUALIFIED_COLUMN_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\b")
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


def _extract_qualified_column_references(value: Any) -> dict[str, list[str]]:
    references: dict[str, list[str]] = {}
    for raw_table, raw_column in QUALIFIED_COLUMN_RE.findall(str(value or "")):
        table = _clean_identifier(raw_table)
        column = _clean_identifier(raw_column)
        if not table or not column:
            continue
        references.setdefault(table, [])
        existing = {_case_key(existing_column) for existing_column in references[table]}
        if _case_key(column) not in existing:
            references[table].append(column)
    return references


def _table_detail_map(table_details: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {_case_key(table["name"]): table for table in table_details}


def _sqlite_foreign_key_relationships(table_detail: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, str], dict[str, Any]] = {}
    for foreign_key in table_detail.get("foreign_keys", []):
        referenced_table = _clean_identifier(foreign_key.get("referenced_table"))
        column = _clean_identifier(foreign_key.get("column"))
        referenced_column = _clean_identifier(foreign_key.get("referenced_column"))
        if not referenced_table or not column or not referenced_column:
            continue

        key = (foreign_key.get("id"), _case_key(referenced_table))
        entry = grouped.setdefault(
            key,
            {
                "constraint_name": f"{table_detail['name']}_fk_{foreign_key.get('id', 0)}",
                "source_table": table_detail["name"],
                "target_table": referenced_table,
                "source_columns": [],
                "target_columns": [],
                "order": [],
            },
        )
        entry["order"].append(
            (
                int(foreign_key.get("seq", 0) or 0),
                column,
                referenced_column,
            )
        )

    relationships: list[dict[str, Any]] = []
    for entry in grouped.values():
        ordered_pairs = sorted(entry.pop("order"), key=lambda item: item[0])
        entry["source_columns"] = [pair[1] for pair in ordered_pairs]
        entry["target_columns"] = [pair[2] for pair in ordered_pairs]
        relationships.append(entry)
    return relationships


def _constraint_foreign_key_relationships(table_detail: dict[str, Any]) -> list[dict[str, Any]]:
    relationships: list[dict[str, Any]] = []
    for foreign_key in table_detail.get("foreign_keys", []):
        referenced_table = _clean_identifier(foreign_key.get("referenced_table"))
        source_columns = _unique_identifiers(foreign_key.get("columns", []))
        target_columns = _unique_identifiers(foreign_key.get("referenced_columns", []))
        if not referenced_table or not source_columns or not target_columns:
            continue
        if len(source_columns) != len(target_columns):
            continue
        relationships.append(
            {
                "constraint_name": foreign_key.get("name") or f"{table_detail['name']}_fk",
                "source_table": table_detail["name"],
                "target_table": referenced_table,
                "source_columns": source_columns,
                "target_columns": target_columns,
            }
        )
    return relationships


def _schema_relationships(table_details: list[dict[str, Any]]) -> list[dict[str, Any]]:
    relationships: list[dict[str, Any]] = []
    for table_detail in table_details:
        foreign_keys = table_detail.get("foreign_keys", [])
        if not foreign_keys:
            continue
        if isinstance(foreign_keys[0], dict) and "column" in foreign_keys[0]:
            relationships.extend(_sqlite_foreign_key_relationships(table_detail))
        else:
            relationships.extend(_constraint_foreign_key_relationships(table_detail))
    return relationships


def _find_join_candidates(
    table_details: list[dict[str, Any]],
    left_table: str,
    right_table: str,
) -> list[dict[str, Any]]:
    left_key = _case_key(left_table)
    right_key = _case_key(right_table)
    return [
        relationship
        for relationship in _schema_relationships(table_details)
        if {_case_key(relationship["source_table"]), _case_key(relationship["target_table"])} == {left_key, right_key}
    ]


def _render_join_condition(relationship: dict[str, Any]) -> str:
    predicates = [
        f"{relationship['source_table']}.{source_column} = {relationship['target_table']}.{target_column}"
        for source_column, target_column in zip(
            relationship.get("source_columns", []),
            relationship.get("target_columns", []),
        )
    ]
    return " AND ".join(predicates)


def generation_schema_requirements(skill_id: str | None, params: Optional[dict[str, Any]]) -> dict[str, Any]:
    normalized_params = params or {}
    normalized_skill = (skill_id or "select_simple").strip().lower()
    table = _clean_identifier(normalized_params.get("table")) or "users"
    explicit_on = str(normalized_params.get("on") or "").strip()
    auto_join_requested = False

    if "join" in normalized_skill:
        table1 = _clean_identifier(normalized_params.get("table1")) or table
        table2 = _clean_identifier(normalized_params.get("table2")) or "orders"
        tables = _unique_identifiers([table1, table2])
        default_column_table = table1
        auto_join_requested = explicit_on.lower() in {"", "auto"}
        join_pairs = [{"left_table": table1, "right_table": table2}] if len(tables) == 2 else []
    else:
        tables = [table]
        default_column_table = table
        join_pairs = []

    columns_by_table: dict[str, list[str]] = {}
    for key in ("cols", "group", "sort"):
        _merge_column_references(
            columns_by_table,
            _extract_column_references(normalized_params.get(key), default_column_table),
        )
    if "join" in normalized_skill and not auto_join_requested:
        _merge_column_references(columns_by_table, _extract_qualified_column_references(explicit_on))

    return {
        "tables": tables,
        "columns_by_table": columns_by_table,
        "join_pairs": join_pairs,
        "auto_join_requested": auto_join_requested,
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
    join_pairs: Optional[list[dict[str, str]]] = None,
) -> dict[str, Any]:
    requested_tables = _unique_identifiers(tables or [])
    requested_columns = columns_by_table or {}
    requested_join_pairs = [
        {
            "left_table": cleaned_left,
            "right_table": cleaned_right,
        }
        for pair in (join_pairs or [])
        for cleaned_left, cleaned_right in [
            (
                _clean_identifier(pair.get("left_table")),
                _clean_identifier(pair.get("right_table")),
            )
        ]
        if cleaned_left and cleaned_right
    ]
    for table in requested_columns:
        cleaned_table = _clean_identifier(table)
        if cleaned_table and _case_key(cleaned_table) not in {_case_key(existing) for existing in requested_tables}:
            requested_tables.append(cleaned_table)
    for pair in requested_join_pairs:
        for table in (pair["left_table"], pair["right_table"]):
            if _case_key(table) not in {_case_key(existing) for existing in requested_tables}:
                requested_tables.append(table)

    schema_detail, error = _load_schema_detail(db_target)
    if error:
        return {
            "source": "schema_detail",
            "status": "unavailable",
            "backend": None,
            "checked_tables": requested_tables,
            "checked_columns": requested_columns,
            "checked_join_pairs": requested_join_pairs,
            "available_tables": [],
            "errors": [],
            "validated_columns": [],
            "validated_joins": [],
            "warnings": [
                {
                    "code": error.code,
                    "message": error.message,
                }
            ],
        }

    assert schema_detail is not None
    table_details = schema_detail.get("tables", [])
    table_map = _table_detail_map(table_details)
    available_tables = [table["name"] for table in table_details]
    errors: list[dict[str, Any]] = []
    validated_columns: list[dict[str, Any]] = []
    validated_joins: list[dict[str, Any]] = []

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

    for pair in requested_join_pairs:
        left_detail = table_map.get(_case_key(pair["left_table"]))
        right_detail = table_map.get(_case_key(pair["right_table"]))
        if not left_detail or not right_detail:
            continue

        candidates = _find_join_candidates(table_details, left_detail["name"], right_detail["name"])
        if not candidates:
            errors.append(
                {
                    "code": "no_join_path",
                    "left_table": left_detail["name"],
                    "right_table": right_detail["name"],
                    "message": (
                        f"No direct schema_detail foreign-key join path found between "
                        f"{left_detail['name']} and {right_detail['name']}."
                    ),
                }
            )
            continue

        if len(candidates) > 1:
            errors.append(
                {
                    "code": "ambiguous_join_path",
                    "left_table": left_detail["name"],
                    "right_table": right_detail["name"],
                    "candidate_count": len(candidates),
                    "candidate_constraints": [candidate["constraint_name"] for candidate in candidates],
                    "message": (
                        f"Multiple direct schema_detail foreign-key join paths found between "
                        f"{left_detail['name']} and {right_detail['name']}."
                    ),
                }
            )
            continue

        relationship = candidates[0]
        validated_joins.append(
            {
                "left_table": left_detail["name"],
                "right_table": right_detail["name"],
                "condition": _render_join_condition(relationship),
                "relationship": relationship,
            }
        )

    return {
        "source": "schema_detail",
        "status": "invalid" if errors else "validated",
        "backend": schema_detail.get("backend"),
        "checked_tables": requested_tables,
        "checked_columns": requested_columns,
        "checked_join_pairs": requested_join_pairs,
        "validated_columns": validated_columns,
        "validated_joins": validated_joins,
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
