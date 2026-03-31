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
