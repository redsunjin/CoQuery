#!/usr/bin/env node

await import("./practice-result-explain.js");
const { buildPracticeExplainModel } = globalThis.coqueryPracticeResultExplain || {};

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

requireCondition(typeof buildPracticeExplainModel === "function", "Explain model export is unavailable");

const grouped = {
  ok: true,
  command: "practice_query",
  data: {
    row_count: 3,
    rows: [
      { region: "Busan", customer_count: 1 },
      { region: "Incheon", customer_count: 1 },
      { region: "Seoul", customer_count: 2 },
    ],
    result_intelligence: {
      shape: "category_measure",
      recommended_view: "visual",
      recommended_visual: "bar",
      dimensions: ["region"],
      measures: ["customer_count"],
      flow_steps: [
        { kind: "from", text: "FROM customers" },
        { kind: "group_by", text: "GROUP BY region" },
        { kind: "aggregate", text: "COUNT(*) AS customer_count" },
        { kind: "execution_scan", text: "Seq Scan customers" },
      ],
    },
  },
};

const snapshot = JSON.stringify(grouped);
const groupedModel = buildPracticeExplainModel(grouped);
requireCondition(groupedModel?.shape === "category_measure", "Explain shape contract changed");
requireCondition(groupedModel.recommended_visual === "bar", "Explain visual contract changed");
requireCondition(groupedModel.dimensions[0] === "region", "Explain dimension missing");
requireCondition(groupedModel.measures[0] === "customer_count", "Explain measure missing");
requireCondition(groupedModel.row_count === 3, "Explain row_count contract changed");
requireCondition(groupedModel.flow_steps.length === 3, "Explain must filter unsupported flow kinds");
requireCondition(!groupedModel.flow_steps.some((step) => step.kind === "execution_scan"), "Explain invented/accepted execution-plan step");
requireCondition(JSON.stringify(grouped) === snapshot, "Explain model must not mutate query evidence");

const tabular = buildPracticeExplainModel({
  ok: true,
  command: "practice_query",
  data: {
    rows: [{ id: 1, name: "A" }],
    result_intelligence: {
      shape: "tabular",
      recommended_view: "table",
      recommended_visual: null,
      dimensions: [],
      measures: [],
      flow_steps: [{ kind: "from", text: "FROM customers" }],
    },
  },
});
requireCondition(tabular?.recommended_visual === null, "Tabular Explain must not invent a visual");
requireCondition(tabular.row_count === 1, "Explain must fall back to actual rows length");

requireCondition(buildPracticeExplainModel({ ok: false, command: "practice_query", data: {} }) === null, "Failed query must not render Explain");
requireCondition(buildPracticeExplainModel({ ok: true, command: "practice_list", data: {} }) === null, "Non-query result must not render Explain");

console.log("practice result explain smoke: ok");
