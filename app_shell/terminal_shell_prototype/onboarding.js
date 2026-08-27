const firstProblemButton = document.getElementById("firstProblemButton");
const problemBankButton = document.getElementById("problemBankButton");
const advancedWorkspaceButton = document.getElementById("advancedWorkspaceButton");
const homeButton = document.getElementById("homeButton");

function setLearningHomeMode(enabled) {
  if (!appShell) {
    return;
  }
  appShell.dataset.homeMode = enabled ? "true" : "false";
  if (typeof setCommandMenuOpen === "function") {
    setCommandMenuOpen(false);
  }
  if (!enabled && commandInput) {
    requestAnimationFrame(() => commandInput.focus());
  }
}

function hasPracticeListBlock() {
  return [...document.querySelectorAll("#terminalScroll .terminal-block .block-command code")].some(
    (node) => node.textContent?.trim() === "practice_list"
  );
}

async function ensurePracticeList() {
  if (hasPracticeListBlock()) {
    return null;
  }
  const result = await postCommand("practice_list", {}, { mode: "training" });
  addBlock(result);
  return result;
}

async function startFirstPracticeProblem() {
  setLearningHomeMode(false);
  try {
    const result = await postCommand("practice_list", {}, { mode: "training" });
    const problems = result.data?.problems || [];
    const firstProblem = problems[0];
    if (!firstProblem) {
      addBlock(result);
      return;
    }
    addBlock(practiceStartResult(firstProblem, result.data?.selected_pack || "sql_basics"));
  } catch (error) {
    addBlock({
      ok: false,
      command: "practice_start",
      block_type: "practice_flow",
      actions: ["copy"],
      cli_equivalent: "practice_list",
      error: { message: error.message },
      data: {},
    });
  }
}

if (firstProblemButton) {
  firstProblemButton.addEventListener("click", () => {
    startFirstPracticeProblem();
  });
}

if (problemBankButton) {
  problemBankButton.addEventListener("click", async () => {
    setLearningHomeMode(false);
    try {
      await ensurePracticeList();
    } catch (error) {
      addBlock({
        ok: false,
        command: "practice_list",
        block_type: "practice_list",
        actions: ["copy"],
        cli_equivalent: "practice_list",
        error: { message: error.message },
        data: {},
      });
    }
  });
}

if (advancedWorkspaceButton) {
  advancedWorkspaceButton.addEventListener("click", () => {
    setLearningHomeMode(false);
  });
}

if (homeButton) {
  homeButton.addEventListener("click", () => {
    setLearningHomeMode(true);
  });
}

if (commandForm) {
  commandForm.addEventListener("submit", () => {
    setLearningHomeMode(false);
  });
}
