#!/usr/bin/env python3
"""JPA entity source scanner.

This module intentionally handles the first JPA support slice only: reading
annotated Java entity source files and returning an agent-friendly schema
model. Runtime JPQL execution belongs behind a separate Java runner.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional


RELATIONSHIP_ANNOTATIONS = {"OneToOne", "OneToMany", "ManyToOne", "ManyToMany", "ElementCollection"}
ID_ANNOTATIONS = {"Id", "EmbeddedId"}
PERSISTENCE_ANNOTATIONS = {
    "Basic",
    "Column",
    "Convert",
    "Embedded",
    "EmbeddedId",
    "Enumerated",
    "GeneratedValue",
    "Id",
    "JoinColumn",
    "JoinColumns",
    "JoinTable",
    "Lob",
    "ManyToMany",
    "ManyToOne",
    "MapsId",
    "OneToMany",
    "OneToOne",
    "OrderBy",
    "Table",
    "Transient",
    "Version",
}


class CoQueryJPAError(Exception):
    """Structured JPA scan error used by CLI handlers."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _strip_comments(source: str) -> str:
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"//.*", "", source)


def _package_name(source: str) -> Optional[str]:
    match = re.search(r"^\s*package\s+([\w.]+)\s*;", source, flags=re.MULTILINE)
    return match.group(1) if match else None


def _short_annotation_name(raw: str) -> str:
    return raw.rsplit(".", 1)[-1]


def _parse_annotation_text(raw: str) -> dict[str, str]:
    match = re.match(r"@(?P<name>[\w.]+)\s*(?:\((?P<args>.*)\))?\s*$", raw.strip(), flags=re.DOTALL)
    if not match:
        return {"name": "", "args": ""}
    return {
        "name": _short_annotation_name(match.group("name")),
        "args": (match.group("args") or "").strip(),
    }


def _annotation_names(annotations: list[dict[str, str]]) -> list[str]:
    return [item["name"] for item in annotations if item["name"]]


def _annotation_value(
    annotations: list[dict[str, str]],
    annotation_name: str,
    key: str = "name",
) -> Optional[str]:
    for annotation in annotations:
        if annotation["name"] != annotation_name:
            continue
        args = annotation["args"]
        if not args:
            return None

        keyed = re.search(rf"\b{re.escape(key)}\s*=\s*\"([^\"]+)\"", args)
        if keyed:
            return keyed.group(1)

        keyed = re.search(rf"\b{re.escape(key)}\s*=\s*'([^']+)'", args)
        if keyed:
            return keyed.group(1)

        unnamed = re.match(r"\s*\"([^\"]+)\"\s*$", args)
        if unnamed:
            return unnamed.group(1)

        unnamed = re.match(r"\s*'([^']+)'\s*$", args)
        if unnamed:
            return unnamed.group(1)

    return None


def _read_annotation_block(lines: list[str], start_index: int) -> tuple[Optional[str], int]:
    first = lines[start_index].strip()
    if not first.startswith("@"):
        return None, start_index

    block = [first]
    paren_depth = first.count("(") - first.count(")")
    index = start_index
    while paren_depth > 0 and index + 1 < len(lines):
        index += 1
        next_line = lines[index].strip()
        block.append(next_line)
        paren_depth += next_line.count("(") - next_line.count(")")

    return " ".join(block), index + 1


def _class_declaration(source: str) -> Optional[re.Match[str]]:
    return re.search(
        r"(?P<annotations>(?:\s*@[\w.]+(?:\s*\([^{}]*?\))?\s*)*)"
        r"(?P<modifiers>(?:public|protected|private|abstract|final|\s)+)?"
        r"\bclass\s+(?P<name>\w+)",
        source,
        flags=re.DOTALL,
    )


def _class_body(source: str, class_match: re.Match[str]) -> str:
    brace_start = source.find("{", class_match.end())
    if brace_start == -1:
        return ""

    depth = 0
    for index in range(brace_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start + 1 : index]
    return source[brace_start + 1 :]


def _parse_annotations(raw_block: str) -> list[dict[str, str]]:
    matches = re.finditer(r"@[\w.]+(?:\s*\([^@]*?\))?", raw_block, flags=re.DOTALL)
    return [_parse_annotation_text(match.group(0)) for match in matches]


def _field_declaration(line: str) -> Optional[re.Match[str]]:
    if "(" in line or not line.endswith(";"):
        return None
    return re.match(
        r"(?P<modifiers>(?:(?:public|protected|private|static|final|transient|volatile)\s+)*)"
        r"(?P<type>[\w.$<>, ?\[\]]+?)\s+"
        r"(?P<name>\w+)\s*(?:=[^;]*)?;",
        line,
    )


def _getter_declaration(line: str) -> Optional[re.Match[str]]:
    return re.match(
        r"(?P<modifiers>(?:(?:public|protected|private|static|final)\s+)*)"
        r"(?P<type>[\w.$<>, ?\[\]]+?)\s+"
        r"(?P<name>get[A-Z]\w*|is[A-Z]\w*)\s*\(\s*\)",
        line,
    )


def _getter_attribute_name(method_name: str) -> str:
    if method_name.startswith("get"):
        raw = method_name[3:]
    elif method_name.startswith("is"):
        raw = method_name[2:]
    else:
        raw = method_name
    return raw[:1].lower() + raw[1:]


