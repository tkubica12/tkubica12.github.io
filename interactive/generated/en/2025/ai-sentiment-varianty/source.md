---
format_version: 1
title: "How to do simple AI text analysis? LLM, fine-tuning, BERT, or embeddings?"
subtitle: "Using short-text sentiment, I compare quality, cost, latency, and practicality across four approaches."
slug: "ai-sentiment-varianty"
date: "2025-07-08"
language: "en"
source_language: "cs-CZ"
source_slug: "ai-sentiment-varianty"
translation: "machine"
translated_from_hash: "2529476DF1D8021C6BB197EF980DCAB9416DF65D6BA146B1EE6E5F04C90B90F7"
translation_status: "current"
status: "experimental"
canonical_url: "/en/2025/ai-sentiment-varianty/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# How to do simple AI text analysis? LLM, fine-tuning, BERT, or embeddings?

Decades ago, natural-language processing was mostly about specialized models for relatively simple tasks. They were small, cheap to run, and you had to know what you were doing. Today we have large language models that can follow instructions and often do the same thing without training your own model.

Let's use sentiment as the lab task. I take a short social-media post and want to put it into one of three classes: **positive**, **negative**, **neutral**. This is not meant as an academic benchmark. It is the practical question: what should I use, how good will it be, how fast will it be, and how much will it cost?

