---
name: interactive-article-authoring
description: Plan, draft, research, restructure, and review Tomas Kubica interactive article sources in interactive/source/**/*.article.md while preserving his Czech writing voice.
---

# Interactive article authoring

Use this skill when planning, drafting, restructuring, or researching an interactive article source in `interactive\source\**\*.article.md`.

## Role

Be a collaborator, not a ghostwriter. Help Tomas shape the story, research facts, identify weak structure, and propose interactive presentation moments. Preserve the author's personal Czech voice; do not replace it with polished marketing prose.

## Inputs

- Existing notes, outline, draft, or Jekyll post.

## Skill contents

This skill is self-contained:

- `references\source-format.md` describes the author-facing Markdown-plus format.
- `references\writing-style.md` captures Tomas's blog voice.
- `references\quality-review.md` folds in the previous review and spell prompt workflows.

Keep this skill separate from `interactive-article-generator`: authoring is for story, research, source structure, and Tomas's voice; generation is for rendered HTML, CSS, JS, caveman output, and accessibility details. The authoring skill must still know the source syntax well enough to produce implementation-ready `.article.md`. Invoke the generator skill only when rendering, validating renderability, or changing shared visual/component behavior.

## Working style

1. Discuss the thesis and reader journey before reorganizing text.
2. Suggest where cards, reveals, tabs, code examples, tables, and callouts help comprehension.
3. Prefer normal Markdown. Use directives only when plain Markdown cannot express the intended interaction.
4. Keep the author's formulations wherever possible.
5. Ask before changing the core opinion, claim strength, or conclusion.
6. Keep research citations close to the claims they support.
7. Use `references\quality-review.md` when reviewing facts, flow, style, links, missing areas, or typos.
8. When Czech source content is added or materially changed, offer to regenerate the optional English machine translation under `interactive\translations\en\...`; Czech remains the source of truth.
9. When converting legacy Jekyll posts, remove `{% raw %}` / `{% endraw %}` wrappers only after confirming their contents are inside fenced code blocks; preserve literal Helm/Liquid templates such as `{{- include "..." . }}` exactly so GitHub Pages cannot interpret them.
10. Do not fix rendering problems by inventing a custom HTML renderer or changing shared templates. First fix the `.article.md` source so `source.md` is a faithful copy in the canonical triple-colon directive format used by existing successful articles.
11. Before using any directive, fence attribute, or component pattern, verify it is supported by the current repo by checking this source-format reference plus an existing successful `.article.md` and its generated HTML. If the needed element is not demonstrably implemented, do not invent syntax; ask whether to implement support or approximate it with existing components.
12. When converting a legacy article, wrap every top-level section (the parts the reader would otherwise see as `## h2`) in a `::: card` inside a `::: group`. Articles whose body uses only Markdown headings render as one giant non-collapsible page; the expandable card flow is the entire point of the format.
13. Put the final takeaway in a `::: closing` block placed AFTER the last group, never inside the last card.
14. The renderer always opens only the very first card in an article and collapses every other card. The `default="open"` hint in a source is documentation only and does not override this rule; never structure an article so the reader needs multiple cards open at once.

## Good interactive candidates

- A concept that can be introduced briefly and then expanded live.
- A comparison with multiple reasonable options.
- A table or code sample that benefits from commentary.
- A warning, rule, or personal verdict.
- A story with stages: problem, mental model, examples, tactics, conclusion.
- A process that deserves `sequence` or `steps`, an evidence transcript that deserves a labeled or wrapped text block, or a final action list that deserves an arrow-style summary.

## Avoid

- Making every paragraph interactive.
- Adding visual components only for decoration.
- Hiding essential content behind JavaScript-only rendering.
- Translating established technical English terms into awkward Czech.
- Removing personal phrasing such as `Za mě`, `Pojďme`, `osobně`, `podle mě`, when it fits the article.
