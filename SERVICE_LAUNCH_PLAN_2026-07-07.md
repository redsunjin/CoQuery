# CoQuery Service Launch Plan

Date: 2026-07-07

## Launch Objective

CoQuery's launch target is a practical AI-assisted SQL learning and controlled query assistant that can be used without immediate production DB access, while preserving a path to governed production DB support.

The first service release should not claim to be a full BI platform. It should launch as:

```text
CLI-first SQL assistant
  + mobile/tablet/desktop terminal shell
  + DB-free practice dataset sandbox
  + bilingual beginner guidance
  + provider presets for learning feedback
  + future governed local-LLM production assist
```

## Product Positioning

Primary message:

```text
Learn freely. Query production carefully.
```

Korean product message:

```text
학습은 자유롭게, 운영 조회는 통제되게.
```

Current product boundary:

- CoQuery is not a complete BI dashboard.
- CoQuery is not yet a packaged mobile app.
- CoQuery is not yet a production DB agent.
- CoQuery is currently a verified CLI core plus local responsive terminal shell prototype.
- CoQuery's iOS path is now a TestFlight-first Training App skeleton with a Capacitor iOS project.

## Launch Tracks

### Track 1: Training Mode

Purpose:

- Help non-specialists learn SQL and query concepts without connecting to real databases.
- Use built-in sample datasets.
- Support Korean/English beginner explanations.
- Allow low-cost or commercial LLM APIs for education, feedback, and practice support.

Launch requirements:

- Practice problem list and schema viewer are usable from the app shell.
- User can submit SQL from the app shell.
- Result and grading appear as terminal blocks.
- Wrong attempts are saved locally.
- Wrong-note review is visible in the UI.
- Optional provider-backed feedback is clearly labeled as AI feedback.

### Track 2: Local App Shell

Purpose:

- Preserve the CLI mental model while making CoQuery usable on phone, tablet, and desktop.
- Keep every UI action reproducible through a CLI equivalent.

Launch requirements:

- No horizontal page scroll on phone widths.
- Korean and English labels are complete for visible menus, buttons, panels, and help text.
- Korean font stack is readable on Windows, macOS, and mobile browsers.
- App shell can run locally without a hosted backend.
- App shell can later be packaged through a desktop/mobile wrapper if needed.

### Track 3: Provider Setup

Purpose:

- Let users connect low-cost or free-tier OpenAI-compatible providers for training and feedback.
- Keep provider configuration explicit and inspectable.

Launch requirements:

- Preset list is visible.
- Provider profile can be saved.
- Model name and API key environment variable are editable.
- Provider test result is visible in the UI.
- Provider pricing/free-tier claims are not hardcoded as guaranteed.

### Track 4: Production Assist Mode

Purpose:

- Prepare a controlled mode for real DB query assistance.
- Use local or internal LLM only when production DB metadata or query intent is involved.

Launch requirements before public production positioning:

- Separate mode flag or profile: `training` vs `production_assist`.
- Production assist rejects external provider use by default.
- Read-only DB connection contract is explicit.
- Generated SQL is preview-only until approved.
- SQL validation and safety review are visible.
- Audit log records prompt, schema context, generated SQL, approval, and execution result.
- Sensitive values are redacted from logs and prompts.

## Recommended `/goal` Units

### Launch Goal 1: Query Practice Flow UI

Complete the current remaining Goal D.

Done when:

- Practice problem appears as a terminal block.
- User can open a problem, inspect schema, type SQL, and submit.
- Result block shows rows and grading.
- Wrong answer creates a local attempt record.
- Mobile layout has no horizontal scroll.
- Smoke test covers the practice submit flow.

### Launch Goal 2: iOS Launch Feasibility And Packaging Decision

Decide whether and how CoQuery should proceed as an iOS app.

Done when:

- iOS release feasibility is documented.
- Packaging approach is selected.
- TestFlight vs public App Store target is clarified.
- Python local server dependency is accepted, rejected, or replaced for iOS.
- First iOS app scope and exclusions are documented.
- Next implementation `/goal` is identified.

