#!/usr/bin/env python3
"""CLI Handler (Phase 0 - Simplified)"""

def schema_handler(db, format='json'):
     """Handle schema command"""
    return {
        'ok': True,
        'command': 'schema',
        'data': {
             'tables': []
         },
        'error': None
    }

def query_handler(db, sql, format='json'):
     """Handle query command"""
    return {
        'ok': True,
        'command': 'query',
        'data': {'rows': []},
        'error': None
    }

def generate_handler(db, skill, format='json'):
     """Handle generate command"""
    return {
        'ok': True,
        'command': 'generate',
        'command': skill,
        'error': None
    }

def natural_handler(db, sql, format='json'):
     """Handle natural command"""
    from sql_cli.nl_core import NLIntentParser
    parser = NLIntentParser()
    intent = parser.parse(sql)
     return {
         'ok': True,
         'command': 'natural',
         'intent': intent,
         'error': None
     }
