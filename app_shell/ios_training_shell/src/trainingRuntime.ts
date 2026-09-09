const SQL_BASICS_PACK = __COQUERY_SQL_BASICS_PACK__;

const ATTEMPT_STORAGE_KEY = "coquery.ios.training.practice_attempts.v1";
const ATTEMPT_LOG_PATH = "local://coquery/practice_attempts";

const BLOCK_TYPES = {
  practice_list: "practice_list",
  practice_schema: "practice_schema",
  practice_query: "practice_query_result",
  practice_grade: "practice_grade",
  practice_attempts: "practice_attempts",
  practice_feedback: "practice_feedback",
};

const ACTIONS = {
  practice_list: ["copy", "start_practice", "show_schema"],
  practice_schema: ["copy", "insert_template", "start_practice"],
  practice_query: ["copy", "start_practice"],
  practice_grade: ["copy", "retry", "next_problem"],
  practice_attempts: ["copy", "review_wrong_notes"],
  practice_feedback: ["copy", "retry", "request_provider_feedback"],
};

class TrainingRuntimeError extends Error {
  constructor(code, message, data = {}) {
    super(message);
    this.code = code;
    this.data = data;
  }
}

function quoteCliValue(value) {
  const text = String(value ?? "");
  if (!text) return '""';
  if (/^[A-Za-z0-9._\-/:@]+$/.test(text)) return text;
  return `"${text.replaceAll("\\", "\\\\").replaceAll('"', '\\"')}"`;
}

