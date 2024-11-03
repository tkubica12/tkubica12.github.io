---
layout: post
title: 'Kusto: Joinovaní tabulek a obohacování dat'
tags:
- Kusto
- Monitoring
---
Kusto Query Language je velmi mocný a dost často se dosahuje výsledků joinováním data sama na sebe, mezi tabulkami (lze i to i mezi workspace) apod. Podívejme se dnes jak na to.

# Joinování dat z různých tabulek či dotazů
Při budování Kusto dotazů poměrně často potřebuji dělat join. Je to jednak z důvodů obohacení dat z jiné tabulky (například zkoumám telemetrii pro VMka, ale chtěl bych z jiné tabulky dodat detaily typu jaký mají sizing), korelace (např. dej mi logy z mašin, kterým chybí updaty) nebo i dva různé pohledy na stejnou tabulku (nejdřív mi najdi stroje s nejhorší průměrnou telemetrií a pak mi k nim přidej podrobnosti). Nejdřív se podíváme obecně na různé varianty join operace.

Výchozí stav je innerunique a ať se nám to dobře ukazuje, použijeme vlastní jednoduchou tabulku. Všimněte si, že první tabulka není unikátní key/value, protože v prvním sloupečku mám dvakrát b a pokaždé s jinou hodnotou. Pošleme to do Kusto.

```
datatable (id:string, value:int)
    [
        "a", 1,
        "b", 2,
        "b", 3,
        "c", 4
    ]
| join kind= innerunique (
        datatable (id:string, value:int)
        [
            "b", 91,
            "c", 92,
            "d", 93
        ]
    ) on id
```

![](/images/2020/2020-01-09-06-19-47.png){:class="img-fluid"}

Join je vnitřní, takže ve výsledku musíme vidět jen řádky, kdy se našlo stejné id nalevo i napravo, takže id "b" a "c". Všimněte si ale, že z první tabulky vzal jen jedno béčko s hodnoou 2, to druhé s trojkou nám odignoroval. Takhle se chová innerunique.

Pokud uděláme totéž s metodou inner, vypadá to jinak.

```
datatable (id:string, value:int)
    [
        "a", 1,
        "b", 2,
        "b", 3,
        "c", 4
    ]
| join kind= inner (
        datatable (id:string, value:int)
        [
            "b", 91,
            "c", 92,
            "d", 93
        ]
    ) on id
```

![](/images/2020/2020-01-09-06-22-34.png){:class="img-fluid"}

Teď už máme řádky jak pro b=2 tak b=3, ale zase logicky máme duplikátně b=91. Co si vybrat záleží na situaci. Osobně bych preferoval se nejdřív duplikací na klíči zbavit, pokud tam jsou, a tím dostat pod kontrolu co se má dít. Tak například bych mohl obě strany nejprve "deduplikovat" použitím agregace průměr.

```
datatable (id:string, value:int)
    [
        "a", 1,
        "b", 2,
        "b", 3,
        "c", 4
    ]
| summarize value=avg(value) by id 
| join kind= inner (
        datatable (id:string, value:int)
        [
            "b", 91,
            "c", 92,
            "d", 93
        ]
        | summarize value=avg(value) by id 
    ) on id
```

![](/images/2020/2020-01-09-06-33-47.png){:class="img-fluid"}

Další možnost je, že si z value uděláme pole, pokud bychom měli víc duplikátních id.

```
datatable (id:string, value:int)
    [
        "a", 1,
        "b", 2,
        "b", 3,
        "c", 4
    ]
| summarize makelist(value) by id 
| join kind= inner (
        datatable (id:string, value:int)
        [
            "b", 91,
            "c", 92,
            "d", 93
        ]
        | summarize makelist(value) by id 
    ) on id
```

![](/images/2020/2020-01-09-06-33-10.png){:class="img-fluid"}

