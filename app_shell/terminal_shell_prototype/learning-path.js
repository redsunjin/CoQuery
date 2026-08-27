const learningPathUnits = [
  {
    id: "foundations",
    ko: { title: "1. 데이터 찾기", description: "필요한 열을 선택하고 결과 순서를 정합니다." },
    en: { title: "1. Find data", description: "Select the columns you need and control result order." },
    match: (concepts) => !concepts.includes("where") && !concepts.includes("join") && !concepts.includes("group_by"),
  },
  {
    id: "filtering",
    ko: { title: "2. 조건으로 찾기", description: "WHERE와 조건 조합으로 원하는 데이터만 찾습니다." },
    en: { title: "2. Filter data", description: "Use WHERE and combined conditions to find the rows you need." },
    match: (concepts) => concepts.includes("where") && !concepts.includes("join") && !concepts.includes("group_by"),
  },
  {
    id: "relationships",
    ko: { title: "3. 테이블 연결하기", description: "JOIN으로 서로 다른 테이블의 정보를 연결합니다." },
    en: { title: "3. Connect tables", description: "Use JOIN to connect information across tables." },
    match: (concepts) => concepts.includes("join") && !concepts.includes("group_by"),
  },
  {
    id: "summaries",
    ko: { title: "4. 요약하고 집계하기", description: "GROUP BY, COUNT, SUM으로 업무 질문에 답합니다." },
    en: { title: "4. Summarize data", description: "Use GROUP BY, COUNT, and SUM to answer business questions." },
    match: (concepts) => concepts.includes("group_by") || concepts.includes("count") || concepts.includes("sum"),
  },
];

const learningPathCopy = {
  ko: {
    title: "SQL 기초 학습",
    subtitle: "순서대로 풀어도 되고, 필요한 개념부터 골라도 됩니다.",
    progress: "전체 진행률",
    continue: "이어서 학습하기",
    review: "완료한 문제 복습하기",
    start: "시작하기",
    resume: "계속하기",
    retry: "다시 풀기",
    completed: "완료",
    inProgress: "진행 중",
    notStarted: "시작 전",
    all: "전체",
    incomplete: "미완료",
    done: "완료",
    attempts: "회 시도",
    problems: "문제",
    fallbackTitle: "추가 연습",
    fallbackDescription: "새로 추가된 문제를 연습합니다.",
    homeContinue: "이어서 학습하기",
    homeReview: "복습 시작하기",
  },
  en: {
    title: "SQL Basics Path",
    subtitle: "Follow the path in order or jump to the concept you need.",
    progress: "Overall progress",
    continue: "Continue learning",
    review: "Review completed problems",
    start: "Start",
    resume: "Continue",
    retry: "Try again",
    completed: "Completed",
    inProgress: "In progress",
    notStarted: "Not started",
    all: "All",
    incomplete: "Incomplete",
    done: "Completed",
    attempts: " attempts",
    problems: "problems",
    fallbackTitle: "More practice",
    fallbackDescription: "Practice newly added problems.",
    homeContinue: "Continue learning",
    homeReview: "Start review",
  },
};

let learningPathSnapshot = null;
let learningPathFilter = "all";

function learningPathLanguage() {
  return document.documentElement.lang === "en" ? "en" : "ko";
}

function learningPathText(key) {
  const lang = learningPathLanguage();
  return learningPathCopy[lang]?.[key] || learningPathCopy.en[key] || key;
}

