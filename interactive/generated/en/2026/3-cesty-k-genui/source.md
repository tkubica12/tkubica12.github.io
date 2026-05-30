---
format_version: 1
title: "Three paths to GenUI and their pros and cons"
eyebrow: "GenUI and AI-first interfaces"
subtitle: "A static artifact, a declarative specification, or fully generated interactive code? Three practical paths to visual GenUI and their trade-offs."
slug: 3-cesty-k-genui
date: 2026-01-27
language: en
source_language: cs-CZ
source_slug: 3-cesty-k-genui
translation: machine
translated_from_hash: "55a145f069659705920e21966ee7a600dd22307f40845d39dd33c2d88dfa00e7"
translation_status: current
status: experimental
canonical_url: "/en/2026/3-cesty-k-genui/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

The area of ad-hoc automatically generated UI fascinates me and I see it as key for modern applications born in an AI world. We will certainly see applications that use non-visual modalities, for example voice (there is speculation that the first consumer AI device from the drawing board of Jony Ive, the iPhone creator now working with OpenAI, will be a smart speaker), but screens will stay with us for some time and will remain part of user interfaces in some form until we move fully to brain-computer interfaces such as Neuralink. But I do not think it is likely that UI will keep being universally pre-programmed inside every application.

::: group id="ai-ui" title="Universal UI for AI vs. AI-first UI"

I expect two approaches:

::: card number="01" title="A UI container for AI" default="open"

That will be, for example, **Copilot** or **Excel**. A universal way to interact with AI will exist, and my specific applications will live inside it. For example, if I am a bank, I will want my advice, overviews and current events to be accessible in my "chat" application, such as Copilot. But when it comes to financial planning, budgets and similar things, chat is not a suitable format and Excel is excellent for that. The bank should therefore have support in my Excel - it must be able to pull in my expenses, help with financial health, offer loan consolidation or various optimizations.

:::

::: card number="02" title="AI-first UI" default="open"

Some applications will be so different and complex that consuming them from a universal UI such as Copilot or PowerPoint will not be suitable. For example, imagine an AI-first solution for musicians where you can hum individual melodies, harmonic progressions and rhythms, and AI helps you turn them into parts, play back how they sound and arrange the composition together with you. I do not think this belongs in chat or Word, do you?

:::

:::

::: group id="tri-cesty" title="Three paths to creating visual GenUI and how they compare"

I see three paths emerging for generated visual user interfaces (GenUI):

::: sequence title="Three paths"
1. **Ad-hoc generated static artifacts** — the output is an image or a similar artifact.
2. **Ad-hoc generated declarative UI specifications** — AI composes predefined components.
3. **Fully generated interactive UI through ad-hoc imperative code generation** — AI creates a small custom application.
:::

Let's look at them more closely and compare their advantages and disadvantages.

::: card number="01" title="Ad-hoc generated static artifacts" default="open"

This became widespread already in 2023, a few months after ChatGPT launched, and later came directly into APIs. It is typically used to generate charts and diagrams from tabular data. You add Code Interpreter as a tool, and if the model sees tabular input where a chart would help, it writes Python code using a library such as Matplotlib or Seaborn and produces an image as the output. It then pulls that from the sandbox and shows it to the user.

::: tabs id="staticke-artefakty"
::: tab id="vyhody" title="Advantages"
- Very safe - the sandbox typically cannot access the internet (so the data cannot leave) and the user receives only a JPEG/PNG image; nothing runs anywhere
- Easy to store in history and recall later; it is enough to keep the file in some blob with a GUID and RBAC for the user and put a link to it in history
:::
::: tab id="nevyhody" title="Disadvantages"
- Zero interactivity - the chart cannot be manipulated, filtered or zoomed
- Visual limitations and weaker adaptation to the application's main design
:::
:::

:::

::: card number="02" title="Ad-hoc generated declarative UI specifications" default="open"

The second variant separates the display code from the way we say what should be displayed. The idea is that you create a declarative language - a list of possible components and their attributes, such as a button, image, list and so on - and AI can generate only within the guardrails of that declarative language. It does not write imperative code such as JavaScript; it only chooses from a field of options what it wants and how it wants to compose it. A typical example is Microsoft's [Adaptive Cards](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/design-effective-cards?tabs=design) for Teams, which were already refined and used before AI arrived. Another interesting option is [A2UI](https://a2ui-composer.ag-ui.com/gallery), primarily from Google, which is more focused on the web and Android and, because it is newer, includes some optimizations for GenUI (for example, Adaptive Cards are JSON, so AI generates the whole thing before Teams can start rendering, while A2UI is JSONL, where each element is its own JSON line, enabling streaming and progressive rendering).

::: tabs id="deklarativni-ui"
::: tab id="vyhody" title="Advantages"
- Safe - AI cannot generate arbitrary code, only predefined components
- Interactive - the user can typically click on some things
- Design is controlled by the client - rendering happens on the client, for example Teams, so the visual implementation is fully under its control
:::
::: tab id="nevyhody" title="Disadvantages"
- Limited options - if AI needs something that is not in the component set, it cannot do it
- Harder to implement - you need to create and maintain the component set and its rendering
:::
:::

:::

::: card number="03" title="Fully generated interactive UI through ad-hoc imperative code generation" default="open"

What if we give AI a free hand to generate any code and show that code to the user in an iframe? This maximum flexibility enables literally custom mini-applications, built ad hoc, and it is a very good variant. I have already played with this; in May I [wrote](https://tomaskubica.cz/post/2025/genui/) here about using the HTMX standard for server-side rendering with AI. As AI coding capabilities keep improving, this can now be pushed much further. A new standard has appeared (an MCP extension) for passing generated code back to the agent - [MCP-Apps](https://mcpui.dev/). Another new thing is that MCP-Apps is now supported in [VS Code Insiders](https://code.visualstudio.com/blogs/2026/01/26/mcp-apps-support).

::: tabs id="imperativni-kod"
::: tab id="vyhody" title="Advantages"
- Maximum flexibility - AI can create anything possible in the given language and framework
- Full interactivity - the user can fully interact with the UI; these are literally mini-applications
:::
::: tab id="nevyhody" title="Disadvantages"
- Security risks - running generated code can pose security threats, so sandboxing and other controls are needed
- Design can be inconsistent - if AI does not have sufficiently clear instructions, it can generate UI that does not match the application's overall design
:::
:::

:::

:::

::: group id="shrnuti" title="Summary"

::: summary-grid
- **Static artifacts**: safe and easy to store, but not interactive.
- **Declarative specifications**: safer and interactive, but limited by the component set.
- **Imperative code**: maximum flexibility and mini-applications, but with security and design risks.
:::

::: callout type="verdict" title="Final question"
So, do your applications already have #GenUI capabilities? Which path are you planning to use?
:::

:::
