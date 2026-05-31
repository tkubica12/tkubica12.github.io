# Source format reference

The source format is Markdown-first. It should be pleasant for the author to write and useful for an agent to regenerate interactive HTML. It is not a strict compiler DSL.

## Canonical file

```text
interactive\source\YYYY\slug.article.md
```

Optional English machine-translation source:

```text
interactive\translations\en\YYYY\slug.article.md
```

Generated public files:

```text
_site\YYYY\slug\index.html
_site\YYYY\slug\source.md
_site\YYYY\slug\caveman.md
_site\en\YYYY\slug\index.html
_site\en\YYYY\slug\source.md
_site\en\YYYY\slug\caveman.md
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
canonical_url: "/YYYY/article-slug/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
---
```

The `date` field is public metadata. Generated HTML must show it in the article header using a semantic `<time datetime="YYYY-MM-DD">D. M. YYYY</time>` element.

English translation sources add provenance fields:

```yaml
language: en
source_language: cs-CZ
source_slug: article-slug
translation: machine
translated_from_hash: "<sha256 of Czech source article>"
translation_status: current
```

Czech remains canonical and default. English translations publish only under `/en/`, must visibly disclose machine translation, and keep `translated_from_hash` as internal provenance for agents/tools. Public pages should keep the notice simple and should not show a reader-facing drift warning.

## Normal Markdown

Use normal Markdown for paragraphs, headings, bold emphasis, links, lists, tables, code fences, blockquotes, and images. Existing image paths under `/images/...` should remain unchanged in source unless the user approves a change. Generated local preview HTML may rewrite those image `src`/`href` values to a relative path so screenshots work from `_site\YYYY\slug\index.html`. Render screenshots as linked images so the shared in-page lightbox can open them with zoom, panning, wheel zoom, and pinch zoom.

## Directives

Directives use `:::` fences. They are semantic hints for the agent, not direct HTML.

Use only directives and fence attributes that are both documented here and demonstrably rendered in existing successful generated article HTML. If a conversion seems to need a new component or syntax, stop and ask the user whether to implement renderer/style support or approximate the layout with existing supported components. Never invent Markdown-plus syntax and leave it for the renderer to guess.

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

Recommended fields: `number`, `title`, `default`. Visible article card numbering starts at `01`; do not render a visible `00`. If the generator creates an introductory helper card that is not a source-numbered article point, leave it unnumbered. The `default="open"` hint is informational only — the renderer is required to expand ONLY the first card in the article and collapse every other card, regardless of how many sources mark `default="open"`. Sources may keep the hint for documentation, but no preview tool may expand more than the first card by default.

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

Use `label="..."` for file paths, commands, transcript titles, or other code-block context that should appear as a compact header attached to the block. Use `tone="good"` or `tone="bad"` only for actual comparisons.

When converting legacy Jekyll posts that use `{% raw %}` / `{% endraw %}` to protect Helm or Liquid-looking templates, remove the raw wrappers in the interactive source only if the content remains inside a fenced code block. Preserve literal expressions such as `{{- include "maf-demo.labels" . | nindent 4 }}` and `{{ .Values.clusterName | default "aks-cluster" | quote }}` exactly; generated public `source.md` and HTML must show those characters, not evaluate or alter them.

If generated HTML shows literal Markdown such as image syntax, bold markers, or backticks, treat that as a source-format bug first. Do not work around it with a custom renderer or template changes; make `source.md` a faithful copy of a valid `.article.md` that follows the same triple-colon directive syntax as existing successful articles.

For prose transcripts or long natural-language text fences, keep a normal fence. The generator must preserve monospace layout and allow horizontal scrolling when needed. Do not request wrapping for transcript fences.

````markdown
```text label="Transcript"
> User prompt

Agent response with long natural-language lines...
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

Tab bodies are alternatives. In HTML the active body must be visually boxed/paneled so readers can see which content changes when a tab is clicked.

### Reveal

```markdown
::: reveal title="Detail"
Text...
:::
```

Reveal content is optional detail, not footnote text. Keep generated body text at normal article size unless the source explicitly says the content is secondary.

### Sequence

Use `sequence` when the source intentionally describes an ordered evolution or path. Keep it to 3-5 compact items.

```markdown
::: sequence title="Cesta od znalosti ke sdílené schopnosti"
1. **Skill jako kontext** — Markdown vysvětlí API, business kontext a dobrý postup použití.
2. **Přidání CLI** — agent používá stabilní příkazy místo ručního skládání API volání.
3. **Vyšší operace v CLI** — opakované workflow se přesune do kódu.
:::
```

### Steps

Use `steps` for lifecycle or process content where every step deserves a title and short explanation. Prefer source items in `**Title** — description` shape.

```markdown
::: steps title="Životní cyklus zlepšení"
1. **Local experiment** — konzumentský tým zkusí dočasný PoC.
2. **Benchmark** — zachytí před/po evidenci.
3. **Issue with template** — otevře se issue v katalogu.
:::
```

### Summary grid

Use `summary-grid` for final results, conclusions, or compact takeaways. It should be visually distinct from normal lists.

```markdown
::: summary-grid
- **Katalog**: centrální zdroj pravdy pro skill a CLI.
- **Governance**: issue, triáž, lidský gate a PR.
- **Měření**: benchmarky místo pocitu.
- **Distribuce**: konzumenti aktualizují sdílený skill.
:::
```

### Detail grid

Use `detail-grid` for 2x2 conclusion or comparison tiles where each item needs a short visible summary and a longer detail. The generated HTML should show the tiles, clearly signal that they are clickable, and open the full detail in an in-page modal when JavaScript is available. Keep the detail content present inline as a no-JS fallback.

```markdown
::: detail-grid title="Závěry" hint="Klikněte na kartu pro detail"
::: detail-card title="Software je paměť" summary="Skript nebo CLI uloží opakovatelný postup."
Delší vysvětlení, seznamy nebo odkazy.
:::
::: detail-card title="Kontext vs. zpětná vazba" summary="Někdy rozhoduje doménový kontext, jindy měřitelná smyčka."
Delší vysvětlení.
:::
:::
```

### Arrow list

Use `arrow-list` for final checklists, action lists, or "what to do next" summaries that should be visually different from ordinary bullets and closer to the reference article's arrow-point summary style.

```markdown
::: arrow-list title="Checklist"
- Používejte centrální katalog.
- Měřte změny benchmarkem.
- Distribuujte vylepšený skill zpět všem.
:::
```

### Closing takeaway

Every article should try to end with one strong standalone sentence. Use `closing` when the source has the final punchline; render it with the shared `.ia-closing` treatment, not as a normal paragraph or callout.

```markdown
::: closing
Lokální skill je začátek. **Centrálně řízený proces** je to, co z něj udělá týmovou schopnost.
:::
```

### Presenter notes

`presenter-note` blocks are for live presentation guidance. Do not render them in public HTML.

### Agent notes

`agent-note` blocks are instructions for future generation, research, or rewriting. Do not render them in public HTML.

## HTML generation

Preserve Czech prose, section order, card order, code, paths, commands, links, and tables. Generate stable readable IDs. Add source and caveman links. Use shared JavaScript for cards, reveals, tabs, and controls. Keep the page readable with JavaScript disabled.
