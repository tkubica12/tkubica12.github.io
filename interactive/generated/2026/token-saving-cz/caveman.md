# Šetříme tokeny v GitHub Copilot

META
- url: /2026/token-saving-cz/
- date: 2026-07-05
- lang: cs-CZ
- source: source.md
- audience: Copilot users, agent mode, skills/MCP autoři
- thesis: scoped sufficiency = dost kontextu pro správné řešení, nic navíc. Tokeny = investice; řešit návratnost, ne spotřebu.

KEY POINTS
- Tokeny žerou: always-on instrukce, otevřené/vybrané soubory, historie chatu, MCP tool definice+JSON schémata, tool results replay, output včetně reasoning/thinking tokenů, retries/subagents/smyčky.
- Typy: input; cached input; output.
- Poměr nákladů: cache : input : output ≈ 1 : 10 : 60.
- Tier dolů ≈ 3-4× levnější; dlouhý kontext ≈ 2× input/cache, ≈1,5× output.
- Reasoning effort zvyšuje nejdražší kategorii: output/reasoning tokens + latenci.
- Modely nemají stejný tokenizer; stejná cena za 1M tokenů ≠ stejná cena za stejný text.
- `/compact` = drahý output bolus + cache invalidace.

DETAILS

## 00 Mentální model
- Cíl: scoped sufficiency.
- Input = prompt + kontext + tool results.
- Cached input = opakovaný prefix ve stejné session; ~10× levnější než fresh input.
- Output = generovaný text + často interní reasoning/thinking; ~6× dražší než fresh input, ~60× dražší než cached input.
- Ceník USD / 1M tokenů:
  - gpt-5.5: cache $0,50; input $5,00; output $30,00; long cache $1,00; input $10,00; output $45,00.
  - gpt-5.4: cache $0,25; input $2,50; output $15,00; long cache $0,50; input $5,00; output $22,50.
  - gpt-5.4-mini: cache $0,075; input $0,75; output $4,50.
  - gpt-5.4-nano: cache $0,02; input $0,20; output $1,25.
  - Mini/nano nemají dlouhý kontext.

## 01 Auto model
- Default Auto, pokud není jasný důvod pro premium reasoning.
- Routuje dle složitosti/dostupnosti/zdraví systému.
- Nezůstane drahý model pinnutý na rutinu.
- Placené plány: 10% sleva na multiplier.
- Override pořád pro architekturu/těžký debug.
- Microsoft HyDRA paper: https://arxiv.org/abs/2605.17106
- HyDRA v Copilot Auto: task-aware routing podle reasoning, code generation, debugging, tool use + model health.
- SWE-Bench Verified:
  - při stejné kvalitě jako silný Sonnet 4.6: 54,1 % cost savings.
  - peak-quality Sonnet 4.6 překoná a pořád šetří 12,9 %.
- GitHub blog: https://github.blog/ai-and-ml/github-copilot/getting-more-from-each-token-how-copilot-improves-context-handling-and-model-routing/
- Cache-aware: nepřepínat model/reasoning/context size uprostřed session bez důvodu; může rozbít cached prefix.

## 02 Explicitní kontext
- Drahé: „Pochop repo a oprav login.“
- Levné: cesty + bug + done criteria.
- Příklad: `src\auth\login.ts`, `tests\auth\login.test.ts`; `validateEmail` odmítá `user+tag@example.com`; přidat test; opravit jen toto.
- Pravidlo: konkrétní cesty levnější než průzkum celého repa.
- Batch: 3-5 souvisejících úkolů. Víc = fokus dolů, retries/chyby nahoru.

## 03 Najít soubory první
- Prompt: „Najdi nejmenší množinu souborů pro event-driven flow. Vypiš jen cesty + 1 větu proč. Neshrnuj celé repo.“
- Pak implementace s přesným kontextem.

