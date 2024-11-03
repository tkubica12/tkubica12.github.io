---
layout: post
published: true
title: Jakou vybrat v Azure databázi pro vektory, důležitou součást řešení pro zahrnutí vlastních dat do ChatGPT?
tags:
- AI
- CosmosDB
- PostgreSQL
---
Velké jazykové modely (LLM) nejsou něco, kam nahrajete svoje data - tak to nefunguje. Pokud chcete firemní dokumenty zpřístupnit přes ChatGPT máte především tyto možnosti:
- Máte dostatečně malý kontext, aby se vešel do promptu, takže ho k dotazu přilepíte. Tohle je dobré v situacích, kdy vám jde o kreativní odpovědi, které LLM samo o sobě umí, ale potřebujete ho správně nasměrovat. Například generovat emaily na základě vstupu uživatele, ale na zero-shot nebo few-shot příkladech chcete zajistit, že model bude odpovídat formálně (nebo naopak neformálně), vysvětlíte mu jeho roli, jakou očekáváte délku, co v emailu nesmí chybět apod. Mimochodem právě včera OpenAI oznámilo 16k kontext pro GPT 3.5 turbo za docela příjemné peníze, to je nějakých 20 stran textu.
- Vaše data uložíte v tradičním vyhledávacím řešení, například nějaký jazykově chápající systém (např. Azure Cognitive Search, který bude umět skloňovat apod.), obyčejný fulltext nebo odkaz do Google či Bingu. Na položený dotaz uživatele si necháte LLM vygenerovat vhodný dotaz do tohoto systému. Ten vám vrátí výsledky, ty vezmete, nahrajete do promptu a necháte vygenerovat výslednou odpověď. Jinak řečeno kontext si "nahrajete" až v závislosti na dotazu uživatele z "offline" paměti, kterou je vaše tradiční vyhledávání a databáze.
- Vaše data převedete do vektorového prostoru, kdy LLM vytvoří jakýsi otisk vašeho dokumentu (embeddings). Při položení dotazu uživatelem uděláte otisk dotazu a najdete body ve vektorovém prostoru, které jsou dotazu nejblíže. Jde tedy vlastně o nalezení podobných dokumentů, ale tentokrát s využitím masivní zabudované znalosti LLM. Pak už vezmete podobné dokumenty, přidáte je do promptu jako kontext a postupujete až k vygenerování odpovědi.

Co když narazíte na limity délky? U druhé varianty se vám může vrátit dokument, který je moc dlouhý. Tak ho rozsekáte na vícero dotazů s požadavkem na sumarizaci toho kousku, čímž vzniknou kratší reprezentace, které jste pak schopni vložit do promptu nebo si nechat dál sumarizovat. U třetí varianty máte omezení už při převádění do vektorového prostoru (embeddings), takže budete postupovat buď stejně (tzn. rozsekáte dokumenty na kratší fragmenty) a všem uděláte otisk (a dál to funguje stejně jako v předchozí případě) nebo tohle vyřešíte už dopředu, tedy rozsekáte, necháte si udělat sumarizaci jednotlivých částí a pak z toho zkompilujete výsledný už krátký dokument a pro něj uděláte embedding.

Dnes se chci podívat co je v Azure k dispozici pro tu třetí variantu - kam ukládat vektory a jak v nich hledat podobnost?

