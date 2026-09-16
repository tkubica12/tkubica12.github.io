---
format_version: 1
title: "An open AI model has many advantages. Most of them do not require your own hardware."
eyebrow: "Open weights, self-hosted inference, and money"
subtitle: "Open weights give you control. But who pays for the GPU when it has no work? Let's explore the advantages of open-weight models, try running them, and calculate the costs of our own server, a cloud VM, and a ready-made API."
slug: vlastni-model-vlastni-server
date: 2026-09-14
language: en
source_language: cs-CZ
source_slug: vlastni-model-vlastni-server
translation: machine
translated_from_hash: 8d4bcb653240b8bf8a6a3fce671aa57b68ccdef84a54964ef5fa17bcd3bc3515
translation_status: current
status: experimental
published: true
canonical_url: "/en/2026/vlastni-model-vlastni-server/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

Why might I want to use an open model? More control over what I run and where I send data. Fewer restrictions during authorized cybersecurity work or AI development. Less dependence on a vendor. The option to achieve lower latency. And finally, what probably sounds the most tempting: **couldn't it be cheaper?**

To me, these are good questions. They just sometimes get rolled into one big conclusion: we need our own server. But I don't think that holds in most cases, and that is what we will unpack today. Some advantages come from choosing the model, others from running inference myself, and only some actually require hardware on my premises.

Let's go through those expectations first. Where does an open model help, and which benefits also depend on a particular way of running it? And which, on the other hand, are universal advantages of an open-weight model regardless of how I get it? Is it cheaper to have a model on my own hardware at home, on rented cloud hardware with a reservation, to switch hardware (a VM) on for batches as needed, or to go with token-as-a-service, paying per token? Let's try measuring and calculating that properly — accounting for load and utilization, batch size, and other aspects will be crucial.

::: group id="co-od-modelu-chci" title="Part one: what do I actually expect from an open model?"

::: card number="01" title="Let's separate the model from where it runs"
I can use an open model through a ready-made API and pay for tokens. I can run the same model on a GPU virtual machine in Azure. Or I can buy a server and run it on my premises.

**The model can be the same. What differs is who handles operations and who pays for unused capacity.**

