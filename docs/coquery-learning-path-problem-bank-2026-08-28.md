# CoQuery Learning Path / Problem Bank Direction

Date: 2026-08-28

## Decision

CoQuery의 문제은행은 단순 문제 목록이 아니라 **학습 경로(Learning Path)** 로 운영한다.

기본 흐름은 다음과 같다.

`Home -> Learning Path -> Focused Practice -> Feedback -> Next Problem`

기존 `practice_list`, `practice_grade`, `practice_attempts` 계약과 샘플 DB는 유지한다.

## Why

현재 Practice Pack에는 SQL 문제, 난이도, 개념, 힌트, 채점, 오답 기록이 이미 있다. 부족한 것은 문제 데이터가 아니라 사용자가 다음 세 가지를 바로 알 수 있는 구조다.

1. 지금 어디까지 했는가
2. 다음에 무엇을 풀어야 하는가
3. 이 문제에서 어떤 SQL 개념을 배우는가

따라서 새 학습 엔진이나 별도 사용자 DB를 만들지 않고, 기존 attempt 로그를 진행률의 근거로 재사용한다.

## Learning Path v1

현재 `sql_basics`의 문제는 개념에 따라 다음 네 구간으로 보여준다.

### 1. 데이터 찾기

핵심 개념:
- SELECT
- ORDER BY

목표:
- 필요한 열만 선택한다.
- 결과의 정렬 순서를 이해한다.

### 2. 조건으로 찾기

핵심 개념:
- WHERE
- AND
- ORDER BY

목표:
- 실제 업무 조건을 SQL 필터로 바꾼다.

### 3. 테이블 연결하기

핵심 개념:
- JOIN
- WHERE

목표:
- 외래키 관계를 이용해 여러 테이블의 정보를 연결한다.

### 4. 요약하고 집계하기

핵심 개념:
- GROUP BY
- COUNT
- SUM

목표:
- 행 조회에서 업무 지표 계산으로 확장한다.

## Progress Rules

진행률의 원천은 기존 `practice_attempts` 로그다.

문제 상태:
- `시작 전`: 시도 기록 없음
- `진행 중`: 시도 기록은 있으나 정답 기록 없음
- `완료`: 한 번 이상 정답 기록 있음

한 문제를 정답 처리한 뒤 다시 오답을 제출하더라도 학습 완료 상태는 유지한다.

전체 진행률:

`완료 문제 수 / 전체 문제 수`

이어하기:
- 아직 완료하지 않은 문제 중 기존 문제 순서상 첫 문제를 선택한다.
- 모든 문제가 완료되면 첫 문제부터 복습 모드로 돌아간다.

## Problem Bank UI

문제은행 기본 화면에서 보여야 하는 정보:
- 전체 진행률
- 이어하기
- 학습 구간별 진행률
- 문제 상태
- 난이도
- 학습 개념
- 시도 횟수

기본 필터:
- 전체
- 미완료
- 완료

보이지 않아도 되는 정보:
- CLI 등가 명령
- Provider 상태
- Production Assist
- Command API 세부 정보

이 정보들은 Advanced Workspace에 남긴다.

## Expansion Contract

문제 수를 20~30개로 확장할 때 한 화면에 문제를 평면적으로 추가하지 않는다.

권장 단계:

### Level 1 — 찾기
- SELECT
- column selection
- ORDER BY
- DISTINCT

### Level 2 — 조건
- WHERE
- AND / OR
- IN
- LIKE
- NULL
- 날짜 조건

### Level 3 — 관계
- INNER JOIN
- LEFT JOIN
- 다중 JOIN
- 관계 오류 찾기

### Level 4 — 집계
- COUNT
- SUM
- AVG
- GROUP BY
- HAVING

### Level 5 — 업무 시나리오
- 지역별 매출
- 미처리 문의
- 고액 주문 고객
- 최근 활동 고객
- 고객별 주문 요약

### Level 6 — My Data Bridge

샘플 데이터에서 풀었던 문제 패턴을 사용자 DB에 적용한다.

이 단계부터 `schema_detail`, Natural Query, Production Assist로 연결한다.

## Content Rule

문제 하나는 한 가지 핵심 학습 목표를 가져야 한다.

좋은 문제:
- 실제 업무 질문처럼 읽힌다.
- 정답 SQL이 짧더라도 사용자가 왜 필요한지 이해할 수 있다.
- 선행 개념과 새 개념의 차이가 명확하다.

피해야 할 문제:
- SQL 문법 자체를 암기시키기 위한 문장
- 한 문제에 새 개념을 과도하게 섞기
- 테이블/컬럼 이름만 바꾼 반복 문제
- 정답 SQL 형태만 맞히게 하는 문제

## Success Criteria

첫 사용자는:
- 30초 안에 학습 경로를 이해한다.
- 자신의 현재 진행 위치를 한 화면에서 확인한다.
- 한 번 클릭으로 다음 문제를 이어서 푼다.

반복 사용자는:
- 완료/미완료 문제를 구분한다.
- 필요한 개념의 문제로 바로 이동한다.
- 별도 계정이나 서버 없이 로컬 attempt 로그로 진행 상태를 유지한다.

## Current Implementation Scope

이번 단계에서는:
- 현재 5개 문제를 유지한다.
- 문제의 `concepts`와 `difficulty`를 학습경로 UI에 사용한다.
- 기존 `practice_attempts`를 진행률 계산에 사용한다.
- Home의 첫 CTA를 `첫 문제`에서 상황에 따라 `이어서 학습`으로 전환한다.
- 학습경로 화면을 별도 presentation layer로 추가한다.

이번 단계에서는 하지 않는다:
- 새로운 계정 시스템
- 서버 진도 저장소
- 기존 SQL grading 변경
- 20~30개 문제 일괄 추가
- Production Assist 계약 변경

문제 확장은 이 학습경로 UX가 실제 사용 가능한지 확인한 후 별도 PR로 진행한다.
