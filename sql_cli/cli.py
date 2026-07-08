#!/usr/bin/env python3
"""CoQuery CLI handlers."""

from __future__ import annotations

from typing import Any, Optional

from sql_cli.db_new import CoQueryDB, CoQueryDBError
from sql_cli.dialect_rules import CoQueryKnowledgeError, lookup_knowledge
from sql_cli.help_catalog import CoQueryHelpError, explain_command, explain_term, get_help_catalog
from sql_cli.jpa import CoQueryJPAError, scan_jpa_project
from sql_cli.knowledge_planner import build_generation_context, build_write_context
from sql_cli.llm_registry import (
    CoQueryLLMError,
    LLMProviderClient,
    LLMProviderRegistry,
    get_provider_preset,
    list_provider_presets,
)
from sql_cli.mode_policy import build_mode_context, provider_policy_block_result
from sql_cli.practice import (
    practice_attempts_handler,
    practice_feedback_handler,
    practice_grade_handler,
    practice_list_handler,
    practice_query_handler,
    practice_schema_handler,
)
from sql_cli.production_assist import (
    production_approve_handler,
    production_execute_handler,
    production_profile_add_handler,
    production_profile_list_handler,
    production_review_handler,
)
from sql_cli.schema_guard import (
    generation_schema_requirements,
    schema_validation_failed,
    schema_validation_message,
    validate_schema_identifiers,
)

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


def _write_metadata(operation: str, sql: str, dry_run: bool = False) -> tuple[list[str], str]:
    sql_upper = sql.strip().upper()
    warnings: list[str] = []

    if dry_run:
        warnings.append("Dry-run mode enabled; changes were rolled back.")

    if operation == "INSERT":
        return warnings, "low"

    if operation in {"UPDATE", "DELETE"}:
        if "WHERE" not in sql_upper:
            warnings.append(f"{operation} without WHERE may affect all rows.")
            return warnings, "high"
        return warnings, "low"

    return warnings, "medium"


def _is_full_table_write(operation: str, sql: str) -> bool:
    sql_upper = sql.strip().upper()
    return operation in {"UPDATE", "DELETE"} and "WHERE" not in sql_upper


def _db_error(command: str, exc: CoQueryDBError) -> dict[str, Any]:
    return _error(command, exc.code, exc.message, exc.data)


def _llm_error_guidance(exc: CoQueryLLMError) -> dict[str, Any]:
    code = exc.code
    message = exc.message

    if code == "missing_api_key":
        env_name = message
        marker = "Environment variable "
        if marker in message:
            env_name = message.split(marker, 1)[1].split(" ", 1)[0].strip(".")
        return {
            "readable_message": "API key is not configured for this provider.",
            "next_step": (
                f"Set {env_name} in your local environment, then run the provider test again. "
                "CoQuery stores the environment variable name, not the secret value."
            ),
            "severity": "action_required",
        }

    if code == "provider_unreachable":
        return {
            "readable_message": "The provider server could not be reached.",
            "next_step": "Check that the local model server or API endpoint is running and that the base URL is correct.",
            "severity": "blocked",
        }

    if code == "provider_timeout":
        return {
            "readable_message": "The provider did not respond in time.",
            "next_step": "Try the test again, or choose a faster model/provider if this repeats.",
            "severity": "retry",
        }

    if code == "model_not_found":
        return {
            "readable_message": "The configured model was not found by the provider.",
            "next_step": "Check the model name in the provider profile, then save and test it again.",
            "severity": "action_required",
        }

    if code == "provider_not_found":
        return {
            "readable_message": "No saved provider matches that name.",
            "next_step": "Save a provider from a preset or choose one from the saved provider list.",
            "severity": "action_required",
        }

    if code == "missing_provider_name":
        return {
            "readable_message": "Choose a provider before testing or removing it.",
            "next_step": "Open the saved provider list and use one of its action buttons.",
            "severity": "action_required",
        }

    if code == "provider_request_failed":
        return {
            "readable_message": "The provider rejected the test request.",
            "next_step": "Check the provider endpoint, model name, and account/API key status.",
            "severity": "action_required",
        }

    return {
        "readable_message": message,
        "next_step": "Review the provider profile, then test it again.",
        "severity": "unknown",
    }


def _llm_error(command: str, exc: CoQueryLLMError) -> dict[str, Any]:
    return _error(command, exc.code, exc.message, _llm_error_guidance(exc))


def _jpa_error(command: str, exc: CoQueryJPAError) -> dict[str, Any]:
    return _error(command, exc.code, exc.message)


