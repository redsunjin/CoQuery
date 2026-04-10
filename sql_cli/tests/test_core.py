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
    db_knowledge_handler,
    delete_handler,
    generate_handler,
    insert_handler,
    jpa_schema_handler,
    natural_handler,
    provider_add_handler,
    provider_list_handler,
    provider_remove_handler,
    provider_test_handler,
    query_handler,
    schema_detail_handler,
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
        if "information_schema.columns" in query:
            return _FakeCursor(
                [
                    ("id", "integer", "NO", "nextval('users_id_seq'::regclass)", 1),
                    ("name", "text", "YES", None, 2),
                    ("org_id", "integer", "YES", None, 3),
                ]
            )
        if "information_schema.table_constraints" in query:
            return _FakeCursor(
                [
                    ("users_pkey", "PRIMARY KEY", "id", None, None),
                    ("users_org_id_fkey", "FOREIGN KEY", "org_id", "orgs", "id"),
                ]
            )
        if "JOIN pg_index" in query:
            return _FakeCursor(
                [
                    ("users_name_idx", False, False, ["name"]),
                    ("users_pkey", True, True, ["id"]),
                ]
            )
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
        with patch("sql_cli.llm_registry.urlopen", side_effect=AssertionError("provider should be skipped")) as provider_urlopen:
            llm_natural = natural_handler("example.db", "show users", provider_name="local_ollama")
assert llm_natural["ok"] is True
assert llm_natural["mode"] == "local_knowledge"
assert llm_natural["provider_skipped"] is True
assert llm_natural["requested_provider_name"] == "local_ollama"
assert llm_natural["provider_name"] is None
assert llm_natural["sql"] == "SELECT * FROM users"
assert "schema" in llm_natural["knowledge_context"]["topic_names"]
assert provider_urlopen.call_count == 0
print("39. test_natural_skips_provider_for_local_knowledge ✓")

with TemporaryDirectory() as tmpdir:
    project_root = Path(tmpdir)
    source_root = project_root / "src" / "main" / "java" / "com" / "example"
    source_root.mkdir(parents=True)
    (source_root / "User.java").write_text(
        """
package com.example;

import jakarta.persistence.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue
    private Long id;

    @Column(name = "user_name")
    private String name;

    private int age;

    @ManyToOne
    @JoinColumn(name = "department_id")
    private Department department;

    @Transient
    private String displayLabel;
}
""",
        encoding="utf-8",
    )
    (source_root / "Department.java").write_text(
        """
package com.example;

import javax.persistence.Entity;
import javax.persistence.Id;

@Entity(name = "DepartmentEntity")
public class Department {
    @Id
    private Long id;
    private String name;
}
""",
        encoding="utf-8",
    )
    (source_root / "Account.java").write_text(
        """
package com.example;

import jakarta.persistence.*;

@Entity
public class Account {
    private Long id;
    private String email;
    private String internalCode;

    @Id
    public Long getId() {
        return id;
    }

    @Column(name = "email_address")
    public String getEmail() {
        return email;
    }
}
""",
        encoding="utf-8",
    )

    jpa_schema = jpa_schema_handler(str(project_root))

assert jpa_schema["ok"] is True
assert jpa_schema["data"]["entity_count"] == 3
entities = {entity["class_name"]: entity for entity in jpa_schema["data"]["entities"]}
assert entities["User"]["table_name"] == "users"
assert entities["User"]["access"] == "field"
assert entities["User"]["id_attributes"] == ["id"]
user_attrs = {attr["name"]: attr for attr in entities["User"]["attributes"]}
assert user_attrs["name"]["column_name"] == "user_name"
assert user_attrs["department"]["relationship"] == "ManyToOne"
assert "displayLabel" not in user_attrs
assert entities["Department"]["entity_name"] == "DepartmentEntity"
assert entities["Account"]["access"] == "property"
account_attrs = {attr["name"]: attr for attr in entities["Account"]["attributes"]}
assert account_attrs["email"]["column_name"] == "email_address"
assert "internalCode" not in account_attrs
print("40. test_jpa_schema_source_scan ✓")

