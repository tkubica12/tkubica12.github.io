# AI coding - context vs. measurement, software as memory, I will not learn your software, OpenClaw and the smart home

Source: `interactive\translations\en\2026\ai-code-context-feedback.article.md`
Canonical: `/en/2026/ai-code-context-feedback/`
Translated from Czech source hash: `eaf693ad7dd1efdcccd5f29bab1c75352c6088dd1277d44ed636934c0c78c601`

## Core thesis

Home Assistant smart-home experiment became a practical AI-agent lab. Main claim: users will not learn software; software and agents must learn users. Software, CLI scripts, MCP servers, skills, and memory become trained procedures for agents. Low-level APIs connect agents to the physical world; agents can build abstractions themselves.

## Main ideas

- **Software and skill are memory**: reusable code, CLI commands, MCP servers, and skills store trained procedures, like muscle memory plus ability to "read the game".
- **Low-level APIs are enough**: agent can handle low-level API detail and create higher abstractions as CLI flags, skills, or A2A offerings.
- **Context vs. feedback**:
  - If outcome is measurable, invest roughly 80% effort into measurement/feedback and 20% into context.
  - If judgment is hard or the agent does not know the domain, invest roughly 80% into context.
  - Closed feedback loops also create new context over time.
- **User-learning reversal**: user should not learn your software; software and agent should learn the user.

## Evolution of the home project

### Phase 1 - custom software instead of learning another tool

Home Assistant works well, but configuring exact behavior was hard. Example: terrace blinds needed to raise left blinds, then when lowered by button, set slat tilt like the right side and avoid dumb timing; YAML solution was not found, though the algorithm is simple.

Implementation used GitHub Copilot CLI with 3-5 agents running simultaneously. Architecture:

- microservice for blinds using local TaHoma API,
- microservice for ZigBee switches/lights,
- microservice for ZigBee sensors,
- microservice for WiFi appliances such as washing machine, dryer, kitchen appliances,
- automation service,
- gateway / BFF with authentication,
- web app.

Copilot ran locally, used SSH to Orange Pi Zero 2 and Orange Pi Zero 3 (2GB RAM), inspected Home Assistant files for configs/device names, created/debugged microservices over SSH, made GitHub Actions publishing to container registry, and deployed via Docker Compose. It discovered TaHoma Switch has local API, so blinds could be controlled locally instead of through cloud.

Result: architecture is more readable; changes can be described to Copilot instead of relearning configuration.

### Phase 2 - not an agent inside software, but software managed by an agent

A web app with login existed, but family members did not want to use it. Agentic interface over WhatsApp/voice seemed useful.

Desired requests are more complex than intent extraction:

- "Tomorrow I need to get up at 6:00; open bedroom blinds a bit at 5:58 and fully at 6:00."
- "Tonight we go to bed earlier; stop heating at 19:00 and close all blinds at 21:00."
- "I am going for herbs; raise the blinds for one minute."

Hard-wiring these would defeat the agentic idea. Need a real agent that can use low-level APIs and add missing capability, not just a chat layer over the web.

Chosen agent: **OpenClaw** (`https://github.com/openclaw/openclaw`). In this setup it runs locally, uses tools, keeps memory, extends itself with skills/scripts, and can modify itself.

Initial plan: agent would use MCP exposed by gateway/BFF. Reality: local agent naturally tried REST API directly and made mistakes. Solution: agree that OpenClaw writes a CLI and documents it in a skill.

Created CLI: `smarthomectl`

- Easier for LLM than assembling JSON and escaping shell commands.
- Adds simple switches.
- Gradually adds abstractions from experience.

Example abstraction: blind groups. Instead of calling API one by one, OpenClaw added flags such as:

- `--include`
- `--exclude`
- `--blinders-group`

This optimizes frequent scenarios by making them faster, simpler, and more reliable.

Architecture rule: low-level API connects digital agent to physical world. Agent maintains CLI ("muscle memory") and skill (context/dexterity) to create higher logic, plus memory/data persistence. This is one meaning of "software collapses into agents": world APIs + code/skill + persistence.

### Phase 3 - GenUI instead of fixed web UI

The web app is clear for the author, but not necessarily for the household. OpenClaw via WhatsApp is useful because nobody installs anything and users stay in their workflow. WhatsApp is robust, supports voice-written messages, and works from anywhere with weak signal.

Question: is a web UI still needed? Web is faster for many controls on one page. Agent is convenient for commands like turning on "lamp and counter" when it infers context. Problem: thinking latency. Smaller faster models may help, but must not lose ability for complex tasks/research.

Example of task that exceeds plain web UI: "if it will not rain tomorrow, let's run watering for x liters tonight" because it needs Internet research and decision-making.

Need GenUI. Consumer channels:

- WhatsApp Flows: `https://developers.facebook.com/docs/whatsapp/flows/` - structured multi-step forms/light UI, but not full mini-apps.
- Telegram Mini Apps: `https://core.telegram.org/bots/webapps` - capable UI, but E2E only for Secret Chats.
- Signal - no rich UI support.
- Discord E2E audio/video: `https://support.discord.com/hc/en-us/articles/25968222946071-End-to-End-Encryption-for-Audio-and-Video` - E2E audio/video, not text.

Planned paths:

1. Web - already exists and works.
2. WhatsApp - works well, execution sandboxed, ideal for non-admin use.
3. Custom chat/voicechat UI via web with mini-app support - next experiment.

Expected direction: voice input plus mini-app GenUI output may be ideal, especially later for glasses with a display.

## Conclusions

### Software is memory / optimization

If agent has low-level APIs, data, tools (Internet, databases), and context or a way to retrieve context, it can do almost anything but may be slow, wrong, token-heavy, and need feedback the first time. Training can encode procedure into:

- script,
- CLI function,
- MCP server,
- skill,
- memory/context.

Software stores repeatable, predictable, modifiable, testable business logic like a tennis serve. Skill/context records how, why, and meaning, like reading the game.

### API into the world, data, abstraction as skill

Agents can handle low-level APIs better than humans, who often need abstractions. Terraform modules help humans manage detail; LLMs may prefer detail. Give agents low-level APIs and data; let them create abstractions as CLI/skill/MCP optimizations.

### Context vs. feedback

Agents are tenacious when they can measure results. For e-commerce optimization, an agent may soon tune the whole app for profit using customer behavior, ordering data, ideas, A/B tests, and measurement. In established measurable systems, feedback can be 80% of success.

When the loop cannot be closed because the agent lacks domain understanding, context is decisive: goals, mechanics, business domain, tests, measurable outputs. In such cases, context can be 80% of success.

Goal: build strong context quickly, then move into mostly feedback-driven work where the agent can work alone.

### Learning user and GenUI

Agent understands varied user phrasing, asks clarification when unsure, remembers user preferences. The agent learns the user instead of the user learning software. Chat alone is not efficient for all scenarios. Graphical UI must also adapt automatically to the user. GenUI should become standard.

## Final takeaway

Users will not learn to use your software. **The software and the agent** will learn to understand the user.
