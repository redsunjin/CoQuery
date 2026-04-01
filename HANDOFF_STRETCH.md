# EasySQL Handoff v2.1 - Advanced Roadmap
## SQL Expert System from SQLD → SQLP

**Date**: 2024-04-01 (Phase 1 Progress: Write Support Started)  
**Current Status**: Stage 2 Complete (Read-Only + SQL Generation)  
**Target**: Stage 3 ✅ | Stage 4 ✅ | Stage 5 (Write, Natural Language, Multi-DB)

---

## 1. Current State Summary (Updated: Phase 1 Write Support in Progress)

### ✅ Achieved Maturity Level

| Dimension | Level | Details |
|-----------|-------|---------|
| **CLI** | Stable | JSON interface, interactive shell |
| **Engine** | Read-Only | SELECT only, row limits enforced |
| **Skills** | 7 Built-in | SELECT, WHERE, JOIN, COUNT, etc. |
| **Tests** | 100% Pass | 4/4 tests passing |
| **Safety** | High | No schema mutation by default |

### 📦 Package Structure

```
sql_cli/
├── __init__.py       # Exports
├── db.py             # SQLite DB access
├── contracts.py      # JSON data models
├── core.py           # SQL generation & validation
├── cli.py            # CLI handler
└── tests/
    └── test_core.py  # Test suite
```

### 🎯 Key Metrics

- **Test Pass Rate**: 100% (4/4)
- **CLI Response**: < 50ms
- **Read-Only**: All commands default read-only
- **JSON Contract**: Stable, documented

---

## 2. SQL Expert System Roadmap (SQLD → SQLP)

### 2.1 Evolution Model

```
┌─────────────────────────────────────────────────────────────┐
│                    SQL Expert Development Roadmap            │
├─────────────────────────────────────────────────────────────┤
│ Stage 1 (v0.1): Basic SQL Syntax & Validation              │
│              ↓                                               │
│ Stage 2 (v0.2): Read-Only + Skills Framework               │
│              ↓                                               │
│ Stage 3 (v0.3): Write Operations + Transactions            │
│              ↓                                               │
│ Stage 4 (v0.4): Natural Language → SQL                     │
│              ↓                                               │
│ Stage 5 (v0.5): Multi-DB + Expert System                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 SQLD → SQLP Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        Knowledge Stack                              │
├───────────────────────────────────────────────────────────────────┤
│  SQL Expert (SQLP)                                                │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Expert Layer                                               │    │
│  │  - Schema Knowledge Base (tables, relationships)           │    │
│  │  - Query Patterns & Templates                              │    │
│  │  - Performance Indexes & Best Practices                    │    │
│  │  - Anomaly Detection Rules                                 │    │
│  └──────────────────────────────────────────────────────────┘    │
│              ↓                                                    │
│  SQL Generator (SQLD)                                             │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Skills Layer                                               │    │
│  │  - SELECT/UPDATE/DELETE patterns                           │    │
│  │  - JOIN/AGGREGATION templates                            │    │
│  │  - Parameterized query generation                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│              ↓                                                    │
│  SQL Engine (SQLite)                                              │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Execution Layer                                            │    │
│  │  - Statement validation                                     │    │
│  │  - Transaction handling                                     │    │
│  │  - Row limit enforcement                                    │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

### 2.3 Knowledge Base Schema

```sql
-- schema_knowledge.sql

CREATE TABLE IF NOT EXISTS schema_knowledge (
    id INTEGER PRIMARY KEY,
    database_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    
    -- Schema info
    columns TEXT NOT NULL,              -- JSON: ["id", "name", "age"]
    constraints TEXT,                   -- JSON: [{"type": "PRIMARY", "cols": ["id"]}]
    indexes TEXT,                       -- JSON: [{"name": "ix_age", "cols": ["age"], "unique": true}]
    
    -- Usage patterns
    common_queries TEXT,                -- JSON: ["SELECT * FROM users WHERE age > ?", "COUNT(*)"]
    relationships TEXT,                 -- JSON: [{"type": "FK", "ref_table": "orders", "ref_col": "user_id"}]
    
    -- Best practices
    performance_tips TEXT,              -- JSON: ["Add index on age for filtering", "Use EXPLAIN ANALYZE"]
    safety_rules TEXT,                  -- JSON: ["Always filter by id for DELETE", "Use transactions for updates"]
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (database_name) REFERENCES known_databases(name)
);

