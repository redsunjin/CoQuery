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
    },
    en: {
      title: "Result explanation",
      transformationLabel: "What the SQL did",
      rowLabel: "What each row represents",
      visualLabel: "Why this view",
      boundaryLabel: "Explanation boundary",
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
    },
  };

  function currentLanguage() {
    if (typeof document === "undefined") return "en";
    return document.documentElement.lang === "en" ? "en" : "ko";
  }

  function text(key, replacements = {}) {
    const lang = currentLanguage();
    let value = copy[lang]?.[key] || copy.en[key] || key;
    Object.entries(replacements).forEach(([name, replacement]) => {
      value = value.replace(`{${name}}`, String(replacement));
    });
    return value;
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
    if (!block || block.dataset.practiceExplainEnhanced === "true") return;
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
  }

  function enhanceExistingPracticeExplain() {
    document.querySelectorAll("#terminalScroll .terminal-block").forEach(renderPracticeExplain);
  }

  root.coqueryPracticeResultExplain = { buildPracticeExplainModel };

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
      requestAnimationFrame(() => {
        document.querySelectorAll("[data-practice-result-explain]").forEach(refreshPracticeExplainCopy);
      });
    });
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
