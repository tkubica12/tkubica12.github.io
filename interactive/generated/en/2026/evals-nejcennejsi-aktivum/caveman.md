---
title: "Your company's most valuable asset in the AI world is the definition of what good looks like."
slug: evals-nejcennejsi-aktivum
date: 2026-07-29
language: en
status: experimental
canonical_url: /en/2026/evals-nejcennejsi-aktivum/
source_slug: evals-nejcennejsi-aktivum
translated_from_hash: 3b97a53f4dfcd1a47a549ac8776b639b58aab0754f99b2bbf43a395adcac6fc7
translation_status: current
---

# Your company's most valuable asset in the AI world is the definition of what good looks like.

Machine translation of the Czech source.

META
- url: /en/2026/evals-nejcennejsi-aktivum/
- source: source.md
- date: 2026-07-29
- audience: CTOs, architects, enterprise AI leads
- thesis: Value moved prompt → context → agentic behaviour → specification → closed loop → **the definition of a good result** (evals). The last stop is the only one nobody can supply from outside.

STRUCTURE
- intro: onboarding a new hire (a day for data, six months for tacit knowledge)
- G0 What this is about: Satya on private evals as the biggest IP
- G1 From prompt to agent: 01 prompt engineering, 02 context engineering, 03 agentic behaviour and memory
- G2 From a line to an intent: 04 growth of the unit of assignment, 05 spec-driven development
- G3 Closing loops in coding: 06 Shumer's Gauntlet Loop, 07 "It does not.", 08 loop engineering and a $70 workshop
- G4 Hill-climbing and enterprise loops: 09 three layers of knowledge + Reverse Information Paradox, 10 hill-climbing and 4 adoption layers, 11 Autopilots and Agent 365, 12 executable evals, 13 employee vs. hired consultant
- G5 Conclusions: 3 detail cards + checklist + closing

KEY POINTS
- Evals = a specification you can run. A spec says *how to do something*, evals say *how I know the result is good*.
- Shumer's loop worked because it had a public definition of a good result (real Call of Duty screenshots). Your company has no such reference point.
- If a model knows your company perfectly, you are a commodity at zero margin.
- Three layers of company knowledge: explicit data / institutional and procedural / tacit in people's heads. Only the first can be handed over in an afternoon.
- Continuous (on-the-job) learning is the next adoption phase, not a better chatbot.
- The result of learning (evals, skills, tuned weights) must stay in your own tenant.

DETAILS

## 01 Prompt engineering
- 2023 techniques: positive phrasing, important stuff last, few-shot, "let's think step by step", structured input. They worked back then.
- Anthropic 2023: "Prompt Engineer and Librarian" role up to 335,000 USD/year (Washington Post).
- arXiv 2506.00058: 72 prompt-engineer roles out of 20,662 on LinkedIn = 0.35%. The market never formed.
- Not dead, just split: the mechanical half disappeared into the model.
- OpenAI reasoning best practices: "Avoid chain-of-thought prompts", "Try zero shot first".
- Anthropic still says examples are "one of the most reliable ways". Not black and white, depends on model family.
- Verdict: we stopped worrying about **how** to ask, started worrying about **what** we ask for.

## 02 Context engineering
- Tobi Lütke 19 Jun 2025: "the art of providing all the context for the task to be plausibly solvable by the LLM".
- Karpathy 25 Jun 2025: "the delicate art and science of filling the context window with just the right information for the next step".
- Anthropic 29 Sep 2025: formalised curation of tokens during inference (prompt, tools, MCP, history, memory, external data).
- Shift: we tune what is in the model's field of view (context window). We still build that field of view.

## 03 Agentic behaviour
- The agent fetches context itself: DB queries, file reads, iteration.
- RAG is not dead - essential for cost, latency and quality.
- Anthropic multi-agent Research: +90.2% over single-agent Opus 4 on an internal eval, but ~15x more tokens than normal chat.
- Microsoft Agentic Retrieval is described as a tool *for* RAG patterns, not a replacement.
- Anthropic Agent Skills 16 Oct 2025, memory tool 29 Sep 2025, open standard agentskills.io 18 Dec 2025.
- Procedural memory = the agent generalises a solved dead end into a skill. The beginning of learning.

