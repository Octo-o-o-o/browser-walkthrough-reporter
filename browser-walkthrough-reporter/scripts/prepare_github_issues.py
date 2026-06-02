#!/usr/bin/env python3
"""Prepare or create English GitHub issues from a walkthrough bug report."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BUG_HEADING = re.compile(r"^###\s+(BUG-[A-Za-z0-9-]+)\s+-\s+(.+?)\s*$", re.MULTILINE)
KNOWN_TITLES = {
    "BUG-P7-WEBHOOK-DELIVERY-NOT-OBSERVED": "[Webhooks] Delivery attempts are not observable after subscribed run events",
}


@dataclass
class BugSection:
    bug_id: str
    source_title: str
    source_body: str
    review_required: bool = False


def parse_bug_report(path: Path) -> list[BugSection]:
    text = path.read_text(encoding="utf-8")
    matches = list(BUG_HEADING.finditer(text))
    bugs: list[BugSection] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        if "No clear product bug was confirmed" in section:
            continue
        bug = BugSection(match.group(1).strip(), match.group(2).strip(), section)
        bug.review_required = needs_manual_english_rewrite(bug)
        bugs.append(bug)
    return bugs


def make_english_title(bug: BugSection) -> str:
    if bug.bug_id in KNOWN_TITLES:
        return KNOWN_TITLES[bug.bug_id]
    words = re.sub(r"^BUG-(P\d+-)?", "", bug.bug_id).replace("-", " ").strip()
    title = words.title() if words else bug.bug_id
    area = title.split(" ", 1)[0] if title else "Walkthrough"
    return f"[{area}] {title}"


def issue_body(bug: BugSection, bug_report_display: str, report_path: str | None) -> str:
    report_line = report_path or "See walkthrough report in the same run directory."
    review_marker = (
        "DRAFT_REVIEW_REQUIRED: This generic draft must be rewritten in complete English before filing.\n\n"
        if bug.review_required
        else ""
    )
    return f"""## Summary

{review_marker}
{summary_for_bug(bug)}

## Triage reflection

{triage_reflection_for_bug(bug)}

## Environment

- Source bug ID: `{bug.bug_id}`
- Full walkthrough report: {report_line}
- Engineering bug report: {bug_report_display}
- Scope: see the linked report
- Time window: see the linked report

## Steps to reproduce

{steps_to_reproduce_for_bug(bug)}

## Expected behavior

{expected_behavior_for_bug(bug)}

## Actual behavior

{actual_behavior_for_bug(bug)}

## Evidence

- Full walkthrough report: {report_line}
- Engineering bug report: {bug_report_display}
- Use the linked full report and engineering bug report for raw step logs and screenshots.

## Impact

{impact_for_bug(bug)}

## Likely areas to inspect

{inspection_areas_for_bug(bug)}

## Not included / not this issue

- Missing fixtures, missing review tasks, missing low-permission accounts, missing controlled receivers, release-gate setup, and real-quality review are manual retest or test-environment items unless the project explicitly tracks them as engineering work.
- Do not include secrets, cookies, CSRF tokens, full API keys, provider secrets, webhook signing secrets, or private report bodies.
"""


def summary_for_bug(bug: BugSection) -> str:
    if bug.bug_id == "BUG-P7-WEBHOOK-DELIVERY-NOT-OBSERVED":
        return (
            "A webhook endpoint can be created, subscribed, and rotated, but no webhook delivery "
            "attempt is observable after a webhook-mode run produces a subscribed event within the wait window."
        )
    return (
        "A browser walkthrough found a reproducible product bug or bug candidate. "
        "Rewrite this generic summary into a concrete English description before filing."
    )


def triage_reflection_for_bug(bug: BugSection) -> str:
    if bug.bug_id == "BUG-P7-WEBHOOK-DELIVERY-NOT-OBSERVED":
        return """- Real issue assessment: The endpoint, subscription, and webhook-mode run preconditions completed, but no delivery attempt became observable within the wait window. This is a webhook delivery or delivery-observability bug candidate, not a missing fixture or browser automation artifact.
