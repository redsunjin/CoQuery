#!/usr/bin/env python3
"""Local DB/JPA knowledge rules for CoQuery."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
DIALECT_DIR = KNOWLEDGE_ROOT / "dialects"
SAFETY_DIR = KNOWLEDGE_ROOT / "safety"
DIALECT_ALIASES = {
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "sqlite": "sqlite",
    "mysql": "mysql",
    "mariadb": "mysql",
    "jpa": "jpql",
    "jpql": "jpql",
}


class CoQueryKnowledgeError(Exception):
    """Structured local knowledge lookup error."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def list_dialects() -> list[str]:
    return sorted(path.stem for path in DIALECT_DIR.glob("*.json"))


def normalize_dialect(dialect: str | None) -> str:
    raw = (dialect or "").strip().lower()
    if not raw:
        raise CoQueryKnowledgeError("missing_dialect", "Dialect is required.")
    normalized = DIALECT_ALIASES.get(raw)
    if not normalized:
        raise CoQueryKnowledgeError("unknown_dialect", f"Unknown dialect: {dialect}.")
    return normalized


def load_dialect_rules(dialect: str | None) -> dict[str, Any]:
    normalized = normalize_dialect(dialect)
    path = DIALECT_DIR / f"{normalized}.json"
    if not path.exists():
        raise CoQueryKnowledgeError("knowledge_not_found", f"Dialect rules not found: {normalized}.")
    payload = _read_json(path)
    payload["rule_path"] = str(path.relative_to(REPO_ROOT))
    return payload


def load_write_rules() -> dict[str, Any]:
    path = SAFETY_DIR / "write_rules.json"
    if not path.exists():
        raise CoQueryKnowledgeError("knowledge_not_found", "Write safety rules not found.")
    payload = _read_json(path)
    payload["rule_path"] = str(path.relative_to(REPO_ROOT))
    return payload


def _topic_from_dialect(payload: dict[str, Any], topic: str) -> dict[str, Any]:
    topic_map = {
        "statements": "statement_support",
        "statement_support": "statement_support",
        "schema": "schema_introspection",
        "schema_introspection": "schema_introspection",
        "pagination": "pagination",
        "upsert": "upsert",
        "parameters": "parameter_styles",
        "parameter_styles": "parameter_styles",
        "sources": "official_sources",
        "safety": "safety_notes",
        "status": "coquery_status",
        "types": "type_mappings",
        "type_mappings": "type_mappings",
        "operators": "operators",
        "joins": "joins",
        "constraints": "constraints",
    }
    key = topic_map.get(topic)
    if not key or key not in payload:
        raise CoQueryKnowledgeError("unknown_topic", f"Unknown knowledge topic for dialect {payload.get('dialect')}: {topic}.")
    return {
        "topic": topic,
        "value": payload[key],
        "dialect": payload["dialect"],
        "rule_path": payload["rule_path"],
    }


def lookup_knowledge(dialect: str | None = None, topic: Optional[str] = None) -> dict[str, Any]:
    normalized_topic = (topic or "overview").strip().lower()

    if normalized_topic in {"write_safety", "write_rules"}:
        return {
            "kind": "safety",
            "topic": normalized_topic,
            "value": load_write_rules(),
        }

    if not dialect:
        if normalized_topic in {"overview", "dialects"}:
            return {
                "kind": "overview",
                "available_dialects": list_dialects(),
                "safety_topics": ["write_safety"],
                "knowledge_root": str(KNOWLEDGE_ROOT.relative_to(REPO_ROOT)),
            }
        raise CoQueryKnowledgeError("missing_dialect", "Dialect is required for this topic.")

    payload = load_dialect_rules(dialect)
    if normalized_topic == "overview":
        return {
            "kind": "dialect",
            "topic": "overview",
            "value": payload,
        }

    return {
        "kind": "dialect_topic",
        "topic": normalized_topic,
        "value": _topic_from_dialect(payload, normalized_topic),
    }
