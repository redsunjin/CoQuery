# CoQuery 소개 사이트·앱 등록 자산 인덱스

최종 갱신: 2026-10-25 (한국 시간).

## 저장소와 공개 주소

| 용도 | 위치 |
|---|---|
| 앱·제품 원본 | https://github.com/redsunjin/CoQuery |
| 소개 사이트 배포 원본 | https://github.com/e3o-labs/e3o-labs.github.io/tree/main/coquery |
| 소개 | https://e3o-labs.github.io/coquery/ |
| 지원 | https://e3o-labs.github.io/coquery/support/ |
| 웹사이트 개인정보 안내 | https://e3o-labs.github.io/coquery/privacy/ |
| 기존 iOS 학습 앱 개인정보 정책 | https://redsunjin.github.io/CoQuery/privacy/ |

Trip119·myquant-lite와 같은 서비스별 폴더 구조를 사용한다. 소개 사이트의 수정 원본은 이응랩스 저장소의 `coquery/`이며, 제품 저장소의 outputs 사본을 최신 배포 원본으로 간주하지 않는다.

## 실제 반영 기록

- 2026-10-25: 이응랩스 main에 `coquery/index.html`, `style.css`, `support/index.html`, `privacy/index.html`, 기존 앱 아이콘·학습 홈 이미지와 루트 서비스 링크를 추가했다.
- 반영 커밋: [226a4fccd1cb9e36ef74ed25c2ed8c5f9c7b73d5](https://github.com/e3o-labs/e3o-labs.github.io/commit/226a4fccd1cb9e36ef74ed25c2ed8c5f9c7b73d5).
- 배포 상태: 공개 소개 URL의 HTTP 200과 최신 문구를 2026-10-25에 확인했다. GitHub Pages 배포 성공 확인. 실행: [40165137910](https://github.com/e3o-labs/e3o-labs.github.io/actions/runs/40165137910).
- 기존 승인 앱 아이콘을 사용했다. 소개 화면의 앱 이미지는 2026-09-09 로컬 캡처를 참고 이미지로 사용한 것으로, 최신 서명 앱의 제출용 스크린샷이 아니다. 이 이력은 내부 인덱스에만 남겼다.
- 공개 페이지는 정식 출시 준비 중이라고 안내한다. App Store 공개 다운로드·TestFlight 외부 초대·개념 퍼즐 제공을 주장하지 않는다.
- 공개 개인정보 페이지는 소개 웹사이트의 접속·문의 처리 범위를 안내한다. 기존 앱 정책을 연결하되 정식 앱 제출용 정책 확정으로 간주하지 않는다. 문의는 다른 이응랩스 서비스와 같은 redsunjin@gmail.com을 연결했다.

## 앱 완성 후 함께 갱신할 항목

1. 실제 제공 기능·대상 플랫폼·버전을 확인해 소개와 FAQ를 수정한다. PR #22의 개념 퍼즐·참여형 검토는 실제 통합·검증된 범위만 안내한다. 실제 사용자 검증과 합성 페르소나 검토는 구분한다.
2. 최신 서명 빌드에서 iPhone·iPad 스크린샷을 새로 촬영해 소개 이미지와 App Store 자산을 교체한다. 원본에 버전·빌드·기기·OS·언어·커밋·촬영일을 기록한다.
3. 실제 수집·전송·SDK·AI/공유·계정·로컬 기록·백업/삭제·문의 처리에 맞춰 앱 개인정보 정책과 App Store 개인정보 응답을 함께 갱신한다. 운영자·시행일·연락처를 최종 확인한다.
4. 공개 App Store 출시 후 검증된 다운로드 URL을 추가한다. 출시 전에는 다운로드 버튼이나 임의의 앱 링크를 넣지 않는다.
5. 지원 안내·한국어/영어 스토어 문구·공개 URL을 맞추고, 페이지 연결·작은 화면·키보드·GitHub Pages 성공 상태를 확인한다.
6. 후속 커밋·배포 실행·검증일을 이 문서의 반영 기록에 추가한다. 기존 출처와 상태 기록을 덮어써서 과거와 현재를 혼동하지 않는다.

자동 업데이트나 예약 작업은 설정하지 않았다. 앱 완성 후 실제 기능을 확인한 작업에서 위 항목을 함께 갱신한다.

## 관련 자산과 과거 기록

- [기존 등록 문구](app-store-registration/app-store-connect-metadata.md)
- [기존 스크린샷 계획](app-store-registration/screenshot-plan.md)
- [아이콘 승인 결정](brand-icon-decision-2026-07-11.md)
- [9월 TestFlight 화면 점검](testflight-ux-audit-2026-09-09.md)
- [PR #22 개념 퍼즐 기획](https://github.com/redsunjin/CoQuery/pull/22)
- 로컬 검토 패키지: `outputs/coquery-appstore-2026-10-25/README.md`. outputs는 이번 제작 산출물이며 공개 사이트의 유지보수 원본이 아니다.

## 제품 전환 후속 변경안 (미배포)

2026-10-25: [제품 전환 감사](product/transition-audit-2026-10-25.ko.md), [공식 소개·지원 원문 기준 변경안](product/public-site-proposal/README.md), [스토어 초안](product/store-copy-draft.ko.md)을 준비했다. 제품 저장소에 둔 검토 자료이며 공개 사이트 원본을 수정/배포한 것이 아니다. 연결된 조건 탐구는 현재 TestFlight 0.8.0(7)에 포함되지 않는다. 기존 앱 개인정보 정책은 유지한다.
