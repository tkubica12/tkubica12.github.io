# Saving tokens in GitHub Copilot

META
- url: /en/2026/token-saving-cz/
- date: 2026-07-05
- lang: en
- source_language: cs-CZ
- source_slug: token-saving-cz
- translated_from_hash: d89db6b18499fcee71ba854b3dd6757e4f49cf415d30ca66e48b7a9d962c85d7
- source: source.md
- audience: Copilot users, agent mode, skills/MCP authors
- thesis: scoped sufficiency = enough context for correct solution, nothing extra. Tokens = investment; optimize return, not consumption.

KEY POINTS
- Token eaters: always-on instructions, open/selected files, chat history, MCP tool definitions + JSON schemas, tool results replay, output including reasoning/thinking tokens, retries/subagents/loops.
- Types: input; cached input; output.
- Cost ratio: cache : input : output ≈ 1 : 10 : 60.
- Tier down ≈ 3-4× cheaper; long context ≈ 2× input/cache, ≈1.5× output.
- Reasoning effort increases the most expensive category: output/reasoning tokens + latency.
- Models do not share one tokenizer; same price per 1M tokens ≠ same price for the same text.
- `/compact` = expensive output bolus + cache invalidation.

DETAILS

## 00 Mental model
- Goal: scoped sufficiency.
- Input = prompt + context + tool results.
- Cached input = repeated prefix in same session; ~10× cheaper than fresh input.
- Output = generated text + often internal reasoning/thinking; ~6× more expensive than fresh input, ~60× more expensive than cached input.
- Pricing USD / 1M tokens:
  - gpt-5.5: cache $0.50; input $5.00; output $30.00; long cache $1.00; input $10.00; output $45.00.
  - gpt-5.4: cache $0.25; input $2.50; output $15.00; long cache $0.50; input $5.00; output $22.50.
  - gpt-5.4-mini: cache $0.075; input $0.75; output $4.50.
  - gpt-5.4-nano: cache $0.02; input $0.20; output $1.25.
  - Mini/nano have no long context.

## 01 Auto model
- Default Auto unless there is a clear reason for premium reasoning.
- Routes by complexity/availability/system health.
- Avoids expensive model pinned to routine work.
- Paid plans: 10% multiplier discount.
- Override still for architecture/hard debug.
- Microsoft HyDRA paper: https://arxiv.org/abs/2605.17106
- HyDRA in Copilot Auto: task-aware routing by reasoning, code generation, debugging, tool use + model health.
- SWE-Bench Verified:
  - same quality as strong Sonnet 4.6: 54.1% cost savings.
  - peak-quality beats Sonnet 4.6 and still saves 12.9%.
- GitHub blog: https://github.blog/ai-and-ml/github-copilot/getting-more-from-each-token-how-copilot-improves-context-handling-and-model-routing/
- Cache-aware: do not switch model/reasoning/context size mid-session without reason; it can break cached prefix.

## 02 Explicit context
- Expensive: "Understand repo and fix login."
- Cheap: paths + bug + done criteria.
- Example: `src\auth\login.ts`, `tests\auth\login.test.ts`; `validateEmail` rejects `user+tag@example.com`; add test; fix only this.
- Rule: exact paths cheaper than whole-repo exploration.
- Batch: 3-5 related tasks. More = lower focus, more retries/errors.

## 03 Find files first
- Prompt: "Find the smallest set of files for event-driven flow. List only paths + 1 sentence why. Do not summarize the whole repo."
- Then implement with exact context.

## 04 Output tokens + reasoning effort
- Output is most expensive.
- Expensive: detailed explanation of everything.
- Cheap: changed files, why, tests; max 5 bullets.
- Caveman report: "Done. List: files, why, validation, risks. No intro. ≤5 bullets."
- Do not shorten safety/destructive/compliance instructions; ambiguity costs more.
- Reasoning effort:
  - low: quick questions, small edits, format conversions; little hidden output.
  - medium: normal agentic work; usually best cost/performance.
  - high: architecture, hard debug, unclear multi-step problem; more reasoning tokens, higher latency.
