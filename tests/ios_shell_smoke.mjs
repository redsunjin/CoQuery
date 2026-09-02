import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import vm from "node:vm";

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
assertFile(join(distDir, "onboarding.css"));
assertFile(join(distDir, "practice-focus.css"));
assertFile(join(distDir, "learning-path.css"));
assertFile(join(distDir, "onboarding.js"));
assertFile(join(distDir, "practice-focus.js"));
assertFile(join(distDir, "learning-path.js"));
assertFile(join(distDir, "curriculum-expansion.js"));
assertFile(runtimePath);
assertFile(join(distDir, "practice_packs", "sql_basics.json"));

const indexHtml = readFileSync(join(distDir, "index.html"), "utf8");
assert.match(indexHtml, /<script src="\.\/ios-training-runtime\.js"><\/script>/);
assert.match(indexHtml, /<script src="\.\/app\.js"><\/script>/);
assert.match(indexHtml, /<script src="\.\/onboarding\.js"><\/script>/);
assert.doesNotMatch(indexHtml, /pwa-runtime\.js/);
assert.match(indexHtml, /https:\/\/redsunjin\.github\.io\/CoQuery\/privacy\//);
assert.match(indexHtml, /id="privacyPolicyLink"/);
assert.match(indexHtml, /privacy\/\?lang=ko/);
assert.match(indexHtml, /viewport-fit=cover/);
assert.match(indexHtml, /commandMenuToggle/);
assert.match(indexHtml, /aria-expanded="false"/);
assert.match(indexHtml, /commandMenuPanel/);
assert.match(indexHtml, /id="detailBackdrop"/);
assert.match(indexHtml, /aria-controls="detailPanel"/);
assert.match(indexHtml, /<h1 data-i18n="appTitle">CoQuery<\/h1>/);
assert.match(indexHtml, /hidden/);
assert.ok(
  indexHtml.indexOf("ios-training-runtime.js") < indexHtml.indexOf("./app.js") &&
    indexHtml.indexOf("./app.js") < indexHtml.indexOf("./onboarding.js"),
  "local runtime, app shell, and onboarding scripts should load in dependency order"
);

const appJs = readFileSync(join(distDir, "app.js"), "utf8");
assert.match(appJs, /coqueryCommandRuntime/);
assert.match(appJs, /setCommandMenuOpen/);
assert.match(appJs, /wrong-note-card/);
assert.match(appJs, /data-retry-practice/);
assert.match(appJs, /data-provider-feedback/);
assert.match(appJs, /AI-generated feedback/);
assert.match(appJs, /documentTitle: "CoQuery"/);
assert.match(appJs, /function setDetailOpen\(open\)/);
assert.match(appJs, /detailBackdrop\?\.addEventListener\("click"/);

const stylesCss = readFileSync(join(distDir, "styles.css"), "utf8");
const onboardingCss = readFileSync(join(distDir, "onboarding.css"), "utf8");
const onboardingJs = readFileSync(join(distDir, "onboarding.js"), "utf8");
assert.match(stylesCss, /--safe-area-top:\s*env\(safe-area-inset-top, 0px\)/);
assert.match(stylesCss, /--safe-area-bottom:\s*env\(safe-area-inset-bottom, 0px\)/);
assert.match(stylesCss, /min-height:\s*calc\(60px \+ var\(--safe-area-top\)\)/);
assert.match(stylesCss, /grid-template-rows:\s*auto minmax\(0, 1fr\) auto/);
assert.match(stylesCss, /\.command-menu-popover\s*\{[^}]*position:\s*fixed;/s);
assert.match(stylesCss, /\.lang-button\s*\{[^}]*min-width:\s*44px;[^}]*min-height:\s*44px;/s);
assert.match(stylesCss, /\.context-chip\s*\{[^}]*min-height:\s*44px;/s);
assert.match(onboardingCss, /\.app-shell\[data-home-mode="true"\]\s+\.terminal-scroll\s*\{\s*align-items:\s*start;/s);
assert.match(onboardingCss, /\.learning-home\s*\{\s*margin:\s*0 auto;\s*padding:\s*34px 18px 44px;/s);
assert.match(onboardingCss, /\.learning-home-privacy a\s*\{[^}]*text-decoration:\s*underline;/s);
assert.match(onboardingJs, /privacyPolicyLink\.href/);
assert.match(stylesCss, /--panel-overlay:\s*#24261f;/);
assert.match(stylesCss, /\.detail-backdrop\s*\{[^}]*background:\s*rgba\(2, 3, 2, 0\.58\);/s);
assert.match(stylesCss, /\.detail-panel\s*\{[^}]*border-radius:\s*18px 18px 0 0;/s);

const runtimeSource = readFileSync(runtimePath, "utf8");
assert.doesNotMatch(runtimeSource, /\bexport\s+(?:async\s+)?(?:function|const)\b/);
const runtimeContext = vm.createContext({ window: {}, fetch: () => Promise.reject(new Error("unexpected fetch")) });
vm.runInContext(runtimeSource, runtimeContext, { filename: runtimePath });
const runtime = runtimeContext.window.coqueryCommandRuntime;
assert.ok(runtime, "the iOS runtime should register the window command adapter");

const result = await runtime.postCommand("practice_list", {}, {});
assert.equal(result.ok, true);
assert.equal(result.command, "practice_list");
assert.equal(result.block_type, "practice_list");
assert.deepEqual(Array.from(result.actions), ["copy", "start_practice", "show_schema"]);
assert.equal(result.data.selected_pack, "sql_basics");
assert.equal(result.data.problems.length, 24);
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

assertFile(join(root, "ios", "App", "App.xcodeproj", "project.pbxproj"));
const projectFile = readFileSync(join(root, "ios", "App", "App.xcodeproj", "project.pbxproj"), "utf8");
assert.match(projectFile, /MARKETING_VERSION = 0\.8\.0;/);
assertFile(join(root, "docs", "testflight-metadata-checklist.md"));
const privacyPolicy = readFileSync(join(root, "docs", "privacy", "index.html"), "utf8");
assert.match(privacyPolicy, /data-policy-lang="ko"/);
assert.match(privacyPolicy, /data-policy-lang="en"/);
assert.match(privacyPolicy, /개인정보 처리방침/);
assert.match(privacyPolicy, /new URLSearchParams\(window\.location\.search\)/);

console.log("ios shell smoke passed");
