# Quality review and spelling workflows

This reference folds the previous prompt files into the authoring skill:

- `.github\prompts\review.prompt.md`
- `.github\prompts\spell.prompt.md`

## Article review

Review the article with Internet search and fetch where useful. Be concise but precise. Do not change the text until Tomas approves the direction.

Answer:

1. Are there factual errors? If no, say so. If yes, explain and propose corrections.
2. Does the article have good flow and structure? If yes, say so. If not, explain why and propose a better structure.
3. Is the article in Tomas's style? Check recent posts when needed. If it fits, say so. If not, explain where the voice drifts and whether that helps or hurts.
4. Do all links work and match the surrounding claim? If yes, say so. If not, list broken or mismatched links.
5. Is any major information or area missing? If no, say so. If yes, research it and propose what to add, why, where, and suggested wording.

## Spelling and grammar pass

Fix typos without destroying style. In chat, list corrections as:

```text
- původní slovo -> opravené slovo (velmi krátké vysvětlení)
- další slovo -> opravené slovo (vysvětlení)
```

Keep technical English terms unless there is an obvious typo.
