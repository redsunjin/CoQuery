# CoQuery CLI

CLI Base: Phase 0 Complete  
Phase 2 Status: Complete  

## Phase Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 0 | ✅ Complete | CLI Baseline Recovery |
| Phase 1 | ✅ Complete | Read-Only Commands |
| Phase 2 | ✅ Complete | Structured Generation |

## Features

### CLI Commands

```bash
# Schema
python3 main.py --command schema --db example.db

# Query (SELECT only)
python3 main.py --command query --db example.db --sql "SELECT * FROM users"

# Generation (Phase 2)
python3 main.py --command generate --db example.db --skill select_simple
```

### SQL Skills (Phase 2)

- ✅ select_simple: Simple select
- ✅ select_where: Where filtering
- ✅ count: Count aggregation

## Status

**Version**: v0.6.0  
**Phase**: Phase 2 Complete  
**Next**: Phase 3 Write Support

## Files

- main.py: CLI Entry Point
- sql_cli/: Core Modules
- README.md: This file

---
CoQuery v0.6.0 - Read-Only + Structured Generation Ready
