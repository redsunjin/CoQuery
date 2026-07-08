#!/usr/bin/env python3
"""Production Assist safety gate for read-only reviewed SQL execution."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse, urlunparse

from sql_cli.db_new import CoQueryDB, CoQueryDBError


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME_DIR = REPO_ROOT / ".coquery"
PROFILE_ENV_VAR = "COQUERY_PRODUCTION_PROFILE_PATH"
REVIEW_ENV_VAR = "COQUERY_PRODUCTION_REVIEW_PATH"
AUDIT_ENV_VAR = "COQUERY_PRODUCTION_AUDIT_LOG"


def _success(command: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "command": command, "data": data, "error": None}


def _error(
    command: str,
    code: str,
    message: str,
    data: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "command": command,
        "data": data or {},
        "error": {"code": code, "message": message},
    }


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _profile_path() -> Path:
    return Path(os.environ.get(PROFILE_ENV_VAR, DEFAULT_RUNTIME_DIR / "production_profiles.json"))


def _review_path() -> Path:
    return Path(os.environ.get(REVIEW_ENV_VAR, DEFAULT_RUNTIME_DIR / "production_reviews.json"))


def _audit_path() -> Path:
    return Path(os.environ.get(AUDIT_ENV_VAR, DEFAULT_RUNTIME_DIR / "production_audit.jsonl"))


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_profiles() -> list[dict[str, Any]]:
    payload = _read_json(_profile_path(), {"profiles": []})
    profiles = payload.get("profiles", [])
    return profiles if isinstance(profiles, list) else []


def _save_profiles(profiles: list[dict[str, Any]]) -> None:
    _write_json(_profile_path(), {"profiles": profiles})


def _load_reviews() -> list[dict[str, Any]]:
    payload = _read_json(_review_path(), {"reviews": []})
    reviews = payload.get("reviews", [])
    return reviews if isinstance(reviews, list) else []


def _save_reviews(reviews: list[dict[str, Any]]) -> None:
    _write_json(_review_path(), {"reviews": reviews})


def _audit(event: str, payload: Optional[dict[str, Any]] = None) -> None:
    path = _audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": _timestamp(),
        "event": event,
        **(payload or {}),
    }
    with path.open("a", encoding="utf-8") as audit_log:
        audit_log.write(json.dumps(record, ensure_ascii=False) + "\n")


def _redact_db_uri(db_uri: Optional[str]) -> Optional[str]:
    if not db_uri:
        return db_uri
    if "://" not in db_uri:
        return db_uri

    parsed = urlparse(db_uri)
    if parsed.password is None:
        return db_uri

    username = parsed.username or ""
    host = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    netloc = f"{username}:***@{host}{port}"
    return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))


def _db_uri_has_embedded_secret(db_uri: Optional[str]) -> bool:
    if not db_uri or "://" not in db_uri:
        return False
    parsed = urlparse(db_uri)
    return parsed.password is not None


def _public_profile(profile: dict[str, Any]) -> dict[str, Any]:
    public = dict(profile)
    if public.get("db_uri"):
        public["db_uri"] = _redact_db_uri(str(public["db_uri"]))
    return public


def _find_profile(profile_name: Optional[str]) -> Optional[dict[str, Any]]:
    if not profile_name:
        return None
    for profile in _load_profiles():
        if profile.get("name") == profile_name:
            return profile
    return None


def _find_review(review_id: Optional[str]) -> tuple[Optional[dict[str, Any]], list[dict[str, Any]], Optional[int]]:
    if not review_id:
        return None, _load_reviews(), None

    reviews = _load_reviews()
    for index, review in enumerate(reviews):
        if review.get("review_id") == review_id:
            return review, reviews, index
    return None, reviews, None


def _review_with_execution_state(review: dict[str, Any]) -> dict[str, Any]:
    public = dict(review)
    public["approval_required"] = public.get("status") != "approved"
    public["execution_allowed"] = public.get("status") == "approved" and bool(public.get("select_only"))
    return public


def _select_only_check(sql: Optional[str]) -> tuple[bool, str]:
    if not sql or not sql.strip():
        return False, "SQL is required for production review."

    candidate = sql.strip()
    if candidate.endswith(";"):
        candidate = candidate[:-1].strip()

    if ";" in candidate:
        return False, "Production Assist accepts one SELECT statement at a time."

    operation = candidate.split(None, 1)[0].upper() if candidate else ""
    if operation != "SELECT":
        return False, "Production Assist can only review and execute SELECT statements."

    return True, "SELECT-only guard passed."


def _resolve_profile_db_uri(profile: dict[str, Any]) -> tuple[Optional[str], Optional[dict[str, str]]]:
    db_uri_env = profile.get("db_uri_env")
    if db_uri_env:
        db_uri = os.environ.get(str(db_uri_env))
        if not db_uri:
            return None, {
                "code": "production_db_uri_env_missing",
                "message": f"Environment variable {db_uri_env} is required for this production profile.",
            }
        return db_uri, None

    db_uri = profile.get("db_uri")
    if not db_uri:
        return None, {
            "code": "production_db_uri_missing",
            "message": "Production profile must include db_uri or db_uri_env.",
        }
    return str(db_uri), None


def production_profile_add_handler(
    profile_name: Optional[str],
    db_uri: Optional[str] = None,
    db_uri_env: Optional[str] = None,
    read_only: bool = True,
    dialect: Optional[str] = None,
) -> dict[str, Any]:
    command = "production_profile_add"
    name = (profile_name or "").strip()
    if not name:
        return _error(command, "production_profile_name_required", "Production profile name is required.")

    if not read_only:
        _audit("profile_rejected", {"profile_name": name, "reason": "read_only_required"})
        return _error(
            command,
            "production_read_only_required",
            "Production Assist profiles must use read-only credentials.",
            {"profile_name": name},
        )

    if not db_uri and not db_uri_env:
        return _error(command, "production_db_uri_required", "Set db_uri or db_uri_env for the production profile.")

    if db_uri and db_uri_env:
        return _error(command, "production_profile_target_conflict", "Use either db_uri or db_uri_env, not both.")

    if _db_uri_has_embedded_secret(db_uri):
        _audit("profile_rejected", {"profile_name": name, "reason": "embedded_secret"})
        return _error(
            command,
            "production_secret_in_profile",
            "Do not store database passwords in production profiles; use db_uri_env instead.",
            {"profile_name": name},
        )

    now = _timestamp()
    profile = {
        "name": name,
        "db_uri": db_uri,
        "db_uri_env": db_uri_env,
        "dialect": dialect,
        "read_only": True,
        "mode": "production_assist",
        "created_at": now,
        "updated_at": now,
    }

    profiles = [item for item in _load_profiles() if item.get("name") != name]
    profiles.append(profile)
    profiles.sort(key=lambda item: str(item.get("name", "")))
    _save_profiles(profiles)
    _audit("profile_added", {"profile_name": name, "read_only": True, "dialect": dialect})
    return _success(command, {"profile": _public_profile(profile), "profile_path": str(_profile_path())})


def production_profile_list_handler() -> dict[str, Any]:
    profiles = [_public_profile(profile) for profile in _load_profiles()]
    return _success(
        "production_profile_list",
        {
            "profiles": profiles,
            "profile_path": str(_profile_path()),
        },
    )


def production_review_handler(
    profile_name: Optional[str],
    sql: Optional[str],
    request_text: Optional[str] = None,
    source_command: Optional[str] = None,
) -> dict[str, Any]:
    command = "production_review"
    name = (profile_name or "").strip()
    profile = _find_profile(name)
    if not profile:
        return _error(command, "production_profile_not_found", f"Production profile not found: {name}.")

    if profile.get("read_only") is not True:
        return _error(
            command,
            "production_read_only_required",
            "Production Assist profiles must be marked read-only.",
            {"profile": _public_profile(profile)},
        )

    select_only, select_message = _select_only_check(sql)
    review = {
        "review_id": f"prodrev_{uuid.uuid4().hex[:12]}",
        "profile_name": name,
        "sql": sql or "",
        "request_text": request_text or "",
        "source_command": source_command or "manual",
        "status": "pending_approval" if select_only else "rejected",
        "select_only": select_only,
        "select_only_message": select_message,
        "approval_required": select_only,
        "execution_allowed": False,
        "created_at": _timestamp(),
        "approved_at": None,
        "executed_at": None,
    }

    if not select_only:
        _audit("review_rejected", {"profile_name": name, "review_id": review["review_id"], "reason": "select_only"})
        return _error(
            command,
            "production_select_only",
            select_message,
            {
                "review": review,
                "profile": _public_profile(profile),
                "audit_log": str(_audit_path()),
            },
        )

    reviews = _load_reviews()
    reviews.append(review)
    _save_reviews(reviews)
    _audit("review_created", {"profile_name": name, "review_id": review["review_id"], "status": review["status"]})
    return _success(
        command,
        {
            "review": review,
            "profile": _public_profile(profile),
            "review_path": str(_review_path()),
            "audit_log": str(_audit_path()),
        },
    )


def production_approve_handler(review_id: Optional[str]) -> dict[str, Any]:
    command = "production_approve"
    review, reviews, index = _find_review(review_id)
    if review is None or index is None:
        return _error(command, "production_review_not_found", f"Production review not found: {review_id}.")

    select_only, select_message = _select_only_check(review.get("sql"))
    if not select_only:
        _audit("approval_blocked", {"review_id": review.get("review_id"), "reason": "select_only"})
        return _error(command, "production_select_only", select_message, {"review": review})

    if review.get("status") == "rejected":
        return _error(command, "production_review_not_approvable", "Rejected production reviews cannot be approved.", {"review": review})

    review["status"] = "approved"
    review["approved_at"] = _timestamp()
    review["select_only"] = True
    review["approval_required"] = False
    review["execution_allowed"] = True
    reviews[index] = review
    _save_reviews(reviews)
    _audit("review_approved", {"profile_name": review.get("profile_name"), "review_id": review.get("review_id")})
    return _success(command, {"review": _review_with_execution_state(review), "audit_log": str(_audit_path())})


def production_execute_handler(review_id: Optional[str]) -> dict[str, Any]:
    command = "production_execute"
    review, reviews, index = _find_review(review_id)
    if review is None or index is None:
        return _error(command, "production_review_not_found", f"Production review not found: {review_id}.")

    profile = _find_profile(review.get("profile_name"))
    if not profile:
        return _error(command, "production_profile_not_found", f"Production profile not found: {review.get('profile_name')}.")

    if profile.get("read_only") is not True:
        _audit("execution_blocked", {"review_id": review.get("review_id"), "reason": "read_only_required"})
        return _error(command, "production_read_only_required", "Production Assist execution requires a read-only profile.")

    select_only, select_message = _select_only_check(review.get("sql"))
    if not select_only:
        _audit("execution_blocked", {"review_id": review.get("review_id"), "reason": "select_only"})
        return _error(command, "production_select_only", select_message, {"review": _review_with_execution_state(review)})

    if review.get("status") != "approved":
        _audit("execution_blocked", {"review_id": review.get("review_id"), "reason": "approval_required"})
        return _error(
            command,
            "production_approval_required",
            "Approve the generated SQL review before execution.",
            {"review": _review_with_execution_state(review), "profile": _public_profile(profile)},
        )

    db_uri, db_uri_error = _resolve_profile_db_uri(profile)
    if db_uri_error:
        _audit("execution_blocked", {"review_id": review.get("review_id"), "reason": db_uri_error["code"]})
        return _error(command, db_uri_error["code"], db_uri_error["message"], {"profile": _public_profile(profile)})

    try:
        with CoQueryDB(str(db_uri)) as conn:
            rows = conn.execute(str(review.get("sql") or ""))
    except CoQueryDBError as exc:
        _audit("execution_blocked", {"review_id": review.get("review_id"), "reason": exc.code})
        return _error(command, exc.code, exc.message, exc.data)
    except Exception as exc:
        _audit("execution_blocked", {"review_id": review.get("review_id"), "reason": "execution_error"})
        return _error(command, "execution_error", str(exc))

    normalized_rows = [list(row) if isinstance(row, tuple) else row for row in (rows or [])]
    review["status"] = "executed"
    review["executed_at"] = _timestamp()
    review["approval_required"] = False
    review["execution_allowed"] = False
    reviews[index] = review
    _save_reviews(reviews)
    _audit(
        "execution_completed",
        {
            "profile_name": profile.get("name"),
            "review_id": review.get("review_id"),
            "row_count": len(normalized_rows),
        },
    )
    return _success(
        command,
        {
            "review": _review_with_execution_state(review),
            "profile": _public_profile(profile),
            "rows": normalized_rows,
            "row_count": len(normalized_rows),
            "audit_log": str(_audit_path()),
        },
    )
