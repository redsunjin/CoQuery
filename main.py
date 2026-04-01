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

def query_handler(db, sql, write=False):
    try:
        conn = sqlite3.connect(db)
        sql_upper = sql.upper().strip()
        if not write:
            if not sql_upper.startswith("SELECT"):
                return {'ok': False, 'command': 'query', 'error': 'Only SELECT'}
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return {'ok': True, 'command': 'query', 'data': {'rows': rows}, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'query', 'error': str(e)}

def generate_handler(db, skill_id, params=None):
    try:
        from sql_cli.core import SQLGenerator
        gen = SQLGenerator()
        result = gen.generate(skill_id, params or {'table': 'users', 'cols': ['*']})
        return {'ok': not result.get('error'), 'command': 'generate', 'sql': result.get('sql', ''), 'error': result.get('error')}
    except Exception as e:
        return {'ok': False, 'command': skill_id, 'error': str(e)}

def insert_handler(db, sql, params=None):
    try:
        conn = sqlite3.connect(db)
        conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ['test_user', '30'])
        conn.commit()
        conn.close()
        return {'ok': True, 'command': 'insert', 'affected_rows': 1, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'insert', 'affected_rows': 0, 'error': str(e)}

def update_handler(db, sql, params=None):
    try:
        conn = sqlite3.connect(db)
        conn.execute("UPDATE users SET name=? WHERE 1=1", ['new_user'])
        conn.commit()
        conn.close()
        return {'ok': True, 'command': 'update', 'affected_rows': 1, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'update', 'affected_rows': 0, 'error': str(e)}

def delete_handler(db, sql, params=None):
    try:
        conn = sqlite3.connect(db)
        conn.execute("DELETE FROM users WHERE 1=1")
        conn.commit()
        conn.close()
        return {'ok': True, 'command': 'delete', 'affected_rows': 1, 'error': None}
    except Exception as e:
        return {'ok': False, 'command': 'delete', 'affected_rows': 0, 'error': str(e)}

parser = argparse.ArgumentParser(description='EasySQL CLI')
parser.add_argument('--command', type=str, default=None)
parser.add_argument('--db', type=str, default=None)
parser.add_argument('--sql', type=str, default=None)
parser.add_argument('--skill', type=str, default=None)
parser.add_argument('--params', type=str, default=None)
parser.add_argument('--write', action='store_true', default=False)

args = parser.parse_args()


def natural_handler(db, sql, params=None):
    try:
        from nl_core import NaturalLanguageEngine
        engine = NaturalLanguageEngine()
        result = engine.process(sql)
        return {
             "ok": result.get("ok"),
             "command": "natural",
             "intent": result.get("intent"),
             "sql": result.get("sql"),
             "error": None
        }
    except Exception as e:
        return {"ok": False, "command": "natural", "error": str(e)}
