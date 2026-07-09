# CoQuery Training TestFlight Metadata Checklist

Goal:

Launch Goal 4: iOS TestFlight Shell Skeleton

## App Identity

- App name: `CoQuery Training`
- Bundle ID: `app.coquery.training`
- Distribution target: TestFlight first, not public App Store release yet
- Primary category: Education or Developer Tools
- First release scope: SQL practice and beginner training only

## Beta App Information

- Short description explains that CoQuery Training is a local SQL practice shell.
- Beta notes state that the build does not connect to production databases.
- Beta notes state that the first build uses bundled sample practice data.
- Feedback contact is set for tester reports.
- Demo account is not required for the first local-only shell.

## Review Safety Notes

- No production DB credentials are requested.
- No Python local server is embedded or started inside the iOS app.
- No provider API key is required for the first TestFlight shell.
- Any future provider-backed feedback must be clearly labeled and stay inside Training Mode.

## Assets Still Needed Before Upload

- iPhone screenshot candidates: `app_store_assets/ios-registration/screenshots/iphone-69/`
- iPad screenshot candidates: `app_store_assets/ios-registration/screenshots/ipad-13/`
- App icon candidate: `app_store_assets/ios-registration/icons/app-icon-1024.png`
- App Store Connect metadata draft: `docs/app-store-registration/app-store-connect-metadata.md`
- Privacy policy draft: `docs/app-store-registration/privacy-policy-draft.md`
- Support page draft: `docs/app-store-registration/support-page-draft.md`
- Screenshot upload plan: `docs/app-store-registration/screenshot-plan.md`
- Hosted privacy/support URLs still need to be created outside the repo before App Store submission.
- Marketing URL can be omitted for the first TestFlight registration unless a public landing page is available.

## Verification Before External Testers

- `npm run ios:shell:test` passes.
- `npm run ios:sync` completes.
- iPhone simulator launches the shell and shows `practice_list`.
- iPad simulator launches the shell and shows `practice_list`.
- TestFlight build uploads through App Store Connect.
