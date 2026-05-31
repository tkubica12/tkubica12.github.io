---
format_version: 1
title: "Vlastní data (RAG) pro vašeho AI agenta část druhá - graf znalostí a pokročilé metody"
eyebrow: "RAG bez magie, část 2"
subtitle: "Knowledge graph, sumarizace konceptů a průchod grafem bez frameworkové magie. Pořád Python, PostgreSQL a filmová data."
slug: "rag-part2"
date: "2025-03-12"
language: "cs-CZ"
status: "experimental"
canonical_url: "/2025/rag-part2/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Vlastní data (RAG) pro vašeho AI agenta část druhá - graf znalostí a pokročilé metody

V minulém díle jsme šli bez magie do vyzkoušení technik jako je full-textové a sémantické vyhledávání, query rewriting, reranking a hybridní search, takže jsme se neschovávali za nějaký framework nebo službu a ponořili se do Pythonu a PostgreSQL. Tím jsme dokázali našeho AI agenta obohatit o cílená data a odpovídat na zvídavé filmové otázky uživatelů.

Dnes budeme pokračovat pokročilejšími metodami a přestože se necháme inspirovat technikami jako je GraphRAG, uplácáme si to opět ze studijních důvodů sami.

::: summary-grid
- **Problém**: některé otázky nejsou o jednom dokumentu, ale o agregaci, tématech, žánrech a vztazích.
- **Nápad**: k filmům přidáme koncepty, hrany a sumarizace konceptů. Tedy malý knowledge graph.
- **Experiment**: porovnám breath-first a depth-first varianty s průchodem grafu.
- **Pointa**: pevně daný postup nestačí. Další meta-úroveň je plánování strategie přes LLM.
:::

::: group id="mentalni-model" title="Proč tabulka přestává stačit"

::: card number="01" title="Od dokumentů ke konceptům" default="open"
Minule jsme viděli, že základní přístup k RAGu je velmi úspěšný zejména u dotazů, pro jejichž zodpovězení je potřeba mít specifický detailní kontext. Typicky například dotaz na název filmu, na který si uživatel nemůže vzpomenout, ale je schopen říct o čem to bylo a přidat pár takových detailů.

Nicméně jsou otázky, pro jejichž odpovězení nestačí kontext jen několika filmů, ale jsou třeba o agregacích, konceptech, žánrech, scenériích a tak podobně. Pro jejich odpovězení je tak ideální mít jednak sumarizovaný pohled a dále představu o nějakých vlastnostech, kategoriích, jejich zástupcích a vzájemných vztazích.

Technicky řečeno nestačí nám tabulka, ale graf uzlů (node) a propojení podle různých vztahů (edge, hrana) s tím, že u každého konceptu (typu nodu) potřebujeme ještě sumarizaci a vysvětlení tohoto konceptu. Tedy chceme **knowledge graph**.

::: reveal title="Co bude v mém grafu"
- uzly typu **Movie**,
- koncepty **Genre**, **Character**, **Theme**, **Setting** a **Series**,
- hrany jako `IN_GENRE`, `FEATURES_CHARACTER`, `INCLUDES_THEME`, `SET_IN`, `PART_OF_SERIES`,
- sumarizace konceptů vytvořené LLM nad filmy, které k nim patří.
:::
:::

