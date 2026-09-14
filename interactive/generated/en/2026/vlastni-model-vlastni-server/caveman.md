# An open AI model has many advantages. Most do not require your own hardware.

META
- url: /en/2026/vlastni-model-vlastni-server/
- source: source.md
- date: 2026-09-14
- language: en; machine translation from cs-CZ
- source-sha256: f6c582131bab5f87f9a5751e9337a514f79a949c77f456aafcc5e749e5e72ac1
- thesis: Separate model choice, self-hosted inference, hardware ownership. Most open-weight benefits need no purchased server. Economics require enough concurrent useful work for enough paid time.

## 01 Model versus location
- Same model via per-token API, Azure GPU VM, or own server; operator and payer for idle capacity differ.
- Open weights = downloadable/runnable under license; not automatically fully open-source AI, not necessarily open training data. [OSI](https://opensource.org/ai/open-source-ai-definition).

## 02 Control and vendor independence
- Keep version; change runtime, quantization, cache, adapters; switch providers/hardware/regions or run own VM.
- Downloaded weights preserve current capabilities, not future innovation. Model migration still changes tool calling, formats, task quality.
- Anthropic disabled Fable 5 globally June 12, 2026 after US export directive; restored July 1; could not verify nationality selectively in real time. [Account](https://www.anthropic.com/news/redeploying-fable-5).
- Weights reduce a service's off-switch dependency, not legal/export obligations. Contracts/governments may prohibit Chinese models or restrict healthcare/children use; personal use may be all that remains.

## 03 Legitimate work and restrictions
- Authorized pentests, incident analysis, AI/biology research may encounter blocking or lower-capability fallback.
- Open weights ≠ no guardrails: refusal in weights; application/license/infrastructure restrictions.
- Fable 5/5.1: some offensive cybersecurity and narrow frontier-LLM tasks (distributed training infrastructure, ML accelerator design, nonstandard-chip kernels); not all AI development/defensive security. Context/files checked, false positives possible, Opus retains safeguards and need not answer. Some defensive use has verification; app/API behavior differs. [Details](https://support.claude.com/en/articles/15363606-why-claude-switched-models-in-your-conversation-with-fable-5-or-fable-5-1).
- Suitable open model may help research/security labs; quality/responsibility remain. API or cloud VM may suffice.

## 04 Data control and security
- Self-hosting controls flows/access/storage, but does not automatically beat API/cloud security.
- [Zero retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): supported features/agreed conditions; limits retention, not inference-time processing.
- [Confidential computing/GPU VMs](https://learn.microsoft.com/en-us/azure/confidential-computing/confidential-vm-overview): protect in-use memory against privileged operator; supported platform/configuration/attestation required; no fix for app bugs or authorized exports.
- Open weights do not prove training provenance or absence of hidden conditional/sleeper-agent behavior. Server location does not solve model trust. European region does not settle all jurisdiction issues; specify threat/defense.
- Suitable region/private access/contracts may avoid on-prem even for sensitive data.

## 05 Latency and offline
- Own inference can prioritize per-request speed over aggregate capacity, typically smaller batch at higher token cost.
- [Claude fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode): same weights, faster inference, higher price; not smarter model, not documented as merely smaller batch; mainly generation, not TTFT.
- Latency = network + queue + prefill + generation. Good remote API can beat small local server; network matters more for voice/many short agent steps.
- Cloud VM can control latency; true offline needs local/device execution. Offline AI need not be LLM: computer vision is a different task.
- Small models may handle extraction/classification/functions; author considers laptop models unusable for his complex coding-agent expectations, not all coding.
- [GLM 5.3](https://huggingface.co/zai-org/GLM-5.3): ~753B parameters. [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3): 2.8T. Large multi-GPU systems/clusters; tens of millions CZK.
- 2T weights only: 4 TB BF16 / 2 TB 8bit / 1 TB 4bit; excludes cache, activations, quantization metadata, overhead. MoE activates subset but other weights still stored.
- [Thinkmate](https://www.thinkmate.com/system/gigabyte-g894-sd1-aax5): complete 8× B200, 1.44 TB HBM, USD 538 120; illustrative CZK 22/USD, not current FX or binding VAT-inclusive quote.

| 2T representation | Weight memory | Minimum 8× B200 servers by HBM | Approx. CZK million |
|---|---:|---:|---:|
| 4bit | 1 TB | 1 | 11.8 |
| 8bit | 2 TB | 2 | 23.7 |
| BF16 | 4 TB | 3 | 35.5 |

- Memory lower bounds only, not recommended configurations or measured performance. Runtime/sharding/context/batch/speed may need more GPUs; interconnect/power/cooling/operations extra. RAM/disk offload changes economics/performance.
- [Moonshot recommendation](https://www.kimi.com/news/kimi-k3): 64+ accelerator supernode for Kimi K3 efficiency/communication. Eight quoted servers = 64 B200 = ~CZK 94.7m before cluster extras; eight HGX servers ≠ one NVLink supernode; price illustration, not validated deployment.

## 06 Cheaper model versus cheaper serving
- Smaller model + cheap API may save immediately if task quality sufficient. License alone guarantees nothing: price, retries, human completion matter.
- Pareto price/performance frontier: cheap closed GPT 5.6 Luna can qualify; current open Mistral models, in author's view, fall short for their hardware demands.
- After model choice, compare same work via API/IaaS/ownership; no justifying server costs with unrelated benefits.

## 07 A100 experiment
- NVIDIA Nemotron 3.5 Lightning 30B-A3B BF16; Mistral also tested but not analyzed here.
- Azure `Standard_NC24ads_A100_v4`; 1× A100 80 GB PCIe; vLLM 0.28.0.
- 16 384 input + 512 output tokens/request; concurrency 1/5/10/20/50/100 × shared/unique prefix × 3 repetitions = 36 measurements, 4 017 successful requests.
- Shared prefix simulates repeated coding-project instructions/tools/context. [Prefix cache](https://docs.vllm.ai/en/v0.28.0/features/automatic_prefix_caching/) reuses processed state, NOT finished response; output still generated.
- Prefix 12 288 tokens = 75% input; hybrid attention/Mamba blocks 2 096; 5 reused blocks = 10 480 tokens; token hits ~63.96% at c5–100, 62.75% c1 including initial misses; no-prefix hits zero.
- Local cache reuse ≠ API billing. API granularity/routing/TTL/hit ratio unmeasured; performance and billing assumption selected separately.
- Raw completions, no chat template, synthetic code, forced 512 output ignoring EOS. New requests for 120 s + drain; throughput includes drain. Closed-loop clients immediately resubmit.
- Weights 58.93 GiB; pinned revision/image; no speculative decoding. API precision/quality/speed unknown; only token volume priced. Purchased server performance inferred from Azure, not separately measured.
- Old A100 available; author expects qualitative trend across newer hardware/larger models, not transferable measured speeds/thresholds.

## 08 Batch size and latency
- Continuous batching changes internal batches dynamically; measured external client concurrency ≠ fixed batch size or registered users.
- Aggregate GPU output tok/s; TTFT/full response seconds; averages of three runs:

| Concurrency | Shared tok/s | TTFT | Full | Unique tok/s | TTFT | Full |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 148.2 | 0.39 | 3.45 | 132.2 | 0.81 | 3.87 |
| 5 | 294.3 | 1.35 | 8.70 | 228.2 | 2.70 | 11.21 |
| 10 | 398.2 | 2.24 | 12.86 | 289.6 | 3.12 | 17.67 |
| 20 | 591.9 | 3.16 | 17.29 | 371.2 | 4.20 | 27.17 |
| 50 | 820.1 | 4.73 | 31.17 | 409.4 | 17.72 | 59.90 |
| 100 | 788.2 | 15.83 | 60.58 | 389.6 | 64.48 | 109.97 |

- Shared c1→c50: ~5.5× aggregate capacity, slower individual response; c100 throughput falls. Count only capacity meeting latency requirement; overnight batch ≠ interactive assistant.

## 09 Time utilization and provider scale
- Concurrency = simultaneous work; utilization = duration with that work. 100% at c1 ≠ volume at c50; `nvidia-smi` is not economic utilization.
- 8h × 5 days = 23.8% calendar, assuming continuous selected concurrency even at work. Meetings/tool waits/fluctuations reduce actual use. 60% = >100h/week; need time zones/apps/night queue.
- Provider pools customer demand, buys cheaper hardware, spreads specialists, lowers PUE. PUE = total datacenter/IT energy; PUE 2 adds 100% energy overhead. Lower PUE does not reduce total inference cost by same ratio.
- Batching/cache/routing do not require sharing private customer data. Separate prefill/decode pools scale distinct workloads independently; KV transfers cost resources, not universal win.
- Speculative decoding drafts tokens, main model verifies together; poor draft match can hurt. CUDA/Triton kernels, memory optimizations, quantization, custom inference hardware depend on model support/acceptable quality.
- [Dynamo disaggregation](https://docs.nvidia.com/dynamo/v1.0.0/design-docs/disaggregated-serving); [Fireworks serving](https://fireworks.ai/inference); [speculative decoding](https://docs.fireworks.ai/deployments/speculative-decoding).
- Self-hosters can use techniques too; skills/operations/cost matter. No claim specific Nemotron endpoint uses all, no invented speed multiplier.

## 10 Five-year cost assumptions
- [Fireworks on Foundry](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/fireworks/) public reference snapshot 2026-09-03: USD 0.06 regular input / 0.01 cached input / 0.22 output per million tokens.
- PAYG VM: USD 4.775/allocated hour.
- Reservation: USD 46 567/3y, same rate extrapolated to 5y = USD 77 611.67.
- Own server purchase USD 45 000; maintenance + energy gives USD 64 834.80/5y at continuous work.
- Modeled ownership lead over reservation USD 12 776.87/5y ≈ USD 2 555/year; additional differential on-prem costs can erase it.
- Five years = planning horizon, not proven lifetime/payback; constant rates/performance, no residual value, not market forecast.
- [Huang/H100 rental report](https://stocktwits.com/news-articles/markets/equity/nvda-rises-overnight-after-strong-week-ceo-jensen-huang-pumps-nvidia-chips-as-highly-rentable-money-minting-assets/cZt3ZqARJxw): ~USD 3.28/h is per GPU, not eight-GPU server. [Ornn methodology](https://ornn.com/product/ornn-data). Rental ≠ resale/accounting depreciation.

## 11 Break-even: enough work in time AND concurrently
- Both main scenarios: local shared prefix; API bills assumed 64% input cached, remainder regular; output separate.
- USD per 1 000 identical requests, c50 while productive. VM stays allocated until completion, including waiting; fixed 5y costs spread over all work, not purchasing for 1 000 requests:

| Paid-time utilization | API | Reserved | Modeled on-prem | PAYG incl. waits |
|---|---:|---:|---:|---:|
| 100% | 0.5714 | 0.3073 | 0.2567 | 0.8281 |
| 90% | 0.5714 | 0.3415 | 0.2828 | 0.9201 |
| 60% | 0.5714 | 0.5122 | 0.4133 | 1.3802 |
| 40% | 0.5714 | 0.7683 | 0.6090 | 2.0703 |
| 20% | 0.5714 | 1.5365 | 1.1962 | 4.1406 |
| 10% | 0.5714 | 3.0731 | 2.3705 | 8.2812 |

- Break-even vs API: reservation 53.78%, on-prem 42.74%; both cheaper at full use, both dearer at 40%.
- 1 000 requests ≈10.4 productive minutes; PAYG ≈USD 0.83 at 100%, ≈104 allocated minutes/USD 8.28 at 10%. Same productive speed/batch, not GPU 10× slower. Startup/loading excluded.
- API same tokens/same cost; reserved always paid, own server idle outside work, PAYG each allocated hour.
- USD/1 000 requests at 100% time utilization, varying concurrency:

| Concurrency | API | Reserved | Modeled on-prem | PAYG |
|---|---:|---:|---:|---:|
| 1 | 0.5714 | 1.7005 | 1.4206 | 4.5826 |
| 5 | 0.5714 | 0.8563 | 0.7154 | 2.3076 |
| 10 | 0.5714 | 0.6329 | 0.5287 | 1.7056 |
| 20 | 0.5714 | 0.4258 | 0.3557 | 1.1473 |
| 50 | 0.5714 | 0.3073 | 0.2567 | 0.8281 |
| 100 | 0.5714 | 0.3197 | 0.2671 | 0.8616 |

- First measured wins: on-prem c10, reserved c20; actual crossings only bracketed c5–10/c10–20. PAYG never wins. c100 worse than c50; TTFT 15.83 vs 4.73 s.
- No shared prefix either side at c50: reservation 56.18%, on-prem 44.73%; different capacity, TTFT 17.72 s.
- 48h allocated, fully productive c50/shared: compute USD 229.20 vs API USD 158.15 at assumed 64% cached billing. Half utilization halves work/API bill, not VM bill.
- Deallocation removes rest-of-month compute cost, not waits/start/loading; disks may continue costing. PAYG vs reservation crosses at >37.1% allocated calendar, INCLUDING waits; different from VM/API break-even.

```text
H = 43 800 hours / five years
u = productive share of calendar
R = measured output tok/s × 3600 / 512
h = API cached-input billing fraction
p = [16384 × ((1 − h) × 0.06 + h × 0.01) + 512 × 0.22] / 1 000 000
API = H × u × R × p
PAYG allocated throughout period = H × USD 4.775
reservation = USD 77 611.67
on-prem = USD 59 316 + H × u × USD 0.126
```

- On-prem fixed = purchase/maintenance/idle energy; productive hour adds active−idle energy difference, not full energy twice.
- Unit cost = total/requests. Fixed option cheaper above attainable threshold; >100% unattainable.
- ~54% at c50 ≈90h/week at that point's capacity, not GPU monitor 54%. Mixed concurrency: sum work by measured points; no averaging concurrency and assuming linear speed.

## 12 Verdict
- Choose capable model first, required control/response second, GPU operator last.
- Most open-weight benefits require no owned hardware. For measured workload, low concurrency/irregular use favors cheap API; sustained concurrent demand may favor self-hosting.
- Compare reserved VM with FULL on-prem budget, not card price versus endless PAYG.
- Working c50/64%-cached-API thresholds ~54% reserved / ~43% on-prem. On-prem advantage only ~USD 2.6k/year for extra differential costs.
- Author prefers quality models via APIs; own hardware only for specific reason AND enough work. Avoiding provider margin does not make idle owned capacity free.