missing_jpa_project = jpa_schema_handler("")
assert missing_jpa_project["ok"] is False
assert missing_jpa_project["error"]["code"] == "missing_jpa_project"
print("41. test_jpa_schema_missing_project_error ✓")

with TemporaryDirectory() as tmpdir:
    project_root = Path(tmpdir)
    source_root = project_root / "src" / "main" / "java" / "com" / "example"
    source_root.mkdir(parents=True)
    (source_root / "User.java").write_text(
        """
package com.example;

import jakarta.persistence.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    private Long id;
}
""",
        encoding="utf-8",
    )
    rc, payload = run_cli(["--command", "jpa_schema", "--jpa-project", str(project_root), "--format", "json"])

assert rc == 0
assert payload["ok"] is True
assert payload["data"]["entity_count"] == 1
assert payload["data"]["entities"][0]["class_name"] == "User"
print("42. test_docs_jpa_schema_example ✓")

knowledge_overview = db_knowledge_handler()
assert knowledge_overview["ok"] is True
assert knowledge_overview["data"]["kind"] == "overview"
assert "sqlite" in knowledge_overview["data"]["available_dialects"]
assert "jpql" in knowledge_overview["data"]["available_dialects"]
print("43. test_db_knowledge_overview ✓")

sqlite_knowledge = db_knowledge_handler("sqlite", "schema")
assert sqlite_knowledge["ok"] is True
assert sqlite_knowledge["data"]["kind"] == "dialect_topic"
assert "sqlite_master" in sqlite_knowledge["data"]["value"]["value"]["tables"]
print("44. test_db_knowledge_sqlite_schema_topic ✓")

jpql_knowledge = db_knowledge_handler("jpa", "parameters")
assert jpql_knowledge["ok"] is True
assert jpql_knowledge["data"]["value"]["dialect"] == "jpql"
assert "named" in jpql_knowledge["data"]["value"]["value"]
print("45. test_db_knowledge_jpa_alias ✓")

write_knowledge = db_knowledge_handler(topic="write_safety")
assert write_knowledge["ok"] is True
assert write_knowledge["data"]["kind"] == "safety"
assert "UPDATE" in write_knowledge["data"]["value"]["write_operations"]
print("46. test_db_knowledge_write_safety ✓")

unknown_knowledge = db_knowledge_handler("db2", "schema")
assert unknown_knowledge["ok"] is False
assert unknown_knowledge["error"]["code"] == "unknown_dialect"
print("47. test_db_knowledge_unknown_dialect ✓")

rc, payload = run_cli(["--command", "db_knowledge", "--dialect", "postgresql", "--topic", "pagination"])
assert rc == 0
assert payload["ok"] is True
assert payload["data"]["value"]["dialect"] == "postgresql"
assert "LIMIT" in payload["data"]["value"]["value"]["template"]
print("48. test_docs_db_knowledge_example ✓")

postgres_types = db_knowledge_handler("postgresql", "types")
assert postgres_types["ok"] is True
assert postgres_types["data"]["value"]["value"]["json"] == "jsonb"
print("49. test_db_knowledge_postgresql_types ✓")

mysql_constraints = db_knowledge_handler("mysql", "constraints")
assert mysql_constraints["ok"] is True
assert "FOREIGN KEY" in mysql_constraints["data"]["value"]["value"]["common"]
print("50. test_db_knowledge_mysql_constraints ✓")

jpql_joins = db_knowledge_handler("jpql", "joins")
assert jpql_joins["ok"] is True
assert "JOIN FETCH" in jpql_joins["data"]["value"]["value"]["fetch"]
print("51. test_db_knowledge_jpql_joins ✓")

sqlite_operators = db_knowledge_handler("sqlite", "operators")
assert sqlite_operators["ok"] is True
assert "LIKE" in sqlite_operators["data"]["value"]["value"]["pattern"]
print("52. test_db_knowledge_sqlite_operators ✓")

