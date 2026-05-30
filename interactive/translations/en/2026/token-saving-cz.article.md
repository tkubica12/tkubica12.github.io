---
format_version: 1
title: "Saving tokens in GitHub Copilot"
eyebrow: "How to reduce costs in 15 minutes"
subtitle: "From easy wins to advanced context engineering. The goal is not to spend the fewest tokens, but to get maximum value from each one."
slug: token-saving-cz
date: 2026-05-29
language: en
source_language: cs-CZ
source_slug: token-saving-cz
translation: machine
translated_from_hash: "b35cee2ce7d4dcd2dd1b7f7fa93ae47594b131a58c3669d3b6551b962832806b"
translation_status: current
status: experimental
canonical_url: "/en/2026/token-saving-cz/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

::: group id="intro" title="Mental model"

::: card number="01" title="What eats tokens" default="open"

Cost does not come only from what you type into chat. It adds up across many layers:

- **Always-on instructions** — `AGENTS.md`, custom instructions, hooks
- **Selected and open files** in context
- **Chat history** and summaries between turns
- **MCP tool definitions** and their JSON schemas — even the ones you do not use
- **Tool call results** replayed as input in the next step
- **Model output** (output tokens are the most expensive)
- **Retries, subagents, loops** in agent mode

::: callout type="rule"
The goal is **scoped sufficiency** — enough context for Copilot to solve the task correctly, but not one extra word.
:::

**Three token types — why they matter:**

- **Input** — everything you send to the model for the first time (prompt, context, tool results)
- **Cached input** — a repeated prefix the model has already seen in a previous turn of the same session. **~10× cheaper** than fresh input.
- **Output** — what the model generates. **~6× more expensive** than fresh input, **~60× more expensive** than cached input.

**Example from current real pricing (USD per 1M tokens):**

| Model | Short cache | Short input | Short output | Long cache | Long input | Long output |
|---|---:|---:|---:|---:|---:|---:|
| **gpt-5.5** | $0.50 | $5.00 | $30.00 | $1.00 | $10.00 | $45.00 |
| **gpt-5.4** | $0.25 | $2.50 | $15.00 | $0.50 | $5.00 | $22.50 |
| **gpt-5.4-mini** | $0.075 | $0.75 | $4.50 | — | — | — |
| **gpt-5.4-nano** | $0.02 | $0.20 | $1.25 | — | — | — |

Mini and nano do not have long context.

**Ballpark rules:**

- **Cache : Input : Output ≈ 1 : 10 : 60**
- **Each tier down is ~3–4× cheaper**
- **Long context makes input/cache ~2× more expensive and output ~1.5× more expensive**
- **Cache is why `/compact` is not free**

:::

:::

::: group id="easy" title="Easy wins for everyone"

::: card number="02" title="Use Auto model as the default"

If you are not sure why you need a premium reasoning model, start with **Auto**.

- It routes by task complexity, availability and system health
- You will not keep an expensive model pinned for routine work
- **10% discount on the multiplier** for paid plans
- Manual override for architecture or hard debugging remains available

In practice, for normal work this means you save 10% compared with pinning a specific model — and often also get a cheaper model that can handle the task.

:::

::: card number="03" title="Explicit context instead of broad prompts"

```text label="Expensive" tone="bad"
Understand this repository and fix the login problem.
```

```text label="Cheap" tone="good"
Focus on src\auth\login.ts and tests\auth\login.test.ts.
Bug: validateEmail rejects user+tag@example.com.
Add a test and fix only this behavior.
```

**Rule:** concrete file paths are cheaper than exploring the whole repository.

**Bonus: batch related tasks into one prompt.**

```text tone="good"
In src\auth\login.ts:
1. validateEmail — allow user+tag@example.com
2. add a test in tests\auth\login.test.ts
3. add a docstring to the function
4. record the change in CHANGELOG.md
```

::: callout type="warning" title="How far should you go?"
The practical limit is **3–5 related tasks** in the same code area. Above that the agent loses focus, makes more mistakes, and retries eat the whole saving.
:::

:::

::: card number="04" title="Find files first, before implementation"

Instead of "do you understand the whole thing?", ask:

```text tone="good"
Find the smallest set of files I need to understand the event-driven flow.
List only paths and one sentence why. Do not summarize the whole repo.
```

Only then give the task — knowing what is relevant.

:::

::: card number="05" title="Limit output length (output tokens are the most expensive)"

```text label="Expensive" tone="bad"
Explain in detail everything you changed.
```

```text label="Cheap" tone="good"
List: changed files, why, tests. Max 5 bullets.
```

