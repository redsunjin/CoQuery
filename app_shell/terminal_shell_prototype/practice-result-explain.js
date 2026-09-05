(function (root) {
  const RECOGNIZED_FLOW_KINDS = new Set([
    "from",
    "join",
    "where",
    "group_by",
    "aggregate",
    "having",
    "order_by",
    "limit",
  ]);

  const copy = {
    ko: {
      title: "결과 해설",
      transformationLabel: "SQL이 한 일",
      rowLabel: "각 행의 의미",
      visualLabel: "왜 이 화면인가",
      boundaryLabel: "해설 범위",
      recommendationLabel: "추천",
      noFlow: "인식 가능한 SQL 변환 단계가 없습니다. 쿼리 구조를 추가로 추론하지 않습니다.",
      boundary: "SQL 구조와 반환 결과만 설명합니다. 업무 원인, 숨은 의미, 실제 DB 실행계획은 추론하지 않습니다.",
      row_category_measure: "각 행은 {dimension} 값 하나와 그에 대응하는 {measure} 값을 담습니다.",
      row_time_series: "각 행은 {dimension} 시점 하나와 그에 대응하는 {measure} 값을 담습니다.",
      row_part_to_whole: "각 행은 {dimension} 항목 하나와 그에 대응하는 {measure} 구성 값을 담습니다.",
      row_numeric_relationship: "각 행은 {dimension}과 {measure}의 한 관측 쌍을 담습니다.",
      row_stage_funnel: "각 행은 {dimension} 단계 하나와 그에 대응하는 {measure} 값을 담습니다.",
      row_source_target_flow: "각 행은 source에서 target으로 이어지는 한 흐름과 value 값을 담습니다.",
      row_single_metric: "결과는 하나의 수치 지표를 반환합니다.",
      row_tabular: "각 행은 쿼리가 반환한 한 레코드입니다. 그 이상의 업무 의미는 추론하지 않습니다.",
      row_unknown: "반환된 행의 업무 의미를 안전하게 특정할 수 없어 원본 Table을 기준으로 봅니다.",
      visual_bar: "카테고리와 수치 측정값이 명확해 Bar 시각화를 추천합니다. 정확한 값은 Table이 기준입니다.",
      visual_line: "시간 순서와 수치 측정값이 명확해 Line 시각화를 추천합니다. 정확한 값은 Table이 기준입니다.",
      visual_ring: "명시적인 구성비 결과라 Ring 시각화를 추천합니다. 정확한 값은 Table이 기준입니다.",
      visual_scatter: "두 수치 변수의 관측 관계를 보기 위해 Scatter 시각화를 추천합니다. 정확한 값은 Table이 기준입니다.",
      visual_funnel: "명시적인 단계와 수치가 있어 Funnel 시각화를 추천합니다. 정확한 값은 Table이 기준입니다.",
      visual_sankey: "source, target, value가 명시되어 Flow/Sankey 시각화를 추천합니다. 정확한 값은 Table이 기준입니다.",
      visual_table: "결과 형태가 모호하거나 상세 레코드 중심이라 별도 차트를 추천하지 않습니다. Table을 기준으로 봅니다.",
      reason_unknown: "반환된 열이 없어 결과 형태를 분류할 수 없습니다.",
      reason_source_target_flow: "source·target·수치 value 열이 명확해 Flow/Sankey를 추천합니다.",
      reason_single_metric: "하나의 수치 지표만 반환되었고 목표값이나 범위가 없어 Table을 기준으로 봅니다.",
      reason_time_series_line: "시간 차원과 수치 측정값이 안전한 시간 순서로 반환되어 Line을 추천합니다.",
      reason_time_series_table: "시간 차원과 수치 측정값은 있지만 반환 순서를 안전한 시간 순서로 확인할 수 없어 Table을 기준으로 봅니다.",
      reason_part_to_whole: "측정값이 명시적인 구성비이고 반환된 항목이 전체를 이루어 Ring을 추천합니다.",
      reason_stage_funnel: "명시적인 단계 차원과 수치 측정값이 있고 SQL에 ORDER BY가 있어 Funnel을 추천합니다.",
      reason_category_measure: "안정적인 카테고리 차원 하나와 수치 측정값 하나가 있어 Bar를 추천합니다.",
      reason_numeric_relationship: "식별자가 아닌 수치 필드 두 개가 행 단위 관측값으로 반환되어 Scatter를 추천합니다.",
      reason_tabular: "결과가 혼합형이거나 불완전하거나 너무 넓거나 의미가 모호해 Table을 기준으로 봅니다.",
      reason_generic_visual: "현재 결과 메타데이터가 {visual} 시각화를 추천합니다. 정확한 값은 Table이 기준입니다.",
      reason_generic_table: "별도 시각화를 안전하게 추천할 근거가 부족해 Table을 기준으로 봅니다.",
    },
    en: {
      title: "Result explanation",
      transformationLabel: "What the SQL did",
      rowLabel: "What each row represents",
      visualLabel: "Why this view",
      boundaryLabel: "Explanation boundary",
      recommendationLabel: "Recommended",
      noFlow: "No recognized SQL transformation steps are available, so no additional query structure is inferred.",
      boundary: "This explanation uses only recognized SQL structure and returned results. It does not infer business causality, hidden meaning, or the physical database execution plan.",
      row_category_measure: "Each row contains one {dimension} value and its corresponding {measure} value.",
      row_time_series: "Each row contains one {dimension} point and its corresponding {measure} value.",
      row_part_to_whole: "Each row contains one {dimension} item and its corresponding {measure} composition value.",
      row_numeric_relationship: "Each row contains one observed pair of {dimension} and {measure}.",
      row_stage_funnel: "Each row contains one {dimension} stage and its corresponding {measure} value.",
      row_source_target_flow: "Each row contains one source-to-target flow and its value.",
      row_single_metric: "The result returns one numeric metric.",
      row_tabular: "Each row is one record returned by the query. No additional business meaning is inferred.",
      row_unknown: "The business meaning of each row cannot be safely identified, so Table remains the evidence view.",
      visual_bar: "A clear category and numeric measure support a Bar visual. Table remains the source of exact values.",
      visual_line: "A clear ordered time dimension and numeric measure support a Line visual. Table remains the source of exact values.",
      visual_ring: "An explicit part-to-whole result supports a Ring visual. Table remains the source of exact values.",
      visual_scatter: "Two numeric observation fields support a Scatter visual. Table remains the source of exact values.",
      visual_funnel: "Explicit ordered stages and a numeric measure support a Funnel visual. Table remains the source of exact values.",
      visual_sankey: "Explicit source, target, and value fields support a Flow/Sankey visual. Table remains the source of exact values.",
      visual_table: "The result is ambiguous or detail-record oriented, so no separate chart is recommended. Table remains the evidence view.",
      reason_unknown: "No returned columns are available to classify the result shape.",
      reason_source_target_flow: "Explicit source, target, and numeric value columns support a Flow/Sankey visual.",
      reason_single_metric: "The result contains one numeric metric and no target or range, so Table remains the evidence view.",
      reason_time_series_line: "A temporal dimension and numeric measure are returned in a safely ordered time sequence, so Line is recommended.",
      reason_time_series_table: "A temporal dimension and numeric measure are present, but the returned time order is not safely chartable, so Table remains the evidence view.",
      reason_part_to_whole: "The measure is an explicit share or percentage and the returned parts form a complete total, so Ring is recommended.",
      reason_stage_funnel: "An explicit stage dimension, numeric measure, and SQL ORDER BY support a Funnel visual.",
      reason_category_measure: "One stable category dimension and one numeric measure support a Bar visual.",
      reason_numeric_relationship: "Two non-identifier numeric fields are returned as row-level observations, so Scatter is recommended.",
      reason_tabular: "The result is mixed, incomplete, too wide, or otherwise ambiguous, so Table remains the truthful default.",
      reason_generic_visual: "The current result metadata recommends a {visual} visual. Table remains the source of exact values.",
      reason_generic_table: "There is not enough evidence to safely recommend a separate visual, so Table remains the evidence view.",
    },
  };

  function currentLanguage() {
    if (typeof document === "undefined") return "en";
    return document.documentElement.lang === "en" ? "en" : "ko";
  }

  function normalizeLanguage(language) {
    return language === "ko" ? "ko" : "en";
  }

  function textForLanguage(key, language, replacements = {}) {
    const lang = normalizeLanguage(language);
    let value = copy[lang]?.[key] || copy.en[key] || key;
    Object.entries(replacements).forEach(([name, replacement]) => {
      value = value.replace(`{${name}}`, String(replacement));
    });
    return value;
  }

  function text(key, replacements = {}) {
    return textForLanguage(key, currentLanguage(), replacements);
  }

  function cleanNames(value) {
    return Array.isArray(value) ? value.filter((item) => typeof item === "string" && item.trim()).map((item) => item.trim()) : [];
  }

  function buildPracticeExplainModel(result) {
    if (!result?.ok || result.command !== "practice_query") return null;

    const data = result.data || {};
    const intelligence = data.result_intelligence || {};
    const rows = Array.isArray(data.rows) ? data.rows : [];
    const explicitRowCount = Number(data.row_count);
    const rowCount = Number.isFinite(explicitRowCount) && explicitRowCount >= 0 ? explicitRowCount : rows.length;
    const flowSteps = (Array.isArray(intelligence.flow_steps) ? intelligence.flow_steps : [])
      .filter((step) => RECOGNIZED_FLOW_KINDS.has(step?.kind) && typeof step?.text === "string" && step.text.trim())
      .map((step) => ({ kind: step.kind, text: step.text.trim() }));

    return {
      type: "result_explain",
      shape: typeof intelligence.shape === "string" ? intelligence.shape : "unknown",
      recommended_visual: typeof intelligence.recommended_visual === "string" ? intelligence.recommended_visual : null,
      recommended_view: typeof intelligence.recommended_view === "string" ? intelligence.recommended_view : "table",
      dimensions: cleanNames(intelligence.dimensions),
      measures: cleanNames(intelligence.measures),
      flow_steps: flowSteps,
      row_count: rowCount,
    };
  }

  function rowMeaning(model) {
    const dimension = model.dimensions[0] || "dimension";
    const measure = model.measures[0] || "measure";
    const key = `row_${model.shape}`;
    const fallback = model.shape === "unknown" ? "row_unknown" : "row_tabular";
    const template = copy[currentLanguage()]?.[key] || copy.en[key];
    if (!template) return text(fallback, { dimension, measure });
    return text(key, { dimension, measure });
  }

  function visualMeaning(model) {
    const visual = model.recommended_visual;
    if (!visual) return text("visual_table");
    const key = `visual_${visual}`;
    if (copy[currentLanguage()]?.[key] || copy.en[key]) return text(key);
    return text("visual_table");
  }

  function transformationMeaning(model) {
    if (!model.flow_steps.length) return text("noFlow");
    return model.flow_steps.map((step) => step.text).join(" → ");
  }

  function recommendationViewName(model) {
    const visual = model?.recommended_visual;
    if (!visual) return "Table";
    return visual.charAt(0).toUpperCase() + visual.slice(1);
  }

  function recommendationReasonForModel(model, language = "en") {
    const lang = normalizeLanguage(language);
    if (!model) return textForLanguage("reason_generic_table", lang);
    if (model.shape === "unknown") return textForLanguage("reason_unknown", lang);
    if (model.shape === "source_target_flow") return textForLanguage("reason_source_target_flow", lang);
    if (model.shape === "single_metric") return textForLanguage("reason_single_metric", lang);
    if (model.shape === "time_series") {
      return textForLanguage(model.recommended_visual === "line" ? "reason_time_series_line" : "reason_time_series_table", lang);
    }
    if (model.shape === "part_to_whole") return textForLanguage("reason_part_to_whole", lang);
    if (model.shape === "stage_funnel") return textForLanguage("reason_stage_funnel", lang);
    if (model.shape === "category_measure") return textForLanguage("reason_category_measure", lang);
    if (model.shape === "numeric_relationship") return textForLanguage("reason_numeric_relationship", lang);
    if (model.shape === "tabular") return textForLanguage("reason_tabular", lang);
    if (model.recommended_visual) {
      return textForLanguage("reason_generic_visual", lang, { visual: recommendationViewName(model) });
    }
    return textForLanguage("reason_generic_table", lang);
  }

  function recommendationTextForModel(model, language = "en") {
    const lang = normalizeLanguage(language);
    return `${textForLanguage("recommendationLabel", lang)}: ${recommendationViewName(model)} · ${recommendationReasonForModel(model, lang)}`;
  }

  function refreshPracticeRecommendationCopy(block) {
    if (!block) return;
    const node = block.querySelector("[data-practice-result-recommendation]");
    if (!node) return;
    const model = buildPracticeExplainModel(block.__result);
    if (!model) return;
    node.textContent = recommendationTextForModel(model, currentLanguage());
  }

  function refreshPracticeExplainCopy(section) {
    const model = section?.__explainModel;
    if (!section || !model) return;

    const title = section.querySelector("[data-practice-explain-title]");
    if (title) title.textContent = text("title");

    const items = {
      transformation: ["transformationLabel", transformationMeaning(model)],
      row: ["rowLabel", rowMeaning(model)],
      visual: ["visualLabel", visualMeaning(model)],
      boundary: ["boundaryLabel", text("boundary")],
    };

    Object.entries(items).forEach(([name, values]) => {
      const label = section.querySelector(`[data-practice-explain-${name}-label]`);
      const body = section.querySelector(`[data-practice-explain-${name}]`);
      if (label) label.textContent = values[0];
      if (body) body.textContent = values[1];
    });

    section.setAttribute("aria-label", `${text("title")}. ${rowMeaning(model)} ${visualMeaning(model)}`);
  }

  function makeExplainItem(name) {
    const item = document.createElement("div");
    item.className = "practice-result-explain-item";
    const label = document.createElement("div");
    label.className = "practice-result-explain-label";
    label.dataset[`practiceExplain${name.charAt(0).toUpperCase()}${name.slice(1)}Label`] = "true";
    const body = name === "transformation" ? document.createElement("code") : document.createElement("p");
    body.className = `practice-result-explain-body${name === "transformation" ? " is-sql" : ""}`;
    body.dataset[`practiceExplain${name.charAt(0).toUpperCase()}${name.slice(1)}`] = "true";
    item.append(label, body);
    return item;
  }

  function renderPracticeExplain(block) {
    if (!block || block.dataset.practiceExplainEnhanced === "true") {
      refreshPracticeRecommendationCopy(block);
      return;
    }
    const model = buildPracticeExplainModel(block.__result);
    if (!model) return;

    const tableWrap = block.querySelector("[data-practice-result-table]");
    if (!tableWrap) return;

    block.dataset.practiceExplainEnhanced = "true";
    const section = document.createElement("section");
    section.className = "practice-result-explain";
    section.dataset.practiceResultExplain = "true";
    section.__explainModel = model;

    const title = document.createElement("h3");
    title.className = "practice-result-explain-title";
    title.dataset.practiceExplainTitle = "true";
    section.append(title, makeExplainItem("transformation"), makeExplainItem("row"), makeExplainItem("visual"), makeExplainItem("boundary"));

    const tableScroller = tableWrap.querySelector(".practice-result-table-scroll");
    if (tableScroller) tableScroller.insertAdjacentElement("beforebegin", section);
    else tableWrap.appendChild(section);

    refreshPracticeExplainCopy(section);
    refreshPracticeRecommendationCopy(block);
  }

  function enhanceExistingPracticeExplain() {
    document.querySelectorAll("#terminalScroll .terminal-block").forEach(renderPracticeExplain);
  }

  root.coqueryPracticeResultExplain = {
    buildPracticeExplainModel,
    recommendationReasonForModel,
    recommendationTextForModel,
  };

  if (typeof document === "undefined") return;

  const scroll = document.getElementById("terminalScroll");
  if (scroll && typeof MutationObserver !== "undefined") {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (!(node instanceof HTMLElement)) return;
          if (node.matches(".terminal-block")) requestAnimationFrame(() => renderPracticeExplain(node));
          node.querySelectorAll?.(".terminal-block").forEach((block) => requestAnimationFrame(() => renderPracticeExplain(block)));
        });
      });
    });
    observer.observe(scroll, { childList: true, subtree: false });
  }

  requestAnimationFrame(enhanceExistingPracticeExplain);
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      setTimeout(() => {
        document.querySelectorAll("[data-practice-result-explain]").forEach(refreshPracticeExplainCopy);
        document.querySelectorAll(".practice-query-result").forEach(refreshPracticeRecommendationCopy);
      }, 0);
    });
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
