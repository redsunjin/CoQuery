(function (root) {
  const RECOGNIZED_KINDS = new Set([
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
      title: "SQL 변환 흐름",
      description: "SQL에 명시된 논리적 변환을 보여줍니다. 실제 DB 실행 순서를 뜻하지 않습니다.",
      result: "결과",
      rows: "{count}행",
      from: "원본",
      join: "결합",
      where: "필터",
      group_by: "그룹",
      aggregate: "집계",
      having: "그룹 필터",
      order_by: "정렬",
      limit: "제한",
    },
    en: {
      title: "SQL transformation flow",
      description: "Shows logical transformations explicitly present in the SQL. This is not the database execution order.",
      result: "Result",
      rows: "{count} rows",
      from: "Source",
      join: "Join",
      where: "Filter",
      group_by: "Group",
      aggregate: "Aggregate",
      having: "Group filter",
      order_by: "Sort",
      limit: "Limit",
    },
  };

  function currentLanguage() {
    if (typeof document === "undefined") {
      return "en";
    }
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

  function buildPracticeQueryFlowModel(result) {
    if (!result?.ok || result.command !== "practice_query") {
      return null;
    }
    const intelligence = result.data?.result_intelligence || {};
    const sourceSteps = Array.isArray(intelligence.flow_steps) ? intelligence.flow_steps : [];
    const steps = sourceSteps
      .filter((step) => RECOGNIZED_KINDS.has(step?.kind) && typeof step?.text === "string" && step.text.trim())
      .map((step) => ({ kind: step.kind, text: step.text.trim() }));
    if (!steps.length) {
      return null;
    }

    const explicitRowCount = Number(result.data?.row_count);
    const rows = Array.isArray(result.data?.rows) ? result.data.rows : [];
    const rowCount = Number.isFinite(explicitRowCount) && explicitRowCount >= 0 ? explicitRowCount : rows.length;

    return {
      type: "query_flow",
      steps,
      row_count: rowCount,
    };
  }

  function refreshPracticeQueryFlowCopy(figure) {
    const model = figure?.__queryFlowModel;
    if (!figure || !model) {
      return;
    }
    const title = figure.querySelector("[data-practice-query-flow-title]");
    const description = figure.querySelector("[data-practice-query-flow-description]");
    if (title) title.textContent = text("title");
    if (description) description.textContent = text("description");

    figure.querySelectorAll("[data-practice-query-flow-kind]").forEach((node) => {
      const kind = node.dataset.practiceQueryFlowKind;
      node.textContent = text(kind);
    });

    const resultKind = figure.querySelector("[data-practice-query-flow-result-kind]");
    const resultRows = figure.querySelector("[data-practice-query-flow-result-rows]");
    if (resultKind) resultKind.textContent = text("result");
    if (resultRows) resultRows.textContent = text("rows", { count: model.row_count });

    figure.setAttribute("aria-label", `${text("title")}. ${text("description")}`);
  }

  function makeNode(step) {
    const item = document.createElement("li");
    item.className = "practice-query-flow-node";

    const kind = document.createElement("span");
    kind.className = "practice-query-flow-kind";
    kind.dataset.practiceQueryFlowKind = step.kind;

    const sql = document.createElement("code");
    sql.className = "practice-query-flow-sql";
    sql.textContent = step.text;

    item.append(kind, sql);
    return item;
  }

  function renderPracticeQueryFlow(block) {
    if (!block || block.dataset.practiceQueryFlowEnhanced === "true") {
      return;
    }
    const model = buildPracticeQueryFlowModel(block.__result);
    if (!model) {
      return;
    }

    const tableWrap = block.querySelector("[data-practice-result-table]");
    if (!tableWrap) {
      return;
    }

    block.dataset.practiceQueryFlowEnhanced = "true";
    const figure = document.createElement("figure");
    figure.className = "practice-query-flow";
    figure.dataset.practiceQueryFlow = "true";
    figure.__queryFlowModel = model;

    const header = document.createElement("div");
    header.className = "practice-query-flow-header";

    const title = document.createElement("figcaption");
    title.className = "practice-query-flow-title";
    title.dataset.practiceQueryFlowTitle = "true";

    const description = document.createElement("p");
    description.className = "practice-query-flow-description";
    description.dataset.practiceQueryFlowDescription = "true";
    header.append(title, description);

    const scroller = document.createElement("div");
    scroller.className = "practice-query-flow-scroll";

    const list = document.createElement("ol");
    list.className = "practice-query-flow-track";
    model.steps.forEach((step) => list.appendChild(makeNode(step)));

    const resultNode = document.createElement("li");
    resultNode.className = "practice-query-flow-node is-result";
    const resultKind = document.createElement("span");
    resultKind.className = "practice-query-flow-kind";
    resultKind.dataset.practiceQueryFlowResultKind = "true";
    const resultRows = document.createElement("span");
    resultRows.className = "practice-query-flow-result-rows";
    resultRows.dataset.practiceQueryFlowResultRows = "true";
    resultNode.append(resultKind, resultRows);
    list.appendChild(resultNode);

    scroller.appendChild(list);
    figure.append(header, scroller);

    const tableScroller = tableWrap.querySelector(".practice-result-table-scroll");
    if (tableScroller) {
      tableScroller.insertAdjacentElement("beforebegin", figure);
    } else {
      tableWrap.appendChild(figure);
    }

    refreshPracticeQueryFlowCopy(figure);
  }

  function enhanceExistingPracticeQueryFlows() {
    document.querySelectorAll("#terminalScroll .terminal-block").forEach(renderPracticeQueryFlow);
  }

  root.coqueryPracticeQueryFlow = { buildPracticeQueryFlowModel };

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
            requestAnimationFrame(() => renderPracticeQueryFlow(node));
          }
          node.querySelectorAll?.(".terminal-block").forEach((block) => {
            requestAnimationFrame(() => renderPracticeQueryFlow(block));
          });
        });
      });
    });
    observer.observe(scroll, { childList: true, subtree: false });
  }

  requestAnimationFrame(enhanceExistingPracticeQueryFlows);
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      requestAnimationFrame(() => {
        document.querySelectorAll("[data-practice-query-flow]").forEach(refreshPracticeQueryFlowCopy);
      });
    });
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