def _knowledge_error(command: str, exc: CoQueryKnowledgeError) -> dict[str, Any]:
    return _error(command, exc.code, exc.message)


def _help_error(command: str, exc: CoQueryHelpError) -> dict[str, Any]:
    return _error(command, exc.code, exc.message, exc.data)


def _run_write_command(
    command: str,
    db: str,
    sql: Optional[str],
    params: Optional[Any],
    write: bool,
    dry_run: bool = False,
    max_affected_rows: Optional[int] = None,
    allow_full_table_write: bool = False,
    expected_operation: Optional[str] = None,
) -> dict[str, Any]:
    operation = _sql_operation(sql) or expected_operation or command.upper()
    knowledge_context = build_write_context(db, operation)

    if not write:
        return _error(
            command,
            "write_flag_required",
            f"{operation} requires explicit --write confirmation.",
            {"knowledge_context": knowledge_context},
        )

    if not sql or not sql.strip():
        return _error(
            command,
            "invalid_write_sql",
            f"{operation} requires explicit SQL.",
            {"knowledge_context": knowledge_context},
        )

    if expected_operation and _sql_operation(sql) != expected_operation:
        return _error(
            command,
            "invalid_write_sql",
            f"{expected_operation} command requires {expected_operation} SQL.",
            {"knowledge_context": knowledge_context},
        )

    if _sql_operation(sql) not in WRITE_OPERATIONS:
        return _error(
            command,
            "unsupported_write_mode",
            f"{_sql_operation(sql)} is not supported by the baseline write contract.",
            {"knowledge_context": knowledge_context},
        )

    if max_affected_rows is not None and max_affected_rows < 0:
        return _error(
            command,
            "invalid_max_affected_rows",
            "max_affected_rows must be zero or greater.",
            {"knowledge_context": knowledge_context},
        )

    warnings, safety_level = _write_metadata(_sql_operation(sql), sql, dry_run=dry_run)

    if _is_full_table_write(_sql_operation(sql), sql) and not allow_full_table_write:
        full_table_warnings = warnings + [
            "Use --allow-full-table-write to run this statement intentionally.",
        ]
        return _error(
            command,
            "full_table_write_requires_flag",
            f"{_sql_operation(sql)} without WHERE requires --allow-full-table-write.",
            {
                "dry_run": dry_run,
                "committed": False,
                "warnings": full_table_warnings,
                "safety_level": safety_level,
                "knowledge_context": knowledge_context,
            },
        )

    try:
        normalized_params = _normalize_write_params(params)
        with CoQueryDB(db) as conn:
            affected_rows = conn.execute(
                sql,
                normalized_params,
                dry_run=dry_run,
                max_affected_rows=max_affected_rows,
            )
        return _success(
            command,
            {
                "affected_rows": affected_rows,
                "max_affected_rows": max_affected_rows,
                "dry_run": dry_run,
                "committed": not dry_run,
                "warnings": warnings,
                "safety_level": safety_level,
                "knowledge_context": knowledge_context,
            },
        )
    except CoQueryDBError as e:
        if e.code == "affected_rows_exceeded":
            limit_warnings = warnings + ["Affected-row limit exceeded; changes were rolled back."]
            return _error(
                command,
                e.code,
                e.message,
                {
                    "affected_rows": e.data.get("affected_rows"),
                    "max_affected_rows": e.data.get("max_affected_rows"),
                    "dry_run": dry_run,
                    "committed": False,
                    "warnings": limit_warnings,
                    "safety_level": safety_level,
                    "knowledge_context": knowledge_context,
                },
            )
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


def schema_detail_handler(db: str, table: Optional[str] = None, format: str = "json") -> dict[str, Any]:
    try:
        with CoQueryDB(db) as conn:
            return _success("schema_detail", conn.get_schema_detail(table))
    except CoQueryDBError as e:
        return _db_error("schema_detail", e)
    except Exception as e:
        return _error("schema_detail", "execution_error", str(e))


def doctor_handler(db: str, format: str = "json") -> dict[str, Any]:
    try:
        conn = CoQueryDB(db, connect_now=False)
        report = conn.doctor()
        if report.get("ready"):
            return _success("doctor", report)

        connection = report.get("connection", {})
        return _error(
            "doctor",
            connection.get("code", "database_not_ready"),
            connection.get("message", "Database target is not ready."),
            report,
        )
    except CoQueryDBError as e:
        return _error("doctor", e.code, e.message, {"requested_target": db})
    except Exception as e:
        return _error("doctor", "execution_error", str(e), {"requested_target": db})