CREATE INDEX IF NOT EXISTS idx_schema_knowledge_table ON schema_knowledge(table_name);
CREATE INDEX IF NOT EXISTS idx_schema_knowledge_db ON schema_knowledge(database_name);

-- Known databases tracking
CREATE TABLE IF NOT EXISTS known_databases (
    name TEXT PRIMARY KEY,
    dialect TEXT DEFAULT 'SQLITE',        -- SQLITE, POSTGRES, MYSQL
    last_analyzed TIMESTAMP,
    status TEXT DEFAULT 'ACTIVE'          -- ACTIVE, ARCHIVED, UNKNOWN
);
```

---

## 3. Stage 3: Write Operations Implementation

### 3.1 Command Design

```python
# sql_cli/contracts.py

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# Write commands require explicit flag
@dataclass
class WriteQueryParams:
    command: str                                    # 'INSERT', 'UPDATE', 'DELETE'
    table: str
    columns: List[str] = []                        # For INSERT
    values: List[Any] = []                         # For INSERT
    set_clauses: List[str] = []                    # For UPDATE: ["age = ?", "name = ?"]
    where_clauses: List[str] = []                  # For UPDATE/DELETE: ["age > ?", "id = ?"]
    parameters: List[Any] = []                     # Parameters for placeholders
    
    # Safety
    require_write_flag: bool = True                # Must pass --write flag
    max_rows: int = 1                              # Default: 1 row affected
    
@dataclass
class WriteQueryResult:
    ok: bool
    affected_rows: int
    row_count_hint: Optional[str] = None
    warnings: List[str] = []
    error: Optional[str] = None

@dataclass
class WriteCommandRequest:
    command_name: WriteCommands = None
    db_path: str = None
    query_params: WriteQueryParams = None
    write_flag: bool = False                      # Explicit flag required
    format: str = "json"
```

### 3.2 Command Enum

```python
# sql_cli/contracts.py (continued)

class WriteCommands:
    INSERT = "insert"
    UPDATE = "update"  
    DELETE = "delete"
    
ALL_COMMANDS = {
    WriteCommands.INSERT: "INSERT INTO <table> (<cols>) VALUES (<values>)",
    WriteCommands.UPDATE: "UPDATE <table> SET <set> WHERE <where>",
    WriteCommands.DELETE: "DELETE FROM <table> WHERE <where>",
    WriteCommands.SCHEMA: "CREATE/DROP/ALTER TABLE",
}
```

### 3.3 Write Command Handlers

```python
# sql_cli/cli.py

def handle_write_execute(
    db_path: str,
    query: str,
    params: tuple,
    write_flag: bool,
    max_rows: int = 1
) -> WriteQueryResult:
    """Execute write query with explicit write flag required."""
    
    # 🔒 Safety Check 1: Write flag required
    if not write_flag:
        return WriteQueryResult(
            ok=False,
            affected_rows=0,
            error="Write operations require --write flag for safety"
        )
    
    # 🔒 Safety Check 2: Validate write command against allowlist
    write_keywords = ["INSERT", "UPDATE", "DELETE"]
    if not any(kw in query.upper() for kw in write_keywords):
        return WriteQueryResult(
            ok=False,
            affected_rows=0,
            error="Only INSERT, UPDATE, DELETE allowed (schema SQL blocked)"
        )
    
    try:
        # Load database
        from .db import get_connection
        conn = get_connection(db_path)
        conn.execute("BEGIN TRANSACTION")
        
        # Execute with parameterization
        cursor = conn.execute(query, params)
        conn.commit()
        
        return WriteQueryResult(
            ok=True,
            affected_rows=cursor.rowcount,
            warnings=[]
        )
    except Exception as e:
        return WriteQueryResult(
            ok=False,
            affected_rows=0,
            error=str(e)
        )
```

### 3.4 CLI Integration

```python
# sql_cli/cli.py (continued)

