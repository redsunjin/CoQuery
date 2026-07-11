const appShell = document.querySelector(".app-shell");
const terminalScroll = document.getElementById("terminalScroll");
const commandForm = document.getElementById("commandForm");
const commandInput = document.getElementById("commandInput");
const detailTitle = document.getElementById("detailTitle");
const detailCli = document.getElementById("detailCli");
const detailJson = document.getElementById("detailJson");
const detailActions = document.getElementById("detailActions");
const detailHelp = document.getElementById("detailHelp");
const sessionList = document.getElementById("sessionList");
const drawerButton = document.getElementById("drawerButton");
const commandMenuToggle = document.getElementById("commandMenuToggle");
const commandMenuPanel = document.getElementById("commandMenuPanel");
const providerStatus = document.getElementById("providerStatus");
const modeToggle = document.getElementById("modeToggle");
const detailToggle = document.getElementById("detailToggle");
const closeDetail = document.getElementById("closeDetail");
const languageButtons = document.querySelectorAll("[data-lang]");
const modeButtons = document.querySelectorAll("[data-mode-option]");

let selectedBlock = null;
let selectedResult = null;
let providerPresets = [];
let helpCatalog = null;
let selectedProviderName = localStorage.getItem("coquery_selected_provider") || "";
const savedAppMode = localStorage.getItem("coquery_app_mode");
let currentAppMode = savedAppMode === "production_assist" ? "production_assist" : "training";
const savedLanguage = localStorage.getItem("coquery_language");
let currentLanguage = savedLanguage === "en" ? "en" : "ko";
const renderedBlocks = [];

const providerDefaults = {
  deepseek: { providerName: "deepseek_mobile", modelName: "deepseek-v4-flash", apiKeyEnv: "DEEPSEEK_API_KEY" },
  gemini: { providerName: "gemini_flash", modelName: "gemini-3.5-flash", apiKeyEnv: "GEMINI_API_KEY" },
  groq: { providerName: "fast_groq", modelName: "llama-3.1-8b-instant", apiKeyEnv: "GROQ_API_KEY" },
  openai: { providerName: "openai_main", modelName: "gpt-4o-mini", apiKeyEnv: "OPENAI_API_KEY" },
  openrouter: { providerName: "openrouter_cheap", modelName: "openai/gpt-4o-mini", apiKeyEnv: "OPENROUTER_API_KEY" },
};

const i18n = {
  ko: {
    documentTitle: "CoQuery",
    sessionRailLabel: "세션",
    sessionListLabel: "세션 목록",
    searchPlaceholder: "세션 검색...",
    brandSubtitle: "터미널 쉘",
    headerKicker: "로컬 SQL 랩",
    appTitle: "CoQuery",
    detailsButton: "상세",
    commandMenuButton: "명령",
    languageToggleLabel: "언어",
    appModeLabel: "작업 모드",
    modeTrainingShort: "Training",
    modeProductionShort: "Assist",
    modeTrainingSummary: "Training Mode: 샘플 데이터와 저비용 AI 제공자 사용",
    modeProductionSummary: "Production Assist Mode: 외부 AI 제공자 기본 차단",
    modeBoundaryBlocked: "Production Assist에서는 정책 승인 없이 외부 AI 제공자를 사용할 수 없습니다.",
    contextLabel: "작업 메뉴",
    chipPresets: "프리셋",
    chipSetupAi: "AI 설정",
    chipSchema: "스키마",
    chipNatural: "자연어",
    chipPractice: "연습",
    chipProduction: "운영 검토",
    chipHelp: "도움말",
    chipTerms: "용어",
    terminalHistoryLabel: "터미널 명령 기록",
    welcomeCopy: "CLI 흐름은 유지하면서 휴대폰, 태블릿, 넓은 화면에서 같은 기능을 사용할 수 있게 합니다. 모든 화면 작업은 동일한 CLI 명령을 함께 보여줍니다.",
    readySummary:
      "Command API 연결 완료. <code>provider_list_presets</code>, <code>provider_setup</code>, <code>schema_detail users</code>, <code>natural show users</code>를 실행해 보세요. DB 없이 연습하려면 <code>practice_list</code>를 사용합니다.",
    commandInputLabel: "명령 입력",
    runButton: "실행",
    panelButton: "패널",
    commandDetailsLabel: "명령 상세",
    detailKicker: "명령 상세",
    noBlockSelected: "선택된 블록 없음",
    closeButton: "닫기",
    cliEquivalentLabel: "CLI 등가 명령",
    cliEquivalentEmpty: "명령을 실행하면 동일한 CLI 호출을 확인할 수 있습니다.",
    actionsLabel: "작업",
    beginnerGuideLabel: "초보자 안내",
    beginnerGuideEmpty: "명령 블록을 선택하면 쉬운 설명이 표시됩니다.",
    structuredOutputLabel: "구조화 출력",
    commandFailed: "명령 실패",
    availablePresets: "저렴한 API/LLM 제공자 프리셋입니다.",
    choosePreset: "저렴한 제공자 프리셋을 고르고, 모델과 환경변수 이름을 확인한 뒤 저장합니다.",
    preset: "프리셋",
    providerName: "제공자 이름",
    model: "모델",
    apiKeyEnv: "API 키 환경변수",
    saveProvider: "제공자 저장",
    showSaved: "저장 목록",
    savingProvider: "제공자 프로필 저장 중...",
    savedProviderStatus: "저장 완료. 이제 자연어 질의에서 이 제공자 프로필을 사용할 수 있습니다.",
    savedProvider: "저장된 제공자",
    savedProviders: "저장된 제공자 프로필입니다.",
    noProviders: "저장된 제공자 없음",
    useSetupAi: "AI 설정을 먼저 사용하세요",
    providerStatusNoProvider: "AI 제공자 선택 안 됨",
    providerStatusSelected: "선택된 AI 제공자",
    providerStatusReady: "연결 준비됨",
    providerStatusNeedsSetup: "설정 확인 필요",
    providerSelect: "선택",
    providerTest: "테스트",
    providerRemove: "삭제",
    providerSelectedSummary: "자연어/AI 요청에 사용할 제공자를 선택했습니다.",
    providerRemoved: "제공자를 삭제했습니다.",
    providerTestPassed: "제공자 테스트 통과",
    providerTestFailed: "제공자 테스트 필요",
    nextStep: "다음 단계",
    responsePreview: "응답 미리보기",
    schemaDetailFor: "스키마 상세",
    mode: "모드",
    noSqlReturned: "반환된 SQL 없음",
    practiceProblems: "DB 없이 사용하는 연습 문제입니다.",
    practiceSchema: "연습 데이터셋 구조입니다.",
    returnedRows: "연습 행 반환",
    practiceAnswer: "연습 답안",
    practiceStart: "연습 시작",
    practiceOpenProblem: "문제 열기",
    practiceInspectSchema: "스키마 보기",
    practiceShowAttempts: "시도 보기",
    practiceProblemPrompt: "문제",
    practiceHint: "힌트",
    practiceSqlLabel: "SQL 입력",
    practiceSqlPlaceholder: "SELECT 문을 입력하세요",
    practiceSubmit: "실행 및 채점",
    practiceRunning: "연습 쿼리 실행 중...",
    practiceFlowSummary: "스키마를 확인하고 SQL을 입력한 뒤 실행 및 채점을 누르세요.",
    practiceAttemptRecorded: "시도 기록 저장됨",
    practiceAttempts: "최근 연습 시도",
    practiceNoAttempts: "저장된 시도 없음",
    wrongNotes: "오답 노트",
    expectedIssue: "예상 문제",
    staticFeedback: "정적 피드백",
    retryPractice: "다시 풀기",
    aiFeedback: "AI 생성 피드백",
    requestAiFeedback: "AI 피드백 요청",
    trainingModeOnly: "Training Mode 전용",
    submittedSql: "제출 SQL",
    actualRows: "실제 행",
    expectedRows: "예상 행",
    correct: "정답",
    needsReview: "복습 필요",
    productionProfileSummary: "운영 Assist 읽기 전용 프로필입니다.",
    productionReviewSummary: "운영 SQL 리뷰 블록입니다.",
    productionApprovalRequired: "실행 전 승인이 필요합니다.",
    productionApproved: "승인됨",
    productionRunReviewed: "검토된 SQL 실행",
    productionApproveSql: "SQL 승인",
    productionAuditLog: "감사 로그",
    productionRows: "반환 행",
    productionSelectOnly: "SELECT 전용",
    commandCompleted: "명령 완료",
    useButton: "사용",
    helpCatalogSummary: "기능 안내와 SQL 용어를 한영으로 볼 수 있습니다.",
    commandsLabel: "명령어",
    termsLabel: "용어",
    commandExample: "예시",
    relatedTerms: "관련 용어",
    sessionLocalTitle: "로컬 SQL 랩",
    sessionLocalSubtitle: "Command API 준비됨",
    sessionProviderTitle: "제공자 설정",
    sessionProviderSubtitle: "프리셋과 모델 점검",
    sessionPracticeTitle: "연습 흐름",
    sessionPracticeSubtitle: "복습과 오답노트 경로",
  },
  en: {
    documentTitle: "CoQuery",
    sessionRailLabel: "Sessions",
    sessionListLabel: "Session list",
    searchPlaceholder: "Search sessions...",
    brandSubtitle: "Terminal Shell",
    headerKicker: "Local SQL Lab",
    appTitle: "CoQuery",
    detailsButton: "Details",
    commandMenuButton: "Commands",
    languageToggleLabel: "Language",
    appModeLabel: "Work mode",
    modeTrainingShort: "Training",
    modeProductionShort: "Assist",
    modeTrainingSummary: "Training Mode: sample datasets and low-cost AI providers",
    modeProductionSummary: "Production Assist Mode: external AI providers blocked by default",
    modeBoundaryBlocked: "Production Assist blocks external AI providers unless policy explicitly overrides it.",
    contextLabel: "Context",
    chipPresets: "Presets",
    chipSetupAi: "Setup AI",
    chipSchema: "Schema",
    chipNatural: "Natural",
    chipPractice: "Practice",
    chipProduction: "Prod Review",
    chipHelp: "Help",
    chipTerms: "Terms",
    terminalHistoryLabel: "Terminal command history",
    welcomeCopy: "Keep the CLI surface intact, but make it usable from phone, tablet, and wide screens. Every UI action shows the CLI equivalent.",
    readySummary:
      "Command API connected. Try <code>provider_list_presets</code>, <code>provider_setup</code>, <code>schema_detail users</code>, or <code>natural show users</code>. Use <code>practice_list</code> for DB-free SQL practice.",
    commandInputLabel: "Command input",
    runButton: "Run",
    panelButton: "Panel",
    commandDetailsLabel: "Command details",
    detailKicker: "Command Detail",
    noBlockSelected: "No block selected",
    closeButton: "Close",
    cliEquivalentLabel: "CLI Equivalent",
    cliEquivalentEmpty: "Run a command to inspect the exact CLI call.",
    actionsLabel: "Actions",
    beginnerGuideLabel: "Beginner Guide",
    beginnerGuideEmpty: "Select a command block to see a plain-language explanation.",
    structuredOutputLabel: "Structured Output",
    commandFailed: "Command failed",
    availablePresets: "Available low-cost/API presets.",
    choosePreset: "Choose a low-cost provider preset, confirm the model/env label, then save it through the Command API.",
    preset: "Preset",
    providerName: "Provider name",
    model: "Model",
    apiKeyEnv: "API key env",
    saveProvider: "Save provider",
    showSaved: "Show saved",
    savingProvider: "Saving provider profile...",
    savedProviderStatus: "Saved. The provider profile is now available to natural queries.",
    savedProvider: "Saved provider",
    savedProviders: "Saved provider profiles.",
    noProviders: "No providers",
    useSetupAi: "Use Setup AI first",
    providerStatusNoProvider: "No AI provider selected",
    providerStatusSelected: "Selected AI provider",
    providerStatusReady: "Connection ready",
    providerStatusNeedsSetup: "Setup needs attention",
    providerSelect: "Select",
    providerTest: "Test",
    providerRemove: "Remove",
    providerSelectedSummary: "Selected provider for natural-language and AI requests.",
    providerRemoved: "Provider removed.",
    providerTestPassed: "Provider test passed",
    providerTestFailed: "Provider test needs attention",
    nextStep: "Next step",
    responsePreview: "Response preview",
    schemaDetailFor: "Schema detail for",
    mode: "Mode",
    noSqlReturned: "No SQL returned",
    practiceProblems: "DB-free practice problems from",
    practiceSchema: "Practice dataset schema.",
    returnedRows: "Returned practice rows",
    practiceAnswer: "Practice answer",
    practiceStart: "Start practice",
    practiceOpenProblem: "Open problem",
    practiceInspectSchema: "Inspect schema",
    practiceShowAttempts: "Show attempts",
    practiceProblemPrompt: "Problem",
    practiceHint: "Hint",
    practiceSqlLabel: "SQL input",
    practiceSqlPlaceholder: "Type a SELECT statement",
    practiceSubmit: "Run and grade",
    practiceRunning: "Running practice query...",
    practiceFlowSummary: "Inspect the schema, type SQL, then run and grade it.",
    practiceAttemptRecorded: "Attempt recorded",
    practiceAttempts: "Recent practice attempts",
    practiceNoAttempts: "No attempts saved",
    wrongNotes: "Wrong notes",
    expectedIssue: "Expected issue",
    staticFeedback: "Static feedback",
    retryPractice: "Retry",
    aiFeedback: "AI-generated feedback",
    requestAiFeedback: "Request AI feedback",
    trainingModeOnly: "Training Mode only",
    submittedSql: "Submitted SQL",
    actualRows: "Actual rows",
    expectedRows: "Expected rows",
    correct: "correct",
    needsReview: "needs review",
    productionProfileSummary: "Production Assist read-only profile.",
    productionReviewSummary: "Production SQL review block.",
    productionApprovalRequired: "Approval is required before execution.",
    productionApproved: "Approved",
    productionRunReviewed: "Run reviewed SQL",
    productionApproveSql: "Approve SQL",
    productionAuditLog: "Audit log",
    productionRows: "Returned rows",
    productionSelectOnly: "SELECT-only",
    commandCompleted: "Command completed",
    useButton: "Use",
    helpCatalogSummary: "Feature guidance and SQL terms are available in Korean and English.",
    commandsLabel: "Commands",
    termsLabel: "Terms",
    commandExample: "Example",
    relatedTerms: "Related terms",
    sessionLocalTitle: "Local SQL Lab",
    sessionLocalSubtitle: "Command API ready",
    sessionProviderTitle: "Provider setup",
    sessionProviderSubtitle: "Presets and model checks",
    sessionPracticeTitle: "Practice flow",
    sessionPracticeSubtitle: "Review and wrong-note path",
  },
};

