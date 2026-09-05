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

function practiceListBlock() {
  return [...document.querySelectorAll("#terminalScroll .terminal-block")].find(
    (block) => block.__result?.command === "practice_list" || block.querySelector(".block-command code")?.textContent?.trim() === "practice_list"
  );
}

function hasPracticeListBlock() {
  return Boolean(practiceListBlock());
}

async function ensurePracticeList() {
  if (hasPracticeListBlock()) {
    return null;
  }
  const result = await postCommand("practice_list", {}, { mode: "training" });
  addBlock(result);
  return result;
}

async function nextPracticeProblem(problems, packId) {
  if (!problems.length) {
    return null;
  }
  try {
    const attemptResult = await postCommand("practice_attempts", { pack: packId, limit: 500 }, { mode: "training" });
    if (attemptResult?.ok) {
      const completed = new Set(
        (attemptResult.data?.attempts || []).filter((attempt) => attempt.correct === true).map((attempt) => attempt.problem_id)
      );
      return problems.find((problem) => !completed.has(problem.id)) || problems[0];
    }
  } catch {
    // Fall back to the first problem when progress cannot be read.
  }
  return problems[0];
}

async function startFirstPracticeProblem() {
  setLearningHomeMode(false);
  try {
    const result = await postCommand("practice_list", {}, { mode: "training" });
    const problems = result.data?.problems || [];
    const packId = result.data?.selected_pack || "sql_basics";
    const problem = await nextPracticeProblem(problems, packId);
    if (!problem) {
      addBlock(result);
      return;
    }
    addBlock(practiceStartResult(problem, packId));
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

function loadPracticeResultVisualAssets() {
  if (!document.querySelector('link[data-practice-result-visual-style]')) {
    const style = document.createElement("link");
    style.rel = "stylesheet";
    style.href = "./practice-result-visual.css";
    style.dataset.practiceResultVisualStyle = "true";
    document.head.appendChild(style);
  }

  if (!document.querySelector('script[data-practice-result-visual-script]')) {
    const script = document.createElement("script");
    script.src = "./practice-result-visual.js";
    script.dataset.practiceResultVisualScript = "true";
    document.body.appendChild(script);
  }
}

function loadPracticeQueryFlowAssets() {
  if (!document.querySelector('link[data-practice-query-flow-style]')) {
    const style = document.createElement("link");
    style.rel = "stylesheet";
    style.href = "./practice-query-flow.css";
    style.dataset.practiceQueryFlowStyle = "true";
    document.head.appendChild(style);
  }

  if (!document.querySelector('script[data-practice-query-flow-script]')) {
    const script = document.createElement("script");
    script.src = "./practice-query-flow.js";
    script.dataset.practiceQueryFlowScript = "true";
    document.body.appendChild(script);
  }
}

function loadPracticeResultExplainAssets() {
  if (!document.querySelector('link[data-practice-result-explain-style]')) {
    const style = document.createElement("link");
    style.rel = "stylesheet";
    style.href = "./practice-result-explain.css";
    style.dataset.practiceResultExplainStyle = "true";
    document.head.appendChild(style);
  }

  if (!document.querySelector('script[data-practice-result-explain-script]')) {
    const script = document.createElement("script");
    script.src = "./practice-result-explain.js";
    script.dataset.practiceResultExplainScript = "true";
    document.body.appendChild(script);
  }
}

function loadPracticeResultIntelligenceAssets() {
  loadPracticeResultVisualAssets();
  loadPracticeQueryFlowAssets();
  loadPracticeResultExplainAssets();
}

function loadPracticeFocusAssets() {
  if (!document.querySelector('link[data-practice-focus-style]')) {
    const style = document.createElement("link");
    style.rel = "stylesheet";
    style.href = "./practice-focus.css";
    style.dataset.practiceFocusStyle = "true";
    document.head.appendChild(style);
  }

  const existing = document.querySelector('script[data-practice-focus-script]');
  if (existing) {
    loadPracticeResultIntelligenceAssets();
    return;
  }

  const script = document.createElement("script");
  script.src = "./practice-focus.js";
  script.dataset.practiceFocusScript = "true";
  script.addEventListener("load", loadPracticeResultIntelligenceAssets, { once: true });
  document.body.appendChild(script);
}

function loadExpandedCurriculumAsset() {
  if (document.querySelector('script[data-curriculum-expansion-script]')) {
    return;
  }
  const script = document.createElement("script");
  script.src = "./curriculum-expansion.js";
  script.dataset.curriculumExpansionScript = "true";
  document.body.appendChild(script);
}

function loadLearningPathAssets() {
  if (!document.querySelector('link[data-learning-path-style]')) {
    const style = document.createElement("link");
    style.rel = "stylesheet";
    style.href = "./learning-path.css";
    style.dataset.learningPathStyle = "true";
    document.head.appendChild(style);
  }

  const existing = document.querySelector('script[data-learning-path-script]');
  if (existing) {
    if (typeof learningPathUnits !== "undefined") {
      loadExpandedCurriculumAsset();
    } else {
      existing.addEventListener("load", loadExpandedCurriculumAsset, { once: true });
    }
    return;
  }

  const script = document.createElement("script");
  script.src = "./learning-path.js";
  script.dataset.learningPathScript = "true";
  script.addEventListener("load", loadExpandedCurriculumAsset, { once: true });
  document.body.appendChild(script);
}

applyLearningHomeTranslations();
loadPracticeFocusAssets();
loadLearningPathAssets();