knowledge_coverage = db_knowledge_handler(topic="coverage")
assert knowledge_coverage["ok"] is True
assert knowledge_coverage["data"]["kind"] == "coverage"
assert knowledge_coverage["data"]["value"]["coverage_level"] == "schema_detail_aware_generation_seed"
assert "sqlite" in knowledge_coverage["data"]["value"]["summary"]["dialects"]
assert "jpql" in knowledge_coverage["data"]["value"]["summary"]["dialects"]
assert knowledge_coverage["data"]["value"]["remaining_gaps"]
print("53. test_db_knowledge_coverage_report ✓")

rc, payload = run_cli(["--command", "db_knowledge", "--topic", "coverage"])
assert rc == 0
assert payload["ok"] is True
assert payload["data"]["kind"] == "coverage"
assert payload["data"]["value"]["implemented_gates"][0]["name"] == "local_knowledge_first_generation"
print("54. test_docs_db_knowledge_coverage_example ✓")

with TemporaryDirectory() as tmpdir:
    registry_path = Path(tmpdir) / "llm_registry.json"
    with patch.dict(os.environ, {"COQUERY_LLM_REGISTRY_PATH": str(registry_path)}):
        provider_add_handler("local_ollama", "ollama", "qwen3.5:4b-nvfp4", "http://127.0.0.1:11434")
        with patch("sql_cli.llm_registry.urlopen", side_effect=_fake_llm_urlopen):
            complex_natural = natural_handler("example.db", "join users and orders", provider_name="local_ollama")
assert complex_natural["ok"] is True
assert complex_natural["mode"] == "provider"
assert complex_natural["provider_skipped"] is False
assert complex_natural["provider_name"] == "local_ollama"
assert "joins" in complex_natural["knowledge_context"]["topic_names"]
print("55. test_natural_provider_fallback_for_complex_request ✓")

generated_with_context = generate_handler("postgresql://user:pass@localhost:5432/dbname", "join_inner")
assert generated_with_context["ok"] is True
assert generated_with_context["knowledge_context"]["knowledge_first"] is True
assert generated_with_context["knowledge_context"]["dialect"] == "postgresql"
assert "statements" in generated_with_context["knowledge_context"]["topic_names"]
assert "joins" in generated_with_context["knowledge_context"]["topic_names"]
print("56. test_generate_uses_local_knowledge_context ✓")

tmpdir, db_path = make_temp_db()
write_context_result = insert_handler(
    str(db_path),
    "INSERT INTO users (name, age) VALUES (?, ?)",
    ["knowledge_write_user", 45],
    write=True,
)
assert write_context_result["ok"] is True
assert write_context_result["data"]["knowledge_context"]["knowledge_first"] is True
assert write_context_result["data"]["knowledge_context"]["dialect"] == "sqlite"
assert "write_safety" in write_context_result["data"]["knowledge_context"]["topic_names"]
tmpdir.cleanup()
print("57. test_write_uses_local_knowledge_context ✓")

schema_detail = schema_detail_handler("example.db", "users")
assert schema_detail["ok"] is True
assert schema_detail["data"]["backend"] == "sqlite"
assert schema_detail["data"]["table_count"] == 1
users_detail = schema_detail["data"]["tables"][0]
assert users_detail["name"] == "users"
assert [column["name"] for column in users_detail["columns"]] == ["id", "name", "age"]
assert users_detail["primary_key"] == ["id"]
assert users_detail["constraints"]["foreign_keys"] == []
print("58. test_schema_detail_sqlite_users ✓")

with TemporaryDirectory() as tmpdir:
    db_path = Path(tmpdir) / "schema-detail.db"
    db = CoQueryDB(str(db_path))
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("CREATE TABLE orgs (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)")
    db.execute(
        "CREATE TABLE members ("
        "id INTEGER PRIMARY KEY, "
        "org_id INTEGER NOT NULL, "
        "email TEXT NOT NULL, "
        "FOREIGN KEY (org_id) REFERENCES orgs(id) ON DELETE CASCADE"
        ")"
    )
    db.execute("CREATE UNIQUE INDEX members_email_idx ON members(email)")
    db.close()

    detail = schema_detail_handler(str(db_path), "members")

