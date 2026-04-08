#!/usr/bin/env python3
"""Small executable baseline tests for CoQuery."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from shutil import copy2
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sql_cli.cli import (
    delete_handler,
    generate_handler,
    insert_handler,
    natural_handler,
    provider_add_handler,
    provider_list_handler,
    provider_remove_handler,
    provider_test_handler,
    query_handler,
    schema_handler,
    update_handler,
)
from sql_cli.core import SQLGenerator, SQLValidator
from sql_cli.db_new import CoQueryDB
from sql_cli.nl_core import NaturalLanguageEngine

ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURE_DB = ROOT_DIR / "example.db"


def make_temp_db() -> tuple[TemporaryDirectory[str], Path]:
    tmpdir = TemporaryDirectory()
    db_path = Path(tmpdir.name) / "write-test.db"
    copy2(FIXTURE_DB, db_path)
    return tmpdir, db_path


def seed_user(db_path: Path, name: str = "seed_user", age: int = 30) -> int:
    db = CoQueryDB(str(db_path))
    db.execute("INSERT INTO users (name, age) VALUES (?, ?)", [name, age])
    row_id = db.execute("SELECT id FROM users WHERE name = ? ORDER BY id DESC LIMIT 1", [name])[0][0]
    db.close()
    return row_id


def run_cli(args: list[str]) -> tuple[int, dict[str, object]]:
    result = subprocess.run(
        ["python3", "main.py", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    return result.returncode, payload


print("=== CoQuery Tests ===")

gen = SQLGenerator()
result = gen.generate("select_simple", {})
assert result["sql"] == "SELECT * FROM USERS"
print("1. test_select_simple ✓")

result = gen.generate("count_simple", {"table": "users"})
assert result["sql"] == "SELECT COUNT(*) FROM USERS"
print("2. test_count_simple ✓")

val = SQLValidator()
errors = val.validate("SELECT * FROM users")
assert errors == []
print("3. test_select_valid ✓")

errors = val.validate("INSERT INTO users VALUES (1, 'test')")
assert errors == []
print("4. test_insert_valid ✓")

db = CoQueryDB("example.db")
assert db.conn is not None
db.close()
print("5. test_db_connect ✓")

db = CoQueryDB("example.db")
rows = db.execute("SELECT * FROM users")
assert isinstance(rows, list)
db.close()
print("6. test_db_execute ✓")

db = CoQueryDB("example.db")
tables = db.get_schemas()
assert "users" in tables
db.close()
print("7. test_db_schemas ✓")

result = schema_handler("example.db")
assert result["ok"] is True
assert "users" in result["data"]["tables"]
print("8. test_schema_command ✓")

result = query_handler("example.db", "SELECT COUNT(*) FROM users")
assert result["ok"] is True
assert len(result["data"]["rows"]) == 1
print("9. test_query_command ✓")

result = generate_handler("example.db", "select_simple")
assert result["ok"] is True
assert result["sql"] == "SELECT * FROM USERS"
print("10. test_generate_command ✓")

nl_result = NaturalLanguageEngine().process("show users")
assert nl_result["ok"] is True
assert nl_result["intent"] == "select"
print("11. test_natural_language ✓")

tmpdir, db_path = make_temp_db()
insert_result = insert_handler(
    str(db_path),
    "INSERT INTO users (name, age) VALUES (?, ?)",
    ["write_test_user", 41],
    write=True,
)
assert insert_result["ok"] is True
assert insert_result["data"]["affected_rows"] == 1
assert insert_result["data"]["warnings"] == []
assert insert_result["data"]["safety_level"] == "low"
db = CoQueryDB(str(db_path))
rows = db.execute("SELECT name, age FROM users WHERE name = 'write_test_user'")
assert rows == [("write_test_user", 41)]
db.close()
tmpdir.cleanup()
print("12. test_insert_command_write_contract ✓")

tmpdir, db_path = make_temp_db()
first_id = seed_user(db_path, name="update_target", age=31)
update_result = update_handler(
    str(db_path),
    "UPDATE users SET age = ? WHERE id = ?",
    [77, first_id],
    write=True,
)
assert update_result["ok"] is True
assert update_result["data"]["affected_rows"] == 1
assert update_result["data"]["warnings"] == []
assert update_result["data"]["safety_level"] == "low"
db = CoQueryDB(str(db_path))
rows = db.execute(f"SELECT age FROM users WHERE id = {first_id}")
assert rows == [(77,)]
db.close()
tmpdir.cleanup()
print("13. test_update_command_write_contract ✓")

tmpdir, db_path = make_temp_db()
seed_user(db_path, name="delete_me", age=29)
delete_result = delete_handler(
    str(db_path),
    "DELETE FROM users WHERE name = 'delete_me'",
    write=True,
)
assert delete_result["ok"] is True
assert delete_result["data"]["affected_rows"] == 1
assert delete_result["data"]["warnings"] == []
assert delete_result["data"]["safety_level"] == "low"
db = CoQueryDB(str(db_path))
rows = db.execute("SELECT COUNT(*) FROM users WHERE name = 'delete_me'")
assert rows == [(0,)]
db.close()
tmpdir.cleanup()
print("14. test_delete_command_write_contract ✓")

tmpdir, db_path = make_temp_db()
missing_write_result = delete_handler(
    str(db_path),
    "DELETE FROM users WHERE id = 1",
)
assert missing_write_result["ok"] is False
assert missing_write_result["error"]["code"] == "write_flag_required"
tmpdir.cleanup()
print("15. test_write_flag_required ✓")

tmpdir, db_path = make_temp_db()
seed_user(db_path, name="bulk_target", age=33)
full_table_update = update_handler(
    str(db_path),
    "UPDATE users SET age = age + 1",
    write=True,
)
assert full_table_update["ok"] is True
assert full_table_update["data"]["affected_rows"] == 1
assert full_table_update["data"]["safety_level"] == "high"
assert "WHERE" in full_table_update["data"]["warnings"][0]
tmpdir.cleanup()
print("16. test_full_table_warning ✓")

tmpdir, db_path = make_temp_db()
query_write_without_flag = query_handler(
    str(db_path),
    "DELETE FROM users WHERE id = 1",
)
assert query_write_without_flag["ok"] is False
assert query_write_without_flag["error"]["code"] == "write_flag_required"
tmpdir.cleanup()
print("17. test_query_write_requires_flag ✓")

tmpdir, db_path = make_temp_db()
wrong_handler_sql = insert_handler(
    str(db_path),
    "UPDATE users SET age = 1 WHERE id = 1",
    write=True,
)
assert wrong_handler_sql["ok"] is False
assert wrong_handler_sql["error"]["code"] == "invalid_write_sql"
tmpdir.cleanup()
print("18. test_write_handler_sql_mismatch ✓")

tmpdir, db_path = make_temp_db()
sqlite_uri = f"sqlite://{db_path}"
result = subprocess.run(
    [
        "python3",
        "main.py",
        "--command",
        "schema",
        "--db-uri",
        sqlite_uri,
        "--format",
        "json",
    ],
    capture_output=True,
    text=True,
    check=False,
)
payload = json.loads(result.stdout)
assert result.returncode == 0
assert payload["ok"] is True
assert "users" in payload["data"]["tables"]
tmpdir.cleanup()
print("19. test_schema_command_db_uri ✓")

unsupported_backend = schema_handler("oracle://user:pass@localhost/db")
assert unsupported_backend["ok"] is False
assert unsupported_backend["error"]["code"] == "unsupported_backend"
print("20. test_unsupported_backend_error ✓")

invalid_postgres_uri = schema_handler("postgresql:///missing_host")
assert invalid_postgres_uri["ok"] is False
assert invalid_postgres_uri["error"]["code"] == "invalid_db_uri"
print("21. test_invalid_db_uri_error ✓")

missing_db_uri = schema_handler("")
assert missing_db_uri["ok"] is False
assert missing_db_uri["error"]["code"] == "missing_db_uri"
print("22. test_missing_db_uri_error ✓")

with patch("sql_cli.db_new.importlib.import_module", side_effect=ModuleNotFoundError("psycopg")):
    missing_driver = schema_handler("postgresql://user:pass@localhost:5432/dbname")
assert missing_driver["ok"] is False
assert missing_driver["error"]["code"] == "driver_not_installed"
print("23. test_postgresql_driver_not_installed_error ✓")


class _FakePsycopgModule:
    @staticmethod
    def connect(uri: str) -> None:
        raise RuntimeError(f"cannot connect to {uri}")


with patch("sql_cli.db_new.importlib.import_module", return_value=_FakePsycopgModule()):
    connection_failed = schema_handler("postgresql://user:pass@localhost:5432/dbname")
assert connection_failed["ok"] is False
assert connection_failed["error"]["code"] == "connection_failed"
print("24. test_postgresql_connection_failed_error ✓")

mysql_stub = schema_handler("mysql://user:pass@localhost:3306/dbname")
assert mysql_stub["ok"] is False
assert mysql_stub["error"]["code"] == "unsupported_backend"
print("25. test_mysql_stub_error ✓")


class _FakeCursor:
    def __init__(self, rows: list[tuple[object, ...]] | None = None, rowcount: int = 0):
        self._rows = rows
        self.rowcount = rowcount

    def fetchall(self) -> list[tuple[object, ...]]:
        return self._rows or []


class _FakePsycopgConnection:
    def __init__(self):
        self.last_query = ""
        self.committed = False

    def execute(self, query: str, params: object | None = None) -> _FakeCursor:
        self.last_query = query
        if "information_schema.tables" in query:
            return _FakeCursor([("users",)])
        if query.strip().upper().startswith("SELECT"):
            return _FakeCursor([("probe_user", 34)])
        return _FakeCursor(rowcount=1)

    def commit(self) -> None:
        self.committed = True

    def close(self) -> None:
        return None


class _FakePsycopgSuccessModule:
    last_connection: _FakePsycopgConnection | None = None

    @staticmethod
    def connect(uri: str) -> _FakePsycopgConnection:
        _FakePsycopgSuccessModule.last_connection = _FakePsycopgConnection()
        return _FakePsycopgSuccessModule.last_connection


with patch("sql_cli.db_new.importlib.import_module", return_value=_FakePsycopgSuccessModule()):
    postgres_schema = schema_handler("postgresql://user:pass@localhost:5432/dbname")
assert postgres_schema["ok"] is True
assert postgres_schema["data"]["tables"] == ["users"]
assert _FakePsycopgSuccessModule.last_connection is not None
assert "information_schema.tables" in _FakePsycopgSuccessModule.last_connection.last_query
print("26. test_postgresql_schema_success_path ✓")

with patch("sql_cli.db_new.importlib.import_module", return_value=_FakePsycopgSuccessModule()):
    postgres_query = query_handler(
        "postgresql://user:pass@localhost:5432/dbname",
        "SELECT name, age FROM users ORDER BY id LIMIT 5",
    )
assert postgres_query["ok"] is True
assert postgres_query["data"]["rows"] == [("probe_user", 34)]
assert _FakePsycopgSuccessModule.last_connection is not None
assert "SELECT name, age FROM users" in _FakePsycopgSuccessModule.last_connection.last_query
print("27. test_postgresql_query_success_path ✓")

with patch("sql_cli.db_new.importlib.import_module", return_value=_FakePsycopgSuccessModule()):
    postgres_insert = insert_handler(
        "postgresql://user:pass@localhost:5432/dbname",
        "INSERT INTO users (name, age) VALUES ('pg_insert_user', 35)",
        write=True,
    )
assert postgres_insert["ok"] is True
assert postgres_insert["data"]["affected_rows"] == 1
assert postgres_insert["data"]["warnings"] == []
assert postgres_insert["data"]["safety_level"] == "low"
assert _FakePsycopgSuccessModule.last_connection is not None
assert _FakePsycopgSuccessModule.last_connection.committed is True
assert "INSERT INTO users" in _FakePsycopgSuccessModule.last_connection.last_query
print("28. test_postgresql_insert_success_path ✓")

with patch("sql_cli.db_new.importlib.import_module", return_value=_FakePsycopgSuccessModule()):
    postgres_update = update_handler(
        "postgresql://user:pass@localhost:5432/dbname",
        "UPDATE users SET age = 36 WHERE name = 'pg_insert_user'",
        write=True,
    )
assert postgres_update["ok"] is True
assert postgres_update["data"]["affected_rows"] == 1
assert postgres_update["data"]["warnings"] == []
assert postgres_update["data"]["safety_level"] == "low"
assert _FakePsycopgSuccessModule.last_connection is not None
assert _FakePsycopgSuccessModule.last_connection.committed is True
assert "UPDATE users SET age = 36" in _FakePsycopgSuccessModule.last_connection.last_query
print("29. test_postgresql_update_success_path ✓")

with patch("sql_cli.db_new.importlib.import_module", return_value=_FakePsycopgSuccessModule()):
    postgres_delete = delete_handler(
        "postgresql://user:pass@localhost:5432/dbname",
        "DELETE FROM users WHERE name = 'pg_delete_user'",
        write=True,
    )
assert postgres_delete["ok"] is True
assert postgres_delete["data"]["affected_rows"] == 1
assert postgres_delete["data"]["warnings"] == []
assert postgres_delete["data"]["safety_level"] == "low"
assert _FakePsycopgSuccessModule.last_connection is not None
assert _FakePsycopgSuccessModule.last_connection.committed is True
assert "DELETE FROM users WHERE name = 'pg_delete_user'" in _FakePsycopgSuccessModule.last_connection.last_query
print("30. test_postgresql_delete_success_path ✓")

rc, payload = run_cli(["--command", "schema", "--db", "example.db", "--format", "json"])
assert rc == 0
assert payload["ok"] is True
assert "users" in payload["data"]["tables"]
print("31. test_docs_schema_example_db ✓")

sqlite_uri = f"sqlite://{FIXTURE_DB}"
rc, payload = run_cli(["--command", "schema", "--db-uri", sqlite_uri, "--format", "json"])
assert rc == 0
assert payload["ok"] is True
assert "users" in payload["data"]["tables"]
print("32. test_docs_schema_example_db_uri ✓")

rc, payload = run_cli(["--command", "generate", "--db", "example.db", "--skill", "select_simple", "--format", "json"])
assert rc == 0
assert payload["ok"] is True
assert payload["sql"] == "SELECT * FROM USERS"
print("33. test_docs_generate_example ✓")

tmpdir, db_path = make_temp_db()
rc, payload = run_cli(
    [
        "--command",
        "insert",
        "--db",
        str(db_path),
        "--write",
        "--sql",
        "INSERT INTO users (name, age) VALUES ('docs_user', 20)",
    ]
)
assert rc == 0
assert payload["ok"] is True
db = CoQueryDB(str(db_path))
rows = db.execute("SELECT name, age FROM users WHERE name = 'docs_user'")
assert rows == [("docs_user", 20)]
db.close()
tmpdir.cleanup()
print("34. test_docs_insert_example ✓")

rc, payload = run_cli(["--command", "natural", "--db", "example.db", "--sql", "show users"])
assert rc == 0
assert payload["ok"] is True
assert payload["intent"] == "select"
print("35. test_docs_natural_example ✓")


class _FakeHTTPResponse:
    def __init__(self, payload: dict[str, object]):
        self.payload = payload

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self) -> "_FakeHTTPResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def _fake_llm_urlopen(request: object, timeout: int = 60) -> _FakeHTTPResponse:
    url = request.full_url  # type: ignore[attr-defined]
    if url.endswith("/api/tags"):
        return _FakeHTTPResponse({"models": [{"name": "qwen3.5:4b-nvfp4"}]})

    payload = json.loads(request.data.decode("utf-8"))  # type: ignore[attr-defined]
    prompt = payload.get("prompt", "")
    if "Return exactly the text OK." in prompt:
        return _FakeHTTPResponse({"response": "OK"})

    return _FakeHTTPResponse(
        {
            "response": json.dumps(
                {
                    "intent": "select",
                    "sql": "SELECT * FROM users",
                    "confidence": 0.91,
                }
            )
        }
    )


with TemporaryDirectory() as tmpdir:
    registry_path = Path(tmpdir) / "llm_registry.json"
    with patch.dict(os.environ, {"COQUERY_LLM_REGISTRY_PATH": str(registry_path)}):
        ollama_provider = provider_add_handler(
            "local_ollama",
            "ollama",
            "qwen3.5:4b-nvfp4",
            "http://127.0.0.1:11434",
        )
        openai_provider = provider_add_handler(
            "remote_api",
            "openai_compatible",
            "gpt-oss-20b",
            "http://127.0.0.1:8000",
            "OPENAI_COMPAT_API_KEY",
        )
        listed = provider_list_handler()
assert ollama_provider["ok"] is True
assert openai_provider["ok"] is True
assert listed["ok"] is True
assert [provider["name"] for provider in listed["data"]["providers"]] == ["local_ollama", "remote_api"]
print("36. test_provider_registry_add_and_list ✓")

with TemporaryDirectory() as tmpdir:
    registry_path = Path(tmpdir) / "llm_registry.json"
    with patch.dict(os.environ, {"COQUERY_LLM_REGISTRY_PATH": str(registry_path)}):
        provider_add_handler("local_ollama", "ollama", "qwen3.5:4b-nvfp4", "http://127.0.0.1:11434")
        removed = provider_remove_handler("local_ollama")
        listed = provider_list_handler()
assert removed["ok"] is True
assert listed["data"]["providers"] == []
print("37. test_provider_registry_remove ✓")

with TemporaryDirectory() as tmpdir:
    registry_path = Path(tmpdir) / "llm_registry.json"
    with patch.dict(os.environ, {"COQUERY_LLM_REGISTRY_PATH": str(registry_path)}):
        provider_add_handler("local_ollama", "ollama", "qwen3.5:4b-nvfp4", "http://127.0.0.1:11434")
        with patch("sql_cli.llm_registry.urlopen", side_effect=_fake_llm_urlopen):
            provider_test = provider_test_handler("local_ollama")
assert provider_test["ok"] is True
assert provider_test["data"]["provider_name"] == "local_ollama"
assert provider_test["data"]["response_preview"] == "OK"
print("38. test_provider_test_ollama ✓")

with TemporaryDirectory() as tmpdir:
    registry_path = Path(tmpdir) / "llm_registry.json"
    with patch.dict(os.environ, {"COQUERY_LLM_REGISTRY_PATH": str(registry_path)}):
        provider_add_handler("local_ollama", "ollama", "qwen3.5:4b-nvfp4", "http://127.0.0.1:11434")
        with patch("sql_cli.llm_registry.urlopen", side_effect=_fake_llm_urlopen):
            llm_natural = natural_handler("example.db", "show users", provider_name="local_ollama")
assert llm_natural["ok"] is True
assert llm_natural["mode"] == "provider"
assert llm_natural["provider_name"] == "local_ollama"
assert llm_natural["sql"] == "SELECT * FROM users"
print("39. test_natural_with_registered_provider ✓")

print("")
print("=== ALL 39 TESTS PASS ✅ ===")
