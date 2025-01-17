---
layout: post
title: 'Azure Stack: disaster recovery do Azure s Azure Site Recovery'
tags:
- AzureStack
---
Přemýšlíte o využití Azure Stack pro aplikace, které z důvodů latence chcete provozovat lokálně nebo pro které chcete využít CAPEX modelu a přitom si zachovat vlastnosti cloudu? Možná ale budete potřebovat některé stroje z Azure Stack zrcadlit do Azure. Důvodem může být třeba DR strategie, kdy chcete mít zdroje v Azure Stack, ale než platit drahé záložní centrum, použijete pro DR Azure. Platíte jen za nějaký replikační software a storage, ale VMka vytočíte (a zaplatíte) jen když to bude potřeba. Další scénář může být, že na infrastruktuře pro aplikaci pracujete lokálně v Azure Stack, ale pak ji budete potřebovat přesunout do Azure. Možná z důvodu navýšení celkové kapacity před Vánoční špičkou nebo přesun aplikace, která se stala tak úspěšnou u zákazníků, že dává větší smysl provozovat ji v public cloudu. Samozřejmě takový scénář je ideální řešit moderními prostředky typu mikroslužby a kontejnery a aplikaci v Azure přenasadit, ale mohou být situace, kdy chcete sáhnout po infrastrukturním řešení a nareplikovat VMka do Azure tak jak jsou v Azure Stack.

Na tyto scénáře můžete použít službu Azure Site Recovery. Podívejme se jak s Azure Stack funguje.

