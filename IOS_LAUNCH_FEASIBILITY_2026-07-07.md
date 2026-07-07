# CoQuery iOS Launch Feasibility And Packaging Decision

Date: 2026-07-07

Goal:

```text
Launch Goal 2: iOS Launch Feasibility And Packaging Decision
```

## Decision

CoQuery can proceed toward an iOS release, but the current repository cannot be submitted directly as an iOS app.

The selected launch path is:

```text
TestFlight-first iOS Training App
  -> Capacitor iOS shell
  -> local Training Mode runtime
  -> no production DB connection
  -> no embedded Python local server
```

The first iOS release target should be a training-focused app:

- DB-free SQL practice datasets
- SQL editor and terminal-style result blocks
- schema viewer
- grading and wrong-attempt review
- Korean/English beginner help
- optional cloud LLM feedback only after privacy and provider storage are implemented

Production DB assistance remains out of scope for the first iOS app. It should return later as a controlled `Production Assist` mode after safety gates are implemented.

## Current Evidence

Current repo state:

- `app_shell/terminal_shell_prototype` is a local browser-based terminal shell.
- `sql_cli.command_api.run_command` is a Python adapter over existing CLI handlers.
- `practice_packs/sql_basics.json` supports DB-free practice.
- There is no `ios/`, Xcode, Capacitor, SwiftUI, Tauri, or Electron project in the repository.
- The app shell is verified for mobile width, but it still depends on the local Python server for Command API execution.

Official platform constraints checked on 2026-07-07:

- Apple App Review expects submitted apps to be complete, tested, and functional, with complete metadata and live backend access when a backend is required: https://developer.apple.com/app-store/review/guidelines/
- Apple's minimum-functionality guidance says an app must be more than a repackaged website and provide useful, unique, app-like value: https://developer.apple.com/app-store/review/guidelines/
- TestFlight supports beta distribution before public App Store release and requires beta app information plus App Review approval for external testers: https://developer.apple.com/testflight/
- Capacitor provides a native iOS runtime, uses WKWebView, is managed with Xcode, and supports iOS 15+ in the current docs: https://capacitorjs.com/docs/ios

## Option Matrix

| Option | Decision | Reason |
| --- | --- | --- |
| Current Python local server inside iOS app | Reject | Too much packaging risk. The current app shell expects a Python HTTP server, which is not a clean App Store runtime boundary. |
| PWA only | Reject for App Store | Useful as a demo channel, but it is not an App Store package and does not satisfy the iOS app launch goal. |
| Native SwiftUI app | Defer | Strongest long-term native fit, but it duplicates the existing HTML/JS terminal shell too early. |
| Capacitor iOS shell with local training runtime | Select | Reuses the current responsive terminal UI direction while allowing an App Store/TestFlight package through Xcode. |

## Runtime Boundary

The iOS app must not rely on `python app_shell/terminal_shell_prototype/server.py`.

The current Python Command API remains the reference implementation, but the iOS app needs an iOS-safe runtime:

```text
Current local prototype
  HTML/CSS/JS shell
  -> Python Command API
  -> Python practice/query/help handlers

iOS Training App target
  Capacitor WebView shell
  -> local Training Runtime contract
  -> bundled practice packs
  -> native SQLite or equivalent local query executor
  -> local attempt storage
```

The next implementation should extract the Training Mode command contract so the same UI concepts can run without the Python HTTP server.

## App Store Positioning

Public positioning for the first iOS release should be narrow:

```text
CoQuery Training
Learn SQL with a terminal-style practice app.
```

Do not position the first iOS release as:

- production DB client
- BI dashboard
- autonomous SQL agent
- local LLM production query generator
- enterprise database connector

## First TestFlight MVP

Minimum TestFlight scope:

- Problem list
- Schema viewer
- SQL editor
- Query result rows
- Grading result
- Wrong-attempt list
- Korean/English help and terminology
- Local-only sample dataset storage

Excluded from first TestFlight:

- production DB connections
- production metadata upload
- live operational SQL execution
- local LLM runtime
- provider-backed feedback unless API key storage and privacy copy are implemented
- subscriptions or payments

## Security And Privacy Decisions

- Training Mode may use bundled or user-created practice datasets.
- Production schema, production query prompts, and production SQL must not be sent to external LLM providers in the first iOS release.
- If provider feedback is added, API keys must use iOS secure storage such as Keychain through a native bridge or vetted Capacitor plugin.
- Attempt logs should remain local until explicit export/sync is designed.
- The app must include a clear privacy boundary before any App Store submission.

## Launch Gates For iOS

The iOS launch track is not ready until all gates below are true:

- An `ios/` app project exists and builds through Xcode.
- The app runs on iPhone and iPad simulator/device.
- Training Mode works without starting a Python server.
- Practice pack loading, query execution, grading, and attempts work inside the iOS runtime.
- Korean and English UI labels fit on phone widths.
- No horizontal scroll appears on iPhone viewport.
- App metadata, privacy notes, and review notes are drafted.
- TestFlight build can be uploaded through App Store Connect.

## Next `/goal`

Recommended next implementation unit:

```text
Launch Goal 4: iOS TestFlight Shell Skeleton
```

Done when:

- Capacitor project files exist.
- `ios/` project exists.
- The shell can load the current terminal UI.
- `postCommand` can call a local Training Runtime adapter for at least `practice_list`.
- iPhone and iPad simulator verification instructions are documented for Mac.

Training Runtime Contract is now documented in `IOS_TRAINING_RUNTIME_CONTRACT_2026-07-08.md`.
