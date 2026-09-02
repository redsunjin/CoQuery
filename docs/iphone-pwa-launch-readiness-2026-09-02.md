# CoQuery iPhone + PWA Launch Readiness

Date: 2026-09-02
Status: TestFlight and public-PWA infrastructure are prepared, but neither channel is ready to be called launched.

## Product Boundary

The initial public scope is a learning-first SQL practice product:

- bundled sample datasets and 24 SQL practice problems
- Korean and English learning flow
- browser-local or device-local attempt history
- no production database connection, external database credentials, account, analytics, payment, or provider API key in the first iPhone release

Production Assist, user database connections, provider configuration, and multi-device progress synchronization are excluded from this launch. Do not present the first release as an operational database client or autonomous SQL agent.

## Readiness Snapshot

| Track | Evidence already present | Release blocker |
| --- | --- | --- |
| iPhone / TestFlight | Capacitor iOS project, iPhone/iPad simulator proof, local practice-list/help/feedback adapter, App Store copy/screenshots/icon, support and privacy pages, and a signing-free Xcode 26.6 / iOS 26.5 Release build | The bundled iOS runtime does not yet implement local `practice_query` or `practice_grade`, so the advertised solve-and-grade loop cannot complete offline. Apple team/signing, archive upload, and real-device proof are also outstanding. |
| Public PWA | Cloudflare Worker + Static Assets implementation, temporary public deployment proof, production deployment workflow, manifest and service worker | Target Cloudflare account credentials, durable deployment, custom-domain decision, TLS/device/install/offline QA, and recorded production evidence are outstanding. |

## Changes Applied in This Pass

- The iOS build now copies every script and stylesheet that the learning flow loads dynamically. It no longer starts the PWA service-worker runtime inside the native WebView.
- The iOS local Training Runtime now loads before the classic shell scripts, preserving their shared browser globals.
- The iOS package smoke test verifies those assets, the runtime registration, the full 24-problem pack, the privacy-policy link, and iOS version `0.8.0`.
- The Xcode marketing version is aligned with the existing App Store Connect metadata draft (`0.8.0`).
- The shared home screen now links to the published privacy policy, which also gives the PWA a visible privacy route.

## iPhone / TestFlight Checklist

### 1. Complete the local training runtime — blocking implementation gate

- [ ] Add a local SQLite-compatible executor (JS/WASM or native Capacitor bridge) to `app_shell/ios_training_shell/src/trainingRuntime.ts`.
- [ ] Implement `practice_query` and `practice_grade` using the bundled `sql_basics` pack; reject non-SELECT SQL and keep attempts local.
- [ ] Make `practice_attempts` persist across relaunches, rather than remaining only in the current in-memory adapter instance.
- [ ] Add parity tests for correct query, incorrect query, grade result, wrong-note creation, and relaunch persistence.
- [ ] On an iPhone and an iPad, complete Home → problem → SQL → run → grade → next problem with networking disabled.

The current TypeScript adapter is intentionally a shell: its supported-command list omits `practice_query` and `practice_grade`. Do not upload an external TestFlight build claiming the full practice loop until this gate passes.

### 2. Apple Developer and Xcode

- [ ] Confirm active Apple Developer Program membership and the correct Team in Xcode.
- [ ] In Certificates, Identifiers & Profiles, create or confirm the explicit App ID `app.coquery.training`; enable no capabilities that the first release does not use.
- [ ] Keep automatic signing, select the Team, and let Xcode create the development/distribution provisioning profiles. Do not commit a Team ID or signing certificate.
- [ ] Run `npm ci` followed by `npm run ios:sync` immediately before building or archiving. Capacitor deliberately generates `ios/App/App/public`, `capacitor.config.json`, and `config.xml` locally; they are ignored by Git but required by Xcode.
- [ ] Build the archive with Xcode 26 or later and the iOS/iPadOS 26 SDK or later. Apple has required that toolchain for App Store Connect uploads since 2026-04-28.
- [ ] Increment `CURRENT_PROJECT_VERSION` for every subsequent upload; retain the semantic version in `MARKETING_VERSION`.
- [ ] Archive, validate in Xcode Organizer, and upload the signed build. A no-sign simulator build is evidence only, not a distributable build.

### 3. App Store Connect registration

