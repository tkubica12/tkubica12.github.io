# Design contract

Keep generated interactive articles visually consistent without making the source Markdown a rigid HTML template.

## Visual direction

The `/new/` article style is an article/presentation hybrid:

- Wide centered reading canvas for live presenting.
- Dark and light mode from first paint.
- Neutral surfaces, thin borders, quiet typography, one blue accent color.
- Mostly text, numbers, arrows, tables, and code.
- No colorful icon set.
- Dense enough for technical readers, but expandable for live explanation.
- No glossy gradients, decorative cards, confetti, emoji-heavy UI, warm brown page backgrounds, or pink/green page accents.
- Match the token-saving article visual baseline: cold charcoal dark mode, white/light gray light mode, GitHub-like blue links, subtle surfaces, and compact technical typography.

## Theme contract

Generated HTML must include:

1. The article theme detection script as the first `<script>` in `<head>`.
2. The exact `:root` and `html[data-theme="dark"]` variable block below in a small inline `<style>`.
3. `../../assets/interactive-article.css`.
4. `../../assets/interactive-article.js`.

The shared stylesheet uses `var(--cp-*)` colors only. Per-article HTML must not define its own palette.

Use this script:

```html
<script>
(() => {
  const params = new URLSearchParams(window.location.search);
  const requested = params.get("clawpilotTheme");
  const isTheme = (value) => value === "light" || value === "dark";
  let stored = null;
  try { stored = localStorage.getItem("interactive-article-theme"); } catch {}
  const system = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", isTheme(requested) ? requested : isTheme(stored) ? stored : system);
})();
</script>
```

Use this variable block exactly:

```css
:root {
  --cp-bg: #ffffff;
  --cp-bg-elevated: #f8fafc;
  --cp-surface: #f6f8fa;
  --cp-surface-soft: #eef2f6;
  --cp-panel: #ffffff;
  --cp-text: #172033;
  --cp-text-muted: #475569;
  --cp-text-soft: #64748b;
  --cp-border: #d8dee9;
  --cp-border-strong: #b6c2cf;
  --cp-accent: #0969da;
  --cp-accent-soft: rgba(9, 105, 218, 0.08);
  --cp-link: #0969da;
  --cp-success: #1a7f37;
  --cp-warning: #9a6700;
  --cp-danger: #cf222e;
  color-scheme: light;
}
html[data-theme="dark"] {
  --cp-bg: #0d1117;
  --cp-bg-elevated: #161b22;
  --cp-surface: #161b22;
  --cp-surface-soft: #21262d;
  --cp-panel: #0d1117;
  --cp-text: #f0f6fc;
  --cp-text-muted: #c9d1d9;
  --cp-text-soft: #8b949e;
  --cp-border: #30363d;
  --cp-border-strong: #484f58;
  --cp-accent: #58a6ff;
  --cp-accent-soft: rgba(88, 166, 255, 0.13);
  --cp-link: #58a6ff;
  --cp-success: #3fb950;
  --cp-warning: #d29922;
  --cp-danger: #f85149;
  color-scheme: dark;
}
```

Dark mode must be visible:

- Initial theme follows `?clawpilotTheme=light|dark`, then stored preference, then OS preference.
- A fixed theme button is present.
- Button label changes between `Světlý režim` and `Tmavý režim`.
- Page remains readable if JavaScript does not run.

## Layout

- Main container max width around 1100-1200px.
- Header: eyebrow, large title, subtitle, source/caveman links.
- Header eyebrow comes from source metadata; do not use generated date/language/status text as the visible eyebrow.
- Header links stay minimal: `source.md` and `caveman.md`.
- Optional table of contents when the article has several groups.
- Major groups use small uppercase labels and a thin divider; do not prefix group headings with duplicated numeric labels.
- Cards are stacked with small gaps.
- Adjacent cards must never touch. If a generated page omits a `.ia-card-list` wrapper, the shared stylesheet still provides fallback vertical spacing.
- Expanded card bodies are indented under the card number/title row.
- Summary may use two columns on desktop and one column on mobile.

## `/new/` landing page

The `/new/` index uses the same theme script, variable block, shared CSS, shared JS, typography, surfaces, borders, and restrained blue accent as article pages. It should not introduce a separate visual brand.

Index pages may use:

- Recent article cards in `.ia-index-grid`.
- Expandable theme cards using the standard `.ia-card` behavior.
- A compact chronological list grouped by year.
- A static search input that lazy-loads compact metadata from `search.json`; do not load full article bodies on first paint.
- A visible link to the classic blog.

Keep theme/category count small, typically 3-5. Theme text, summaries, labels, and featured article order come from `interactive\article-index.json`, which agents maintain as a compact semantic cache.

## Article navigation and recommendations

Every generated article page should have a consistent navigation/footer layer:

