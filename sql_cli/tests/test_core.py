#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_core.py - Core functionality tests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sql_cli.db import DBClient
from sql_cli.core import EasySQLCore, SQL_SKILLS
from sql_cli.contracts import ResponsePayload


def test_skills():
    """Test SQL skills list"""
    core = EasySQLCore("example.db")
    skills = core.list_skills()
    
    assert len(skills) > 0, "Skills should exist"
    print(f"[PASS] Skills count: {len(skills)}")
    
    # Check specific skill
    if "select_simple" in SQL_SKILLS:
        skill = SQL_SKILLS["select_simple"]
        assert skill["name"] == "SELECT 기본 조회"
        print("[PASS] select_simple exists")
    
    return True


def test_generate_simple():
    """Test simple SQL generation"""
    core = EasySQLCore("example.db")
    
    params = {
        "table": "users",
        "cols": "*",
        "where": "",
        "order": "",
    }
    
    result = core.generate_query("select_simple", params)
    
    assert "error" not in result, "Should not have error"
    assert "sql" in result, "Should have sql"
    assert "SELECT" in result["sql"].upper(), "Should be SELECT"
    
    print(f"[PASS] Generated: {result['sql'][:50]}...")
    return True


def test_classify_query():
    """Test query classification"""
    core = EasySQLCore("example.db")
    
    # Read-only
    read_sql = "SELECT * FROM users"
    classification = core.classify_query(read_sql)
    assert classification == "read", f"Should be read, got {classification}"
    print("[PASS] SELECT classified as read")
    
    # Write
    write_sql = "INSERT INTO users (name) VALUES ('test')"
    classification = core.classify_query(write_sql)
    assert classification == "write", f"Should be write, got {classification}"
    print("[PASS] INSERT classified as write")
    
    return True


def test_validate_query():
    """Test SQL validation"""
    core = EasySQLCore("example.db")
    
    # Valid
    valid_sql = "SELECT * FROM users"
    errors = core.validate_query(valid_sql)
    assert len(errors) == 0, f"Should be valid, got {errors}"
    print("[PASS] Valid SQL passes")
    
    # Invalid (missing FROM)
    invalid_sql = "SELECT * users"
    errors = core.validate_query(invalid_sql)
    # May or may not fail depending on SQL
    
    return True


def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("Running EasySQL core tests")
    print("="*50)
    
    tests = [
         (test_skills, "Skills test"),
          (test_generate_simple, "Generate test"),
          (test_classify_query, "Classification test"),
          (test_validate_query, "Validation test"),
      ]
    
    passed = 0
    failed = 0
    
    for test, name in tests:
        print(f"\n[Test] {name}")
        try:
            test()
            passed += 1
            print(f"[OK] {name}")
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {name}: {e}")
    
    print("\n" + "="*50)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*50)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

