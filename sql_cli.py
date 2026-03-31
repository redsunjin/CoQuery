#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EasySQL - AI 대화형 SQL 에이전트"""

import sqlite3
import sys

DB_FILE = "example.db"

SQL_SKILLS = {
    "select_simple": {"name": "SELECT", "level": "entry"},
    "select_where": {"name": "WHERE 조건", "level": "entry"},
    "join_inner": {"name": "INNER JOIN", "level": "entry"},
    "join_left": {"name": "LEFT JOIN", "level": "entry"},
    "count": {"name": "COUNT 집계", "level": "entry"},
    "group_by": {"name": "GROUP BY", "level": "intermediate"},
}

class EasySQLAgent:
    def __init__(self):
        self.conn = None
        self.schema = {}
        self.ai_model = "light"
        self.level = "entry"
        self.progress = 0

    def connect(self, path=DB_FILE):
        try:
            self.conn = sqlite3.connect(path)
            print("[OK] DB 연결: " + path)
            return True
        except Exception as e:
            print("[Error] 연결 실패: " + str(e))
            return False

    def sample(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
        c.execute("DELETE FROM users")
        c.executemany("INSERT INTO users (name, age) VALUES (?, ?)",
                      [("Alice", 30), ("Bob", 25), ("Charlie", 35), ("Diana", 28)])
        self.conn.commit()
        self.schema['users'] = ['id', 'name', 'age']
        print("[OK] 테이블 생성 완료")

    def list_tables(self):
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print("\n[Tables]:")
        for t in c.fetchall():
            name = t[0]
            cols = self.schema.get(name, ['col'])
            print("     " + name + ": " + ','.join(cols))

    def interactive_build(self):
        print("\n=== 대화형 생성 ===")
        print("     1. select_simple")
        print("     2. select_where")
        print("     3. join_inner")
        skill_input = input("skill 선택 (1-3): ") or "1"
        try:
            skill_idx = int(skill_input)
        except ValueError:
            print("[Error] 숫자 입력 필요")
            return None
        if skill_idx < 1 or skill_idx > 3:
            print("[Error] 1-3 범위")
            return None
        keys = list(SQL_SKILLS.keys())
        skill = SQL_SKILLS.get(keys[skill_idx-1])
        print("     " + skill['name'])
        table = input("table (users): ") or "users"
        cols = input("cols (*): ") or "name,age"
        where = input("where (skip 엔터): ") or ""
        sql = "SELECT " + cols + " FROM " + table
        if where: sql += " WHERE " + where
        return sql.upper()

    def natural_build(self):
        print("\n=== 자연어 생성 ===")
        q = input("질문: ") or ""
        table = "users"
        cols = "*"
        sql = "SELECT " + cols + " FROM " + table
        return sql.upper()

    def create(self):
        print("\n=== SQL 생성 ===")
        mode = input("mode (1대화형/2자연어): ") or "1"
        if mode.strip() == "1":
            sql = self.interactive_build()
        elif mode.strip() == "2":
            sql = self.natural_build()
        else:
            print("[Error] 잘못된 모드")
            return
        if not sql:
            print("[Error] SQL 없음")
            return
        print("\n[SQL] " + sql)
        print("\n[Optimize]:")
        print("     - 구체 컬럼 권장")
        print("     - LIMIT 고려")
        confirm = input("실행 (y): ") or "y"
        if confirm.strip().lower() == 'y':
            try:
                cur = self.conn.cursor()
                cur.execute(sql)
                rows = cur.fetchall()
                print("\n[Result] " + str(len(rows)) + "건")
                for r in rows[:10]:
                    print("     " + str(r))
            except Exception as e:
                print("[Error] " + str(e))
        else:
            print("취소")

    def learn(self):
        print("\n=== 학습 ===")
        print("level: " + self.level + " (" + str(self.progress) + "%)")
        print("\nSQL 가이드:")
        print("   SELECT * FROM users")
        print("   WHERE age > 30")
        print("   ORDER BY age DESC")
        input("엔터 입력")
        self.progress = min(self.progress + 10, 100)

    def skill_manager(self):
        print("\n=== 스킬 관리 ===")
        print("총: " + str(len(SQL_SKILLS)) + ", level: " + self.level)
        for k, v in SQL_SKILLS.items():
            print("     " + k + ": " + v['name'])

    def ai_dashboard(self):
        print("\n=== AI 대시보드 ===")
        print("   light: 빠름")
        print("   balanced: 균형")
        print("   pro: 최고")
        print("   현재: " + self.ai_model)

    def menu(self):
        while True:
            print("\n==============================")
            print("   EasySQL AI Agent (" + self.level + ")")
            print("==============================")
            print("   1. 테이블")
            print("   2. SQL 생성")
            print("   3. 학습")
            print("   4. 스킬")
            print("   5. AI")
            print("   0. 종료")
            ch = input("선택: ") or ""
            if ch == "1":
                self.list_tables()
            elif ch == "2":
                self.create()
            elif ch == "3":
                self.learn()
            elif ch == "4":
                self.skill_manager()
            elif ch == "5":
                self.ai_dashboard()
            elif ch == "0":
                print("\nEasySQL 종료!")
                break
            else:
                print("[Error] 잘못된 입력")

def main():
    agent = EasySQLAgent()
    if agent.connect():
        agent.sample()
        agent.menu()
        agent.conn.close()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
