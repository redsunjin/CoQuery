#!/usr/bin/env python3
"""CoQuery Database Interface - Simple"""

import sqlite3

class CoQueryDB:
    """Unified Database Interface"""
    
    def __init__(self, db_path):
        self.path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def execute(self, sql, params=None):
        """Execute SQL"""
        cursor = self.conn.execute(sql, params or [])
        return cursor.fetchall()
    
    def get_schemas(self):
        """Get table names"""
        tables = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        return [t[0] for t in tables]
    
    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def __repr__(self):
        return f"CoQueryDB(path={self.path})"
