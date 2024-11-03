---
layout: post
published: true
title: On-demand capacity reservation vs. reserved instances v Azure - kdy co a proč nejčastěji oboje
tags:
- Compute
---
Mohou v cloudu někdy dojít servery? Dlouhodobě určitě ne, ale události jako byl začátek COVID (a s tím spojený masivní nárůst spotřeby služeb jako Teams) nebo dočasný nedostatek serverů nějakého speciálnějšího typu v nějakém regionu se vyskytnout mohou a to i ve velkých cloudech. Je to vzácné, ale možné. Technická havárie datového centra (nebo celé zóny) vzhledem k HA a DR ostatních zákazníků jistě také zvýší nároky na kapacitu v těch zbývajících.

Řešením je typicky zkusit to o chvilku později, ideálně večer, a pokud to nepomůže, tak zvolit jiný typ serveru, jinou zónu a nebo jiný region. 

Běžící nehavarovanou VM vám nikdo nevezme (nikdo neřekne tuhle VM vypínáme, dostane ji někdo jiný - samozřejmě s výjimkou Spot instancí, které slouží přesně na využití zbytkové kapacity pokud tolerujete, že nikdy nevíte dopředu kolik čeho dostanete a jaká bude aukční cena), takže by vlastně stačilo ji mít pro jistotu dopředu spuštěnou a je to. Jasně, pokud by to byl třeba AKS node, tak na něj pak pustíte kontejnery podle potřeby, ale u starších aplikací to může znamenat hodiny instalace nebo dokonce tým ani neví jak na to (má připravený image od dodavatele například). Představme si teď, že mám legacy aplikace, které neumí nějaký cluster. App1 běží v AZ1, App2 v AZ2 a chtěl bych mít jistotu, že v AZ3 mám garantovanou kapacitu na to, abych v něm spustil buď App1 nebo App2, pokud by AZ1 nebo AZ2 vypadla (tedy chci režim N+1 aka spare nikoli 1+1 aka hot-standby pro každou aplikaci zvlášť). U kontejnerů je to jedno, na AKS node jednoduše hodím kontejnery App1 nebo App2, ale u legacy aplikace to bude spíš o tom, jaký spustím image. VM tedy efektivně nahodím až když vím jaký image potřebuji - a hodilo by se mi SLA, že tam pro ni budu mít dedikovaný prostor. O tom jsou on-demand capacity reservation.

# Jak on-demand capacity reservation funguje
Rezervaci si snadno zajistíte přes portál, API, PowerShell nebo ARM/Bicep šablonu. 

[![](/images/2021/2021-09-13-12-22-35.png){:class="img-fluid"}](/images/2021/2021-09-13-12-22-35.png)

[![](/images/2021/2021-09-13-12-23-27.png){:class="img-fluid"}](/images/2021/2021-09-13-12-23-27.png)

[![](/images/2021/2021-09-13-12-24-05.png){:class="img-fluid"}](/images/2021/2021-09-13-12-24-05.png)

V tento okamžik (tedy až bude služba dostupná v GA) máte SLA na to, že rezervace je vaše a můžete si spustit VM. To lze udělat například v průvodci vytváření VM:

[![](/images/2021/2021-09-13-13-11-16.png){:class="img-fluid"}](/images/2021/2021-09-13-13-11-16.png)

Další možností je použít existující VM, ale nejdřív ji musíte vypnout a spustit v capacity rezervaci.

[![](/images/2021/2021-09-13-13-15-13.png){:class="img-fluid"}](/images/2021/2021-09-13-13-15-13.png)

Rezervace kapacity má svoje vlastní SLA, které zatím nebylo zveřejněno - jasné bude jakmile půjde tato funkce z preview do GA.