assert detail["ok"] is True
member_detail = detail["data"]["tables"][0]
assert member_detail["primary_key"] == ["id"]
assert member_detail["foreign_keys"][0]["referenced_table"] == "orgs"
assert member_detail["foreign_keys"][0]["on_delete"] == "CASCADE"
assert member_detail["indexes"][0]["name"] == "members_email_idx"
assert member_detail["indexes"][0]["unique"] is True
assert "org_id" in member_detail["constraints"]["not_null"]
print("59. test_schema_detail_sqlite_fk_index_fixture ✓")

missing_detail = schema_detail_handler("example.db", "missing_table")
assert missing_detail["ok"] is False
assert missing_detail["error"]["code"] == "table_not_found"
print("60. test_schema_detail_missing_table_error ✓")

with patch("sql_cli.db_new.importlib.import_module", return_value=_FakePsycopgSuccessModule()):
    pg_detail = schema_detail_handler("postgresql://user:pass@localhost:5432/dbname", "users")
assert pg_detail["ok"] is True
pg_users = pg_detail["data"]["tables"][0]
assert pg_detail["data"]["backend"] == "postgresql"
assert pg_users["primary_key"] == ["id"]
assert pg_users["columns"][0]["primary_key"] is True
assert pg_users["foreign_keys"][0]["referenced_table"] == "orgs"
assert pg_users["indexes"][1]["primary"] is True
print("61. test_schema_detail_postgresql_success_path ✓")

rc, payload = run_cli(["--command", "schema_detail", "--db", "example.db", "--table", "users", "--format", "json"])
assert rc == 0
assert payload["ok"] is True
assert payload["data"]["tables"][0]["name"] == "users"
assert payload["data"]["tables"][0]["primary_key"] == ["id"]
print("62. test_docs_schema_detail_example ✓")

schema_detail_knowledge = db_knowledge_handler("sqlite", "schema_detail")
assert schema_detail_knowledge["ok"] is True
assert schema_detail_knowledge["data"]["kind"] == "dialect_topic"
assert "PRAGMA table_info" in schema_detail_knowledge["data"]["value"]["value"]["columns"]
print("63. test_db_knowledge_schema_detail_topic ✓")

schema_valid_generated = generate_handler(
    "example.db",
    "select_simple",
    params={"table": "users", "cols": ["id", "name"]},
)
assert schema_valid_generated["ok"] is True
assert schema_valid_generated["sql"] == "SELECT ID, NAME FROM USERS"
assert schema_valid_generated["schema_validation"]["status"] == "validated"
assert "schema_detail" in schema_valid_generated["knowledge_context"]["topic_names"]
assert {"table": "users", "column": "id"} in schema_valid_generated["schema_validation"]["validated_columns"]
print("64. test_generate_validates_schema_detail_columns ✓")

schema_invalid_generated = generate_handler(
    "example.db",
    "select_simple",
    params={"table": "missing_table"},
)
assert schema_invalid_generated["ok"] is False
assert schema_invalid_generated["error"]["code"] == "schema_validation_failed"
assert schema_invalid_generated["schema_validation"]["errors"][0]["code"] == "unknown_table"
print("65. test_generate_rejects_unknown_schema_table ✓")

natural_count = natural_handler("example.db", "count users")
assert natural_count["ok"] is True
assert natural_count["sql"] == "SELECT COUNT(*) FROM users"
assert natural_count["schema_validation"]["status"] == "validated"
assert natural_count["table_inference"]["table"] == "users"
assert "schema_detail" in natural_count["knowledge_context"]["topic_names"]
print("66. test_natural_uses_schema_detail_table_inference ✓")

natural_missing_table = natural_handler("example.db", "show missing_table")
assert natural_missing_table["ok"] is False
assert natural_missing_table["sql"] is None
assert natural_missing_table["error"]["code"] == "schema_validation_failed"
assert natural_missing_table["schema_validation"]["errors"][0]["code"] == "unknown_table"
print("67. test_natural_rejects_unknown_schema_table ✓")

print("")
print("=== ALL 67 TESTS PASS ✅ ===")
