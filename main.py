#!/usr/bin/env python3
"""EasySQL Entry Point - Phase 2 Clean"""
import sys, json, sqlite3, argparse

def schema_handler(db):
    try:
        conn = sqlite3.connect(db)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return {'ok': True, 'command': 'schema', 'data': {'tables': tables}, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'schema', 'data': {}, 'error': str(e)}

def query_handler(db, sql, write=False):
    try:
        conn = sqlite3.connect(db)
        sql_upper = sql.upper().strip()
        if write:
            pass
        elif not sql_upper.startswith("SELECT"):
            conn.close()
            return {'ok': False, 'command': 'query', 'error': 'Only SELECT queries'}
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] if cursor.description else []
        conn.close()
        return {'ok': True, 'command': 'query', 'data': {'rows': rows, 'columns': columns}, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'query', 'error': str(e)}

def generate_handler(db, skill_id, params=None):
    try:
        from sql_cli.core import SQLGenerator
        core = SQLGenerator()
        if params is None:
            params = {'table': 'users', 'cols': ['*']}
        result = core.generate(skill_id, params)
        if not result.get('error'):
            return {'ok': True, 'command': 'generate', 'sql': result.get('sql', '')}
        else:
            return {'ok': False, 'command': skill_id, 'error': result['error']}
    except Exception as e:
        return {'ok': False, 'command': skill_id, 'error': str(e)}

parser = argparse.ArgumentParser(description='EasySQL CLI')
parser.add_argument('--command', type=str, default=None, help='Command to run')
parser.add_argument('--db', type=str, default=None, help='Database path')
parser.add_argument('--sql', type=str, default=None, help='SQL query')
parser.add_argument('--skill', type=str, default=None, help='Skill ID')
parser.add_argument('--params', type=str, default=None, help='Skills parameters')
parser.add_argument('--write', action='store_true', default=False, help='Write flag')

args = parser.parse_args()

if not args.command:
    print("EasySQL v0.6.0 Phase 2")
    print("Commands: schema, query, generate")
    sys.exit(0)

if args.command == 'schema':
    result = schema_handler(args.db)
elif args.command == 'query':
    result = query_handler(args.db, args.sql, args.write)
elif args.command == 'generate':
    params = None
    if args.params:
        try:
            params = json.loads(args.params)
        except:
            params = {'table': 'users', 'cols': ['*']}
    params = params or {'table': 'users', 'cols': ['*']}
    result = generate_handler(args.db, args.skill or 'select_simple', params)
else:
    result = {'ok': False, 'command': args.command, 'error': 'Unknown command'}

print(json.dumps(result, indent=2))
