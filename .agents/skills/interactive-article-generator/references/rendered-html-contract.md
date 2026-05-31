# Rendered HTML markup contract

This file lists the exact HTML structure that the shared CSS and JS in
`.agents\skills\interactive-article-generator\assets\` expect for every
directive used in `.article.md` sources. Use these snippets verbatim when
producing `index.html` for an article. If markup deviates from this contract,
controls, reveals, tabs, detail grids, callouts and the closing block will look
unstyled or break out of the article layout.

The shell, controls and navigation are also part of the contract and must be
present on every article HTML page.

## Page shell

```html
<!doctype html>
<html lang="cs-CZ">
<head>
  <!-- theme detection script must be first script in head, see THEME_SCRIPT in tools\generate_interactive_site.py -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>/* the canonical THEME_VARIABLES block from the design contract */</style>
  <link rel="stylesheet" href="../../assets/interactive-article.css">
  <title>Article title</title>
</head>
<body>
  <div class="ia-controls" aria-label="Ovládání článku">
    <button class="ia-control" type="button" data-expand-all>Rozbalit vše</button>
    <button class="ia-control" type="button" data-collapse-all>Sbalit vše</button>
    <button class="ia-control theme" type="button" data-theme-toggle>Tmavý režim</button>
  </div>
  <div class="ia-page">
    <header class="ia-header">
      <p class="ia-eyebrow">Eyebrow text</p>
      <h1 class="ia-title">Article title</h1>
      <p class="ia-subtitle">Subtitle</p>
      <p class="ia-date"><time datetime="YYYY-MM-DD">D. M. YYYY</time></p>
      <nav class="ia-links" aria-label="Navigace článku">
        <a href="../../">← Všechny interaktivní články</a>
        <a href="./" aria-current="page" lang="cs-CZ" hreflang="cs-CZ">CZ</a>
        <a href="../../en/YYYY/slug/" lang="en" hreflang="en">EN</a>
        <a href="./source.md">source.md</a>
        <a href="./caveman.md">caveman.md</a>
      </nav>
    </header>
    <main id="content">
      <!-- article body -->
    </main>
    <footer class="ia-footer">
      <div class="ia-article-nav"><a href="../../">← Všechny interaktivní články</a></div>
      <p>Agent-friendly: <a href="./source.md">source.md</a> · <a href="./caveman.md">caveman.md</a></p>
    </footer>
  </div>
  <script src="../../assets/interactive-article.js"></script>
</body>
</html>
```

EN pages use the same shell with `<html lang="en">`, English control labels
(`Expand all`, `Collapse all`, `Dark mode`, `Article controls`,
`Article navigation`, `← All interactive articles`), and the asset path prefix
becomes `../../..` because they live one level deeper under `/en/`.

The controls bar MUST include all three buttons with `class="ia-control"` and
the `data-expand-all`, `data-collapse-all`, `data-theme-toggle` attributes;
shared JS wires them up. The nav MUST include the back link to the index, the
CZ/EN language switcher, and the agent-friendly source/caveman links.

## Group

```html
<section class="ia-group" id="group-id">
  <h2 class="ia-group-title">Group title</h2>
  <div class="ia-card-list">
    <!-- cards -->
  </div>
</section>
```

## Card

```html
<article class="ia-card is-open" data-ia-card>
  <button class="ia-card-head" type="button" aria-expanded="true"
          aria-controls="card-01" data-ia-card-button>
    <span class="ia-card-num">01</span>
    <span class="ia-card-title">Card title</span>
    <span class="ia-card-toggle" aria-hidden="true">▾</span>
  </button>
  <div class="ia-card-body" id="card-01" data-ia-card-panel>
    <div class="ia-card-body-clip">
      <div class="ia-card-content ia-prose">
        <!-- card body -->
      </div>
    </div>
  </div>
</article>
```

Add `is-open` and `aria-expanded="true"` only for the first visible card or any
card explicitly marked `default="open"`; the others use `aria-expanded="false"`
and omit the `is-open` class.

## Callout

```html
<aside class="ia-callout verdict">
  <span class="ia-callout-title">Pointa</span>
  <p>Body...</p>
</aside>
```

`type` attribute maps to one of `note`, `warning`, `rule`, `author`, `source`,
`verdict` and becomes the second class on `.ia-callout`. The title MUST use the
`.ia-callout-title` span; without it the label is unstyled.

## Reveal

```html
<div class="ia-reveal" data-ia-reveal>
  <button class="ia-reveal-button" type="button" aria-expanded="false"
          aria-controls="reveal-id" data-ia-reveal-button>
    <span class="ia-reveal-arrow" aria-hidden="true">›</span>Reveal title
  </button>
  <div class="ia-reveal-body" id="reveal-id" data-ia-reveal-panel>
    <div class="ia-reveal-body-clip">
      <div class="ia-reveal-content ia-prose">
        <!-- reveal body -->
      </div>
    </div>
  </div>