- Merge/split decision: Keep this issue separate from review/report fixture gaps and UI-only findings. Merge only with another webhook symptom that shares the same event enqueue, dispatcher, or delivery-list visibility path.
- Confidence: medium. The walkthrough repeatedly observed the missing delivery row; backend queue/dispatcher logs are still needed to decide whether enqueue failed, dispatch failed, or the delivery API hid the record."""
    return """- Real issue assessment: DRAFT_REVIEW_REQUIRED. Confirm the walkthrough evidence shows product behavior violating an expected contract, not a missing fixture, missing account, unavailable receiver, or automation crash.
- Merge/split decision: DRAFT_REVIEW_REQUIRED. Merge only with bugs sharing the same root path, owner, reproduction flow, and likely fix. Split if another symptom affects a different module, permission boundary, or workflow.
- Confidence: DRAFT_REVIEW_REQUIRED. Set to high, medium, or low after reviewing the latest run and any superseding evidence."""


def actual_behavior_for_bug(bug: BugSection) -> str:
    if bug.bug_id == "BUG-P7-WEBHOOK-DELIVERY-NOT-OBSERVED":
        return "No matching webhook delivery attempt was observed through the delivery API within the configured wait window, even though the endpoint and subscription setup completed."
    return "Rewrite this section in English with the exact status, timeout, error code, missing row, bad UI state, or leaked data observed in the walkthrough."


def steps_to_reproduce_for_bug(bug: BugSection) -> str:
    if bug.bug_id == "BUG-P7-WEBHOOK-DELIVERY-NOT-OBSERVED":
        return """1. Log in to the tested environment with an owner or integration-capable test account.
2. Create or open a test workspace that can run the product's workflow.
3. Create a webhook endpoint and subscribe it to terminal run events.
4. Trigger a webhook-mode run that reaches a terminal state covered by the subscription.
5. Wait through the configured webhook delivery window.
6. Query or open the webhook delivery list for the endpoint/run and check whether a delivery attempt was recorded."""
    return """1. Open the linked engineering bug report.
2. Follow the `Minimal Reproduction` steps for this source bug ID.
3. Replace this draft with exact English reproduction steps before filing."""


def expected_behavior_for_bug(bug: BugSection) -> str:
    if bug.bug_id == "BUG-P7-WEBHOOK-DELIVERY-NOT-OBSERVED":
        return (
            "After a subscribed terminal run event occurs, the webhook system should create an observable "
            "delivery attempt, retry state, failure state, or DLQ/diagnostic state for the endpoint within "
            "the documented processing window."
        )
    return "Rewrite this section in English with the concrete product contract that should have been satisfied."


def inspection_areas_for_bug(bug: BugSection) -> str:
    if bug.bug_id == "BUG-P7-WEBHOOK-DELIVERY-NOT-OBSERVED":
        return """- Event mapping between internal run terminal events and public webhook event types.