"Caveman" output style for reports:

```text tone="good"
Done. List: files, why, validation, risks. No intro. ≤5 bullets.
```

::: callout type="warning" title="Careful"
Do not shorten safety, destructive or compliance instructions. Ambiguity costs more than the saved tokens.
:::

:::

::: card number="★" title="Example — a message for a child in three versions"

The same information in three versions. It shows the "sweet spot" between readability and compactness.

::: tabs id="kid-message"

::: tab id="v1" title="1 · Careful mom"

Hi sweetheart, mom will come home around six in the evening. Please do your math and Czech homework first, okay? Once you are done, you can play on the tablet for an hour. There is tomato soup in the fridge; heat it in the microwave for three minutes on high. Please do not forget to walk Bertik around five o'clock and then put kibble in his bowl. I love you very much, mom 💕

| Metric | Value |
|---|---:|
| Characters | 388 |
| Tokens (GPT-5) | 140 |
| Readability | high |
| For whom | people with time |

:::

::: tab id="v2" title="2 · Compact (caveman)"

Home at 18:00. Homework: M + Cz → then tablet 1h. Soup in fridge → microwave 3 min. Dog out 17:00 + kibble. Mom 💕

| Metric | Value |
|---|---:|
| Characters | 110 −72 % |
| Tokens (GPT-5) | 48 −66 % |
| Readability | still good |
| For whom | human who understands |

:::

::: tab id="v3" title="3 · Extreme (agent → agent)"

```text
18→mom. homework→tablet1h. soup:micro3m. dog:17→out+eat.
```

| Metric | Value |
|---|---:|
| Characters | 57 −85 % |
| Tokens (GPT-5) | 29 −79 % |
| Readability | poor |
| For whom | agent → agent |

:::

:::

::: callout type="verdict" title="Point"
Caveman style is the sweet spot for reports that a human still reads. Extreme style makes sense only for agent-to-agent handoff or durable context.
:::

:::

::: card number="06" title="Paste excerpts, not whole logs — and prefer Playwright for UI"

For terminal output, a screenshot is an antipattern. Instead of 5,000 lines of CI log, send only the relevant excerpt:

```text tone="good"
Command: npm test
Exit code: 1
Relevant error:
  TypeError: Cannot read property 'id' of undefined
  at UserService.findById (src/services/user.ts:42)

Last 30 lines:
  ...
```

For visual questions, it is more efficient to use **Playwright MCP or browser canvas**.

::: callout type="rule"
Rule: text for text, controlled browser for visuals. Static screenshot only as a last resort.
:::

:::

::: card number="07" title="Prompt language and structure — why English is not dogma"

The tokenizer is trained mostly on English text, but this is not dogma:

1. **Structured format erases most of the difference**
2. **Quality comes before saving**
3. **Cost of a mistake > cost of tokens**

::: reveal title="Normal prompt"

```text
Create a POST endpoint /api/users that validates required fields name and email,
returns 400 on error and 201 with the created user on success.
```

| Language | Characters | Tokens | vs EN |
|---|---:|---:|---:|
| English | 148 | **31** | 1.00× |
| Czech | 148 | **50** | 1.61× |

:::

::: reveal title="Structured prompt"

```text
POST /api/users
Validate: name req, email req+valid
400 errors
201 user
```

| Language | Characters | Tokens | vs EN |
|---|---:|---:|---:|
| English | 71 | **20** | 1.00× |
| Czech | 70 | **23** | 1.15× |

:::

::: reveal title="Verbose prompt"

```text
Please, could you create a new HTTP endpoint of type POST
at path /api/users that accepts JSON with fields name and email,
validates that both values are present and the email is in the correct format,
and on success returns 201 Created with the created user object,
while on validation error it returns 400 Bad Request with error details?
```

| Version | Tokens | vs structured |
|---|---:|---:|
| Verbose CZ | **~95** | +313 % |
| Normal CZ | 50 | +117 % |
| Structured CZ | 23 | baseline |

:::

::: callout type="verdict" title="Conclusion"
Use your native language when quality matters and you are expressing nuance. For repeated operational prompts, compact English or structured keys win.
:::

:::

:::

::: group id="advanced" title="Advanced techniques"

::: card number="08" title="Hierarchical context — skills instead of a giant AGENTS.md"

Always-on instructions are a **recurring tax** — you pay them on every turn.

