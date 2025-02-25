---
layout: post
published: true
title: Vlastní data (RAG) pro vašeho AI agenta krok za krokem s Python a PostgreSQL
tags:
- AI
- PostgreSQL
---
Když se vás zeptám na nějaké faktické informace, třeba na něco z firemních směrnic, dám vám otázku z testu na Azure nebo jaký film doporučíte někomu, kdo viděl Matrix a chtěl by něco podobného, tak se můžete pokusit to udělat z hlavy. Budete mít možná problém si vzpomenou úplně přesně, možná uděláte i nějakou chybu, něco trochu popletete a když budu chtít, abyste citovali potřebné zdroje (na které stránce jakého dokumentu se o tom píše), tak často nebudete vědět, kde jste ke své znalosti přišli.

Srovnejte to ale s tím, když vám řeknu, že si klidně můžete před odpovědí pohledat po Internetu, prolistovat poznámky, prolétnout vytištěné směrnice nebo si zaklikat v Azure dokumentaci. Předpokládám, že tím se jednak výrazně zlepší přesnost vašich odpovědí a také mi řeknete, kde se o tom píše, ocitujete zdroje. Výborná věc. Jenže co když místo dobrého zacílení na určitou část dokumentace nebo směrnici vám nabídnu stránky z celé knihovny, ale bez přebalů a jakéhokoli řazení nebo indexování titulů? Pomůže to? Asi ano, ale bude vám to trvat mnohem déle, spotřebujete daleko víc energie a může se stát, že pokud naprostá většina stránek není pro odpověď důležitá, tak ztratíte pozornost a správné odpovědi si tam někde uprostřed nevšimnete.

To co jsem právě popsal funguje ve velkých jazykových modelech (LLM) taky a říká se tomu Retrieval Augmented Generation (RAG). Ideální je, když se model dostane k co nejlépe zacíleným dokumentům, ve kterých se skrývá odpověď a on tak může dávat naprosto přesné, rychlé a levné výstupy. Když se netrefíme a dáme mu dokumenty, které moc relevantní nejsou, odpovědi se zhorší. Když budeme mít model s velkým kontextem (podporou velkého množství vstupních tokenů) a nahrneme mu celou knihovnu, bude to drahé, pomalé a výsledky stejně nebudou tak dobré, jako v případě dobře zvolených referenčních dokumentů.

Dnes se chci zaměřit na problematiku hledání těch správných podkladů pro vaše LLM. Nebudeme tentokrát řešit přípravu dokumentů a jejich krájení ani složitější znalostní báze postavené na grafu provázaností a sumarizací. O tom jindy.

