---
name: interactive-article-generator
description: Generate public root interactive HTML, source.md, caveman.md, and shared assets from Tomas Kubica .article.md sources using the repo-local design contract.
---

# Interactive article generator

Use this skill when generating public root interactive HTML from an `.article.md` source.

This skill is a repo-local reference document. Do not assume the runtime auto-loads it; orchestration prompts should explicitly point agents to this file.

## Skill contents

This skill is self-contained:

- `references\source-format.md` explains the Markdown-plus source format.
- `references\design-contract.md` defines the visual and interaction contract.
- `references\rendered-html-contract.md` lists the exact HTML markup the shared
  CSS/JS expect for every directive, the page shell, the controls bar, and the
  article navigation. Treat it as the binding output contract for any agent
  that produces article HTML; deviations cause unstyled controls, broken
  reveals/tabs/detail grids, or hidden closing takeaways.
- `references\writing-style.md` captures Tomas's blog voice for preservation during conversion.
- `references\caveman-compression.md` defines the compact agent-friendly output.
- `assets\interactive-article.css` is the shared public stylesheet.
- `assets\interactive-article.js` is the shared public interaction script.

Do not fetch or read any previous rendered HTML unless the user explicitly asks for comparison. Source Markdown plus this skill folder are the generation contract.

## Output contract

For source `interactive\source\YYYY\slug.article.md`, create:

- `interactive\generated\YYYY\slug\index.html`
- `interactive\generated\YYYY\slug\source.md`
- `interactive\generated\YYYY\slug\caveman.md`
- `_site\YYYY\slug\index.html`
- `_site\YYYY\slug\source.md`
- `_site\YYYY\slug\caveman.md`
- `_site\index.html`
- `_site\search.json`
- `_site\assets\interactive-article.css`
- `_site\assets\interactive-article.js`

Optional English machine translations are non-default and live under `/en/`. For translated source `interactive\translations\en\YYYY\slug.article.md`, create and commit:

- `interactive\generated\en\YYYY\slug\index.html`
- `interactive\generated\en\YYYY\slug\source.md`
- `interactive\generated\en\YYYY\slug\caveman.md`
- `_site\en\YYYY\slug\index.html`
- `_site\en\YYYY\slug\source.md`
- `_site\en\YYYY\slug\caveman.md`
- `_site\en\index.html`
- `_site\en\search.json`

`source.md` must be a faithful copy of the source article, excluding only internal `agent-note` blocks if the source clearly marks them as non-public.

Update `interactive\article-index.json` whenever a published interactive article is added or materially rewritten. Draft sources use `published: false`, stay out of `interactive\article-index.json`, and are excluded from landing page, search, RSS, `llms.txt`, and normal `_site` article output. For styled local review of a draft that already has a generated snapshot, run `python tools\generate_interactive_site.py --preview-drafts`; normal runs remove draft pages from `_site` again. Keep published entries compact: title, subtitle, date, URL, a short summary, a few labels, and theme IDs. Update `interactive\article-index.en.json` when adding or refreshing English translations. The Python site generator uses these committed caches to render the root interactive site, English `/en/` layer, lightweight search data, back-links, language links, and related-article recommendations without LLM calls in CI.

After changing Czech source content materially, actively offer to regenerate or refresh the English translation. Do not edit Czech source while translating. English translations must disclose machine translation and set `translated_from_hash` to the current Czech source hash for agent/tool use, but public pages should keep the notice simple and should not show a reader-facing drift warning.

Copy public assets from this skill folder:

- `.agents\skills\interactive-article-generator\assets\interactive-article.css`
- `.agents\skills\interactive-article-generator\assets\interactive-article.js`

## HTML requirements

