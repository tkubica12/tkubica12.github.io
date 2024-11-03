---
layout: post
published: true
title: Nový Cold tier Azure Blob storage - kolik stojí premium, hot, cool, cold, archive
tags:
- Kubernetes
---
Azure před pár dny oznámil nový tier pro Blob storage - Cold. Z názvu je patrné, že by měl být ještě chladnější, než stávající Cool, ale stále to nebýt Archive. Co to znamená? Cena za uložená data je nižší, než u Cool (a samozřejmě než u Hot nebo Premium), ale přístup k nim je dražší a je tam delší minimální doba uložení. Na druhou stranu je to ale stále plně online úložiště - data jsou k dispozici okamžitě. To je zásadní rozdíl oproti Archive, kdy na data musíte nějakou dobu čekat (hodinu u high-priority doručení nebo 8 hodin u normálního).

Nebylo by zajímavé spočítat body zlomu, tedy při jakém použití se cena vyššího tieru rovná nižšímu? Přesně to se pokusím dnes udělat. Protože je to docela dost vzorců, napsal jsem si na to Python prográmek. Počítat to budeme pro 1TB dat (neberu tedy v úvahu, že cena se při obrovských objemech trochu snižuje slevou a je také možné udělat rezervaci - to budu ignorovat, protože nám dnes jde o poměry tierů a tyhle věci to kromě Premium nijak zásadně nemění). Další co ovlivňuje cenu je velikost bloku - obecně velikánské soubory budou mít veliké bloky a tím nižší cenu za transakce a malinkaté souborky jsou v tomto ohledu problematické. Soustředit se budu pouze na čtení, ne zápis a zajímá nás tedy kolik z těch 1TB musím přečíst, aby například tier hot stál stejně jako tier cool. Neberu v úvahu minimální uložení (cool musíte bez pokuty držet 30 dní, cold 90 dní a archive 180).

Ještě jeden předpoklad - počítat budu situaci, kdy tam data jsou a já je čtu, neřešíme tedy jejich zápis. 

