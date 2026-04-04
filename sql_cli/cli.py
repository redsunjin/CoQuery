#!/usr/bin/env python3
"""CoQuery CLI handlers."""

from __future__ import annotations

from typing import Any, Optional

from sql_cli.db_new import CoQueryDB


def _default_write_sql(command: str) -> str:
    defaults = {
        "insert": "INSERT INTO users (name, age) VALUES ('test_user', 30)",
        "update": "UPDATE users SET name='new_user' WHERE id = 1",
        "delete": "DELETE FROM users WHERE id = 1",
    }
    return defaults[command]


def schema_handler(db: str, format: str = "json") -> dict[str, Any]:
    try:
        with CoQueryDB(db) as conn:
            tables = conn.get_schemas()
        return {"ok": True, "command": "schema", "data": {"tables": tables}, "error": None}
    except Exception as e:
        return {"ok": False, "command": "schema", "data": {}, "error": str(e)}


def query_handler(db: str, sql: str, format: str = "json", write: bool = False) -> dict[str, Any]:
    try:
        sql_upper = sql.strip().upper()
        if not write and not sql_upper.startswith("SELECT"):
            return {"ok": False, "command": "query", "data": {}, "error": "Only SELECT"}

        with CoQueryDB(db) as conn:
            result = conn.execute(sql)

        payload = {"rows": result} if isinstance(result, list) else {"affected_rows": result}
        return {"ok": True, "command": "query", "data": payload, "error": None}
    except Exception as e:
        return {"ok": False, "command": "query", "data": {}, "error": str(e)}


def generate_handler(
    db: str,
    skill: Optional[str] = None,
    format: str = "json",
    params: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    try:
        from sql_cli.core import SQLGenerator

        gen = SQLGenerator()
        result = gen.generate(skill or "select_simple", params or {})
        return {
            "ok": "error" not in result,
            "command": "generate",
            "sql": result.get("sql", ""),
            "warnings": result.get("warnings", []),
            "error": result.get("error"),
        }
    except Exception as e:
        return {"ok": False, "command": "generate", "error": str(e)}


def insert_handler(db: str, sql: Optional[str] = None, params: Optional[list[Any]] = None) -> dict[str, Any]:
    try:
        with CoQueryDB(db) as conn:
            affected_rows = conn.execute(sql or _default_write_sql("insert"), params)
        return {"ok": True, "command": "insert", "affected_rows": affected_rows, "error": None}
    except Exception as e:
        return {"ok": False, "command": "insert", "affected_rows": 0, "error": str(e)}


def update_handler(db: str, sql: Optional[str] = None, params: Optional[list[Any]] = None) -> dict[str, Any]:
    try:
        with CoQueryDB(db) as conn:
            affected_rows = conn.execute(sql or _default_write_sql("update"), params)
        return {"ok": True, "command": "update", "affected_rows": affected_rows, "error": None}
    except Exception as e:
        return {"ok": False, "command": "update", "affected_rows": 0, "error": str(e)}


def delete_handler(db: str, sql: Optional[str] = None, params: Optional[list[Any]] = None) -> dict[str, Any]:
    try:
        with CoQueryDB(db) as conn:
            affected_rows = conn.execute(sql or _default_write_sql("delete"), params)
        return {"ok": True, "command": "delete", "affected_rows": affected_rows, "error": None}
    except Exception as e:
        return {"ok": False, "command": "delete", "affected_rows": 0, "error": str(e)}


def natural_handler(db: str, sql: Optional[str] = None, format: str = "json") -> dict[str, Any]:
    try:
        from sql_cli.nl_core import NaturalLanguageEngine

        result = NaturalLanguageEngine().process(sql or "show users")
        return {
            "ok": result.get("ok"),
            "command": "natural",
            "intent": result.get("intent"),
            "sql": result.get("sql"),
            "complexity": result.get("complexity"),
            "error": None,
        }
    except Exception as e:
        return {"ok": False, "command": "natural", "error": str(e)}
