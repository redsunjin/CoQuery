import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const root = resolve(new URL("..", import.meta.url).pathname);
const distDir = join(root, "dist", "ios-shell");
const runtimePath = join(distDir, "ios-training-runtime.js");
const capacitorConfigPath = join(root, "capacitor.config.json");

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function assertFile(path) {
  assert.equal(existsSync(path), true, `${path} should exist`);
}

assertFile(capacitorConfigPath);
const capacitorConfig = readJson(capacitorConfigPath);
assert.equal(capacitorConfig.appId, "app.coquery.training");
assert.equal(capacitorConfig.appName, "CoQuery");
assert.equal(capacitorConfig.webDir, "dist/ios-shell");

assertFile(join(distDir, "index.html"));
assertFile(join(distDir, "app.js"));
assertFile(join(distDir, "styles.css"));
assertFile(runtimePath);
assertFile(join(distDir, "practice_packs", "sql_basics.json"));

const indexHtml = readFileSync(join(distDir, "index.html"), "utf8");
assert.match(indexHtml, /<script type="module" src="\.\/ios-training-runtime\.js"><\/script>/);
assert.match(indexHtml, /<script type="module" src="\.\/app\.js"><\/script>/);
assert.match(indexHtml, /commandMenuToggle/);
assert.match(indexHtml, /aria-expanded="false"/);
assert.match(indexHtml, /commandMenuPanel/);
assert.match(indexHtml, /<h1 data-i18n="appTitle">CoQuery<\/h1>/);
assert.match(indexHtml, /hidden/);
assert.ok(
  indexHtml.indexOf("ios-training-runtime.js") < indexHtml.indexOf("./app.js"),
  "local runtime should load before app.js"
);

const appJs = readFileSync(join(distDir, "app.js"), "utf8");
assert.match(appJs, /coqueryCommandRuntime/);
assert.match(appJs, /setCommandMenuOpen/);
assert.match(appJs, /wrong-note-card/);
assert.match(appJs, /data-retry-practice/);
assert.match(appJs, /data-provider-feedback/);
assert.match(appJs, /AI-generated feedback/);
assert.match(appJs, /documentTitle: "CoQuery"/);

const runtime = await import(pathToFileURL(runtimePath).href);
let apiFetchCalled = false;
const originalFetch = globalThis.fetch;
globalThis.fetch = async (input) => {
  if (String(input).includes("/api/commands/run")) {
    apiFetchCalled = true;
  }
  throw new Error(`unexpected fetch in local runtime: ${input}`);
};

try {
  const result = await runtime.postCommand("practice_list", {}, {});
  assert.equal(apiFetchCalled, false, "practice_list should not call the Python HTTP API");
  assert.equal(result.ok, true);
  assert.equal(result.command, "practice_list");
  assert.equal(result.block_type, "practice_list");
  assert.deepEqual(result.actions, ["copy", "start_practice", "show_schema"]);
  assert.equal(result.data.selected_pack, "sql_basics");
  assert.equal(result.data.problems.length, 5);
  assert.equal(result.data.problems[0].id, "basic_select_customers");
  assert.match(result.cli_equivalent, /python main\.py --command practice_list/);

  const staticFeedback = await runtime.postCommand(
    "practice_feedback",
    { problem_id: "basic_select_customers", sql: "SELECT id, name FROM customers ORDER BY id" },
    {}
  );
  assert.equal(staticFeedback.ok, true);
  assert.equal(staticFeedback.command, "practice_feedback");
  assert.equal(staticFeedback.block_type, "practice_feedback");
  assert.equal(staticFeedback.data.feedback.source, "static");
  assert.equal(staticFeedback.data.feedback.ai_generated, false);
  assert.equal(staticFeedback.data.provider_feedback_allowed, false);
  assert.match(staticFeedback.data.expected_issue, /region/);

  const providerBlocked = await runtime.postCommand(
    "practice_feedback",
    {
      problem_id: "basic_select_customers",
      sql: "SELECT id, name FROM customers ORDER BY id",
      provider_name: "local_ollama",
      mode: "review",
    },
    {}
  );
  assert.equal(providerBlocked.ok, false);
  assert.equal(providerBlocked.error.code, "provider_feedback_training_only");
} finally {
  globalThis.fetch = originalFetch;
}

assertFile(join(root, "ios", "App", "App.xcodeproj", "project.pbxproj"));
assertFile(join(root, "docs", "testflight-metadata-checklist.md"));

console.log("ios shell smoke passed");
