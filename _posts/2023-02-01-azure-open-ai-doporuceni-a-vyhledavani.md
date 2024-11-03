---
layout: post
published: true
title: "Azure OpenAI Service - doporučení podobného filmu a chytré vyhledávání prakticky"
tags:
- AI
---
Jak vám může Azure OpenAI pomoci s doporučováním podobných produktů nebo chytrým vyhledáváním? V případě krátkého textu by mohlo stačit položit dotaz podobně jako v ChatGPT, ale co když mám databázi popisu 33 000 filmů v češtině? Vyzkoušejme si jak na to s embeddings v Azure OpenAI.

Notebook s dnešní ukázkou najdete na mém [GitHubu](https://github.com/tkubica12/ai-demos/blob/main/openai/notebooks/movies.ipynb) a můžete jej rozjet jak lokálně tak třeba v Azure Machine Learning.

# Embeddings - redukce dimenzí komplexního textu
Když velký jazykový model jako je GPT 3 zpracovává text, dokáže výsledek převést na soubor hodnot (čísel) v abstraktních dimenzích, které sice lze jen velmi obtížně nebo vůbec interpretovat, nicméně dva takto vzniklé výsledky lze srovnávat mezi sebou. Zní to komplikovaně, pojďme si to ukázat na jednoduchém příkladu. Představme si, že místo modelu máte lidi, kteří budou vytrénovaní na schopnost rozeznávání jedné vlastnosti textu. Jeden z nich se bude zaměřovat třeba na to, jak moc se text rýmuje a má rytmické opakující se šablony. Vysoké kladné číslo bude naznačovat velmi pravidelnou říkanku, o něco nižší přerývaný verš a čísla pod nulou budou znamenat jasnou prózu. Jiný hodnotitel bude zaznamenávat míru vtipnosti, další tragičnosti, ještě další míru vědečnosti, slovní rozmanitosti, míru zahrnutí přírody jako tématu nebo hodnocení erotičnosti. Pokud by takových dimenzí bylo třeba 1000, tak už o textu získáte docela dost informací. I kdyby vám teď někdo vymazal názvy dimenzí, tak texty, které jsou v každé dimenzi hodnoceny víceméně stejně, si budou dost podobné. Pokud si dimenze představíte jako vícerozměrný prostor, tak body, které jsou si blízko, budou mít vysokou míru podobnosti zdrojových textů. Tohle můžete vyřešit matematicky třeba přes Cosine similarity.

Tohle nám dává minimálně dva zajímavé příklady použití. Mohu vzít celý soubor dat (třeba popis jednotlivých filmů) a u každého spočítat a uložit embeddings. Díky tomu pak dokážu k danému filmu najít ty, které mu jsou (co do popisu) nejpodobnější nebo naopak jsou nejvíc jiné (až to níže budeme řešit prakticky tak nezapomínejme, že vše stojí na kvalitě a konzistenci popisovacích textů, které ne vždy musí dobře vystihovat podstatu filmu ... jako vždy - na kvalitě dát hodně záleží). Druhým příkladem je chytré vyhledávání. Stejně jako v předchozím případě si seženete embeddings na všechny vaše texty - popisky filmů, články ve znalostní bázi, profily uživatelů nebo novinové příspěvky. Následně necháte uživatele napsat co hledá, z toho uděláte embeddings a najdete nejpodobnější texty přes ten vektor čísel v nicneříkajících dimenzích. 

Proč je tohle zajímavé v kombinaci s GPT? To nemůžu hledat podobné texty přes podobnost slov jako v případě K-Means nebo použít full-textové vyhledávání, nejlépe takové, které umí skloňovat a dávat větší score těm odpovědím, které mají stejné pořadí slov a tak podobně? Jasně že můžu. Finta je ale v tom, že GPT model byl trénován na enormním vzorku dat s neuvěřitelným množstvím parametrů. Tady si tedy nehrajeme s počítáním výskytu stejných slov ani "mechanickými" vylepšeními takových řešení jako je korelace se seznamem synonym, skloňování nebo "chytré" scorování výsledků podle četnosti výskytu nebo pořadí slov. OpenAI tomu textu daleko víc "rozumí". Vzpomínáte na všechna kouzla ChatGPT nebo sumarizace, o které jsem psal minule? Všechno tohle je v embeddings implicitně schováno. 

# Příprava dat
Jako vzorek dat jsem se rozhodl využít databázi filmů TMDB a přes jejich API si je stáhl do souboru (kód pro stažení najdete u mě: [https://github.com/tkubica12/ai-demos/blob/main/openai/src/tbdb_downloader/tmdb_downloader.py](https://github.com/tkubica12/ai-demos/blob/main/openai/src/tbdb_downloader/tmdb_downloader.py)). Tady pár důležitých upozornění:
- Z cenových a časových důvodů jsem nepoužil největší GPT 3 model DaVinci, protože čekám, až se v Azure OpenAI objeví next-gen řešení pro embeddings. GPT model, který použiji, je dramaticky menší a to bude znát hodně u češtiny - přesto jsem ji chtěl použít.
- Popisky na TMDB v češtině mají menší kvalitu, než u angličtiny. Některé filmy jsou popsány skvěle (třeba právě Pulp Fiction), jiné ne.

Nahraji filmy do Pandas DataFrame a vyhledejme si popisek Pulp Fiction.

[![](/images/2023/2023-01-31-17-10-10.png){:class="img-fluid"}](/images/2023/2023-01-31-17-10-10.png)

Zkusme si jen tak tento test prohnat přes Azure OpenAI API a získat embeddings.

[![](/images/2023/2023-01-31-17-11-56.png){:class="img-fluid"}](/images/2023/2023-01-31-17-11-56.png)

Dle očekávání je to hromada čísel. V datech jsou ještě vyjmenované žánry a to dává smysl do dat přidat. Model očekává textový řetězec bez ukončování řádek apod., takže pojďme žánry naházet za sebou jako text a pokračovat s textem Overview: a sem dosadit popisek filmu. Dávalo by smysl, tam dát i název filmu, ale já to schválně neudělal, ať to má těžší. Použiji lambda funkci v rámci Pandas DataFrame a přes apply jím proženu celý svůj soubor dat.

[![](/images/2023/2023-01-31-17-15-53.png){:class="img-fluid"}](/images/2023/2023-01-31-17-15-53.png)

Tím mám data pro scoring připravena a můžeme provolat Azure OpenAI opět s využitím lambda funkce v rámci apply v Pandas. Tím získáme nový sloupeček, ve kterém bude vždy pole výsledných embeddings.

[![](/images/2023/2023-01-31-17-20-18.png){:class="img-fluid"}](/images/2023/2023-01-31-17-20-18.png)

# Doporučení podobných textů
Pojďme tedy najít filmy, jejichž popisy jsou podobné tomu pro Pulp Fiction. OpenAI SDK nabízí funkci cosine_similarity, takže nemusím programovat logiku hledání nejbližších sousedů ve vektorech. Z praktického hlediska by ale určitě stálo za to se zamyslet nad dalšími možnostmi, protože jednak ne vždy se celý DataFrame vejde do paměti, projet operace přes všechny záznamy může být pomalé a hodila by se nějaká paralelizace a dokonce existují i specializované databáze navržené právě pro úkoly hledání sousedů ve vektorech (například Pinecone).

Vezmu si tedy vektor z Pulp Fiction jako základ.

[![](/images/2023/2023-01-31-18-34-21.png){:class="img-fluid"}](/images/2023/2023-01-31-18-34-21.png)

Teď musím spočítat "vzdálenost" jednoho každého filmu a k tomu opět použiji apply lambda funkci v Pandas a vznikne mi tak sloupeček míry podobnosti textu s Pulp Fiction popisem.

[![](/images/2023/2023-01-31-18-35-25.png){:class="img-fluid"}](/images/2023/2023-01-31-18-35-25.png)

Pak už stačí jen výsledky seřadit a to buď shora (získám nejpodobnější popisky) nebo opačně (získám ty nejméně podobné).

```python
top5 = df.sort_values('similarities', ascending=False).head(6).tail(5)
last5 = df.sort_values('similarities', ascending=False).tail(5)
```

Jak to dopadlo? Nezapomeňme na omezení mého příkladu - české popisky na TMDB nemusí být dostatečně kvalitní a vypovídající (pokud máte Pulp Fiction rádi, určitě o něm víte víc, než co je v popisku), curie generace OpenAI modelu není tak mohutná a čeština ji nemusí jít nějak skvěle. Připomínám, že název filmu jsem do embeddings nezahrnoval, aby to bylo zajímavější. Posuďte sami.

Nejpodobnější popisky:
- Ruang talok 69: 69 je thajským příspěvkem do vlny kriminálek, které využívají jako hybný prvek děje fenomén náhody, mezi něž dále spadají například filmy bratří Coenů, Pulp Fiction – Historky z podsvětí (Pulp Fiction, USA, 1994) Quentina Tarantina nebo tvorba Brita Guye Ritchieho či Japonce SABUa. Ratanaruangův snímek se od nich liší především v tom, že náhodu vztahuje ke světu čísel.
- Casino: V zaběhané mašinérii vztahů, orientované na legální i nelegální vydělávání peněz, se v rozmezí deseti let odehrává příběh trojice zúčastněných osob: Sam "Ace" Rothstein je bývalý hazardní hráč, dosazený mafiánským gangem do Las Vegas na vedoucí místo velkého kasina, které se jeho přičiněním stane minořádně úspěšným. Rothsteinovu osobní bezpečnost zajišťuje jeho nejlepší přítel, brutální gangster Nicky Santoro. Osudový zvrat do Samova života přinese profesionální podvodnice Ginger McKennaová, do níž se Rothstein zamiluje a jíž bezmezně věří. Město, obklopené ze všech stran pouští, je pro Scorseseho prostorem ze zvláštní působivostí, místem, kde platí odlišná pravidla a kde může organizovaný zločin dospět k naprosté dokonalosti. Snímek Casino je velice podrobnou studií situace, kdy mafie bez problémů dosáhla všech svých cílů, ale místo trvalého fungování se ze své vlastní podstaty začíná hroutit. Jeden z nejlepších filmů Roberta de Nira a 90. let vůbec.
- Plump Fiction: Komediální efekt je založen na citátech známých scén z úspěšných filmů poslední doby. Jak naznačuje název filmu, nejvíce se utahuje z Tarantinových filmů as chutí se zde přehrávají scény z nejrůznějších gangsterek, komedií a psychologických filmů.
- Gomora: Brutálně syrová freska o cestách, jakými neapolská camorra ovládá všední život lidí. Jsme ve světě, kde jediným zákonem je násilí, jedinou hodnotou moc a jedinou řečí štěkot zbraní. Jde o nadvládu nad trhem s narkotiky, s nebezpečným odpadem a dokonce i s oblékáním. Film vznikl na základě knihy Roberta Saviana, která se v roce 2006 stala rázem bestsellerem. Na nedávném festivalu v Cannes získala Gomorra Velkou cenu.
- Lovcova noc: Film noir o zradě, hříchu, nevinnosti, a zejména odvěkém souboji dobra se zlem. Jeden z nejúchvatnějších padouchů filmového historie, ďábelský Harry Powell, se snaží vetřít do rodiny svého bývalého spoluvězně. Jeho děti by totiž měly vědět, kde je ukrytý lup. Když před tímto zákeřným a nemilosrdným reverendem děti prchnou, pronásleduje své malé oběti vytrvale až do velkého finále. Vizionářský film, který je také poctou němé kinematografii od Griffitha po vrcholná díla německého expresionismu, byl ve své době nepochopen a propadl u diváků i kritiky. Dnes je snímek absolutní klasikou, nechybí v prestižních žebříčcích kultovních filmů a sám se stal jedním z nejcitovanějších filmových děl.

**UPDATE:** V Azure už je nejnovější model text-embedding-ada-002 a tady jsou výsledky - zdají se vám lepší? Těžko přesně hodnotit, určitě nejsou horší a vzhledem k tomu, že jsou rozhodně levnější, tak to je pozitivní posun. Určitě se mi nelíbí, že je ve výsledku dokument o Bruce Willisov (asi bychom měli klást větší důraz na žánr), ale na druhou stranu ostatní texty sedí velmi dobře.
- Ruang talok 69: 69 je thajským příspěvkem do vlny kriminálek, které využívají jako hybný prvek děje fenomén náhody, mezi něž dále spadají například filmy bratří Coenů, Pulp Fiction – Historky z podsvětí (Pulp Fiction, USA, 1994) Quentina Tarantina nebo tvorba Brita Guye Ritchieho či Japonce SABUa. Ratanaruangův snímek se od nich liší především v tom, že náhodu vztahuje ke světu čísel.
- Můj velký tlustý nezávislý film: První parodie, která si dálá legraci z nezávislých filmů jako Memento, Pulp Fiction, Desperado. Zamotaný příběh několika lidských osudů vytváří vtipné scény, které se prolínají v jeden příběh a navzájem se ovlivňují.
- Kill Bill - Celá krvavá záležitost: Odkdy vyšel Kill Bill Volume 1 v roce 2003, poslouchali jsme, že režisér Quentin Tarantino nakonec plánoval vydat obě poloviny v jednom epickém balíčku. Kill Bill Volume 2 vyšel o rok později a zdálo se to jako logický čas na velké odhalení. Nestalo se.  Pak v roce 2004 uvedl Tarantino na filmovém festivalu v Cannes kombinovanou verzi filmu, která se stala známou jako Kill Bill: Celá krvavá záležitost / Kill Bill - The Whole Bloody Affair. Roky prošly a nakonec Tarantino divadlo, New Beverly Cinema v Los Angeles, dostalo povolení poprvé tento film uvést v USA v roce 2011.  Film je v podstatě shodný s původními dvěma originálními filmy Kill Bill vol.1 a vol.2, je jen mistrovsky spojen v jeden celek ... má však o něco delší scénky a hlavně má pasáž bitvy "nevěsty" a Crazy 88 plně kolorizovanú'
- Bruce Willis - vyvolený: Portrét fenomenálního amerického filmového herce... Smrtonosná past, Pulp Fiction, Pátý element… V několika filmech na začátku devadesátých let se Bruce Willis prosadil jako novodobý americký akční hrdina. V době, kdy se oblíbený filmový žánr vyznačoval především velkými bicepsy a kdy se na plakátech k blockbusterům střídali Sylvester Stallone a Arnold Schwarzenegger, nebylo nic méně samozřejmého. Bruce Willis však svým šibalským úsměvem prolomil do té doby velkou bariéru mezi televizí a filmem a stal se jednou z největších hollywoodských hvězd své doby.
- Lepší zítřek 2: Ve druhém filmu se vrací hrdinové prvního dílu a přidává se k nim i Ken Gor s párátkem v ústech a pistolí v každé ruce. Woo rozehrává další typické kriminální melodrama, další příběh pomsty, věrnosti, cti a zrady. Jako většina Woových filmů, má i tenhle příchuť tragédie. Ne všichni kladní hrdinové dobře dopadnou... ale můžeme zaručit, že ti, co odejdou, rozhodně odejdou ve velkém stylu. Proto se není co divit, že finální přestřelku citoval Quentin Tarantino ve svém a Scottově filmu Pravdivá romance.

A co naopak zcela odlišné popisky?
- Silvestr 79 aneb hrajeme si jako děti: Záznam Silvestrovského programu 1979
- Silvestr na přání aneb Čí jsou hory Kavčí: Silvestrovský program roku 1977-78
- Dalur: Poetická utopie o malém chlapci.
- Ludovico Einaudi - Živě  Waldbuhne Berlin 2017: Koncert živě z Berlína
- Sting - Live at iHeartRadio: Záznam koncertu

To docela sedí, ne? S lepším modelem (next-gen, který v Azure brzy bude) a možná s lepším vyladěním co scorovat (teď třeba nerozlišujeme mezi rozpočtem či hodnocením filmů, což je fajn na hledání obecné shody, ale v reálném případě možná přecijen budete chtít, aby alternativní film preferoval jiné alternativní a naopak profláklé kasovní trháky mířily na sebe - možná do embeddings zahrnete hodnocení či rozpočet) a ověřením kvality popisků to může být hodně přesné.

# Chytré vyhledávání
Vyzkoušejme druhou úlohu. Nechme uživatele zadat text, z něj vytvořme embeddings a najděme nejpodobnější popisky filmů. 

Použiji tento vyhledávací text:
*Genres: Vědeckofantastický Overview: Film z budoucnosti, ve kterém se bojuje mezi lidmi a roboty. Používají se hvězdné lodě, laserové zbraně a lidé se musí spojit, aby vzbouřené roboty porazili.*

[![](/images/2023/2023-01-31-18-45-02.png){:class="img-fluid"}](/images/2023/2023-01-31-18-45-02.png)

Výsledek?
- Za čárou: V blízké budoucnosti dostane pilot dronu rozkaz přesunout se do válečné zóny, kde mu má velet android v přísném utajení – a společně pak musí zabránit jadernému útoku.
- Americké válečné lodě: Záhadné mimozemské lodě dosedají v Tichém oceánu a začínají válku o Zemi. Jedinou lodí, která je může zastavit je posádka lodi Iowa.
- Junk Head 1: Ve vzdálené budoucnosti lidstvo zahájí výzkum klonů, které žijí v podzemí a hledají ztracené genetické informace.
- Smyčka času: Film se točí kolem týmu vojenských agentů a civilních vědců, kteří musí použít netestovanou technologii k návratu časem, aby pozměnili minulé události a tak se postarali o jinou budoucnost. Hrozí totiž drtivý teroristický útok.
- The Cloverfield Paradox: Na oběžné dráze nad planetou na pokraji války, vědci testují zařízení, které řeší energetickou krizi a končí tváří v tvář temné alternativní realitě.

Za mě to není zlé. Samozřejmě takhle krátký popisek asi není dostatečný, aby vystihl plný obsah filmu, ale i tak to rozhodně není mimo. Všimněte si, že na rozdíl od klasického full-text hledání tady často není slovní podobnost skoro žádná. Například v druhém popisku zdá se mi vidím jen jediné společné slovo - lodě. Z pohledu slov je tohle strašně málo, klidně by to mohl být film o tom, jak se náctiletí vydají sjíždět řeku. I přes jediné stejné slovo je význam blízko - model evidentně chápe, že mimozemské lodě a hvězdné lodě jsou si blízké, to, že někdo začíná válku je podobné slovu bojovat a tak dál. Myslím ale, že model je ještě daleko dál a pokud ho nakrmíme bohatšími daty, ukáže se to ještě víc. A teď si připomeňme, že používám model curie (ne velký GPT 3 model davinci) a k tomu všemu OpenAI už má novou generaci modelů pro embeddings, které jsou přesnější a přitom menší a levnější.

**UPDATE:** Takhle vypadají výsledky z nejnovějšího text-embedding-ada-002, tedy modelu, který je výrazně menší (= levnější) a přitom přepracovaný speciálně na embeddings.
- Robot Jox - Zápas robotů: Daleká budoucnost. Lidé ze zkumavky už nejsou jen fantazií, vzduch plný prachu, nedostatek jídla a kvalitního kyslíku připravuje pozemšťany o naděje na lepší zítřek. Lidé o poslední zásoby potravin nebojují na vojenských polích, ale v arénách, kde o vítězství rozhodují stotunové bojové stroje. Finální zápas se pomalu blíží a stáje robotů Alexander a MasimutoTech připravují piloty na závěrečný boj, který zkomplikuje nejen průmyslová špionáž, ale i láska.
- Pacific Rim - Útok na Zemi: Z moře se vynoří obrovské příšery Kaiju a pustí se do války s lidstvem, která si vyžádá milióny životů a lidstvo na roky zatíží. Pro boj s Kaiju byla vyvinuta speciální zbraň: masivní roboti zvaní Jaegers, kteří jsou simultánně ovládáni dvěma piloty, jejichž mozky jsou propojeny neurálním mostem. Jenže i tihle roboti se tváří v tvář nezničitelným Kaiju zdají být téměř bezmocní. Na pokraji porážky nakonec síly bránící lidstvo nemají jinou možnost než obrátit svoji naději směrem ke dvěma nečekaným hrdinům: bývalému pilotovi a nezkušenému nováčkovi, kteří se dají dohromady, aby společně řídli slavného, nicméně zároveň zjevně zastaralého Jaegera. Společně budou čelit hrozící apokalypse.
- Kung fu Traveler: Kung fu Traveler
- 2019 - Noví barbaři: V postapokalyptické budoucnosti skupina unavených přeživších čelí neustálým útokům ze strany gangu potulných banditů. Do tohoto konfliktu vstupují dva lidé, rivalové od přírody, kteří jsou teď nuceni postavit se na stejnou stranu proti společnému nepříteli. Přežití lidské rasy závisí na následující bitvě...
- Space Station 76: Skupina lidí a několika robotů žije na vesmírné stanici v budoucnosti ve stylu sedmdesátých let. Když na palubu dorazí nová pomocná kapitánka (Liv Tylerová), bezděky vyvolá mezi členy posádky napětí tím, že je vybídne, aby se postavili tváří v tvář svým nejtemnějším tajemstvím. Na povrch tak začíná prosakovat chtíč, žárlivost a vztek, což je stejně nebezpečné jako asteroid řítící se přímo proti nim.

# Náklady
Nemám to spočítané přesně, ale pojďme si to říct na modelovém příkladu. Dejme tomu, že popisek má v průměru 300 českých znaků, tj. asi 150 tokenů. Filmů je 33 000. Kolik vyjde scoring embeddings pro celý soubor?
- Model Ada - to je paradoxně nejstarší a nejlevnější, ale současně ve variantě text-embeddings-ada-002 ten nejnovější - 2 USD
- Model Babbage - 2,5 USD
- Model Currie (ten jsem použil) - 10 USD
- Model Davinci (obrovitánský GPT 3.5) - 100 USD

Jakmile score mám, tak hledání podobností vektorů už mě nic nestojí. Search znamená, že musím provést scoring uživatelova vstupu, ale pak už jen hledám. 


Minule jsme řešili sumarizaci a dnes si dali odbočku k embeddings, které mohou ve velkém řešit problematiku clusteringu (najít skryté kategorie, škatulky), hledání podobností (například pro doporučení) nebo chytré vyhledávání (představte si třeba chatbota, kterého se uživatel ptá a on mu naservíruje dokumenty, které mají k jeho otázce nejblíž). Příště se chci vrátit k hlavnímu jazykovému modelu a zkoušet věci jako extrakci informací, kategorizaci textu a další vychytávky.