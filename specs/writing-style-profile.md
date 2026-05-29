# Writing-style profile for interactive article work

Status: draft v0.1

Source: background analysis of `_posts\` articles from 2024, 2025, and 2026, with more emphasis on recent posts.

Purpose: guide agents that help with research, structure, source Markdown, caveman versions, and HTML conversion while preserving the author's voice.

## Voice

- Language is Czech, with technical terms kept in English: `agent`, `skill`, `tokens`, `cache`, `MCP`, `OpenTelemetry`, `AGENTS.md`, `RBAC`, `PTU`, `MoE`, `neuralese`.
- Tone is expert peer-to-peer, first-person, conversational, and opinionated.
- Common phrases: `Za mě`, `Já osobně`, `Myslím`, `Pojďme`, `Podívejme se`, `OK, jde se...`.
- Humor and Czech idioms are part of the style, not noise to remove.
- The author often hedges with `záleží`, `typicky`, `v mém případě`, then gives a clear opinion.
- Long compound sentences, asides, and em-dashes are normal. Do not shorten reflexively.

## Article anatomy

- Jekyll front matter is minimal: `layout`, `published`, `title`, `tags`.
- The article starts directly with a framing paragraph. Do not add `# Úvod`.
- Long technical posts may include a short key-takeaways block near the top.
- Major sections use `#`; sub-sections use `##`.
- Typical sequence: framing -> background/why -> mechanism -> demo/code -> trade-offs -> personal verdict.
- Bold emphasis is used heavily as a scanning aid. Preserve it.

## Recurring endings

Common closing shapes:

- `Shrnutí` or `Závěr` with practical bullets.
- A bold personal verdict paragraph.
- A reader question or next-article teaser.

## Genre templates

| Genre | Typical structure |
|---|---|
| Deep tutorial | Repo link -> architecture -> code/Terraform excerpts -> screenshots -> monitoring -> closing bullets |
| Opinion essay | Hook -> 3-5 perspectives -> bold personal verdict -> reader question |
| Comparison | Setup -> variant A/B/C -> pros/cons -> "kdy použít co" |
| Workflow | Personal practice -> phases -> prompts/files -> tooling tips |
| Benchmark | Question -> setup -> table/graph -> findings -> practical implications |
| Recommendation list | Personal framing -> top picks -> categories -> CTA |

## Interactive conversion opportunities

| Source pattern | Interactive treatment |
|---|---|
| Pros/cons per option | Tabs or comparison cards |
| "Kdy použít X vs Y" | Scenario picker or decision matrix |
| Long CLI sessions | Collapsible detail with copy button |
| Token math | Calculator or live estimate widget |
| Caveman/Wenyan examples | Side-by-side or tabbed comparison with token counts |
| Warning paragraph | Subtle callout |
| Personal verdict | Pull-quote or `Autorův názor` box |
| TL;DR bullets | Sticky or top summary panel |
| Screenshot walkthrough | Step-through carousel |
| Architecture prose | Mermaid/SVG diagram if the source describes it clearly |
| Series links | Previous/next/all-parts navigator |
| Numbered phases | Stepper or expandable cards |

## Assistant do/don't

Do:

- Help with research, source verification, structure, story shaping, and component suggestions.
- Suggest section outlines using the genre templates above.
- Preserve author identity markers: `Za mě`, `Já`, `Myslím`, rhetorical questions, bold thesis sentences, Czech idioms, English technical terms.
- Keep existing image references and code blocks unless the author asks for transformation.
- Ask before inserting external links, changing paragraph order, expanding code samples, or adding diagrams not described by the text.
- Present proposed wording as suggestions for the author to edit.

Don't:

- Do not rewrite Czech prose just to make it smoother.
- Do not translate technical English terms into Czech.
- Do not sanitize humor, strong opinions, or personal phrasing.
- Do not add corporate filler such as "In conclusion", "It is worth noting that", or generic intro paragraphs.
- Do not add `# Úvod`.
- Do not shorten long sentences unless asked.
- Do not fabricate citations, benchmark numbers, or claims.
- Do not introduce new Jekyll front-matter fields for legacy posts without asking.

## Checkable review rubric

Before accepting generated source or HTML, verify:

- The opening still sounds like a personal framing, not a generic abstract.
- At least the key thesis sentences and bold emphasis from source are preserved.
- Technical English terms remain English.
- No `# Úvod` was added.
- Long code/log sections became collapsible only when the full content remains accessible.
- Every added callout, tab, or diagram is grounded in source content.
- The ending contains either practical summary, personal verdict, or reader/next-step question.

## Representative citations

| Observation | File |
|---|---|
| Token-cost math and caveman examples | `_posts\2026-05-04-techniky-pro-usporu-tokenu-v-kodovacich-agentech.md` |
| Agent skills tutorial and CLI captures | `_posts\2026-05-11-agent-skills-centralni-sprava.md` |
| Pros/cons comparison template | `_posts\2026-01-27-3-cesty-k-genui.md` |
| Workflow article with phases and prompts | `_posts\2025-07-03-jak-delam-vibe-coding.md` |
| Opinion essay with bold verdict | `_posts\2025-07-31-ai-self-orchestrace.md` |
| Async AI tutorial with screenshots | `_posts\2025-02-10-async-ai.md` |
| 2024 benchmark style continuity | `_posts\2024-11-04-je-uz-na-case-naskocit-do-arm64-v-cloudu.md` |
