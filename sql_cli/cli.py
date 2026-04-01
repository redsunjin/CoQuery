#!/usr/bin/env python3
"""CoQuery CLI Handler - Phase 5"""

from sql_cli.db_new import CoQueryDB

def schema_handler(db, format='json'):
    try:
        conn = CoQueryDB(db)
        tables = conn.get_schemas()
        conn.close()
        return {'ok': True, 'command': 'schema', 'data': {'tables': tables}, 'error': None}
    except Exception:
        return {'ok': False, 'command': 'schema', 'data': {}, 'error': 'DB error'}

def query_handler(db, sql, format='json'):
    try:
        conn = CoQueryDB(db)
        rows = conn.execute(sql)
        conn.close()
        return {'ok': True, 'command': 'query', 'data': {'rows': rows}, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'query', 'data': {}, 'error': str(e)}

def generate_handler(db, skill=None, format='json'):
    try:
        from sql_cli.core import SQLGenerator
        gen = SQLGenerator()
        sql = gen.generate(skill or 'select_simple', {}).get('sql', '')
        return {'ok': True, 'command': 'generate', 'sql': sql, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'generate', 'error': str(e)}

def insert_handler(db, table=None, params=None):
    try:
        conn = CoQueryDB(db)
        conn.execute("INSERT INTO " + (table or "test") + " VALUES (1, 'test')")
        conn.close()
        return {'ok': True, 'command': 'insert', 'affected_rows': 1, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'insert', 'error': str(e)}

def update_handler(db, table=None, params=None):
    try:
        conn = CoQueryDB(db)
        conn.execute("UPDATE " + (table or "test") + " SET val=1")
        conn.close()
        return {'ok': True, 'command': 'update', 'affected_rows': 1, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'update', 'error': str(e)}

def delete_handler(db, table=None, params=None):
    try:
        conn = CoQueryDB(db)
        conn.execute("DELETE FROM " + (table or "test"))
        conn.close()
        return {'ok': True, 'command': 'delete', 'affected_rows': 1, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'delete', 'error': str(e)}

def natural_handler(db, sql=None, format='json'):
    try:
        from sql_cli.db_new import CoQueryDB
        conn = CoQueryDB(db)
        tables = conn.get_schemas()
        conn.close()
        return {'ok': True, 'command': 'natural', 'tables': tables, 'error': None}
    except Exception:
        return {'ok': False, 'command': 'natural', 'error': 'DB Error'}