const actionLabels = {
  ko: {
    copy: "복사",
    explain: "설명",
    retry: "다시 실행",
    export: "내보내기",
    copy_sql: "SQL 복사",
    run_query: "조회 실행",
    review: "검토",
    save_as_practice: "연습 저장",
    run_again: "다시 실행",
    review_safety: "안전 검토",
    start_practice: "연습 시작",
    show_schema: "구조 보기",
    grade: "채점",
    save_attempt: "시도 저장",
    save_wrong_note: "오답 저장",
    review_wrong_notes: "오답 보기",
    request_provider_feedback: "AI 피드백",
    select_provider: "제공자 선택",
    add_provider: "제공자 추가",
    test_provider: "연결 테스트",
    use_provider: "사용",
    remove_provider: "삭제",
    select_preset: "프리셋 선택",
    save_provider: "제공자 저장",
    copy_cli: "CLI 복사",
    explain_command: "명령 설명",
    explain_term: "용어 설명",
    insert_example: "예시 입력",
    show_terms: "용어 보기",
    show_related_commands: "관련 명령",
    insert_template: "템플릿 입력",
    approve: "승인",
    execute: "실행",
    audit: "감사",
  },
  en: {
    copy: "Copy",
    explain: "Explain",
    retry: "Retry",
    export: "Export",
    copy_sql: "Copy SQL",
    run_query: "Run query",
    review: "Review",
    save_as_practice: "Save as practice",
    run_again: "Run again",
    review_safety: "Review safety",
    start_practice: "Start practice",
    show_schema: "Show schema",
    grade: "Grade",
    save_attempt: "Save attempt",
    save_wrong_note: "Save wrong note",
    review_wrong_notes: "Review wrong notes",
    request_provider_feedback: "AI feedback",
    select_provider: "Select provider",
    add_provider: "Add provider",
    test_provider: "Test provider",
    use_provider: "Use provider",
    remove_provider: "Remove",
    select_preset: "Select preset",
    save_provider: "Save provider",
    copy_cli: "Copy CLI",
    explain_command: "Explain command",
    explain_term: "Explain term",
    insert_example: "Insert example",
    show_terms: "Show terms",
    show_related_commands: "Related commands",
    insert_template: "Insert template",
    approve: "Approve",
    execute: "Execute",
    audit: "Audit",
  },
};

function t(key) {
  return i18n[currentLanguage]?.[key] || i18n.en[key] || key;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function quoteCliValue(value) {
  const text = String(value || "");
  if (!text) {
    return '""';
  }
  if (/^[A-Za-z0-9._\-/:@]+$/.test(text)) {
    return text;
  }
  return `"${text.replaceAll("\\", "\\\\").replaceAll('"', '\\"')}"`;
}

function actionLabel(action) {
  return actionLabels[currentLanguage]?.[action] || action;
}

function normalizeAppMode(mode) {
  return mode === "production_assist" ? "production_assist" : "training";
}

function modeLabel(mode = currentAppMode) {
  return normalizeAppMode(mode) === "production_assist" ? t("modeProductionShort") : t("modeTrainingShort");
}

function modeSummary(mode = currentAppMode) {
  return normalizeAppMode(mode) === "production_assist" ? t("modeProductionSummary") : t("modeTrainingSummary");
}

function resultModeLabel(result = {}) {
  return modeLabel(result.mode_context?.mode || result.data?.mode_context?.mode || currentAppMode);
}

function modeContext(extra = {}) {
  return {
    mode: currentAppMode,
    allow_external_provider: false,
    ...extra,
  };
}

function applyModeIndicator() {
  document.documentElement.dataset.appMode = currentAppMode;
  modeButtons.forEach((button) => {
    const isActive = normalizeAppMode(button.dataset.modeOption) === currentAppMode;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-pressed", isActive ? "true" : "false");
    button.title = modeSummary(button.dataset.modeOption);
  });
  if (modeToggle) {
    modeToggle.setAttribute("aria-label", `${t("appModeLabel")}: ${modeLabel()}`);
  }
}

function applyStaticTranslations() {
  document.documentElement.lang = currentLanguage;
  document.title = t("documentTitle");
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((node) => {
    node.innerHTML = t(node.dataset.i18nHtml);
  });
  document.querySelectorAll("[data-i18n-attr]").forEach((node) => {
    node.dataset.i18nAttr.split(";").forEach((item) => {
      const [attribute, key] = item.split(":");
      if (attribute && key) {
        node.setAttribute(attribute, t(key));
      }
    });
  });
  languageButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.lang === currentLanguage);
  });
  applyModeIndicator();
  updateProviderReadinessStatus();
}