::: card number="02" title="Inspirace GraphRAG, ale pořád bez magie" 
V následující ukázce se budu volně inspirovat metodou [GraphRAG](https://microsoft.github.io/graphrag/), ale určitě se odchýlím, zjednoduším, abychom si to mohli postavit skutečně sami bez magie.

Vycházejme z předpokladu, že u filmů máme opět jen název a popisek, nic dalšího. V realitě filmů bychom některé graph informace měli v datové sadě vytažené rovnou - herce, režiséra apod. Podobně jako v GraphRAG použijme jazykový model (LLM) k extrakci konceptů jako je prostředí, postava, žánr, téma a série.

Na základě toho potom sestavíme celkový graf a pro každý tento koncept vezmeme filmy, které k němu patří a použijeme LLM k vytvoření sumarizace této vlastnosti.

::: callout label="Pozor na cenu"
Tato přípravná fáze je velmi náročná na čas a spotřebované tokeny LLM. Navíc pokud se k datům něco přidá, musí se pro ně postup spustit také. Objevují se proto i varianty, které část těch volání LLM odkládají ad-hoc až na chvíli, kdy je to potřeba - například [LazyGraphRAG](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/).
:::
:::

::: card number="03" title="Jak se na graf ptát" 
Základním konceptem je vyhledání vstupních uzlů do grafu (nody jsou filmy, žánry a podobné koncepty) a pak nějaké procházení grafu (jdeme po hranách, spojnicích), kde objevujeme další uzly a případně kombinujeme s nějakým snížením počtu nalezených uzlů přes reranking nebo sémantickou podobnost z minulého dílu.

Otázka je, na jaké vstupní body se zaměřit.

| Strategie | Kde začnu | Co tím získám | Co riskuji |
| --- | --- | --- | --- |
| **Depth-first** | konkrétní filmy | detail a konkrétní příklady | chybí globálnější kontext |
| **Breath-first** | koncepty a jejich sumarizace | nadhled, témata, agregace | méně vazby na konkrétní filmy |
| **Traversal** | pohyb po hranách | propojení konceptů a filmů | může explodovat počet kandidátů |
| **Reranking** | redukce kandidátů | menší a relevantnější kontext | pořád nemusí pochopit záměr otázky |

Tím to pro dnešek skončí, ale ještě chci připravit další díl, ve kterém budeme s využitím LLM plánovat a iterativně procházet celým procesem podobně, jako je to u metody DRIFT (Dynamic Reasoning and Inference with Flexible Traversal). Tohle, i když ve značně vylepšené a komplikovanější formě, je pod kapotou **Deep Research** na platformách jako je Perplexity, Google Gemini nebo ChatGPT.
:::

:::

::: group id="pipeline" title="Jak graf postavím"

::: card number="04" title="Notebooky a celý postup" 
Jako minule, **otevřete si prosím k článku patřičný [notebook](https://github.com/tkubica12/azure-workshops/tree/main/d-ai-rag)** - odkaz na konkrétní dám do každé kapitolky.

::: steps
1. **Extrakce konceptů**: z popisu filmu vytáhneme žánry, postavy, témata, prostředí a série.
2. **Uložení grafu**: v PostgreSQL přes Apache AGE založíme nody a hrany.
3. **Sumarizace konceptů**: pro každý koncept necháme LLM shrnout, co znamená v rámci naší kolekce filmů.
4. **Vektorizace**: filmy i koncepty dostanou embedding pro sémantické hledání.
5. **Dotazování**: kombinujeme semantic search, traversal a reranking.
:::
:::

::: card number="05" title="Extrakce konceptů" 
Nejprve musíme extrahovat koncepty z popisu filmů. **Tady je [notebook](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step1_extract.ipynb)**.

Víceméně jednoduše jdeme film po filmu s jednoduchým promptem:

```text
Extract structured information from the following movie title and overview.

Title: {{title}}
Overview: {{overview}}

Please extract the following information in JSON format:
- genres: [list of genres]
- characters: [list of character names]
- themes: [list of thematic elements]
- setting: [time periods and/or locations]
- series: [list of series or saga names]

If there are no relevant details for a category, return an empty array.
```

doplněným o structure output, tedy o předvídatelný formát výstupu:

```python
class EnhancedMovie(BaseModel):
    genres: List[str]
    characters: List[str]
    themes: List[str]
    setting: List[str]
    series: List[str]
```

Všechno naházím do JSON souborů a nakonec z něj vytvořím jeden velký. Výsledek je [tady](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/data/movies_graph.json).
:::

::: card number="06" title="Uložení grafu do PostgreSQL" 
**Uložení do PostgreSQL hledejte v tomto [notebooku](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step2_store.ipynb)**.

PostgreSQL má k dispozici speciální extension, která z klasické relační databáze udělá grafovou podporující rozšířený dotazovací jazyk cypher. Alternativou je Gremlin jazyk, ale to tato extension nepodporuje. Místo nějaké specializované databáze typu Neo4J tak můžeme použít Apache AGE, která je kompatibilní s Azure Database for PostgreSQL Flexible Server.

Nejdřív pozakládáme nody typu Movie a následně nody typu Genre, Character, Theme, Setting a Series. Zatím v nich nebude víc, než jméno, například horor nebo Harry Potter. Pak přidáme jejich hrany.

::: reveal title="Co mě na AGE trochu trápilo"
Trochu nepříjemné pro mě je, že cypher query se musí uzavřít do SQL query, čímž mi nefungovalo použití parametrů v psycopg2, takže jsem musel jít přes f-stringy a escapovat jednoduché uvozovky.

Jak se zjistí později tahle "rozdvojenost" je nepříjemným limitem jazyka, kdy bude obtížné kombinovat sémantické vyhledávání (vyžaduje klasické PostgreSQL tabulky) s grafovým - jak uvidíte, budu to lepit v Pythonu. Což ale vzhledem k potřebě rerankingu nakonec nevadilo.

Rozhodně se plánuji podívat na využití Cosmos DB a jeho schopnost vektorového hledání v kombinaci s graf dotazy, jestli to tam není lepší.
:::
:::

::: card number="07" title="Sumarizace konceptů" 
**Jdeme do [notebooku pro sumarizaci](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step3_summarize.ipynb)**.

V dalším kroku potřebuji pro jednotlivé nalezené koncepty (Sci-Fi, 13. století, Star Wars, Praha, Rytíř, Albert Einstein) udělat sumarizaci, tedy shrnout, co to je. LLM naservíruji seznam příslušných filmů.

U některých konceptů, třeba žánr drama, vyteču z kontextového okna - to jsem pro jednoduchou ukázku nechtěl řešit, tak to prostě oříznu. Ono jich zas tak moc co se nevejdou není.

::: reveal title="Prompt pro sumarizaci archetypu postavy"
```text
TASK:
Create a comprehensive summary of the "{{name}}" character archetype based on movies featuring this type of character. Make sure all information is based on the movies in the collection and not on external knowledge.

Instructions:
1. Define essential traits, motivations, and narrative functions of the "{{name}}" archetype.
2. Provide examples of at least 5 movies prominently featuring this archetype.
3. Describe typical audience expectations and emotional responses associated with this archetype.
4. Highlight common narrative arcs and character development patterns involving this archetype.
5. Explain how this archetype typically interacts with specific genres, settings, or themes.
6. Include aggregated data from the movie collection to support your summary.
```
:::
:::

::: card number="08" title="Vektorizace mimo grafové properties" 
**Vektorizaci uděláme v [notebooku](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step4_index.ipynb)**.

Tady bylo nutné vyřešit jeden zádrhel. AGE pod kapotou funguje tak, že v PostgreSQL vytvoří tabulku nodů s unikátním ID a atributem properties. Když potom u nodů uložím nějaké jejich parametry, například popis filmu nebo sumarizace konceptu, ukládá to do properties sloupečku jako JSON.

Pokud bych do toho přidal embedding jako vlastnost nodu, skončí to někde uvnitř JSON a nebude možné použít pgvector pro hledání podobností. To je nepříjemný limit, který jsem vyřešil tak, že držím separátní standardní tabulky čistě pro embedding - id a vektor per film nebo koncepty.
:::

:::

::: group id="dotazovani" title="Velké finále: ptáme se přes graf"

::: card number="09" title="Sada otázek pro porovnání" 
Teď přichází velké finále a jdeme odpovídat na otázky. Hledejte **v tomto [notebooku](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level2_step5_query.ipynb)**.

Rozšířil jsem okruh otázek, ať je to zajímavější:

```python
questions = [
    "What movies are about Abby?",
    "I have seen all Star Wars movies and would like tips for something similar I can watch next.",
    "What is the most common genre of the movies where one of key figures is called Mark?",
    "Are there any movies where Prague takes major role and present city as mysterious and ancient?",
    "When movies about drugs are concerned, is it usually rather serious or funny?",
    "What are some movies featuring a strong female lead that also involve adventure?",
    "Which Western films feature outlaws riding to their doom in the American Southwest?"
]
```

Ty otázky schválně nejsou všechny stejného typu. Některé hledají konkrétní film, jiné podobnost, jiné agregaci a jiné atmosféru.
:::

::: card number="10" title="Čtyři strategie vedle sebe" 
::: tabs

::: tab title="Breath-first"
Pojďme najít vstupní uzly a já to udělám přes všechny typy, tedy jak popisky filmů, tak popisky všech konceptů (Character, Genre, Theme, Series, Setting). Uděláme sémantický search na popisky, vezmeme 20 nejbližších a naservírujeme je LLM.

| Otázka | Pozorování |
| --- | --- |
| Abby | S obrovskou převahou vybírá Character nody s Abby nebo podobným jménem, ale odpověď není nic moc, protože sumarizace konceptů neobsahují dost referencí na filmy. |
| Star Wars | Chytá se na Setting a Series, například Imperial Era, Clone Wars Era, Various Planets nebo Star Wars Saga. Odpověď na filmy je tentokrát velmi slušná. |
| Mark | Všechno nody typu Character, dle očekávání. |
| Praha | Vrací hlavně Setting, byť Praha tam není; možná ji LLM nevyextrahovalo jako samostatný koncept. Hodně tam jsou Evropská města a Czechoslovakia. |
| Drogy | Hodně Theme (Drug Trade, Substance Abuse) a důležité Genre (Stoner a komedie). Díky příkladům v sumarizacích je odpověď slušná. |
| Silná žena + adventure | Nachází hodně uzlů Character. |
| Westerny z jihozápadu | Logicky docela dost Setting. |
:::

::: tab title="Breath-first + traversal"
Pojďme teď udělat to důležité - přidejme k výsledkům nějaký pohyb po grafu, zejména z konceptů směrem k filmům. Pokud jich je tam víc, vybereme nejlepší přes reranking a nakonec ještě výsledek omezíme a znovu uděláme reranking.

| Otázka | Změna proti čistému breath-first |
| --- | --- |
| Abby | 6 filmů místo 2, mnohem lepší. |
| Star Wars | Dopadl podobně; ani tento postup není tak dokonalý, jak bychom mohli chtít. |
| Mark | Prakticky stejně. |
| Praha | Spíše hůř, byť se o filmu Nesnesitelná lehkost bytí dozvídáme víc. |
| Drogy | Za mě určitě zlepšení, výsledků je víc a připadají mi přesnější. |
| Silná žena + adventure | Spíše horší. |
| Westerny | Podobné. |

Když bych to srovnal se špičkou z minulého dílu, tedy hybrid search, query rewriting a reranking, tak myslím, že pokročilejší metoda byla lepší. Ale nemůžu plně srovnávat, limitovali jsme minule počet filmů na 10.
:::

::: tab title="Depth-first"
Zkusme to teď jinak. Uděláme jednoduchý sémantický search výhradně na filmy, podobně jako v minulém díle. Jasně - nemáme tu full-text část, jen sémantickou. Do LLM pošleme rovnou 30 nejlepších filmů.

| Otázka | Pozorování |
| --- | --- |
| Abby | Problém. To už jsme viděli minule, tam nás zachránil full-text. |
| Star Wars | Super, víc filmů pomohlo, přesně, jak jsme minule spekulovali. |
| Mark | Zdá se, že dost špatně, agregační dotaz a chybí globálnější kontext. |
| Praha | Celkem ok, pořád ten stejný jeden film. |
| Drogy | Výčet filmů je celkem ok, ale odpovědi chybí globálnější kontext. Nepopisuje, v čem jsou ty filmy vážné nebo vtipné, umí dát jen výčet. |
| Silná žena + adventure | Zdá se mi dobré. |
| Westerny | Dobré. |
:::

::: tab title="Depth-first + traversal"
Tady je to v kódu trochu komplikovanější, ale postup jsem zkusil tenhle:

::: steps
1. **Najdu filmy**: sémantické vyhledávání nad filmy, tentokrát top 20.
2. **Jdu nahoru do grafu**: od vybraných filmů směrem ke konceptům, po cestě limituji počty, ať mi to nevybouchne.
3. **Vyberu opakující se koncepty**: seřadím je podle četnosti, oříznu seznam a později jejich sumarizace použiji do LLM.
4. **Jdu zase dolů k filmům**: od častých konceptů najdu napojené filmy a vyberu zajímavé přes reranking.
5. **Složím kontext**: do LLM pošlu 20 filmů z prvního kroku, 30 konceptů z druhého kroku a 20 filmů z třetího kroku.
:::

| Otázka | Pozorování |
| --- | --- |
| Abby | Setrvalý stav. |
| Star Wars | Méně filmů, ale zdá se mi přesnější. Stále se nám to nedaří plně cracknout. |
| Mark | Asi lepší, globální kontext pomohl. Nicméně tady bych potřeboval asi jít a ručně to rozsoudit. |
| Praha | Zajímavá změna filmu. Pokud vím Iluzionista se odehrává ve Vídni, ale film se točil hlavně v Praze. Tady se nám do extrakce evidentně vloudila implicitní znalost LLM, které ji dělalo. |
| Drogy | Tradičně dobré, trochu více kontextu okolo. |
| Silná žena + adventure | Kupodivu spíše zhoršení, dané asi menším množstvím filmů v kroku 1. |
| Westerny | Také spíše zhoršení. |
:::

:::
:::

::: card number="11" title="Co z experimentu vychází" 
Cílem dnes bylo vyzkoušet si koncepty a jako demonstrace to myslím dobře poslouží. Reálné úlohy budou větší a složitější a věřím, že síla těchto postupů se v nich projeví ještě výrazněji.

Pro mě je fascinující hlavně to, jak breath-first i bez jednotlivých filmů dává zajímavé výsledky a jsou kvalitativně jiné: víc porozumění tématům, ale menší znalost detailů - což je logické.

::: summary-grid
- **Breath-first**: dobrý pro otázky nad tématy, žánry, náladou a agregacemi.
- **Depth-first**: dobrý pro konkrétní filmové tipy a detailní odpovědi.
- **Traversal**: umí přidat souvislosti, ale někdy zhorší přesnost.
- **Největší problém**: postup máme dopředu daný a spoléháme, že sémantika a reranking všechno vyřeší.
:::

Přitom víme, že právě u Star Wars tohle tragicky nefunguje - ani embedding ani reranking není dostatečně silný pro pochopení, že hledáme "jako Star Wars" a ne Star Wars.
:::

:::

::: group id="co-dal" title="Kam bych to posunul dál"

::: card number="12" title="Ručně zvolený plán pro otázku jako Star Wars" 
Jak by to vypadalo, kdybychom využili zmíněné techniky, ale na příkladu Star Wars volili postup ručně?

::: steps
1. **Nezačínal bych filmy**: z otázky bych usoudil, že přímo hledat filmy není optimální a začal bych koncepty - zejména Theme, Setting a Genre. Character nebo Series moc ne, to mi nenajde filmy Star Wars podobné, ale spíše stejné.
2. **Rozpadl bych dotaz na větve**: pro každý z těchto konceptů bych možná otázku přeformuloval, aby sémantický search byl přesnější. Query rewriting by vytvořil plán tří větví.
3. **Nechal bych LLM vybrat koncepty**: z vrácených názvů nejbližších konceptů bych se obrátil na LLM s tím, které z nich se nejlépe hodí k otázce. Tady to bude o pokročilém LLM, které pochopí, že nechceme koncepty "Star Wars", "Imperial Era" nebo "Dark Side", ale spíše "Sci-Fi", "Space", "Planets", "Galaxy" a tak podobně.
4. **Procházel bych graf k filmům**: na vybraných konceptech bych začal procházet graf směrem k filmům. Po nějaké době bych se zastavil a zeptal se LLM na názor. Máme teď lepší podklady pro odpověď a můžeme hledání ukončit nebo nám pořád něco chybí?
5. **Dovolil bych změnu strategie**: pokud něco chybí, LLMku už na začátku představíme naše možnosti - co jak se dá vyhledávat (full-text, depth, breath, ...). Očekávám, že možná změní strategii a třeba vytvoří klíčová slova pro full-text a řekne si o něj nebo vygeneruje něco jako doplňující otázku pro sémantiku.
6. **Iteroval bych do limitu**: takhle to půjde tak dlouho, dokud něco nevyprší nebo dokud nebude mít LLM pocit, že už je podkladů dost a lze vytvořit odpověď.
:::
:::

::: card number="13" title="Směr: agent plánuje vlastní průchod" 
Nějak takhle funguje **deep research** a už jsou k tomu i různé open source frameworky nebo designové návrhy, třeba DRIFT. Nicméně stejně jako minule a dnes, pokusím se jen základní myšlenky vzít a poskládat něco od nuly.

::: callout label="Za mě"
Není to o tom, že graf automaticky vyřeší RAG. Graf přidá další typ kontextu a další možnosti pohybu, ale někdo musí rozumně rozhodovat, kdy jít do detailu, kdy do nadhledu a kdy změnit plán.
:::

Tak zas někdy příště.
:::

:::


::: closing
Někdy nestačí lepší similarity search; agent musí umět rozhodnout, kudy se za odpovědí vydat.
:::
