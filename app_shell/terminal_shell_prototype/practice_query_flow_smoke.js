#!/usr/bin/env node

await import("./practice-query-flow.js");
const { buildPracticeQueryFlowModel } = globalThis.coqueryPracticeQueryFlow || {};

function requireCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

requireCondition(typeof buildPracticeQueryFlowModel === "function", "Query Graph model export is unavailable");

const source = {
  ok: true,
  command: "practice_query",
  data: {
    row_count: 3,
    rows: [{ region: "Busan", count: 1 }, { region: "Seoul", count: 2 }, { region: "Incheon", count: 1 }],
    result_intelligence: {
      flow_steps: [
        { kind: "from", text: "FROM customers" },
        { kind: "where", text: "WHERE active = 1" },
        { kind: "group_by", text: "GROUP BY region" },
        { kind: "aggregate", text: "COUNT(*) AS count" },
        { kind: "order_by", text: "ORDER BY count DESC" },
      ],
    },
  },
};
const snapshot = JSON.stringify(source);
const model = buildPracticeQueryFlowModel(source);
requireCondition(model?.type === "query_flow", "recognized flow_steps must build a Query Graph model");
requireCondition(model.row_count === 3, "Query Graph result row count changed");
requireCondition(
  model.steps.map((step) => step.kind).join(",") === "from,where,group_by,aggregate,order_by",
  "Query Graph step order changed"
);
requireCondition(model.steps[1].text === "WHERE active = 1", "Query Graph must preserve exact recognized SQL text");
requireCondition(JSON.stringify(source) === snapshot, "Query Graph model must not mutate the result payload");

const mixedKinds = {
  ok: true,
  command: "practice_query",
  data: {
    rows: [{ id: 1 }],
    result_intelligence: {
      flow_steps: [
        { kind: "from", text: "FROM users" },
        { kind: "invented_runtime_node", text: "Hash Join" },
        { kind: "limit", text: "LIMIT 1" },
      ],
    },
  },
};
const mixed = buildPracticeQueryFlowModel(mixedKinds);
requireCondition(mixed.steps.length === 2, "Query Graph must ignore unsupported/invented step kinds");
requireCondition(mixed.steps.map((step) => step.kind).join(",") === "from,limit", "unsupported step filtering changed");

const noFlow = {
  ok: true,
  command: "practice_query",
  data: { rows: [], result_intelligence: { flow_steps: [] } },
};
requireCondition(buildPracticeQueryFlowModel(noFlow) === null, "empty flow_steps must not invent a Query Graph");

const failed = {
  ok: false,
  command: "practice_query",
  data: { result_intelligence: { flow_steps: [{ kind: "from", text: "FROM users" }] } },
};
requireCondition(buildPracticeQueryFlowModel(failed) === null, "failed query must not render a Query Graph");

console.log("practice query flow smoke: ok");
