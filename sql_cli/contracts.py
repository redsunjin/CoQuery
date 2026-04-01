#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contracts.py - JSON payload models
Stable command interface definition
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional


@dataclass
class ResponsePayload:
    """
    Standard response envelope
    
    Success:
    {
        ok: true,
        command: "schema",
        data: { ... },
        error: null
    }
    
    Failure:
    {
        ok: false,
        command: "query",
        data: {},
        error: {
            code: "invalid_sql",
            message: "..."
        }
    }
    """

    ok: bool
    command: str
    data: Dict[str, Any]
    error: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def success(cls, command: str, data: Dict[str, Any]) -> "ResponsePayload":
        return cls(ok=True, command=command, data=data, error=None)

    @classmethod
    def failure(cls, command: str, code: str, message: str) -> "ResponsePayload":
        return cls(ok=False, command=command, data={}, error={"code": code, "message": message})


@dataclass
class SchemaRequest:
    """Database schema inspection request"""
    db_path: str


@dataclass
class QueryRequest:
    """Read-only query execution request"""
    db_path: str
    sql: str
    limit: int = 20


@dataclass
class GenerateRequest:
    """SQL generation request with structured parameters"""
    db_path: str
    skill_id: str
    table: str
    columns: str = "*"
    where: str = ""
    order: str = ""


@dataclass
class SchemaResponse:
    """Schema response structure"""
    tables: List[Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tables": [
                {
                    "name": t.name,
                    "columns": [c.name for c in t.columns],
                    "is_view": t.is_view,
                 }
                for t in self.tables
            ],
         }


@dataclass
class QueryResponse:
    """Query execution response"""
    row_count: int
    rows: List[Dict[str, Any]]
    truncated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row_count": self.row_count,
            "rows": self.rows,
            "truncated": self.truncated,
            "columns": list(self.rows[0].keys()) if self.rows else [],
         }


@dataclass
class GenerateResponse:
    """SQL generation response"""
    skill_id: str
    sql: str
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "sql": self.sql,
            "warnings": self.warnings,
         }

# Write Command Support (Phase 1)
from enum import Enum
from typing import List, Optional, Any

class WriteCommands(Enum):
    INSERT = 'insert'
    UPDATE = 'update'  
    DELETE = 'delete'

class WriteOperationType(Enum):
    TABLE_INSERT = 'table_insert'
    TABLE_UPDATE = 'table_update'  
    TABLE_DELETE = 'table_delete'
    
class WriteSafetyLevel(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

class WriteQueryParams:
    def __init__(self, command, table, columns=None, values=None, set_clauses=None, where_clauses=None, parameters=None, safety_level='low', require_explicit_flag=True):
        self.command = command
        self.table = table
        self.columns = columns
        self.values = values
        self.set_clauses = set_clauses
        self.where_clauses = where_clauses
        self.parameters = parameters
        self.safety_level = safety_level
        self.require_explicit_flag = require_explicit_flag

    def to_sql(self):
        if self.command == 'insert':
            return self._build_insert()
        elif self.command == 'update':
            return self._build_update()
        elif self.command == 'delete':
            return self._build_delete()
        return ""

    def _build_insert(self):
        if not self.columns or not self.values:
            raise ValueError("INSERT requires columns and values")
        cols = ', '.join(self.columns)
        placeholders = ', '.join(['?' for _ in self.values])
        return f"INSERT INTO {self.table} ({cols}) VALUES ({placeholders})"

    def _build_update(self):
        if not self.set_clauses:
            raise ValueError("UPDATE requires SET clauses")
        set_clause = ', '.join(self.set_clauses)
        return f"UPDATE {self.table} SET {set_clause}"

    def _build_delete(self):
        return f"DELETE FROM {self.table}"

class WriteQueryResult:
    def __init__(self, ok, command, affected_rows=0, safety_level=None, warnings=None, error=None):
        self.ok = ok
        self.command = command
        self.affected_rows = affected_rows
        self.safety_level = safety_level
        self.warnings = warnings or []
        self.error = error

    def to_dict(self):
        return {
            'ok': self.ok,
            'command': self.command,
            'affected_rows': self.affected_rows,
            'safety_level': self.safety_level if self.safety_level else None,
            'warnings': self.warnings,
            'error': self.error
        }


# Natural Language Query Support (Phase 2)
from enum import Enum
from typing import List, Optional, Any, Dict

class IntentType(Enum):
    SELECT = 'select'
    COUNT = 'count'
    INSERT = 'insert'
    UPDATE = 'update'
    DELETE = 'delete'
    EXPLAIN = 'explain'
    SCHEMA = 'schema'
    
class EntityPattern(Enum):
    TABLE = 'table'
    COLUMN = 'column'
    FILTER = 'filter'
    AGGREGATE = 'aggregate'

class NLQuery:
    def __init__(self, text, language="en"):
        self.text = text
        self.language = language
        self.intent = None
        self.entities = []
        self.constraints = {}
        self.confidence = 0.0
        
    def parse_intent(self):
        text_lower = self.text.lower().strip()
        if any(w in text_lower for w in ['count', 'total', 'how many']):
            self.intent = IntentType.COUNT
        elif 'select' in text_lower or 'find' in text_lower or 'show' in text_lower:
            self.intent = IntentType.SELECT
        elif 'insert' in text_lower or 'add' in text_lower:
            self.intent = IntentType.INSERT
        elif 'update' in text_lower or 'modify' in text_lower:
            self.intent = IntentType.UPDATE
        elif 'delete' in text_lower or 'remove' in text_lower:
            self.intent = IntentType.DELETE
        else:
            self.intent = IntentType.EXPLAIN
        return self.intent
        
    def extract_entities(self):
        entities = []
        text_lower = self.text.lower()
        known_tables = ['users', 'orders', 'products', 'customers', 'items']
        for table in known_tables:
            if table in text_lower:
                entities.append({'type': 'table', 'name': table, 'confidence': 0.8})
        known_cols = {
            'users': ['id', 'name', 'email', 'age'],
            'orders': ['id', 'user_id', 'total', 'date'],
            'products': ['id', 'name', 'price', 'quantity']
        }
        for table, cols in known_cols.items():
            for col in cols:
                if col in text_lower:
                    entities.append({'type': 'column', 'name': col, 'table': table, 'confidence': 0.7})
        self.entities = entities
        return entities
        
    def to_dict(self):
        return {
            'text': self.text,
            'intent': self.intent.value if self.intent else None,
            'entities': self.entities,
            'constraints': self.constraints,
            'confidence': self.confidence
        }


# WriteCommand Support (Phase 3)
from enum import Enum
from typing import List, Optional, Any

class WriteCommands(Enum):
     INSERT = "insert"
     UPDATE = "update"
     DELETE = "delete"

class WriteQueryParams:
     def __init__(self, command, table):
          self.command = command
          self.table = table
          self.columns = []
          self.values = []
          self.where = None
          
     def to_sql(self):
          return f"SQL for {self.table}"
          
class WriteQueryResult:
     def __init__(self, ok, command: str, affected_rows: int = 0):
          self.ok = ok
          self.command = command
          self.affected_rows = affected_rows
          self.error: Optional[str] = None
