# EasySQL - AI 기반 대화형 SQL 에이전트

**Entry → Junior → Intermediate → Expert → SQL Professional(SQLP)**

AI 가 지원하는 안전한 SQL 개발 도구입니다.

---

## 🚀 Quick Start

### 새로운 버전 (Latest)

```bash
# Interactive mode
python main.py

# JSON Commands (Machine-Readable)

# Schema listing
python main.py --command schema --db example.db --format json

# Query execution (read-only)
python main.py --command query --db example.db \
   --sql "SELECT * FROM users WHERE age>30" --format json

# SQL generation
python main.py --command generate --db example.db \
   --skill select_simple --format json

# Help
python main.py --help
```

---

## 📁 Project Structure

```
/Users/Agent/py/
├── main.py                 # Main entry point (v0.2.0)
│
├── sql_cli/                # Core modules package
│   ├── __init__.py        # Package exports
│   ├── db.py              # SQLite database access
│   ├── contracts.py       # JSON payload models
│   ├── core.py            # SQL generation & validation
│   ├── cli.py             # CLI handler
│   └── tests/
│       └── test_core.py   # Test suite (✅ 4/4 passing)
│
├── README.md              # This file
├── PROJECT_SUMMARY.md     # Executive summary
├── HANDOFF.md             # Handoff documentation (preserved)
│
# Legacy (preserved, not recommended)
├── sql_cli.py             # Original prototype (kept for reference)
└── example.db             # Sample database
```

---

## 🎯 Features

### Interactive Mode
```bash
$ python main.py

=== EasySQL AI Agent ===
1. 테이블 목록 (schema)
2. SQL 생성 (interactive)
3. SQL 생성 (JSON)
4. 스킬 목록
5. AI 대시보드
0. 종료
```

### JSON Commands (Machine-Readable)

✅ **stable JSON contracts** - 모든 출력이 안정적인 JSON 포맷

```json
// Schema response
{
   "ok": true,
   "command": "schema",
   "data": {
     "tables": [
       {"name": "users", "columns": ["id","name","age"]}
     ]
   },
   "error": null
}
```

---

## 📊 SQL Skills (7 Skills)

| Skill ID | Name | Level | Description |
|----------|------|-------|-------------|
| `select_simple` | SELECT | entry | 기본 조회 |
| `select_where` | WHERE | entry | 조건 필터 |
| `join_inner` | JOIN | entry | INNER JOIN |
| `join_left` | JOIN | entry | LEFT JOIN |
| `count` | AGGREGATE | entry | COUNT 집계 |
| `aggregate_group` | AGGREGATE | intermediate | GROUP BY |
| `order` | SORT | entry | ORDER BY |

---

## 🔒 Safety First

All commands default to **READ-ONLY**:
- ✅ SELECT statements only
- ✅ Row limits enforced (max 20)
- ✅ Explicit DB path required
- ✅ No hidden schema mutations
- ⏳ Write operations (with `--write` flag) coming in Stage 3

---

## 🧪 Tests

```bash
$ python sql_cli/tests/test_core.py
==================================================
Running EasySQL core tests
==================================================

[Test] Skills test                  ✅
[Test] Generate test                ✅
[Test] Classification test          ✅
[Test] Validation test              ✅

Results: 4 passed, 0 failed
==================================================
```

**100% Pass Rate** ✅

---

## 📈 Development Stages

### ✅ Stage 1: Read-Only Commands (Complete)
- `schema --db <path>` - List table schemas
- `query --db <path> --sql <query>` - Execute SELECT queries
- Read-only enforcement

### ✅ Stage 2: SQL Generation (Complete)
- Skill-based SQL generation
- 7 SQL skills available
- Validation & safety checks

### ⏳ Stage 3: Write Operations (Next)
- `insert`, `update`, `delete` commands
- Transaction support
- Explicit `--write` flag required

### ⏳ Stage 4: AI Natural Language (Future)
- Natural language → SQL conversion
- LLM integration (optional)
- Model routing (light/balanced/pro)

### ⏳ Stage 5: Multi-Database (Future)
- PostgreSQL support
- MySQL support  
- Unified API

---

## 🎯 Usage Examples

### 1. Interactive Mode

```bash
$ python main.py

# Menu options:
# 1 - Schema listing
# 2 - Interactive SQL build
# 3 - JSON SQL generation
# 4 - Skills list
# 5 - AI dashboard
# 0 - Exit
```

### 2. Query Execution

```bash
# Simple query
$ python main.py --command query --db example.db --sql "SELECT * FROM users" --format json

# With conditions
$ python main.py --command query --db example.db --sql "SELECT * FROM users WHERE age > 30" --format json
```

### 3. Schema Listing

```bash
$ python main.py --command schema --db example.db --format json
{
   "ok": true,
   "command": "schema",
   "data": {
       "tables": [
           {"name": "users", "columns": ["id", "name", "age"]}
       ]
    },
   "error": null
}
```

### 4. SQL Generation

```bash
$ python main.py --command generate --db example.db --skill select_simple --format json

$ python main.py --command generate --db example.db --skill join_inner --format json
```

---

## 📚 Legacy Files (Preserved)

The following files have served their purpose and are now preserved:

| File | Status | Description |
|------|--------|-------------|
| `sql_cli.py` | ⚠️ Preserved | Original interactive prototype - kept for reference |
| `HANDOFF.md` | ⚠️ Preserved | Handoff documentation - roadmap reference |

**Use these for reference only. The latest version is `main.py` + `sql_cli/` package.**

---

## 🤝 Contributing

1. ✅ Small slices only - minimal changes
2. ✅ Tests required for all features  
3. ✅ No breaking changes without notice
4. ✅ Follow 4-stage harness (Plan → Review → Execute → Verify)

---

## 📖 Documentation

| File | Description |
|------|-------------|
| [`README.md`](./README.md) | This file - user guide |
| [`PROJECT_SUMMARY.md`](./PROJECT_SUMMARY.md) | Executive summary |
| [`HANDOFF.md`](./HANDOFF.md) | Roadmap reference (preserved) |
| [`contracts.py`](./sql_cli/contracts.py) | JSON contract specification |
| [`test_core.py`](./sql_cli/tests/test_core.py) | Test suite |

---

## 🎯 Quick Reference

```bash
# Interactive CLI
python main.py

# JSON commands
python main.py --command schema --db example.db
python main.py --command query --db example.db --sql "SELECT * FROM users"
python main.py --command generate --db example.db --skill select_simple

# Help
python main.py --help

# Version
python main.py --version

# Tests
python sql_cli/tests/test_core.py
```

---

## 📊 Status Summary

| Metric | Value |
|--------|-------|
| **Version** | v0.2.0 |
| **Status** | Stable (Stage 2) |
| **Tests** | ✅ 4/4 passing (100%) |
| **Commands** | ✅ schema, query, generate |
| **Safety** | ✅ Read-only enforced |
| **Skills** | ✅ 7 implementations |

---

**EasySQL** - From SQLD to SQLP, one safe query at a time.

_Last Updated: 2024-04-01 | Status: Stable | Tests: 4/4_ ✅
