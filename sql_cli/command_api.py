#!/usr/bin/env python3
"""App-facing command adapter for CoQuery handlers."""

from __future__ import annotations

import json
from typing import Any, Callable

from sql_cli.cli import (
    command_explain_handler,
    db_knowledge_handler,
    delete_handler,
    doctor_handler,
    generate_handler,
    help_catalog_handler,
    insert_handler,
    jpa_schema_handler,
    natural_handler,
    practice_attempts_handler,
    practice_feedback_handler,
    practice_grade_handler,
    practice_list_handler,
    practice_query_handler,
    practice_schema_handler,
    production_approve_handler,
    production_execute_handler,
    production_profile_add_handler,
    production_profile_list_handler,
    production_review_handler,
    provider_add_handler,
    provider_add_preset_handler,
    provider_list_handler,
    provider_list_presets_handler,
    provider_remove_handler,
    provider_test_handler,
    query_handler,
    schema_detail_handler,
    schema_handler,
    term_explain_handler,
    update_handler,
)
from sql_cli.mode_policy import build_mode_context, provider_policy_block_result


CommandArgs = dict[str, Any]
CommandResult = dict[str, Any]

DEFAULT_DB = "example.db"
DEFAULT_FORMAT = "json"


BLOCK_TYPES = {
    "schema": "schema",
    "schema_detail": "schema_detail",
    "doctor": "diagnostic",
    "query": "query_result",
    "generate": "sql_generation",
    "insert": "write_result",
    "update": "write_result",
    "delete": "write_result",
    "natural": "natural_sql",
    "help_catalog": "help_catalog",
    "command_explain": "command_help",
    "term_explain": "term_help",
    "practice_list": "practice_list",
    "practice_schema": "practice_schema",
    "practice_query": "practice_query_result",
    "practice_grade": "practice_grade",
    "practice_attempts": "practice_attempts",
    "practice_feedback": "practice_feedback",
    "jpa_schema": "model_schema",
    "db_knowledge": "knowledge",
    "provider_add": "provider_config",
    "provider_list_presets": "provider_presets",
    "provider_add_preset": "provider_config",
    "provider_list": "provider_list",
    "provider_remove": "provider_config",
    "provider_test": "provider_diagnostic",
    "production_profile_add": "production_profile",
    "production_profile_list": "production_profile",
    "production_review": "production_review",
    "production_approve": "production_review",
    "production_execute": "production_execution",
}


ACTIONS = {
    "schema": ["copy", "insert_template", "explain"],
    "schema_detail": ["copy", "insert_template", "explain"],
    "doctor": ["copy", "retry"],
    "query": ["copy", "export", "explain"],
    "generate": ["copy_sql", "run_query", "review", "save_as_practice"],
    "insert": ["copy", "run_again", "review_safety"],
    "update": ["copy", "run_again", "review_safety"],
    "delete": ["copy", "run_again", "review_safety"],
    "natural": ["copy_sql", "run_query", "review", "save_as_practice"],
    "help_catalog": ["copy", "explain_command", "explain_term"],
    "command_explain": ["copy", "insert_example", "show_terms"],
    "term_explain": ["copy", "show_related_commands"],
    "practice_list": ["copy", "start_practice", "show_schema"],
    "practice_schema": ["copy", "insert_template", "start_practice"],
    "practice_query": ["copy", "grade", "save_attempt"],
    "practice_grade": ["copy", "retry", "save_wrong_note"],
    "practice_attempts": ["copy", "review_wrong_notes"],
    "practice_feedback": ["copy", "retry", "request_provider_feedback"],
    "jpa_schema": ["copy", "explain"],
    "db_knowledge": ["copy", "explain"],
    "provider_add": ["copy", "test_provider", "use_provider"],
    "provider_list_presets": ["copy", "add_provider"],
    "provider_add_preset": ["copy", "test_provider", "use_provider"],
    "provider_list": ["copy", "test_provider", "remove_provider"],
    "provider_remove": ["copy"],
    "provider_test": ["copy", "retry", "use_provider"],
    "production_profile_add": ["copy", "review"],
    "production_profile_list": ["copy", "review"],
    "production_review": ["copy_sql", "approve", "audit"],
    "production_approve": ["copy_sql", "execute", "audit"],
    "production_execute": ["copy", "export", "audit"],
}


CLI_FLAG_ORDER = [
    "db",
    "db_uri",
    "sql",
    "table",
    "skill",
    "params",
    "provider_name",
    "provider_kind",
    "preset",
    "model_name",
    "base_url",
    "chat_completions_url",
    "models_url",
    "api_key_env",
    "profile_name",
    "db_uri_env",
    "review_id",
    "request_text",
    "source_command",
    "read_write",
    "jpa_project",
    "dialect",
    "topic",
    "lang",
    "pack",
    "problem_id",
    "limit",
    "mode",
    "allow_external_provider",
    "provider_policy",
    "no_record",
    "format",
    "write",
    "dry_run",
    "max_affected_rows",
    "allow_full_table_write",
]


