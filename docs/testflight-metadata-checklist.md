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

- iPhone screenshots from simulator or device.
- iPad screenshots from simulator or device.
- App icon set.
- Privacy nutrition answers.
- Support URL.
- Marketing URL, if needed.

## Verification Before External Testers

- `npm run ios:shell:test` passes.
- `npm run ios:sync` completes.
- iPhone simulator launches the shell and shows `practice_list`.
- iPad simulator launches the shell and shows `practice_list`.
- TestFlight build uploads through App Store Connect.