function buildCliEquivalent(command, args = {}, context = {}) {
  const merged = { ...context, ...args };
  const parts = ["python", "main.py", "--command", command];
  for (const [key, flag] of [
    ["pack", "--pack"], ["table", "--table"], ["problem_id", "--problem-id"],
    ["sql", "--sql"], ["provider_name", "--provider-name"], ["mode", "--mode"], ["limit", "--limit"],
  ]) {
    if (merged[key] !== undefined && merged[key] !== null && merged[key] !== "") parts.push(flag, quoteCliValue(merged[key]));
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
  return enrich({ ok: false, command, data, error: { code, message } }, args, context);
}

function resultFromError(command, error, args = {}, context = {}) {
  if (error instanceof TrainingRuntimeError) return errorResult(command, error.code, error.message, args, context, error.data);
  return errorResult(command, "practice_error", error?.message || String(error), args, context);
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
    throw new TrainingRuntimeError("practice_table_not_found", `Table not found in practice pack: ${tableName}.`, {
      pack: pack.id,
      available_tables: tables.map((table) => table.name),
    });
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
  const requestedId = String(problemId || "").trim();
  if (!requestedId) throw new TrainingRuntimeError("missing_problem_id", "practice_grade requires --problem-id.");
  const problem = (pack.problems || []).find((item) => item.id === requestedId);
  if (!problem) {
    throw new TrainingRuntimeError("practice_problem_not_found", `Practice problem not found: ${requestedId}.`, {
      pack: pack.id,
      available_problem_ids: (pack.problems || []).map((item) => item.id),
    });
  }
  return problem;
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

function quoteIdentifier(identifier) {
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(String(identifier))) {
    throw new TrainingRuntimeError("invalid_practice_schema", `Invalid identifier in practice pack: ${identifier}.`);
  }
  return `"${identifier}"`;
}

function sqliteType(rawType) {
  const normalized = String(rawType || "TEXT").toUpperCase();
  return ["INTEGER", "REAL", "TEXT"].includes(normalized) ? normalized : "TEXT";
}

function ensureSelect(sql) {
  const text = String(sql || "").trim();
  if (!text) throw new TrainingRuntimeError("missing_practice_sql", "A SELECT statement is required.");
  const firstToken = text.split(/\s+/, 1)[0].toUpperCase();
  if (firstToken !== "SELECT") {
    throw new TrainingRuntimeError("practice_sql_not_select", "Practice sandbox only accepts SELECT statements.", {
      first_token: firstToken,
    });
  }
  if (text.replace(/;\s*$/, "").includes(";")) {
    throw new TrainingRuntimeError("practice_sql_error", "Practice sandbox only accepts one SELECT statement.", { sql: text });
  }
  return text;
}

function parseLimit(value, defaultValue) {
  const resolved = value === undefined || value === null || value === "" ? defaultValue : Number(value);
  if (!Number.isInteger(resolved) || resolved < 0) {
    throw new TrainingRuntimeError("invalid_practice_limit", "limit must be zero or greater.");
  }
  return resolved;
}

function buildDatabase(SQL, pack) {
  const database = new SQL.Database();
  try {
    for (const table of pack.dataset?.tables || []) {
      const columns = table.columns || [];
      if (columns.length === 0) throw new TrainingRuntimeError("invalid_practice_schema", `Table has no columns: ${table.name}.`);
      const definitions = columns.map((column) => `${quoteIdentifier(column.name)} ${sqliteType(column.type)}`);
      if ((table.primary_key || []).length > 0) definitions.push(`PRIMARY KEY (${table.primary_key.map(quoteIdentifier).join(", ")})`);
      for (const foreignKey of table.foreign_keys || []) {
        definitions.push(
          `FOREIGN KEY (${quoteIdentifier(foreignKey.column)}) REFERENCES ${quoteIdentifier(foreignKey.references_table)}(${quoteIdentifier(foreignKey.references_column)})`
        );
      }
      database.run(`CREATE TABLE ${quoteIdentifier(table.name)} (${definitions.join(", ")})`);
    }
    for (const table of pack.dataset?.tables || []) {
      const columns = (table.columns || []).map((column) => column.name);
      const insert = database.prepare(
        `INSERT INTO ${quoteIdentifier(table.name)} (${columns.map(quoteIdentifier).join(", ")}) VALUES (${columns.map(() => "?").join(", ")})`
      );
      try {
        for (const row of table.rows || []) insert.run(columns.map((column) => row[column] ?? null));
      } finally {
        insert.free();
      }
    }
    return database;
  } catch (error) {
    database.close();
    throw error;
  }
}

function executeSelect(SQL, pack, sql, limit = null) {
  const safeSql = ensureSelect(sql);
  const database = buildDatabase(SQL, pack);
  try {
    const resultSets = database.exec(safeSql);
    const resultSet = resultSets[0] || { columns: [], values: [] };
    const values = limit === null ? resultSet.values : resultSet.values.slice(0, limit);
    const rows = values.map((row) => Object.fromEntries(resultSet.columns.map((column, index) => [column, row[index] ?? null])));
    return { columns: resultSet.columns, rows, row_count: rows.length };
  } catch (error) {
    if (error instanceof TrainingRuntimeError) throw error;
    throw new TrainingRuntimeError("practice_sql_error", error?.message || String(error), { sql: safeSql });
  } finally {
    database.close();
  }
}

function resultSignature(result) {
  return JSON.stringify([result.columns, result.rows.map((row) => result.columns.map((column) => row[column]))]);
}

function expectedIssue(actual, expected) {
  const actualColumns = actual.columns.map(String);
  const expectedColumns = expected.columns.map(String);
  if (JSON.stringify(actualColumns) !== JSON.stringify(expectedColumns)) {
    const missing = expectedColumns.filter((column) => !actualColumns.includes(column));
    const extra = actualColumns.filter((column) => !expectedColumns.includes(column));
    const details = [];
    if (missing.length > 0) details.push(`Expected column(s) missing from the result: ${missing.join(", ")}.`);
    if (extra.length > 0) details.push(`Unexpected column(s) returned: ${extra.join(", ")}.`);
    if (details.length === 0) details.push("Returned columns have a different order than the expected answer.");
    return details.join(" ");
  }
  if (actual.row_count !== expected.row_count) {
    return `Expected ${expected.row_count} row(s), but the submitted query returned ${actual.row_count} row(s). Check filters, joins, and grouping.`;
  }
  if (JSON.stringify(actual.rows) !== JSON.stringify(expected.rows)) {
    return "Returned rows differ from the expected answer. Check selected values, sorting, joins, and aggregate logic.";
  }
  return "No issue detected. Result columns and rows match the expected answer.";
}

function staticFeedbackMessage(problem, issue) {
  const concepts = (problem.concepts || []).filter(Boolean).join(", ");
  const conceptPart = concepts ? ` Focus concept(s): ${concepts}.` : "";
  const hintPart = problem.hint ? ` Hint: ${problem.hint}.` : "";
  return `${issue} Retry by adjusting the submitted SQL, then run practice_grade again.${conceptPart}${hintPart}`;
}

function staticWrongNote(pack, problem, submittedSql, actual, expected) {
  const issue = expectedIssue(actual, expected);
  const message = staticFeedbackMessage(problem, issue);
  return {
    pack_id: pack.id,
    problem_id: problem.id,
    problem_title: problem.title,
    prompt: problem.prompt,
    submitted_sql: submittedSql,
    expected_issue: issue,
    static_feedback: { source: "static", label: "Static feedback", message, ai_generated: false },
    retry_action: { label: "Retry", command: "practice_start", pack_id: pack.id, problem_id: problem.id, sql: submittedSql },
    provider_feedback: {
      available: true,
      mode_required: "training",
      request_command: "practice_feedback",
      label: "AI-generated feedback",
    },
  };
}

function resolveStorage(options) {
  if (options.storage && typeof options.storage.getItem === "function" && typeof options.storage.setItem === "function") return options.storage;
  try {
    if (typeof window !== "undefined" && window.localStorage) return window.localStorage;
  } catch {
    return null;
  }
  return null;
}

function createAttemptStore(storage, seedAttempts = []) {
  let attempts = Array.isArray(seedAttempts) ? [...seedAttempts] : [];
  if (!storage) {
    return {
      read: () => [...attempts],
      append: (attempt) => {
        attempts = [...attempts, attempt];
        return true;
      },
    };
  }
  try {
    const stored = storage.getItem(ATTEMPT_STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed)) attempts = parsed;
    } else if (attempts.length > 0) {
      storage.setItem(ATTEMPT_STORAGE_KEY, JSON.stringify(attempts));
    }
  } catch {
    // Local history is optional; a corrupt or unavailable store must not prevent practice.
  }
  return {
    read: () => [...attempts],
    append: (attempt) => {
      attempts = [...attempts, attempt];
      try {
        storage.setItem(ATTEMPT_STORAGE_KEY, JSON.stringify(attempts));
        return true;
      } catch {
        return false;
      }
    },
  };
}

