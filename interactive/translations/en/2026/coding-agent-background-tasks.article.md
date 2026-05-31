---
format_version: 1
title: "Coding agents — parallel agent work on your tasks"
subtitle: "How to use GitHub Copilot CLI, git worktree and background agents in VS Code when you want to run multiple agents locally without them overwriting each other's files."
slug: "coding-agent-background-tasks"
date: "2026-01-06"
language: "en"
source_language: "cs-CZ"
source_slug: "coding-agent-background-tasks"
translation: "machine"
translated_from_hash: "7BC13B908D660E72E0759DA4ADBBA4AA0E232399E17D2B94DD8F0F8129E84EC1"
translation_status: "current"
status: "experimental"
canonical_url: "/en/2026/coding-agent-background-tasks/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Coding agents — parallel agent work on your tasks

As AI models grow more capable at coding and working independently, I am trying to incorporate more parallelism into my workflow.

There are situations where I want to work interactively with the agent — watching what it does, partly to learn from it, but also to step in if it goes off track or starts digging into the architecture and coming up with workarounds instead of figuring out the right approach. But other times I do not need that — these are tasks where I have a clear specification or sufficient requirements and I only need to look at the result — for example some investigation (suggestions for improvements, I often ask whether I should refactor, better modularize, abstract, etc.), documentation updates, deployment scripts and definitions (such as Helm chart manifests — I do not need to be present for those, I just need to review the result), small tweaks, finishing off Dockerfiles and checking they work (building the image, running it locally to see if it starts — via MCP tools or CLI, for example).

Whenever I am doing something interactively in the main window, I used to handle it by opening another GitHub Copilot window and assigning something else there. But then all agents run and touch the same files, which may not end well. I have therefore been limiting this to investigative tasks (discussion, analysis) or situations where the work involves completely separate parts of the project (for example, the /src directory with code versus /specs). Occasionally I use the cloud agent in GitHub, which runs entirely in the cloud and creates a Pull Request — but for quick turnarounds where it is just me, that feels overly robust and slows me down a bit. I would rather run multiple agents locally and only push the results to origin once I have finished. How to do that?

::: callout type="verdict" title="The Point"
Parallel work by multiple agents makes sense, but I don't want them all touching the same files. Isolation via worktree and background agents is a practical way to do this locally and quickly.
:::

::: group id="cli" title="CLI agent"

