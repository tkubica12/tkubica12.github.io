---
layout: post
published: true
title: Jak si vybrat souborové úložiště v Azure
tags:
- Storage
---
Kdy použít Azure Files a v jakém tieru? Kdy raději Azure NetApp Files? A jde Blob storage napojit do operačního systému jako volume? A kdy vlastně použít souborové řešení vs. alternativy?

# Perzsitentní data v Azure
Pojďme připomenout základní kategorie a jejich aspekty:
- **Blokové RAW** zařízení jako je Azure Disk - velmi univerzální, velmi nízkoúrovňové. Některá historická negativa dnes už neplatí - například ZRS disky činí disk zónově redundantním, shared disky nabízí single-write multi-read třeba pro clustery se sdílenou storage a snapshoty disků lze dnes replikovat do jiného regionu. Úžasný pokrok v poslední době.
- **POSIX-compliant souborové systémy** jako jsou Azure Files nebo Azure NetApp Files. Obvyklá pozitiva jsou možnost sdílení na víc systémů včetně multi-write, transparentnost, možnosti redundance, kompatibilita i s mnoha let starými aplikacemi.
- **Scale-out append-optimized objektové úložiště** typu Blob storage nebo souborově přistupované, ale ne POSIX compliant. Určitě standard pro masivní škálování, výbornou cenu a data lake situace. Kompatibilita se starou aplikací relativně mizerná.
- **Strukturovanější úložiště na bázi záznamů** ať už jsou to tradiční relační databáze nebo NoSQL svět s různými formami optimalizací (na transakce, na analytiku se sloupcovou orientací, na append only a ad-hoc analytiku, na flexibilní schéma a masivní škálu s agresivní partitioningem apod.). Pod kapotou samozřejmě mají něco z předešlých variant, ale když je to jako služba, můžeme se soustředit jen na tuhle vrstvu.
- **Zprávy a proudové zpracování** obvykle postavené na jednoduchém (a proto velmi výkoném a škálovatelném) append log-based přístupu (Kafka, Event Hub) nebo na nějaké formě chytrého zpracování (více funkcí typu exactly once delivery na úkor škálovatelnosti) typu AMQP, JMS, Service Bus.

Dnes se chci podívat na charakteristiky těch, co podporují souborový přístup a otestovat jejich výkonnostní parametry.

# Soutěžící
Představme si, kdo do zápasu nastupuje. Později budeme srovnávat výkon a cenu, ale rozdílů je pochopitelně víc a často jsou níže zmíněné vlastnosti důležitější, než výkon a cena.

