const SQL_BASICS_PACK = __COQUERY_SQL_BASICS_PACK__;

const BLOCK_TYPES = {
  practice_list: "practice_list",
  practice_schema: "practice_schema",
  practice_attempts: "practice_attempts",
  practice_feedback: "practice_feedback",
};

const ACTIONS = {
  practice_list: ["copy", "start_practice", "show_schema"],
  practice_schema: ["copy", "insert_template", "start_practice"],
  practice_attempts: ["copy", "review_wrong_notes"],
  practice_feedback: ["copy", "retry", "request_provider_feedback"],
};

function quoteCliValue(value) {
  const text = String(value ?? "");
  if (!text) {
    return '""';
  }
  if (/^[A-Za-z0-9._\-/:@]+$/.test(text)) {
    return text;
  }
  return `"${text.replaceAll("\\", "\\\\").replaceAll('"', '\\"')}"`;
}

function buildCliEquivalent(command, args = {}, context = {}) {
  const merged = { ...context, ...args };
  const parts = ["python", "main.py", "--command", command];
  for (const [key, flag] of [
    ["pack", "--pack"],
    ["table", "--table"],
    ["problem_id", "--problem-id"],
    ["sql", "--sql"],
    ["provider_name", "--provider-name"],
    ["mode", "--mode"],
    ["limit", "--limit"],
  ]) {
    if (merged[key] !== undefined && merged[key] !== null && merged[key] !== "") {
      parts.push(flag, quoteCliValue(merged[key]));
    }
  }
  parts.push("--format", "json");
  return parts.join(" ");
}

function enrich(result, args = {}, context = {}) {
  const command = result.command || "";
  return {
    ok: false,
    data: {},
    error: null,
    ...result,
    block_type: BLOCK_TYPES[command] || "command_result",
    actions: ACTIONS[command] || ["copy"],
    cli_equivalent: buildCliEquivalent(command, args, context),
  };
}

function errorResult(command, code, message, args = {}, context = {}, data = {}) {
  return enrich(
    {
      ok: false,
      command,
      data,
      error: { code, message },
    },
    args,
    context
  );
}

function packSummary(pack) {
  const tables = pack.dataset?.tables || [];
  const problems = pack.problems || [];
  return {
    id: pack.id,
    title: pack.title,
    description: pack.description || "",
    dataset_id: pack.dataset?.id,
    table_count: tables.length,
    problem_count: problems.length,
    path: "local://coquery/practice_packs/sql_basics.json",
  };
}

function problemSummaries(pack) {
  return (pack.problems || []).map((problem) => ({
    id: problem.id,
    title: problem.title,
    difficulty: problem.difficulty,
    prompt: problem.prompt,
    concepts: problem.concepts || [],
    hint: problem.hint,
  }));
}

function tableSummaries(pack, tableName) {
  const tables = pack.dataset?.tables || [];
  const filtered = tableName ? tables.filter((table) => table.name === tableName) : tables;
  if (tableName && filtered.length === 0) {
    throw new Error(`Table not found in practice pack: ${tableName}.`);
  }
  return filtered.map((table) => ({
    name: table.name,
    description: table.description || "",
    columns: table.columns || [],
    primary_key: table.primary_key || [],
    foreign_keys: table.foreign_keys || [],
    row_count: (table.rows || []).length,
  }));
}

function problemById(pack, problemId) {
  const selectedId = problemId || "basic_select_customers";
  return (pack.problems || []).find((problem) => problem.id === selectedId) || null;
}

function problemPayload(problem) {
  return {
    id: problem.id,
    title: problem.title,
    difficulty: problem.difficulty,
    prompt: problem.prompt,
    concepts: problem.concepts || [],
    hint: problem.hint,
  };
}

function selectColumns(sql) {
  const match = String(sql || "").match(/^\s*select\s+([\s\S]+?)\s+from\s+/i);
  if (!match) {
    return [];
  }
  return match[1]
    .split(",")
    .map((item) => item.trim().replace(/\s+as\s+.+$/i, "").split(".").pop())
    .filter(Boolean);
}

function expectedIssue(problem, submittedSql) {
  const expectedColumns = selectColumns(problem.expected_sql);
  const actualColumns = selectColumns(submittedSql);
  const missing = expectedColumns.filter((column) => !actualColumns.includes(column));
  if (missing.length > 0) {
    return `Expected column(s) missing from the result: ${missing.join(", ")}.`;
  }
  return "Static iOS feedback can inspect the submitted SQL shape. Compare the expected SELECT list, filters, joins, grouping, and ordering.";
}

function staticWrongNote(pack, problem, submittedSql) {
  const issue = expectedIssue(problem, submittedSql);
  const message = `${issue} Retry by adjusting the submitted SQL, then run practice_grade again.`;
  return {
    pack_id: pack.id,
    problem_id: problem.id,
    problem_title: problem.title,
    prompt: problem.prompt,
    submitted_sql: submittedSql,
    expected_issue: issue,
    static_feedback: {
      source: "static",
      label: "Static feedback",
      message,
      ai_generated: false,
    },
    retry_action: {
      label: "Retry",
      command: "practice_start",
      pack_id: pack.id,
      problem_id: problem.id,
      sql: submittedSql,
    },
    provider_feedback: {
      available: true,
      mode_required: "training",
      request_command: "practice_feedback",
      label: "AI-generated feedback",
    },
  };
}

