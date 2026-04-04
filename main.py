#!/usr/bin/env python3
"""CoQuery CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from sql_cli.cli import (
    delete_handler,
    generate_handler,
    insert_handler,
    natural_handler,
    query_handler,
    schema_handler,
    update_handler,
)


def _parse_params(raw: str | None) -> Any:
    if not raw:
        return None
    return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="CoQuery CLI")
    parser.add_argument("--command", type=str, default=None)
    parser.add_argument("--db", type=str, default="example.db")
    parser.add_argument("--sql", type=str, default=None)
    parser.add_argument("--skill", type=str, default=None)
    parser.add_argument("--params", type=str, default=None)
    parser.add_argument("--format", type=str, default="json")
    parser.add_argument("--write", action="store_true", default=False)
    args = parser.parse_args()

    if not args.command:
        print("CoQuery v0.7.0")
        print("commands: schema, query, generate, insert, update, delete, natural")
        return 0

    parsed_params = _parse_params(args.params)

    if args.command == "schema":
        result = schema_handler(args.db, args.format)
    elif args.command == "query":
        result = query_handler(args.db, args.sql or "SELECT * FROM users", args.format, args.write)
    elif args.command == "generate":
        result = generate_handler(args.db, args.skill or "select_simple", args.format, parsed_params)
    elif args.command == "insert":
        result = insert_handler(args.db, args.sql, parsed_params)
    elif args.command == "update":
        result = update_handler(args.db, args.sql, parsed_params)
    elif args.command == "delete":
        result = delete_handler(args.db, args.sql, parsed_params)
    elif args.command == "natural":
        result = natural_handler(args.db, args.sql, args.format)
    else:
        result = {"ok": False, "command": args.command, "error": "Unknown"}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