CLI_FLAGS = {
    "db": "--db",
    "db_uri": "--db-uri",
    "sql": "--sql",
    "table": "--table",
    "skill": "--skill",
    "params": "--params",
    "provider_name": "--provider-name",
    "provider_kind": "--provider-kind",
    "preset": "--preset",
    "model_name": "--model-name",
    "base_url": "--base-url",
    "chat_completions_url": "--chat-completions-url",
    "models_url": "--models-url",
    "api_key_env": "--api-key-env",
    "profile_name": "--profile-name",
    "db_uri_env": "--db-uri-env",
    "review_id": "--review-id",
    "request_text": "--request-text",
    "source_command": "--source-command",
    "read_write": "--read-write",
    "jpa_project": "--jpa-project",
    "dialect": "--dialect",
    "topic": "--topic",
    "lang": "--lang",
    "pack": "--pack",
    "problem_id": "--problem-id",
    "limit": "--limit",
    "mode": "--mode",
    "allow_external_provider": "--allow-external-provider",
    "provider_policy": "--provider-policy",
    "no_record": "--no-record",
    "format": "--format",
    "write": "--write",
    "dry_run": "--dry-run",
    "max_affected_rows": "--max-affected-rows",
    "allow_full_table_write": "--allow-full-table-write",
}


MODE_AWARE_COMMANDS = {
    "natural",
    "practice_list",
    "practice_schema",
    "practice_query",
    "practice_grade",
    "practice_attempts",
    "practice_feedback",
    "production_profile_add",
    "production_profile_list",
    "production_review",
    "production_approve",
    "production_execute",
}


def _get(args: CommandArgs, context: CommandArgs, key: str, default: Any = None) -> Any:
    if key in args and args[key] is not None:
        return args[key]
    if key in context and context[key] is not None:
        return context[key]
    return default


def _db_target(args: CommandArgs, context: CommandArgs) -> str:
    db_uri = _get(args, context, "db_uri")
    if db_uri is not None:
        return str(db_uri)
    return str(_get(args, context, "db", DEFAULT_DB))


def _coerce_params(raw: Any) -> Any:
    if raw is None:
        return None
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


def _command_error(command: str, code: str, message: str, args: CommandArgs, context: CommandArgs) -> CommandResult:
    result = {
        "ok": False,
        "command": command,
        "data": {},
        "error": {"code": code, "message": message},
    }
    return _enrich_result(result, command, args, context)


def _mode_context(args: CommandArgs, context: CommandArgs) -> dict[str, Any]:
    return build_mode_context(
        mode=_get(args, context, "mode"),
        allow_external_provider=_get(args, context, "allow_external_provider", False),
        provider_policy=_get(args, context, "provider_policy"),
    )


def _has_mode_input(args: CommandArgs, context: CommandArgs) -> bool:
    return any(
        key in args or key in context
        for key in ("mode", "allow_external_provider", "provider_policy")
    )


def _quote_cli_value(value: Any) -> str:
    text = str(value)
    if text == "":
        return '""'
    if all(ch.isalnum() or ch in "._-/:@" for ch in text):
        return text
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _cli_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _cli_args(command: str, args: CommandArgs, context: CommandArgs) -> CommandArgs:
    cli_args: CommandArgs = {"format": _get(args, context, "format", DEFAULT_FORMAT)}

    for key in CLI_FLAG_ORDER:
        if key == "format":
            continue
        value = _get(args, context, key)
        if value is not None:
            cli_args[key] = value

    if "db_uri" not in cli_args and "db" not in cli_args:
        if command in {"schema", "schema_detail", "doctor", "query", "generate", "insert", "update", "delete", "natural"}:
            cli_args["db"] = DEFAULT_DB

    if command == "query" and "sql" not in cli_args:
        cli_args["sql"] = "SELECT * FROM users"
    if command == "generate" and "skill" not in cli_args:
        cli_args["skill"] = "select_simple"
    if command == "natural" and "sql" not in cli_args:
        cli_args["sql"] = "show users"
    if command == "practice_query" and "sql" not in cli_args:
        cli_args["sql"] = "SELECT * FROM customers"
    if command == "practice_grade" and "problem_id" not in cli_args:
        cli_args["problem_id"] = "basic_select_customers"
    if command == "practice_grade" and "sql" not in cli_args:
        cli_args["sql"] = "SELECT id, name, region FROM customers ORDER BY id"
    if command == "practice_feedback" and "problem_id" not in cli_args:
        cli_args["problem_id"] = "basic_select_customers"
    if command == "practice_feedback" and "sql" not in cli_args:
        cli_args["sql"] = "SELECT id, name FROM customers ORDER BY id"
    if command == "production_profile_add" and _get(args, context, "read_only") is False:
        cli_args["read_write"] = True
    if command in {"production_review", "production_profile_add"} and "profile_name" not in cli_args:
        cli_args["profile_name"] = "prod_readonly"
    if command == "production_review" and "sql" not in cli_args:
        cli_args["sql"] = "SELECT * FROM users"
    if command in {"production_approve", "production_execute"} and "review_id" not in cli_args:
        cli_args["review_id"] = "prodrev_id"

    return cli_args


