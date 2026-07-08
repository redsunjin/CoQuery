#!/usr/bin/env python3
"""Built-in practice dataset sandbox for CoQuery."""

from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from sql_cli.llm_registry import CoQueryLLMError, LLMProviderClient, LLMProviderRegistry


DEFAULT_PACK = "sql_basics"
PACK_DIR = Path(__file__).resolve().parents[1] / "practice_packs"
DEFAULT_ATTEMPT_LOG = Path(".coquery") / "practice_attempts.jsonl"
SAFE_PACK_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TRAINING_MODE = "training"


class CoQueryPracticeError(Exception):
    """Structured practice sandbox error."""

    def __init__(self, code: str, message: str, data: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data or {}


def _error(command: str, exc: CoQueryPracticeError) -> dict[str, Any]:
    return {
        "ok": False,
        "command": command,
        "data": exc.data,
        "error": {"code": exc.code, "message": exc.message},
    }


def _success(command: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "command": command, "data": data, "error": None}


def _resolve_pack_id(pack: Optional[str]) -> str:
    pack_id = (pack or DEFAULT_PACK).strip()
    if not pack_id or not SAFE_PACK_RE.match(pack_id):
        raise CoQueryPracticeError("invalid_practice_pack", f"Invalid practice pack id: {pack_id!r}.")
    return pack_id


def _pack_path(pack: Optional[str]) -> Path:
    return PACK_DIR / f"{_resolve_pack_id(pack)}.json"


def _load_pack(pack: Optional[str] = None) -> dict[str, Any]:
    path = _pack_path(pack)
    if not path.exists():
        raise CoQueryPracticeError(
            "practice_pack_not_found",
            f"Practice pack not found: {_resolve_pack_id(pack)}.",
            {"available_packs": [item["id"] for item in _list_pack_summaries()]},
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CoQueryPracticeError(
            "invalid_practice_pack",
            f"Practice pack JSON is invalid: {exc.msg}.",
            {"path": str(path)},
        ) from exc


def _list_pack_summaries() -> list[dict[str, Any]]:
    packs: list[dict[str, Any]] = []
    if not PACK_DIR.exists():
        return packs
    for path in sorted(PACK_DIR.glob("*.json")):
        try:
            pack = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        dataset = pack.get("dataset", {})
        tables = dataset.get("tables", [])
        problems = pack.get("problems", [])
        packs.append(
            {
                "id": pack.get("id", path.stem),
                "title": pack.get("title", path.stem),
                "description": pack.get("description", ""),
                "dataset_id": dataset.get("id"),
                "table_count": len(tables),
                "problem_count": len(problems),
                "path": str(path),
            }
        )
    return packs


def _table_summaries(pack: dict[str, Any], table: Optional[str] = None) -> list[dict[str, Any]]:
    requested = table.strip() if table else None
    tables: list[dict[str, Any]] = []
    for source in pack.get("dataset", {}).get("tables", []):
        if requested and source.get("name") != requested:
            continue
        rows = source.get("rows", [])
        tables.append(
            {
                "name": source.get("name"),
                "description": source.get("description", ""),
                "columns": source.get("columns", []),
                "primary_key": source.get("primary_key", []),
                "foreign_keys": source.get("foreign_keys", []),
                "row_count": len(rows),
            }
        )
    if requested and not tables:
        raise CoQueryPracticeError(
            "practice_table_not_found",
            f"Table not found in practice pack: {requested}.",
            {"pack": pack.get("id"), "available_tables": [t.get("name") for t in pack.get("dataset", {}).get("tables", [])]},
        )
    return tables


def _problem_summaries(pack: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": problem.get("id"),
            "title": problem.get("title"),
            "difficulty": problem.get("difficulty"),
            "prompt": problem.get("prompt"),
            "concepts": problem.get("concepts", []),
            "hint": problem.get("hint"),
        }
        for problem in pack.get("problems", [])
    ]


def _get_problem(pack: dict[str, Any], problem_id: Optional[str]) -> dict[str, Any]:
    requested = (problem_id or "").strip()
    if not requested:
        raise CoQueryPracticeError("missing_problem_id", "practice_grade requires --problem-id.")
    for problem in pack.get("problems", []):
        if problem.get("id") == requested:
            return problem
    raise CoQueryPracticeError(
        "practice_problem_not_found",
        f"Practice problem not found: {requested}.",
        {"pack": pack.get("id"), "available_problem_ids": [p.get("id") for p in pack.get("problems", [])]},
    )


def _quote_identifier(identifier: str) -> str:
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", identifier):
        raise CoQueryPracticeError("invalid_practice_schema", f"Invalid identifier in practice pack: {identifier!r}.")
    return f'"{identifier}"'


def _sqlite_type(raw_type: str) -> str:
    normalized = (raw_type or "TEXT").upper()
    if normalized not in {"INTEGER", "REAL", "TEXT"}:
        return "TEXT"
    return normalized


def _build_connection(pack: dict[str, Any]) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        for table in pack.get("dataset", {}).get("tables", []):
            table_name = _quote_identifier(str(table["name"]))
            columns = table.get("columns", [])
            if not columns:
                raise CoQueryPracticeError("invalid_practice_schema", f"Table has no columns: {table.get('name')}.")
            column_defs = [
                f"{_quote_identifier(str(column['name']))} {_sqlite_type(str(column.get('type', 'TEXT')))}"
                for column in columns
            ]
            primary_key = table.get("primary_key", [])
            if primary_key:
                pk_cols = ", ".join(_quote_identifier(str(column)) for column in primary_key)
                column_defs.append(f"PRIMARY KEY ({pk_cols})")
            for fk in table.get("foreign_keys", []):
                column_name = _quote_identifier(str(fk["column"]))
                ref_table = _quote_identifier(str(fk["references_table"]))
                ref_column = _quote_identifier(str(fk["references_column"]))
                column_defs.append(f"FOREIGN KEY ({column_name}) REFERENCES {ref_table}({ref_column})")
            conn.execute(f"CREATE TABLE {table_name} ({', '.join(column_defs)})")

        for table in pack.get("dataset", {}).get("tables", []):
            columns = [str(column["name"]) for column in table.get("columns", [])]
            column_sql = ", ".join(_quote_identifier(column) for column in columns)
            placeholders = ", ".join("?" for _ in columns)
            sql = f"INSERT INTO {_quote_identifier(str(table['name']))} ({column_sql}) VALUES ({placeholders})"
            for row in table.get("rows", []):
                conn.execute(sql, [row.get(column) for column in columns])
        conn.commit()
        return conn
    except Exception:
        conn.close()
        raise


def _ensure_select(sql: Optional[str]) -> str:
    text = (sql or "").strip()
    if not text:
        raise CoQueryPracticeError("missing_practice_sql", "A SELECT statement is required.")
    first_token = text.split(None, 1)[0].upper()
    if first_token != "SELECT":
        raise CoQueryPracticeError(
            "practice_sql_not_select",
            "Practice sandbox only accepts SELECT statements.",
            {"first_token": first_token},
        )
    return text


def _execute_select(pack: dict[str, Any], sql: str, limit: Optional[int] = None) -> dict[str, Any]:
    safe_sql = _ensure_select(sql)
    conn = _build_connection(pack)
    try:
        cursor = conn.execute(safe_sql)
        columns = [item[0] for item in cursor.description or []]
        if limit is None:
            raw_rows = cursor.fetchall()
        else:
            raw_rows = cursor.fetchmany(max(0, limit))
        rows = [{column: row[column] for column in columns} for row in raw_rows]
        return {"columns": columns, "rows": rows, "row_count": len(rows)}
    except sqlite3.Error as exc:
        raise CoQueryPracticeError("practice_sql_error", str(exc), {"sql": safe_sql}) from exc
    finally:
        conn.close()


def _signature(result: dict[str, Any]) -> tuple[tuple[str, ...], tuple[tuple[Any, ...], ...]]:
    columns = tuple(result["columns"])
    rows = tuple(tuple(row.get(column) for column in columns) for row in result["rows"])
    return columns, rows


def _problem_payload(problem: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": problem.get("id"),
        "title": problem.get("title"),
        "difficulty": problem.get("difficulty"),
        "prompt": problem.get("prompt"),
        "concepts": problem.get("concepts", []),
        "hint": problem.get("hint"),
    }


def _expected_issue(actual: dict[str, Any], expected: dict[str, Any]) -> str:
    actual_columns = [str(column) for column in actual.get("columns", [])]
    expected_columns = [str(column) for column in expected.get("columns", [])]

    if actual_columns != expected_columns:
        missing = [column for column in expected_columns if column not in actual_columns]
        extra = [column for column in actual_columns if column not in expected_columns]
        details = []
        if missing:
            details.append(f"Expected column(s) missing from the result: {', '.join(missing)}.")
        if extra:
            details.append(f"Unexpected column(s) returned: {', '.join(extra)}.")
        if not details:
            details.append("Returned columns have a different order than the expected answer.")
        return " ".join(details)

    if actual.get("row_count") != expected.get("row_count"):
        return (
            f"Expected {expected.get('row_count')} row(s), but the submitted query returned "
            f"{actual.get('row_count')} row(s). Check filters, joins, and grouping."
        )

    if actual.get("rows") != expected.get("rows"):
        return "Returned rows differ from the expected answer. Check selected values, sorting, joins, and aggregate logic."

    return "No issue detected. Result columns and rows match the expected answer."


def _static_feedback_message(problem: dict[str, Any], expected_issue: str) -> str:
    concepts = ", ".join(str(item) for item in problem.get("concepts", []) if item)
    concept_part = f" Focus concept(s): {concepts}." if concepts else ""
    hint_part = f" Hint: {problem.get('hint')}." if problem.get("hint") else ""
    return f"{expected_issue} Retry by adjusting the submitted SQL, then run practice_grade again.{concept_part}{hint_part}"


def _feedback_payload(source: str, message: str, ai_generated: bool, provider_name: Optional[str] = None) -> dict[str, Any]:
    payload = {
        "source": source,
        "label": "AI-generated feedback" if ai_generated else "Static feedback",
        "message": message,
        "ai_generated": ai_generated,
    }
    if provider_name:
        payload["provider_name"] = provider_name
    return payload


def _provider_feedback_prompt(problem: dict[str, Any], submitted_sql: str, expected_issue: str, static_feedback: str) -> str:
    return (
        "You are CoQuery's SQL training-mode tutor. "
        "Return concise feedback in two short sentences. "
        "Label no markdown, no JSON, no code fence. "
        "Explain the likely mistake and one retry step.\n"
        f"Problem: {problem.get('title')}\n"
        f"Prompt: {problem.get('prompt')}\n"
        f"Submitted SQL: {submitted_sql}\n"
        f"Expected issue: {expected_issue}\n"
        f"Static feedback: {static_feedback}"
    )


def _wrong_note(
    pack_id: str,
    problem: dict[str, Any],
    submitted_sql: str,
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> dict[str, Any]:
    expected_issue = _expected_issue(actual, expected)
    static_message = _static_feedback_message(problem, expected_issue)
    return {
        "pack_id": pack_id,
        "problem_id": problem.get("id"),
        "problem_title": problem.get("title"),
        "prompt": problem.get("prompt"),
        "submitted_sql": submitted_sql,
        "expected_issue": expected_issue,
        "static_feedback": _feedback_payload("static", static_message, ai_generated=False),
        "retry_action": {
            "label": "Retry",
            "command": "practice_start",
            "pack_id": pack_id,
            "problem_id": problem.get("id"),
            "sql": submitted_sql,
        },
        "provider_feedback": {
            "available": True,
            "mode_required": TRAINING_MODE,
            "request_command": "practice_feedback",
            "label": "AI-generated feedback",
        },
    }


def _fallback_wrong_note_from_attempt(entry: dict[str, Any], message: str) -> dict[str, Any]:
    pack_id = str(entry.get("pack_id") or DEFAULT_PACK)
    problem_id = entry.get("problem_id") or "practice"
    submitted_sql = str(entry.get("sql") or "")
    expected_issue = f"Stored attempt could not be regraded: {message}. Retry the problem to refresh the wrong note."
    return {
        "pack_id": pack_id,
        "problem_id": problem_id,
        "problem_title": entry.get("problem_title") or problem_id,
        "prompt": "",
        "submitted_sql": submitted_sql,
        "expected_issue": expected_issue,
        "static_feedback": _feedback_payload("static", expected_issue, ai_generated=False),
        "retry_action": {
            "label": "Retry",
            "command": "practice_start",
            "pack_id": pack_id,
            "problem_id": problem_id,
            "sql": submitted_sql,
        },
        "provider_feedback": {
            "available": True,
            "mode_required": TRAINING_MODE,
            "request_command": "practice_feedback",
            "label": "AI-generated feedback",
        },
    }


def _attempt_with_wrong_note(entry: dict[str, Any]) -> dict[str, Any]:
    if entry.get("correct") is not False or entry.get("wrong_note"):
        return entry

    augmented = dict(entry)
    try:
        loaded = _load_pack(str(entry.get("pack_id") or DEFAULT_PACK))
        problem = _get_problem(loaded, str(entry.get("problem_id") or ""))
        submitted_sql = _ensure_select(str(entry.get("sql") or ""))
        actual = _execute_select(loaded, submitted_sql, limit=None)
        expected = _execute_select(loaded, str(problem["expected_sql"]), limit=None)
        augmented["wrong_note"] = _wrong_note(str(loaded.get("id")), problem, submitted_sql, actual, expected)
    except CoQueryPracticeError as exc:
        augmented["wrong_note"] = _fallback_wrong_note_from_attempt(entry, exc.message)
    return augmented


def _attempt_log_path() -> Path:
    override = os.environ.get("COQUERY_PRACTICE_ATTEMPT_LOG")
    return Path(override) if override else DEFAULT_ATTEMPT_LOG


def _write_attempt(entry: dict[str, Any]) -> Path:
    path = _attempt_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def _read_attempts(limit: int, pack: Optional[str] = None, problem_id: Optional[str] = None) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    path = _attempt_log_path()
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if pack and entry.get("pack_id") != pack:
            continue
        if problem_id and entry.get("problem_id") != problem_id:
            continue
        entries.append(entry)
    return entries[-limit:]


def practice_list_handler(pack: Optional[str] = None) -> dict[str, Any]:
    try:
        packs = _list_pack_summaries()
        if pack:
            loaded = _load_pack(pack)
            return _success(
                "practice_list",
                {
                    "packs": [summary for summary in packs if summary["id"] == loaded.get("id")],
                    "selected_pack": loaded.get("id"),
                    "problems": _problem_summaries(loaded),
                    "examples": loaded.get("examples", []),
                },
            )
        selected = _load_pack(DEFAULT_PACK) if packs else None
        return _success(
            "practice_list",
            {
                "packs": packs,
                "selected_pack": selected.get("id") if selected else None,
                "problems": _problem_summaries(selected) if selected else [],
                "examples": selected.get("examples", []) if selected else [],
            },
        )
    except CoQueryPracticeError as exc:
        return _error("practice_list", exc)
    except Exception as exc:
        return _error("practice_list", CoQueryPracticeError("practice_error", str(exc)))


def practice_schema_handler(pack: Optional[str] = None, table: Optional[str] = None) -> dict[str, Any]:
    try:
        loaded = _load_pack(pack)
        dataset = loaded.get("dataset", {})
        tables = _table_summaries(loaded, table)
        return _success(
            "practice_schema",
            {
                "pack_id": loaded.get("id"),
                "dataset_id": dataset.get("id"),
                "dataset_title": dataset.get("title"),
                "table_count": len(tables),
                "tables": tables,
            },
        )
    except CoQueryPracticeError as exc:
        return _error("practice_schema", exc)
    except Exception as exc:
        return _error("practice_schema", CoQueryPracticeError("practice_error", str(exc)))


def practice_query_handler(sql: Optional[str], pack: Optional[str] = None, limit: Optional[int] = 50) -> dict[str, Any]:
    try:
        loaded = _load_pack(pack)
        resolved_limit = 50 if limit is None else int(limit)
        if resolved_limit < 0:
            raise CoQueryPracticeError("invalid_practice_limit", "limit must be zero or greater.")
        result = _execute_select(loaded, _ensure_select(sql), limit=resolved_limit)
        return _success(
            "practice_query",
            {
                "pack_id": loaded.get("id"),
                "dataset_id": loaded.get("dataset", {}).get("id"),
                "sql": sql,
                "limit": resolved_limit,
                **result,
            },
        )
    except CoQueryPracticeError as exc:
        return _error("practice_query", exc)
    except Exception as exc:
        return _error("practice_query", CoQueryPracticeError("practice_error", str(exc)))


def practice_grade_handler(
    problem_id: Optional[str],
    sql: Optional[str],
    pack: Optional[str] = None,
    record: bool = True,
) -> dict[str, Any]:
    command = "practice_grade"
    try:
        loaded = _load_pack(pack)
        problem = _get_problem(loaded, problem_id)
        actual = _execute_select(loaded, _ensure_select(sql), limit=None)
        expected = _execute_select(loaded, str(problem["expected_sql"]), limit=None)
        correct = _signature(actual) == _signature(expected)
        wrong_note = None if correct else _wrong_note(str(loaded.get("id")), problem, str(sql or ""), actual, expected)
        feedback = (
            "Correct. Result columns and rows match the expected answer."
            if correct
            else wrong_note["static_feedback"]["message"]
        )
        attempt = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pack_id": loaded.get("id"),
            "problem_id": problem.get("id"),
            "problem_title": problem.get("title"),
            "correct": correct,
            "sql": sql,
            "actual_row_count": actual["row_count"],
            "expected_row_count": expected["row_count"],
        }
        if wrong_note is not None:
            attempt["wrong_note"] = wrong_note
        log_path = str(_write_attempt(attempt)) if record else None
        return _success(
            command,
            {
                "pack_id": loaded.get("id"),
                "dataset_id": loaded.get("dataset", {}).get("id"),
                "problem": _problem_payload(problem),
                "correct": correct,
                "feedback": feedback,
                "feedback_source": "static",
                "ai_generated": False,
                "wrong_note": wrong_note,
                "actual": actual,
                "expected": expected,
                "expected_sql": problem.get("expected_sql"),
                "attempt_recorded": record,
                "attempt_log_path": log_path,
            },
        )
    except CoQueryPracticeError as exc:
        return _error(command, exc)
    except Exception as exc:
        return _error(command, CoQueryPracticeError("practice_error", str(exc)))


def practice_feedback_handler(
    problem_id: Optional[str],
    sql: Optional[str],
    pack: Optional[str] = None,
    provider_name: Optional[str] = None,
    mode: Optional[str] = None,
) -> dict[str, Any]:
    command = "practice_feedback"
    try:
        loaded = _load_pack(pack)
        problem = _get_problem(loaded, problem_id)
        submitted_sql = _ensure_select(sql)
        actual = _execute_select(loaded, submitted_sql, limit=None)
        expected = _execute_select(loaded, str(problem["expected_sql"]), limit=None)
        note = _wrong_note(str(loaded.get("id")), problem, submitted_sql, actual, expected)

        requested_provider = (provider_name or "").strip()
        normalized_mode = (mode or "static").strip().lower()
        if requested_provider and normalized_mode != TRAINING_MODE:
            raise CoQueryPracticeError(
                "provider_feedback_training_only",
                "Provider-backed practice feedback can only be requested in Training Mode.",
                {
                    "mode": normalized_mode,
                    "required_mode": TRAINING_MODE,
                    "provider_name": requested_provider,
                },
            )

        feedback = note["static_feedback"]
        provider_feedback_allowed = False
        if requested_provider:
            profile = LLMProviderRegistry().get_profile(requested_provider)
            static_message = str(note["static_feedback"]["message"])
            provider_message = LLMProviderClient(profile).complete_text(
                _provider_feedback_prompt(problem, submitted_sql, str(note["expected_issue"]), static_message)
            )
            feedback = _feedback_payload(
                "provider",
                provider_message or static_message,
                ai_generated=True,
                provider_name=profile.name,
            )
            provider_feedback_allowed = True

        return _success(
            command,
            {
                "pack_id": loaded.get("id"),
                "dataset_id": loaded.get("dataset", {}).get("id"),
                "problem": _problem_payload(problem),
                "submitted_sql": submitted_sql,
                "expected_issue": note["expected_issue"],
                "wrong_note": note,
                "feedback": feedback,
                "provider_feedback_allowed": provider_feedback_allowed,
                "mode": normalized_mode,
                "requested_provider_name": requested_provider or None,
            },
        )
    except CoQueryPracticeError as exc:
        return _error(command, exc)
    except CoQueryLLMError as exc:
        return _error(command, CoQueryPracticeError(exc.code, exc.message, getattr(exc, "data", {})))
    except Exception as exc:
        return _error(command, CoQueryPracticeError("practice_error", str(exc)))


def practice_attempts_handler(
    pack: Optional[str] = None,
    problem_id: Optional[str] = None,
    limit: Optional[int] = 20,
) -> dict[str, Any]:
    try:
        resolved_limit = 20 if limit is None else int(limit)
        if resolved_limit < 0:
            raise CoQueryPracticeError("invalid_practice_limit", "limit must be zero or greater.")
        pack_id = _resolve_pack_id(pack) if pack else None
        attempts = [_attempt_with_wrong_note(entry) for entry in _read_attempts(resolved_limit, pack=pack_id, problem_id=problem_id)]
        return _success(
            "practice_attempts",
            {
                "attempt_log_path": str(_attempt_log_path()),
                "pack_id": pack_id,
                "problem_id": problem_id,
                "limit": resolved_limit,
                "attempts": attempts,
                "attempt_count": len(attempts),
            },
        )
    except CoQueryPracticeError as exc:
        return _error("practice_attempts", exc)
    except Exception as exc:
        return _error("practice_attempts", CoQueryPracticeError("practice_error", str(exc)))
