# Browser Walkthrough Reporter

Reusable AI-agent skill for planning and running browser-based simulated manual walkthroughs for web/API products.

The skill helps an agent:

- inspect a project and map product capabilities to a browser walkthrough plan;
- generate a reusable walkthrough plan and Playwright runner scaffold;
- record every step with `START` and terminal status rows;
- capture screenshots for every step;
- produce three per-run Markdown documents: full report, engineering bug report, and manual retest checklist;
- update `kanban.html` or another test board with links, screenshots, and direct manual-confirmation items.

## Repository Layout

```text
browser-walkthrough-reporter/
├── README.md
├── LICENSE
└── browser-walkthrough-reporter/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/reporting-standard.md
    └── scripts/scaffold_browser_walkthrough.py
```

The nested `browser-walkthrough-reporter/` directory is the actual skill folder. The repository root contains open-source project metadata only.

## Install

### Codex

Copy the skill folder into your Codex skills directory:

```sh
cp -R browser-walkthrough-reporter "${CODEX_HOME:-$HOME/.codex}/skills/"
```

If your Codex home is `~/.codex-company`, copy there instead.

### Claude Code

Copy or symlink the nested `browser-walkthrough-reporter/` skill directory into your Claude Code skills directory, or use it from a project-level skills location supported by your Claude Code setup.

## Usage

Ask your agent:

```text
Use $browser-walkthrough-reporter to inspect this project, design and run a browser walkthrough, generate the three reports, and update kanban.html.
```

To scaffold files manually inside a target project:

```sh
python3 /path/to/browser-walkthrough-reporter/scripts/scaffold_browser_walkthrough.py --project-root .
```

The scaffold creates:

- `doc/browser-walkthrough-plan.md`
- `scripts/browser-walkthrough.mjs`
- `doc/browser-walkthrough-reports/`

Adapt the generated script to the target project's routes, selectors, APIs, fixtures, cleanup rules, and test board before treating coverage as complete.

## Output Contract

Each run must create:

```text
doc/browser-walkthrough-reports/<YYYYMMDD-HHmmss>-browser-walkthrough-<env>/
├── report.md
├── bugs-for-engineers.md
├── manual-retest-needed.md
├── screenshots/
└── downloads/
```

`bugs-for-engineers.md` is intentionally strict: missing fixtures and manual-only risks should not be counted as product bugs. Those belong in `manual-retest-needed.md` and in the Kanban/test-board manual-confirmation list.

## Safety

Do not write passwords, cookies, CSRF tokens, full API keys, provider secrets, webhook signing secrets, or private report bodies into reports, screenshots, logs, or Kanban/test boards.

Use disposable test data and clean up temporary credentials, webhooks, provider secrets, and other mutable resources after each run.
