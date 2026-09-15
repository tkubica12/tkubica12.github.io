---
format_version: 1
title: "Why aren't open-source models a hundred times cheaper? Let's explore the Pareto frontier."
eyebrow: "Model pricing, inference, and the Pareto frontier"
subtitle: "A cheaper token doesn't mean cheaper work. Open weights don't mean free GPUs. And a small model isn't a large model with the margin removed. Let's use one chart to see what actually makes sense to compare when choosing a model."
slug: proc-open-source-modely-nejsou-stokrat-levnejsi
date: 2026-09-15
language: en
source_language: cs-CZ
source_slug: proc-open-source-modely-nejsou-stokrat-levnejsi
translation: machine
translated_from_hash: 1d877be4260b8e96093556b13d47fd471d0608ebba87812cd2eb591fd7f9532c
translation_status: current
status: experimental
published: true
canonical_url: "/en/2026/proc-open-source-modely-nejsou-stokrat-levnejsi/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

"This open-source model is a hundred times cheaper than Claude or GPT." Could that be true? Of course. I'd just immediately ask: **cheaper than which model, at what settings, and doing what work?**

In [my previous article about open models and your own hardware](/en/2026/vlastni-model-vlastni-server/), I separated two things: which model I choose and who will run it. Our measurements showed why having your own GPU makes sense only if you have plenty of work for it — larger batch sizes and 24×7 operation. Today I want to come back to the first question. Is openness of the weights itself a reason for a dramatically lower price?

It seems to mean a lower price, yes, but not a dramatically lower one. I'm a fan of open models, but a price comparison needs two perspectives. **How much work the model can handle, and how much that work costs me.** And that's exactly where the Pareto frontier comes in.

As in the previous article, I'll be more precise than the headline: I'm mainly talking about **open-weight models**, whose weights I can download and run under the terms of their license. Their counterparts are closed-weight models, not "commercial models." Both groups are offered commercially.

::: group id="paretova-hranice" title="First, a picture: what's a good buy?"

::: card number="01" title="The Pareto frontier: getting better means making a tradeoff"
Let's look at this chart from Artificial Analysis.

![Artificial Analysis chart from September 15, 2026: the horizontal logarithmic axis shows the cost of a benchmark task in USD, the vertical axis the Intelligence Index. The dotted Pareto frontier connects non-dominated variants; GPT-5.6 Luna and GLM-5.3-Flash are among the low-cost points, while GPT-6 Astra and Claude Fable 5.1 have the highest scores.](../../../images/2026/2026-09-15-paretova-hranice-modelu.png)

