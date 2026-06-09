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
published: true
canonical_url: "/YYYY/slug/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
---
```

The `date` is not only internal metadata. The generator shows it in the article header, so keep it accurate when creating or converting articles.

`published` controls whether the source participates in the public site. Omit it or set `published: true` for published articles. Use `published: false` for drafts; draft sources may live in `interactive\source`, but they must not be added to `interactive\article-index.json` and are excluded from landing page, search, RSS, `llms.txt`, and normal `_site` article output. For local styled preview of a draft, keep a generated snapshot under `interactive\generated\YYYY\slug\` and run `python tools\generate_interactive_site.py --preview-drafts`; normal generator runs remove draft pages from `_site` again.

During iterative drafting Tomas may use standalone `<...>` blocks for instructions to the assistant. Treat those as private authoring notes, not public article text. Do not strip or reinterpret angle brackets inside code fences, HTML snippets, generic type examples, or normal inline prose unless the note is clearly a standalone instruction block.

Prefer normal Markdown for prose, headings, lists, tables, links, code, blockquotes, and images. Screenshots can stay as normal Markdown images in source; the generator renders them as linked figures that use the shared in-page lightbox with zoom, panning, wheel zoom, and pinch zoom.

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

Visible source-numbered cards should start at `01`. Do not use `number="00"` for public article points; if an introductory wrapper is useful during generation, keep it unnumbered.

## Component syntax authors should know

Use `label="..."` on code fences when the reader needs context such as a file path, command purpose, transcript title, or generated artifact path. The generator renders that label as a compact header attached to the block.

````markdown
```bash label="Instalace z centrálního katalogu"
gh skill install owner/catalog skill-name --scope project --agent github-copilot
```
````

For long natural-language transcripts, keep a normal labeled text fence. The generator preserves monospace layout and uses horizontal scrolling when needed; do not ask for wrapping inside transcript fences.

````markdown
```text label="Transcript"
> User prompt

Agent response...
```
````

Use `sequence` only for a deliberate short evolution/path, usually 3-5 items:

```markdown
::: sequence title="Cesta od znalosti ke sdílené schopnosti"
1. **Skill jako kontext** — Markdown vysvětlí API a dobrý postup.
2. **Přidání CLI** — agent používá stabilní příkazy.
3. **Vyšší operace v CLI** — opakované workflow se přesune do kódu.
:::
```

Use `steps` for a lifecycle or process where each item needs a title plus short explanation:

```markdown
::: steps title="Životní cyklus zlepšení"
1. **Local experiment** — konzumentský tým zkusí dočasný PoC.
2. **Benchmark** — zachytí před/po evidenci.
3. **Issue with template** — otevře se issue v katalogu.
:::
```

Use `summary-grid` for the final article payoff with short labeled takeaways. Use `detail-grid` for 2x2 conclusion/comparison tiles where each item has a short visible summary and a longer detail. Use `arrow-list` for final checklists or action lists that should look like summary arrows rather than ordinary bullets. Use `closing` for the final one-sentence punchline; every article should try to end with one.

```markdown
::: summary-grid
- **Katalog**: centrální zdroj pravdy.
- **Governance**: issue, triáž, lidský gate a PR.
:::

::: detail-grid title="Závěry" hint="Klikněte na kartu pro detail"
::: detail-card title="Software je paměť" summary="Skript nebo CLI uloží opakovatelný postup."
Delší detail pro čtenáře.
:::
::: detail-card title="Kontext vs. zpětná vazba" summary="Někdy rozhoduje doménový kontext, jindy měřitelná smyčka."
Delší detail pro čtenáře.
:::
:::

::: arrow-list title="Checklist"
- Používejte centrální katalog.
- Měřte změny benchmarkem.
- Distribuujte vylepšený skill zpět všem.
:::

::: closing
Lokální skill je začátek. **Centrálně řízený proces** je to, co z něj udělá týmovou schopnost.
:::
```

Do not infer a complex infographic from every numbered list. Use `sequence` and `steps` only when the author intends a visual process/timeline treatment.

`presenter-note` is for live talk hints and should not appear in public HTML. `agent-note` is for future agents and should not appear in public HTML.
