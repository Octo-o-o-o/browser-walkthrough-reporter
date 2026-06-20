---
name: browser-walkthrough-reporter
description: Plan/run browser walkthroughs for web/API apps; generate screenshots, reports, bug reports, manual retest lists, Kanban updates, and English GitHub issues.
---

# Browser Walkthrough Reporter

## Workflow

1. Inspect the project first: read product docs, API docs, UI routes, existing tests, deployment notes, and any `kanban.html` or test board. Identify all user-visible and operator-visible capabilities. Also identify the **delivery units and their host type** — pure web / SPA / SSR, Electron (or Tauri) renderer, mobile WebView, admin console, or desktop-native-only logic — because the host decides whether a browser can reach a working UI at all, and a single product often ships several hosts with different walkthrough entries.
2. Create or update one walkthrough plan in the target repo. If there is no existing structure, run `scripts/scaffold_browser_walkthrough.py` from this skill, then adapt the generated files to the project.
3. Pick a reachable host, then check browser dependencies before running. The walkthrough URL must point at an entry that actually renders working UI. A non-web host (Electron/Tauri renderer, mobile WebView) is **not** walkthrough-able by aiming a headless browser at a bare production URL — its renderer needs the native bridge / IPC (`window.electronAPI` and similar), so the right entry is the project's own dev/preview server that injects the bridge, a renderer-only mock, or a logged-in session. Record the chosen entry (URL, host type, what is injected) in the plan. Prefer the project's Playwright dependency; if absent, either install it in the project or set `WALKTHROUGH_PLAYWRIGHT_REQUIRE_FROM` to a package.json that can require `playwright`. The bundled `.mjs` runner is only one execution path: when the agent has MCP browser tools (Playwright MCP, an Electron preview tool, an in-browser extension) that fit the host better, those may drive the run instead — but the same contract still holds (a `START` row and a terminal row per step, a screenshot per step, the three Markdown documents, and the test-board update).
4. Split coverage into runnable scopes, normally `config`, `usage`, `full`, and `diagnostic`. A scope must be independently runnable when practical.
5. Execute with browser tooling where credentials and environment are available. Every step must write a `START` row before action and a final `PASS`, `FAIL`, `TIMEOUT`, `SKIP`, or `BLOCKED` row after action.
6. Screenshot every step. File names must be `<ModuleName>_<YYYYMMDD-HHmmss>_<STATUS>.png`; store them in the run's `screenshots/` directory.
7. Generate three Markdown files for every run:
   - `report.md`: complete factual trace.
   - `bugs-for-engineers.md`: only clear bugs or bug candidates with engineer-ready reproduction detail.
   - `manual-retest-needed.md`: uncertain, blocked, fixture-dependent, or human-judgment items for the requester.
8. Update `kanban.html` or the nearest test board after every run. Link all three documents, include at least one screenshot, and list "人工确认事项" directly in the card instead of only linking the manual retest document.
9. If the user asks to file GitHub issues, do this only after all requested test scopes are complete and the three run documents are final. Triage in English: verify each item is a real issue, decide which bugs should be merged or split, exclude manual retest/fixture gaps, then create professional issue drafts or call `gh issue create` only after explicit confirmation/request. Use `references/github-issue-standard.md`.
10. Validate before final response: script syntax, Markdown existence, screenshot count, no secret leakage, test-board image/link rendering **and on-disk existence of every linked target**, phase/filter behavior if present, GitHub issue triage/drafts when requested, and no leftover walkthrough process.

## Classification Rules

Use strict separation:

- `Product bug`: preconditions are satisfied and the product violates expected behavior.
- `Bug candidate`: strong repeated evidence exists, but backend logs or external infrastructure are needed to confirm root cause.
- `Fixture blocked`: a safe completed run, review task, low-permission user, receiver, or similar precondition is missing.
- `Automation limitation`: browser tooling cannot observe or safely mutate the path, but a human can.
- `Manual retest`: real quality, third-party behavior, release gates, operator-only logs, or other human/CI confirmation remains.

Do not inflate the bug count by converting missing fixtures into product bugs. If a first-release project has few confirmed bugs, explain what was actually covered and which risks remain unconfirmed.

## Lessons From Prior Runs

