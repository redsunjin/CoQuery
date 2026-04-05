#!/usr/bin/env python3
"""Lightweight database wrapper used by the CLI handlers."""

from __future__ import annotations

import importlib
import sqlite3
from urllib.parse import urlparse
from typing import Any, Optional


SUPPORTED_BACKENDS = {"sqlite", "postgresql", "mysql"}
BACKEND_ALIASES = {"postgres": "postgresql"}
BACKEND_LABELS = {
    "sqlite": "SQLite",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
}


class CoQueryDBError(Exception):
    """Structured DB/runtime error used by CLI handlers."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class CoQueryDB:
    """SQLite-first DB wrapper with simple URI detection."""

    def __init__(self, db_uri: str, db_type: Optional[str] = None):
        self.uri = self._normalize_db_uri(db_uri)
        self.type = self._detect_type(self.uri, db_type)
        self.conn: Optional[Any] = None
        self.connect()

    def _normalize_db_uri(self, db_uri: str) -> str:
        if db_uri is None:
            raise CoQueryDBError("missing_db_uri", "Database URI is required.")

        normalized = db_uri.strip()
        if not normalized:
            raise CoQueryDBError("missing_db_uri", "Database URI is required.")
        return normalized

    def _detect_type(self, db_uri: str, db_type: Optional[str] = None) -> str:
        if "://" not in db_uri:
            if db_type and db_type != "sqlite":
                raise CoQueryDBError(
                    "invalid_db_uri",
                    "Legacy --db paths support SQLite only. Use --db-uri for non-SQLite backends.",
                )
            return "sqlite"

        parsed = urlparse(db_uri)
        scheme = BACKEND_ALIASES.get(parsed.scheme.lower(), parsed.scheme.lower())
        if scheme not in SUPPORTED_BACKENDS:
            raise CoQueryDBError(
                "unsupported_backend",
                f"Unsupported database backend: {parsed.scheme}.",
            )

        self._validate_uri(scheme, db_uri, parsed)

        if db_type and db_type != scheme:
            raise CoQueryDBError(
                "invalid_db_uri",
                f"Database URI scheme does not match requested backend: {db_type}.",
            )

        return scheme

    def _validate_uri(self, backend: str, db_uri: str, parsed: Any) -> None:
        if backend == "sqlite":
            sqlite_location = db_uri.replace("sqlite://", "", 1)
            if not sqlite_location or sqlite_location == "/":
                raise CoQueryDBError(
                    "invalid_db_uri",
                    "SQLite URI must include a database path.",
                )
            return

        label = BACKEND_LABELS[backend]
        if not parsed.netloc:
            raise CoQueryDBError(
                "invalid_db_uri",
                f"{label} URI must include host information.",
            )
        if not parsed.path or parsed.path == "/":
            raise CoQueryDBError(
                "invalid_db_uri",
                f"{label} URI must include a database name.",
            )

    def _sqlite_path(self) -> str:
        if self.uri.startswith("sqlite://"):
            return self.uri.replace("sqlite://", "", 1)
        return self.uri

    def connect_sqlite(self) -> bool:
        try:
            self.conn = sqlite3.connect(self._sqlite_path())
            return True
        except sqlite3.Error as exc:
            self.conn = None
            raise CoQueryDBError(
                "connection_failed",
                "Failed to connect to the SQLite database.",
            ) from exc

    def connect_postgresql(self) -> bool:
        try:
            psycopg = importlib.import_module("psycopg")
        except ModuleNotFoundError as exc:
            raise CoQueryDBError(
                "driver_not_installed",
                "PostgreSQL support requires psycopg[binary]. Install it before using postgresql:// URIs.",
            ) from exc

        try:
            self.conn = psycopg.connect(self.uri)
            return True
        except Exception as exc:
            self.conn = None
            raise CoQueryDBError(
                "connection_failed",
                "Failed to connect to the PostgreSQL database.",
            ) from exc

    def connect_mysql(self) -> bool:
        raise CoQueryDBError(
            "unsupported_backend",
            "MySQL support is not implemented yet.",
        )

    def connect(self) -> bool:
        if self.conn:
            return True
        if self.type == "sqlite":
            return self.connect_sqlite()
        if self.type == "postgresql":
            return self.connect_postgresql()
        if self.type == "mysql":
            return self.connect_mysql()
        raise CoQueryDBError(
            "unsupported_backend",
            f"Unsupported database backend: {self.type}.",
        )

    def execute(self, sql: str, params: Optional[list[Any]] = None) -> Any:
        if not self.connect():
            raise CoQueryDBError("connection_failed", "Database connection failed")

        cursor = self.conn.execute(sql, params or [])
        if sql.strip().upper().startswith("SELECT"):
            return cursor.fetchall()

        self.conn.commit()
        return cursor.rowcount

    def get_schemas(self) -> list[str]:
        if not self.connect():
            raise CoQueryDBError("connection_failed", "Database connection failed")

        if self.type == "sqlite":
            query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        elif self.type == "postgresql":
            query = (
                "SELECT table_name "
                "FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
                "ORDER BY table_name"
            )
        else:
            raise CoQueryDBError(
                "unsupported_backend",
                f"{BACKEND_LABELS[self.type]} schema inspection is not implemented yet.",
            )

        cursor = self.conn.execute(query)
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
