# Interactive blog modernization plan

Status: draft v0.1

## Goal

Create a parallel article system for interactive, presenter-friendly articles without changing the current Jekyll blog behavior. Existing `_posts\` articles stay canonical for the normal site. New experiments publish under `https://tomaskubica.cz/new/`.

The new system has three public artifacts per article:

1. Interactive HTML for humans and live presentation.
2. Source Markdown as the canonical source of truth.
3. Caveman Markdown as a compressed, agent-friendly reading format.

## Current repository constraints

- The site is Jekyll + Chirpy (`_config.yml`, `theme: jekyll-theme-chirpy`) and is deployed by `.github\workflows\pages.yaml`.
- The current workflow runs `bundle exec jekyll build` and uploads `_site`.
- `_posts\` and `images\` are already stable conventions. Keep `images\` unchanged.
- `_drafts\` exists, but using it for this project risks accidental interaction with Jekyll draft previews.

## Recommended architecture

Use a build-time generator that runs after Jekyll and writes directly into `_site\new\...`.

```text
interactive\
  drafts\
    2026\
      article-slug.article.md
  source\
    2026\
      article-slug.article.md
  caveman\
    2026\
      article-slug.caveman.md
  snapshots\
    token-saving-cz.reference.html
  README.md

specs\
  interactive-blog-modernization-plan.md
  interactive-article-source-format.md
  writing-style-profile.md
  token-saving-cz.reverse-source.md
  token-saving-cz.generation-test.md

.agents\
  skills\
    interactive-article-authoring\
      SKILL.md
    interactive-article-generator\
      SKILL.md
    caveman-compressor\
      SKILL.md
    tomas-writing-style\
      SKILL.md
```

Generated output:

```text
_site\
  new\
    2026\
      article-slug\
        index.html
        source.md
        caveman.md
    assets\
      interactive-article.css
      interactive-article.js
```

Why this shape:

- `interactive\source\...` is canonical and not accidentally rendered by Jekyll as a page.
- `_site\new\...` is created only during the GitHub Actions build, so the existing site remains untouched.
- `source.md` and `caveman.md` are copied next to the HTML article, making the agent-friendly links stable.
- Shared `new\assets\...` prevents every article from inventing its own JS/CSS.

## Source of truth rule

`interactive\source\YYYY\slug.article.md` is the only editable source.

Generated HTML is a build artifact. Do not hand-edit generated HTML. If HTML needs a change, update the source Markdown or the generation skill.

The caveman version is derived from source, but it is committed or generated as a visible artifact only when it is reviewed enough to be useful to agents. For v1, generate it into `_site\new\...\caveman.md`; decide later whether to commit `interactive\caveman\...`.

## Build and deploy plan

Phase 1 can be documentation-only and manual generation. Phase 2 wires CI.

Recommended CI evolution:

```yaml
- name: Build Jekyll
  run: bundle exec jekyll build

- name: Generate interactive articles
  run: |
    # future: tool/agent-backed generator
    # reads interactive/source/**/*.article.md
    # writes _site/new/**/index.html, source.md, caveman.md

- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
```

No `_config.yml` change is needed if generated output is written after Jekyll into `_site`. If generated HTML is ever committed under repository root `new\`, then `_config.yml` must explicitly prevent unwanted Jekyll processing and copy behavior must be tested.

## Design principles from the reference HTML

Reference: `https://tomaskubica.cz/gh-copilot-demo/talks/token-saving-cz.html`

Observed components:

- Full-page article/presentation hybrid with a strong title, subtitle, and grouped sections.
- Expandable numbered cards for each idea.
- Nested examples inside cards.
- Tabs for comparing versions of the same content.
- Compact tables for pricing and token comparisons.
- Callouts for punch lines, warnings, and rules.
- Code blocks with positive/negative labels.
- Summary blocks at the end.
- JavaScript-driven accordions, tabs, and reveal blocks.
- Minimal visual language: neutral background, subtle borders, single accent, no colorful icon set.

Design contract for this blog:

