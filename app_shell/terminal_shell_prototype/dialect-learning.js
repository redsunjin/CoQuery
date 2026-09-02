(() => {
  /**
   * @typedef {Object} DialectLesson
   * @property {string} id
   * @property {string[]} relatedProblemIds
   * @property {{ko: DialectLessonCopy, en: DialectLessonCopy}} copy
   */

  /**
   * @typedef {Object} DialectLessonCopy
   * @property {string} concept
   * @property {string} intent
   * @property {string} commonExplanation
   * @property {string} whyItDiffers
   * @property {Array<{engine: string, sql: string, explanation: string, verificationState: string}>} variants
   */

  const VerificationStates = Object.freeze({
    common: "common",
    reference: "reference",
    verified: "verified",
  });

  const DialectLessons = Object.freeze([
    Object.freeze({
      id: "string_concatenation",
      relatedProblemIds: Object.freeze(["customer_names_segments"]),
      copy: Object.freeze({
        ko: Object.freeze({
          concept: "문자열 연결",
          intent: "고객 이름과 등급처럼 여러 텍스트 값을 하나의 표시 값으로 만듭니다.",
          commonExplanation: "텍스트를 하나로 합친다는 SQL의 의도는 같지만, 사용하는 연산자나 함수는 DB마다 다를 수 있습니다.",
          whyItDiffers: "PostgreSQL과 SQLite는 `||` 연산자를 쓰고, MySQL은 보통 `CONCAT()` 함수를 씁니다.",
          variants: Object.freeze([
            Object.freeze({
              engine: "postgresql",
              sql: "SELECT 'Ada' || ' ' || 'Lovelace' AS full_name;",
              explanation: "`||`로 텍스트 조각을 연결합니다.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "mysql",
              sql: "SELECT CONCAT('Ada', ' ', 'Lovelace') AS full_name;",
              explanation: "MySQL 문서 기준의 `CONCAT()` 비교 예시입니다. CoQuery의 MySQL 실행 지원은 아닙니다.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "sqlite",
              sql: "SELECT 'Ada' || ' ' || 'Lovelace' AS full_name;",
              explanation: "현재 CoQuery 연습 환경과 같은 SQLite에서 테스트로 실행합니다.",
              verificationState: VerificationStates.verified,
            }),
          ]),
        }),
        en: Object.freeze({
          concept: "String concatenation",
          intent: "Make one display value from text such as a customer name and segment.",
          commonExplanation: "The SQL intent is the same—combine text—but the operator or function can differ by database.",
          whyItDiffers: "PostgreSQL and SQLite use `||`; MySQL commonly uses `CONCAT()`.",
          variants: Object.freeze([
            Object.freeze({
              engine: "postgresql",
              sql: "SELECT 'Ada' || ' ' || 'Lovelace' AS full_name;",
              explanation: "Use `||` to join text pieces.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "mysql",
              sql: "SELECT CONCAT('Ada', ' ', 'Lovelace') AS full_name;",
              explanation: "A documented MySQL `CONCAT()` comparison. It does not mean CoQuery runs MySQL.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "sqlite",
              sql: "SELECT 'Ada' || ' ' || 'Lovelace' AS full_name;",
              explanation: "Executed by a test against SQLite, CoQuery's current practice environment.",
              verificationState: VerificationStates.verified,
            }),
          ]),
        }),
      }),
    }),
    Object.freeze({
      id: "current_date_time",
      relatedProblemIds: Object.freeze(["orders_chronological", "march_orders"]),
      copy: Object.freeze({
        ko: Object.freeze({
          concept: "현재 날짜와 시간",
          intent: "오늘 또는 지금 시점을 기준으로 날짜가 있는 데이터를 다룹니다.",
          commonExplanation: "현재 시점을 가져오는 목적은 같지만, DB마다 날짜·시간 값을 만드는 함수 표기가 다릅니다.",
          whyItDiffers: "PostgreSQL과 MySQL은 `CURRENT_TIMESTAMP` 계열을 제공하고, SQLite는 내장 날짜·시간 함수를 사용합니다.",
          variants: Object.freeze([
            Object.freeze({
              engine: "postgresql",
              sql: "SELECT CURRENT_TIMESTAMP AS current_datetime;",
              explanation: "PostgreSQL의 현재 시각 표현 예시입니다.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "mysql",
              sql: "SELECT CURRENT_TIMESTAMP() AS current_datetime;",
              explanation: "MySQL 문서 기준의 현재 시각 표현입니다. CoQuery에서 실행 검증하지 않았습니다.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "sqlite",
              sql: "SELECT datetime('now') AS current_datetime;",
              explanation: "SQLite의 내장 날짜·시간 함수이며 CoQuery 회귀 테스트로 실행합니다.",
              verificationState: VerificationStates.verified,
            }),
          ]),
        }),
        en: Object.freeze({
          concept: "Current date and time",
          intent: "Work with date-bearing data relative to today or the current moment.",
          commonExplanation: "The intent is to get the current moment, but databases spell their date/time functions differently.",
          whyItDiffers: "PostgreSQL and MySQL provide `CURRENT_TIMESTAMP` forms; SQLite uses built-in date/time functions.",
          variants: Object.freeze([
            Object.freeze({
              engine: "postgresql",
              sql: "SELECT CURRENT_TIMESTAMP AS current_datetime;",
              explanation: "A PostgreSQL current-time expression.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "mysql",
              sql: "SELECT CURRENT_TIMESTAMP() AS current_datetime;",
              explanation: "A documented MySQL current-time expression; CoQuery has not runtime-verified it.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "sqlite",
              sql: "SELECT datetime('now') AS current_datetime;",
              explanation: "SQLite's built-in date/time function, executed by a CoQuery regression test.",
              verificationState: VerificationStates.verified,
            }),
          ]),
        }),
      }),
    }),
    Object.freeze({
      id: "date_arithmetic",
      relatedProblemIds: Object.freeze(["march_orders", "monthly_paid_sales"]),
      copy: Object.freeze({
        ko: Object.freeze({
          concept: "날짜 계산",
          intent: "기준 날짜에서 7일 뒤처럼 날짜를 더하거나 뺍니다.",
          commonExplanation: "날짜를 이동한다는 개념은 공통이지만, interval과 날짜 수정자를 쓰는 방식이 DB마다 다릅니다.",
          whyItDiffers: "PostgreSQL은 interval 식을, MySQL은 `DATE_ADD`를, SQLite는 날짜 수정자를 사용합니다.",
          variants: Object.freeze([
            Object.freeze({
              engine: "postgresql",
              sql: "SELECT DATE '2026-09-02' + INTERVAL '7 days' AS target_date;",
              explanation: "PostgreSQL에서는 날짜와 interval을 더합니다.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "mysql",
              sql: "SELECT DATE_ADD(DATE '2026-09-02', INTERVAL 7 DAY) AS target_date;",
              explanation: "MySQL 문서 기준의 `DATE_ADD` 비교 예시입니다. CoQuery에서 실행 검증하지 않았습니다.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "sqlite",
              sql: "SELECT date('2026-09-02', '+7 days') AS target_date;",
              explanation: "SQLite는 날짜 함수에 수정자를 전달하며, 이 예시는 회귀 테스트로 실행합니다.",
              verificationState: VerificationStates.verified,
            }),
          ]),
        }),
        en: Object.freeze({
          concept: "Date arithmetic",
          intent: "Add to or subtract from a date, such as finding the date seven days later.",
          commonExplanation: "Moving a date is a common idea, but databases differ in how they express intervals and date modifiers.",
          whyItDiffers: "PostgreSQL adds an interval, MySQL uses `DATE_ADD`, and SQLite passes a modifier to a date function.",
          variants: Object.freeze([
            Object.freeze({
              engine: "postgresql",
              sql: "SELECT DATE '2026-09-02' + INTERVAL '7 days' AS target_date;",
              explanation: "PostgreSQL adds an interval to a date.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "mysql",
              sql: "SELECT DATE_ADD(DATE '2026-09-02', INTERVAL 7 DAY) AS target_date;",
              explanation: "A documented MySQL `DATE_ADD` comparison; CoQuery has not runtime-verified it.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "sqlite",
              sql: "SELECT date('2026-09-02', '+7 days') AS target_date;",
              explanation: "SQLite passes a modifier to its date function; this example runs in a regression test.",
              verificationState: VerificationStates.verified,
            }),
          ]),
        }),
      }),
    }),
    Object.freeze({
      id: "limit_rows",
      relatedProblemIds: Object.freeze(["largest_orders"]),
      copy: Object.freeze({
        ko: Object.freeze({
          concept: "행 수 제한",
          intent: "정렬한 결과 중 앞의 몇 행만 가져옵니다.",
          commonExplanation: "이 비교에서는 PostgreSQL, MySQL, SQLite가 모두 같은 `LIMIT` 형태를 사용합니다.",
          whyItDiffers: "항상 다른 문법만 있는 것은 아닙니다. 이 예시는 공통 SQL을 먼저 배울 수 있는 경우입니다.",
          variants: Object.freeze([
            Object.freeze({
              engine: "postgresql",
              sql: "SELECT id FROM orders ORDER BY total_amount DESC LIMIT 3;",
              explanation: "이 예시에서는 공통 `LIMIT` 문법을 사용합니다.",
              verificationState: VerificationStates.common,
            }),
            Object.freeze({
              engine: "mysql",
              sql: "SELECT id FROM orders ORDER BY total_amount DESC LIMIT 3;",
              explanation: "문서 비교용 MySQL 예시이며, CoQuery의 MySQL 실행 지원을 뜻하지 않습니다.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "sqlite",
              sql: "SELECT id FROM orders ORDER BY total_amount DESC LIMIT 3;",
              explanation: "현재 연습 SQL과 같은 공통 `LIMIT` 형태입니다.",
              verificationState: VerificationStates.common,
            }),
          ]),
        }),
        en: Object.freeze({
          concept: "Limit rows",
          intent: "Return only the first few rows after ordering a result.",
          commonExplanation: "For this comparison, PostgreSQL, MySQL, and SQLite all use the same `LIMIT` form.",
          whyItDiffers: "Not every lesson has different syntax. This is a case where learners can keep using common SQL first.",
          variants: Object.freeze([
            Object.freeze({
              engine: "postgresql",
              sql: "SELECT id FROM orders ORDER BY total_amount DESC LIMIT 3;",
              explanation: "This example uses the common `LIMIT` syntax.",
              verificationState: VerificationStates.common,
            }),
            Object.freeze({
              engine: "mysql",
              sql: "SELECT id FROM orders ORDER BY total_amount DESC LIMIT 3;",
              explanation: "A MySQL reference comparison only; it does not mean CoQuery runs MySQL.",
              verificationState: VerificationStates.reference,
            }),
            Object.freeze({
              engine: "sqlite",
              sql: "SELECT id FROM orders ORDER BY total_amount DESC LIMIT 3;",
              explanation: "The same common `LIMIT` shape used in the practice SQL.",
              verificationState: VerificationStates.common,
            }),
          ]),
        }),
      }),
    }),
  ]);

  const DialectCatalog = Object.freeze({
    id: "coquery-sql-dialect-learning",
    version: "2026-09-02",
    lessons: DialectLessons,
  });

  const EmptyLessons = Object.freeze([]);

  function getLesson(lessonId) {
    return DialectLessons.find((lesson) => lesson.id === lessonId) || null;
  }

  function lessonsForProblem(problemId) {
    const normalizedProblemId = String(problemId || "").trim();
    if (!normalizedProblemId) return EmptyLessons;
    return Object.freeze(DialectLessons.filter((lesson) => lesson.relatedProblemIds.includes(normalizedProblemId)));
  }

  globalThis.CoQueryDialectLearning = Object.freeze({
    DialectCatalog,
    VerificationStates,
    getLesson,
    lessonsForProblem,
  });
})();
