# CoQuery Todo List

**Version**: 0.6.0-Ready Recovery  
**Session**: Continue Across Sessions (Memorize This)  
**Next Action**: Phase 0 - CLI Baseline Recovery

---

## 🎯 Phase 0: CLI Baseline Recovery

### Priority 1: Fix main.py

**Goal**: CLI command routing restored

**Tasks:**
```
[ ] 1. Fix command routing in main.py
    - Handle --command flag
    - Dispatch to appropriate handler
    - Support schema, query, generate commands
    
[ ] 2. Verify single test case
    python3 main.py --command schema --db example.db --format json
    
[ ] 3. Add error handling
    - Invalid command handling
    - Missing parameter handling
```

**Success:** Commands work correctly

---

### Priority 2: Fix CLI Handler

**Goal**: CLI stable and importable

**Tasks:**
```
[ ] 1. Fix click dependency issue
    - Use optional import pattern
    - Move CLI imports to runtime
    
[ ] 2. Fix imports in __init__.py
    - Remove eager CLI import
    - Use lazy import pattern
    
[ ] 3. Fix handlers in cli.py
    - Fix format_json reference
    - Fix UnifiedDatabase reference
```

**Success:** `python3 -c "import sql_cli.core"` works

---

### Priority 3: Fix Tests

**Goal**: Test core module runnable

**Tasks:**
```
[ ] 1. Fix indentation errors in test_core.py
    - line 140 and other errors
    
[ ] 2. Add minimal working test
    - One simple test case
    
[ ] 3. Document test command
    python3 sql_cli/tests/test_core.py
```

**Success:** Tests pass without errors

---

### Priority 4: Update Docs

**Goal**: Docs reflect actual state

**Tasks:**
```
[ ] 1. Update HANDOFF.md
    - Phase claims to actual state
    - Remove false completion claims
    
[ ] 2. Update STAGE_STATUS.md
    - Phase status based on tests
    - Accurate Phase claims
    
[ ] 3. Document working baseline
```

**Success:** Docs truthful and accurate

---

## ✅ Phase 0 Completion Criteria

```
✓ main.py --command schema works
✓ Imports work without click
✓ Tests runnable
✓ Docs truthful
```

---

## 📝 Next Phases (After Phase 0)

### Phase 1: Read-Only Commands
```
[ ] schema command working
[ ] query command working
```

### Phase 2: Structured Generation
```
[ ] SQL generation stable
[ ] Write safe (if enabled)
```

### Phase 3: Write Support
```
[ ] INSERT/UPDATE/DELETE
[ ] Write flag safety
```

### Phase 4: Natural Language
```
[ ] Intent parser
[ ] NL to SQL converter
```

### Phase 5: Knowledge Base
```
[ ] KB integration
[ ] Optimizer
```

### Phase 6: Multi-DB
```
[ ] UnifiedDatabase
[ ] Postgres/MySQL
```

---

## 🔄 Session Continuation

### How to Continue
1. Remember this file: `EASY_SQL_TODO.md`
2. Remember this file: `EASY_SQL_CHECKPOINT.md`
3. Remember next step: Phase 0 Priority 1

### Checkpoint Summary
```
Phase: 0 - Recovery
Next: main.py command routing
Status: Ready to start
```

---

## 📋 Quick Start Commands

**Test Status:**
```bash
# Test CLI
python3 main.py --command schema --db example.db --format json

# Test Import
python3 -c "import sql_cli.core"

# Test Tests
python3 sql_cli/tests/test_core.py
```

**Expected:** All commands work without errors

---

Last Updated: 2026-04-01  
Session Safe: This file continues across sessions  
Next Action: Execute Phase 0 Priority 1