Implemented as `IOS_LAUNCH_FEASIBILITY_2026-07-07.md`.

Current decision:

- Proceed with a TestFlight-first iOS Training App.
- Use a Capacitor iOS shell as the first packaging path.
- Do not embed the current Python local server in the iOS app.
- Keep production DB assistance out of the first iOS release.

### Launch Goal 3: iOS Training Runtime Contract

Extract the current training command behavior into a portable contract for iOS.

Done when:

- Portable command contracts are documented for `practice_list`, `practice_schema`, `practice_query`, `practice_grade`, `practice_attempts`, `help_catalog`, `command_explain`, and `term_explain`.
- Local storage contracts are defined for practice packs and attempt logs.
- iOS-safe query execution strategy is selected.
- The app shell knows which commands can run without the Python server.
- The next `/goal` can scaffold the Capacitor iOS shell without re-deciding architecture.

Implemented as `IOS_TRAINING_RUNTIME_CONTRACT_2026-07-08.md`.

Current decision:

- Use the current Python handlers as the reference behavior.
- Implement the first iOS runtime as a TypeScript Training Runtime adapter.
- Bundle `practice_packs/sql_basics.json`.
- Prefer a SQLite-compatible JS/WASM executor first; fall back to native SQLite only if needed.
- Keep attempts local and expose `local://coquery/practice_attempts` as the logical path.

### Launch Goal 4: iOS TestFlight Shell Skeleton

Create the first iOS package path.

Done when:

- Capacitor project files exist.
- `ios/` project exists.
- The app can load the terminal shell on iPhone and iPad simulator.
- The shell can run at least one local Training Runtime command without the Python server.
- TestFlight metadata checklist exists.

Implemented with:

- `package.json`
- `capacitor.config.json`
- `app_shell/ios_training_shell/src/trainingRuntime.ts`
- `ios/`
- `docs/testflight-metadata-checklist.md`

Current proof:

- `practice_packs/sql_basics.json` is bundled into the Capacitor web assets.
- `postCommand("practice_list")` routes to the local iOS Training Runtime adapter without calling the Python HTTP API.
- The iOS Training Runtime also exposes local `practice_attempts` and static `practice_feedback` contracts.
- iPhone 17 simulator launch renders the terminal shell and `practice_list`.
- iPad Pro 13-inch simulator launch renders the terminal shell and `practice_list`.

### Launch Goal 5: Wrong Note And Feedback

Turn attempt records into a usable learning loop.

Done when:

- Wrong attempts are listed in the app shell.
- Each wrong note shows submitted SQL, expected issue, and retry action.
- Static feedback works without any provider.
- Optional provider feedback can be requested only in Training Mode.
- Feedback is labeled as AI-generated when provider-backed.

Implemented with:

- wrong-note metadata on `practice_grade` attempt records
- `practice_feedback` CLI and Command API handler
- terminal-shell wrong-note cards with submitted SQL, expected issue, retry action, static feedback, and Training Mode provider request action
- iOS Training Runtime static `practice_feedback` and `practice_attempts` support

### Launch Goal 6: Provider Test And Model Readiness UI

Make provider setup launch-ready.

Done when:

- Saved providers can be listed, tested, selected, and removed in the app shell.
- Test failures are readable for non-specialists.
- Provider status is visible near the command input.
- CLI equivalent is shown for each provider action.

Implemented with:

- saved provider rows in the app shell with Select, Test, and Remove actions
- provider readiness status beside the command input
- readable `provider_test` failure guidance with a next step
- CLI-equivalent blocks for save, list, select, test, and remove provider actions

### Launch Goal 7: Mode Separation

Separate Training Mode from Production Assist Mode.

Done when:

- UI has a clear mode indicator.
- Command API accepts mode context.
- Training Mode can use sample datasets and commercial/low-cost providers.
- Production Assist Mode blocks external provider use unless explicitly overridden by policy.
- Docs explain the security boundary.

Implemented with:

- terminal-shell `Training` / `Assist` mode indicator in the command bar
- Command API `mode_context` metadata on mode-aware commands
- `production_external_provider_blocked` guard for saved external providers in Production Assist Mode
- `allow_external_provider=true` policy override support
- security boundary documentation in `docs/mode-security-boundary.md`

