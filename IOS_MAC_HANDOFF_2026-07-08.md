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

## Next `/goal`

```text
Launch Goal 4: iOS TestFlight Shell Skeleton
```

Done when:

- Capacitor project files exist.
- `ios/` project exists.
- The shell can load the current terminal UI.
- `postCommand` can call a local Training Runtime adapter for at least `practice_list`.
- iPhone and iPad simulator verification instructions are documented for Mac.

## First Mac Work Sequence

1. Confirm Node, npm, Xcode, and CocoaPods or Swift Package setup as required by the chosen Capacitor version.
2. Add minimal web packaging files if missing.
3. Create the Capacitor shell.
4. Add iOS platform.
5. Wire the current terminal shell assets into the Capacitor app.
6. Add a minimal local Training Runtime adapter for `practice_list`.
7. Launch on iPhone simulator.
8. Launch on iPad simulator.
9. Commit and push the iOS shell skeleton.

## Guardrails

- Keep `sql_cli.command_api.run_command` as the Python reference behavior.
- Keep the existing local browser prototype working.
- Do not remove the Python CLI or server.
- Do not introduce production DB access in the iOS shell skeleton.
- Keep all iOS changes tied to Training Mode until the Production Assist safety gate exists.
