#!/usr/bin/env python3
"""Natural-language processing helpers for CoQuery."""

from __future__ import annotations

from sql_cli.knowledge_planner import build_natural_context, can_answer_natural_locally
from sql_cli.llm_registry import LLMProviderClient, LLMProviderRegistry


class NLIntentParser:
    def parse(self, text: str) -> str:
        text_lower = text.lower()
        if "count" in text_lower:
            return "count"
        if "select" in text_lower or "find" in text_lower or "show" in text_lower:
            return "select"
        if "insert" in text_lower or "add" in text_lower:
            return "insert"
        if "update" in text_lower or "modify" in text_lower:
            return "update"
        if "delete" in text_lower or "remove" in text_lower:
            return "delete"
        return "select"

    def estimate_complexity(self, text: str) -> str:
        if "join" in text.lower() or "group by" in text.lower():
            return "high"
        return "low"


class NLToSQLConverter:
    def convert(self, nl_text: str, intent: str | None = None) -> dict[str, str]:
        if intent is None:
            intent = NLIntentParser().parse(nl_text)
        if intent == "count":
            return {"sql": "SELECT COUNT(*) FROM users"}
        if intent == "select":
            return {"sql": "SELECT * FROM users"}
        if intent == "insert":
            return {"sql": "INSERT INTO users VALUES (?, ?)"}
        if intent == "update":
            return {"sql": "UPDATE users SET age = ?"}
        if intent == "delete":
            return {"sql": "DELETE FROM users"}
        return {"sql": "SELECT * FROM users"}


class NaturalLanguageEngine:
    def __init__(self, provider_name: str | None = None, db_target: str | None = "example.db"):
        self.provider_name = provider_name
        self.db_target = db_target
        self.parser = NLIntentParser()
        self.converter = NLToSQLConverter()

    def process(self, nl_text: str) -> dict[str, object]:
        complexity = self.parser.estimate_complexity(nl_text)
        intent = self.parser.parse(nl_text)
        sql_result = self.converter.convert(nl_text, intent)
        sql = sql_result.get("sql")
        knowledge_context = build_natural_context(self.db_target, intent, complexity)

        if self.provider_name and can_answer_natural_locally(intent, complexity, sql, knowledge_context):
            return {
                "intent": intent,
                "sql": sql,
                "complexity": complexity,
                "confidence": 0.35,
                "provider_name": None,
                "provider_kind": None,
                "model_name": None,
                "requested_provider_name": self.provider_name,
                "provider_skipped": True,
                "knowledge_context": knowledge_context,
                "mode": "local_knowledge",
                "ok": bool(sql),
            }

        if self.provider_name:
            profile = LLMProviderRegistry().get_profile(self.provider_name)
            result = LLMProviderClient(profile).generate_structured_sql(nl_text)
            return {
                "intent": result["intent"],
                "sql": result["sql"],
                "complexity": complexity,
                "confidence": result["confidence"],
                "provider_name": result["provider_name"],
                "provider_kind": result["provider_kind"],
                "model_name": result["model_name"],
                "requested_provider_name": self.provider_name,
                "provider_skipped": False,
                "knowledge_context": knowledge_context,
                "mode": "provider",
                "ok": bool(result["sql"]),
            }

        return {
            "intent": intent,
            "sql": sql,
            "complexity": complexity,
            "confidence": 0.25,
            "provider_name": None,
            "provider_kind": None,
            "model_name": None,
            "requested_provider_name": None,
            "provider_skipped": False,
            "knowledge_context": knowledge_context,
            "mode": "heuristic",
            "ok": bool(sql),
        }
