#!/usr/bin/env python3
import sys
sys.path.insert(0, '..')
sys.path.insert(0, '.')

def test_phase0_done():
    """Test Phase 0 baseline"""
    from main import schema_handler, query_handler
    schema_result = schema_handler('example.db')
    assert schema_result['ok'], "Schema handler should work"

def test_phase1_schema():
    """Test schema command"""
    from main import schema_handler
    result = schema_handler('example.db')
    assert result['ok'], "Schema should work"
    assert 'tables' in result.get('data', {})

def test_phase1_query():
    """Test query command"""
    from main import query_handler
    result = query_handler('example.db', 'SELECT * FROM users')
    assert result['ok'], "Query should work"
    assert 'rows' in result.get('data', {})

if __name__ == '__main__':
    test_phase0_done()
    test_phase1_schema()
    test_phase1_query()
    print("✅ All Phase 1 tests passing")