# Uložit a hledat
Jak fungují embeddings jsem už na tomhle blogu vysvětloval [tady](https://www.tomaskubica.cz/post/2023/azure-open-ai-doporuceni-a-vyhledavani/), ale tam jsem to jen jednoduše držel v paměti. Pro praxi potřebujeme nějakou databázi, která je perzistentní a spolehlivá. Co chceme k vektoru uložit? Možná to bude celý původní text (ať to můžeme rovnou vložit do promptu), ale někdy to bude odkaz do blob storage, kde najdeme původní dokument případně oboje (pokud byl dokument moc velký a rozsekal jsem ho na kousky, můžu si uložit ten kousek, ale pořád si chci nechat odkaz na celý původní dokument, abych mohl svou odpověď ozdrojovat uživateli). Dost možná se nám k tomu hodí vytáhnout další metadata, která můžeme využít při budování promptu. Co třeba? Pro výběr co zahrnout do odpovědi se nám může hodit datum dokumentu (třeba preferujeme novější), autora (např. oficiální dokumentace bude mít větší váhu než příspěvek na blogu), kategorizace (můžeme například použít k vyloučení nevhodných výsledků), klasifikace (určité informace jsou jen pro zaměstnance nějakého oddělení) apod. Následně potřebujeme hledat na základě podobnosti vektorů - najdi mi záznamy, které mají k danému vektoru (ten vznikl dotazem uživatele) nejblíže.

# Pár variant prakticky
Níže je popis pár variant v Azure, které jsem vyzkoušel a změřil - samozřejmě neprůkazně a amatérsky, ale pro představu mi to zatím stačí. Soustředil jsem se na následující:
- Chci vyzkoušet platformní služby, abych se o to nemusel starat. Jedinou výjimkou bude Redis, protože Azure Cache for Redis Enterprise nemůžu ve své subskripci z interních důvodů použít, tak ho pro testy nahradím podobně sizovaným kontejnerem (ale pro praxi bych to tak neudělal).
- Je celá řada zajímavých open source řešení - ale ty zkusím až někdy jindy, dnes se nechci o databázi nijak starat.
- Existují SaaS databáze specializované na vektor - moje jednoduché scénáře ale za to nestojí, chci použít něco v Azure.
- Zajímá mě řádový čas ingestingu a query pro srovnání variant.
- Chci si udělat cenovou představu o variantách.
- Budu přemýšlet o synergiích co navíc mi konkrétní volba přinese pro celkové řešení.
- Jako vzorek použiji OpenAI CSV s 25000 články z Wikipedie s vektory z text-embedding-ada-002 (1536 dimenzí) jak pro title tak pro text.
- U všech databází do nich uložím i samotný text, title a url - nebudou tedy jen pro vektory, ale pro všechno, ať mám všechno dohromadě a nemusel by se pak dělat lookup někam jinam.
- Všechny query budou hledat 3 nejpodobnější vektory a použiji pro měření 100 těchto dotazů sekvenčně za sebou.

Moje příklady najdete v [tomhle notebooku](https://github.com/tkubica12/ai-demos/blob/main/vector_databases/vector_databases.ipynb)

## Azure Cosmos DB for MongoDB vCore
Na rozdíl od klasické Request Units varianty (čistě cloud native služba) je tahle vCore varianta v preview postavená na tom, že dostanete infrastrukturu přímo pro sebe a měla by být funkčně blíže k MongoDB. Funguje to tak, že si vytvoříte vektorový index a uložíte si JSON dokumenty s příslušným políčkem. Omezení je, že embeddings vektory mohou být do velikost 2000. To stačí pro dnes nejdoporučovanější model text-embedding-ada-002 (1536 dimenzí), ale davinci do toho nenacpete (cirka 12k) - to by ale nemělo tolik vadit, protože ada-002 vykazuje podle měření stejné nebo lepšé výsedky při zlomku ceny. Co do vyhledávání (měření vzdálenosti či chcete-li podobnosti) podporuje euklidovskou vzdálenost (L2 euclidean), kosinusovou podobnost (cosine) nebo skalární součin (inner product).

- **Náklady**: Vezmu plný 2-core za **209 USD** bez HA
- **Ingesting**:  1:43 minuty, Cosmos potvrzuje výbornou rychlost na zápisu
- **Query**: 3:51 minut není žádná sláva

## pgvector v Azure Database for PostgreSQL
Projekt pgvector je open source nadstavba pro PostgreSQL přinášející práci s vektory. Toto rozšíření je podporováno v Azure Database for PostgreSQL, takže ho můžete mít nad plně platformní službou. Stejně jako v předchozím případě je řešení omezeno na 2000 dimenzí, podporuje všechny tři metody (euklidovskou vzdálenost, kosinusovou podobnost i skalární součin). Zajímavé je, že si můžete vybrat mezi přesným a přibližným hledání - to druhé nedává předvídatelné výsledky, ale je výkonnější a může krásně stačit (protože na výsledky se pak často stejně dívá pan profesor GPT-4). 

- **Náklady**: Vezmu plný 2-core za **550 USD** bez HA
- **Ingesting**:  4:17 minuty
- **Query**: 0:16 minut - 16 vteřin je super, zajímavé je, že přesné vs. nepřesné hledání, indexace ani počet probe na to neměly prakticky vliv (asi se projeví až u většího množství dat)

## Azure Data Explorer
ADX je databáze s velmi volným formátem a masivní škálovatelností a přitom zaměřená na ad-hoc analytické dotazy (na rozdíl třeba od CosmosDB, které je svou podstatou především o ukládání a hledání). Samotné uložení vektoru je prostě a jednoduše použití dynamického datového typu a nad tím si můžete napsat funkci pro kosinusovou podobnost. Není to tam tedy "od výroby", ale výsledku lze snadno dosáhnout.

- **Náklady**: Vezmu plný 2-core za **650 USD** v HA
- **Ingesting**:  15 minut (nejdřív 5 minut uploaduje soubor do storage a pak to na pozadí batchově ingestuje, ale trvá to)
- **Query**: 7:04 minut je dost

## Azure Cognitive Search
Tahle varianta je přirozeným rozšířením řešení pro vyhledávání a vektory jsou aktuálně v preview. Azure Cognitive Search dokáže klasické vyhledávací kouzla jako je indexace různými způsoby, klíčová slova, ale kromě toho i orchestraci zpracování a obohacování dat (zavolá si kognitivky pro záskání popisku obrázků, překlady apod.). V preview umí Semantic Search, kdy využívá AI pro přetřídění výsledků a právě i vektorové vyhledávání, což je co nás zajímá.

- **Náklady**: Na moje data by měl stačit S1 za **245 USD** bez HA
- **Ingesting**:  37 minut, takže si opravdu počkáte, ale abych byl fér - nechal jsem ho dělat i ostatní klasické indexy, což ostatní nemuseli
- **Query**: 0 vteřin, v mém scénáři nezměřitelné - asi třikrát jsem si kontroloval, že to opravdu něco vrací a ono ano, neuvěřitelná rychlost

## Redis
Tahle původně in-memory key-value databáze jako cache se rozrostla do nejrůznější oblastí včetně podpory perzistence a search vlastností. V rámci Azure je dostupná pouze u Enterprise tier služby. Zejména pro věci, které se vejdou do paměti (což je můj případ) to nemusí být vůbec špatný nápad.

- **Náklady**: Enterprise verze vyjde draho a má o dost větší paměť, než potřebuji, ale dělá to  **975 USD** s HA
- **Ingesting**:  2:27 minut není špatné
- **Query**: 5 vteřin, je vidět, že takhle pěkně v paměti to dokáže opravdu frčet


# Co si tedy vybrat?
Volil bych podle toho co dalšího v rámci řešení potřebujete.

- Pokud to myslíte hodně vážně se search, použijte Azure Cognitive Search. Můžete dělat hybridní vyhledávání, spojit klasické i AI funkce, využít data k našeptávačům a autocomplete, orchestrovat obohacování dat a tak podobně. Dává mi smysl použít platformu na tohle zaměřenou a obohatit ji o AI, než vymýšlet něco jiného.
- Pokud potřebujete ve své aplikaci embeddingy doplňovat podle toho jak uživatelé vkládají informace, bude to chtít něco co je trochu operačnějšího, tedy něco co má i rychlé ukládání. Tady bych to rozdělil na dva scénáře:
  - Není to nic kritického, potřebujete ke stávajícímu řešení přidat pomocníčka, který obohatí co děláte. Tady může dávat smysl jít do Redisu. Vektory bych si uložil do nějaké tradiční databáze (jejich výpočet stojí peníze, tak proč ho dokola opakovat) a vždycky bych je nahrál do Redisu pro používání. Ono hledání podobnosti vektorů je výpočetně celkem náročná věc a nechcete si sestřelit primární databázi.
  - Chcete to jako integrální součást aplikace, což je z dlouhodobého hlediska myslím lepší varianta. Pak je šance, že půjde o komplexní search a vraťte se zpět k Azure Cognitive Search. Pokud to přecijen dává smysl využít v rámci operační databáze (třeba u katalogu produktů mít uložené i embeddingy), tak pokud je to převážně o čtení/hledání, tak mě příjemně překvapil pgvector na PostgreSQL. 

Sečteno a podtrženo - za mě doporučuji tohle téma uchopit koncepčně a jít do **Azure Cognitive Search**. Každý vendor se díky humbuku kolem OpenAI snaží do své databáze narvat vektory, ale mě prostě přijde, že do operační databáze to není optimální (snad kromě případů, kdy vytváříte embeddingy neustále a interaktivně) a do cache je to nekoncepční.