---
title: "How to centrally manage and govern skills for agents"
slug: agent-skills-centralni-sprava
date: 2026-05-11
language: en
source_language: cs-CZ
source_slug: agent-skills-centralni-sprava
translation: machine
translated_from_hash: e5295c09b619c061b1271149b03d9d98d2dd6051e8d2b845e4a7186eec0a4239
translation_status: current
status: experimental
canonical_url: /en/2026/agent-skills-centralni-sprava/
---

# Central skill management

Goal: local skill -> team capability. Demo: https://github.com/tkubica12/skills-demo-catalog. This is not GitHub API; it uses a simulated Task API: tasks, comments, `waiting-for-response`, occasional `429`. Skill `task-api-helper` contains instructions, `scripts/task_cli.py`, API reference, and improvement process.

## Point

Skill = knowledge + instructions + governance. CLI/tool = repeatable multi-step work. GitHub = catalog, audit trail, issue process, PR, release.

## Flow

1. Skill gives the agent Task API context.
2. CLI wraps mechanics: commands, retry, JSON, error handling.
3. Higher-level CLI operation wraps repeatable workflow.
4. Consumer creates disposable local PoC.
5. PoC is measured.
6. Local patch is discarded.
7. Issue with evidence goes to the catalog.
8. Agentic triage adds recommendation, e.g. `copilot-recommended`.
9. Human adds `accepted`.
10. Cloud Copilot implements PR.
11. Improved skill is released back to everyone.
12. After merge, consumers update the skill through `gh skill`.

## Installation

```bash
gh skill install tkubica12/skills-demo-catalog task-api-helper --scope project --agent github-copilot
```

`.env` inside the skill:

```dotenv
TASK_API_URL=https://task-api-demo.example.azurecontainerapps.io
```

## Local pain

Task: list `waiting-for-response` tasks, open a task, add a comment, then add the same comment to all waiting tasks. The agent managed it, but workflow was list -> get each task -> duplicate check -> post comment one by one. Slow and exposed to `429`.

Agent proposed command:

```bash
python task_cli.py bulk-add-comment --status waiting-for-response --text "Following up - please provide an update." --skip-existing
```

Meaning: retry/backoff, skip duplicates, one summary updated/skipped.

## PoC evidence

Upstream issue: https://github.com/tkubica12/skills-demo-catalog/issues/15

| Variant | Success | Time | 429/fail |
|---|---:|---:|---:|
| Baseline loop | 4/5 | 29.96s | 1 |
| Bulk PoC | 5/5 | 6.27s | 0 |

Repeated run validated `--skip-existing`: it does not duplicate comments.

## Governance

Catalog repository is the source of truth for skill, CLI, API reference, and improvement process. Agentic GitHub Actions triage reads the issue and checks whether proposal has PoC + measurement. It adds recommendation/advisory label, but not final approval. Human gate is `accepted`.

Workflow definition: `.github/workflows/task-api-enhancement-triage.md` in `skills-demo-catalog`. Important labels: `copilot-recommended` = agent recommends; `accepted` = human approved implementation.

## Delivery

After `accepted`, issue is assigned to Copilot cloud agent. Agent creates PR: higher-level CLI operation, skill instruction changes, tests, benchmark spec. Human reviews/merges.

Benchmark in PR can use GitHub Copilot SDK to compare skill from `main` vs skill from PR on same task. Metrics: success, updated tasks, time, input/output tokens, LLM calls, Task API requests, `429`.

## Result

- Local finding does not remain local hack.
- Catalog: `skills-demo-catalog` holds source of truth.
- Governance: PoC -> issue -> triage -> human `accepted` -> PR -> release.
- Measurement: benchmarks instead of feeling.
- Distribution: `gh skill`, no local forks.

## Checklist

- Manage skills through central repo and `gh skill`.
- Add improvement process to the skill.
- Allow local PoC, but only as disposable patch.
- Proposal must have before/after evidence.
- Agentic triage is advisory; human decides.
- Cloud agent implements PR, not final merge.
- Measure skill quality with pipeline benchmark.
