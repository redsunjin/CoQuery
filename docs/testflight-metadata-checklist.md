# CoQuery TestFlight Metadata Checklist

Goal:

Launch Goal 4: iOS TestFlight Shell Skeleton

## App Identity

- App name: `CoQuery`
- Bundle ID: `app.coquery.training`
- Distribution target: TestFlight first, not public App Store release yet
- Primary category: Education or Developer Tools
- First release scope: SQL practice and beginner training only

## Beta App Information

- Short description explains that CoQuery is a local SQL practice shell.
- Beta notes state that the build does not connect to production databases.
- Beta notes state that the first build uses bundled sample practice data.
- Feedback contact is set for tester reports.
- Demo account is not required for the first local-only shell.

## Review Safety Notes

- No production DB credentials are requested.
- No Python local server is embedded or started inside the iOS app.
- No provider API key is required for the first TestFlight shell.
- Any future provider-backed feedback must be clearly labeled and stay inside Training Mode.

## Repository Package Ready

- iPhone screenshot candidates: `app_store_assets/ios-registration/screenshots/iphone-69/`
- iPad screenshot candidates: `app_store_assets/ios-registration/screenshots/ipad-13/`
- Approved primary app icon: `app_store_assets/ios-registration/icons/app-icon-1024.png`
- Approved brand master: `app_store_assets/brand/coquery-liquid-glass-sql-tokens-master-v4.png`
- App Store Connect metadata draft: `docs/app-store-registration/app-store-connect-metadata.md`
- Privacy policy page source: `docs/privacy/index.html`
- Support page source: `docs/support/index.html`
- Privacy policy draft: `docs/app-store-registration/privacy-policy-draft.md`
- Support page draft: `docs/app-store-registration/support-page-draft.md`
- Screenshot upload plan: `docs/app-store-registration/screenshot-plan.md`
- GitHub Pages is enabled from `main` `/docs`.
- Privacy Policy URL verified with HTTP 200 on 2026-07-11: `https://redsunjin.github.io/CoQuery/privacy/`
- Support URL verified with HTTP 200 on 2026-07-11: `https://redsunjin.github.io/CoQuery/support/`
- Marketing URL can be omitted for the first TestFlight registration unless a public landing page is available.

## Repository Verification (2026-07-11)

- `npm run rc:verify` passes: release contract, 121 core CLI/Command API tests, terminal shell, local packaging, and iOS shell smoke.
- `npm run ios:sync` completes.
- Release iOS Simulator build passes with `CODE_SIGNING_ALLOWED=NO`.
- GitHub Actions `baseline`, `postgresql-smoke`, and `pages-build-deployment` pass for commit `124ee89`.

## Remaining Before External Testers

- Select the Apple Developer Team and confirm the App ID for `app.coquery.training`; `DEVELOPMENT_TEAM` is intentionally not committed in the project.
- Create or confirm the App Store Connect app record using the final App name, Bundle ID, SKU, category, and feedback email.
- Complete App Privacy, export compliance, and age-rating answers in App Store Connect.
- Open the signed archive in Xcode Organizer, validate, and upload it to App Store Connect.
- On physical iPhone and iPad, launch the signed build and run `practice_list`; include the mobile focus/auto-zoom check recorded in `docs/terminal-shell-mobile-ux-verification-2026-07-11.md`.
