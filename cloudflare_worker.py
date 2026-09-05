"""Cloudflare Python Worker entrypoint for the hosted CoQuery PWA.

The hosted surface intentionally exposes the learning/practice commands only.
Durable learner progress lives in browser localStorage for this MVP; the
Worker runs practice grading with no_record=True so it never relies on the
Worker's ephemeral filesystem for progress.
"""

from __future__ import annotations

import json
from urllib.parse import urlparse

from workers import Response, WorkerEntrypoint

from sql_cli.command_api import run_command
from sql_cli.result_integration import enrich_practice_query_result


HOSTED_COMMANDS = {
    "practice_list",
    "practice_schema",
    "practice_query",
    "practice_grade",
    "practice_feedback",
    "help_catalog",
    "command_explain",
    "term_explain",
    "db_knowledge",
}


def _json_response(payload: dict, status: int = 200) -> Response:
    return Response(
        json.dumps(payload, ensure_ascii=False),
        status=status,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-store",
        },
    )


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        path = urlparse(request.url).path
        method = request.method

        if path == "/api/health" and "GET" in method:
            return _json_response(
                {
                    "ok": True,
                    "service": "coquery-pwa-worker",
                    "runtime": "cloudflare-python-worker",
                    "hosted_mode": "practice-first",
                    "progress_storage": "browser-localStorage",
                }
            )

        if path == "/api/sessions" and "GET" in method:
            return _json_response(
                {
                    "ok": True,
                    "sessions": [
                        {
                            "id": "practice-flow",
                            "title": "SQL Practice",
                            "subtitle": "Hosted learning path",
                            "active": True,
                        }
                    ],
                }
            )

        if path == "/api/commands/run" and "POST" in method:
            try:
                payload = await request.json()
                command = str(payload.get("command", "")).strip()
                args = dict(payload.get("args") or {})
                context = dict(payload.get("context") or {})

                if command not in HOSTED_COMMANDS:
                    return _json_response(
                        {
                            "ok": False,
                            "command": command,
                            "data": {
                                "hosted_mode": "practice-first",
                                "next_step": "Use the local/advanced CoQuery runtime for provider, production, or external database features.",
                            },
                            "error": {
                                "code": "hosted_command_unavailable",
                                "message": "This command is not exposed by the public practice-first PWA.",
                            },
                        },
                        400,
                    )

                if command == "practice_grade":
                    args["no_record"] = True

                if command == "practice_feedback":
                    # Public PWA feedback remains deterministic/static until a
                    # server-side provider policy and durable secret storage are added.
                    args.pop("provider_name", None)
                    args["mode"] = "static"

                result = run_command(command, args=args, context=context)
                if command == "practice_query":
                    result = enrich_practice_query_result(result, args)
                return _json_response(result, 200 if result.get("ok") else 400)
            except Exception as exc:
                return _json_response(
                    {
                        "ok": False,
                        "error": {"code": "worker_error", "message": str(exc)},
                    },
                    500,
                )

        if path.startswith("/api/"):
            return _json_response(
                {"ok": False, "error": {"code": "not_found", "message": f"Unknown endpoint: {path}"}},
                404,
            )

        return await self.env.ASSETS.fetch(request)
