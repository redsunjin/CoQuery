#!/usr/bin/env python3
"""CLI Handler (Phase 0 - Simplified)"""

def schema_handler(db, format='json'):
     """Handle schema command"""
    return {
        'ok': True,
        'command': 'schema',
        'data': {
             'tables': []
         },
        'error': None
    }

def query_handler(db, sql, format='json'):
     """Handle query command"""
    return {
        'ok': True,
        'command': 'query',
        'data': {'rows': []},
        'error': None
    }

def generate_handler(db, skill, format='json'):
     """Handle generate command"""
    return {
        'ok': True,
        'command': 'generate',
        'command': skill,
        'error': None
    }

def natural_handler(db, sql, format='json'):
     """Handle natural command"""
    from sql_cli.nl_core import NLIntentParser
    parser = NLIntentParser()
    intent = parser.parse(sql)
     return {
         'ok': True,
         'command': 'natural',
         'intent': intent,
         'error': None
     }

# ============================
# Write Command Handlers (Phase 3)
# ============================

def insert_handler(db, table, columns, values):
     """INSERT new row"""
    try:
        import sqlite3
        conn = sqlite3.connect(db)
        cols = ", ".join(columns)
        vals = ", ".join(["?" for _ in values])
        conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({vals})", values)
        conn.commit()
        row_count = 1
        conn.close()
        return {"ok": True, "command": "insert", "affected_rows": row_count, "error": None}
    except Exception as e:
        return {"ok": False, "command": "insert", "affected_rows": 0, "error": str(e)}

def update_handler(db, table, set_clauses, where_clauses=None):
        """UPDATE rows"""
    try:
        import sqlite3
        conn = sqlite3.connect(db)
          if not where_clauses:
              where_clauses = "1=1"
          cols_str = ", ".join(set_clauses)
          where_str = where_clauses
          conn.execute(f"UPDATE {table} SET {cols_str} WHERE {where_str}")
          conn.commit()
        row_count = 1
        conn.close()
        return {"ok": True, "command": "update", "affected_rows": row_count, "error": None}
    except Exception as e:
        return {"ok": False, "command": "update", "affected_rows": 0, "error": str(e)}

def delete_handler(db, table, where_clauses=None):
      """DELETE rows"""
    try:
        import sqlite3
        conn = sqlite3.connect(db)
          if not where_clauses:
              where_clauses = "1=1"
          conn.execute(f"DELETE FROM {table} WHERE {where_clauses}")
          conn.commit()
        row_count = 1
        conn.close()
        return {"ok": True, "command": "delete", "affected_rows": row_count, "error": None}
    except Exception as e:
        return {"ok": False, "command": "delete", "affected_rows": 0, "error": str(e)}