## 04 Output tokeny + reasoning effort
- Output nejdražší.
- Drahé: detailní vysvětlení všeho.
- Levné: změněné soubory, proč, testy; max 5 odrážek.
- Caveman report: „Hotovo. Vypiš: soubory, proč, validace, rizika. Bez úvodu. ≤5 odrážek.“
- Nezkracovat safety/destructive/compliance instrukce; nejasnost stojí víc.
- Reasoning effort:
  - nízké: rychlé dotazy, malé editace, převody formátu; málo skrytého outputu.
  - střední: běžná agentická práce; obvykle nejlepší poměr cena/výkon.
  - vysoké: architektura, těžký debug, nejasný multi-step problém; víc reasoning tokenů, vyšší latence.
- Verdikt: střední reasoning dobrý default; Expert-SWE/refactor benchmark (https://www.digitalapplied.com/blog/reasoning-effort-cost-vs-quality-benchmarks-2026) ukazuje střed jako sweet spot, vysoký přidává cenu/latenci a někdy over-engineering.

## ★ Vzkaz pro dítě
- Verbose máma: 388 znaků; 140 tokenů; vysoká čitelnost.
- Caveman: „Doma v 18:00. Úkoly: M + Č → pak tablet 1h. Polévka v lednici → mikro 3 min. Pes ven 17:00 + granule. Mamka 💕“
  - 110 znaků; 48 tokenů; −66 %; pořád čitelné.
- Agent→agent: `18→mom. úkoly→tablet1h. polévka:mikro3m. pes:17→ven+jíst.`
  - 57 znaků; 29 tokenů; −79 %; špatně pro člověka.
- Pointa: caveman = sweet spot pro člověkem čtené reporty. Extrém jen agent-to-agent/durable context.

## 05 Logy a UI
- Terminál: screenshot antipattern.
- Místo 5 000 řádků CI logu poslat: command, exit code, relevantní chyba, stack frame, posledních 30 řádků.
- UI: Playwright MCP / browser canvas.
- Pravidlo: text pro text, řízený browser pro vizuál; statický screenshot poslední možnost.

## 06 Jazyk, struktura, tokenizer
- Angličtina tokenově lepší, ale ne dogma.
- Strukturovaný formát smaže většinu rozdílu.
- Kvalita > úspora. Cena chyby > cena tokenů.
- Endpoint prompt data:
  - normální EN: 148 znaků, 31 tokenů.
  - normální CZ: 148 znaků, 50 tokenů = 1,61×.
  - strukturovaný EN: 71 znaků, 20 tokenů.
  - strukturovaný CZ: 70 znaků, 23 tokenů = 1,15×.
  - verbose CZ: ~95 tokenů; +313 % vs strukturovaný.
- Závěr: rodný jazyk pro nuance; opakované operační prompty = úsporná angličtina / strukturované klíče.
- Claude Sonnet 5 tokenizer: stejný text ≈ o 30 % víc tokenů než Claude Sonnet 4.6; per-token cena stejná, ekvivalentní request může stát víc.
- Měřit cenu za vyřešený úkol: tokenizer, reasoning effort, tool calls, retry rate, kvalita.

## 07 Hierarchický kontext
- Always-on instrukce = opakovaná daň.
- Kam co patří:
  - `AGENTS.md`: drobná fakta, která agent neodvodí.
  - `.github\instructions\*.instructions.md`: path-specific.
  - prompt files: workflow-specific, na vyžádání.
  - `.github\skills\`: detailní capability, progressive reveal.
  - MCP: live data, fetch on demand.
- Malý `AGENTS.md` + relevantní skill vs obří `AGENTS.md`: 68,8 % úspora weighted units.
- Po složitém zjištění nechat agenta napsat stručný skill ≤60 řádků: vstupní body, klíčové soubory, pasti, změny; seznamy+odkazy; žádná próza.

## 08 MCP progresivně
- Skryté náklady: tool definice+schémata v kontextu; argumenty tool callu jako output; tool results replay jako input.
- Flow: search/list kandidáty → vybrat jednoho → fetch jen detail nutný pro rozhodnutí → stručné shrnutí.
- Nepoužívané globální MCP servery stojí tokeny před zavoláním. Držet MCP per-workspace.
- Copilot tool search: https://code.visualstudio.com/blogs/2026/06/17/improving-token-efficiency-in-github-copilot
- Tool search: model dostane lightweight metadata, plná JSON schémata se načtou on demand.
- OpenAI GPT-5.4/5.5 experiment: median total tokens/turn −8,61 až −9,81 %; median session tokens −8,97 až −10,92 %.
- Anthropic deferring tool definitions: median user total tokens zhruba −18 %.
- Tool search šetří definice toolů, ne objem výsledků. MCP pořád má vracet malé kandidáty, filtrovat, detail až na vyžádání.

## 09 Deterministické nástroje
- Pokud přesný algoritmus existuje, nepoužívat vícetahový reasoning.
- Kandidáti: JSON→XML/CSV, token counting, log slicing, schema validace, dependency graph, sort/filter/dedupe, ID generátory, šablony.
- Script-backed skill: 1 tool call s deterministickým výstupem místo 5 tahů a rizika chyby.

## 10 Session management
- Ekonomika: stará cache nejlevnější; fresh input ~10×; output ~60×.
- `/ask`/`/btw`: mimo téma, cache zůstává, odpověď neroste do historie.
- `/undo`/`/rewind`: odstraní špatný poslední tah i jeho kontext.
- `/fork`: sidequest na stejném cached prefixu.
- `/resume`: návrat po pauze; často cache hit, později fresh input.
- `/new`: nové téma, žádná cache.
- `/clear`: ukončí session; soubory zůstávají.
- `/compact`: drahé, cache-invalidating.
- `/share`: export pro analýzu.
- `/chronicle tips|cost-tips|improve`: self-reflection.
- `/limits set max-ai-credits NUMBER` / `--max-ai-credits NUMBER`: měkký session limit v Copilot CLI; 1 AI credit = $0.01.
- Admin governance: user-level budgets, cost center per-user limity, cost center budgets, organization/enterprise budgets, hard stop.

## 11 Subagents
- Šetří wall-clock, ale mohou znásobit input tokeny, když čtou stejné soubory.
- Použít: nezávislá práce; shardovatelný kontext; levnější model; krátké shrnutí.
- Nepoužít: stejný kontext pro všechny; sekvenční úkol; coordination overhead.
- Malý handoff: cíl, známá fakta, přesné soubory, omezení, akceptační kritéria, formát výstupu.
- GitHub/VS Code směr: specializovaní subagenti pro workspace search, command execution, result summarization; nejmenší model, který úkol zvládne.
- Menší model může být levný na token, ale drahý na výsledek, pokud udělá víc tool callů, přečte víc souborů nebo vyvolá retries.

## 12 Měření skills
- Token efficiency = engineering discipline + feedback loop.
- Měřit: input, output, cached tokens, tahy, tool calls, latency, retry rate, kvalitu.
- CI pro `.github/skills/**`, `AGENTS.md`, `.github/prompts/**`:
  - `copilot-token-lab run --scenarios skills-regression --iterations 3`
  - `copilot-token-lab compare --baseline main --head HEAD`
  - fail-if: `weighted_units_delta > +10% AND quality_score < baseline`
  - comment-pr: `report.md`
- Rada: změřte vlastní workload. Cheaper model ≠ automaticky cheaper outcome.

WARNINGS
- Nezkracovat safety/destructive/compliance instrukce.
- Batch limit prakticky 3-5 souvisejících úkolů.
- Vysoký reasoning effort nenechávat připnutý na rutinu.
- `/compact` drahé a cache-invalidating.
- Změna modelu/reasoningu/context size uprostřed session může rozbít cache.
- Globální MCP servery mají always-on náklad.
- Tool search šetří definice toolů, ne objem výsledků tool callů.
- Subagents nejsou magická úspora tokenů.
- Levnější model ≠ automaticky levnější výsledek.

VERDICT
- Snadné: Auto model; reasoning effort vědomě; přesné soubory+done criteria; najít soubory první; krátký výstup; výňatky z logů; strukturovaný formát.
- Pokročilé: malý `AGENTS.md` + skills/path instructions; MCP search→select→fetch; počítat s různými tokenizery; deterministické toolery; `/ask`, `/fork`, `/resume`; `/compact` opatrně; subagents jen na nezávislou práci; discovery/search subagenti slibný směr; měřit v CI.
- Tokeny nejsou náklad ke škrcení. Jsou investice. Řešit návratnost, ne spotřebu.
