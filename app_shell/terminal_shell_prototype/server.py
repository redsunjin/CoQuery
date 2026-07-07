#!/usr/bin/env python3
"""Local prototype server for the CoQuery responsive terminal shell."""

from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any


PROTOTYPE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROTOTYPE_DIR.parents[1]
RUNTIME_DIR = PROTOTYPE_DIR / ".runtime"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sql_cli.command_api import run_command  # noqa: E402


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


class TerminalShellHandler(SimpleHTTPRequestHandler):
    """Serve the static shell and expose a small command API."""

    server_version = "CoQueryTerminalShell/0.1"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(PROTOTYPE_DIR), **kwargs)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = _json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/health":
            self._send_json(
                200,
                {
                    "ok": True,
                    "service": "coquery-terminal-shell",
                    "runtime_registry": os.environ.get("COQUERY_LLM_REGISTRY_PATH"),
                },
            )
            return
        if self.path == "/api/sessions":
            self._send_json(
                200,
                {
                    "ok": True,
                    "sessions": [
                        {
                            "id": "local-sql-lab",
                            "title": "Local SQL Lab",
                            "subtitle": "Command API ready",
                            "active": True,
                        },
                        {
                            "id": "provider-setup",
                            "title": "Provider setup",
                            "subtitle": "Presets and model checks",
                            "active": False,
                        },
                        {
                            "id": "practice-flow",
                            "title": "Practice flow",
                            "subtitle": "Review and wrong-note path",
                            "active": False,
                        },
                    ],
                },
            )
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/commands/run":
            self._send_json(
                404,
                {
                    "ok": False,
                    "error": {"code": "not_found", "message": f"Unknown endpoint: {self.path}"},
                },
            )
            return

        try:
            payload = self._read_json_body()
            command = str(payload.get("command", "")).strip()
            args = payload.get("args") or {}
            context = payload.get("context") or {}
            if not isinstance(args, dict) or not isinstance(context, dict):
                raise ValueError("args and context must be JSON objects")
            result = run_command(command, args=args, context=context)
            self._send_json(200 if result.get("ok") else 400, result)
        except json.JSONDecodeError as exc:
            self._send_json(
                400,
                {
                    "ok": False,
                    "error": {"code": "invalid_json", "message": exc.msg},
                },
            )
        except Exception as exc:
            self._send_json(
                500,
                {
                    "ok": False,
                    "error": {"code": "server_error", "message": str(exc)},
                },
            )

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("[terminal-shell] " + format % args + "\n")


def ensure_runtime() -> None:
    RUNTIME_DIR.mkdir(exist_ok=True)
    os.environ.setdefault("COQUERY_LLM_REGISTRY_PATH", str(RUNTIME_DIR / "llm_providers.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the CoQuery responsive terminal shell prototype")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    ensure_runtime()
    server = ThreadingHTTPServer((args.host, args.port), TerminalShellHandler)
    print(f"CoQuery terminal shell running at http://{args.host}:{args.port}")
    print(f"Runtime registry: {os.environ['COQUERY_LLM_REGISTRY_PATH']}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping CoQuery terminal shell")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
