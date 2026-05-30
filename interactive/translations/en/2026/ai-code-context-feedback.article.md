---
format_version: 1
title: "AI coding - context vs. measurement, software as memory, I will not learn your software, OpenClaw and the smart home"
eyebrow: "A home experiment with AI agents"
subtitle: "A home project with Home Assistant, Copilot CLI, and OpenClaw as a practical lab for thinking about context, feedback, software as memory, and GenUI."
slug: ai-code-context-feedback
date: 2026-03-30
language: en
source_language: cs-CZ
source_slug: ai-code-context-feedback
translation: machine
translated_from_hash: eaf693ad7dd1efdcccd5f29bab1c75352c6088dd1277d44ed636934c0c78c601
translation_status: current
status: experimental
canonical_url: "/en/2026/ai-code-context-feedback/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

# AI coding - context vs. measurement, software as memory, I will not learn your software, OpenClaw and the smart home

I started a home experiment that ultimately leads to having an AI agent at its core. Along the way I noticed that I keep thinking through the following concepts, and that this kind of experience is really important:
- What matters more - context or feedback?
- How, already today, does an agent actually improve itself by incorporating my feedback?
- Does an agent for coding make sense, or is it simply an agent?
- In what way is agentic UX better than a graphical UI, and does it replace it?

The point is that my smart home is controlled through Home Assistant, which is connected to ZigBee components, while some devices are WiFi and some are large appliances available only through the cloud, and all of that gets controlled and automated there. The goal was to try to replace ready-made software, where I constantly have to learn how to do things, with a custom solution using AI coding, so that when I want the software changed I can simply "say it". But then came the second phase - automation and the web are fine, but it would be good to add an agentic interface (for example, "close all blinds except the study"). At that point, though, I realized I was thinking about it backwards - I do not want an agent that can "click" in software (that was last year's thing), but an agent that, among other things, manages and creates software. I am now in phase 3 and exploring what the right UI/UX should look like - I clearly want full GenUI and a multimodal solution, but for now I am running into the limits of the channels I use (for example, WhatsApp only through the Business Platform, and even there it is just buttons, not full mini-apps).

Before I dive into more detail, so your agents do not have to read the whole thing, here are the main ideas:

::: summary-grid
- **Software and skill are memory**: It is an energy and performance optimization that leads to a better chance of surviving in the future. Muscle memory and the ability to read the game, created by training.
- **A low-level API connects the agent to the real world**: It does not need to be complex or have abstractions. The agent implements those itself as a CLI/skill, or then offers them further to colleagues through A2A.
- **Context vs. feedback**: Context is essential, but the main breakthrough comes from closing the feedback loop, which in the end also leads to creating context. If something can be measured well, it is better to invest 80% of the effort into measurement and only 20% into context (especially in the form of constitution and concepts). If something is hard to judge, you need to invest 80% of the effort into context.
- **Users will not learn to use your software**: This has to be the other way around.
:::

::: group id="evoluce" title="Evolution of my home project"

I will try to describe how I proceeded, and I warmly recommend trying something like this - it is fun.

::: sequence title="Three phases of the home experiment"
1. **Custom software** — replace parts of Home Assistant with a tailored solution that I can change through AI coding.
2. **The agent manages software** — do not just add chat on top of the web; give the agent a low-level API, CLI, skill, and the ability to improve its own capabilities.
3. **GenUI instead of a fixed web app** — explore when chat is enough, when visual output is needed, and when the UI should adapt to the user.
:::

::: card number="01" title="Phase 1 - Why should I learn someone else's software when having my own is simpler?" default="open"
Home Assistant is an excellent piece of software, but I never really managed to make things work in it exactly the way I wanted. For example, automations there are powerful, but you need to know them, understand all the parameters that devices use, and learn their YAML language properly, and even then it is not quite it. For example - when I go out onto the terrace, I need to raise the left blinds, and when I then send them back down with the button, they lower with the slats in full-shade position. I needed two things - first, after they come down, set their tilt the same way as on the right side, and also perhaps not lower them all the way from the top, so instead of dumb timing by seconds (you must not send the slat-tilt command while they are moving down, otherwise they stop), watch what position they are in, and when they reach the bottom, tilt them immediately. I did not find a solution in YAML, even though it is obvious that this is not a complicated algorithm and that vibe-coding something like this cannot be a problem.

So I took GitHub Copilot CLI and started a project where 3-5 agents always ran simultaneously, and for a few days I jumped between windows (this time the ones on the computer) and directed them. I described an architecture where I have individual microservices for different device types (one for blinds, using the local API of the TaHoma box; another for switches and lights on ZigBee; another for ZigBee sensors; another for appliances on WiFi such as the washing machine, dryer, or kitchen appliances), then an automation service, a gateway (de facto backend-for-frontend with added authentication), and a web app. Copilot ran on my computer and got SSH access to the original minicomputer (Orange Pi Zero 2) and also to the new one (Orange Pi Zero 3 - 2GB of memory) - it looked into the old one to steal configurations and device names from Home Assistant files, created microservices, debugged them in a short loop over SSH, made a GitHub Actions workflow with publishing to a container registry, launched final versions in Docker Compose on the device, and so on. For example, it managed to discover that TaHoma Switch also supports a local API, which I did not know. In Home Assistant I had used their cloud integration; here we found out that I can control the blinds locally. Copilot scanned my network, searched for and recognized devices, read documentation, and overall the development was great fun.

The resulting solution is architecturally more readable for me, and I achieved what I needed - in some areas it is better, somewhere maybe not yet, but the main thing is something else. I am not alone in it. I describe what I want and how, I can experiment, I do not have to study manuals and suffer through it. And most importantly - most of what I configured in Home Assistant I later forgot and had to go back and look up how it actually worked when I added something new or needed a change. This software and all of its configuration is available through GitHub Copilot CLI - I definitely would not want it any other way. Or maybe, in the end, yes?
:::

::: card number="02" title="Phase 2 - Why only add an agent into software when it can be the other way around?" default="open"
At this point I had a web app with login and everyone was happy, but not everyone in the family was willing to connect to the web. It was clear that some agentic interface would make sense - so it could be said through WhatsApp or something like that, basically classic home control à la Google Home, but with a modern LLM that really understands what is being solved and without a proprietary solution. Does it make sense or not? We add an agent into the software, actually more of a chatbot and/or voicebot.

But here I quickly started to realize we would have a meta-problem. I probably do not want only classic intent extraction and turning on a light; I would like to solve more complex things, for example:
- Tomorrow morning I have to get up at 6:00 this time, so open the bedroom blinds just a little at 5:58 and fully at 6:00
- Today we will go to bed earlier, stop heating already at 19:00 and close all blinds at 21:00
- I am going to get herbs, raise the blinds for one minute

All of this would have to be prepared for - I would have to think through these use cases and hard-wire specific mechanisms. But the agentic approach is about AI understanding what I want and finding a way to do it. The agent will not necessarily be limited by the current state of the software in terms of UI or automation; through a low-level API it can add whatever will be needed. So I do not want a chat thing on top of the web, but a real agent.

At that moment it became clear what I wanted to get onto the device - **[OpenClaw](https://github.com/openclaw/openclaw)**. In my setup, it is a locally running agent that can use tools, keep memory, and continuously extend its own capabilities with skills and scripts. Thanks to it, tasks like these are achievable, and above all OpenClaw can modify itself. For example - in my architecture there are microservices with their own API and a gateway (BFF) that aggregates them and adds things like security or an MCP variant. The web pulls on this, and the original plan was for the agent to use MCP. But the agent now runs directly on site and rather naturally tended to jump straight into the REST API, making mistakes there.

How did it turn out? We agreed that, because everything is local, the ideal thing would be for OpenClaw to write itself a CLI and document it in a skill. We created smarthomectl, which is much easier for the LLM to use than trying to assemble JSON objects and figure out how to escape them correctly when running commands. A simple CLI and nice switches. However, the CLI is gradually adding abstraction based on experience!

Example: groups of blinds, such as turning all blinds in the morning except two in the room where a child is still sleeping. Instead of calling the API one by one, OpenClaw, by agreement, created the option in the CLI to enter things like --include and --exclude and then also --blinders-group. So because this is a frequent thing, we agreed it makes sense to add it - essentially optimizing the solution (speeding up and simplifying common scenarios and increasing their reliability).

::: callout type="rule" title="Architecture"
So the architecture is - a low-level API connects the agent (the digital world) with the physical world. The agent maintains its own CLI ("muscle memory") and skill (context, dexterity), through which it creates "higher logic". On top of that it has memory. This is what people mean when they claim software collapses into agents - the basic components of the solution are APIs for interaction with the world, code and skill (the agent's apprenticeship certificate and the ability to develop it further), and data persistence (memory, some database, and so on).
:::
:::

::: card number="03" title="Phase 3 - Why should I have a web interface when I can have GenUI?" default="open"
The web is fine - clear for me, tailored to my needs, but perhaps not for the other members of the household. Maybe they have a different idea of what should be there and how it should be arranged. And besides - where should the agent live, as chat on the web? Connecting OpenClaw through WhatsApp is great - nobody has to install anything, everyone stays in their workflow, a specialized group for controlling the home is created, and it works. WhatsApp is robust, a message can easily be written by voice, and it works quite securely from anywhere even with poor signal. So the question is - do I still need the web at all? It is clearer in the sense that I have controls on one page, and if I need to do several actions at once, it is fast. But if the agent is already smart today and understands commands like "turn on the lamp and the counter" (meaning it realizes there is only one kitchen counter, so by lamp I probably mean the one in the living room, and I want both turned on at once), then it is also comfortable through the agent. The only thing that bothers me is the long thinking time. I still need to try smaller, faster models, but at the same time I would not want the model to become stupid the moment it needs to do something more complex or answer research and more demanding questions at the Copilot level (which it of course does very well). A prompt such as "if it is not going to rain tomorrow, let's run watering for x liters tonight" already requires looking up information on the Internet and deciding based on the result, so through a pure web UI this kind of control starts to be unnecessarily clumsy.

What I would need is GenUI, but in the consumer world I have not yet managed to find a suitable option. [WhatsApp Flows](https://developers.facebook.com/docs/whatsapp/flows/) can do structured multi-step forms and lightweight UI, but they still are not full-fledged mini-apps. [Telegram Mini Apps](https://core.telegram.org/bots/webapps) are very capable from a UI perspective, but Telegram keeps end-to-end encryption only for Secret Chats. Signal does not support rich UI. [Discord](https://support.discord.com/hc/en-us/articles/25968222946071-End-to-End-Encryption-for-Audio-and-Video) already has E2E for audio and video, but not for text messages. So in the future I will try three paths and see what works best:

::: arrow-list title="Three paths"
- Web (I already have that and it works well)
- WhatsApp (works great, I have execution in a sandbox, and it is ideal for non-admin use)
- My own chat/voicechat UI through the web with mini-app support (that is what I am going to try right now)
:::

I do not have the result yet, and I will definitely come back to this - in any case I think especially the combination of voice on input and a mini-app GenUI screen on output will often be ideal and literally "made for" some later glasses with a display.
:::

:::

::: group id="zavery" title="Conclusions"

::: detail-grid title="Four conclusions" hint="Click a card for detail"
::: detail-card title="Software is memory, optimization" summary="A script, CLI, or MCP server is a way for an agent to store a trained procedure."
If the agent is smart enough, has access to all necessary low-level APIs and data, has the required tools available (Internet, databases, and so on), and has context (or can obtain it effectively, for example from a knowledge base), it can handle practically anything. But it may have a hard time - it will make lots of mistakes, load a large amount of content, maybe need help and feedback, and consume a pile of tokens and time. Something like when you do that thing for the first time. Next time, though, you can train it - you gain muscle memory for the activity, your movements and thought processes become encoded and optimized, and at the same time learning gave you a lot of context: what it is good for, why you do it, how it works. An agent can do this too!
- **Software**, for example a written script or a new function in a CLI or another MCP server, is a way for the agent to store a procedure, business logic, in a way that is repeatable, predictable, modifiable and extensible, and testable - meaning trainable. Just like your tennis serve.
- Context, for example a **skill** or another way to influence what gets to the model (such as an MCP server with memory), records how to do it, what it is good for, and how it works. Just like your ability to "read the game".
:::

::: detail-card title="API into the world, data, abstraction as skill" summary="Low-level APIs do not bother the agent; it can store its own abstractions in a CLI or skill."
An agent is able to handle the complexity of a low-level API into the world, and unlike a human, it is more comfortable with those than with abstractions. We create modules in Terraform because we are not able to handle detail well, and abstracted objects fit wonderfully into our heads because they fit into the broad context we keep. LLMs have it more or less the other way around. Rather than forcing our idea of abstractions on them, we will probably do better by giving them low-level APIs and access to data.

The agent may find its own abstractions, but those will again be about optimization - a skill, added things in a CLI, or new MCP functions become notes on how to perform some "higher-level" user requests faster and more reliably.
:::

::: detail-card title="Context vs. feedback" summary="When the result can be measured, the loop decides; when the agent does not know what it is doing, context decides."
The tenacity of agents is amazing - if they have the ability to measure the result, they will make incredible progress in order to succeed. I am convinced that if you have an e-shop, an agent will very soon (if not already now) be able to take over tuning the whole application with profit maximization in mind. It will be able to work with customer behavior, with what and how they order, and it will come up with all kinds of ideas that it will immediately A/B test and measure. In such a feedback loop, the agent is capable of achieving fascinating results, and in addition, while doing so it will continuously build new context - which hypotheses are confirmed, and so on. Once the e-shop is established and running, I think feedback is 80% of success.

But there are situations where this loop cannot be fully closed because the agent does not know what it is doing. At that moment, context is absolutely essential - what it should do, how it works, understanding the business domain, and so on. It is of course important to also have feedback in the form of some tests and measurable outputs, but at this point context will be 80% of success.

For me, then, I try to build the best possible context so I can get as quickly as possible into a state where it will be more or less only about feedback; at that moment I am more of a nuisance to the agent, and I want it to work on it by itself.
:::

::: detail-card title="Learning from the user and GenUI" summary="The user will not learn the software; the software and agent must learn the user."
An agent has a great ability to understand what the user wants even when everyone says it a bit differently. If the agent is not sure, it asks; the user clarifies; the agent remembers. The agent learns to understand the user, not the user having to learn how to control your solution. This is powerful, and people will demand it.

But a chat interface will not be efficient enough for some scenarios, and its combination with visuals will be important; yet the more you work with agents, the less you like trying to understand how the UI is supposed to work. The graphical interface will have to be able to adapt automatically to the user, just like the text one. It is of course more complicated, but GenUI must become the standard.
:::

:::

::: closing
Users will not learn to use your software. **The software and the agent** will learn to understand the user.
:::

:::
