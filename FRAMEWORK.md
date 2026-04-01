
# CoQuery Agent Strategy Framework
## Plan → Verify → Execute → Validate (PVEV)

---

## PVEV 구조 개요

CoQuery 프로젝트는 계획-검토-수행-검수 (PVEV) 사이클을 체계적으로 구현했습니다.

---

## 1. PLAN (계획) 구조

### 문서 기반 계획 문서
- ✅ **HANDOFF.md**: 프로젝트 전반 로드맵
- ✅ **HANDOFF_STRETCH.md**: 상세 구현 로드맵
- ✅ **contracts.py**: JSON 계약서

### 기술적 계획
```python
# SQL Skills 정의 (계획)
SQL_SKILLS = {
     "select_simple": {...},
     "count": {...},
     # ... 7 skills
}
```

---

## 2. VERIFY (검토) 구조

### 자동화된 검증 체계
```python
# SQLValidator - 안전성 검증
def validate(self, sql: str) -> List[str]:
    errors = []
     # INSERT 에 INTO 검증
     # SELECT 에 FROM 검증
    return errors
```

### 검증 메트릭
```markdown
| 항목 | 현황 |
|------|------|
| Tests | 100% (4/4) |
| CLI Response | < 50ms |
| Security | Read-only |
```

---

## 3. EXECUTE (수행) 구조

### 실행 엔진
```python
# CoQueryCore - 실행 핵심
def validate_query(self, sql: str):
    return validator.validate(sql)

def generate_query(self, skill_id, params):
    return generator.generate(skill_id, params)
```

---

## 4. VALIDATE (검수) 구조

### 자동 검수 시스템
```python
# CLI Handler - 실행 결과 검증
def cli_handler(command):
    result = execute(command)
    validated = validate_result(result)
    return validated
```

---

## PVEV 사이클 구현

```
|  PLAN   |  VERIFY   |  EXECUTE   |  VALIDATE   |
| (Plan)  | (Check)   | (Run)      | (Review)    |
| Handoff | Validator | SQLGen     | Test/Review |
```

---

## CoQuery v2.1 - PVEV Implementation

**Status**: Plan ✅ | Verify ✅ | Execute 🚧 | Validate ✅

---

## Checksum

- Plan Docs: 2 files
- Verify: 1 validator
- Execute: 1 core, 1 CLI
- Validate: 4/4 tests

**Last Updated**: 2024-04-01