function practiceList(pack, args = {}, context = {}) {
  return enrich(
    {
      ok: true,
      command: "practice_list",
      data: {
        packs: [packSummary(pack)],
        selected_pack: pack.id,
        problems: problemSummaries(pack),
        examples: pack.examples || [],
      },
      error: null,
    },
    args,
    context
  );
}

function practiceSchema(pack, args = {}, context = {}) {
  const table = args.table || context.table;
  try {
    const tables = tableSummaries(pack, table);
    return enrich(
      {
        ok: true,
        command: "practice_schema",
        data: {
          pack_id: pack.id,
          dataset_id: pack.dataset?.id,
          dataset_title: pack.dataset?.title,
          table_count: tables.length,
          tables,
        },
        error: null,
      },
      args,
      context
    );
  } catch (error) {
    return errorResult("practice_schema", "practice_table_not_found", error.message, args, context, {
      pack: pack.id,
      available_tables: (pack.dataset?.tables || []).map((item) => item.name),
    });
  }
}

function practiceAttempts(pack, attempts, args = {}, context = {}) {
  const problemId = args.problem_id || context.problem_id;
  const limit = Number(args.limit || context.limit || 20);
  const filtered = attempts
    .filter((attempt) => !problemId || attempt.problem_id === problemId)
    .slice(-Math.max(0, limit));
  return enrich(
    {
      ok: true,
      command: "practice_attempts",
      data: {
        attempt_log_path: "local://coquery/practice_attempts",
        pack_id: pack.id,
        problem_id: problemId || null,
        limit,
        attempts: filtered,
        attempt_count: filtered.length,
      },
      error: null,
    },
    args,
    context
  );
}

function practiceFeedback(pack, args = {}, context = {}) {
  const providerName = args.provider_name || context.provider_name || "";
  const mode = String(args.mode || context.mode || "static").toLowerCase();
  if (providerName && mode !== "training") {
    return errorResult(
      "practice_feedback",
      "provider_feedback_training_only",
      "Provider-backed practice feedback can only be requested in Training Mode.",
      args,
      context,
      { mode, required_mode: "training", provider_name: providerName }
    );
  }

  const problem = problemById(pack, args.problem_id || context.problem_id);
  if (!problem) {
    return errorResult("practice_feedback", "practice_problem_not_found", "Practice problem not found.", args, context, {
      pack: pack.id,
      available_problem_ids: (pack.problems || []).map((item) => item.id),
    });
  }

  const submittedSql = args.sql || context.sql || "";
  const note = staticWrongNote(pack, problem, submittedSql);
  if (providerName) {
    return errorResult(
      "practice_feedback",
      "provider_feedback_unavailable",
      "Provider-backed feedback is delegated to the Python Command API in this iOS shell skeleton.",
      args,
      context,
      { mode, provider_name: providerName }
    );
  }

  return enrich(
    {
      ok: true,
      command: "practice_feedback",
      data: {
        pack_id: pack.id,
        dataset_id: pack.dataset?.id,
        problem: problemPayload(problem),
        submitted_sql: submittedSql,
        expected_issue: note.expected_issue,
        wrong_note: note,
        feedback: note.static_feedback,
        provider_feedback_allowed: false,
        mode,
        requested_provider_name: null,
      },
      error: null,
    },
    args,
    context
  );
}

function sessions() {
  return {
    ok: true,
    sessions: [
      {
        id: "practice-flow",
        title: "Practice flow",
        subtitle: "Local iOS Training Runtime",
        active: true,
      },
      {
        id: "local-sql-lab",
        title: "Local SQL Lab",
        subtitle: "Training Mode only",
        active: false,
      },
    ],
  };
}

export function createTrainingRuntime(options = {}) {
  const pack = options.pack || SQL_BASICS_PACK;
  const attempts = Array.isArray(options.attempts) ? options.attempts : [];
  return {
    initialCommand: "practice_list",
    async getSessions() {
      return sessions();
    },
    async postCommand(command, args = {}, context = {}) {
      if (command === "practice_list") {
        return practiceList(pack, args, context);
      }
      if (command === "practice_schema") {
        return practiceSchema(pack, args, context);
      }
      if (command === "practice_attempts") {
        return practiceAttempts(pack, attempts, args, context);
      }
      if (command === "practice_feedback") {
        return practiceFeedback(pack, args, context);
      }
      return errorResult(
        command,
        "unsupported_ios_training_command",
        `The iOS Training Runtime skeleton only supports Training Mode commands in this goal.`,
        args,
        context,
        { supported_commands: ["practice_list", "practice_schema", "practice_attempts", "practice_feedback"] }
      );
    },
  };
}

export const coqueryTrainingRuntime = createTrainingRuntime();

export async function postCommand(command, args = {}, context = {}) {
  return coqueryTrainingRuntime.postCommand(command, args, context);
}

if (typeof window !== "undefined") {
  window.coqueryCommandRuntime = coqueryTrainingRuntime;
}
