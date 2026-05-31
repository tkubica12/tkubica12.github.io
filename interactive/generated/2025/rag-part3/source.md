---
format_version: 1
title: "Vlastní data (RAG) pro vašeho AI agenta část třetí - AI samo volí strategii, jak se dostat k datům"
eyebrow: "RAG část 3"
subtitle: "Od hrubé síly k agentovi, který přeformuluje dotaz, navrhne SQL strategii přes fulltext, vektory a graf, opraví chyby, vybere nejlepší cestu a až potom skládá finální odpověď."
slug: "rag-part3"
date: "2025-03-18"
language: "cs-CZ"
status: "experimental"
canonical_url: "/2025/rag-part3/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Vlastní data (RAG) pro vašeho AI agenta část třetí - AI samo volí strategii, jak se dostat k datům

V první díle jsem dával dohromady základní techniky pro práci se znalostní bází v AI agentech a řešili jsme sémantické, fulltextové a hybridní vyhledávání. Abychom lépe adresovali komplexnější problémy a agregační dotazy, použili jsme v druhém díle AI pro extrakci kritických konceptů z dat, vytvořili jejich sumarizace a vše propojili do znalostního grafu. Následně jsme použili několik technik vstupu do grafu a pohybu po grafu, ale šlo o předem dané postupy, které jsem otiskl do kódu. Dnes to bude jinak - **plánovat strategii bude přímo AI, bude ji exekuovat, samo vytvářet potřebná query a opravovat se**, když se mu to nepovede. U problematiky filmů zůstáváme i dnes.

::: callout type="verdict" title="Co dnes stavíme"
AI nebude jen odpovídat nad předem vybranými výsledky. Necháme ji nejdřív rozmyslet cestu k datům: přeformulovat dotaz, navrhnout několik SQL strategií, spustit je, opravit chyby, vybrat nejlepší stopu a tu rozšířit.
:::

::: group id="plan" title="Od dotazu ke strategii"

::: card number="01" title="Celý postup v šesti krocích" default="open"
V tomto článku zkusím implementovat následující postup:

::: steps title="Agentický RAG workflow"
1. **Uživatel vznese dotaz** — začínáme normální otázkou, žádnou ruční volbou strategie.
2. **AI vytvoří reformulace** — zeptá se jinak, abychom měli variabilitu v textu.
3. **AI vytvoří query plány** — včetně SQL dotazů kombinujících fulltext, sémantické vyhledávání a pohyb po grafu.
4. **Kód dotazy provede** — pokud některý spadne na syntaxi, chybovou zprávu pošleme zpět AI k opravě.
5. **AI vyhodnotí relevance** — vybere nejslibnější strategii a vyškáluje ji tak, aby vrátila víc výsledků.
6. **AI složí finální odpověď** — až teď dostane posbírané podklady a formuluje odpověď uživateli.
:::
:::

::: card number="02" title="Přechod na Azure SQL a příprava dat" default="open"
Po uveřejnění druhého dílu seriálu mi kolega ukázal, jak lze různé formy vyhledávání dělat v Microsoft SQL, konkrétně v **Azure SQL Serverless**. Vyšlo najevo, že funkce tradičního hledání, fulltext hledání, vektorového hledání i pohyb po grafu je těsně integrovaná do jazyka. To z něj dělá velmi univerzální řešení, což se mi pro dnešní díl náramně hodí, protože SQL dotazy bude dnes generovat AI a chci mu to co nejvíc zjednodušit.

Pro dnešní díl jsem tedy přešel na Azure SQL a definoval Node a Edge tabulky, fulltext index přes `CONTAINS`, vektorový sloupeček přes `vector_distance` a pohyb po grafu přes `MATCH` v query.

- Konkrétní postup najdete [v mém notebooku](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level3_preparation.ipynb).
- Referenční query pro srovnání jsou v [tomto notebooku](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level3_query_reference.ipynb).
:::

::: card number="03" title="Referenční query: dobré, ale pořád hrubá síla"
V dnešním díle budeme do modelu posílat výrazně víc filmů, takže je fér udělat srovnání s jednoduchým RAG přístupem: sémantické hledání a do LLM poslat 200 nejbližších filmů. Výsledky jsou za mě velmi dobré. Nicméně je cítit, že přestože samotný seznam filmů je relevantní a poměrně úplný, odpověď nemá kontext a nadhled. Nemluví o ságách, archetypech hlavních postav, nevysvětluje tak dobře, jak konkrétně tento film zapadá do otázky uživatele.

