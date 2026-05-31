---
format_version: 1
title: "Vlastní data (RAG) pro vašeho AI agenta část první - krok za krokem s Python a PostgreSQL"
subtitle: "Od nepřesné paměti přes full-text a embeddingy až k hybridnímu hledání s re-rankingem."
slug: "rag-part1"
date: "2025-03-05"
language: "cs-CZ"
status: "experimental"
canonical_url: "/2025/rag-part1/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Vlastní data (RAG) pro vašeho AI agenta část první

::: group id="uvod" title="Proč RAG vůbec řešit"

::: card number="01" title="Problém: z hlavy to jde, ale ne vždy správně" default="open"
Když se vás zeptám na nějaké faktické informace, třeba na něco z firemních směrnic, dám vám otázku z testu na Azure nebo jaký film doporučíte někomu, kdo viděl Matrix a chtěl by něco podobného, tak se můžete pokusit to udělat z hlavy.

Budete mít možná problém si vzpomenout úplně přesně, možná uděláte i nějakou chybu, něco trochu popletete a když budu chtít, abyste citovali potřebné zdroje (na které stránce jakého dokumentu se o tom píše), tak často nebudete vědět, kde jste ke své znalosti přišli.

::: callout type="note" title="Stejně se chová LLM"
Velký jazykový model umí krásně formulovat odpověď, ale jeho vnitřní znalost není databáze s citacemi. Když potřebujete přesnost a dohledatelnost, musí dostat dobré podklady.
:::
:::

::: card number="02" title="Lepší varianta: nejdřív si dohledat podklady" default="closed"
Srovnejte to s tím, když vám řeknu, že si klidně můžete před odpovědí pohledat po Internetu, prolistovat poznámky, prolétnout vytištěné směrnice nebo si zaklikat v Azure dokumentaci. Předpokládám, že tím se jednak výrazně zlepší přesnost vašich odpovědí a také mi řeknete, kde se o tom píše, ocitujete zdroje.

Jenže co když místo dobrého zacílení na určitou část dokumentace nebo směrnici vám nabídnu stránky z celé knihovny, ale bez přebalů a jakéhokoli řazení nebo indexování titulů? Pomůže to? Asi ano, ale bude vám to trvat mnohem déle, spotřebujete daleko víc energie a může se stát, že pokud naprostá většina stránek není pro odpověď důležitá, tak ztratíte pozornost a správné odpovědi si tam někde uprostřed nevšimnete.
:::

::: card number="03" title="Co je RAG v jedné větě" default="closed"
To, co jsem právě popsal, funguje ve velkých jazykových modelech (LLM) taky a říká se tomu **Retrieval Augmented Generation (RAG)**.

Ideální je, když se model dostane k co nejlépe zacíleným dokumentům, ve kterých se skrývá odpověď, a on tak může dávat naprosto přesné, rychlé a levné výstupy. Když se netrefíme a dáme mu dokumenty, které moc relevantní nejsou, odpovědi se zhorší. Když budeme mít model s velkým kontextem a nahrneme mu celou knihovnu, bude to drahé, pomalé a výsledky stejně nebudou tak dobré, jako v případě dobře zvolených referenčních dokumentů.

::: reveal title="Co v tomhle díle záměrně neřeším"
Dnes se chci zaměřit na problematiku hledání těch správných podkladů pro vaše LLM. Nebudeme tentokrát řešit přípravu dokumentů a jejich krájení ani složitější znalostní báze postavené na grafu provázaností a sumarizací. O tom jindy.
:::
:::

::: card number="04" title="Dnešní cesta: od jednoduchého hledání k re-rankingu" default="closed"
Pracovat budeme s PostgreSQL, protože se tam můžu naučit, co se všechno děje. Pro svoje projekty ale určitě zvažte i **Azure AI Search**, který tohle všechno rovnou jednoduše umí a kromě toho řeší i problematiku krájení a nabírání.

::: sequence title="RAG progres v tomto článku"
1. **Full-text** — klasické hledání slov a jejich kořenů.
2. **Query rewriting** — úprava dotazu tak, aby se lépe hledal.
3. **Embeddingy** — významové hledání v latentním prostoru.
4. **Hybrid search** — spojení full-textu a vektorů.
5. **Re-ranking** — menší model přerovná předvybrané výsledky podle relevance.
:::

Všechny techniky si ukážeme na jednoduchém příkladu s filmy a jejich popisky. Příště se pak pustíme do složitějších technik vyžadujících hlubší zpracování dat, hierarchické a grafové přístupy a sumarizace.
:::

