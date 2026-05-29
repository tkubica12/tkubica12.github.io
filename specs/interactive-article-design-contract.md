# Interactive article design contract

Status: draft v0.1

Purpose: keep generated interactive articles visually consistent without making the source Markdown a rigid HTML template. Agents should use this contract together with the generator skill assets in `.agents\skills\interactive-article-generator\assets\`.

## Visual direction

The `/new/` article style is an article/presentation hybrid:

- Wide, centered reading canvas for live presenting.
- Dark and light mode from the first paint.
- Neutral surfaces, thin borders, quiet typography, one accent color.
- Mostly text, numbers, arrows, tables, and code; no colorful icon set.
- Dense enough for technical readers, but with expandable sections for live explanation.
- No glossy gradients, decorative cards, confetti, emoji-heavy UI, or generic "AI blue".

## Theme contract

Generated HTML must include:

1. The Clawpilot theme detection script as the first `<script>` in `<head>`.
2. The exact Clawpilot `:root` and `html[data-theme="dark"]` variable block in a small inline `<style>`.
3. A link to `../../assets/interactive-article.css` from article pages under `/new/YYYY/slug/`.

The shared stylesheet must use `var(--cp-*)` color variables only. Per-article HTML must not define its own palette.

Dark mode must be obvious:

- Initial theme follows `?clawpilotTheme=light|dark`, then stored preference, then OS preference.
- A visible fixed theme button is present.
- The button label changes between `Světlý režim` and `Tmavý režim`.
- The page remains readable if JavaScript does not run.

## Layout

- Main container: wide enough for live presenting, about 1100-1200px max width.
- Page top: eyebrow, large title, short subtitle, then a compact source/caveman link row.
- Optional table of contents can be added when the article has several groups.
- Major groups use small uppercase labels and a thin divider.
- Cards are stacked with small gaps.
- Expanded card bodies are indented under the card number/title row.
- Summary can use two columns on desktop and one column on mobile.

## Components

### Cards

Use cards for major ideas, not every paragraph.

- Header is a real `<button>`.
- Number is visible, monospace, and compact.
- `aria-expanded` and `aria-controls` are required.
- Closed cards should still be understandable from the title.
- Default-open cards are allowed for the mental model or opening card.

### Reveals

Use nested reveals for examples and optional detail inside cards.

- Header is a real `<button>`.
- Keep the full content in the HTML so no-JS users can read it.

### Tabs

Use tabs only for true alternatives.

- Use `role="tablist"`, `role="tab"`, and `role="tabpanel"`.
- Keep inactive tab panels in the HTML.
- First tab is selected by default unless source says otherwise.

### Code

Render labeled code blocks with subtle labels, not big warning banners.

- `tone="good"` and `tone="bad"` can affect the left border and label color.
- Preserve file paths, commands, and text exactly.
- Do not add copy buttons in v1 unless requested.

### Callouts

Use callouts sparingly:

- `rule` for durable rule.
- `warning` for practical risk.
- `verdict` for author conclusion.
- `author` for personal viewpoint.

Callouts should be quiet: left border, soft background, short label.

## Generation flexibility

The generator may choose the exact card grouping, IDs, and whether to include a table of contents if the source does not specify them. It must not invent a new visual system.

Do not overfit to one reference page:

- Do not copy reference-only class names or inline style quirks.
- Do not rewrite content to resemble a previous page.
- Convert observed design gaps into this contract or shared assets, not one-off page hacks.
