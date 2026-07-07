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
const detailToggle = document.getElementById("detailToggle");
const closeDetail = document.getElementById("closeDetail");
const languageButtons = document.querySelectorAll("[data-lang]");

let selectedBlock = null;
let selectedResult = null;
let providerPresets = [];
let helpCatalog = null;
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
    documentTitle: "CoQuery 터미널 쉘",
    sessionRailLabel: "세션",
    sessionListLabel: "세션 목록",
    searchPlaceholder: "세션 검색...",
    brandSubtitle: "터미널 쉘",
    headerKicker: "로컬 SQL 랩",
    appTitle: "반응형 터미널 쉘",
    detailsButton: "상세",
    languageToggleLabel: "언어",
    contextLabel: "작업 메뉴",
    chipPresets: "프리셋",
    chipSetupAi: "AI 설정",
    chipSchema: "스키마",
    chipNatural: "자연어",
    chipPractice: "연습",
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
    schemaDetailFor: "스키마 상세",
    mode: "모드",
    noSqlReturned: "반환된 SQL 없음",
    practiceProblems: "DB 없이 사용하는 연습 문제입니다.",
    practiceSchema: "연습 데이터셋 구조입니다.",
    returnedRows: "연습 행 반환",
    practiceAnswer: "연습 답안",
    correct: "정답",
    needsReview: "복습 필요",
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
    documentTitle: "CoQuery Terminal Shell",
    sessionRailLabel: "Sessions",
    sessionListLabel: "Session list",
    searchPlaceholder: "Search sessions...",
    brandSubtitle: "Terminal Shell",
    headerKicker: "Local SQL Lab",
    appTitle: "Responsive Terminal Shell",
    detailsButton: "Details",
    languageToggleLabel: "Language",
    contextLabel: "Context",
    chipPresets: "Presets",
    chipSetupAi: "Setup AI",
    chipSchema: "Schema",
    chipNatural: "Natural",
    chipPractice: "Practice",
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
    schemaDetailFor: "Schema detail for",
    mode: "Mode",
    noSqlReturned: "No SQL returned",
    practiceProblems: "DB-free practice problems from",
    practiceSchema: "Practice dataset schema.",
    returnedRows: "Returned practice rows",
    practiceAnswer: "Practice answer",
    correct: "correct",
    needsReview: "needs review",
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
    return { command, args: { table: tail || "users" }, context: { db: "example.db" } };
  }
  if (command === "natural") {
    const cleaned = tail.replace(/^["']|["']$/g, "") || "show users";
    return { command, args: { sql: cleaned }, context: { db: "example.db", provider_name: "local_ollama" } };
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
  if (command === "practice_schema") {
    return { command, args: { table: tail || undefined }, context: {} };
  }
  if (command === "practice_query") {
    return { command, args: { sql: tail || "SELECT * FROM customers", limit: 20 }, context: {} };
  }
  if (command === "practice_grade") {
    const [problemId, ...sqlParts] = rest;
    return {
      command,
      args: {
        problem_id: problemId || "basic_select_customers",
        sql: sqlParts.join(" ") || "SELECT id, name, region FROM customers ORDER BY id",
      },
      context: {},
    };
  }
  if (command === "practice_list" || command === "practice_attempts") {
    return { command, args: {}, context: {} };
  }
  return { command, args: {}, context: command === "provider_list_presets" ? {} : { db: "example.db" } };
}

async function postCommand(command, args = {}, context = {}) {
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

  const result = await postCommand(parsed.command, parsed.args || {}, parsed.context || {});
  if (result.command === "provider_list_presets" && result.ok) {
    providerPresets = result.data?.presets || [];
  }
  if (result.command === "help_catalog" && result.ok) {
    helpCatalog = result.data;
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

function summarizeResult(result) {
  if (!result.ok) {
    return `<p class="block-summary">${escapeHtml(t("commandFailed"))}: ${escapeHtml(
      result.error?.message || "Unknown error"
    )}</p>`;
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
        return `<div class="schema-row"><strong>${escapeHtml(provider.name)}</strong><span>${escapeHtml(
          provider.model_name || provider.kind || "model pending"
        )}</span></div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("savedProviders"))}</p><div class="block-grid">${
      rows || `<div class="schema-row"><strong>${escapeHtml(t("noProviders"))}</strong><span>${escapeHtml(t("useSetupAi"))}</span></div>`
    }</div>`;
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
    return `<p class="block-summary">${escapeHtml(t("mode"))}: <strong>${escapeHtml(result.mode)}</strong></p>
      <div class="cli-line">${escapeHtml(result.sql || t("noSqlReturned"))}</div>`;
  }

  if (result.command === "practice_list") {
    const rows = (result.data?.problems || [])
      .slice(0, 6)
      .map((problem) => {
        return `<div class="schema-row"><strong>${escapeHtml(problem.id)}</strong><span>${escapeHtml(
          problem.difficulty || "practice"
        )}</span></div>`;
      })
      .join("");
    return `<p class="block-summary">${escapeHtml(t("practiceProblems"))} <strong>${escapeHtml(
      result.data?.selected_pack || "sql_basics"
    )}</strong>.</p><div class="block-grid">${rows}</div>`;
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
    return `<p class="block-summary">${escapeHtml(t("practiceAnswer"))}: <strong>${
      result.data?.correct ? escapeHtml(t("correct")) : escapeHtml(t("needsReview"))
    }</strong></p>
      <div class="cli-line">${escapeHtml(result.data?.feedback || "")}</div>`;
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

function bindPresetButtons(block) {
  block.querySelectorAll(".preset-use-button").forEach((button) => {
    button.addEventListener("click", () => {
      addBlock(providerSetupResult(button.dataset.preset || "gemini"));
    });
  });
}

function blockTemplate(result) {
  return `
    <div class="block-command">
      <span class="prompt">&gt;</span>
      <code>${escapeHtml(result.command)}</code>
      <span class="pill">${escapeHtml(result.block_type || "command_result")}</span>
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
  const response = await fetch("/api/sessions");
  const payload = await response.json();
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
    if (button.getAttribute("data-template") === "provider_setup") {
      runParsedCommand(parseCommand(commandInput.value));
    }
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
loadSessions();
loadHelpCatalog().finally(() => runParsedCommand(parseCommand("provider_list_presets")));