- Verdict: medium reasoning is a good default; Expert-SWE/refactor benchmark (https://www.digitalapplied.com/blog/reasoning-effort-cost-vs-quality-benchmarks-2026) shows medium as the sweet spot, while high adds cost/latency and sometimes over-engineering.

## ★ Child message
- Verbose mom: 388 chars; 140 tokens; high readability.
- Caveman: "Home at 18:00. Homework: M + Cz → then tablet 1h. Soup in fridge → microwave 3 min. Dog out 17:00 + kibble. Mom 💕"
  - 110 chars; 48 tokens; −66%; still readable.
- Agent→agent: `18→mom. homework→tablet1h. soup:micro3m. dog:17→out+eat.`
  - 57 chars; 29 tokens; −79%; poor for humans.
- Point: caveman = sweet spot for human-read reports. Extreme only agent-to-agent/durable context.

## 05 Logs and UI
- Terminal: screenshot antipattern.
- Instead of 5,000 CI log lines send: command, exit code, relevant error, stack frame, last 30 lines.
- UI: Playwright MCP / browser canvas.
- Rule: text for text, controlled browser for visuals; static screenshot last resort.

## 06 Language, structure, tokenizer
- English is token-cheaper, but not dogma.
- Structured format erases most of the difference.
- Quality > saving. Cost of mistake > token cost.
- Endpoint prompt data:
  - normal EN: 148 chars, 31 tokens.
  - normal CZ: 148 chars, 50 tokens = 1.61×.
  - structured EN: 71 chars, 20 tokens.
  - structured CZ: 70 chars, 23 tokens = 1.15×.
  - verbose CZ: ~95 tokens; +313% vs structured.
- Conclusion: native language for nuance; repeated operational prompts = compact English / structured keys.
- Claude Sonnet 5 tokenizer: same text ≈ 30% more tokens than Claude Sonnet 4.6; per-token price unchanged, equivalent request can cost more.
- Measure cost per solved task: tokenizer, reasoning effort, tool calls, retry rate, quality.

## 07 Hierarchical context
- Always-on instructions = recurring tax.
- Where things belong:
  - `AGENTS.md`: small facts the agent cannot infer.
  - `.github\instructions\*.instructions.md`: path-specific.
  - prompt files: workflow-specific, on demand.
  - `.github\skills\`: detailed capability, progressive reveal.
  - MCP: live data, fetch on demand.
- Small `AGENTS.md` + relevant skill vs giant `AGENTS.md`: 68.8% weighted-units saving.
- After hard discovery, let agent write concise skill ≤60 lines: entry points, key files, pitfalls, changes; lists+links; no prose.

## 08 MCP progressively
- Hidden costs: tool definitions+schemas in context; tool-call args as output; tool results replay as input.
- Flow: search/list candidates → choose one → fetch only detail needed for decision → concise summary.
- Unused global MCP servers cost tokens before call. Keep MCP per-workspace.
- Copilot tool search: https://code.visualstudio.com/blogs/2026/06/17/improving-token-efficiency-in-github-copilot
- Tool search: model gets lightweight metadata, full JSON schemas load on demand.
- OpenAI GPT-5.4/5.5 experiment: median total tokens/turn −8.61 to −9.81%; median session tokens −8.97 to −10.92%.
- Anthropic deferring tool definitions: median user total tokens roughly −18%.
- Tool search saves tool definitions, not result volume. MCP should still return small candidates, filter, and fetch detail only on demand.

## 09 Deterministic tools
- If exact algorithm exists, do not use multi-turn reasoning.
- Candidates: JSON→XML/CSV, token counting, log slicing, schema validation, dependency graph, sort/filter/dedupe, ID generators, templates.
- Script-backed skill: 1 tool call with deterministic output instead of 5 turns and error risk.

## 10 Session management
- Economics: old cache cheapest; fresh input ~10×; output ~60×.
- `/ask`/`/btw`: off-topic, cache stays, answer does not grow into history.
- `/undo`/`/rewind`: removes bad last turn and its context.
- `/fork`: sidequest on same cached prefix.
- `/resume`: return after break; often cache hit, later fresh input.
- `/new`: new topic, no cache.
- `/clear`: ends session; files remain.
- `/compact`: expensive, cache-invalidating.
- `/share`: export for analysis.
- `/chronicle tips|cost-tips|improve`: self-reflection.
- `/limits set max-ai-credits NUMBER` / `--max-ai-credits NUMBER`: soft Copilot CLI session limit; 1 AI credit = $0.01.
- Admin governance: user-level budgets, cost center per-user limits, cost center budgets, organization/enterprise budgets, hard stops.

## 11 Subagents
- Save wall-clock, but can multiply input tokens when reading same files.
- Use: independent work; shardable context; cheaper model; short summary.
- Do not use: same context for all; sequential task; coordination overhead.
- Keep the handoff small: objective, known facts, exact files, constraints, acceptance criteria, output format.
- GitHub/VS Code direction: specialized subagents for workspace search, command execution, result summarization; smallest model that can do the job.
- Smaller model can be cheap per token but expensive per result if it makes more tool calls, reads more files, or triggers retries.

## 12 Measuring skills
- Token efficiency = engineering discipline + feedback loop.
- Measure: input, output, cached tokens, turns, tool calls, latency, retry rate, quality.
- CI for `.github/skills/**`, `AGENTS.md`, `.github/prompts/**`:
  - `copilot-token-lab run --scenarios skills-regression --iterations 3`
  - `copilot-token-lab compare --baseline main --head HEAD`
  - fail-if: `weighted_units_delta > +10% AND quality_score < baseline`
  - comment-pr: `report.md`
- Advice: measure your own workload. Cheaper model ≠ automatically cheaper outcome.

WARNINGS
- Do not shorten safety/destructive/compliance instructions.
- Batch limit practically 3-5 related tasks.
- Do not leave high reasoning effort pinned for routine work.
- `/compact` is expensive and cache-invalidating.
- Changing model/reasoning/context size mid-session can break cache.
- Global MCP servers have always-on cost.
- Tool search saves tool definitions, not tool result volume.
- Subagents are not magic token savings.
- Cheaper model ≠ automatically cheaper result.

VERDICT
- Easy: Auto model; reasoning effort consciously; exact files+done criteria; find files first; short output; log excerpts; structured format.
- Advanced: small `AGENTS.md` + skills/path instructions; MCP search→select→fetch; account for different tokenizers; deterministic tooling; `/ask`, `/fork`, `/resume`; `/compact` carefully; subagents only for independent work; discovery/search subagents promising; measure in CI.
- Tokens are not a cost to throttle. They are investment. Optimize return, not consumption.
