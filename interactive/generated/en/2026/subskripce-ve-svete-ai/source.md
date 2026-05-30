---
format_version: 1
title: "Is subscription a suitable business model for an AI product? Is AI getting more expensive? Are tokens getting more expensive? Or are we just moving toward a fair model?"
eyebrow: "Subscription, tokens and agents"
subtitle: "Flat subscription is great for adoption, but agents break the natural limits of consumption. I see the future more in a license as an entry ticket, pooled prepaid consumption, and fair top-up units."
slug: subskripce-ve-svete-ai
date: 2026-04-27
language: en
source_language: cs-CZ
source_slug: subskripce-ve-svete-ai
translation: machine
translated_from_hash: "ff13eec8e86981125d72348688373f06386882c6ee2fcabefd460e0204daf507"
translation_status: current
status: experimental
canonical_url: "/en/2026/subskripce-ve-svete-ai/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

Recently there have been many changes in the business models of some AI products, especially those around coding. I think this is a preview of changes in other areas too - once we see the same phase transition we experienced in coding in December 2025 (when it simply started working beautifully and reliably), similar pressure will emerge on other products, including those for non-developers. And I would guess agents such as OpenClaw or Cowork are the next service that will follow this trend.

::: group id="predplatne" title="Why classic subscription worked"

::: card number="01" title="Classic subscription" default="open"
If you make people pay based on how they use a service, it is well known that they then use it little and cannot realize its full value - they never really learn it, because they keep counting money and feeling afraid. Subscription solved this brilliantly in the past - it pulls you into the game, you use it, get used to it, do not want to lose it. And you spread it around, increasing the user base. In short, **flat subscription is ideal for adoption**.

::: reveal title="Spotify, the gym and a natural limit"
How does the service provider make money on that? It is clear they have calculated it so they have a good margin on the average user. They earn much more on those who use it little, earn little on power users, and may lose money on a few extreme ones. Take Spotify, for example. It certainly has some fixed costs per user (servers, app development, and so on), but many costs are consumption-driven - royalties to authors, data transfer fees. An average user may consume, say, 50 hours per month. And a "power user"? There is a natural limit - even if they never slept, it cannot be more than 730 hours per month; with some sleep, say about 10x more than the average user (gym or public transport subscriptions have similar natural limits). Another type of business may have a smaller difference (for example an electronic magazine subscription - how many articles a power user reads does not matter much) or a larger one (for example Box-like storage with unlimited space also has unlimited costs). Where there is no natural limit (such as the number of hours in a month), the provider often protects itself with an "asterisk" - it is unlimited, but unfair use is detected and a vague limit is applied.
:::
:::

::: card number="02" title="Why AI makes this problematic" default="open"
With ordinary chat, of course, a very active user consumes far more tokens and therefore generates costs not 10x between the average and power user, but certainly more like 100x. Maybe the business model can still handle that, but some restrictions may be used:

- Limits within an hour
- Temporary switch to a cheaper model
- Slower response (not deliberately, but perhaps because someone overshooting is deprioritized)

But that is chat - **agents change everything**. So-called Deep Research was already a bit of a problem, but a full-fledged agent is much bigger - and in coding it is the only thing that makes sense today. An agent can work on a given task for hours, load code and documentation (so it has enormous token context), call tools across hundreds of interactions, create colleague subagents and let them work on parts of the problem in parallel. And if your agent works on something for an hour, will you watch it, or open another window and start another one solving something else? Of course you will do that, so in the end a de facto unlimited number of hungry agents and subagents is running. The ratio between your average user and Power User can easily reach a 4-order-of-magnitude difference and can practically go completely off the rails - not intentionally at all, the user simply used agents fully and sleep is not a natural limit.

::: sequence title="The path from chat to agents"
1. **Chat** — the difference between average and power user may be more like 100x.
2. **Deep Research** — already a bit of a problem because it runs longer and consumes more context.
3. **Full-fledged agent** — hours of work, hundreds of tool calls, subagents and parallel windows can drive consumption up by whole orders of magnitude.
:::

::: callout type="verdict" title="The point"
What to do about it? **It cannot be flat subscription** - and that is why there are so many market changes and a move toward paying by fair use. Let us first look at what will actually be paid for, and then at what the model may look like.
:::
:::

:::

::: group id="naklady" title="Two sources of cost"

::: card number="03" title="Tokens and compute are measurable" default="open"
A solution typically has to include payment for the fact that it exists - someone built it, handles its security, architecture, compliance, and also has some basic operating costs. But that is not what we care about now - we want to focus on two sources of cost that are directly measurable and directly depend on the user (without the user they do not arise).

::: summary-grid
- **Tokens**: input, cached input and output tokens are a direct model cost.
- **Compute**: a cloud agent needs CPU, RAM and an isolated environment; for an agent this is the second key component.
:::

::: reveal title="Tokens"
**Tokens** are real costs of the given solution. People say Anthropic has a 40%-50% margin on tokens (which includes model IP and inferencing, meaning GPU), so we can assume it will be similar elsewhere. Even if the provider hosts the model itself or has a discount, token costs are still very real - this is not some license or something similar, but actual electrons converted into intelligence. Input, cached input and output tokens are a direct cost. Of course different models have different prices (they differ in hardware demands), and that must be included, so some conversion is usually used in the form of an "AI unit" - medium model 1x, large model 3x, and so on. Some places count money directly, but for services supporting different models (for example GitHub Copilot with support for OpenAI, Anthropic and Google), conversion through a virtual currency is more common.
:::