- Webhook enqueue path when a run reaches a failed or completed terminal state.
- Queue consumer and webhook dispatcher bindings/runtime state in the tested environment.
- Delivery API filtering by endpoint, run, status, or workspace.
- Endpoint status and subscription filters."""
    return "Rewrite this section in English with short hypotheses from the engineering bug report. Keep them as inspection hints, not conclusions."


def impact_for_bug(bug: BugSection) -> str:
    if bug.bug_id == "BUG-P7-WEBHOOK-DELIVERY-NOT-OBSERVED":
        return (
            "Webhook integrations cannot confirm that terminal run events were delivered or retried. "
            "Operators also lose the delivery log needed to diagnose downstream endpoint failures, which reduces release confidence for integration workflows."
        )
    return "Rewrite this section in English with the user, operator, integration, security, or release impact."


def needs_manual_english_rewrite(bug: BugSection) -> bool:
    return bug.bug_id not in KNOWN_TITLES


def infer_report_path_from_bug_report(bug_report: Path) -> str:
    candidate = bug_report.parent / "report.md"
    return candidate.as_posix() if candidate.exists() else "See walkthrough report in the same run directory."


def safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")[:120] or "issue"


def write_issue_drafts(
    bugs: list[BugSection],
    bug_report_display: str,
    output_dir: Path,
    report_path: str | None,
) -> list[dict[str, str]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str]] = []
    for bug in bugs:
        title = make_english_title(bug)
        body = issue_body(bug, bug_report_display, report_path)
        body_path = output_dir / f"{safe_filename(bug.bug_id)}.md"
        body_path.write_text(body, encoding="utf-8")
        manifest.append(
            {
                "bug_id": bug.bug_id,
                "title": title,
                "body_file": body_path.as_posix(),
                "review_required": bug.review_required,
            }
        )
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_triage_review(bugs, output_dir)
    return manifest


def write_triage_review(bugs: list[BugSection], output_dir: Path) -> None:
    lines = [
        "# GitHub Issue Triage Review",
        "",
        "Review this file before creating live GitHub issues.",
        "",
    ]
    if not bugs:
        lines.extend(
            [
                "No fileable bug candidates were found in `bugs-for-engineers.md`.",
                "Do not create GitHub issues for fixture gaps, manual retest items, or automation-only failures.",
                "",
            ]
        )
    for bug in bugs:
        lines.extend(
            [
                f"## {bug.bug_id}",
                "",
                f"- Proposed title: {make_english_title(bug)}",
                f"- Is this truly an issue?: {'review required before filing' if bug.review_required else 'yes as a bug candidate: the required preconditions completed and the observed product path violated the expected delivery/visibility contract'}",
                "- Merge/split decision: keep separate unless another candidate has the same root path, owner, reproduction flow, and likely fix.",
                f"- Draft status: {'DRAFT_REVIEW_REQUIRED; rewrite in complete English before filing' if bug.review_required else 'ready for final human/AI review'}",
                "- Do not file if later evidence supersedes this candidate or shows it was a fixture/environment gap.",
                "",
            ]
        )
    (output_dir / "triage-review.md").write_text("\n".join(lines), encoding="utf-8")


def create_issues(manifest: list[dict[str, str]], repo: str, labels: list[str]) -> None:
    for item in manifest:
        body = Path(item["body_file"]).read_text(encoding="utf-8")
        if "DRAFT_REVIEW_REQUIRED" in body:
            raise SystemExit(f"{item['body_file']} still requires a complete English rewrite before filing")
        if not is_ascii(body) or not is_ascii(item["title"]):
            raise SystemExit(f"{item['body_file']} or its title contains non-ASCII text; rewrite the issue in English before filing")
        command = [
            "gh",
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            item["title"],
            "--body-file",
            item["body_file"],
        ]
        for label in labels:
            command.extend(["--label", label])
        subprocess.run(command, check=True)


def is_ascii(value: str) -> bool:
    try:
        value.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bug-report", required=True, type=Path, help="Path to bugs-for-engineers.md")
    parser.add_argument("--output-dir", type=Path, help="Directory for GitHub issue draft files")
    parser.add_argument("--report-path", help="Optional full report path/link to include in issues")
    parser.add_argument("--repo", help="GitHub repo in OWNER/REPO format")
    parser.add_argument("--label", action="append", default=[], help="Label to apply when --create is used; repeatable")
    parser.add_argument("--create", action="store_true", help="Create issues with gh issue create")
    parser.add_argument("--yes", action="store_true", help="Required with --create to acknowledge reflective triage was completed")
    args = parser.parse_args()

    bug_report_display = args.bug_report.as_posix()
    bug_report = args.bug_report.resolve()
    bugs = parse_bug_report(bug_report)
    output_dir = args.output_dir or bug_report.parent / "github-issues"
    report_path = args.report_path or infer_report_path_from_bug_report(bug_report)
    manifest = write_issue_drafts(bugs, bug_report_display, output_dir, report_path)
    print(f"Prepared {len(manifest)} GitHub issue draft(s) in {output_dir}")

    if args.create:
        if not args.repo:
            raise SystemExit("--repo OWNER/REPO is required with --create")
        if not args.yes:
            raise SystemExit("--yes is required with --create after confirming issue triage, merge/split decisions, and English issue completeness")
        create_issues(manifest, args.repo, args.label)

    if not manifest:
        print("No fileable bugs found. Do not create GitHub issues for fixture gaps or manual retest items.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