Občas ale potřebujeme do výsledku dát i záznamy, které nemají v druhé tabulce protikus. Tak například v prvním dotazu získáváme seznam VM s chybějícími updaty a v druhé straně k nim dohledáváme počet chybových hlášek v logu. To je pro mě doplňková informace - klíčové je, kde nemám updaty. Nechci tedy, aby stroj vypadl ze seznamu jen kvůli tomu, že nevykazuje chyby. Na levé straně tedy chci záznamy všechny bez ohledu na to, jestli k nim na pravé straně něco najdu nebo ne.

```
datatable (id:string, value:int)
    [
        "a", 1,
        "b", 2,
        "b", 3,
        "c", 4
    ]
| join kind= leftouter (
        datatable (id:string, value:int)
        [
            "b", 91,
            "c", 92,
            "d", 93
        ]
    ) on id
```

![](/images/2020/2020-01-09-06-38-28.png){:class="img-fluid"}

Totéž samozřejmě můžeme udělat i z druhé strany.

Někdy můžu chtít vidět všechno - pokud se najdou protikusy fajn, pokud na jedné nebo druhé straně bude nějaký sirotek, chci vidět i je.

```
datatable (id:string, value:int)
    [
        "a", 1,
        "b", 2,
        "b", 3,
        "c", 4
    ]
| join kind= fullouter (
        datatable (id:string, value:int)
        [
            "b", 91,
            "c", 92,
            "d", 93
        ]
    ) on id
```

![](/images/2020/2020-03-16-16-02-36.png){:class="img-fluid"}

Co když mě zajímají pouze údaje z levé strany, ale pravou potřebuji jako filtr. Tedy nezajímají mě údaje z pravé strany pro zobrazení, beru je jen jako filtr. Mohl bych udělat inner join a odprojektovat nepotřebné sloupečky, ale to je zbytečná operace navíc - mohu použít leftsemi typ joinu.

```
datatable (id:string, value:int)
    [
        "a", 1,
        "b", 2,
        "b", 3,
        "c", 4
    ]
| join kind= leftsemi (
        datatable (id:string, value:int)
        [
            "b", 91,
            "c", 92,
            "d", 93
        ]
    ) on id
```

![](/images/2020/2020-01-09-06-42-58.png){:class="img-fluid"}

Podobné kousky se dají dělat z obou stran a kromě semi lze použít i opak, tedy anitsemi.

# Příklady nad reálnými daty
Dejme tomu, že nás zajímá, k jakým změnám v systémových souborech, nainstalovaných komponentách nebo registrech došlo na strojích, kterým chybí některé kritické updaty. To uděláme třeba takhle:

```
Update
| where Classification == "Critical Updates" and UpdateState == "Needed"
| summarize count() by Computer   
| join (
    ConfigurationChange
) on Computer 
```

Můžeme si to upravit tak, že si vypíšeme jen změny na třech nejhorších co do počtu chybějících updatů.

```
Update
| where Classification == "Critical Updates" and UpdateState == "Needed"
| summarize count() by Computer
| sort by count_ desc
| limit 3
| join kind= rightsemi (
    ConfigurationChange
) on Computer 
```

Ne vždy je join jen jedinou možností. Zejména v našem případě, kdy nepotřebujeme sjednocovat vícero sloupců na obou stranách, ale jde nám vlastně jen o získání seznamu počítačů, na základě kterého filtrujeme v dalším kroku. Můžeme tedy získat seznam počítačů, udělat z něj pole a uložit v proměnné. Následně provedeme jednoduchý dotaz do jiné tabulky s where Computer je součástí obsahu proměnné.

```
let worstComputers = toscalar(
    Update
    | where Classification == "Critical Updates" and UpdateState == "Needed"
    | summarize count() by Computer
    | sort by count_ desc
    | project Computer
    | limit 3);
ConfigurationChange
    | where Computer in (worstComputers)
```