::: reveal title="Compute"
**Compute** will become the second key component, because for a chatbot the consumed compute is relatively small, but for an agent the situation is different. Yes, an agent can run locally on the user's laptop (see for example GitHub Copilot CLI), but for security and practical reasons it will increasingly be a machine in the cloud. An agent needs a computer, and giving it one in the cloud will make enormous sense. But then it is rented compute - real costs for electrons flowing through CPU and RAM. Infrastructure cloud has some margin (let us count 30%-40%), so again it is true that even if there is an operations discount or the provider hosts it itself, most of the price still remains a cost.
:::
:::

:::

::: group id="cloud-model" title="A model for cloud"

::: card number="04" title="Subscription as an entry ticket, consumption package and top-ups" default="open"
I think this is the model of the future - a subscription that unlocks features and typically also includes some **prepaid consumption**, ideally pooled. Let us explain.

GitHub Copilot (announced and in effect from June) or Cursor work on the principle that you have a subscription that lets you use its features and at the same time includes some amount of consumption. That amount may even be absolutely zero (seat-only, as Anthropic Claude Enterprise has it, with nothing included in the price), or smaller (for a 20 USD license you get 10 USD included), but the standard is usually from 1:1 upward (Cursor has 1:1 on the 20 USD license, but the 60 USD plan includes 70 USD of consumption; GitHub Copilot uses 1:1, so a 19 USD license includes 19 USD of consumption).

::: tabs id="modely-spotreby"
::: tab id="seat-only" title="Seat-only"
The license unlocks the product, but no consumption is included in the price. Anthropic Claude Enterprise has it this way: the license includes absolutely nothing, you buy everything extra.
:::
::: tab id="included" title="Included consumption"
With the license you also receive some consumption bundle. It can be smaller than the license price, 1:1, or even higher - for example Cursor's 60 USD license includes 70 USD of consumption.
:::
::: tab id="pool" title="Pool"
All purchased licenses create a pool of money for the whole company, so a user who uses the product little does not mean their consumption is lost - someone else uses it.
:::
::: tab id="dokupy" title="Top-ups and limits"
Enterprise needs to manage per-user limits and top-up policy by company or organization. In my view this replaces the era of vague limits such as week, hour, exceptions and unclear changes.
:::
:::

What I find very fair, and as far as I know only GitHub Copilot and Cursor have it, is the **pool**. All purchased licenses create a pool of money for the whole company, so a user who uses it little does not mean their consumption is lost - someone else uses it. Ideal for AI infusing into an organization - everyone should have it! This is a good incentive: nobody is "not promising" and therefore without AI; everyone has it, and if someone does not use it fully, someone else consumes it. Of course it is important to have good ways to manage possible per-user limits and top-up policy by company or its organizations - GitHub Copilot has this handled very well.

Claude Code is very readable in the Enterprise version - **the license includes absolutely nothing, you buy everything extra**. I think the era of vague limits (week, hour, we will never say exactly, or we will say it but then keep changing it and granting exceptions) will end, especially for enterprise, because that kind of fog is not good for companies. OpenAI Codex, however, is still currently operating this way.
:::

:::

::: group id="zbytek-ai" title="Beyond coding"

::: card number="05" title="That is coding, what about the rest?" default="open"
Currently all of this concerns coding agents, but other AI services such as M365 Copilot, Gemini, OpenAI and Claude still typically run on a more classic subscription with strange limits. Claude Enterprise is an exception - even for ordinary chatting, nothing is included in the price; it is seat-only. I guess this is a preview that one day other enterprise services will also move into a different model, and I expect something quite similar to coding agents - a fee per hour of borrowed computer (for example for Cowork), and a fee for tokens.

What about you? Do you prefer a flat subscription world with strange and unclear limits, subtle quality reduction (see some Claude affairs from the last few days), but potentially better price predictability and the ability to get several orders of magnitude more out of it if you are a power user? Or do you prefer a model based on actual consumption with a separate entry-ticket fee? Personally, because I grew up on Azure and consider pay-as-you-go the most natural and fair model, I like the model GitHub Copilot has now - subscription costs something, but you get its value back in tokens and it is pooled, so you do not have to be afraid to give a subscription even to people who do not yet know how to use it that much.
:::

::: card number="06" title="Is AI getting more expensive?" default="open"
So is AI getting more expensive? I do not think so - tokens across the whole market are priced very fairly with a reasonable margin and never get more expensive for a specific generation/quality. Rather, new models arrive, and in practice today's mini model in the cloud gives you a similar service at 5x lower price than a high-end model a year ago; the fee per unit of intelligence is therefore dropping absolutely dramatically, more than in any other IT technology over the last 50 years. But - today a coding agent writes a whole application for you in an hour; a year ago an AI assistant suggested a new class, and when you ran it, you dealt with the fact that it did not work and sent it back. If living in the past is enough for you, use a 5x cheaper model and enjoy saving money - AI has become brutally cheaper. I would rather ride a different wave - for very similar money to a year or two ago, today I have a substantially better and more useful solution. I prefer intelligence and growth over savings. But everyone can have it differently, and that is fine - **but AI has not become more expensive**. However, we have hit the limit of a business model that is unsustainable in this era. In my view we need a model where, for predictable costs, we introduce AI to everyone, do not lose unused tokens thanks to pooling, and sensibly manage top-up limits, for example by organization or individually.

::: summary-grid
- **Adoption**: flat subscription pulls people into using the product.
- **Limit**: agents do not have a natural consumption ceiling like listening hours or gym visits.
- **Costs**: tokens and cloud compute are real and measurable costs.
- **Fairness**: the ideal is a predictable license, pooled consumption and managed top-ups.
:::

I have prepared and tested tips for saving tokens - we will look at that in the next article!
:::

:::
