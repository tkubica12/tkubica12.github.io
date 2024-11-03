---
layout: post
published: true
title: Nová generace disků Premium SSD v2 v Azure - rychlejší, levnější, flexibilnější
tags:
- Storage
---
Do preview jde nová generace storage v Azure pro disky - Premium SSD v2. V čem je jiná, kolik stojí a jak si vede v porovnání se stávajími modely?

# Stávající varianty disků
Co v Azure najdete?
- **Standard HDD** je nejlevnější disk a kromě relativně vysoké latence typicky 2ms-5ms můžete očekávat i výkyvy a slabší vyšší percentily, kdy vám storage čas od času dá transakci v detítkách ms. Je to logické - jde o točivé médium a už to samo o sobě znamená, že občas musíte počkat něž vám čtecí hlava najede do správné polohy a plotna se dotočí na to místo, kde data jsou (jen fyzika otáčení vám dává 11ms u 5400 otáčkového disku a 6ms u 10000 RPM). Do toho přidáte efekty sítě, replikace a konkurentních přístupů a je to jasné.
- **Standard SSD** je levná SSD storage s dobře vyrovnaným základním výkonem. Na disk operačního systému nebo běžná použití typu aplikační servery je obvykle skvělou volbou.
- **Premium SSD** nabízí velmi stabilní výkon a latenci (pod 2ms) a u velkých disků se dostává na velmi vysoké IOPS a slušné propustnosti (MBps). Nejčastější storage pro databáze a náročnější, nikoli však extrémní, systémy. Výkonnostní parametry jsou svázané s velikostí - čím větší disk, tím více IOPS a MBps. Později se rigidnost postupně snižovala a záváděla se příjemná zlepšení:
  - Malé disky do 512 GB používají credit-based bursting v ceně, takže strop není fixní, ale občas si mohou sáhnout na víc.
  - Velké disky nad 512 GB mají možnost přikoupení on-demand burstingu, kdy za fixní příplatek (za zapnutí této vlastnosti) může disk dostat víc (až 30000 IOPS), za které ovšem zaplatíte transakční poplatky. Nicméně máte tak třeba 1TB, který má 5000 IOPS a víte, že párkrát za den si vezme 20000 IOPS a vaší aplikaci to prospěje - a protože je tak málo časté je to levnější, než si pořizovat větší výkonnější disk.
  - Každých 12 hodin můžete dynamicky změnit tier disku a přitom si nechat jeho původní velikost (= "zvětšit" disk, ale kapacitně ho ponechat, takže hp nepotřebujete odpojovat a zastavovat aplikaci). Funguje to v řádách do P50 a pak pro P60-P80. Koupíte si tedy například disk P20, který má 512 GB a 2300 IOPS a na pondělí, kdy máte špičku, ho změníte (připlatíte si) defacto na P30 s 5000 IOPS.
- **Ultra SSD** je velmi drahá varianta, ale s extrémními výkony - můžete z něj vytáhnout až 160 00 IOPS a 4000 MBps což je na vzdálenou plně redudnantní storage perfektní a navíc latenci tady obvykle naměřím jen 0.4ms, což je výborné. Příjemné je, že charakteristiky velikost, IOPS a propustnost jsou od sebe oddělené a můžete si tak koupit co potřebujete i to zaživa měnit - třeba malý disk s vysokým výkonem, disk optimalizovaný na propustnost (např. pro nějaké sekvenční masivní operace), IOPS (hromadu malinkatých paralelních transakcí) nebo nějakou vyváženou kombinaci. Tuhle storage použijete pro klasické velké databáze (Oracle, SQL, SAP), kde potřebujete brutální výkon, ale spolehlivost redundantní storage.
- Lokální storage sice nemá redundanci, ale má skvělý výkon a to zejména u L-series mašin, které obsahují NVMe storage karty s miliony IOPS a samozřejmě extrémně nízkou latencí. Pro dočasné zpracování dat (například výpočetní clustery s úlohami, které se nevejdou do paměti) nebo pro systémy, které si replikaci dat dokáží udělat samostatně mezi nody (shared-nothing architektura), je to skvělá volba.