# Kolik stojí a jak to souvisí s reserved instances
Efekt vytvoření rezervace kapacity je vlastně stejný, jako spuštění VM. Scheduler vám najde volnou kapacitu a tu vám zabere - stejně, jako kdyby tam běželo vaše VM. S tím souvisí logická věc - je to stejné, jako kdyby VM běželo i finančně. To znamená pokud jedete v režimu pay as you go, platíte jeho plnou cenu. Nicméně pro některé případy viz dále to dává smysl. Ještě častější ale bude kombinace s Reserved Instance. Ta říká, že si rezervujete VM na rok, například 8 cores typu Dav4 v regionu West Europe a získáte velmi pěknou slevu. Tahle rezervace vám sice dává přednost na zdroje, ale ne jejich garanci. Ostatně je tam velká flexibilita - neříkáte v které zóně (platí to automaticky na všechny), neříkáte jestli to má být jedna 8-corová mašina nebo dvě 4-corové a své rozhodnutí o regionu můžete kdykoli změnit a rezervaci si přesunout jinam. Za Reserved Instance platíte bez ohledu na to, jestli nějaké takové VM běží nebo ne - efektivně tedy platíte RI a VM máte díky tomu "zdarma". Nedává tedy smysl takovou VM nepoužívat, takže pokud jste rozhodnuti v které zóně ji chcete, udělejte si on-demand capacity rezervaci - nic navíc vás to nestojí a k moc pěkně ceně si přidáte i rezervovanou fyzickou kapacitu v konkrétní zóně.

S tím souvisí další logická věc - rezervace kapacity nemůže vědět, jestli tam pak bude OS zdarma (Linux, Windows financované přes AHUB) nebo z cloudu placené Windows - proto rezervovaná kapacita stojí jen compute, dokud nad ní nepustíte Windows.

# Jaké jsou scénáře použití
Tady jsou za mne nejdůležitější scénáře použití:
- Hned na začátku jsem zmínil scénář DR, kdy můžu chtít v DR prostředí garanci nějaké základní kapacity. Jasně, mohl bych mít pro každou aplikaci její hot-standby dvojče, ale varianta podobná N+1 bude ekonomičtější.
- Máte zakoupenou reserved instance, takže za VM stejně platíte ať už běží nebo ne. Pak vás on-demand rezervace nestojí nic navíc, takže pokud víte jakou konfiguraci (např. zda D16 nebo D32) chcete a v které zóně, udělal bych to.
- Potřebujete provést nějakou změnu, která znamená vypínání VM a vytváření jiných. Můžete samozřejmě vytvořit paralelní infrastrukturu, všechno rozchodit a pak přepnout uživatele (green/blue deployment), ale u starších aplikací to nemusí být technicky nebo licenčně možné či je to příliš komplikované. Ale vypnout a nemít jistotu, že máte kapacitu znova zapnout se u Vánoční špičky bojíte? On-demand rezervace je řešením.
- Pro dobrou uživatelskou zkušenost potřebujete pracovat "atomicky", tedy mít jistotu, že vám doběhne deployment všech VM, které jsou součástí řešení. Pokud jich potřebujete deset a ta desátá se nepovede, tak je vám těch devět k ničemu. Například jako SaaS poskytovatel takto nasazujete single-tenant řešení svým zákazníkům nebo jako centrální IT spouštíte komplexní šablony, jejichž nasazení trvá třeba i hodinu. Pak je pro vás možná výhodné si nejprve sehnat všechny zdroje s on-demand rezervací a pak máte garanci, že je kapacita k dispozici. Můžete tak daleko dřív zareagovat na případné omezení kapacity změnou typu VM, zóny či regionu a lze to relativně jednoduše automatizovat (srovnejte s tím, že po 45 minutách zjistíte, že jedna VM chybí a šablona vrátila chybu - řešit takovou situaci, odmazávat apod. je určitě složitější, než nezačínat reálný deployment, dokud nemáte plně rezervovanou kapacitu).

Takhle tedy funguje on-demand capacity reservation v Azure a zejména bych ji doporučil, pokud máte tradiční workload a nakoupenou reserver instance.