#!/usr/bin/env python3
"""Lightweight database wrapper used by the CLI handlers."""

from __future__ import annotations

import sqlite3
from typing import Any, Optional


class CoQueryDB:
    """SQLite-first DB wrapper with simple URI detection."""

    def __init__(self, db_uri: str, db_type: Optional[str] = None):
        self.uri = db_uri
        self.type = db_type or self._detect_type(db_uri)
        self.conn: Optional[sqlite3.Connection] = None
        self.connect()

    def _detect_type(self, db_uri: str) -> str:
        if db_uri.startswith(("postgresql://", "postgres://")):
            return "postgresql"
        if db_uri.startswith("mysql://"):
            return "mysql"
        return "sqlite"

    def _sqlite_path(self) -> str:
        if self.uri.startswith("sqlite://"):
            return self.uri.replace("sqlite://", "", 1)
        return self.uri

    def connect_sqlite(self) -> bool:
        try:
            self.conn = sqlite3.connect(self._sqlite_path())
            return True
        except sqlite3.Error:
            self.conn = None
            return False

    def connect_postgresql(self) -> bool:
        raise NotImplementedError("PostgreSQL support is not implemented yet")

    def connect_mysql(self) -> bool:
        raise NotImplementedError("MySQL support is not implemented yet")

    def connect(self) -> bool:
        if self.conn:
            return True
        if self.type == "sqlite":
            return self.connect_sqlite()
        if self.type == "postgresql":
            return self.connect_postgresql()
        if self.type == "mysql":
            return self.connect_mysql()
        raise ValueError(f"Unsupported database type: {self.type}")

    def execute(self, sql: str, params: Optional[list[Any]] = None) -> Any:
        if not self.connect():
            raise RuntimeError("Database connection failed")

        cursor = self.conn.execute(sql, params or [])
        if sql.strip().upper().startswith("SELECT"):
            return cursor.fetchall()

        self.conn.commit()
        return cursor.rowcount

    def get_schemas(self) -> list[str]:
        if not self.connect():
            raise RuntimeError("Database connection failed")

        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in cursor.fetchall()]

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self) -> "CoQueryDB":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"CoQueryDB(type={self.type}, uri={self.uri!r})"