function practiceList(pack, args = {}, context = {}) {
  return enrich(
    {
      ok: true,
      command: "practice_list",
      data: { packs: [packSummary(pack)], selected_pack: pack.id, problems: problemSummaries(pack), examples: pack.examples || [] },
      error: null,
    },
    args,
    context
  );
}

function practiceSchema(pack, args = {}, context = {}) {
  try {
    const tables = tableSummaries(pack, args.table || context.table);
    return enrich(
      {
        ok: true,
        command: "practice_schema",
        data: { pack_id: pack.id, dataset_id: pack.dataset?.id, dataset_title: pack.dataset?.title, table_count: tables.length, tables },
        error: null,
      },
      args,
      context
    );
  } catch (error) {
    return resultFromError("practice_schema", error, args, context);
  }
}

function practiceAttempts(pack, attemptStore, args = {}, context = {}) {
  try {
    const problemId = args.problem_id || context.problem_id;
    const limit = parseLimit(args.limit ?? context.limit, 20);
    const attempts = attemptStore.read().filter((attempt) => attempt.pack_id === pack.id).filter((attempt) => !problemId || attempt.problem_id === problemId).slice(-limit);
    return enrich(
      {
        ok: true,
        command: "practice_attempts",
        data: { attempt_log_path: ATTEMPT_LOG_PATH, pack_id: pack.id, problem_id: problemId || null, limit, attempts, attempt_count: attempts.length },
        error: null,
      },
      args,
      context
    );
  } catch (error) {
    return resultFromError("practice_attempts", error, args, context);
  }
}

function sessions() {
  return {
    ok: true,
    sessions: [
      { id: "practice-flow", title: "Practice flow", subtitle: "Local iOS Training Runtime", active: true },
      { id: "local-sql-lab", title: "Local SQL Lab", subtitle: "Training Mode only", active: false },
    ],
  };
}

