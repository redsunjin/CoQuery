#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasySQL - AI 보조 대화형 SQL CLI 에이전트
비전공자를 위한 대화형 SQL 생성 도구
"""

import sqlite3
import sys

DB_FILE = "example.db"

SQL_STYLES = {
    "select": {"name": "SELECT", "desc": "기본 조회"},
    "join": {"name": "JOIN", "desc": "조인 조회"},
    "order": {"name": "ORDER BY", "desc": "정렬 조회"},
    "limit": {"name": "LIMIT", "desc": "제한 조회"},
}

class easySQL:
    def __init__(self):
        self.conn = None
        self.schema = {}

    def connect(self, path=DB_FILE):
        try:
            self.conn = sqlite3.connect(path)
            print(f"[OK] 연결: {path}")
            return True
        except Exception as e:
            print(f"[Error] 연결 실패: {e}")
            return False

    def sample(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
        c.execute("DELETE FROM users")
        c.executemany("INSERT INTO users (name, age) VALUES (?, ?)",
                      [('Alice', 30), ('Bob', 25), ('Charlie', 35), ('Diana', 28), ('Eve', 32)])
        self.conn.commit()
        print("[OK] users 생성")

    def tables(self):
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print("\n[Tables] 테이블:")
        for t in c.fetchall():
            name = t[0]
            c.execute(f"PRAGMA table_info({name})")
            cols = [r[1] for r in c.fetchall()]
            print(f"     {name}: {', '.join(cols)}")

    def build_sql(self):
        skill = input("스킬 (1/2/3/4): ").strip()
        table = input("테이블 (users): ").strip()
        if not table:
            table = "users"
        
        cols = input("컬럼 (*): ").strip()
        if not cols:
            cols = "name,age"
        
        where = input("WHERE 조건 (skip 엔터): ").strip()
        
        sql = f"SELECT {cols} FROM {table}"
        if where:
            sql += f" WHERE {where}"
        
        return sql.upper()

    def create(self):
        print("\n" + "="*50)
        print("EasySQL SQL 생성")
        print("="*50)
        
        print("\n스킬:")
        for i, (sid, data) in enumerate(SQL_STYLES.items(), 1):
            print(f"     {i}. {sid} ({data['name']})")
        
        sql = self.build_sql()
        print(f"\n[SQL] {sql}")
        
        print("\n[Optimize] 제안:")
        if "SELECT *" in sql:
            print("     컬럼 구체화 추천")
        if "ORDER BY" in sql and "LIMIT" not in sql:
            print("     LIMIT 고려")
        
        print("\n[Security] 체크:")
        if "DROP" in sql or "DELETE" in sql:
            print("     주의 필요")
        
        c = input("실행? (y): ").strip().lower()
        if c != 'y':
            print("취소됨")
            return

        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            print(f"\n[Result] {len(rows)} 건")
            for r in rows[:10]:
                print(f"     {r}")
        except Exception as e:
            print(f"[Error] {e}")

    def learn(self):
        print("\n" + "="*50)
        print("EasySQL 학습")
        print("="*50)
        
        guides = [
            ("SELECT", "SELECT * FROM users"),
            ("WHERE", "WHERE age > 25"),
            ("ORDER", "ORDER BY age DESC"),
            ("LIMIT", "LIMIT 10"),
        ]
        
        for title, sql in guides:
            print(f"\n{title}:")
            print(f"     {sql}")

    def menu(self):
        print("\n" + "="*60)
        print("                  EasySQL AI Agent")
        print("="*60)
        print("대화형 SQL 생성 도구")
        print("")
        print("     1. 테이블 목록")
        print("     2. SQL 생성")
        print("     3. 학습모드")
        print("     0. 종료")
        print("="*60)

        while True:
            m = input("\n선택: ").strip()
            if m == "1":
                self.tables()
            elif m == "2":
                self.create()
            elif m == "3":
                self.learn()
            elif m == "0":
                print("\nEasySQL 종료!")
                break
            else:
                print("잘못된 입력")

def main():
    agent = easySQL()
    if agent.connect():
        agent.sample()
        agent.menu()
        agent.conn.close()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
