const practiceFocusCopy = {
  ko: {
    hintShow: "힌트 보기",
    hintHide: "힌트 숨기기",
    problemBank: "문제 목록",
    sqlLabel: "내 SQL",
    run: "실행하고 확인하기",
    ready: "SQL을 작성한 뒤 실행해 보세요.",
  },
  en: {
    hintShow: "Show hint",
    hintHide: "Hide hint",
    problemBank: "Problem list",
    sqlLabel: "My SQL",
    run: "Run and check",
    ready: "Write your SQL, then run it.",
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
      block.classList.remove("practice-focus-block", "practice-feedback-block", "practice-query-result", "practice-grade-result");
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
  const cliEquivalent = directCliLines.at(-1);
  if (cliEquivalent) {
    cliEquivalent.hidden = true;
  }
}

function leavePracticeForProblemBank() {
  setPracticeFocusMode(false);
  if (typeof ensurePracticeList === "function") {
    Promise.resolve(ensurePracticeList()).finally(() => {
      const blocks = [...document.querySelectorAll("#terminalScroll .terminal-block")];
      const listBlock = blocks.reverse().find((block) => practiceCommandForBlock(block) === "practice_list");
      listBlock?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
}

function enhancePracticeStart(block) {
  if (!block || block.dataset.practiceFocusEnhanced === "true") {
    return;
  }
  block.dataset.practiceFocusEnhanced = "true";

  document.querySelectorAll(".practice-focus-block, .practice-feedback-block").forEach((item) => {
    item.classList.remove("practice-focus-block", "practice-feedback-block", "practice-query-result", "practice-grade-result");
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
    hintButton.textContent = practiceFocusText("hintShow");
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
    bankButton.textContent = practiceFocusText("problemBank");
    bankButton.addEventListener("click", leavePracticeForProblemBank);
    supportActions.append(bankButton);
  }

  const sqlField = form.querySelector(".practice-sql-field");
  const sqlLabel = sqlField?.querySelector(":scope > span");
  if (sqlLabel) {
    sqlLabel.textContent = practiceFocusText("sqlLabel");
  }

  const submit = form.querySelector("[data-practice-submit]");
  if (submit) {
    submit.textContent = practiceFocusText("run");
  }

  const preview = form.querySelector("[data-practice-preview]");
  if (preview) {
    preview.hidden = true;
  }

  const status = form.querySelector("[data-practice-status]");
  if (status && !status.classList.contains("ok") && !status.classList.contains("error")) {
    status.textContent = practiceFocusText("ready");
  }

  const textarea = form.querySelector('textarea[name="sql"]');
  requestAnimationFrame(() => textarea?.focus());
}

function enhancePracticeFeedback(block, command) {
  if (!block || block.dataset.practiceFeedbackEnhanced === "true" || appShell?.dataset.practiceFocus !== "true") {
    return;
  }
  block.dataset.practiceFeedbackEnhanced = "true";
  block.classList.add("practice-feedback-block");
  if (command === "practice_query") {
    block.classList.add("practice-query-result");
  }
  if (command === "practice_grade") {
    block.classList.add("practice-grade-result");
  }
  hideTerminalChrome(block);

  if (command === "practice_grade") {
    requestAnimationFrame(() => block.scrollIntoView({ behavior: "smooth", block: "nearest" }));
  }
}

function enhancePracticeBlock(block) {
  const command = practiceCommandForBlock(block);
  if (command === "practice_start") {
    enhancePracticeStart(block);
    return;
  }
  if (command === "practice_query" || command === "practice_grade") {
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
      const current = document.querySelector(".practice-focus-block");
      if (!current) {
        return;
      }
      current.dataset.practiceFocusEnhanced = "false";
      enhancePracticeStart(current);
    }, 0);
  });
});
