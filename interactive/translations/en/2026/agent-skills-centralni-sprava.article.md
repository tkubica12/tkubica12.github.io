---
format_version: 1
title: "How to centrally manage and govern skills for agents"
eyebrow: "Skills as a team capability"
subtitle: "Download a central skill, create a local PoC when it needs improvement, send the proposal to GitHub, let agents triage and prepare a PR after human approval, and distribute the improved skill to everyone."
slug: agent-skills-centralni-sprava
date: 2026-05-11
language: en
source_language: cs-CZ
source_slug: agent-skills-centralni-sprava
translation: machine
translated_from_hash: e5295c09b619c061b1271149b03d9d98d2dd6051e8d2b845e4a7186eec0a4239
translation_status: current
status: experimental
canonical_url: "/en/2026/agent-skills-centralni-sprava/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

# How to centrally manage and govern skills for agents

Want to teach your agent something? I will show it on the [skills-demo-catalog](https://github.com/tkubica12/skills-demo-catalog) demo: a central skill catalog, a simulated Task API, a local PoC in a consumer repository, the issue process, agentic triage, a cloud agent, and a benchmark that measures whether the skill really improved.

::: callout type="verdict" title="The point"
A skill is great for knowledge, instructions, and governance. A CLI or another tool is great for repeatable, multi-step, measurable work. GitHub is the natural place where a local experience becomes a team-governed capability.
:::

::: group id="idea" title="Idea"

::: card number="01" title="Task API as a safe demo problem" default="open"
For the purposes of the demo, I built my own API for managing tasks. It is not the GitHub API and it is not about real company systems. It is a simulated, controlled problem: tasks, comments, the `waiting-for-response` state, occasional `429`, and a workflow realistic enough for an agent to hit the same problems as in practice. The whole demo catalog is public in the [tkubica12/skills-demo-catalog](https://github.com/tkubica12/skills-demo-catalog) repository.

The catalog contains the `task-api-helper` skill, which includes:

- `SKILL.md` with instructions and a description of the capability.
- `scripts/task_cli.py` as a CLI wrapper over the Task API.
- `references/API.md` for understanding the underlying API when the CLI is not enough.
- `references/IMPROVEMENT-PROCESS.md` with rules for improving the skill through a central process.
:::

::: card number="02" title="Evolution: context -> CLI -> higher-level operations" default="open"
In my view, the typical evolution of a skill over an API looks like this:

::: sequence title="The path from knowledge to shared capability"
1. **Skill as context** — Markdown explains the API, business context, and the right way to use it.
2. **Adding a CLI** — the agent uses stable commands instead of composing `curl`, escaping JSON, and handling retries manually.
3. **Higher-level operations in the CLI** — repeatable multi-step workflows move into code so the agent does not have to reconstruct them every time.
:::

This is where the key question appeared: if skills like this start emerging locally, how do we manage them centrally for the team? I do not want everyone copying files by hand. I want governance, change proposals, approvals, benchmarks, and clear distribution.
:::

:::

::: group id="lokalni-zkusenost" title="Local experience"

::: card number="03" title="Installing the skill from the catalog" default="open"
In a new, completely ordinary repository, I install the skill from the central catalog using `gh skill`:

```bash label="Installation from the central catalog"
gh skill install tkubica12/skills-demo-catalog task-api-helper --scope project --agent github-copilot
```

Then I configure `.env` in the installed skill so the CLI knows where the demo Task API is running:

```dotenv label=".agents/skills/task-api-helper/.env"
TASK_API_URL=https://task-api-demo.example.azurecontainerapps.io
```

The consumer repository is still clean. The capability came from the catalog, not from a local copy-paste prompt.
:::

::: card number="04" title="First use: it works, but it hurts" default="open"
The agent can use the Task API. It can list tasks waiting for a response, open a specific task, and add a comment. The problem starts when I want to add the same comment to all tasks in the `waiting-for-response` state.

::: reveal title="Transcript from using the Task API"
```text
> List tasks waiting for response and summarize what needs attention.

The Task API is responding, but the first request hit a rate limit. I’m checking the response shape and then retrying with a short pause so I can give you the actual waiting items instead of a guess.

5 tasks are waiting for response. The ones needing the most attention are the two high-priority items stalled on external confirmation or approval.

  ┌──────────────────────────────────────────────────────────────────┬──────────┬───────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Task                                                             │ Priority │ Assignee          │ Needs attention                                                                                                        │
  ├──────────────────────────────────────────────────────────────────┼──────────┼───────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ task-1 — Waiting on customer confirmation — order #8821          │ High     │ alice@example.com │ Customer still has not confirmed after the initial outreach and a 48-hour follow-up.                                   │
  │ task-3 — Awaiting legal sign-off on NDA amendment                │ High     │ carol@example.com │ Legal review is pending after the NDA draft was forwarded.                                                             │
  │ task-2 — Pending vendor reply for Q3 renewal                     │ Medium   │ bob@example.com   │ Vendor has not replied since the renewal quote was sent.                                                               │
  │ task-5 — Infrastructure cost review — ops team response needed   │ Medium   │ eve@example.com   │ Ops response is pending, and there is no comment history, so this likely needs owner context or a first follow-up.     │
  │ task-4 — Customer reported login failure — needs repro steps     │ Low      │ dave@example.com  │ Blocked waiting for the customer to provide reproduction steps.                                                        │
  └──────────────────────────────────────────────────────────────────┴──────────┴───────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

> Open task-1 and add this comment: "Following up - please provide an update."

Added the comment to task-1. The API accepted it as comment c-c0d260d5.

> Add the same comment to every task waiting for response.

The bulk run hit rate limits mid-stream. I’m reading the exact output and then I’ll finish only the tasks that didn’t get updated.
task-5 was the only one not updated. I’m retrying that single task with a slower cadence to get it through cleanly.
Done. The comment was added to all other tasks currently in waiting-for-response, and task-1 was skipped because it already had the same comment.
```
:::
:::

::: card number="05" title="The agent suggests an improvement on its own"
This is exactly the moment when it makes sense to ask the agent what could be done better. Not so it immediately changes the central catalog, but so it first describes the repeated pain and proposes a verifiable local experiment.

::: reveal title="Improvement proposal"
```text
Best improvement: add a first-class bulk command to the shared CLI, for example:

python task_cli.py bulk-add-comment --status waiting-for-response --text "Following up - please provide an update." --skip-existing

That would help because this workflow currently requires list -> get each task -> detect duplicates -> post comment, which is slow and exposed to 429 rate limits. A bulk command could make it both faster and more reliable by handling:

- built-in retry/backoff for rate limits
- duplicate-comment detection (--skip-existing)
- a single summary of which tasks were updated or skipped

Per the skill’s process, the right next step would be a local proof of concept that captures before/after evidence: fewer API calls, fewer retries, and cleaner operator output.
```
:::
:::

::: card number="06" title="Local PoC: issue, benchmark, and evidence" default="open"
Here is an important governance detail: the consumer agent can create a **temporary local PoC** to validate the hypothesis. But it must not permanently fork the central skill. After validation, it should throw away the local change and open an issue in the catalog with evidence.

The result in the demo: [skills-demo-catalog issue #15](https://github.com/tkubica12/skills-demo-catalog/issues/15).

::: tabs id="poc-evidence"
::: tab id="baseline-loop" title="Baseline loop"
The original process had to do list -> get individual tasks -> duplicate checks -> comments one by one. In the PoC measurement it handled **4/5 tasks**, took about **29.96s**, and hit **1 rate-limit failure**.
:::
::: tab id="bulk-poc" title="Bulk PoC"
The temporary `bulk-add-comment` command solved the same goal as one higher-level operation. Result: **5/5 tasks**, about **6.27s**, **0 failures**.
:::
::: tab id="repeat-run" title="Repeated run"
A repeated run validated `--skip-existing`: the agent does not duplicate comments and gets a clean summary of what it updated and what it skipped.
:::
:::

::: reveal title="The agent writes the PoC into the upstream issue"
```text
> OK, this make sense. Follow improvement guide, test this idea locally as PoC and if it is good, publish this is detailed issue into skills-demo-catalog repository.

I’m setting up a proper local PoC in the installed skill, capturing before/after evidence, and then I’ll revert the local patch before opening the upstream issue if the results hold.
I’ve got a clean baseline: 11 calls over ~30s, one 429, and only 4 of 5 tasks updated.
The first PoC run worked cleanly: all 5 tasks updated in about 6 seconds with no failures.
I’ve got enough evidence now: the PoC fixed the partial-failure case and validated duplicate skipping. I’m writing the findings down, restoring the installed skill to the published baseline, and then I’ll open the upstream issue from that evidence.

https://github.com/tkubica12/skills-demo-catalog/issues/15
```
:::
:::

:::

::: group id="centralni-governance" title="Central governance"

::: card number="07" title="Repository as catalog and process" default="open"
A local PoC is good for learning. For a team we need a repository that is a catalog, an audit trail, a distribution mechanism, and the place where changes are decided.

::: steps title="Improvement lifecycle"
1. **Local experiment** — the consumer team tries a temporary PoC against the workflow that hurts.
2. **Benchmark** — it captures before/after evidence: time, retries, fewer manual steps, cleaner output.
3. **Issue with template** — local changes are discarded and an issue is opened in the catalog.
4. **Advisory triage** — an agentic workflow adds a recommendation and possibly `copilot-recommended`.
5. **Human triage** — the maintainer decides whether the change belongs in the shared contract.
6. **Copilot implementation** — after `accepted`, the cloud agent implements the change.
7. **Pull request** — the PR changes the CLI, documentation, tests, and benchmark spec.
8. **Catalog release** — after merge, the catalog is tagged and released.
9. **Consumer update** — consumers update the skill and remove the local workaround.
:::
:::

::: card number="08" title="Agentic triage in GitHub Actions" default="open"
For triage I used GitHub Agentic Workflows in GitHub Actions. The workflow reads the issue, checks whether it has local PoC evidence, and adds a short recommendation for the maintainer. Important: the agent does not add `accepted` and does not replace the human decision.

- Workflow definition: [`task-api-enhancement-triage.md`](https://github.com/tkubica12/skills-demo-catalog/blob/main/.github/workflows/task-api-enhancement-triage.md)
- Issue: [#15 Bulk add comment command](https://github.com/tkubica12/skills-demo-catalog/issues/15)
- Advisory label: `copilot-recommended`
- Human gate: `accepted`

::: reveal title="Screenshots of triage and labels"
![Issue with PoC evidence](/images/2026/2026-05-02-12-13-01.png)
![Agentic triage workflow run](/images/2026/2026-05-02-12-13-48.png)
![Accepted label as a signal for the next step](/images/2026/2026-05-02-12-22-20.png)
:::
:::

:::

::: group id="agenticke-doruceni" title="Agentic delivery"

::: card number="09" title="The accepted label starts the cloud agent" default="open"
The next step is intentionally simple: after the `accepted` label is added, the issue is assigned to Copilot in the cloud. From the issue and the catalog it has enough context to prepare the change as a pull request. The human still decides, but repetitive implementation work goes to the agent.

::: reveal title="Cloud agent workflow and run"
![Workflow for starting the cloud agent](/images/2026/2026-05-02-12-23-31.png)
![The cloud agent starts working](/images/2026/2026-05-02-12-23-52.png)
:::
:::

::: card number="10" title="Pull request without ongoing steering" default="open"
In this experiment I did not intervene with the agent any further. The result was not perfect, but it was good enough for review: it added a higher-level CLI operation, updated skill instructions, added tests, and prepared a benchmark spec. That is exactly what I think the first agentic delivery should look like.

::: reveal title="Pull request and changes"
![Pull request from the agent](/images/2026/2026-05-02-14-31-15.png)
![Detail of changes in the PR](/images/2026/2026-05-02-14-31-55.png)
:::
:::

::: card number="11" title="Benchmark as evidence, not a feeling" default="open"
The benchmark matters because otherwise this would only be an impression. In the local PoC we already have evidence that the higher-level operation helped:

| Variant | Success rate | Time | Rate-limit failure |
|---|---:|---:|---:|
| Baseline loop | 4/5 | 29.96s | 1 |
| Bulk PoC | 5/5 | 6.27s | 0 |

In the PR the demo goes even further: the `ci-benchmark.yml` workflow runs an agentic benchmark through the GitHub Copilot SDK and compares the same target task with the skill from `main` and with the skill from the PR. It measures success, the number of updated tasks, time, input/output tokens, LLM calls, Task API requests, and `429`.

::: reveal title="Benchmark workflow and output"
![Benchmark workflow](/images/2026/2026-05-02-14-32-31.png)
![Benchmark summary](/images/2026/2026-05-02-14-33-02.png)
:::
:::

:::

::: group id="shrnuti" title="Summary and what to try"

::: card number="12" title="Final result" default="open"
The point is not one prettier prompt. The point is that a local finding does not remain a local hack, but goes through evidence, an issue, a human decision, agentic implementation, and a measured release back into the shared catalog.

::: summary-grid
- **Catalog**: `skills-demo-catalog` holds the source of truth for the skill, CLI, API reference, and improvement process.
- **Governance**: a local PoC leads to an issue, triage, human `accepted`, and a PR.
- **Measurement**: benchmarks show time, tokens, LLM calls, API requests, and `429`.
- **Distribution**: consumers update the central skill through `gh skill` instead of maintaining a local fork.
:::
:::

::: card number="13" title="Practical checklist" default="open"
If you want to try something similar, I would recommend:

::: arrow-list title="Checklist for your own catalog"
- Use `gh skill` to manage skills and their versioning in a central repository.
- Add a clear improvement process to the skill: PoC, evidence, issue template.
- Let the agent first try a local disposable PoC, but do not let it secretly fork the central skill.
- Use GitHub Actions and labels as explicit governance signals.
- Try GitHub Agentic Workflows for triage, documentation, or agentic testing.
- Use the GitHub Copilot cloud agent to turn an issue into code and a pull request.
- Measure skill quality through Copilot CLI or SDK directly in the pipeline.
- Review the whole demo: [tkubica12/skills-demo-catalog](https://github.com/tkubica12/skills-demo-catalog).
:::
:::

:::
