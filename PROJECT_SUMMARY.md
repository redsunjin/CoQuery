# CoQuery - Project Summary v0.7.0

**AI 기반 대화형 SQL 에이전트**  
**Entry → Junior → Intermediate → Expert → SQL Professional(SQLP)**

---

## 🎉 Current Status: READY

```
✅ All tests passing (4/4)
✅ JSON contracts stable
✅ Read-only enforced
✅ CLI ready for all modes
```

---

## 📁 Project Structure

```
/Users/Agent/py/
├── main.py                     # CLI Entry Point (v0.7.0)
├── README.md                   # Documentation
├── HANDOFF.md                  # Handoff documentation
├── PROJECT_SUMMARY.md          # Summary (this file)
└── sql_cli/                    # Core modules
     ├── __init__.py          # Package exports
     ├── db.py                # SQLite access layer
     ├── contracts.py         # JSON payload models
     ├── core.py              # SQL generation & validation
     ├── cli.py               # CLI handler
     └── tests/
         └── test_core.py     # Test suite (4 tests)
```

---

## 🚀 Features Implemented

### 1. Interactive CLI
- Menu-driven interface
- SQL generation from structured inputs
- Skill-based query builder

### 2. Stable JSON Commands
- `schema` - List table schemas
- `query` - Execute SELECT queries (read-only)
- `generate` - Generate SQL from skill ID

### 3. Safety Measures
- **Read-only default** (no write without flag)
- **Row limits** (limit 20 by default)
- **Explicit DB path** (no hidden mutations)
- **Validation layer** (syntax checks)

### 4. SQL Skills (7 total)
```
select_simple       - Basic SELECT
select_where        - WHERE-based filtering
join_inner          - INNER JOIN
join_left           - LEFT JOIN
count               - COUNT aggregation
aggregate_group     - GROUP BY
order               - ORDER BY sorting
```

---

## 📊 Test Results

```bash
$ python sql_cli/tests/test_core.py
==================================================
Running CoQuery core tests
==================================================

[Test] Skills test                 ✅
[Test] Generate test               ✅
[Test] Classification test         ✅
[Test] Validation test             ✅

Results: 4 passed, 0 failed
==================================================
```

---

## 🎯 Usage Examples

### Interactive Mode
```bash
$ python main.py

### Menu
1. 테이블 목록 (schema)
2. 쿼리 실행 (query)
3. SQL 생성 (generate)
4. 스킬 목록
0. 종료
```

### JSON Commands
```bash
# Schema listing
$ python main.py --command schema --db example.db --format json
# Output: JSON with table info

# Query execution
$ python main.py --command query --db example.db \
   --sql "SELECT * FROM users WHERE age>30" --format json
# Output: JSON with result rows

# SQL generation
$ python main.py --command generate --db example.db \
   --skill select_simple --format json
# Output: Generated SQL with warnings
```

---

## 📈 Progress Stages

### ✅ Stage 1: Read-Only (Complete)
- Schema command
- Query execution (read-only)
- Read/write enforcement

### ✅ Stage 2: SQL Generation (Complete)  
- Skill-based generation
- 7 SQL skills
- Validation & warnings

### ⏳ Stage 3: Write Support (To Do)
- INSERT/UPDATE/DELETE
- Explicit write flag
- Transaction support

### ⏳ Stage 4: AI Natural Language (To Do)
- Natural → SQL conversion
- LLM integration
- Model routing

### ⏳ Stage 5: Multi-DB Support (To Do)
- PostgreSQL
- MySQL
- Unified API

---

## 🔒 Safety Profile

| Feature | Status |
|---------|--------|
| Read-only default | ✅ Enforced |
| Row limits | ✅ Max 20 |
| Explicit DB path | ✅ Required |
| Validation | ✅ Syntax checks |
| Write flag | ⏳ Pending |

---

## 📖 Quick Start

```bash
# 1. Run interactive mode
$ python main.py

# 2. List schemas (JSON)
$ python main.py --command schema --db example.db --format json

# 3. Execute query (JSON)
$ python main.py --command query --db example.db \
   --sql "SELECT * FROM users LIMIT 10" --format json

# 4. Generate SQL (JSON)
$ python main.py --command generate --db example.db \
   --skill select_simple --format json
```

---

## 🤝 Contributing

- Small slices only
- Tests required  
- No breaking changes
- Follow 4-stage harness

---

## 📝 Next Steps

1. Implement write commands (INSERT/UPDATE/DELETE)
2. Add natural language support
3. Integrate with RFS-CLI
4. Add multi-database support
5. Performance benchmarks

---

## 📎 References

- [main.py](./main.py) - CLI Entry Point
- [HANDOFF.md](./HANDOFF.md) - Project Roadmap
- [README.md](./README.md) - User Guide
- [contracts.py](./sql_cli/contracts.py) - JSON Spec
- [test_core.py](./sql_cli/tests/test_core.py) - Tests

---

**CoQuery v0.7.0** - From SQLD to SQLP, one safe query at a time.

Last Updated: 2026-04-02  
Status: Stable (Stage 2)  
Score: 4/4 tests ✅