# RAG s Python a PostgreSQL
Otevřete si prosím [Jupyter Notebook na mém GitHubu](https://github.com/tkubica12/azure-workshops/blob/main/d-ai-rag/rag_guide.ipynb). Najdete tam konkrétní výsledky a výstupy, doporučuji si vzít při čtení k ruce.

Celý příběh začíná tím, že vezmeme dokumenty, kterými budou  popisky filmů a vložíme je do PostgreSQL s tím, že vytvoříme kombinovaný sloupeček s název a popisem (ať nemusíme dělat vektory z obou). Potřebnou infrastrukturu jako jsou Azure OpenAI modely a Azure PostgreSQL Flexible Server a si můžete nahodit z mého Terraformu v příslušném adresáři. Než udělám samotný import je potřeba přidat některá rozšíření, která budeme používat, konkrétně:
- azure_ai extension, díky které můžu přímo z PSQL provolávat Azure OpenAI pro získání embeddingů (vektorů), ale i volat do kognitivních služeb Azure (extrakce entit, PII identifikace a tak podobně) nebo modelů nasazených v Azure Machine Learning
- pgvector extension, který nám umožní ukládat embeddingy přímo do PostgreSQL a provádět nad nimi vyhledávání
- pg_diskann extension, který nám umožní provádět vyhledávání v embeddingových vektorech rychleji a efektivněji

Založím tabulku, přidám sloupeček embedding s 2000 dimenzemi, přidám další sloupeček full_test_search pro tsvector (statistika pro full text, víceméně kořeny použitých slov a jejich výskyty) a přidám diskann index. Pak vložím data a následně k nim přidám embeddings s využitím SQL příkazu UPDATE společně s funkcí z azure_ai, takže databáze si do Azure OpenAI služby bude volat sama a zařídí si to.

## Co je embedding a vector search?
Ve strojovém učení je časté, že chceme svět s jeho velkou variabilitou a složitostí zjednodušit na menší počet vlastností, defacto ho zkomprimovat do menšího a to ztrátovým způsobem (nejde tedy o zip, ale spíš si představte něco jako MP3). Představme si třeba, že pro text připravíme score v několika dimenzích, například "míra veršovanosti", "míra humoru" a tak podobně. Pokud takových vlastností použijeme stovky, tak budou mít dobrou vypovídací schopnost, dobře budou reprezentovat původní text. Ve strojovém učení ale nebudeme AI diktovat, co to má být za dimenze a vlastnosti, to necháme na něm. Tyto techniky jakési extrakce najzásadnějších vlastností s co největší vypovídací schopností, tyto vektory (vyjmenovaná čísla, score za jednotlivé vlastnosti, dimenze), embeddingy, se pak používají pro reprezentaci původního vstupu a významovou extrakci jak u textů (to je náš případ), extrakci vlastností z obrázku (například klasifikace), tak třeba u Diffusion modelů (generování obrázků a videa).

Strojové učení našlo pravidla, jak extrahovat score v jednotlivých dimenzích tak, aby byl text co nejvíce zachován a díky masivní kompresi se soustředí na význam. Je jedno jak to řeknu, ale podstatný je význam - ten je tedy to nejdůležitější a je tedy vhodným embeddingem v omezeném prostoru. Tyto dimenze skutečně představují nějaký n-rozměrný prostor, říkáme mu typicky latentní prostor a každý text je tak zasazen do nějakého bodu tohoto prostoru. Z různých textů umístěných v prostoru pak můžeme usuzovat na míru jejich příbuznosti a významové podobnosti. Mohli bychom například změřit euklidovskou vzdálenost mezi těmito body, udělat skalární součin nebo úhel mezi přímkou z počátku do jednoho bodu a do druhého (cosinus - to použijeme my, protože najde podobnost i při rozdílné škále).

Jak v tom tedy hledat? Nejprve ke všem popiskům filmů nechám model vytvořit embedding, ten si uložíme a až pak dostaneme dotaz, tak i ten zasadíme do latentního prostoru a koukneme, které body jsou dotazu nejpodobnější.

## Full-text řešení a vylepšení dotazu
Nejprve ale nasaďme full-text, kdy PostgreSQL prošel jednotlivé popisky, identifikovat kořeny slov, spočítal si je a statistiky si u každého filmu uložil. Vzneseme dotaz, proženeme full-textem a necháme si prvních 10 nejbližších odpovědí a s těmi budeme pracovat. Jednotlivé otázky a odpovědi najdete v mém odkazovaném Jupyter notebooku a následně je předhodíme LLM pro formulaci odpovědi. 

První pokus nic moc. Otázka na Abby vedle jen na jeden film (což je špatně) a ostatní také nejsou moc dobré. Potíž je, že full-text search není ChatGPT, takže otázka "What movies are about Abby?" je značně nevhodná, protože tím hledáme všechna tato slova z nich kromě Abby vlastně žádné není důležité a nepotřebujeme ho v textu vůbec mít. 

Pojďme provést tzv. question rewriting, tedy necháme menší jazykový model (já použiji gpt-4o-mini) dotaz přeformulovat a optimalizovat pro full text. V notebooku vidíte tento scénář ve výstupech včetně přeformulovaného dotazu a na Abby máme tentokrát výsledky mnohem lepší (4 filmy). Nicméně druhé dva dotazy jsou stále špatné - hledáme filmy jako Star Wars, ale ne Star Wars, což ale full-text samozřejmě nemá jak pochopit, takže nám právě najde všechny Star Wars a to nechceme - ty už tazatel všechny viděl. Asi to bude chtít hledat spíše význam.

## Sémantické vyhledávání a vylepšení dotazu
Třetí varianta je sémantický search, nebo-li vektorové hledání podobností z embeddingů. Nicméně na první otázce, tedy filmy kde je postava Abby, nám to selhává. Tímto příkladem jsem chtěl demonstrovat, že vektory jsou povětšinou skvělé, ale v okamžiku, kdy vlastně potřebujeme hledat konkrétní krátkou faktickou informaci typu číslo faktury, tak to moc nedávají. Nicméně druhé dvě otázky jsou teď určitě lepší, byť Star Wars jsou stále problém. Přestože tentokrát už máme ve výsledcích i podobné sci-fi filmy, tak přímo těch Star Wars co nepotřebujeme je tam pořád dost. Je to něco, s čím jednoduchých scénářích nic moc neuděláme - na embedding je to moc komplikovaná konstrukce. V praxi bychom asi museli dávat do kontextu filmů víc a LLM si to v seznamu najde. Embeddingy tam ve finále ty správné věci mají, i když trochu zastřené těmi Star Wars a LLM to v tomhle počtu v klidu dá.

Stejně jako v předchozím případě může dávat smysl dotaz přeformulovat, než podle něj budeme hledat. V mém případě jsem použil opět menší LLM (gpt-4o-mini) s cílem otázku učinit jasnou, dobře formulovanou a bez překlepů a gramatických chyb. Zejména u vstupu od skutečného uživatele tohle pomůže k lepšímu vyhledávání. V mém případě rozdíl není zásadní, ale je viditelný třeba u filmů jako Star Wars. Existuje i pár dalších technik z nichž asi nejznámější je HyDE (Hypothetical Document Embedding). Tam necháte LLM na základě otázky vysnit si fiktivní dokument, který by byl ideálním podpokladem pro odpověď na takovou otázku a podle něj pak provedete vekotorové hledání. 

## Hybridní řešení a re-ranking výsledků