Standard SSD a Premium SSD (ale ne Ultra SSD z důvodu výkonu) nabízí i zónovou redundanci (ZRS - replikaci přes 3 zóny dostupnosti, tedy řekněme datová centra) a všechny kromě Standard HDD i shared přístup (přes SCSI PR - například pro legacy shared-storage databáze, což je vlastnost, která u ostatních cloudů chybí, kde sice shared disk umí, ale to je bez IO Fencingu pro legacy appky obtížně použitelné).

# Premium SSD v2
Nová generace diskové storage přinese výborné výkony a flexibilitu, ale za přístupnou cenu. Jasně - Ultra SSD pořád zůstane o úroveň jinde, ale Premium SSD v2 je co do flexibility snad ještě lepší a při tom, jak uvidíme, stojí míň jak dnešní Premium SSD:
- Za velikost platíte podle vzorečku a můžete si vybrat jakoukoli od 1GB to 64TB, takže disk 131 GB je levnější, než disk 132 GB.
- IOPS máte v hodnotě 3000 v ceně storage, ale můžete si připlatit za víc a to až na úroveň 80 000 IOPS (takhle vysoko je minimální velikost disku 160 GB, ale to je pořád fajn).
- MBps máte v hodnotě 125 v ceně storage a připlácet lze až do 1200 MBps.
- Stejně jako u Ultra SSD můžete výkonnostní nastavení měnit bez restartu serveru, takže si můžete narychlit disky třeba pro víkendový load dat nebo pondělní špičku.
- Při testech jsem naměřil latenci krásných 0,7 ms tedy výrazně nižší, než u Premium SSD. Tohle bude hodně znát pro starší aplikace, které dělají blokující čtení (čekají na ACK za každou storage transakcí, tedy datlují to písmenko po písmenku), kde vám velké IOPS nijak nepomůžou (aplikace jich nedokáže využít, protože nepošle transakce v balíku a/nebo nevyužívá více vláken apod.).

# Jak to vychází cenově ve srovnání s ostatními typy?
Níže uvedené výpočty jsou moje - mohl jsem se splést, tak si to všechno raději přepočítejte!

Nejdřív jsem srovnal dva malé disky a naladil požadované IOPS a MBps, aby to sedlo na dnešní Premium SSD. Nová generace vychází nesmírně příjemně a ještě má v základu vyšší výkon. Tady nutno říct, že malé disky Premium SSD ale mají credit-based burst IOPS na podobných 3500 a propustnost 170 MBps. Jasně - není to garantované a je to jen na špičky, ale efektivně pokud nebudete mít nějakou velkou trvalou zátěž nebude v IOPS a MBps rozdíl mezi v1 a v2 příliš patrný. Ale v latenci ano a hlavně - v2 je levnější, takže nebude o čem.

[![](/images/2022/2022-10-04-10-41-57.png){:class="img-fluid"}](/images/2022/2022-10-04-10-41-57.png)

Co kdybych potřeboval stále docela malý disk, ale s větším výkonem? V klasickém Premium SSD budu muset sáhnout po větším disku (nebo použít víc malých, ale to zkusíme později) a to je ohromná cenová penalizace.

[![](/images/2022/2022-10-04-10-43-31.png){:class="img-fluid"}](/images/2022/2022-10-04-10-43-31.png)

Vraťme se k něčemu, co přesně kopíruje Premium SSD model P30. Pro něj rovněž platí cenová výhodnost nové generace.

[![](/images/2022/2022-10-04-10-44-33.png){:class="img-fluid"}](/images/2022/2022-10-04-10-44-33.png)

Jak by vypada varianta 4TB s už poměrně velkým výkonem? V případě Premium SSD bychom se dostali na ještě větší disk a byl by to finanční nesmysl, proto použijeme jinou taktiku a pořídíme dva menší disky, které v OS spojíme do stripu a rozložíme na ně zátěž. Je s tím tedy nějaká práce navíc a i tak je nová generace pořád výhodnější.

[![](/images/2022/2022-10-04-10-46-21.png){:class="img-fluid"}](/images/2022/2022-10-04-10-46-21.png)

