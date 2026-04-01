#!/usr/bin/env python3
"""UnifiedDatabase for Multi-DB Support (Phase 4)"""

class UnifiedDatabase:
    """
    Unified Database Interface
    Supports SQLite, PostgreSQL, MySQL
    """
    
    SUPPORTED_DB_TYPES = {
        'sqlite': 'SQLite',
        'postgresql': 'PostgreSQL', 
        'mysql': 'MySQL'
    }
    
    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.db_type = self._detect_type(db_uri)
        self.conn = None
        self.schema_knowledge = None
    
    def _detect_type(self, uri):
        """Detect database type from URI"""
        if uri.startswith('sqlite://'):
            return 'sqlite'
        elif uri.startswith('postgresql://') or uri.startswith('postgres://'):
            return 'postgresql'
        elif uri.startswith('mysql://'):
            return 'mysql'
        else:
            return 'sqlite'  # default
    
    def connect(self):
        """Establish database connection"""
        if self.db_type == 'sqlite':
            try:
                import sqlite3
                path = self.db_uri.replace('sqlite://', '')
                self.conn = sqlite3.connect(path)
                return True
            except Exception as e:
                print(f"SQLite connection failed: {e}")
                return False
        elif self.db_type in ['postgresql', 'mysql']:
            # TODO: Implement for PostgreSQL/MySQL
            print(f"Connection not implemented for {self.db_type}")
            return False
        return False
    
    def execute(self, query, params=None):
        """Execute query with parameters"""
        if not self.conn:
            self.connect()
        
        if self.db_type == 'sqlite' and self.conn:
            try:
                cursor = self.conn.execute(query, params or [])
                return cursor.fetchall()
            except Exception as e:
                print(f"Execution error: {e}")
                return []
        return []
    
    def get_schemas(self):
        """Get database schema information"""
        if self.db_type == 'sqlite' and self.conn:
            try:
                cursor = self.conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = [row[0] for row in cursor.fetchall()]
                return [
                    {
                        'name': table,
                        'columns': self._get_columns(table),
                        'is_view': False
                    }
                    for table in tables
                ]
            except Exception:
                return []
        return []
    
    def _get_columns(self, table_name):
        """Get column names for table"""
        try:
            cursor = self.conn.execute(
                f"PRAGMA table_info({table_name})"
            )
            return [col[1] for col in cursor.fetchall()]
        except Exception:
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __repr__(self):
        return f"UnifiedDatabase(type={self.db_type}, uri={self.db_uri[:30]}...)"


class TableColumn:
    """Table Column definition"""
    
    def __init__(self, name, col_type, is_primary=False):
        self.name = name
        self.col_type = col_type
        self.is_primary = is_primary
    
    def to_dict(self):
        return {
            'name': self.name,
            'col_type': self.col_type,
            'is_primary': self.is_primary
         }

def create_table(db_uri, table_name, columns):
    """Create table in database"""
    db = UnifiedDatabase(db_uri)
    db.connect()
    
    col_defs = ", ".join([
        f"{col.name} {col.col_type}" for col in columns
    ])
    
    if any(col.is_primary for col in columns):
        col_defs += ", PRIMARY KEY"
    
    db.execute(f"CREATE TABLE {table_name} ({col_defs})")
    return db

def drop_table(db_uri, table_name):
    """Drop table from database"""
    db = UnifiedDatabase(db_uri)
    db.connect()
    db.execute(f"DROP TABLE {table_name}")
    return db


class TableSchema:
    """Table Schema definition"""
    
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.is_view = False
    
    def to_dict(self):
        return {
            'name': self.name,
            'columns': [c.name for c in self.columns],
            'is_view': self.is_view
         }

class TableSchemaBuilder:
    """Builder for table schemas"""
    
    def __init__(self):
        self.schema = TableSchema("", [])
    
    def set_table(self, name):
        self.schema.name = name
        return self
    
    def add_column(self, name, col_type, primary=False):
        col = TableColumn(name, col_type, primary)
        self.schema.columns.append(col)
        return self
    
    def build(self):
        return self.schema

def create_schema(db_uri, table_name, columns):
    """Create table with columns"""
    builder = TableSchemaBuilder()
    for col in columns:
        builder.add_column(col['name'], col['type'], col.get('primary', False))
    
    schema = builder.build()
    return schema
