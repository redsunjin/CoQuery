#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db.py - SQLite database access module
SQL Developer(SQLD) → SQL Professional(SQLP)
"""

import sqlite3
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class TableColumn:
    """테이블 컬럼 정보"""
    cid: int
    name: str
    type: str
    notnull: int
    dflt_value: Optional[str]
    pk: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cid": self.cid,
            "name": self.name,
            "type": self.type,
            "notnull": self.notnull != 0,
            "dflt_value": self.dflt_value,
            "pk": self.pk != 0,
        }


@dataclass
class TableSchema:
    """테이블 스키마 정보"""
    name: str
    columns: List[TableColumn]
    is_view: bool

    def to_dict(self) -> Dict[str, Any]:
        columns_list = [col.to_dict() for col in self.columns]
        return {
            "name": self.name,
            "columns": columns_list,
            "is_view": self.is_view,
            "column_names": [col.name for col in self.columns],
        }


class DBClient:
    """SQLite 데이터베이스 클라이언트"""

    def __init__(self, db_path: str):
        """
        Initialize database client
        Args:
            db_path: SQLite database file path
        """
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        """
        Connect to database
        Returns:
            sqlite3.Connection object
        """
        return sqlite3.connect(self.db_path)

    def get_tables(self) -> List[TableSchema]:
        """
        Get all table schemas (read-only)
        
        Acceptance Criteria:
        - No interactive prompts
        - Returns stable table list
        - Supports both tables and views
        
        Returns:
            List of TableSchema objects
        Raises:
            sqlite3.Error on connection failure
        """
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, sql FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY name"
            )
            tables = []
            for row in cursor.fetchall():
                name, sql = row
                is_view = sql is not None and "CREATE VIEW" in sql.upper()
                
                cursor.execute(f"PRAGMA table_info({name})")
                columns = [
                    TableColumn(
                        cid=row[0],
                        name=row[1],
                        type=row[2],
                        notnull=row[3],
                        dflt_value=row[4],
                        pk=row[5],
                    )
                    for row in cursor.fetchall()
                ]
                
                tables.append(TableSchema(name=name, columns=columns, is_view=is_view))
            
            return tables
        finally:
            conn.close()

    def execute_query(self, sql: str, limit: int = 20) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Execute SELECT query safely
        
        Acceptance Criteria:
        - Accept only SELECT statements
        - Enforce row limit
        - Return (row_count, rows_dict_list)
        - No write operations allowed
        
        Args:
            sql: SQL query (SELECT only)
            limit: Max rows to return
            
        Returns:
            Tuple of (row_count, [row_dicts])
        Raises:
            sqlite3.Error on execution failure
        """
        if not sql.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT statements allowed")
        
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            results = []
            for row in rows[:limit]:
                row_dict = {col: row[i] for i, col in enumerate(columns)}
                results.append(row_dict)
            
            return (len(rows), results)
        finally:
            conn.close()

    def close(self):
        """Close database connection"""
        pass  # Connection auto-closed in methods
