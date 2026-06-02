# GitHub Issue Filing Standard

Use this standard only after the walkthrough run is complete and the user asks to prepare or file GitHub issues.

## Required Reflection Before Filing

For every candidate from `bugs-for-engineers.md`, answer these in English before creating an issue:

1. **Is this truly an issue?**
   - Preconditions were satisfied.
   - The behavior violates a product, API, security, UX, reliability, or operations expectation.
   - The evidence is from the product under test, not from a runner crash, missing fixture, missing account, missing receiver, or unsupported environment.
   - The issue is not superseded by a later rerun or already resolved by later evidence.

2. **Should it be merged or split?**
   - Merge when multiple symptoms share the same root path, same owner, same reproduction flow, and same likely fix.
   - Split when bugs affect different user workflows, different services, different permissions/security boundaries, different owners, or can be fixed independently.
   - Keep fixture/manual gaps out of GitHub issues unless the project explicitly tracks missing test fixtures as engineering work.

3. **Is the issue complete enough for an engineer or AI agent?**
   - A reader should understand the problem without opening the full report first.
   - The issue should still link the full report and screenshots.
   - Include exact environment, run id, timestamps, scope, endpoint/page, steps, expected behavior, actual behavior, impact, evidence, and likely inspection areas.

## Fileability Gate

Create a live GitHub issue only when all gates pass:

- The item comes from `bugs-for-engineers.md`, not `manual-retest-needed.md`.
- It is still valid after reviewing the latest run and any superseding reruns.
- It is not only a missing fixture, missing external receiver, low-permission-account gap, CI/release gate, or human-quality judgment item.
- Related symptoms have been deliberately merged or split, with the decision written in the issue body.
- The title and body are fully English and include enough context for an engineer or AI agent to reproduce without asking for basic details.
- The issue contains no passwords, cookies, CSRF tokens, full API keys, provider secrets, webhook signing secrets, private report bodies, or raw customer data.

## English Issue Template

Use this structure for every issue body:

```markdown
## Summary

One or two sentences describing the user-visible or operator-visible failure.

## Triage reflection

- Real issue assessment: why this is a product bug or bug candidate, not a fixture gap or automation artifact.
- Merge/split decision: why this issue stands alone or was merged with related symptoms.
- Confidence: high / medium / low, with the reason.

## Environment

- Environment:
- Walkthrough run ID:
- Scope:
- Web URL:
- API base URL:
- Test workspace/account/resource IDs:
- Time window:

## Steps to reproduce

1. ...
2. ...
3. ...

## Expected behavior

Describe the expected product behavior in concrete, testable terms.

## Actual behavior

Describe exactly what happened, including status, timeout, error code, missing row, bad UI state, or leaked data.

## Evidence

- Full walkthrough report:
- Step log rows:
- Screenshots:
- Request IDs / trace IDs:
- Related historical runs:

## Impact

Explain why this matters for users, operators, integrations, security, or release confidence.

## Likely areas to inspect

- Keep this short. These are hypotheses, not conclusions.

## Not included / not this issue

List nearby fixture-blocked or manual-retetest items that should not be conflated with this issue.
```

## Title Rules

- Start with the area or module in brackets, for example `[Webhooks] Delivery attempts are not observable after subscribed run events`.
- Keep titles specific and action-oriented.
- Avoid vague titles like `Webhook broken` or `Run issue`.

## Filing Rules

- Default to creating Markdown drafts under `github-issues/`.
- Use `gh issue create --repo OWNER/REPO --title ... --body-file ... --label ...` only when the user explicitly asks to create issues.
- When using `scripts/prepare_github_issues.py`, review `triage-review.md`, `manifest.json`, and every draft before live filing.
- Do not file drafts marked `DRAFT_REVIEW_REQUIRED`; rewrite them into complete English first or drop them.
- Do not include secrets, cookies, CSRF tokens, full API keys, private report bodies, or raw customer data.
- Use English for title and body even if source reports are multilingual.
- If no issues are truly fileable, create no GitHub issue; report why candidates were rejected.
