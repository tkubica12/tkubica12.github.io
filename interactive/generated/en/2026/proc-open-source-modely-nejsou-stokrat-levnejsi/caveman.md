# Why aren't open-source models a hundred times cheaper? Let's explore the Pareto frontier.

META
- Date: 2026-09-15. Language: en. Published. Machine translation from cs-CZ.
- URL: `/en/2026/proc-open-source-modely-nejsou-stokrat-levnejsi/`.
- Full source: `source.md`; translation source: `interactive\translations\en\2026\proc-open-source-modely-nejsou-stokrat-levnejsi.article.md`.
- Czech source SHA256: `1d877be4260b8e96093556b13d47fd471d0608ebba87812cd2eb591fd7f9532c`; translation status: current.
- Follows [open models and your own hardware](/en/2026/vlastni-model-vlastni-server/): model choice versus operation. Now: price versus quality across models.
- Thesis: openness probably lowers prices, but not dramatically by itself. A hundredfold saving needs comparison of the same work, quality, settings, and full costs.
- Precise term: open weights, downloadable and runnable under license; not necessarily fully open source. Both open and closed models can be commercially provided.

## 01 Pareto frontier
- Image: `../../../images/2026/2026-09-15-paretova-hranice-modelu.png`; Artificial Analysis snapshot, September 15, 2026. Commentary describes this image, not changing live data.
- [Interactive chart, same selection](https://artificialanalysis.ai/?models=gemini-3-5-flash-lite%2Cglm-5-3-flash%2Cgpt-6-astra%2Cclaude-fable-5-1%2Cgpt-5-6-luna%2Cmuse-glimmer%2Cdeepseek-v4-pro%2Cgemini-3-8-flash%2Cqwen3-8-2-4t-a95b%2Cmuse-spark-1-3%2Cqwen3-8-27b%2Cclaude-opus-5%2Cgpt-5-6-terra%2Cgrok-4-6%2Cclaude-fable-5%2Cglm-5-3%2Cgpt-5-6-sol%2Cdeepseek-v4-1-flash%2Cmistral-medium-3-5%2Ckimi-k3%2Cinkling%2Cclaude-fable-5-1-low%2Cclaude-sonnet-5-high%2Cclaude-4-5-haiku-reasoning%2Cgpt-6-astra-medium%2Cgpt-5-6-luna-medium%2Cgemini-3-1-pro-preview%2Cgemini-3-8-flash-medium%2Cqwen3-8-flash-next#intelligence-comparison-tabs). More models/settings can be added.
- Y: aggregate Intelligence Index; higher is better. X: USD per benchmark task, not per million tokens; left is cheaper.
- X logarithmic: $0.10→$1 is the same multiple/distance as $1→$10.
- Dotted frontier connects non-dominated choices. Dominance: alternative at least as good on both criteria, strictly better on one; cheaper at equal/higher quality, or better at equal price.
- On frontier, improving one criterion means sacrificing the other. No winner for every budget/task; no single best price/performance ratio.
- Score 50 does not mean twice the usefulness of 25. Set required quality first.
- Connecting lines aren't purchasable models or guaranteed mixtures. Guide to measured options, not a physical law.

## 02 Two economic layers
- Operations: GPU, memory, interconnects, power, datacenter, software, staff; provider compensation and unused-capacity risk. Conventional cloud economics.
- Weights: research, data, training, post-training, value of the result. Closed: pay owner/partner for access. Open: potentially no ongoing license payment, if permitted by license.
- Open development wasn't free; funding differs. Removing a weights license fee doesn't remove hardware work.
- API invoices don't separate layers. Price need not equal token-generation cost plus weights margin: competition, capacity, strategy, customer acquisition; temporarily below cost possible.
- Economies of scale: demand across applications/time zones, larger batches, caching, specialists' costs spread across volume.
- Previous measurement with cache: concurrency 1→50 yielded about 5.5× aggregate capacity; each request slower.
- Need utilization concurrently and over time, not an idle GPU every evening. Near-24×7 work helps; exactly continuous operation is not a universal break-even condition.
- Decisive: useful work at acceptable latency. Both open/closed providers benefit from scale; removing their margin doesn't give me their operating costs.

## 03 Small isn't large without a margin
- Small open versus expensive frontier changes the product, not just license: hardware and capability classes.
- B = billion; T = trillion; 2T = two trillion. Single-digit B→single-digit T: roughly three orders of magnitude.

| Illustrative parameters | Compared with 3T |
|---|---:|
| 3B = 3 billion | 1,000× fewer |
| 30B = 30 billion | 100× fewer |
| 300B = 300 billion | 10× fewer |
| 3T = 3 trillion | baseline |

- [Kimi K3 model card](https://huggingface.co/moonshotai/Kimi-K3): 2.8T total, 104B active/token.
- MoE: active parameters affect compute; all weights must fit somewhere. Memory bandwidth limits loading needed weights/cache work; not every expert loaded for every token.
- [Prefill/decode disaggregation](https://docs.nvidia.com/dynamo/v1.0.0/design-docs/disaggregated-serving): input often compute-bound, generation memory/bandwidth-bound. Large serving, unlike home use: separately configured hardware and independent scaling can help, but KV-cache transfer must justify its cost.
- [MoE/reasoning experiments](https://arxiv.org/html/2508.18672v3): more parameters at high sparsity help knowledge storage; reasoning also needs active compute and training data/parameter. Sparsity can't rise arbitrarily without capability impact; no universally optimal ratio, endlessly adding inactive experts insufficient.
- Size isn't a precise inference price or automatic quality measure. Architecture, training, quantization, task matter; smaller specialist may beat larger generalist.
- 100× parameters does not guarantee 100× inference cost, but still substantially different hardware/capability classes.

### Reveal: laptop feasibility
- Weights only, 30B: about 15 GB at four bits or 60 GB at two-byte BF16. Excludes KV cache, activations, quantization metadata, runtime overhead. 3B: one tenth; 3T: 100×.
- Single-digit B can fit smaller devices; tens of B need more memory. Dedicated GPU isn't the only route: large unified memory or RAM offload; speed, context length, battery tradeoffs.
- "Fits" ≠ "I want to work with it"; neither proves suitability for frontier coding-agent tasks.
- Cheap small models can be excellent; include cheap closed-weight models too.

## 04 Efficiency versus the weights premium
- Snapshot: closed Astra/Fable at top; capable open GLM-5.3/Kimi K3 below.
- Author's hypothesis: technical lead may deliver equivalent quality with less compute, shorter reasoning, optimized serving; lower hardware costs can offset some closed-weights premium.
- [2025 media estimates](https://techcrunch.com/2025/11/04/anthropic-expects-b2b-demand-to-boost-revenue-to-70b-in-2028-report/): leading provider around 50% gross margin.
- [September 2026 report](https://money.usnews.com/investing/news/articles/2026-09-13/anthropic-tells-investors-it-will-be-profitable-for-second-straight-quarter-ft-reports): over 80%, before distribution partners' shares and training costs; Reuters did not independently verify. Ballpark estimates, not an audited time series for one API.
- [AWS FY2025](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Fourth-Quarter-Results/default.aspx): revenue $128.7B, operating income $45.6B; operating margin about 35%. Not GPU-rental gross margin; cannot subtract unlike margins to infer weights pricing.
- Illustrative model: closed-service total modeled margin 50%/80%, including serving compensation and model premium. Open API: 30% serving margin.
- Same cost basis, not company-account reconstruction. Purchased cloud compute may already include infrastructure margin; don't double-count.
- Same work, direct inference cost: closed 100 units, open 15% higher = 115. Open price at 30% margin: 115/0.70 = 164.29, not 149.50 from a 30% markup.

| Closed-service total modeled margin | Closed price | Open price, 30% serving margin | Closed/open ratio |
|---|---:|---:|---:|
| 50% | 200 | 164.29 | 1.22× |
| 80% | 500 | 164.29 | 3.04× |

- Closed decomposition at cost 100: serving alone at 30% margin = 142.86; 100 inference + 42.86 operator compensation. Model premium: 57.14 to reach 200, or 357.14 to reach 500; not pure profit, funds development/training/other costs.
- 15% efficiency difference and 30% serving margin: assumptions, not endpoint measurements. Equal efficiency: price ratio 1.4×–3.5×; open 15% costlier: about 1.2×–3×. Potentially worthwhile, nowhere near 100×.

## 05 Tokens versus completed work
- Compare token consumption for same work: input, reasoning, repeated context, retries, output. Half output-token price with 3× output tokens = 50% higher output cost, excluding input/cache.
- AA data available during preparation, max settings:
  - [Kimi K3](https://artificialanalysis.ai/models/kimi-k3): about 160M output tokens per Intelligence Index run; output $15/M.
  - [GPT-5.6 Sol](https://artificialanalysis.ai/models/gpt-5-6-sol): about 90M; output $20/M.
  - Both around $2 per weighted benchmark task: Kimi cheaper tokens, greater consumption.
  - [Opus 5](https://artificialanalysis.ai/models/claude-opus-5): about 140M output; much smaller consumption gap. Don't generalize Kimi using multiples of all closed models' tokens; comparator/settings matter.
- [Cost per Intelligence Index Task methodology](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index): weighted average of individual evaluations' per-task costs; index weights and billed input/cache/reasoning/answer tokens. Can't derive X-axis by simply dividing aggregate output totals.
- Benchmark-task cost ≠ successfully solved business-case cost; quality on second axis. Failed agent still bills tokens without finishing work.
- Self-hosting: substitute full own operating costs for API prices. Chart alone doesn't price Kimi on my cluster.

## 06 What the snapshot shows
- Frontier mixes open/proprietary vendors. Peak Astra/Fable around score 53; GLM-5.3/Kimi 44–45, Sol 47, Opus 5 around 51.
- Open models may equal/beat closed on specific tasks; this benchmark ranks them as above. Use cases differ, but author doesn't expect dramatically different results.
- Kimi, GLM-5.3, Sol around $2/task; Opus around $6 with higher score. Kimi may be a sensible tradeoff, not proof of the same result at one-third the price.
- Luna medium around $0.016/task, score 25.5 versus Sol's 47. Over 100× price difference within one closed-model vendor, but different quality.
- Open GLM-5.3-Flash: frontier point around $0.25, score 42. Not the GLM-5.3 max variant.
- Author's assessment at writing:
  - **OpenAI**: well-balanced portfolio, small Luna/Terra to large, highly capable Sol/Astra.
  - **Anthropic**: excels at high end; more affordable options off frontier. Haiku way off, Sonnet not great, Opus losing price optimality too.
  - **Google**: high-end Gemini Pro out of the running; midrange Gemini 3.8 Flash on frontier; lower-end 3.5 Flash-Lite out.
- Both weight types occupy interesting positions; some alternatives cheaper and more capable regardless of license. "Open = cheap, closed = expensive" fails.

## 07 My own frontier
- AA chart starts selection, doesn't finish it. Aggregate task weights may differ from my application repeatedly doing one thing a smaller model excels at.
- Own examples and clear quality/error bar; compare cheap/strong, open/closed, sensible reasoning settings.
- Measure entire bill for completed work: every attempt, tools, fallback, human corrections.
- Own evaluation suites and training environments (RLE) important for future; see [evals as the most valuable asset](/en/2026/evals-nejcennejsi-aktivum/).

VERDICT
- Biggest price gap isn't open versus closed; choose **just right for my task**, not too dumb (cheap) or unnecessarily smart (expensive).
