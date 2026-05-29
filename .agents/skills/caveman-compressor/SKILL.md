# Caveman compressor

Use this skill to generate agent-friendly compressed Markdown from an article source.

## Goal

Produce `caveman.md`: compact, structured, human-readable, and optimized for future agents. It is not a teaser and not SEO copy. It is a compressed source of truth for understanding the article fast.

## Rules

- Preserve claims, caveats, commands, code identifiers, URLs, prices, token counts, dates, file paths, and warnings.
- Preserve the article's section order.
- Use short headings and terse bullets.
- Prefer fragments over full prose when meaning stays clear.
- Keep Czech language, but keep technical English terms as-is.
- Remove filler, transitions, repeated examples, and rhetorical padding.
- Do not remove security, destructive-action, compliance, or cost ambiguity.
- Do not invent facts or conclusions.

## Suggested shape

```markdown
# Title

META
- url:
- source:
- audience:
- thesis:

STRUCTURE
- 01 ...
- 02 ...

KEY POINTS
- ...

DETAILS
## Section
- ...

COMMANDS / CODE / TABLE FACTS
- ...

WARNINGS
- ...

VERDICT
- ...
```

Use this shape flexibly. If the article is short, compress harder. If it contains code or exact numeric comparisons, keep those parts more explicit.
