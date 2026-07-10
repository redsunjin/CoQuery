# CoQuery Training Screenshot Plan

Date: 2026-07-09
Scope: iPhone/iPad App Store Connect screenshot package.

Reference checked on 2026-07-09:

- Apple screenshot specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications

## Official Size Targets Used

The generated package uses:

- iPhone 6.9 inch portrait: `1320 x 2868`
- iPad 13 inch portrait: `2048 x 2732`

Apple's current screenshot reference accepts one to ten `.jpeg`, `.jpg`, or `.png` screenshots per device family. If high-resolution iPhone screenshots are supplied, App Store Connect can scale to smaller iPhone sizes where allowed. iPad screenshots are required when the app runs on iPad.

## Generated Candidate Screens

Run:

```bash
python3 scripts/prepare_ios_registration_assets.py
```

Generated output:

- `app_store_assets/ios-registration/icons/app-icon-1024.png`
- `app_store_assets/ios-registration/screenshots/iphone-69/01-training-home.png`
- `app_store_assets/ios-registration/screenshots/iphone-69/02-practice-flow.png`
- `app_store_assets/ios-registration/screenshots/iphone-69/03-safety-boundary.png`
- `app_store_assets/ios-registration/screenshots/ipad-13/01-training-home.png`
- `app_store_assets/ios-registration/screenshots/ipad-13/02-practice-flow.png`
- `app_store_assets/ios-registration/screenshots/ipad-13/03-safety-boundary.png`
- `app_store_assets/ios-registration/asset-manifest.json`

## Recommended Upload Order

1. Training home: first-TestFlight scope and local practice shell.
2. Practice flow: bundled sample data and read-only SQL practice.
3. Safety boundary: no production DB access in the iOS Training shell.

## Final Capture Gate

These generated screenshots are registration candidates. Before public App Store release, capture device or simulator screenshots from the signed build and compare them against these claims.

For TestFlight-only registration, these candidates are acceptable repo-side package materials only after App Store Connect preview is manually checked.