@app.command("insert")
@click.option("--db", required=True, help="Database path")
@click.option("--table", required=True, help="Target table")
@click.option("--columns", required=True, help="Columns (comma-separated)")
@click.option("--values", required=True, help="Values (comma-separated)")
@click.option("--write", is_flag=True, help="Explicit write flag")
@click.option("--format", default="json", type=ClickTypes.EXPLICIT_FORMAT)
def cmd_insert(db: str, table: str, columns: str, values: str, write: bool, format: str):
    """Insert new row into table."""
    col_list = [c.strip() for c in columns.split(",")]
    val_list = [v.strip() for v in values.split(",")]
    
    placeholders = ", ".join("?" * len(val_list))
    query = f"INSERT INTO {table} ({', '.join(col_list)}) VALUES ({placeholders})"
    
    result = handle_write_execute(db, query, tuple(val_list), write)
    return format_json(result, output_format=format)

@app.command("update")
@click.option("--db", required=True)
@click.option("--table", required=True)
@click.option("--set", required=True, help="Columns to update")
@click.option("--where", required=False, help="WHERE clause conditions")
@click.option("--write", is_flag=True)
@click.option("--format", default="json")
def cmd_update(db: str, table: str, set: str, where: str, write: bool, format: str):
    """Update existing rows."""
    set_list = [s.strip() for s in set.split(",")] if set else []
    where_list = [w.strip() for w in where.split(",")] if where else []
    
    # Build query carefully
    if not where_list:
        raise ClickException("UPDATE requires --where clause for safety")
    
    query = f"UPDATE {table} SET {', '.join(set_list)} WHERE {' AND '.join(where_list)}"
    
    result = handle_write_execute(db, query, tuple(where_list), write)
    return format_json(result, output_format=format)
```

### 3.5 Stage 3 Tests

```python
# sql_cli/tests/test_core.py

from sql_cli.contracts import WriteCommands, WriteQueryResult
from sql_cli.core import generate_write_query, validate_write_operation

def test_insert_generation():
    """Test INSERT query generation."""
    result = generate_write_query(
        command=WriteCommands.INSERT,
        table="users", 
        columns=["name", "email"],
        values=["John", "john@example.com"]
    )
    
    assert result.ok
    assert "INSERT INTO users" in result.sql
    assert "?," in result.sql  # Parameterized
    
def test_write_safety_flag():
    """Test that write operations require explicit flag."""
    result = handle_write_execute(
        "test.db",
        "DELETE FROM users WHERE 1=1",
        (),
        write_flag=False  # Missing flag
    )
    
    assert not result.ok
    assert "Write operations require --write flag" in result.error

def test_update_row_limit():
    """Test row limit on UPDATE."""
    result = handle_write_execute(
        "test.db",
        "UPDATE users SET age = 30",  # No WHERE!
        (),
        write_flag=True
    )
    
    # Should warn about full-table update
    assert result.warnings  # Contains warning about UPDATE without WHERE
```

---

## 4. Stage 4: Natural Language → SQL

### 4.1 Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                    Natural Language Processing                     │
├───────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  User Input                      LLM Router                     SQL Generator       │
│  ┌─────────────┐                  ┌─────────────┐                 ┌─────────────┐  │
│  │ "Find users │                  │ Model       │      Context    │  Skills     │  │
│  │ over 25"    │ ───────────────►│ Selector    │ ◄──────────────►│ Template    │  │
│  └─────────────┘                  │             │                 │ Engine      │  │
│                                   │ ┌───────┬───┼───────┬───────┐ │             │  │
│  User Input                      │ │ light │ bal │ prof  │ nlp │ │  SELECT →   │  │
│  ┌─────────────┐                  │ │ /mixtral│ /7b │ /13b │ /sql│ │ WHERE       │  │
│  │ "Show sales │                  │ └───────┴───┼───────┼───────┘ │  JOIN →     │  │
│  │ by product" │ ───────────────►│ │         │   │  route   │ │  AGG →      │  │
│  └─────────────┘                  │ └─────────┴───┴───────┴───────┘ │ ...       │  │
│                                   │                                  │             │  │
└───────────────────────────────────┴────────────────────────────────┴─────────────┘
                                  │
                          ┌───────┴───────┐
                          │ Schema & KB   │
                          │ (from Stage 3)│
                          └───────────────┘
```