function setCommandMenuOpen(open) {
  if (!commandMenuToggle || !commandMenuPanel) {
    return;
  }
  commandMenuToggle.setAttribute("aria-expanded", open ? "true" : "false");
  commandMenuPanel.hidden = !open;
}

function updateProviderReadinessStatus(providerName = selectedProviderName, state = "selected", detail = "") {
  if (!providerStatus) {
    return;
  }
  const summary = providerStatus.querySelector("[data-provider-status-summary]");
  providerStatus.dataset.state = providerName ? state : "none";
  providerStatus.dataset.providerName = providerName || "";
  providerStatus.dataset.mode = currentAppMode;
  const prefix = modeLabel();
  if (summary) {
    if (!providerName) {
      summary.textContent = `${prefix} · ${t("providerStatusNoProvider")}`;
    } else {
      const stateLabel =
        state === "ready" ? t("providerStatusReady") : state === "error" ? t("providerStatusNeedsSetup") : t("providerStatusSelected");
      const boundary = currentAppMode === "production_assist" ? ` · ${t("modeBoundaryBlocked")}` : "";
      summary.textContent = `${prefix} · ${stateLabel}: ${providerName}${detail ? ` · ${detail}` : ""}${boundary}`;
    }
  }
}

function selectProvider(providerName, state = "selected", detail = "") {
  selectedProviderName = providerName || "";
  if (selectedProviderName) {
    localStorage.setItem("coquery_selected_provider", selectedProviderName);
  } else {
    localStorage.removeItem("coquery_selected_provider");
  }
  updateProviderReadinessStatus(selectedProviderName, state, detail);
}

function providerDefaultsFor(presetName) {
  const preset = providerPresets.find((item) => item.name === presetName) || {};
  const fallback = providerDefaults[presetName] || providerDefaults.gemini;
  return {
    providerName: fallback.providerName || `${presetName}_mobile`,
    modelName: preset.default_model || fallback.modelName || "",
    apiKeyEnv: preset.api_key_env || fallback.apiKeyEnv || "",
  };
}

function providerCliEquivalent(values) {
  const parts = [
    "python",
    "main.py",
    "--command",
    "provider_add_preset",
    "--preset",
    quoteCliValue(values.preset),
    "--provider-name",
    quoteCliValue(values.providerName),
  ];
  if (values.modelName) {
    parts.push("--model-name", quoteCliValue(values.modelName));
  }
  if (values.apiKeyEnv) {
    parts.push("--api-key-env", quoteCliValue(values.apiKeyEnv));
  }
  parts.push("--format", "json");
  return parts.join(" ");
}

function providerSetupResult(presetName = "gemini") {
  const defaults = providerDefaultsFor(presetName);
  const values = {
    preset: presetName,
    providerName: defaults.providerName,
    modelName: defaults.modelName,
    apiKeyEnv: defaults.apiKeyEnv,
  };
  return {
    ok: true,
    command: "provider_setup",
    block_type: "provider_setup",
    actions: ["select_preset", "save_provider", "copy_cli"],
    cli_equivalent: providerCliEquivalent(values),
    data: { values, presets: providerPresets },
    error: null,
  };
}

function providerSelectCliEquivalent(providerName) {
  return [
    "python",
    "main.py",
    "--command",
    "natural",
    "--db",
    "example.db",
    "--sql",
    quoteCliValue("show users"),
    "--provider-name",
    quoteCliValue(providerName || "provider_name"),
    "--mode",
    currentAppMode,
    "--format",
    "json",
  ].join(" ");
}

function providerSelectResult(provider = {}) {
  const providerName = provider.name || selectedProviderName || "";
  return {
    ok: true,
    command: "provider_select",
    block_type: "provider_status",
    actions: ["copy", "select_provider", "test_provider"],
    cli_equivalent: providerSelectCliEquivalent(providerName),
    data: { provider, mode_context: modeContext() },
    mode_context: modeContext(),
    error: null,
  };
}

function practiceCliEquivalent(problemId, sql = "", packId = "sql_basics") {
  const parts = [
    "python",
    "main.py",
    "--command",
    "practice_grade",
    "--problem-id",
    quoteCliValue(problemId || "basic_select_customers"),
    "--sql",
    quoteCliValue(sql || "SELECT ..."),
  ];
  if (packId && packId !== "sql_basics") {
    parts.push("--pack", quoteCliValue(packId));
  }
  parts.push("--mode", "training");
  parts.push("--format", "json");
  return parts.join(" ");
}

function practiceStartResult(problem = {}, packId = "sql_basics", initialSql = "") {
  const problemId = problem.id || "basic_select_customers";
  const values = {
    packId,
    initialSql,
    problem: {
      id: problemId,
      title: problem.title || problemId,
      difficulty: problem.difficulty || "practice",
      prompt: problem.prompt || t("practiceProblemPrompt"),
      concepts: Array.isArray(problem.concepts) ? problem.concepts : [],
      hint: problem.hint || "",
    },
  };
  return {
    ok: true,
    command: "practice_start",
    block_type: "practice_flow",
    actions: ["show_schema", "grade", "save_attempt", "review_wrong_notes"],
    cli_equivalent: practiceCliEquivalent(problemId, initialSql, packId),
    data: values,
    error: null,
  };
}

function practiceProblemFromWrongNote(note = {}) {
  return {
    id: note.problem_id || "basic_select_customers",
    title: note.problem_title || note.problem_id || "Practice",
    difficulty: note.difficulty || "practice",
    prompt: note.prompt || "",
    concepts: Array.isArray(note.concepts) ? note.concepts : [],
    hint: note.hint || "",
  };
}