function learningPathEscape(value) {
  if (typeof escapeHtml === "function") {
    return escapeHtml(value);
  }
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function learningPathCommand(block) {
  return block?.__result?.command || block?.querySelector(".block-command code")?.textContent?.trim() || "";
}

function learningPathProblemState(problemId, attempts) {
  const matches = attempts.filter((attempt) => attempt.problem_id === problemId);
  const completed = matches.some((attempt) => attempt.correct === true);
  return {
    completed,
    attempted: matches.length > 0,
    attemptCount: matches.length,
    lastAttempt: matches.at(-1) || null,
    status: completed ? "completed" : matches.length ? "in_progress" : "not_started",
  };
}

function buildLearningPathSnapshot(problems, attempts, packId = "sql_basics") {
  const states = new Map();
  problems.forEach((problem) => states.set(problem.id, learningPathProblemState(problem.id, attempts)));

  const units = learningPathUnits.map((unit) => ({ ...unit, problems: [] }));
  const fallback = {
    id: "more",
    ko: { title: learningPathCopy.ko.fallbackTitle, description: learningPathCopy.ko.fallbackDescription },
    en: { title: learningPathCopy.en.fallbackTitle, description: learningPathCopy.en.fallbackDescription },
    problems: [],
  };

  problems.forEach((problem, index) => {
    const concepts = Array.isArray(problem.concepts) ? problem.concepts : [];
    const unit = units.find((candidate) => candidate.match?.(concepts)) || fallback;
    unit.problems.push({ ...problem, originalIndex: index, progress: states.get(problem.id) });
  });

  const visibleUnits = units.filter((unit) => unit.problems.length);
  if (fallback.problems.length) {
    visibleUnits.push(fallback);
  }

  visibleUnits.forEach((unit) => {
    unit.completedCount = unit.problems.filter((problem) => problem.progress.completed).length;
    unit.attemptedCount = unit.problems.filter((problem) => problem.progress.attempted).length;
    unit.percent = unit.problems.length ? Math.round((unit.completedCount / unit.problems.length) * 100) : 0;
  });

  const completedCount = problems.filter((problem) => states.get(problem.id)?.completed).length;
  const attemptedCount = problems.filter((problem) => states.get(problem.id)?.attempted).length;
  const nextProblem = problems.find((problem) => !states.get(problem.id)?.completed) || problems[0] || null;

  return {
    packId,
    problems,
    attempts,
    units: visibleUnits,
    completedCount,
    attemptedCount,
    totalCount: problems.length,
    percent: problems.length ? Math.round((completedCount / problems.length) * 100) : 0,
    nextProblem,
    allCompleted: problems.length > 0 && completedCount === problems.length,
  };
}

async function fetchLearningPathSnapshot(listResult = null) {
  const list = listResult || (await postCommand("practice_list", {}, { mode: "training" }));
  if (!list?.ok) {
    return null;
  }
  const packId = list.data?.selected_pack || "sql_basics";
  let attempts = [];
  try {
    const attemptResult = await postCommand("practice_attempts", { pack: packId, limit: 500 }, { mode: "training" });
    if (attemptResult?.ok) {
      attempts = attemptResult.data?.attempts || [];
    }
  } catch {
    attempts = [];
  }
  return buildLearningPathSnapshot(list.data?.problems || [], attempts, packId);
}

function statusCopy(status) {
  return status === "completed"
    ? learningPathText("completed")
    : status === "in_progress"
      ? learningPathText("inProgress")
      : learningPathText("notStarted");
}

function problemActionCopy(progress) {
  if (progress.completed) return learningPathText("retry");
  if (progress.attempted) return learningPathText("resume");
  return learningPathText("start");
}

function renderLearningPathProblem(problem, packId) {
  const concepts = (problem.concepts || [])
    .map((concept) => `<span class="learning-concept">${learningPathEscape(concept)}</span>`)
    .join("");
  const progress = problem.progress;
  const attempts = progress.attemptCount
    ? `<span class="learning-attempt-count">${learningPathEscape(progress.attemptCount)}${learningPathEscape(learningPathText("attempts"))}</span>`
    : "";
  return `<article class="learning-problem-card" data-learning-problem data-status="${learningPathEscape(progress.status)}"
      data-problem-id="${learningPathEscape(problem.id)}" data-pack-id="${learningPathEscape(packId)}">
      <div class="learning-problem-main">
        <div class="learning-problem-meta">
          <span class="learning-status" data-status="${learningPathEscape(progress.status)}">${learningPathEscape(statusCopy(progress.status))}</span>
          <span class="learning-difficulty">${learningPathEscape(problem.difficulty || "practice")}</span>
          ${attempts}
        </div>
        <h4>${learningPathEscape(problem.title || problem.id)}</h4>
        <p>${learningPathEscape(problem.prompt || "")}</p>
        <div class="learning-concepts">${concepts}</div>
      </div>
      <button class="${progress.completed ? "ghost-button" : "primary-button"} learning-problem-start" type="button">
        ${learningPathEscape(problemActionCopy(progress))}
      </button>
    </article>`;
}

function renderLearningPathUnit(unit, packId) {
  const lang = learningPathLanguage();
  const copy = unit[lang] || unit.en || unit.ko || {};
  const problems = unit.problems.map((problem) => renderLearningPathProblem(problem, packId)).join("");
  return `<section class="learning-unit" data-learning-unit>
      <div class="learning-unit-head">
        <div>
          <h3>${learningPathEscape(copy.title || unit.id)}</h3>
          <p>${learningPathEscape(copy.description || "")}</p>
        </div>
        <div class="learning-unit-progress">
          <strong>${learningPathEscape(unit.completedCount)} / ${learningPathEscape(unit.problems.length)}</strong>
          <span>${learningPathEscape(unit.percent)}%</span>
        </div>
      </div>
      <div class="learning-unit-bar" aria-hidden="true"><span style="width:${unit.percent}%"></span></div>
      <div class="learning-problem-list">${problems}</div>
    </section>`;
}

function bindLearningPathBlock(block, snapshot) {
  block.querySelectorAll("[data-learning-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      learningPathFilter = button.dataset.learningFilter || "all";
      applyLearningPathFilter(block);
    });
  });

  block.querySelector("[data-learning-continue]")?.addEventListener("click", () => {
    if (snapshot.nextProblem) {
      startProblemFromLearningPath(snapshot.nextProblem, snapshot.packId);
    }
  });

  block.querySelectorAll("[data-learning-problem]").forEach((card) => {
    card.querySelector(".learning-problem-start")?.addEventListener("click", () => {
      const problem = snapshot.problems.find((item) => item.id === card.dataset.problemId);
      if (problem) {
        startProblemFromLearningPath(problem, card.dataset.packId || snapshot.packId);
      }
    });
  });

  applyLearningPathFilter(block);
}

