---
layout: post
published: true
title: Nativní Azure Monitor a Microsoft Sentinel nově umí levnější logy a zabudovanou levnější archivaci - analýza nákladů (část 1)
tags:
- Monitoring
- Security
- Kubernetes
---
Log Analytics jsou kombinace specializovaného databázového stroje, ingesting pipelines a agentů pro sběr dat ze strojů. Pod kapotou je v roli datového engine Azure Data Explorer. Nad Log Analytics jsou pak vystavena tři velká řešení. 
- Tím prvním je **Azure Monitor**, který do toho vnáší sběr specializovaných informací (obohacuje základní agenty třeba o monitoring síťového provozu stanice nebo sbírání inventáře v Kubernetes), specializované vizualizace (na VM, na kontejnery, na storage apod.), alerting a atd.
- Dále je to **Microsoft Sentinel**, který se zaměřuje na bezpečnostní analýzu logů. Dokáže dělat jak Microsoftem připravené tak vlastní analytické operace včetně strojového učení a velmi komplexních věcí, vyšetřování, hunting, obohacování dat, detekce anomálií nebo sledování chování entit jako jsou uživatel nebo stanice.
- **Application Insights** je specializovaná nadstavba na Application Performance Monitoring a tracing. Ta přichází se sadou SDK přímo do aplikací (nebo s podporou pro OpenTelemetry standardy) a přináší specializovanou analytiku aplikací (proč běží pomalu), vizualizaci architektury a interakcí komponent, analyzuje interakci mezi součástkami, měží dostupnost, výkonnost, chybovost a tak podobně.

Když si uvědomíte, že analytická pravidla v Sentinelu, kterých můžete zapnout stovky, jsou hodně komplexní (parsing, mnoho join na různé datové tabulky) a běží každých 5 minut nebo dokonce každou minutu (takže očekáváte, že i složitá query budou trvat v řádu jednotek či desítek vteřin), je jasné, že Azure Data Explorer pod tím je hodně optimalizovaný na masivní výkon. Cluster bude nepochybně držet velké množství dat v paměti a na extrémně rychlých NVMe storage a tak podobně - zkrátka sizing je optimalizovaný na to, že nad tím stavíte extrémně náročná řešení typu Sentinel. To samozřejmě znamená vyšší cenu - těžko to srovnávat se situací, kdy chcete jen základní search/filtraci nebo jste ochotni na výstupy čekat minuty a platit za jednotlivé query.

Nicméně tenhle přístup s použitím masivního děla na všechno může znamenat nižší cenovou efektivitu pro běžné logy, kde pokročilou analýzu nepotřebujete nebo ji neděláte běžně, jen když se něco zpětně vyšetřuje nebo kde potřebujete držet data v systému ze zákonných důvodů, ale reálně se na ně moc často nekoukáte. Přesně tuhle nevýhodu chce Azure řešit s technologií Basic Logs tier, Archive tier, Search jobs a restoration. Podívejme se dnes k čemu je to dobré a jak se to bude počítat. Příště si pak vyzkoušíme v praxi.

# Nabírání dat pro pokročilou analytiku vs. pro základní logy
Pro nabírání analytických logů se platí 2,682 EUR za GB (v pay-as-you-go ve West Europe s tím, že při vysoké spotřebě můžete rezervovat a dostat se až na 1,87 EUR za GB při 5TB denně) a v ceně je retenece na 30 dní (případně 90, když si nad tím ještě přikoupíte Sentinel). K dispozici máte plné funkce včetně joinů, sumarizací, strojového učení, statistiky, alertování a tak podobně. Pokud chcete v tomto tieru udržet data déle (se všemi možnostmi analytiky), můžete si přikoupit retenci za 0,117 EUR za GB měsíčně. Druhá možnost (viz dále) je nově Archive tier.

Nová varianta Basic Logs je tier, kde platíte jen 0,584 EUR za GB ingestingu a v ceně je retence na 8 dní. Prodloužit ji nelze, ale můžete si tam dát Archive tier. V Basic logs můžete vyhledávat vysokou rychlostí (odezvy řádu pár vteřin), ale možnosti query jazyka jsou omezené na vyhledávání, parsování a filtraci. Lze tedy přidávat sloupečky, parsovat text Regex pravidly, hledat slova a řetězce uvnitř políček, čistit data, filtrovat výstup a to i z dynamicky vytvořeného sloupce z předchozího kroku a tak podobně. Nemůžete ale dělat analytiku - sumarizovat, agregovat, aplikovat analýzu časové řady typu predikce dalšího vývoje, joinovat na jiné tabulky. Navíc jednotlivé dotazy jsou zpoplatněny a to tak, že platíte 0,006 EUR za GB dat, které proscanujete (přes které váš dotaz jde, například data za poslední hodinu, bez ohledu na výsledek). Basic logs se aktuálně nastavují per tabulka a ze zabudovaných jsou podporované zatím jen ContainerLog (Azure Monitor for Containers), aplikační tracing z Application Insights a pak custom tabulky.

