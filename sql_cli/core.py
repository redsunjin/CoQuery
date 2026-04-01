from . import nl_core

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core.py - SQL generation and validation core
Entry → Junior → Intermediate → Expert → SQLP
"""

from typing import List, Dict, Any, Optional


# ==================== SQL Skills ====================
SQL_SKILLS = {
    "select_simple": {
        "name": "SELECT 기본 조회",
        "category": "SELECT",
        "level": "entry",
        "description": "단순 테이블 조회",
        "example": "users 테이블 조회",
        "pattern": "SELECT {cols} FROM {table}",
     },
    "select_where": {
        "name": "WHERE 조건부 조회",
        "category": "SELECT",
        "level": "entry",
        "description": "조건 필터링",
        "example": "age > 30 사용자 조회",
        "pattern": "SELECT {cols} FROM {table} WHERE {where}",
     },
    "join_inner": {
        "name": "INNER JOIN 조회",
        "category": "JOIN",
        "level": "entry",
        "description": "두 테이블 조인",
        "example": "users 와 orders 조인",
        "pattern": "SELECT {cols} FROM {table1} JOIN {table2} ON {on}",
     },
    "join_left": {
        "name": "LEFT JOIN 조회",
        "category": "JOIN",
        "level": "entry",
        "description": "왼쪽 테이블 전체 + 조건부",
        "example": "모든 사용자 + 주문",
        "pattern": "SELECT {cols} FROM {table1} LEFT JOIN {table2} ON {on}",
     },
    "count": {
        "name": "COUNT 집계",
        "category": "AGGREGATE",
        "level": "entry",
        "description": "행수 계산",
        "example": "사용자 총수",
        "pattern": "SELECT COUNT(*) FROM {table}",
     },
    "aggregate_group": {
        "name": "GROUP BY 집계",
        "category": "AGGREGATE",
        "level": "intermediate",
        "description": "그룹별 집계",
        "example": "department 별 평균",
        "pattern": "SELECT {group}, COUNT(*) FROM {table} GROUP BY {group}",
     },
    "order": {
        "name": "ORDER BY 정렬",
        "category": "SORT",
        "level": "entry",
        "description": "정렬 조회",
        "example": "나이 오름차순",
        "pattern": "SELECT {cols} FROM {table} ORDER BY {sort}",
     },
}


class SQLValidator:
    """SQL 검증기"""

    def validate(self, sql: str) -> List[str]:
        """Validate SQL syntax safety"""
        errors = []
        sql_upper = sql.strip().upper()
        
        if sql_upper.startswith("SELECT"):
            if "FROM" not in sql_upper:
                errors.append("SELECT 에 FROM 필요")
        elif sql_upper.startswith("INSERT"):
            if "INTO" not in sql_upper:
                errors.append("INSERT 에 INTO 필요")
        elif sql_upper.startswith("UPDATE"):
            if "SET" not in sql_upper:
                errors.append("UPDATE 에 SET 필요")
        elif sql_upper.startswith("DELETE"):
            if "WHERE" not in sql_upper:
                errors.append("DELETE 에 WHERE 선택사항")
        
        return errors

    def classify(self, sql: str) -> str:
        """Classify SQL operation type"""
        sql_upper = sql.strip().upper().split()[0] if sql.strip() else ""
        
        if "SELECT" in sql_upper:
            return "read"
        elif "INSERT" in sql_upper or "UPDATE" in sql_upper or "DELETE" in sql_upper or "CREATE" in sql_upper or "DROP" in sql_upper:
            return "write"
        else:
            return "unknown"


class SQLGenerator:
    """SQL 생성기"""

    def generate(self, skill_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SQL from structured parameters"""
        skill = SQL_SKILLS.get(skill_id)
        if not skill:
            return {
                "error": f"Skill not found: {skill_id}",
            }

        table = params.get("table", "users")
        cols = params.get("cols", "*")
        where = params.get("where", "")

        pattern = skill["pattern"]
        sql = pattern.format(table=table, cols=cols, where=where)

        warnings = []
        if cols == "*":
            warnings.append("SPECIFIC_COLUMNS recommended")

        return {
            "skill_id": skill_id,
            "sql": sql.upper(),
            "warnings": warnings,
        }


class EasySQLCore:
    """EasySQL 핵심 로직"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_sql_skill(self, skill_id: str) -> Dict[str, Any]:
        """Get skill definition"""
        return SQL_SKILLS.get(skill_id, {})

    def list_skills(self) -> List[Dict[str, Any]]:
        """List all available skills"""
        return list(SQL_SKILLS.values())

    def classify_query(self, sql: str) -> str:
        """Classify query as read/write"""
        validator = SQLValidator()
        return validator.classify(sql)

    def validate_query(self, sql: str) -> List[str]:
        """Validate SQL safety"""
        validator = SQLValidator()
        return validator.validate(sql)

    def generate_query(self, skill_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SQL from skill"""
        generator = SQLGenerator()
        return generator.generate(skill_id, params)



# ============================
# Natural Language Processing (Phase 2)
# ============================

# ============================
# Natural Language Processing (Phase 2)
# ============================

# ============================
# Natural Language Processing (Phase 2)
# ============================

# ============================
# Natural Language Processing (Phase 2)
# ============================

# ============================
# Natural Language Processing (Phase 2)
# ============================


# ============================
# Natural Language Processing (Phase 2)
# ============================

# ============================
# Natural Language Processing (Phase 2)
# ============================


# ============================
# Natural Language Processing (Phase 2)
# ============================
