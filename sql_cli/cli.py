#!/usr/bin/env python3
"""CoQuery CLI handlers."""

from __future__ import annotations

from typing import Any, Optional

from sql_cli.db_new import CoQueryDB, CoQueryDBError
from sql_cli.dialect_rules import CoQueryKnowledgeError, lookup_knowledge
from sql_cli.jpa import CoQueryJPAError, scan_jpa_project
from sql_cli.llm_registry import CoQueryLLMError, LLMProviderClient, LLMProviderRegistry

WRITE_OPERATIONS = {"INSERT", "UPDATE", "DELETE"}


def _success(command: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "command": command, "data": data, "error": None}


def _error(
    command: str,
    code: str,
    message: str,
    data: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "command": command,
        "data": data or {},
        "error": {"code": code, "message": message},
    }


def _sql_operation(sql: Optional[str]) -> str:
    if not sql or not sql.strip():
        return ""
    return sql.strip().split(None, 1)[0].upper()


def _normalize_write_params(params: Optional[Any]) -> Optional[list[Any]]:
    if params is None:
        return None
    if isinstance(params, list):
        return params
    if isinstance(params, tuple):
        return list(params)
    raise TypeError("Write params must be a JSON array")


def _write_metadata(operation: str, sql: str) -> tuple[list[str], str]:
    sql_upper = sql.strip().upper()
    warnings: list[str] = []

    if operation == "INSERT":
        return warnings, "low"

    if operation in {"UPDATE", "DELETE"}:
        if "WHERE" not in sql_upper:
            warnings.append(f"{operation} without WHERE may affect all rows.")
            return warnings, "high"
        return warnings, "low"

    return warnings, "medium"


def _db_error(command: str, exc: CoQueryDBError) -> dict[str, Any]:
    return _error(command, exc.code, exc.message)


def _llm_error(command: str, exc: CoQueryLLMError) -> dict[str, Any]:
    return _error(command, exc.code, exc.message)


def _jpa_error(command: str, exc: CoQueryJPAError) -> dict[str, Any]:
    return _error(command, exc.code, exc.message)


def _knowledge_error(command: str, exc: CoQueryKnowledgeError) -> dict[str, Any]:
    return _error(command, exc.code, exc.message)


def _run_write_command(
    command: str,
    db: str,
    sql: Optional[str],
    params: Optional[Any],
    write: bool,
    expected_operation: Optional[str] = None,
) -> dict[str, Any]:
    operation = _sql_operation(sql) or expected_operation or command.upper()

    if not write:
        return _error(
            command,
            "write_flag_required",
            f"{operation} requires explicit --write confirmation.",
        )

    if not sql or not sql.strip():
        return _error(
            command,
            "invalid_write_sql",
            f"{operation} requires explicit SQL.",
        )

    if expected_operation and _sql_operation(sql) != expected_operation:
        return _error(
            command,
            "invalid_write_sql",
            f"{expected_operation} command requires {expected_operation} SQL.",
        )

    if _sql_operation(sql) not in WRITE_OPERATIONS:
        return _error(
            command,
            "unsupported_write_mode",
            f"{_sql_operation(sql)} is not supported by the baseline write contract.",
        )

    try:
        normalized_params = _normalize_write_params(params)
        warnings, safety_level = _write_metadata(_sql_operation(sql), sql)
        with CoQueryDB(db) as conn:
            affected_rows = conn.execute(sql, normalized_params)
        return _success(
            command,
            {
                "affected_rows": affected_rows,
                "warnings": warnings,
                "safety_level": safety_level,
            },
        )
    except CoQueryDBError as e:
        return _db_error(command, e)
    except NotImplementedError as e:
        return _error(command, "unsupported_write_mode", str(e))
    except RuntimeError as e:
        code = "database_connection_failed" if "Database connection failed" in str(e) else "execution_error"
        return _error(command, code, str(e))
    except TypeError as e:
        return _error(command, "unsupported_write_mode", str(e))
    except Exception as e:
        return _error(command, "execution_error", str(e))


def schema_handler(db: str, format: str = "json") -> dict[str, Any]:
    try:
        with CoQueryDB(db) as conn:
            tables = conn.get_schemas()
        return _success("schema", {"tables": tables})
    except CoQueryDBError as e:
        return _db_error("schema", e)
    except Exception as e:
        return _error("schema", "execution_error", str(e))


def query_handler(db: str, sql: str, format: str = "json", write: bool = False) -> dict[str, Any]:
    operation = _sql_operation(sql)

    if operation != "SELECT":
        return _run_write_command("query", db, sql, None, write)

    try:
        with CoQueryDB(db) as conn:
            result = conn.execute(sql)

        payload = {"rows": result} if isinstance(result, list) else {"affected_rows": result}
        return _success("query", payload)
    except CoQueryDBError as e:
        return _db_error("query", e)
    except Exception as e:
        return _error("query", "execution_error", str(e))


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