- A visible link back to `/new/`.
- Existing `source.md` and `caveman.md` links.
- One `Doporučeno dál` related-article block generated from compact metadata.

Recommendations are deterministic at build time: use shared themes, labels, summary/title overlap, and recency as a tiebreaker. Do not hard-code a forever recommendation into article prose.

## Components

Cards:

- Use for major ideas, not every paragraph.
- Header is a real `<button>`.
- Number is visible, monospace, compact.
- Visible numbered article cards start at `01`, not `00`. Introductory helper cards created by the generator should be unnumbered rather than numbered `00`.
- `aria-expanded` and `aria-controls` are required.
- Closed cards must be understandable from the title.

Reveals:

- Use for optional detail inside cards.
- Header is a real `<button>`.
- Keep full content in HTML.
- Keep reveal body text at normal article reading size. Optional does not mean small.
- Keep reveal button text and figure captions at normal article-reading size; evidence labels should not look like fine print.

Sequences and steps:

- `sequence` is for compact evolution/path content, usually 3-5 items, with a visible arrow/progression treatment.
- `steps` is for lifecycle/process content where each item has a title plus explanation.
- Do not infer a complex infographic from an arbitrary numbered list. Use these components only when the source explicitly uses the directive or clearly asks for a sequence/timeline/process visualization.

Tabs:

- Use only for true alternatives.
- Use `role="tablist"`, `role="tab"`, and `role="tabpanel"`.
- First tab selected by default unless source says otherwise.
- Render the panel body as a bordered soft box so the changing content is visually distinct from surrounding prose.

Code:

- Render labeled code blocks with subtle labels.
- Preserve file paths, commands, and text exactly.
- Preserve monospace layout in transcript and code fences. Use horizontal scrolling for long lines; do not wrap transcript fences.
- Ensure inline-code styling does not leak into `<pre><code>`: no per-line text background, no inline padding, no mixed darker text strips inside the code block.
- Do not add copy buttons in v1 unless requested.

Figures:

- Render screenshots and diagrams as clickable `<figure class="ia-figure">` blocks with linked `<img class="ia-image">` elements.
- Keep captions short and factual.
- Put screenshot-heavy evidence inside reveal panels so the main article stays readable.
- For local `_site\new\YYYY\slug\index.html` preview, convert root `/images/...` paths in HTML to a relative path from the rendered file, while leaving `source.md` unchanged.
- The shared JavaScript opens image links in an in-page lightbox when the link target is an image file. The lightbox includes shared zoom controls, keyboard zoom (`+`/`-`), mouse/finger panning when zoomed, wheel zoom, and pinch zoom. Do not replace this with browser navigation or per-page scripts.

`/new/` landing page:

- Lead with newest articles first; search should be compact and collapsed by default so it does not push recent content down.
- Theme cards are closed by default and limited to a small curated set.
- Keep article labels in metadata for search and recommendations, but do not render them as passive non-clickable pills.
- Use relative links from the landing page to article folders and the classic blog so local static preview works.
- For long archives, keep all links in the HTML for no-JS fallback and progressively reveal older rows in client-side batches.

Article defaults:

- Generated article pages should open only the first main card by default. The rest start collapsed; readers can expand individual cards or use page controls.

Final result and summaries:

- A final result section should be visually distinct from ordinary cards when it is the article payoff.
- Prefer `.ia-summary-grid` with short labeled takeaways for final synthesis.
- Use `.ia-detail-grid` for 2x2 conclusion/comparison tiles where readers should click for a longer explanation. Keep the long detail inline in HTML for no-JS fallback; shared JavaScript hides it and opens it in a native dialog when available.
- Prefer `.ia-arrow-list` for practical final checklists or action lists so they read as summary arrows rather than normal article bullets.
- Use `.ia-closing` for the final one-sentence takeaway. Every article should try to end with this concise pointa instead of fading out into an ordinary paragraph.

Handwritten notes:

- Use only for short personal notes, memo examples, or human-message demos, not for normal article prose.
- Render as `.ia-handwritten-note` so the shared stylesheet controls the look.
- Keep the treatment quiet and readable in both themes; it intentionally uses the same warm paper background and dark ink in light and dark mode.
- In a tabbed comparison of multiple versions of the same note, apply the treatment to all versions so switching tabs does not change the visual metaphor.
- Do not add per-page colors or decorative images.

Callouts:

- Use sparingly.
- `rule` for durable rule.
- `warning` for practical risk.
- `verdict` for conclusion.
- `author` for personal viewpoint.
- Keep them quiet: left border, soft background, short label. Use the article accent unless the warning/risk meaning really needs the warning tone.

## Flexibility

The generator may choose exact card grouping, IDs, and table of contents if the source does not specify them. It must not invent a new visual system. If the design is insufficient, update this reference or the shared assets instead of adding one-off page styling.
