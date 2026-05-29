# Interactive article source format

Status: draft v0.1

This format is Markdown-first. It is meant to be pleasant for the author to write and useful for an agent to regenerate interactive HTML. It is not a strict compiler DSL, but it uses a tiny set of semantic directives where normal Markdown is too ambiguous.

## Canonical file

Path:

```text
interactive\source\YYYY\slug.article.md
```

Public generated links:

```text
https://tomaskubica.cz/YYYY/slug/
https://tomaskubica.cz/YYYY/slug/source.md
https://tomaskubica.cz/YYYY/slug/caveman.md
```

## Front matter

```yaml
---
format_version: 1
title: "Jak snížit náklady v 15 minutách"
subtitle: "Od snadných výher po pokročilý context engineering."
slug: token-saving-cz
date: 2026-05-29
language: cs-CZ
status: draft
tags:
- AI
- GitHub
source_post: "_posts\\2026-05-04-techniky-pro-usporu-tokenu-v-kodovacich-agentech.md"
canonical_url: "/2026/token-saving-cz/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---
```

Required fields: `format_version`, `title`, `slug`, `language`.

`format_version` is mandatory so old articles remain regenerable when the directive set evolves.

## Normal Markdown stays normal

Use standard Markdown for:

- Paragraphs.
- Headings.
- Bold emphasis.
- Links.
- Bullet and numbered lists.
- Pipe tables.
- Code fences.
- Blockquotes.
- Existing image references such as:

```markdown
[![](/images/2025/2025-02-04-15-32-01.png){:class="img-fluid"}](/images/2025/2025-02-04-15-32-01.png)
```

The generator may convert images into richer lightbox/carousel components, but the source should keep the existing path style.

## Semantic directives

Directives use `:::` fences. They are hints for the generating agent, not direct HTML.

### Group

Groups become major visual sections.

```markdown
::: group id="easy" title="Snadné výhry pro každého"
...
:::
```

### Card

Cards become expandable sections. The body is standard Markdown.

```markdown
::: card number="02" title="Explicitní kontext místo širokých promptů" default="open"
Text...
:::
```

Recommended fields:

- `number`: visible ordering label (`00`, `01`, `★`, `A`, ...).
- `title`: card title.
- `default`: `open` or `closed`.

### Callout

```markdown
::: callout type="warning" title="Pozor"
Nezkracujte bezpečnostní nebo destruktivní instrukce.
:::
```

Types: `note`, `warning`, `rule`, `author`, `source`, `verdict`.

### Labeled code

Prefer code fences with optional labels:

````markdown
```text label="Drahé" tone="bad"
Pochop tento repozitář a oprav problém s loginem.
```

```text label="Levné" tone="good"
Soustřeď se na src\auth\login.ts a tests\auth\login.test.ts.
Bug: validateEmail odmítá user+tag@example.com.
Přidej test a oprav jen tohle chování.
```
````

The generator can render `tone="good"` and `tone="bad"` as subtle labels, not colorful warning banners.

### Tabs

```markdown
::: tabs id="kid-message"
::: tab id="v1" title="1 · Pečlivá máma"
Text...
:::
::: tab id="v2" title="2 · Úsporně (caveman)"
Text...
:::
:::
```

Tabs are for true alternatives: same scenario, different level, different model, different implementation option.

### Reveal

Use for nested optional detail inside a card.

```markdown
::: reveal title="Klikněte na příklady níže"
Detailed content...
:::
```

### Presenter notes

Presenter notes are not primary article text. They may become a slide-mode overlay or stay hidden in source only.

```markdown
::: presenter-note
When presenting live, spend less time on the model price table and more on cache/input/output ratios.
:::
```

### Agent notes

Agent notes are instructions for future generation, research, or rewriting. They must not appear in public HTML unless explicitly requested.

```markdown
::: agent-note
Keep the next paragraph byte-identical. Do not summarize.
:::
```

## Generated HTML requirements

The generator should:

- Preserve Czech prose unless the source asks for rewriting.
- Preserve section and card order.
- Generate stable IDs from `id`, `slug`, and card titles.
- Add links to `source.md` and `caveman.md`.
- Render with dark/light support.
- Use shared JavaScript for accordions, tabs, and reveal blocks.
- Avoid inline event handlers.
- Use accessible buttons for controls.
- Add `aria-expanded`, `aria-controls`, and keyboard-friendly behavior.
- Keep page readable with JavaScript disabled.

## Caveman generation rules

Caveman Markdown is for agents and technically skilled humans who want a compressed version.

It should:

- Remove greetings, filler, repeated framing, and decorative prose.
- Keep headings, numbers, commands, file paths, URLs, citations, warnings, and constraints.
- Use key/value, arrows, short bullets, and compact tables.
- Preserve ambiguity-sensitive content verbatim: security warnings, destructive commands, legal/compliance claims, benchmark numbers, and instructions where small wording changes change meaning.
- Keep Czech or English terms as in source; do not translate technical English.

Example style:

```markdown
## 04 Output tokeny

Rule: output nejdražší.

Drahé: "Vysvětli detailně všechno..."
Levné: "Vypiš: soubory, proč, testy. Max 5 odrážek."

Pozor: security/destructive/compliance instrukce nezkracovat.
```

## Raw HTML policy

Raw HTML in source is allowed only when:

- It is copied from an existing post and must be preserved.
- It is wrapped in an `agent-note` explaining why Markdown is insufficient.

The generator should not silently drop raw HTML. It must either preserve it or report a blocking conversion issue.

## Review checklist

- Source is readable as Markdown without running a generator.
- Every interactive component has a semantic reason.
- No prose was rewritten by the generator.
- All images use existing `/images/...` paths unless approved.
- `source.md` and `caveman.md` links are present.
- Dark/light theme works.
- JavaScript-disabled page still shows all content.
- Caveman version keeps warnings, numbers, commands, paths, and links.
