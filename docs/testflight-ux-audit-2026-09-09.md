# TestFlight 캡처 피드백 점검 — 2026-09-09

## 범위와 기준

App Store Connect의 CoQuery(6808960658) 스크린샷 피드백 4건을 직접 열어 캡처와 접수 문구를 확인했다. 최초 빌드 요약은 피드백 3건이었으나 상세 목록에는 빌드 2의 신규 접수 1건이 더 있었다.

실제 배포 작업 소스는 `/Users/Agent/.codex/worktrees/d0fc/CoQuery`, `codex/iphone-pwa-ui-polish`, `a2bbdfb`였다. 이 작업 시작 시 현재 저장소 main은 `5752cd2`로 오래된 상태였다. 이전 main의 iOS 번들 화면을 최신 TestFlight 화면으로 판단하지 않았다. 수정 브랜치는 `a2bbdfb`에서 만든 `codex/testflight-ux-audit-2026-09-09`다.

## 접수별 대조

| 접수 | 빌드 | 원문 | 점검 결과 |
|---|---|---|---|
| [9/6 09:48](https://appstoreconnect.apple.com/teams/2e5e8091-f836-45ac-974d-053174123af9/apps/6808960658/testflight/screenshots/AOnH1KOeVkE1Sfd3xrVPE60) | 0.8.0 (1) | 1. 홈버튼 정렬오류 2. 힌트보기 한국어는 한국어로, | 힌트 번역은 기존 수정에 포함돼 실제 한국어 표시 확인. 홈 글자의 세로 정렬은 여전히 위로 붙어 이번에 수정. 언어 전환 시 풀이 UI가 무너지는 추가 오류도 수정. |
| [9/6 09:49](https://appstoreconnect.apple.com/teams/2e5e8091-f836-45ac-974d-053174123af9/apps/6808960658/testflight/screenshots/ABwCYAbKSoQhiJWYZUpEE_E) | 0.8.0 (1) | 스키마보기등 시도보기들이 중복을 생성됨 | 기존 수정이 동작함. 스키마와 시도 버튼을 각각 반복 클릭해 카드가 중복 추가되지 않음을 확인. |
| [9/6 09:50](https://appstoreconnect.apple.com/teams/2e5e8091-f836-45ac-974d-053174123af9/apps/6808960658/testflight/screenshots/AGQfJwXTIq1zZ_wfhVO05m8) | 0.8.0 (1) | 좌우여백문제 반응형 최소 사이즈 문제인듯 | 기존 여백 수정 확인. 402px·320px에서 문서 가로 넘침 없음. 데이터 표 자체는 가로 스크롤을 사용함. |
| [9/9 22:23](https://appstoreconnect.apple.com/teams/2e5e8091-f836-45ac-974d-053174123af9/apps/6808960658/testflight/screenshots/AOElGKRGITh8V7ustS9a1-E) | 0.8.0 (2) | 아래 버튼들은 작동하지 않음, 버튼인가?? | 캡처의 작업 칩은 이벤트가 없는 span. 학습 모드에서 숨기려던 칩과 CLI 헤더가 CSS 때문에 노출됨. 이번에 숨김 규칙 복구. |

## 원인과 수정

1. `.block-command`, `.block-actions`의 `display:flex`가 HTML `hidden`을 무효화했다. 브라우저에서 `hidden:true`, `display:flex`, 실제 너비 348px를 확인했다. `.app-shell [hidden]`에 명시적 숨김 스타일을 적용해 의도한 학습 화면을 복구했다.
2. 홈 버튼에 `align-items:center`를 적용했다. 최소 44px 터치 영역과 문구 줄바꿈 방지를 유지했다.
3. KR/EN 전환 시 `rerenderBlocks()`가 DOM을 교체하지만 이전 enhancement 표식을 유지했고, 최상위 카드 추가만 관찰하는 코드가 재실행되지 않았다. 힌트·문제 목록 버튼이 없어지고 CLI가 다시 나타났다. 재렌더 완료 이벤트로 활성 풀이와 결과 도구를 복원하며 작성 SQL·힌트 펼침 상태를 보존한다. 언어 전환 자체가 편집기에 강제로 포커스를 주지 않도록 했다.

기본 흐름은 `홈 → 문제 선택/계속하기 → 문제와 SQL 편집기 → 실행·채점 → 다음 문제/학습경로`다. CLI는 고급 기능에서 접근하는 별도 작업 방식으로 다뤄야 한다.

## 화면 검증

아래 파일은 이번 작업에서 직접 캡처했다. TestFlight 원본을 표시한 화면과 로컬 재현 화면을 구분한다.

| 단계 | 결과 | 증거 |
|---|---|---|
| 1. 홈 | 시작·문제 선택 표시 정상 | `../.audit/testflight-2026-09-09/05-current-home.png` |
| 2. 문제 풀이 | 수정 전 CLI/작업 칩 노출, 수정 후 해소 | `06-before-practice.png`, `07-fixed-practice.png` |
| 3. 학습 보조 | 한국어 힌트 확인, 스키마·시도 반복 시 중복 없음 | 브라우저 AX 및 DOM 검증 |
| 4. 실행·채점 | 정답 4행, 시도 저장, 결과 표·흐름 탭 동작 | `08-fixed-result.png` |
| 5. 다음 문제·홈 | 다음 문제 정상, 홈 복귀 후 진행률 1/24 | `09-fixed-320px.png`, 브라우저 AX 검증 |

원본 접수 화면은 같은 폴더의 `01-feedback-home-hint.png`부터 `04-feedback-duplicates.png`에 저장했다. 브라우저 크기 검증은 실기기의 키보드·WKWebView·VoiceOver 검증을 대체하지 않는다.

검증 완료:

- `npm run ios:shell:test`
- `python3 app_shell/terminal_shell_prototype/practice_focus_smoke.py`
- `npm run rc:verify` 전체 통과. 첫 실행의 로컬 서버 바인드 제한은 권한 확장 후 동일 명령 재실행으로 해소.
- `npm run ios:sync`: 생성 번들을 iOS 프로젝트에 복사 완료.
- 복사한 iOS 런타임과 dist 런타임의 SHA-1 일치, 복사된 패키지의 홈→첫 문제 브라우저 확인.
- KR↔EN 전환 후 SQL·힌트 상태·문제 목록·결과 표·흐름 탭 유지.
- 402px 및 320px 문서 가로 넘침 없음.

## 출시 전 남은 확인

- 점검 당시 빌드 3은 테스트 준비 완료지만 테스트 그룹 미지정. 빌드 2는 내부 테스트 중이며 신규 피드백도 빌드 2에서 접수됐다. 빌드 2→3 커밋은 버전/암호화 설정 변경이며 이번 UI 수정은 포함하지 않는다.
- 이번 수정은 로컬 코드·iOS 리소스에만 반영했다. 새 archive/IPA 업로드, 그룹 배정, 실기기 설치, 접수 항목 승인/삭제는 하지 않았다.
- 후속 UX 정리: 한국어 채점 화면의 영어 결과 설명과 yes, beginner 등 혼용 문구; 고급 기능의 비활성 작업 칩. 현재 수정의 검증 완료 범위는 학습 흐름의 노출/정렬/언어 전환 오류다.
- 같은 iPhone 16 Pro에서 수정 빌드를 설치한 뒤 4건을 다시 확인해야 TestFlight 반영 완료로 판정할 수 있다.
