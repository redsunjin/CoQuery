/* Conditions studio: bounded rules, no SQL execution or external AI. */
(function (root) {
  "use strict";
  const VERSION = 1,
    KEY = "coquery.exploration.v1";
  const stages = [
    "이해",
    "예상·실험",
    "반례",
    "자기 설명",
    "새 상황에 적용",
    "나만의 퍼즐",
  ];
  const cards = [
    { id: "A", name: "A", a: true, b: true },
    { id: "B", name: "B", a: true, b: false },
    { id: "C", name: "C", a: false, b: true },
    { id: "D", name: "D", a: false, b: false },
  ];
  const books = cards.map((x, i) => ({
    ...x,
    name: ["별 이야기", "숲 이야기", "달 지도", "바다 지도"][i],
  }));
  const evaluate = (rows, mode) =>
    rows
      .filter((x) => (mode === "and" ? x.a && x.b : x.a || x.b))
      .map((x) => x.id);
  const same = (a, b) => a.length === b.length && a.every((x) => b.includes(x));
  const fresh = () => ({
    version: VERSION,
    stage: 0,
    guided: { selected: [], checked: false },
    independent: { selected: [], checked: false },
    counter: "",
    counterChecked: false,
    notes: "",
    transfer: { selected: [], checked: false, mode: "or", notes: "" },
    savedProject: null,
    project: {
      title: "나의 조건 퍼즐",
      aLabel: "빨강",
      bLabel: "원",
      mode: "and",
      rows: cards.map((x) => ({ ...x })),
      selected: [],
      checked: false,
      notes: "",
      saved: false,
    },
    visited: [],
  });
  function restore(value) {
    const s = fresh();
    if (!value || value.version !== VERSION) return s;
    if (
      Number.isInteger(value.stage) &&
      value.stage >= 0 &&
      value.stage < stages.length
    )
      s.stage = value.stage;
    const clean = (v) => (typeof v === "string" ? v.slice(0, 1500) : "");
    for (const k of ["guided", "independent", "transfer"]) {
      const v = value[k];
      if (!v || typeof v !== "object") continue;
      s[k].selected = Array.isArray(v.selected)
        ? [...new Set(v.selected.filter((x) => cards.some((c) => c.id === x)))]
        : [];
      s[k].checked = v.checked === true;
    }
    s.notes = clean(value.notes);
    s.counter = ["A", "B", "C", "D"].includes(value.counter)
      ? value.counter
      : "";
    s.counterChecked = value.counterChecked === true;
    s.transfer.mode = value.transfer?.mode === "and" ? "and" : "or";
    s.transfer.notes = clean(value.transfer?.notes);
    const p = value.project;
    if (p && typeof p === "object") {
      for (const k of ["title", "aLabel", "bLabel"])
        s.project[k] = clean(p[k]).slice(0, 80) || s.project[k];
      s.project.mode = p.mode === "or" ? "or" : "and";
      s.project.notes = clean(p.notes);
      if (Array.isArray(p.rows) && p.rows.length === 4)
        s.project.rows = cards.map((x, i) => ({
          ...x,
          name: clean(p.rows[i]?.name).slice(0, 80) || x.id,
          a: p.rows[i]?.a === true,
          b: p.rows[i]?.b === true,
        }));
      s.project.selected = Array.isArray(p.selected)
        ? [...new Set(p.selected.filter((x) => cards.some((c) => c.id === x)))]
        : [];
      s.project.checked = p.checked === true;
      s.project.saved = p.saved === true;
    }
    if (value.savedProject && typeof value.savedProject === "object")
      s.savedProject = restore({
        version: VERSION,
        project: value.savedProject,
      }).project;
    s.visited = Array.isArray(value.visited)
      ? value.visited.filter((x) => Number.isInteger(x) && x >= 0 && x < 6)
      : [];
    return s;
  }
  root.CoqueryExploration = { fresh, restore, evaluate, same, VERSION };
  if (typeof document === "undefined") return;
  const host = document.getElementById("explorationLearning"),
    shell = document.querySelector(".app-shell");
  if (!host || !shell) return;
  let state = fresh(),
    persistent = true,
    status = "",
    help = false,
    sql = false;
  try {
    state = restore(JSON.parse(localStorage.getItem(KEY) || "null"));
  } catch {
    persistent = false;
  }
  const esc = (v) =>
    String(v).replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  const btn = (label, action, value = "", primary = false) =>
    `<button type="button" class="${primary ? "primary-button" : "ghost-button"}" data-explore="${action}" data-value="${esc(value)}">${esc(label)}</button>`;
  const rule = (mode) =>
    mode === "and" ? "두 조건 모두 (그리고)" : "하나 이상 (또는 · 둘 다 포함)";
  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch {
      persistent = false;
      const notice = host.querySelector("#exploreStorage");
      if (notice)
        notice.textContent =
          "저장소를 사용할 수 없어 현재 탭에서만 유지합니다. 탭을 닫으면 사라집니다.";
    }
  }
  function announce(message) {
    status = message;
    const n = host.querySelector("#exploreStatus");
    if (n) n.textContent = message;
  }
  function invalidateProject() {
    state.project.checked = false;
    state.project.saved = false;
    host.querySelector("#exploreResult")?.remove();
    host.querySelector("#projectSaved")?.remove();
    announce("퍼즐을 수정했습니다. 다시 예상·실행한 뒤 저장하세요.");
  }
  function open() {
    setLearningHomeMode(true);
    shell.dataset.conceptOpen = "false";
    document.getElementById("conceptLearning").hidden = true;
    shell.dataset.explorationOpen = "true";
    host.hidden = false;
    render(true);
  }
  function close() {
    shell.dataset.explorationOpen = "false";
    host.hidden = true;
  }
  function selection(rows, a, labels) {
    return `<p class="concept-muted">남을 항목을 먼저 골라 보세요. 아무것도 고르지 않는 예상도 실험할 수 있습니다.</p><div class="concept-cards">${rows.map((x) => `<button type="button" id="explore-card-${x.id}" class="concept-card" data-explore="select" data-value="${x.id}" aria-pressed="${a.selected.includes(x.id)}"><strong>${esc(x.name)}</strong><span>${esc(labels[0])}: ${x.a ? "예" : "아니요"}<br>${esc(labels[1])}: ${x.b ? "예" : "아니요"}</span></button>`).join("")}</div>`;
  }
  function result(rows, a, mode, labels) {
    if (!a.checked) return "";
    const actual = evaluate(rows, mode);
    return `<section class="concept-result" id="exploreResult"><h3 tabindex="-1" id="exploreResultHeading">${same(a.selected, actual) ? "예상과 결과가 같아요." : "차이를 발견했어요. 다시 살펴보세요."}</h3><p>내 예상: ${esc(a.selected.map((id) => rows.find((x) => x.id === id)?.name).join(" · ") || "없음")}<br>실제: ${esc(
      rows
        .filter((x) => actual.includes(x.id))
        .map((x) => x.name)
        .join(" · ") || "없음",
    )}</p><p class="concept-notice">입력 ${rows.length}개 → ${esc(rule(mode))} → 결과 ${actual.length}개</p><table class="concept-table"><caption>각 항목이 남거나 빠진 근거</caption><thead><tr><th scope="col">항목</th><th scope="col">${esc(labels[0])}</th><th scope="col">${esc(labels[1])}</th><th scope="col">결과</th></tr></thead><tbody>${rows.map((x) => `<tr><th scope="row">${esc(x.name)}</th><td>${x.a ? "예" : "아니요"}</td><td>${x.b ? "예" : "아니요"}</td><td>${actual.includes(x.id) ? "포함" : "제외"}</td></tr>`).join("")}</tbody></table><p class="concept-muted">두 조건의 참·거짓으로 계산했습니다. 예상 일치는 이해도 평가가 아닙니다.</p></section>`;
  }
  let experiment = "guided";
  function render(focus = false) {
    const s = state,
      p = s.project;
    let body = `<div class="concept-toolbar">${btn("홈", "home")}${btn("SQL 학습", "sql-learning")}${btn("조건·관계·규칙 문제 선택", "bank")}</div><p class="concept-kicker">조건 탐구 · 한국어 · 내부 베타</p><h2 id="exploreHeading" tabindex="-1">${stages[s.stage]}${s.stage === 0 ? " — 함께 필요한 조건, 하나면 되는 조건" : ""}</h2><nav class="explore-steps" aria-label="탐구 단계">${stages.map((x, i) => `<button type="button" data-explore="stage" data-value="${i}" ${s.stage === i ? 'aria-current="step"' : ""}>${i + 1}. ${x}</button>`).join("")}</nav>`;
    if (s.stage === 0)
      body += `<p>‘빨강 <strong>그리고</strong> 원’과 ‘빨강 <strong>또는</strong> 원’은 같은 카드를 남길까요?</p><p>그리고는 두 조건이 모두 필요합니다. 또는은 하나만 맞아도 되고, 둘 다 맞아도 됩니다.</p><p class="concept-notice">먼저 카드로 확인하고, 책 고르기에 적용한 뒤 나만의 조건 퍼즐을 만듭니다. SQL·AI 설정은 필요하지 않습니다. 언제든 단계를 오가며 고칠 수 있습니다.</p>`;
    if (s.stage === 1) {
      const a = s[experiment],
        mode = experiment === "guided" ? "and" : "or";
      body += `<div class="concept-toolbar">${btn("안내형: 그리고", "experiment", "guided")}${btn("독립형: 또는", "experiment", "independent")}</div><h3>${experiment === "guided" ? "안내형 · 빨강 그리고 원" : "독립형 · 빨강 또는 원"}</h3><p>${experiment === "guided" ? "빨강인 것부터 보고, 그중 원인 것만 남겨 보세요." : "안내 없이 예상하세요. 두 조건을 모두 만족하는 카드도 포함할까요?"}</p>${selection(cards, a, ["빨강", "원"])}${btn("예상과 결과 비교", "run", "", true)}${result(cards, a, mode, ["빨강", "원"])}<p>기록: 안내형 ${s.guided.checked ? "실험함" : "미실험"} · 독립형 ${s.independent.checked ? "실험함" : "미실험"}</p>`;
    }
    if (s.stage === 2)
      body += `<p>“빨강이면 모두 ‘빨강 그리고 원’에 남는다”라는 주장을 깨는 카드를 찾아보세요.</p><div class="concept-cards">${cards.map((x) => `<button type="button" class="concept-card" data-explore="counter" data-value="${x.id}" aria-pressed="${s.counter === x.id}">${x.id} · ${x.a ? "빨강" : "파랑"} · ${x.b ? "원" : "네모"}</button>`).join("")}</div>${btn("반례 확인", "check-counter", "", true)}${s.counterChecked ? `<p class="concept-notice">${s.counter === "B" ? "B는 빨강이지만 원이 아닙니다. 빨강만으로 충분하다는 주장을 깨는 반례입니다." : s.counter === "A" ? "A는 두 조건을 모두 만족합니다. 주장을 깨려면 빨강인데도 제외되는 카드를 찾아보세요." : "이 카드는 빨강이 아닙니다. 주장에 포함된 빨강 카드 중에서 찾아보세요."}</p>` : ""}`;
    if (s.stage === 3)
      body += `<label>그리고와 또는의 차이를 내 말로 설명하기<textarea id="explore-notes" data-note="notes" maxlength="1500" placeholder="왜 B는 그리고에서 빠지고 또는에 남나요? 둘 다 맞는 A는요?">${esc(s.notes)}</textarea></label><p>스스로 확인: 두 조건 모두 / 하나 이상 / 둘 다 맞는 경우 / 반례를 포함했나요?</p><p class="concept-muted">입력은 자동 보존합니다. 문장의 길이나 특정 단어로 이해를 채점하지 않습니다. 별도 검토자가 아직 평가하지 않았습니다.</p>`;
    if (s.stage === 4)
      body += `<p>도서관에서 <strong>이야기책 또는 짧은 책</strong>을 찾습니다. 카드에서 쓴 규칙을 새로운 상황에 적용해 보세요.</p><label>비교할 조건<select id="explore-transfer-mode" data-field="transfer-mode"><option value="or" ${s.transfer.mode === "or" ? "selected" : ""}>이야기책 또는 짧은 책</option><option value="and" ${s.transfer.mode === "and" ? "selected" : ""}>이야기책 그리고 짧은 책</option></select></label>${selection(books, s.transfer, ["이야기책", "짧은 책"])}${btn("책 선택 실험", "run", "", true)}${result(books, s.transfer, s.transfer.mode, ["이야기책", "짧은 책"])}<label>처음 카드와 같은 점·달라진 점은 무엇인가요?<textarea data-note="transfer" maxlength="1500">${esc(s.transfer.notes)}</textarea></label>`;
    if (s.stage === 5)
      body += `<p>두 조건과 네 항목을 직접 바꿔 다른 사람이 예상해 볼 퍼즐을 만드세요. 빈 결과·모두 선택도 허용됩니다. 자유 문장은 실행 코드가 되지 않습니다.</p><label>퍼즐 제목<input data-project="title" maxlength="80" value="${esc(p.title)}"></label><div class="concept-tables"><label>조건 1 이름<input data-project="aLabel" maxlength="80" value="${esc(p.aLabel)}"></label><label>조건 2 이름<input data-project="bLabel" maxlength="80" value="${esc(p.bLabel)}"></label></div><label>규칙<select data-field="project-mode"><option value="and" ${p.mode === "and" ? "selected" : ""}>두 조건 모두 (그리고)</option><option value="or" ${p.mode === "or" ? "selected" : ""}>하나 이상 (또는)</option></select></label><fieldset><legend>항목별 조건을 바꾸기</legend>${p.rows.map((x, i) => `<div class="explore-edit-row"><label>${x.id} 이름<input data-row="${i}" data-prop="name" maxlength="80" value="${esc(x.name)}"></label><label class="concept-check"><input type="checkbox" aria-label="${x.id} · ${esc(p.aLabel)}" data-row="${i}" data-prop="a" ${x.a ? "checked" : ""}> 조건 1: 예</label><label class="concept-check"><input type="checkbox" aria-label="${x.id} · ${esc(p.bLabel)}" data-row="${i}" data-prop="b" ${x.b ? "checked" : ""}> 조건 2: 예</label></div>`).join("")}</fieldset>${btn("편집한 조건으로 예상 시작", "preview")}<div id="projectPreview">${selection(p.rows, p, [p.aLabel, p.bLabel])}</div>${btn("내 퍼즐 다시 실행", "run", "", true)}${result(p.rows, p, p.mode, [p.aLabel, p.bLabel])}<label>이 규칙의 의도와 반례 · 바꾸면 달라질 점<textarea data-note="project" maxlength="1500">${esc(p.notes)}</textarea></label><div class="concept-toolbar">${btn("퍼즐과 설명 저장", "save-project")}${btn("저장한 퍼즐 다시 풀기", "replay")}${btn("내 탐구 기록 삭제", "delete")}</div>${p.saved ? `<p id="projectSaved">${persistent ? "이 기기에" : "현재 탭에만 임시로"} 퍼즐과 설명을 저장했습니다. 위에서 수정하고 다시 실행할 수 있습니다.</p>` : ""}`;
    body += `<div class="concept-toolbar">${s.stage > 0 ? btn("이전 단계", "stage", s.stage - 1) : ""}${s.stage < 5 ? btn("다음: " + stages[s.stage + 1], "next", "", true) : btn("새 상황에서 다시 탐구", "stage", 4)}</div><details class="explore-record"><summary>내 탐구 기록 · 평가 전</summary><ul><li>안내형: ${s.guided.checked ? "실험함" : "미실험"}</li><li>독립형: ${s.independent.checked ? "실험함" : "미실험"}</li><li>반례: ${s.counterChecked ? "확인 시도함" : "미시도"}</li><li>자기 설명: ${s.notes.trim() ? "기록함" : "미기록"}</li><li>전이: ${s.transfer.checked ? "실험함" : "미실험"} / 설명 ${s.transfer.notes.trim() ? "기록함" : "미기록"}</li><li>창작: ${p.saved ? "저장함" : "편집 중 또는 미시작"}</li></ul><p>단계를 열거나 다음으로 이동한 것은 숙달·학습 완료가 아닙니다.</p></details><div class="concept-toolbar">${btn(help ? "도움 닫기" : "막혔을 때 도움", "help")}${btn(sql ? "SQL 표현 닫기" : "같은 규칙을 SQL로 보기", "sql")}</div>`;
    if (help)
      body += `<aside class="concept-notice"><h3>지금 생각할 질문</h3><p>${["조건 하나만 맞는 항목과 둘 다 맞는 항목을 찾아보세요.", "선택을 바꾸어도 괜찮습니다. 실제 표에서 예상과 다른 행을 찾아보세요.", "빨강이지만 원이 아닌 카드를 찾아보세요.", "B와 A를 예로 들어 두 규칙을 비교해 보세요.", "이야기책이면서 짧기도 한 책은 두 규칙에서 어떻게 될까요?", "조건 하나만 맞는 항목을 만들고 그리고·또는의 결과를 비교해 보세요."][s.stage]}</p><p>기기에 내장된 안내입니다. AI나 다른 사람에게 보내지 않습니다.</p></aside>`;
    if (sql) {
      const mode =
        s.stage === 4
          ? s.transfer.mode
          : s.stage === 5
            ? p.mode
            : experiment === "independent" && s.stage === 1
              ? "or"
              : "and";
      const rows = s.stage === 4 ? books : s.stage === 5 ? p.rows : cards;
      body += `<aside class="concept-notice"><h3>선택 경로 · SQL로 같은 조건 표현하기</h3><p>condition_1과 condition_2는 위 표의 예/아니요를 1/0으로 옮긴 값입니다. 아래 SQL은 표현 예시이며 이 화면에서 SQL 엔진으로 실행한 결과는 아닙니다.</p><pre class="explore-sql">${esc(`WITH items(id, condition_1, condition_2) AS (VALUES\n${rows.map((x) => `  ('${x.id}', ${+x.a}, ${+x.b})`).join(",\n")}\n)\nSELECT id FROM items\nWHERE condition_1 = 1 ${mode.toUpperCase()} condition_2 = 1\nORDER BY id;`)}</pre>${btn("기존 SQL 학습 시작 / 이어서하기", "sql-learning")}<p>SQL 학습 후 홈에서 조건 탐구를 다시 열면 기록한 단계로 돌아옵니다.</p></aside>`;
    }
    body += `<p id="exploreStatus" role="status">${esc(status)}</p><p id="exploreStorage" class="concept-muted" role="status">${persistent ? "기록은 이 브라우저/기기에만 보존됩니다." : "저장소를 사용할 수 없어 현재 탭에서만 유지합니다. 탭을 닫으면 사라집니다."} 서버 전송·기기 간 동기화는 없습니다. 실제 초보자·학생의 이해와 학습 효과는 미검증입니다.</p>`;
    host.innerHTML = body;
    if (focus) {
      host.querySelector("#exploreHeading").focus({ preventScroll: true });
      document.getElementById("terminalScroll")?.scrollTo(0, 0);
    }
  }
  function go(n) {
    state.stage = n;
    if (!state.visited.includes(n)) state.visited.push(n);
    status = "";
    save();
    render(true);
  }
  host.addEventListener("click", (e) => {
    const b = e.target.closest("[data-explore]");
    if (!b) return;
    const a = b.dataset.explore,
      v = b.dataset.value;
    if (a === "home") {
      close();
      document.getElementById("explorationButton").focus();
      return;
    }
    if (a === "sql-learning") {
      close();
      document.getElementById("firstProblemButton").click();
      return;
    }
    if (a === "bank") {
      close();
      document.getElementById("conceptPuzzlesButton").click();
      return;
    }
    if (a === "stage") {
      go(Number(v));
      return;
    }
    if (a === "next") {
      const s = state,
        ready =
          s.stage === 0 ||
          (s.stage === 1 && s.guided.checked && s.independent.checked) ||
          (s.stage === 2 && s.counterChecked && s.counter === "B") ||
          (s.stage === 3 && s.notes.trim()) ||
          (s.stage === 4 && s.transfer.checked && s.transfer.notes.trim());
      if (!ready) {
        announce(
          [
            "",
            "안내형과 독립형을 모두 실험해 보세요.",
            "주장을 깨는 반례를 다시 확인해 보세요.",
            "내 말로 설명을 남겨 보세요.",
            "책 선택 실험과 설명을 남겨 보세요.",
          ][s.stage],
        );
        return;
      }
      go(s.stage + 1);
      return;
    }
    if (a === "experiment") {
      experiment = v;
      status = "";
      render(true);
      return;
    }
    const attempt =
      state.stage === 4
        ? state.transfer
        : state.stage === 5
          ? state.project
          : state[experiment];
    if (a === "select") {
      attempt.selected = attempt.selected.includes(v)
        ? attempt.selected.filter((x) => x !== v)
        : [...attempt.selected, v];
      attempt.checked = false;
      if (state.stage === 5) state.project.saved = false;
    }
    if (a === "run") attempt.checked = true;
    if (a === "counter") {
      state.counter = v;
      state.counterChecked = false;
    }
    if (a === "check-counter") {
      if (!state.counter) {
        announce("먼저 카드를 골라 보세요.");
        return;
      }
      state.counterChecked = true;
    }
    if (a === "help") help = !help;
    if (a === "sql") sql = !sql;
    if (a === "preview") {
      state.project.checked = false;
      state.project.saved = false;
    }
    if (a === "save-project") {
      const p = state.project;
      if (
        !p.checked ||
        !p.notes.trim() ||
        ![p.title, p.aLabel, p.bLabel, ...p.rows.map((x) => x.name)].every(
          (x) => x.trim(),
        )
      ) {
        announce(
          "제목·조건·항목 이름을 채우고, 다시 실행한 뒤 의도와 반례를 기록하세요.",
        );
        return;
      }
      p.saved = true;
      state.savedProject = JSON.parse(JSON.stringify(p));
      status = "퍼즐과 설명을 저장했습니다.";
    }
    if (a === "replay") {
      if (!state.savedProject) {
        announce("퍼즐을 먼저 실행하고 저장하세요.");
        return;
      }
      state.project = JSON.parse(JSON.stringify(state.savedProject));
      state.project.selected = [];
      state.project.checked = false;
      status = "저장한 규칙을 불러왔습니다. 결과를 다시 예상해 보세요.";
    }
    if (a === "delete") {
      state = fresh();
      try {
        localStorage.removeItem(KEY);
      } catch {
        persistent = false;
      }
      status =
        "조건 탐구 기록만 지웠습니다. SQL과 기존 퍼즐 기록은 유지됩니다.";
      render(true);
      return;
    }
    save();
    if (a === "save-project" && !persistent)
      status = "현재 탭에만 임시 저장했습니다. 탭을 닫으면 사라집니다.";
    render();
    const target =
      a === "run" ? host.querySelector("#exploreResultHeading") : null;
    if (target) {
      target.focus({ preventScroll: true });
      target.scrollIntoView({ block: "center" });
    } else {
      const replacement = [...host.querySelectorAll("[data-explore]")].find(
        (x) => x.dataset.explore === a && x.dataset.value === v,
      );
      replacement?.focus({ preventScroll: true });
    }
  });
  host.addEventListener("input", (e) => {
    const t = e.target;
    if (t.dataset.note) {
      if (t.dataset.note === "notes") state.notes = t.value;
      else if (t.dataset.note === "project") {
        state.project.notes = t.value;
        state.project.saved = false;
        host.querySelector("#projectSaved")?.remove();
      } else state.transfer.notes = t.value;
      save();
      return;
    }
    if (t.dataset.project) {
      state.project[t.dataset.project] = t.value;
      invalidateProject();
      save();
    }
    if (t.dataset.row !== undefined && t.dataset.prop === "name") {
      state.project.rows[Number(t.dataset.row)].name = t.value;
      invalidateProject();
      save();
    }
  });
  host.addEventListener("change", (e) => {
    const t = e.target;
    if (t.dataset.field === "transfer-mode") {
      state.transfer.mode = t.value;
      state.transfer.checked = false;
      state.transfer.selected = [];
    }
    if (t.dataset.field === "project-mode") {
      state.project.mode = t.value;
      invalidateProject();
    }
    if (t.dataset.row !== undefined && ["a", "b"].includes(t.dataset.prop)) {
      state.project.rows[Number(t.dataset.row)][t.dataset.prop] = t.checked;
      invalidateProject();
    }
    if (t.dataset.field || t.type === "checkbox") {
      const field = t.dataset.field,
        row = t.dataset.row,
        prop = t.dataset.prop;
      save();
      render();
      [...host.querySelectorAll("select,input")]
        .find((x) =>
          field
            ? x.dataset.field === field
            : x.dataset.row === row && x.dataset.prop === prop,
        )
        ?.focus({ preventScroll: true });
    }
  });
  document.getElementById("explorationButton")?.addEventListener("click", open);
  [
    "homeButton",
    "firstProblemButton",
    "problemBankButton",
    "advancedWorkspaceButton",
    "conceptPuzzlesButton",
  ].forEach((id) =>
    document.getElementById(id)?.addEventListener("click", close),
  );
})(globalThis);
