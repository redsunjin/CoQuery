(function (root) {
  const VIEW_ORDER = ["table", "visual", "flow", "explain"];
  const copy = {
    ko: {
      groupLabel: "쿼리 결과 보기",
      table: "표",
      visual: "시각화",
      flow: "흐름",
      explain: "해설",
    },
    en: {
      groupLabel: "Query result views",
      table: "Table",
      visual: "Visual",
      flow: "Flow",
      explain: "Explain",
    },
  };

  let viewInstance = 0;

  function currentLanguage() {
    if (typeof document === "undefined") return "en";
    return document.documentElement.lang === "en" ? "en" : "ko";
  }

  function text(key) {
    const lang = currentLanguage();
    return copy[lang]?.[key] || copy.en[key] || key;
  }

  function availableViewNames(flags = {}) {
    return VIEW_ORDER.filter((name) => name === "table" ? flags.table !== false : Boolean(flags[name]));
  }

  function nextViewIndex(count, currentIndex, key) {
    if (!Number.isInteger(count) || count <= 0) return -1;
    const current = Math.max(0, Math.min(count - 1, Number(currentIndex) || 0));
    if (key === "Home") return 0;
    if (key === "End") return count - 1;
    if (key === "ArrowRight" || key === "ArrowDown") return (current + 1) % count;
    if (key === "ArrowLeft" || key === "ArrowUp") return (current - 1 + count) % count;
    return current;
  }

  function elementsForBlock(block) {
    const table = block?.querySelector("[data-practice-result-table] .practice-result-table-scroll") || null;
    const visual = block?.querySelector("[data-practice-bar-visual], [data-practice-line-visual]") || null;
    const flow = block?.querySelector("[data-practice-query-flow]") || null;
    const explain = block?.querySelector("[data-practice-result-explain]") || null;
    return { table, visual, flow, explain };
  }

  function availableForElements(elements) {
    return availableViewNames({
      table: Boolean(elements.table),
      visual: Boolean(elements.visual),
      flow: Boolean(elements.flow),
      explain: Boolean(elements.explain),
    });
  }

  function activateView(block, name, focusTab = false) {
    const switcher = block?.querySelector("[data-practice-result-view-switcher]");
    if (!block || !switcher) return;
    const elements = elementsForBlock(block);
    const names = availableForElements(elements);
    const selected = names.includes(name) ? name : "table";
    block.dataset.practiceResultViewSelected = selected;

    switcher.querySelectorAll("[role=tab]").forEach((tab) => {
      const active = tab.dataset.practiceResultView === selected;
      tab.setAttribute("aria-selected", active ? "true" : "false");
      tab.tabIndex = active ? 0 : -1;
      if (active && focusTab) tab.focus();
    });

    names.forEach((viewName) => {
      const panel = elements[viewName];
      if (!panel) return;
      const active = viewName === selected;
      panel.hidden = !active;
      panel.tabIndex = active ? 0 : -1;
    });
  }

  function ensurePanelSemantics(block, switcher, elements, names) {
    if (!block.dataset.practiceResultViewInstance) {
      viewInstance += 1;
      block.dataset.practiceResultViewInstance = String(viewInstance);
    }
    const instance = block.dataset.practiceResultViewInstance;
    names.forEach((name) => {
      const panel = elements[name];
      if (!panel) return;
      const panelId = `practice-result-${instance}-${name}-panel`;
      const tabId = `practice-result-${instance}-${name}-tab`;
      panel.id = panelId;
      panel.dataset.practiceResultViewPanel = "true";
      panel.setAttribute("role", "tabpanel");
      panel.setAttribute("aria-labelledby", tabId);
      const tab = switcher.querySelector(`[data-practice-result-view="${name}"]`);
      if (tab) {
        tab.id = tabId;
        tab.setAttribute("aria-controls", panelId);
      }
    });
  }

  function refreshSwitcherCopy(block) {
    const switcher = block?.querySelector("[data-practice-result-view-switcher]");
    if (!switcher) return;
    switcher.setAttribute("aria-label", text("groupLabel"));
    switcher.querySelectorAll("[data-practice-result-view]").forEach((tab) => {
      tab.textContent = text(tab.dataset.practiceResultView);
    });
  }

  function renderSwitcher(block) {
    if (!block?.__result?.ok || block.__result.command !== "practice_query") return;
    const tableWrap = block.querySelector("[data-practice-result-table]");
    if (!tableWrap) return;

    const elements = elementsForBlock(block);
    const names = availableForElements(elements);
    if (!elements.table || names.length < 2) return;

    const signature = names.join("|");
    let switcher = block.querySelector("[data-practice-result-view-switcher]");
    if (!switcher) {
      switcher = document.createElement("div");
      switcher.className = "practice-result-view-switcher";
      switcher.dataset.practiceResultViewSwitcher = "true";
      switcher.setAttribute("role", "tablist");
      switcher.setAttribute("aria-orientation", "horizontal");
      switcher.addEventListener("keydown", (event) => {
        if (!["ArrowRight", "ArrowLeft", "ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
        const tabs = [...switcher.querySelectorAll("[role=tab]")];
        const currentIndex = Math.max(0, tabs.indexOf(document.activeElement));
        const nextIndex = nextViewIndex(tabs.length, currentIndex, event.key);
        if (nextIndex < 0) return;
        event.preventDefault();
        activateView(block, tabs[nextIndex].dataset.practiceResultView, true);
      });
      const evidence = tableWrap.querySelector("[data-practice-result-evidence]");
      if (evidence) evidence.insertAdjacentElement("afterend", switcher);
      else tableWrap.prepend(switcher);
    }

    if (switcher.dataset.practiceResultViewSignature !== signature) {
      switcher.dataset.practiceResultViewSignature = signature;
      switcher.replaceChildren();
      names.forEach((name) => {
        const tab = document.createElement("button");
        tab.type = "button";
        tab.className = "practice-result-view-tab";
        tab.dataset.practiceResultView = name;
        tab.setAttribute("role", "tab");
        tab.setAttribute("aria-selected", "false");
        tab.tabIndex = -1;
        tab.addEventListener("click", () => activateView(block, name, false));
        switcher.appendChild(tab);
      });
    }

    refreshSwitcherCopy(block);
    ensurePanelSemantics(block, switcher, elements, names);
    const selected = names.includes(block.dataset.practiceResultViewSelected)
      ? block.dataset.practiceResultViewSelected
      : "table";
    activateView(block, selected, false);
  }

  function enhanceExisting() {
    document.querySelectorAll("#terminalScroll .terminal-block").forEach(renderSwitcher);
  }

  const api = { availableViewNames, nextViewIndex };
  root.coqueryPracticeResultViews = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof document === "undefined") return;

  const scroll = document.getElementById("terminalScroll");
  const pending = new WeakSet();
  function schedule(block) {
    if (!block || pending.has(block)) return;
    pending.add(block);
    requestAnimationFrame(() => {
      pending.delete(block);
      renderSwitcher(block);
    });
  }

  if (scroll && typeof MutationObserver !== "undefined") {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        const targetBlock = mutation.target instanceof Element ? mutation.target.closest(".terminal-block") : null;
        if (targetBlock) schedule(targetBlock);
        mutation.addedNodes.forEach((node) => {
          if (!(node instanceof HTMLElement)) return;
          if (node.matches(".terminal-block")) schedule(node);
          const nestedBlock = node.closest?.(".terminal-block");
          if (nestedBlock) schedule(nestedBlock);
          node.querySelectorAll?.(".terminal-block").forEach(schedule);
        });
      });
    });
    observer.observe(scroll, { childList: true, subtree: true });
  }

  requestAnimationFrame(enhanceExisting);
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => requestAnimationFrame(() => {
      document.querySelectorAll(".terminal-block").forEach(refreshSwitcherCopy);
    }));
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