</div>
```

The `.ia-reveal-button` class and `.ia-reveal-arrow` span are required for the
button to look like a clickable disclosure. The body wrapper layers
`.ia-reveal-body > .ia-reveal-body-clip > .ia-reveal-content` are all required
for the slide-down animation.

## Tabs

```html
<div class="ia-tabs" data-ia-tabs>
  <div class="ia-tab-list" role="tablist">
    <button class="ia-tab" id="tab-foo" role="tab" aria-selected="true"
            aria-controls="panel-foo" type="button">Foo</button>
    <button class="ia-tab" id="tab-bar" role="tab" aria-selected="false"
            aria-controls="panel-bar" type="button">Bar</button>
  </div>
  <div class="ia-tab-panel" id="panel-foo" role="tabpanel" aria-labelledby="tab-foo">
    <!-- foo body -->
  </div>
  <div class="ia-tab-panel" id="panel-bar" role="tabpanel" aria-labelledby="tab-bar" hidden>
    <!-- bar body -->
  </div>
</div>
```

Exactly one panel is visible at a time; the others MUST have the `hidden`
attribute. Buttons sit in a single `.ia-tab-list`, panels are siblings to the
list, never nested in it.

## Sequence

```html
<div class="ia-sequence">
  <h3 class="ia-sequence-title">Sequence title</h3>
  <ol class="ia-sequence-list">
    <li class="ia-sequence-item">
      <span class="ia-sequence-step">1</span>
      <strong>Item title</strong>
      <p>Item description.</p>
    </li>
    <!-- 3-5 items -->
  </ol>
</div>
```

## Steps

```html
<div class="ia-steps">
  <h3 class="ia-steps-title">Steps title</h3>
  <ol class="ia-steps-list">
    <li class="ia-step">
      <span class="ia-step-num">1</span>
      <div>
        <strong class="ia-step-title">Step title</strong>
        <p>Step description.</p>
      </div>
    </li>
  </ol>
</div>
```

## Summary grid

```html
<div class="ia-summary-grid">
  <div class="ia-summary-item">
    <strong>Label</strong>
    <p>Short description.</p>
  </div>
  <!-- 2 to 6 items -->
</div>
```

Each item MUST be `.ia-summary-item` with `<strong>` for the label and `<p>`
for the body. A bare `<ul>` inside `.ia-summary-grid` is not styled correctly.

## Arrow list

```html
<div class="ia-arrow-list">
  <h3 class="ia-arrow-list-title">Checklist title</h3>
  <ul>
    <li>Item one.</li>
    <li>Item two.</li>
  </ul>
</div>
```

The arrow glyph is added by CSS via `li::before`; do not bake arrows into the
text.

## Detail grid and detail card

```html
<div class="ia-detail-grid">
  <div class="ia-detail-grid-head">
    <h3 class="ia-detail-grid-title">Grid title</h3>
    <p class="ia-detail-grid-hint">Hint text.</p>
  </div>
  <div class="ia-detail-grid-items">
    <article class="ia-detail-card">
      <div class="ia-detail-card-button">
        <span class="ia-detail-card-title">Card title</span>
        <span class="ia-detail-card-summary">Short summary.</span>
      </div>
      <div class="ia-detail-content ia-prose">
        <p>Longer body shown inline as no-JS fallback.</p>
      </div>
    </article>
    <!-- target 2 or 4 cards for a balanced grid -->
  </div>
</div>
```

The `.ia-detail-grid-items` wrapper is what creates the 2-column grid layout.
Omitting it makes the cards stack full-width and look broken. Title plus
summary MUST be inside `.ia-detail-card-button`; `<h3>` directly inside
`.ia-detail-card` is not styled.

## Closing takeaway

```html
<section class="ia-closing" aria-label="Závěr">
  <div class="ia-quote ia-prose">
    <p>Final one-sentence takeaway with optional <strong>emphasis</strong>.</p>
  </div>
</section>
```

The `closing` block MUST be a top-level section AFTER the last `::: group`,
never inside a card or group. Putting it inside a card hides it behind a
collapsible header and ruins the article ending.

## Figures

```html
<figure class="ia-figure">
  <a href="../../images/YYYY/file.png" data-ia-lightbox>
    <img class="ia-image" src="../../images/YYYY/file.png" alt="Alt text" loading="lazy">
  </a>
  <figcaption>Caption.</figcaption>
</figure>
```

EN pages use the prefix `../../../images/...`. Source Markdown should keep
`/images/...` paths; only generated HTML rewrites them.

## Code blocks with labels

A source fence like:

````
```python label="Setup observability"
code
```
````

renders to:

```html
<p class="ia-code-label"><strong>Setup observability</strong></p>
<pre><code class="language-python">code</code></pre>
```

The label is rendered as a bold paragraph before the block. Do not pass the
`label=` attribute through into the `<pre>` info string; markdown-it/Python
markdown will not recognize it and the label will leak into the page.

## Forbidden shortcuts that produced broken output before

- `<button>Theme</button>` without `ia-control` and `data-theme-toggle` (button
  appears unstyled).
- Omitting `data-expand-all` / `data-collapse-all` buttons (Expand/Collapse all
  controls disappear).
- Omitting the back link and CZ/EN switcher from the article nav.
- Rendering `tab` directives as standalone `<section class="ia-tab-panel">`
  blocks without a `.ia-tab-list` button bar (all panels show stacked
  full-width).
- Rendering `detail-card` as `<div class="ia-detail-card"><h3>...</h3>` without
  `.ia-detail-grid-items` and `.ia-detail-card-button` (cards stack full-width).
- Rendering `summary-grid` as a plain `<ul>` (no boxed items).
- Putting `closing` inside a card (final sentence is hidden in a collapsible).
- Plain `<p>` inside `<section class="ia-closing"><p class="ia-quote">`
  (invalid nested `<p>` after markdown rendering wraps the body again).
