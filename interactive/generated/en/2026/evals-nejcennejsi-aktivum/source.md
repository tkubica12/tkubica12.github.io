---
format_version: 1
title: "Your company's most valuable asset in the AI world is the definition of what good looks like."
eyebrow: "Where value is moving in AI"
subtitle: "Prompting got old, the agent finds its own context, and it will write the spec for you. So what is left for you to do?"
slug: evals-nejcennejsi-aktivum
date: 2026-07-29
language: en
source_language: cs-CZ
source_slug: evals-nejcennejsi-aktivum
translation: machine
translated_from_hash: 3b97a53f4dfcd1a47a549ac8776b639b58aab0754f99b2bbf43a395adcac6fc7
translation_status: current
status: experimental
canonical_url: "/en/2026/evals-nejcennejsi-aktivum/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

# Your company's most valuable asset in the AI world is the definition of what good looks like.

When a new person joins a company, they get access, documentation, data and code. That is the easy part, it takes a day, and it still matters - without it they would not function at all. But then they sit there for another six months before they become genuinely useful. During that time they learn something nobody knows how to write down: when a given process gets bypassed and why that is fine, which customer actually means it, what it means when someone says "we'll manage that" in a meeting.

That is exactly the situation of every AI system you let into your company today. You can hand over the first part in an afternoon. The second part you cannot.

Which raises the question of how you actually recognise that person after six months. How do you know they are good now? Because until you can answer that, you cannot teach it to an AI either.

::: group id="o-co-jde" title="What this is about"

::: card number="" title="Not just data, code and models" default="open"
At Build this June, Satya Nadella said something that I think got less attention than it deserved - that **private evals may be the biggest intellectual property (IP) a company can have today**. And he added a test: you have a private eval, you are running on model A. Can you switch to model B and keep climbing? If yes, you have it under control.

Not just data. Not just code. Not just models. Not even just specifications, which have been talked about for the past year as the new corporate gold. The ability to measure that a result is good.
:::

:::

::: group id="prompt-agent" title="From prompt to agent"

First it was a science to ask the right way. Then to retrieve the right information and serve it to the model. And today we mostly tune tools and a computer for the agent - it figures out the rest itself.

::: card number="01" title="Prompt engineering and a profession that never was one" default="closed"
In the beginning it was clearly the prompt. The art of asking. A whole "profession" grew around it and there were elaborate rule sets we all passed around - phrase things positively rather than as negations, repeat the most important part at the end, give a few examples, force the model into step-by-step reasoning with "let's think step by step", separate sections, structure the input.

And back then it really worked. The difference between a good and a bad prompt was the difference between a usable and an unusable output.