:::

::: group id="priprava" title="Příprava dat v PostgreSQL"

::: card number="05" title="Notebook a databázový základ" default="closed"
**Otevřete si prosím [Jupyter Notebook na mém GitHubu](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_level1_guide.ipynb)**. Najdete tam konkrétní výsledky a výstupy, doporučuji si ho vzít při čtení k ruce.

Celý příběh začíná tím, že vezmeme dokumenty, kterými budou popisky filmů, a vložíme je do PostgreSQL s tím, že vytvoříme kombinovaný sloupeček s názvem a popisem (ať se mi dobře dělají vektory). Potřebnou infrastrukturu jako jsou Azure OpenAI modely a Azure PostgreSQL Flexible Server a vše si můžete nahodit z mého Terraformu v příslušném adresáři.

::: summary-grid
- **Data**: názvy a popisky filmů.
- **Databáze**: PostgreSQL, abych viděl, co se děje pod kapotou.
- **Modely**: Azure OpenAI pro embeddingy.
- **Cíl**: pochopit vyhledávací vrstvy, ne postavit hotový enterprise produkt.
:::
:::

::: card number="06" title="Rozšíření, která použijeme" default="closed"
Než udělám samotný import, je potřeba přidat některá rozšíření:

| Rozšíření | K čemu ho používám |
| --- | --- |
| **azure_ai** | Přímo z PSQL provolávám Azure OpenAI pro embeddingy a případně další Azure AI služby. |
| **pgvector** | Ukládání embeddingů přímo do PostgreSQL a vektorové vyhledávání. |
| **pg_diskann** | Rychlejší a efektivnější vyhledávání v embeddingových vektorech. |

Založím tabulku, přidám sloupeček `embedding` s 2000 dimenzemi, přidám další sloupeček `full_text_search` pro `tsvector` (statistika pro full text, víceméně kořeny použitých slov a jejich výskyty) a přidám DiskANN index. Pak vložím data a následně k nim přidám embeddings s využitím SQL příkazu `UPDATE` společně s funkcí z `azure_ai`, takže databáze si do Azure OpenAI služby bude volat sama a zařídí si to.
:::

:::

::: group id="techniky" title="Jednotlivé techniky hledání"

::: card number="07" title="Full-text: dobrý sluha pro konkrétní slova" default="closed"
Nejprve nasaďme full-text. PostgreSQL prošel jednotlivé popisky, identifikoval kořeny slov, spočítal si je a statistiky si u každého filmu uložil. Vzneseme dotaz, proženeme full-textem a necháme si prvních 10 nejbližších odpovědí. Jednotlivé otázky a odpovědi najdete v odkazovaném Jupyter notebooku a následně je předhodíme LLM pro formulaci odpovědi.

První pokus nic moc. Otázka na Abby vede jen na jeden film (což je málo) a ostatní také nejsou moc dobré. Potíž je, že full-text search není ChatGPT, takže otázka `What movies are about Abby?` je značně nevhodná, protože tím hledáme všechna tato slova, z nichž kromě Abby vlastně žádné není důležité a nepotřebujeme ho v textu vůbec mít.

::: reveal title="Vylepšení: question rewriting"
Pojďme provést tzv. question rewriting, tedy necháme menší jazykový model (já použiji `gpt-4o-mini`) dotaz přeformulovat a optimalizovat pro full text. V notebooku vidíte tento scénář ve výstupech včetně přeformulovaného dotazu a na Abby máme tentokrát výsledky mnohem lepší (4 filmy).

Nicméně druhé dva dotazy jsou stále špatné - hledáme filmy jako Star Wars, ale ne Star Wars, což full-text samozřejmě nemá jak pochopit, takže nám právě najde všechny Star Wars a to nechceme. Asi to bude chtít hledat spíše význam.
:::
:::

::: card number="08" title="Embeddingy: význam místo přesných slov" default="closed"
Ve strojovém učení je časté, že chceme svět s jeho velkou variabilitou a složitostí zjednodušit na menší počet vlastností, defacto ho zkomprimovat do menšího a to ztrátovým způsobem. Nejde tedy o zip, ale spíš si představte něco jako MP3.

