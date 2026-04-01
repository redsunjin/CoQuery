#!/usr/bin/env python3
"""EasySQL Entry Point

Command routing restored for Phase 0 Recovery
"""

import sys
import click

# Lazy imports - avoid click dependency at import time
def load_sql_cli():
    try:
        from sql_cli.cli import main
        return main
    except ImportError as e:
        print(f"CLI import error: {e}")
        return None

@click.command()
@click.option('--command', type=str, default=None, help='Command to run')
@click.option('--db', type=str, default=None, help='Database path')
@click.option('--sql', type=str, default=None, help='SQL query')
@click.option('--skill', type=str, default=None, help='SQL skill ID')
@click.option('--format', type=str, default='json', help='Output format')
def main(command, db, sql, skill, format):
    """EasySQL CLI Entry Point"""
    
    if not command:
        print("EasySQL v0.6.0")
        print("Commands: schema, query, generate, natural, insert, update, delete")
        sys.exit(0)
    
    # Load CLI handler
    cli_handler = load_sql_cli()
    
    if not cli_handler:
        print(f"Error: Could not load CLI handler")
        print(f"Missing: click dependency")
        sys.exit(1)
    
    # Route to command
    if command == 'schema':
        result = cli_handler(command='schema', db=db, format=format)
    elif command == 'query':
        result = cli_handler(command='query', db=db, sql=sql, format=format)
    elif command == 'generate':
        result = cli_handler(command='generate', db=db, skill=skill, format=format)
    elif command == 'natural':
        result = cli_handler(command='natural', db=db, sql=sql, format=format)
    elif command == 'insert':
        result = cli_handler(command='insert', db=db, format=format)
    elif command == 'update':
        result = cli_handler(command='update', db=db, format=format)
    elif command == 'delete':
        result = cli_handler(command='delete', db=db, format=format)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    # Print result
    import json
    if format == 'json':
        print(json.dumps(result, indent=2))
    else:
        print(result)

if __name__ == '__main__':
    main()
