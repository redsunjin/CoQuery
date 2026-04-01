#!/usr/bin/env python3
import sqlite3

class CoQueryDB:
    def __init__(self, db_type='sqlite', db_uri=None):
        self.type = db_type
        self.uri = db_uri
        self.conn = None
        if db_type == 'sqlite':
            self.connect_sqlite()
    
    def connect_sqlite(self):
        try:
            path = self.uri.replace('sqlite://', '')
            self.conn = sqlite3.connect(path)
            return True
        except Exception as e:
            print(f"SQLite error: {e}")
            return False
    
    def connect_postgresql(self):
        print("PostgreSQL not yet implemented")
        return False
    
    def connect_mysql(self):
        print("MySQL not yet implemented")
        return False
    
    def connect(self):
        if self.type == 'sqlite':
            return self.connect_sqlite()
        elif self.type == 'postgresql':
            return self.connect_postgresql()
        elif self.type == 'mysql':
            return self.connect_mysql()
        return False
    
    def execute(self, sql, params=None):
        if not self.conn:
            self.connect()
        if self.conn:
            cursor = self.conn.execute(sql, params or [])
            return cursor.fetchall()
        return []
    
    def get_schemas(self):
        if self.conn:
            return [t[0] for t in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        return []
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def __repr__(self):
        return f"CoQueryDB(type={self.type})"