function wrongNoteCard(note = {}, index = 0) {
  const retryAction = note.retry_action || {};
  const staticFeedback = note.static_feedback || {};
  const providerFeedback = note.provider_feedback || {};
  const packId = retryAction.pack_id || note.pack_id || "sql_basics";
  const problemId = retryAction.problem_id || note.problem_id || "basic_select_customers";
  const submittedSql = retryAction.sql || note.submitted_sql || "";
  return `<div class="wrong-note-card"
      data-wrong-note
      data-pack-id="${escapeHtml(packId)}"
      data-problem-id="${escapeHtml(problemId)}"
      data-problem-title="${escapeHtml(note.problem_title || problemId)}"
      data-problem-prompt="${escapeHtml(note.prompt || "")}"
      data-submitted-sql="${escapeHtml(submittedSql)}">
      <div class="attempt-row-head">
        <strong>${escapeHtml(note.problem_title || problemId)}</strong>
        <span class="pill">${escapeHtml(t("wrongNotes"))}</span>
      </div>
      ${note.timestamp ? `<div class="preset-meta">${escapeHtml(note.timestamp)}</div>` : ""}
      <div class="wrong-note-section">
        <span class="section-label">${escapeHtml(t("submittedSql"))}</span>
        <div class="cli-line">${escapeHtml(submittedSql)}</div>
      </div>
      <div class="wrong-note-section">
        <span class="section-label">${escapeHtml(t("expectedIssue"))}</span>
        <p>${escapeHtml(note.expected_issue || "")}</p>
      </div>
      <div class="wrong-note-section">
        <span class="section-label">${escapeHtml(staticFeedback.label || t("staticFeedback"))}</span>
        <p>${escapeHtml(staticFeedback.message || "")}</p>
      </div>
      <div class="practice-flow-actions">
        <button class="ghost-button wrong-note-retry-button" type="button" data-retry-practice="${escapeHtml(index)}">${escapeHtml(
          retryAction.label || t("retryPractice")
        )}</button>
        ${
          providerFeedback.mode_required === "training"
            ? `<button class="ghost-button wrong-note-provider-button" type="button" data-provider-feedback="${escapeHtml(
                index
              )}" title="${escapeHtml(t("trainingModeOnly"))}">${escapeHtml(t("requestAiFeedback"))}</button>`
            : ""
        }
      </div>
      <div class="practice-status" data-feedback-status>${escapeHtml(t("trainingModeOnly"))}</div>
    </div>`;
}

function parseCommand(raw) {
  const text = raw.trim();
  if (!text) {
    return { command: "provider_list_presets", args: {}, context: {} };
  }

  const [command, ...rest] = text.split(/\s+/);
  const tail = rest.join(" ").trim();
  if (command === "help" || command === "help_catalog") {
    return { command: "help_catalog", args: {}, context: { lang: currentLanguage } };
  }
  if (command === "command_explain") {
    return { command, args: { topic: rest[0] || "natural" }, context: { lang: currentLanguage } };
  }
  if (command === "term_explain") {
    return { command, args: { topic: rest[0] || "join" }, context: { lang: currentLanguage } };
  }
  if (command === "schema_detail") {
    return { command, args: { table: tail || "users" }, context: modeContext({ db: "example.db" }) };
  }
  if (command === "natural") {
    const cleaned = tail.replace(/^["']|["']$/g, "") || "show users";
    return {
      command,
      args: { sql: cleaned },
      context: modeContext({ db: "example.db", provider_name: selectedProviderName || "local_ollama" }),
    };
  }
  if (command === "provider_add_preset") {
    return {
      command,
      args: {
        preset: rest[0] || "gemini",
        provider_name: rest[1] || `${rest[0] || "gemini"}_mobile`,
        model_name: rest[2] || undefined,
        api_key_env: rest[3] || undefined,
      },
      context: {},
    };
  }
  if (command === "provider_setup") {
    return { local: "provider_setup", preset: rest[0] || "gemini" };
  }
  if (command === "provider_list") {
    return { command, args: {}, context: {} };
  }
  if (command === "provider_test" || command === "provider_remove") {
    return { command, args: { provider_name: rest[0] || selectedProviderName || "" }, context: {} };
  }
  if (command === "provider_select") {
    return { local: "provider_select", provider: { name: rest[0] || selectedProviderName || "" } };
  }
  if (command === "practice_start") {
    return { local: "practice_start", problem: { id: rest[0] || "basic_select_customers" }, pack: rest[1] || "sql_basics" };
  }
  if (command === "practice_schema") {
    return { command, args: { table: tail || undefined }, context: { mode: "training" } };
  }
  if (command === "practice_query") {
    return { command, args: { sql: tail || "SELECT * FROM customers", limit: 20 }, context: { mode: "training" } };
  }
  if (command === "practice_grade") {
    const [problemId, ...sqlParts] = rest;
    return {
      command,
      args: {
        problem_id: problemId || "basic_select_customers",
        sql: sqlParts.join(" ") || "SELECT id, name, region FROM customers ORDER BY id",
      },
      context: { mode: "training" },
    };
  }
  if (command === "practice_feedback") {
    const [problemId, ...sqlParts] = rest;
    return {
      command,
      args: {
        problem_id: problemId || "basic_select_customers",
        sql: sqlParts.join(" ") || "SELECT id, name FROM customers ORDER BY id",
        provider_name: selectedProviderName || "local_ollama",
        mode: "training",
      },
      context: { mode: "training" },
    };
  }
  if (command === "practice_list" || command === "practice_attempts") {
    return { command, args: {}, context: { mode: "training" } };
  }
  if (command === "production_profile_add") {
    const [profileName, ...targetParts] = rest;
    return {
      command,
      args: {
        profile_name: profileName || "prod_readonly",
        db_uri: targetParts.join(" ") || "example.db",
      },
      context: { mode: "production_assist" },
    };
  }
  if (command === "production_profile_list") {
    return { command, args: {}, context: { mode: "production_assist" } };
  }
  if (command === "production_review") {
    const [profileName, ...sqlParts] = rest;
    const sql = sqlParts.join(" ") || "SELECT COUNT(*) FROM users";
    return {
      command,
      args: {
        profile_name: profileName || "prod_readonly",
        sql,
        request_text: sql,
        source_command: "terminal_shell",
      },
      context: { mode: "production_assist" },
    };
  }
  if (command === "production_approve" || command === "production_execute") {
    return {
      command,
      args: { review_id: rest[0] || "" },
      context: { mode: "production_assist" },
    };
  }
  return { command, args: {}, context: command === "provider_list_presets" ? {} : modeContext({ db: "example.db" }) };
}

async function postCommand(command, args = {}, context = {}) {
  if (window.coqueryCommandRuntime?.postCommand) {
    return window.coqueryCommandRuntime.postCommand(command, args, context);
  }
  const response = await fetch("/api/commands/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command, args, context }),
  });
  return response.json();
}

async function loadHelpCatalog() {
  try {
    const result = await postCommand("help_catalog", {}, { lang: currentLanguage });
    if (result.ok) {
      helpCatalog = result.data;
    }
  } catch {
    helpCatalog = null;
  }
}

async function runParsedCommand(parsed) {
  if (parsed.local === "provider_setup") {
    addBlock(providerSetupResult(parsed.preset));
    return;
  }
  if (parsed.local === "provider_select") {
    selectProvider(parsed.provider?.name || "", "selected");
    addBlock(providerSelectResult(parsed.provider || {}));
    return;
  }
  if (parsed.local === "practice_start") {
    addBlock(practiceStartResult(parsed.problem, parsed.pack));
    return;
  }

  const result = await postCommand(parsed.command, parsed.args || {}, parsed.context || {});
  if (result.command === "provider_list_presets" && result.ok) {
    providerPresets = result.data?.presets || [];
  }
  if (result.command === "help_catalog" && result.ok) {
    helpCatalog = result.data;
  }
  if (result.command === "provider_add_preset" && result.ok) {
    selectProvider(result.data?.provider?.name || "", "selected");
  }
  if (result.command === "provider_test") {
    const providerName = result.data?.provider_name || parsed.args?.provider_name || selectedProviderName;
    if (result.ok) {
      selectProvider(providerName, "ready", result.data?.model_name || "");
    } else if (providerName) {
      updateProviderReadinessStatus(providerName, "error", result.data?.readable_message || result.error?.message || "");
    }
  }
  if (result.command === "provider_remove" && result.ok && result.data?.provider?.name === selectedProviderName) {
    selectProvider("", "none");
  }
  addBlock(result);
}

function commandHelp(commandId) {
  return (helpCatalog?.commands || []).find((item) => item.id === commandId);
}

function termsFor(ids) {
  const wanted = new Set(ids || []);
  return (helpCatalog?.terms || []).filter((term) => wanted.has(term.id));
}

function termListHtml(terms) {
  if (!terms.length) {
    return "";
  }
  const rows = terms
    .slice(0, 4)
    .map((term) => {
      return `<div class="term-item"><strong>${escapeHtml(term.label)}</strong><span>${escapeHtml(term.plain)}</span></div>`;
    })
    .join("");
  return `<div><strong>${escapeHtml(t("relatedTerms"))}</strong><div class="term-list">${rows}</div></div>`;
}

function helpHtmlForCommand(command) {
  if (!command) {
    return `<div>${escapeHtml(t("beginnerGuideEmpty"))}</div>`;
  }
  const relatedTerms = termsFor(command.related_terms || []);
  return `<div><strong>${escapeHtml(command.label || command.id)}</strong></div>
    <div>${escapeHtml(command.summary || "")}</div>
    <div>${escapeHtml(command.beginner || "")}</div>
    ${command.example ? `<code>${escapeHtml(command.example)}</code>` : ""}
    ${termListHtml(relatedTerms)}`;
}

function detailHelpHtml(result) {
  if (!result) {
    return `<div>${escapeHtml(t("beginnerGuideEmpty"))}</div>`;
  }
  if (result.command === "command_explain") {
    return helpHtmlForCommand(result.data?.command);
  }
  if (result.command === "term_explain") {
    const term = result.data?.term;
    if (!term) {
      return `<div>${escapeHtml(t("beginnerGuideEmpty"))}</div>`;
    }
    return `<div><strong>${escapeHtml(term.label)}</strong></div>
      <div>${escapeHtml(term.plain || "")}</div>
      ${term.example ? `<code>${escapeHtml(term.example)}</code>` : ""}`;
  }
  if (result.command === "help_catalog") {
    return `<div><strong>${escapeHtml(t("helpCatalogSummary"))}</strong></div>
      <div>${escapeHtml(t("commandsLabel"))}: ${(result.data?.commands || []).length}</div>
      <div>${escapeHtml(t("termsLabel"))}: ${(result.data?.terms || []).length}</div>`;
  }
  return helpHtmlForCommand(commandHelp(result.command));
}

function productionReviewButtons(review = {}) {
  const reviewId = review.review_id || "";
  if (!reviewId) {
    return "";
  }
  if (review.status === "pending_approval") {
    return `<div class="practice-flow-actions">
      <button class="primary-button" type="button" data-production-approve="${escapeHtml(reviewId)}">${escapeHtml(
        t("productionApproveSql")
      )}</button>
    </div>`;
  }
  if (review.status === "approved") {
    return `<div class="practice-flow-actions">
      <button class="primary-button" type="button" data-production-execute="${escapeHtml(reviewId)}">${escapeHtml(
        t("productionRunReviewed")
      )}</button>
    </div>`;
  }
  return "";
}

function summarizeResult(result) {
  if (!result.ok && !String(result.command || "").startsWith("production_")) {
    const readable = result.data?.readable_message || result.error?.message || "Unknown error";
    const nextStep = result.data?.next_step || "";
    return `<p class="block-summary">${escapeHtml(t("commandFailed"))}: ${escapeHtml(
      readable
    )}</p>${nextStep ? `<div class="cli-line"><strong>${escapeHtml(t("nextStep"))}</strong>: ${escapeHtml(nextStep)}</div>` : ""}`;
  }

  if (result.command === "help_catalog") {
    const commands = (result.data?.commands || [])
      .slice(0, 8)
      .map((command) => {
        return `<div class="schema-row"><strong>${escapeHtml(command.label)}</strong><span>${escapeHtml(
          command.id
        )}</span></div>`;
      })
      .join("");
    const terms = (result.data?.terms || [])
      .slice(0, 6)
      .map((term) => {
        return `<div class="schema-row"><strong>${escapeHtml(term.label)}</strong><span>${escapeHtml(term.id)}</span></div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("helpCatalogSummary"))}</p>
      <div class="block-grid"><div class="section-label">${escapeHtml(t("commandsLabel"))}</div>${commands}</div>
      <div class="block-grid"><div class="section-label">${escapeHtml(t("termsLabel"))}</div>${terms}</div>`;
  }

  if (result.command === "command_explain") {
    const command = result.data?.command || {};
    return `<p class="block-summary"><strong>${escapeHtml(command.label || command.id || "")}</strong> · ${escapeHtml(
      command.summary || ""
    )}</p>
      <div class="cli-line">${escapeHtml(command.beginner || "")}</div>
      ${command.example ? `<div class="cli-line">${escapeHtml(t("commandExample"))}: ${escapeHtml(command.example)}</div>` : ""}`;
  }

  if (result.command === "term_explain") {
    const term = result.data?.term || {};
    return `<p class="block-summary"><strong>${escapeHtml(term.label || term.id || "")}</strong></p>
      <div class="cli-line">${escapeHtml(term.plain || "")}</div>
      ${term.example ? `<div class="cli-line">${escapeHtml(term.example)}</div>` : ""}`;
  }

  if (result.command === "provider_list_presets") {
    const rows = (result.data?.presets || [])
      .map((preset) => {
        return `<div class="preset-row">
          <span class="preset-copy">
            <strong>${escapeHtml(preset.label)}</strong>
            <span class="preset-meta">${escapeHtml(preset.name)} · ${escapeHtml(preset.api_key_env || "API_KEY")}</span>
          </span>
          <span class="preset-row-actions">
            <span class="pill">${escapeHtml(preset.cost_profile || "unknown")}</span>
            <button class="mini-button preset-use-button" type="button" data-preset="${escapeHtml(preset.name)}">${escapeHtml(
              t("useButton")
            )}</button>
          </span>
        </div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("availablePresets"))}</p><div class="block-grid">${rows}</div>`;
  }

  if (result.command === "provider_setup") {
    const selected = result.data?.values?.preset || "gemini";
    const defaults = providerDefaultsFor(selected);
    const presetOptions = (providerPresets.length ? providerPresets : Object.keys(providerDefaults).map((name) => ({ name, label: name })))
      .map((preset) => {
        return `<option value="${escapeHtml(preset.name)}" ${preset.name === selected ? "selected" : ""}>${escapeHtml(
          preset.label || preset.name
        )}</option>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("choosePreset"))}</p>
      <form class="provider-setup-form" data-provider-form>
        <div class="form-grid">
          <label class="field">
            <span>${escapeHtml(t("preset"))}</span>
            <select name="preset">${presetOptions}</select>
          </label>
          <label class="field">
            <span>${escapeHtml(t("providerName"))}</span>
            <input name="provider_name" value="${escapeHtml(defaults.providerName)}" autocomplete="off" />
          </label>
          <label class="field">
            <span>${escapeHtml(t("model"))}</span>
            <input name="model_name" value="${escapeHtml(defaults.modelName)}" autocomplete="off" />
          </label>
          <label class="field">
            <span>${escapeHtml(t("apiKeyEnv"))}</span>
            <input name="api_key_env" value="${escapeHtml(defaults.apiKeyEnv)}" autocomplete="off" />
          </label>
        </div>
        <div class="cli-line provider-preview" data-provider-preview>${escapeHtml(result.cli_equivalent || "")}</div>
        <div class="provider-flow-actions">
          <button class="primary-button" type="submit">${escapeHtml(t("saveProvider"))}</button>
          <button class="ghost-button provider-list-button" type="button">${escapeHtml(t("showSaved"))}</button>
        </div>
        <div class="provider-status" data-provider-status></div>
      </form>`;
  }

  if (result.command === "provider_add_preset") {
    const provider = result.data?.provider || {};
    return `<p class="block-summary">${escapeHtml(t("savedProvider"))} <strong>${escapeHtml(
      provider.name || "provider"
    )}</strong>.</p>
      <div class="block-grid">
        <div class="schema-row"><strong>${escapeHtml(t("preset"))}</strong><span>${escapeHtml(
          provider.preset || result.data?.preset?.name || "custom"
        )}</span></div>
        <div class="schema-row"><strong>${escapeHtml(t("model"))}</strong><span>${escapeHtml(provider.model_name || "not set")}</span></div>
        <div class="schema-row"><strong>${escapeHtml(t("apiKeyEnv"))}</strong><span>${escapeHtml(provider.api_key_env || "not set")}</span></div>
      </div>`;
  }

  if (result.command === "provider_list") {
    const rows = (result.data?.providers || [])
      .map((provider) => {
        const isSelected = provider.name === selectedProviderName;
        return `<div class="provider-row" data-provider-name="${escapeHtml(provider.name)}" data-provider-kind="${escapeHtml(
          provider.kind || ""
        )}" data-provider-model="${escapeHtml(provider.model_name || "")}" data-provider-api-key-env="${escapeHtml(provider.api_key_env || "")}">
          <span class="provider-copy">
            <strong>${escapeHtml(provider.name)}${isSelected ? ` · ${escapeHtml(t("providerStatusSelected"))}` : ""}</strong>
            <span class="preset-meta">${escapeHtml(provider.kind || "provider")} · ${escapeHtml(
              provider.model_name || "model pending"
            )}</span>
            <span>${escapeHtml(provider.api_key_env || "no API key env")}</span>
          </span>
          <span class="preset-row-actions">
            <button class="mini-button provider-select-button" type="button" data-provider-select="${escapeHtml(provider.name)}">${escapeHtml(
              t("providerSelect")
            )}</button>
            <button class="mini-button provider-test-button" type="button" data-provider-test="${escapeHtml(provider.name)}">${escapeHtml(
              t("providerTest")
            )}</button>
            <button class="mini-button provider-remove-button" type="button" data-provider-remove="${escapeHtml(provider.name)}">${escapeHtml(
              t("providerRemove")
            )}</button>
          </span>
        </div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("savedProviders"))}</p><div class="block-grid">${
      rows || `<div class="schema-row"><strong>${escapeHtml(t("noProviders"))}</strong><span>${escapeHtml(t("useSetupAi"))}</span></div>`
    }</div>`;
  }

  if (result.command === "provider_select") {
    const provider = result.data?.provider || {};
    return `<p class="block-summary">${escapeHtml(t("providerSelectedSummary"))}</p>
      <div class="block-grid">
        <div class="schema-row"><strong>${escapeHtml(t("providerName"))}</strong><span>${escapeHtml(provider.name || selectedProviderName)}</span></div>
      </div>`;
  }

  if (result.command === "provider_test") {
    return `<p class="block-summary">${escapeHtml(t("providerTestPassed"))}: <strong>${escapeHtml(
      result.data?.provider_name || "provider"
    )}</strong></p>
      <div class="block-grid">
        <div class="schema-row"><strong>${escapeHtml(t("model"))}</strong><span>${escapeHtml(result.data?.model_name || "")}</span></div>
        <div class="schema-row"><strong>${escapeHtml(t("responsePreview"))}</strong><span>${escapeHtml(
          result.data?.response_preview || ""
        )}</span></div>
      </div>`;
  }

  if (result.command === "provider_remove") {
    const provider = result.data?.provider || {};
    return `<p class="block-summary">${escapeHtml(t("providerRemoved"))} <strong>${escapeHtml(
      provider.name || "provider"
    )}</strong>.</p>
      <div class="block-grid">
        <div class="schema-row"><strong>${escapeHtml(t("model"))}</strong><span>${escapeHtml(provider.model_name || "")}</span></div>
      </div>`;
  }

  if (result.command === "production_profile_add" || result.command === "production_profile_list") {
    const profiles = result.data?.profiles || (result.data?.profile ? [result.data.profile] : []);
    const rows = profiles
      .map((profile) => {
        return `<div class="schema-row"><strong>${escapeHtml(profile.name || "profile")}</strong><span>${escapeHtml(
          profile.read_only ? "read_only" : "not_read_only"
        )}</span></div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(
      result.ok ? t("productionProfileSummary") : result.error?.message || t("commandFailed")
    )}</p>
      <div class="block-grid">${rows}</div>
      ${result.data?.profile_path ? `<div class="cli-line">${escapeHtml(result.data.profile_path)}</div>` : ""}`;
  }

  if (result.command === "production_review" || result.command === "production_approve") {
    const review = result.data?.review || {};
    const statusLabel = result.ok ? review.status || "pending_approval" : result.error?.message || t("commandFailed");
    return `<p class="block-summary">${escapeHtml(t("productionReviewSummary"))} <strong>${escapeHtml(statusLabel)}</strong>.</p>
      <div class="block-grid">
        <div class="schema-row"><strong>${escapeHtml(t("productionProfileSummary"))}</strong><span>${escapeHtml(
          review.profile_name || result.data?.profile?.name || "profile"
        )}</span></div>
        <div class="schema-row"><strong>${escapeHtml(t("productionSelectOnly"))}</strong><span>${escapeHtml(
          review.select_only ? "yes" : "no"
        )}</span></div>
        <div class="schema-row"><strong>${escapeHtml(t("productionApprovalRequired"))}</strong><span>${escapeHtml(
          review.approval_required ? "yes" : t("productionApproved")
        )}</span></div>
      </div>
      <div class="cli-line">${escapeHtml(review.sql || "")}</div>
      ${productionReviewButtons(review)}
      ${result.data?.audit_log ? `<div class="cli-line">${escapeHtml(t("productionAuditLog"))}: ${escapeHtml(result.data.audit_log)}</div>` : ""}`;
  }

  if (result.command === "production_execute") {
    const rows = (result.data?.rows || [])
      .slice(0, 5)
      .map((row) => `<div class="metric-row"><strong>${escapeHtml(JSON.stringify(row))}</strong></div>`)
      .join("");
    return `<p class="block-summary">${escapeHtml(
      result.ok ? t("productionRunReviewed") : result.error?.message || t("commandFailed")
    )}: <strong>${escapeHtml(result.data?.row_count ?? 0)}</strong> ${escapeHtml(t("productionRows"))}.</p>
      <div class="block-grid">${rows}</div>
      ${result.data?.audit_log ? `<div class="cli-line">${escapeHtml(t("productionAuditLog"))}: ${escapeHtml(result.data.audit_log)}</div>` : ""}`;
  }

  if (result.command === "schema_detail") {
    const tables = result.data?.tables || [];
    const table = tables[0] || {};
    const columns = table.columns || [];
    const rows = columns
      .slice(0, 6)
      .map((column) => {
        return `<div class="schema-row"><strong>${escapeHtml(column.name)}</strong><span>${escapeHtml(
          column.type || "unknown"
        )}</span></div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("schemaDetailFor"))} <strong>${escapeHtml(
      table.name || "unknown"
    )}</strong>.</p><div class="block-grid">${rows}</div>`;
  }

  if (result.command === "natural") {
    return `<p class="block-summary">${escapeHtml(t("mode"))}: <strong>${escapeHtml(resultModeLabel(result))}</strong> · ${escapeHtml(
      result.mode || "natural"
    )}</p>
      <div class="cli-line">${escapeHtml(result.sql || t("noSqlReturned"))}</div>`;
  }

  if (result.command === "practice_list") {
    const packId = result.data?.selected_pack || "sql_basics";
    const rows = (result.data?.problems || [])
      .slice(0, 6)
      .map((problem) => {
        const concepts = (problem.concepts || []).join(",");
        return `<div class="preset-row practice-problem-row"
          data-pack-id="${escapeHtml(packId)}"
          data-problem-id="${escapeHtml(problem.id)}"
          data-problem-title="${escapeHtml(problem.title || problem.id)}"
          data-problem-difficulty="${escapeHtml(problem.difficulty || "practice")}"
          data-problem-prompt="${escapeHtml(problem.prompt || "")}"
          data-problem-hint="${escapeHtml(problem.hint || "")}"
          data-problem-concepts="${escapeHtml(concepts)}">
          <span class="practice-problem-copy">
            <strong>${escapeHtml(problem.title || problem.id)}</strong>
            <span class="preset-meta">${escapeHtml(problem.id)} · ${escapeHtml(problem.difficulty || "practice")}</span>
            <span>${escapeHtml(problem.prompt || "")}</span>
          </span>
          <span class="preset-row-actions">
            <button class="mini-button practice-start-button" type="button">${escapeHtml(t("practiceOpenProblem"))}</button>
            <button class="mini-button practice-schema-button" type="button">${escapeHtml(t("practiceInspectSchema"))}</button>
          </span>
        </div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("practiceProblems"))} <strong>${escapeHtml(
      packId
    )}</strong>.</p><div class="block-grid">${rows}</div>`;
  }

  if (result.command === "practice_start") {
    const problem = result.data?.problem || {};
    const packId = result.data?.packId || "sql_basics";
    const initialSql = result.data?.initialSql || "";
    const concepts = (problem.concepts || []).map((concept) => `<span class="pill">${escapeHtml(concept)}</span>`).join("");
    return `<p class="block-summary">${escapeHtml(t("practiceStart"))}: <strong>${escapeHtml(
      problem.title || problem.id || "practice"
    )}</strong></p>
      <form class="practice-flow-form" data-practice-form data-problem-id="${escapeHtml(
        problem.id || "basic_select_customers"
      )}" data-pack-id="${escapeHtml(packId)}">
        <div class="practice-problem-card">
          <div class="practice-problem-head">
            <span class="pill">${escapeHtml(problem.difficulty || "practice")}</span>
            ${concepts}
          </div>
          <div class="section-label">${escapeHtml(t("practiceProblemPrompt"))}</div>
          <p>${escapeHtml(problem.prompt || "")}</p>
          ${
            problem.hint
              ? `<div class="practice-hint"><strong>${escapeHtml(t("practiceHint"))}</strong><span>${escapeHtml(problem.hint)}</span></div>`
              : ""
          }
        </div>
        <div class="practice-flow-actions">
          <button class="ghost-button practice-schema-button" type="button">${escapeHtml(t("practiceInspectSchema"))}</button>
          <button class="ghost-button practice-attempts-button" type="button">${escapeHtml(t("practiceShowAttempts"))}</button>
        </div>
        <label class="field practice-sql-field">
          <span>${escapeHtml(t("practiceSqlLabel"))}</span>
          <textarea name="sql" spellcheck="false" autocomplete="off" placeholder="${escapeHtml(
            t("practiceSqlPlaceholder")
          )}">${escapeHtml(initialSql)}</textarea>
        </label>
        <div class="cli-line practice-preview" data-practice-preview>${escapeHtml(
          practiceCliEquivalent(problem.id, initialSql, packId)
        )}</div>
        <div class="practice-flow-actions">
          <button class="primary-button" type="submit" data-practice-submit>${escapeHtml(t("practiceSubmit"))}</button>
        </div>
        <div class="practice-status" data-practice-status>${escapeHtml(t("practiceFlowSummary"))}</div>
      </form>`;
  }

  if (result.command === "practice_schema") {
    const rows = (result.data?.tables || [])
      .map((table) => {
        return `<div class="schema-row"><strong>${escapeHtml(table.name)}</strong><span>${escapeHtml(
          `${table.columns?.length || 0} cols / ${table.row_count || 0} rows`
        )}</span></div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("practiceSchema"))}</p><div class="block-grid">${rows}</div>`;
  }

  if (result.command === "practice_query") {
    const rows = (result.data?.rows || [])
      .slice(0, 5)
      .map((row) => {
        return `<div class="metric-row"><strong>${escapeHtml(JSON.stringify(row))}</strong></div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("returnedRows"))}: <strong>${escapeHtml(
      result.data?.row_count || 0
    )}</strong>.</p><div class="block-grid">${rows}</div>`;
  }

  if (result.command === "practice_grade") {
    const wrongNote = result.data?.wrong_note;
    return `<p class="block-summary">${escapeHtml(t("practiceAnswer"))}: <strong>${
      result.data?.correct ? escapeHtml(t("correct")) : escapeHtml(t("needsReview"))
    }</strong></p>
      <div class="block-grid">
        <div class="metric-row"><strong>${escapeHtml(t("actualRows"))}</strong><span>${escapeHtml(
          result.data?.actual?.row_count ?? 0
        )}</span></div>
        <div class="metric-row"><strong>${escapeHtml(t("expectedRows"))}</strong><span>${escapeHtml(
          result.data?.expected?.row_count ?? 0
        )}</span></div>
        <div class="metric-row"><strong>${escapeHtml(t("practiceAttemptRecorded"))}</strong><span>${escapeHtml(
          result.data?.attempt_recorded ? "yes" : "no"
        )}</span></div>
      </div>
      <div class="cli-line">${escapeHtml(result.data?.feedback || "")}</div>
      ${wrongNote ? `<div class="block-grid">${wrongNoteCard(wrongNote, 0)}</div>` : ""}`;
  }

  if (result.command === "practice_attempts") {
    const wrongAttempts = (result.data?.attempts || []).filter((attempt) => attempt.correct === false);
    const rows = wrongAttempts
      .slice()
      .reverse()
      .map((attempt, index) => {
        const note =
          attempt.wrong_note ||
          {
            pack_id: attempt.pack_id || result.data?.pack_id || "sql_basics",
            problem_id: attempt.problem_id,
            problem_title: attempt.problem_title || attempt.problem_id,
            timestamp: attempt.timestamp,
            submitted_sql: attempt.sql,
            expected_issue: "",
            static_feedback: { label: t("staticFeedback"), message: "" },
            retry_action: {
              label: t("retryPractice"),
              command: "practice_start",
              pack_id: attempt.pack_id || result.data?.pack_id || "sql_basics",
              problem_id: attempt.problem_id,
              sql: attempt.sql,
            },
            provider_feedback: { mode_required: "training" },
          };
        if (!note.timestamp) {
          note.timestamp = attempt.timestamp;
        }
        return wrongNoteCard(note, index);
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("wrongNotes"))}: <strong>${escapeHtml(
      wrongAttempts.length
    )}</strong>.</p><div class="block-grid">${
      rows || `<div class="schema-row"><strong>${escapeHtml(t("practiceNoAttempts"))}</strong><span>${escapeHtml(t("practiceStart"))}</span></div>`
    }</div>`;
  }

  if (result.command === "practice_feedback") {
    const feedback = result.data?.feedback || {};
    return `<p class="block-summary">${escapeHtml(feedback.label || t("staticFeedback"))}: <strong>${escapeHtml(
      feedback.ai_generated ? t("aiFeedback") : t("staticFeedback")
    )}</strong></p>
      <div class="block-grid">
        <div class="wrong-note-card">
          <div class="wrong-note-section">
            <span class="section-label">${escapeHtml(t("expectedIssue"))}</span>
            <p>${escapeHtml(result.data?.expected_issue || "")}</p>
          </div>
          <div class="wrong-note-section">
            <span class="section-label">${escapeHtml(feedback.label || t("staticFeedback"))}</span>
            <p>${escapeHtml(feedback.message || "")}</p>
          </div>
        </div>
      </div>`;
  }

  return `<p class="block-summary">${escapeHtml(t("commandCompleted"))}: <strong>${escapeHtml(
    result.block_type || "command_result"
  )}</strong>.</p>`;
}

