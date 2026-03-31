"""
EasySQL SQL Development Assistant
Entry → Junior → Intermediate → Expert → SQL Professional(SQLP)
"""

from .db import DBClient, TableColumn, TableSchema
from .contracts import ResponsePayload, SchemaRequest, QueryRequest, GenerateResponse
from .core import EasySQLCore, SQL_SKILLS, SQLGenerator, SQLValidator
from .cli import InteractiveCLI, CLIContext, main_interactive, main_json_command

__version__ = "0.1.0"
__all__ = [
    "DBClient",
    "TableColumn",
    "TableSchema",
    "ResponsePayload",
    "SchemaRequest",
    "QueryRequest",
    "GenerateResponse",
    "EasySQLCore",
    "SQL_SKILLS",
    "SQLGenerator",
    "SQLValidator",
    "InteractiveCLI",
    "CLIContext",
    "main_interactive",
    "main_json_command",
]
