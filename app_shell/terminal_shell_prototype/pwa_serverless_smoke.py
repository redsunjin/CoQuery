#!/usr/bin/env python3
"""Static checks for the CoQuery PWA + Cloudflare serverless scaffold."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = Path(__file__).resolve().parent


def require(path: Path, text: str) -> None:
    content = path.read_text(encoding="utf-8")
    if text not in content:
        raise AssertionError(f"{path} is missing expected text: {text}")


def main() -> int:
    manifest = json.loads((APP / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert manifest["display"] == "standalone"
    assert manifest["start_url"] == "./"
    assert manifest["icons"]

    wrangler = json.loads((ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
    assert wrangler["main"] == "./cloudflare_worker.py"
    assert "python_workers" in wrangler["compatibility_flags"]
    assert wrangler["assets"]["directory"] == "./app_shell/terminal_shell_prototype"
    assert "/api/*" in wrangler["assets"]["run_worker_first"]

    require(APP / "index.html", 'rel="manifest" href="./manifest.webmanifest"')
    require(APP / "index.html", '<script src="./pwa-runtime.js"></script>')
    require(APP / "service-worker.js", 'url.pathname.startsWith("/api/")')
    require(APP / "pwa-runtime.js", 'safeArgs.no_record = true')
    require(APP / "pwa-runtime.js", 'browser:localStorage')
    require(ROOT / "cloudflare_worker.py", 'HOSTED_COMMANDS = {')
    require(ROOT / "cloudflare_worker.py", 'args["no_record"] = True')
    require(ROOT / "cloudflare_worker.py", 'hosted_command_unavailable')
    require(APP / ".assetsignore", "*.py")

    print("PWA/serverless scaffold smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