```python
from sympy import symbols, solve

size_in_gb = 1000

premium_price_per_gb = 0.195
premium_price_10k_operations = 0.0019
premium_price_retrieval_per_gb = 0
hot_price_per_gb = 0.0196
hot_price_10k_operations = 0.0043
hot_price_retrieval_per_gb = 0
cool_price_per_gb = 0.01
cool_price_10k_operations = 0.01
cool_price_retrieval_per_gb = 0.01
cold_price_per_gb = 0.0045
cold_price_10k_operations = 0.1
cold_price_retrieval_per_gb = 0.03
archive_price_per_gb = 0.0018
archive_price_10k_operations = 6
archive_price_retrieval_per_gb = 0.024
archive_high_priority_price_per_gb = 0.0018
archive_high_priority_price_10k_operations = 65
archive_high_priority_price_retrieval_per_gb = 0.13

reads_per_month_gb = symbols('reads_per_month_gb', positive=True)

blocks_per_gb = [1, 10, 1000, 100000, 1000000]  # 1GB, 100MB, 1MB, 10KB, 1KB
premium_hot = []
hot_cool = []
cold_cool = []
archive_cold = []
archive_cool = []
archivehp_cold = []

for block_per_gb in blocks_per_gb:
    premium_price = premium_price_per_gb * size_in_gb + premium_price_10k_operations * reads_per_month_gb * block_per_gb / 10000 + premium_price_retrieval_per_gb * reads_per_month_gb
    hot_price = hot_price_per_gb * size_in_gb + hot_price_10k_operations * reads_per_month_gb * block_per_gb / 10000 + hot_price_retrieval_per_gb * reads_per_month_gb
    cool_price = cool_price_per_gb * size_in_gb + cool_price_10k_operations * reads_per_month_gb * block_per_gb / 10000 + cool_price_retrieval_per_gb * reads_per_month_gb
    cold_price = cold_price_per_gb * size_in_gb + cold_price_10k_operations * reads_per_month_gb * block_per_gb / 10000 + cold_price_retrieval_per_gb * reads_per_month_gb
    archive_price = archive_price_per_gb * size_in_gb + archive_price_10k_operations * reads_per_month_gb * block_per_gb / 10000 + archive_price_retrieval_per_gb * reads_per_month_gb
    archive_high_priority_price = archive_high_priority_price_per_gb * size_in_gb + archive_high_priority_price_10k_operations * reads_per_month_gb * block_per_gb / 10000 + archive_high_priority_price_retrieval_per_gb * reads_per_month_gb
    premium_hot.append(solve(premium_price - hot_price))
    hot_cool.append(solve(hot_price - cool_price))
    cold_cool.append(solve(cool_price - cold_price))
    archive_cold.append(solve(archive_price - cold_price))
    archive_cool.append(solve(archive_price - cool_price))
    archivehp_cold.append(solve(archive_high_priority_price - cold_price))

for block_per_gb in blocks_per_gb:
    # break even points
    premium_hot_even = round(premium_hot[blocks_per_gb.index(block_per_gb)][0])
    hot_cool_even = round(hot_cool[blocks_per_gb.index(block_per_gb)][0])
    cold_cool_even = round(cold_cool[blocks_per_gb.index(block_per_gb)][0],1)
    if archive_cold[blocks_per_gb.index(block_per_gb)]:
        archive_cold_even = round(archive_cold[blocks_per_gb.index(block_per_gb)][0], 5)
    else:
        archive_cold_even = 0
    archivehp_cold_even = round(archivehp_cold[blocks_per_gb.index(block_per_gb)][0], 5)
    # prices
    premium_hot_even_price = round(premium_price_per_gb * size_in_gb + premium_price_10k_operations * premium_hot_even * block_per_gb / 10000 + premium_price_retrieval_per_gb * premium_hot_even, 1)
    hot_cool_even_price = round(hot_price_per_gb * size_in_gb + hot_price_10k_operations * hot_cool_even * block_per_gb / 10000 + hot_price_retrieval_per_gb * hot_cool_even, 1)
    cold_cool_even_price = round(cool_price_per_gb * size_in_gb + cool_price_10k_operations * cold_cool_even * block_per_gb / 10000 + cool_price_retrieval_per_gb * cold_cool_even, 1)
    archive_cold_even_price = round(archive_price_per_gb * size_in_gb + archive_price_10k_operations * archive_cold_even * block_per_gb / 10000 + archive_price_retrieval_per_gb * archive_cold_even, 1)
    archivehp_cold_even_price = round(archive_high_priority_price_per_gb * size_in_gb + archive_high_priority_price_10k_operations * archivehp_cold_even * block_per_gb / 10000 + archive_high_priority_price_retrieval_per_gb * archivehp_cold_even, 1)
    print('Block size: {} MB'.format(1 / block_per_gb*1000))
    print('----------------------------------------')
    print(f'Premium-Hot: {premium_hot_even} GB for ${premium_hot_even_price} USD')
    print(f'Hot-Cool: {hot_cool_even} GB for ${hot_cool_even_price} USD')
    print(f'Cold-Cool: {cold_cool_even} GB for ${cold_cool_even_price} USD')
    print(f'Archive-Cold: {archive_cold_even} GB for ${archive_cold_even_price} USD')
    print(f'ArchiveHP-Cold: {archivehp_cold_even} GB for ${archivehp_cold_even_price} USD')
    print()
    print()
```

Tady jsou výsledky:

```
Block size: 1000.0 MB
----------------------------------------
Premium-Hot: 730833333 GB for $333.9 USD
Hot-Cool: 960 GB for $19.6 USD
Cold-Cool: 274.9 GB for $12.7 USD
Archive-Cold: 0 GB for $1.8 USD
ArchiveHP-Cold: 25.35449 GB for $5.3 USD


Block size: 100.0 MB
----------------------------------------
Premium-Hot: 73083333 GB for $333.9 USD
Hot-Cool: 959 GB for $19.6 USD
Cold-Cool: 273.8 GB for $12.7 USD
Archive-Cold: 0 GB for $1.8 USD
ArchiveHP-Cold: 16.37356 GB for $5.00000000000000 USD


Block size: 1.0 MB
----------------------------------------
Premium-Hot: 730833 GB for $333.9 USD
Hot-Cool: 908 GB for $20.0000000000000 USD
Cold-Cool: 189.7 GB for $12.1 USD
Archive-Cold: 4.62329 GB for $4.7 USD
ArchiveHP-Cold: 0.40971 GB for $4.5 USD


Block size: 0.01 MB
----------------------------------------
Premium-Hot: 7308 GB for $333.9 USD
Hot-Cool: 143 GB for $25.7 USD
Cold-Cool: 6.00000000000000 GB for $10.7 USD
Archive-Cold: 0.04577 GB for $4.5 USD
ArchiveHP-Cold: 0.00416 GB for $4.5 USD


Block size: 0.001 MB
----------------------------------------
Premium-Hot: 731 GB for $333.9 USD
Hot-Cool: 17 GB for $26.9 USD
Cold-Cool: 0.6 GB for $10.6 USD
Archive-Cold: 0.00458 GB for $4.5 USD
ArchiveHP-Cold: 0.00042 GB for $4.5 USD
```