def provider_add_handler(
    provider_name: Optional[str],
    provider_kind: Optional[str],
    model_name: Optional[str],
    base_url: Optional[str] = None,
    api_key_env: Optional[str] = None,
) -> dict[str, Any]:
    try:
        registry = LLMProviderRegistry()
        provider = registry.upsert_profile(
            name=provider_name or "",
            kind=provider_kind or "",
            model_name=model_name or "",
            base_url=base_url or "",
            api_key_env=api_key_env,
        )
        return _success(
            "provider_add",
            {
                "provider": provider,
                "registry_path": str(registry.path),
            },
        )
    except CoQueryLLMError as e:
        return _llm_error("provider_add", e)
    except Exception as e:
        return _error("provider_add", "execution_error", str(e))


def provider_list_handler() -> dict[str, Any]:
    try:
        registry = LLMProviderRegistry()
        return _success(
            "provider_list",
            {
                "providers": registry.list_profiles(),
                "registry_path": str(registry.path),
            },
        )
    except CoQueryLLMError as e:
        return _llm_error("provider_list", e)
    except Exception as e:
        return _error("provider_list", "execution_error", str(e))


def provider_remove_handler(provider_name: Optional[str]) -> dict[str, Any]:
    try:
        registry = LLMProviderRegistry()
        removed = registry.remove_profile(provider_name or "")
        return _success(
            "provider_remove",
            {
                "provider": removed,
                "registry_path": str(registry.path),
            },
        )
    except CoQueryLLMError as e:
        return _llm_error("provider_remove", e)
    except Exception as e:
        return _error("provider_remove", "execution_error", str(e))


def provider_test_handler(provider_name: Optional[str]) -> dict[str, Any]:
    try:
        registry = LLMProviderRegistry()
        profile = registry.get_profile(provider_name or "")
        result = LLMProviderClient(profile).test_connection()
        result["registry_path"] = str(registry.path)
        return _success("provider_test", result)
    except CoQueryLLMError as e:
        return _llm_error("provider_test", e)
    except Exception as e:
        return _error("provider_test", "execution_error", str(e))


def jpa_schema_handler(project_path: Optional[str], format: str = "json") -> dict[str, Any]:
    try:
        return _success("jpa_schema", scan_jpa_project(project_path))
    except CoQueryJPAError as e:
        return _jpa_error("jpa_schema", e)
    except Exception as e:
        return _error("jpa_schema", "execution_error", str(e))


def db_knowledge_handler(dialect: Optional[str] = None, topic: Optional[str] = None) -> dict[str, Any]:
    try:
        return _success("db_knowledge", lookup_knowledge(dialect=dialect, topic=topic))
    except CoQueryKnowledgeError as e:
        return _knowledge_error("db_knowledge", e)
    except Exception as e:
        return _error("db_knowledge", "execution_error", str(e))


def insert_handler(
    db: str,
    sql: Optional[str] = None,
    params: Optional[list[Any]] = None,
    write: bool = False,
) -> dict[str, Any]:
    return _run_write_command("insert", db, sql, params, write, expected_operation="INSERT")


def update_handler(
    db: str,
    sql: Optional[str] = None,
    params: Optional[list[Any]] = None,
    write: bool = False,
) -> dict[str, Any]:
    return _run_write_command("update", db, sql, params, write, expected_operation="UPDATE")


def delete_handler(
    db: str,
    sql: Optional[str] = None,
    params: Optional[list[Any]] = None,
    write: bool = False,
) -> dict[str, Any]:
    return _run_write_command("delete", db, sql, params, write, expected_operation="DELETE")


def natural_handler(
    db: str,
    sql: Optional[str] = None,
    format: str = "json",
    provider_name: Optional[str] = None,
) -> dict[str, Any]:
    try:
        from sql_cli.nl_core import NaturalLanguageEngine

        result = NaturalLanguageEngine(provider_name=provider_name).process(sql or "show users")
        return {
            "ok": result.get("ok"),
            "command": "natural",
            "intent": result.get("intent"),
            "sql": result.get("sql"),
            "complexity": result.get("complexity"),
            "confidence": result.get("confidence"),
            "mode": result.get("mode"),
            "provider_name": result.get("provider_name"),
            "provider_kind": result.get("provider_kind"),
            "model_name": result.get("model_name"),
            "error": None,
        }
    except CoQueryLLMError as e:
        return _llm_error("natural", e)
    except Exception as e:
        return {"ok": False, "command": "natural", "error": str(e)}
