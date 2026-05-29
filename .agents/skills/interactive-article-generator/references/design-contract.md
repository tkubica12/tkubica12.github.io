# Design contract

Keep generated interactive articles visually consistent without making the source Markdown a rigid HTML template.

## Visual direction

The `/new/` article style is an article/presentation hybrid:

- Wide centered reading canvas for live presenting.
- Dark and light mode from first paint.
- Neutral surfaces, thin borders, quiet typography, one accent color.
- Mostly text, numbers, arrows, tables, and code.
- No colorful icon set.
- Dense enough for technical readers, but expandable for live explanation.
- No glossy gradients, decorative cards, confetti, emoji-heavy UI, or generic "AI blue".

## Theme contract

Generated HTML must include:

1. The Clawpilot theme detection script as the first `<script>` in `<head>`.
2. The exact Clawpilot `:root` and `html[data-theme="dark"]` variable block in a small inline `<style>`.
3. `../../assets/interactive-article.css`.
4. `../../assets/interactive-article.js`.

The shared stylesheet uses `var(--cp-*)` colors only. Per-article HTML must not define its own palette.

Dark mode must be visible:

- Initial theme follows `?clawpilotTheme=light|dark`, then stored preference, then OS preference.
- A fixed theme button is present.
- Button label changes between `Světlý režim` and `Tmavý režim`.
- Page remains readable if JavaScript does not run.

## Layout

- Main container max width around 1100-1200px.
- Header: eyebrow, large title, subtitle, source/caveman links.
- Optional table of contents when the article has several groups.
- Major groups use small uppercase labels and a thin divider.
- Cards are stacked with small gaps.
- Expanded card bodies are indented under the card number/title row.
- Summary may use two columns on desktop and one column on mobile.

## Components

Cards:

- Use for major ideas, not every paragraph.
- Header is a real `<button>`.
- Number is visible, monospace, compact.
- `aria-expanded` and `aria-controls` are required.
- Closed cards must be understandable from the title.

Reveals:

- Use for optional detail inside cards.
- Header is a real `<button>`.
- Keep full content in HTML.

Tabs:

- Use only for true alternatives.
- Use `role="tablist"`, `role="tab"`, and `role="tabpanel"`.
- First tab selected by default unless source says otherwise.

Code:

- Render labeled code blocks with subtle labels.
- Preserve file paths, commands, and text exactly.
- Do not add copy buttons in v1 unless requested.

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
- Keep them quiet: left border, soft background, short label.

## Flexibility

The generator may choose exact card grouping, IDs, and table of contents if the source does not specify them. It must not invent a new visual system. If the design is insufficient, update this reference or the shared assets instead of adding one-off page styling.
