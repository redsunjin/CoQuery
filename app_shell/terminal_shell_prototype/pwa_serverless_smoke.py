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
    require(ROOT / "cloudflare_worker.py", 'enrich_practice_query_result')
    require(ROOT / "cloudflare_worker.py", 'if command == "practice_query"')
    require(ROOT / "cloudflare_worker.py", 'return await self.env.ASSETS.fetch(request)')
    require(ROOT / "sql_cli" / "result_integration.py", 'data["result_intelligence"] = classify_result')
    require(APP / ".assetsignore", "*.py")

    bundle_script = ROOT / "scripts" / "prepare_cloudflare_bundle.py"
    require(bundle_script, 'BUILD_ROOT = ROOT / ".cloudflare-build"')
    require(bundle_script, '"run_worker_first": True')
    require(bundle_script, '"configPath": "../../.cloudflare-build/wrangler.jsonc"')

    temporary_workflow = ROOT / ".github" / "workflows" / "cloudflare-temporary-deploy.yml"
    require(temporary_workflow, "pywrangler deploy --temporary")
    require(temporary_workflow, "Verify hosted practice API")
    require(temporary_workflow, '"command":"practice_grade"')

    production_workflow = ROOT / ".github" / "workflows" / "cloudflare-production-deploy.yml"
    require(production_workflow, "workflow_dispatch:")
    require(production_workflow, "environment: production")
    require(production_workflow, "CLOUDFLARE_API_TOKEN")
    require(production_workflow, "CLOUDFLARE_ACCOUNT_ID")
    require(production_workflow, "python3 scripts/prepare_cloudflare_bundle.py")
    require(production_workflow, "uv run pywrangler deploy")
    require(production_workflow, "Verify production health endpoint")
    require(production_workflow, "Verify PWA shell and manifest")
    require(production_workflow, "Verify hosted practice API")
    if "pywrangler deploy --temporary" in production_workflow.read_text(encoding="utf-8"):
        raise AssertionError("production deployment must not use a temporary Cloudflare account")

    gitignore = ROOT / ".gitignore"
    require(gitignore, ".cloudflare-build/")
    require(gitignore, ".wrangler/")
    require(gitignore, ".venv-workers/")

    print("PWA/serverless scaffold smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