Nutno také vzít v úvahu, že datová sada je velmi malá, asi 8500 filmů, takže do LLM aktuálně posílám nějaké 2 % veškerých dat. Pokud by znalostní báze byla o několik řádů větší, tak tento přístup hrubou silou bude fungovat dramaticky hůř.

::: callout type="note" title="Důležitý kontext"
U malé datové sady bude chytřejší vyhledávání často vracet podobné konkrétní filmy jako hrubá síla. U velké datové sady ale bude mít inteligentnější strategie mnohem větší efekt.
:::
:::

:::

::: group id="reformulace" title="Reformulace dotazu"

::: card number="04" title="Necháme AI zeptat se víckrát jinak" default="open"
V [notebooku](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level3_query_sql.ipynb) začínám tím, že uživatelský dotaz nechám přeformulovat na víc variant nebo podotázek. Jde o to, že někdy uživatel má v otázce překlepy nebo se vyjádří nejasně a vyhledávání tím pak může trpět. Navíc jiná formulace otázky může zásadním způsobem vylepšit šance na správné vyhledávání.

Výborně je to vidět u **Star Wars** otázky, která je myslím přesně ta, kde jsme v předchozích dílech nejvíce trpěli a inteligentní RAG se tu osvědčuje.

::: reveal title="Výstup reformulace pro Star Wars otázku"
```text
Question: I have seen all Star Wars movies and would like tips for something similar I can watch next.
Generating sub-questions.
  -> Sub-question: What are some science fiction movies similar to Star Wars?
  -> Sub-question: Can you suggest movies or shows with epic space battles and adventures?
  -> Sub-question: What are some recommendations for movies with themes of rebellion against tyranny?
  -> Sub-question: Are there any film series with iconic characters and expansive universes like Star Wars?
  -> Sub-question: What are other popular franchises that mix science fiction and fantasy elements?
```
:::

Všimněte si, že hned několik variant konečně neobsahuje slovo Star Wars, které nám dělalo takové potíže v hledání, protože nám vracelo hlavně ty Star Wars.

::: reveal title="Prompt pro reformulaci"
```markdown
Your task is to rephrase the user's question to improve retrieval accuracy in a Retrieval Augmented Generation system, following a ReSP pattern (retrieve, summarize, plan).

Keep the following in mind:
- Preserve all essential details from the original question.
- Do not introduce new information or context.
- Improve phrasing to be concise and clear.
```
:::
:::

:::

::: group id="query-planning" title="Příprava query plánu"

::: card number="05" title="LLM vybírá, jestli použít vektory, fulltext nebo graf" default="open"
To hlavní kouzlo se odehrává v přípravě query strategie přímo v LLM. Celý [prompt najdete tady](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/prompts/query_strategy_sql.jinja2), ale podstatné je, že po modelu chceme, aby vymyslel jak nejlépe formulovat SQL dotazy tak, aby získal data relevantní pro uživatelský dotaz.

::: reveal title="Zkrácená ukázka instrukcí pro query strategii"
```markdown
Your task is to create a query strategy for a Retrieval Augmented Generation system. The strategy should:

# Instructions
- Analyze the user query and decide whether to use semantic search, full_text search or graph search.
- Identify one or more traits (e.g., Movie, Genre, Character, Setting, Theme, Series) to target.
- Rewrite the user query:
    - For keyword search, extract ONLY the essential identifying terms (names, entities, specific descriptors) from the user's question.
    - For semantic search, rewrite the user query to semantically match articles that might be in the knowledge base.
- Provide one, preferably two or more strategies. Make sure each strategy is distinct.
- All SQL searches must return no more than 20 results.
- For graph search, use the MATCH clause to find related nodes and edges.
- For keyword search, use CONTAINS clause to find related nodes and edges.
- Use TOP 20 in the final result to limit the number of results returned.
```
:::
:::

::: card number="06" title="Datový model musí být pro model explicitní"
Aby model negeneroval SQL naslepo, dostane jednoduchý, ale přesný kontrakt datového modelu. Má node tabulky `Movie`, `Character`, `Setting`, `Theme`, `Series` a `Genre`, všude stejné sloupce `Id`, `Name`, `Content` a `Embedding`. Edge tabulky jsou `IN_GENRE`, `SET_IN`, `INCLUDES_THEME`, `FEATURES_CHARACTER` a `PART_OF_SERIES`.