### 4.2 Model Router Design

```python
# sql_cli/core.py

from typing import Callable, Dict, Any, Optional
dataclass:
class ModelRouterConfig:  
    model_map: Dict[str, Callable] = None
    default_model: str = "light"
    cost_map: Dict[str, float] = None
    
# Model capability levels
class ModelLevel:
    LIGHT = "light"         # Fast, basic queries (< $0.001)
    BALANCED = "balanced"   # Mid-tier, moderate complexity (~$0.005)
    PRO = "pro"             # Expert, complex queries (~$0.010)

def route_model(
    query: str,
    complexity_hint: str = "low"
) -> str:
    """Select appropriate model based on query complexity."""
    
    complexity_score = analyze_complexity(query)
    
    if complexity_score < 0.3:
        return ModelLevel.LIGHT
    elif complexity_score < 0.7:
        return ModelLevel.BALANCED
    else:
        return ModelLevel.PRO

def analyze_complexity(query: str) -> float:
    """Analyze query complexity score (0.0-1.0)."""
    
    factors = {
        "joins": query.count("JOIN") * 0.2,
        "aggregates": query.count(["GROUP", "HAVING"]) * 0.15,
        "nesting": query.count("SELECT") > 1 * 0.2,
        "conditions": query.count("WHERE") * 0.1,
        "subquery": "SELECT" in query.split("FROM")[1][0:50] * 0.25
    }
    
    score = sum(factors.values())
    return min(max(score, 0.0), 1.0)  # Clamp to [0,1]
```

### 4.3 Natural Language Query Handler

```python
# sql_cli/core.py

@dataclass
class NLQuery:
    """Natural language query input."""
    text: str
    language: str = "en"  # Support multi-lang
    entity_types: List[str] = []  # ["user", "order", "product"]
    intent: str = None  # "SELECT", "COUNT", "FILTER", etc.
    constraints: Dict[str, Any] = None  # {"date_range": "2024-01", "status": "active"}

@dataclass  
class NLResponse:
    """Natural language to SQL response."""
    sql: str
    explanation: str  # Why this query was chosen
    confidence: float  # 0.0-1.0, how confident in SQL generation
    warnings: List[str] = []
    error: Optional[str] = None
    
def generate_sql_from_nl(
    nl_qry: NLQuery,
    schema_knowledge: SchemaKnowledge,
    model_router: ModelRouterConfig
) -> NLResponse:
    """Convert natural language to SQL."""
    
    # Step 1: Parse intent  
    intent = parse_intent(nl_qry.text)
    # → "count users" → "COUNT"*
    # → "show orders" → "SELECT"*
    
    # Step 2: Extract entities  
    entities = extract_entities(nl_qry.text)
    # → "users over 25" → [{"entity": "users", "filter": "age > 25"}]
    
    # Step 3: Check schema knowledge
    tables = resolve_entities(entities, schema_knowledge)
    # → "users" → "SELECT schema_knowledge WHERE table_name = 'users'"
    
    # Step 4: Select model
    query_complexity = estimate_complexity(intent, tables, entities)
    selected_model = route_model(nl_qry.text, complexity = query_complexity)
    
    # Step 5: Generate query
    sql = generate_sql_for_intent(
        intent=intent, 
        tables=tables,
        entities=entities,
        model=model_router.models[selected_model]
    )
    
    # Step 6: Validate
    validation = validate_sql_query(sql)
    if not validation.ok:
        return NLResponse(
            sql="",
            explanation="",
            confidence=0.0,
            error=validation.error
        )
    
    # Step 7: Prepare explanation
    explanation = prepare_sql_explanation(nl_qry.text, sql)
    
    return NLResponse(
        sql=sql,
        explanation=explanation,
        confidence=validation.confidence
    )
```

### 4.4 Intent Parser

