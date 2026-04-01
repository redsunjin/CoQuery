#!/usr/bin/env python3
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

def query_handler(db, sql):
    try:
        conn = sqlite3.connect(db)
        sql_upper = sql.upper().strip()
        if not sql_upper.startswith("SELECT"):
            conn.close()
            return {'ok': False, 'command': 'query', 'error': 'Only SELECT queries'}
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] if cursor.description else []
        conn.close()
        return {'ok': True, 'command': 'query', 'data': {'rows': rows, 'columns': columns}, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'query', 'error': str(e)}

parser = argparse.ArgumentParser(description='EasySQL CLI')
parser.add_argument('--command', type=str, default=None, help='Command to run')
parser.add_argument('--db', type=str, default=None, help='Database path')
parser.add_argument('--sql', type=str, default=None, help='SQL query')
args = parser.parse_args()

if not args.command:
    print("EasySQL v0.6.0 Phase 1")
    print("Commands: schema, query, generate")
    sys.exit(0)

if args.command == 'schema':
    result = schema_handler(args.db)
elif args.command == 'query':
    result = query_handler(args.db, args.sql)
else:
    result = {'ok': False, 'command': args.command, 'error': 'Unknown command'}

print(json.dumps(result, indent=2))
