#!/usr/bin/env python3
"""Focused proof that the local/advanced shell receives additive result intelligence."""

from __future__ import annotations

import json
import sys
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app_shell.terminal_shell_prototype.server import TerminalShellHandler  # noqa: E402


def request_json(port: int, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    body = json.dumps(payload).encode("utf-8")
    conn = HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        conn.request("POST", "/api/commands/run", body=body, headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        parsed = json.loads(response.read().decode("utf-8"))
        return response.status, parsed
    finally:
        conn.close()


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 0), TerminalShellHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        sql = "SELECT region, COUNT(*) AS customer_count FROM customers GROUP BY region ORDER BY region"
        status, result = request_json(
            port,
            {
                "command": "practice_query",
                "args": {"sql": sql, "pack": "sql_basics", "limit": 50},
                "context": {"mode": "training"},
            },
        )
        assert status == 200
        assert result["ok"] is True
        assert result["block_type"] == "practice_query_result"
        assert result["data"]["columns"] == ["region", "customer_count"]
        assert result["data"]["rows"] == [
            {"region": "Busan", "customer_count": 1},
            {"region": "Incheon", "customer_count": 1},
            {"region": "Seoul", "customer_count": 2},
        ]
        assert result["data"]["row_count"] == 3
        intelligence = result["data"].get("result_intelligence") or {}
        assert intelligence.get("shape") == "category_measure"
        assert intelligence.get("recommended_view") == "visual"
        assert intelligence.get("recommended_visual") == "bar"
        assert intelligence.get("dimensions") == ["region"]
        assert intelligence.get("measures") == ["customer_count"]

        invalid_status, invalid = request_json(
            port,
            {
                "command": "practice_query",
                "args": {"sql": "DELETE FROM customers"},
                "context": {"mode": "training"},
            },
        )
        assert invalid_status == 400
        assert invalid["ok"] is False
        assert invalid["error"]["code"] == "practice_sql_not_select"
        assert "result_intelligence" not in invalid.get("data", {})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    print("local practice result-intelligence smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