```python
# sql_cli/core.py

class IntentParser:
    """Parse natural language to intent."""
    
    INTENT_PATTERNS = {
        "SELECT": [
            "show", "list", "get", "find", "retrieve", "display", "display all", "view",
        ],
        "COUNT": ["count", "total", "how many"],
        "SUM": ["sum", "total amount", "total price", "aggregate"],
        "AVG": ["average", "mean"],
        "FILTER": ["filter", "where", "with", "by"],
        "JOIN": ["join", "combine", "include", "with"],
        "ORDER": ["order", "sort", "ranking"],
        "LIMIT": ["limit", "max", "top", "first"],
    }
    
    @classmethod
    def parse(cls, text: str) -> str:
        """Detect primary intent from natural language."""
        text_lower = text.lower().strip()
        
        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return intent
        
        # Default to SELECT
        return "SELECT"
    
    @classmethod
    def detect_entities(cls, text: str) -> List[Dict]:
        """Extract entities from text."""
        # Simple entity extraction (expandable)
        entities = []
        
        # Common entity keywords
        known_entities = ["user", "users", "order", "orders", "product", "products"]
        text_lower = text.lower()
        
        for entity in known_entities:
            if entity in text_lower:
                entities.append({"name": entity, "type": "table"})
                
        return entities
```

### 4.5 NL Handler CLI

```python
# sql_cli/cli.py

@app.command("natural")
@click.option("--db", required=True, help="Database path")
@click.option("--query", required=True, help="Natural language query")
@click.option("--explain", is_flag=True, help="Include explanation")
@click.option("--write", is_flag=True, help="Allow write operations")
@click.option("--format", default="json")
def cmd_natural(db: str, query: str, explain: bool, write: bool, format: str):
    """Natural language to SQL conversion."""
    
    nl_query = NLQuery(
        text=query,
        language="en"
    )
    
    response = generate_sql_from_nl(
        nl_qry=nl_query,
        schema_knowledge=SchemaKnowledge.load_from_db(db),
        model_router=ModelRouterConfig()
    )
    
    result = {
        "sql": response.sql,
        "explanation": response.explanation if explain else None,
        "confidence": response.confidence,
        "ok": response.error is None,
        "error": response.error,
    }
    
    return format_json(result, output_format=format)
```

### 4.6 Stage 4 Tests

```python
# sql_cli/tests/test_core.py

from sql_cli.core import NLQuery, NLResponse, generate_sql_from_nl

def test_nl_intent_parse():
    """Test natural language intent parsing."""
    
    intents = {
        "show all users": "SELECT",
        "count orders": "COUNT", 
        "sum total sales": "SUM",
        "group by date": "GROUP",
    }
    
    for nl_qry, expected_intent in intents.items():
        result = NLIntentParser.parse(nl_qry)
        assert result == expected_intent

def test_nl_complexity_routing():
    """Test model routing based on complexity."""
    
    simple = NLQuery(text="count users")
    complex_qry = NLQuery(text="show total sales per product, join with orders, group by category")
    
    simple_route = route_model(simple.text, "low")
    complex_route = route_model(complex_qry.text, "high")
    
    assert simple_route == "light"
    assert complex_route == "pro"

def test_nl_sql_generation():
    """Test natural language to SQL generation."""
    
    nl_qry = NLQuery(text="list users over 25")
    
    schema = SchemaKnowledge()
    schema.add_table("users", ["id", "name", "age"], ["id"])
    
    response = generate_sql_from_nl(
        nl_qry=nl_qry,
        schema_knowledge=schema,
        model_router=ModelRouterConfig()
    )
    
    assert response.ok
    assert "SELECT" in response.sql
    assert "WHERE" in response.sql
    assert "age" in response.sql
```

---

## 5. Stage 5: Multi-Database Support

### 5.1 Universal DB Interface

