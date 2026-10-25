# CoQuery TestFlight 0.8.0 (8)

2026-10-26 KST. App ID `6808960658`, bundle `app.coquery.training`.

## 소스와 검증

- 병합된 main `0773fb035aa02dfb0d22bb80e263cd2f4e3758c9`에 빌드 번호만 7→8로 변경했다. 버전은 0.8.0이다.
- 개념 탐구·예상/실험·반례·설명·전이·나만의 퍼즐과 넓은 화면의 좌우 배치, iPhone Duo 창 크기/안전 여백/세로 분할 영역 전달이 포함된다. 기존 SQL 연습과 9개 퍼즐을 유지한다.
- `npm run ios:sync`, `npm run rc:verify` 통과. 최초 제한 실행에서 로컬 테스트 서버가 열리지 않아 권한이 허용된 환경에서 전체 검사를 다시 통과했다.
- Xcode 27.1 (27A9275), iphoneos27.1 SDK, Release 서명 아카이브 성공. `codesign --verify --deep --strict` 통과. 제한된 환경의 인증서 신뢰 조회 실패는 권한이 허용된 검증에서 재확인했다.
- 아카이브의 bundle/version/build와 비면제 암호화 미사용 설정을 확인했다. index.html, exploration.js, concept-puzzles.css, onboarding.js, concept-puzzles.js, community-demo.js가 최종 dist/ios-shell과 바이트 단위로 일치한다.

## 베타 검증 범위

[직전 화면·Duo 대표 경로 검증](adaptive-duo-implementation-2026-10-26.ko.md)을 근거로 한다. 실제 iPhone/iPad/Duo 및 실제 SQL 초보자 검증은 수행하지 않았다. 사용자는 기기와 참여자가 아직 확보되지 않았다고 답했다. 모집 연락이나 새 테스터 초대는 하지 않는다.

실제 한글 조합 중 접기, VoiceOver 전체 탐색, 두 앱 나란히 사용, 모든 가림/상하 접힘 조합은 미검증이다. 시뮬레이터의 일반 JS Eval 및 Apple WebKit 접근성 경고 원인·영향 확인은 후속 출시 관문에 남아 있다. 내부 기능 베타 배정이 완제품·접근성·학습 효과 검증 완료를 뜻하지 않는다.

App Store 심사 제출·공개 출시·공개 웹 배포는 범위에 포함하지 않는다.

## 배포 결과

- 2026-10-26 01:14 KST `xcodebuild -exportArchive`의 `Upload succeeded`/`EXPORT SUCCEEDED`를 확인했다. App Store Connect 업로드 목록에서도 0.8.0(8) 처리 중을 확인했다.
- Apple의 계약 갱신 알림이 있으나 이번 서명·업로드는 통과했다. 이 작업에서 계약 동의를 대신 진행하지 않았다.