function applyLearningPathFilter(block) {
  block.querySelectorAll("[data-learning-filter]").forEach((button) => {
    button.classList.toggle("active", button.dataset.learningFilter === learningPathFilter);
  });
  block.querySelectorAll("[data-learning-problem]").forEach((card) => {
    const status = card.dataset.status;
    const visible =
      learningPathFilter === "all" ||
      (learningPathFilter === "completed" && status === "completed") ||
      (learningPathFilter === "incomplete" && status !== "completed");
    card.hidden = !visible;
  });
  block.querySelectorAll("[data-learning-unit]").forEach((unit) => {
    unit.hidden = !unit.querySelector("[data-learning-problem]:not([hidden])");
  });
}

function startProblemFromLearningPath(problem, packId) {
  if (appShell) {
    appShell.dataset.learningPath = "false";
  }
  addBlock(practiceStartResult(problem, packId || "sql_basics"));
}

function updateLearningHomeProgress(snapshot) {
  const home = document.querySelector(".learning-home-inner");
  if (!home || !snapshot) return;
  let progress = home.querySelector("[data-home-progress]");
  if (!progress) {
    progress = document.createElement("div");
    progress.className = "learning-home-progress";
    progress.dataset.homeProgress = "true";
    const actions = home.querySelector(".learning-home-actions");
    actions?.insertAdjacentElement("afterend", progress);
  }
  progress.innerHTML = `<span>${learningPathEscape(learningPathText("progress"))}</span>
    <strong>${learningPathEscape(snapshot.completedCount)} / ${learningPathEscape(snapshot.totalCount)}</strong>
    <div class="learning-home-progress-bar" aria-hidden="true"><span style="width:${snapshot.percent}%"></span></div>`;

  if (firstProblemButton) {
    if (snapshot.allCompleted) {
      firstProblemButton.textContent = learningPathText("homeReview");
    } else if (snapshot.attemptedCount > 0) {
      firstProblemButton.textContent = learningPathText("homeContinue");
    }
  }
}