| Context type | Where it belongs | Rule |
|---|---|---|
| Always-on (small) | `AGENTS.md` | only facts the agent cannot infer |
| Path-specific | `.github\instructions\*.instructions.md` | loaded only for relevant files |
| Workflow-specific | prompt files | invoked on demand |
| Detailed capability | `.github\skills\` | progressive reveal — only when the topic appears |
| Live data | MCP server | fetch on demand |

::: callout type="rule"
Big AGENTS.md vs. small AGENTS.md + one relevant skill → **68.8% saving in weighted units**.
:::

**Let the agent write context for the future.**

```text tone="good"
Write into .github\skills\auth-flow\SKILL.md
a concise (≤60 lines) description of the auth flow as we have just
understood it. Focus on: entry points, key files, pitfalls,
what to do when changing it. No prose, only lists and links.
```

::: callout type="rule"
If you learned something the hard way in a session, it is a **candidate for durable context**.
:::

:::

::: card number="09" title="MCP progressively — search → select → fetch"

**MCP has three hidden cost layers:**

1. Tool definitions and JSON schemas loaded into context
2. Tool call arguments as output tokens
3. Tool results replayed as input in the next step

```text tone="good"
1. search or list candidates
2. choose one
3. fetch only the detail you need for the decision
4. summarize the result before continuing
```

::: callout type="warning"
Unused global MCP servers cost tokens before you even call them. Keep MCP per-workspace.
:::

:::

::: card number="10" title="Deterministic tools instead of many-turn reasoning"

If an algorithm exists that solves the task **exactly**, do not force the model to do it across several turns.

Typical candidates:

- JSON → XML / CSV conversion
- Token counting, log slicing, schema validation
- Dependency graph extraction
- Sort, filter, dedupe large data
- ID generators, parameterized templates

::: callout type="rule"
A skill with a script-backed tool does 1 tool call with deterministic output instead of 5 turns with error probability.
:::

:::

::: card number="11" title="Session management — /ask, /undo, /fork, /resume, /new, /clear, /compact, /share, /chronicle"

The economics are always the same: old cache is cheapest, fresh input ~10×, output ~60×.

| Situation | Command | What happens |
|---|---|---|
| Short off-topic question | `/ask` (`/btw`) | cache stays, answer does not grow into history |
| Bad last turn | `/undo` (`/rewind`) | removes changes and the context of the last turn |
| Sidequest on the same base | `/fork` | branches share the cached prefix |
| Return after a break | `/resume` | often cache hit, later input |
| New topic | `/new` | old session saved, new one without cache |
| End permanently | `/clear` | session discarded, file changes are not |
| Context grew | `/compact` | expensive operation, output bolus + cache invalidation |
| Export session | `/share` | input for analysis and improvement |

`/chronicle tips`, `/chronicle cost-tips` and `/chronicle improve` serve as regular self-reflection.

:::

::: card number="12" title="Subagents — isolation, not magic savings"

Parallel agents can save wall-clock time, but **multiply input tokens** if they read the same files.

Use a subagent when:

- The work is truly independent
- Context can be sharded by service / file area
- A cheaper model is enough
- The result can come back as a short summary

Do not use when:

- All agents need the same context
- The task is sequential
- Coordination overhead dominates

::: callout type="rule"
Handoff small: objective, known facts, exact files, constraints, acceptance criteria, output format.
:::

:::

::: card number="13" title="Measurement as part of skills development — CI/CD + self-improvement"

Token efficiency is not a one-time audit — it is an **engineering discipline with a feedback loop**.

Measure:

- input, output, cached tokens
- number of turns
- tool calls
- latency
- retry rate
- quality of result

```yaml
on: pull_request
  paths: ['.github/skills/**', 'AGENTS.md', '.github/prompts/**']

steps:
  - run: copilot-token-lab run --scenarios skills-regression --iterations 3
  - run: copilot-token-lab compare --baseline main --head HEAD
  - fail-if: weighted_units_delta > +10% AND quality_score < baseline
  - comment-pr: report.md
```

::: callout type="verdict"
The only universal advice: **measure your workload**. Cheaper model is not automatically cheaper outcome.
:::

:::

:::

::: group id="summary" title="Summary"

### Easy

- Auto model as the default
- Name exact files and done criteria
- Find files as the first step
- Limit output
- Log excerpts, not dumps
- Structured format erases the language difference

### Advanced

- Small `AGENTS.md` + skills + path instructions
- MCP as search → select → fetch
- Deterministic tooling
- Use `/ask`, `/fork`, `/resume` consciously, `/compact` carefully
- Subagents only for independent work
- Measure in CI and ask the agent for self-improvement

::: callout type="verdict"
Tokens are not a cost to throttle. They are an **investment**. Optimize return, not consumption.
:::

:::
