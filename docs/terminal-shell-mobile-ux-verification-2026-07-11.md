# Terminal Shell Mobile UX Verification — 2026-07-11

## Purpose

Record the mobile usability correction and its evidence in this repository so it can be reviewed without Figma or an external design account.

## Scope

- Surface: `app_shell/terminal_shell_prototype`
- Target: phone-width command-entry and command-result flow
- Source change: `app_shell/terminal_shell_prototype/styles.css`
- Evidence directory: `.audit/ui-ux-2026-07-11/`

## Resolved issues

| Issue | Resolution | Evidence |
| --- | --- | --- |
| Tapping a command input could trigger iOS browser auto-zoom. | Mobile text inputs, selects, and textareas use `16px` text. The narrow-phone rule no longer reduces the command input to `13px`. | Source review and 390 × 844 device-view check |
| The command bar occupied the bottom of the phone viewport as a sticky element. | The mobile command bar is now in normal document flow (`position: static`), and the terminal content uses page scrolling. | `04-phone-final-start.png`, `05-phone-command-entry.png` |
| A command result needed to remain usable after this layout change. | Executing `practice_list` through the visible **실행** button rendered the training result in the terminal stream. | `06-phone-practice-run.png` |

## Interaction boundary

- The default menu and command-entry area are not fixed on phone widths.
- The detail panel remains a fixed drawer only after the user explicitly opens **패널**. This is intentional: it is an on-demand inspection view rather than always-visible navigation.
- Desktop and tablet behavior are unchanged; these CSS rules are inside the mobile media query (`max-width: 760px`).

## Evidence

| Artifact | What it proves |
| --- | --- |
| [`04-phone-final-start.png`](../.audit/ui-ux-2026-07-11/04-phone-final-start.png) | Initial phone layout; the page is not constrained to a fixed viewport command bar. |
| [`05-phone-command-entry.png`](../.audit/ui-ux-2026-07-11/05-phone-command-entry.png) | Command input, mode selection, and execution controls are reachable by normal scrolling. |
| [`06-phone-practice-run.png`](../.audit/ui-ux-2026-07-11/06-phone-practice-run.png) | `practice_list` executed successfully and rendered a practice result. |

Keep the `.audit/ui-ux-2026-07-11/` directory with this document if the verification record is committed or copied elsewhere.

## Automated checks run

```text
git diff --check
python3 app_shell/terminal_shell_prototype/smoke.py
```

Both passed on 2026-07-11. The smoke output includes expected negative-path HTTP 400 cases and ends with `terminal shell prototype smoke passed`.

## Remaining device proof

This is browser/device-viewport evidence, not final native iPhone proof. Before TestFlight distribution, verify on a physical iPhone or the iOS WKWebView shell that focusing the command input does not zoom and that the command result remains reachable after execution.