- **Azure Files** jsou nativní volbou, která škáluje od 0 (můžu si koupit hrozně málo). Ve variantě standard (HDD pod kapotou) platím podle toho jak se mi to zaplňuje a vybírám z různě cenově odstupňovaných variant (nejdražší transaction optimized, pak hot a levnou cool). Ve variantě premium (SSD pod kapotou) platím za provisionovanou kapacitu a čím víc si vezmu, tím větší dostanu výkon. Azure Files historicky byly jen o SMB, ale dnes podporují NFS 4.1 (dobrá zpráva pro Linux, kde SMB implementace - CIFS - má dost limitů). Síla Azure Files je v podpoře ACL a propojení s Windows světem, AD/AAD, možností sychronizovat či tierovat Windows share v on-prem do cloudu (Azure Files Sync), plně POSIX compliant operace nebo velmi vysoká úroveň zabezpečení SMBv3. LRS/ZRS SLA je 99,9%, pokud potřebujete víc, pak jen geo-replikace s GRS a 99,99% - nicméně premium tier zatím GRS neumí.
- **Azure Blob a Data Lake Gen2** je klasické scale-out objektové řešení. Bloby mají schopnost servírovat obsah rovnou klientovi přes https (například video stream), mají různé tiery od premium až po off-line archiv, různé formy redundance od místní repliky (LRS) k zónové i regionální redundanci (ZRS, GRS, RA-GRS, RA-GZRS), podporují vychytávky jako je replikace objektů, automatický tiering dle vašich pravidel nebo immutable storage (WORM) pro garantovanou nezměnitelnost a nesmazatelnost, auditní logy. Dají se použít i jako web server pro statický obsah a mají pěkná SDK pro aplikační integraci (například jeden z patternů je, že webová aplikace může umožnit uživateli nahrát soubor přímo do storage, ne přes webový backend). Nadstavbou nad klasickým blobem je hierarchický souborový systém, který umožňuje hierarchicky řídit práva (adresáře a tak) nebo promítnout storage jako vzdálený souborový systém (HDFS, NFSv3 - ale možnosti ověřování jsou u NFS implementace prakticky nulové, takže se aktuálně musíte spolehnout na síťovou izolaci). Tento režim nemusí ještě podporovat všechny vlastnosti blobů, ale to se rychle přidává. Škálování je enormní - jeden storage account pojme v základu 60 Gbps ingress a 120 Gbps egress (čtení), 5PB kapacity a všechny tyto hodnoty support umí navýšit. Navíc storage accountů můžete mít v subskripci 250 per region ... a počet subskripcí, které můžete vytvořit, není omezen. Maximální velikost jediného blobu (souboru) je šílených 190 TB. LRS/ZRS SLA je 99,9%, pokud potřebujete víc, pak jen geo-replikace s GRS a 99,99% - nicméně premium tier zatím GRS neumí.
- **Azure NetApp Files** je hardwarové řešení připravené ve spolupráci s firmou NetApp, jedním z lídrů na poli Network Attached Storage. Obě předchozí varianty jsou softwarově definovaná řešení běžící nad běžnou infrastrukturou, což jim dává výbornou škálovatelnost i cenu. Tady ale jde o specializovaný hardware, řešení navržené od základu pro tento účel, takže bude fér očekávat, že výkonnostní charakteristiky budou skvělé, ale možná to bude dražší a škálovatelnost jistě nebude tak nekonečná jako u Blobů. Pohybuje se v řádu desítek TB na zařízení což je o několik řádů méně, než scale-out řešení blobů. NetApp Files nepodporují zónovou redundanci, ale i přesto nabízí 99,99% SLA (o řád víc než LRS i ZRS ostatních variant). Geo-replikaci podporují, byť s horším RPO než GRS varianty nativních řešení.

Po funkční stránce tedy například pro nejlevnější archiv použijete blob, pro immutable storage taky blob, pro plnohodnotný file system Azure Files nebo Azure NetApp Files, pro maximální škálu bloby, pro integraci s on-prem Windows světem Azure Files. A co výkon a náklady?

# Výkon a náklady
Provedl jsem pár testů - rozhodně nejsem storage specialista, takže je prosím nepovažujte za něco oficiálního nebo přesného. Šlo mi spíše o řády, o základní představu, abych měl potřebné podklady pro architektonická rozhodnutí - cílem není ladit výkon.

