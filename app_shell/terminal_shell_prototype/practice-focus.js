const practiceFocusCopy = {
  ko: {
    hintShow: "힌트 보기",
    hintHide: "힌트 숨기기",
    problemBank: "문제 목록",
    sqlLabel: "내 SQL",
    run: "실행하고 확인하기",
    ready: "SQL을 작성한 뒤 실행해 보세요.",
    nextProblem: "다음 문제",
    reviewPath: "학습경로 보기",
    resultTable: "쿼리 결과",
    recommendation: "추천",
    evidenceTable: "표는 원본 결과를 그대로 보여주는 기준 화면입니다.",
  },
  en: {
    hintShow: "Show hint",
    hintHide: "Hide hint",
    problemBank: "Problem list",
    sqlLabel: "My SQL",
    run: "Run and check",
    ready: "Write your SQL, then run it.",
    nextProblem: "Next problem",
    reviewPath: "View learning path",
    resultTable: "Query result",
    recommendation: "Recommended",
    evidenceTable: "The table remains the canonical view of the returned result.",
  },
};

function practiceFocusLanguage() {
  return document.documentElement.lang === "en" ? "en" : "ko";
}

function practiceFocusText(key) {
  return practiceFocusCopy[practiceFocusLanguage()]?.[key] || practiceFocusCopy.en[key] || key;
}

function practiceCommandForBlock(block) {
  return block?.__result?.command || block?.querySelector(".block-command code")?.textContent?.trim() || "";
}

function setPracticeFocusMode(enabled) {
  if (!appShell) {
    return;
  }
  appShell.dataset.practiceFocus = enabled ? "true" : "false";
  if (!enabled) {
    document.querySelectorAll(".practice-focus-block, .practice-feedback-block").forEach((block) => {
      block.classList.remove(
        "practice-focus-block",
        "practice-feedback-block",
        "practice-query-result",
        "practice-grade-result",
        "practice-support-result"
      );
    });
  }
}

function hideTerminalChrome(block) {
  const commandHeader = block.querySelector(":scope > .block-command");
  const actionBar = block.querySelector(":scope > .block-actions");
  if (commandHeader) {
    commandHeader.hidden = true;
  }
  if (actionBar) {
    actionBar.hidden = true;
  }

  const directCliLines = [...block.children].filter((node) => node.classList?.contains("cli-line"));
  const cliEquivalent = directCliLines[directCliLines.length - 1];
  if (cliEquivalent) {
    cliEquivalent.hidden = true;
  }
}

