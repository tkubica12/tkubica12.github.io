# Spiral reading: AI podcast from PDFs without losing context

- Source: `interactive\translations\en\2026\spiralni-cteni.article.md`
- Canonical: `/en/2026/spiralni-cteni/`
- Machine translation from Czech slug `spiralni-cteni`, source hash `60164b8b2f44943bf69341adc039c9e5160b1b4dea19487addd3e9faa3a33d15`.

## Thesis

Do not turn a PDF into audio in one blind step. Use AI for spiral reading first: understand the document map, summarize at several levels, ask focused questions, and only then create an audio script for TTS. The real goal is preserving context while changing the medium.

## Workflow

1. Upload the PDF to an AI assistant and map chapters, sections, tables, definitions, warnings, and examples.
2. Ask for a hierarchical summary: five bullets, then chapter-level, then parts relevant to the current need.
3. Build a reading plan: what deserves audio, what is enough as a summary, and what can be skipped.
4. Generate a spoken script from selected parts, with fluent listening language but preserved technical meaning.
5. Send the verified script to TTS or a podcast-style generator.

## Quality checks

- Structure: audio must say whether the current part is introduction, method, result, limitation, recommendation, etc.
- Claims: words like “may”, “usually”, and “only if” must not become “always”. Caveats matter.
- Data: numbers, units, table labels, and assumptions must be accurate or intentionally omitted.

## Prompt pattern

First prompt asks for structure and main argument only, not rewriting. It should return hierarchy, key claims, warnings/limitations/assumptions, and parts likely worth audio.

Second prompt asks for a spoken audio script from selected parts, precise meaning, easier listening sentences, clear chapter transitions, and no invented examples or conclusions.

## Control questions before TTS

- Which important claim from the original PDF was omitted and why?
- Which numbers or tables were intentionally left out?
- Which script parts are paraphrases rather than direct content?
- What should be verified in the original PDF before sharing the audio?

## Use cases and warnings

Useful for first-pass orientation, focused listening to relevant chapters, and remembering the author's logic. For important details, return to the original PDF. For legal, contractual, safety, or medical content, audio is only orientation; the original remains authoritative.

## Final rule

Start with structure, keep the original hierarchy visible, force AI to state omissions/simplifications, and use TTS only after the script is faithful enough.