async function renderLearningPathBlock(block, listResult = null) {
  if (!block) return;
  const result = listResult || block.__result;
  const snapshot = await fetchLearningPathSnapshot(result);
  if (!snapshot) return;
  learningPathSnapshot = snapshot;
  block.classList.add("learning-path-block");

  const continueLabel = snapshot.allCompleted ? learningPathText("review") : learningPathText("continue");
  const units = snapshot.units.map((unit) => renderLearningPathUnit(unit, snapshot.packId)).join("");
  block.innerHTML = `<div class="learning-path-header">
      <div>
        <p class="learning-path-kicker">LEARNING PATH</p>
        <h2>${learningPathEscape(learningPathText("title"))}</h2>
        <p>${learningPathEscape(learningPathText("subtitle"))}</p>
      </div>
      <div class="learning-path-total">
        <span>${learningPathEscape(learningPathText("progress"))}</span>
        <strong>${learningPathEscape(snapshot.percent)}%</strong>
        <small>${learningPathEscape(snapshot.completedCount)} / ${learningPathEscape(snapshot.totalCount)}</small>
      </div>
    </div>
    <div class="learning-path-bar" aria-hidden="true"><span style="width:${snapshot.percent}%"></span></div>
    <div class="learning-path-actions">
      <button class="primary-button" type="button" data-learning-continue>${learningPathEscape(continueLabel)}</button>
      <div class="learning-filter-group" role="group" aria-label="Problem filter">
        <button class="ghost-button active" type="button" data-learning-filter="all">${learningPathEscape(learningPathText("all"))}</button>
        <button class="ghost-button" type="button" data-learning-filter="incomplete">${learningPathEscape(learningPathText("incomplete"))}</button>
        <button class="ghost-button" type="button" data-learning-filter="completed">${learningPathEscape(learningPathText("done"))}</button>
      </div>
    </div>
    <div class="learning-units">${units}</div>`;
  bindLearningPathBlock(block, snapshot);
  updateLearningHomeProgress(snapshot);
}

function findLearningPathBlock() {
  return [...document.querySelectorAll("#terminalScroll .terminal-block")]
    .reverse()
    .find((block) => learningPathCommand(block) === "practice_list");
}

async function refreshLearningPath() {
  const block = findLearningPathBlock();
  if (block) {
    await renderLearningPathBlock(block, block.__result);
    return block;
  }
  const result = await postCommand("practice_list", {}, { mode: "training" });
  addBlock(result);
  return findLearningPathBlock();
}

function setLearningPathMode(enabled) {
  if (!appShell) return;
  appShell.dataset.learningPath = enabled ? "true" : "false";
}

const learningPathObserver = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (!(node instanceof HTMLElement) || !node.matches(".terminal-block")) return;
      const command = learningPathCommand(node);
      if (command === "practice_list") {
        renderLearningPathBlock(node, node.__result);
      }
      if (command === "practice_grade") {
        setTimeout(() => refreshLearningPath(), 0);
      }
    });
  });
});

if (terminalScroll) {
  learningPathObserver.observe(terminalScroll, { childList: true });
  terminalScroll.querySelectorAll(".terminal-block").forEach((block) => {
    if (learningPathCommand(block) === "practice_list") renderLearningPathBlock(block, block.__result);
  });
}

problemBankButton?.addEventListener("click", () => {
  setLearningPathMode(true);
  setTimeout(async () => {
    const block = await refreshLearningPath();
    block?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 0);
});

firstProblemButton?.addEventListener("click", () => setLearningPathMode(false));
homeButton?.addEventListener("click", () => setLearningPathMode(false));
advancedWorkspaceButton?.addEventListener("click", () => setLearningPathMode(false));

languageButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setTimeout(() => {
      const block = findLearningPathBlock();
      if (block) renderLearningPathBlock(block, block.__result);
      if (learningPathSnapshot) updateLearningHomeProgress(learningPathSnapshot);
    }, 0);
  });
});