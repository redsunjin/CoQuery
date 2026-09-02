#!/usr/bin/env node

await import("./practice-result-visual.js");
const { buildPracticeBarModel } = globalThis.coqueryPracticeResultVisual || {};

function requireCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function near(actual, expected, tolerance = 0.0001) {
  return Math.abs(actual - expected) <= tolerance;
}

requireCondition(typeof buildPracticeBarModel === "function", "Bar visual model export is unavailable");

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

console.log("practice result visual smoke: ok");
