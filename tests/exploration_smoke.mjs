import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import initSqlJs from "sql.js";
const source = readFileSync(
  new URL(
    "../app_shell/terminal_shell_prototype/exploration.js",
    import.meta.url,
  ),
  "utf8",
);
const ctx = vm.createContext({});
vm.runInContext(source, ctx);
const SQL = await initSqlJs();
const sqlite = new SQL.Database();
const { fresh, restore, evaluate, same, sqlFor } = ctx.CoqueryExploration;
const plain = (x) => JSON.parse(JSON.stringify(x));
assert.deepEqual(plain(evaluate(fresh().project.rows, "and")), ["A"]);
assert.deepEqual(plain(evaluate(fresh().project.rows, "or")), ["A", "B", "C"]);
// All 256 assignments of two boolean conditions to four editable items.
for (let mask = 0; mask < 256; mask++) {
  const rows = Array.from({ length: 4 }, (_, i) => ({
    id: String(i),
    a: !!(mask & (1 << (i * 2))),
    b: !!(mask & (1 << (i * 2 + 1))),
  }));
  for (const mode of ["and", "or"]) {
    const expected = rows
      .filter((x) =>
        mode === "and"
          ? Number(x.a) + Number(x.b) === 2
          : Number(x.a) + Number(x.b) >= 1,
      )
      .map((x) => x.id);
    assert.deepEqual(plain(evaluate(rows, mode)), expected);
    const query = sqlFor(rows, mode);
    assert.ok(query.includes("\n"));
    assert.ok(!query.includes("\\n"));
    const actual = sqlite.exec(query)[0]?.values.map((row) => row[0]) || [];
    assert.deepEqual(actual, expected);
  }
}
sqlite.close();
const s = fresh();
s.stage = 5;
s.notes = "두 조건을 비교";
s.project.notes = "반례";
s.project.rows[0].name = "<img onerror=alert(1)>";
s.savedProject = plain(s.project);
s.project.title = "아직 저장 안 한 변경";
const restored = restore(JSON.parse(JSON.stringify(s)));
assert.equal(restored.savedProject.title, "나의 조건 퍼즐");
assert.equal(restored.project.title, "아직 저장 안 한 변경");
assert.equal(restored.project.rows[0].name, "<img onerror=alert(1)>"); // remains inert text, rendered escaped
assert.equal(restored.stage, 5);
assert.equal(restored.notes, s.notes);
for (const bad of [
  null,
  [],
  {},
  { version: 99 },
  {
    version: 1,
    stage: -3,
    project: { rows: [null], mode: "evil" },
    guided: { selected: ["Z", "A", "A"], checked: "yes" },
  },
]) {
  const v = restore(bad);
  assert.ok(v.stage >= 0 && v.stage <= 5);
  assert.equal(v.project.rows.length, 4);
  assert.ok(["and", "or"].includes(v.project.mode));
}
assert.deepEqual(
  plain(
    restore({
      version: 1,
      guided: { selected: ["Z", "A", "A"], checked: "yes" },
    }).guided,
  ),
  { selected: ["A"], checked: false },
);
assert.ok(same(["A"], ["A"]));
assert.ok(!same(["A"], ["A", "B"]));
const root = new URL("../", import.meta.url),
  read = (p) => readFileSync(new URL(p, root), "utf8");
for (const file of [
  "app_shell/terminal_shell_prototype/index.html",
  "app_shell/terminal_shell_prototype/service-worker.js",
  "scripts/build_ios_shell.mjs",
])
  assert.match(read(file), /exploration\.js/);
assert.match(
  read("app_shell/terminal_shell_prototype/index.html"),
  /id="explorationButton"/,
);
assert.doesNotMatch(source, /\bfetch\(|\beval\(|new Function/);
console.log(
  "exploration: 512 rule evaluations and real SQLite SQL examples, restoration, draft/saved separation and bundle contracts passed",
);
// Exercise UI event handlers without a browser; browser observations remain separate.
function surface(blocked = false) {
  let persisted = null;
  const buttons = new Map(),
    listeners = {};
  const liveStatus = { textContent: "" };
  const inert = { focus() {}, scrollIntoView() {}, scrollTo() {}, remove() {} };
  const host = {
    hidden: true,
    innerHTML: "",
    addEventListener(k, v) {
      listeners[k] = v;
    },
    querySelector(selector) {
      return selector === "#exploreStatus" ? liveStatus : inert;
    },
    querySelectorAll() {
      return [];
    },
  };
  const shell = { dataset: {} };
  const doc = {
    getElementById(id) {
      if (id === "explorationLearning") return host;
      if (!buttons.has(id))
        buttons.set(id, {
          ...inert,
          addEventListener(k, v) {
            this[k] = v;
          },
          click() {
            this.clickHandler?.();
          },
          hidden: false,
        });
      return buttons.get(id);
    },
    querySelector() {
      return shell;
    },
  };
  const storage = {
    getItem() {
      if (blocked) throw Error("blocked");
      return persisted;
    },
    setItem(k, v) {
      if (blocked) throw Error("blocked");
      persisted = v;
    },
    removeItem() {
      persisted = null;
    },
  };
  const c = vm.createContext({
    document: doc,
    localStorage: storage,
    setLearningHomeMode() {},
  });
  vm.runInContext(source, c);
  buttons.get("explorationButton").click();
  return {
    host,
    liveStatus,
    click(action, value = "") {
      listeners.click({
        target: {
          closest: () => ({
            dataset: { explore: action, value: String(value) },
          }),
        },
      });
    },
    input(dataset, value) {
      listeners.input({ target: { dataset, value } });
    },
    change(dataset, value, checked) {
      listeners.change({
        target: { dataset, value, checked, type: "checkbox" },
      });
    },
    state: () => JSON.parse(persisted),
  };
}
const ui = surface();
ui.click("stage", 5);
ui.click("save-project");
assert.match(ui.host.innerHTML, /퍼즐과 설명 저장/);
assert.equal(ui.state().project.saved, false);
ui.input({ project: "title" }, "<b>비 오는 날</b>");
ui.input({ note: "project" }, "조건과 반례를 기록");
ui.click("run");
ui.click("save-project");
assert.equal(ui.state().project.saved, true);
assert.equal(ui.state().savedProject.title, "<b>비 오는 날</b>");
assert.match(ui.host.innerHTML, /&lt;b&gt;비 오는 날&lt;\/b&gt;/);
ui.input({ project: "title" }, "수정 초안");
assert.equal(ui.state().project.checked, false);
assert.equal(ui.state().project.saved, false);
ui.click("replay");
assert.equal(ui.state().project.title, "<b>비 오는 날</b>");
assert.equal(ui.state().project.checked, false);
ui.change({ row: "1", prop: "b" }, "", true);
ui.click("run");
assert.match(ui.host.innerHTML, /실제: A · B/);
ui.click("stage", 1);
ui.click("next");
assert.equal(ui.state().stage, 1);
assert.match(ui.liveStatus.textContent, /안내형과 독립형을 모두 실험/);
const temp = surface(true);
assert.match(temp.host.innerHTML, /현재 탭에서만 유지/);
temp.click("stage", 5);
temp.input({ note: "project" }, "임시 설명");
temp.click("run");
temp.click("save-project");
assert.match(temp.host.innerHTML, /현재 탭에서만 유지/);
assert.doesNotMatch(temp.host.innerHTML, /이 기기에 퍼즐과 설명을 저장/);
console.log(
  "exploration UI contracts: incomplete progress, escaped labels, changed-result invalidation, saved replay, blocked storage passed",
);
