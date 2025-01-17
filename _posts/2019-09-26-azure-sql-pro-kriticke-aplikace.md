---
layout: post
title: Azure SQL pro kritické aplikace
tags:
- SQL
---
Tým kolem Azure SQL publikoval v červenci nové SLA pro vaše nejkritičtější aplikace a nabízí garance, které jsou na trhu public cloudu vyjímečné. Podívejme se co znamená provozovat kritické systémy na Azure SQL.

SLA si můžete prostudovat [na webu](https://azure.microsoft.com/en-us/support/legal/sla/sql-database/v1_4/).

# Vysoká dostupnost
Jedním ze způsobů zajištění HA je provoz databáze v clusteru na vícero nodech tak, že tyto jsou synchronně replikovány. To znamená, že aplikaci je vráceno OK až v okamžiku, kdy jsou data bezpečně uložena na více serverech a případné překlopení na jiný node neznamená žádnou ztrátu dat. Z výkonostních důvodů daných PACELC teorémem je zřejmé, že fyzická vzdálenost mezi nody nesmí být příliš veliká (řekněme třeba 1ms), ale to neznamená, že musí být ve stejném sále. Velké regiony Azure včetně několika v Evropě nabízí koncept nezávislých datových center, availability zón. Pokud by například v budově vypukl požár, je celkem jedno kolik nodů tam máte a jak redundantní je síť - datové centrum prostě hoří. Tato havárie ale nemá vliv na ostatní datová centra v regionu. 

Azure SQL v tieru Premium nebo Business Critical je ve skutečnosti synchronně replikovaný cluster, který můžete nasadit v režimu, kdy jeho nody jsou rozprostřeny do tří zón dostupnosti (datových center). Díky tomu lze dosahovat velmi vysoké dostupnosti. SLA služby bylo povýšeno na 99,995% pro takto nastavený Azure SQL a jde podle všeho o nejvyšší SLA na trhu velkých public cloudů alespoň v době psaní tohoto článku. Pro srovnání s on-premises doporučuji uvědomit si, že SLA se vztahuje na to, že se vám podaří sestavit connection do databáze a pracovat s ní. Zahrnuje tedy jak nečekané události, tak patchování strojů a jinou maintenance. Logicky musí pokrývat celou potřebnou infrastrukturu, tedy compute, storage i networking a také databázovou vrstvu samotnou. Pokud tedy srovnáváte, nezapomeňte, že kromě bedny vám může on-premises SQL vypadnout z jiných důvodů, například problémy v síti nebo nutnost provádět maintenance.

Ještě neopomeňme jednu věc - vysoká dostupnost je daná schopností automatické nápravy chybových stavů. Nějaká komponenta může umřít, ale celý systém se velmi rychle sám dostane do funkčního stavu bez ztráty dat a všechno překlopí. To ale může znamenat rozpadnutí session. Ověřte si, že vaše aplikace má retry a sama se pokouší znova připojit, pokud jí spojení vypadne (většina SDK to pro vás umí zajistit).

SLA je s finačním závazkem ze strany Microsoftu.

# Business continuity
Vysoká dostupnost je základ a snažil bych se ji maximalizovat, protože umožňuje automatické vyřešení potíží bez jakékoli ztráty dat. Nicméně jsou i další situace, proti kterým se chcete chránit. Může to být snížení (už tak velmi malého) rizika selhání celého regionu například v důsledku zemětřesení, které sundá všechny datová centra v regionu. Druhé riziko je poškození dat vlivem aplikační chyby nebo malware.

## Disaster recovery
Azure SQL umožňuje vytvoření další instance v jiném regionu vzdáleném stovky kilometrů. Při těchto vzdálenostech už není možné z důvodu PACELC teorému (výkon databáze) používat synchronní repliku, musíme asynchronně. Funguje to tak, že máte masivní HA cluster v jednom regionu a k tomu asychronně replikujete data do dalšího HA clusteru v jiném regionu. Jsou tu dvě klíčové otázky, které chceme znát - RPO a RTO a cloud obvykle nedává garance těchto hodnot. Ale jak správně tušíte, Azure SQL v tieru Business Critical ano za předpokladu, že sekundární Azure SQL má stejný sizing jako primární.

První důležitá věc je, o kolik je sekundární region pozadu za primárním. Díky asynchronnímu chování je jasné, že může při překlopení dojít ke ztrátě dat (těch co jsou "na cestě" a nestihly se nakopírovat do druhého regionu, když primární pohřbila třeba sopka). Tento ukazatel je RPO - Recovery Point Objective. Azure SQL, v době psaní článku jako jediný z velkých public cloudů, dává garance na RPO a to 5 vteřin. Počítá se to jako 99. percentil v rámci hodiny, který musí být 5 a méně vteřin. Jinak řečeno zhruba 59 a půl minuty z hodiny nebude zpoždění větší jak 5 vteřin. Drobné zaškobrtnutí je tedy přípustné, ale opravdu jen málo pravdědopodbné a malé (velké zaškobrtnutí třeba 40 vteřin už by se nevešlo do SLA). 

Druhá otázka je jak dlouho trvá překlopení databáze na jiný region, tedy RTO. I tady má pro vás Azure SQL Business Critical připravené SLA. Od okamžiku kdy si řeknete o překlopení (kliknutí v portálu) se stane druhý region aktivní do 30 vteřin. Pokud preferujete automatické překlopení s auto-failover groups je RTO 1 hodina (ale samozřejmě kdykoli můžete zasáhnout a překlopit manuálně).

SLA na RPO i RTO je s finančním závazkem Microsoftu.

## Backup
Ochrana proti poškození dat třeba z důvodu aplikační chyby se řeší zálohováním, které má služba Azure SQL v sobě. Automaticky se provádí plná záloha DB každý týden, inkrementální každých 12 hodin a záloha logů každých 5-10 minut. Díky funkci point-in-time restore jednoduše řeknete do jakého času v minulosti chcete obnovit data a Azure sám najde potřebné zálohy a přehraje logy přesně do času, který si řeknete. Vlastní zálohy se ukládají na geo-redundantní storage, takže jsou dostupné nejen v hlavním regionu, ale i v párovém regionu.

Provozujete kritické aplikace s využitím SQL? Azure SQL Business Critical vám nabídne vysoce dostupný cluster běžící současně ve třech datových centrech s vysokým SLA zahrnujím compute, storage, networking, maintenance i SQL samotný. Potřebujete pokrýt i megakatastrofy? Přidejte geo-replikaci s SLA na RPO i RTO. Bojíte se ztráty dat chybou nebo malwarem? Azure SQL pro vás zálohuje a to opět geo-redundantním způsobem. Dosáhnout stejného výsledku v on-premises znamená mít 6 datových center a hodně personálu. V Azure je to na kliknutí hned, bez stavebního povolení a platíte jen za to, co opravdu spotřebujete. Můžete se tak soustředit na to, co je pro vás nejdůležitější a co vás odlišuje od konkurence - vaše data a aplikace.