```python
# sql_cli/db.py

from dataclasses import dataclass
from typing import Optional, Generator
import sqlite3
from sqlalchemy import create_engine, text

@dataclass
class DBInfo:
    """Database connection info."""
    db_type: str  # "sqlite", "postgresql", "mysql"
    uri: str      # Connection URI
    dialect: str  # SQL dialect name
    
# Unified database interface
class UnifiedDatabase:
    """Multi-database unified interface."""
    
    SUPPORTED_TYPES = ["sqlite", "postgresql", "mysql"]
    
    def __init__(self, db_uri: str):
        """Initialize database connection."""
        self.uri = db_uri
        self.type = self._detect_type(db_uri)
        self.conn = self._connect()
    
    def _detect_type(self, uri: str) -> str:
        """Detect database type from URI."""
        if uri.startswith("sqlite://"):
            return "sqlite"
        elif uri.startswith("postgresql://") or uri.startswith("postgres://"):
            return "postgresql"
        elif uri.startswith("mysql://"):
            return "mysql"
        else:
            raise ValueError(f"Unsupported database type: {uri}")
    
    def _connect(self):
        """Establish connection."""
        if self.type == "sqlite":
            import sqlite3
            path = self.uri.replace("sqlite://", "")
            return sqlite3.connect(path)
        elif self.type == "postgresql":
            from sqlalchemy import create_engine
            return create_engine(self.uri)
        elif self.type == "mysql":
            from sqlalchemy import create_engine
            return create_engine(self.uri)
        else:
            raise ValueError(f"Unsupported type: {self.type}")
    
    def execute(self, query: str, params: tuple = ()) -> Optional[Generator]:
        """Execute query with parameterization."""
        if self.type == "sqlite":
            cursor = self.conn.execute(query, params)
            return (row for row in cursor.fetchall())
        elif self.type in ["postgresql", "mysql"]:
            from sqlalchemy import text
            with self.conn.begin() as trans:
                result = trans.execute(text(query), params)
                return (row._asdict() for row in result)
        else:
            raise ValueError(f"Execute not supported for {self.type}")
    
    def get_schemas(self) -> list:
        """Get database schema information."""
        if self.type == "sqlite":
            return self._get_sqlite_schemas()
        elif self.type == "postgresql":
            return self._get_postgres_schemas()
        elif self.type == "mysql":
            return self._get_mysql_schemas()
        else:
            raise ValueError(f"Get schemas not supported for {self.type}")
    
    def _get_sqlite_schemas(self) -> List[Dict]:
        """Get SQLite schema info."""
        import sqlite3  
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = []
        for table in tables:
            cursor = self.conn.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            schema.append({
                "name": table,
                "columns": columns,
                "is_view": False
            })
        
        return schema
```

### 5.2 Multi-DB Schema Knowledge

```python
# sql_cli/core.py

class SchemaKnowledge:
    """Schema knowledge base for multi-database."""
    
    def __init__(self):
        self.tables: Dict[str, TableDef] = {}
        self.relationships: List[Relationship] = []
        self.indices: Dict[str, IndexDef] = {}
        self.best_practices: List[Rule] = []
    
    def load_from_db(self, db_uri: str):
        """Load schema from database connection."""
        db = UnifiedDatabase(db_uri)
        
        tables = db.get_schemas()
        
        for table in tables:
            self.add_table(table["name"], table["columns"])
    
    def get_schema_for_table(self, table_name: str) -> Optional[Dict]:
        """Get schema info for specific table."""
        if table_name in self.tables:
            return self.tables[table_name].to_dict()
        return None
    
    @classmethod
    def generate_best_practices(
        cls,
        tables: List[Dict],
        db_type: str = "sqlite"
    ) -> List[Rule]:
        """Generate best practices for database."""
        
        rules = []
        
        for table in tables:
            # Rule: Index foreign keys
            for col in table.get("columns", []):
                if col.endswith("_id"):
                    rules.append(Rule(
                        id=f"idx_fk_{table['name']}_{col}",
                        description=f"Add index on '{table['name']}'.{col}",
                        priority="HIGH",
                        db_type=db_type
                    ))
            
            # Rule: Use transactions for writes
            rules.append(Rule(
                id=f"trans_{table['name']}_write",
                description=f"Wrap writes on '{table['name']}' in transaction",
                priority="CRITICAL",  
                db_type=db_type
            ))
        
        return rules
```

### 5.3 Stage 5 Commands

