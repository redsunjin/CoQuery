# 조건 탐구 구현 검증

2026-10-25 KST. 최신 main 086aaba에서 별도 codex/concept-exploration-journey 브랜치로 수행했다. **개발자 기능 점검이며 실제 사람의 학습 검증이 아니다.**

## 실행과 결과

| 검사 | 실행 범위 | 결과와 제한 |
|---|---|---|
| 전체 회귀 | npm run rc:verify | 통과. 기존 SQL/CLI·Command API 121검사, 9퍼즐, 참여형 예외, 셸·방언·iOS 자산·새 조건 탐구 포함 |
| 추가 기존 계약 | pwa_serverless_smoke.py, learning_path_smoke.py | 통과. 실제 설치형 PWA의 장기 캐시/업데이트 관찰이 아님 |
| 조건 계산 | tests/exploration_smoke.mjs | 4항목 × 2조건의 256개 데이터 배치 × AND/OR=512 계산, 빈/전체 결과 포함. 별도 산술 기준과 대조하고 생성된 SQL 512개를 실제 SQLite(sql.js)에서 실행해 동일 결과 확인 |
| 상태·이벤트 계약 | 같은 테스트 | 버전/잘못된 저장값 복구, 선택 정규화, 단계 미충족, 창작 저장 요건, 수정 후 결과 무효화, 편집본/저장본 분리, 재실행, HTML 이스케이프, 저장소 차단의 임시 기록 표시 통과 |
| 브라우저 기본 여정 | 새 localhost:8803, dist/ios-shell 자산, 인앱 브라우저 | 홈→이해→안내형 빈 예상/오답/정답→독립형 A/B/C→반례 A 오답/다음 차단→B→한글 자기 설명→책 선택 A/B/C→설명→창작 실행·저장 확인 |
| 창작 변경·복원 | 같은 브라우저 | 제목/조건 이름 변경·설명 기록·저장. 미저장 제목 변경 후 저장본 불러오기에서 원래 제목 복구. B의 두 번째 조건 변경 후 A/B 2개 결과로 재계산 확인 |
| 재방문/SQL 왕복 | 같은 브라우저 | 새로고침 후 창작 단계와 한글 기록 복구. SQL 학습 첫 문제 진입→홈→탐구 복귀. SQL 진행률 0/24 유지 확인(정답 제출은 안 함) |
| SQL 선택 표현 | 같은 브라우저 | 편집된 참/거짓이 CTE 예시에 반영됨. SQL 엔진 실행 결과가 아님을 UI에 명시 |
| 모바일 재배치 | 390×844 브라우저 | 6단계 각각 document.scrollWidth=390, viewport=390. 창작 화면 시각 확인. 실제 iPhone/Safari·확대·음성 검증 아님 |
| 키보드/초점 | 브라우저와 이벤트 코드 | 진입/단계 제목, 결과 제목, 선택 후 컨트롤 초점 확인. 전체 키보드 단독 완주와 실제 스크린리더는 미실시 |
| iOS 동기화 | npm ci → npm run ios:sync | 통과. 오래된 로컬 node_modules의 Capacitor 8.4.1이 생성 파일을 낮추는 문제를 잠금 버전 재설치로 제거. Package.swift 최종 변경 없음 |
| iOS 컴파일 | xcodebuild, App Debug, generic iOS Simulator, CODE_SIGNING_ALLOWED=NO | BUILD SUCCEEDED. /tmp 전용 DerivedData 사용. 이번 앱 설치·실행·실기기·TestFlight 검증 아님 |
| 소개/지원 변경안 | 공식 사이트 main def79e8b9568a612db9838665a9eee2b3b6a8851 원문 | 로컬 패치 적용 가능성 git apply --check 통과. 공식 사이트 쓰기/배포 안 함 |

최초 로컬 회귀 실행은 OS의 로컬 서버 접근 제한으로 중단되었고, 허용된 실행 환경에서 재실행해 통과했다. 이를 제품 결함이나 검사 통과로 섞어 세지 않았다.

## 화면 증거

- [개념 중심 홈](conditions-exploration/home.png)
- [예상과 실험](conditions-exploration/experiment.png)
- [390px 창작 화면](conditions-exploration/mobile-create.png)
- [390px 결과·SQL 선택 안내](conditions-exploration/mobile-result.png)

입력한 설명은 개발자 시험 문구다. 사람의 이해나 자연스러운 사용자 반응을 관찰한 자료가 아니다. 이 화면은 현재 TestFlight 0.8.0(7)의 스크린샷이 아니다.

## 자체 코드 검토와 잔여 관문

입력은 HTML 이스케이프하며 자유 문장을 SQL/JavaScript로 실행하지 않는다. 저장 데이터는 제한된 버전·유형·길이로 복구한다. 네트워크/AI 요청을 추가하지 않았다. 조건 탐구 키만 삭제하며 기존 SQL/9퍼즐 키를 변경하지 않는다. 초안 수정은 저장본을 덮어쓰지 않고 명시적 저장만 저장본을 갱신한다. 결과 수정은 이전 checked를 지운다. 단계 이동은 실험 기록이나 숙달을 자동 생성하지 않는다. 다음 버튼의 필요한 기록 확인은 학습 능력 평가가 아니며 단계 메뉴를 통한 자유 이동을 허용한다.

실제 초보자 모집/관찰·독립 교육자 검토는 미실시다. 물리 iPhone·음성/로터 연속 탐색·실제 200% 확대·저장소 퇴거·설치형 PWA 업데이트/오프라인·iOS 실행은 이번 미실시 항목이다. 웹/iOS 자산 공유와 컴파일만으로 동등한 경험을 단정하지 않는다. PR의 CI/리뷰/병합 이력은 GitHub 최종 상태를 따르며 이 자체 검토를 독립 리뷰 승인으로 부르지 않는다.

관련: [전환 감사](../product/transition-audit-2026-10-25.ko.md), [실제 사용자 검증과 출시 기준](../product/novice-validation-and-release-gates.ko.md).

## PR #33 자동 리뷰 후 보완

자동 코드 리뷰가 선택 SQL 예시의 줄바꿈이 실제 개행 대신 역슬래시+n으로 표시되어 복사 실행이 실패하는 P2 문제를 찾았다. sqlFor 생성 함수를 분리하고 실제 개행을 사용하도록 수정했다. 표시에만 의존하던 검사를 보강해 512개 참/거짓 조합의 SQL을 SQLite에서 실행·결과 비교한다. 이 검사를 CI에서 재현하도록 baseline에 잠금 의존성 설치를 추가했다. UI 자체가 SQL 엔진을 실행한다는 의미는 아니며 선택 표현의 유효성을 검증한 것이다.
