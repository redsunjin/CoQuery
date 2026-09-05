#!/usr/bin/env node

await import("./practice-result-visual.js");
const { buildPracticeBarModel, buildPracticeLineModel } = globalThis.coqueryPracticeResultVisual || {};

function requireCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function near(actual, expected, tolerance = 0.0001) {
  return Math.abs(actual - expected) <= tolerance;
}

requireCondition(typeof buildPracticeBarModel === "function", "Bar visual model export is unavailable");
requireCondition(typeof buildPracticeLineModel === "function", "Line visual model export is unavailable");

const positiveResult = {
  ok: true,
  command: "practice_query",
  data: {
    rows: [
      { region: "Busan", customer_count: 1 },
      { region: "Seoul", customer_count: 2 },
    ],
    result_intelligence: {
      shape: "category_measure",
      recommended_visual: "bar",
      dimensions: ["region"],
      measures: ["customer_count"],
    },
  },
};
const positiveSnapshot = JSON.stringify(positiveResult.data.rows);
const positive = buildPracticeBarModel(positiveResult);
requireCondition(positive?.type === "bar", "category_measure must build a Bar model");
requireCondition(positive.dimension === "region", "dimension contract changed");
requireCondition(positive.measure === "customer_count", "measure contract changed");
requireCondition(positive.rows.map((row) => row.label).join(",") === "Busan,Seoul", "returned row order changed");
requireCondition(near(positive.zero_position, 0), "positive-only domain must start at zero");
requireCondition(near(positive.rows[0].width_percent, 50), "first positive bar width is wrong");
requireCondition(near(positive.rows[1].width_percent, 100), "second positive bar width is wrong");
requireCondition(JSON.stringify(positiveResult.data.rows) === positiveSnapshot, "Bar model must not mutate returned rows");

const signedResult = {
  ok: true,
  command: "practice_query",
  data: {
    rows: [
      { category: "loss", amount: -2 },
      { category: "gain", amount: 4 },
      { category: "zero", amount: 0 },
    ],
    result_intelligence: {
      shape: "category_measure",
      recommended_visual: "bar",
      dimensions: ["category"],
      measures: ["amount"],
    },
  },
};
const signed = buildPracticeBarModel(signedResult);
requireCondition(signed !== null, "signed category_measure should remain chartable");
requireCondition(near(signed.zero_position, 33.3333333333), "signed domain zero position is wrong");
requireCondition(signed.rows[0].negative === true, "negative value flag missing");
requireCondition(signed.rows[0].width_percent > 0, "negative bar must have visible magnitude");
requireCondition(signed.rows[1].negative === false, "positive value flagged negative");
requireCondition(near(signed.rows[2].width_percent, 0), "zero must remain zero-width, not missing");

const unsafeNull = {
  ok: true,
  command: "practice_query",
  data: {
    rows: [{ region: "A", count: null }],
    result_intelligence: {
      shape: "category_measure",
      recommended_visual: "bar",
      dimensions: ["region"],
      measures: ["count"],
    },
  },
};
requireCondition(buildPracticeBarModel(unsafeNull) === null, "null measures must not be charted");

const nonBar = {
  ok: true,
  command: "practice_query",
  data: {
    rows: [{ id: 1, name: "A" }],
    result_intelligence: {
      shape: "tabular",
      recommended_visual: null,
      dimensions: [],
      measures: [],
    },
  },
};
requireCondition(buildPracticeBarModel(nonBar) === null, "tabular results must not invent a Bar visual");

const orderedTimeSeries = {
  ok: true,
  command: "practice_query",
  data: {
    rows: [
      { month: "2026-01", revenue: 10 },
      { month: "2026-02", revenue: 20 },
      { month: "2026-03", revenue: 15 },
    ],
    result_intelligence: {
      shape: "time_series",
      recommended_visual: "line",
      dimensions: ["month"],
      measures: ["revenue"],
    },
  },
};
const orderedSnapshot = JSON.stringify(orderedTimeSeries.data.rows);
const line = buildPracticeLineModel(orderedTimeSeries);
requireCondition(line?.type === "line", "ordered time_series must build a Line model");
requireCondition(line.dimension === "month", "Line temporal dimension changed");
requireCondition(line.measure === "revenue", "Line measure changed");
requireCondition(line.points.map((point) => point.label).join(",") === "2026-01,2026-02,2026-03", "Line must preserve returned temporal order");
requireCondition(near(line.points[0].x_percent, 0) && near(line.points[1].x_percent, 50) && near(line.points[2].x_percent, 100), "Line x sequence geometry changed");
requireCondition(near(line.points[0].y_percent, 100) && near(line.points[1].y_percent, 0) && near(line.points[2].y_percent, 50), "Line y geometry changed");
requireCondition(line.domain_min === 10 && line.domain_max === 20, "Line domain must use exact returned min/max");
requireCondition(JSON.stringify(orderedTimeSeries.data.rows) === orderedSnapshot, "Line model must not mutate returned rows");

const descendingTimeSeries = {
  ...orderedTimeSeries,
  data: {
    ...orderedTimeSeries.data,
    rows: [
      { month: "2026-03", revenue: 15 },
      { month: "2026-02", revenue: 20 },
      { month: "2026-01", revenue: 10 },
    ],
  },
};
const descendingLine = buildPracticeLineModel(descendingTimeSeries);
requireCondition(descendingLine !== null, "safely descending temporal order must remain chartable");
requireCondition(descendingLine.points[0].label === "2026-03" && descendingLine.points[2].label === "2026-01", "descending order must not be resorted");

const unorderedTimeSeries = {
  ...orderedTimeSeries,
  data: {
    ...orderedTimeSeries.data,
    rows: [
      { month: "2026-02", revenue: 20 },
      { month: "2026-01", revenue: 10 },
      { month: "2026-03", revenue: 15 },
    ],
  },
};
requireCondition(buildPracticeLineModel(unorderedTimeSeries) === null, "unordered temporal rows must not render a Line even if stale metadata says line");

const nullTimeSeries = {
  ...orderedTimeSeries,
  data: {
    ...orderedTimeSeries.data,
    rows: [
      { month: "2026-01", revenue: 10 },
      { month: "2026-02", revenue: null },
    ],
  },
};
requireCondition(buildPracticeLineModel(nullTimeSeries) === null, "null time-series measures must remain Table-only");
requireCondition(buildPracticeLineModel(positiveResult) === null, "Bar metadata must not invent a Line visual");

console.log("practice result visual smoke: ok");
