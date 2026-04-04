#!/usr/bin/env python3
"""Small executable baseline tests for CoQuery."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sql_cli.cli import generate_handler, query_handler, schema_handler
from sql_cli.core import SQLGenerator, SQLValidator
from sql_cli.db_new import CoQueryDB
from sql_cli.nl_core import NaturalLanguageEngine


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

print("")
print("=== ALL 11 TESTS PASS ✅ ===")