Co zkusit nějaký extrém, třeba 32TB disk s velmi malým požadavkem na výkon? Tady jsem do srovnání přidal i Standard HDD. Ten vyjde samozřejmě o hodně levněji, než všechno ostatní, ale zajímavé je, že má Premium SSD v2 cenově o kousek blíž k Standard SSD, než k Premium SSD. Na ten ale můžete vzít cirka 5% slevu za roční rezervaci, čímž se v2 dostane zpět tak někam doprostřed. Možná vás ale napadne, že jasně, v zadání ten výkon není požadován, ale je příjemnější mít 20 000? Vzhledem k masivní velikosti disku je u Premium SSD v2 kapacita majoritní částí ceny - pokud vyrovnám výkon v2 s v1 tak by to stálo jen 3379 EUR (příplatek za IOPS a MBps nebude v ceně takhle velkého disku tak zásadní).

[![](/images/2022/2022-10-04-10-53-49.png){:class="img-fluid"}](/images/2022/2022-10-04-10-53-49.png)

A poslední extrém - naložíme Premium SSD v2 a Ultra SSD co snese. Ultra SSD skutečně nevychází nejlevněji, ale když potřebujete maximum... má dvojnásobné IOPS, poloviční latenci a víc jak třikrát lepší propustnost. 

[![](/images/2022/2022-10-04-11-00-38.png){:class="img-fluid"}](/images/2022/2022-10-04-11-00-38.png)

# Nezapomeňte na VM
Prorvat tolik storage provozu z VM do sítě není zas až tak jednoduché i když servery v Azure mají dnes běžně síťovky na rychlostech 40 nebo 100 Gbps (storage a datový provoz je konvergovaný) - jenže to je potřeba spravedlivě rozdělit mezi "nájemce", tedy VMka. Totéž platí pro celý storage subsystém hypervisoru. Jinak řečeno typ a velikost VM ovlivňuje maximální výkon do storage, takže koupit si super Azure Disk nestačí, limit může být ve VM.

Pokud například vezmete postarší D-series v3 a pořídíte malé VM s 2-core, tak do storage dostanete 3200 IOPS a 48 MBps. Bude potřeba jít na nejvyšší 64-core model, abyste vytáhli z Premium SSD v2 maximum (80000 IOPS a 1200 MBps). Pokud ale půjdete do compute v5, tak nám stačí 48-core model (76800 IOPS a 1315 MBps u Intelu a 1152 MBps u AMD). 

# Omezení v preview
Služba je v limitovaném preview, takže je tam celá řada omezení co do regionů a vlastností. Dá se předpokládat, že většina z nich zmizí s GA uvedením Premium SSD v2 a jen některé budou trvalejšího rázu. Umím si představit, že podobně jako u Ultra SSD, zůstane nějakou dobu nemožnost je použít jako OS disk a jsem zvědav jak to bude s podporou ZRS (u Ultra SSD to technologicky nejde a navíc by to nedávalo smysl platit takhle drahou storage a pak jí degradovat replikací mezi zónami, ale u Premium SSD v2?). A snapshoty a Azure Backup? Uvidíme, to se rozhodně hodí, ale jestli to bude už do GA?

# A jak v jiných cloudech?
V jiných cloudech se moc nevyznám, takže bez záruky - jde mi jen o nějaký základní přehled jaká je tam situace.

AWS má General Purpose SSD gp3 a co myslíte? Pricing model úplně stejný a stojí úplně stejně :) Pokud tomu ale správně rozumím, tak končí na 16000 IOPS na Volume (vs. 80000), maximální propustnost je podobná (1000 vs 1200 MBps) a maximální velikost je 16 TB (vs 64 TB v Azure). Je vidět, že to měli dřív a zpoždění u Azure je kompenzováno tím, že se to rovnou udělalo o něco lepší.

GCP podle všeho v této kategorii má pd-ssd a cenotvorba je zdá se daná pouze velikostí disku tedy modelově má blíž k Azure Premium SSD v1 a AWS gp2. Výkon per-GB ale roste poměrně rychle, ale s ním je i dost vysoká cena. Myslím, že proti Premium v2 a gp3 to bude finančně nutné optimalizovat rozhodováním mezi pd-ssd a pd-balanced - zkrátka uvidíme, jestli i GCP přenese flexibilitu nejvyššího modelu pd-extreme do střední třídy tak, jako to udělalo AWS a teď Azure.


Tolik tedy k diskům Premium SSD v2, na které se moc těším. Co vy?