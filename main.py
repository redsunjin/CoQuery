#!/usr/bin/env python3
"""CoQuery CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from sql_cli.cli import (
    doctor_handler,
    db_knowledge_handler,
    delete_handler,
    generate_handler,
    insert_handler,
    jpa_schema_handler,
    natural_handler,
    provider_add_handler,
    provider_list_handler,
    provider_remove_handler,
    provider_test_handler,
    query_handler,
    schema_detail_handler,
    schema_handler,
    update_handler,
)


def _parse_params(raw: str | None) -> Any:
    if not raw:
        return None
    return json.loads(raw)


def _resolve_db_target(db: str, db_uri: str | None) -> str:
    if db_uri is not None:
        return db_uri
    return db


def main() -> int:
    parser = argparse.ArgumentParser(description="CoQuery CLI")
    parser.add_argument(
        "--command",
        type=str,
        default=None,
        help="schema, schema_detail, doctor, query, generate, insert, update, delete, natural, jpa_schema, db_knowledge, provider_add, provider_list, provider_remove, provider_test",
    )
    parser.add_argument("--db", type=str, default="example.db", help="Legacy SQLite path or DB URI")
    parser.add_argument("--db-uri", type=str, default=None, help="Preferred multi-backend database URI")
    parser.add_argument("--sql", type=str, default=None, help="Raw SQL or natural-language text for natural")
    parser.add_argument("--table", type=str, default=None, help="Optional table name for schema_detail")
    parser.add_argument("--skill", type=str, default=None, help="SQL generation skill id")
    parser.add_argument("--params", type=str, default=None, help="JSON parameters payload")
    parser.add_argument("--provider-name", type=str, default=None, help="Registered LLM provider name")
    parser.add_argument("--provider-kind", type=str, default=None, help="LLM provider kind: ollama, openai_compatible")
    parser.add_argument("--model-name", type=str, default=None, help="LLM model name for provider registration")
    parser.add_argument("--base-url", type=str, default=None, help="Base URL for provider registration")
    parser.add_argument("--api-key-env", type=str, default=None, help="Environment variable name for API key")
    parser.add_argument("--jpa-project", type=str, default=None, help="Path to a Java/JPA project or .java entity file")
    parser.add_argument("--dialect", type=str, default=None, help="Knowledge dialect: sqlite, postgresql, mysql, jpql")
    parser.add_argument("--topic", type=str, default=None, help="Knowledge topic, such as overview, statements, schema, schema_detail, pagination, coverage, write_safety")
    parser.add_argument("--format", type=str, default="json", help="Output format")
    parser.add_argument(
        "--write",
        action="store_true",
        default=False,
        help="Required for state-changing SQL in query/insert/update/delete",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Execute state-changing SQL inside a rollback-only preview",
    )
    parser.add_argument(
        "--max-affected-rows",
        type=int,
        default=None,
        help="Abort and roll back if a write affects more than this many rows",
    )
    parser.add_argument(
        "--allow-full-table-write",
        action="store_true",
        default=False,
        help="Allow UPDATE/DELETE statements without WHERE",
    )
    args = parser.parse_args()

    if not args.command:
        print("CoQuery v0.7.1")
        print("commands: schema, schema_detail, doctor, query, generate, insert, update, delete, natural, jpa_schema, db_knowledge, provider_add, provider_list, provider_remove, provider_test")
        print("write commands require explicit --write and --sql")
        print("state-changing commands support optional --dry-run preview and --max-affected-rows guard")
        print("full-table UPDATE/DELETE requires explicit --allow-full-table-write")
        print("prefer --db-uri for multi-backend contracts; --db remains SQLite-first compatibility")
        return 0

    parsed_params = _parse_params(args.params)
    db_target = _resolve_db_target(args.db, args.db_uri)

    if args.command == "schema":
        result = schema_handler(db_target, args.format)
    elif args.command == "schema_detail":
        result = schema_detail_handler(db_target, args.table, args.format)
    elif args.command == "doctor":
        result = doctor_handler(db_target, args.format)
    elif args.command == "query":
        result = query_handler(
            db_target,
            args.sql or "SELECT * FROM users",
            args.format,
            args.write,
            args.dry_run,
            args.max_affected_rows,
            args.allow_full_table_write,
        )
    elif args.command == "generate":
        result = generate_handler(db_target, args.skill or "select_simple", args.format, parsed_params)
    elif args.command == "insert":
        result = insert_handler(
            db_target,
            args.sql,
            parsed_params,
            args.write,
            args.dry_run,
            args.max_affected_rows,
            args.allow_full_table_write,
        )
    elif args.command == "update":
        result = update_handler(
            db_target,
            args.sql,
            parsed_params,
            args.write,
            args.dry_run,
            args.max_affected_rows,
            args.allow_full_table_write,
        )
    elif args.command == "delete":
        result = delete_handler(
            db_target,
            args.sql,
            parsed_params,
            args.write,
            args.dry_run,
            args.max_affected_rows,
            args.allow_full_table_write,
        )
    elif args.command == "natural":
        result = natural_handler(db_target, args.sql, args.format, args.provider_name)
    elif args.command == "jpa_schema":
        result = jpa_schema_handler(args.jpa_project, args.format)
    elif args.command == "db_knowledge":
        result = db_knowledge_handler(args.dialect, args.topic)
    elif args.command == "provider_add":
        result = provider_add_handler(
            args.provider_name,
            args.provider_kind,
            args.model_name,
            args.base_url,
            args.api_key_env,
        )
    elif args.command == "provider_list":
        result = provider_list_handler()
    elif args.command == "provider_remove":
        result = provider_remove_handler(args.provider_name)
    elif args.command == "provider_test":
        result = provider_test_handler(args.provider_name)
    else:
        result = {"ok": False, "command": args.command, "error": "Unknown"}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
