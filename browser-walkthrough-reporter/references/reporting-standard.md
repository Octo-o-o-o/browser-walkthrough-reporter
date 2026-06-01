# Browser Walkthrough Reporting Standard

## Plan Requirements

The walkthrough plan must include:

- Environment variables and credential handling.
- Scope definitions: `config`, `usage`, `full`, `diagnostic`.
- Feature coverage mapped to project modules, routes, APIs, and test-board tasks.
- Test data rules and cleanup rules.
- Status taxonomy: `PASS`, `FAIL`, `TIMEOUT`, `SKIP`, `BLOCKED`.
- Wait/timeout rules for page load, login, mutation consistency, async jobs, downloads, webhooks, and cleanup.
- Distinction between platform-flow success and business-result success.
- Required report files and Kanban/test-board update requirements.

## Step Log Format

Every step must append one `START` row and one terminal row:

```markdown
| 时间 | 状态 | 步骤 | 对象 | 结果摘要 | request_id/trace_id | 证据 |
|---|---|---|---|---|---|---|
| 2026-06-01T10:00:00+08:00 | START | P4.1 | runs | Start create run | - | pending |
| 2026-06-01T10:00:31+08:00 | PASS | P4.1 | run_... | created and visible in list | req_... | screenshots/P4-Runs-Create_20260601-100031_PASS.png |
```

Use local time with timezone. A wait window is also a step.

## Screenshot Rules

- Screenshot every step, including API-only checks.
- Use `<ModuleName>_<YYYYMMDD-HHmmss>_<STATUS>.png`.
- Store screenshots under the run's `screenshots/` directory.
- Review screenshots for secrets before treating a report as ready.

## Three Output Documents

### `report.md`

Must include:

- Run ID, tester, env, browser, web URL, API base URL, start/end times.
- Scope and coverage.
- Original resource IDs and test resource IDs.
- API key prefixes only, never full secrets.
- Step log.
- Result classification.
- Console/page/network error summary.
- Cleanup details.
- Links to `bugs-for-engineers.md` and `manual-retest-needed.md`.
- Kanban/test-board update status.

### `bugs-for-engineers.md`

Only include bugs or bug candidates with enough evidence for an engineer or AI agent to start work.

Each item needs:

- Stable ID, severity, current status.
- Complete description in concrete terms.
- Expected result and actual result.
- Minimal reproduction steps.
- Evidence screenshot and report link.
- Impact.
- Short likely areas to inspect.
- Historical context if repeated.

Do not include fixture gaps or manual-only checks as bugs.

When historical context is useful, summarize it. Avoid pasting long stack traces. Use short labels such as:

- `early automation/browser-context failure; not product evidence`
- `superseded by later rerun`
- `repeated webhook delivery timeout`
- `fixture blocked: no completed run with FinalReport`

### `manual-retest-needed.md`

Write for a human requester. Include:

- What automation already covered.
- What remains uncertain.
- Why automation cannot safely or fully confirm it.
- What the requester should prepare.
- How to retest.
- Which engineering bug must be fixed first, if any.

## Kanban/Test Board Update

After every run, update `kanban.html` or the nearest test board with:

- Run timestamp, scope, environment, result, and release-blocking status.
- Links to all three documents.
- At least one screenshot, preferring `FAIL`, `TIMEOUT`, or `BLOCKED`.
- A direct "人工确认事项" list sourced from `manual-retest-needed.md`.
- Cleanup summary.

Use relative links and no base64 images.

If the board already has filters or phases, verify them after updating. At minimum, open the board with a browser tool and check that:

- The latest record exists.
- Links to all three documents exist.
- Referenced screenshots load.
- The direct "人工确认事项" list is visible.
- Existing task filters still show the expected groups.

## Common Bug vs Manual Decisions

Classify as a bug:

- Endpoint exists and subscribed, event occurs, but no delivery row appears.
- Permission preconditions are valid and unauthorized mutation succeeds.
- Secret appears in DOM/list/audit/download/log.
- Expected API envelope is missing for a tested path.
- Mutation succeeds but refresh/audit/list proves wrong state.

Classify as manual/fixture blocked:

- No completed run with FinalReport exists.
- No safe review task exists for approve/reject/rerun/edit.
- No low-permission user exists.
- No controlled receiver exists for HMAC/retry/DLQ.
- Release gate requires CI/operator secrets.
- Real research quality needs human judgment.

## Retrospective Checklist Before Final Answer

Before reporting back to the user:

- Confirm whether any product bug is genuinely new, repeated, or superseded.
- If only one bug is confirmed, state why other suspicious areas are not yet bugs.
- List manual confirmation items in plain language.
- Mention cleanup leftovers separately from product bugs.
- Mention any tool/dependency limitation, such as missing local Playwright or missing PyYAML for skill validation.
- Include the latest run's three document links.
