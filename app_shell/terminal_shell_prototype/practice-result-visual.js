(function (root) {
  const copy = {
    ko: {
      title: "결과 시각화 · Bar",
      summary: "{dimension}별 {measure} 값을 쿼리 반환 순서대로 표시합니다.",
      evidence: "이 시각화는 현재 반환된 행만 사용합니다. Table이 기준 데이터입니다.",
    },
    en: {
      title: "Result visual · Bar",
      summary: "Shows {measure} by {dimension} in the exact returned row order.",
      evidence: "This visual uses only the current returned rows. Table remains the canonical evidence.",
    },
  };

  function isFiniteNumber(value) {
    return typeof value === "number" && Number.isFinite(value);
  }

  function clampPercent(value) {
    return Math.max(0, Math.min(100, value));
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

  function currentLanguage() {
    if (typeof document === "undefined") {
      return "en";
    }
    return document.documentElement.lang === "en" ? "en" : "ko";
  }

  function barCopy(key, model) {
    const lang = currentLanguage();
    const template = copy[lang]?.[key] || copy.en[key] || key;
    return template
      .replace("{dimension}", model?.dimension || "dimension")
      .replace("{measure}", model?.measure || "measure");
  }

  function formatBarValue(value) {
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
    if (title) title.textContent = barCopy("title", model);
    if (summary) summary.textContent = barCopy("summary", model);
    if (evidence) evidence.textContent = barCopy("evidence", model);
    figure.setAttribute("aria-label", `${barCopy("title", model)}. ${barCopy("summary", model)}`);
    figure.querySelectorAll("[data-practice-bar-value]").forEach((node) => {
      const value = Number(node.dataset.practiceBarValue);
      node.textContent = Number.isFinite(value) ? formatBarValue(value) : node.dataset.practiceBarValue;
    });
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
      value.textContent = formatBarValue(point.value);

      row.setAttribute("aria-label", `${point.label}: ${point.value}`);
      row.append(label, track, value);
      chart.appendChild(row);
    });

    const evidence = document.createElement("p");
    evidence.className = "practice-result-bar-evidence";
    evidence.dataset.practiceBarEvidence = "true";

    figure.append(header, chart, evidence);

    const tableScroller = tableWrap.querySelector(".practice-result-table-scroll");
    if (tableScroller) {
      tableScroller.insertAdjacentElement("beforebegin", figure);
    } else {
      tableWrap.appendChild(figure);
    }

    refreshPracticeBarCopy(figure);
  }

  function enhanceExistingPracticeBars() {
    document.querySelectorAll("#terminalScroll .terminal-block").forEach(renderPracticeBarVisual);
  }

  const api = { buildPracticeBarModel };
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
            requestAnimationFrame(() => renderPracticeBarVisual(node));
          }
          node.querySelectorAll?.(".terminal-block").forEach((block) => {
            requestAnimationFrame(() => renderPracticeBarVisual(block));
          });
        });
      });
    });
    observer.observe(scroll, { childList: true, subtree: false });
  }

  requestAnimationFrame(enhanceExistingPracticeBars);
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      requestAnimationFrame(() => {
        document.querySelectorAll("[data-practice-bar-visual]").forEach(refreshPracticeBarCopy);
      });
    });
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