Pojďme si to okomentovat. Začněme analýzu v situaci, kdy tady máme veliké bloky o délce 1 GB. To bude snižovat množství transakcí, takže výhody teplejších tierů v jejich nižší ceně transakcí nebudou tak znát. Proto se Premium tier srovná až při šílených 730 PB přečtených dat měsíčně (ten 1 TB uložených dat byste museli přečíst 730 000 krát). Co rozdíl mezi Hot a Cool? Vyšší cena Hot tieru, ale na druhou stranu nulový poplatek za přečtená data a levné transakce znamenají, že se pro náročné čtenáře může vyplatit. Je tomu tak od 960GB přečtených dat měsíčně. Pokud tedy 1 TB uložené storage za měsíc celý přečtu, už se mi Hot vyplatil. Pokud je to pod 960GB, tak bude levnější Cool. Jak je na tom nový tier Cold? Nezapomeňte, že data tam musím nechat 90 dní (abych nedostal pokutu), ale jsou mi online dostupná. Bod zlomu mezi Cool a Cold je 274,9 GB. Zjednodušeně řečeno pokud tedy přečtu méně jak čtvrtinu uložených dat, pak bude Cold tier dobrá volba. Zajímavé je, že pro velké bloky bude Archive vždy levnější - nicméně je to jiná kategorie, offline médium. Pokud bych ale chtěl rychlejší vybavování z archive (high-priority), tak je poplatek docela velký, takže přes 25GB přečtených z 1TB měsíčně už bude levnější Cold.

To jsme ale měli velké bloky - ideální situace pro backup soubory zálohovacích řešení nebo nějaké exporty z databáze (mimochodem schválně nepíšu video soubory, protože tam je to komplikovanější - pokud se neservírují z CDN ale nasává se to ze storage, tak velké bloky jsou fajn, ale často zpomalují načítání jak na začátku tak při přeskakování v rámci přehrávače, ale pokud je to na zpracování nebo zálohu, velké bloky jsou optimální). Jak se situace změní, když budou bloky 1MB - tedy budeme v rozměrech řádově běžných třeba pro obrázky, PDF dokumenty a tak podobně? Menší bloky vygenerují 1000x víc transakcí, ale cena za uložení i vybavení dat se nemění. To způsobilo, že Premium by se vyplatilo "už" při 730 TB přečtených dat měsíčně (tzn. mám uloženo 1 TB, ale každou hodinu si to celé přečtu). Bod zlomu Hot a Cool to neovlivnilo nijak zásadně (908 GB vs. 960 GB u obřích bloků), u Cool a Cold už trochu výrazněji (189,7 GB vs. 274,9 GB). Archive už ale krvácí na poplatcích a pokud za měsíc přečtu víc jak 4,6 GB dat z 1 TB uložených, tak už je levnější to nechat v Cold (a mám data ihned, nemusím na nic čekat). Pokud si ještě připlácím za rychlé vybavení dat, tak je to jen 0,4 GB, tedy pod jedno promile.

A co bloky 10KB, typické pro malé JSON a CSV soubory v některých datařských úlohách nebo různé ikonky apod.? Premium už se vyplatí u 7,3 TB přečtení z 1 TB dat. Všimněte si, že hranice výhodnost Cool i Cold se posunula hodně dolu a Archive vs. Cold už je prakticky nesmysl. 10KB soubory evidentně do Archive nepatří, pokud jich objemově budete číst víc.

