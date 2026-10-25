/* Optional concept learning surface. SQL runtime and SQL progress are unchanged. */
(function () {
  "use strict";
  const host = document.getElementById("conceptLearning");
  const shell = document.querySelector(".app-shell");
  const api = window.CoqueryPuzzles;
  if (!host || !shell || !api) return;
  const key = "coquery.concept-puzzles.v1";
  const types = { condition: "조건 탐정", relation: "관계 연결", rule: "규칙 바꾸기" };
  let records = {}, current = null, filter = "all", storageAvailable = true;
  try {
    const parsed = JSON.parse(localStorage.getItem(key) || "{}");
    for (const p of api.puzzles) {
      const a = parsed[p.id];
      if (!a || a.version !== p.version) continue;
      records[p.id] = { ...api.fresh(), notes: typeof a.notes === "string" ? a.notes.slice(0,1500) : "", recorded: a.recorded === true, seen: Array.isArray(a.seen) ? a.seen.filter(x => ["base","strict","id"].includes(x)) : [], rules: Array.isArray(a.rules) ? a.rules.filter(x => p.type === "rule" && p.allowedRules.some(r => r.min === x.min && r.newOnly === x.newOnly)).map(x => ({ min:x.min, newOnly:x.newOnly })) : [] };
    }
  } catch { storageAvailable = false; }
  const esc = value => String(value).replace(/[&<>"']/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]));
  const button = (text, action, value = "", primary = false) => `<button type="button" class="${primary ? "primary-button" : "ghost-button"}" data-concept-action="${action}" data-value="${esc(value)}">${text}</button>`;
  const table = (heads, rows) => `<table class="concept-table"><thead><tr>${heads.map(x=>`<th scope="col">${esc(x)}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(x=>`<td>${esc(x)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
  const attempt = () => records[current] || (records[current] = api.fresh());
  function save() {
    try {
      const data = {};
      for (const p of api.puzzles) if (records[p.id]) { const a = records[p.id]; data[p.id] = { version:p.version, notes:a.notes, recorded:a.recorded, seen:a.seen, rules:a.rules }; }
      localStorage.setItem(key,JSON.stringify(data));
    } catch { storageAvailable = false; }
  }
  function open() { current = null; setLearningHomeMode(true); shell.dataset.conceptOpen = "true"; host.hidden = false; render(true); }
  function close() { shell.dataset.conceptOpen = "false"; host.hidden = true; document.getElementById("conceptPuzzlesButton")?.focus({preventScroll:true}); document.getElementById("terminalScroll")?.scrollTo(0,0); }
  function render(moveFocus = false) {
    const focused = document.activeElement?.id;
    let content = `<div class="concept-toolbar">${button("SQL 학습 홈", "home")}${current ? button("9개 문제 선택", "list") : ""}${button("개념 기록 지우기", "reset")}</div>`;
    content += `<p class="concept-kicker">개념 퍼즐 · 한국어 콘텐츠</p><h2 tabindex="-1" id="conceptHeading">${current ? esc(api.puzzles.find(x=>x.id===current).title) : "조건·관계·규칙을 직접 확인해 보세요."}</h2>`;
    if (!current) {
      content += `<p class="concept-muted">SQL 문법 없이 시작하는 9문제입니다. 기존 SQL 학습은 ‘SQL 학습 홈’에서 계속할 수 있습니다.</p><nav class="concept-toolbar" aria-label="퍼즐 유형">${[["all","전체"],...Object.entries(types)].map(([id,t])=>button(t,"filter",id)).join("")}</nav><div class="concept-bank">`;
      for (const p of api.puzzles.filter(p=>filter==="all"||p.type===filter)) {
        const a=records[p.id];
        const status = a?.recorded ? (api.coverage(p,a) ? "설명 기록 · 필수 실험 확인" : "설명 기록 · 추가 실험 필요") : a?.seen.length ? "실험 확인 · 설명 미기록" : "미시도";
        content += `<button class="concept-problem" data-concept-action="open" data-value="${p.id}"><span>${p.id} · ${p.level} · ${types[p.type]}</span><strong>${esc(p.title)}</strong><small>${status}</small></button>`;
      }
      content += `</div><aside class="concept-simulation"><strong>참여형 기능은 별도의 모의 체험입니다.</strong><p>실제 AI·서버·다른 참여자와 연결되지 않습니다. 개념 학습 기록도 공유하지 않습니다.</p><a class="ghost-button" href="./community-demo.html">참여형 모의 체험 열기</a></aside>`;
    } else content += problem(api.puzzles.find(x=>x.id===current),attempt());
    content += `<p class="concept-muted concept-storage" role="status">${storageAvailable ? "개념 기록과 자기 설명은 이 브라우저/기기에만 저장됩니다. SQL 기록과 분리되며 서버로 보내지 않습니다." : "이 환경에서는 저장소를 사용할 수 없어 현재 탭에서만 기록을 유지합니다."} 실험·설명 기록은 숙달 평가가 아닙니다.</p>`;
    host.innerHTML = content;
    if (moveFocus) { host.querySelector("#conceptHeading").focus({preventScroll:true}); document.getElementById("terminalScroll")?.scrollTo(0,0); }
    else if (focused) document.getElementById(focused)?.focus({preventScroll:true});
  }
  function numeric(label, name, value) { return `<label>${label}<input id="concept-${name}" type="number" name="${name}" min="0" max="20" step="1" required value="${esc(value)}"></label>`; }
  function problem(p,a) {
    let html=`<p class="concept-kicker">${p.id} · ${p.level} · ${types[p.type]}</p><p>${esc(p.prompt)}</p><form id="conceptExperiment">`;
    if(p.id==="C3"||p.id==="R3") html+=`<label>비교할 기준<select id="concept-variant" data-concept-field="variant">${(p.id==="C3"?[["base","10 이상"],["strict","10 초과"]]:[["base","이름 ↔ 이름"],["id","회원 ID ↔ 회원 ID"]]).map(([v,t])=>`<option value="${v}" ${a.variant===v?"selected":""}>${t}</option>`).join("")}</select></label>`;
    if(p.type==="condition")html+=`<div class="concept-cards">${p.data.map(x=>`<button type="button" id="concept-card-${x.id}" class="concept-card" data-concept-action="select" data-value="${x.id}" aria-pressed="${a.selected.includes(x.id)}"><strong>${x.id}</strong><span>${x.score===undefined?`${x.color} · ${x.shape}`:`${x.score}점`}</span></button>`).join("")}</div><p class="concept-muted">남을 것으로 예상하는 카드를 모두 선택하세요. 빈 결과도 확인할 수 있습니다.</p>`;
    if(p.type==="relation")html+=`<div class="concept-tables">${table(["회원 ID","이름"],p.data.members.map(x=>[x.id,x.name]))}${table(["대여 ID","회원 ID","책"],p.data.loans.map(x=>[x.id,x.member_id,x.book]))}</div>${numeric("예상 결과 행 수","prediction",a.prediction)}`;
    if(p.type==="rule")html+=`${table(["신청자","점수","이력"],p.data.map(x=>[x.name,x.score,x.new?"신규":"기존"]))}<div class="concept-rule"><label>점수 기준<select id="concept-min" data-concept-field="min">${[1,2,3,4].map(n=>`<option value="${n}" ${a.min===n?"selected":""}>${n}점 이상</option>`).join("")}</select></label><label class="concept-check"><input id="concept-newOnly" type="checkbox" data-concept-field="newOnly" ${a.newOnly?"checked":""}> 신규만 선택</label></div><div class="concept-tables">${numeric("예상 선택 인원","total",a.total)}${numeric("그중 예상 신규 인원","newcomers",a.newcomers)}</div>`;
    html+=`<div class="concept-toolbar"><button class="primary-button" type="submit">예상과 결과 확인</button>${button(a.hint?"힌트 닫기":"힌트","hint")}</div></form>${a.hint?`<p class="concept-notice">${esc(p.hint)}</p>`:""}`;
    if(a.checked) {
      const r=api.evaluate(p,a);const same=p.type==="condition"?a.selected.length===r.length&&r.every(x=>a.selected.includes(x)):p.type==="relation"?Number(a.prediction)===r.length:Number(a.total)===r.selected.length&&Number(a.newcomers)===r.newcomers;
      html+=`<section id="conceptResult" class="concept-result" aria-live="polite"><h3 id="conceptResultHeading" tabindex="-1">${same?"예상과 결과가 같아요.":"차이를 발견했어요."}</h3>`;
      if(p.type==="condition")html+=table(["내 예상","실제 결과"],[[a.selected.join(" · ")||"없음",r.join(" · ")||"없음"]]);
      if(p.type==="relation")html+=`<p>내 예상 ${esc(a.prediction)}행 / 실제 ${r.length}행</p>${table(["회원","책"],r)}`;
      if(p.type==="rule")html+=`<p>내 예상 ${esc(a.total)}명 / 신규 ${esc(a.newcomers)}명</p><p>실제 ${r.selected.map(x=>x.name).join(" · ")||"없음"} · ${r.selected.length}명 / 신규 ${r.newcomers}명</p><p class="concept-notice">${r.ok?"이 데이터에서 목표를 충족합니다.":"목표 또는 정원 조건을 충족하지 못했습니다."}</p><p>발견한 대안 ${a.rules.length}개</p><ul>${a.rules.map(x=>`<li>${x.min}점 이상${x.newOnly?" · 신규만":""}</li>`).join("")}</ul>`;
      html+=`<p>${esc(p.explanation)}</p><details><summary>반례와 설명 검토 기준</summary><p>${esc(p.counter)}</p><p>${esc(p.rubric)}</p></details><p class="concept-notice">${api.coverage(p,a)?"필수 실험 범위를 확인했습니다.":"추가 실험이 필요합니다. "+(p.id==="U3"?"서로 다른 대안 2개를 확인하세요.":p.id==="C3"||p.id==="R3"?"두 기준을 모두 확인하세요.":"목표를 충족하는 규칙을 확인하세요.")}</p></section>`;
    }
    html+=`<form id="conceptExplanation"><label>내 말로 설명하기<textarea id="concept-notes" maxlength="1500" name="notes" placeholder="왜 이런 결과가 나왔나요? 반례도 생각해 보세요.">${esc(a.notes)}</textarea></label><p class="concept-muted">자동 채점하거나 AI에 보내지 않습니다. 결과 확인과 자기 설명은 별개입니다.</p><button class="ghost-button" type="submit">설명 기록하기</button>${a.recorded?'<p id="conceptRecorded">설명을 기록했습니다. 검토자의 평가 전입니다.</p>':""}</form>`;
    return html;
  }
  host.addEventListener("click",event=> {
    const b=event.target.closest("[data-concept-action]");if(!b)return;
    const action=b.dataset.conceptAction,v=b.dataset.value;
    if(action==="home"){close();return;}
    if(action==="reset"){records={};try{localStorage.removeItem(key);}catch{storageAvailable=false;}render(true);return;}
    if(action==="filter"){filter=v;render();return;}
    if(action==="list"){current=null;render(true);return;}
    if(action==="open"){current=v;render(true);return;}
    const a=attempt();
    if(action==="select"){a.selected=a.selected.includes(v)?a.selected.filter(x=>x!==v):[...a.selected,v];a.checked=false;}
    if(action==="hint")a.hint=!a.hint;
    render();
  });
  host.addEventListener("change",event=> {
    const field=event.target.dataset.conceptField;if(!field)return;
    const a=attempt();a[field]=field==="min"?Number(event.target.value):field==="newOnly"?event.target.checked:event.target.value;a.checked=false;render();
  });
  host.addEventListener("input",event=> {
    if(!current)return;const a=attempt();
    if(event.target.name==="notes"){a.notes=event.target.value;a.recorded=false;host.querySelector("#conceptRecorded")?.remove();save();}
    else if(["prediction","total","newcomers"].includes(event.target.name)){a[event.target.name]=event.target.value;a.checked=false;host.querySelector("#conceptResult")?.remove();}
  });
  host.addEventListener("submit",event=> {
    event.preventDefault();const a=attempt(),p=api.puzzles.find(x=>x.id===current);
    if(event.target.id==="conceptExplanation"){if(!a.notes.trim())return;a.recorded=true;}
    else {
      a.checked=true;if(!a.seen.includes(a.variant))a.seen.push(a.variant);
      const r=api.evaluate(p,a);if(p.type==="rule"&&r.ok&&!a.rules.some(x=>x.min===a.min&&x.newOnly===a.newOnly))a.rules.push({min:a.min,newOnly:a.newOnly});
    }
    save();render();
    const resultTarget=event.target.id==="conceptExplanation"?host.querySelector("#conceptRecorded"):host.querySelector("#conceptResultHeading");
    if(resultTarget){resultTarget.setAttribute("tabindex","-1");resultTarget.scrollIntoView({block:"center"});resultTarget.focus({preventScroll:true});}
  });
  document.getElementById("conceptPuzzlesButton")?.addEventListener("click",open);
  // Existing home/SQL commands must be able to close the optional surface.
  ["homeButton","firstProblemButton","problemBankButton","advancedWorkspaceButton"].forEach(id=>document.getElementById(id)?.addEventListener("click",()=>{shell.dataset.conceptOpen="false";host.hidden=true;}));
  window.coqueryConceptState=()=>({current,filter,records,storageAvailable});
})();