*Source: Artificial Analysis, snapshot from September 15, 2026. [Open the interactive chart with this selection of models](https://artificialanalysis.ai/?models=gemini-3-5-flash-lite%2Cglm-5-3-flash%2Cgpt-6-astra%2Cclaude-fable-5-1%2Cgpt-5-6-luna%2Cmuse-glimmer%2Cdeepseek-v4-pro%2Cgemini-3-8-flash%2Cqwen3-8-2-4t-a95b%2Cmuse-spark-1-3%2Cqwen3-8-27b%2Cclaude-opus-5%2Cgpt-5-6-terra%2Cgrok-4-6%2Cclaude-fable-5%2Cglm-5-3%2Cgpt-5-6-sol%2Cdeepseek-v4-1-flash%2Cmistral-medium-3-5%2Ckimi-k3%2Cinkling%2Cclaude-fable-5-1-low%2Cclaude-sonnet-5-high%2Cclaude-4-5-haiku-reasoning%2Cgpt-6-astra-medium%2Cgpt-5-6-luna-medium%2Cgemini-3-1-pro-preview%2Cgemini-3-8-flash-medium%2Cqwen3-8-flash-next#intelligence-comparison-tabs). You can add more models and settings. The live data will change; the commentary below refers to the image.*

**Up is better, left is cheaper.** The vertical axis shows the aggregate Intelligence Index score, the horizontal axis the cost of one benchmark task. Not the price of a million tokens. The horizontal axis is also logarithmic: moving from $0.10 to $1 is the same multiple as moving from $1 to $10. So as we move right, the money adds up faster than it might seem.

The dotted line shows the **Pareto frontier**. Formally, the frontier of Pareto-optimal solutions; in practice, a set of choices that another option can't simply beat.

If I find a model that is cheaper and produces the same or better results, the more expensive model is **inferior** on these two criteria. The same applies if I get a better result for the same price. I improve on at least one criterion without making either one worse.

On the frontier, there is no such unambiguously better alternative. Want higher quality? I have to pay more. Want a lower price? I have to give up some quality. **There is no single winner for every budget and every task.**

That's an important difference from looking for a single "best price/performance ratio." A score of 50 doesn't mean twice the usefulness of a score of 25, either. First I need to decide what quality I actually require.

And one more thing: the line between two points isn't an offer for a model I can buy somewhere in the middle. Nor does it guarantee that mixing two models will give me a point on that line. It's a guide to the measured options, not a law of physics.
:::

:::

::: group id="odkud-se-bere-cena" title="Why open weights don't mean free inference"

::: card number="02" title="I'm paying for operations and for the model's capabilities"
To start with, I'd separate two economic layers in an API price.

The first is **running the model**. GPUs, memory, interconnects, power, the datacenter, software, and the people keeping it all running. Plus compensation for the provider that handles all this and bears the risk of unused capacity. In this respect, model serving is a fairly conventional cloud business.

The second is **developing the model and the value of its weights**. Someone paid for research, data, training, and post-training. With a closed model, I buy access to the result from its owner or a partner. With an open model, I may have the right to use the weights without an ongoing license payment, if its license allows it.

That doesn't mean developing the open model cost nothing. It means I don't have to pay for it in the same way. **Openness can remove a license payment for the weights. It doesn't remove the work the hardware has to do when I use the model.**

Besides, I usually won't see these two layers itemized on the invoice. An API price doesn't have to be "the cost of generating tokens plus a margin for the weights." Competition, capacity, business strategy, and efforts to attract customers all affect it. It can even be below cost temporarily.

I think economies of scale will play a crucial role in the operational layer. A large provider has demand from multiple applications and time zones. It can combine requests into larger batches, make better use of caching, and spread the cost of serving specialists across enormous volumes.

In our previous measurements, going from one to fifty concurrent requests with caching gave us about **5.5 times the aggregate capacity**. But each request took longer. And alongside batch size, I also need utilization over time: ideally, work that approaches continuous operation, not a GPU waiting every evening for morning to come.

That doesn't mean self-hosted inference has to run exactly 24×7 or it can never pay off. It means its economics are determined by **the amount of useful work at an acceptable latency**.

Providers of both open and closed models can take advantage of these benefits. **Removing their margin doesn't automatically give me their operating costs.**
:::

::: card number="03" title="A small model isn't a large model with the margin removed"
This, I think, is where much of the talk about hundredfold savings comes from. I take a relatively small open model and compare it with an expensive frontier model. The difference on the price list can be enormous. But I haven't just changed the license. I've also changed what I'm buying.

Just to be clear about the units: **B means billion, T means trillion**. A 2T model therefore has two trillion parameters.

| Illustrative size | In words | Parameter count compared with 3T |
|---|---|---:|
| 3B | 3 billion | 1,000× fewer |
| 30B | 30 billion | 100× fewer |
| 300B | 300 billion | 10× fewer |
| 3T | 3 trillion | comparison baseline |

These aren't imaginary size categories detached from reality. [According to its published model card, Kimi K3 has 2.8T total parameters and 104B active per token](https://huggingface.co/moonshotai/Kimi-K3). With **Mixture of Experts**, active parameters have a major effect on compute requirements, but all the weights still have to fit somewhere. And it's not just about memory capacity: memory bandwidth when loading the necessary weights and working with the cache is another crucial limit. That doesn't mean I load every expert for every token.

That's also one reason why, unlike home use, large-scale serving benefits from [disaggregating prefill and decode](https://docs.nvidia.com/dynamo/v1.0.0/design-docs/disaggregated-serving). Processing the input tends to be more compute-bound, while generating tokens one by one is more constrained by memory and its bandwidth. A provider can send each phase to differently configured hardware and scale them independently. But transferring the KV cache between them has to be worth the cost, too.

Nor can I increase **sparsity** — how small a fraction of the experts I activate — arbitrarily without affecting capabilities. [Experiments with MoE and reasoning](https://arxiv.org/html/2508.18672v3) show that more parameters at high sparsity help with knowledge storage, but reasoning also needs enough active computation and training data per parameter. So what's efficient for knowledge isn't necessarily efficient for reasoning. This isn't a universally optimal ratio for every model, but it is a good reason why simply adding more and more inactive experts isn't enough.

From single-digit billions to single-digit trillions, we're looking at roughly three orders of magnitude. Size isn't a precise price list or an automatic measure of quality, though. Architecture, training, quantization, and the specific task all matter. A smaller specialized model can outperform a larger general-purpose one on my task.

So I can't take a hundred times as many parameters and declare that inference costs a hundred times as much. But I'm still comparing significantly different hardware and capability classes, not the same product with its license price tag peeled off.

::: reveal title="And which of these will actually run on a laptop?"
Just storing the weights of a 30B model takes approximately **15 GB** at four bits, or about **60 GB** in two-byte BF16. That's without the KV cache, activations, quantization metadata, and runtime overhead. For 3B, it's a tenth of that; for 3T, a hundred times as much.

Models with single-digit billions of parameters can therefore fit on smaller devices, while tens of billions need substantially more memory. But a laptop with a large dedicated GPU isn't the only way. Plenty of unified memory or offloading to RAM can help; speed, context length, and battery life remain the question.

**"It fits" and "I want to work with it" are two different criteria.** Neither one, on its own, tells me whether the model can handle the tasks I routinely give a frontier coding agent.
:::

A cheap small model can be a great choice. It just doesn't need open weights to be one. Cheap closed-weight models exist too — and I mustn't forget to include those in the price comparison.
:::

::: card number="04" title="A technological lead can offset part of the open-weight advantage"
At the very top of this chart snapshot are the closed models Astra and Fable. A little further down, we already find very capable open models such as GLM-5.3 and Kimi K3.

My working hypothesis is that a team at the technological frontier can also turn some of its lead into efficiency: achieving a certain quality with less computation, shorter reasoning, or better-optimized serving. A closed model might then need less hardware for comparable work while charging me more for access to its weights.

What sort of margins are we even talking about? [Media estimates for 2025](https://techcrunch.com/2025/11/04/anthropic-expects-b2b-demand-to-boost-revenue-to-70b-in-2028-report/) put a leading model provider at around **50% gross margin**. [Reports from September 2026](https://money.usnews.com/investing/news/articles/2026-09-13/anthropic-tells-investors-it-will-be-profitable-for-second-straight-quarter-ft-reports) already talk about more than **80%**, but before distribution partners' shares and training costs. I treat these as ballpark estimates, not an audited time series for a single API; Reuters also did not independently verify the September report.

For context on the cloud side, we can look at [AWS's 2025 revenue of $128.7 billion and operating income of $45.6 billion](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Fourth-Quarter-Results/default.aspx), or an operating margin of about **35%**. But that isn't the gross margin on renting out a single GPU. I can't simply subtract these differently defined percentages and call the difference the price of the weights.

So for a back-of-the-envelope calculation, I'll use **50% or 80% as the total modeled margin of the closed service**, including compensation for serving and the model premium. For the open alternative, I'll keep **30% for serving**. This isn't a reconstruction of any particular company's accounts: if it buys compute from a cloud provider, some infrastructure margin may already be included in its costs. Here I'm calculating both options from the same cost basis without counting anything twice.

The direct inference cost of the same work will be **100 units** for the closed model. In our example, the open alternative will cost **15% more**, or 115. A 30% provider margin means costs make up 70% of the selling price: the open API therefore costs **164.29 units**, not 149.50 as it would with a simple 30% markup.

| Total modeled margin of the closed service | Closed-service price | Open-service price with a 30% serving margin | How many times more expensive the closed option is |
|---|---:|---:|---:|
| 50% | 200 | 164.29 | 1.22× |
| 80% | 500 | 164.29 | 3.04× |

How do I separate the two components in this model? At a direct cost of 100, serving alone with a 30% margin would cost **142.86**: a hundred for inference and 42.86 as the operator's compensation. That leaves **57.14** of the final 200 as the model premium; at 500, it leaves **357.14**. This isn't pure profit on the weights — it also funds development, training, and other costs.

The 15% efficiency difference and the 30% serving margin remain **assumptions in this example**, not measurements of a specific endpoint. If both options were equally efficient to run, the price ratio would be **1.4× to 3.5×**. With our efficiency difference, it's approximately **1.2× to 3×**. For a company, that could be a worthwhile saving, but we're still nowhere near the order of magnitude of **100×**.
:::

::: card number="05" title="A cheaper token doesn't necessarily mean a cheaper answer"
When I compare models through APIs, the price per million tokens isn't enough. I need to know how many tokens they'll use for the same work. Including reasoning, input, repeated context, and any additional attempts.

A very simple example: one model's output tokens cost half as much, but it needs three times as many. **Its output alone then costs me 50% more.** I'm leaving input and caching aside for now.

With Kimi K3, this isn't just an academic question. In the Artificial Analysis data available while preparing this article, [Kimi K3 at max settings](https://artificialanalysis.ai/models/kimi-k3) uses approximately **160 million output tokens** for an Intelligence Index run, while [GPT-5.6 Sol at max settings](https://artificialanalysis.ai/models/gpt-5-6-sol) uses about **90 million**. Yet the listed output price for Kimi is $15 per million, versus $20 for Sol. Cheaper tokens, but higher consumption; the weighted cost per benchmark task comes out to around two dollars for both.

Compared with [Opus 5 at max settings](https://artificialanalysis.ai/models/claude-opus-5), which is listed at about 140 million output tokens, the consumption difference is much smaller. So I wouldn't make a blanket claim that Kimi needs several times more tokens than all closed models. **It depends on what I compare it with and at what settings.**

Nor can I work out the chart's horizontal axis just by dividing these aggregate token counts. [Cost per Intelligence Index Task](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index) is a weighted average of the per-task costs of individual evaluations. It accounts for their weights in the index and the relevant billable tokens — input, cache, reasoning, and the answer.

That's why I like this chart more than a price list on its own. But it still shows **the cost of a benchmark task, not the cost of a successfully solved business case**. Quality is on the other axis. If a cheap agent messes up the task, its tokens still get billed just fine, but my work still isn't done.

And with self-hosting, I have to replace the API price with my own full operating cost. This picture alone doesn't tell me what Kimi would cost on my cluster.
:::

:::

::: group id="jak-to-pouzivat" title="Back to the chart: what it tells me about choosing a model"

::: card number="06" title="The Pareto frontier mixes vendors of open and proprietary models"
Coming back to the picture, I see three important things.

**The very highest level of capability isn't automatically available in an open version.** Astra and Fable are at the top, scoring around 53. GLM-5.3 and Kimi K3 are around 44–45, Sol around 47, and Opus 5 around 51. That doesn't mean an open model can't handle a specific task just as well or better, but this is how the benchmark comes out. Your use case can of course be different — though I don't expect dramatically different results.

**A little further down, open models really do compete, but I don't see an automatic hundredfold discount.** Kimi K3, GLM-5.3, and Sol are all roughly around two dollars per task here. Opus costs around six, but it also scores higher. Choosing Kimi instead of Opus may be the right decision. In this chart, though, it's a tradeoff between price and quality, not proof of the same result at a third of the price.

**The cheap end of the market isn't reserved for open models.** GPT-5.6 Luna at medium settings sits all the way to the left, at approximately $0.016 per task. That's a price difference of more than a hundredfold compared with Sol — within the range of a single closed-model vendor. But Luna's score here is around 25.5, not Sol's 47. Meanwhile, the open GLM-5.3-Flash is an interesting point on the frontier at around $0.25 and a score of 42. Careful: Flash isn't the same variant as GLM-5.3 max from the previous paragraph.

It's interesting to see how some vendors are doing as of the day I wrote this article. **OpenAI** has a very well-balanced portfolio, from small models (Luna, Terra) to large, highly capable ones (Sol, Astra). **Anthropic** can excel at the high end, but its more affordable variants can't make the Pareto frontier today (Haiku is way off, Sonnet isn't great, and Opus is also running out of steam on price optimality). **Google** is currently in a position where its high end, Gemini Pro, is out of the running, but the midrange Gemini 3.8 Flash is on the Pareto frontier, while the lower-end 3.5 Flash-Lite is currently out of the running.

For me, this is exactly what breaks the shortcut of "open equals cheap, closed equals expensive." Both groups occupy interesting positions. Some other models have an alternative that's both cheaper and more capable on the two criteria we're tracking, regardless of the license.
:::

::: card number="07" title="In the end, I need my own Pareto frontier"
I'd use this chart as an excellent starting point for choosing a model, not the end of the process. The Intelligence Index combines different types of tasks and their weights. But my application might spend all day doing one thing that a smaller model is excellent at.

I'd start with my own examples and a clear bar: what the model must handle and what counts as an error. Then I'd compare several cheap and more capable models, both open and closed, including sensible reasoning settings. Alongside the results, I'd measure **the entire bill for completed work**: every attempt, tool, possible fallback, and human correction.

This shows once again why **our own evaluation suites and training environments (RLE)** are so important for the future, as I already [wrote in my article about evals as the most valuable asset](/en/2026/evals-nejcennejsi-aktivum/).
:::

:::

::: closing
The biggest price difference isn't between an open and a closed model, but between a model that's **just right for my task** and one that's too dumb (and cheap) or unnecessarily smart (and expensive) for it.
:::