### Launch Goal 8: Desktop/Local Packaging Decision

Decide how the non-iOS local app is shipped.

Recommended launch path:

1. Local web app first: Python local server + browser.
2. Desktop wrapper second: Tauri or Electron only after the web shell stabilizes.
3. Mobile wrapper follows the iOS decision in `IOS_LAUNCH_FEASIBILITY_2026-07-07.md`.

Done when:

- Launch target is selected and documented.
- Start command is stable.
- Runtime storage paths are documented.
- Update and rollback path is documented.

Implemented with:

- Selected launch target: local web app first
- stable start wrapper: `python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765`
- npm convenience script: `npm run local:shell`
- runtime storage path documentation for provider profiles and practice attempts
- update and rollback documentation in `docs/desktop-local-packaging-decision.md`
- smoke coverage in `tests/local_packaging_decision_smoke.py`

### Launch Goal 9: Production Assist Safety Gate

Prepare production DB support without overclaiming.

Done when:

- Read-only connection profile exists.
- Generated SQL review block exists.
- Approval state is required before execution.
- `SELECT`-only guard is enforced for production assist.
- Audit log is written.

Implemented with:

- Read-only profile registry commands: `production_profile_add` and `production_profile_list`.
- Generated SQL review records: `production_review`.
- Approval-required execution path: `production_approve` then `production_execute`.
- `SELECT`-only rejection for review and execution.
- JSONL audit log for profile, review, approval, blocked execution, and completed execution events.
- Terminal shell review/approve/execute blocks and smoke coverage.
- Boundary documentation in `docs/production-assist-safety-gate.md`.

### Launch Goal 10: Release Candidate Hardening

Make the service release candidate testable.

Done when:

- One command runs all launch checks.
- Tests cover CLI, Command API, app shell smoke, practice flow, provider setup, and bilingual help.
- README has a launch quickstart.
- Release notes list exact supported and unsupported claims.

Implemented with:

- One-command RC verifier: `npm run rc:verify`.
- Shell verifier: `scripts/verify-rc.sh`.
- RC contract smoke: `python3 tests/rc_hardening_smoke.py`.
- Launch quickstart in `readme.md`.
- Exact supported/unsupported release claims in `RELEASE.md`.

## Launch Readiness Gates

The project is launch-ready only when all gates below are true:

- `python sql_cli/tests/test_core.py` passes.
- `python app_shell/terminal_shell_prototype/smoke.py` passes.
- No horizontal scroll at phone width in the app shell.
- Korean and English UI labels are verified.
- Practice flow works without DB connection.
- Provider setup works without storing secret key values.
- Docs clearly state what is experimental.
- Release package or local start path is documented.
- Current changes are committed and pushed.

## Current State

Completed:

- SQLite-first CLI baseline.
- PostgreSQL narrow experimental smoke path.
- Provider presets and OpenAI-compatible endpoint override.
- Command API Adapter.
- Responsive dark-mode terminal shell prototype.
- Provider Preset Mobile Flow.
- Practice Dataset Sandbox backend and CLI.
- Query Practice Flow UI.
- iOS Launch Feasibility And Packaging Decision.
- iOS Training Runtime Contract.
- iOS TestFlight Shell Skeleton.
- Bilingual beginner help.
- Korean font/readability improvement.
- Wrong Note And Feedback.
- Provider Test And Model Readiness UI.
- Mode Separation.
- Desktop/Local Packaging Decision.
- Production Assist Safety Gate.
- Release Candidate Hardening.

Still required before declaring `v0.8.0` released:

- Create and push the `v0.8.0` tag if publication is requested.
- Publish release notes that keep Training Mode, local shell, iOS skeleton, and Production Assist limits explicit.

## Immediate Next Action

After Launch Goal 10, PR #4 merge, `npm run rc:verify`, and green `baseline` / `postgresql-smoke` Actions, the next release step should be:

```text
Prepare the v0.8.0 release tag and release notes, or choose the next PostgreSQL verification slice before feature work resumes.
```
