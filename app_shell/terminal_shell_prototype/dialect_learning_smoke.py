#!/usr/bin/env python3
"""Deterministic contract checks for the optional SQL dialect lessons."""

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP = Path(__file__).resolve().parent
CATALOG_SOURCE = APP / "dialect-learning.js"


def load_catalog() -> dict:
    script = """
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
const context = { globalThis: {} };
vm.createContext(context);
vm.runInContext(source, context, { filename: process.argv[1] });
const api = context.globalThis.CoQueryDialectLearning;
console.log(JSON.stringify({ catalog: api.DialectCatalog, mapped: {
  customer_names_segments: api.lessonsForProblem('customer_names_segments').map((lesson) => lesson.id),
  march_orders: api.lessonsForProblem('march_orders').map((lesson) => lesson.id),
  largest_orders: api.lessonsForProblem('largest_orders').map((lesson) => lesson.id),
  basic_select_customers: api.lessonsForProblem('basic_select_customers').map((lesson) => lesson.id)
} }));
"""
    result = subprocess.run(
        ["node", "-e", script, str(CATALOG_SOURCE)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def require(path: Path, text: str) -> None:
    if text not in path.read_text(encoding="utf-8"):
        raise AssertionError(f"{path.name} is missing expected dialect-learning contract: {text}")


def main() -> int:
    loaded = load_catalog()
    catalog = loaded["catalog"]
    lessons = catalog["lessons"]

    assert catalog["id"] == "coquery-sql-dialect-learning"
    assert catalog["version"] == "2026-09-02"
    assert [lesson["id"] for lesson in lessons] == [
        "string_concatenation",
        "current_date_time",
        "date_arithmetic",
        "limit_rows",
    ]
    assert loaded["mapped"] == {
        "customer_names_segments": ["string_concatenation"],
        "march_orders": ["current_date_time", "date_arithmetic"],
        "largest_orders": ["limit_rows"],
        "basic_select_customers": [],
    }

    allowed_states = {"common", "reference", "verified"}
    sqlite_verified_sql: dict[str, str] = {}
    for lesson in lessons:
        assert lesson["relatedProblemIds"], f"{lesson['id']} must map to at least one problem"
        for language in ("ko", "en"):
            copy = lesson["copy"][language]
            assert all(copy[key] for key in ("concept", "intent", "commonExplanation", "whyItDiffers"))
            assert [variant["engine"] for variant in copy["variants"]] == ["postgresql", "mysql", "sqlite"]
            for variant in copy["variants"]:
                assert variant["verificationState"] in allowed_states
                assert variant["sql"] and variant["explanation"]
                if variant["engine"] == "mysql":
                    assert variant["verificationState"] == "reference", "MySQL must remain reference-only"
                if language == "en" and variant["engine"] == "sqlite" and variant["verificationState"] == "verified":
                    sqlite_verified_sql[lesson["id"]] = variant["sql"]

    assert set(sqlite_verified_sql) == {"string_concatenation", "current_date_time", "date_arithmetic"}
    connection = sqlite3.connect(":memory:")
    try:
        assert connection.execute(sqlite_verified_sql["string_concatenation"]).fetchone()[0] == "Ada Lovelace"
        current_datetime = connection.execute(sqlite_verified_sql["current_date_time"]).fetchone()[0]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", current_datetime or "")
        assert connection.execute(sqlite_verified_sql["date_arithmetic"]).fetchone()[0] == "2026-09-09"
    finally:
        connection.close()

    index = APP / "index.html"
    app_js = APP / "app.js"
    styles = APP / "styles.css"
    service_worker = APP / "service-worker.js"
    ios_builder = ROOT / "scripts" / "build_ios_shell.mjs"
    require(index, '<script src="./dialect-learning.js"></script>')
    require(app_js, "function dialectLessonsForProblem(problemId)")
    require(app_js, "data-dialect-toggle")
    require(app_js, "aria-expanded=\"false\"")
    require(app_js, "function bindDialectComparison(block)")
    require(styles, ".dialect-comparison-panel")
    require(styles, ".dialect-verification-state")
    require(service_worker, '"./dialect-learning.js"')
    require(ios_builder, 'cpSync(join(sourceDir, "dialect-learning.js"), join(distDir, "dialect-learning.js"));')

    print("dialect learning smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
