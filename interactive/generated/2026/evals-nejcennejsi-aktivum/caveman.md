# Nejcennější aktivum vaší firmy ve světě AI je definice toho, co je dobře.

META
- url: /2026/evals-nejcennejsi-aktivum/
- source: source.md
- date: 2026-07-29
- audience: CTO, architekti, AI leadi v enterprise
- thesis: Hodnota se stěhovala prompt → kontext → agentické chování → specifikace → uzavřená smyčka → **definice toho, co je dobrý výsledek** (evals). Poslední zastávka je jediná, kterou nikdo nedodá zvenčí.

STRUCTURE
- perex: onboarding nového člověka (den na data, půl roku na tacitní znalost)
- G0 O co tady jde: Satya o privátních evalech jako největším IP
- G1 Od promptu k agentovi: 01 prompt engineering, 02 context engineering, 03 agentické chování a paměť
- G2 Od řádku k záměru: 04 růst jednotky zadání, 05 spec-driven development
- G3 Uzavírání smyček u kódování: 06 Shumerův Gauntlet Loop, 07 "It does not.", 08 loop engineering a workshop za $70
- G4 Hill-climbing a enterprise smyčky: 09 tři vrstvy znalosti + Reverse Information Paradox, 10 hill-climbing a 4 vrstvy adopce, 11 Autopiloti a Agent 365, 12 evals spustitelné, 13 zaměstnanec vs. najatý konzultant
- G5 Závěry: 3 sbalovací karty + checklist + closing

KEY POINTS
- Evals = specifikace, kterou jde spustit. Specifikace říká *jak něco udělat*, evals *jak poznám, že je výsledek dobrý*.
- Shumerova smyčka fungovala, protože měla veřejnou definici dobrého výsledku (skutečné screenshoty z Call of Duty). Vaše firma takový referenční bod nemá.
- Pokud model zná vaši firmu dokonale, jste komodita s nulovou marží.
- Tři vrstvy firemní znalosti: explicitní data / institucionální a procedurální / implicitní v hlavách. Předat za odpoledne jde jen ta první.
- Continuous learning (on-the-job) je další fáze adopce, ne lepší chatbot.
- Výsledek učení (evals, skilly, doladěné váhy) musí zůstat ve vlastním tenantu.

DETAILS

## 01 Prompt engineering
- Techniky 2023: pozitivní formulace, důležité na konec, few-shot, "let's think step by step", strukturovat vstup. Tehdy fungovaly.
- Anthropic 2023: inzerát "Prompt Engineer and Librarian" až 335 000 USD/rok (Washington Post).
- arXiv 2506.00058: 72 prompt-engineer pozic z 20 662 na LinkedIn = 0,35 %. Trh nikdy nevznikl.
- Neumřel, jen se rozdělil: mechanická část zmizela v modelu.
- OpenAI reasoning best practices: "Avoid chain-of-thought prompts", "Try zero shot first".
- Anthropic naopak dodnes: příklady jsou "one of the most reliable ways". Není to černobílé, závisí na modelové rodině.
- Verdikt: přestali jsme řešit **jak** se zeptat, začali **na co** se ptáme.

## 02 Context engineering
- Tobi Lütke 19. 6. 2025: "the art of providing all the context for the task to be plausibly solvable by the LLM".
- Karpathy 25. 6. 2025: "the delicate art and science of filling the context window with just the right information for the next step".
- Anthropic 29. 9. 2025: formalizace kurátorství tokenů během inference (prompt, tools, MCP, historie, paměť, externí data).
- Posun: ladíme, co je v zorném poli modelu (context window). Pole ale pořád stavíme my.

## 03 Agentické chování
- Agent si kontext dotáhne sám: query do DB, čtení souborů, iterace.
- RAG není mrtvý - zásadní pro náklady, rychlost a kvalitu.
- Anthropic multi-agent Research: +90,2 % nad single-agent Opus 4 v interním evalu, ale ~15× víc tokenů než běžný chat.
- Microsoft Agentic Retrieval je popsán jako nástroj *pro* RAG patterny, ne náhrada.
- Anthropic Agent Skills 16. 10. 2025, memory tool 29. 9. 2025, otevřený standard agentskills.io 18. 12. 2025.
- Procedurální paměť = agent zobecní vyřešenou slepou uličku do skillu. Začátek učení.

## 04 Jak rostla jednotka zadání
- Řádek (autocomplete) → funkce / multi-file edit → úloha (kódovací agent, sám spustí a opraví).
- Neubývalo práce, ubývalo "jak".
- Na úrovni úlohy se poprvé objevila zpětná vazba (testy → červená → oprava). Zárodek zbytku článku.