async function openPracticeLearningPath() {
  setPracticeFocusMode(false);
  if (typeof setLearningPathMode === "function") {
    setLearningPathMode(true);
  } else if (appShell) {
    appShell.dataset.learningPath = "true";
  }

  if (typeof refreshLearningPath === "function") {
    const block = await refreshLearningPath();
    block?.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }

  if (typeof ensurePracticeList === "function") {
    await Promise.resolve(ensurePracticeList());
    const blocks = [...document.querySelectorAll("#terminalScroll .terminal-block")];
    const listBlock = blocks.reverse().find((block) => practiceCommandForBlock(block) === "practice_list");
    listBlock?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function leavePracticeForProblemBank() {
  openPracticeLearningPath().catch((error) => {
    console.error("Failed to open learning path", error);
  });
}

async function startNextPracticeProblem(currentProblemId) {
  const listResult = await postCommand("practice_list", {}, { mode: "training" });
  if (!listResult?.ok) {
    addBlock(listResult);
    return;
  }

  const problems = listResult.data?.problems || [];
  const packId = listResult.data?.selected_pack || "sql_basics";
  const attemptResult = await postCommand("practice_attempts", { pack: packId, limit: 500 }, { mode: "training" });
  const completed = new Set(
    (attemptResult?.ok ? attemptResult.data?.attempts || [] : [])
      .filter((attempt) => attempt.correct === true)
      .map((attempt) => attempt.problem_id)
  );

  const currentIndex = Math.max(0, problems.findIndex((problem) => problem.id === currentProblemId));
  const afterCurrent = problems.slice(currentIndex + 1).find((problem) => !completed.has(problem.id));
  const nextProblem = afterCurrent || problems.find((problem) => !completed.has(problem.id));

  if (!nextProblem) {
    await openPracticeLearningPath();
    return;
  }

  if (typeof setLearningPathMode === "function") {
    setLearningPathMode(false);
  } else if (appShell) {
    appShell.dataset.learningPath = "false";
  }
  addBlock(practiceStartResult(nextProblem, packId));
}

function refreshPracticeFocusCopy(block = document.querySelector(".practice-focus-block")) {
  if (!block) {
    return;
  }
  const form = block.querySelector("[data-practice-form]");
  if (!form) {
    return;
  }

  const hint = form.querySelector(".practice-hint");
  const hintButton = form.querySelector(".practice-hint-toggle");
  if (hintButton) {
    hintButton.textContent = practiceFocusText(hint?.hidden === false ? "hintHide" : "hintShow");
  }

  const bankButton = form.querySelector(".practice-bank-button");
  if (bankButton) {
    bankButton.textContent = practiceFocusText("problemBank");
  }

  const sqlLabel = form.querySelector(".practice-sql-field > span");
  if (sqlLabel) {
    sqlLabel.textContent = practiceFocusText("sqlLabel");
  }

  const submit = form.querySelector("[data-practice-submit]");
  if (submit) {
    submit.textContent = practiceFocusText("run");
  }

  const status = form.querySelector("[data-practice-status]");
  if (status && !status.classList.contains("ok") && !status.classList.contains("error")) {
    status.textContent = practiceFocusText("ready");
  }
}

function practiceResultCellText(value) {
  if (value === null) {
    return "NULL";
  }
  if (value === undefined) {
    return "";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function practiceResultRecommendationName(intelligence = {}) {
  const visual = intelligence.recommended_visual;
  if (visual) {
    return visual.charAt(0).toUpperCase() + visual.slice(1);
  }
  return "Table";
}

function refreshPracticeQueryTableCopy(block) {
  if (!block) {
    return;
  }
  const result = block.__result || {};
  const rowCount = Array.isArray(result.data?.rows) ? result.data.rows.length : Number(result.data?.row_count || 0);
  const caption = block.querySelector("[data-practice-result-caption]");
  if (caption) {
    caption.textContent = `${practiceFocusText("resultTable")} · ${rowCount}`;
  }

  const recommendation = block.querySelector("[data-practice-result-recommendation]");
  if (recommendation) {
    const intelligence = result.data?.result_intelligence || {};
    const view = practiceResultRecommendationName(intelligence);
    const reason = intelligence.reason ? ` · ${intelligence.reason}` : "";
    recommendation.textContent = `${practiceFocusText("recommendation")}: ${view}${reason}`;
  }

  const evidence = block.querySelector("[data-practice-result-evidence]");
  if (evidence) {
    evidence.textContent = practiceFocusText("evidenceTable");
  }
}

function enhancePracticeQueryTable(block) {
  if (!block || block.dataset.practiceResultTableEnhanced === "true") {
    return;
  }
  const result = block.__result;
  if (!result?.ok || result.command !== "practice_query") {
    return;
  }

  const columns = Array.isArray(result.data?.columns) ? result.data.columns : [];
  const rows = Array.isArray(result.data?.rows) ? result.data.rows : [];
  if (!columns.length) {
    return;
  }

  block.dataset.practiceResultTableEnhanced = "true";

  const oldGrid = block.querySelector(":scope > .block-grid");
  if (oldGrid) {
    oldGrid.hidden = true;
  }

  const wrapper = document.createElement("div");
  wrapper.className = "practice-result-table-wrap";
  wrapper.dataset.practiceResultTable = "true";

  const recommendation = document.createElement("div");
  recommendation.className = "practice-result-recommendation";
  recommendation.dataset.practiceResultRecommendation = "true";

  const evidence = document.createElement("div");
  evidence.className = "practice-result-evidence";
  evidence.dataset.practiceResultEvidence = "true";

  const scroller = document.createElement("div");
  scroller.className = "practice-result-table-scroll";

  const table = document.createElement("table");
  table.className = "practice-result-table";

  const caption = document.createElement("caption");
  caption.dataset.practiceResultCaption = "true";
  table.appendChild(caption);

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  columns.forEach((column) => {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = String(column);
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    columns.forEach((column) => {
      const td = document.createElement("td");
      const value = row?.[column];
      td.textContent = practiceResultCellText(value);
      if (value === null) {
        td.classList.add("is-null");
      } else if (typeof value === "number") {
        td.classList.add("is-number");
      }
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  scroller.appendChild(table);
  wrapper.append(recommendation, evidence, scroller);

  const summary = block.querySelector(":scope > .block-summary");
  if (summary) {
    summary.insertAdjacentElement("afterend", wrapper);
  } else {
    block.appendChild(wrapper);
  }

  refreshPracticeQueryTableCopy(block);
}

function enhancePracticeStart(block) {
  if (!block || block.dataset.practiceFocusEnhanced === "true") {
    return;
  }
  block.dataset.practiceFocusEnhanced = "true";

  document.querySelectorAll(".practice-focus-block, .practice-feedback-block").forEach((item) => {
    item.classList.remove(
      "practice-focus-block",
      "practice-feedback-block",
      "practice-query-result",
      "practice-grade-result",
      "practice-support-result"
    );
  });

  setPracticeFocusMode(true);
  block.classList.add("practice-focus-block");
  hideTerminalChrome(block);

  const summary = block.querySelector(":scope > .block-summary");
  summary?.classList.add("practice-title-summary");

  const form = block.querySelector("[data-practice-form]");
  if (!form) {
    return;
  }

  const problemCard = form.querySelector(".practice-problem-card");
  problemCard?.classList.add("practice-focus-problem");

  const hint = form.querySelector(".practice-hint");
  const supportActions = [...form.querySelectorAll(".practice-flow-actions")].find((row) => row.querySelector(".practice-schema-button"));
  const primaryActions = [...form.querySelectorAll(".practice-flow-actions")].find((row) => row.querySelector("[data-practice-submit]"));
  supportActions?.classList.add("practice-support-actions");
  primaryActions?.classList.add("practice-primary-actions");

  if (hint && supportActions) {
    hint.hidden = true;
    const hintButton = document.createElement("button");
    hintButton.className = "ghost-button practice-hint-toggle";
    hintButton.type = "button";
    hintButton.addEventListener("click", () => {
      hint.hidden = !hint.hidden;
      hintButton.textContent = practiceFocusText(hint.hidden ? "hintShow" : "hintHide");
      hintButton.setAttribute("aria-expanded", hint.hidden ? "false" : "true");
    });
    hintButton.setAttribute("aria-expanded", "false");
    supportActions.prepend(hintButton);
  }

  if (supportActions) {
    const bankButton = document.createElement("button");
    bankButton.className = "ghost-button practice-bank-button";
    bankButton.type = "button";
    bankButton.addEventListener("click", leavePracticeForProblemBank);
    supportActions.append(bankButton);
  }

  const preview = form.querySelector("[data-practice-preview]");
  if (preview) {
    preview.hidden = true;
  }

  refreshPracticeFocusCopy(block);

  const textarea = form.querySelector('textarea[name="sql"]');
  requestAnimationFrame(() => textarea?.focus());
}

function addPracticeGradeNavigation(block) {
  const result = block?.__result;
  if (!result?.ok || result.command !== "practice_grade" || result.data?.correct !== true) {
    return;
  }
  if (block.querySelector("[data-practice-next-actions]")) {
    return;
  }

  const actions = document.createElement("div");
  actions.className = "practice-flow-actions practice-grade-next-actions";
  actions.dataset.practiceNextActions = "true";

  const nextButton = document.createElement("button");
  nextButton.className = "primary-button";
  nextButton.type = "button";
  nextButton.textContent = practiceFocusText("nextProblem");
  nextButton.addEventListener("click", () => {
    nextButton.disabled = true;
    startNextPracticeProblem(result.data?.problem?.id || "")
      .catch((error) => {
        addBlock({
          ok: false,
          command: "practice_next",
          block_type: "practice_flow",
          actions: ["copy"],
          cli_equivalent: "practice_list",
          error: { message: error.message },
          data: {},
        });
      })
      .finally(() => {
        nextButton.disabled = false;
      });
  });

  const pathButton = document.createElement("button");
  pathButton.className = "ghost-button";
  pathButton.type = "button";
  pathButton.textContent = practiceFocusText("reviewPath");
  pathButton.addEventListener("click", leavePracticeForProblemBank);

  actions.append(nextButton, pathButton);
  block.appendChild(actions);
}

function enhancePracticeFeedback(block, command) {
  if (!block || block.dataset.practiceFeedbackEnhanced === "true" || appShell?.dataset.practiceFocus !== "true") {
    return;
  }
  block.dataset.practiceFeedbackEnhanced = "true";
  block.classList.add("practice-feedback-block");
  if (command === "practice_query") {
    block.classList.add("practice-query-result");
  } else if (command === "practice_grade") {
    block.classList.add("practice-grade-result");
  } else {
    block.classList.add("practice-support-result");
  }
  hideTerminalChrome(block);

  if (command === "practice_query") {
    enhancePracticeQueryTable(block);
  }

  if (command === "practice_grade") {
    addPracticeGradeNavigation(block);
    requestAnimationFrame(() => block.scrollIntoView({ behavior: "smooth", block: "nearest" }));
  }
}

function enhancePracticeBlock(block) {
  const command = practiceCommandForBlock(block);
  if (command === "practice_start") {
    enhancePracticeStart(block);
    return;
  }
  if (["practice_query", "practice_grade", "practice_schema", "practice_attempts", "practice_feedback"].includes(command)) {
    enhancePracticeFeedback(block, command);
  }
}

const practiceFocusObserver = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (!(node instanceof HTMLElement)) {
        return;
      }
      if (node.matches(".terminal-block")) {
        enhancePracticeBlock(node);
      }
      node.querySelectorAll?.(".terminal-block").forEach(enhancePracticeBlock);
    });
  });
});

if (terminalScroll) {
  practiceFocusObserver.observe(terminalScroll, { childList: true, subtree: false });
  terminalScroll.querySelectorAll(".terminal-block").forEach(enhancePracticeBlock);
}

homeButton?.addEventListener("click", () => setPracticeFocusMode(false));
problemBankButton?.addEventListener("click", () => setPracticeFocusMode(false));
advancedWorkspaceButton?.addEventListener("click", () => setPracticeFocusMode(false));

languageButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setTimeout(() => {
      refreshPracticeFocusCopy();
      document.querySelectorAll("[data-practice-next-actions]").forEach((actions) => {
        const buttons = actions.querySelectorAll("button");
        if (buttons[0]) buttons[0].textContent = practiceFocusText("nextProblem");
        if (buttons[1]) buttons[1].textContent = practiceFocusText("reviewPath");
      });
      document.querySelectorAll(".practice-query-result").forEach(refreshPracticeQueryTableCopy);
    }, 0);
  });
});
