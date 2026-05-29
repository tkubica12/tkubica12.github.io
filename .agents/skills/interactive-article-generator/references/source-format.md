# Source format reference

The source format is Markdown-first. It should be pleasant for the author to write and useful for an agent to regenerate interactive HTML. It is not a strict compiler DSL.

## Canonical file

```text
interactive\source\YYYY\slug.article.md
```

Generated public files:

```text
_site\new\YYYY\slug\index.html
_site\new\YYYY\slug\source.md
_site\new\YYYY\slug\caveman.md
```

## Front matter

Required fields:

```yaml
---
format_version: 1
title: "Article title"
subtitle: "Optional subtitle"
slug: article-slug
date: 2026-05-29
language: cs-CZ
status: experimental
canonical_url: "/new/YYYY/article-slug/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
---
```

## Normal Markdown

Use normal Markdown for paragraphs, headings, bold emphasis, links, lists, tables, code fences, blockquotes, and images. Existing image paths under `/images/...` should remain unchanged unless the user approves a change.

## Directives

Directives use `:::` fences. They are semantic hints for the agent, not direct HTML.

### Group

```markdown
::: group id="easy" title="Snadné výhry"
...
:::
```

### Card

```markdown
::: card number="02" title="Explicitní kontext" default="open"
Text...
:::
```

Recommended fields: `number`, `title`, `default`.

### Callout

```markdown
::: callout type="warning" title="Pozor"
Text...
:::
```

Types: `note`, `warning`, `rule`, `author`, `source`, `verdict`.

### Labeled code

````markdown
```text label="Drahé" tone="bad"
Prompt...
```

```text label="Levné" tone="good"
Prompt...
```
````

### Tabs

```markdown
::: tabs id="example"
::: tab id="v1" title="Varianta 1"
Text...
:::
::: tab id="v2" title="Varianta 2"
Text...
:::
:::
```

### Reveal

```markdown
::: reveal title="Detail"
Text...
:::
```

### Presenter notes

`presenter-note` blocks are for live presentation guidance. Do not render them in public HTML.

### Agent notes

`agent-note` blocks are instructions for future generation, research, or rewriting. Do not render them in public HTML.

## HTML generation

Preserve Czech prose, section order, card order, code, paths, commands, links, and tables. Generate stable readable IDs. Add source and caveman links. Use shared JavaScript for cards, reveals, tabs, and controls. Keep the page readable with JavaScript disabled.
