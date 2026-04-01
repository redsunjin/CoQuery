#!/usr/bin/env python3
"""CoQuery Package Init

Lazy imports - avoid click dependency at import time
"""

# Core modules only (no click dependency)
from sql_cli.core import SQLGenerator, SQLValidator, CoQueryCore, SQL_SKILLS
from sql_cli.db import UnifiedDatabase, TableColumn, TableSchema
from sql_cli.knowledge import KnowledgeMultiDB, SchemaKnowledge
from sql_cli.nl_core import NLIntentParser, NLToSQLConverter
