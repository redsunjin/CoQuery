# iOS 학습 흐름 시뮬레이터 검증 — 2026-10-25

## 환경과 방법
- 시작 기준: main b94bba2, Capacitor 8.4.3. 수정 브랜치: fix/ios-simulator-learning-qa.
- Xcode 27.1, Release/arm64 시뮬레이터 빌드, 서명 없음. iPhone 17e / iOS 27.0의 실제 설치 앱(capacitor://localhost)에서 검증했다.
- XcodeBuildMCP로 빌드·설치·실행·스크린샷을 확인하고, serve-sim의 WebKit 검사 도구를 통해 실제 WKWebView 안의 DOM 버튼과 input/change/submit 이벤트로 흐름을 실행했다. 데스크톱 브라우저의 동일 페이지로 대체하지 않았다.
- 접근성 도구는 웹뷰 버튼을 노출하지 않았고, 미러의 HID 터치는 기록되지만 화면 전환으로 확인되지 않았다. 따라서 **손가락 터치·키보드 사용성, VoiceOver 검증 완료를 주장하지 않는다.** 도구 문제인지 앱의 입력 처리 문제인지는 확정하지 못했다. 별도 직접 터치 검증이 필요하다. 후속 네이티브 앱 탐색에서 컴퓨터 사용 도구가 Mac 잠금 상태이며 자동 잠금 해제가 불가능하다고 보고했다. 사용자에게 수동 잠금 해제를 요청했다. 이 상태를 직접 입력 검증의 환경 제약으로 기록하며, 앞선 미반영 입력의 원인까지 확정하지는 않는다.
- iPhone Duo / iOS 27.1에도 설치·프로세스 실행을 시도했으나 화면이 검게 캡처되어 기능 검증 범위에서 제외했다.

## 발견 및 수정
1. 기존 앱은 빌드는 성공하지만 iOS 27.0 실행 직후 종료됐다. 크래시 스택의 `UIApplicationEvaluateRuntimeIssueForNoSceneLifecycleAdoption`와 누락된 scene manifest를 확인했다.
   - 단일 UIWindowScene 설정과 SceneDelegate를 추가했다. 기존 Main.storyboard의 CAPBridgeViewController와 웹 UI를 그대로 사용한다.
   - URL 및 사용자 활동을 Capacitor 프록시에 전달하는 초기 연결/실행 중 콜백을 유지했다. 링크 유입 자체의 런타임 검증은 이번 범위에 포함하지 않았다.
2. iOS 번들에 없는 `manifest.webmanifest`를 요청하는 오류를 네이티브 웹뷰 콘솔에서 확인했다.
   - iOS HTML 생성 단계에서만 PWA manifest 링크를 제거했다. 웹 PWA의 원본 HTML·manifest·서비스 워커는 변경하지 않았다.

## 실제 수행 결과
| 영역 | 실행한 확인 | 결과 |
|---|---|---|
| 네이티브 시작 | 수정 후 Release 빌드·설치·실행 및 재실행 | 학습 홈 정상 표시, 시작 종료 재발 없음 |
| SQL | 첫 문제에서 `SELECT id, name, region FROM customers ORDER BY id;` 실행·채점 | 4행 반환, 정답, 로컬 시도 저장 |
| C1/C2/C3 | 빈 예상의 오답 피드백, A / A·B·C / Q·R 선택의 정답 피드백 | 모두 확인 |
| C3 전이 | 10 초과 조건으로 바꾸어 R만 예상 | 정답 및 경계값 설명 확인 |
| R1/R2/R3 | 예상 3/4/7행 입력 및 계산 결과 | 각각 3/4/7행 확인 |
| R3 전이 | ID 기준 연결, 예상 4행 | 정답, 실제 4행, 이름 중복 반례 설명 확인 |
| U1/U2/U3 | 최소 2점·신규만 선택, 목표 2/2·2/2·3/3 입력 | 목표 충족 피드백 확인 |
| 기록 | C3 자기 설명 저장, 별도 페이지 왕복 및 앱 재빌드·재실행 | 9개 실험 기록·C3 설명·SQL 1개 정답 기록 복원, 홈 1/24 |
| 참여형 정상 | 질문 검사→사람 발행 대기→승인→근거/반례/대안 답변 제출→사람 승인→요약 | 사실/의견/가설과 원문 연결 표시 확인 |
| 신고·항소 | 신고→검토 지연→M1 임시 비공개→항소→재심 지연→M2 원결정 변경 | 공개 복원, 요약 재검토, 모의 감사 이력 확인 |
| 예외 | 검사·답변·요약의 실패/대기에서 취소, 질문 제출 철회 | 초안·답변 보존, 자동 공개 없음 확인 |
| 취소 | 신고 철회, 항소 취소 | 원결정 유지 및 요약 확인 무효화 확인 |
| 폭 | 퍼즐 및 참여형 화면의 scrollWidth와 viewport 비교 | 가로 넘침 없음 |
| 최종 자산 | 재빌드 앱의 manifest 링크 및 웹뷰 콘솔 확인 | manifest 링크 없음, 해당 누락 요청 오류 재발 없음 |

실제 AI·서버·다른 참여자와 연결하지 않았다. 참여형 데이터는 모의이며 페이지 전환 시 소멸한다. 실사용자·미성년자 대상 검증, 실기기, 모든 iOS 버전, 터치·접근성·회전·배경 복귀의 종합 검증은 수행하지 않았다. 런타임에 Capacitor의 일반적인 `JS Eval error A JavaScript exception occurred` 1줄과 시뮬레이터 WebKit 접근성 클래스 중복 경고가 남았으며, 이 문구만으로 기능 오류의 원인을 확정하지 않았다. 실제 학습 결과 검증 중 관찰된 JavaScript error/unhandledrejection 이벤트는 없었다.

## 회귀 검사와 리뷰
- 새 plist 파싱 검사는 실제 scene 설정, 기존 Capacitor storyboard 연결, 컴파일 대상 delegate, 초기/실행 중 링크 전달 계약을 확인한다. 네이티브 실행 검사를 대신하지 않는다.
- iOS 자산 smoke는 생성된 HTML에 PWA manifest 링크가 없는지 확인한다.
- 로컬 rc:verify 전체, 의존성 보안 smoke, npm audit(0건) 통과.
- 코드 검토 범위: 단일 창 구성, storyboard 소유권, 기존 Capacitor 링크 전달, 원본 PWA 무변경, 번들 생성·회귀 검사. 별도 사람 또는 독립 에이전트의 승인 리뷰는 수행하지 않았다.
- 원격 검사 및 병합 결과는 PR에서 확인한다. 배포·앱스토어 제출은 수행하지 않는다.

근거: [Apple의 scene 생명주기 전환 안내](https://developer.apple.com/documentation/uikit/transitioning-to-the-uikit-scene-based-life-cycle).
