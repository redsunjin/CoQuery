from sql_cli.core import SQLGenerator, SQLValidator
from sql_cli.db_new import CoQueryDB
from sql_cli.cli import schema_handler, query_handler

print("=== CoQuery Tests ===")

# Test 1: SELECT
gen = SQLGenerator()
result = gen.generate('select_simple', {})
assert 'sql' in result
print("1. test_select_simple ✓")

# Test 2: COUNT
result = gen.generate('count_simple', {'table': 'users'})
assert 'sql' in result
print("2. test_count ✓")

# Test 3: SELECT Valid
val = SQLValidator()
errors = val.validate("SELECT * FROM users")
assert errors == []
print("3. test_select_valid ✓")

# Test 4: INSERT Valid
errors = val.validate("INSERT INTO users VALUES (1, 'test')")
assert errors == []
print("4. test_insert_valid ✓")

# Test 5: Connect
db = CoQueryDB("example.db")
assert db.conn is not None
db.close()
print("5. test_db_connect ✓")

# Test 6: Execute
db = CoQueryDB("example.db")
result = db.execute("SELECT * FROM users")
assert isinstance(result, list)
db.close()
print("6. test_db_execute ✓")

# Test 7: Schemas
db = CoQueryDB("example.db")
tables = db.get_schemas()
assert isinstance(tables, list)
db.close()
print("7. test_db_schemas ✓")

# Test 8: Schema Command
result = schema_handler("example.db")
assert result.get('ok') == True
print("8. test_schema_command ✓")

# Test 9: Query Command
result = query_handler("example.db", "SELECT * FROM users LIMIT 1")
assert result.get('ok') == True
print("9. test_query_command ✓")

print("")
print("=== ALL 9 TESTS PASS ✅ ===")
