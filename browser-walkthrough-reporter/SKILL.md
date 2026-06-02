---
name: browser-walkthrough-reporter
description: Plan/run browser walkthroughs for web/API apps; generate screenshots, reports, bug reports, manual retest lists, Kanban updates, and English GitHub issues.
---

# Browser Walkthrough Reporter

## Workflow

1. Inspect the project first: read product docs, API docs, UI routes, existing tests, deployment notes, and any `kanban.html` or test board. Identify all user-visible and operator-visible capabilities.
2. Create or update one walkthrough plan in the target repo. If there is no existing structure, run `scripts/scaffold_browser_walkthrough.py` from this skill, then adapt the generated files to the project.
3. Check browser dependencies before running. Prefer the project's Playwright dependency; if absent, either install it in the project or set `WALKTHROUGH_PLAYWRIGHT_REQUIRE_FROM` to a package.json that can require `playwright`.
4. Split coverage into runnable scopes, normally `config`, `usage`, `full`, and `diagnostic`. A scope must be independently runnable when practical.
5. Execute with browser tooling where credentials and environment are available. Every step must write a `START` row before action and a final `PASS`, `FAIL`, `TIMEOUT`, `SKIP`, or `BLOCKED` row after action.
6. Screenshot every step. File names must be `<ModuleName>_<YYYYMMDD-HHmmss>_<STATUS>.png`; store them in the run's `screenshots/` directory.
7. Generate three Markdown files for every run:
   - `report.md`: complete factual trace.
   - `bugs-for-engineers.md`: only clear bugs or bug candidates with engineer-ready reproduction detail.
   - `manual-retest-needed.md`: uncertain, blocked, fixture-dependent, or human-judgment items for the requester.
8. Update `kanban.html` or the nearest test board after every run. Link all three documents, include at least one screenshot, and list "人工确认事项" directly in the card instead of only linking the manual retest document.
9. If the user asks to file GitHub issues, do this only after all requested test scopes are complete and the three run documents are final. Triage in English: verify each item is a real issue, decide which bugs should be merged or split, exclude manual retest/fixture gaps, then create professional issue drafts or call `gh issue create` only after explicit confirmation/request. Use `references/github-issue-standard.md`.
10. Validate before final response: script syntax, Markdown existence, screenshot count, no secret leakage, test-board image/link rendering, phase/filter behavior if present, GitHub issue triage/drafts when requested, and no leftover walkthrough process.

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