export function createTrainingRuntime(options = {}) {
  const pack = options.pack || SQL_BASICS_PACK;
  const attemptStore = createAttemptStore(resolveStorage(options), options.attempts);
  let sqlEnginePromise = null;

  async function loadSqlEngine() {
    if (!sqlEnginePromise) {
      const initializer = options.initSqlJs || (typeof initSqlJs === "function" ? initSqlJs : null);
      if (!initializer) {
        throw new TrainingRuntimeError("ios_sql_engine_unavailable", "The local SQLite engine could not be loaded. Reinstall the iOS app and try again.");
      }
      sqlEnginePromise = Promise.resolve(initializer({ locateFile: options.locateFile || ((file) => `./${file}`) }));
    }
    try {
      return await sqlEnginePromise;
    } catch (error) {
      sqlEnginePromise = null;
      throw new TrainingRuntimeError(
        "ios_sql_engine_unavailable",
        "The local SQLite engine could not be loaded. Reinstall the iOS app and try again.",
        { cause: error?.message || String(error) }
      );
    }
  }

  async function practiceQuery(args = {}, context = {}) {
    try {
      const SQL = await loadSqlEngine();
      const limit = parseLimit(args.limit ?? context.limit, 50);
      const submittedSql = ensureSelect(args.sql ?? context.sql);
      const result = executeSelect(SQL, pack, submittedSql, limit);
      const resultIntelligence = classifyPracticeResult(result.columns, result.rows, submittedSql);
      return enrich(
        {
          ok: true,
          command: "practice_query",
          data: { pack_id: pack.id, dataset_id: pack.dataset?.id, sql: submittedSql, limit, ...result, result_intelligence: resultIntelligence },
          error: null,
        },
        args,
        context
      );
    } catch (error) {
      return resultFromError("practice_query", error, args, context);
    }
  }

  async function practiceGrade(args = {}, context = {}) {
    try {
      const problem = problemById(pack, args.problem_id || context.problem_id);
      const submittedSql = ensureSelect(args.sql ?? context.sql);
      const SQL = await loadSqlEngine();
      const actual = executeSelect(SQL, pack, submittedSql);
      const expected = executeSelect(SQL, pack, problem.expected_sql);
      const correct = resultSignature(actual) === resultSignature(expected);
      const wrongNote = correct ? null : staticWrongNote(pack, problem, submittedSql, actual, expected);
      const noRecord = Boolean(args.no_record ?? context.no_record ?? false);
      const attempt = {
        timestamp: new Date().toISOString(),
        pack_id: pack.id,
        problem_id: problem.id,
        problem_title: problem.title,
        correct,
        sql: submittedSql,
        actual_row_count: actual.row_count,
        expected_row_count: expected.row_count,
        ...(wrongNote ? { wrong_note: wrongNote } : {}),
      };
      const attemptRecorded = noRecord ? false : attemptStore.append(attempt);
      return enrich(
        {
          ok: true,
          command: "practice_grade",
          data: {
            pack_id: pack.id,
            dataset_id: pack.dataset?.id,
            problem: problemPayload(problem),
            correct,
            feedback: correct ? "Correct. Result columns and rows match the expected answer." : wrongNote.static_feedback.message,
            feedback_source: "static",
            ai_generated: false,
            wrong_note: wrongNote,
            actual,
            expected,
            expected_sql: problem.expected_sql,
            attempt_recorded: attemptRecorded,
            attempt_log_path: attemptRecorded ? ATTEMPT_LOG_PATH : null,
          },
          error: null,
        },
        args,
        context
      );
    } catch (error) {
      return resultFromError("practice_grade", error, args, context);
    }
  }

  async function practiceFeedback(args = {}, context = {}) {
    try {
      const providerName = args.provider_name || context.provider_name || "";
      const mode = String(args.mode || context.mode || "static").toLowerCase();
      if (providerName && mode !== "training") {
        throw new TrainingRuntimeError(
          "provider_feedback_training_only",
          "Provider-backed practice feedback can only be requested in Training Mode.",
          { mode, required_mode: "training", provider_name: providerName }
        );
      }
      const problem = problemById(pack, args.problem_id || context.problem_id);
      const submittedSql = ensureSelect(args.sql ?? context.sql);
      const SQL = await loadSqlEngine();
      const actual = executeSelect(SQL, pack, submittedSql);
      const expected = executeSelect(SQL, pack, problem.expected_sql);
      const note = staticWrongNote(pack, problem, submittedSql, actual, expected);
      if (providerName) {
        throw new TrainingRuntimeError(
          "provider_feedback_unavailable",
          "Provider-backed feedback is unavailable in the offline iOS Training Runtime.",
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
    } catch (error) {
      return resultFromError("practice_feedback", error, args, context);
    }
  }

  return {
    initialCommand: "practice_list",
    async getSessions() {
      return sessions();
    },
    async postCommand(command, args = {}, context = {}) {
      if (command === "practice_list") return practiceList(pack, args, context);
      if (command === "practice_schema") return practiceSchema(pack, args, context);
      if (command === "practice_query") return practiceQuery(args, context);
      if (command === "practice_grade") return practiceGrade(args, context);
      if (command === "practice_attempts") return practiceAttempts(pack, attemptStore, args, context);
      if (command === "practice_feedback") return practiceFeedback(args, context);
      return errorResult(
        command,
        "unsupported_ios_training_command",
        "The iOS Training Runtime only supports local Training Mode commands.",
        args,
        context,
        { supported_commands: ["practice_list", "practice_schema", "practice_query", "practice_grade", "practice_attempts", "practice_feedback"] }
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
