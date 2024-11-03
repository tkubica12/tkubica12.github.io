---
layout: post
published: true
title: Datové hřiště - jak si hrát s daty bez sebemenšího kliknutí s Terraform a Azure
tags:
- Data Analytics
- Automatizace
- Databricks
- Data Factory
- SQL
---
Chci se vzdělat v datové oblasti a neznám lepší způsob než si všechno vyzkoušet. Jenže většinou jsem v příkladech nalezl hromadu klikání, skriptování a závislost na existujících datech a to se mi nelíbí. Chci 100% automatizovatelné opakovatelné hřiště zcela bez jakýchkoli závislostí - na spuštění Terraformu chci všechno od založení infrastruktury přes vygenerování syntetických dat k jejich přesouvání, spouštění Data Factory pipeline a Databricks Jobů, zpracování a snad i nějakou vizualizaci. Takovou tělocvičnu jsem nenašel, tak se ji pokusím vytvořit tady: [https://github.com/tkubica12/dataplayground](https://github.com/tkubica12/dataplayground).

# Datové hřiště
Moje základní požadavky:
- Nechci žádné klikání, skriptování ani nesourodé šablony (viz fakt, že Bicep neumí Databricks objekty) - celé řešení musí být jeden Terraform projekt od A do Z.
- Nechci žádné závislosti na něčem, co si musím přinést - například chci mít možnost mít poměrně hodně dat (říct si kolik jich chci) a odnikud je nestahovat.
- Prostředí nesmí mít nic proč ho nebudu chtít smazat, když ho potřebuji až za dva dny - tj. všechny změny budou prakticky ihned zanášeny do kódu a jediný důvod proč to nesmazat bude určitý čas co vybudování trvá (cílem je, aby do 20 minut všechny komponenty běžely, do 1 hodiny aby to mohlo být kompletně včetně zpracovaných dat při ručním triggeru pipeline a do 2 hodiny aby se všechno včetně zpracování orchestrovalo samo bez zásahu, takže 2 hodiny od spuštění máte výsledky aniž na to sáhnete)
- Náklady spuštěného řešení by měly být rozumné (skripty nebo nody co se nepoužívají ať se vypnou, SQL seškáluje na minimum apod.).

Tady jsou jednotlivé součástky a v dalších článcích se k nim vrátím podrobněji.

# Generování dat a datové zdroje
Chci mít data vypadající jako data - české texty, města apod., ale nechci mít závislost na jejich stažení odněkud, protože jejich objem chci mít velmi variabilní. Jdu tedy cestou generátoru s použitím Fake balíčku pro Python. Nicméně - tohle všechno samozřejmě také musí být automatizované. Kód jednotlivých generátorů jsem tedy zabalil do kontejnerového image a Terraform je spouští jako Azure Container Instances. Generátory sypou data do různých datových zdrojů - něco jde rovnou na Data Lake jako soubory (jeden jako jeden JSON lines soubor a druhý jako JSON soubor per produkt), něco do relačního Azure SQL jako tabulky a jedno běží jako nekonečný data stream do Event Hubu.

Tohle v době psaní článku už na mém GitHub najdete.

# ETL
Tady jsem použil jednak Capture funkci v Event Hubu ale paralelně (pro vyzkoušení) také Stream Analytics - oboje v této fázi jen zapisuje RAW eventy do Data Lake (jeden ve formátu Avro, druhý v Parquet). Data Factory má na starost jednak pravidelné sbírání dat ze SQL tabulek a jejich vyplivnutí jako Parquet do Data Lake a dále orchestruje Notebook v Databricks. Jeho úkolem je všechna RAW data v bronze tier Data Lake vzít a vytvořit z nich Delta tabulky, které budou fyzicky žít v jiném kontejneru (silver tier).

I tohle už je na mém GitHubu hotové.

# Zpracování
V době psaní článku mám zatím spíš jen základní představu, ale chystám se implementovat nějaké agregační procesy nad daty a jejich vyplivnutí do gold tieru Data Lake. Dále vzít nějaká data a připravit je pro ML, třeba udělat dummy sloupečky apod. Další věc je, že jsem schválně v pageviews generátoru nechal občas náhodně vynechávat některá data, ať máme tady ve zpracování co opravovat. Určitě budu i data obohacovat - tak například vzít timestamp a vypočítat z něj den v týdnu případně přes nějaký externí zdroj dat udělat flag jestli to bylo přes den nebo až po setmění (na základě informace o východu a západu slunce). Tohle všecho pro pomalou cestu, ale chtěl bych udělat i něco nad eventy (proto tam jsou). Nějaké obohacení a nějaký alert - jednak s využitím Stream Analytics ale na vyzkoušení i Spark Streaming.

# Vizualizace
Jasným kandidátem je PowerBI, ale v době psaní článku vůbec netuším jesli se mi s ním podaří dodržet princip totální automatizace - tak uvidíme. Rozhodně budou i Notebooky v Databricks s příklady query, obrázky a tak podobně a to jednak na vyzkoušení práce se SQL dotazy, tak i něco v Pythonu.

# ML
Generátory chrlí náhodná data, takže na ML se to opravdu nehodí, ale i tak budu chtít alespoň ten proces vyzkoušený. Jde o to jak napojím připravená data na ML v Databricks ale taky na workflow v Azure ML. Uvidíme - na ML jako takové bude lepší přinést reálná data, ale alespoň ten technický proces vyzkoušet určitě půjde.

Pokud chcete, pojďte do toho se mnou. První dvě části už mám hotové, klidně si na GitHub vyzkoušejte a v dalších článcích je popíšu podrobněji. A pak snad bude čas postoupit dál ke zpracování a vizualizaci.

Tak ještě jednou - zkuste, pokud vás napadne zlepšovák nebo chcete opravit chybu, ideálně Pull Request nebo písněte na LinkedIn.
[https://github.com/tkubica12/dataplayground](https://github.com/tkubica12/dataplayground)