# Rozchození replikace
Nebudu detailně popisovat postup, protože jsem šel krok za krokem přesně podle dokumentace zde: [https://docs.microsoft.com/en-us/azure/site-recovery/azure-stack-site-recovery](https://docs.microsoft.com/en-us/azure/site-recovery/azure-stack-site-recovery)

V zásadě jsem v azure vytvořil Recovery Services Vault a stáhnul si soubor s přihlašovacími údaji. V Azure Stack jsem rozjel VM s Windows a nainstaloval do něj ASR komponentu Configuration Server, která slouží jako lokální překladiště a zajišťuje komunikaci a koordinaci s ASR v cloudu. Pro Azure Stack se aktuálně využívá model ASR podobný replikaci VMware farmy nebo fyzických serverů. Na chráněná VM se doinstaluje komponenta Mobility Service, která monitoruje zapisovací operace a zrcadlí je do Configuration Server. Ten je bere a posílá do cloudu. Díky tomuto řešení je možné se dostat na velmi nízké RPO - podle přírustků dat a kapacity linky to klidně může být v jednotkách minut.

Replikace tedy funguje tak, že ASR jednou za čas udělá aplikačně konzistentní snapshot s využitím VSC technologie. To je vhodné zejména pro aplikace, kde je aplikační konzistence zásadní, jako jsou databáze. Kromě toho následně posílá přírůstkové informace z jednotlivých write operací. ASR v cloudu tyto přijímá, dává si je do překladiště ve formě blob storage a nasazuje optimalizační technologie jako je caching, komprese a zajišťuje silné šifrování při přenosu. ASR na základě toho průběžně montuje Azure Disk, který je připravený pro nastartování VM v případě potřeby.

Při havárii tedy máte na výběr ze tří možností:
* Maximální konzistence - použijte App consistent snapshot. Ten může být nějakou dobu pozadu (třeba 30 minut, tedy RPO) a jeho nasazení nějakou dobu potrvá (RTO bude vyšší), protože ASR z tohoto snapshotu bude muset teprve vytvořit disk.
* Co nejnižší RTO - v takovém případě použijete poslední zpracovaný write. Tak jak přichází jednotlivé zápisy, ASR je zpracovává tak, že z nich montuje výsledný disk. RPO bude pravděpodobně velmi nízké (třeba 5 minut) a RTO bude také nízké, protože disk už je vytvořen, takže jde o nahození VM.
* Co nejnižší RPO - použijte nejčerstvější data, která má ASR už v cloudu k dispozici. RPO tedy může být velmi malé, klidně i jen několik vteřin, ale ASR musí nejprve data zpracovat a vyrobit disk, tedy RTO bude o něco vyšší.

Problematika DR je podstatně složitější a v tomto článku nemám ambici ji celou rozebrat. Jsou tu otázky jak se sítí (možnost pustit na stejných IP a předělat routing nebou pouštět na jiných a předělat DNS), můžete naskriptovat pořadí spouštění různých strojů a tak podobně.

Ještě musím zmínit jedno aktuální omezení ASR z pohledu Azure Stack. Ten totiž v tuto chvíli může být pouze zdroj, nikoli cíl. ASR tedy nelze použít pro replikaci mezi dvěma Azure Stacky ani z Azure do Azure Stack. Počítejte tedy s tím, že pokud technologii využíváte ne pro migraci, ale pro DR, tak zpětné překlopení z Azure do Azure Stack už nebude automatizované tímto produktem a musí se udělat ručně (například nakopírováním VHD disků nebo synchronizací dat apod.). Pokud hledáte řešení i na tyto situace, Azure i Azure Stack podporuje například Commvault nebo ZeroDown.

# Vyzkoušíme výsledek

V Azure Recovery Vault mám v tuto chvíli dvě VM, které jsou replikované.

![](/images/2019/2019-06-03-20-43-12.png){:class="img-fluid"}

Aktuálně se mi daří RPO na úrovni 3 minuty. To samozřejmě záleží na přírůstku nových dat ve VM vs. kompresní poměr vs. kapacita linky.

![](/images/2019/2019-06-03-20-44-37.png){:class="img-fluid"}

Grafika hezky ukazuje jak technologie ASR funguje. Co je tam nepřesně je vCenter - ASR pro Azure Stack totiž používá stejný mechanismus, jako pro VMware nebo bare metal (jde o to, že z bezpečnostních důvodu v Azure Stack nemá nikdo, tedy ani ASR, přístup k Hyper-V, aby orchestrovalo přímo jeho vlastnosti).

![](/images/2019/2019-06-03-20-47-26.png){:class="img-fluid"}

Všimněte si v obrázku, že ASR průběžně montuje Azure Disk tak, aby byl připraven pro rychlé naběhnutí VM v případě potřeby. Ty ostatně najdeme v příslušné resource group.

![](/images/2019/2019-06-03-20-48-50.png){:class="img-fluid"}

V rámci nastavení si můžeme pohrát s velikostí VM a dalšími parametry, které chceme v procesu DR použít. V mém případě jsou tam stejná nastavení sizingu jako v mém Azure Stack, což odpovídá mým požadavkům. Napojeno to mám do VNETu dr-net. Ten je udělaný tak, že má separátní rozsah IP a je VPNkou napojený a routovaný v rámci firmy (používám tedy variantu jiných IP po fail over a nastavení přes DNS pro interní nebo Azure Traffic Manager z pohledu externích přístupů).

V Azure Stack mám nasazen Process Server, který zpracovává data z chráněných VM, provádí kompresi, šifrování, vyrovnávací paměť a upload do Azure Blob Storage. Jak se mu daří? V mém případě v pohodě, ale může se hodit možnost přidat další a balancovat na ně, pokud by nestíhaly.

![](/images/2019/2019-06-03-20-54-17.png){:class="img-fluid"}

Proveďme testovací fail over, zda se nám VM rozeběhne v Azure.

![](/images/2019/2019-06-03-20-55-17.png){:class="img-fluid"}

Vyberu si nejrychlejší recovery, tedy nízké RTO - crash konzistentní snapshot, který už je zpracovaný a připravený v Azure Disk.

![](/images/2019/2019-06-03-20-56-22.png){:class="img-fluid"}

Můžeme sledovat průběh testování.

![](/images/2019/2019-06-03-20-58-18.png){:class="img-fluid"}

Po chvilce vidím Azure zdroje, jak startují.

![](/images/2019/2019-06-03-20-59-47.png){:class="img-fluid"}

Připojím se, otestuji a pak mohu stroje zase nechat odmazat.

![](/images/2019/2019-06-03-21-02-04.png){:class="img-fluid"}

Při přípravě DR můžeme vytvořit plány.

![](/images/2019/2019-06-03-21-05-13.png){:class="img-fluid"}

Můžeme například poštelovat pořadí, v jakém chceme stroje nahazovat (třeba po nějakých skupinkách - infra, pak DB, pak app, pak web).

![](/images/2019/2019-06-03-21-06-51.png){:class="img-fluid"}


Azure Site Recovery můžete použít v těchto scénářích:
* Azure Stack -> Azure
* Azure -> Azure
* Hyper-V -> Hyper-V
* VMWare -> VMware
* Hyper-V -> Azure
* Azure -> Hyper-V
* VMware -> Azure
* Azure -> VMware
* Bare metal -> Azure

Pokud sedne do vaší DR strategie, použijte. Je to cenově velmi atraktivní v porovnání s nutností budovat DR lokalitu. Platíte totiž za ASR službu a storage, ale VM budíky se vám začnou točit teprve, až když je skutečně budete potřebovat.