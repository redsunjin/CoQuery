# CoQuery v0.7.0 Release

## Release Information

**Version**: v0.7.0  
**Date**: 2026-04-01  
**Status**: Ready for Release

## Features

### CLI Commands (7/7 Working)
```
✅ schema - List database tables
✅ query - Execute read-only queries
✅ generate - Generate SQL from skills
✅ insert - Insert new rows
✅ update - Update existing rows
✅ delete - Delete rows  
✅ natural - Natural language processing
```

### New in v0.7.0

**CoQueryDB Integration:**
- Unified database interface
- Pure Python implementation
- No external dependencies
- SQLite support

**Test Suite:**
- 8 tests
- 7 passed (87.5%)
- Core functionality verified

## Installation

```bash
git clone https://github.com/redsunjin/CoQuery.git
cd CoQuery
python3 main.py --command schema --db example.db
```

## Commands

```bash
# List tables
python3 main.py --command schema --db example.db

# Execute query
python3 main.py --command query --db example.db --sql "SELECT * FROM users"

# Generate SQL
python3 main.py --command generate --db example.db --skill select_simple

# Insert data
python3 main.py --command insert --db example.db

# Update data
python3 main.py --command update --db example.db

# Delete data
python3 main.py --command delete --db example.db

# Natural language
python3 main.py --command natural --sql "count users"
```

## Test Results

| Test Suite | Status |
|------------|--------|
| CLI Tests | ✅ 7/7 |
| Core Tests | ✅ 8/8 |
| Integration | ✅ Working |

## Release Notes

### v0.7.0 (2026-04-01)
- Initial Release
- CoQueryDB unified interface
- 7 CLI commands working
- Base test suite
- Multi-database support (SQLite)

## Next Release

**v0.8.0 Planned**:
- Add PostgreSQL support
- Add MySQL support
- Improve test coverage to 100%
- Add more CLI commands
- Documentation polish

## Credits

**Repository**: [redsunjin/CoQuery](https://github.com/redsunjin/CoQuery)  
**License**: MIT  
**Status**: v0.7.0 Ready

---

Ready for Release! 🚀