::: detail-grid title="Jaké strategie tím model může skládat"
::: detail-card title="Sémantika"
Vektorové hledání přes `vector_distance`, typicky nad `Movie`, `Character`, `Theme` nebo `Series`.
:::
::: detail-card title="Fulltext"
Přes `CONTAINS`, ideálně s extrahovanými klíčovými slovy místo dlouhé přirozené věty.
:::
::: detail-card title="Graf"
Přes `MATCH`, když je potřeba jít od tématu, postavy, žánru nebo série k souvisejícím filmům.
:::
::: detail-card title="Kombinace"
Například fulltext zúží kandidáty a vektorové skóre je seřadí, nebo sémantika najde témata a graf dohledá filmy.
:::
:::

::: reveal title="Příklad SQL dotazů z promptu"
```sql
-- Similarity search on Movie
SELECT TOP 10 Id, Content, vector_distance('cosine', Embedding, @q) AS Similarity
FROM [dbo].[Movie]
WHERE Embedding IS NOT NULL AND Content IS NOT NULL
ORDER BY Similarity ASC

-- Fulltext search on Movie together with semantic search on results
SELECT TOP 10 Id, Content, vector_distance('cosine', Embedding, @q) AS Similarity
FROM [dbo].[Movie]
WHERE CONTAINS (Content, '"Indiana Jones" AND "Temple"')
ORDER BY Similarity ASC

-- Semantic search on Character, graph search to find related Movie
WITH topcharacters AS (
    SELECT TOP 50 Id, vector_distance('cosine', Embedding, @q) AS Similarity
    FROM [dbo].[Character]
    WHERE Embedding IS NOT NULL AND Content IS NOT NULL
    ORDER BY Similarity ASC
),
MovieMatches AS (
    SELECT TOP 10 m.Content as Content, COUNT(c.Id) AS MatchedCharacterCount
    FROM [dbo].[Movie] m, [dbo].[FEATURES_CHARACTER] fc, [dbo].[Character] c
    WHERE MATCH (m-(fc)->c)
    AND c.Id IN (SELECT Id FROM topcharacters)
    GROUP BY m.Content
)
SELECT TOP 10 Content
FROM MovieMatches
ORDER BY MatchedCharacterCount DESC;
```
:::
:::

::: card number="07" title="Structured Outputs: aby se strategie dala spustit"
Abych to mohl dobře zpracovávat, využívám Structured Outputs, tedy předepisuji modelu strukturu odpovědi včetně popisu políček. To lze dělat Pydantic způsobem a výstupní struktura drží zprávu pro uživatele, embedding query a SQL příkaz.

::: reveal title="Pydantic struktura pro query strategie"
```python
class QueryStrategy(BaseModel):
    id: str = Field(
        description="Unique random identifier for this strategy"
    )
    message_to_user: str = Field(
        description="Message to be displayed to the user, explaining the purpose of this query. Include type of each query step and its relation to other steps. Wording should be about what you are doing, example: 'Searching Movie using keyword search for Star Wars followed by graph query to get related genres and semantic movie search among results."
    )
    query: str = Field(
        description="Rewrite query to better match knowledge base using semantic search. This field is used to create embedding and store as @q variable for command to use."
    )
    command: str = Field(
        description="Command to be executed in the database. This should be a SQL query that can be executed directly against the database. All text-based queries should be hardcoded, just vector will be referenced as %q."
    )

class QueryStrategies(BaseModel):
    strategies: List[QueryStrategy] = Field(
        description="List of strategies, each containing a series of steps to be executed sequentially. Each strategy is a sequence of steps, where each step depends on the results of previous steps."
    )
```
:::

Funguje to překvapivě dobře a LLM servíruje docela dobré nápady, jak se k datům dostat.
:::

:::

::: group id="execution" title="Exekuce, opravy a škálování"

::: card number="08" title="Když SQL spadne, agent ho zkusí opravit" default="open"
V následujícím kroku pošlu jednotlivé dotazy do SQL databáze, ale občas se stane, že je tam syntaktická chyba. To řeším tak, že ji vezmu a znovu zavolám LLM s žádostí o opravu a dám tomu pět pokusů, jestli se to nepovede. Většinou pokud tam nějakou chybu měl, tak při první opravě už to dá.

Celý [prompt na opravu](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/prompts/fix_query.jinja2) si můžete prohlédnout, je v něm znovu SQL schéma a příklady, ale jeho začátek vypadá takto:

::: reveal title="Prompt pro opravu SQL"
```markdown
Your task is to fix a Microsoft SQL query that is failing with syntax errors.

# Instructions
- Analyze the query and errors
- All SQL searches must return no more than 20 results. Use various techniques to select best ones if query matches more, eg. reorder results using semantic search (vector similarity).
- For graph search, use the MATCH clause to find related nodes and edges. Use WITH clause to create temporary tables for intermediate results.
- Use TOP 20 in the final result to limit the number of results returned.

# Original query
{{query}}

# Error
{{error}}
```
:::
:::

::: card number="09" title="Star Wars běh: deset strategií, několik oprav" default="open"
Zůstaňme u Star Wars otázky. Agent zkusil kombinaci přímého sémantického hledání, fulltextu, pohybu přes témata, série i postavy. Několik strategií spadlo na syntaxi, ale oprava přes LLM je dotáhla.

::: reveal title="Transcript exekuce strategií"
```text
Generating query strategies.
 -> Using semantic search to find science fiction movies similar to Star Wars.
    -> Found 20 records
 -> Performing keyword search for science fiction movies and Star Wars, followed by semantic search within results.
    -> Trying to fix error in query
    -> Fixed query successful on attempt 1.
    -> Found 20 records
 -> Searching for Movies and Series using semantic search to match the theme of epic space battles and adventures.
    -> Found 20 records
 -> Searching for Movies and Series using semantic search to match the theme of epic space battles and adventures.
    -> Found 20 records
 -> Searching for themes related to rebellion against tyranny using semantic search, followed by a graph query to retrieve associated movies.
    -> Trying to fix error in query
    -> Fixed query successful on attempt 4.
    -> Found 20 records
 -> Performing a semantic search directly on movies to find content matching the theme of rebellion against tyranny.
    -> Found 20 records
 -> Performing semantic search for expansive film series with iconic characters and universes.
    -> Found 20 records
 -> Using keyword search for iconic series and characters, followed by graph search to explore related movies.
    -> Found 18 records
 -> Performing semantic search on the Series table to identify franchises blending science fiction and fantasy elements.
    -> Found 20 records
 -> Using a keyword-based search on the Theme table to find themes combining science fiction and fantasy, followed by graph search to identify related franchises.
    -> Trying to fix error in query
    -> Fixed query successful on attempt 1.
    -> Found 20 records
```
:::
:::

::: card number="10" title="Volba nejlepší strategie a její vyškálování" default="open"
Poté co opravíme některé dotazy, držím si seznam exekucí: připravené a opravené strategie a výsledky, které to vrátilo. V dalším kroku požádáme AI o vyhodnocení strategií a identifikaci té, která byla nejlepší a přinesla nejužitečnější výsledky. Tuto strategii pak vyškálujeme, tedy necháme model ji vybrat a SQL dotaz přeformulovat tak, aby vracel víc výstupů, protože jde nadějným směrem.

::: reveal title="Prompt pro výběr nejlepší strategie"
```markdown
# Role
Your task is to review JSON with executions of different query strategies each identified by unique ID, assess results of each strategy and select the one that is most useful for answering the user question. Based on the selected strategy, you will tak winning SQL query and modify it capture larger set of results by increasing TOP value to 60.

# Instructions
- Review the JSON with query strategy executions and their results. JSON will be provided to you in the next user message.
- User question will be provided to you in the last user message as a string.
- Assess quality of results for each strategy. Consider the following:
  - Are the results relevant to the user question?
  - Are there any missing or incomplete results?
  - Is the number of results appropriate?
- Based on your assessment, select the best strategy.
- Modify the winning SQL query to increase the TOP value to 60.
- Provide the modified SQL query as output.
```
:::

Model to skutečně udělal.

::: reveal title="Výsledek škálování nejlepší strategie"
```text
Selecting the best strategy based on the results.
Expanding results of the best strategy.
 -> This query is designed to find film series that are similar to Star Wars in their blending of science fiction, fantasy, and epic storytelling. It aims to identify options for viewers seeking engaging narratives and expansive universes.
    -> Found 60 records
```
:::
:::

:::

::: group id="answer" title="Kompilace závěrečné odpovědi"

::: card number="11" title="Teprve teď skládáme odpověď pro uživatele" default="open"
Teď už je to stejné jako ve všech ostatních příkladech. LLM naservírujeme otázku a všechny posbírané podklady. Tady je výsledek pro Star Wars otázku.