Kompletní sadu testů a jak je replikovat najdete v [repozitáři](https://github.com/tkubica12/azure-remote-fs-perf-test).

Souhrnné výsledky jsou zjednodušené tady: [results.xlsx](https://github.com/tkubica12/azure-remote-fs-perf-test/blob/master/results.xlsx?raw=true).

Pro cenovou diskusi je důležité následující:
- Standard tiery Azure Files a Azure Blob se účtují čistě podle obsazeného prostoru. To je ideální a cenově velmi efektivní.
- Premium tiery Azure Files a Azure Blob se účtují podle provisionované kapacity bez ohledu na to, kolik dat reálně zaplníte. To je dané tím, že výkon SSD disků je pro vás alokovaný a čím větší prostor alokujete, tím větší máte výkon (často tedy můžete potřebovat koupit větší kapacitu ne kvůli prostoru, ale většímu výkonu). Nicméně není zde nějaká minimální kapacita, takže cena škáluje víceméně od nuly.
- Azure NetApp Files se platí také dle provisionované kapacity, ale minimální kapacita jsou 4TB. Bednu prostě nelze řezat na nekonečné množství bedniček. Pokud potřebujete málo prostoru, může to být nepříjemné. Na druhou stranu není to volume, ale pool, který je minimálně 4TB. Měli byste tedy být schopni bezpečně pool sdílet třeba i s jinou aplikací a náklady rozložit. 

Cenová srovnání jsem stavěl na 4TB kapacitě a v případě Azure Files Standard jsem počítal Transactio Optimized (ne Hot nebo Cool, které jsou o dost levnější). Pro zajímavost na posledním řádku je malý Azure Files Premium. Obecně vzato pro malé file share je tu zkrátka efekt toho, že u NetApp Files se méně jak 4TB koupit nedá.

Nejdřív jsem přes smallfiles utilitku zkusil výkonnost metadata operací - vytváření velkého množství malinkatých souborů. Všimněte si, že tady NetApp brutálně exceluje.

[![](/images/2021/2021-11-03-10-16-33.png){:class="img-fluid"}](/images/2021/2021-11-03-10-16-33.png)

Dál jsem zkusil přes smallfiles vytvářet nové, ale velké soubory, což by mělo být hlavně o propustnosti. Všimněte si, že standardní Blob nabízí velmi dobrý výkon, což vzhledem k jeho ceně dává o řád lepší cenovou efektivitu. Malé Azure Files se ale příliš nezpomalí, takže pro malé share budou rovněž výhodné. NetApp je na tom výkonnostně skvěle, ale ne zas o tolik, takže cena za propustnost je tam vysoká.

[![](/images/2021/2021-11-03-10-18-01.png){:class="img-fluid"}](/images/2021/2021-11-03-10-18-01.png)

Další test je čtecí a zapisovací latence. Je tu jedna anomálie u zápisu na blob - použitý test (fio) totiž dělal update, nikoli nový soubor. To je obrovský problém pro blob, jehož technologie pod kapotou je append only, takže operace update jsou nesmírně neefektivní. Proto databázový soubor na blob prostě dát nemůžete. Z čísel je vidět, že premium verze jak blobů tak Azure Files nabízí lepší a hlavně vyrovnanější latenci, než standard. Nicméně totálním šampionem jsou NetApp Files - latence méně jak 1 ms je úžasná - považte, že ve srovnání s Azure diskem je to nejblíže k diskům UltraSSD, i PremiumSSD je pomalejší. Pro databáze nebo cokoli co vyžaduje nízkou latenci je NetApp jiná liga.

[![](/images/2021/2021-11-03-10-20-44.png){:class="img-fluid"}](/images/2021/2021-11-03-10-20-44.png)

Poslední parametr, co jsem chtěl otestovat, byly čtecí a zapisovací IOPS. Z čísel je vidět, že pokud vám jde o velké IOPSy, nemá NetApp konkurenci a výkon je tak vysoký, že přepočet na cenu vychází také skvěle (mám za to, že u Ultra tieru jsem narazil na limit jinde, než ve storage - technicky vzato by IOPS mohl být až dvojnásobek varianty Premium). V této metrice je také zřetelné, že malý Azure Files Premium share (100GB) vs. velký share (4TB) dělá velký rozdíl. Ještě musím říct, že Azure Files Premium čísla vychází z trvalejší zátěže - pro krátké okamžiky je k dispozici burst skoro na trojnásobek .

[![](/images/2021/2021-11-03-10-24-16.png){:class="img-fluid"}](/images/2021/2021-11-03-10-24-16.png)



Na závěr tedy připomínka - bez znalosti potřeb workloadu se těžko vybírá. Streamování videa udělá skvěle blob, ale jako úložiště pro databázi by byl katastrofou. NetApp má geniální výkon, ale jeho použití pro archivaci je úplný nesmysl jak co do ceny tak kapacity, tam patří blob nebo alespoň Azure Files v cool tieru. Pokud potřebuji malý share, Azure Files budou cenově efektivní cesta. Často se lidé rozhodují podle IOPS nebo propustnosti i když jejich aplikace je ve skutečnosti citlivá na latenci (špatně paralelizuje, takže vysoké IOPS nebo propustnost získatelné konkurentními přístupy nevyužije a ve skutečnosti je to celé jen o latenci) a tam NetApp Files Standard udělá dramaticky lepší službu, než stejně velký a dražší Azure Files Premium s jeho výrazně lepší propustností. Proto je myslím důležité pátrat po tom, co aplikace dělá a potřebuje a ideálně si vyzkoušet více variant v PoC.