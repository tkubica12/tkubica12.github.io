---
layout: post
title: 'Kusto: úvod do Azure jazyka pro práci s logy, telemetrií nebo IoT nejen v rámci Azure Monitor'
tags:
- Kusto
- Monitoring
---
Kusto Query Language je velmi mocný jazyk pro vyhledávání v datech, která jsou strukturovaná, ale s rozmanitými atributy, měnící se strukturou, obsahující vnořené objekty či texty, časové řady a tak podobně. Proto se ideálně hodí pro logy, telemetrii, data z IoT nebo roztodivné kolekce objektů, které mají mezi sebou dost odlišnou strukturu. Na co je ideální? Jaké formy a použití v Azure má? A jak ho srovnat s CosmosDB (a jinými NoSQL) nebo Spark?

# KQL - analytický pohled na data s proměnlivou strukturou
Platforma Kusto se zaměřuje na data s proměnlivou strukturou a velký objem, ale klíčovou vlastností je, že se soustředí na interaktivní analytickou práci. V tom se odlišuje od jiných řešení. Pojďme si to trochu srovnat.

## CosmosDB (NoSQL)
Kusto má s CosmosDB společné zaměření na data s roztodivnou strukturou včetně vnořených objektů, proměnlivých struktur, časových řad a velkých objemů. CosmosDB se ale primárně stará o schopnost data uložit a provádět v nich základní vyhledávání, má různé modely konzistence a SLA na zápis i čtení v řádech milisekund, ale není to analytická platforma. Všechny atributy jsou indexované a připravené pro exact match, range dotazy nebo graph indexy a na to je CosmosDB rozhodně skvělá. Jakmile ale začnete od NoSQL chtít pokročilejší analýzu, výkon jde dolu (což v cloudu znamená, že zaplatíte víc, pokud to chcete zvládat). Už například vytváření agregací ze skupin záznamů (ekvivalent GROUP BY v SQL) má nemalou spotřebu zdrojů natož pak kombinace s JOIN, regex search, ML funkce typu autobasket nebo detekce anomálií či cross-table query (některé ze zmíněných funkcí ani udělat nemůžete). První rozdíl - CosmosDB není analytický systém, je optimalizovaná na brutálně rychlé uložení a přečtení.

Druhý rozdíl je v API. V naprosté většině případů bude uživatel pracovat s nějakou aplikací napsanou nad CosmosDB a nebude zadávat přímé dotazy. SQL nebo CQL (Cassandra) je docela dobře pochopitelná, ale například mocnější data pipes v MongoDB protokolu nejsou pro nedatové lidi jako je operations nebo security zrovna příjemné. CosmosDB tedy není primárně zaměřeno na interaktivní dotazy přímo od uživatelů, například bezpečáků hledajících patterny útočníka.

## SQL
Kusto má se SQL společné velmi mocné vlastnosti v oblasti analytiky často včetně parsování v okamžiku query, machine learning operace nebo složité joiny. Nicméně SQL je řešení pro strukturovaná data s relativně pevným schématem a rozumné objemy. Pokud řešíte tuny záznamů s roztodivnou strukturou (třeba logy z různých systémů) nebo velké množství counterů a časových řad (telemetrie, IoT), SQL není ideální řešení.

## Spark a jiné analytické platformy
Velká data a analytika - to zní jako úkol pro Spark a další udělátka v rámci Azure Databricks. Nicméně oproti Kusto tu jsou zásadní rozdíly. Tím asi nejdůležitějším je míra interaktivnosti. Typicky chcete v Databricks data zpracovávat v dávkách a hledat v nich nějaké zajímavosti podle předem připravených algoritmů, zatímco Kusto je zaměřeno na interakci. U něj chcete sednout a spustit query právě teď a očekáváte výsledek během pár vteřin. Dotaz chcete interaktivně modifikovat nebo ho rovnou napsat z hlavy. Kusto jazyk je na to dělaný a nemusíte být datový analytik na pochopení jeho fungování a úspěšnou formulaci dotazu. Sparku nerozumím, ale co jsem pochytil, tak dost se toho dělá v Java/Scala a tak podobně - nic ideálního pro člověka z provozu nebo security.

