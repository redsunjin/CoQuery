#!/usr/bin/env python3
"""Prepare an isolated Cloudflare Worker bundle for CoQuery.

The source repository contains local tooling, tests, virtual environments, and
other files that must never be discovered as Worker modules. This script builds
an explicit deployment tree and writes Wrangler's generated-config redirect so
`pywrangler deploy` uses only the staged runtime files.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = ROOT / ".cloudflare-build"
SRC_ROOT = BUILD_ROOT / "src"
ASSET_ROOT = BUILD_ROOT / "assets"
WRANGLER_DIR = ROOT / ".wrangler" / "deploy"


def _ignore_runtime_noise(_directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in {"tests", "__pycache__", ".runtime", ".gitignore", ".assetsignore", "README.md"}:
            ignored.add(name)
        elif name.endswith((".pyc", ".pyo")):
            ignored.add(name)
    return ignored


def _ignore_static_noise(_directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in {".runtime", "__pycache__", ".gitignore", ".assetsignore", "README.md"}:
            ignored.add(name)
        elif name.endswith((".py", ".pyc", ".pyo")):
            ignored.add(name)
    return ignored


def copy_tree(source: Path, destination: Path, ignore) -> None:
    if not source.exists():
        raise SystemExit(f"Missing required Cloudflare bundle source: {source}")
    shutil.copytree(source, destination, ignore=ignore)


def main() -> int:
    if BUILD_ROOT.exists():
        shutil.rmtree(BUILD_ROOT)
    BUILD_ROOT.mkdir(parents=True)
    SRC_ROOT.mkdir(parents=True)

    shutil.copy2(ROOT / "cloudflare_worker.py", SRC_ROOT / "cloudflare_worker.py")
    copy_tree(ROOT / "sql_cli", SRC_ROOT / "sql_cli", _ignore_runtime_noise)
    copy_tree(ROOT / "practice_packs", SRC_ROOT / "practice_packs", _ignore_runtime_noise)
    copy_tree(ROOT / "knowledge", SRC_ROOT / "knowledge", _ignore_runtime_noise)
    copy_tree(
        ROOT / "app_shell" / "terminal_shell_prototype",
        ASSET_ROOT,
        _ignore_static_noise,
    )

    config = {
        "name": "coquery-pwa",
        "main": "./src/cloudflare_worker.py",
        "compatibility_date": "2026-08-28",
        "compatibility_flags": ["python_workers"],
        "find_additional_modules": True,
        "base_dir": "./src",
        "rules": [
            {
                "type": "Data",
                "globs": ["practice_packs/**/*.json", "knowledge/**/*.json"],
                "fallthrough": True,
            }
        ],
        "assets": {
            "directory": "./assets",
            "binding": "ASSETS",
            "not_found_handling": "single-page-application",
            "run_worker_first": ["/api/*"],
        },
        "observability": {"enabled": True},
    }
    config_path = BUILD_ROOT / "wrangler.jsonc"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    WRANGLER_DIR.mkdir(parents=True, exist_ok=True)
    redirect = {"configPath": "../../.cloudflare-build/wrangler.jsonc"}
    (WRANGLER_DIR / "config.json").write_text(json.dumps(redirect) + "\n", encoding="utf-8")

    runtime_files = sum(1 for item in SRC_ROOT.rglob("*") if item.is_file())
    asset_files = sum(1 for item in ASSET_ROOT.rglob("*") if item.is_file())
    print(f"Prepared Cloudflare bundle: {runtime_files} runtime files, {asset_files} asset files")
    print(f"Generated config: {config_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
