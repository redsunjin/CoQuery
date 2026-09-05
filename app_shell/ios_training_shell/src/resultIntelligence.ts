const RESULT_INTELLIGENCE_AGGREGATE_RE = /\b(COUNT|SUM|AVG|MIN|MAX)\s*\([^)]*\)(?:\s+AS\s+[A-Za-z_][A-Za-z0-9_]*)?/gi;
const RESULT_INTELLIGENCE_TEMPORAL_NAMES = new Set(["date", "day", "datetime", "month", "quarter", "time", "timestamp", "week", "year"]);
const RESULT_INTELLIGENCE_PART_TO_WHOLE_NAMES = new Set(["pct", "percent", "percentage", "ratio", "share"]);
const RESULT_INTELLIGENCE_STAGE_NAMES = new Set(["phase", "stage", "step"]);
const RESULT_INTELLIGENCE_FLOW_COLUMNS = new Set(["source", "target", "value"]);

function resultIntelligenceNormalizeName(name) {
  return String(name).trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

function resultIntelligenceTokens(name) {
  return resultIntelligenceNormalizeName(name).split("_").filter(Boolean);
}

function resultIntelligenceHasName(name, names) {
  return resultIntelligenceTokens(name).some((token) => names.has(token));
}

function resultIntelligenceIsIdentifier(name) {
  const normalized = resultIntelligenceNormalizeName(name);
  return normalized === "id" || normalized.endsWith("_id");
}

function resultIntelligenceIsNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function resultIntelligenceTemporalKey(value) {
  if (resultIntelligenceIsNumber(value)) return [value];
  const text = String(value ?? "").trim();
  if (/^\d{4}$/.test(text)) return [Number(text)];
  const match = text.match(/^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?$/) || text.match(/^(\d{4})[./](\d{1,2})(?:[./](\d{1,2}))?$/);
  return match ? [Number(match[1]), Number(match[2]), Number(match[3] || 0)] : null;
}

function resultIntelligenceCompareTemporal(left, right) {
  const length = Math.max(left.length, right.length);
  for (let index = 0; index < length; index += 1) {
    if (index >= left.length) return -1;
    if (index >= right.length) return 1;
    if (left[index] < right[index]) return -1;
    if (left[index] > right[index]) return 1;
  }
  return 0;
}

function resultIntelligenceIsOrderedTemporal(values) {
  const keys = values.map(resultIntelligenceTemporalKey);
  if (!keys.length || keys.some((key) => key === null)) return false;
  let ascending = true;
  let descending = true;
  for (let index = 1; index < keys.length; index += 1) {
    const comparison = resultIntelligenceCompareTemporal(keys[index - 1], keys[index]);
    if (comparison > 0) ascending = false;
    if (comparison < 0) descending = false;
  }
  return ascending || descending;
}

function resultIntelligenceNonNull(rows, column) {
  return rows.map((row) => row?.[column]).filter((value) => value !== null && value !== undefined);
}

function resultIntelligenceProfile(column, rows) {
  const values = resultIntelligenceNonNull(rows, column);
  const temporalName = resultIntelligenceHasName(column, RESULT_INTELLIGENCE_TEMPORAL_NAMES);
  const kind = values.length === 0
    ? "unknown"
    : values.every(resultIntelligenceIsNumber)
      ? (temporalName ? "temporal" : "numeric")
      : temporalName && values.every((value) => resultIntelligenceTemporalKey(value) !== null)
        ? "temporal"
        : "categorical";
  return {
    name: column,
    kind,
    identifier: resultIntelligenceIsIdentifier(column),
    null_count: rows.length - values.length,
    distinct_count: new Set(values.map((value) => JSON.stringify(value))).size,
  };
}

function resultIntelligenceExtractClause(text, clause, stopClauses) {
  const stops = stopClauses.map((item) => item.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|");
  const suffix = stops ? `(?=\\b(?:${stops})\\b|$)` : "$";
  const match = text.match(new RegExp(`\\b${clause.replace(" ", "\\s+")}\\b\\s+(.+?)${suffix}`, "i"));
  return match ? `${clause.toUpperCase()} ${match[1].trim()}` : null;
}

function extractPracticeSqlFlow(sql) {
  const text = String(sql || "").trim().replace(/\s+/g, " ").replace(/;$/, "");
  if (!text) return [];
  const steps = [];
  const from = text.match(/\bFROM\b\s+(.+?)(?=\b(?:LEFT\s+JOIN|RIGHT\s+JOIN|FULL\s+JOIN|INNER\s+JOIN|CROSS\s+JOIN|JOIN|WHERE|GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT)\b|$)/i);
  if (from) steps.push({ kind: "from", text: `FROM ${from[1].trim()}` });
  const joins = /\b((?:LEFT|RIGHT|FULL|INNER|CROSS)\s+JOIN|JOIN)\b\s+(.+?)(?=\b(?:LEFT\s+JOIN|RIGHT\s+JOIN|FULL\s+JOIN|INNER\s+JOIN|CROSS\s+JOIN|JOIN|WHERE|GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT)\b|$)/gi;
  for (const match of text.matchAll(joins)) steps.push({ kind: "join", text: `${match[1].toUpperCase()} ${match[2].trim()}` });
  for (const [clause, stops, kind] of [["WHERE", ["GROUP BY", "HAVING", "ORDER BY", "LIMIT"], "where"], ["GROUP BY", ["HAVING", "ORDER BY", "LIMIT"], "group_by"]]) {
    const fragment = resultIntelligenceExtractClause(text, clause, stops);
    if (fragment) steps.push({ kind, text: fragment });
  }
  const select = text.match(/\bSELECT\b\s+(.+?)\s+\bFROM\b/i);
  if (select) {
    for (const aggregate of select[1].matchAll(new RegExp(RESULT_INTELLIGENCE_AGGREGATE_RE.source, "gi"))) {
      steps.push({ kind: "aggregate", text: aggregate[0].trim() });
    }
  }
  for (const [clause, stops, kind] of [["HAVING", ["ORDER BY", "LIMIT"], "having"], ["ORDER BY", ["LIMIT"], "order_by"], ["LIMIT", [], "limit"]]) {
    const fragment = resultIntelligenceExtractClause(text, clause, stops);
    if (fragment) steps.push({ kind, text: fragment });
  }
  return steps;
}

function resultIntelligenceBase(shape, recommendedView, recommendedVisual, confidence, reason, dimensions, measures, profiles, flowSteps) {
  return {
    shape,
    recommended_view: recommendedView,
    recommended_visual: recommendedVisual,
    confidence,
    reason,
    dimensions,
    measures,
    column_profiles: profiles,
    flow_steps: flowSteps,
  };
}

function classifyPracticeResult(columns, rows, sql = "") {
  const columnList = (columns || []).map(String);
  const rowList = (rows || []).map((row) => ({ ...row }));
  const profiles = columnList.map((column) => resultIntelligenceProfile(column, rowList));
  const flowSteps = extractPracticeSqlFlow(sql);
  if (!columnList.length) {
    return resultIntelligenceBase("unknown", "table", null, 1, "No returned columns are available to classify.", [], [], profiles, flowSteps);
  }
  const profileByName = Object.fromEntries(profiles.map((profile) => [profile.name, profile]));
  const numeric = columnList.filter((column) => profileByName[column].kind === "numeric" && !profileByName[column].identifier);
  const temporal = columnList.filter((column) => profileByName[column].kind === "temporal");
  const normalizedColumns = Object.fromEntries(columnList.map((column) => [resultIntelligenceNormalizeName(column), column]));
  const normalizedNames = new Set(Object.keys(normalizedColumns));
  const hasGrouping = /\bGROUP\s+BY\b/i.test(sql);
  const hasAggregate = new RegExp(RESULT_INTELLIGENCE_AGGREGATE_RE.source, "i").test(sql);
  const hasOrder = /\bORDER\s+BY\b/i.test(sql);

  if (normalizedNames.size === RESULT_INTELLIGENCE_FLOW_COLUMNS.size && [...RESULT_INTELLIGENCE_FLOW_COLUMNS].every((name) => normalizedNames.has(name))) {
    const valueColumn = normalizedColumns.value;
    if (profileByName[valueColumn].kind === "numeric") {
      return resultIntelligenceBase("source_target_flow", "flow", "sankey", 0.99, "The result exposes exact source, target, and numeric value columns.", [normalizedColumns.source, normalizedColumns.target], [valueColumn], profiles, flowSteps);
    }
  }
  if (columnList.length === 1 && rowList.length === 1 && numeric.length) {
    return resultIntelligenceBase("single_metric", "table", null, 0.99, "The result is one numeric metric; no target or range was provided for a gauge.", [], [numeric[0]], profiles, flowSteps);
  }
  if (columnList.length === 2 && rowList.length >= 2) {
    const measures = columnList.filter((column) => numeric.includes(column));
    const dimensions = columnList.filter((column) => !measures.includes(column));
    if (temporal.length === 1 && measures.length === 1) {
      const timeColumn = temporal[0];
      const measureColumn = measures[0];
      const timeValues = resultIntelligenceNonNull(rowList, timeColumn);
      const complete = timeValues.length === rowList.length && resultIntelligenceNonNull(rowList, measureColumn).length === rowList.length;
      const ordered = complete && resultIntelligenceIsOrderedTemporal(timeValues);
      return resultIntelligenceBase("time_series", ordered ? "visual" : "table", ordered ? "line" : null, ordered ? 0.96 : 0.75, ordered ? "A temporal dimension and numeric measure are returned in chronological order." : "A temporal dimension and numeric measure are present, but the returned time order is not safely chartable.", [timeColumn], [measureColumn], profiles, flowSteps);
    }
    if (measures.length === 1 && dimensions.length === 1) {
      const dimension = dimensions[0];
      const measure = measures[0];
      const measureValues = resultIntelligenceNonNull(rowList, measure);
      const dimensionValues = resultIntelligenceNonNull(rowList, dimension);
      const complete = measureValues.length === rowList.length && dimensionValues.length === rowList.length;
      const total = measureValues.reduce((sum, value) => sum + Number(value), 0);
      if (complete && rowList.length <= 6 && resultIntelligenceHasName(measure, RESULT_INTELLIGENCE_PART_TO_WHOLE_NAMES) && measureValues.length && (Math.abs(total - 100) <= 0.5 || Math.abs(total - 1) <= 0.01)) {
        return resultIntelligenceBase("part_to_whole", "visual", "ring", 0.98, "The measure is explicitly a share/percentage and the returned parts form a complete total.", [dimension], [measure], profiles, flowSteps);
      }
      if (complete && resultIntelligenceHasName(dimension, RESULT_INTELLIGENCE_STAGE_NAMES) && hasOrder) {
        return resultIntelligenceBase("stage_funnel", "visual", "funnel", 0.95, "The result has an explicit stage dimension, numeric measure, and SQL ORDER BY.", [dimension], [measure], profiles, flowSteps);
      }
      const dimensionProfile = profileByName[dimension];
      if (dimensionProfile.kind === "categorical" && complete && dimensionProfile.distinct_count === rowList.length && rowList.length <= 20) {
        return resultIntelligenceBase("category_measure", "visual", "bar", 0.94, "The result has one stable category dimension and one numeric measure.", [dimension], [measure], profiles, flowSteps);
      }
    }
    if (numeric.length === 2 && !hasGrouping && !hasAggregate && numeric.every((column) => resultIntelligenceNonNull(rowList, column).length === rowList.length)) {
      return resultIntelligenceBase("numeric_relationship", "visual", "scatter", 0.92, "Two non-identifier numeric fields are returned for row-level observations.", [numeric[0]], [numeric[1]], profiles, flowSteps);
    }
  }
  return resultIntelligenceBase("tabular", "table", null, 1, "The returned result is mixed, incomplete, too wide, or otherwise ambiguous; Table is the truthful default.", [], numeric, profiles, flowSteps);
}
