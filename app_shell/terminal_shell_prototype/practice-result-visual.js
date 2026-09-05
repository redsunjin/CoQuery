(function (root) {
  const copy = {
    ko: {
      barTitle: "결과 시각화 · Bar",
      barSummary: "{dimension}별 {measure} 값을 쿼리 반환 순서대로 표시합니다.",
      barEvidence: "이 시각화는 현재 반환된 행만 사용합니다. Table이 기준 데이터입니다.",
      lineTitle: "결과 시각화 · Line",
      lineSummary: "{dimension}의 안전하게 확인된 시간 순서대로 {measure} 값을 연결합니다.",
      lineEvidence: "현재 반환된 모든 행과 순서를 그대로 사용합니다. 가로 간격은 반환 순서를 나타내며 실제 시간 간격의 크기를 추정하지 않습니다. 정확한 값은 Table이 기준입니다.",
      min: "최소",
      max: "최대",
    },
    en: {
      barTitle: "Result visual · Bar",
      barSummary: "Shows {measure} by {dimension} in the exact returned row order.",
      barEvidence: "This visual uses only the current returned rows. Table remains the canonical evidence.",
      lineTitle: "Result visual · Line",
      lineSummary: "Connects {measure} across the safely verified temporal order of {dimension}.",
      lineEvidence: "Uses every returned row in its exact order. Horizontal spacing represents returned sequence and does not infer elapsed-time distance. Table remains the canonical source for exact values.",
      min: "Min",
      max: "Max",
    },
  };

  function isFiniteNumber(value) {
    return typeof value === "number" && Number.isFinite(value);
  }

  function clampPercent(value) {
    return Math.max(0, Math.min(100, value));
  }

  function temporalKey(value) {
    if (isFiniteNumber(value)) {
      return [Number(value)];
    }
    const text = String(value ?? "").trim();
    if (/^\d{4}$/.test(text)) {
      return [Number(text)];
    }
    let match = text.match(/^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?$/);
    if (!match) {
      match = text.match(/^(\d{4})[./](\d{1,2})(?:[./](\d{1,2}))?$/);
    }
    if (!match) {
      return null;
    }
    return [Number(match[1]), Number(match[2]), Number(match[3] || 0)];
  }

  function compareTemporalKeys(left, right) {
    const length = Math.max(left.length, right.length);
    for (let index = 0; index < length; index += 1) {
      if (index >= left.length) return -1;
      if (index >= right.length) return 1;
      if (left[index] < right[index]) return -1;
      if (left[index] > right[index]) return 1;
    }
    return 0;
  }

  function isSafelyOrderedTemporal(values) {
    const keys = values.map(temporalKey);
    if (!keys.length || keys.some((key) => key === null)) {
      return false;
    }
    let ascending = true;
    let descending = true;
    for (let index = 1; index < keys.length; index += 1) {
      const comparison = compareTemporalKeys(keys[index - 1], keys[index]);
      if (comparison > 0) ascending = false;
      if (comparison < 0) descending = false;
    }
    return ascending || descending;
  }

  function buildPracticeBarModel(result) {
    const data = result?.data || {};
    const intelligence = data.result_intelligence || {};
    if (
      !result?.ok ||
      result.command !== "practice_query" ||
      intelligence.shape !== "category_measure" ||
      intelligence.recommended_visual !== "bar"
    ) {
      return null;
    }

    const dimensions = Array.isArray(intelligence.dimensions) ? intelligence.dimensions : [];
    const measures = Array.isArray(intelligence.measures) ? intelligence.measures : [];
    const rows = Array.isArray(data.rows) ? data.rows : [];
    if (dimensions.length !== 1 || measures.length !== 1 || rows.length === 0 || rows.length > 20) {
      return null;
    }

    const dimension = dimensions[0];
    const measure = measures[0];
    const points = [];
    for (const row of rows) {
      const label = row?.[dimension];
      const value = row?.[measure];
      if (label === null || label === undefined || !isFiniteNumber(value)) {
        return null;
      }
      points.push({ label: String(label), value });
    }

    const rawMin = Math.min(0, ...points.map((point) => point.value));
    const rawMax = Math.max(0, ...points.map((point) => point.value));
    let domainMin = rawMin;
    let domainMax = rawMax;
    if (domainMin === domainMax) {
      domainMin = -1;
      domainMax = 1;
    }
    const range = domainMax - domainMin;
    const zeroPosition = clampPercent(((0 - domainMin) / range) * 100);

    const normalizedRows = points.map((point) => {
      const valuePosition = clampPercent(((point.value - domainMin) / range) * 100);
      const left = Math.min(zeroPosition, valuePosition);
      const width = Math.abs(valuePosition - zeroPosition);
      return {
        label: point.label,
        value: point.value,
        left_percent: left,
        width_percent: width,
        negative: point.value < 0,
      };
    });

    return {
      type: "bar",
      dimension,
      measure,
      domain_min: rawMin,
      domain_max: rawMax,
      zero_position: zeroPosition,
      rows: normalizedRows,
    };
  }

  function buildPracticeLineModel(result) {
    const data = result?.data || {};
    const intelligence = data.result_intelligence || {};
    if (
      !result?.ok ||
      result.command !== "practice_query" ||
      intelligence.shape !== "time_series" ||
      intelligence.recommended_visual !== "line"
    ) {
      return null;
    }

    const dimensions = Array.isArray(intelligence.dimensions) ? intelligence.dimensions : [];
    const measures = Array.isArray(intelligence.measures) ? intelligence.measures : [];
    const rows = Array.isArray(data.rows) ? data.rows : [];
    if (dimensions.length !== 1 || measures.length !== 1 || rows.length < 2) {
      return null;
    }

    const dimension = dimensions[0];
    const measure = measures[0];
    const temporalValues = [];
    const points = [];
    for (const row of rows) {
      const label = row?.[dimension];
      const value = row?.[measure];
      if (label === null || label === undefined || !isFiniteNumber(value)) {
        return null;
      }
      temporalValues.push(label);
      points.push({ label: String(label), value });
    }
    if (!isSafelyOrderedTemporal(temporalValues)) {
      return null;
    }

    const domainMin = Math.min(...points.map((point) => point.value));
    const domainMax = Math.max(...points.map((point) => point.value));
    const range = domainMax - domainMin;
    const normalizedPoints = points.map((point, index) => ({
      label: point.label,
      value: point.value,
      x_percent: points.length === 1 ? 50 : (index / (points.length - 1)) * 100,
      y_percent: range === 0 ? 50 : ((domainMax - point.value) / range) * 100,
    }));

    return {
      type: "line",
      dimension,
      measure,
      domain_min: domainMin,
      domain_max: domainMax,
      points: normalizedPoints,
    };
  }

  function currentLanguage() {
    if (typeof document === "undefined") {
      return "en";
    }
    return document.documentElement.lang === "en" ? "en" : "ko";
  }

  function visualCopy(key, model) {
    const lang = currentLanguage();
    const template = copy[lang]?.[key] || copy.en[key] || key;
    return template
      .replace("{dimension}", model?.dimension || "dimension")
      .replace("{measure}", model?.measure || "measure");
  }

  function formatVisualValue(value) {
    const locale = currentLanguage() === "ko" ? "ko-KR" : "en-US";
    try {
      return new Intl.NumberFormat(locale, { maximumFractionDigits: 6 }).format(value);
    } catch {
      return String(value);
    }
  }

  function refreshPracticeBarCopy(figure) {
    const model = figure?.__barModel;
    if (!figure || !model) {
      return;
    }
    const title = figure.querySelector("[data-practice-bar-title]");
    const summary = figure.querySelector("[data-practice-bar-summary]");
    const evidence = figure.querySelector("[data-practice-bar-evidence]");
    if (title) title.textContent = visualCopy("barTitle", model);
    if (summary) summary.textContent = visualCopy("barSummary", model);
    if (evidence) evidence.textContent = visualCopy("barEvidence", model);
    figure.setAttribute("aria-label", `${visualCopy("barTitle", model)}. ${visualCopy("barSummary", model)}`);
    figure.querySelectorAll("[data-practice-bar-value]").forEach((node) => {
      const value = Number(node.dataset.practiceBarValue);
      node.textContent = Number.isFinite(value) ? formatVisualValue(value) : node.dataset.practiceBarValue;
    });
  }

  function refreshPracticeLineCopy(figure) {
    const model = figure?.__lineModel;
    if (!figure || !model) {
      return;
    }
    const title = figure.querySelector("[data-practice-line-title]");
    const summary = figure.querySelector("[data-practice-line-summary]");
    const evidence = figure.querySelector("[data-practice-line-evidence]");
    const min = figure.querySelector("[data-practice-line-min]");
    const max = figure.querySelector("[data-practice-line-max]");
    if (title) title.textContent = visualCopy("lineTitle", model);
    if (summary) summary.textContent = visualCopy("lineSummary", model);
    if (evidence) evidence.textContent = visualCopy("lineEvidence", model);
    if (min) min.textContent = `${visualCopy("min", model)} ${formatVisualValue(model.domain_min)}`;
    if (max) max.textContent = `${visualCopy("max", model)} ${formatVisualValue(model.domain_max)}`;
    figure.setAttribute("aria-label", `${visualCopy("lineTitle", model)}. ${visualCopy("lineSummary", model)}. ${visualCopy("lineEvidence", model)}`);
  }

  function insertVisualBeforeTable(tableWrap, figure) {
    const tableScroller = tableWrap.querySelector(".practice-result-table-scroll");
    if (tableScroller) {
      tableScroller.insertAdjacentElement("beforebegin", figure);
    } else {
      tableWrap.appendChild(figure);
    }
  }

  function renderPracticeBarVisual(block) {
    if (!block || block.dataset.practiceBarEnhanced === "true") {
      return;
    }
    const model = buildPracticeBarModel(block.__result);
    if (!model) {
      return;
    }

    const tableWrap = block.querySelector("[data-practice-result-table]");
    if (!tableWrap) {
      return;
    }

    block.dataset.practiceBarEnhanced = "true";
    const figure = document.createElement("figure");
    figure.className = "practice-result-bar-visual";
    figure.dataset.practiceBarVisual = "true";
    figure.__barModel = model;

    const header = document.createElement("div");
    header.className = "practice-result-bar-header";

    const title = document.createElement("figcaption");
    title.className = "practice-result-bar-title";
    title.dataset.practiceBarTitle = "true";

    const summary = document.createElement("p");
    summary.className = "practice-result-bar-summary";
    summary.dataset.practiceBarSummary = "true";
    header.append(title, summary);

    const chart = document.createElement("div");
    chart.className = "practice-result-bar-chart";
    chart.setAttribute("role", "img");

    model.rows.forEach((point) => {
      const row = document.createElement("div");
      row.className = "practice-result-bar-row";

      const label = document.createElement("div");
      label.className = "practice-result-bar-label";
      label.textContent = point.label;
      label.title = point.label;

      const track = document.createElement("div");
      track.className = "practice-result-bar-track";
      track.style.setProperty("--practice-bar-zero", `${model.zero_position}%`);

      const zero = document.createElement("span");
      zero.className = "practice-result-bar-zero";
      zero.setAttribute("aria-hidden", "true");

      const fill = document.createElement("span");
      fill.className = `practice-result-bar-fill${point.negative ? " is-negative" : ""}`;
      fill.style.left = `${point.left_percent}%`;
      fill.style.width = `${point.width_percent}%`;
      fill.setAttribute("aria-hidden", "true");
      track.append(zero, fill);

      const value = document.createElement("div");
      value.className = "practice-result-bar-value";
      value.dataset.practiceBarValue = String(point.value);
      value.textContent = formatVisualValue(point.value);

      row.setAttribute("aria-label", `${point.label}: ${point.value}`);
      row.append(label, track, value);
      chart.appendChild(row);
    });

    const evidence = document.createElement("p");
    evidence.className = "practice-result-bar-evidence";
    evidence.dataset.practiceBarEvidence = "true";
    figure.append(header, chart, evidence);
    insertVisualBeforeTable(tableWrap, figure);
    refreshPracticeBarCopy(figure);
  }

  function renderPracticeLineVisual(block) {
    if (!block || block.dataset.practiceLineEnhanced === "true") {
      return;
    }
    const model = buildPracticeLineModel(block.__result);
    if (!model) {
      return;
    }

    const tableWrap = block.querySelector("[data-practice-result-table]");
    if (!tableWrap) {
      return;
    }

    block.dataset.practiceLineEnhanced = "true";
    const figure = document.createElement("figure");
    figure.className = "practice-result-line-visual";
    figure.dataset.practiceLineVisual = "true";
    figure.__lineModel = model;

    const header = document.createElement("div");
    header.className = "practice-result-line-header";
    const title = document.createElement("figcaption");
    title.className = "practice-result-line-title";
    title.dataset.practiceLineTitle = "true";
    const summary = document.createElement("p");
    summary.className = "practice-result-line-summary";
    summary.dataset.practiceLineSummary = "true";
    header.append(title, summary);

    const shell = document.createElement("div");
    shell.className = "practice-result-line-chart-shell";
    const yAxis = document.createElement("div");
    yAxis.className = "practice-result-line-y-axis";
    const max = document.createElement("span");
    max.dataset.practiceLineMax = "true";
    const min = document.createElement("span");
    min.dataset.practiceLineMin = "true";
    yAxis.append(max, min);

    const plot = document.createElement("div");
    plot.className = "practice-result-line-plot";
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.classList.add("practice-result-line-svg");
    svg.setAttribute("viewBox", "0 0 1000 260");
    svg.setAttribute("preserveAspectRatio", "none");
    svg.setAttribute("aria-hidden", "true");

    const coordinates = model.points.map((point) => ({
      ...point,
      x: 24 + (point.x_percent / 100) * 952,
      y: 20 + (point.y_percent / 100) * 200,
    }));
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.classList.add("practice-result-line-path");
    path.setAttribute("d", coordinates.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" "));
    svg.appendChild(path);

    coordinates.forEach((point) => {
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.classList.add("practice-result-line-point");
      circle.setAttribute("cx", String(point.x));
      circle.setAttribute("cy", String(point.y));
      circle.setAttribute("r", "5");
      const pointTitle = document.createElementNS("http://www.w3.org/2000/svg", "title");
      pointTitle.textContent = `${point.label}: ${point.value}`;
      circle.appendChild(pointTitle);
      svg.appendChild(circle);
    });

    const xAxis = document.createElement("div");
    xAxis.className = "practice-result-line-x-axis";
    const firstLabel = document.createElement("span");
    firstLabel.textContent = model.points[0].label;
    const lastLabel = document.createElement("span");
    lastLabel.textContent = model.points[model.points.length - 1].label;
    xAxis.append(firstLabel, lastLabel);
    plot.append(svg, xAxis);
    shell.append(yAxis, plot);

    const evidence = document.createElement("p");
    evidence.className = "practice-result-line-evidence";
    evidence.dataset.practiceLineEvidence = "true";
    figure.append(header, shell, evidence);
    insertVisualBeforeTable(tableWrap, figure);
    refreshPracticeLineCopy(figure);
  }

  function renderPracticeResultVisual(block) {
    renderPracticeBarVisual(block);
    renderPracticeLineVisual(block);
  }

  function enhanceExistingPracticeVisuals() {
    document.querySelectorAll("#terminalScroll .terminal-block").forEach(renderPracticeResultVisual);
  }

  const api = { buildPracticeBarModel, buildPracticeLineModel };
  root.coqueryPracticeResultVisual = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }

  if (typeof document === "undefined") {
    return;
  }

  const scroll = document.getElementById("terminalScroll");
  if (scroll && typeof MutationObserver !== "undefined") {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (!(node instanceof HTMLElement)) {
            return;
          }
          if (node.matches(".terminal-block")) {
            requestAnimationFrame(() => renderPracticeResultVisual(node));
          }
          node.querySelectorAll?.(".terminal-block").forEach((block) => {
            requestAnimationFrame(() => renderPracticeResultVisual(block));
          });
        });
      });
    });
    observer.observe(scroll, { childList: true, subtree: false });
  }

  requestAnimationFrame(enhanceExistingPracticeVisuals);
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      requestAnimationFrame(() => {
        document.querySelectorAll("[data-practice-bar-visual]").forEach(refreshPracticeBarCopy);
        document.querySelectorAll("[data-practice-line-visual]").forEach(refreshPracticeLineCopy);
      });
    });
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
