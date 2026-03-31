#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasySQL - Main entry point
AI Assistant for SQL Development
Entry → Junior → Intermediate → Expert → SQLP
"""

import argparse
import sys
import json

from sql_cli import main_interactive, main_json_command


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
         description="EasySQL CLI - SQL Assistant for all levels",
         formatter_class=argparse.RawDescriptionHelpFormatter,
         epilog="""\
Examples:
   # Interactive mode
   python main.py
   
   # JSON mode: List schemas
   python main.py --command schema --db example.db --format json
   
   # JSON mode: Execute query
   python main.py --command query --db example.db --sql "SELECT * FROM users WHERE age>30" --format json
   
   # JSON mode: Generate SQL
   python main.py --command generate --db example.db --skill select_simple --format json
""",
    )
    
    parser.add_argument(
         "--interactive",
         action="store_true",
         help="Run in interactive mode (default)",
     )
    
    parser.add_argument(
         "--command",
         choices=["schema", "query", "generate"],
         help="Command to execute",
     )
    
    parser.add_argument(
         "--db",
         default="example.db",
         help="Database path (default: example.db)",
     )
    
    parser.add_argument(
         "--sql",
         help="SQL query for query command",
     )
    
    parser.add_argument(
         "--skill",
         help="Skill ID for generate command",
     )
    
    parser.add_argument(
         "--limit",
         type=int,
         default=20,
         help="Row limit (default: 20)",
     )
    
    parser.add_argument(
         "--format",
         choices=["text", "json"],
         default="text",
         help="Output format (default: text)",
     )
    
    parser.add_argument(
         "--version",
         action="store_true",
         help="Show version",
     )

    args = parser.parse_args()
    
    if args.version:
        print("EasySQL v0.1.0")
        print("SQL Developer → SQL Professional")
        sys.exit(0)
    
    # Choose mode
    if args.command:
        # JSON command mode
        sys.argv = [
             "sql_cli",
             "--command", args.command,
             "--db", args.db,
         ]
        if args.sql:
            sys.argv.extend(["--sql", args.sql])
        if args.skill:
            sys.argv.extend(["--skill", args.skill])
        if args.limit:
            sys.argv.extend(["--limit", str(args.limit)])
        sys.argv.extend(["--format", args.format])
        
        main_json_command()
    else:
        # Interactive mode (or default)
        main_interactive(args.db)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Exit] Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"[Error] {e}")
        sys.exit(1)
