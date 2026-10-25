const firstProblemButton = document.getElementById("firstProblemButton");
const problemBankButton = document.getElementById("problemBankButton");
const advancedWorkspaceButton = document.getElementById("advancedWorkspaceButton");
const homeButton = document.getElementById("homeButton");

const learningHomeCopy = {
  ko: {
    home: "홈",
    exploration: "조건 탐구 시작 / 이어가기",
    conceptPuzzles: "조건·관계·규칙 문제 선택",
    title: "조건을 바꾸고, 생각을 확인해 보세요.",
    copy: "SQL을 몰라도 시작할 수 있습니다. 예상하고, 반례를 찾고, 나만의 규칙을 만들어 보세요. 현재는 학습 효과를 검증 중인 내부 베타입니다.",
    firstProblem: "SQL 학습 시작 / 이어가기",
    problemBank: "SQL 문제 선택",
    advanced: "데이터 작업 도구",
    intro: "서비스 소개",
    support: "고객 지원",
    privacy: "개인정보 처리방침",
    step1Title: "1. 예상하고 실험하기",
    step1Copy: "조건에 따라 남을 항목을 먼저 골라 보세요.",
    step2Title: "2. 반례로 설명 다듬기",
    step2Copy: "예상과 다른 이유를 찾고 새 상황에 적용하세요.",
    step3Title: "3. 나만의 규칙 만들기",
    step3Copy: "직접 만든 퍼즐을 저장하고 다시 실험하세요.",
  },
  en: {
    home: "Home",
    exploration: "Explore conditions (Korean)",
    conceptPuzzles: "Conditions, relations & rules (Korean)",
    title: "Change a condition. Test your thinking.",
    copy: "Predict, find counterexamples and build your own rules without SQL. This internal beta has not been validated for learning effectiveness. Exploration content is in Korean.",
    firstProblem: "Start / resume SQL",
    problemBank: "Choose a SQL problem",
    advanced: "Advanced tools",
    intro: "About CoQuery",
    support: "Support",
    privacy: "Privacy Policy",
    step1Title: "1. Predict and experiment",
    step1Copy: "Choose what you expect a rule to keep.",
    step2Title: "2. Explain a counterexample",
    step2Copy: "Revise your explanation and apply it to a new situation.",
    step3Title: "3. Create your own rule",
    step3Copy: "Save your puzzle, replay it and revise it.",
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

  const privacyPolicyLink = document.getElementById("privacyPolicyLink");
  if (privacyPolicyLink) {
    privacyPolicyLink.href = `https://redsunjin.github.io/CoQuery/privacy/?lang=${lang}`;
  }
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

// Optional task-based guidance. Reading a guide never marks a lesson complete.
(() => {
  const guide = document.getElementById("learningGuide");
  if (!guide) return;
  let path = "concept";
  const copy = {
    ko: {
      summary: "처음이라면: 사용법과 세 가지 시작 방법", title: "어떤 방식으로 시작할까요?",
      paths: ["개념부터 이해하기", "SQL 연습하기", "함께 검토하는 과정 보기"], done: "안내 읽음 · 접기",
      read: "안내를 읽었습니다. 필요할 때 언제든 다시 펼칠 수 있습니다.", unavailable: "이 기기에 읽음 표시를 저장하지 못했습니다. 안내는 계속 볼 수 있습니다.",
      concept: ["SQL을 몰라도 조건·관계·규칙을 직접 비교할 수 있습니다.", ["‘조건 탐구 시작 / 이어가기’를 누르세요. 그리고·또는의 차이부터 시작합니다.", "안내형 그리고와 독립형 또는을 각각 예상·실험하세요.", "주장을 깨는 반례를 고르고 내 말로 설명한 뒤 책 선택에 적용하세요.", "나만의 조건·항목·규칙을 바꾸고 실행·저장하세요. SQL 학습 후 홈에서 이어갈 수 있습니다."], "기록은 이 브라우저/기기에만 저장됩니다. 설명 기록은 숙달 평가가 아니며 기기 간 동기화되지 않습니다.", "조건 탐구 열기"],
      sql: ["샘플 데이터로 SQL을 실행하고 결과를 확인합니다. DB·AI 설정 없이 시작합니다.", ["SQL 학습을 시작하거나 아직 풀지 않은 문제를 이어서 여세요.", "문제와 힌트를 읽고 테이블 이름을 확인하세요. 첫 문제의 열은 id, name, region입니다.", "SQL을 작성해 ‘실행하고 확인하기’를 누르세요. 오류가 나면 열 이름과 조건을 고쳐 다시 실행하세요.", "정답 여부와 실제 행을 확인하고 표·흐름·해설을 비교한 뒤 다음 문제로 이동하세요."], "정답은 해당 문제의 결과 비교입니다. 학습 효과나 다른 상황에서의 이해를 보장하지 않습니다.", "SQL 학습 시작 / 이어서하기"],
      community: ["질문을 함께 검토하고 이의를 제기하는 과정을 모의 데이터로 체험합니다.", ["모의 질문을 작성하고 사실·의견·창의적 가설 중 성격을 구분하세요. 개인정보는 쓰지 마세요.", "AI 사전 검사와 중립적 표현 제안을 살펴보세요. 실패·대기·취소도 선택할 수 있습니다.", "사람 검토 단계를 거친 뒤 주장·근거·반례·대안을 담아 답하고 요약의 출처를 확인하세요.", "신고와 항소를 체험하세요. 모의 검토자 판단도 실제 제재나 다른 사람에게 전달되지 않습니다."], "실제 AI·서버·다른 참여자와 연결되지 않습니다. 입력은 공개되지 않으며 페이지를 새로 열면 모의 체험이 초기화됩니다.", "참여형 모의 체험 열기"]
    },
    en: {
      summary: "New here? Explore three ways to start", title: "What would you like to try?", paths: ["Understand concepts", "Practice SQL", "Explore community review"], done: "Read · close guide", read: "Guide read. You can reopen it anytime.", unavailable: "Could not save the read marker on this device. The guide is still available.",
      concept: ["Compare conditions, relationships and rules without SQL.", ["Start the conditions exploration (Korean content).", "Predict the result, select cards and run an experiment.", "Compare your prediction with the result. Change rules and look for counterexamples.", "Apply the rule to books, then create, save and replay your own puzzle."], "Notes stay in this browser/device. A saved explanation is not a mastery assessment and does not sync across devices.", "Open conditions exploration"],
      sql: ["Run SQL against sample data without database or AI setup.", ["Start SQL practice or continue with an unsolved problem.", "Read the task and hint. The first task uses id, name and region from customers.", "Write SQL and run it. Correct column names or conditions after an error, then retry.", "Check grading and actual rows. Compare Table, Flow and Explain, then continue."], "A correct result only verifies this task; it does not establish learning or transfer.", "Start / resume SQL"],
      community: ["Try collaborative review using mock data (Korean content).", ["Write a mock question and distinguish fact, opinion or creative hypothesis. Avoid personal data.", "Review the simulated AI check and wording suggestion. Try failure, waiting and cancellation.", "After simulated human review, answer with evidence, counterexamples and alternatives. Check summary sources.", "Try reporting and appealing. Simulated decisions do not sanction or notify anyone."], "No real AI, server or other participants are connected. Inputs are not published; reopening the page resets this demo.", "Open community demo"]
    }
  };
  const byId = (id) => document.getElementById(id);
  function renderGuide() {
    const c = copy[document.documentElement.lang === "en" ? "en" : "ko"];
    byId("learningGuideSummary").textContent = c.summary;
    byId("learningGuideTitle").textContent = c.title;
    byId("learningGuidePaths").setAttribute("aria-label", document.documentElement.lang === "en" ? "Guide paths" : "사용 안내 경로");
    guide.querySelectorAll("[data-guide-path]").forEach((button, index) => {
      button.textContent = c.paths[index];
      button.setAttribute("aria-pressed", String(button.dataset.guidePath === path));
    });
    byId("learningGuidePurpose").textContent = c[path][0];
    byId("learningGuideSteps").querySelectorAll("li").forEach((item, index) => { item.textContent = c[path][1][index]; });
    byId("learningGuideLimit").textContent = c[path][2];
    byId("learningGuideStart").textContent = c[path][3];
    byId("learningGuideDemo").textContent = c[path][3];
    byId("learningGuideStart").hidden = path === "community";
    byId("learningGuideDemo").hidden = path !== "community";
    byId("learningGuideDone").textContent = c.done;
    try { byId("learningGuideStatus").textContent = localStorage.getItem("coquery.guide.v1") === "read" ? c.read : ""; } catch { /* Guidance works without storage. */ }
  }
  guide.querySelectorAll("[data-guide-path]").forEach((button) => button.addEventListener("click", () => { path = button.dataset.guidePath; renderGuide(); }));
  byId("learningGuideStart").addEventListener("click", () => byId(path === "sql" ? "firstProblemButton" : "explorationButton").click());
  byId("learningGuideDone").addEventListener("click", () => {
    const c = copy[document.documentElement.lang === "en" ? "en" : "ko"];
    try { localStorage.setItem("coquery.guide.v1", "read"); byId("learningGuideStatus").textContent = c.read; }
    catch { byId("learningGuideStatus").textContent = c.unavailable; }
    guide.open = false;
    byId("learningGuideSummary").focus();
  });
  document.querySelectorAll("[data-lang]").forEach((button) => button.addEventListener("click", () => requestAnimationFrame(renderGuide)));
  renderGuide();
})();