def build_cli_equivalent(command: str, args: CommandArgs | None = None, context: CommandArgs | None = None) -> str:
    """Build the CLI command shown in app shells for trust and reproducibility."""

    safe_args = dict(args or {})
    safe_context = dict(context or {})
    cli_args = _cli_args(command, safe_args, safe_context)

    parts = ["python", "main.py", "--command", command]
    for key in CLI_FLAG_ORDER:
        if key not in cli_args:
            continue
        value = cli_args[key]
        flag = CLI_FLAGS[key]
        if isinstance(value, bool):
            if value:
                parts.append(flag)
            continue
        parts.extend([flag, _quote_cli_value(_cli_value(value))])
    return " ".join(parts)


def _enrich_result(result: CommandResult, command: str, args: CommandArgs, context: CommandArgs) -> CommandResult:
    enriched = dict(result)
    enriched.setdefault("ok", False)
    enriched.setdefault("command", command)
    enriched.setdefault("data", {})
    enriched.setdefault("error", None)
    if command in MODE_AWARE_COMMANDS or _has_mode_input(args, context):
        mode_context = dict(enriched.get("mode_context") or _mode_context(args, context))
        enriched["mode_context"] = mode_context
        if isinstance(enriched["data"], dict):
            enriched["data"].setdefault("mode_context", mode_context)
    enriched["block_type"] = BLOCK_TYPES.get(command, "command_result")
    enriched["actions"] = ACTIONS.get(command, ["copy"])
    enriched["cli_equivalent"] = build_cli_equivalent(command, args, context)
    return enriched