::: reveal title="Ukázka finální odpovědi"
```markdown
If you've watched all the "Star Wars" movies and are seeking something similar, here are recommendations based on themes, world-building, and narrative structures akin to the "Star Wars" saga:

### 1. "Star Trek" Movie Series

- Why Similar: Like "Star Wars," the "Star Trek" series explores interstellar conflicts, diplomacy, and the moral complexities of leadership and humanity's place in the universe. It features compelling ensemble casts, advanced technology, and philosophical undertones.
- Highlights: Iconic characters like Captain Kirk and Spock navigate moral dilemmas and thrilling adventures across the galaxy. Key films include Star Trek II: The Wrath of Khan and the 2009 reboot Star Trek, which reintroduce classic elements with modern storytelling.

### 2. "Battlestar Galactica" Series

- Why Similar: This series delves into the survival of humanity against an AI-driven race, the Cylons, blending space-based action with moral struggles and complex interpersonal dynamics. It mirrors "Star Wars" themes of rebellion and redemption.
- Highlights: The movies Battlestar Galactica: Razor and Battlestar Galactica: The Plan provide deeper insights into character backstories and philosophical questions about existence and war.

### 3. "Guardians of the Galaxy" Series

- Why Similar: With its mix of humor, heartfelt character dynamics, and intergalactic adventures, "Guardians of the Galaxy" mirrors the camaraderie and action-packed escapades of "Star Wars."
- Highlights: The films Guardians of the Galaxy and Guardians of the Galaxy Vol. 2 focus on a ragtag group of misfits who band together to confront cosmic threats, offering both emotional depth and humor.

### 4. "Pacific Rim" Series

- Why Similar: Lush visuals, teamwork, and humanity's battle against towering alien threats resonate with the larger-than-life battles in "Star Wars."
- Highlights: Pilots join forces to control giant robots in Pacific Rim and Pacific Rim: Uprising, blending epic battles with themes of sacrifice and resilience.

### 5. "Dune Saga"

- Why Similar: "Dune" shares the epic scale and political intrigue of "Star Wars," with a focus on power and rebellion in a world driven by mystical elements similar to the Force.
```
:::

Tady je podle mě vidět rozdíl: nejde jen o seznam nejbližších embeddingů. Odpověď už má oporu ve více typech signálů a umí lépe vysvětlit, proč návrhy dávají smysl.
:::

::: card number="12" title="Co si z toho odnést" default="open"
Za mě je tohle hezký příklad posunu od RAG jako jednoho dotazu do vektorové databáze k RAG jako malému agentickému procesu. Důležité není jen, že máme vektory, fulltext a graf. Důležité je, že model dostane dostatečně jasný kontrakt, aby mohl sám rozhodovat, kdy kterou techniku použít.

::: summary-grid
- **Reformulace pomáhá**: už samotné odstranění problematického slova `Star Wars` z části podotázek zlepší šanci na relevantní retrieval.
- **SQL jako společný jazyk**: fulltext, vektory i graf v jednom dotazovacím rozhraní výrazně zjednodušují plánování.
- **Opravy chyb jsou součást workflow**: generované SQL občas spadne, ale chybová zpráva je dobrý vstup pro další LLM krok.
- **Nejlepší strategie se dá škálovat**: místo aby se rozšiřovalo všechno, rozšíříme jen stopu, která se v datech osvědčila.
:::
:::

::: card number="13" title="Praktický checklist" default="open"
Pokud bych to převáděl do produkčnějšího řešení, hlídal bych hlavně tyhle věci:

::: arrow-list title="Checklist pro agentický RAG nad vlastními daty"
- Dejte modelu přesné schéma dat, příklady query a tvrdé limity na počet výsledků.
- Oddělte reformulaci dotazu, návrh strategie, exekuci, opravu a finální odpověď jako samostatné kroky.
- Logujte každou strategii, opravenou query i počet vrácených záznamů.
- Nechte model hodnotit kvalitu výsledků, ale držte si možnost auditovat, proč strategii vybral.
- U velkých datových sad počítejte s tím, že hrubá síla přestane fungovat a plánování retrievalu začne být zásadní.
:::
:::

:::


::: closing
RAG není jen o tom najít nejbližší chunk; u složitějších dotazů je často cennější nechat agenta nejdřív naplánovat, kudy se k datům vůbec dostat.
:::
