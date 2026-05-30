# Is subscription a suitable business model for an AI product?

META
- url: /en/2026/subskripce-ve-svete-ai/
- source: interactive\translations\en\2026\subskripce-ve-svete-ai.article.md
- original: interactive\source\2026\subskripce-ve-svete-ai.article.md
- translated_from_hash: ff13eec8e86981125d72348688373f06386882c6ee2fcabefd460e0204daf507
- date: 2026-04-27
- audience: people dealing with AI products, enterprise AI and agentic costs
- thesis: flat subscription helps adoption, but agents break natural consumption limits; fairer model = license as entry ticket + pooled consumption + top-ups.

STRUCTURE
- 01 Classic subscription: good for adoption; works because averages and natural limits exist.
- 02 AI problem: chat can be constrained, agents change consumption by orders of magnitude.
- 03 Costs: tokens + compute are real measurable costs.
- 04 Cloud model: subscription unlocks product, includes consumption, ideally pooled, with extra top-ups.
- 05 Beyond coding: similar model likely for enterprise AI services.
- 06 Verdict: AI has not become more expensive; the old business model hit its limit.

KEY POINTS
- Flat subscription = ideal for adoption: users stop counting each use, learn the product, spread it.
- Provider earns more on low-use users, less on power users; model holds if natural usage ceiling exists.
- Spotify example: average 50 h/month; hard maximum 730 h/month; practical power-user difference about 10x.
- Where no natural limit exists, provider uses an "asterisk": unlimited, but unfair use is vaguely limited.
- Chat: power user may burn about 100x more tokens; still manageable with hourly limits, cheaper model, deprioritization.
- Agent: hours of work, huge context, hundreds of tool calls, subagents, parallel windows; ratio can reach 4 orders of magnitude without abuse.
- Agent conclusion: it cannot be flat subscription; fair-use billing is necessary.

DETAILS
## Costs
- Base product existence: development, security, architecture, compliance, operations.
- Direct user-driven costs:
  - Tokens: input, cached input, output; model prices differ; often converted to "AI units".
  - Anthropic token margin reportedly 40-50%; tokens are not a license, but inferencing/GPU/electricity/model IP.
  - Multi-model services such as GitHub Copilot with OpenAI, Anthropic and Google more often use virtual currency.
  - Compute: cloud agent needs CPU/RAM/isolated environment; infrastructure cloud margin about 30-40%, still real cost.

## Cloud model
- Future model: subscription unlocks features + usually includes prepaid consumption.
- Consumption can be:
  - zero, seat-only (Anthropic Claude Enterprise / Claude Code Enterprise: nothing included),
  - smaller than license (20 USD license, 10 USD consumption),
  - 1:1 or more (Cursor 20 USD = 20 USD, 60 USD = 70 USD; GitHub Copilot 19 USD = 19 USD).
- Pool is fair: licenses create a company-wide pool; unused consumption from low-use users is not lost.
- Pool encourages giving AI to everyone: nobody is considered "not promising" and left without AI.
- Enterprise needs per-user limits and top-up policy by company/organization; author says GitHub Copilot handles this very well.
- Author expects vague limits (week/hour/not precise/changed/exceptions) to end mainly in enterprise; OpenAI Codex still uses this style.

## Beyond coding
- Today this mainly concerns coding agents.
- M365 Copilot, Gemini, OpenAI, Claude mostly still use classic subscription with strange limits.
- Claude Enterprise exception: even ordinary chatting is seat-only with no included consumption.
- Author expects enterprise model: fee per hour of borrowed computer (for example Cowork) + token fees.

VERDICT
- Author prefers actual-consumption, Azure-like model with separate entry ticket.
- Preferred current model: GitHub Copilot — license costs money, value returns in pooled tokens.
- AI has not become more expensive:
  - tokens priced fairly with reasonable margin,
  - same generation/quality does not get more expensive,
  - new mini models deliver similar service to older high-end at about 5x less,
  - price per unit of intelligence drops dramatically.
- Difference: today a coding agent can write a whole app in an hour; older assistant suggested a class that often failed.
- Author prefers intelligence and growth over savings.
- Problem is not AI price inflation, but unsustainable old flat business model.
- Need predictable costs, AI for everyone, pooled unused tokens, sensible top-up limits by organization/user.
- Next article: tested tips for saving tokens.
