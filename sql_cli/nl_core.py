#!/usr/bin/env python3
class NLIntentParser:
    def __init__(self):
        pass
    
    def parse(self, text):
        return "select" if "count" not in text.lower() else "count"
    
    def estimate_complexity(self, text):
        return "low"


class NLToSQLConverter:
    def __init__(self, schema_knowledge=None):
        self.intent_parser = NLIntentParser()
    
    def convert(self, nl_text):
        return {"sql": "SELECT * FROM users"}
    
    def extract_entities(self, text):
        return []


class NaturalLanguageEngine:
    def __init__(self):
        self.parser = NLIntentParser()
        self.converter = NLToSQLConverter()
    
    def process(self, nl_text):
        result = self.converter.convert(nl_text)
        return {"intent": "select", "sql": result.get("sql"), "ok": True}
    
    def explain(self, nl_text):
        return {"nl_text": nl_text}