- If a user challenges a low bug count, do not defend the count abstractly. Re-run or re-check, then explain the difference between confirmed bugs, blocked coverage, and manual risk.
- Keep historical context short. Summarize prior runner crashes as automation history, not product evidence. Mark superseded failures clearly.
- Do not let long stack traces dominate `bugs-for-engineers.md` or `manual-retest-needed.md`; keep full details in `report.md`.
- If a route reaches a terminal `failed` state under dummy or low-budget settings, that can pass lifecycle coverage while still blocking artifact/report quality coverage.
- If Kanban/test-board records link a manual checklist but do not show the checklist titles inline, update the record; the requester should not have to open another file to know what needs attention.
- Treat cleanup summaries as evidence, not guarantees. Report unremovable test workspaces, invitations, or fixtures explicitly.
- Never drive navigation by guessed localized labels. Discover nav targets from the app's stable selectors (`data-testid`, `role`, `id`, `aria-label`); a label you assume is `通用`/`General` may actually render as `常规`, `远程桌面` as `电脑工作台`, `Bridge` as `本地 Agent 桥接`. Guessed labels create false `BLOCKED`/`SKIP` rows that read like coverage gaps but are runner defects. If you must match by text, read the real rendered label first and key off a stable attribute for the click.
- A `BLOCKED` caused by a selector miss is a runner defect, not a `Fixture blocked`. When a whole batch of same-shaped steps blocks (e.g. every settings group), suspect the selector strategy before reporting a coverage gap — re-derive the targets from the source and re-run.
- If the test board has no insertion marker, the runner must self-heal (inject a walkthrough section before a known anchor or `</body>`) rather than silently skipping the board update. A silent skip reads as "board updated" when it was not. The scaffold runner now self-heals; keep that behavior in adapted runners.
- A browser cannot walk through a host it cannot load. If a non-web target (Electron/Tauri renderer, mobile WebView) is opened at a bare URL without its native bridge, IPC-backed calls fail and the run fills with `FAIL`/blank-screen rows. That is a host/environment mismatch — a runner setup defect — not product evidence. Resolve it by choosing the project's real dev/preview entry (bridge or renderer-only mock injected, or a logged-in session) before reporting any bug. An empty run directory with no `report.md` is the classic symptom of pointing a bare runner at a host it could not boot.
- Be honest about what the chosen entry can prove. A renderer-only / mock / logged-out entry exercises UI structure, navigation, rendering health, and client-side interaction, but not real business-result correctness — mark those as `Manual retest` or `Fixture blocked`, and never report a mock-backed happy path as confirmed product behavior. Missing credentials that turn a whole `config`/`usage` scope into `BLOCKED` is fixture-blocked coverage, not a coverage defect to hide and not a bug to inflate.
- Validate the execution layer before trusting it. MCP browser tools are convenient eyes for interactive discovery (snapshot, click, console), but they are not guaranteed everywhere: a Playwright MCP can fail to launch (`kill EPERM`), and a preview MCP may be unable to save named screenshots into the run directory. Confirm the chosen tool can both reach the host AND write archivable, correctly-named evidence; if not, fall back to a project-local Playwright runner. The runner owns reproducibility and archivable screenshots — the live MCP is the eyes, not necessarily the recorder.
- An action that did not throw is not a `PASS`. A step that only resized the viewport, clicked, or navigated will "succeed" on a blank or crashed page. Every terminal `PASS` needs a positive assertion (expected content present, no error boundary, no new console/page error). Otherwise a connection-refused blank page sails through the responsive checks.
- Do not assume `127.0.0.1`. Dev servers (Vite and friends) often bind `localhost` only, which can resolve to IPv6 `::1`; a runner pointed at `127.0.0.1` then gets `ERR_CONNECTION_REFUSED` and a blank screenshot on every step. Drive on the host the server actually prints, or detect it (`curl` both). A P0 load failure is a host/port-reachability defect to fix first, never product evidence.
- Judge render health from the whole document, not one container. Assuming every screen renders into `<main>` (or any single node) yields a batch of false "empty" `FAIL`s the moment an app uses different workspace containers for list/detail screens. Use full-document text minus the fixed chrome (nav + banner), plus error-boundary detection, plus a non-blank screenshot. If many same-shaped steps "fail empty" while their screenshots show real UI, fix the health check, not the product.
- Verify board links resolve to files on disk, not just that the board renders. A record can claim `PASS 31` and link a report + screenshot whose run directory is actually empty — dead links that read as evidence. After updating the board, `stat` every linked document and image; a record pointing at missing artifacts is worse than no record.
- A green run can still be testing the wrong thing. A multi-host product may silently fall back to a different surface unless the run opens the right entry AND completes the host handshake before load. Example: a mobile WebView bundle served the desktop shell from `/` and only rendered the real mobile app at `/index.mobile.html` after injecting the native-shell handshake (`window.octodesk.surface` + a completed onboarding state) — reuse the project's own e2e injection (e.g. an `e2e/.../_helpers.ts` `addInitScript`), never reverse-engineer it. A naive runner pointed at `/` returned 10/10 PASS while screenshotting the desktop fallback. Make every PASS assert it is on the intended surface (a stable marker such as `[data-...-mobile-app]`), not merely that *something* rendered.