Do našeho výpočetního modelového příkladu určitě zahrneme obě kategorie. Typicky pro bezpečnostní logy, které chci analyzovat v Sentinelu (analyzovat = parsovat, seskupovat, hledat anomálie, korelovat), potřebuji běžný analytický tier. Ale na logy spíše forenzního typu, kde mi jde o jednoduchý search, jako jsou například logy z kontejnerů a aplikací, rád použiji Basic logs.

# Archivní tier, search jobs vs. restore
Ať už se jedná o analytické nebo basic logy, můžete si tabulku po určité době nechat hodit do archivního tieru. V případě analytických logů tedy máte tři roviny - retence, která je v ceně ingestingu (30 dní u Azure Monitor a 90 dní když si dokoupíte Sentinel) + případná prodloužená retence za poplatek (v tom stejném tieru) + případný archiv. U basic logů je to 8 dní + případný archiv. V archivním tieru platíte 0,024 EUR za GB měsíčně.

V datech v archivu můžeme vyhledávat a to použitím omezeného query, které funkčně odpovídá tomu, jak fungují Basic logs. Můžeme tedy filtrovat, parsovat, vytvářet sloupce a tak podobně, ale ne agregovat, sumarizovat, joinovat. Tyto Search Job fungují na rozdíl od tieru Analytics nebo Basic asynchronně - zadáte dotaz, on běží na pozadí a svoje výsledky vám ukládá jako speciální novou tabulku do vašeho Log Analytics workspace. Platíte 0,006 EUR za scanovaný GB (stejně jako u Basic logs) a k tomu ingesting výsledků do nové tabulky (2,682 EUR za GB). Tím, že výsledky jsou nahrány jako samostatná plná analytics tabulka, lze s nimi pak dál pracovat - zpřesňovat, agregovat, vizualizovat, joinovat a tak podobně.

Druhou variantou je nechat si celý blok dat (tabulku a časové rozmezí s tím, že minimum je okno dvou dní) zavlažit, tedy přesunout její data do rychlého analytického tieru. To se platí částkou 0,117 EUR za GB a jeden den v rychlém tieru. Zatímco v prvním případě zaplatím relativně drahý ingesting, takže Search Job se hodí tam, kde chci z archivu vytáhnout jen menší podmnožinu specificky definovaných dat (např. data jednoho uživatele), proces zavlažení celého bloku (bez filtrace) je výhodný v okamžiku, kdy vlastně nevíte co přesně hledáte - potřebujete mít k dispozici všechno v plné palbě a nad tím dělat analýzu (vyšetřujete potenciální bezpečnostní útok a hledáte stopy).

Zní to složitě, ale v následujícím výpočtu to bude snad srozumitelné.

# Model a výpočet
Mějme následující situaci:
- 10 GB denně bezpečnostních logů
  - vyžadujeme pokročilou analýzu a to na datech po dobu 4 měsíců
  - dalších 8 měsíců chceme data v archivu s možností v nich prohledávat, případně je obnovit
- 10 GB denně aplikačních logů
  - vyžadujeme search, ne pokročilou analytiku
  - data potřebujeme držet po dobu 12 měsíců v archivu s možností v nich vyhledávat
- Úkol 1 - potřebujeme vyhledat ERROR hlášky konkrétní aplikace ve včerejších datech (hlášky představují 100 MB dat) a tento úkon děláme 200x měsíčně
- Úkol 2 - potřebujeme vyhledat ERROR hlášky konkrétní aplikace v archivu v rozmezí 5 dnů (hlášky představují 500 MB dat) a tento úkon děláme 10x měsíčně
- Úkol 3 - potřebujeme analyzovat chování (nevíme přesně co hledáme) jedné aplikace z dat v archivu v rozmezí 5 dní (objem dat aplikace představuje 1 GB dat) a tento úkon děláme 5x měsíčně
- Úkol 4 - potřebujeme analyzovat chování jedné aplikace z dat v archivu v rozmezí 5 dní (objem dat aplikace představuje 25 GB dat) a tento úkon děláme 5x měsíčně

Srovnávat budeme klasickou variantu (všechno v analytickém tieru a připlacená retence) vs. optimalizované řešení s využitím basic logs a archivu. Objemy a s tím spojenou cenu budu počítat na konci období, tedy kolik zaplatím 12. měsíc (všechny následující jsou pak bez změny množství dat na vstupu stejné ... z jedné strany přiteče, z druhé strany zmizí)