def _dispatch(command: str, args: CommandArgs, context: CommandArgs) -> CommandResult:
    fmt = str(_get(args, context, "format", DEFAULT_FORMAT))
    db = _db_target(args, context)
    params = _coerce_params(_get(args, context, "params"))
    mode_context = _mode_context(args, context)
    if command in {"natural", "practice_feedback"}:
        policy_result = provider_policy_block_result(
            command,
            _get(args, context, "provider_name"),
            mode_context,
        )
        if policy_result:
            return policy_result

    dispatchers: dict[str, Callable[[], CommandResult]] = {
        "schema": lambda: schema_handler(db, fmt),
        "schema_detail": lambda: schema_detail_handler(db, _get(args, context, "table"), fmt),
        "doctor": lambda: doctor_handler(db, fmt),
        "query": lambda: query_handler(
            db,
            str(_get(args, context, "sql", "SELECT * FROM users")),
            fmt,
            bool(_get(args, context, "write", False)),
            bool(_get(args, context, "dry_run", False)),
            _get(args, context, "max_affected_rows"),
            bool(_get(args, context, "allow_full_table_write", False)),
        ),
        "generate": lambda: generate_handler(db, _get(args, context, "skill", "select_simple"), fmt, params),
        "insert": lambda: insert_handler(
            db,
            _get(args, context, "sql"),
            params,
            bool(_get(args, context, "write", False)),
            bool(_get(args, context, "dry_run", False)),
            _get(args, context, "max_affected_rows"),
            bool(_get(args, context, "allow_full_table_write", False)),
        ),
        "update": lambda: update_handler(
            db,
            _get(args, context, "sql"),
            params,
            bool(_get(args, context, "write", False)),
            bool(_get(args, context, "dry_run", False)),
            _get(args, context, "max_affected_rows"),
            bool(_get(args, context, "allow_full_table_write", False)),
        ),
        "delete": lambda: delete_handler(
            db,
            _get(args, context, "sql"),
            params,
            bool(_get(args, context, "write", False)),
            bool(_get(args, context, "dry_run", False)),
            _get(args, context, "max_affected_rows"),
            bool(_get(args, context, "allow_full_table_write", False)),
        ),
        "natural": lambda: natural_handler(
            db,
            _get(args, context, "sql"),
            fmt,
            _get(args, context, "provider_name"),
            mode_context["mode"],
            mode_context["allow_external_provider"],
            mode_context["provider_policy"],
        ),
        "help_catalog": lambda: help_catalog_handler(_get(args, context, "lang")),
        "command_explain": lambda: command_explain_handler(
            _get(args, context, "topic"),
            _get(args, context, "lang"),
        ),
        "term_explain": lambda: term_explain_handler(
            _get(args, context, "topic"),
            _get(args, context, "lang"),
        ),
        "practice_list": lambda: practice_list_handler(_get(args, context, "pack")),
        "practice_schema": lambda: practice_schema_handler(
            _get(args, context, "pack"),
            _get(args, context, "table"),
        ),
        "practice_query": lambda: practice_query_handler(
            _get(args, context, "sql"),
            _get(args, context, "pack"),
            _get(args, context, "limit"),
        ),
        "practice_grade": lambda: practice_grade_handler(
            _get(args, context, "problem_id"),
            _get(args, context, "sql"),
            _get(args, context, "pack"),
            record=not bool(_get(args, context, "no_record", False)),
        ),
        "practice_attempts": lambda: practice_attempts_handler(
            _get(args, context, "pack"),
            _get(args, context, "problem_id"),
            _get(args, context, "limit"),
        ),
        "practice_feedback": lambda: practice_feedback_handler(
            _get(args, context, "problem_id"),
            _get(args, context, "sql"),
            _get(args, context, "pack"),
            _get(args, context, "provider_name"),
            _get(args, context, "mode"),
        ),
        "jpa_schema": lambda: jpa_schema_handler(_get(args, context, "jpa_project"), fmt),
        "db_knowledge": lambda: db_knowledge_handler(_get(args, context, "dialect"), _get(args, context, "topic")),
        "provider_add": lambda: provider_add_handler(
            _get(args, context, "provider_name"),
            _get(args, context, "provider_kind"),
            _get(args, context, "model_name"),
            _get(args, context, "base_url"),
            _get(args, context, "api_key_env"),
            _get(args, context, "chat_completions_url"),
            _get(args, context, "models_url"),
        ),
        "provider_list_presets": provider_list_presets_handler,
        "provider_add_preset": lambda: provider_add_preset_handler(
            _get(args, context, "preset"),
            _get(args, context, "provider_name"),
            _get(args, context, "model_name"),
            _get(args, context, "api_key_env"),
            _get(args, context, "base_url"),
            _get(args, context, "chat_completions_url"),
            _get(args, context, "models_url"),
        ),
        "provider_list": provider_list_handler,
        "provider_remove": lambda: provider_remove_handler(_get(args, context, "provider_name")),
        "provider_test": lambda: provider_test_handler(_get(args, context, "provider_name")),
        "production_profile_add": lambda: production_profile_add_handler(
            _get(args, context, "profile_name"),
            _get(args, context, "db_uri"),
            _get(args, context, "db_uri_env"),
            bool(_get(args, context, "read_only", True)),
            _get(args, context, "dialect"),
        ),
        "production_profile_list": production_profile_list_handler,
        "production_review": lambda: production_review_handler(
            _get(args, context, "profile_name"),
            _get(args, context, "sql"),
            _get(args, context, "request_text"),
            _get(args, context, "source_command"),
        ),
        "production_approve": lambda: production_approve_handler(_get(args, context, "review_id")),
        "production_execute": lambda: production_execute_handler(_get(args, context, "review_id")),
    }

    if command not in dispatchers:
        return _command_error(command, "unknown_command", f"Unknown command: {command}.", args, context)
    return dispatchers[command]()


def run_command(
    command: str,
    args: CommandArgs | None = None,
    context: CommandArgs | None = None,
) -> CommandResult:
    """Run one CoQuery command through handlers and return app-shell metadata."""

    normalized_command = (command or "").strip()
    safe_args = dict(args or {})
    safe_context = dict(context or {})
    if not normalized_command:
        return _command_error("", "missing_command", "Command is required.", safe_args, safe_context)

    try:
        result = _dispatch(normalized_command, safe_args, safe_context)
    except json.JSONDecodeError as exc:
        result = {
            "ok": False,
            "command": normalized_command,
            "data": {},
            "error": {
                "code": "invalid_params",
                "message": f"params must be valid JSON: {exc.msg}.",
            },
        }
    except Exception as exc:
        result = {
            "ok": False,
            "command": normalized_command,
            "data": {},
            "error": {
                "code": "command_api_error",
                "message": str(exc),
            },
        }

    return _enrich_result(result, normalized_command, safe_args, safe_context)