## Required Report Semantics

Use the detailed standard in `references/reporting-standard.md` when designing or auditing a run.
Use `references/github-issue-standard.md` when preparing or filing GitHub issues.

Minimum run directory:

```text
doc/browser-walkthrough-reports/<YYYYMMDD-HHmmss>-browser-walkthrough-<env>/
├── report.md
├── bugs-for-engineers.md
├── manual-retest-needed.md
├── screenshots/
└── downloads/
```

The full report is the source of truth. The bug report is for engineers and AI agents who need to fix concrete issues. The manual retest list is for the requester and must be human-friendly.

## Using The Scaffold Script

From the target project root:

```sh
python3 /path/to/browser-walkthrough-reporter/scripts/scaffold_browser_walkthrough.py --project-root .
```

The script creates:

- `doc/browser-walkthrough-plan.md`
- `scripts/browser-walkthrough.mjs`
- `doc/browser-walkthrough-reports/`

Treat the generated browser script as a project-specific starting point. Adapt selectors, routes, API helpers, fixture setup, cleanup, and Kanban insertion to the actual application before running against a live environment.

Useful validation commands after adaptation:

```sh
node --check scripts/browser-walkthrough.mjs
git diff --check -- scripts/browser-walkthrough.mjs doc/browser-walkthrough-plan.md kanban.html
rg -n "PASSWORD|Bearer |csrf|cookie|whsec_|prp_live_[A-Za-z0-9_-]{20,}" doc/browser-walkthrough-reports scripts/browser-walkthrough.mjs kanban.html || true
pgrep -fl "node scripts/browser-walkthrough.mjs" || true
```

If the target project has no `kanban.html`, create or update the nearest equivalent test board, or record in `report.md` why no board update was possible.

## GitHub Issue Support

Default to issue drafts, not live issue creation. Run this only after all testing is complete and `report.md`, `bugs-for-engineers.md`, and `manual-retest-needed.md` have been reviewed:

```sh
python3 /path/to/browser-walkthrough-reporter/scripts/prepare_github_issues.py \
  --bug-report doc/browser-walkthrough-reports/<run>/bugs-for-engineers.md \
  --output-dir doc/browser-walkthrough-reports/<run>/github-issues
```

Review `github-issues/triage-review.md`, `manifest.json`, and each draft. Drafts marked `DRAFT_REVIEW_REQUIRED` are intentionally blocked from live filing until rewritten with complete English issue details.

To create issues after explicit user request:

```sh
python3 /path/to/browser-walkthrough-reporter/scripts/prepare_github_issues.py \
  --bug-report doc/browser-walkthrough-reports/<run>/bugs-for-engineers.md \
  --repo OWNER/REPO \
  --create \
  --yes \
  --label bug \
  --label walkthrough
```

Before filing, verify the draft answers: "is this truly an issue?", "should this be merged with another bug?", "does it include complete environment, reproduction, expected/actual behavior, evidence, impact, and likely areas to inspect?", and "is every title/body fully English and free of secrets?".

## Safety

- Never write passwords, cookies, CSRF tokens, full API keys, provider secrets, webhook signing secrets, or private report bodies into reports, screenshots, logs, or test boards.
- Prefer disposable workspaces/accounts and prefixed test data.
- Do not mutate customer or non-test data.
- Do not downgrade or remove the only owner/admin to simulate low permissions.
- Clean up temporary API keys, provider secrets, webhook endpoints, invitations where possible, and record anything that cannot be cleaned.
