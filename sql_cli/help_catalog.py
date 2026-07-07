#!/usr/bin/env python3
"""Bilingual help catalog for CoQuery commands and SQL terms."""

from __future__ import annotations

from typing import Any


SUPPORTED_LANGUAGES = ("ko", "en")


class CoQueryHelpError(Exception):
    """Help catalog lookup failure."""

    def __init__(self, code: str, message: str, data: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data or {}


def _lang(lang: str | None) -> str:
    normalized = (lang or "ko").strip().lower()
    if normalized in SUPPORTED_LANGUAGES:
        return normalized
    return "ko"


CATEGORIES: list[dict[str, Any]] = [
    {
        "id": "learn",
        "label": {"ko": "학습", "en": "Learning"},
        "summary": {
            "ko": "DB 접속 없이 샘플 데이터셋으로 SQL을 연습합니다.",
            "en": "Practice SQL with built-in sample datasets without connecting to a real DB.",
        },
    },
    {
        "id": "inspect",
        "label": {"ko": "구조 확인", "en": "Inspect"},
        "summary": {
            "ko": "테이블, 컬럼, 관계 같은 DB 구조를 확인합니다.",
            "en": "Inspect database structure such as tables, columns, and relationships.",
        },
    },
    {
        "id": "ask",
        "label": {"ko": "질문/생성", "en": "Ask & Generate"},
        "summary": {
            "ko": "자연어 질문이나 템플릿으로 SQL 생성을 보조합니다.",
            "en": "Assist SQL generation from natural language or templates.",
        },
    },
    {
        "id": "ai",
        "label": {"ko": "AI 연결", "en": "AI Providers"},
        "summary": {
            "ko": "로컬 LLM 또는 저렴한 OpenAI 호환 API를 등록하고 점검합니다.",
            "en": "Register and check local LLMs or low-cost OpenAI-compatible APIs.",
        },
    },
    {
        "id": "safety",
        "label": {"ko": "안전 실행", "en": "Safe Execution"},
        "summary": {
            "ko": "조회와 쓰기 실행을 구분하고 위험한 변경을 막습니다.",
            "en": "Separate read and write execution and guard risky changes.",
        },
    },
]


COMMANDS: list[dict[str, Any]] = [
    {
        "id": "help_catalog",
        "category": "learn",
        "label": {"ko": "도움말 목록", "en": "Help catalog"},
        "summary": {
            "ko": "CoQuery 기능과 SQL 용어 설명을 한 번에 보여줍니다.",
            "en": "Shows CoQuery features and SQL term explanations in one place.",
        },
        "beginner": {
            "ko": "처음 사용하는 사람은 이 명령으로 어떤 기능이 있는지 먼저 확인하면 됩니다.",
            "en": "Start here to see what the tool can do before writing a command.",
        },
        "example": "python main.py --command help_catalog --lang ko --format json",
        "related_terms": ["cli_equivalent", "dataset"],
    },
    {
        "id": "command_explain",
        "category": "learn",
        "label": {"ko": "명령어 설명", "en": "Command explanation"},
        "summary": {
            "ko": "특정 명령이 언제 필요한지 비전공자 관점으로 설명합니다.",
            "en": "Explains when to use a specific command in beginner-friendly language.",
        },
        "beginner": {
            "ko": "`--topic`에 명령어 이름을 넣으면 목적, 예시, 관련 용어를 볼 수 있습니다.",
            "en": "Pass a command name through `--topic` to see purpose, example, and related terms.",
        },
        "example": "python main.py --command command_explain --topic natural --lang ko --format json",
        "related_terms": ["command", "cli_equivalent"],
    },
    {
        "id": "term_explain",
        "category": "learn",
        "label": {"ko": "용어 설명", "en": "Term explanation"},
        "summary": {
            "ko": "JOIN, WHERE, Schema 같은 SQL/DB 용어를 쉽게 설명합니다.",
            "en": "Explains SQL and DB terms such as JOIN, WHERE, and schema.",
        },
        "beginner": {
            "ko": "`--topic join`처럼 궁금한 용어를 넣어 확인합니다.",
            "en": "Use a topic such as `join` to look up a term.",
        },
        "example": "python main.py --command term_explain --topic join --lang ko --format json",
        "related_terms": ["join", "schema", "select"],
    },
    {
        "id": "practice_list",
        "category": "learn",
        "label": {"ko": "연습 문제 보기", "en": "List practice problems"},
        "summary": {
            "ko": "내장 샘플 데이터셋의 SQL 연습 문제를 보여줍니다.",
            "en": "Lists SQL practice problems from the built-in sample dataset.",
        },
        "beginner": {
            "ko": "실제 회사 DB에 연결하지 않고도 SQL 조회 연습을 시작할 수 있습니다.",
            "en": "You can start practicing SQL without connecting to a company database.",
        },
        "example": "python main.py --command practice_list --format json",
        "related_terms": ["dataset", "query", "select"],
    },
    {
        "id": "practice_schema",
        "category": "learn",
        "label": {"ko": "연습 데이터 구조", "en": "Practice schema"},
        "summary": {
            "ko": "연습용 테이블과 컬럼 구성을 보여줍니다.",
            "en": "Shows the tables and columns in the practice dataset.",
        },
        "beginner": {
            "ko": "엑셀의 시트 이름과 열 이름을 먼저 보는 과정으로 이해하면 됩니다.",
            "en": "Think of this as checking sheet names and column names before analysis.",
        },
        "example": "python main.py --command practice_schema --table orders --format json",
        "related_terms": ["schema", "table", "column"],
    },
    {
        "id": "practice_query",
        "category": "learn",
        "label": {"ko": "연습 쿼리 실행", "en": "Run practice query"},
        "summary": {
            "ko": "연습 데이터셋에서 SELECT SQL을 실행합니다.",
            "en": "Runs SELECT SQL against the practice dataset.",
        },
        "beginner": {
            "ko": "연습 환경은 읽기 전용이라 DELETE나 UPDATE 같은 변경 SQL을 막습니다.",
            "en": "The practice sandbox is read-only and blocks DELETE or UPDATE statements.",
        },
        "example": "python main.py --command practice_query --sql \"SELECT id, name FROM customers\" --format json",
        "related_terms": ["select", "read_only", "where"],
    },
    {
        "id": "practice_grade",
        "category": "learn",
        "label": {"ko": "연습 답안 채점", "en": "Grade practice answer"},
        "summary": {
            "ko": "작성한 SQL이 연습 문제의 기대 결과와 맞는지 확인합니다.",
            "en": "Checks whether your SQL matches the expected result for a practice problem.",
        },
        "beginner": {
            "ko": "틀린 답은 나중에 오답노트와 AI 피드백으로 확장할 수 있는 핵심 입력입니다.",
            "en": "Wrong answers become useful inputs for future wrong-note and AI feedback features.",
        },
        "example": "python main.py --command practice_grade --problem-id basic_select_customers --sql \"SELECT id, name, region FROM customers ORDER BY id\" --format json",
        "related_terms": ["query", "order_by", "wrong_note"],
    },
    {
        "id": "schema_detail",
        "category": "inspect",
        "label": {"ko": "스키마 상세", "en": "Schema detail"},
        "summary": {
            "ko": "테이블의 컬럼, PK/FK, 인덱스 같은 구조 정보를 확인합니다.",
            "en": "Shows structure such as columns, primary keys, foreign keys, and indexes.",
        },
        "beginner": {
            "ko": "AI가 SQL을 만들기 전에 어떤 데이터가 있는지 확인하는 지도 역할을 합니다.",
            "en": "This works like a map the AI checks before producing SQL.",
        },
        "example": "python main.py --command schema_detail --db example.db --table users --format json",
        "related_terms": ["schema", "table", "pk", "fk"],
    },
    {
        "id": "natural",
        "category": "ask",
        "label": {"ko": "자연어 질의", "en": "Natural-language query"},
        "summary": {
            "ko": "사람 말로 요청하면 CoQuery가 가능한 SQL 형태로 바꿉니다.",
            "en": "Turns plain-language requests into SQL when the request is covered.",
        },
        "beginner": {
            "ko": "현재는 완성형 AI 분석이 아니라 검증 가능한 기본 요청부터 처리하는 보조 기능입니다.",
            "en": "This is an assistant for covered, verifiable requests rather than a complete BI engine.",
        },
        "example": "python main.py --command natural --db example.db --sql \"show users\" --format json",
        "related_terms": ["natural_language", "provider", "schema"],
    },
    {
        "id": "generate",
        "category": "ask",
        "label": {"ko": "SQL 생성", "en": "Generate SQL"},
        "summary": {
            "ko": "정해진 템플릿과 파라미터로 SQL을 생성합니다.",
            "en": "Generates SQL from a known template and parameters.",
        },
        "beginner": {
            "ko": "완전히 자유로운 생성보다 예측 가능해서 학습과 안전한 반복 업무에 적합합니다.",
            "en": "It is more predictable than free-form generation, useful for learning and repeat work.",
        },
        "example": "python main.py --command generate --skill select_simple --params '{\"table\":\"users\",\"cols\":[\"id\",\"name\"]}' --format json",
        "related_terms": ["template", "select", "schema"],
    },
    {
        "id": "provider_setup",
        "category": "ai",
        "label": {"ko": "AI 제공자 설정", "en": "Set up AI provider"},
        "summary": {
            "ko": "모바일/웹 쉘에서 저렴한 API 또는 로컬 LLM 프로필을 등록하는 안내 화면입니다.",
            "en": "A mobile/web shell form for registering a low-cost API or local LLM profile.",
        },
        "beginner": {
            "ko": "API 키 값은 화면에 넣지 않고, 키가 저장된 환경변수 이름만 등록합니다.",
            "en": "You register the environment variable name, not the secret API key value.",
        },
        "example": "provider_setup gemini",
        "related_terms": ["provider", "api_key_env", "local_llm"],
    },
    {
        "id": "provider_list_presets",
        "category": "ai",
        "label": {"ko": "AI 프리셋 목록", "en": "List AI presets"},
        "summary": {
            "ko": "OpenAI 호환 API 프리셋과 기본 모델 후보를 보여줍니다.",
            "en": "Shows OpenAI-compatible API presets and suggested default models.",
        },
        "beginner": {
            "ko": "저렴하거나 무료 티어가 있는 제공자를 비교할 때 시작점으로 사용합니다.",
            "en": "Use it as a starting point when comparing low-cost or free-tier providers.",
        },
        "example": "python main.py --command provider_list_presets --format json",
        "related_terms": ["provider", "model", "openai_compatible"],
    },
    {
        "id": "provider_add_preset",
        "category": "ai",
        "label": {"ko": "AI 프리셋 저장", "en": "Save AI preset"},
        "summary": {
            "ko": "선택한 제공자 프리셋을 사용할 수 있는 프로필로 저장합니다.",
            "en": "Saves a selected provider preset as a reusable profile.",
        },
        "beginner": {
            "ko": "학습 모드에서는 상용/저가 API, 운영 보조 모드에서는 통제된 로컬 LLM을 분리해 등록할 수 있습니다.",
            "en": "You can separate commercial APIs for learning from governed local LLMs for production assist.",
        },
        "example": "python main.py --command provider_add_preset --preset groq --provider-name fast_groq --api-key-env GROQ_API_KEY --format json",
        "related_terms": ["provider", "model", "local_llm"],
    },
    {
        "id": "query",
        "category": "safety",
        "label": {"ko": "SQL 실행", "en": "Run SQL"},
        "summary": {
            "ko": "DB 또는 연습 환경에서 SQL을 실행합니다.",
            "en": "Runs SQL against a database or practice path.",
        },
        "beginner": {
            "ko": "SELECT 조회는 기본 허용되지만 INSERT/UPDATE/DELETE는 명시적 안전 옵션이 필요합니다.",
            "en": "SELECT is allowed by default; INSERT/UPDATE/DELETE require explicit safety flags.",
        },
        "example": "python main.py --command query --db example.db --sql \"SELECT * FROM users\" --format json",
        "related_terms": ["query", "select", "write_safety"],
    },
    {
        "id": "doctor",
        "category": "safety",
        "label": {"ko": "연결 점검", "en": "Connection doctor"},
        "summary": {
            "ko": "DB 연결 가능 여부와 실패 원인을 점검합니다.",
            "en": "Checks whether a database target is reachable and explains connection failures.",
        },
        "beginner": {
            "ko": "실제 운영 DB를 보기 전에 연결 상태와 권한 문제를 먼저 분리해서 확인합니다.",
            "en": "Use it before touching a real DB to separate connection and permission issues.",
        },
        "example": "python main.py --command doctor --db example.db --format json",
        "related_terms": ["db_connection", "read_only", "write_safety"],
    },
]


TERMS: list[dict[str, Any]] = [
    {
        "id": "dataset",
        "label": {"ko": "데이터셋", "en": "Dataset"},
        "plain": {
            "ko": "분석 목적에 맞게 묶어 둔 데이터입니다. 엑셀 파일 하나나 여러 테이블 조합으로 생각하면 됩니다.",
            "en": "A collection of data for one analysis purpose, like one spreadsheet or a useful group of tables.",
        },
        "example": {"ko": "고객 목록, 주문 내역, 민원 현황", "en": "customer list, order history, support tickets"},
    },
    {
        "id": "schema",
        "label": {"ko": "스키마", "en": "Schema"},
        "plain": {
            "ko": "테이블과 컬럼의 설계도입니다. 어떤 데이터가 어디에 있는지 알려줍니다.",
            "en": "The blueprint of tables and columns that shows where data lives.",
        },
        "example": {"ko": "`customers` 테이블에는 `id`, `name`, `region` 컬럼이 있습니다.", "en": "`customers` has `id`, `name`, and `region` columns."},
    },
    {
        "id": "table",
        "label": {"ko": "테이블", "en": "Table"},
        "plain": {
            "ko": "같은 종류의 데이터를 행과 열로 저장한 공간입니다.",
            "en": "A place that stores one kind of data in rows and columns.",
        },
        "example": {"ko": "고객 테이블, 주문 테이블", "en": "customers table, orders table"},
    },
    {
        "id": "column",
        "label": {"ko": "컬럼", "en": "Column"},
        "plain": {
            "ko": "테이블의 한 항목입니다. 엑셀의 열과 비슷합니다.",
            "en": "One field in a table, similar to a spreadsheet column.",
        },
        "example": {"ko": "`name`은 이름 컬럼, `created_at`은 생성일 컬럼입니다.", "en": "`name` is a name column; `created_at` is a created-date column."},
    },
    {
        "id": "select",
        "label": {"ko": "SELECT", "en": "SELECT"},
        "plain": {
            "ko": "데이터를 조회하는 SQL입니다. 데이터를 바꾸지 않습니다.",
            "en": "SQL that reads data without changing it.",
        },
        "example": {"ko": "SELECT name FROM customers", "en": "SELECT name FROM customers"},
    },
    {
        "id": "where",
        "label": {"ko": "WHERE", "en": "WHERE"},
        "plain": {
            "ko": "필요한 행만 고르는 조건입니다.",
            "en": "A condition that keeps only the rows you need.",
        },
        "example": {"ko": "WHERE status = 'paid'", "en": "WHERE status = 'paid'"},
    },
    {
        "id": "join",
        "label": {"ko": "JOIN", "en": "JOIN"},
        "plain": {
            "ko": "두 테이블을 연결해서 한 결과처럼 보는 방법입니다.",
            "en": "A way to combine two tables into one result.",
        },
        "example": {"ko": "주문 테이블과 고객 테이블을 고객 ID로 연결합니다.", "en": "Combine orders and customers by customer ID."},
    },
    {
        "id": "order_by",
        "label": {"ko": "ORDER BY", "en": "ORDER BY"},
        "plain": {
            "ko": "결과를 원하는 순서로 정렬합니다.",
            "en": "Sorts results in a chosen order.",
        },
        "example": {"ko": "ORDER BY created_at DESC", "en": "ORDER BY created_at DESC"},
    },
    {
        "id": "pk",
        "label": {"ko": "PK", "en": "Primary key"},
        "plain": {
            "ko": "각 행을 구분하는 대표 번호입니다.",
            "en": "The main identifier that makes each row distinct.",
        },
        "example": {"ko": "고객 ID", "en": "customer ID"},
    },
    {
        "id": "fk",
        "label": {"ko": "FK", "en": "Foreign key"},
        "plain": {
            "ko": "다른 테이블의 행을 가리키는 연결 키입니다.",
            "en": "A link from one table to a row in another table.",
        },
        "example": {"ko": "주문의 `customer_id`가 고객의 `id`를 가리킵니다.", "en": "`orders.customer_id` points to `customers.id`."},
    },
    {
        "id": "provider",
        "label": {"ko": "AI 제공자", "en": "AI provider"},
        "plain": {
            "ko": "질문을 처리할 LLM 서비스 또는 로컬 모델 프로필입니다.",
            "en": "A profile for the LLM service or local model that handles AI requests.",
        },
        "example": {"ko": "Ollama 로컬 모델, Groq API, Gemini API", "en": "Ollama local model, Groq API, Gemini API"},
    },
    {
        "id": "local_llm",
        "label": {"ko": "로컬 LLM", "en": "Local LLM"},
        "plain": {
            "ko": "외부 API 대신 내부 PC나 서버에서 실행하는 AI 모델입니다.",
            "en": "An AI model running on a local machine or internal server instead of an external API.",
        },
        "example": {"ko": "운영 DB 보조 기능은 통제된 로컬 LLM만 허용할 수 있습니다.", "en": "Production DB assist can be limited to governed local LLMs."},
    },
    {
        "id": "api_key_env",
        "label": {"ko": "API 키 환경변수", "en": "API key environment variable"},
        "plain": {
            "ko": "비밀 키 값을 직접 저장하지 않고, 키가 들어 있는 환경변수 이름만 쓰는 방식입니다.",
            "en": "A way to reference a secret key by environment variable name instead of storing the key value.",
        },
        "example": {"ko": "GROQ_API_KEY", "en": "GROQ_API_KEY"},
    },
    {
        "id": "cli_equivalent",
        "label": {"ko": "CLI 등가 명령", "en": "CLI equivalent"},
        "plain": {
            "ko": "화면에서 누른 작업이 실제로 어떤 터미널 명령인지 보여주는 재현용 명령입니다.",
            "en": "The exact terminal command that reproduces a UI action.",
        },
        "example": {"ko": "python main.py --command practice_list --format json", "en": "python main.py --command practice_list --format json"},
    },
    {
        "id": "read_only",
        "label": {"ko": "읽기 전용", "en": "Read-only"},
        "plain": {
            "ko": "데이터를 조회만 하고 변경하지 않는 모드입니다.",
            "en": "A mode that reads data but does not change it.",
        },
        "example": {"ko": "운영 DB 조회는 읽기 전용 계정으로 제한합니다.", "en": "Production queries should use read-only credentials."},
    },
    {
        "id": "write_safety",
        "label": {"ko": "쓰기 안전장치", "en": "Write safety"},
        "plain": {
            "ko": "INSERT, UPDATE, DELETE가 실수로 실행되지 않도록 확인 절차를 둔 것입니다.",
            "en": "Guards that prevent INSERT, UPDATE, or DELETE from running accidentally.",
        },
        "example": {"ko": "`--write`, `--dry-run`, `--max-affected-rows`", "en": "`--write`, `--dry-run`, `--max-affected-rows`"},
    },
    {
        "id": "wrong_note",
        "label": {"ko": "오답노트", "en": "Wrong note"},
        "plain": {
            "ko": "틀린 SQL 시도와 이유를 모아 다음 학습 피드백으로 쓰는 기록입니다.",
            "en": "A record of incorrect SQL attempts and why they need review.",
        },
        "example": {"ko": "JOIN 조건 누락, WHERE 조건 실수", "en": "missing JOIN condition, wrong WHERE filter"},
    },
]


def _select_text(value: dict[str, str], lang: str) -> str:
    return value.get(lang) or value.get("ko") or value.get("en") or ""


def _localize_record(record: dict[str, Any], lang: str) -> dict[str, Any]:
    localized: dict[str, Any] = {"id": record["id"]}
    for key, value in record.items():
        if key == "id":
            continue
        if isinstance(value, dict) and any(code in value for code in SUPPORTED_LANGUAGES):
            localized[key] = _select_text(value, lang)
            localized[f"{key}_i18n"] = value
        else:
            localized[key] = value
    return localized


def get_help_catalog(lang: str | None = None) -> dict[str, Any]:
    selected = _lang(lang)
    return {
        "language": selected,
        "supported_languages": list(SUPPORTED_LANGUAGES),
        "categories": [_localize_record(category, selected) for category in CATEGORIES],
        "commands": [_localize_record(command, selected) for command in COMMANDS],
        "terms": [_localize_record(term, selected) for term in TERMS],
    }


def explain_command(command_id: str | None, lang: str | None = None) -> dict[str, Any]:
    selected = _lang(lang)
    requested = (command_id or "").strip()
    if not requested:
        raise CoQueryHelpError("missing_command_topic", "command_explain requires --topic with a command name.")
    for command in COMMANDS:
        if command["id"] == requested:
            return {
                "language": selected,
                "command": _localize_record(command, selected),
                "related_terms": [
                    _localize_record(term, selected)
                    for term in TERMS
                    if term["id"] in set(command.get("related_terms", []))
                ],
            }
    raise CoQueryHelpError(
        "unknown_command_topic",
        f"No help entry exists for command: {requested}.",
        {"available_commands": [command["id"] for command in COMMANDS]},
    )


def explain_term(term_id: str | None, lang: str | None = None) -> dict[str, Any]:
    selected = _lang(lang)
    requested = (term_id or "").strip()
    if not requested:
        raise CoQueryHelpError("missing_term_topic", "term_explain requires --topic with a term id.")
    for term in TERMS:
        if term["id"] == requested:
            return {"language": selected, "term": _localize_record(term, selected)}
    raise CoQueryHelpError(
        "unknown_term_topic",
        f"No term entry exists for topic: {requested}.",
        {"available_terms": [term["id"] for term in TERMS]},
    )
