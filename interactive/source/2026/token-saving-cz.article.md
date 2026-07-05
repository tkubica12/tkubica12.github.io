---
format_version: 1
title: "Šetříme tokeny v GitHub Copilot"
eyebrow: "Jak snížit náklady v 15 minutách"
subtitle: "Od snadných výher po pokročilý context engineering. Cílem není utratit nejméně tokenů, ale získat z každého maximální hodnotu."
slug: token-saving-cz
language: cs-CZ
status: experimental
date: 2026-07-05
canonical_url: "/2026/token-saving-cz/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

::: group id="intro" title="Mentální model"

::: card number="01" title="Co všechno žere tokeny" default="open"

Náklad neplyne jen z toho, co napíšete do chatu. Sčítá se z mnoha vrstev:

- **Vždy-zapnuté instrukce** — `AGENTS.md`, custom instructions, hooky
- **Vybrané a otevřené soubory** v kontextu
- **Historie chatu** a shrnutí mezi tahy
- **Definice MCP nástrojů** a jejich JSON schémata — i ty, které nepoužijete
- **Výsledky tool callů** zopakované jako input v dalším kroku
- **Výstup modelu** včetně reasoning/thinking tokenů (output tokeny jsou nejdražší)
- **Retries, subagents, smyčky** v agent módu

::: callout type="rule"
Cíl je **scoped sufficiency** — dostatek kontextu, aby Copilot úkol vyřešil správně, ale ani slovo navíc.
:::

**Tři typy tokenů — proč na nich záleží:**

- **Input** — vše, co posíláte modelu poprvé (prompt, kontext, tool results)
- **Cached input** — opakovaný prefix, který model už viděl v předchozím tahu téže session. **~10× levnější** než fresh input.
- **Output** — to, co model vygeneruje, často včetně interních reasoning/thinking tokenů. **~6× dražší** než fresh input, **~60× dražší** než cached input.

::: callout type="warning" title="Output není jen text, který vidíte"
U reasoning modelů se do výstupního rozpočtu a účtování typicky počítá i skryté přemýšlení. Vyšší reasoning effort tedy nezvyšuje jen kvalitu a latenci, ale i nejdražší kategorii tokenů.
:::

**Příklad z reálného aktuálního ceníku (USD za 1M tokenů):**

| Model | Krátký cache | Krátký input | Krátký output | Dlouhý cache | Dlouhý input | Dlouhý output |
|---|---:|---:|---:|---:|---:|---:|
| **gpt-5.5** | $0,50 | $5,00 | $30,00 | $1,00 | $10,00 | $45,00 |
| **gpt-5.4** | $0,25 | $2,50 | $15,00 | $0,50 | $5,00 | $22,50 |
| **gpt-5.4-mini** | $0,075 | $0,75 | $4,50 | — | — | — |
| **gpt-5.4-nano** | $0,02 | $0,20 | $1,25 | — | — | — |

Mini a nano dlouhý kontext nemají.

**Zjednodušená pravidla:**

- **Cache : Input : Output ≈ 1 : 10 : 60**
- **Každý tier dolů je ~3–4× levnější**
- **Dlouhý kontext zdraží ~2× input/cache a ~1,5× output**
- **Cache je důvod, proč `/compact` není zadarmo**

:::

:::

::: group id="easy" title="Snadné výhry pro každého"

::: card number="02" title="Použijte Auto model jako default"

Pokud si nejste jistí, proč potřebujete premium reasoning model, začněte s **Auto**.

- Routuje podle složitosti úkolu, dostupnosti a zdraví systému
- Nezůstane vám pinnutý drahý model na rutinu
- **10% sleva na multiplier** u placených plánů
- Manuální override pro architekturu nebo těžký debug zůstává