```python
# sql_cli/cli.py

@app.command("db")
@click.option("subcommand", type=Choice(["list", "info", "analyze"]))
@click.option("--uri", required=True, help="Database URI")
@click.option("--format", default="json")
def cmd_db(subcommand: str, uri: str, format: str):
    """Database operations."""
    
    if subcommand == "list":
        result = {
            "databases": [
                {"uri": uri, "type": "sqlite", "status": "active"}
            ]
        }
    elif subcommand == "info":
        db = UnifiedDatabase(uri)
        schema = db.get_schemas()
        result = {"schema": schema}
    elif subcommand == "analyze":
        db = UnifiedDatabase(uri)
        knowledge = SchemaKnowledge.load_from_db(uri)
        rules = knowledge.generate_best_practices(schema, db.type)
        
        result = {
            "schema": schema,
            "best_practices": [{"id": r.id, "desc": r.desc} for r in rules]
        }
    
    return format_json(result, output_format=format)
```

### 5.4 Stage 5 Tests

```python
# sql_cli/tests/test_core.py

from sql_cli.db import UnifiedDatabase
from sql_cli.core import MultiDBSchemaKnowledge

def test_unified_db_init():
    """Test UnifiedDatabase initialization."""
    db = UnifiedDatabase("sqlite:///:memory:")
    assert db.type == "sqlite"
    
    db = UnifiedDatabase("postgresql://postgres@localhost/db")  
    assert db.type == "postgresql"

def test_multi_db_schema_load():
    """Test schema loading for different DB types."""
    for db_type, uri in [("sqlite", "sqlite:///:memory:"), ("postgresql", "postgresql://localhost/db")]:
        db = UnifiedDatabase(uri)
        schemas = db.get_schemas()
        assert isinstance(schemas, list)

def test_schema_best_practices():
    """Test best practice generation."""
    tables = [
        {"name": "orders", "columns": ["id", "user_id", "total"]}
    ]
    
    db_type = "sqlite"
    practices = SchemaKnowledge.generate_best_practices(tables, db_type)
    
    assert len(practices) > 0
    assert any("index" in p.desc.lower() for p in practices)
```

---

## 6. Complete Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           EasySQL v0.5 (Complete)                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐       │
│  │ CLI Interface   │◄──►│ Command Handler │◄──►│ Schema Knowledge│       │
│  │ (JSON/Shell)    │    │ (Stage 3/4/5)   │    │ Base (Stage 5)  │       │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘       │
│         │                    │                    │                       │
│         │                    ▼                    │                       │
│         │         ┌──────────────────────┐        │                       │
│         │         │  SQL Generator       │        │                       │
│         │         │  (Stage 2+ SQLD)     │        │                       │
│         │         └──────────────────────┘        │                       │
│         │                    │                    │                       │
│         │                    ▼                    │                       │
│         │         ┌──────────────────────┐        │       ┌───────────┐    │
│         │         │  Model Router        │        │       │ DB Layer  │    │
│         │         │  (Stage 4 Routing)   │◄────────┼───────┼──(SQLite) │    │
│         │         └──────────────────────┘        │       │(Postgres) │    │
│         │            │        │                    │       │(MySQL)    │    │
│         │            ▼        ▼                    │       └───────────┘    │
│         │  ┌────────────────┴──────────────┐       │                       │
│         │  │ Knowledge Base (SQLP)          │◄──────┘                       │
│         │  │ - Table schemas                │                               │
│         │  │ - Patterns & templates         │                               │
│         │  │ - Best practices               │                               │
│         │  └────────────────────────────────┘                               │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Implementation Timeline

### Phase 1: Write Support (Stage 3) - 2 Weeks

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1 | Write commands, safety layer | `insert`, `update`, `delete` CLI |
| 2 | Transaction support, tests | Write safety tests |

### Phase 2: Natural Language (Stage 4) - 3 Weeks

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1 | Intent parser, entity extraction | NL parsing tests |
| 2 | Model router, SQL generation | NL generation tests |
| 3 | Integration, NL commands | CLI NL command |

### Phase 3: Multi-DB (Stage 5) - 2 Weeks

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1 | UnifiedDB, multi-dialect | Multi-database support |
| 2 | Schema knowledge, optimization | Best practices |

---

## 8. SQLD → SQLP Knowledge Integration

### 8.1 Embedding Strategy

