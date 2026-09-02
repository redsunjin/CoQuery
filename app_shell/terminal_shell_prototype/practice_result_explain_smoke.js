#!/usr/bin/env node

await import("./practice-result-explain.js");
const {
  buildPracticeExplainModel,
  recommendationReasonForModel,
  recommendationTextForModel,
} = globalThis.coqueryPracticeResultExplain || {};

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

requireCondition(typeof buildPracticeExplainModel === "function", "Explain model export is unavailable");
requireCondition(typeof recommendationReasonForModel === "function", "Recommendation reason export is unavailable");
requireCondition(typeof recommendationTextForModel === "function", "Recommendation copy export is unavailable");

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
      reason: "The result has one stable category dimension and one numeric measure.",
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

const koBar = recommendationTextForModel(groupedModel, "ko");
const enBar = recommendationTextForModel(groupedModel, "en");
requireCondition(koBar.includes("추천: Bar"), "Korean recommendation label/view missing");
requireCondition(koBar.includes("안정적인 카테고리 차원"), "Korean Bar reason missing");
requireCondition(!koBar.includes(grouped.data.result_intelligence.reason), "Korean UI must not reuse backend-English reason text");
requireCondition(enBar.includes("Recommended: Bar"), "English recommendation label/view missing");
requireCondition(enBar.includes("stable category dimension"), "Deterministic English Bar reason missing");

const safeTimeModel = buildPracticeExplainModel({
  ok: true,
  command: "practice_query",
  data: {
    rows: [
      { month: "2026-01", revenue: 10 },
      { month: "2026-02", revenue: 12 },
    ],
    result_intelligence: {
      shape: "time_series",
      recommended_view: "visual",
      recommended_visual: "line",
      dimensions: ["month"],
      measures: ["revenue"],
      flow_steps: [],
    },
  },
});
requireCondition(recommendationReasonForModel(safeTimeModel, "ko").includes("안전한 시간 순서"), "Safe Korean time-series reason missing");
requireCondition(recommendationReasonForModel(safeTimeModel, "en").includes("safely ordered time sequence"), "Safe English time-series reason missing");

const unsafeTimeModel = buildPracticeExplainModel({
  ok: true,
  command: "practice_query",
  data: {
    rows: [
      { month: "2026-02", revenue: 12 },
      { month: "2026-01", revenue: 10 },
    ],
    result_intelligence: {
      shape: "time_series",
      recommended_view: "table",
      recommended_visual: null,
      dimensions: ["month"],
      measures: ["revenue"],
      flow_steps: [],
    },
  },
});
requireCondition(recommendationTextForModel(unsafeTimeModel, "ko").startsWith("추천: Table"), "Unsafe time-series must stay Table in Korean copy");
requireCondition(recommendationReasonForModel(unsafeTimeModel, "ko").includes("안전한 시간 순서로 확인할 수 없어"), "Unsafe Korean time-series reason missing");

const singleMetricModel = buildPracticeExplainModel({
  ok: true,
  command: "practice_query",
  data: {
    rows: [{ total: 42 }],
    result_intelligence: {
      shape: "single_metric",
      recommended_view: "table",
      recommended_visual: null,
      dimensions: [],
      measures: ["total"],
      flow_steps: [],
    },
  },
});
requireCondition(recommendationReasonForModel(singleMetricModel, "ko").includes("목표값이나 범위가 없어"), "Single-metric gauge guard reason missing");

const flowModel = buildPracticeExplainModel({
  ok: true,
  command: "practice_query",
  data: {
    rows: [{ source: "A", target: "B", value: 3 }],
    result_intelligence: {
      shape: "source_target_flow",
      recommended_view: "flow",
      recommended_visual: "sankey",
      dimensions: ["source", "target"],
      measures: ["value"],
      flow_steps: [],
    },
  },
});
requireCondition(recommendationTextForModel(flowModel, "ko").includes("Flow/Sankey"), "Flow recommendation localization missing");

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
requireCondition(recommendationReasonForModel(tabular, "ko").includes("혼합형이거나 불완전하거나"), "Tabular Korean fallback reason missing");
requireCondition(recommendationTextForModel(tabular, "en").startsWith("Recommended: Table"), "Tabular English recommendation copy changed");

const deterministicA = recommendationTextForModel(groupedModel, "ko");
const deterministicB = recommendationTextForModel(groupedModel, "ko");
requireCondition(deterministicA === deterministicB, "Recommendation localization must be deterministic");

requireCondition(buildPracticeExplainModel({ ok: false, command: "practice_query", data: {} }) === null, "Failed query must not render Explain");
requireCondition(buildPracticeExplainModel({ ok: true, command: "practice_list", data: {} }) === null, "Non-query result must not render Explain");

console.log("practice result explain smoke: ok");
