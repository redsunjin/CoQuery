#!/usr/bin/env python3
"""Agent wrapper for repeatable CoQuery CLI operations."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def default_install_root() -> Path:
    return Path.home() / ".codex" / "skills"


def load_capabilities_manifest() -> dict[str, Any]:
    manifest_path = skill_dir() / "references" / "capabilities.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _is_repo(path: Path) -> bool:
    return (path / "main.py").is_file() and (path / "sql_cli").is_dir()


def _candidate_roots(script_path: Path) -> list[Path]:
    candidates: list[Path] = []

    env_repo = os.environ.get("COQUERY_REPO")
    if env_repo:
        candidates.append(Path(env_repo).expanduser())

    cwd = Path.cwd()
    candidates.append(cwd)
    candidates.extend(cwd.parents)

    candidates.append(script_path.parent)
    candidates.extend(script_path.parents)

    return candidates


def find_repo(explicit_repo: str | None = None) -> Path:
    if explicit_repo:
        repo = Path(explicit_repo).expanduser().resolve()
        if _is_repo(repo):
            return repo
        raise SystemExit(f"Not a CoQuery repository: {repo}")

    script_path = Path(__file__).resolve()
    seen: set[Path] = set()
    for candidate in _candidate_roots(script_path):
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if _is_repo(resolved):
            return resolved

    raise SystemExit("Could not find CoQuery repo. Pass --repo or set COQUERY_REPO.")


def maybe_find_repo(explicit_repo: str | None = None) -> Path | None:
    try:
        return find_repo(explicit_repo)
    except SystemExit:
        return None


def _tail(text: str, max_chars: int = 4000) -> str:
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def create_join_demo_db(db_path: Path) -> Path:
    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("CREATE TABLE orgs (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)")
        conn.execute(
            "CREATE TABLE members ("
            "id INTEGER PRIMARY KEY, "
            "org_id INTEGER NOT NULL, "
            "email TEXT NOT NULL, "
            "FOREIGN KEY (org_id) REFERENCES orgs(id) ON DELETE CASCADE"
            ")"
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def run_process(repo: Path, args: list[str], name: str) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    payload: dict[str, Any] | None = None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = None

    return {
        "name": name,
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "payload": payload,
        "stdout": _tail(result.stdout),
        "stderr": _tail(result.stderr),
    }


def coquery_command(repo: Path, cli_args: list[str], name: str) -> dict[str, Any]:
    return run_process(repo, [sys.executable, "main.py", *cli_args], name)


def command_describe(args: argparse.Namespace) -> int:
    manifest = load_capabilities_manifest()
    repo = maybe_find_repo(args.repo)
    package_dir = skill_dir()
    refs = {
        name: {
            "relative_path": relative_path,
            "absolute_path": str((package_dir / relative_path).resolve()),
        }
        for name, relative_path in manifest["references"].items()
    }

    payload = {
        "ok": True,
        "skill": {
            **manifest["skill"],
            "source_dir": str(package_dir),
            "default_install_root": str(default_install_root()),
            "default_install_dir": str(default_install_root() / manifest["skill"]["name"]),
        },
        "repo": {
            "detected": repo is not None,
            "path": str(repo) if repo is not None else None,
            "env_var": "COQUERY_REPO",
        },
        "wrapper_commands": manifest["wrapper_commands"],
        "run_passthrough_flags": manifest["run_passthrough_flags"],
        "coquery_commands": manifest["coquery_commands"],
        "backend_support": manifest["backend_support"],
        "driver_requirements": manifest["driver_requirements"],
        "references": refs,
        "consumption_notes": manifest["consumption_notes"],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    repo = find_repo(args.repo)
    with tempfile.TemporaryDirectory(prefix="coquery-agent-verify-") as tmpdir:
        join_db = create_join_demo_db(Path(tmpdir) / "join-verify.db")
        checks = [
            coquery_command(repo, ["--help"], "help"),
            coquery_command(repo, ["--command", "schema", "--db", "example.db", "--format", "json"], "sqlite_schema"),
            coquery_command(
                repo,
                ["--command", "schema_detail", "--db", "example.db", "--table", "users", "--format", "json"],
                "sqlite_schema_detail",
            ),
            coquery_command(
                repo,
                [
                    "--command",
                    "generate",
                    "--db",
                    str(join_db),
                    "--skill",
                    "join_inner",
                    "--params",
                    '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}',
                    "--format",
                    "json",
                ],
                "schema_detail_join_generate",
            ),
            coquery_command(
                repo,
                [
                    "--command",
                    "generate",
                    "--db",
                    str(join_db),
                    "--skill",
                    "join_left",
                    "--params",
                    '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}',
                    "--format",
                    "json",
                ],
                "schema_detail_left_join_generate",
            ),
            run_process(repo, [sys.executable, "sql_cli/tests/test_core.py"], "baseline_tests"),
        ]

        if args.postgres:
            checks.append(run_process(repo, ["bash", "scripts/run_postgresql_local_smoke.sh"], "postgres_smoke"))

    payload = {
        "ok": all(check["ok"] for check in checks),
        "repo": str(repo),
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["ok"] else 1


def command_install_skill(args: argparse.Namespace) -> int:
    manifest = load_capabilities_manifest()
    package_dir = skill_dir()
    repo = maybe_find_repo(args.repo)
    skill_name = args.skill_name or manifest["skill"]["name"]
    target_root = Path(args.target_root).expanduser().resolve() if args.target_root else default_install_root().resolve()
    target_dir = target_root / skill_name

    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package_dir, target_dir, dirs_exist_ok=True)

    payload = {
        "ok": True,
        "skill_name": skill_name,
        "source_dir": str(package_dir),
        "target_root": str(target_root),
        "target_dir": str(target_dir),
        "repo_detected": repo is not None,
        "repo_path": str(repo) if repo is not None else None,
        "repo_hint_env_var": "COQUERY_REPO",
        "repo_hint_value": str(repo) if repo is not None else None,
        "next_steps": [
            f"Use {target_dir / 'scripts' / 'coquery_agent.py'} describe --repo /path/to/CoQuery",
            f"Use {target_dir / 'scripts' / 'coquery_agent.py'} verify --repo /path/to/CoQuery",
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def command_demo(args: argparse.Namespace) -> int:
    repo = find_repo(args.repo)
    fixture = repo / "example.db"
    if not fixture.exists():
        raise SystemExit(f"Missing fixture database: {fixture}")

    with tempfile.TemporaryDirectory(prefix="coquery-agent-demo-") as tmpdir:
        demo_db = Path(tmpdir) / "demo.db"
        join_db = create_join_demo_db(Path(tmpdir) / "join-demo.db")
        shutil.copy2(fixture, demo_db)

        checks = [
            coquery_command(repo, ["--command", "schema", "--db", str(demo_db), "--format", "json"], "schema"),
            coquery_command(
                repo,
                ["--command", "schema_detail", "--db", str(demo_db), "--table", "users", "--format", "json"],
                "schema_detail",
            ),
            coquery_command(repo, ["--command", "generate", "--db", str(demo_db), "--skill", "select_simple", "--format", "json"], "generate"),
            coquery_command(
                repo,
                [
                    "--command",
                    "generate",
                    "--db",
                    str(join_db),
                    "--skill",
                    "join_inner",
                    "--params",
                    '{"table1":"members","table2":"orgs","cols":["members.email","orgs.name"]}',
                    "--format",
                    "json",
                ],
                "generate_join",
            ),
            coquery_command(
                repo,
                [
                    "--command",
                    "generate",
                    "--db",
                    str(join_db),
                    "--skill",
                    "join_left",
                    "--params",
                    '{"table1":"orgs","table2":"members","cols":["orgs.name","members.email"]}',
                    "--format",
                    "json",
                ],
                "generate_left_join",
            ),
            coquery_command(repo, ["--command", "natural", "--db", str(demo_db), "--sql", "show users", "--format", "json"], "natural"),
            coquery_command(
                repo,
                [
                    "--command",
                    "insert",
                    "--db",
                    str(demo_db),
                    "--write",
                    "--sql",
                    "INSERT INTO users (name, age) VALUES ('agent_demo_user', 30)",
                    "--format",
                    "json",
                ],
                "insert",
            ),
            coquery_command(
                repo,
                [
                    "--command",
                    "query",
                    "--db",
                    str(demo_db),
                    "--sql",
                    "SELECT name, age FROM users WHERE name = 'agent_demo_user'",
                    "--format",
                    "json",
                ],
                "query_after_insert",
            ),
            coquery_command(
                repo,
                [
                    "--command",
                    "update",
                    "--db",
                    str(demo_db),
                    "--write",
                    "--sql",
                    "UPDATE users SET age = 31 WHERE name = 'agent_demo_user'",
                    "--format",
                    "json",
                ],
                "update",
            ),
            coquery_command(
                repo,
                [
                    "--command",
                    "delete",
                    "--db",
                    str(demo_db),
                    "--write",
                    "--sql",
                    "DELETE FROM users WHERE name = 'agent_demo_user'",
                    "--format",
                    "json",
                ],
                "delete",
            ),
            coquery_command(
                repo,
                [
                    "--command",
                    "query",
                    "--db",
                    str(demo_db),
                    "--sql",
                    "SELECT COUNT(*) FROM users WHERE name = 'agent_demo_user'",
                    "--format",
                    "json",
                ],
                "query_after_delete",
            ),
        ]

    payload = {
        "ok": all(check["ok"] for check in checks),
        "repo": str(repo),
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["ok"] else 1


def command_run(args: argparse.Namespace) -> int:
    repo = find_repo(args.repo)
    cli_args = ["--command", args.command, "--format", args.format]

    if args.db is not None:
        cli_args.extend(["--db", args.db])
    if args.db_uri is not None:
        cli_args.extend(["--db-uri", args.db_uri])
    if args.sql is not None:
        cli_args.extend(["--sql", args.sql])
    if args.table is not None:
        cli_args.extend(["--table", args.table])
    if args.skill is not None:
        cli_args.extend(["--skill", args.skill])
    if args.params is not None:
        cli_args.extend(["--params", args.params])
    if args.provider_name is not None:
        cli_args.extend(["--provider-name", args.provider_name])
    if args.provider_kind is not None:
        cli_args.extend(["--provider-kind", args.provider_kind])
    if args.preset is not None:
        cli_args.extend(["--preset", args.preset])
    if args.model_name is not None:
        cli_args.extend(["--model-name", args.model_name])
    if args.base_url is not None:
        cli_args.extend(["--base-url", args.base_url])
    if args.chat_completions_url is not None:
        cli_args.extend(["--chat-completions-url", args.chat_completions_url])
    if args.models_url is not None:
        cli_args.extend(["--models-url", args.models_url])
    if args.api_key_env is not None:
        cli_args.extend(["--api-key-env", args.api_key_env])
    if args.jpa_project is not None:
        cli_args.extend(["--jpa-project", args.jpa_project])
    if args.dialect is not None:
        cli_args.extend(["--dialect", args.dialect])
    if args.topic is not None:
        cli_args.extend(["--topic", args.topic])
    if args.lang is not None:
        cli_args.extend(["--lang", args.lang])
    if args.pack is not None:
        cli_args.extend(["--pack", args.pack])
    if args.problem_id is not None:
        cli_args.extend(["--problem-id", args.problem_id])
    if args.limit is not None:
        cli_args.extend(["--limit", str(args.limit)])
    if args.write:
        cli_args.append("--write")
    if args.dry_run:
        cli_args.append("--dry-run")
    if args.max_affected_rows is not None:
        cli_args.extend(["--max-affected-rows", str(args.max_affected_rows)])
    if args.allow_full_table_write:
        cli_args.append("--allow-full-table-write")
    if args.no_record:
        cli_args.append("--no-record")

    result = coquery_command(repo, cli_args, args.command)
    if result["payload"] is not None:
        print(json.dumps(result["payload"], indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent wrapper for CoQuery CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    describe = subparsers.add_parser("describe", help="Emit machine-readable capability metadata")
    describe.add_argument("--repo", default=None, help="Optional path to the CoQuery repository")
    describe.set_defaults(func=command_describe)

    verify = subparsers.add_parser("verify", help="Run readiness checks")
    verify.add_argument("--repo", default=None, help="Path to the CoQuery repository")
    verify.add_argument("--postgres", action="store_true", help="Also run the PostgreSQL local smoke")
    verify.set_defaults(func=command_verify)

    demo = subparsers.add_parser("demo", help="Run a safe SQLite demo on a temporary database copy")
    demo.add_argument("--repo", default=None, help="Path to the CoQuery repository")
    demo.set_defaults(func=command_demo)

    run = subparsers.add_parser("run", help="Run one CoQuery CLI command")
    run.add_argument("--repo", default=None, help="Path to the CoQuery repository")
    run.add_argument("--command", required=True, help="CoQuery command name")
    run.add_argument("--db", default=None, help="SQLite path or legacy DB target")
    run.add_argument("--db-uri", default=None, help="Preferred multi-backend database URI")
    run.add_argument("--sql", default=None, help="SQL or natural-language text")
    run.add_argument("--table", default=None, help="Optional table name for schema_detail")
    run.add_argument("--skill", default=None, help="SQL generation skill id")
    run.add_argument("--params", default=None, help="JSON parameters payload")
    run.add_argument("--provider-name", default=None, help="Registered provider name")
    run.add_argument("--provider-kind", default=None, help="Provider kind")
    run.add_argument("--preset", default=None, help="Known provider preset name")
    run.add_argument("--model-name", default=None, help="Provider model name")
    run.add_argument("--base-url", default=None, help="Provider base URL")
    run.add_argument("--chat-completions-url", default=None, help="Direct chat completions endpoint override")
    run.add_argument("--models-url", default=None, help="Direct model listing endpoint override")
    run.add_argument("--api-key-env", default=None, help="Provider API key environment variable name")
    run.add_argument("--jpa-project", default=None, help="Path to a Java/JPA project or .java entity file")
    run.add_argument("--dialect", default=None, help="Knowledge dialect")
    run.add_argument("--topic", default=None, help="Knowledge or help topic")
    run.add_argument("--lang", default=None, help="Help language: ko or en")
    run.add_argument("--pack", default=None, help="Practice pack id")
    run.add_argument("--problem-id", default=None, help="Practice problem id")
    run.add_argument("--limit", type=int, default=None, help="Practice query or attempts row limit")
    run.add_argument("--format", default="json", help="Output format")
    run.add_argument("--write", action="store_true", help="Confirm state-changing SQL")
    run.add_argument("--dry-run", action="store_true", help="Run state-changing SQL in rollback-only preview mode")
    run.add_argument("--max-affected-rows", type=int, default=None, help="Abort and roll back if a write affects too many rows")
    run.add_argument(
        "--allow-full-table-write",
        action="store_true",
        help="Allow UPDATE/DELETE or write-mode query statements without WHERE",
    )
    run.add_argument("--no-record", action="store_true", help="Do not write a practice_grade attempt record")
    run.set_defaults(func=command_run)

    install = subparsers.add_parser("install-skill", help="Copy this skill package into a Codex skills directory")
    install.add_argument("--repo", default=None, help="Optional path to the CoQuery repository for repo hints")
    install.add_argument("--target-root", default=None, help="Destination skills root directory")
    install.add_argument("--skill-name", default=None, help="Installed skill directory name")
    install.set_defaults(func=command_install_skill)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