def _attribute_payload(
    name: str,
    java_type: str,
    annotations: list[dict[str, str]],
) -> dict[str, Any]:
    annotation_names = _annotation_names(annotations)
    relationship = next((item for item in annotation_names if item in RELATIONSHIP_ANNOTATIONS), None)
    column_name = _annotation_value(annotations, "Column") or _annotation_value(annotations, "JoinColumn") or name

    return {
        "name": name,
        "java_type": " ".join(java_type.split()),
        "column_name": column_name,
        "id": any(item in ID_ANNOTATIONS for item in annotation_names),
        "relationship": relationship,
        "transient": "Transient" in annotation_names,
        "annotations": annotation_names,
    }


def _scan_members(body: str) -> tuple[list[dict[str, Any]], str]:
    lines = body.splitlines()
    index = 0
    brace_depth = 0
    pending_annotations: list[dict[str, str]] = []
    field_attributes: dict[str, dict[str, Any]] = {}
    property_attributes: dict[str, dict[str, Any]] = {}
    field_access = False
    property_access = False

    while index < len(lines):
        stripped = lines[index].strip()

        if not stripped:
            index += 1
            continue

        if brace_depth == 0 and stripped.startswith("@"):
            annotation_block, next_index = _read_annotation_block(lines, index)
            if annotation_block:
                pending_annotations.extend(_parse_annotations(annotation_block))
                index = next_index
                continue

        if brace_depth == 0:
            field_match = _field_declaration(stripped)
            if field_match:
                modifiers = field_match.group("modifiers") or ""
                annotation_names = _annotation_names(pending_annotations)
                if "Id" in annotation_names or "EmbeddedId" in annotation_names:
                    field_access = True
                if not any(modifier in modifiers.split() for modifier in ("static", "final", "transient")):
                    payload = _attribute_payload(
                        field_match.group("name"),
                        field_match.group("type"),
                        pending_annotations,
                    )
                    field_attributes[payload["name"]] = payload
                pending_annotations = []
                index += 1
                continue

            getter_match = _getter_declaration(stripped)
            if getter_match:
                annotation_names = _annotation_names(pending_annotations)
                if "Id" in annotation_names or "EmbeddedId" in annotation_names:
                    property_access = True
                payload = _attribute_payload(
                    _getter_attribute_name(getter_match.group("name")),
                    getter_match.group("type"),
                    pending_annotations,
                )
                property_attributes[payload["name"]] = payload
                pending_annotations = []
            elif not stripped.startswith("{") and not stripped.startswith("}"):
                pending_annotations = []

        brace_depth += stripped.count("{") - stripped.count("}")
        if brace_depth < 0:
            brace_depth = 0
        index += 1

    if field_access:
        access = "field"
        selected_attributes = field_attributes
    elif property_access:
        access = "property"
        selected_attributes = property_attributes
    else:
        access = "unknown"
        selected_attributes = {
            **{
                name: value
                for name, value in field_attributes.items()
                if any(item in PERSISTENCE_ANNOTATIONS for item in value["annotations"])
            },
            **{
                name: value
                for name, value in property_attributes.items()
                if any(item in PERSISTENCE_ANNOTATIONS for item in value["annotations"])
            },
        }

    filtered = [
        value
        for value in selected_attributes.values()
        if not value["transient"] or value["id"]
    ]
    return filtered, access


def parse_jpa_entity_file(path: Path, project_root: Path) -> Optional[dict[str, Any]]:
    source = _strip_comments(path.read_text(encoding="utf-8"))
    class_match = _class_declaration(source)
    if not class_match:
        return None

    class_annotations = _parse_annotations(class_match.group("annotations") or "")
    class_annotation_names = _annotation_names(class_annotations)
    if "Entity" not in class_annotation_names:
        return None

    class_name = class_match.group("name")
    entity_name = _annotation_value(class_annotations, "Entity") or class_name
    table_name = _annotation_value(class_annotations, "Table") or entity_name
    attributes, access = _scan_members(_class_body(source, class_match))

    return {
        "class_name": class_name,
        "package": _package_name(source),
        "entity_name": entity_name,
        "table_name": table_name,
        "access": access,
        "id_attributes": [item["name"] for item in attributes if item["id"]],
        "attributes": attributes,
        "source": str(path.relative_to(project_root)),
    }


def scan_jpa_project(project_path: str | None) -> dict[str, Any]:
    if not project_path or not project_path.strip():
        raise CoQueryJPAError("missing_jpa_project", "JPA project path is required.")

    root = Path(project_path).expanduser().resolve()
    if not root.exists():
        raise CoQueryJPAError("jpa_project_not_found", f"JPA project path does not exist: {root}.")

    java_files = [root] if root.is_file() and root.suffix == ".java" else sorted(root.rglob("*.java"))
    entities = []
    for java_file in java_files:
        entity = parse_jpa_entity_file(java_file, root if root.is_dir() else root.parent)
        if entity:
            entities.append(entity)

    warnings = []
    if not entities:
        warnings.append("No annotation-based JPA entities were found.")

    return {
        "project_path": str(root),
        "entity_count": len(entities),
        "entities": entities,
        "warnings": warnings,
        "support_level": "source_introspection_only",
    }
