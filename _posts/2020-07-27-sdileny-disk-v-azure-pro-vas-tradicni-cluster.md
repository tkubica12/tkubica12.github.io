---
layout: post
published: true
title: Sdílený disk v Azure pro váš tradiční cluster
tags:
- Storage
---
Jsem zastáncem moderních přístupů k vysoké dostupnosti a ještě lépe to nejsložitější, což jsou stavové věci typu databáze, přenechat povolanějším jako jsou inženýři Azure a jejich platformní služby. Ideálně tak mám aplikační logiku zcela bezestavovou, což mi dramaticky zjednodušuje nasazování, škálování, řešení výpadků a DR, a stav je v platformní službě Azure ať už jde o data strukturovaná a trvalá (např. Azure SQL), dočasná (Azure Cache for Redis nebo Cosmos DB s TTL), události, fronty či zprávy (Event Hub, Event Grid, Service Bus) nebo nějaké orchestrační workflow (Logic App). Pokud už musím stav řešit, tak bych preferoval cestu shared nothing architektury, tedy bych měl tři na sobě nezávislé instance každou s vlastní storage a mezi nimi protokol, kterým si data synchronizují a udržují se ve formě (SQL AlwaysOn, Cassandra, MongoDB). Tradiční cluster se sdílenou storage bych nepreferoval.

Nicméně - někdy není prostor modernizovat. Další vlastní datové centrum už si prostě kupovat nechcete a je na čase odstěhovat se do Azure. Naložit co máte na virtuální rudlík a virtuální servery si rozvěsit v Azure. Na modernizaci bude prostor později. Pak se ale bez podpory pro tradiční cluster asi neobejdu.

# Možnosti v Azure
Sdílený blokový Volume není ve skutečném cloudu velké trojky nic jednoduchého. Jsou k tomu zřejmé technické důvody vzhledem ke škále v jaké tito poskytovatelé operují - máte softwarově definovaný systém a VM mohou být na mnoha místech - není to zkrátka vaše DC s pěti racky a v tom šestém nějaké klasické pole. 

Azure přichází s možností sdílet disk v režimu single writer s využitím standardních SCSI PR (ale o tom později) a je tak plně připraven na tradiční HA. AWS pokud vím nepodporuje SCSI PR, ale všechny disky připojuje v multi-write (nechává tak válku o zdroj na aplikaci či file-system, což není tak univerzální vzhledem ke starším aplikacím - což je problém, když to děláte hlavně pro ně). GPC nepodporuje zápisy, pokud disk napojíte na víc VM, musí být všechny read only (takže pro HA cluster nepoužitelné). Pro tradiční HA je tedy Azure připraven v tuto chvíli asi nejlépe, ale proberme si nejdřív jiné možnosti.

## Souborové řešení
Pokud nemůžete sdílet blokové zařízení včetně koordinace zápisů, co to přenechat na file system? Vezměme si třeba takové Azure Files, tedy plně platformní službu postavenou na SMB/CIFS protokolu (NFS je v private preview). Jejím limitem donedávna mohl být výkon, ale už pár měsíců je k dispozici Premium verze postavená na SSD discích, takže z tohoto pohledu to vůbec není špatné. S Azure Files Premium se dostanete až na 100 000 IOPS, nicméně je to tak, že dostáváte 1 IOPS za každý koupený GB (ty na rozdíl od Azure Files Standard platíte bez ohledu na obsazenost), takže na získání 10 000 IOPSů si musíte pořídit 10 TB storage, což je fajn pokud ji využijete, ale pokud ne, může to vyjít relativně draho. Jinak řečeno Azure Files Premium vám dá 1000 IOPS na každý koupený TB.

Pokud se pohybujete v extrémnějších výkonech a potřebujete agresivnější poměr výkonu ke kapacitě, můžete použít Azure NetApp Files. Premium storage vám dá cca 16k IOPS na TB (při 4KB blocích) a ultra dvakrát tolik. Zakoupené minimum je 4TB, ale to můžete krájet na vícero prostorů (sharů) a použít tak pro víc aplikací. 

Třetí cesta samozřejmě je si file system vyrobit sami použitím VM a premium disků. Může to být ONTAP od NetAppu (virtuální varianta - co jsem počítal, tak pokud jde o soubory, vyplatí se jít do Azure NetApp Files), Gluster, Luster, SMB share nad Windows clusterem apod.

Za mě - pokud jde o share pro provozování databáze, Azure NetApp Files je myslím nejlepší volba.