function providerFormValues(form) {
  const data = new FormData(form);
  return {
    preset: String(data.get("preset") || "gemini"),
    providerName: String(data.get("provider_name") || ""),
    modelName: String(data.get("model_name") || ""),
    apiKeyEnv: String(data.get("api_key_env") || ""),
  };
}

function updateProviderFormPreview(form) {
  const preview = form.querySelector("[data-provider-preview]");
  if (preview) {
    preview.textContent = providerCliEquivalent(providerFormValues(form));
  }
}

function bindProviderSetup(block) {
  const form = block.querySelector("[data-provider-form]");
  if (!form) {
    return;
  }

  const presetSelect = form.querySelector('select[name="preset"]');
  const providerInput = form.querySelector('input[name="provider_name"]');
  const modelInput = form.querySelector('input[name="model_name"]');
  const apiKeyInput = form.querySelector('input[name="api_key_env"]');
  const status = form.querySelector("[data-provider-status]");

  presetSelect.addEventListener("change", () => {
    const defaults = providerDefaultsFor(presetSelect.value);
    providerInput.value = defaults.providerName;
    modelInput.value = defaults.modelName;
    apiKeyInput.value = defaults.apiKeyEnv;
    if (status) {
      status.textContent = "";
      status.className = "provider-status";
    }
    updateProviderFormPreview(form);
  });

  [providerInput, modelInput, apiKeyInput].forEach((input) => {
    input.addEventListener("input", () => updateProviderFormPreview(form));
  });

  const listButton = form.querySelector(".provider-list-button");
  if (listButton) {
    listButton.addEventListener("click", () => {
      runParsedCommand({ command: "provider_list", args: {}, context: {} });
    });
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const values = providerFormValues(form);
    if (status) {
      status.textContent = t("savingProvider");
      status.className = "provider-status";
    }
    runParsedCommand({
      command: "provider_add_preset",
      args: {
        preset: values.preset,
        provider_name: values.providerName,
        model_name: values.modelName || undefined,
        api_key_env: values.apiKeyEnv || undefined,
      },
      context: {},
    })
      .then(() => {
        if (status) {
          status.textContent = t("savedProviderStatus");
          status.className = "provider-status ok";
        }
      })
      .catch((error) => {
        if (status) {
          status.textContent = error.message;
          status.className = "provider-status error";
        }
      });
  });

  updateProviderFormPreview(form);
}