Throughout this article, I will mainly use the term **open weights**: I can download the weights and run them under the terms of the license. That is not automatically the same as fully open-source AI under the [OSI definition](https://opensource.org/ai/open-source-ai-definition). For example, the data used to train the model might not be open — we will come back to that when assessing security. For our discussion, what matters is precisely the ability to run it ourselves.
:::

::: card number="02" title="I want control and don't want to depend on a single vendor"
This is where I am a fan of open models. I can keep a specific version, change the runtime, quantization, or cache, or add my own adapter. I don't have to wait for the provider to expose such an option through its API.

And if the vendor shuts down the API? Either there are plenty of others, or I can take the downloaded weights and spin up a GPU somewhere else.

If the team developing the model shuts down, I retain today's capabilities. **That does not automatically give me its future innovations.** And switching to a different model is not just changing a URL, either: tool calling, response formats, or quality on my task may behave differently.

None of that requires me to buy a server, though. The same model is offered by large providers as well as smaller and local ones, or I can run inference on my own VM — so we have the option to move elsewhere relatively easily, and I retain the flexibility to change anything at any time (provider, hardware type, region).

On June 12, 2026, Anthropic disabled Fable 5 for all users following a **US export directive**; it restored global access on July 1. [It explains](https://www.anthropic.com/news/redeploying-fable-5) that it was unable to verify users' nationality in real time to apply the restrictions selectively. This was not an ordinary server outage. Downloaded open weights reduce dependence on this kind of off switch for a particular service, but they are not an exemption from laws or export rules.

Although it is hard to hide weights once they are on the internet, access to them does not mean you can use them without restrictions. Companies and governments can contractually prohibit Chinese models in their contracts, and a government can restrict use in healthcare or when working with children, for example. You may end up with a model you can only use for "personal use."
:::

::: card number="03" title="I don't want the model needlessly stopping my legitimate work"
Imagine I am doing an authorized penetration test or analyzing logs from a compromised system. I need to work with offensive techniques too, otherwise I can hardly understand the incident. Or I may be doing research in AI or biology. A filter can see a dangerous topic and stop the work or switch me to a less capable model, which can be limiting.

**An open model does not automatically mean a model without guardrails.** Refusal behavior can be learned into its weights. The application, license, or infrastructure operator can add further restrictions.

::: reveal title="Fable, Opus, and some AI development tasks"
[Anthropic explicitly describes](https://support.claude.com/en/articles/15363606-why-claude-switched-models-in-your-conversation-with-fable-5-or-fable-5-1) blocking or falling back to Opus for some offensive cybersecurity techniques in Fable 5 and 5.1. It also mentions a narrow group of frontier LLM development tasks: distributed training infrastructure, ML accelerator design, or kernels for some nonstandard chips.

This is not a ban on all AI development or defensive security. But the checks also assess loaded files and other context, so the problem need not be just what I typed into the last prompt. The provider acknowledges false positives; Opus has its own safeguards too, and a fallback does not guarantee an answer. A verification program exists for some legitimate defensive scenarios. Behavior and fallback settings also differ between the application and the API.

For a security lab or research team, a suitable open model can be an important alternative. That does not remove responsibility or the need to verify its quality. And again: an API service or self-hosted serving on a cloud VM may be enough.
:::
:::

::: card number="04" title="I want control over my data. Is it safer on my premises?"
Running inference myself lets me decide where data flows, who sees it, and what gets stored. That is a real advantage, but it does not mean that using a per-token API automatically gives someone access to my data, or that a cloud operator must be able to see inside my VM. An API can have a [zero retention policy](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) that limits data retention for supported features and under agreed conditions. **Confidential computing**, in turn, can protect data in memory even from a privileged infrastructure operator. These are different protections — zero retention alone does not mean the service never processes data during inference.

What differs is how much I configure and take responsibility for myself. But that does not tell us which option is more or less secure; it depends on the details.

And let me return to training data: open weights alone do not reveal its origin and are not proof that the model has no undesirable or covertly conditional behavior (such as a so-called sleeper agent). The location of the server does not resolve this question of trust in the model on its own.

If a suitable region, private access, and the service's contractual terms meet my needs, sensitive data does not automatically force me on-prem.

::: reveal title="What about confidential computing and jurisdiction?"
[Confidential computing, including GPU VMs](https://learn.microsoft.com/en-us/azure/confidential-computing/confidential-vm-overview), can protect data even while it is in use. But I need a supported platform, correct configuration, and attestation.

Even this technology does not eliminate application bugs or authorized data exports. And a European region alone does not resolve every jurisdiction question. To me, it is better to describe the specific threat and defense than to argue over which label is safer.
:::
:::

::: card number="05" title="I want lower latency. Or to work entirely without the internet"
Running the model myself lets me reserve capacity for my application and tune it for a fast response rather than the maximum number of tokens per day. In other words, I can influence inference parameters and prioritize more tokens per second for one request at the expense of total capacity. Typically, I reduce batch size: an individual request runs faster, but the cost per token can rise significantly.

Commercial providers offer similar choices. For example, [Claude fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) uses the same weights with faster inference settings at a higher price. It is not a different, smarter model. However, Anthropic does not describe the specific implementation as merely reducing batch size, and the speedup mainly concerns token generation, not time to first token.

Besides the network, I also wait in a queue, for input processing, and for response generation. A well-run remote API can beat a small local server. With voice or many short agent steps, on the other hand, I will notice network round trips more than with a single long response.

**When I want to control latency, my own cloud VM may be enough. When I have to work without the internet, it isn't.** That is where an on-device model or a local server makes sense.

But where a system must not have internet access, I often do not need an LLM at all. An attack drone can use "AI" in the form of computer vision; for that task, it does not need to discuss the differences between the approaches of Plato and Socrates. Offline AI is therefore not automatically an argument for a local large language model.

With a laptop, I would first check whether a smaller model can handle my task at all. It may be excellent for extraction or classification; a complex coding agent is a different assignment. **For the coding I expect from an agent, I find anything that can run on a laptop completely unusable.** That is my bar for this way of working, not a claim that a small model cannot write a useful function.

I think open models such as [GLM 5.3](https://huggingface.co/zai-org/GLM-5.3) or [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3) are amazing, but they are not in the laptop league. They are not both the same size, either: the published GLM 5.3 weights have approximately 753 billion parameters, while Kimi K3 has 2.8 trillion. To run them efficiently, I need large multi-GPU systems, and for the largest models a cluster whose price will be in the tens of millions of Czech crowns. The hardware Moonshot AI recommends for running Kimi K3 comes to almost 100 million Czech crowns.

::: reveal title="Roughly how much does hardware for a 2T model cost?"
For orientation, I will take a model with two trillion parameters, or 2T. The weights alone need approximately **4 TB in BF16, 2 TB in an eight-bit representation, and 1 TB in a four-bit representation**. This is rough memory arithmetic excluding cache, activations, quantization metadata, and other overhead. With MoE, only some experts are used for one token, but I still have to keep the other weights somewhere.

A specific [Thinkmate configurator](https://www.thinkmate.com/system/gigabyte-g894-sd1-aax5) shows a complete server with **8× B200 and 1.44 TB of HBM for USD 538 120**. At a purely illustrative exchange rate of CZK 22/USD, that is about 11.8 million Czech crowns. This is neither a current exchange rate nor a binding quote including Czech VAT.

| Representation of 2T weights | Weights alone | Minimum number of eight-GPU B200 servers by total HBM | Their indicative price |
|---|---:|---:|---:|
| 4bit | 1 TB | 1 | CZK 11.8 million |
| 8bit | 2 TB | 2 | CZK 23.7 million |
| BF16 | 4 TB | 3 | CZK 35.5 million |

**These are not recommended configurations or measured performance.** The counts are only a lower bound based on memory. A particular runtime may need more GPUs because of overhead, supported model partitioning, context, batch size, and the required speed. Server interconnects, power, cooling, and operations are additional items. Offloading to RAM or disk can reduce the HBM required, but then I have to calculate cost and speed in a completely different way.

For comparison: [for the 2.8T Kimi K3, Moonshot recommends a supernode with 64 or more accelerators](https://www.kimi.com/news/kimi-k3) for inference efficiency and high-speed communication. Eight of the servers above, or 64 B200s, add up to about **CZK 94.7 million**, still excluding additional cluster infrastructure. Moreover, eight HGX servers do not by themselves make one NVLink supernode; this is a price illustration for the same number of GPUs, not a verified Kimi deployment design.

:::
:::

::: card number="06" title="I want a model that costs less"
Here I would first separate two kinds of savings. **Choosing a cheaper model is not the same as running the same model more cheaply.**

For many tasks, I can take a smaller open model with a cheap API instead of an expensive frontier model and save money. If it can do the task, why not? I get the savings immediately, without buying a GPU. But the license alone does not guarantee them: they depend on pricing, quality, the number of attempts, and how much work a human ultimately has to finish. Typically, we talk about the so-called Pareto-optimal frontier: models offering the best price-performance trade-off. For example, the very inexpensive GPT 5.6 Luna is on this frontier — a closed-source model does not necessarily have a poor price-performance ratio. Similarly, current Mistral models are quite far from that frontier — they are open, but their results relative to hardware requirements are not as good as those of others.

The second question is different: once I have chosen a model, is it cheaper to buy its tokens as a service, run it on IaaS, or buy my own hardware?

And that is exactly what I want to calculate in the second part. We have covered control, security, and restrictions. Now I will not justify a server with other advantages — I am interested in **the price of the same work**.
:::

:::

::: group id="kolik-stoji-provoz" title="Part two: the same model, three ways to pay"

::: card number="07" title="What I ran on an A100"
I tested both Mistral and Nemotron, but from here on I will only discuss **NVIDIA Nemotron 3.5 Lightning 30B-A3B in BF16**. The comparison principle also applies to other models; the specific speed and break-even thresholds obviously do not carry over.

I used an Azure `Standard_NC24ads_A100_v4` VM with one **A100 80 GB PCIe** and vLLM 0.28.0. Each request had 16 384 input and 512 output tokens. I tried 1, 5, 10, 20, 50, and 100 concurrent requests, each with and without a repeated prefix. Each combination was repeated three times — 36 measurements and 4 017 successful requests in total.

The shared-prefix variant simulates a coding agent repeatedly working in one project: I resend instructions, tools, and part of the context (so this is a test with a large proportion of cached tokens). Without a shared beginning, the model does more work on new input (the uncached scenario).

::: reveal title="Cache: resending the same input isn't free"
In both scenarios, I send the same number of input tokens and generate the same number of output tokens. With [prefix caching](https://docs.vllm.ai/en/v0.28.0/features/automatic_prefix_caching/), the state of an already processed beginning is reused. **This is not a finished answer from a cache; the output is still generated.**

The shared prefix has 12 288 tokens, or 75% of the input. However, this hybrid attention/Mamba runtime stores cache in blocks of 2 096 tokens. It reuses five complete blocks, or 10 480 tokens. I therefore measured approximately **63.96% token hits** at concurrency 5 through 100 and 62.75% with one stream, including the initial misses. Without a shared prefix, there were no hits.

This is local reuse. **How many tokens the API will bill at a lower rate is a separate question.** I did not measure its granularity, routing, TTL, or actual hit ratio. In the financial calculations, I therefore select measured performance and the API billing assumption separately.
:::

::: reveal title="Methodology and limits of the comparison"
I use raw completions without a chat template, synthetic code content, and a forced 512 output tokens while ignoring EOS. New requests are launched for 120 seconds, then we wait for the outstanding ones to complete; throughput includes this drain time. Each client immediately sends another request after completion.

The weights occupied 58.93 GiB of GPU memory. I ran a BF16 model with a pinned revision and vLLM image; I did not enable speculative decoding. I do not know the internal precision, quality, or speed of the actual API. On its side, I am only pricing the same volume of tokens. Below, I derive the performance of a potential purchased server from the measured Azure A100; this is not a second physical measurement.
:::

The A100 is a fairly old card; I did not have another one available — but I think that is fine for an order-of-magnitude comparison on a small model, and the trend we get a feel for here will be similar for larger models and newer cards.
:::

::: card number="08" title="Batch size: more work at once, but not for free"
Let's imagine the GPU is serving only me. It loads weights and generates tokens one by one. When it serves more requests together, it can make better use of work over the same weights. **Batch size is the size of that jointly processed batch.**

Modern serving uses *continuous batching*: completed requests leave and new ones keep arriving. From the outside, I set **client concurrency**, not a fixed size for every internal batch. Concurrency 50 does not mean 50 registered users, either, but 50 requests in progress at the same time.

What did that do to economically useful capacity? The tables show **aggregate output tok/s for the entire card**, not one person's speed. TTFT is time to first token; all figures are averages of three repetitions.

::: tabs id="nemotron-vykon"
::: tab id="vykon-cache" title="Shared prefix"
| Concurrency | Output tok/s | TTFT | Full response time |
|---|---:|---:|---:|
| 1 | 148.2 | 0.39 s | 3.45 s |
| 5 | 294.3 | 1.35 s | 8.70 s |
| 10 | 398.2 | 2.24 s | 12.86 s |
| 20 | 591.9 | 3.16 s | 17.29 s |
| 50 | 820.1 | 4.73 s | 31.17 s |
| 100 | 788.2 | 15.83 s | 60.58 s |
:::
::: tab id="vykon-bez-cache" title="Unique inputs"
| Concurrency | Output tok/s | TTFT | Full response time |
|---|---:|---:|---:|
| 1 | 132.2 | 0.81 s | 3.87 s |
| 5 | 228.2 | 2.70 s | 11.21 s |
| 10 | 289.6 | 3.12 s | 17.67 s |
| 20 | 371.2 | 4.20 s | 27.17 s |
| 50 | 409.4 | 17.72 s | 59.90 s |
| 100 | 389.6 | 64.48 s | 109.97 s |
:::
:::

With cache, going from one to fifty streams gave me approximately **5.5 times the total capacity**. But an individual's response takes longer. At one hundred, throughput actually falls. So "I'll add a bigger batch and get cheaper" does not hold forever.

To me, this gives us a simple rule for the calculator: **I can only count capacity whose latency still meets my needs.** An overnight batch and an interactive assistant are different scenarios, and each calls for a different batch size.
:::

::: card number="09" title="Utilization: who will be working on it on Sunday evening?"
Now for the second axis. **Concurrency tells me how much work I do at once. Time utilization tells me how long I have that work at all.**

One hundred percent of the time at one stream is not the same volume as one hundred percent at fifty. And a reading from `nvidia-smi` answers neither of these economic questions. What matters to me is completed useful work across which I can spread the costs.

Eight hours, five days a week is only **23.8% of the calendar**. And even then I would have to maintain the selected concurrency nonstop during working hours. But people attend meetings, agents wait for tools, and demand fluctuates. Sixty percent utilization means over a hundred hours of work per week. For that, I already need something like multiple time zones, multiple applications, or an overnight task queue.

This is where a large provider has a practical advantage: it combines demand from many customers. When I finish, someone else starts. My own server will not acquire such a queue of work by itself.

Economies of scale can give a provider substantially lower costs: cheaper hardware, a more efficient datacenter, custom kernels or inference chips, or better-tuned solutions (for example, prefill/decode disaggregation or speculative decoding). More on that below.

::: reveal title="Why a provider need not be just an expensive GPU reseller"
Removing its margin does not give me its costs. It may buy hardware on better terms, run a datacenter with a lower PUE, and spread specialists' work across a large volume. **PUE is the ratio of total datacenter energy to IT energy**: at PUE 2, energy overhead adds another 100% of the server's consumption. A lower PUE reduces this overhead, not the whole inference price by the same ratio.

It also has room to tune serving itself:

- **Batching, cache, and routing.** It groups suitable requests and sends them where usable context already exists. More customers does not mean sharing their private data; shared capacity alone brings a benefit.
- **Separate prefill and decode.** Processing long input and generating incrementally have different demands. They can run on separate pools or clusters and scale independently, rather than competing for the same resources.
- **Speculative decoding.** A small draft model or another cheap mechanism proposes several tokens ahead. The main model verifies them together. When the proposals often match, generation can speed up; when they do not, the extra work can even hurt.
- **Optimization close to the hardware.** Custom CUDA/Triton kernels for NVIDIA GPUs, better memory handling, quantization, or specialized inference hardware. Support for the particular model and acceptable quality remain prerequisites.

[NVIDIA Dynamo describes disaggregated serving](https://docs.nvidia.com/dynamo/v1.0.0/design-docs/disaggregated-serving), including KV cache transfers between prefill and decode engines. Transfers have a cost, so this is not automatically a win for every workload. [Fireworks mentions custom kernels and separate serving pools](https://fireworks.ai/inference) and [documents speculative decoding](https://docs.fireworks.ai/deployments/speculative-decoding), including the risk of an unsuitable drafter.

I can deploy some of these techniques too. They are not magic reserved for clouds. The difference is whether I can and want to develop, operate, and pay for them for a single server. I am not claiming that the particular Nemotron endpoint uses all of them, nor am I assigning it an invented performance multiplier based on them.
:::
:::

::: card number="10" title="What I put into the calculator"
I compare five years and three ways of running the same model. For the VM, I also distinguish between switching it on only for a batch and holding capacity long-term.

| Option | Pricing assumption |
|---|---|
| API, pay per token | USD 0.06 / 0.01 / 0.22 per million regular input / cached input / output tokens |
| Azure VM PAYG | USD 4.775 for every allocated hour |
| Azure VM, three-year reservation | USD 46 567 for three years; I extrapolate the same rate to five years: **USD 77 611.67** |
| Own server | Purchase USD 45 000 + five years of maintenance and energy: with continuous work **USD 64 834.80** |

The API rate is the [public Fireworks on Foundry reference](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/fireworks/) from a September 3, 2026 snapshot.

Cloud reservation and ownership are not orders of magnitude apart here. The difference comes to **USD 12 776.87 over five years**, or about **USD 2 555 per year**. That is how much room is left for additional on-prem costs relative to the VM before the modeled lead disappears.

::: reveal title="Why I am sticking with five years"
An older GPU need not be worthless in three years. [The report on Huang's response to rising H100 rental prices](https://stocktwits.com/news-articles/markets/equity/nvda-rises-overnight-after-strong-week-ceo-jensen-huang-pumps-nvidia-chips-as-highly-rentable-money-minting-assets/cZt3ZqARJxw) is an interesting signal of continued demand. But the price of around USD 3.28/h in it is a per-GPU rental price, not the price for a complete eight-GPU server; [Ornn Data](https://ornn.com/product/ornn-data) describes the methodology of such indices.

Rental prices are not the same as a used server's resale price or accounting depreciation. I use five years as a planning horizon, not a proven useful life or payback period. I do not include residual value, and I hold the same rates and performance throughout the period. This is a comparison model, not a market forecast.
:::
:::

::: card number="11" title="When does running it myself become cheaper?"
Let's change one thing at a time: **how well I use the time I pay for, and how many requests I process at once**. In both scenarios, I use a local shared prefix and assume that the API bills **64% of input tokens as cheaper cached tokens**. I pay the regular rate for the remaining input; output is generated and billed separately.

::: tabs id="nemotron-penize"
::: tab id="penize-vyuziti" title="1. Utilization over time"
In this scenario, I compare costs for **1 000 identical requests at concurrency 50 during processing** and look at how utilization of paid time changes the price. **I start the VM and leave it allocated until the work is complete. So I also pay for gaps when it is waiting for more work.**

At 100% utilization, work follows on without gaps. At 10% utilization, the server works productively for only one tenth of its allocated time — completing the same work takes ten times as much paid time. When it works, I maintain the same measured rate at concurrency 50. So I am not changing batch size or assuming the GPU itself computes ten times more slowly.

For the reservation and my own server, I spread the five-year costs across all work over that period and convert the result to the same 1 000 requests. This is a unit price at a given utilization, not buying a server just for a thousand requests.

| Utilization of paid time | API, 64% of input cached | Reserved VM | Modeled on-prem | PAYG VM including waiting |
|---|---:|---:|---:|---:|
| 100% | 0.5714 | 0.3073 | 0.2567 | 0.8281 |
| 90% | 0.5714 | 0.3415 | 0.2828 | 0.9201 |
| 60% | 0.5714 | 0.5122 | 0.4133 | 1.3802 |
| 40% | 0.5714 | 0.7683 | 0.6090 | 2.0703 |
| 20% | 0.5714 | 1.5365 | 1.1962 | 4.1406 |
| 10% | 0.5714 | 3.0731 | 2.3705 | 8.2812 |

All in USD. **At full utilization, both the reservation and on-prem are cheaper. At 40%, both are already more expensive than the API.** The reservation breaks even with the API at 53.78%, and modeled on-prem at 42.74%.

Specifically: a thousand requests need approximately **10.4 minutes of productive runtime**. At 100% utilization, I pay about **USD 0.83** for PAYG. At 10% utilization, the VM is allocated for approximately **104 minutes**, and I pay about **USD 8.28**. Startup and model loading would add more paid time, which I have not yet included here.

**The API always costs the same for the same tokens. My own inference gets more expensive when I pay for time in which it does no useful work.** I pay for the reservation continuously, keep my own server powered on and idle outside productive work, and PAYG bills every allocated hour.
:::
::: tab id="penize-soubeh" title="2. Request concurrency"
In this scenario, I again compare the price of **1 000 identical requests**, but keep **100% time utilization** and change concurrency. This lets me examine the effect of batch size on the economics of self-hosted inference versus the API. The server has work nonstop; what differs is how many requests it serves at once and how quickly it completes them overall.

Local prefix caching remains enabled. For the API, I still assume that **64% of input tokens receive the cheaper cached-token rate**.

| Concurrency | API, 64% of input cached | Reserved VM | Modeled on-prem | PAYG VM |
|---|---:|---:|---:|---:|
| 1 | 0.5714 | 1.7005 | 1.4206 | 4.5826 |
| 5 | 0.5714 | 0.8563 | 0.7154 | 2.3076 |
| 10 | 0.5714 | 0.6329 | 0.5287 | 1.7056 |
| 20 | 0.5714 | 0.4258 | 0.3557 | 1.1473 |
| 50 | 0.5714 | 0.3073 | 0.2567 | 0.8281 |
| 100 | 0.5714 | 0.3197 | 0.2671 | 0.8616 |

All in USD per 1 000 requests with continuous work. **Among the measured points, modeled on-prem first beats the API at concurrency 10, and the reserved VM at concurrency 20. PAYG does not beat it at any of them.** I have not measured the exact break-even point: on-prem changes places between concurrency 5 and 10, and the reservation between 10 and 20. I do not want to invent a precise batch size from these few points.

**So having work all the time is not enough. I also need enough work at once.** And a hundred is not economically better than fifty, because measured throughput is already falling. Also, at concurrency 50, I wait 4.73 s for the first token; at concurrency 100, it is already 15.83 s.
:::
:::

In short: **self-hosted inference needs enough work both over time and at once.** The API's cached-token discount also affects the result: the cheaper it makes the API, the more work I need for self-hosting to pay off.

Without a shared prefix on either side, at the measured concurrency of 50, the required utilization is **56.18%** for the reservation and **44.73%** for on-prem. Similar percentages, but different capacity and significantly worse latency: the first token takes 17.72 s.

::: reveal title="Just two days a month: does turning on a PAYG VM make sense?"
If I turn on the VM for 48 hours and can keep it supplied with work at concurrency 50 with a shared prefix throughout, compute costs **USD 229.20**. The API for the same work, assuming 64% of input is billed as cached, costs **USD 158.15**. At half utilization within those 48 hours, I do half the work but still pay USD 229.20 for the VM; the API costs only half as much.

So in our scenario, PAYG does not beat the API even at full utilization at any of the measured concurrency levels. Deallocating after the batch finishes removes the bill for the rest of the month, not the paid gaps during its processing. Startup and model loading also take time, and disks can cost money even after deallocation.

If I compare just the two VM rates, PAYG stops being cheaper than a reservation when allocated for more than **37.1% of the calendar**. What matters here is paid time, including waiting, not just productive work. This is a different break-even point from VM versus API.
:::

::: reveal title="The math, briefly"
```text
H = 43 800 hours over five years
u = productive share of the calendar
R = measured output tok/s × 3600 / 512
h = assumed share of input tokens billed by the API as cached
p = [16384 × ((1 − h) × 0.06 + h × 0.01) + 512 × 0.22] / 1 000 000
API = H × u × R × p
PAYG allocated throughout the comparison period = H × USD 4.775
reservation = USD 77 611.67
on-prem = USD 59 316 + H × u × USD 0.126
```

The fixed on-prem component includes purchase, maintenance, and idle energy. An active hour adds the active−idle difference, not all the energy again. Unit price is total cost divided by the number of requests. Above an attainable break-even threshold, the given fixed-cost option is cheaper; above 100%, the threshold is unattainable.

Approximately 54% at c50 means around 90 hours of work a week at that point's capacity, not 54% on a GPU monitor. If the application alternates between different concurrency levels, I have to sum the volume across those points. I cannot average concurrency and assume linear performance.
:::

:::

::: card number="12" title="What I take away from this"
I want open models among my options. For control, the ability to keep a version, custom behavior, and somewhere to go when a service no longer suits me. **But I do not need to buy a server for most of these advantages.**

And the money? For this model and workload, a cheap API works out better at low concurrency or with irregular work. When I have enough concurrent work for a large part of the week, self-hosted inference can pay off. Then I would primarily compare a reserved cloud VM with a genuinely complete on-prem budget, not the purchase price of a card with PAYG running forever.

Our working scenario, with 64% of input billed by the API as cached, needs, at concurrency 50, roughly **54% of time for the reservation and 43% for on-prem**. Meanwhile, on-prem's modeled lead over the reservation is only about USD 2.6 thousand a year for further differential costs. An operational estimate can turn that around quite easily.

So, to me: first choose a model that can do the work. Then state the control and responsiveness I need. And only then ask who will operate the GPU. **Not paying a provider's margin is a pleasant thought. Paying for my own unused server, less so.**
:::

:::

::: closing
Open weights bring many benefits, such as control, flexibility, and the ability to handle unusual situations, including political instability. Use them through an API from a trusted provider such as Microsoft. I think running them on your own server makes no sense at all for the vast majority of use cases - it is absurdly expensive.
:::
