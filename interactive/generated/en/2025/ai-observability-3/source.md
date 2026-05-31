---
format_version: 1
title: "Deep dive into AI agent observability with Microsoft Agent Framework - tracing with open-source tools Aspire Dashboard and Langfuse"
subtitle: "Tracing AI agents via Aspire Dashboard and Langfuse: a quick developer view, anonymization through the collector, and specialized AI observability."
slug: "ai-observability-3"
date: "2025-11-27"
language: "en"
source_language: "cs-CZ"
source_slug: "ai-observability-3"
translation: "machine"
translated_from_hash: "9385E187CE86A52D8570C1DA6296A852935856C4C4ABE5BE993D9FAAC7426878"
translation_status: "current"
status: "experimental"
canonical_url: "/en/2025/ai-observability-3/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Deep dive into AI agent observability with Microsoft Agent Framework - tracing with open-source tools Aspire Dashboard and Langfuse

In the first part we covered the basic architecture and reasons why I like to use the OpenTelemetry collector, so that last time we could focus on metrics and their use in Azure Monitor for Prometheus and Azure Managed Grafana. Today we dive into tracing, the most important discipline for AI agent observability, and we start with open-source tools: Aspire Dashboard for a quick developer view and Langfuse.

::: group id="open-source-tracing" title="Open-source tracing for AI agents"

::: card number="01" title="Aspire Dashboard: quick developer view" default="open"
OpenTelemetry is eating the observability world and I am a huge fan. After many years of combining proprietary tools and approaches with an alternative open-source SDK zoo, OpenTelemetry arrived with an ambition to unify metrics, logs, and tracing under a single protocol, single SDK and API. There are numerous backends that provide visualizations and data persistence, but for quick developer assessments they are all cumbersome, slow, expensive, or consume too many resources. That is why the .NET team developed **Aspire Dashboard**, a simple solution running in a single lightweight container where you can visualize OpenTelemetry quickly and nearly in real time.

Here we can see tracing from a multi-tenant Magentic-style solution in Microsoft Agent Framework.

::: reveal title="Screenshot: trace overview in Aspire"
![Trace overview in Aspire Dashboard](/images/2025/2025-11-27-10-24-40.png)
:::
:::

::: card number="02" title="Aspire: full telemetry vs. anonymized view"
In my case I also enabled logging of individual messages and responses.

::: reveal title="Screenshot: texts and responses in a trace"
![Texts and responses in an Aspire trace](/images/2025/2025-11-27-10-26-08.png)
:::

I also collect custom attributes, such as session ID, logged-in user, user roles, department, and so on.

::: reveal title="Screenshot: custom attributes in spans"
![Custom attributes in Aspire Dashboard spans](/images/2025/2025-11-27-10-26-56.png)
:::

As you can verify in the first part of this series, my OpenTelemetry collector is configured to filter certain fields and hash others, thereby masking the original information. I have created another Aspire instance to which the OTEL collector sends filtered and anonymized information. Notice that I have no conversation content at all, the user ID is masked, but I still have the necessary technical information such as timings and token consumption.

::: reveal title="Screenshot: anonymized Aspire view"
![Anonymized Aspire view without conversation content](/images/2025/2025-11-27-10-29-12.png)
:::

::: callout type="verdict" title="The power of the collector"
That is the enormous strength - I have one stream from the agent and in the OTEL collector I fan it out to various systems: full-fidelity Aspire, anonymized Aspire, Langfuse, AI Foundry, etc.
:::
:::

::: card number="03" title="Aspire: detail of a tool call"
This is what a tool call looks like.

::: reveal title="Screenshot: tool call in a trace"
![Tool call detail in an Aspire trace](/images/2025/2025-11-27-10-32-24.png)
:::

For quick monitoring data snapshots, Aspire Dashboard is excellent - simple, tiny, fast.
:::

::: card number="04" title="Langfuse: specialized AI tracing" default="open"
Looking for a tracing tool that is open-source and specifically specialized for AI scenarios? Langfuse is very popular, but unfortunately even it is not fully open in terms of project governance (it is not under CNCF, Apache Foundation, or Linux Foundation) and is more of an MIT core. Nevertheless it is a very good solution, so let's take a look.

Right from the home screen you can see that Langfuse is not only about observability but also touches on the area of evaluation, which we will cover later in this series.

::: reveal title="Screenshots: Langfuse opening screens"
![Langfuse project overview](/images/2025/2025-11-27-10-40-17.png)
![Langfuse navigation to tracing and evaluations](/images/2025/2025-11-27-10-40-37.png)
![Langfuse observability and datasets view](/images/2025/2025-11-27-10-40-53.png)
:::
:::

::: card number="05" title="Langfuse: concrete trace and token economics"
This is what a specific trace looks like - the same as what we saw in Aspire. Graphically it is different, but in principle the basic information is the same.

::: reveal title="Screenshot: concrete trace in Langfuse"
![Concrete trace in Langfuse](/images/2025/2025-11-27-10-41-59.png)
:::

However, some things are not directly in the data but are derived - the calculation of token consumption in monetary terms is excellent.

::: reveal title="Screenshot: costs and tokens"
![Cost and token calculation in Langfuse](/images/2025/2025-11-27-10-42-40.png)
:::

Of course we can again nicely see the conversation itself.

::: reveal title="Screenshots: conversation content"
![Conversation in a Langfuse trace](/images/2025/2025-11-27-10-43-21.png)
![Message detail in a Langfuse trace](/images/2025/2025-11-27-10-43-39.png)
:::
:::

::: card number="06" title="Langfuse: users, sessions, and evaluations"
Langfuse directly parses some well-known parameters, for example user ID. This allows it to immediately provide an overview of users and their token consumption.

::: reveal title="Screenshot: user overview"
![User overview and token consumption](/images/2025/2025-11-27-10-44-49.png)
:::

From there you can drill down and see individual traces, sessions, and so on.

::: reveal title="Screenshots: sessions and individual traces"
![User detail and sessions in Langfuse](/images/2025/2025-11-27-10-45-18.png)
![Individual traces in a session](/images/2025/2025-11-27-10-45-28.png)
:::

Langfuse also goes into evaluations, but we will discuss that later. You can take a captured conversation, add it to some dataset, annotate it, try it in a simulator, and so on.

::: reveal title="Screenshot: dataset and evaluation"
![Langfuse datasets and evaluation](/images/2025/2025-11-27-10-47-15.png)
:::

For me, Langfuse is the best tracing tool specifically focused on AI in the open-source category. Even though it is not fully open in terms of governance, it is my first choice when I have to stay in the self-managed world. Its evaluation capabilities we will discuss later and it has its place there too, even though projects like DeepEval are strong, albeit somewhat differently focused, competition.

Today we dove into open-source options - Aspire for quick developer snapshots, Langfuse as an open-source specialized AI solution. Further alternatives lie in using non-specialized developer tools and in hosted solutions focused on AI scenarios. We will look at those next time - Azure Monitor and Azure AI Foundry.

::: summary-grid
- **Aspire Dashboard**: small, fast, and excellent for a developer view nearly in real time.
- **Anonymization**: the same telemetry stream can be sent via the OTEL collector once fully and once sanitized.
- **Langfuse**: specialized AI observability tool with tracing, token economics, and a link to evaluations.
- **Tool choice**: Aspire for quick troubleshooting, Langfuse as a self-managed AI tracing option.
:::

:::
:::


::: closing
The next step is to look at service-based variants - Azure Monitor and Azure AI Foundry.
:::
