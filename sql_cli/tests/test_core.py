#!/usr/bin/env python3
"""Test suite for EasySQL (Phase 0)"""

def test_core_imports():
    """Test core module imports"""
    from sql_cli import core
    from sql_cli.core import SQLGenerator, SQLValidator
    assert True

def test_generate_sql():
    """Test SQL generation"""
    from sql_cli.core import SQLGenerator
    gen = SQLGenerator()
    result = gen.generate('select_simple', {'table': 'users'})
    assert 'sql' in result

def test_validate_sql():
    """Test SQL validation"""
    from sql_cli.core import SQLValidator
    val = SQLValidator()
    errors = val.validate("SELECT * FROM users")
    assert isinstance(errors, list)

if __name__ == '__main__':
    test_core_imports()
    test_generate_sql()
    test_validate_sql()
    print("✓ All tests passing")