- Keep the visual language simple, dark/light, neutral, and quiet.
- Prefer text labels, numbers, arrows, and subtle typographic hierarchy over icons.
- No glossy gradients, decorative emoji-heavy UI, card confetti, or generic "AI blue" visual style.
- Use a shared theme with CSS variables and one small JS file.
- Every interactive control must still degrade to readable static HTML if JavaScript fails.
- Public generated HTML should include links to `source.md` and `caveman.md` near the top and bottom.

## Source format philosophy

The source should not become a rigid one-to-one HTML DSL. The author should still write a readable Markdown article and collaborate with an agent on structure.

But generation must be reproducible enough. Therefore use a small set of semantic hints:

- Front matter for stable metadata.
- Normal Markdown for prose, headings, lists, tables, links, images, code.
- A minimal directive vocabulary for components that plain Markdown cannot express reliably: `group`, `card`, `callout`, `tabs`, `tab`, `reveal`, `presenter-note`, `agent-note`.
- Directives describe intent, not markup. The agent may choose final layout details while preserving component semantics and content.

See `specs\interactive-article-source-format.md`.

## Proposed skills

The `.agents\skills\` directory is a proposed repo-local convention for reusable instructions. Before implementation, confirm which agent runtimes will load it automatically. If a runtime does not load `.agents`, the files still work as source-controlled reference docs, and future AGENTS.md or prompt files can point agents to them explicitly.

Recommended skills:

| Skill | Purpose |
|---|---|
| `interactive-article-authoring` | Help plan an article, research sources, shape the story, suggest components, keep author voice. |
| `interactive-article-generator` | Generate HTML from `.article.md`; enforce design, accessibility, links to source/caveman, shared CSS/JS. |
| `caveman-compressor` | Create compressed Markdown for agents; remove filler but preserve meaning, warnings, commands, numbers, citations. |
| `tomas-writing-style` | Preserve observed Czech author style and editing boundaries. |

## Migration experiment

Use 2-3 articles to tune the workflow:

1. `2026-05-04-techniky-pro-usporu-tokenu-v-kodovacich-agentech.md` - best fit because it already overlaps with the reference talk and has tables, comparisons, caveman examples, and token math.
2. `2026-01-27-3-cesty-k-genui.md` - good fit for tabs/cards/decision matrix.
3. `2026-03-30-ai-code-context-feedback.md` or `2026-05-11-agent-skills-centralni-sprava.md` - good fit for process stepper, CLI collapses, and presenter mode.

## Reverse-engineering test

The reference HTML should be captured as a snapshot in `interactive\snapshots\` before using it as a regression target, because the live URL can change.

Test flow:

1. Reverse-engineer source into `specs\token-saving-cz.reverse-source.md`.
2. Give a subagent only the source-format spec, design contract, and reverse source.
3. Forbid the subagent from fetching or reading the original HTML.
4. Generate a test HTML artifact.
5. Compare against the reference by component inventory, order, text preservation, and interaction coverage.

Pass/fail criteria:

- Must preserve title, subtitle, section groups, card order, card numbers, card titles, core prose, tables, code snippets, callouts, tabs, and summary sections.
- Must implement accordion cards, nested reveal blocks, and tab switching.
- Must expose source/caveman links.
- Exact class names, whitespace, and minor layout choices may differ.
- Czech prose should not be rewritten unless the source explicitly asks for adaptation.

## Out of scope for v1

- Replacing the existing Jekyll homepage, RSS, tags, or sitemap.
- Migrating all old posts.
- Search across `/new/`.
- Comments, analytics changes, newsletter integration.
- A fully deterministic Markdown-to-HTML compiler.
- Perfect visual byte-for-byte match with the reference HTML.

## Open decisions

1. Should `interactive\caveman\...` be committed, or should caveman files be generated only into `_site\new\...`?
2. Should the final public URL be `/new/YYYY/slug/` or `/new/slug/`?
3. Should generated HTML be fully self-contained per article, or use shared `new\assets\interactive-article.css` and `.js` from day one? Recommendation: shared assets.
4. Should external fonts be allowed? Recommendation: no external fonts for v1; use system fonts for privacy, speed, and consistency.
5. Which agent runtime should treat `.agents\skills\...` as executable skills, and which should treat them as reference docs?
