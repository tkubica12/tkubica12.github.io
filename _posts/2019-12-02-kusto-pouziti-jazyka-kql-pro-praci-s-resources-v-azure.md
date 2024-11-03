---
layout: post
title: 'Kusto: použití jazyka KQL pro práci s resources v Azure'
tags:
- Kusto
- Monitoring
---
Co je Kusto Query Language, kde ho v Azure najdete a na co je dobrý, už jsme rozebrali minule. Dnes s ním začneme pro něco, co si jednoduše vyzkoušíte, aniž byste museli cokoli zapínat nebo platit. Podíváme se na Azure Resource Explorer.

# Proč Kusto v Azure Resource Explorer
Jakmile máte hodně subskripcí a zdrojů v Azure, můžete začít hledat cesty pro rychlejší orientaci. Díky portálu jste schopni v jedné obrazovce vidět všechny vaše zdroje ve všech subskripcích, ke kterým máte přístup, a ve všech regionech. Můžete v nich vyhledávat apod. Mimochodem něco takového není ve všech cloudech samozřejmostí.

Nicméně jen filtrovat a hledat nemusí stačit. Možná potřebujete nějaké agregační informace (kolik čeho kde mám) nebo dokonce vztahy mezi objekty. Nad vašimi resources v Azure můžete dělat dotazy jazykem Kusto a to si dnes vyzkoušíme. Nebojte se, nebude to nic složitého. Všechno v Azure najdete přes All Services -> Azure Resource Graph Explorer.

# Základní dotazy na VM
Začneme jednoduše. V tabulce Resources najdeme všechny zdroje, ke kterým máme přístup. Nás budou zajímat jen VM, odfiltrujeme tedy tento type (všimněte si, že je to stejný type, který můžete znát třeba z ARM šablon).

```
Resources
 | where type == "microsoft.compute/virtualmachines"
```

![](/images/2019/2019-11-02-12-23-07.png){:class="img-fluid"}

Co řádek, to VM. Podívejme se na detaily.

![](/images/2019/2019-11-02-12-23-42.png){:class="img-fluid"}

Tagy jsou vnořený objekt - můžeme podle nich různě hledat a parsovat je.

![](/images/2019/2019-11-02-12-24-13.png){:class="img-fluid"}

Jak vidíme, properties jsou také vnořený objekt a můžeme podle nich třeba filtrovat.

Co třeba udělat si výpis počtu VM dle jejich velikosti? Na to použijeme funkci summarize (něco jako GROUP BY v SQL) a co chceme spočítat je count(), tedy počet řádků (máme přece jedno VM na každý řádek) a seskupíme podle velikosti VM. Tu získáme vyparsováním properties na cestě properties.hardwareProfile.vmSize a protože je to vnořený objekt, poradíme Kusto, že výsledek chceme brát jako řetězec.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | summarize count() by tostring(properties.hardwareProfile.vmSize)
```

![](/images/2019/2019-11-02-12-27-30.png){:class="img-fluid"}

Máme to. Jen názvy sloupečků nejsou moc pěkné, tak je změníme.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | summarize vmCount=count() by vmSize=tostring(properties.hardwareProfile.vmSize)
```

![](/images/2019/2019-11-02-12-28-16.png){:class="img-fluid"}

Totéž třeba můžeme udělat podle regionů.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | summarize vmCount=count() by location
```

![](/images/2019/2019-11-02-12-29-05.png){:class="img-fluid"}

# Použité image u VM
Občas by se mi hodil přehled z jakých image mám nastartované svoje VM. To se dá najít v properties.storageProfile a můžeme si takový výpis udělat. Abych tam neměl víc informací než potřebuji, použiji funkci project a vyjmenuji sloupečky resourceGroup a name. Dále přidám "dopočítané" sloupce imagePublisher, imageOffer a imageSku, které vzniknou parsováním properties.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | project resourceGroup, name, 
 			imagePublisher=properties.storageProfile.imageReference.publisher,
			imageOffer=properties.storageProfile.imageReference.offer,
			imageSku=properties.storageProfile.imageReference.sku
```

![](/images/2019/2019-11-02-14-11-21.png){:class="img-fluid"}

Možná chceme spojit informace o image do jediného sloupce a publisher, offer a sku oddělit dvojtečkou podobně, jako je tomu třeba v ARMu. Sloupeček můžeme smontovat použitím strcat.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | project resourceGroup, name, image = strcat(
 				properties.storageProfile.imageReference.publisher, ":",
				properties.storageProfile.imageReference.offer,  ":",
				properties.storageProfile.imageReference.sku)
```

![](/images/2019/2019-11-02-14-13-05.png){:class="img-fluid"}

Pojďme si spočítat počty VM na základě jednotlivých imagePublisher.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | project name, imagePublisher = tostring(properties.storageProfile.imageReference.publisher)
 | summarize vmCount=count() by imagePublisher
```

![](/images/2019/2019-11-02-14-15-11.png){:class="img-fluid"}

Můžeme si to vizualizovat třeba do koblížkového grafu.

![](/images/2019/2019-11-02-14-16-05.png){:class="img-fluid"}

A výsledné sestavy lze přišpendlit na Dashboard.

![](/images/2019/2019-11-02-14-17-30.png){:class="img-fluid"}

# Join tabulky subskripcí
Tabulka Resources obsahuje informace o zdrojích a u každého je i subscritionId. Report počet VM za subskripce by vypadal takhle:

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | summarize vmCount=count() by subscriptionId
```

![](/images/2019/2019-11-02-14-20-01.png){:class="img-fluid"}

To je fajn, ale kdo si má ID subskripcí pamatovat. Ty mají i svůj název, ale ten není v této tabulce. Najdeme ho v resourcecontainers, kde zdroje z vyšších scopes, například seznam resource group a seznam subskripcí s jejich jménem.

```
resourcecontainers
 | where type == "microsoft.resources/subscriptions"
 | project subscriptionName=name, subscriptionId