## 05 Spec-driven development
- AWS Kiro 14. 7. 2025; GitHub Spec Kit 2. 9. 2025 (Specify → Plan → Tasks → Implement).
- Tři důvody: kód je výstupní artefakt; spec čte člověk i stroj; spec je testovatelná.
- Přinesl nezávislého kontrolora (jeden agent píše, druhý ověřuje) = auditní artefakt.
- TRHLINA: specifikace popisuje **jak něco udělat**, neříká, jak poznám, že je výsledek dobrý.

## 06 Gauntlet Loop
- Matt Shumer 25. 7. 2026: "Claude Opus 5 one-shotted this game" (FPS v ThreeJS). Metodika Gauntlet Loop o 2 dny později.
- Prompt neříká JAK, říká JAK SE POZNÁ HOTOVO: oddělený subagent, tvrdý kritik, slepé srovnání, /loop dokud kritik neřekne dost.
- Shumer: "I gave Claude Code one prompt, then left it alone... I did not sit there steering it, at all." ~55 000 řádků, mnoho hodin.
- Referenční bod: "For the game, I used actual Call of Duty screenshots." Skutečné snímky, ne jen paměť modelu.
- Harness: Playwright + headless Chromium, 11 předdefinovaných pohledů ve full HD (prostředí, světlo, materiály, zbraň, zaměřování, dopady, HUD), slepé srovnání proti CoD snímkům.
- KLÍČOVÝ MOMENT: smyčka fungovala, protože měla hotovou veřejnou definici toho, co je dobře - doslova obrázky ke stažení.

## 07 Vaše firma není Call of Duty
- Repo mshumer/Claude-of-Duty: "The goal was to match a modern Call of Duty. It does not."
- Skóre 3,59 → 4,14 → 4,05 → 5,05 z 10 (jedno kolo horší než předchozí). 2 z 11 pohledů "CLOSE", zbytek "AMATEUR".
- Ve **všech** slepých A/B vyhrálo skutečné Call of Duty.
- Smyčka poctivě změřila neúspěch. To je cennější než naleštěná ukázka bez čísla.
- ZÁSADNÍ ZJIŠTĚNÍ: váš referenční bod nikde neleží. Pokud model zná vaši firmu dokonale, jste komodita s nulovou marží.

## 08 Loop engineering
- Addy Osmani 7. 6. 2026: "replacing yourself as the person who prompts the agent. You design the system that does it instead."
- Peter Steinberger (autor OpenClaw), tentýž den: "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents."
- Autorova interpretace: nemluvím s agentem, mluvím s **předákem**. Ten rozseká záměr, napíše specifikace, rozdá práci a bičuje agenty.
- Případ: jednodenní workshop na Microsoft Foundry. Subagenti očima pedagoga, studenta, grafika, inženýra.
- Výsledek za ~70 USD: dokonalé materiály, fakticky správné, pedagogicky výborné. **Nebyl tam žádný Azure.** Celé do koše.
- Chyba autora: smyčka kontrolovala témata, strukturu, vizuál, návaznost - nikdy nesáhla na reálný zdroj v Azure.
- Verdikt: loop engineering těžkou práci nepřesouvá pryč, jen jinam - z "napiš, jak to má vypadat" na "napiš, podle čeho poznáš, že je to dobře".

## 09 Víme víc, než říkáme
- Tři vrstvy: (1) explicitní data, (2) institucionální a procedurální znalost (často v kódu), (3) implicitní znalost v hlavách.
- Polanyi 1966: "we can know more than we can tell."
- První vrstva je jediná, kterou předáte za odpoledne - a co předáte, jde zkopírovat.
- Předat data výrobci na trénink = výhoda spíš pro něj. Mít data v cloudu není problém, odevzdat kontrolu nad nimi je.
- Satya Nadella 12. 7. 2026 (x.com/satyanadella/article/2076323181154230284): **Reverse Information Paradox**.
  - Arrow: kupující nezná hodnotu informace, dokud ji neodhalíte; po odhalení ji má zadarmo.
  - AI to otočila: know-how musí odhalit **kupující**. Platíte dvakrát - penězi a znalostí.
  - "Models learn from exhaust... Every correction is distilled into institutional know-how... leaks almost imperceptibly: trace by trace, correction by correction, eval by eval."
- Verdikt: co je univerzální, bude v modelu. Co je vaše, si musíte umět nechat - platí pro všechny tři vrstvy.

## 10 Hill-climbing machine
- MAI tým 2. 6. 2026: cíl je "what we think of as a hill-climbing machine: an organization that can continuously improve, cycle after cycle".
- Thinking Machines Lab 10. 7. 2026: "Most AI in use today is trained in a handful of places and then frozen."
- Inkling (15. 7. 2026): model si sám připraví evaly, nasbírá data a dotrénuje se přes Tinker. Řízený experiment.
- Čtyři vrstvy adopce: (1) pomocník na chatu, (2) auditovatelné automatizační workflow, (3) osobní pracant s dopadem do reálného světa, (4) digitální pracovník jako entita v organizaci.
- Vrstva 3 prakticky: Microsoft 365 Copilot Cowork (GA od 6/2026, Outlook + Teams + Office + SharePoint, schvalování citlivých akcí).
- Foundry Agent Optimizer: baseline konfigurace + eval dataset → automaticky lepší instrukce, skilly, popisy nástrojů, volba modelu.
- Foundry Observability: z produkčních traces vyrobí eval dataset. Smyčka: běhy → dataset → optimalizace → lepší agent.