function providerFromRow(row) {
  return {
    name: row?.dataset.providerName || "",
    kind: row?.dataset.providerKind || "",
    model_name: row?.dataset.providerModel || "",
    api_key_env: row?.dataset.providerApiKeyEnv || "",
  };
}

function bindProviderListButtons(block) {
  block.querySelectorAll("[data-provider-select]").forEach((button) => {
    button.addEventListener("click", () => {
      const row = button.closest(".provider-row");
      const provider = providerFromRow(row);
      selectProvider(provider.name, "selected");
      addBlock(providerSelectResult(provider));
    });
  });

  block.querySelectorAll("[data-provider-test]").forEach((button) => {
    button.addEventListener("click", () => {
      runParsedCommand({ command: "provider_test", args: { provider_name: button.dataset.providerTest || "" }, context: {} });
    });
  });

  block.querySelectorAll("[data-provider-remove]").forEach((button) => {
    button.addEventListener("click", () => {
      runParsedCommand({ command: "provider_remove", args: { provider_name: button.dataset.providerRemove || "" }, context: {} });
    });
  });
}

function bindPresetButtons(block) {
  block.querySelectorAll(".preset-use-button").forEach((button) => {
    button.addEventListener("click", () => {
      addBlock(providerSetupResult(button.dataset.preset || "gemini"));
    });
  });
}

