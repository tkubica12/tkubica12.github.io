# Authoring source format

Write articles as normal Markdown with a small number of semantic hints for interactivity.

Canonical path:

```text
interactive\source\YYYY\slug.article.md
```

Use front matter:

```yaml
---
format_version: 1
title: "Title"
subtitle: "Optional subtitle"
slug: slug
date: 2026-05-29
language: cs-CZ
status: experimental
canonical_url: "/new/YYYY/slug/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
---
```

Prefer normal Markdown for prose, headings, lists, tables, links, code, blockquotes, and images.

Use directives only when they add meaning:

```markdown
::: group id="easy" title="Snadné výhry"
...
:::

::: card number="02" title="Explicitní kontext" default="closed"
...
:::

::: callout type="warning" title="Pozor"
...
:::

::: reveal title="Detail"
...
:::

::: tabs id="alternatives"
::: tab id="v1" title="Varianta 1"
...
:::
::: tab id="v2" title="Varianta 2"
...
:::
:::
```

`presenter-note` is for live talk hints and should not appear in public HTML. `agent-note` is for future agents and should not appear in public HTML.