## 11 Autopiloti a agent jako člen týmu
- Build 2026: "Today we are introducing a new category of agents called Autopilots. Autopilots are always-on agents that work autonomously, with their own identity, and act on your behalf."
- První zástupce: Microsoft Scout. Copilot čeká, až se ozvete; Autopilot běží, i když u toho nejste. Souběžné kategorie, ne konkurenti.
- Microsoft Agent 365 GA od 1. 5. 2026: registr agentů, lifecycle, přístupy, Purview, Defender, identita v Entra. "Agent user" má mailbox, OneDrive, UPN, dá se zmínit v Teams.
- Alternativy: Hermes Agent (Nous Research) - "creates skills from experience, improves them during use"; OpenClaw. Můžou běžet v Azure, napojit se na M365 a být spravované přes Agent 365.
- POZOR: "self-improving" dnes = zápis do paměti a úprava lokálních instrukcí/skillů. **Zatím** ne automatická změna vah - ale směr (RLE, doladěné váhy) je jasný.
- Na jindy: koordinované kolektivní učení agentů.

## 12 Evals musí být spustitelné
- Doporučení: formalizovat definici dobrého výsledku (evals, reward funkce, reward model, testy, akceptační kritéria). Musí být **spustitelná**, ne jen napsaná.
- Mustafa Suleyman, MAI keynote: "So with us, the RLEs and the models you build inside of them become your moat." Gradace: evals → prostředí → vlastní model.
- Greg Brockman 12/2023: "evals are surprisingly often all you need".
- Garry Tan (YC) 2025: "Evals are emerging as the real moat for AI startups".
- Anthropic Demystifying evals: jejich "value compounds over the lifecycle of an agent".
- Co odemknou: test modelů proti **své** definici kvality; dotrénování menšího specializovaného modelu; ladění skillů/kontextu/nástrojů proti měřitelnému výsledku; schopnost přepnout model bez létání naslepo.
- Trh není jen OpenAI vs. Anthropic: xAI + SpaceX (2. 2. 2026) a Grok 4.5; Mistral (Apache 2.0); Kimi K3 nad GPT-5.5 i Opus 4.8 v Artificial Analysis indexu; GLM-5.2 celkově níž, ale na dlouhých kódovacích úlohách srovnatelný.

## 13 Zaměstnanec vs. najatý konzultant
- Cloud rozhodně ano. Výnosy z rozsahu jsou zásadní - nejen infra, ale platformy, orchestrace, bezpečnost, compliance, evaluační nástroje, rychlost příchodu modelů.
- Otázka není cloud/onprem, ale **komu se učení připíše**.
- Zaměstnanec: zkušenost zůstává ve firmě, zapisuje ji do vašich systémů. Od dodavatele beru stavební bloky, výsledek je můj (evals, skilly, doladěné váhy, vlastní tenant).
- Konzultant: zkušenost si odnáší k sobě a příští čtvrtletí ji prodá konkurenci = Reverse Information Paradox.
- Satya: firemní traces mají trénovat "not a generalist model, but... the company veteran agent".
- Požadavek na dodavatele: **skutečná hranice důvěry**, uvnitř které se data, traces, evals, doladěné váhy a paměť hromadí dohromady (místo, kde se skládá lidský a token kapitál).
- "In consuming intelligence, you are creating intelligence. And what you create should belong to you."
- Hranice vede mezi **schopností, kterou kupuji** (Copilot pro Excel - v pořádku) a **schopností, kterou vychovávám** (Copilot Cowork, Scout nebo vlastní řešení ve Foundry přes Agent 365).
- Není to o tom, jestli si to napíšete sami. Je to o tom, jestli si necháte to, co se naučí.

WARNINGS
- "Self-improving" dnes neznamená změnu vah modelu.
- Skóre v Claude-of-Duty nebylo monotónní (4,14 → 4,05); jde o Shumerovo vlastní hodnocení, syrová data nejsou publikovaná.
- GLM-5.2 dosahuje frontier úrovně jen na části úloh; Kimi K3 je konzistentnější.
- Multi-agent přístupy stojí řádově víc tokenů (Anthropic ~15×).

VERDICT
- Kdo neumí změřit, co je dobrý výsledek, nemá vlastní AI. Má předplatné.
- Praktické kroky: nejdřív definice dobrého výsledku, pak prompt a nástroje; ověřit, že smyčka měří výsledek a ne formu; sbírat evals jako aktivum; Satyův test - dokážete vyměnit model a stoupat dál?