V praxi to znamená dvě věci: Auto vybere vhodný model pro session a u placených plánů má **10% slevu na multiplier**. Microsoft k tomu publikoval paper **HyDRA** ([arXiv](https://arxiv.org/abs/2605.17106)): na SWE-Bench Verified umí při stejné kvalitě jako silný Sonnet 4.6 ušetřit **54,1 % nákladů**; v režimu maximální kvality Sonnet dokonce překoná a pořád šetří **12,9 %**.

::: callout type="rule" title="Auto není random výběr modelu"
Copilot kombinuje zdraví modelů v reálném čase s odhadem nároků úkolu — reasoning, code generation, debugging a tool use. Zároveň je cache-aware: model nemění v každém tahu, protože přepnutí modelu, reasoning levelu nebo context size umí rozbít cache prefixu a zdražit další krok ([GitHub blog](https://github.blog/ai-and-ml/github-copilot/getting-more-from-each-token-how-copilot-improves-context-handling-and-model-routing/)).
:::

:::

::: card number="03" title="Explicitní kontext místo širokých promptů"

```text label="Drahé" tone="bad"
Pochop tento repozitář a oprav problém s loginem.
```

```text label="Levné" tone="good"
Soustřeď se na src\auth\login.ts a tests\auth\login.test.ts.
Bug: validateEmail odmítá user+tag@example.com.
Přidej test a oprav jen tohle chování.
```

**Pravidlo:** konkrétní cesty k souborům jsou levnější než průzkum celého repozitáře.

**Bonus: batchujte související úkoly do jednoho promptu.**

```text tone="good"
V src\auth\login.ts:
1. validateEmail — povol user+tag@example.com
2. přidej test do tests\auth\login.test.ts
3. doplň docstring k funkci
4. zapiš změnu do CHANGELOG.md
```

::: callout type="warning" title="Kam až jít?"
Praktický limit je **3–5 souvisejících úkolů** ve stejné oblasti kódu. Nad to agent ztrácí fokus, dělá víc chyb, retries to celé sežerou.
:::

:::

::: card number="04" title="Nalezení souborů jako první krok před implementací"

Místo „rozumíš tomu celému?" se zeptejte:

```text tone="good"
Najdi nejmenší množinu souborů, kterou potřebuju pro pochopení event-driven flow.
Vypiš jen cesty a jednu větu proč. Nedělej shrnutí celého repa.
```

Pak teprve zadejte úkol — s vědomím, co je relevantní.

:::

::: card number="05" title="Omezte délku výstupu (output tokeny jsou nejdražší)"

```text label="Drahé" tone="bad"
Vysvětli detailně všechno, co jsi změnil.
```

```text label="Levné" tone="good"
Vypiš: změněné soubory, proč, testy. Max 5 odrážek.
```

„Caveman" styl výstupu pro reporty:

```text tone="good"
Hotovo. Vypiš: soubory, proč, validace, rizika. Bez úvodu. ≤5 odrážek.
```

::: callout type="warning" title="Pozor"
Nezkracujte bezpečnostní, destruktivní nebo compliance instrukce. Nejednoznačnost stojí víc než ušetřené tokeny.
:::

**Reasoning effort nastavujte stejně vědomě jako délku odpovědi.**

| Nastavení | Kdy dává smysl | Tokenový dopad |
|---|---|---|
| Nízké | rychlé dotazy, malé editace, převody formátu | málo skrytého outputu |
| Střední | běžná agentická práce | obvykle nejlepší poměr cena/výkon |
| Vysoké | architektura, těžký debug, nejasný multi-step problém | více reasoning tokenů, vyšší latence |

::: callout type="verdict" title="Za mě"
Střední reasoning je pro běžné kódování dobrý default. Benchmarky typu Expert-SWE ([benchmark](https://www.digitalapplied.com/blog/reasoning-effort-cost-vs-quality-benchmarks-2026)) ukazují, že u refactoringu bývá sweet spot právě střední effort: nízký často mine cross-file souvislosti, vysoký přidá cenu a někdy i over-engineering.
:::

:::

::: card number="★" title="Ukázka — vzkaz pro dítě ve třech verzích"

Stejná informace ve třech verzích. Ukazuje, kde je „sweet spot" mezi srozumitelností a úsporností.

::: tabs id="kid-message"

::: tab id="v1" title="1 · Pečlivá máma"

Ahoj zlatíčko, mamka přijde domů kolem šesté hodiny večerní. Prosím tě, udělej si nejdřív domácí úkoly z matematiky a češtiny, ano? Až je budeš mít hotové, můžeš si hodinu hrát na tabletu. V lednici je rajská polévka, kterou si ohřej v mikrovlnce na tři minuty na nejvyšší výkon. Nezapomeň prosím vyvenčit Bertíka kolem páté hodiny a dej mu pak granule do misky. Mám tě moc ráda, mamka 💕

| Metrika | Hodnota |
|---|---:|
| Znaky | 388 |
| Tokeny (GPT-5) | 140 |
| Čitelnost | vysoká |
| Pro koho | lidi s časem |

:::

::: tab id="v2" title="2 · Úsporně (caveman)"

Doma v 18:00. Úkoly: M + Č → pak tablet 1h. Polévka v lednici → mikro 3 min. Pes ven 17:00 + granule. Mamka 💕

| Metrika | Hodnota |
|---|---:|
| Znaky | 110 −72 % |
| Tokeny (GPT-5) | 48 −66 % |
| Čitelnost | stále dobrá |
| Pro koho | člověk co rozumí |

:::

::: tab id="v3" title="3 · Extrémně (agent → agent)"

```text
18→mom. úkoly→tablet1h. polévka:mikro3m. pes:17→ven+jíst.
```

| Metrika | Hodnota |
|---|---:|
| Znaky | 57 −85 % |
| Tokeny (GPT-5) | 29 −79 % |
| Čitelnost | špatná |
| Pro koho | agent → agent |

:::

:::

::: callout type="verdict" title="Pointa"
Caveman styl je sweet spot pro reporty, které ještě čte člověk. Extrémní styl má smysl jen pro agent-to-agent handoff nebo durable context.
:::

:::

::: card number="06" title="Vkládejte výňatky, ne celé logy — a u UI raději Playwright"

U terminálových výstupů je screenshot antipattern. Místo 5 000 řádků CI logu pošlete jen relevantní výňatek:

```text tone="good"
Command: npm test
Exit code: 1
Relevantní chyba:
  TypeError: Cannot read property 'id' of undefined
  at UserService.findById (src/services/user.ts:42)

Posledních 30 řádků:
  ...
```

U vizuálních otázek je efektivnější použít **Playwright MCP nebo browser canvas**.

::: callout type="rule"
Pravidlo: text pro text, řízený browser pro vizuál. Statický screenshot až jako poslední možnost.
:::

:::

::: card number="07" title="Jazyk, struktura promptu a tokenizer — proč angličtina není dogma"

Tokenizer je trénovaný hlavně na anglickém textu, ale není to dogma:

1. **Strukturovaný formát smaže většinu rozdílu**
2. **Kvalita má přednost před úsporou**
3. **Cena za chybu > cena za tokeny**

::: reveal title="Normální prompt"

```text
Vytvoř POST endpoint /api/users, který validuje povinné pole name a email,
při chybě vrátí 400 a při úspěchu 201 s vytvořeným uživatelem.
```

| Jazyk | Znaky | Tokeny | vs EN |
|---|---:|---:|---:|
| Angličtina | 148 | **31** | 1.00× |
| Čeština | 148 | **50** | 1.61× |

:::

::: reveal title="Strukturovaný prompt"

```text
POST /api/users
Validuj: name pov, email pov+platny
400 chyby
201 user
```

| Jazyk | Znaky | Tokeny | vs EN |
|---|---:|---:|---:|
| Angličtina | 71 | **20** | 1.00× |
| Čeština | 70 | **23** | 1.15× |

:::

::: reveal title="Verbose prompt"

```text
Prosím tě, mohl bys mi vytvořit nový HTTP endpoint typu POST
na cestě /api/users, který přijme JSON s polem name a email,
validuje, že jsou obě hodnoty přítomné a email je ve správném formátu,
a v případě úspěchu vrátí 201 Created s vytvořeným objektem uživatele,
zatímco při validační chybě vrátí 400 Bad Request s detaily chyb?
```

| Verze | Tokeny | vs strukturovaný |
|---|---:|---:|
| Verbose CZ | **~95** | +313 % |
| Normální CZ | 50 | +117 % |
| Strukturovaný CZ | 23 | baseline |

:::

::: callout type="verdict" title="Závěr"
Používejte rodný jazyk, když jde o kvalitu a vyjadřujete nuance. Pro opakované operační prompty vítězí úsporná angličtina nebo strukturované klíče.
:::

Ještě jedna vrstva: **modely nemají stejný slovník**. To, že dva modely mají stejnou cenu za milion tokenů, neznamená stejnou cenu za stejný text. Anthropic u Claude Sonnet 5 píše, že nový tokenizer vyrobí pro stejný text přibližně **o 30 % víc tokenů** než Claude Sonnet 4.6; per-token cena je stejná, ale ekvivalentní request může stát víc ([Anthropic docs](https://platform.claude.com/docs/en/about-claude/models/whats-new-sonnet-5)). Podobně se mohou lišit modely různých výrobců.

::: callout type="rule"
Když porovnáváte modely, neměřte jen cenu za 1M tokenů. Měřte **cenu za vyřešený úkol**: tokenizer, reasoning effort, počet tool callů, retry rate a kvalitu výsledku.
:::

:::

:::

::: group id="advanced" title="Pokročilé techniky"

::: card number="08" title="Hierarchický kontext — skills místo obřího AGENTS.md"

Always-on instrukce jsou **opakovaná daň** — platíte je v každém tahu.

| Typ kontextu | Kam patří | Pravidlo |
|---|---|---|
| Always-on (drobné) | `AGENTS.md` | jen fakta, která agent nemůže odvodit |
| Path-specific | `.github\instructions\*.instructions.md` | načítá se jen u relevantních souborů |
| Workflow-specific | prompt files | spouští se na vyžádání |
| Detailní capability | `.github\skills\` | progressive reveal — jen když je téma |
| Live data | MCP server | fetch on demand |

::: callout type="rule"
Velký AGENTS.md vs. malý AGENTS.md + jedna relevantní skill → **68,8 % úspora ve weighted units**.
:::

**Nechte agenta psát kontext pro budoucnost.**

```text tone="good"
Napiš do .github\skills\auth-flow\SKILL.md
stručný (≤60 řádků) popis auth flow tak, jak jsme ho právě
pochopili. Zaměř se na: vstupní body, klíčové soubory, pasti,
co dělat při změně. Žádná próza, jen seznamy a odkazy.
```

::: callout type="rule"
Pokud jste se v sessioně něco složitě dozvěděli, je to **kandidát na trvalý kontext**.
:::

:::

::: card number="09" title="MCP progressivně — search → select → fetch"

**MCP má tři skryté nákladové vrstvy:**

1. Tool definice a JSON schémata načtená do kontextu
2. Argumenty tool callu jako output tokeny
3. Výsledky toolu replayované jako input v dalším kroku

```text tone="good"
1. search nebo list kandidáty
2. vyberte jednoho
3. fetch jen detail, co potřebujete pro rozhodnutí
4. shrňte výsledek, než pokračujete
```

::: callout type="warning"
Nepoužívané globální MCP servery stojí tokeny dřív, než je vůbec zavoláte. Držte MCP per-workspace.
:::

Dobrá zpráva: část téhle práce už Copilot začal dělat za vás. VS Code tým popsal **tool search**, kde model dostane jen lehká metadata nástrojů a plná JSON schémata se načtou až na vyžádání ([VS Code blog](https://code.visualstudio.com/blogs/2026/06/17/improving-token-efficiency-in-github-copilot)). U OpenAI modelů GPT-5.4/5.5 to v experimentu snížilo medián celkových tokenů na tah o **8,61–9,81 %** a medián session tokenů o **8,97–10,92 %**. U Anthropic modelů deferring tool definitions snížil u mediánového uživatele celkové tokeny zhruba o **18 %**.

Princip ale zůstává: tool search šetří **definice toolů**, ne objem jejich výsledků. MCP má dál vracet malé kandidáty, filtrovat a detail posílat až na vyžádání.

:::

::: card number="10" title="Deterministické nástroje místo reasoningu přes mnoho tahů"

Pokud existuje algoritmus, který úkol vyřeší **přesně**, nenuťme model dělat to přes několik tahů.

Typičtí kandidáti:

- JSON → XML / CSV konverze
- Token counting, log slicing, schema validace
- Extrakce dependency grafu
- Sort, filter, deduplikace velkých dat
- Generátory ID, šablony s parametry

::: callout type="rule"
Skill se script-backed toolem dělá 1 tool call s deterministickým výstupem místo 5 tahů s pravděpodobností chyby.
:::

:::

::: card number="11" title="Session management — /ask, /undo, /fork, /resume, /new, /clear, /compact, /share, /chronicle"

Ekonomika je vždy stejná: stará cache je nejlevnější, fresh input ~10×, output ~60×.

| Situace | Příkaz | Co se stane |
|---|---|---|
| Krátký dotaz mimo téma | `/ask` (`/btw`) | cache zůstává, odpověď neroste do historie |
| Špatný poslední tah | `/undo` (`/rewind`) | odstraní změny i kontext posledního tahu |
| Sidequest na stejném základě | `/fork` | větve sdílejí cached prefix |
| Návrat po pauze | `/resume` | často cache hit, později input |
| Nové téma | `/new` | stará session uložena, nová bez cache |
| Trvale ukončit | `/clear` | session zahozena, změny v souborech ne |
| Context narostl | `/compact` | drahá operace, output bolus + invalidace cache |
| Export sezení | `/share` | vstup pro analýzu a zlepšování |

`/chronicle tips`, `/chronicle cost-tips` a `/chronicle improve` slouží jako pravidelná self-reflection.

**Governance spotřeby je další vrstva.** V Copilot CLI jde na session nastavit měkký limit přes `/limits set max-ai-credits NUMBER` nebo v neinteraktivním běhu `--max-ai-credits NUMBER` ([docs](https://docs.github.com/copilot/how-tos/copilot-cli/use-copilot-cli/set-session-limit)). Admini pak mohou řídit user-level budgets, cost center per-user limity, cost center budgety, organization/enterprise budgety a hard stop při vyčerpání ([docs](https://docs.github.com/en/copilot/concepts/billing/budgets-for-usage-based-billing)).

:::

::: card number="12" title="Subagents — izolace, ne magická úspora"

Paralelní agenti mohou ušetřit wall-clock, ale **znásobit input tokeny**, pokud čtou stejné soubory.

Použijte subagenta když:

- Práce je opravdu nezávislá
- Kontext jde shardovat podle service / file area
- Stačí levnější model
- Výsledek lze vrátit jako krátké shrnutí

Nepoužívejte když:

- Všichni agenti potřebují stejný kontext
- Úkol je sekvenční
- Coordination overhead dominuje

::: callout type="rule"
Malý handoff: cíl, známá fakta, přesné soubory, omezení, akceptační kritéria, formát výstupu.
:::

Subagent ale nemusí být jen „další velký model ve vedlejším okně". Směr, který GitHub/Vs Code tým popisuje, jsou specializovaní subagenti pro úzké úkoly: hledání ve workspace, spouštění příkazů a sumarizaci výsledků. Cíl je přesunout hlučnou práci mimo hlavního agenta a nechat ji běžet na nejmenším modelu, který ji zvládne ([VS Code blog](https://code.visualstudio.com/blogs/2026/06/17/improving-token-efficiency-in-github-copilot)).

::: callout type="warning" title="Levnější model není automaticky levnější výsledek"
Menší model může být levný na token, ale méně efektivní v hledání, plánování nebo používání nástrojů. Když kvůli tomu udělá víc tool callů, přečte víc souborů nebo vyvolá retries, vyjde nakonec dráž než silnější model, který trefí cestu napoprvé.
:::

:::

::: card number="13" title="Měření jako součást vývoje skills — CI/CD + self-improvement"

Token efficiency není jednorázový audit — je to **engineering discipline s feedback loopem**.

Měřte:

- input, output, cached tokens
- počet tahů
- tool calls
- latency
- retry rate
- kvalitu výsledku

```yaml
on: pull_request
  paths: ['.github/skills/**', 'AGENTS.md', '.github/prompts/**']

steps:
  - run: copilot-token-lab run --scenarios skills-regression --iterations 3
  - run: copilot-token-lab compare --baseline main --head HEAD
  - fail-if: weighted_units_delta > +10% AND quality_score < baseline
  - comment-pr: report.md
```

::: callout type="verdict"
Jediná univerzální rada: **změřte svůj workload**. Cheaper model není automaticky cheaper outcome.
:::

:::

:::

::: group id="summary" title="Shrnutí"

### Snadné

- Auto model jako default
- Reasoning effort nenechávat zbytečně vysoko
- Pojmenujte přesné soubory a done criteria
- Nalezení souborů jako první krok
- Omezte výstup
- Výňatky z logů, ne dumpy
- Strukturovaný formát smaže rozdíl jazyka

### Pokročilé

- Drobný `AGENTS.md` + skills + path instructions
- MCP jako search → select → fetch
- Počítat s tím, že modely mají různé tokenizery
- Deterministické toolery
- `/ask`, `/fork`, `/resume` vědomě, `/compact` opatrně
- Subagents jen na nezávislou práci; discovery/search subagenti jsou slibný směr
- Měřte v CI a ptejte se agenta na sebezlepšení

::: callout type="verdict"
Tokeny nejsou náklad ke škrcení. Jsou **investicí**. Řešte návratnost, ne spotřebu.
:::

:::
