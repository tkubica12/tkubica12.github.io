---
title: "Cheaper and faster agents with progressive disclosure MCP through Foundry Toolbox Search"
slug: foundry-toolbox-search
date: 2026-06-09
language: en
status: published
canonical_url: /en/2026/foundry-toolbox-search/
source_slug: foundry-toolbox-search
translated_from_hash: b6cf4c9ec39f63038337faf89a15f4503641d175fa3a98784f3d2419c71ac8a4
translation_status: current
---

# Cheaper and faster agents with progressive disclosure MCP through Foundry Toolbox Search

Machine translation of the Czech source.

- Published interactive article: `/en/2026/foundry-toolbox-search/`; translated source in `interactive\translations\en\2026\foundry-toolbox-search.article.md`.
- Demo repo: https://github.com/tkubica12/foundry-toolbox-search
- Main idea: Foundry Toolbox unifies MCP endpoints; Tool Search reduces model-side input tokens through progressive disclosure.
- Chapters: MCP token explosion; Foundry Toolbox; direct MCP; cold Tool Search; warm auto-pin; variant comparison.
- Direct MCP imports all 150 tool schemas into model context. It is simple, but expensive because the model pays for all tool definitions even when it uses one tool or none.
- Cold Tool Search gives the model only `tool_search` and `call_tool`, then retrieves full definitions as needed. In the demo, input dropped about 75% for one tool and about 72% for three tools compared with direct MCP.
- Warm Toolbox with auto-pin keeps frequent tools visible and sends the long tail through search. In the demo it had the lowest cost and fewest MCP calls.
- Key takeaway: progressive disclosure with Foundry Toolbox lowers costs and increases AI agent speed.
