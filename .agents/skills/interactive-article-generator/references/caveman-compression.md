# Caveman compression reference

Generate `caveman.md`: compact, structured, human-readable, and optimized for future agents.

## Compression target

- Default target: 40-55% of the source token count.
- Hard ceiling: 60% unless the source is already dense with code, tables, prices, commands, or legal/safety nuance.
- If first pass is above target, run one more compression pass: merge repeated bullets, remove explanatory transitions, collapse examples to facts, and keep only the shortest wording that preserves meaning.
- Do not chase maximum compression. The result must still be understandable by a human who knows the topic.

## Rules

- Preserve claims, caveats, commands, code identifiers, URLs, prices, token counts, dates, file paths, warnings, and conclusions.
- Preserve article section order.
- Use short headings and terse bullets.
- Prefer fragments over full prose when meaning stays clear.
- Keep Czech language, but keep technical English terms as-is.
- Remove filler, transitions, repeated examples, and rhetorical padding.
- Do not remove security, destructive-action, compliance, cost, or benchmark ambiguity.
- Do not invent facts.

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