- Put the article theme detection script as the first `<script>` in `<head>`.
- Include the exact interactive article CSS variable block from `references\design-contract.md` in a small inline `<style>`.
- Link shared CSS with `../../assets/interactive-article.css`.
- Load shared JS with `../../assets/interactive-article.js`.
- For English article pages under `/en/YYYY/slug/`, link shared CSS/JS with `../../../assets/...` and use `<html lang="en">`.
- Do not add per-article palettes, gradients, or extra component CSS. The visual baseline is the token-saving article: cold GitHub-like dark mode, white/light gray light mode, restrained blue links/accent, thin borders, no warm brown or pink page palette.
- Use semantic HTML: `header`, `main`, `section`, `article`, `footer`, tables, lists, code.
- Preserve Czech prose and technical terms from the source unless the source asks for adaptation.
- Render the front matter `date` visibly in the article header as `<p class="ia-date"><time datetime="YYYY-MM-DD">D. M. YYYY</time></p>`.
- Include visible top links to `./source.md` and `./caveman.md`.
- Include the same links in the footer.
- Article pages should also include a generated link back to the root interactive index and a generated `Doporučeno dál` related-article block based on `interactive\article-index.json`.
- Generated article pages MUST start with ONLY the first main card expanded; every later card is collapsed regardless of any `default="open"` hint in the source. The official site generator enforces this via `normalize_article_card_defaults` and any custom renderer used for preview MUST do the same. Predictable reading start beats per-card author hints.
- The root landing page should lead with recent articles, keep search collapsed behind a compact search control, keep theme cards collapsed by default, and use relative links for local preview.
- Article labels stay in `interactive\article-index.json` for search and recommendations; do not show them as non-clickable pills on index cards.
- Exclude `presenter-note` and `agent-note` content from public HTML.

## Canonical article shell

All generated article HTML, including English translations, must use the same current shell as the shared assets:

- Theme state is controlled by the first head script using `localStorage` key `interactive-article-theme` and `document.documentElement.dataset.theme`.
- The inline variable block uses the shared `--cp-*` tokens from `references\design-contract.md`; do not emit legacy `--ia-*` variables or one-off palettes.
- The page body uses `.ia-controls`, `.ia-page`, `.ia-header`, `.ia-links`, `.ia-card`, `.ia-card-head`, `.ia-card-num`, `.ia-card-toggle`, `data-ia-card-panel`, `.ia-card-body-clip`, and `.ia-card-content.ia-prose`.
- The `.ia-controls` bar MUST include the three buttons with `class="ia-control"` and attributes `data-expand-all`, `data-collapse-all`, `data-theme-toggle`. Without them the dark-mode and expand/collapse-all controls disappear or render unstyled.
- The article `.ia-links` nav MUST include, in this order: the back link to the interactive index (`../../` for CZ, `../../../` for EN), the CZ/EN language switcher, and the `source.md` / `caveman.md` links. The current language link has `aria-current="page"`.
- The `closing` directive MUST render as a top-level `<section class="ia-closing">` AFTER the last group, never inside a card. Inside a card the final takeaway is hidden in a collapsible.
- See `references\rendered-html-contract.md` for the exact markup for every directive, including the required wrappers for `.ia-detail-grid-items`, `.ia-summary-item`, `.ia-tab-list`, `.ia-reveal-body-clip`, etc. Renderers that skip these wrappers produce visibly broken pages.
- Do not emit legacy or foreign shell classes such as `.ia-hero`, `.ia-hero-inner`, `.ia-main`, `.ia-group-heading`, `.ia-group-kicker`, `.ia-card-number`, or `.ia-card-badge`.
- Do not add a visible skip link such as `Skip to content` or `.ia-skip` unless the shared stylesheet defines its hidden-until-focused behavior.

## Component mapping

