#!/usr/bin/env python3
"""Local-knowledge-first planning helpers."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from sql_cli.dialect_rules import CoQueryKnowledgeError, lookup_knowledge


DIALECT_SCHEME_ALIASES = {
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "sqlite": "sqlite",
    "mysql": "mysql",
}


def infer_dialect_from_db_target(db_target: str | None) -> str:
    raw = (db_target or "").strip()
    if not raw or "://" not in raw:
        return "sqlite"

    scheme = urlparse(raw).scheme.lower()
    return DIALECT_SCHEME_ALIASES.get(scheme, scheme)


def _compact_topic_value(topic: str, value: dict[str, Any]) -> dict[str, Any]:
    topic_value = value.get("value")
    compact: dict[str, Any] = {
        "topic": topic,
        "dialect": value.get("dialect"),
        "rule_path": value.get("rule_path"),
    }

    if topic == "status":
        compact["value"] = topic_value
    elif topic == "statements" and isinstance(topic_value, dict):
        compact["statement_count"] = len(topic_value)
    elif topic == "parameters":
        compact["parameter_styles"] = topic_value
    elif topic == "safety":
        compact["note_count"] = len(topic_value) if isinstance(topic_value, list) else 0
    else:
        compact["available"] = topic_value is not None

    return compact


def _compact_safety_value(topic: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "topic": topic,
        "rule_path": value.get("rule_path"),
        "rule_set": value.get("rule_set"),
        "requires_write_flag": value.get("requires_write_flag"),
        "write_operations": value.get("write_operations", []),
    }


def build_knowledge_context(
    db_target: str | None,
    topics: list[str],
    reason: str,
) -> dict[str, Any]:
    dialect = infer_dialect_from_db_target(db_target)
    deduped_topics = list(dict.fromkeys(topics))
    context: dict[str, Any] = {
        "knowledge_first": True,
        "reason": reason,
        "dialect": dialect,
        "topics": [],
        "rule_paths": [],
        "errors": [],
    }

    for topic in deduped_topics:
        try:
            if topic == "write_safety":
                result = lookup_knowledge(topic=topic)
                entry = _compact_safety_value(topic, result["value"])
            else:
                result = lookup_knowledge(dialect=dialect, topic=topic)
                entry = _compact_topic_value(topic, result["value"])

            context["topics"].append(entry)
            rule_path = entry.get("rule_path")
            if rule_path and rule_path not in context["rule_paths"]:
                context["rule_paths"].append(rule_path)
        except CoQueryKnowledgeError as exc:
            context["errors"].append(
                {
                    "topic": topic,
                    "code": exc.code,
                    "message": exc.message,
                }
            )

    context["topic_names"] = [entry["topic"] for entry in context["topics"]]
    context["complete"] = not context["errors"]
    return context


def build_generation_context(db_target: str | None, skill_id: str | None) -> dict[str, Any]:
    topics = ["status", "statements", "schema", "parameters", "safety"]
    normalized_skill = (skill_id or "").strip().lower()
    if "join" in normalized_skill:
        topics.append("joins")
    return build_knowledge_context(db_target, topics, "generate")


def build_natural_context(db_target: str | None, intent: str, complexity: str) -> dict[str, Any]:
    topics = ["status", "statements", "parameters", "safety"]
    if intent in {"select", "count"}:
        topics.append("schema")
    if intent in {"insert", "update", "delete"}:
        topics.append("write_safety")
    if complexity == "high":
        topics.append("joins")
    return build_knowledge_context(db_target, topics, "natural")


def build_write_context(db_target: str | None, operation: str) -> dict[str, Any]:
    return build_knowledge_context(
        db_target,
        ["status", "statements", "parameters", "safety", "write_safety"],
        f"write:{operation.lower()}",
    )


def can_answer_natural_locally(
    intent: str,
    complexity: str,
    sql: str | None,
    context: dict[str, Any],
) -> bool:
    return (
        bool(sql)
        and complexity == "low"
        and intent in {"select", "count", "insert", "update", "delete"}
        and bool(context.get("complete"))
    )