## Kusto Query Language a jeho vlastnosti
Teď už asi můžeme shrnout na co tedy KQL cílí. Jsou to analytické operace v téměr reálném čase s interaktivním přístupem nad velkým množstvím roztodivně strukturovaných dat. Logy, telemetrie nebo IoT jsou určitě dobrým příkladem.

# Kde Kusto v Azure najdete
Kusto Query Language a příslušný engine najdete v Azure na několika místech.

## Azure Resource Explorer
Jste velký zákazník Azure? Pak máte hromadu subskripcí, ještě větší nášup resource group a obrovské množství zdrojů. Každý má pár společných atributů (název, region, tagy), ale spoustu specifických (VM má size, SQL má SKU apod.). Kolik mám VM podle jejich velikostí za jednotlivé subskripce? Nebo počet VM podle tagu environment či owner přes všechny subskripce? A co takhle jaké VM mají jen Premium disky a splňují tak podmínky pro single-instance VM SLA?

Jak vidíte samotné zdroje v Azure tak vlastně mohou být kandidát na analytickou interaktivní platformu. Právě proto Azure Resource Explorer má pod kapotou Kusto a v příštích dílech si ho vyzkoušíme.

## Azure Monitor
Kusto začalo jako platforma pro analýzu logů a telemetrie pro interní support týmy Azure. Dokážete si představit kolik logů ze svého vnitřního fungování musí Azure denně vygenerovat? Support potřeboval platformu, v které to všechno bude a dokáží interaktivně hledat a korelovat události z různých systémů podle toho, co se zákazníkem řeší. Tento náročný úkol vedl ke vzniku Kusto. Výsledek byl skvělý a proto se před několika lety začala tato platforma nabízet i pro logy a telemetrii přímo zákazníků. Nejdřív to byl Application Insights pro aplikační logy a později na tento engine přešel celý Azure Monitor. Vaše infrastrukturní, bezpečnostní a aplikační logy i telemetrii tak můžete sbírat do Kusto. Na to se v sérii článků také podíváme.

## Azure Sentinel
Kusto je tak mocné, že můžete implementovat v reálném čase velmi sofistikované dotazy korelující různé informační zdroje, analyzující anomálie a časové řady a odhalující určité patterny chování nebo podezřelé stavy. Tohle je hodně důležité pro bezpečnost a systémy typu SIEM. Azure Sentinel, SIEM zrozený v cloudu, využívá přesně toho. Sentinel je tedy v zásadě GUI a soubor velkého množství připravených KQL dotazů nad Kusto, do kterého se ukládají auditní a bezpečnostní logy z různých systémů v cloudu i mimo něj. Kusto umožnilo vznik Azure Sentinel.

## Azure Data Explorer
Ve všech předchozích případech je Kusto pod kapotou těchto řešení jako služba. Platíte podle objemu dat a Microsoft se stará o škálování clusterů a všechny další potřebné věci. Platforma je ale pro vás možná zajímavá i pro vaše vlastní data, například datové proudy z IoT. Azure Data Explorer umožňuje získat Kusto jako takové a plnit si ho jak chcete a čím chcete.

# Základ jazyka
Dnes už nebudeme zkoušet nějaká reálná query, to si necháme na příště. Pojďme ale projít základní koncept.

Začínáme specifikací tabulky. To nám vrátí všechno co v ní je.

Pak použijete symbol pipe a pokračujete dál. Myšlenkově tedy vezmete zdrojová data a pošlete je pipou na další zpracování. Uděláme co potřebujeme a přes další pipe zpracováváme dál. Může to vypadat třeba nějak takhle:

```
Tabulka
 | project /vybereme jen nějaké sloupečky/
 | where /odfiltrujeme podle obsahu/
 | extend /přidáme další vypočítané sloupečky/
 | summarize /seskupíme data a spočítáme agregace/
 | where /výsledek znova přefiltrujeme/
 | join (jinaTabulka   /provedeme join na jinou tabulku/
        | where ) on id  /s jejím vlastním query a join přes atribut id/
 | sort /výsledek setřídíme/
 | limit /odřízneme třeba 20 nejhorších výsledků/
```

Kromě základních možností můžeme zařadit machine learning (autocluster, basket, diffpatterns), časové řady (třeba make_series), geospatial funkce a velkou spoustu dalších operací.


To pro dnešek stačí. Přístě se vrhneme do reálných příkladů a začneme s Azure Resource Explorer.