## 04 How the unit of assignment grew
- Line (autocomplete) → function / multi-file edit → task (coding agent runs and fixes itself).
- Work did not shrink, the "how" did.
- At the task level, feedback appeared for the first time (tests → red → fix). The seed of the rest of the article.

## 05 Spec-driven development
- AWS Kiro 14 Jul 2025; GitHub Spec Kit 2 Sep 2025 (Specify → Plan → Tasks → Implement).
- Three reasons: code is an output artefact; a spec is readable by humans and machines; a spec is testable.
- Introduced an independent checker (one agent writes, another verifies) = audit artefact.
- THE CRACK: a specification describes **how to do something**, it does not say how to know the result is good.

## 06 Gauntlet Loop
- Matt Shumer 25 Jul 2026: "Claude Opus 5 one-shotted this game" (FPS in ThreeJS). Gauntlet Loop methodology two days later.
- The prompt does not say HOW, it says HOW YOU KNOW IT IS DONE: separate subagent, harsh critic, blind comparison, /loop until the critic says enough.
- Shumer: "I gave Claude Code one prompt, then left it alone... I did not sit there steering it, at all." ~55,000 lines, many hours.
- Reference point: "For the game, I used actual Call of Duty screenshots." Real frames, not just model memory.
- Harness: Playwright + headless Chromium, 11 predefined full HD views (environment, lighting, materials, weapon, aiming, impacts, HUD), blind comparison against CoD frames.
- KEY MOMENT: the loop worked because it had a ready-made public definition of good - literally downloadable images.

## 07 Your company is not Call of Duty
- Repo mshumer/Claude-of-Duty: "The goal was to match a modern Call of Duty. It does not."
- Score 3.59 → 4.14 → 4.05 → 5.05 out of 10 (one round was worse than the previous). 2 of 11 views "CLOSE", the rest "AMATEUR".
- In **every** blind A/B the real Call of Duty won.
- The loop honestly measured failure. That is worth more than a polished demo with no number.
- ESSENTIAL FINDING: your reference point does not exist anywhere. If a model knows your company perfectly, you are a commodity at zero margin.

## 08 Loop engineering
- Addy Osmani 7 Jun 2026: "replacing yourself as the person who prompts the agent. You design the system that does it instead."
- Peter Steinberger (author of OpenClaw), same day: "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents."
- Author's interpretation: I do not talk to the agent, I talk to a **foreman**. He splits the intent, writes the specs, hands out work and whips the agents.
- Case: a one-day Microsoft Foundry workshop. Subagents through the eyes of educator, student, designer, engineer.
- Result for ~70 USD: perfect materials, factually correct, pedagogically excellent. **There was no Azure in it.** All binned.
- Author's mistake: the loop checked topics, structure, visuals, flow - it never touched a real Azure resource.
- Verdict: loop engineering does not remove the hard work, it moves it - from "tell me what it should look like" to "tell me how you will know it is good".

## 09 We know more than we can tell
- Three layers: (1) explicit data, (2) institutional and procedural knowledge (often in code), (3) tacit knowledge in people's heads.
- Polanyi 1966: "we can know more than we can tell."
- The first layer is the only one you can hand over in an afternoon - and what you hand over can be copied.
- Giving data to a vendor for training benefits them more. Having data in the cloud is fine, giving up control over it is not.
- Satya Nadella 12 Jul 2026 (x.com/satyanadella/article/2076323181154230284): **Reverse Information Paradox**.
  - Arrow: a buyer does not know the value of information until revealed; once revealed they have it for free.
  - AI flipped it: the **buyer** must reveal know-how. You pay twice - with money and with knowledge.
  - "Models learn from exhaust... Every correction is distilled into institutional know-how... leaks almost imperceptibly: trace by trace, correction by correction, eval by eval."
- Verdict: what is universal ends up in the model. What is yours you must keep - for all three layers.

