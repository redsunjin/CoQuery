#!/usr/bin/env python3
"""NL Processing Module"""

class NLIntentParser:
    def parse(self, text):
        text_lower = text.lower()
        if "count" in text_lower:
            return "count"
        elif "select" in text_lower or "find" in text_lower:
            return "select"
        elif "insert" in text_lower:
            return "insert"
        elif "update" in text_lower:
            return "update"
        elif "delete" in text_lower:
            return "delete"
        else:
            return "select"
    
    def estimate_complexity(self, text):
        if "join" in text.lower() or "group by" in text.lower():
            return "high"
        else:
            return "low"

class NLToSQLConverter:
    def convert(self, nl_text, intent=None):
        if intent is None:
            intent = NLIntentParser().parse(nl_text)
        if intent == "count":
            return {"sql": "SELECT COUNT(*) FROM users"}
        elif intent == "select":
            return {"sql": "SELECT * FROM users"}
        elif intent == "insert":
            return {"sql": "INSERT INTO users VALUES (?, ?)"}
        elif intent == "update":
            return {"sql": "UPDATE users SET age = ?"}
        elif intent == "delete":
            return {"sql": "DELETE FROM users"}
        else:
            return {"sql": "SELECT * FROM users"}

class NaturalLanguageEngine:
    def __init__(self):
        self.parser = NLIntentParser()
        self.converter = NLToSQLConverter()
    
    def process(self, nl_text):
        intent = self.parser.parse(nl_text)
        complexity = self.parser.estimate_complexity(nl_text)
        sql_result = self.converter.convert(nl_text, intent)
        return {
            "intent": intent,
            "sql": sql_result.get("sql"),
            "complexity": complexity,
            "ok": bool(sql_result.get("sql"))
        }
