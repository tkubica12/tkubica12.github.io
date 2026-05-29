# Interactive article generator

Use this skill when generating public `/new/` HTML from an `.article.md` source.

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

- `_site\new\YYYY\slug\index.html`
- `_site\new\YYYY\slug\source.md`
- `_site\new\YYYY\slug\caveman.md`
- `_site\new\assets\interactive-article.css`
- `_site\new\assets\interactive-article.js`

`source.md` must be a faithful copy of the source article, excluding only internal `agent-note` blocks if the source clearly marks them as non-public.

Copy public assets from this skill folder:

- `.agents\skills\interactive-article-generator\assets\interactive-article.css`
- `.agents\skills\interactive-article-generator\assets\interactive-article.js`

## HTML requirements

- Put the Clawpilot theme detection script as the first `<script>` in `<head>`.
- Include the exact Clawpilot CSS variable block in a small inline `<style>`.
- Link shared CSS with `../../assets/interactive-article.css`.
- Load shared JS with `../../assets/interactive-article.js`.
- Do not add per-article palettes, gradients, or extra component CSS.
- Use semantic HTML: `header`, `main`, `section`, `article`, `footer`, tables, lists, code.
- Preserve Czech prose and technical terms from the source unless the source asks for adaptation.
- Include visible top links to `./source.md` and `./caveman.md`.
- Include the same links in the footer.
- Exclude `presenter-note` and `agent-note` content from public HTML.

## Component mapping

- `group` -> `<section class="ia-group">`
- `card` -> `<article class="ia-card" data-ia-card>`
- `card` title -> real `<button class="ia-card-head" data-ia-card-button>`
- `reveal` -> nested reveal using `data-ia-reveal`
- `tabs`/`tab` -> ARIA tablist and panels
- `callout` -> `.ia-callout` with a short visible label
- code blocks -> `.ia-code`, optional label, and `good`/`bad` tone classes
- summary or checklist sections -> `.ia-summary-grid` when useful
- short standalone human notes, messages, or memo examples -> `.ia-handwritten-note` when the source context clearly presents them as a handwritten/personal note rather than normal prose; when tabs compare multiple versions of the same message, apply the treatment consistently to every comparable version

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
- HTML links to source and caveman.
- HTML references the shared CSS and JS.
- No original reference HTML path or URL appears in generated outputs.
- No `presenter-note` or `agent-note` content appears in HTML.
- No inline style attributes or per-page component CSS beyond the mandatory theme variable block.
- Controls have ARIA attributes.
