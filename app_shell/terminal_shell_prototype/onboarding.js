const firstProblemButton = document.getElementById("firstProblemButton");
const problemBankButton = document.getElementById("problemBankButton");
const advancedWorkspaceButton = document.getElementById("advancedWorkspaceButton");
const homeButton = document.getElementById("homeButton");

const learningHomeCopy = {
  ko: {
    home: "홈",
    conceptPuzzles: "개념 퍼즐 9개",
    title: "데이터로 직접 확인하며 SQL을 배워보세요.",
    copy: "별도 DB 연결이나 AI 설정 없이 샘플 데이터로 바로 시작할 수 있습니다. 첫 문제를 풀고, 필요할 때 실제 데이터와 고급 기능으로 확장하세요.",
    firstProblem: "첫 문제 시작하기",
    problemBank: "문제 선택",
    advanced: "고급 기능",
    intro: "서비스 소개",
    support: "고객 지원",
    privacy: "개인정보 처리방침",
    step1Title: "1. 문제를 읽고",
    step1Copy: "실제 업무와 비슷한 데이터 질문에서 시작합니다.",
    step2Title: "2. SQL을 실행하고",
    step2Copy: "내장 샘플 DB에서 결과를 바로 확인합니다.",
    step3Title: "3. 피드백을 받기",
    step3Copy: "채점, 힌트, 오답 노트로 다음 문제까지 이어갑니다.",
  },
  en: {
    home: "Home",
    conceptPuzzles: "Concept puzzles (Korean)",
    title: "Learn SQL by checking real data results.",
    copy: "Start immediately with built-in sample data—no database connection or AI setup required. Solve the first problem, then expand into your own data and advanced tools when you need them.",
    firstProblem: "Start first problem",
    problemBank: "Choose a problem",
    advanced: "Advanced tools",
    intro: "About CoQuery",
    support: "Support",
    privacy: "Privacy Policy",
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
      concept: ["SQL을 몰라도 조건·관계·규칙을 직접 비교할 수 있습니다.", ["개념 퍼즐 목록에서 C1 ‘두 조건을 모두 만족하기’를 여세요.", "결과를 먼저 예상하고 카드를 선택한 뒤 실험하세요.", "예상과 실제 결과를 비교하세요. 조건이나 규칙을 바꾸며 반례도 확인하세요.", "‘내 말로 설명하기’에 이유를 쓰고 기록하세요. SQL 학습 홈으로 돌아올 수 있습니다."], "기록은 이 브라우저/기기에만 저장됩니다. 설명 기록은 숙달 평가가 아니며 기기 간 동기화되지 않습니다.", "개념 퍼즐 열기"],
      sql: ["샘플 데이터로 SQL을 실행하고 결과를 확인합니다. DB·AI 설정 없이 시작합니다.", ["SQL 학습을 시작하거나 아직 풀지 않은 문제를 이어서 여세요.", "문제와 힌트를 읽고 테이블 이름을 확인하세요. 첫 문제의 열은 id, name, region입니다.", "SQL을 작성해 ‘실행하고 확인하기’를 누르세요. 오류가 나면 열 이름과 조건을 고쳐 다시 실행하세요.", "정답 여부와 실제 행을 확인하고 표·흐름·해설을 비교한 뒤 다음 문제로 이동하세요."], "정답은 해당 문제의 결과 비교입니다. 학습 효과나 다른 상황에서의 이해를 보장하지 않습니다.", "SQL 학습 시작 / 이어서하기"],
      community: ["질문을 함께 검토하고 이의를 제기하는 과정을 모의 데이터로 체험합니다.", ["모의 질문을 작성하고 사실·의견·창의적 가설 중 성격을 구분하세요. 개인정보는 쓰지 마세요.", "AI 사전 검사와 중립적 표현 제안을 살펴보세요. 실패·대기·취소도 선택할 수 있습니다.", "사람 검토 단계를 거친 뒤 주장·근거·반례·대안을 담아 답하고 요약의 출처를 확인하세요.", "신고와 항소를 체험하세요. 모의 검토자 판단도 실제 제재나 다른 사람에게 전달되지 않습니다."], "실제 AI·서버·다른 참여자와 연결되지 않습니다. 입력은 공개되지 않으며 페이지를 새로 열면 모의 체험이 초기화됩니다.", "참여형 모의 체험 열기"]
    },
    en: {
      summary: "New here? Explore three ways to start", title: "What would you like to try?", paths: ["Understand concepts", "Practice SQL", "Explore community review"], done: "Read · close guide", read: "Guide read. You can reopen it anytime.", unavailable: "Could not save the read marker on this device. The guide is still available.",
      concept: ["Compare conditions, relationships and rules without SQL.", ["Open C1 from the concept puzzle list (Korean content).", "Predict the result, select cards and run an experiment.", "Compare your prediction with the result. Change rules and look for counterexamples.", "Write your own explanation and save it. Return with SQL learning home."], "Notes stay in this browser/device. A saved explanation is not a mastery assessment and does not sync across devices.", "Open concept puzzles"],
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
  byId("learningGuideStart").addEventListener("click", () => byId(path === "sql" ? "firstProblemButton" : "conceptPuzzlesButton").click());
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