```python
# sql_cli/knowledge.py

import json
import sqlite3
from typing import List, Dict, Optional

class KnowledgeEmbedder:
    """Embed SQL expertise into system."""
    
    def __init__(self, embedder_model: str = "all-MiniLM-L6-v2"):
        self.model = self._load_model(embedder_model)
    
    def embed_schema(self, tables: List[Dict]) -> List[Dict]:
        """Embed table schemas for vector search."""
        embeddings = []
        
        for table in tables:
            # Create embedding key from table structure
            table_def = {
                "name": table["name"], 
                "columns": table["columns"],
                "join_candidates": self._suggest_join_candidates(table)
            }
            
            # Generate vector embedding
            vector = self.model.embed(json.dumps(table_def))
            
            embeddings.append({
                "table_name": table["name"],
                "vector": vector,
                "table_def": table_def
            })
        
        return embeddings
    
    def query_by_pattern(self, tables: List[Dict], pattern: str) -> List[Dict]:
        """Find tables matching query pattern."""
        pattern_embedding = self.model.embed(pattern)
        
        results = []
        for table_embedding in tables:
            similarity = cosine_similarity(
                pattern_embedding, 
                table_embedding["vector"]
            )
            results.append({
                "table": table_embedding["table_name"],
                "similarity": similarity
            })
        
        return sorted(results, key=lambda x: x["similarity"], reverse=True)
```

### 8.2 Best Practices Storage

```python
# sql_cli/knowledge.py

class BestPracticesDB:
    """Store best practices knowledge."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.db.connect(db_path)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize knowledge tables."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS best_practices (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                pattern TEXT,
                priority TEXT,
                db_types TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS query_patterns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                schema_pattern TEXT,
                example_sql TEXT
            );
        """)
    
    def save_practice(self, table_def: Dict):
        """Save best practices for table."""
        for col in table_def["columns"]:
            if col.endswith("_id"):
                self.conn.execute("""
                    INSERT OR REPLACE INTO best_practices
                    (id, name, description, pattern, priority, db_types)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ("fk_idx", "foreign_key_index", f"Index {table_def['name']}.{col}", 
                      "SELECT...JOIN", "HIGH", '["sqlite","postgresql","mysql"]'))
```

---

## 9. Test Coverage Matrix

| Stage | Feature | Test | Pass Criteria |
|-------|---------|------|---------------|
| 2 | Read-only | ALL tests pass | 4/4 existing |
| 3 | Write | write_safety_test | Flag required + safe |
| 3 | Write | write_execute_test | Rows affected correct |
| 4 | NL | nl_intent_parse | Correct intent detected |
| 4 | NL | nl_sql_generation | Valid SQL |
| 5 | MultiDB | unified_db_init | Correct type detected |
| 5 | MultiDB | multi_schema_load | All schemas loaded |

---

## 10. Summary

### Current State
- ✅ Stage 2: Read-only + SQL Generation Complete
- ✅ Tests: 100% Pass Rate (4/4)
- ⏳ Stages 3-5: Targeted for next 7 weeks

### Next Milestones
1. **Week 2**: Write Operations (Stage 3) - Safety First
2. **Week 5**: Natural Language Interface (Stage 4) - Smart Routing
3. **Week 7**: Multi-Database Support (Stage 5) - Unified Layer

### Key Innovation
- **SQLD → SQLP**: Transform from basic syntax to expert knowledge system
- **Safety-First Design**: Write operations require explicit flag
- **Knowledge-Based**: Best practices learned from schemas

---

**EasySQL v0.2.1 Roadmap**: From SQLD to SQLP, building a true SQL expert system.

**Last Updated**: 2024-04-01  
**Version**: 0.2.1-roadmap  
**Status**: Ready for Stage 3 implementation


---

## 14. Phase 1 Status: Write Support Implementation

**Started**: 2024-04-01  
**Current Phase**: Write Support (Stage 3)  
**Completion**: 35%

### Completed Items ✅
- [x] WriteCommands Enum (INSERT/UPDATE/DELETE)
- [x] WriteQueryParams, WriteQueryResult Models
- [x] CLI stubs for write commands

### In Progress 🚧
- [ ] Full WriteQueryParams implementation
- [ ] CLI handler with write flag validation
- [ ] Safety level enforcement
- [ ] Transaction support

### TODO
- [ ] Complete CLI write handlers
- [ ] Write safety tests
- [ ] Integration with existing query engine

**Next Phase**: Phase 2 - Natural Language Processing
