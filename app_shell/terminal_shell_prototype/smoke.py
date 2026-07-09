#!/usr/bin/env python3
"""Smoke checks for the responsive terminal shell prototype."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app_shell.terminal_shell_prototype.server import TerminalShellHandler  # noqa: E402


ROOT = Path(__file__).resolve().parent


def assert_contains(path: Path, expected: str) -> None:
    text = path.read_text(encoding="utf-8")
    if expected not in text:
        raise AssertionError(f"{path.name} does not contain expected text: {expected}")


def request_json(port: int, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    conn = HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        data = response.read().decode("utf-8")
        parsed = json.loads(data)
        if response.status >= 500:
            raise AssertionError(f"{method} {path} returned {response.status}: {data}")
        return parsed
    finally:
        conn.close()


def run_server_smoke() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["COQUERY_LLM_REGISTRY_PATH"] = str(Path(tmpdir) / "llm_providers.json")
        os.environ["COQUERY_PRACTICE_ATTEMPT_LOG"] = str(Path(tmpdir) / "practice_attempts.jsonl")
        os.environ["COQUERY_PRODUCTION_PROFILE_PATH"] = str(Path(tmpdir) / "production_profiles.json")
        os.environ["COQUERY_PRODUCTION_REVIEW_PATH"] = str(Path(tmpdir) / "production_reviews.json")
        os.environ["COQUERY_PRODUCTION_AUDIT_LOG"] = str(Path(tmpdir) / "production_audit.jsonl")
        server = ThreadingHTTPServer(("127.0.0.1", 0), TerminalShellHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            health = request_json(port, "GET", "/api/health")
            assert health["ok"] is True
            sessions = request_json(port, "GET", "/api/sessions")
            assert sessions["ok"] is True
            assert len(sessions["sessions"]) >= 1

            presets = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "provider_list_presets", "args": {}, "context": {}},
            )
            assert presets["ok"] is True
            assert presets["block_type"] == "provider_presets"
            assert "cli_equivalent" in presets

            saved_provider = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "provider_add_preset",
                    "args": {
                        "preset": "gemini",
                        "provider_name": "gemini_mobile",
                        "model_name": "gemini-3.5-flash",
                        "api_key_env": "GEMINI_API_KEY",
                    },
                    "context": {},
                },
            )
            assert saved_provider["ok"] is True
            assert saved_provider["block_type"] == "provider_config"
            assert saved_provider["data"]["provider"]["name"] == "gemini_mobile"

            production_provider_block = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "natural",
                    "args": {"sql": "show users"},
                    "context": {
                        "db": "example.db",
                        "provider_name": "gemini_mobile",
                        "mode": "production_assist",
                    },
                },
            )
            assert production_provider_block["ok"] is False
            assert production_provider_block["error"]["code"] == "production_external_provider_blocked"
            assert production_provider_block["data"]["mode_context"]["mode"] == "production_assist"

            production_profile = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "production_profile_add",
                    "args": {"profile_name": "prod_readonly", "db_uri": "example.db"},
                    "context": {"mode": "production_assist"},
                },
            )
            assert production_profile["ok"] is True
            assert production_profile["block_type"] == "production_profile"
            assert production_profile["data"]["profile"]["read_only"] is True

            production_review = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "production_review",
                    "args": {
                        "profile_name": "prod_readonly",
                        "sql": "SELECT COUNT(*) FROM users",
                        "request_text": "count users",
                    },
                    "context": {"mode": "production_assist"},
                },
            )
            assert production_review["ok"] is True
            assert production_review["block_type"] == "production_review"
            assert production_review["data"]["review"]["approval_required"] is True
            assert production_review["data"]["review"]["execution_allowed"] is False
            review_id = production_review["data"]["review"]["review_id"]

            production_execute_blocked = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "production_execute",
                    "args": {"review_id": review_id},
                    "context": {"mode": "production_assist"},
                },
            )
            assert production_execute_blocked["ok"] is False
            assert production_execute_blocked["error"]["code"] == "production_approval_required"

            production_approved = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "production_approve",
                    "args": {"review_id": review_id},
                    "context": {"mode": "production_assist"},
                },
            )
            assert production_approved["ok"] is True
            assert production_approved["data"]["review"]["execution_allowed"] is True

            production_executed = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "production_execute",
                    "args": {"review_id": review_id},
                    "context": {"mode": "production_assist"},
                },
            )
            assert production_executed["ok"] is True
            assert production_executed["block_type"] == "production_execution"
            assert production_executed["data"]["row_count"] == 1

            production_write_rejected = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "production_review",
                    "args": {"profile_name": "prod_readonly", "sql": "DELETE FROM users"},
                    "context": {"mode": "production_assist"},
                },
            )
            assert production_write_rejected["ok"] is False
            assert production_write_rejected["error"]["code"] == "production_select_only"
            audit_events = [
                json.loads(line)["event"]
                for line in Path(os.environ["COQUERY_PRODUCTION_AUDIT_LOG"]).read_text(encoding="utf-8").splitlines()
            ]
            assert "profile_added" in audit_events
            assert "review_created" in audit_events
            assert "execution_blocked" in audit_events
            assert "review_approved" in audit_events
            assert "execution_completed" in audit_events
            assert "review_rejected" in audit_events

            saved_list = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "provider_list", "args": {}, "context": {}},
            )
            assert saved_list["ok"] is True
            assert saved_list["block_type"] == "provider_list"
            assert saved_list["data"]["providers"][0]["name"] == "gemini_mobile"
            assert "--command provider_list" in saved_list["cli_equivalent"]

            provider_test_missing_key = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "provider_test", "args": {"provider_name": "gemini_mobile"}, "context": {}},
            )
            assert provider_test_missing_key["ok"] is False
            assert provider_test_missing_key["block_type"] == "provider_diagnostic"
            assert provider_test_missing_key["error"]["code"] == "missing_api_key"
            assert provider_test_missing_key["data"]["readable_message"]
            assert provider_test_missing_key["data"]["next_step"]
            assert "--provider-name gemini_mobile" in provider_test_missing_key["cli_equivalent"]

            removed_provider = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "provider_remove", "args": {"provider_name": "gemini_mobile"}, "context": {}},
            )
            assert removed_provider["ok"] is True
            assert removed_provider["block_type"] == "provider_config"
            assert removed_provider["data"]["provider"]["name"] == "gemini_mobile"
            assert "--provider-name gemini_mobile" in removed_provider["cli_equivalent"]

            schema = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "schema_detail", "args": {"table": "users"}, "context": {"db": "example.db"}},
            )
            assert schema["ok"] is True
            assert schema["block_type"] == "schema_detail"

            practice = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "practice_list", "args": {}, "context": {}},
            )
            assert practice["ok"] is True
            assert practice["block_type"] == "practice_list"
            assert practice["data"]["selected_pack"] == "sql_basics"
            assert any(item["id"] == "basic_select_customers" for item in practice["data"]["problems"])

            practice_schema = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "practice_schema", "args": {}, "context": {}},
            )
            assert practice_schema["ok"] is True
            assert practice_schema["block_type"] == "practice_schema"
            assert practice_schema["data"]["table_count"] >= 1

            practice_query = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "practice_query",
                    "args": {"sql": "SELECT id, name, region FROM customers ORDER BY id", "limit": 20},
                    "context": {},
                },
            )
            assert practice_query["ok"] is True
            assert practice_query["block_type"] == "practice_query_result"
            assert practice_query["data"]["row_count"] == 4

            wrong_grade = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "practice_grade",
                    "args": {"problem_id": "basic_select_customers", "sql": "SELECT id, name FROM customers ORDER BY id"},
                    "context": {},
                },
            )
            assert wrong_grade["ok"] is True
            assert wrong_grade["block_type"] == "practice_grade"
            assert wrong_grade["data"]["correct"] is False
            assert wrong_grade["data"]["attempt_recorded"] is True
            assert wrong_grade["data"]["wrong_note"]["submitted_sql"] == "SELECT id, name FROM customers ORDER BY id"
            assert wrong_grade["data"]["wrong_note"]["static_feedback"]["ai_generated"] is False
            assert wrong_grade["data"]["wrong_note"]["provider_feedback"]["mode_required"] == "training"

            practice_attempts = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "practice_attempts",
                    "args": {"problem_id": "basic_select_customers", "limit": 5},
                    "context": {},
                },
            )
            assert practice_attempts["ok"] is True
            assert practice_attempts["block_type"] == "practice_attempts"
            assert practice_attempts["data"]["attempt_count"] >= 1
            assert practice_attempts["data"]["attempts"][-1]["correct"] is False
            assert practice_attempts["data"]["attempts"][-1]["wrong_note"]["expected_issue"]
            assert practice_attempts["data"]["attempts"][-1]["wrong_note"]["retry_action"]["command"] == "practice_start"

            static_feedback = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "practice_feedback",
                    "args": {
                        "problem_id": "basic_select_customers",
                        "sql": "SELECT id, name FROM customers ORDER BY id",
                    },
                    "context": {},
                },
            )
            assert static_feedback["ok"] is True
            assert static_feedback["block_type"] == "practice_feedback"
            assert static_feedback["data"]["feedback"]["source"] == "static"
            assert static_feedback["data"]["feedback"]["ai_generated"] is False

            provider_feedback_blocked = request_json(
                port,
                "POST",
                "/api/commands/run",
                {
                    "command": "practice_feedback",
                    "args": {
                        "problem_id": "basic_select_customers",
                        "sql": "SELECT id, name FROM customers ORDER BY id",
                        "provider_name": "gemini_mobile",
                        "mode": "review",
                    },
                    "context": {},
                },
            )
            assert provider_feedback_blocked["ok"] is False
            assert provider_feedback_blocked["error"]["code"] == "provider_feedback_training_only"

            help_catalog = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "help_catalog", "args": {}, "context": {"lang": "ko"}},
            )
            assert help_catalog["ok"] is True
            assert help_catalog["block_type"] == "help_catalog"
            assert help_catalog["data"]["language"] == "ko"

            command_help = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "command_explain", "args": {"topic": "natural"}, "context": {"lang": "en"}},
            )
            assert command_help["ok"] is True
            assert command_help["block_type"] == "command_help"
            assert command_help["data"]["command"]["id"] == "natural"

            term_help = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "term_explain", "args": {"topic": "join"}, "context": {"lang": "ko"}},
            )
            assert term_help["ok"] is True
            assert term_help["block_type"] == "term_help"
            assert term_help["data"]["term"]["plain"].startswith("두 테이블")

            unknown = request_json(
                port,
                "POST",
                "/api/commands/run",
                {"command": "not_a_command", "args": {}, "context": {}},
            )
            assert unknown["ok"] is False
            assert unknown["error"]["code"] == "unknown_command"
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


def main() -> int:
    assert_contains(ROOT / "index.html", '<html lang="ko">')
    assert_contains(ROOT / "index.html", "반응형 터미널 쉘")
    assert_contains(ROOT / "index.html", "세션 검색...")
    assert_contains(ROOT / "index.html", "초보자 안내")
    assert_contains(ROOT / "index.html", "commandForm")
    assert_contains(ROOT / "index.html", "providerStatus")
    assert_contains(ROOT / "index.html", "modeToggle")
    assert_contains(ROOT / "index.html", "data-mode-option")
    assert_contains(ROOT / "index.html", "production_assist")
    assert_contains(ROOT / "index.html", "drawerButton")
    assert_contains(ROOT / "index.html", "commandMenuToggle")
    assert_contains(ROOT / "index.html", 'aria-expanded="false"')
    assert_contains(ROOT / "index.html", "commandMenuPanel")
    assert_contains(ROOT / "index.html", "hidden")
    assert_contains(ROOT / "index.html", "provider_setup")
    assert_contains(ROOT / "index.html", "production_review")
    assert_contains(ROOT / "index.html", "chipProduction")
    assert_contains(ROOT / "index.html", "language-toggle")
    assert_contains(ROOT / "index.html", "term_explain join")
    assert_contains(ROOT / "index.html", "detailHelp")
    assert_contains(ROOT / "styles.css", "color-scheme: dark")
    assert_contains(ROOT / "styles.css", "Noto Sans KR")
    assert_contains(ROOT / "styles.css", "Malgun Gothic")
    assert_contains(ROOT / "styles.css", 'html[lang="ko"] body')
    assert_contains(ROOT / "styles.css", "overflow-x: clip")
    assert_contains(ROOT / "styles.css", "flex-wrap: wrap")
    assert_contains(ROOT / "styles.css", "@media (max-width: 760px)")
    assert_contains(ROOT / "styles.css", "grid-template-columns: 276px minmax(420px, 1fr) 360px")
    assert_contains(ROOT / "styles.css", "max-width: 100%")
    assert_contains(ROOT / "styles.css", ".command-menu-popover[hidden]")
    assert_contains(ROOT / "styles.css", "help-box")
    assert_contains(ROOT / "app.js", "provider_list_presets")
    assert_contains(ROOT / "app.js", "provider-setup-form")
    assert_contains(ROOT / "app.js", "provider_add_preset")
    assert_contains(ROOT / "app.js", "provider_select")
    assert_contains(ROOT / "app.js", "data-provider-select")
    assert_contains(ROOT / "app.js", "data-provider-test")
    assert_contains(ROOT / "app.js", "data-provider-remove")
    assert_contains(ROOT / "app.js", "providerStatus")
    assert_contains(ROOT / "app.js", "currentAppMode")
    assert_contains(ROOT / "app.js", "production_assist")
    assert_contains(ROOT / "app.js", "mode_context")
    assert_contains(ROOT / "app.js", "allow_external_provider")
    assert_contains(ROOT / "app.js", "readable_message")
    assert_contains(ROOT / "app.js", "help_catalog")
    assert_contains(ROOT / "app.js", "currentLanguage")
    assert_contains(ROOT / "app.js", 'documentTitle: "CoQuery 터미널 쉘"')
    assert_contains(ROOT / "app.js", 'copy_sql: "Copy SQL"')
    assert_contains(ROOT / "app.js", "practice_list")
    assert_contains(ROOT / "app.js", "practice_start")
    assert_contains(ROOT / "app.js", "practice-flow-form")
    assert_contains(ROOT / "app.js", "data-practice-submit")
    assert_contains(ROOT / "app.js", "practice_attempts")
    assert_contains(ROOT / "app.js", "practice_feedback")
    assert_contains(ROOT / "app.js", "production_profile_add")
    assert_contains(ROOT / "app.js", "production_review")
    assert_contains(ROOT / "app.js", "production_approve")
    assert_contains(ROOT / "app.js", "production_execute")
    assert_contains(ROOT / "app.js", "data-production-approve")
    assert_contains(ROOT / "app.js", "data-production-execute")
    assert_contains(ROOT / "app.js", "productionAuditLog")
    assert_contains(ROOT / "app.js", "wrong-note-card")
    assert_contains(ROOT / "app.js", "data-retry-practice")
    assert_contains(ROOT / "app.js", "data-provider-feedback")
    assert_contains(ROOT / "app.js", "AI-generated feedback")
    assert_contains(ROOT / "styles.css", ".wrong-note-card")
    assert_contains(ROOT / "app.js", "/api/commands/run")
    assert_contains(ROOT / "app.js", "setCommandMenuOpen")
    run_server_smoke()
    print("terminal shell prototype smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
