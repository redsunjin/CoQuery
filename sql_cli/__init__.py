#!/usr/bin/env python3
"""EasySQL Package Init

Lazy imports - avoid click dependency at import time
"""

# Core modules only (no click dependency)
from sql_cli.core import SQLGenerator, SQLValidator, EasySQLCore, SQL_SKILLS
from sql_cli.db import UnifiedDatabase, TableColumn, TableSchema
from sql_cli.knowledge import KnowledgeMultiDB, SchemaKnowledge
from sql_cli.nl_core import NLIntentParser, NLToSQLConverter