Nicméně váš databázový cluster musí podporovat HA nad souborovým systémem (SMB u Azure Files, NFS nebo SMB u Azure NetApp Files). A to nebude vždy, takže dobře prostudujte a vyzkoušejte, než se rozhodnete stěhovat workload v tomto režimu.

## Blokové řešení postavené nad VM
Možná ale váš cluster prostě a jednoduše potřebuje blokové médium a ten nejtradičnější přístup ke sdílení disku. Ne zrovna příjemnou ale určitě funkční variantou je si vyrobit takový disk virtuálně. Jednou z možností mohou být Storage Spaces ve Windows Server. Vezmete několik VM s disky a tato zařízení se namapují do Storage Spaces, které na ně budou redundantním způsobem distribuovat data a ven to nabídnou jako iSCSI target. Ve vašem clusteru tedy bude iSCSI iniciátor a uvidí disk. Podobného řešení lze dosáhnout v Linuxu přes DRBR (Distributed Replicated Block Device) nebo použitím CEPH (s RADOS Block Device). Jsou i komerční varianty jako je virtuální ONTAP od NetAppu.

Hlavní nevýhodou všech těchto variant samozřejmě je, že jsme si smotnovali storage sami a máme tak o hodně víc věcí, o které se musíme starat. A věcí komplikovaných a souvisejících přímo s datovou integritou, takže případné chyby nejsou jen "no nic, otočíme to".

# Azure Shared Disk
Velkou novinkou v Azure je možnost sdílet Azure Disk a to způsobem, který nám se scénářem HA clusterů pro tradiční aplikace opravdu pomůže. Pokud správně koukám na ostatní cloudy tak rozdíl je právě v implementaci SCSI Persistent Reservations. To jsou tradiční blokové instrukce pro registraci zařízení do vícero nodů s tím, že pouze jeden z nich může být ve write režimu, ostatní jsou read. Pokud databáze spadne, druhý node se může zmocnit zapisovacího práva a přesně na tom principu je HA postaveno. Není tedy potřeba nějaká specifická podpora na úrovni file system, toto řešení je postaveno čistě na sdílení blokového přístupu. 

Jak to funguje? U podporovaného disku nastavíte maxShares na hodnotu větší než jedna a tento datový disk (OS disk logicky není podporovaný) připojíte do vícero VM a nainstaluje příslušné clusterovací řešení jako je Windows Server Failover Cluster nebo Pacemaker v Linuxu. 

Řešení má nějaká omezení. Podporuje pouze vyjmenované typy disků z kategorie Premium a Ultra a velmi omezený výčet regionů (ale na tom se pracuje). Pro deployment zatím musíte použít ARM šablonu (nebo API), zatím nemůžete pro takový systém použít Azure Backup a tak podobně. Z výkonnostního hlediska Premium disky mají fixní výkon v IOPS (a bursting není u shared disků aktuálně podporován), bez ohledu který node s ním mluví. U Ultra disků nastavujete kolik IOPS a propustnosti si chcete pořídit a k témto dvěma hodnotám se přidala další - kolik IOPS a propustnosti chcete pro ty nody, které jsou v režimu čtení. Obě metriky jsou oddělené, takže máte jasné výkonnostní garance a můžete si s nimi šoupat i za běhu systému.

Více se dozvíte v [dokumentaci](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/disks-shared)


Migrujete do Azure? Pokud můžete, modernizujete aplikace tak, aby aplikační vrstva nebyla stavová a pro veškeré datové potřeby použijte platformní služby. Musíte si postavit vlastní databázovou vrstvu v Azure? Pokud to jde, použijte share nothing architekturu a replikujte data mezi nody prostředky databáze jako je AlwaysOn v SQL. Potřebujete sdílenou storage, jinak to nepůjde? Může to být souborový systém? Pak se podívejte primárně na Azure NetApp Files. Musí to být blokové řešení? Zkuste Azure Disk v shared režimu, pokud můžete ještě chvilku počkat, než se dostane do Evropy (jinak si budete muset vyrobit řešení sami). No a na závěr - u legacy HA řešení se můžete potkat i s problematikou síťové dostupnosti. V cloudu technologie typu gratious ARP, VRRP/HSRP a podobné principy postavené na L2 protokolech a broadcast/multicast vlastnostech nefungují. Často to lze řešit nastavením Azure Load Balanceru (třeba u SQL), ale jsou situace, kdy nezbyde než tradiční sítě simulovat... ale to není předmětem dnešního článku.