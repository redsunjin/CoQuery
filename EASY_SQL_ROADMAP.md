# EasySQL 로드맵 (v0.6.0-Ready)

**Base**: Analysis Report v1 (2026-04-01)  
**Status**: Recovery Phase  
**Next**: Phase 1 - CLI Baseline Restoration

---

## 📊 Current State (Based on Analysis)

```
Phase  Status     Problems
────────────────────────────────────────────────────────
Phase 1  Not Started ✗ CLI broken, tests fail
Phase 2  Partial    NL incomplete, placeholders
Phase 3  Partial    KB incomplete, not integrated
Phase 4  Partial    Multi-DB incomplete, dependencies
```

---

## 🎯 Recommended Priority Order

### Phase 0: Recovery (Immediate Priority)

**Goal**: Restore runnable baseline

**Tasks:**
```
[✓] 1. main.py command routing fix
[✓] 2. CLI handler restoration
[✓] 3. __init__.py import fix
[✓] 4. Test integrity restoration
[✓] 5. Documentation truthfulness
```

**Success:**
```bash
python3 main.py --command schema --db example.db --format json  # Works
python3 -c "import sql_cli.core"                               # Works
python3 sql_cli/tests/test_core.py                            # Runs
```

### Phase 1: Read-Only Commands
**Goal**: Stable CLI baseline
**Tasks:** `schema`, `query` commands working

### Phase 2: Structured Generation
**Goal**: SQL generation stable
**Tasks**: Write commands with safety

### Phase 3: Write Support
**Goal**: Safe write operations
**Tasks**: INSERT/UPDATE/DELETE with --write flag

### Phase 4: Natural Language
**Goal**: NL to SQL converter
**Tasks**: Intent parsing, SQL generation

### Phase 5: Knowledge Base
**Goal**: KB integration complete
**Tasks**: Schema knowledge, optimizer

### Phase 6: Multi-DB Support
**Goal**: PostgreSQL/MySQL support
**Tasks**: UnifiedDatabase complete

### Phase 7: Expert System
**Goal**: SQLD → SQLP evolution
**Tasks**: Self-learning, optimization

### Phase 8: Release v1.0
**Goal**: Production ready
**Tasks**: Security, performance, docs

---

## 📋 Execution Strategy

### Strategy: One Slice At A Time

**Rule**: Never mix recovery with feature expansion

**Process:**
1. Plan: Pick one minimal slice
2. Review: Check impact on imports/docs
3. Execute: Implement only that slice
4. Verify: Run tests and baseline commands

---

## 🔄 Active Loop

Until recovery complete:

```
Loop:
  1. Restore runnable baseline
  2. Restore truthful validation
  3. Re-enable feature tracks one by one
  
Stop: When Phase 0 complete
Resume: When Phase 1+ ready
```

---

## 📁 Files Requiring Attention

| File | Status | Action |
|------|--------|--------|
| main.py | BROKEN | Fix command routing |
| cli.py | BROKEN | Fix imports and handlers |
| __init__.py | BROKEN | Fix import order |
| test_core.py | BROKEN | Fix indentation |
| HANDOFF.md | DRIFTED | Truthful status |
| STAGE_STATUS.md | DRIFTED | Truthful status |

---

## ✅ Recovery Criteria

```
✓ main.py works: python3 main.py --command schema --db exam.db --format json
✓ Imports work: python3 -c "import sql_cli.core"
✓ Tests pass: python3 sql_cli/tests/test_core.py
✓ Docs truthful: Phase claims match runtime
```

---

## 🎯 Next Phase

**Immediate**: Phase 0 - Recovery  
**Next**: Phase 1 - Read-Only Commands  
**Timeline**: Start Phase 0, then Phase 1 → 8

---

Last Updated: 2026-04-01  
Status: Phase 0 Recovery Ready  
Next Action: Execute Phase 0 Recovery
