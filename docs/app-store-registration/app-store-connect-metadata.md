# CoQuery Training App Store Connect Metadata Draft

Date: 2026-07-09
Scope: iPhone/iPad registration package for the TestFlight-first Training Mode app.

References checked on 2026-07-09:

- Apple App Store Connect required properties: https://developer.apple.com/help/app-store-connect/reference/app-information/required-localizable-and-editable-properties/
- Apple App Store Connect app privacy: https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/
- Apple App Store Connect TestFlight test information: https://developer.apple.com/help/app-store-connect/test-a-beta-version/provide-test-information/

## App Record

| Field | Draft value |
| --- | --- |
| App name | CoQuery Training |
| Bundle ID | app.coquery.training |
| SKU | coquery-training-ios |
| Primary language | English (U.S.) |
| Primary category | Education |
| Secondary category | Developer Tools |
| Distribution target | TestFlight first |
| First public release posture | Not ready for public App Store sale until signed build, hosted URLs, and real screenshots are validated |

## Version Metadata

| Field | Draft value |
| --- | --- |
| Version | 0.8.0 |
| Copyright | 2026 CoQuery |
| Support URL | `https://redsunjin.github.io/CoQuery/support/` after GitHub Pages is enabled for `main` `/docs` |
| Marketing URL | Optional; can be omitted for first TestFlight |
| Privacy Policy URL | `https://redsunjin.github.io/CoQuery/privacy/` after GitHub Pages is enabled for `main` `/docs` |

## Product Page Copy

### Subtitle

SQL practice shell

### Promotional Text

Practice SQL with bundled sample data before connecting any real database.

### Description

CoQuery Training is a focused SQL practice shell for learning query habits safely on iPhone and iPad.

The first iOS build is Training Mode only. It uses bundled sample data, local practice commands, and clear command output so testers can learn SQL flow without creating an account, adding an API key, or connecting to a production database.

What testers can try:

- List built-in SQL practice problems.
- Inspect the sample schema.
- Run read-only SELECT practice commands.
- Review local attempt feedback.
- See the boundary between Training Mode and future Production Assist workflows.

Current limits:

- This build is not a hosted public web service.
- This build is not a production database client.
- The Python local server is not embedded in the iOS app.
- Provider-backed AI feedback is not required for the first TestFlight shell.

### Keywords

SQL,database,SQLite,practice,training,developer,query,learning

### What's New

Initial TestFlight registration package for the CoQuery Training iOS shell. This build focuses on bundled SQL practice data and Training Mode boundaries.

## TestFlight Beta Information

### Beta App Description

CoQuery Training is a TestFlight-first SQL practice shell. This beta uses bundled sample data and local Training Mode commands only. It does not connect to production databases, request production credentials, or require API keys.

### What to Test

1. Launch the app on iPhone and iPad.
2. Confirm the shell opens in Training Mode.
3. Run `practice_list`.
4. Inspect a practice schema.
5. Run a practice grading flow.
6. Confirm Production Assist / production database flows are clearly unavailable in this iOS Training shell.

### Feedback Email

Pending Apple-side account decision.

### Demo Account

Not required. The first TestFlight shell is local-only and does not use accounts.

## Review Notes

This iOS build is a Training Mode shell. It uses bundled sample SQL practice data and local app storage only.

No production database credentials are requested. No Python local server is embedded or started inside the iOS app. No provider API key is required for the first TestFlight build. Production Assist remains out of scope for this iOS Training release.

## Privacy Draft

Suggested App Privacy response for the current first-TestFlight scope:

- Data collection: No, this app does not collect data from the app.
- Tracking: No.
- Third-party analytics/advertising SDKs: None in the current iOS shell scope.

Recheck this before submission if any remote provider, analytics, crash reporting, account, telemetry, or feedback upload is added.

## Apple-Side Values Still Required

- Apple Developer Team ID.
- App Store Connect app record owner.
- Hosted support URL.
- Hosted privacy policy URL.
- Final feedback email.
- Export compliance answer for the signed build.
- Age rating questionnaire answers.