function problemFromRow(row) {
  if (!row) {
    return { id: "basic_select_customers", title: "Practice", difficulty: "practice", prompt: "", hint: "", concepts: [] };
  }
  const concepts = row.dataset.problemConcepts
    ? row.dataset.problemConcepts.split(",").map((item) => item.trim()).filter(Boolean)
    : [];
  return {
    id: row.dataset.problemId || "basic_select_customers",
    title: row.dataset.problemTitle || row.dataset.problemId || "Practice",
    difficulty: row.dataset.problemDifficulty || "practice",
    prompt: row.dataset.problemPrompt || "",
    hint: row.dataset.problemHint || "",
    concepts,
  };
}

function updatePracticePreview(form) {
  const preview = form.querySelector("[data-practice-preview]");
  const textarea = form.querySelector('textarea[name="sql"]');
  if (preview && textarea) {
    preview.textContent = practiceCliEquivalent(form.dataset.problemId, textarea.value.trim(), form.dataset.packId);
  }
}

function bindPracticeButtons(block) {
  block.querySelectorAll(".practice-problem-row .practice-start-button").forEach((button) => {
    button.addEventListener("click", () => {
      const row = button.closest(".practice-problem-row");
      addBlock(practiceStartResult(problemFromRow(row), row?.dataset.packId || "sql_basics"));
    });
  });
  block.querySelectorAll(".practice-problem-row .practice-schema-button").forEach((button) => {
    button.addEventListener("click", () => {
      const row = button.closest(".practice-problem-row");
      runParsedCommand({
        command: "practice_schema",
        args: { pack: row?.dataset.packId || "sql_basics" },
        context: { mode: "training" },
      });
    });
  });
}

function bindPracticeFlow(block) {
  const form = block.querySelector("[data-practice-form]");
  if (!form) {
    return;
  }

  const textarea = form.querySelector('textarea[name="sql"]');
  const status = form.querySelector("[data-practice-status]");
  const problemId = form.dataset.problemId || "basic_select_customers";
  const packId = form.dataset.packId || "sql_basics";

  const setStatus = (message, state = "") => {
    if (status) {
      status.textContent = message;
      status.className = `practice-status ${state}`.trim();
    }
  };

  if (textarea) {
    textarea.addEventListener("input", () => updatePracticePreview(form));
  }

  const schemaButton = form.querySelector(".practice-schema-button");
  if (schemaButton) {
    schemaButton.addEventListener("click", () => {
      runParsedCommand({ command: "practice_schema", args: { pack: packId }, context: { mode: "training" } });
    });
  }

  const attemptsButton = form.querySelector(".practice-attempts-button");
  if (attemptsButton) {
    attemptsButton.addEventListener("click", () => {
      runParsedCommand({ command: "practice_attempts", args: { pack: packId, problem_id: problemId, limit: 5 }, context: { mode: "training" } });
    });
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const sql = textarea?.value.trim() || "";
    if (!sql) {
      setStatus(t("practiceSqlPlaceholder"), "error");
      return;
    }

    setStatus(t("practiceRunning"));
    updatePracticePreview(form);

    try {
      const queryResult = await postCommand("practice_query", { sql, pack: packId, limit: 20 }, { mode: "training" });
      addBlock(queryResult);
      if (!queryResult.ok) {
        setStatus(queryResult.error?.message || t("commandFailed"), "error");
        return;
      }

      const gradeResult = await postCommand("practice_grade", { problem_id: problemId, sql, pack: packId }, { mode: "training" });
      addBlock(gradeResult);
      if (!gradeResult.ok) {
        setStatus(gradeResult.error?.message || t("commandFailed"), "error");
        return;
      }

      const verdict = gradeResult.data?.correct ? t("correct") : t("needsReview");
      const recorded = gradeResult.data?.attempt_recorded ? ` · ${t("practiceAttemptRecorded")}` : "";
      setStatus(`${verdict}${recorded}`, gradeResult.data?.correct ? "ok" : "error");

      if (!gradeResult.data?.correct) {
        const attemptsResult = await postCommand(
          "practice_attempts",
          { pack: packId, problem_id: problemId, limit: 5 },
          { mode: "training" }
        );
        addBlock(attemptsResult);
      }
    } catch (error) {
      setStatus(error.message, "error");
    }
  });

  updatePracticePreview(form);
}

