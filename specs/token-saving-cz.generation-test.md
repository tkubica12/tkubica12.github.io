# Blind generation test: token-saving-cz

Status: completed draft test

## Test setup

A separate subagent generated `specs\token-saving-cz.generated-test.html` using only:

- `specs\interactive-blog-modernization-plan.md`
- `specs\interactive-article-source-format.md`
- `specs\token-saving-cz.reverse-source.md`

The subagent was explicitly forbidden from reading or fetching the original reference HTML.

## Result

The generated HTML is a usable self-contained interactive page.

Implemented:

- Page header with title, eyebrow, subtitle.
- Links to placeholder `source.md` and `caveman.md`.
- Accordion cards.
- Nested reveal blocks.
- Tabbed comparison block.
- Tables.
- Code blocks with labels.
- Callouts.
- Dark/light theme support.
- Keyboard-aware tabs.
- Accessible buttons with `aria-expanded`, `aria-controls`, `role="tab"`, and `role="tabpanel"`.

Measured component inventory:

| Item | Count |
|---|---:|
| Cards | 14 |
| Reveal matches | 12 |
| Tab-related matches | 8 |
| `source.md` links | 4 |
| `caveman.md` links | 4 |
| JavaScript event handlers | 5 |

## Fidelity assessment

The source format was sufficient to regenerate the article structure and interactions without the original HTML. The result is close enough for a first workflow test, but not close enough to be a visual regression replacement.

What worked well:

- Card order and group structure survived.
- Core Czech text, tables, and code snippets were preserved.
- The "vzkaz pro dítě" tab block regenerated naturally from the source.
- Nested reveal blocks were recreated from semantic hints.
- The generator did not need strict one-to-one HTML tags in the source.

Gaps:

- Visual styling is similar but not exact. Exact spacing, card density, header treatment, and original micro-layout need a stronger design spec or a shared CSS file.
- The generator created some implementation details by taste, such as exact class names and comments.
- Component counting by regex is approximate; a proper future test should parse DOM.
- Initial generation used a few hardcoded colors outside CSS variables. These were manually corrected in the test HTML, and the generator skill must explicitly forbid this.

## Recommendation

The experiment validates the overall approach:

- Keep source flexible and Markdown-readable.
- Use a small semantic directive vocabulary.
- Put stricter reproducibility requirements in the generator skill, not in the author's writing format.
- Add a shared CSS/JS implementation early so future generated articles share exact behavior and visual identity.

Next workflow improvement:

1. Snapshot the original reference HTML into `interactive\snapshots\`.
2. Build the first real `.agents\skills\interactive-article-generator\SKILL.md`.
3. Keep shared assets with the generator skill in `.agents\skills\interactive-article-generator\assets\` and copy them to `_site\assets\` during generation.
4. Re-run the test with a DOM-based checklist instead of visual memory and regex counts.