## Základní cena
Pokud použijeme klasické řešení, tak na ingesting potřebujeme 20 GB denně, tedy 600 GB za měsíc. To stojí 600 x 2,682 EUR = 1609 EUR. V ceně je retence 30 dní, my potřebujeme 12 měsíců, tedy 11 měsíců musíme připlatit - ve dvanáctý měsíc máme tedy jeden měsíc pokrytý ingestingem a k tomu 11 x 600 GB retence navíc. To dělá 11 x 600 x 0,117 EUR = 772 EUR.

Celkem tedy 2381 EUR měsíčně.

Optimalizovaná varianta využije ingesting 10 GB denně do analytického tieru, tedy 300 GB měsíčně za 805 EUR. K tomu si přikoupíme 3 měsíce retence navíc (jeden je v ceně, tři potřebujeme, ať máme potřebné 4), což je 1200 GB x 0,117 EUR = 140 EUR. Dalších 8 měsíců pokryjeme archivem, tedy 8 x 300G GB x 0,024 EUR = 58 EUR.

Pro aplikační logy půjdeme do basic logs, což bude dělat 300 GB x 0,584 EUR = 175 EUR. Zanedbám teď to, že 8 dní retence je v ceně, takže k tomu přidáme 12 měsíců v archivu, tedy 12 x 300 GB x 0,024 EUR = 86 EUR.

Celkem tedy 1264 EUR.

## Vyhledávací úlohy
Pro srovnání musíme říci, že v klasickém případě (analytický tier a prodloužená retence) jsou všechny tyto úkony v ceně.

Na úkol 1 se pohybujeme v Basic logs a cena query záleží na množství dat, která scanujeme. Včerejší data = 1 den = 10 GB. Cena tedy bude 10 x 0,006 EUR, tedy 0,06 EUR. Pokud něco takového děláme 200x měsíčně, jsme na 12 EUR.

Úkol 2 vede na Search Job v archivu, kde budeme prohledávat 5 dní dat (50 GB), což je 50 x 0,006 EUR = 0,3 EUR. Výsledky se nám zapíšou do analytického tieru a výsledek dle zadání představuje 100 MB dat (zbytek jsou jiné aplikace, nekritické hlášky apod.), což nás na ingestingu bude stát 0,1 x 2,682 EUR = 0,27 EUR. Pokud tohle celé děláme 10x měsíčně, jsme na 2,7 EUR.

V úkolu 3 je problém v tom, že nevíme přesně co hledáme, takže nemáme nějaké velmi specifické query, které nám řekne co potřebujeme nebo takové query sice udělat umíme, ale vyžaduje analytické funkce (joiny, agregace). Mohli bychom to vyřešit tím, že uděláme generický Search Job, který vytáhne všechna data konkrétní aplikace (dle zadání to dělá 1 GB dat). To nás tedy bude stát scan 50 GB dat za 50 x 0,006 EUR = 0,3 EUR a ingesting 1 GB dat, tedy 2,682 EUR. Tato data pak máme v analytickém tieru, takže další jejich zkoumání už je zdarma. Pokud tohle udělám 5x měsíčně, bude to asi 15 EUR.

Čím je jiný úkol 4? Naše schopnost data filtrovat je tady ještě horší, protože search vrátí 50% všech dat. Při použití search bych dal zas 0,3 EUR za scanning, ale ingesting už mě bude stát 25 x 2,682 EUR = 67 EUR. Tedy už bude rozhodně lepší nic nefiltrovat a data raději zavlažit. To nás vyjde jen na 50 GB x 0,117 EUR = 5,9 EUR na jeden den, kdy to mohu analyzovat. Určitě lepší volba. Pokud to dělám 5x do měsíce, jsme na asi 30 EUR.

Co vybrat - Search Job nebo Restore? Pokud budu dělat Restore jen na jeden den (tedy jeden den investigace), tak se to vyplatí, pokud jsem si tedy rovnice a grafy správně nahodil, když očekáváte, že vám search vrátí víc jak 4% všech scanovaných dat.

[![](/images/2022/graf.png){:class="img-fluid"}](/images/2022/graf.png)

Celkem z úkony v mém modelovém případě musíme počítat 0 EUR pro klasické řešení a 60 EUR měsíčně pro optimalizované.




Nové funkce Log Analytics jsou myslím skvělá finanční zpráva pro Azure Monitor (aktuálně zejména logy z kontejnerů), Application Insights i Microsoft Sentinel. V příštím díle se do všech zmíněných funkcí pustíme prakticky.