Na závěr si ukažme něco o trošku složitějšího, ale zase ne moc. Bude to ze světa kontejnerů. Představte si, že potřebujete vygenerovat Alert v okamžiku, kdy se obsazenost paměti kontejneru dostane nad 90% nastaveného limitu. Důvod je, že při přelezení 100% bude kontejner orchestrátorem sestřelen (trochu proces OOM zabíjení zjednodušuji, ale to pro teď nevadí), takže je vhodné vědět dříve, že nám něco dělá velkou spotřebu a možná to chce limity zvednout či aplikaci upravit. V Azure Monitor for Kubernetes jsou na tohle téma nádherné grafy připravené, ale Alert ne. Některé věci z AKS jdou přímo do Azure Metrics, nad kterými se dají dělat alerty bez KQL dotazů, ale tato konkrétní v době psaní článku ne. A to je skvělé, protože si alespoň můžeme vyzkoušet query.

První věc - v tabulce Perf jsou ošklivé názvy Podů (řekněme ID). Já bych raději hezčí a obohatil si ho například o namespace ve kterém se nachází nebo o Deployment jehož jsou součástí podle label nebo tak nějak. Začnu tedy tím, že si z tabulky inventáře připravím hezký název (chci ho ve formátu namespace/nazev) a k tomu ID. Zatím se budu koukat do dlouhé historie (to brzy změníme).

```
let threshold = 90;
let endDateTime = now();
let startDateTime = ago(50d);
let trendBinSize = 1m;
let capacityCounterName = 'memoryLimitBytes';
let usageCounterName = 'memoryRssBytes';
KubePodInventory
| where TimeGenerated < endDateTime
| where TimeGenerated >= startDateTime
| extend InstanceName = strcat(ClusterId, '/', ContainerName),
         ContainerName = strcat(Namespace, '/', tostring(split(ContainerName, '/')[1]))
| distinct Computer, InstanceName, ContainerName
```

![](/images/2020/2020-01-28-09-42-15.png){:class="img-fluid"}

Výborně. Máme tabulku ošklivý vs. hezký název, to se hodí.

Co dál? Telemetrie nesbírá poměr spotřeby paměti vs. nastavený limit, ale (a to dává smysl) jen právě tyto dvě hodnoty. Nejprve tedy potřebuji nastavený limit. Ten se ale může u kontejneru měnit, takže si najdu jeho maximální hodnotu v daném intervalu. Join mi umožní to, že koreluji podle ošklivého názvu, ale ve výpisu vidím i svůj hezký.

```
let threshold = 90;
let endDateTime = now();
let startDateTime = ago(5m);
let trendBinSize = 1m;
let capacityCounterName = 'memoryLimitBytes';
let usageCounterName = 'memoryRssBytes';
KubePodInventory
| where TimeGenerated < endDateTime
| where TimeGenerated >= startDateTime
| extend InstanceName = strcat(ClusterId, '/', ContainerName),
         ContainerName = strcat(Namespace, '/', tostring(split(ContainerName, '/')[1]))
| distinct Computer, InstanceName, ContainerName
| join hint.strategy=shuffle (
    Perf
    | where TimeGenerated < endDateTime
    | where TimeGenerated >= startDateTime
    | where ObjectName == 'K8SContainer'
    | where CounterName == capacityCounterName
    | summarize LimitValue = max(CounterValue) by Computer, InstanceName, bin(TimeGenerated, trendBinSize)
    | project Computer, InstanceName, LimitStartTime = TimeGenerated, LimitEndTime = TimeGenerated + trendBinSize, LimitValue
) on Computer, InstanceName
```

![](/images/2020/2020-01-28-09-45-25.png){:class="img-fluid"}

Výborně. Dalším joinem přidáme totéž pro skutečnou spotřebu a opět mě zajímá maximum.