::: callout type="note" title="Data and code"
I use a dataset with roughly 25 thousand human-labeled training examples, 6 thousand validation examples, and 5 thousand test examples. All details, including test and training code, are on my [GitHub](https://github.com/tkubica12/d-ai-sentiment/tree/main).
:::

::: group id="uvod" title="Introduction to the comparison"

::: card number="01" title="Four options side by side" default="open"
For the same classification task I have four practical paths. The next cards walk through each one, but here is a quick preview of what I will be comparing.

::: tabs id="approaches"
::: tab id="llm" title="LLM without training"
I instruct the model to return one class. I try almost-zero-shot and few-shot with 100 or 1000 examples. This is the simplest variant, but cost and latency grow with context length.
:::
::: tab id="ft" title="Fine-tuned LLM"
I take GPT-4.1 nano or mini and fine-tune it on 25 thousand examples. It is still a generative model, but now specialized for this task.
:::
::: tab id="bert" title="BERT encoder"
A classic encoder-only transformer is very natural for text classification. It is not generative, looks at the whole input bidirectionally, and returns a class.
:::
::: tab id="emb" title="Embeddings + LR"
I convert text into a vector with an embedding model and train simple logistic regression on top. The cloud provides a universal representation; the tiny local model decides the class.
:::
:::

::: summary-grid
- **Best accuracy**: fine-tuned GPT-4.1-mini, 80.0%.
- **Lowest cost**: embeddings + logistic regression, about $0.0005 per 1000 samples.
- **Lowest latency**: BERT, about 0.09 seconds per sample.
- **Easiest changes**: plain LLM, because I change the prompt, not the model.
:::
:::

::: card number="02" title="Results: accuracy, cost, and speed" default="closed"
The accuracy may not look amazing at first glance. Part of the reason is that the boundary between positive and neutral sentiment is often fuzzy. Some posts are simply labeled differently by different people.

**Classification quality**

| Group | Experiment | Model / approach | Strategy | Accuracy | Run cost | Time | Samples/s |
|---|---:|---|---|---:|---:|---:|---:|
| LLM | LLM_NANO_ZEROSHOT | GPT-4.1-nano | Zero-shot | 67.7% | $0.13 | 3306.7 s | 1.56 |
| LLM | LLM_NANO_FEWSHOT_100 | GPT-4.1-nano | Few-shot 100 | 68.6% | $1.45 (~$0.87 cached) | 4215.4 s | 1.23 |
| LLM | LLM_NANO_FEWSHOT_1000 | GPT-4.1-nano | Few-shot 1000 | 68.4% | $13.39 (~$8.03 cached) | 9160.4 s | 0.56 |
| LLM | LLM_MINI_ZEROSHOT | GPT-4.1-mini | Zero-shot | 69.3% | $0.55 | 3919.9 s | 1.38 |
| LLM | LLM_MINI_FEWSHOT_100 | GPT-4.1-mini | Few-shot 100 | 69.4% | $5.88 (~$3.53 cached) | 5565.6 s | 0.94 |
| LLM | LLM_MINI_FEWSHOT_1000 | GPT-4.1-mini | Few-shot 1000 | 68.4% | $55.53 (~$33.32 cached) | 16084.1 s | 0.33 |
| Fine-tuned LLM | LLM_FT_NANO_ZEROSHOT | GPT-4.1-nano FT | Zero-shot | 79.0% | $0.26 | 1907.0 s | 2.71 |
| Fine-tuned LLM | LLM_FT_NANO_FEWSHOT_100 | GPT-4.1-nano FT | Few-shot 100 | 78.4% | $2.90 (~$1.74 cached) | 1940.0 s | 2.66 |
| Fine-tuned LLM | LLM_FT_MINI_ZEROSHOT | GPT-4.1-mini FT | Zero-shot | 80.0% | $1.04 | 1564.2 s | 3.30 |
| Fine-tuned LLM | LLM_FT_MINI_FEWSHOT_100 | GPT-4.1-mini FT | Few-shot 100 | 79.3% | $11.58 (~$6.95 cached) | 1918.4 s | 2.69 |
| Embeddings + ML | LR_100 | OpenAI Embeddings + LR | 100 samples | 60.9% | $0.0025 | 963.2 s | 5.40 |
| Embeddings + ML | LR_1000 | OpenAI Embeddings + LR | 1000 samples | 67.1% | $0.0025 | 951.7 s | 5.47 |
| Embeddings + ML | LR_ALL | OpenAI Embeddings + LR | full dataset | 73.2% | $0.0025 | 932.1 s | 5.58 |
| Transformer encoder | BERT_SENTIMENT | BERT-base FT | full dataset | 74.5% | $0.028 | 465.4 s | 11.19 |

::: reveal title="Full token and completion measurements"
| Experiment | Completed | Failed | Total tokens | Input tokens | Output tokens |
|---|---:|---:|---:|---:|---:|
| LLM_NANO_ZEROSHOT | 5166 (99.3%) | 39 (0.7%) | 1,289,946 | 1,284,780 | 5166 |
| LLM_NANO_FEWSHOT_100 | 5165 (99.2%) | 40 (0.8%) | 14,470,776 | 14,465,611 | 5165 |
| LLM_NANO_FEWSHOT_1000 | 5166 (99.3%) | 39 (0.7%) | 133,890,834 | 133,885,668 | 5166 |
| LLM_MINI_ZEROSHOT | 5076 (97.5%) | 129 (2.5%) | 1,351,565 | 1,346,144 | 5421 |
| LLM_MINI_FEWSHOT_100 | 5140 (98.8%) | 65 (1.2%) | 14,688,863 | 14,683,620 | 5243 |
| LLM_MINI_FEWSHOT_1000 | 5088 (97.8%) | 117 (2.2%) | 138,814,519 | 138,809,163 | 5356 |
| LLM_FT_NANO_ZEROSHOT | 5166 (99.3%) | 39 (0.7%) | 1,289,946 | 1,284,780 | 5166 |
| LLM_FT_NANO_FEWSHOT_100 | 5166 (99.3%) | 39 (0.7%) | 14,473,578 | 14,468,412 | 5166 |
| LLM_FT_MINI_ZEROSHOT | 5166 (99.3%) | 39 (0.7%) | 1,289,946 | 1,284,780 | 5166 |
| LLM_FT_MINI_FEWSHOT_100 | 5165 (99.2%) | 40 (0.8%) | 14,470,685 | 14,465,520 | 5165 |
| LR_100 | 5205 (100%) | 0 | 124,123 | 124,123 | 0 |
| LR_1000 | 5205 (100%) | 0 | 124,123 | 124,123 | 0 |
| LR_ALL | 5205 (100%) | 0 | 124,123 | 124,123 | 0 |
| BERT_SENTIMENT | 5205 (100%) | 0 | N/A | N/A | N/A |
:::

::: reveal title="Cost per 1000 samples and latency"
**Cost per 1000 samples**

| Category | Experiment | Cost per 1000 samples | Rank |
|---|---|---:|---:|
| Cheapest | LR_100 | $0.0005 | 1 |
| Cheapest | LR_1000 | $0.0005 | 1 |
| Cheapest | LR_ALL | $0.0005 | 1 |
| Low | LLM_NANO_ZEROSHOT | $0.025 | 4 |
| Low | BERT_SENTIMENT | $0.028 | 5 |
| Low | LLM_FT_NANO_ZEROSHOT | $0.050 | 6 |
| Low | LLM_MINI_ZEROSHOT | $0.106 | 7 |
| Low | LLM_FT_MINI_ZEROSHOT | $0.202 | 8 |
| Medium | LLM_NANO_FEWSHOT_100 | $0.280 ($0.168 cached) | 9 |
| Medium | LLM_FT_NANO_FEWSHOT_100 | $0.562 ($0.337 cached) | 10 |
| Medium | LLM_MINI_FEWSHOT_100 | $1.130 ($0.678 cached) | 11 |
| Medium | LLM_FT_MINI_FEWSHOT_100 | $2.242 ($1.345 cached) | 12 |
| Expensive | LLM_NANO_FEWSHOT_1000 | $2.590 ($1.554 cached) | 13 |
| Expensive | LLM_MINI_FEWSHOT_1000 | $10.670 ($6.402 cached) | 14 |

**Latency**

| Category | Experiment | Time per sample |
|---|---|---:|
| Fastest | BERT_SENTIMENT | 0.09 s |
| Fast | LR_ALL | 0.18 s |
| Fast | LR_1000 | 0.18 s |
| Fast | LR_100 | 0.19 s |
| Medium | LLM_FT_MINI_ZEROSHOT | 0.30 s |
| Medium | LLM_FT_MINI_FEWSHOT_100 | 0.37 s |
| Medium | LLM_FT_NANO_ZEROSHOT | 0.37 s |
| Medium | LLM_FT_NANO_FEWSHOT_100 | 0.38 s |
| Slow | LLM_NANO_ZEROSHOT | 0.64 s |
| Slow | LLM_MINI_ZEROSHOT | 0.72 s |
| Slow | LLM_NANO_FEWSHOT_100 | 0.81 s |
| Slow | LLM_MINI_FEWSHOT_100 | 1.06 s |
| Outlier | LLM_NANO_FEWSHOT_1000 | 1.77 s |
| Outlier | LLM_MINI_FEWSHOT_1000 | 3.00 s |
:::
:::

:::

::: group id="varianty" title="Four options in depth"

::: card number="03" title="Large language model without training" default="closed"
An LLM can follow instructions, so we can simply tell it: classify this text and return only one output token. In my case `0`, `1`, or `2`. If I let the model think and explain at length it might be more accurate, but also many times more expensive. I care about practical operation here.

::: detail-grid title="What we saw with the LLM" hint="Click a card for the detail"
::: detail-card title="Quality" summary="Mini is a bit better than nano, but not dramatically."
Few-shot with 100 examples helps a little. Few-shot with 1000 examples actually confuses small models and stretches context so much that the result stops making sense.
:::
::: detail-card title="Cost" summary="Input tokens dominate."
That is why few-shot 1000 is practically nonsense: dramatically more expensive and worse. Input-token caching helps for few-shot scenarios, but it does not change the rules.
:::
::: detail-card title="Latency" summary="Short context is faster; nano is faster."
Sequential processing comes out at roughly 0.64 to 1.06 seconds per sample. The 1000-example variant is completely off, three seconds per sample with the mini model.
:::
::: detail-card title="Flexibility" summary="This is where LLM wins."
No training, no pipeline, no specialized model. I change the prompt and get different behavior. One endpoint, one library, one runtime model.
:::
:::
:::

::: card number="04" title="Fine-tuning a large language model" default="closed"
Here I again take the mini and nano models and show them 25,000 training examples. Then I use them zero-shot and with few-shot 100 examples.

::: detail-grid title="Fine-tuned LLM in practice" hint="Click a card for the detail"
::: detail-card title="Quality" summary="Best result of the whole test."
Fine-tuning helped dramatically. GPT-4.1-mini reached 80.0%. Interestingly, few-shot stops helping and actually hurts. My guess is that 100 randomly picked examples are not representative against the 25,000 used in training.
:::
::: detail-card title="Cost" summary="Inferencing is not the whole story."
Fine-tuning itself cost $40. In Azure OpenAI Service the fine-tuned model uses the same token prices as the regular version, but hosting is billed at $1.7/h. With OpenAI you do not pay hosting, but tokens are more expensive. Sometimes one is cheaper, sometimes the other.
:::
::: detail-card title="Latency" summary="Markedly better in my measurement."
I tested in Azure where you pay hosting. This should not be taken as an official guarantee, but I measured 2x to 3x lower latency than the regular variant.
:::
::: detail-card title="Flexibility" summary="You can still bend it with prompts."
It is a specialized model, but still generative. Small instruction tweaks or in-context examples work. Bigger changes mean another fine-tuning run.
:::
:::
:::

::: card number="05" title="Fine-tuned transformer encoder (BERT)" default="closed"
BERT is older, but for text classification it works very well. Generative models are decoder-only and learn to predict the next token. An encoder-only model does not generate text, but processes the whole input well and outputs a class.

::: detail-grid title="BERT: older approach, still strong" hint="Click a card for the detail"
::: detail-card title="Quality" summary="Very good, but fine-tuned LLM is higher."
A simple and briefly trained variant ended up clearly above the plain LLMs and similar to logistic regression on embeddings. I believe BERT could be pushed further.
:::
::: detail-card title="Cost" summary="Model is free-ish; operation is not."
We need a GPU machine. I counted two older NVIDIA T4 nodes on Azure VM at $0.56/h. Training ran for 500 seconds, so almost nothing. But inferencing costs compute and that brings BERT into GPT-4.1-nano territory.
:::
::: detail-card title="Latency" summary="Best in the test."
BERT ran locally on Azure VM, so it did not have the same cloud round-trip as the other variants. Even if 0.09 s became 0.12 s in a more realistic setup, it is still excellent.
:::
::: detail-card title="Flexibility" summary="The biggest weakness."
You need code or AutoML; the model is single-purpose and you cannot tune it via a prompt. Plus I started from BERT, which does not speak Czech, so Czech and multilingual scenarios are harder.
:::
:::
:::

::: card number="06" title="Embeddings and logistic regression" default="closed"
This is a combination of modern pre-training and prehistorically simple classification. An embedding model turns text into the latent space, roughly 1500 dimensions, and logistic regression decides the three classes.

::: reveal title="Why this combination feels interesting to me"
Embeddings on their own are not a classifier. They will not say "positive" or "negative". But they are a universal representation of meaning. On top of them I can put a tiny model that trains quickly, runs on CPU, and costs almost nothing. Inferencing is then the cloud call for embeddings plus a local classification computation.
:::

::: detail-grid title="Embeddings + LR" hint="Click a card for the detail"
::: detail-card title="Quality" summary="Surprisingly good with the full dataset."
Training on the full dataset puts the result clearly above the plain LLM and close to BERT.
:::
::: detail-card title="Cost" summary="Lowest by orders of magnitude."
The cost of logistic regression is negligible. What matters is the embedding token price and that is very low.
:::
::: detail-card title="Latency" summary="Very good."
Embeddings come back from the cloud quickly and the local LR model is instant.
:::
::: detail-card title="Flexibility" summary="Single-purpose, but language-friendly."
Like BERT, the final classifier is fixed. Unlike BERT, modern embeddings typically speak Czech and other languages, which is a big practical advantage.
:::
:::
:::

:::

::: group id="zaver" title="What I would pick"

::: card number="07" title="My practical recommendation" default="open"
None of the variants is the absolute winner. It depends on the task, volume, language, and how much future flexibility you want.

| Scenario | Choice | Why |
|---|---|---|
| I am a nerd and a saver | LR + embeddings | Lowest cost, great speed, more complex and single-purpose. |
| I want something general and tunable over time | LLM | Baseline quality, higher cost and latency, but extreme simplicity. |
| I want best quality and relatively easy operation | Fine-tuned LLM | Best quality, hosted, but specialized and more expensive. |
| I am a nerd, no cloud, English only, GPU to spare | BERT fine-tuning | Very good quality, low cost with good utilization, best latency, least flexibility. |

::: arrow-list title="My practical shortcut"
- If the task is not yet stable, I would start with a plain LLM and a prompt.
- If you have high volume and a clearly defined class, try embeddings + a simple classifier.
- If you chase quality and want hosted operation, reach for fine-tuning an LLM.
- If you have a strong ML team and your own compute, an encoder model makes sense.
:::
:::

:::


::: closing
Of course, this is my example; in yours it may turn out differently. The important thing is not to think only about accuracy, but also about cost, latency, operation, and future changes in the task.
:::