```

![](/images/2019/2019-11-02-14-21-43.png){:class="img-fluid"}

Pojďme teď obě informace spojit dohromady. Použijeme join a pro dnešek zůstaneme o toho výchozího. Ten ke všem řádkům nalevo (tabulka resources) přidá sloupečky z tabulky napravo tak, aby subscriptionId bylo stejné. Pokud na pravé straně informace není (což ale logicky v našem případě nehrozí), tak řádek vznikne, ale nebude mít hodnoty z pravé tabulky. V podstatě tedy oba předchozí dotazy zkombinujeme do jednoho. Necháme si vypsat VM a provedeme join na seznam subskripcí na základě shodného subscriptionId. Na závěr použijeme project a zobrazíme pouze jméno subskripce a počet VM v ní.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | summarize vmCount=count() by subscriptionId
 | join (resourcecontainers
			| where type == "microsoft.resources/subscriptions"
			| project subscriptionName=name, subscriptionId
		) on subscriptionId
 | project subscriptionName, vmCount
```

![](/images/2019/2019-11-02-14-27-08.png){:class="img-fluid"}

# Disky
Chystáme si nějaký složitější (ale ne zas moc) příklad, tak si ještě připravme něco s disky. Tak například se podívejme na celkovou kapacitu disků za tiery Premium a Standard.

```
Resources
 | where type == "microsoft.compute/disks"
 | project tier = tostring(sku.tier), size = toint(properties.diskSizeGB)
 | summarize totalStorageGB = sum(size) by tier
```

![](/images/2019/2019-11-02-14-34-41.png){:class="img-fluid"}

U disků nás může zajímat, zda patří k nějaké VM. To je stav Attached (u spuštěné VM) nebo Reserved (u vypnuté VM) a v obou případech najdeme v políčku managedBy identifikaci VM, ke které patří. Takhle tedy můžeme najít nepřipojené disky a ověřit si, že je ještě potřebujeme (zapomenutý nepřipojený disk stojí peníze).

```
Resources
 | where type == "microsoft.compute/disks"
 | where managedBy == ""
 | project name, resourceGroup, sku = tostring(sku.name), diskState = tostring(properties.diskState)
```

![](/images/2019/2019-11-02-14-39-20.png){:class="img-fluid"}

# Složitější dotaz - jaké VM mají single-instance SLA?
V Azure můžete kromě SLA na availability sety a availability zóny dostat SLA i na jednotlivé VM instance. Musíte ovšem splňovat to, že všechny OS a datové disky používají Premium disky. Pojďme si udělat report, který nám řekne, které z našich VM tuto podmínku splňují.

Začneme tím, že si vypíšeme seznam VM a zredukujeme výstup jen na jméno a id (budeme potřebovat později).

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | project name, id
```

![](/images/2019/2019-11-02-10-07-12.png){:class="img-fluid"}

Výborně. Teď si tento výpis spojíme se seznamem disků. U nich najdeme položku managedBy, tedy ke které VM disk patří. Provedeme tedy join s tím, že z pohledu disku nás bude zajímat jen managedBy a sku (to vyparsujeme z sku objektu) a join bude tak, že v levé tabulce použijeme id VM a v druhé políčko managedBy.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | project name, id
 | join (Resources
            | where type == "microsoft.compute/disks"
            | project managedBy, sku = tostring(sku.tier)
        ) on $left.id == $right.managedBy
```

![](/images/2019/2019-11-02-10-09-21.png){:class="img-fluid"}

Co se stalo? Pro každý disk, který patří k nějakému VM, máme samostatný řádek. Všimněte si, že moje VM dataEdge-vm má tedy dva řádky, protože má OS disk a ještě datový disk. Také je tu vidět, že zatímco OS disk je Premium, datový je Standard, takže tato VM nesplňuje podmínky pro single-instance SLA.

Jak VM zpátky zredukovat pro jeden řádek pro každou? Použijeme sumarizaci na základě id a name (id by nám stačilo, ale chceme do výpisu dostat i jméno - jen podle name to ale dělat nechci, protože nemusí být unikátní). Jak ze sumarizace ale poznáme, jaké disky tam jsou? Použiji funkci countif s sku == "Standard", tedy efektivně počítám počet Standard disků, které VM má.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | project name, id
 | join (Resources
            | where type == "microsoft.compute/disks"
            | project managedBy, sku = tostring(sku.tier)
        ) on $left.id == $right.managedBy
 | summarize standardDiskCount = countif(sku == "Standard") by id, name
```

![](/images/2019/2019-11-02-10-13-24.png){:class="img-fluid"}

Výborně. Všechny VM, které mají nulový počet Standard disků budou mít single-instance SLA. Pojďme to tedy pro uživatele udělat přehlednější. Místo počtu Standard disků uděláme sloupeček singleVmSla, v kterém bude buď yes, pokud je počet Standard disků 0 nebo no, pokud je nenulový.

```
Resources
 | where type == "microsoft.compute/virtualmachines"
 | project name, id
 | join (Resources
            | where type == "microsoft.compute/disks"
            | project name, managedBy, sku = tostring(sku.tier)
        ) on $left.id == $right.managedBy
 | summarize standardDiskCount = countif(sku == "Standard") by id, name
 | project name, id, singleVmSla = case(standardDiskCount == 0, 'yes', 'no')
```

![](/images/2019/2019-11-02-10-16-16.png){:class="img-fluid"}

A je to.


Dnes jsme si využili Kusto jazyka pro prohledávání nasazených zdrojů v Azure. Příště už se vrhneme na logy a telemetrii v rámci Azure Monitor.