The media peak came around spring 2023, when Anthropic advertised a "Prompt Engineer and Librarian" role paying [up to 335,000 dollars a year](https://www.washingtonpost.com/business/2023/02/25/prompt-engineers-techs-next-big-job/). What is interesting though is that it was never a real market - an [analysis of LinkedIn job postings](https://arxiv.org/abs/2506.00058) found only 72 prompt-engineer roles out of 20,662, roughly 0.35%. A bubble that never actually inflated. It just got written about a lot.

It would not be fair to say prompt engineering died though - it simply split in two, and the mechanical half disappeared into the model itself and its matured reasoning abilities. For reasoning models, OpenAI today explicitly recommends **"Avoid chain-of-thought prompts"** and **"Try zero shot first"** ([reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices)), because the model does the reasoning on its own and your crutch is more likely to throw it off. Anthropic, on the other hand, still says examples are **"one of the most reliable ways"** to steer a model. It is not black and white, it depends on the model family and the task.

But the content half - what I actually want - is suddenly more important than the form. And that is the whole point.

::: callout type="rule" title="Verdict"
Those techniques did not disappear because they were bad. They disappeared because the model stopped needing the crutch. We stopped worrying about **how** to ask, and started worrying about **what** we are asking for.
:::
:::

::: card number="02" title="Context engineering, picking what the model should read" default="closed"
Once the phrasing stopped mattering, attention moved up a floor. What does the model get into its context window? Which data, which texts, how to prepare them, how to chunk, how to rerank. I built a [whole RAG series](/en/2025/rag-part1/) on this topic and it really was a science.

The term went viral thanks to Tobi Lütke on 19 June 2025 with the definition **"the art of providing all the context for the task to be plausibly solvable by the LLM"** ([source](https://x.com/tobi/status/1935533422589399127)). Six days later Andrej Karpathy extended it to **"the delicate art and science of filling the context window with just the right information for the next step"** ([source](https://x.com/karpathy/status/1937902205765607626)). Anthropic then [formalised it](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) on 29 September 2025 as strategies for curating and maintaining the optimal set of tokens during inference, including the prompt, tools, MCP, history, memory and external data.

Notice the shift. We stopped tuning the question and started tuning what is in the model's field of view (context window). But we were still the ones building that field of view.
:::

::: card number="03" title="The agentic approach: I'll find the context myself, thanks" default="closed"
Around the same time came tools, and with them agentic behaviour. An agent can decide to go get something. It queries existing systems, writes its own database query, reads a file, tries again a different way. And it iterates.

That partly dissolved the careful context preparation. We no longer have to agonise over picking exactly the right five paragraphs, because the agent will find them itself.

RAG is no longer the centre of the universe, but it remains an essential way to optimise cost, latency and answer quality. Anthropic did show that their multi-agent Research system beat single-agent Claude Opus 4 on an internal eval [by 90.2%](https://www.anthropic.com/engineering/multi-agent-research-system), but it consumed roughly **fifteen times more tokens** than a normal chat. Microsoft describes its [Agentic Retrieval](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview) explicitly as something *for* RAG patterns, not as their replacement. Well-prepared context still increases reliability and lowers cost. It just is no longer a precondition for the thing working at all.

And then came the part I enjoy most - **the agent started writing notes for its own future work**. Anthropic released [Agent Skills](https://claude.com/blog/skills) on 16 October 2025 and the [memory tool](https://claude.com/blog/context-management) on 29 September 2025, and the skill format [became an open standard](https://agentskills.io/) on 18 December 2025.

When an agent struggles through three dead ends before finding the right way to query a database, it can now generalise that and store it as a skill. Procedural memory. A thinking cache. That is no longer retrieval, that is the beginning of learning. I wrote about it in more detail in the article on [software as memory](/en/2026/ai-code-context-feedback/), where my home agent wrote its own CLI and documented it for itself in a skill.

::: callout type="info" title="Where we are"
Context stopped being something I supply to the agent. It became something the agent builds - and remembers between runs.
:::
:::

:::

::: group id="radek-zamer" title="From a line to an intent"

In coding, the change of the last few years looks a bit different, but it rests on the same principles. The result is a change in the unit of work and of the assignment - and it gradually led us to the phenomenon of spec-driven development.

::: card number="04" title="How the unit of assignment grew" default="closed"
The unit of work in software has shifted over three years so much that it is barely comparable. I wrote about it in more detail in a [separate article](/en/2026/agenti-token-kapital-build-2026/), so here is just the short version:

::: sequence title="The chunk of work I can hand over"
1. **A line** — finish this for loop for me. Autocomplete guessing the next line.
2. **A function** — write a whole function from a comment or a signature. And soon after, a change across ten files.
3. **A task** — a coding agent. It assembles it, runs it, tests it, sees the error and fixes it.
:::

The key thing is that **the work did not shrink, the "how" did**. On the first rung I had to know exactly what belonged on the next line. On the third I only needed to know what should be finished at the end.

On that third rung, **feedback** appeared for the first time. The agent runs the tests, sees red, and goes to fix it. That is the seed of the entire rest of this article - we will just move one layer of loops up.
:::

::: card number="05" title="Spec-driven development: I tell the agent exactly what to do" default="closed"
When the unit of assignment grew into a "task", a new problem appeared. The agent now works for an hour without my supervision. The chat where I told it what to do is unreliable, it gets forgotten, nobody reads it a second time. I needed a durable artefact.

That is how spec-driven development came about. AWS introduced [Kiro](https://kiro.dev/blog/introducing-kiro/) on 14 July 2025, GitHub released [Spec Kit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/) on 2 September 2025 with the Specify → Plan → Tasks → Implement cycle. The specification as a living source of truth.

I want to stress that this is not a fad but a good engineering idea, for three reasons:

::: steps title="Why spec-driven makes sense"
1. **Code stopped being an input** — it became an output artefact. I can throw it away and have it regenerated. The specification is then the only thing I truly own.
2. **It is readable by humans and machines alike** — unlike code, a specification is understandable to sales, lawyers or compliance.
3. **And most importantly: it is testable** — you can verify afterwards that the agent wrote it the way we wanted.
:::

That third point is the important one and it is rarely discussed. Spec-driven brought an **independent checker** into the story. One agent writes code from the specification, another agent or a human independently verifies that it was followed. That is an incredibly useful property, it is an audit artefact, and I do not want to lose it in the future either.

Except. And here is the crack that made me write this article in the first place.

::: callout type="warning" title="The crack"
A specification describes **how to do something**. It does not say how I will recognise that the result is good.
:::
:::

:::

::: group id="smycka" title="Closing loops in coding"

Up to here it was about how to hand work to an agent well. Now comes the turn: the most interesting things started happening the moment we stopped assigning and started building a loop that evaluates the result itself.

::: card number="06" title="Keep going until it is as good as Call of Duty" default="closed"
On 25 July 2026 Matt Shumer published a [post](https://x.com/mattshumer_/status/2081054356405731740) saying "Claude Opus 5 one-shotted this game" along with a demo of a first-person shooter. The internet lost its mind. Two days later he described the methodology under the name [Gauntlet Loop](https://somethingbig.ai/gauntlet-loop).

The prompt is worth reading in full, because it is a nicely clean essence of the approach.

::: reveal title="The full text of Shumer's prompt"
```text label="mshumer/Claude-of-Duty - prompt.md"
I want you to build a first-person shooter at the level of the most recent
Call of Duty games. It should be utterly perfect, visually beautiful, with
every single thing done at AAA quality—from textures to physics to anything
you could think of.

Fan out sub-agents and have sub-agents tackle each one individually so that
the game is utterly perfect. You should /loop on each item and have a separate
sub-agent check it visually to ensure it looks triple A. That separate
sub-agent should be a really harsh critic, and if it doesn't look triple A,
it should keep going.

Don't stop until each sub-agent is utterly wowed with the quality when compared
with the actual Call of Duty game. It should literally compare them side by
side blind and say which one looks better. Do this in ThreeJS. /loop until it's
utterly perfect. Fan out sub-agents and ultracode.
```
:::

The point is not the game assignment. The point is that it does not say **how** to do it at all. It says **how you recognise it is done**: a separate subagent, a merciless critic, a blind side-by-side comparison with the real game, and the loop keeps running until the critic says enough.

Shumer clarified two days later: *"I gave Claude Code one prompt, then left it alone. It spent many hours working, spawned a massive fleet of subagents, wrote roughly 55,000 lines of code... I did not sit there steering it, at all."* One prompt, no follow-up questions, many hours of autonomous work and roughly 55,000 lines of code.

On top of that, the critic did not have its reference point only in the model's memory. Shumer described it literally: *"For the game, I used actual Call of Duty screenshots. The critic was supposed to look at the two side by side, decide which was better, and keep going whenever ours lost."*

Technically it worked like this: Playwright ran the game under construction in headless Chromium, captured eleven predefined views in full HD - environment, lighting, materials, weapon in hand, aiming, impacts, HUD - and those then went to the critic against real Call of Duty frames. Blind, so it did not know which image was whose.

::: callout type="rule" title="The key moment"
That loop did not work only because it was cleverly written. It worked because it had a ready-made, public, shared definition of what good looks like - literally in the form of images anyone can download.
:::
:::

::: card number="07" title="Your company is not Call of Duty" default="closed"
If you open [his repository](https://github.com/mshumer/Claude-of-Duty), you will find something that never made it into the viral posts:

> **"The goal was to match a modern Call of Duty. It does not."**

Over those loops the score moved from 3.59 through 4.14 and 4.05 to a final 5.05 out of ten - note that one round was actually worse than the previous one. Two of the eleven views reached a "CLOSE" rating, the rest stayed at "AMATEUR". And in **every** blind A/B comparison the real Call of Duty won.

The loop did exactly what it was built for. It honestly measured that it had not reached the goal, and said so out loud. That is far more valuable than a polished demo with no number - because from a number you can continue.

And here is the unpleasant news for you.

::: callout type="warning" title="The essential finding"
Your reference point does not exist anywhere. There is no folder of frames a critic could put next to your process and say "this is where it falls short". And if a model knows your company perfectly, you have a much bigger problem than slow AI adoption - you are a commodity heading for zero margin. Put differently: if you are an interesting company, the model does **not** know the vast majority of what makes you you.
:::

Which means the part Shumer got for free, you have to manufacture yourself. And that is the hardest work in the whole chain.
:::

::: card number="08" title="Loop engineering and 70 USD in the bin" default="closed"
That shift from assigning work to designing loops got a name in June 2026 too. On 7 June, [Addy Osmani](https://addyosmani.com/blog/loop-engineering/) defined it as **"replacing yourself as the person who prompts the agent. You design the system that does it instead."** Peter Steinberger, the author of [OpenClaw](https://github.com/openclaw/openclaw), said the same thing differently on the same day: **"You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents."**

Here is how I translate it for myself. I stopped talking to the agent and started talking to a **foreman**. I do not tell him how and what to program. I tell him what I want to achieve. The foreman chops it into subtasks, writes the specifications himself, hands work to other agents and then whips them until the result matches the intent. I do not touch it in the meantime.

Sounds great. So I built myself such a loop.

The goal was a one-day workshop on Microsoft Foundry - a combination of a short presentation, demos and short hands-on labs for participants. I had an agenda, I had a plan. I created an ecosystem of subagents entirely in Matt's spirit: one looked at it through the eyes of an educator, another through the eyes of a student, a third through the eyes of a designer, a fourth through the eyes of an engineer. And they worked hard on it.

Seventy dollars later they presented the result. Perfectly polished materials. Beautiful, detailed, factually completely correct, pedagogically excellently structured.

**There was no Azure in it.**

I wanted real demos and real labs where a participant touches a real resource. They took it as a theoretical exercise where the practical part consisted of interactive forms in which an AI architecture was elegantly assembled. Excellent. But not what I wanted. The whole thing went in the bin.

The mistake was mine, of course. My loop checked topics, structure, visuals and pedagogical flow. It never touched a real resource in Azure. **I whipped the model to perfection in a discipline that was not the essential one for the result.** The model has no internal idea of what the result is, it is not Call of Duty - and my definition of a good result was poorly prepared.

::: callout type="rule" title="Verdict"
Loop engineering does not move the hard work away. It only moves it elsewhere. Instead of "tell me what it should look like", the question is "tell me how you will know it is good". And that is a much harder question, because most companies do not have an answer even for their own people.
:::
:::

:::

::: group id="firma" title="Hill-climbing and enterprise loops"

So far we have been in code, where the result can be run and tested. Now let us try the same thing in a company, where most of the work cannot be run at all - and yet you still have to be able to tell whether it is good.

::: card number="09" title="We know more than we can tell" default="closed"
Imagine you want to move these principles into human work in a company full of unique knowledge. Often unspoken. Often working differently than it is written down - and working well and flexibly, because the company simply functions.

It helps me to look at it through three layers:

::: steps title="What makes your company your company"
1. **Explicit knowledge** — data. Documents, databases, numbers, documentation. Everyone knows this one and for twenty years it has been labelled corporate gold.
2. **Institutional and procedural knowledge** — procedures, processes, rules. Often set in concrete in application code, often never written down in full.
3. **Tacit knowledge** — what employees carry in their heads. What a new person has to gather over those six months, because nobody knows how to write it down for them.
:::

Michael Polanyi summed it up in 1966 in a sentence nobody has beaten: **"we can know more than we can tell."**

I am not claiming the first layer is worthless, that would be silly - nothing works without data. My point is different: **it is the only layer you can hand over in an afternoon.** And what you hand over can be copied.

If you give your data to a model vendor to train on, that is an advantage more for them than for you. And if you also let them listen to human interactions and store them for analysis, the unspoken part can leak too. Having data in the cloud is not the problem, giving up control over it is. I want to use my company's uniqueness in the cloud to get tailored AI - but I want to own the result.

I do not see this as a problem right now. I am slightly worried, though, about a time when some vendors will own that result *for* you in the interest of "safety". And a year later your uniqueness will happen to be on offer "as a service" for everyone.

Satya Nadella gave this a name in a [text from 12 July 2026](https://x.com/satyanadella/article/2076323181154230284): the **Reverse Information Paradox**. The economist Kenneth Arrow once described how a buyer does not know the value of information until you reveal it - but once you reveal it, they have it for free. According to Nadella, AI flipped that problem around: now it is the **buyer** who has to reveal their know-how for that intelligence to be useful at all. So you pay twice. Once with money, and again with knowledge. And the better a result you want, the more of that knowledge you have to give.

> **"Models learn from exhaust, the prompts people write, the tools agents use, and especially the corrections people make when the model is wrong. Every correction is distilled into institutional know-how. It's the kind of knowledge a competitor could never buy, and the kind that leaks almost imperceptibly: trace by trace, correction by correction, eval by eval."**

Notice how that ends. Trace by trace, correction by correction, **eval by eval**.

::: callout type="rule" title="Verdict"
What is universal will end up in the model. What is yours, you have to know how to keep - and that goes for all three layers, data included.
:::
:::

::: card number="10" title="The hill-climbing machine and learning on the job" default="closed"
Once we know the loop is what matters, and we know that for company matters we have no ready-made definition of success, where next? For me the answer is continuous learning, or rather on-the-job learning. Experience gathered while actually doing the work and interacting with others is irreplaceable for the vast majority of economically important activities. If AI is really to multiply people's abilities, it has to learn from unclear signals too.

Microsoft has a nice name for this. In the announcement of the new MAI models on 2 June 2026, the team writes that the goal is to build **"what we think of as a hill-climbing machine: an organization that can continuously improve, cycle after cycle"** ([source](https://microsoft.ai/news/building-a-hillclimbing-machine-launching-seven-new-mai-models/)).

Thinking Machines Lab describes it from the other end: **"Most AI in use today is trained in a handful of places and then frozen"** ([manifesto from 10 July 2026](https://thinkingmachines.ai/blog/the-future-worth-building-is-human/)). Their [Inkling](https://thinkingmachines.ai/news/introducing-inkling/) from 15 July 2026 is particularly nice for my argument - it is a demonstration of a model that prepares its own evals, gathers data and fine-tunes itself through Tinker. A controlled experiment, not magic, but the direction is clear.

Where are we really today? For me, in four overlapping layers:

::: sequence title="Four layers of today's adoption"
1. **A chat helper** — I ask, I get answers. The most widespread and the least interesting.
2. **Auditable automation workflow** — invoice processing and similar processes. Deterministic guardrails, a clear output.
3. **A personal worker with real-world impact** — it reaches into the calendar, creates something, emails it, waits for replies, gathers data, analyses it and files a lead in CRM or adds a note from a meeting transcript.
4. **A digital worker** — no longer my tool but an entity in the organisation. It has its own mailbox, it is on Teams, it has assigned access rights and it learns from how its work turned out.
:::

The third layer is the most interesting one in practice today, because you can **raise** such a worker. It changes its own skills and learns from you. Practically this works through, for example, [Microsoft 365 Copilot Cowork](https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/), which has been GA since June 2026 and works across Outlook, Teams, Office and SharePoint with approvals for sensitive actions.

The fourth layer is the reason I am writing this article, and I am giving it a whole chapter of its own.

An interesting piece of the puzzle sits in Foundry, though. [Agent Optimizer](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview) takes a baseline agent configuration and an eval dataset and automatically improves its instructions, skill content, tool descriptions and even the model choice. And [Observability](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset) can build that eval dataset from production traces. Together it is a loop: real runs → dataset → optimisation → better agent.
:::

::: card number="11" title="Autopilots and the agent as a team member" default="closed"
For an agent to learn from work, it has to be part of it. Not a tool I open, but a colleague who receives things.

At Build 2026 Microsoft introduced a new product category for this, quite explicitly: **"Today we are introducing a new category of agents called Autopilots. Autopilots are always-on agents that work autonomously, with their own identity, and act on your behalf."** ([announcement](https://www.microsoft.com/en-us/microsoft-365/blog/2026/06/02/introducing-microsoft-scout-your-always-on-personal-agent/)). The first representative is [Microsoft Scout](https://learn.microsoft.com/en-us/microsoft-scout/overview). Copilot sits next to you and waits for you to speak. An Autopilot runs even when you are not there. They are not competitors, they are parallel categories - but the direction seems unambiguous to me.

It becomes usable for a company only with management. [Microsoft Agent 365](https://learn.microsoft.com/en-us/microsoft-agent-365/overview) has been GA since 1 May 2026 as an enterprise control plane: an agent registry, lifecycle, access rights, Purview, Defender, identity in Entra. A licensed "agent user" has its own mailbox, OneDrive, UPN and can be mentioned in Teams.

That it does not have to be only Microsoft is hopefully obvious - [Hermes Agent](https://github.com/NousResearch/hermes-agent) from Nous Research describes itself as an agent that *"creates skills from experience, improves them during use"*, and I run [OpenClaw](https://github.com/openclaw/openclaw) at home. And it is not either-or: these systems can run in Azure, connect to Microsoft 365 and be managed through Agent 365 just like Scout.

::: callout type="warning" title="Careful with the word self-improving"
For all these systems today, "self-improving" means writing to memory and editing local instructions or skills. **For now** it does not mean automatically changing model weights - but the direction Microsoft and others are taking is clear: not just skill optimisation, but reinforcement learning environments and tuned weights too.
:::

::: callout type="info" title="For another time"
The next step is coordinated collective learning across agents - one learns something and the others receive it. That is a topic for a separate article.
:::
:::

::: card number="12" title="You have to be able to run your definition of a good result" default="closed"
Here is my main recommendation. A company should systematically build and formalise the definition of what a good result is. Evaluations, reward functions, a reward model, tests, acceptance criteria, user stories - call it whatever you like. What matters is that it has to be **executable**, not just written down.

Fortunately I am not alone in this. Besides the quoted Satya line about private evals as the biggest IP ([full interview](https://www.latent.space/p/satya-2026)), Mustafa Suleyman said something on the MAI keynote that pushes the idea further: **"So with us, the RLEs and the models you build inside of them become your moat."** ([transcript](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/)). Meaning the moat is made of reinforcement learning environments and the models you train inside them. That is a nice escalation - evals are the first step, environments the second, your own model the third.

Outside Microsoft it sounds the same. Greg Brockman wrote back in December 2023 that **"evals are surprisingly often all you need"** ([source](https://x.com/gdb/status/1733553161884127435)), Garry Tan of Y Combinator said in 2025 that **"Evals are emerging as the real moat for AI startups"** ([source](https://x.com/garrytan/status/1892952656940880036)) and Anthropic points out in [Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) that their *"value compounds over the lifecycle of an agent"*.

What good evals unlock:

::: arrow-list title="What you get when you can measure quality"
- You can test models from different vendors and open source against **your** definition of quality, not against someone else's benchmark.
- You can fine-tune a smaller specialised model for a specific company role.
- You can tune skills, context and tools against a measurable result instead of a gut feeling.
- You gain the ability to **switch** solutions and models without flying blind.
:::

That last item is the most underrated one in my view, and it is what Satya's model A versus B test is aiming at. The environment changes technologically, politically and strategically, and it will not be just OpenAI versus Anthropic. xAI [merged with SpaceX on 2 February 2026](https://x.ai/news/xai-joins-spacex) and released [Grok 4.5](https://x.ai/news/grok-4-5). In Europe there is Mistral with open models under Apache 2.0. And open source is genuinely good today - [Kimi K3](https://www.kimi.com/blog/kimi-k3) sits above both GPT-5.5 and Claude Opus 4.8 in the independent [Artificial Analysis index](https://artificialanalysis.ai/models/kimi-k3), that is above models that were world-class just two months ago. [GLM-5.2](https://z.ai/blog/glm-5.2) is a fair bit lower overall, but on long-horizon coding tasks it measures up to that class too. Whether that holds for *your* task, you will find out only with your own evals.
:::

::: card number="13" title="I want an employee, not hired consultants" default="closed"
This is not about whether cloud yes or no. Cloud definitely yes. Returns to scale are absolutely essential in this game and they do not concern only infrastructure - they concern mainly platforms, orchestration, security and compliance systems, evaluation tooling and the speed at which new models arrive. You will not build this at home and I do not think it makes sense to try.

It is about something else: **who gets credited with the learning.**

::: tabs id="dva-modely"
::: tab id="zamestnanec" title="An employee (want)"
An employee learns at your company for six months and that experience stays in the company. They know when a given process gets bypassed. They know your customers. And when they write that knowledge down, they write it into your systems.

That is what I want from AI. From the vendor I take building blocks - flexible model choice, an isolated environment, encrypted storage, evaluation tooling, agent identity management and lifecycle control. On top of that I build my own AI, whether it is Scout, Copilot Cowork, Hermes, or a custom solution in Foundry managed through Agent 365.

My evals, my skills, my possibly fine-tuned weights. All in my tenant, isolated, encrypted. If I decide to switch models or leave, I take it with me.
:::

::: tab id="konzultant" title="A hired consultant (do not want)"
A consultant arrives, solves the problem and shows results immediately. But the most valuable thing they take away is the experience with your environment - and they take it away **to themselves**. Next quarter they will sell it to someone else. In your industry. Possibly directly to your competitor.

Translated into AI: I hand someone what is unique to me, and they "add it to the model". But then they use that model elsewhere too.

It would work great - for the first year. Then my uniqueness would become part of a general capability that my competitors have too. I would effectively be paying for someone to drain away the reason for my existence. That is exactly what Satya calls the Reverse Information Paradox.
:::
:::

Satya named it precisely this way - company traces from real work should train *"not a generalist model, but... the company veteran agent"*. And from that follows what to demand from a vendor: **a real trust boundary**, inside which your data, traces, evals, tuned weights and memory accumulate and improve together. He talks about it as the place where human and token capital compound - and I wrote about [token capital separately](/en/2026/agenti-token-kapital-build-2026/). He summed it up in one sentence I would put on my wall:

> **"In consuming intelligence, you are creating intelligence. And what you create should belong to you."**

That boundary does not run between cloud and on-prem. It runs between **a capability I buy** and **a capability I raise**.

The first one is perfectly fine and I will keep doing it - when I want a Copilot that understands Excel, I do not want to teach it Excel. The second one is a worker you give company tools to, let loose on real work, and teach. It can perfectly well be from Microsoft too: Copilot Cowork, Scout, or a hand-built solution in Foundry connected to Microsoft 365 and managed through Agent 365. It is not about whether you write it yourself. It is about whether you keep what it learns.
:::

:::

::: group id="zavery" title="Conclusions"

::: detail-grid title="Three things to take away" hint="Click a card for detail"
::: detail-card title="Value is moving toward measurement" summary="AI will write the prompt, the context and the spec for you today. Not the definition of success."
Every stop along that road was briefly the most important thing and then soaked into the model or into the tools. Prompt engineering dissolved into model capabilities. Context engineering was largely taken over by agentic behaviour. A spec will be written for you by an agent today if you describe the intent.

What does not soak away is the definition of what a good result is. It cannot be derived from public data, because it is specific to you.
:::

::: detail-card title="The model knows general things, not your company" summary="A critic can run Call of Duty side by side. Not your process."
Shumer's loop worked mainly because it had a perfect reference point for free. Your company is not like that and should not be - if a model knows your procedures perfectly, you are a commodity heading for zero margin.

So the fact that the model does not know your procedural and tacit knowledge is not a problem to be solved. It is your competitive advantage, which you have to be able to turn into measurable form without giving it away.
:::

::: detail-card title="No hill-climbing without evals" summary="Just a random walk that looks like progress."
The next phase of adoption is not a better chatbot but a digital worker that learns from how its work turned out. First tuning skills and context, later environments and tuned models for specific company roles.

Both need the same thing: a signal you can climb the hill by. And you have to manufacture that signal yourself - and keep it.
:::
:::

::: arrow-list title="What to do about it in practice"
- For every AI use case, first write down how you will know the result is good. Only then deal with the prompt and the tools.
- Check whether your loop measures the **result**, not just the form. Mine did not and it cost me seventy dollars.
- Collect evals as a company asset, not as a by-product of a project. Their value grows over time.
- Take Satya's test: can you swap the model and keep climbing? If not, you are not the one in control.
:::

:::

::: closing
Anyone who cannot measure what a good result is does not have **their own AI**. They have a subscription.
:::