```
let threshold = 90;
let endDateTime = now();
let startDateTime = ago(5m);
let trendBinSize = 1m;
let capacityCounterName = 'memoryLimitBytes';
let usageCounterName = 'memoryRssBytes';
KubePodInventory
| where TimeGenerated < endDateTime
| where TimeGenerated >= startDateTime
| extend InstanceName = strcat(ClusterId, '/', ContainerName),
         ContainerName = strcat(Namespace, '/', tostring(split(ContainerName, '/')[1]))
| distinct Computer, InstanceName, ContainerName
| join hint.strategy=shuffle (
    Perf
    | where TimeGenerated < endDateTime
    | where TimeGenerated >= startDateTime
    | where ObjectName == 'K8SContainer'
    | where CounterName == capacityCounterName
    | summarize LimitValue = max(CounterValue) by Computer, InstanceName, bin(TimeGenerated, trendBinSize)
    | project Computer, InstanceName, LimitStartTime = TimeGenerated, LimitEndTime = TimeGenerated + trendBinSize, LimitValue
) on Computer, InstanceName
| join kind=inner hint.strategy=shuffle (
    Perf
    | where TimeGenerated < endDateTime + trendBinSize
    | where TimeGenerated >= startDateTime - trendBinSize
    | where ObjectName == 'K8SContainer'
    | where CounterName == usageCounterName
    | project Computer, InstanceName, UsageValue = CounterValue, TimeGenerated
) on Computer, InstanceName
```

![](/images/2020/2020-01-28-09-47-28.png){:class="img-fluid"}

Zbývá očistit časově, zobrazit méně sloupců, vypočítat procento a to následně sumarizovat podle kontejneru a najít jeho maximální hodnotu. Teď udělat filtr na to, že procento je větší než sledovaný threshold.

```
let threshold = 90;
let endDateTime = now();
let startDateTime = ago(5m);
let trendBinSize = 1m;
let capacityCounterName = 'memoryLimitBytes';
let usageCounterName = 'memoryRssBytes';
KubePodInventory
| where TimeGenerated < endDateTime
| where TimeGenerated >= startDateTime
| extend InstanceName = strcat(ClusterId, '/', ContainerName),
         ContainerName = strcat(Namespace, '/', tostring(split(ContainerName, '/')[1]))
| distinct Computer, InstanceName, ContainerName
| join hint.strategy=shuffle (
    Perf
    | where TimeGenerated < endDateTime
    | where TimeGenerated >= startDateTime
    | where ObjectName == 'K8SContainer'
    | where CounterName == capacityCounterName
    | summarize LimitValue = max(CounterValue) by Computer, InstanceName, bin(TimeGenerated, trendBinSize)
    | project Computer, InstanceName, LimitStartTime = TimeGenerated, LimitEndTime = TimeGenerated + trendBinSize, LimitValue
) on Computer, InstanceName
| join kind=inner hint.strategy=shuffle (
    Perf
    | where TimeGenerated < endDateTime + trendBinSize
    | where TimeGenerated >= startDateTime - trendBinSize
    | where ObjectName == 'K8SContainer'
    | where CounterName == usageCounterName
    | project Computer, InstanceName, UsageValue = CounterValue, TimeGenerated
) on Computer, InstanceName
| where TimeGenerated >= LimitStartTime and TimeGenerated < LimitEndTime
| project Computer, ContainerName, TimeGenerated, UsagePercent = UsageValue * 100.0 / LimitValue
| summarize MaxUsage = max(UsagePercent) by ContainerName
| where MaxUsage > threshold
```

Výsledkem je jednoduchá tabulka obsahující hezký název kontejneru a maximální obsazenost paměti vzhledem k nastavenému limitu a odfiltrováno od 90% nahoru. Já v prostředí takový kontejner nemám, tak jsem zrušil poslední řádek s filtrací a vypadá to takhle:

![](/images/2020/2020-01-28-09-50-58.png){:class="img-fluid"}

Teď vrátím where pro filtraci jen těch přes 90% a změnil bych časové okno z 50 dní na 5 minut. Tím vidím, jestli v posledních pěti minutách jsou nějaké kontejnery se spotřebou přes 90%. To už můžu začlenit do alertu a v případě nenulové množiny spustit akci typu push notifikace, email, SMSka nebo Logic App s jakýmkoli workflow (zpráva do Teams apod.). Alert nechám vyhodnocovat situaci (spouštět query) každých minut.

Dnes jsme si v Kusto vyzkoušeli joinování. Někdy příště nás určitě budou zajímat nějaké další podrobnosti ohledně zpracování logů, parsování, pivot tabulky a určitě i různé vizualizace nebo alerty.