::: card number="01" title="GitHub Copilot CLI — an agent without an IDE running practically anywhere" default="open"
There has been a lot of talk lately about AI coding agents that do not run inside an IDE but come in the form of some CLI. It is interesting how interface principles from computers sixty years ago still hold in some modified form. I will be using [GitHub Copilot CLI](https://github.com/features/copilot/cli/), but similarly you can use the open-source [OpenCode](https://opencode.ai/), which can have various local and cloud models on the backend — you can connect it to your Microsoft Foundry in Azure and use models like GPT-5.1-codex-max or Claude Sonnet 4.5, or [OpenAI CODEX CLI](https://developers.openai.com/codex/cli) or the proprietary [Claude Code](https://claude.com/product/claude-code).

GitHub Copilot CLI also has a nice ASCII UI.

```
┌──                                                                         ──┐
│                                                           ▄██████▄          │
    Welcome to GitHub                                   ▄█▀▀▀▀▀██▀▀▀▀▀█▄
    █████┐ █████┐ █████┐ ██┐██┐     █████┐ ██████┐     ▐█      ▐▌      █▌
   ██┌───┘██┌──██┐██┌─██┐██│██│    ██┌──██┐└─██┌─┘     ▐█▄    ▄██▄    ▄█▌
   ██│    ██│  ██│█████┌┘██│██│    ██│  ██│  ██│      ▄▄███████▀▀███████▄▄
   ██│    ██│  ██│██┌──┘ ██│██│    ██│  ██│  ██│     ████     ▄  ▄     ████
   └█████┐└█████┌┘██│    ██│██████┐└█████┌┘  ██│     ████     █  █     ████
    └────┘ └────┘ └─┘    └─┘└─────┘ └────┘   └─┘     ▀███▄            ▄███▀
│                              CLI Version 0.0.363      ▀▀████████████▀▀      │
└──                                                                         ──┘
 Version 0.0.363 · Commit 66416ad

 Copilot can write, test and debug code right from your terminal. Describe a task to get started or enter ? for help.
 Copilot uses AI, check for mistakes.

 ● Logged in with gh as user: tkubica12

 ● Connected to GitHub MCP Server

 C:\git\gh-copilot-demo\src\services\toy[⎇ main]                                                claude-sonnet-4.5 (1x)
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 >  Enter @ to mention files or / for commands
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Ctrl+c Exit · Ctrl+r Expand recent
```

I find the interactive mode particularly interesting in situations where I am on some remote system and need help solving tasks there. For example, on my home Orange Pi (a Chinese "clone" of Raspberry Pi), which is a small passively-cooled box with an ARM processor running Docker with a few containers, I can use GitHub Copilot CLI.

```
 Welcome to GitHub Copilot CLI
 Version 0.0.374 · Commit 9fecd24

 Copilot can write, test and debug code right from your terminal. Describe a task to get started or enter ? for help.
 Copilot uses AI, check for mistakes.

 ● Logged in as user: tkubica12

 ● Connected to GitHub MCP Server

 ~                                                                                              claude-sonnet-4.5 (1x)
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 > Na tomhle počítači běží několik Docker kontejnerů. Zjisti jaké to jsou, analyzuj jejich logy jestli tam nejsou
   nějaké chyby a stručně mi je popiš a posuď míru závažnosti. Také prozkoumej jak zatěžují tento systém a zda jsou
   to aktuální verze nebo ne a pokud ne, uveď 3 nejdůležitější změny u každého kontejnerového image.
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Ctrl+c Exit · Ctrl+r Expand recent



 ● Dobře, provedu komplexní analýzu Docker kontejnerů běžících na tomto systému.
   Začnu zjištěním, jaké kontejnery běží, a pak provedu detailní analýzu.

 ○ Zobrazit běžící Docker kontejnery
   $ docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
   ↪ 1 line...

 ╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
 │ Zobrazit běžící Docker kontejnery:                                                                                 │
 │                                                                                                                    │
 │ ╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮ │
 │ │ docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"                            │ │
 │ ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯ │
 │                                                                                                                    │
 │ Do you want to run this command?                                                                                   │
 │                                                                                                                    │
 │ ❯ 1. Yes                                                                                                           │
 │   2. Yes, and approve `docker` for the rest of the running session                                                 │
 │   3. No, and tell Copilot what to do differently (Esc)                                                             │
 │                                                                                                                    │
 │ Confirm with number keys or ↑↓ keys and Enter, Cancel with Esc                                                     │
 ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

However, the biggest attraction of CLI versions is not really the interactive mode or file editing (for that I prefer VS Code — and if the remote system has no UI, that is fine, I use local VS Code with a remote SSH connection), but standalone use — running with a specific task and parameters directly from the command line while Copilot does the work and exits. Great for scripts, CI/CD pipelines (for example generating a description of changes to display during approval in GitHub Actions) or specifically for running a standalone agent.

:::

:::

::: group id="worktree" title="Parallel Local Work"

::: card number="02" title="Manual Use of Multiple Agents with Git Worktree" default="open"
I would like to assign tasks to several agents locally on a single repository, but in a way where I control all the agents and all changes myself and do not need to set up complex Pull Requests and CI/CD pipelines for each of these changes separately. On the other hand, running them all against the same files — when they all need to write, run, and test — will not end well. We need isolation, but local-only is enough for me. Git supports creating branches (of course), but you switch to a specific branch and we want to run agents in parallel. That is why we can use the worktree concept, which lets us create a separate directory for each branch, keeping files locally isolated and allowing us to work on multiple branches simultaneously.

Let's create two new worktrees and an associated new branch for each — one per agent.

```bash
git worktree add ../gh-copilot-demo-agent1 -b agent1-task
git worktree add ../gh-copilot-demo-agent2 -b agent2-task

git worktree list
C:/git/gh-copilot-demo         fc02290 [main]
C:/git/gh-copilot-demo-agent1  fc02290 [agent1-task]
C:/git/gh-copilot-demo-agent2  fc02290 [agent2-task]
```

In one terminal I assign work to one agent (I specify the model, but there can be more).

```bash
cd ../gh-copilot-demo-agent1
copilot --allow-all-tools --model claude-sonnet-4.5 --prompt "I have k6 perftest, but no README for it. Create README.md file explaining how to run the perftest, what scenarios it covers, and how to interpret results."
git add -A
git commit -m "Agent 1 commit"
```

And in the second, the other one runs in parallel.

```bash
cd ../gh-copilot-demo-agent2
copilot --allow-all-tools --model claude-sonnet-4.5 --prompt "Some of Python services are using pip and requirements.txt. I want to migrate everything to uv as package manager. Make sure to migrate to toml files, remove requirements.txt and change Dockerfile and READMEs accordingly. Test your able to sync uv and that Dockerfile builds without errors."
git add -A
git commit -m "Agent 2 commit"
```

Now we can review and test both changes separately. Once I am satisfied, I can locally merge the changes into my main branch, remove the worktrees and branches, and only then push the whole thing to origin on GitHub (or create a Pull Request for the complete set of changes).

```bash
git merge agent1-task
git merge agent2-task
git worktree remove ../gh-copilot-demo-agent1
git worktree remove ../gh-copilot-demo-agent2
git branch -D agent1-task agent2-task
```

```
git log --graph --oneline --all
*   71e7342 (HEAD -> main) Merge branch 'agent2-task'
|\
| * 4d53ba3 Agent 2 commit
* | fdf038c Agent 1 commit
|/
```

:::

:::

::: group id="vscode" title="Background Agent in VS Code"

::: card number="03" title="Agent HQ: starting a background agent" default="open"
Directly in Visual Studio Code I can, in addition to interactive work with the agent, choose a new background agent.

::: reveal title="Screenshot: choosing a background agent"
![Choosing a background agent in VS Code](/images/2026/2026-01-06-07-39-38.png)
:::

GitHub Copilot directly offers isolation via worktree - it automates what we were doing manually.

Note: the background agent in VS Code is in practice a Copilot CLI session. This means it has access to tools and MCP servers available/configured for the CLI (typically a different list than the MCP servers you have in VS Code itself) and at the same time does not have access to VS Code extension tools.

::: reveal title="Screenshot: automatically created worktree"
![Automatically created worktree for the background agent](/images/2026/2026-01-06-07-41-05.png)
:::

```bash
git worktree list
C:/git/gh-copilot-demo                                         fc02290 [main]
C:/git/gh-copilot-demo.worktrees/worktree-2026-01-06T06-41-14  fc02290 [worktree-2026-01-06T06-41-14]
```
:::

::: card number="04" title="Monitoring, switching, and handing work off"
I can then monitor the work of individual running agents and switch between them.

::: reveal title="Screenshot: list of running agents"
![List of running background agents](/images/2026/2026-01-06-07-42-19.png)
:::

The great thing is that we can perform a handoff - passing work between agents. For example, I can have an interactive discussion about how to implement or improve something, and at the moment when I no longer feel the need to stay involved, I hand it off to a background agent.

::: reveal title="Screenshot: handoff to a background agent"
![Passing work from an interactive conversation to a background agent](/images/2026/2026-01-06-07-47-54.png)
:::

You can also invoke a background agent directly from the prompt using the @ sign.

```
@cli I have k6 perftest, but no README for it. Create README.md file explaining how to run the perftest, what scenarios it covers, and how to interpret results.
```
:::

::: card number="05" title="Applying changes back to the main workspace"
I can easily view the status of each agent and see what it is doing, what it is writing, and what changes it is proposing. I can simply decide which changes to accept - I have a UI for automating the merge into the branch where my VS Code workspace is. So I have the classic Keep/Undo button and also an "Apply to main workspace" button.

::: reveal title="Screenshot: Keep/Undo and applying changes"
![UI for accepting or reverting background agent changes](/images/2026/2026-01-06-07-55-57.png)
:::

Once I apply, I will see this change directly in my main workspace, i.e. in the branch where my VS Code is open.

::: reveal title="Screenshot: change after applying"
![Change projected into the main VS Code workspace](/images/2026/2026-01-06-07-58-18.png)
:::

In the agent list I can see who has unread messages, how many changes there are, and decide what to do next.

::: reveal title="Screenshot: agent status and unread messages"
![Agent status, unread messages, and number of changes](/images/2026/2026-01-06-07-59-49.png)
:::

:::

:::

::: group id="volba" title="When to Use What"

::: card number="06" title="When to Use Background or Cloud Agents vs. Interactive Local Agent" default="open"
When do I use which?

**Interactive local agent**
- I need interaction, want to present options and opinions, I choose and direct the conversation
- I want to watch how Copilot processes my request because I am interested in how it is done, or I need to supervise it so it does not go off track and start doing something I did not want
- The task is short and waiting for it will not take long — switching thoughts to background and back is not worth it for half a minute
- I do need parallel running, but everything is in read-only mode — for example I am having a parallel discussion about the next step or architecture, and a new window is enough for that

**Background agent in VS Code**
- I already know what I want, I have a specification or a good prompt, and I trust that the model handles this task well (we have done this before, I know it turns out well).
- I need to try different solution approaches or different models, I am not proceeding linearly — for example, 3 ways to solve it come to mind and I am not sure whether it will be better in GPT-5.2 or Sonnet 4.5; there is no problem assigning these to background agents and once they are done, selecting the one that led to the best result.
- Key for this scenario is that the tasks are all mine and I evaluate them myself, and I will present them to the "project" — i.e. other team members — all at once. I treat it as a kind of fast-turnaround solution for myself, and only its compilation produces the Pull Request that goes through the full approval and testing cycle.

**Cloud agent in GitHub.com**
- For me mainly for situations where I do not need my computer running — I want to kick it off perhaps from my phone and check the results later, especially if there is already an Issue created for it.
- But the main thing is a robust, auditable solution within the collaboration of many people and agents, where proposed changes go through various team members or AI agents (such as security agents), each step requires robust testing, etc. Then using a cloud agent that produces a proper PR is the right and sustainable approach.

Into all of this, of course, tools still play a role — and today not only MCP, but also Skills (which can also be used for more efficient context management) — we will look at that next time. And also in VS Code there is the concept of a Custom Agent, we will look at that too — how agents can be customized and how to prepare more specialized ones.


::: summary-grid
- **Interactive agent**: when I want to learn, control direction, or discuss architecture.
- **Background agent**: when I have a clear task, want parallel variants, and will evaluate the result locally.
- **Cloud agent**: when I need an auditable PR process, team collaboration, or work without a running computer.
- **Worktree**: basic local isolation so agents do not fight over the same files.
:::

:::
:::


::: closing
In my view, a good agentic workflow is a mix: interactive where decisions are being made, background where the task is already clear, and cloud where a team-auditable PR needs to emerge.
:::
