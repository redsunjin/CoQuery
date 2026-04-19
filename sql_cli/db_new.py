#!/usr/bin/env python3
"""Lightweight database wrapper used by the CLI handlers."""

from __future__ import annotations

import importlib
import sqlite3
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlunparse
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

    def __init__(self, code: str, message: str, data: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data or {}


class CoQueryDB:
    """SQLite-first DB wrapper with simple URI detection."""

    def __init__(self, db_uri: str, db_type: Optional[str] = None, connect_now: bool = True):
        self.uri = self._normalize_db_uri(db_uri)
        self.type = self._detect_type(self.uri, db_type)
        self.conn: Optional[Any] = None
        if connect_now:
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

    def _display_uri(self) -> str:
        if self.type == "sqlite":
            return self.uri

        parsed = urlparse(self.uri)
        auth = ""
        if parsed.username:
            auth = parsed.username
            if parsed.password is not None:
                auth += ":***"
            auth += "@"

        host = parsed.hostname or ""
        port = f":{parsed.port}" if parsed.port else ""
        netloc = f"{auth}{host}{port}"
        return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    def _postgresql_target_details(self) -> dict[str, Any]:
        parsed = urlparse(self.uri)
        query = parse_qs(parsed.query)
        explicit_port = parsed.port
        return {
            "host": parsed.hostname,
            "port": explicit_port,
            "resolved_port": explicit_port or 5432,
            "port_source": "explicit" if explicit_port else "default",
            "database": parsed.path.lstrip("/"),
            "username": parsed.username,
            "has_password": parsed.password is not None,
            "sslmode": query.get("sslmode", [None])[-1],
            "connect_timeout": query.get("connect_timeout", [None])[-1],
        }

    def _doctor_readiness(self, driver_available: bool) -> dict[str, bool]:
        return {
            "target_parsed": True,
            "driver_available": driver_available,
            "connection_ok": False,
            "schema_probe_ok": False,
        }

    def _classify_postgresql_connect_error(self, exc: Exception) -> tuple[str, str, Optional[str]]:
        raw_error = str(exc).strip()
        normalized = raw_error.lower()

        if isinstance(exc, TimeoutError) or any(
            marker in normalized
            for marker in ("timeout expired", "timed out", "operation timed out")
        ):
            return (
                "timeout",
                "PostgreSQL connection attempt timed out.",
                "Check host, port, firewall rules, and any connect_timeout setting.",
            )

        if any(
            marker in normalized
            for marker in (
                "could not translate host name",
                "name or service not known",
                "temporary failure in name resolution",
                "nodename nor servname provided",
                "failed to resolve host",
                "no route to host",
                "network is unreachable",
            )
        ):
            return (
                "host_unreachable",
                "PostgreSQL host could not be reached.",
                "Check the hostname, DNS resolution, and network path to the server.",
            )

        if "connection refused" in normalized:
            return (
                "connection_refused",
                "PostgreSQL server refused the connection.",
                "Check whether PostgreSQL is running and listening on the requested host and port.",
            )

        if any(
            marker in normalized
            for marker in (
                "password authentication failed",
                "authentication failed",
                "no password supplied",
                "pg_hba.conf",
            )
        ) or ("role " in normalized and " does not exist" in normalized):
            return (
                "auth_failed",
                "PostgreSQL authentication failed.",
                "Check the username, password, and pg_hba.conf access rules.",
            )

        if "database " in normalized and " does not exist" in normalized:
            return (
                "database_not_found",
                "PostgreSQL database does not exist.",
                "Check the database name in the connection URI.",
            )

        if "ssl" in normalized or "certificate verify failed" in normalized:
            return (
                "ssl_error",
                "PostgreSQL SSL negotiation failed.",
                "Check sslmode and the server/client certificate configuration.",
            )

        return (
            "connection_failed",
            "Failed to connect to the PostgreSQL database.",
            "Inspect the underlying driver error for more detail.",
        )

    def _postgresql_connect_error_data(self, exc: Exception, hint: Optional[str]) -> dict[str, Any]:
        data = {
            "backend": "postgresql",
            "normalized_target": self._display_uri(),
            "connection_target": self._postgresql_target_details(),
            "driver": self._driver_details(),
            "raw_error": str(exc),
            "raw_error_type": type(exc).__name__,
        }
        if hint:
            data["hint"] = hint
        return data

    def _driver_details(self) -> dict[str, Any]:
        if self.type == "sqlite":
            return {
                "module": "sqlite3",
                "available": True,
                "install_hint": None,
            }

        if self.type == "postgresql":
            try:
                importlib.import_module("psycopg")
                return {
                    "module": "psycopg",
                    "available": True,
                    "install_hint": "Install psycopg[binary] for postgresql:// URIs.",
                }
            except ModuleNotFoundError:
                return {
                    "module": "psycopg",
                    "available": False,
                    "install_hint": "Install psycopg[binary] for postgresql:// URIs.",
                }

        return {
            "module": None,
            "available": False,
            "install_hint": "MySQL is still a stub in the current baseline.",
        }

    def describe_target(self) -> dict[str, Any]:
        details: dict[str, Any] = {
            "backend": self.type,
            "target_kind": "db_uri" if "://" in self.uri else "legacy_path",
            "normalized_target": self._display_uri(),
            "driver": self._driver_details(),
        }

        if self.type == "sqlite":
            db_path = Path(self._sqlite_path()).expanduser()
            details["path"] = {
                "value": self._sqlite_path(),
                "absolute": str(db_path.resolve()),
                "exists": db_path.exists(),
            }
            return details

        parsed = urlparse(self.uri)
        details["connection_target"] = self._postgresql_target_details()
        return details

    def doctor(self) -> dict[str, Any]:
        report = self.describe_target()
        report["ready"] = False
        report["readiness"] = self._doctor_readiness(report["driver"]["available"])

        if self.type == "sqlite" and not report["path"]["exists"]:
            report["connection"] = {
                "ok": False,
                "code": "database_not_found",
                "message": "SQLite database file does not exist.",
            }
            return report

        if self.type == "postgresql" and not report["driver"]["available"]:
            report["connection"] = {
                "ok": False,
                "code": "driver_not_installed",
                "message": "PostgreSQL support requires psycopg[binary]. Install it before using postgresql:// URIs.",
            }
            return report

        if self.type == "mysql":
            report["connection"] = {
                "ok": False,
                "code": "unsupported_backend",
                "message": "MySQL support is not implemented yet.",
            }
            return report

        try:
            self.connect()
            tables = self.get_schemas()
            report["schemas"] = {
                "table_count": len(tables),
                "tables_preview": tables[:10],
            }
            report["connection"] = {
                "ok": True,
                "code": None,
                "message": "Connection successful.",
            }
            report["readiness"]["connection_ok"] = True
            report["readiness"]["schema_probe_ok"] = True
            report["ready"] = True
            return report
        except CoQueryDBError as exc:
            report["connection"] = {
                "ok": False,
                "code": exc.code,
                "message": exc.message,
            }
            if exc.data.get("raw_error"):
                report["connection"]["raw_error"] = exc.data["raw_error"]
            if exc.data.get("raw_error_type"):
                report["connection"]["raw_error_type"] = exc.data["raw_error_type"]
            if exc.data.get("hint"):
                report["connection"]["hint"] = exc.data["hint"]
            if exc.data.get("connection_target"):
                report["connection_target"] = exc.data["connection_target"]
            if exc.data.get("driver"):
                report["driver"] = exc.data["driver"]
            return report
        finally:
            self.close()

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
            code, message, hint = self._classify_postgresql_connect_error(exc)
            raise CoQueryDBError(
                code,
                message,
                self._postgresql_connect_error_data(exc, hint),
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

    def execute(
        self,
        sql: str,
        params: Optional[list[Any]] = None,
        dry_run: bool = False,
        max_affected_rows: Optional[int] = None,
    ) -> Any:
        if not self.connect():
            raise CoQueryDBError("connection_failed", "Database connection failed")

        is_select = sql.strip().upper().startswith("SELECT")
        try:
            cursor = self.conn.execute(sql, params or [])
            if is_select:
                return cursor.fetchall()

            rowcount = cursor.rowcount
            if max_affected_rows is not None and rowcount > max_affected_rows:
                self.conn.rollback()
                raise CoQueryDBError(
                    "affected_rows_exceeded",
                    f"Write affected {rowcount} rows, which exceeds the allowed limit of {max_affected_rows}.",
                    {
                        "affected_rows": rowcount,
                        "max_affected_rows": max_affected_rows,
                    },
                )
            if dry_run:
                self.conn.rollback()
            else:
                self.conn.commit()
            return rowcount
        except Exception:
            if not is_select and self.conn is not None:
                try:
                    self.conn.rollback()
                except Exception:
                    pass
            raise

    def _quote_sqlite_identifier(self, identifier: str) -> str:
        return '"' + identifier.replace('"', '""') + '"'

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

    def get_schema_detail(self, table: Optional[str] = None) -> dict[str, Any]:
        if not self.connect():
            raise CoQueryDBError("connection_failed", "Database connection failed")

        if self.type == "sqlite":
            return self._get_sqlite_schema_detail(table)
        if self.type == "postgresql":
            return self._get_postgresql_schema_detail(table)

        raise CoQueryDBError(
            "unsupported_backend",
            f"{BACKEND_LABELS[self.type]} schema detail inspection is not implemented yet.",
        )

    def _sqlite_table_names(self, table: Optional[str]) -> list[str]:
        tables = self.get_schemas()
        if not table:
            return tables
        if table not in tables:
            raise CoQueryDBError("table_not_found", f"Table not found: {table}.")
        return [table]

    def _get_sqlite_create_sql(self, table: str) -> Optional[str]:
        cursor = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            [table],
        )
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]

    def _get_sqlite_table_detail(self, table: str) -> dict[str, Any]:
        quoted_table = self._quote_sqlite_identifier(table)
        columns = [
            {
                "name": row[1],
                "type": row[2],
                "nullable": not bool(row[3]) and not bool(row[5]),
                "default": row[4],
                "primary_key": bool(row[5]),
                "primary_key_position": int(row[5] or 0),
                "position": int(row[0]) + 1,
            }
            for row in self.conn.execute(f"PRAGMA table_info({quoted_table})").fetchall()
        ]

        foreign_keys = [
            {
                "id": row[0],
                "seq": row[1],
                "referenced_table": row[2],
                "column": row[3],
                "referenced_column": row[4],
                "on_update": row[5],
                "on_delete": row[6],
                "match": row[7],
            }
            for row in self.conn.execute(f"PRAGMA foreign_key_list({quoted_table})").fetchall()
        ]

        indexes = []
        for row in self.conn.execute(f"PRAGMA index_list({quoted_table})").fetchall():
            index_name = row[1]
            quoted_index = self._quote_sqlite_identifier(index_name)
            indexes.append(
                {
                    "name": index_name,
                    "unique": bool(row[2]),
                    "origin": row[3] if len(row) > 3 else None,
                    "partial": bool(row[4]) if len(row) > 4 else False,
                    "columns": [
                        column_row[2]
                        for column_row in self.conn.execute(f"PRAGMA index_info({quoted_index})").fetchall()
                    ],
                }
            )

        primary_key = [
            column["name"]
            for column in sorted(columns, key=lambda item: item["primary_key_position"])
            if column["primary_key"]
        ]
        not_null = [column["name"] for column in columns if not column["nullable"]]
        unique_indexes = [index for index in indexes if index["unique"]]

        return {
            "name": table,
            "columns": columns,
            "primary_key": primary_key,
            "foreign_keys": foreign_keys,
            "indexes": indexes,
            "constraints": {
                "primary_key": primary_key,
                "not_null": not_null,
                "foreign_keys": foreign_keys,
                "unique_indexes": unique_indexes,
            },
            "create_sql": self._get_sqlite_create_sql(table),
        }

    def _get_sqlite_schema_detail(self, table: Optional[str] = None) -> dict[str, Any]:
        tables = [self._get_sqlite_table_detail(table_name) for table_name in self._sqlite_table_names(table)]
        return {
            "backend": "sqlite",
            "table_count": len(tables),
            "tables": tables,
        }

    def _postgresql_table_names(self, table: Optional[str]) -> list[str]:
        if table:
            return [table]
        return self.get_schemas()

    def _postgresql_columns(self, table: str) -> list[dict[str, Any]]:
        query = (
            "SELECT column_name, data_type, is_nullable, column_default, ordinal_position "
            "FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = %s "
            "ORDER BY ordinal_position"
        )
        return [
            {
                "name": row[0],
                "type": row[1],
                "nullable": row[2] == "YES",
                "default": row[3],
                "primary_key": False,
                "position": int(row[4]),
            }
            for row in self.conn.execute(query, [table]).fetchall()
        ]

    def _postgresql_constraints(self, table: str) -> list[dict[str, Any]]:
        query = (
            "SELECT tc.constraint_name, tc.constraint_type, kcu.column_name, "
            "ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name "
            "FROM information_schema.table_constraints tc "
            "LEFT JOIN information_schema.key_column_usage kcu "
            "ON tc.constraint_name = kcu.constraint_name "
            "AND tc.table_schema = kcu.table_schema "
            "AND tc.table_name = kcu.table_name "
            "LEFT JOIN information_schema.constraint_column_usage ccu "
            "ON tc.constraint_name = ccu.constraint_name "
            "AND tc.table_schema = ccu.table_schema "
            "WHERE tc.table_schema = 'public' AND tc.table_name = %s "
            "ORDER BY tc.constraint_name, kcu.ordinal_position"
        )
        grouped: dict[str, dict[str, Any]] = {}
        for row in self.conn.execute(query, [table]).fetchall():
            name = row[0]
            constraint = grouped.setdefault(
                name,
                {
                    "name": name,
                    "type": row[1],
                    "columns": [],
                    "referenced_table": row[3],
                    "referenced_columns": [],
                },
            )
            if row[2] and row[2] not in constraint["columns"]:
                constraint["columns"].append(row[2])
            if row[4] and row[4] not in constraint["referenced_columns"]:
                constraint["referenced_columns"].append(row[4])
        return list(grouped.values())

    def _postgresql_indexes(self, table: str) -> list[dict[str, Any]]:
        query = (
            "SELECT i.relname AS index_name, ix.indisunique, ix.indisprimary, "
            "ARRAY( "
            "SELECT a.attname "
            "FROM unnest(ix.indkey) WITH ORDINALITY AS k(attnum, ord) "
            "JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum "
            "ORDER BY k.ord "
            ") AS columns "
            "FROM pg_class t "
            "JOIN pg_index ix ON t.oid = ix.indrelid "
            "JOIN pg_class i ON i.oid = ix.indexrelid "
            "JOIN pg_namespace n ON n.oid = t.relnamespace "
            "WHERE n.nspname = 'public' AND t.relname = %s "
            "ORDER BY i.relname"
        )
        indexes = []
        for row in self.conn.execute(query, [table]).fetchall():
            columns = row[3]
            if not isinstance(columns, list):
                columns = list(columns or [])
            indexes.append(
                {
                    "name": row[0],
                    "unique": bool(row[1]),
                    "primary": bool(row[2]),
                    "columns": columns,
                }
            )
        return indexes

    def _get_postgresql_table_detail(self, table: str) -> dict[str, Any]:
        columns = self._postgresql_columns(table)
        if not columns:
            raise CoQueryDBError("table_not_found", f"Table not found: {table}.")

        constraints = self._postgresql_constraints(table)
        primary_key = []
        foreign_keys = []
        unique_constraints = []
        for constraint in constraints:
            if constraint["type"] == "PRIMARY KEY":
                primary_key.extend(constraint["columns"])
            elif constraint["type"] == "FOREIGN KEY":
                foreign_keys.append(constraint)
            elif constraint["type"] == "UNIQUE":
                unique_constraints.append(constraint)

        for column in columns:
            column["primary_key"] = column["name"] in primary_key

        return {
            "name": table,
            "columns": columns,
            "primary_key": primary_key,
            "foreign_keys": foreign_keys,
            "indexes": self._postgresql_indexes(table),
            "constraints": {
                "primary_key": primary_key,
                "not_null": [column["name"] for column in columns if not column["nullable"]],
                "foreign_keys": foreign_keys,
                "unique_constraints": unique_constraints,
                "all": constraints,
            },
        }

    def _get_postgresql_schema_detail(self, table: Optional[str] = None) -> dict[str, Any]:
        tables = [self._get_postgresql_table_detail(table_name) for table_name in self._postgresql_table_names(table)]
        return {
            "backend": "postgresql",
            "table_count": len(tables),
            "tables": tables,
        }

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