def query_handler(
    db: str,
    sql: str,
    format: str = "json",
    write: bool = False,
    dry_run: bool = False,
    max_affected_rows: Optional[int] = None,
    allow_full_table_write: bool = False,
) -> dict[str, Any]:
    operation = _sql_operation(sql)

    if operation != "SELECT":
        return _run_write_command(
            "query",
            db,
            sql,
            None,
            write,
            dry_run=dry_run,
            max_affected_rows=max_affected_rows,
            allow_full_table_write=allow_full_table_write,
        )

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
    knowledge_context = build_generation_context(db, skill or "select_simple")
    try:
        from sql_cli.core import SQLGenerator

        requirements = generation_schema_requirements(skill or "select_simple", params)
        schema_validation = validate_schema_identifiers(
            db,
            requirements["tables"],
            requirements["columns_by_table"],
            requirements.get("join_pairs"),
        )
        validation_warnings = [
            f"schema_validation_unavailable:{warning['code']}"
            for warning in schema_validation.get("warnings", [])
        ]
        if schema_validation_failed(schema_validation):
            return {
                "ok": False,
                "command": "generate",
                "sql": "",
                "warnings": validation_warnings,
                "knowledge_context": knowledge_context,
                "schema_validation": schema_validation,
                "error": {
                    "code": "schema_validation_failed",
                    "message": schema_validation_message(schema_validation),
                },
            }

        prepared_params = dict(params or {})
        if requirements.get("auto_join_requested"):
            if schema_validation.get("status") == "unavailable":
                return {
                    "ok": False,
                    "command": "generate",
                    "sql": "",
                    "warnings": validation_warnings,
                    "knowledge_context": knowledge_context,
                    "schema_validation": schema_validation,
                    "error": {
                        "code": "schema_detail_unavailable_for_join",
                        "message": "Automatic join generation requires schema_detail access for both tables.",
                    },
                }

            validated_joins = schema_validation.get("validated_joins", [])
            if not validated_joins:
                return {
                    "ok": False,
                    "command": "generate",
                    "sql": "",
                    "warnings": validation_warnings,
                    "knowledge_context": knowledge_context,
                    "schema_validation": schema_validation,
                    "error": {
                        "code": "schema_validation_failed",
                        "message": "Automatic join generation requires a validated direct join path.",
                    },
                }
            prepared_params["on"] = validated_joins[0]["condition"]

        gen = SQLGenerator()
        result = gen.generate(skill or "select_simple", prepared_params)
        warnings = validation_warnings + result.get("warnings", [])
        if "error" in result:
            return {
                "ok": False,
                "command": "generate",
                "sql": result.get("sql", ""),
                "warnings": warnings,
                "knowledge_context": knowledge_context,
                "schema_validation": {
                    "source": "schema_detail",
                    "status": "not_checked",
                    "reason": "generation_error",
                    "errors": [],
                    "warnings": [],
                },
                "error": result.get("error"),
            }

        return {
            "ok": "error" not in result,
            "command": "generate",
            "sql": result.get("sql", ""),
            "warnings": warnings,
            "knowledge_context": knowledge_context,
            "schema_validation": schema_validation,
            "error": result.get("error"),
        }
    except Exception as e:
        return {"ok": False, "command": "generate", "knowledge_context": knowledge_context, "error": str(e)}


