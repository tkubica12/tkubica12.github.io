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

Update `interactive\article-index.json` whenever an interactive article is added or materially rewritten. Keep entries compact: title, subtitle, date, URL, a short summary, a few labels, and theme IDs. Update `interactive\article-index.en.json` when adding or refreshing English translations. The Python site generator uses these committed caches to render the root interactive site, English `/en/` layer, lightweight search data, back-links, language links, and related-article recommendations without LLM calls in CI.

After changing Czech source content materially, actively offer to regenerate or refresh the English translation. Do not edit Czech source while translating. English translations must disclose machine translation, set `translated_from_hash` to the current Czech source hash, and remain publishable when stale; stale translations must show the stronger warning that the Czech original changed and remains authoritative.

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
- Generated article pages should start with only the first main card expanded; later cards should be collapsed for a predictable reading start.
- The root landing page should lead with recent articles, keep search collapsed behind a compact search control, keep theme cards collapsed by default, and use relative links for local preview.
- Article labels stay in `interactive\article-index.json` for search and recommendations; do not show them as non-clickable pills on index cards.
- Exclude `presenter-note` and `agent-note` content from public HTML.

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
