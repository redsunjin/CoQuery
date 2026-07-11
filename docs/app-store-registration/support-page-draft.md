# CoQuery Support Page Draft

Date: 2026-07-09
Status: Draft for a hosted support page before TestFlight/App Store submission.

Reference checked on 2026-07-09:

- Apple required properties include Support URL as platform version information: https://developer.apple.com/help/app-store-connect/reference/app-information/required-localizable-and-editable-properties/

## CoQuery Support

CoQuery is a TestFlight-first SQL practice shell for iPhone and iPad.

## What This Build Supports

- Bundled SQL practice problems.
- Sample schema inspection.
- Read-only practice queries.
- Local practice attempt review.
- Training Mode boundary checks.

## What This Build Does Not Support

- Production database connections.
- Production database credentials.
- Hosted public web service behavior.
- Embedded Python local server behavior.
- Provider-backed AI feedback as a required path.

## Tester Checklist

1. Launch the app.
2. Confirm Training Mode is visible.
3. Run `practice_list`.
4. Open a practice problem.
5. Submit a read-only SELECT answer.
6. Confirm any production database action is unavailable in the iOS Training shell.

## Known Limits

This is an early TestFlight shell. The first build is intended to validate packaging, launch behavior, and the bundled Training Mode practice path.

## Contact

Feedback email is pending Apple-side registration setup.
