#!/usr/bin/env node

await import("./practice-result-views.js");
const api = globalThis.coqueryPracticeResultViews || {};

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

requireCondition(typeof api.availableViewNames === "function", "availableViewNames export missing");
requireCondition(typeof api.nextViewIndex === "function", "nextViewIndex export missing");

requireCondition(
  JSON.stringify(api.availableViewNames({ table: true, visual: true, flow: true, explain: true })) ===
    JSON.stringify(["table", "visual", "flow", "explain"]),
  "View order contract changed"
);
requireCondition(
  JSON.stringify(api.availableViewNames({ table: true, visual: false, flow: true, explain: true })) ===
    JSON.stringify(["table", "flow", "explain"]),
  "Unavailable Visual must be omitted"
);
requireCondition(
  JSON.stringify(api.availableViewNames({ table: true })) === JSON.stringify(["table"]),
  "Table must remain the canonical fallback"
);

requireCondition(api.nextViewIndex(4, 0, "ArrowRight") === 1, "ArrowRight must move forward");
requireCondition(api.nextViewIndex(4, 3, "ArrowRight") === 0, "ArrowRight must wrap");
requireCondition(api.nextViewIndex(4, 0, "ArrowLeft") === 3, "ArrowLeft must wrap backward");
requireCondition(api.nextViewIndex(4, 2, "ArrowDown") === 3, "ArrowDown must move forward");
requireCondition(api.nextViewIndex(4, 2, "ArrowUp") === 1, "ArrowUp must move backward");
requireCondition(api.nextViewIndex(4, 2, "Home") === 0, "Home must select first tab");
requireCondition(api.nextViewIndex(4, 1, "End") === 3, "End must select last tab");
requireCondition(api.nextViewIndex(4, 2, "Enter") === 2, "Unrecognized keys must not move focus");
requireCondition(api.nextViewIndex(0, 0, "ArrowRight") === -1, "Empty tablist must remain safe");

console.log("practice result views accessibility smoke: ok");