Představme si třeba, že pro text připravíme score v několika dimenzích, například „míra veršovanosti“, „míra humoru“ a tak podobně. Pokud takových vlastností použijeme stovky, budou mít dobrou vypovídací schopnost. Ve strojovém učení ale nebudeme AI diktovat, co to má být za dimenze a vlastnosti, to necháme na něm.

Tyto vektory (vyjmenovaná čísla, score za jednotlivé vlastnosti, dimenze), embeddingy, se pak používají pro reprezentaci původního vstupu a významovou extrakci u textů, obrázků i třeba difúzních modelů.

::: callout type="note" title="Latentní prostor prakticky"
Každý text je zasazen do bodu v n-rozměrném latentním prostoru. Z různých textů umístěných v prostoru pak můžeme usuzovat na míru jejich příbuznosti a významové podobnosti. My použijeme kosinovou podobnost, protože najde podobnost i při rozdílné škále.
:::

Jak v tom hledat? Nejprve ke všem popiskům filmů nechám model vytvořit embedding, ten si uložíme a až pak dostaneme dotaz, tak i ten zasadíme do latentního prostoru a koukneme, které body jsou dotazu nejpodobnější.
:::

::: card number="09" title="Sémantické vyhledávání a jeho slabiny" default="closed"
Třetí varianta v notebooku je sémantický search, tedy vektorové hledání podobností z embeddingů. Na první otázce, tedy filmy kde je postava Abby, nám to selhává. Tímto příkladem jsem chtěl demonstrovat, že vektory jsou povětšinou skvělé, ale v okamžiku, kdy vlastně potřebujeme hledat konkrétní krátkou faktickou informaci typu číslo faktury, tak to moc nedávají.

Na druhé dvě otázky jsou teď určitě lepší, byť Star Wars jsou stále problém. Přestože tentokrát už máme ve výsledcích i podobné sci-fi filmy, přímo těch Star Wars, co nepotřebujeme, je tam pořád dost. Je to něco, s čím v jednoduchých scénářích nic moc neuděláme - na embedding je to moc komplikovaná konstrukce.

::: tabs id="semantic-query"
::: tab id="rewrite" title="Přeformulovat dotaz"
Stejně jako u full-textu může dávat smysl dotaz přeformulovat. Použil jsem opět menší LLM (`gpt-4o-mini`) s cílem otázku učinit jasnou, dobře formulovanou a bez překlepů a gramatických chyb. U vstupu od skutečného uživatele tohle pomůže k lepšímu vyhledávání.
:::
::: tab id="hyde" title="HyDE"
Známá technika HyDE (Hypothetical Document Embedding) nechá LLM na základě otázky vysnít si fiktivní dokument, který by byl ideálním podkladem pro odpověď. Podle něj pak provedete vektorové hledání. Někdy to výborně funguje, protože dokumenty samozřejmě nejsou formulované jako otázky.
:::
:::
:::

::: card number="10" title="Hybrid search: vezmeme to nejlepší z obou světů" default="closed"
Je zřejmé, že na některé otázky je vhodné sémantické hledání, ale jinde je úspěšnější klasický full-text. Pojďme tedy používat oboje a nasadit hybridní hledání.

SQL dotaz trochu naboptnal, ale nic hrozivého. Nejprve provedu full-text search a vrátím si 15 výsledků, následně uděláme sémantický search a dostanu také 15 výsledků. Do obou tabulek jsem si přidal pořadové číslo (index), prioritu, aby se mi to pak dobře slévalo, a taky sloupeček s použitou metodou. Následně udělám union obou tabulek a proženu to dalším dotazem, kde provedu deduplikaci podle ID filmu. V závěru takto odfiltrované výsledky seřadím podle priority a oříznu po 10 řádcích.

```sql label="Hybridní hledání v PostgreSQL"
WITH fulltext AS (
    SELECT 
        id, 
        title, 
        overview, 
        combined_text, 
        ts_rank(full_text_search, plainto_tsquery('english', %s)) AS score,
        'fulltext' AS method,
        ROW_NUMBER() OVER (ORDER BY ts_rank(full_text_search, plainto_tsquery('english', %s)) DESC) AS index
    FROM movies
    ORDER BY score DESC
    LIMIT 15
),
semantic AS (
    SELECT 
        id, 
        title, 
        overview, 
        combined_text, 
        (embedding <=> azure_openai.create_embeddings('text-embedding-3-large', %s, 2000, max_attempts => 5, retry_delay_ms => 500)::vector) AS score,
        'semantic' AS method,
        ROW_NUMBER() OVER (ORDER BY (embedding <=> azure_openai.create_embeddings('text-embedding-3-large', %s, 2000, max_attempts => 5, retry_delay_ms => 500)::vector)) AS index
    FROM movies
    ORDER BY score 
    LIMIT 15
),
combined_results AS (
    SELECT * FROM fulltext
    UNION ALL
    SELECT * FROM semantic
),
deduped_results AS (
    SELECT DISTINCT ON (id) 
        id, 
        title, 
        overview, 
        combined_text, 
        score, 
        method, 
        index
    FROM combined_results
)
SELECT * FROM deduped_results
ORDER BY index
LIMIT 10;
```

