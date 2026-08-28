(() => {
  const STORAGE_KEY = "coquery_pwa_practice_attempts_v1";

  function readAttempts() {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  function writeAttempts(attempts) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(attempts.slice(-1000)));
  }

  function saveGradeAttempt(result, args = {}) {
    const data = result?.data || {};
    if (!result?.ok || result.command !== "practice_grade") return;

    const attempt = {
      timestamp: new Date().toISOString(),
      pack_id: data.pack_id || args.pack || "sql_basics",
      problem_id: data.problem?.id || args.problem_id || "",
      problem_title: data.problem?.title || args.problem_id || "",
      correct: data.correct === true,
      sql: args.sql || "",
      actual_row_count: data.actual?.row_count ?? 0,
      expected_row_count: data.expected?.row_count ?? 0,
    };
    if (data.wrong_note) attempt.wrong_note = data.wrong_note;

    const attempts = readAttempts();
    attempts.push(attempt);
    writeAttempts(attempts);

    data.attempt_recorded = true;
    data.attempt_log_path = "browser:localStorage";
  }

  function localAttemptsResult(args = {}) {
    const pack = args.pack || null;
    const problemId = args.problem_id || null;
    const limit = Number.isFinite(Number(args.limit)) ? Math.max(0, Number(args.limit)) : 20;
    let attempts = readAttempts();
    if (pack) attempts = attempts.filter((item) => item.pack_id === pack);
    if (problemId) attempts = attempts.filter((item) => item.problem_id === problemId);
    attempts = attempts.slice(-limit);
    return {
      ok: true,
      command: "practice_attempts",
      block_type: "practice_attempts",
      actions: ["copy", "review_wrong_notes"],
      cli_equivalent: "browser localStorage",
      data: {
        attempt_log_path: "browser:localStorage",
        pack_id: pack,
        problem_id: problemId,
        limit,
        attempts,
        attempt_count: attempts.length,
      },
      error: null,
    };
  }

  async function networkCommand(command, args = {}, context = {}) {
    const safeArgs = { ...args };
    if (command === "practice_grade") safeArgs.no_record = true;

    const response = await fetch("/api/commands/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command, args: safeArgs, context }),
    });
    const result = await response.json();
    if (command === "practice_grade") saveGradeAttempt(result, args);
    return result;
  }

  window.coqueryCommandRuntime = window.coqueryCommandRuntime || {};
  window.coqueryCommandRuntime.initialCommand = window.coqueryCommandRuntime.initialCommand || "practice_list";
  window.coqueryCommandRuntime.postCommand = async (command, args = {}, context = {}) => {
    if (command === "practice_attempts") return localAttemptsResult(args);
    return networkCommand(command, args, context);
  };

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("./service-worker.js").catch((error) => {
        console.warn("CoQuery service worker registration failed", error);
      });
    });
  }
})();