Pojďme na extrém - 1KB soubory, což mohou být typicky exporty nějakých datových zpráv třeba z IoT zařízení do JSON nebo AVRO souborů per zpráva. Takhle malé bloky znamenají, že se vám zdánlivě drahé Premium vyplatí už při přečtení 731 GB z 1 TB uložených - tedy hodně brzo. Studené tiery jsou pravděpodobně nesmysl - Cool je drahý už při 17 GB z 1 TB nemluvě o Cold nebo Archive, které jsou zcela mimo. Mimochodem pokud v těchto úlohách půjde daleko víc o zápisy tak vězte, že poměr Premium vs. Standard Hot je sice stejný (Premium je 2x levnější), ale poměr ceny transakce k ceně uložení je u obou o řád posunutý. Jinak řečeno při miliardách zápisů bude hlavním faktorem ceny řešení nikoli cena uložení (která je u Premium o řád vyšší), ale cena zapisovacích transakcí (která je u Premium poloviční). Jestli je tedy hlavním smyslem storage posbírat malinkaté souborky za účelem jejich zpracování do agregátů a pak už je v tomhle stavu netřeba (= relativně málo uložených dat vs. relativně hodně transakcí), bude nejlepší zvolit Premium.

Co nám tohle všechno říká?
- Teplejší tiery jsou pro situace, kdy hodně přistupujete nebo když se jedná o malé souborky. Pokud jste si například lámali hlavu k čemu je dobrý tier Premium, když je o tolik dražší a z pohledu propustnosti jen asi 2-3x lepší, tak má jednak daleko nižší latence, ale hlavně při obrovském množství transakcí dost ušetříte - storage pod data z Kafky nebo pod Databricks Delta Live Tables může být typický příklad.
- Chladnější tiery mají rády spíše velké soubory. Pokud mám data v malinkatých, tak bych si měl spočítat, jestli je levnější je prostě nechat propadnout tak jak jsou do nižších tierů nebo bude lepší konsolidace do nějakého zipu, taru apod. To strašně záleží na režimu čtení. Když potřebujete z archivu vytáhnout ten jeden 1 KB soubor, tak je to pořád dobrý nápad (protože se platí i vybavený objem a ten je malý). Když ale budete vytahávat celý pondělní provoz, tak můžete na minitransakcích dost prodělat. 
- Nový Cold tier vnímám jako velmi příjemnou novinku, protože z pohledu uživatelské aplikace je rozdíl mít data okamžitě dostupná vs. programovat logiku, kdy je uživatel vyžádá a pak se na ně nějakou hodinu čeká a dá se mu vědět. Přestože archiv smluv vypadá jako "archiv", tak z těchto aplikačních důvodů bych asi raději online uložení, ale data starší jak pár měsíců mají poměr čtení třeba naprosto zanedbatelný. Cold pak bude výrazně levnější, než Cool (asi na polovinu) a přitom nevznikají nepříjemnosti offline obsluhy.
- A co zápisy? Ty jsem dnes neřešil, ale zmiňme dva aspekty:
  - Zapisovací transakce jsou o dost dražší, než čtecí - pokud tedy malé soubory nevyhovují chladnějším tierům, tak pro zápis to platí ještě víc. Při započtení zápisů se tak hranice výhodnosti mezi tiery bude u malých bloků posouvat k teplejším variantám.
  - Write operace zahrnují jak vytvoření blobu tak změnu jeho tieru (přesunutí do chladnějšího) a ceny mezi hot, cool a cold jsou vždy téměř dvojnásobek předchozího. Pokud se rozhodnete zapisovat rovnou do Cool vs. zapsat do Hot a hned přesunout do Cool tak to vyjde dost podobně. Jinak řečeno granulárního tierování z Hot do Coold a pak do Cold a/nebo archive bych nebál - jen dodržujte minimální dobu uložení a neochlazujte data předčasně, ať nerostou vybavovací náklady.
- Nezapomínejte, že tiery Cool a Cold mají horší SLA dostupnosti (ale nikoli durability - ta je stejná), takže pokud na úložišti stojí funkčnost důležité aplikace, tyhle tiery tam nepatří. 