## 10 Hill-climbing machine
- MAI team 2 Jun 2026: the goal is "what we think of as a hill-climbing machine: an organization that can continuously improve, cycle after cycle".
- Thinking Machines Lab 10 Jul 2026: "Most AI in use today is trained in a handful of places and then frozen."
- Inkling (15 Jul 2026): a model prepares its own evals, gathers data and fine-tunes through Tinker. A controlled experiment.
- Four adoption layers: (1) chat helper, (2) auditable automation workflow, (3) personal worker with real-world impact, (4) digital worker as an entity in the organisation.
- Layer 3 in practice: Microsoft 365 Copilot Cowork (GA since Jun 2026, Outlook + Teams + Office + SharePoint, approvals for sensitive actions).
- Foundry Agent Optimizer: baseline config + eval dataset → automatically better instructions, skills, tool descriptions, model choice.
- Foundry Observability: builds the eval dataset from production traces. Loop: runs → dataset → optimisation → better agent.

## 11 Autopilots and the agent as a team member
- Build 2026: "Today we are introducing a new category of agents called Autopilots. Autopilots are always-on agents that work autonomously, with their own identity, and act on your behalf."
- First representative: Microsoft Scout. Copilot waits for you; an Autopilot runs when you are not there. Parallel categories, not competitors.
- Microsoft Agent 365 GA since 1 May 2026: agent registry, lifecycle, access, Purview, Defender, Entra identity. An "agent user" has a mailbox, OneDrive, UPN, can be mentioned in Teams.
- Alternatives: Hermes Agent (Nous Research) - "creates skills from experience, improves them during use"; OpenClaw. Can run in Azure, connect to M365 and be managed via Agent 365.
- CAREFUL: "self-improving" today = writing to memory and editing local instructions/skills. **For now** not automatic weight changes - but the direction (RLE, tuned weights) is clear.
- For another time: coordinated collective learning across agents.

## 12 Evals must be executable
- Recommendation: formalise the definition of a good result (evals, reward functions, reward model, tests, acceptance criteria). It must be **executable**, not just written.
- Mustafa Suleyman, MAI keynote: "So with us, the RLEs and the models you build inside of them become your moat." Escalation: evals → environments → own model.
- Greg Brockman Dec 2023: "evals are surprisingly often all you need".
- Garry Tan (YC) 2025: "Evals are emerging as the real moat for AI startups".
- Anthropic Demystifying evals: their "value compounds over the lifecycle of an agent".
- What they unlock: testing models against **your** definition of quality; fine-tuning a smaller specialised model; tuning skills/context/tools against a measurable result; switching models without flying blind.
- The market is not just OpenAI vs Anthropic: xAI + SpaceX (2 Feb 2026) and Grok 4.5; Mistral (Apache 2.0); Kimi K3 above GPT-5.5 and Opus 4.8 in the Artificial Analysis index; GLM-5.2 lower overall but comparable on long-horizon coding.

## 13 Employee vs. hired consultant
- Cloud definitely yes. Returns to scale matter - not just infra, but platforms, orchestration, security, compliance, evaluation tooling, speed of new models.
- The question is not cloud/on-prem but **who gets credited with the learning**.
- Employee: experience stays in the company and gets written into your systems. From the vendor I take building blocks, the result is mine (evals, skills, tuned weights, own tenant).
- Consultant: takes the experience with them and sells it to a competitor next quarter = Reverse Information Paradox.
- Satya: company traces should train "not a generalist model, but... the company veteran agent".
- Ask of the vendor: **a real trust boundary** inside which data, traces, evals, tuned weights and memory accumulate together (where human and token capital compound).
- "In consuming intelligence, you are creating intelligence. And what you create should belong to you."
- The boundary runs between **a capability I buy** (Copilot for Excel - fine) and **a capability I raise** (Copilot Cowork, Scout or a custom Foundry solution via Agent 365).
- It is not about whether you write it yourself. It is about whether you keep what it learns.

WARNINGS
- "Self-improving" today does not mean changing model weights.
- The Claude-of-Duty score was not monotonic (4.14 → 4.05); it is Shumer's own scoring, raw data not published.
- GLM-5.2 reaches frontier level only on some tasks; Kimi K3 is more consistent.
- Multi-agent approaches cost an order of magnitude more tokens (Anthropic ~15x).

VERDICT
- Anyone who cannot measure what a good result is does not have their own AI. They have a subscription.
- Practical steps: define a good result first, then prompt and tools; verify the loop measures the result and not the form; collect evals as an asset; take Satya's test - can you swap the model and keep climbing?