- `group` -> `<section class="ia-group">`
- `card` -> `<article class="ia-card" data-ia-card>`
- `card` title -> real `<button class="ia-card-head" data-ia-card-button>`
- `reveal` -> nested reveal using `data-ia-reveal`
- `tabs`/`tab` -> ARIA tablist and panels
- `sequence` -> `.ia-sequence` for 3-5 ordered evolution/path items that should read left-to-right on desktop
- `steps` -> `.ia-steps` for lifecycle/process content where every step needs a short title and explanation
- `callout` -> `.ia-callout` with a short visible label
- screenshots and diagrams -> `<figure class="ia-figure">` with linked `<img class="ia-image">` and short caption
- code blocks -> `.ia-code`, optional label, and `good`/`bad` tone classes
- transcript and code fences must preserve monospace layout with horizontal scrolling when needed; do not wrap text fences or apply inline-code background styling inside `<pre><code>`
- summary or checklist sections -> `.ia-summary-grid` when useful
- `detail-grid`/`detail-card` -> `.ia-detail-grid` with clickable tiles for 2x2 conclusion/comparison details; keep detail content inline for no-JS fallback and let shared JS open a native dialog
- `arrow-list` -> `.ia-arrow-list` for final checklists or action lists that should read like summary arrows, not ordinary bullets
- `closing` -> `.ia-closing` for the final strong one-sentence article takeaway; every generated article should try to include one
- short standalone human notes, messages, or memo examples -> `.ia-handwritten-note` when the source context clearly presents them as a handwritten/personal note rather than normal prose; when tabs compare multiple versions of the same message, apply the treatment consistently to every comparable version
- header eyebrow -> source `eyebrow` when present; do not replace it with generated metadata text
- source/caveman header links -> only `source.md` and `caveman.md` unless the source explicitly asks for more
- group headings -> source group title only; numbering belongs in the card number and optional table of contents, not duplicated in the visible group title
- tab panel body content must be visually boxed using `.ia-tab-panel`; do not render changing tab content as plain prose.
- reveal body content must stay readable at normal article size; do not shrink transcript or screenshot evidence text just because it is optional.
- reveal buttons and figure captions must use normal article-reading size; do not make evidence labels look like footnotes.
- when generating local preview HTML under `_site\YYYY\slug\`, make `/images/...` references locally reviewable by using a relative path such as `../../images/...` in `src`/`href`; keep Markdown source paths unchanged.
- final result or conclusion sections should get a distinct summary treatment, typically `.ia-summary-grid`, rather than another plain checklist.
- visible source-numbered cards must start at `01`, not `00`; generated introductory helper cards should be unnumbered.
- adjacent cards must never visually touch. Use `.ia-card-list` where appropriate; the shared stylesheet also provides fallback spacing for adjacent cards.
- linked screenshots/images should rely on the shared in-page lightbox behavior, including built-in zoom controls, mouse/finger panning, wheel zoom, keyboard zoom, and pinch zoom; do not navigate the browser directly to the image.

IDs may be chosen by the generator, but must be stable, readable, and unique.

## Accessibility and no-JS

- Use `aria-expanded` and `aria-controls` for cards and reveals.
- Use `role="tablist"`, `role="tab"`, `role="tabpanel"` for tabs.
- Keep all content present in the HTML.
- The page must be readable if JavaScript fails.
- Do not use inline event handlers.

## Flexibility rule

The generator may choose grouping, card defaults, and whether a table of contents is useful. It must not invent a new visual system. If the design seems insufficient, update the shared design contract or shared assets instead of adding one-off styling to a page.

## Validation checklist

Before finishing:

- Output files exist in the expected paths.
- `interactive\article-index.json` contains the article with compact summary, labels, and theme IDs.
- `interactive\generated\YYYY\slug\` contains the durable rendered snapshot for CI.
- `/index.html` and `/search.json` are regenerated by `tools\build_site.py`.
- HTML links to source and caveman.
- Article HTML links back to the root interactive index and includes one related-article recommendation.
- HTML references the shared CSS and JS.
- No original reference HTML path or URL appears in generated outputs.
- No `presenter-note` or `agent-note` content appears in HTML.
- No inline style attributes or per-page component CSS beyond the mandatory theme variable block.
- Controls have ARIA attributes.
- Article HTML follows the canonical shell and contains no legacy shell tokens (`--ia-`, `theme-light`, `.ia-hero`, `.ia-main`, `.ia-card-number`, `.ia-card-badge`, or visible `.ia-skip`).
