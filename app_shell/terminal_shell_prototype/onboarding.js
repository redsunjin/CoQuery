const firstProblemButton = document.getElementById("firstProblemButton");
const problemBankButton = document.getElementById("problemBankButton");
const advancedWorkspaceButton = document.getElementById("advancedWorkspaceButton");
const homeButton = document.getElementById("homeButton");

const learningHomeCopy = {
  ko: {
    home: "홈",
    title: "데이터로 직접 확인하며 SQL을 배워보세요.",
    copy: "별도 DB 연결이나 AI 설정 없이 샘플 데이터로 바로 시작할 수 있습니다. 첫 문제를 풀고, 필요할 때 실제 데이터와 고급 기능으로 확장하세요.",
    firstProblem: "첫 문제 시작하기",
    problemBank: "문제 선택",
    advanced: "고급 기능",
    step1Title: "1. 문제를 읽고",
    step1Copy: "실제 업무와 비슷한 데이터 질문에서 시작합니다.",
    step2Title: "2. SQL을 실행하고",
    step2Copy: "내장 샘플 DB에서 결과를 바로 확인합니다.",
    step3Title: "3. 피드백을 받기",
    step3Copy: "채점, 힌트, 오답 노트로 다음 문제까지 이어갑니다.",
  },
  en: {
    home: "Home",
    title: "Learn SQL by checking real data results.",
    copy: "Start immediately with built-in sample data—no database connection or AI setup required. Solve the first problem, then expand into your own data and advanced tools when you need them.",
    firstProblem: "Start first problem",
    problemBank: "Choose a problem",
    advanced: "Advanced tools",
    step1Title: "1. Read a problem",
    step1Copy: "Begin with a concrete data question similar to real work.",
    step2Title: "2. Run SQL",
    step2Copy: "Check the result immediately against the built-in sample database.",
    step3Title: "3. Get feedback",
    step3Copy: "Use grading, hints, and wrong notes to continue learning.",
  },
};

function applyLearningHomeTranslations() {
  const lang = document.documentElement.lang === "en" ? "en" : "ko";
  const copy = learningHomeCopy[lang];
  document.querySelectorAll("[data-home-copy]").forEach((node) => {
    const key = node.dataset.homeCopy;
    if (copy[key]) {
      node.textContent = copy[key];
    }
  });
}

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

document.querySelectorAll("[data-lang]").forEach((button) => {
  button.addEventListener("click", () => {
    requestAnimationFrame(applyLearningHomeTranslations);
  });
});

applyLearningHomeTranslations();
