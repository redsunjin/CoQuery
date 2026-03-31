#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli.py - CLI interface (interactive + JSON)
Stable command surface definition
"""

import json
import sys
from typing import Optional

from .db import DBClient
from .contracts import ResponsePayload, SchemaRequest, QueryRequest, GenerateRequest
from .core import EasySQLCore, SQL_SKILLS


class CLIContext:
    """CLI context holder"""
    def __init__(self):
        self.is_json_mode = False

    def set_json_mode(self, flag: bool):
        self.is_json_mode = flag

    def output(self, payload: ResponsePayload):
        """Output payload as JSON or human-readable"""
        if self.is_json_mode:
            print(json.dumps(payload.to_dict(), indent=2, ensure_ascii=False))
        else:
            self.output_human(payload)

    def output_human(self, payload: ResponsePayload):
        """Human-readable output"""
        if payload.ok:
            print(f"[OK] {payload.command}")
            if payload.data:
                if isinstance(payload.data, dict) and "tables" in payload.data:
                    self.print_tables(payload.data["tables"])
                else:
                    for k, v in payload.data.items():
                        print(f"   {k}: {v}")
        else:
            print(f"[ERROR] {payload.command}: {payload.error}")


class DBCommand:
    """Database commands handler"""

    def __init__(self, ctx: CLIContext):
        self.ctx = ctx

    def schema_list(self, request: SchemaRequest) -> ResponsePayload:
        """
        List table schemas (read-only)
        Command: easysql schema --db <path> --format json
        """
        try:
            db = DBClient(request.db_path)
            tables = db.get_tables()
            schema_response = {
                "tables": [
                    {
                        "name": t.name,
                        "columns": [c.name for c in t.columns],
                        "is_view": t.is_view,
                    }
                    for t in tables
                ]
            }
            return ResponsePayload.success("schema", schema_response)
        except Exception as e:
            return ResponsePayload.failure(
                "schema",
                "db_error",
                f"Database error: {str(e)})",
            )

    def query_execute(self, request: QueryRequest) -> ResponsePayload:
        """
        Execute query (read-only)
        Command: easysql query --db <path> --sql <query> --limit <n>
        """
        if request.sql.strip().upper().startswith("SELECT") is False:
            return ResponsePayload.failure("query", "read_only", "Only SELECT allowed")

        try:
            db = DBClient(request.db_path)
            row_count, rows = db.execute_query(request.sql, request.limit)
            
            if len(rows) > request.limit:
                truncated = True
                rows = rows[:request.limit]
            else:
                truncated = False
            
            query_response = {
                "row_count": row_count,
                "rows": rows,
                "truncated": truncated,
            }
            return ResponsePayload.success("query", query_response)
        except Exception as e:
            return ResponsePayload.failure(
                "query", "execution_error", f"Query execution failed: {str(e)})",
            )


class GenerateCommand:
    """Generate command handler"""

    def __init__(self, ctx: CLIContext):
        self.ctx = ctx
        self.core = EasySQLCore

    def list_skills(self) -> ResponsePayload:
        """List all SQL skills"""
        skills = SQL_SKILLS
        return ResponsePayload.success("skills", {"count": len(skills)})


class InteractiveCLI:
    """Interactive CLI interface"""

    def __init__(self):
        self.ctx = CLIContext()

    def show_menu(self):
        """Show main menu"""
        print("\n==============================")
        print("   EasySQL AI Agent")
        print("==============================")
        print("   1. 테이블 목록 (schema)")
        print("   2. 쿼리 실행 (query)")
        print("   3. SQL 생성 (generate)")
        print("   4. 스킬 목록")
        print("   0. 종료")
        print("==============================")
        print("   --format json: JSON 모드")
        print("==============================")

    def run_interactive(self, db_path: str = "example.db"):
        """Run interactive mode"""
        while True:
            self.show_menu()
            cmd = input("선택 (skill-id): ") or ""

            if cmd == "0":
                print("\nEasySQL 종료!")
                break

            elif cmd == "1":
                 # schema
                self.db_command.db_path = db_path
                payload = self.db_command.schema_list(SchemaRequest(db_path))
                self.ctx.output(payload)

            elif cmd == "2":
                 # query
                self.db_command.db_path = db_path
                print("SQL 입력: ", end="", flush=True)
                query = input()
                if query.strip().upper().startswith("SELECT"):
                    payload = self.db_command.query_execute(QueryRequest(db_path, query, 20))
                else:
                    payload = ResponsePayload.failure("query", "read_only", "SELECT only")
                self.ctx.output(payload)

            elif cmd == "3":
                 # generate
                print("Skill ID: ", end="", flush=True)
                skill_id = input() or "select_simple"
                params = {
                    "table": input("Table: ") or "users",
                    "cols": input("Columns: ") or "*",
                    "where": input("WHERE: ") or "",
                    "order": input("ORDER: ") or "",
                }
                core = EasySQLCore(db_path)
                result = core.generate_query(skill_id, params)
                
                if "error" in result:
                    payload = ResponsePayload.failure(
                        "generate", "skill_error", result["error"]
                    )
                else:
                    payload = ResponsePayload.success(
                        "generate", result
                    )
                self.ctx.output(payload)

            elif cmd == "4":
                 # skills list
                core = EasySQLCore(db_path)
                skills = core.list_skills()
                payload = ResponsePayload.success("skills", {"skills": skills})
                self.ctx.output(payload)

            else:
                print("[Error] 잘못된 입력")


def main_interactive(db_path: str = "example.db"):
    """Main entry point for interactive mode"""
    cli = InteractiveCLI()
    cli.run_interactive(db_path)


def main_json_command():
    """JSON command interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EasySQL CLI")
    parser.add_argument("--command", required=True, help="Command (schema/query/generate)")
    parser.add_argument("--db", required=True, help="Database path")
    parser.add_argument("--sql", help="SQL query")
    parser.add_argument("--skill", help="Skill ID for generate")
    parser.add_argument("--limit", type=int, default=20, help="Row limit")
    parser.add_argument("--format", default="text", help="Output format (text/json)")

    args = parser.parse_args()

    if args.command == "schema":
        ctx = CLIContext()
        ctx.set_json_mode(args.format == "json")
        payload = DBCommand(ctx).schema_list(SchemaRequest(args.db))
        ctx.output(payload)

    elif args.command == "query":
        if not args.sql:
            print('ERROR: --sql required')
            sys.exit(1)
        ctx = CLIContext()
        ctx.set_json_mode(args.format == "json")
        payload = DBCommand(ctx).query_execute(QueryRequest(args.db, args.sql, args.limit))
        ctx.output(payload)

    elif args.command == "generate":
        if not args.skill:
            print('ERROR: --skill required')
            sys.exit(1)
        ctx = CLIContext()
        ctx.set_json_mode(args.format == "json")
        core = EasySQLCore(args.db)
        params = {
            "table": args.sql.split("FROM")[-1].strip().split()[0] if args.sql else "users",
            "cols": "*",
            "where": "",
            "order": "",
        }
        result = core.generate_query(args.skill, params)
        
        if "error" not in result:
            payload = ResponsePayload.success("generate", result)
        else:
            payload = ResponsePayload.failure("generate", "skill_error", result["error"])
        
        if args.format == "json":
            print(json.dumps(payload.to_dict(), indent=2))
        else:
            ctx.output(payload)

    else:
        print(f"ERROR: Unknown command {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main_json_command()