- [ ] Verify the Account Holder has accepted current agreements before creating the record.
- [ ] Create a new iOS app record: name `CoQuery`, primary language English (U.S.), bundle ID `app.coquery.training`, SKU `coquery-training-ios`, primary category Education, secondary category Developer Tools.
- [ ] Enter the repository drafts from `docs/app-store-registration/`; replace the pending feedback contact with a monitored address.
- [ ] Verify the final support and privacy URLs over HTTPS. The privacy-policy link must remain available both in App Store Connect and in the app.
- [ ] Complete App Privacy as “no data collected” only if the shipped build still has no analytics, crash reporting, remote feedback, account, provider, or telemetry code. Re-answer it when any of those changes.
- [ ] Complete age rating and export-compliance answers from the actual signed build. Do not reuse an answer blindly after adding a library or network feature.
- [ ] Upload real signed-build screenshots for the enabled iPhone and iPad device families; the repository images are candidates, not final device evidence.

### 4. TestFlight rollout

- [ ] Start with internal testers and collect launch, crash, layout, and full-flow evidence.
- [ ] Before inviting external testers, supply Beta App Description, What to Test, review notes, and a monitored feedback email.
- [ ] Submit the first external build for TestFlight App Review, then create the external tester group/public link only after approval.
- [ ] Record tested device model, iOS/iPadOS version, build number, known limits, and reviewer feedback in `HANDOFF.md`.

Apple references: [new app record](https://developer.apple.com/help/app-store-connect/create-an-app-record/add-a-new-app/), [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview), [SDK requirement](https://developer.apple.com/news/upcoming-requirements/?id=02032026a), [app privacy](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/), and [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).

## PWA / Cloudflare Checklist

### 1. Deploy a durable Worker

- [ ] Create a target Cloudflare account and identify its account ID.
- [ ] Create a least-privilege, account-owned CI token restricted to this account. The current workflow needs Worker script deployment permission; add route/domain permission only if the deployment workflow will manage the custom domain itself.
- [ ] Add `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` as GitHub Actions secrets in the protected `production` environment. Never commit either value.
- [ ] Manually run `.github/workflows/cloudflare-production-deploy.yml`; it stages the isolated Worker bundle, deploys it, then verifies health, shell, manifest, and known practice grading.
- [ ] Record the durable `workers.dev` URL, workflow run URL, commit SHA, and results. The 2026-08-28 temporary URL is not a production endpoint.

### 2. Attach the production domain and HTTPS

- [ ] Choose the canonical hostname before changing `wrangler.jsonc` (recommended shape: `app.<your-domain>`). Do not commit a guessed domain.
- [ ] Add the domain as an active Cloudflare zone. Because this Worker is the whole origin for the hostname, use a Workers **Custom Domain**, not a route in front of a separate origin.
- [ ] Add it in Workers & Pages → CoQuery Worker → Settings → Domains & Routes → Add Custom Domain, or later add a matching `routes` entry with `custom_domain: true` after the hostname is known.
- [ ] Confirm the hostname has no conflicting CNAME. Cloudflare will create the required DNS record and certificate for the Custom Domain.
- [ ] If both root and `www` must work, configure a single canonical redirect. Custom Domains match exact hostnames; register or redirect both intentionally.
- [ ] Enable Always Use HTTPS after certificate issuance and verify that `http://` redirects once to the canonical `https://` URL. Postpone HSTS until redirects and certificates have been stable in production.

### 3. Release QA and operational boundary

- [ ] Verify `/api/health`, shell, manifest, all 24 practice problems, one valid query, and one valid grade on the custom-domain URL.
- [ ] Test Chrome/Edge desktop installation, then Safari Add to Home Screen on iPhone/iPad. Verify name, icon, standalone launch, and progress after refresh/relaunch.
- [ ] Visit once online, go offline, reopen the shell, and confirm that cached UI opens while SQL execution reports a recoverable network-required state.
- [ ] Verify that `/api/*` responses are not served from the application-shell cache and that learner attempts remain in browser `localStorage` only.
- [ ] Before public promotion, add and validate raster manifest icons and an `apple-touch-icon` fallback using the approved icon asset. The current manifest is valid but offers only an SVG icon, so device install appearance has not yet been proven.
- [ ] Monitor deployment errors and Worker limits. Do not add provider configuration, Production Assist, or durable learner data to the public Worker without an explicit privacy/security review.

Cloudflare references: [production routes and domains](https://developers.cloudflare.com/workers/configuration/routing/), [Custom Domains](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/), [API tokens](https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/), and [Always Use HTTPS](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/always-use-https/).

## Release Order

1. Finish and real-device-verify the iOS local execute/grade runtime.
2. Configure Apple signing and release an internal TestFlight build.
3. Configure Cloudflare production secrets, deploy the durable Worker, and perform browser/device PWA QA.
4. Choose and attach the canonical PWA domain, then complete HTTPS and install validation.
5. Submit the first external TestFlight build only after the app loop, privacy answers, metadata, and real-device evidence are complete.

Until those steps are complete, describe CoQuery as “launch preparation complete with temporary PWA proof and an iOS shell,” not as a publicly launched iPhone app or PWA.
