# CoQuery iOS Mac Handoff

Date: 2026-07-08

## Current Remote Checkpoint

Repository:

```text
https://github.com/redsunjin/CoQuery.git
```

Branch:

```text
main
```

Expected checkpoint after Windows sync:

```text
Launch Goal 3: iOS Training Runtime Contract
```

## Mac Start Commands

```bash
git clone https://github.com/redsunjin/CoQuery.git
cd CoQuery
git log -1 --oneline
```

The latest commit should include:

```text
iOS Training Runtime Contract
```

## Read First

1. `IOS_LAUNCH_FEASIBILITY_2026-07-07.md`
2. `IOS_TRAINING_RUNTIME_CONTRACT_2026-07-08.md`
3. `SERVICE_LAUNCH_PLAN_2026-07-07.md`
4. `app_shell/terminal_shell_prototype/README.md`

## Current Decision

- First iOS target: TestFlight-first Training App.
- Packaging path: Capacitor iOS shell.
- Runtime path: TypeScript Training Runtime adapter.
- Bundled dataset: `practice_packs/sql_basics.json`.
- Do not embed or start the Python local server inside the iOS app.
- Do not add production DB support to the first iOS app.

## Next Step

```text
Commit and push if publication is requested, after `npm run rc:verify` passes.
```

Goal 4 completed on 2026-07-08.
Goal 5 completed on 2026-07-08.
Goal 6 completed on 2026-07-08.
Goal 7 completed on 2026-07-08.
Goal 8 completed on 2026-07-08.
Goal 9 completed on 2026-07-08.
Goal 10 completed on 2026-07-08.

Completed proof:

- Capacitor project files exist.
- `ios/` project exists.
- The shell can load the current terminal UI.
- `postCommand` can call a local Training Runtime adapter for at least `practice_list`.
- iPhone and iPad simulator launches render the `practice_list` shell.
- TestFlight metadata checklist exists at `docs/testflight-metadata-checklist.md`.
- Wrong attempts render as wrong-note cards with submitted SQL, expected issue, retry action, and static feedback.
- `practice_feedback` works without a provider and gates provider-backed feedback to Training Mode.
- Provider-backed feedback is labeled as AI-generated in the command contract.
- Saved providers can be selected, tested, and removed from the app shell.
- Provider test failures show readable next-step guidance.
- Provider readiness is visible near the command input.
- The app shell now shows a Training/Assist mode indicator.
- Command API responses include mode context for mode-aware commands.
- Production Assist blocks saved external providers unless `allow_external_provider=true` is explicitly supplied.
- The mode security boundary is documented at `docs/mode-security-boundary.md`.
- Non-iOS local packaging is selected as local web app first.
- Stable local start command is `python3 scripts/start_local_shell.py --host 127.0.0.1 --port 8765`.
- Runtime storage, update path, and rollback path are documented at `docs/desktop-local-packaging-decision.md`.
- Production Assist Safety Gate supports read-only profiles, SQL review, explicit approval, SELECT-only execution, and JSONL audit logging.
- The production assist boundary is documented at `docs/production-assist-safety-gate.md`.
- Release Candidate Hardening provides `npm run rc:verify` as the local launch check.

## Completed Mac Work Sequence

1. Confirm Node, npm, Xcode, and CocoaPods or Swift Package setup as required by the chosen Capacitor version.
2. Add minimal web packaging files if missing.
3. Create the Capacitor shell.
4. Add iOS platform.
5. Wire the current terminal shell assets into the Capacitor app.
6. Add a minimal local Training Runtime adapter for `practice_list`.
7. Launch on iPhone simulator.
8. Launch on iPad simulator.
9. Commit and push the iOS shell skeleton if the user asks for publication.

## Guardrails

- Keep `sql_cli.command_api.run_command` as the Python reference behavior.
- Keep the existing local browser prototype working.
- Do not remove the Python CLI or server.
- Do not introduce production DB access in the iOS shell skeleton.
- Keep the iOS shell tied to Training Mode unless a separate iOS production-assist validation goal is opened.
- Treat Goal 7 as a mode boundary only; Goal 9 adds a reviewed read-only SELECT gate, not broad production DB automation.
- Treat Goal 8 as a local packaging decision only; it does not add production DB safety approval.