function bindWrongNoteButtons(block) {
  block.querySelectorAll("[data-retry-practice]").forEach((button) => {
    button.addEventListener("click", () => {
      const noteNode = button.closest("[data-wrong-note]");
      if (!noteNode) {
        return;
      }
      const note = {
        pack_id: noteNode.dataset.packId || "sql_basics",
        problem_id: noteNode.dataset.problemId || "basic_select_customers",
        problem_title: noteNode.dataset.problemTitle || noteNode.dataset.problemId || "Practice",
        prompt: noteNode.dataset.problemPrompt || "",
        submitted_sql: noteNode.dataset.submittedSql || "",
      };
      addBlock(practiceStartResult(practiceProblemFromWrongNote(note), note.pack_id, note.submitted_sql));
    });
  });

  block.querySelectorAll("[data-provider-feedback]").forEach((button) => {
    button.addEventListener("click", async () => {
      const noteNode = button.closest("[data-wrong-note]");
      const status = noteNode?.querySelector("[data-feedback-status]");
      if (!noteNode) {
        return;
      }
      if (status) {
        status.textContent = t("requestAiFeedback");
        status.className = "practice-status";
      }
      try {
        const feedbackResult = await postCommand(
          "practice_feedback",
          {
            pack: noteNode.dataset.packId || "sql_basics",
            problem_id: noteNode.dataset.problemId || "basic_select_customers",
            sql: noteNode.dataset.submittedSql || "",
            provider_name: selectedProviderName || "local_ollama",
            mode: "training",
          },
          { mode: "training" }
        );
        addBlock(feedbackResult);
        if (status) {
          status.textContent = feedbackResult.ok
            ? feedbackResult.data?.feedback?.label || t("aiFeedback")
            : feedbackResult.error?.message || t("commandFailed");
          status.className = `practice-status ${feedbackResult.ok ? "ok" : "error"}`;
        }
      } catch (error) {
        if (status) {
          status.textContent = error.message;
          status.className = "practice-status error";
        }
      }
    });
  });
}

function bindProductionButtons(block) {
  block.querySelectorAll("[data-production-approve]").forEach((button) => {
    button.addEventListener("click", () => {
      runParsedCommand({
        command: "production_approve",
        args: { review_id: button.dataset.productionApprove || "" },
        context: { mode: "production_assist" },
      });
    });
  });

  block.querySelectorAll("[data-production-execute]").forEach((button) => {
    button.addEventListener("click", () => {
      runParsedCommand({
        command: "production_execute",
        args: { review_id: button.dataset.productionExecute || "" },
        context: { mode: "production_assist" },
      });
    });
  });
}

function blockTemplate(result) {
  const modePill = result.mode_context
    ? `<span class="pill mode-context-pill" title="${escapeHtml(modeSummary(result.mode_context.mode))}">${escapeHtml(
        resultModeLabel(result)
      )}</span>`
    : "";
  return `
    <div class="block-command">
      <span class="prompt">&gt;</span>
      <code>${escapeHtml(result.command)}</code>
      <span class="pill">${escapeHtml(result.block_type || "command_result")}</span>
      ${modePill}
    </div>
    ${summarizeResult(result)}
    <div class="cli-line">${escapeHtml(result.cli_equivalent || "")}</div>
    <div class="block-actions">${(result.actions || ["copy"])
      .map((action) => `<span title="${escapeHtml(action)}">${escapeHtml(actionLabel(action))}</span>`)
      .join("")}</div>
  `;
}

function renderBlock(block, result) {
  block.innerHTML = blockTemplate(result);
  bindPresetButtons(block);
  bindProviderSetup(block);
  bindProviderListButtons(block);
  bindPracticeButtons(block);
  bindPracticeFlow(block);
  bindWrongNoteButtons(block);
  bindProductionButtons(block);
}

function addBlock(result) {
  const block = document.createElement("article");
  block.className = `terminal-block ${result.ok ? "" : "error-block"}`;
  block.tabIndex = 0;
  block.__result = result;
  renderBlock(block, result);

  block.addEventListener("click", () => selectBlock(block, result));
  block.addEventListener("focus", () => selectBlock(block, result));
  renderedBlocks.push(block);
  terminalScroll.appendChild(block);
  selectBlock(block, result);
  terminalScroll.scrollTop = terminalScroll.scrollHeight;
}

function selectBlock(block, result) {
  if (selectedBlock) {
    selectedBlock.classList.remove("active");
  }
  selectedBlock = block;
  selectedResult = result;
  selectedBlock.classList.add("active");
  detailTitle.textContent = result.command || "Command";
  detailCli.textContent = result.cli_equivalent || "";
  detailJson.textContent = JSON.stringify(result, null, 2);
  detailActions.innerHTML = (result.actions || ["copy"])
    .map((action) => `<span title="${escapeHtml(action)}">${escapeHtml(actionLabel(action))}</span>`)
    .join("");
  detailHelp.innerHTML = detailHelpHtml(result);
}

function rerenderBlocks() {
  renderedBlocks.forEach((block) => {
    renderBlock(block, block.__result);
  });
  if (selectedBlock && selectedResult) {
    selectBlock(selectedBlock, selectedResult);
  }
}

function localizedSession(session) {
  const labels = {
    "local-sql-lab": { title: t("sessionLocalTitle"), subtitle: t("sessionLocalSubtitle") },
    "provider-setup": { title: t("sessionProviderTitle"), subtitle: t("sessionProviderSubtitle") },
    "practice-flow": { title: t("sessionPracticeTitle"), subtitle: t("sessionPracticeSubtitle") },
  };
  return labels[session.id] || { title: session.title, subtitle: session.subtitle };
}

async function loadSessions() {
  let payload;
  if (window.coqueryCommandRuntime?.getSessions) {
    payload = await window.coqueryCommandRuntime.getSessions();
  } else {
    const response = await fetch("/api/sessions");
    payload = await response.json();
  }
  sessionList.innerHTML = (payload.sessions || [])
    .map((session) => {
      const copy = localizedSession(session);
      return `<button class="session-card ${session.active ? "active" : ""}" type="button">
        <span class="session-dot">${escapeHtml(copy.title.slice(0, 1))}</span>
        <span>
          <span class="session-title">${escapeHtml(copy.title)}</span>
          <span class="session-subtitle">${escapeHtml(copy.subtitle)}</span>
        </span>
      </button>`;
    })
    .join("");
}

commandForm.addEventListener("submit", (event) => {
  event.preventDefault();
  setCommandMenuOpen(false);
  runParsedCommand(parseCommand(commandInput.value)).catch((error) => {
    addBlock({
      ok: false,
      command: "client_error",
      block_type: "command_result",
      actions: ["copy"],
      cli_equivalent: commandInput.value,
      error: { message: error.message },
      data: {},
    });
  });
});

document.querySelectorAll("[data-template]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-template]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    commandInput.value = button.getAttribute("data-template");
    commandInput.focus();
    setCommandMenuOpen(false);
    if (button.getAttribute("data-template") === "provider_setup") {
      runParsedCommand(parseCommand(commandInput.value));
    }
  });
});

if (commandMenuToggle && commandMenuPanel) {
  commandMenuToggle.addEventListener("click", () => {
    setCommandMenuOpen(commandMenuToggle.getAttribute("aria-expanded") !== "true");
  });

  document.addEventListener("click", (event) => {
    if (
      commandMenuToggle.getAttribute("aria-expanded") === "true" &&
      !commandMenuPanel.contains(event.target) &&
      !commandMenuToggle.contains(event.target)
    ) {
      setCommandMenuOpen(false);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setCommandMenuOpen(false);
    }
  });
}

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    currentAppMode = normalizeAppMode(button.dataset.modeOption);
    localStorage.setItem("coquery_app_mode", currentAppMode);
    applyModeIndicator();
    updateProviderReadinessStatus();
  });
});

languageButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    currentLanguage = button.dataset.lang || "ko";
    localStorage.setItem("coquery_language", currentLanguage);
    applyStaticTranslations();
    await loadHelpCatalog();
    await loadSessions();
    rerenderBlocks();
  });
});

[drawerButton, detailToggle].forEach((button) => {
  button.addEventListener("click", () => {
    appShell.dataset.detailOpen = appShell.dataset.detailOpen === "true" ? "false" : "true";
  });
});

closeDetail.addEventListener("click", () => {
  appShell.dataset.detailOpen = "false";
});

applyStaticTranslations();
const initialCommand = window.coqueryCommandRuntime?.initialCommand || "provider_list_presets";
if (window.coqueryCommandRuntime?.initialCommand) {
  commandInput.value = initialCommand;
}
loadSessions();
loadHelpCatalog().finally(() => runParsedCommand(parseCommand(initialCommand)));