def provider_add_handler(
    provider_name: Optional[str],
    provider_kind: Optional[str],
    model_name: Optional[str],
    base_url: Optional[str] = None,
    api_key_env: Optional[str] = None,
    chat_completions_url: Optional[str] = None,
    models_url: Optional[str] = None,
) -> dict[str, Any]:
    try:
        registry = LLMProviderRegistry()
        provider = registry.upsert_profile(
            name=provider_name or "",
            kind=provider_kind or "",
            model_name=model_name or "",
            base_url=base_url or "",
            api_key_env=api_key_env,
            chat_completions_url=chat_completions_url,
            models_url=models_url,
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


def provider_list_presets_handler() -> dict[str, Any]:
    try:
        return _success("provider_list_presets", {"presets": list_provider_presets()})
    except CoQueryLLMError as e:
        return _llm_error("provider_list_presets", e)
    except Exception as e:
        return _error("provider_list_presets", "execution_error", str(e))


def provider_add_preset_handler(
    preset: Optional[str],
    provider_name: Optional[str],
    model_name: Optional[str],
    api_key_env: Optional[str] = None,
    base_url: Optional[str] = None,
    chat_completions_url: Optional[str] = None,
    models_url: Optional[str] = None,
) -> dict[str, Any]:
    try:
        preset_data = get_provider_preset(preset)
        resolved_model = model_name or preset_data.get("default_model") or ""
        registry = LLMProviderRegistry()
        provider = registry.upsert_profile(
            name=provider_name or preset_data["name"],
            kind=str(preset_data["kind"]),
            model_name=str(resolved_model),
            base_url=base_url or str(preset_data.get("base_url") or ""),
            api_key_env=api_key_env or preset_data.get("api_key_env"),
            preset=preset_data["name"],
            cost_profile=preset_data.get("cost_profile"),
            chat_completions_url=chat_completions_url or preset_data.get("chat_completions_url"),
            models_url=models_url or preset_data.get("models_url"),
        )
        return _success(
            "provider_add_preset",
            {
                "preset": preset_data,
                "provider": provider,
                "registry_path": str(registry.path),
            },
        )
    except CoQueryLLMError as e:
        return _llm_error("provider_add_preset", e)
    except Exception as e:
        return _error("provider_add_preset", "execution_error", str(e))


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


def help_catalog_handler(lang: Optional[str] = None) -> dict[str, Any]:
    try:
        return _success("help_catalog", get_help_catalog(lang))
    except Exception as e:
        return _error("help_catalog", "execution_error", str(e))


def command_explain_handler(topic: Optional[str] = None, lang: Optional[str] = None) -> dict[str, Any]:
    try:
        return _success("command_explain", explain_command(topic, lang))
    except CoQueryHelpError as e:
        return _help_error("command_explain", e)
    except Exception as e:
        return _error("command_explain", "execution_error", str(e))


def term_explain_handler(topic: Optional[str] = None, lang: Optional[str] = None) -> dict[str, Any]:
    try:
        return _success("term_explain", explain_term(topic, lang))
    except CoQueryHelpError as e:
        return _help_error("term_explain", e)
    except Exception as e:
        return _error("term_explain", "execution_error", str(e))


def insert_handler(
    db: str,
    sql: Optional[str] = None,
    params: Optional[list[Any]] = None,
    write: bool = False,
    dry_run: bool = False,
    max_affected_rows: Optional[int] = None,
    allow_full_table_write: bool = False,
) -> dict[str, Any]:
    return _run_write_command(
        "insert",
        db,
        sql,
        params,
        write,
        dry_run=dry_run,
        max_affected_rows=max_affected_rows,
        allow_full_table_write=allow_full_table_write,
        expected_operation="INSERT",
    )


def update_handler(
    db: str,
    sql: Optional[str] = None,
    params: Optional[list[Any]] = None,
    write: bool = False,
    dry_run: bool = False,
    max_affected_rows: Optional[int] = None,
    allow_full_table_write: bool = False,
) -> dict[str, Any]:
    return _run_write_command(
        "update",
        db,
        sql,
        params,
        write,
        dry_run=dry_run,
        max_affected_rows=max_affected_rows,
        allow_full_table_write=allow_full_table_write,
        expected_operation="UPDATE",
    )


def delete_handler(
    db: str,
    sql: Optional[str] = None,
    params: Optional[list[Any]] = None,
    write: bool = False,
    dry_run: bool = False,
    max_affected_rows: Optional[int] = None,
    allow_full_table_write: bool = False,
) -> dict[str, Any]:
    return _run_write_command(
        "delete",
        db,
        sql,
        params,
        write,
        dry_run=dry_run,
        max_affected_rows=max_affected_rows,
        allow_full_table_write=allow_full_table_write,
        expected_operation="DELETE",
    )


def natural_handler(
    db: str,
    sql: Optional[str] = None,
    format: str = "json",
    provider_name: Optional[str] = None,
    mode: Optional[str] = None,
    allow_external_provider: bool = False,
    provider_policy: Optional[str] = None,
) -> dict[str, Any]:
    try:
        from sql_cli.nl_core import NaturalLanguageEngine

        mode_context = build_mode_context(
            mode=mode,
            allow_external_provider=allow_external_provider,
            provider_policy=provider_policy,
        )
        policy_result = provider_policy_block_result("natural", provider_name, mode_context)
        if policy_result:
            return policy_result

        result = NaturalLanguageEngine(provider_name=provider_name, db_target=db).process(sql or "show users")
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
            "requested_provider_name": result.get("requested_provider_name"),
            "provider_skipped": result.get("provider_skipped"),
            "knowledge_context": result.get("knowledge_context"),
            "schema_validation": result.get("schema_validation"),
            "table_inference": result.get("table_inference"),
            "mode_context": mode_context,
            "error": result.get("error"),
        }
    except CoQueryLLMError as e:
        return _llm_error("natural", e)
    except Exception as e:
        return {"ok": False, "command": "natural", "error": str(e)}