Výsledky na Abby jsou někde mezi full-textem a sémantikou, což logicky celkem odpovídá. To znamená, že jsem odstranil extrémní situace, které jsou špatné - Abby přes sémantiku a Star Wars přes full-text.

[![Screenshot 2025-02-25-09-15-24](/images/2025/2025-02-25-09-15-24.png)](/images/2025/2025-02-25-09-15-24.png)
:::

::: card number="11" title="Re-ranking: druhé kolo relevance" default="closed"
Pojďme do toho teď zamontovat další magii - re-ranking. Jde v zásadě o typicky malý jazykový model, který je specificky trénován na schopnost zhodnotit relevanci dokumentu k dané otázce.

Je příliš velký na to, abych podle něj dělal hledání o složitosti O(n), ale na druhou stranu dostatečně rychlý na to, abych pár desítek či set předvybraných výsledků podrobil zkoumání. Protože zatím není k dispozici jako extension pro PostgreSQL v Azure Flexible Server, tak to dělám na serverové straně v Pythonu a používám jednoduchý model [MultiBERT](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-12-v2), který má asi jen 33M parametrů a v pohodě poběží i v CPU.

SQL dotaz je stejný, jen si vezmu všech 30 výsledků, MultiBERTem je seřadím dle relevance a zase vezmu top 10 a pošlu do LLM. Výsledky jsou nejlepší.

::: reveal title="Výsledky v notebooku"
Abby je správně.

[![Screenshot 2025-02-25-09-21-01](/images/2025/2025-02-25-09-21-01.png)](/images/2025/2025-02-25-09-21-01.png)

Filmy podobné Star Wars jsou těžká disciplína, takže výsledek pořád není ideální, ale oproti ostatním řešením je nejlepší.

[![Screenshot 2025-02-25-09-22-07](/images/2025/2025-02-25-09-22-07.png)](/images/2025/2025-02-25-09-22-07.png)
:::
:::

:::

::: group id="zaver" title="Kam odtud dál"

::: card number="12" title="Co jsme vyřešili a co ještě ne" default="closed"
RAG metody, které jsme si společně vyzkoušeli, nejsou žádná raketová věda, ale je vidět, že použité techniky vedou k značnému zlepšení výsledků. Nicméně zůstává pár problémů.

::: summary-grid
- **Agregační dotazy**: nejsou dobře pokryté, protože nemáme sumarizované údaje.
- **Graf informací**: konkrétní postavy, herci, režiséři, žánry a vztahy jsou mimo dnešní jednoduchý model.
- **Předžvýkaná data**: příště bude potřeba extrahovat atributy, propojit je a přidat sumarizace.
- **GraphRAG**: přesně tímhle směrem se dá jít dál.
:::

Na to se zaměříme někdy příště - zkusíme data vzít, extrahovat z nich klíčové atributy a ty mezi sebou vztahově propojit a ještě přidat sumarizační a agregované pohledy.
:::

::: card number="13" title="PostgreSQL na učení, Azure AI Search pro praxi" default="closed"
Ještě nutno říct, že jsem použil PostgreSQL, protože mě fascinuje jeho univerzálnost a rozšiřitelnost a je to nejlepší způsob, jak se věci naučit a zjistit, co se tam děje.

Nicméně objevuji tak trochu kolo a pokud jste v cloudu, zkuste rovnou použít **Azure AI Search**, který nejen co jsme dělali, ale i další techniky má rovnou v sobě. Navíc je to nejen řešení pro ukládání a hledání, ale i pro zpracování vstupů, ať už jde o indexaci, extrakci, řezání a další součásti RAG, které rozebereme také někdy příště.

:::
:::


::: closing
LLM není databáze. Kvalitní data a chytrý přístup k nim nejsou pro lidstvo nový problém - hodí se lidem a budou se hodit i vašim AI agentům.
:::
