---
layout: post
published: true
title: Azure, Kubernetes, FinOps a strategie účtování nákladů
tags:
- Kubernetes
- Monitoring
---
Jak mám rozúčtovávat svůj Azure Kubernetes Cluster? Podle clusterů? Můžu nějak řešit náklady jednotlivých týmů přes node-pooly? A co přímo jednotlivé mikroslužby? Tahle otázka zní poslední dobou dost často a moje odpověď na ní je - ano, cloudy typu Azure to často nativně do granularity jednotlivých mikroslužeb neumí, ale chtít takovou míru  je mnohdy značně zbytečné a vychází z nepochopení komplexity problému. Pokud jako já žijete v činžáku, podívejte se na rozúčtování vašich nákladů na centrální vytápění - kolik procent nákladů ovlivňujete svým chováním? Přemýšleli jste proč to tak je a proč dokonce je to upraveno vyhláškou? Rozpočítávání nákladů na mikroslužby v clusteru je v tomhle trochu podobné a navíc - opravdu chcete jeden velký multi-tenant cluster s jedním node-poolem pro všechno? Většinou byste neměli. Proberme detaily, ukážeme si strategii pro správné tagování node-poolů a taky jako to řešit kombinací Azure Cost Management s OpenCost projektem pro Kubernetes (open source komponenta komerčního Kubecost).

# FinOps a sledování nákladů
Než se pustíme do podrobností, tak osobně bych ten tolik diskutovaný FinOps nerad redukoval na zpětné účtování jednotlivým projektům. Tato strategie by měla potenciálně zahrnovat mnohem víc:
- Schopnost napočítat náklady budoucích projektů
- Schopnost optimalizovat náklady existujících workloadů
- Zpětovazební smyčka z nákladů operations do vývoje a architektury (ukládat velké obrázky do SQL je finanční pitomost stejně jako naškálovat datový sklad tak, aby stíhal masivní počty zápisů jednoduchých OLTP key-value dat)
- Začlenění finančních aspektů do "změnového řízení" - např. nechť jsou nákladové dopady změn v Infrastructure as Code součástí každého Pull Requestu

Těmto aspektům se chci věnovat někdy příště, dnes se budeme soustředit na rozúčtovávání.

# Multi-tenant Kubernetes
Musíme rozebrat dva zásadní aspekty - sdílení clusteru a sdílení nodů.

## Sdílení clusteru
Kubernetes má nějaké verze a ty major jdou ven třikrát do roka a podpora pro starší verze je jen jeden rok. Upgradovat prostě musíte na poměry klasického enterprise "často". Každá major verze ale přichází se svým seznamem deprecated API - tedy v těchto verzích vám některé stávající věci přestanou fungovat. Třeba ve verzi 1.22 se vám mohl rozbít Ingress nebo CRD, v přicházející verzi 1.26 zase HPA. Nové verze ale zase přinášejí nové vlastnosti a navíc nechcete běžet nějakou, kterou vám cloud nebude supportovat. Jsme u první nevýhody velikánského sdíleného clusteru - některé týmy chtějí upgradovat, aby dostaly nové funkce, ale jiné nejsou připravené a musí svoje deployment YAMLy předělat. Čím víc "multi-tenant" cluster je co do vzdálenosti týmů od sebe, tím větší problém to bude. V rámci mikroslužeb pro jednu aplikaci se dohodnu snáze, než když jsou tam různé aplikace z HR, ale ještě o hodně horší bude, když tam jsou aplikace HR, IT, Finance, ERP a e-comm.

Nezapomínejme také, že jsou některé objekty, které žijí na úrovni celého clusteru. ClusterRole je dle definice celo-clusterová záležitost, definice CRD a různé admission kontrolery typu Gatekeeper/OPA taky nechcete běžet desetkrát. Zejména nadstavbové projekty nemusí nutně podporovat režim, kdy máte pro každý tým jeho vlastní instanci service mesh, ingressu, cert-manageru, Kafka operátora apod. Většinou to jde, ale ... co je pak přínos stejného clusteru, když stejně všechno máte pro jednotlivé týmy zvlášť? Nebo vy ingress sdílíte? Pak zpátky k předchozímu bodu - jak budete koordinovat změny verzí komponent, které přináší nové funkce (to chce jeden tým), ale rozbíjí některé starší (což nechce jiný tým)?

Chápu v on-prem, kde vás postavit cluster možná stálo dva roky života, ale v cloudu je to na zavolání a není důvod počtem clusterů šetřit. Možná máte snahu o overcommit a tím ušetřit, ale k tomu se ještě dostaneme - tak snadné to není.

**V cloudu se nesnažte všechno narvat do jediného clusteru - přiděláváte si hodně práce v oblasti bezpečnosti, monitoringu, správě, podpory i účtování. Hledejte rozumné hranice - nedávejte dohromady test a prod nebo týmy z různých oddělení.**

## Sdílení nodů
Dobrá, identifikovali jsme tedy týmy, pro které má smysl sdílet cluster - jsou ze stejného oddělení, mají podobné zaměření, podobnou rychlost vývoje a určitě se spolu domluví. Výborně. Pak se tedy věnujme tomu, jestli mají sdílet i jednotlivé nody nebo má mít každý tým vyhrazenou svou vlastní sadu nodů. Co je potíž při sdílení nodu?
- Obligátní problém s nastavováním requestů a limitů, kdy někdo, kdo to pokazí, může nepříznivě ovlivnit ostatní. Jasně, můžeme to vynucovat třeba přes Azure Policy (potažmo Open Policy Agent s Gatekeeper), ale to je významná složitost navíc. Nestačí kontrolovat, že je nastaven limit, když někdo limit nastaví na velikost celého nodu. Fajn, tak uděláte politiky, že limit je maximálně 4 CPU? A co když legitimně potřebuji víc? Rozjedeme tedy spirálu výjimek? Uspravujeme to?
- Kontejnery se ovlivňují i v aspektech, které resource management Kubernetu aktuálně neřeší. Tak například kernel má limit na množství spuštěných procesů - pokud ve svém kontejneru vyžeru všechny, nic jiného na nodu už nepoběží. Používám emptydir? Pak jde o společný disk - co když mu někdo vyžere I/O? Jasně, tak budeme na všechno mít Volume a to je lepší (ale dražší) - jenže node má taky limity v maximálním I/O směrem do storage a do sítě, budeme tedy hrát na to, že je tak vysoko, že to nikdo nerozbije? 
- Z bezpečnostního hlediska byste měli u oddělení procesů považovat za precizně oddělené jen to, co je implementováno v HW, tedy např. s využitím VT-X instrukcí - a to je hypervisor, tedy VM mezi sebou. Uvnitř jediného VM je oddělení kontejnerů dáno jen funkcemi kernelu jako jsou namespace, cgroup nebo chroot. To je významně menší garance - o vrstvu méně.

**To co máte ve stejném clusteru ne vždy chcete, aby sdílelo nody z důvodu bezpečnosti, předvídatelnosti a ochrany před vzájemným ovlivňováním. Zvažte použití separátních node-pool a například uzamčení namespace projektu jen na jeden určitý. Získáte tak i samostatnost pro každý tým, ať zvolí vlastní strategii správy zdrojů - autoškálování, rezervace, savings plány, použitý typ VM.**

## Problém rozpočítání společného topení
Dostáváme se dovnitř projektu a jeho mikroslužeb, kde je sdílení nodu žádoucí, protože vejde k overcommitu a tím potenciálně lepší efektivitě využití cloudových zdrojů. Dále je tu efekt fragmentace - velké kontejnery se špatně trefují do relativně malých nodů, kde pak zůstává nevyužitá kapacita a problém malého workloadu, kdy malé nody mají větší overhead zdrojů alokovaných pro Kubernetes samotný a fakt, že ideální HA je běžet ve třech zónách dostupnosti (takže bych měl mít alespoň 3 nody a navíc ne malé, ať nemají takový overhead). No a teď k tomu ještě připočtěme overhead nízké granularity pro škálování - příliš velké nody znamenají, že když potřebuji přiškálovat kvůli 2 core, pustím VM s 64 core a 62 je zbytečných, takže pro škálování bych zas raději nody co nejmenší (to mi ale zvyšuje overhead a problém fragmentace). Takže tohle evidentně nebude snadné.

Vraťme se k příkladu z činžáku - podle vyhlášky je 30%-50% společného tepla rozpočítáno na podlahovou plochu bez ohledu na to, co se naměří v jednotlivých bytech. Proč? Já se obvykle spokojím s teplotami kolem 20 stupňů a pro ty pokud není pod nulou nemusím nic dělat - vytopí mě sousedi, kteří asi rádi teploučko. Kdybych měl byt jak bungalov mimo budovu, asi bych měl těžko 20 bez jakéhokoli topení. Správcovská firma tedy provedla nějaké brutální výpočty zahrnující světové strany, okna, zdi sousedů a určila koeficienty. Proč to všechno? Měřáky v bytě zaznamenávají kolik jste přivedli vytápění do svých radiátorů, ale ne kolik tepla přišlo jakou zdí. Nemáme tedy všechny údaje - proto musí přijít aproximace.

Pro jednotlivé clustery nemusím rozpočítávat skoro nic - tam je to jasné, možná tedy outbound traffic z cloudu nebo processing na firewallu, ale to není nic neobvyklého. Na to jsou v Azure Cost Management nástroje jak tyto centrální komponenty rozpočítat. Pro jednotlivé node-pool do rozpočítání musím přidat poplatek za SLA master nodů AKS (to je ale asi 70 USD na cluster, takže to není nic zásadního) a případě systémový node-pool, pokud používám (doporučuji používat a dát na něj i sdílené komponenty typu Ingress kontroler). 

Kde to začne být komplikované je, když půjdeme na úroveň sdílených nodů. Tam samozřejmě potřebujeme sledovat kdy kolik Podů běželo a komu patřilo. Navíc ale tady budeme muset řešit neefektivitu typu nevyužité zdroje na nodu a komu je rozúčtovat. Tohle by asi mělo být rovnoměrně rozděleno mezi všechny, co prostředky sdílí. Jenže - co když někdo způsobí, že cluster je přiškálován a kvůli jednomu workload nepracuje efektivně (workload má velké Pody a tím způsobuje fragmentační problém a tedy rostoucí overhead nebo díky právě tomuto workloadu musíme přidat další node, který bychom jinak nepotřebovali a který je prakticky prázdný). A co teprve když Pod využívá emptydir díky čemuž znesnadní clusteru seškálovat zpět - klasický autoscaler není nějak superchytrý a pokud se nemáme chovat k Podům nějak neurvale (což může třeba jednomu týmu vadit - být zabíjeni a přicházet o obsah emptydir zbytečně), tak efektivně jeden workload může zařídit, že cluster neseškáluje zpět a vzniknou náklady. Co s tím? To přece není spravedlivé? Připadá mi to jako situace, kdy se při rozpočítávání některých poplatků v činžáku používá počet osob (třeba u rozpočítání odpadů) a neustálé hádky, proč má někdo nahlášeno 4, ale vypadá to, že jich je tam 5 - je to strejda na návštěvě? Jak dlouho musí být na návštěvě, aby se měl podíl bytu zvednout? 

**Rozpočítávání je relativně snadné u separátních clusterů a podle vícero node-pool. U sdílených nodů je nutné sledovat aktuální obsazenost v čase a zvolit strategii na rozpočítání nevyužitých zdrojů.**

# Praktické rozpočítávání
Podívejme se prakticky na řešení s využitím nativních Azure nástrojů (scénář se sdíleným clusterem a izolací přes node-pooly) a pak na OpenCost pro ještě granulárnější počítání nákladů uvnitř clusteru. Všechno najdete jako obvykle automatizované na mém GitHubu: [https://github.com/tkubica12/azure-workshops/tree/main/d-aks-cost-management](https://github.com/tkubica12/azure-workshops/tree/main/d-aks-cost-management)

## Finanční analýza AKS clusterů a node-poolů

### Základní model a zajištění správných tagů

V popsaném modelu využívání AKS bych měl vždy oddělené clustery pro týmy, které mají k sobě daleko. "Vzdálenost" týmů je totiž nejen o jejich schopnosti se dohodnout, ale má i účetní, organizační nebo dokonce právní či regulatorní důsledky - zkrátka náklady musí být přesné. V takovém případě doporučuji workload rozdělit do separátních subskripcí, protože pak to máte celkem bez práce a nemůžete se splést.

Jiná situace je u provozování několika clusterů v jediné subskripci či dokonce Resource Group nebo pro případ, kdy máme cluster jen jeden a vytváříme node-pool pro každý tým. Tam bude potřeba řešit tagování a to tady je pár tipů jak na to:
- Při vytváření AKS si můžete určit tag - využijte toho. Tento se propíše na cluster samotný a komponenty clusteru jako je jeho public IP, Load Balancer apod. Pod ním tedy najdete relativně levné věci clusteru - nějaké to síťování, SLA na API server a tak.
- Každý nodepool může mít svůj vlastní tag a to je důležité, protože tady se bavíme o hlavní nákladové položce. Pokud máte účtování na úrovni clusterů, dejte každému stejný tag jako clusteru. Pokud jedete režimem účtuji podle nodepool, pak doporučuji (a je to dobré i z hlediska výkonnosti a stability) udělat 3-členný node-pool jako systémový node a na něm provozovat pouze oficiální systémové Pody + takové, které berete jako součást sdíleného řešení clusteru (třeba Ingress implementaci) a tomu dejte stejný tag jako clusteru (to oboje pro nás bude představovat sdílené prostředí clusteru). Pak už dělejte node-pool pro každý tým a dejte mu unikátní tag.
- Namespace mají možnost být přiřazeni k node-pool a to je dobrý způsob jak zajistit, aby tým nelezl do cizího. Dejme tomu že má tým potřebu 3 namespace, ale je to jeden tým - o zdrojích se dohodnou. Pak jim uděláme node-pool, dáme mu účetní tag a založíme 3 namespace, které budou svázané s tímto node-poolem.
- Některé zdroje si Kubernetes vytváří sám a z těch, co žerou hodně peněz jsou to hlavně disky (PV/PVC), ale týká se to i věcí typu Public IP pro služby (ačkoli tam jsou náklady malé). Tady si musíte tagy ohlídat zevnitř Kubernetu použitím anotací.
- Kromě tagů, kterým říkám L2 (tedy vlastní to konkrétní tým nebo je to shared komponenta typu system pool) dejte ke každému zdroji i společný tag pro všechno, co se clusteru týká (tomu říkám L1). Tím si budete moci odfiltrovat konkrétní cluster (L1 tag) a v něm seskupovat podle vlastnictví (L2 tag).

V mém praktickém případě je úroveň cluster (první úroveň) řešena tagem L1=AKS01, který chci dávat všem zdrojům, abych tak jednoduše našel celkové náklady clusteru. Současně v L2 budu řešit komu zdroj patří a proto u komponent clusteru a default nodepoolu bude L2=AKS01-SHARED (to potřebujeme, abychom potom mohli tyto náklady alokovat na týmy). Tady jak to vypadá v Terraformu:

```
resource "azurerm_kubernetes_cluster" "aks1" {
  name                = "d-kubecost"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "d-kubecost"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_B2ms"

    tags = {
      L1 = "AKS01",
      L2 = "AKS01-SHARED"
    }

    node_labels = {
      L1 = "AKS01",
      L2 = "AKS01-SHARED"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    L1 = "AKS01",
    L2 = "AKS01-SHARED"
  }
}
```

Pak pro jednotlivé týmy T01 a T02 (L2 úroveň) vytvářím jejich node-pooly s příslušnými tagy.

```
resource "azurerm_kubernetes_cluster_node_pool" "aks1_pool1" {
  name                  = "pool1"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks1.id
  vm_size               = "Standard_B2ms"
  node_count            = 2

  tags = {
    L1 = "AKS01",
    L2 = "AKS01-T01"
  }

  node_labels = {
    L1 = "AKS01",
    L2 = "AKS01-T01"
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "aks1_pool2" {
  name                  = "pool2"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks1.id
  vm_size               = "Standard_B2ms"
  node_count            = 1

  tags = {
    L1 = "AKS01",
    L2 = "AKS01-T02"
  }

  node_labels = {
    L1 = "AKS01",
    L2 = "AKS01-T02"
  }
}
```

Namespace jsem pak svázal s node-pooly - mám tu dva namespace pro každý tým.

{% raw %}
```
apiVersion: v1
kind: Namespace
metadata:
  name: t01-a
  labels:
    L1: {{ .Values.L1 }}
    L2: {{ .Values.L1 }}-T01
    L3: {{ .Values.L1 }}-T01-A
  annotations:
    scheduler.alpha.kubernetes.io/node-selector: L2={{ .Values.L1 }}-T01
---
apiVersion: v1
kind: Namespace
metadata:
  name: t01-b
  labels:
    L1: {{ .Values.L1 }}
    L2: {{ .Values.L1 }}-T01
    L3: {{ .Values.L1 }}-T01-B
  annotations:
    scheduler.alpha.kubernetes.io/node-selector: L2={{ .Values.L1 }}-T01
---
apiVersion: v1
kind: Namespace
metadata:
  name: t02-a
  labels:
    L1: {{ .Values.L1 }}
    L2: {{ .Values.L1 }}-T02
    L3: {{ .Values.L1 }}-T02-A
  annotations:
    scheduler.alpha.kubernetes.io/node-selector: L2={{ .Values.L1 }}-T02
---
apiVersion: v1
kind: Namespace
metadata:
  name: t02-b
  labels:
    L1: {{ .Values.L1 }}
    L2: {{ .Values.L1 }}-T02
    L3: {{ .Values.L1 }}-T02-B
  annotations:
    scheduler.alpha.kubernetes.io/node-selector: L2={{ .Values.L1 }}-T02
```
{% endraw %}

Jak s PVC? Tam se tagování dá určit na základě Storage Class. Udělal jsem tedy pro každý tým separátní storage class a zajistil správné tagování (tady je Helm šablona):

{% raw %}
```
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: storage-t01
provisioner: disk.csi.azure.com
parameters:
  skuname: Premium_LRS 
  tags: "L1={{ .Values.L1 }},L2={{ .Values.L1 }}-T01"
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: storage-t02
provisioner: disk.csi.azure.com
parameters:
  skuname: Premium_LRS 
  tags: "L1={{ .Values.L1 }},L2={{ .Values.L1 }}-T02"
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: t01-a-app1
  namespace: t01-a
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: storage-t01
  resources:
    requests:
      storage: 16Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: t01-b-app1
  namespace: t01-b
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: storage-t01
  resources:
    requests:
      storage: 128Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: t02-a-app1
  namespace: t02-a
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: storage-t02
  resources:
    requests:
      storage: 128Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: t02-b-app1
  namespace: t02-b
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: storage-t02
  resources:
    requests:
      storage: 128Gi
```
{% endraw %}

Pak jsem přidal služby.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: t01-a-app1
  namespace: t01-a
  annotations:
    service.beta.kubernetes.io/azure-pip-tags: "L1={{ .Values.L1 }},L2={{ .Values.L1 }}-T01"
spec:
  type: LoadBalancer
  selector:
    app: t01-a-app1
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: t01-b-app1
  namespace: t01-b
  annotations:
    service.beta.kubernetes.io/azure-pip-tags: "L1={{ .Values.L1 }},L2={{ .Values.L1 }}-T01"
spec:
  type: LoadBalancer
  selector:
    app: t01-b-app1
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: t02-b-app1
  namespace: t02-a
  annotations:
    service.beta.kubernetes.io/azure-pip-tags: "L1={{ .Values.L1 }},L2={{ .Values.L1 }}-T02"
spec:
  type: LoadBalancer
  selector:
    app: t02-a-app1
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: t02-b-app1
  namespace: t02-b
  annotations:
    service.beta.kubernetes.io/azure-pip-tags: "L1={{ .Values.L1 }},L2={{ .Values.L1 }}-T02"
spec:
  type: LoadBalancer
  selector:
    app: t02-b-app1
  ports:
  - port: 80
    targetPort: 80
```

Následně deploymenty (tam už není nic zajímavého, všechny zdroje najdete na mém GitHubu).

Když se podívám na jednotlivé komponenty, tak mají potřebné tagy - tady je například jeden z Volume.

[![](/images/2022/2022-12-19-17-40-52.png){:class="img-fluid"}](/images/2022/2022-12-19-17-40-52.png)

Aplikační node-pool

[![](/images/2022/2022-12-19-17-41-26.png){:class="img-fluid"}](/images/2022/2022-12-19-17-41-26.png)

Systémový node-pool

[![](/images/2022/2022-12-19-17-41-58.png){:class="img-fluid"}](/images/2022/2022-12-19-17-41-58.png)

Public IP

[![](/images/2022/2022-12-19-17-42-22.png){:class="img-fluid"}](/images/2022/2022-12-19-17-42-22.png)

### Pohled v Azure Cost Managementu

Máme tedy vše potřebné pro finanční analýzu v Azure Cost Management. Pokud používáte novou funkci v preview na dědění tagů z resource group na zdroje, ujistěte se, že tag u zdroje má přednost a není ignorován (MC_ rg totiž bude mít tag clusteru včetně L2=AKS01-SHARED, ale zdroje uvnitř budou mít L2 tagy jiné tak, jak jsme specifikovali).

[![](/images/2022/2022-12-20-10-48-56.png){:class="img-fluid"}](/images/2022/2022-12-20-10-48-56.png)

Takhle si zobrazím rozpad nákladů clusteru - ve filtru si vyberu L1=AKS01 a nechám náklady seskupit podle L2 tagu. Tím získáme náklady sdílené a za jednotlivé node-pooly (týmy).

[![](/images/2022/2022-12-20-17-43-21.png){:class="img-fluid"}](/images/2022/2022-12-20-17-43-21.png)

Dají se s tím samozřejmě dělat další pohledy, alerty, exporty - to je jasné, tenhle článek není o Azure Cost Management, takže to už najdete v dokumentaci. Takhle bych například mohl udělat alert pro tým T01 v clusteru AKS01 tak, že se spustí nějaká akce (email, SMS, Teams zpráva, orchestrační workflow, Azure Function, ticket do ServiceNow apod.) pokud se překročí nebo přiblíží limitu nákladů a to jak ve skutečné hodnotě za například stávající měsíc nebo na základě predikce do konce měsíce (tzn. upozornění typu "jestli takhle budeš pokračovat dál, na konci měsíce přešvihneš rozpočet"). Jen nezapomínejte, že Azure Cost Management vyhodnocuje data v dávkách, takže obvykle trvá tak 12-24 hodin, než se nová spotřeba objeví. 

[![](/images/2022/2022-12-20-17-47-30.png){:class="img-fluid"}](/images/2022/2022-12-20-17-47-30.png)

Je tu ale ještě jedna otázka - sdílené náklady. Co s nimi?

### Sdílené náklady
Problematika sdílených nákladů je široká a obvykle zahrnuje i věci jako rozpočítání Express Route, Azure Firewallu a dalších komponent. To teď nechme stranou a zaměřme se vyloženě na AKS. Samozřejmě napočítáme nejdřív dedikované náklady za node-pool týmu, jejich disky PV/PVC apod. (to jsme vyřešili tagováním). Otázkou je, zda jim to přeúčtujeme 1:1 nebo si na to hodíte nějaký servisní poplatek ať už ve fixní sazbě nebo v procentu navíc (poplatek za to, že jim cluster a node-pool vytvoříte a nabídnete první vrstvu podpory či konzultací - coby platformní tým). 

Jakou můžeme zvolit strategii na ty sdílené části? A připomeňme, že tyto části AKS pravděpodobně nebudou velké procento celkové útraty (na rozdíl od rozpuštění drahých komponent typu Express Route).

- Týmům budeme účtovat fixní poplatek za to, že tam vůbec jsou. Vychází to z předpokladu, že skutečné náklady za Azure vlastně nejsou to podstatné - platformní tým pro vás musí node-pool vytvořit, spravovat a je vám často k dispozici jako první vrstva podpory. To ve finále stojí daleko víc, takže varianta nemít uplift na individuální spotřebu, ale sdílené části a poplatek za možnost v clusteru být sfouknout paušálem může dávat smysl. Nebo to uděláte z důvodu jednoduchosti - proč se pro pár dolarů tak natrápit, tak ať je to jednoduché - 20 USD za sdílené komponenty pro každý node-pool a hotovo.
- Sdílené náklady přeúčtujete týmům poměrově podle jejich finanční spotřeby ať už za všechny cloudové služby přímo spojené s clusterem (compute a disky) nebo třeba jen podle compute (vyjdete z toho, že zátěž sdílených komponent jako je system node-pool nebo Ingress je poměrově blízko poměrům v compute, ty naznačují množství aplikací - storage na to vliv nemá).
- Sdílené náklady ručně rozprostřete nějakým procentem dle dohody - všichni stejně nebo hlavní uživatelé každý po 20% nebo tak nějak.

Toho dosáhnete s využitím Azure Cost Managementu. Ten v preview podporuje alokace nákladů, kde dokážete vzít sdílené náklady (identifikované subskripcí, resource group nebo právě tagem) a přesunete je do jiné škatulky (opět identifikované subskripcí, resource group nebo tagem). Alokační pravidla mohou být například podle celkových Azure nákladů, nákladů za compute nebo podle ručně stanovených vah. V našem případě bychom tedy udělali to, že tag L2=AKS01-SHARED rozdělíme v nějakém dynamickém nebo statickém poměru do L2=AKS-T01 a L2=AKS-T02. Víc čtěte v [dokumentaci](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/allocate-costs).

Za mě - pro většinu mých enterprise zákazníků je tento režim účtování po clusterech a následně node-poolech naprosto dostatečný a přitom to není složité.

## Maximální granularita s OpenCost projektem
Jak už jsem naznačoval - pro mě je vyšší granularita důležitá spíše pro nějaké vnitřní pochopení v rámci týmu (která mikroslužba je největší žrout peněz), než nějaké právně platné skutečné přeúčtovávání a hádání se o výsledcích. Obyčejný monitoring tak často může stačit k tomu udělat si představu, kdo ten žrout je - třeba s Azure Monitor Container Insights to není problém, stačí nasadit nějakou vhodnou strategii na labely Kubernetes prostředků nebo dobře zvolit namespace (proto v mé ukázce je u namespace ještě L3 tag). Ale někdy pohled na statistiku zátěže nemusí stačit - třeba vás trápí, že si někdo alokuje (resource requests) velké množství zdrojů a při tom je vůbec nepoužívá (takže snižuje možnost sdílení prostředků, tedy zvyšuje cenu). Někdo jiný zase resource request dává nesmyslně malé a spoléhá se na to, že si přes bursting sežere co mu kdo dá (hraje na velký overcommit, čímž sice sobě snižuje náklady, ale destabilizuje celé prostředí - agresivní overcommit má vždy tendenci se vymstít v okamžiku, kdy vzroste skutečná potřeba zdrojů pro všechny mikroslužby - pak se to pořeže mezi sebou a cluster ani neví, že by měl přiškálovat, protože scheduler se orientuje podle requestů, ne podle reálných požadavků na zdroje).

V takových situacích tedy využijeme něco, co by měřilo spotřebu jednotlivých Podů co do CPU, RAM a GPU a Volume co do diskového prostoru. Tohle potřebujeme uložit s potřebnými metadaty tak, aby bylo následně možné dělat agregace podle kontroleru, namespace a tak podobně. To tedy znamená sbírat historické údaje a třeba každou minutu spočítat kolik co sežralo, aby nám z toho na konci vyšly nějaké ty CPU-hodiny, RAM-hodiny a tak podobně. Z čeho to ale počítat? Optimální metodika je vzít požadovanou alokaci (requesty, tedy garantované zdroje a za ty byste měli platit bez ohledu na to, jak moc je využíváte) nebo skutečnou zátěž podle toho co je vyšší (pokud Pod vezme víc než jeho resource request až do úrovně resource limit, tak je to v pořádku, ale neměl by to mít zadarmo). Jinak řečeno svoje requesty platíte vždy a co si vezmete nad to platíte dle skutečné zátěže. 

Existuje jeden nástroj, který je v této oblasti velmi oblíbený - jde o komerční řešení Kubecost a funguje velmi dobře. Jde ale o dost dál - snaží se z tagů postahovat i spotřebu jiných zdrojů v cloudu, než jen Kubernetes, dělá vizualizace, umožňuje alokace sdílených zdrojů (pozor - sdíleným zdrojem je v tomto scénáři i nespotřebovaný výkon nodů, takže spravedlnost rozdělení je ještě zapeklitější téma, než v předchozí kapitolce). Zkrátka stává se z něj "konkurence" pro jiné cloudové cost management nástroje včetně Azure Cost Management (ten je pro Azure zdarma, ale pokud ho chcete použít pro multi-cloud, zdroje z AWS a GCP jsou placené). Myslím, že udělali jeden velmi dobrý krok - oddělili základní koncept správy nákladů v Kubernetu a software pro sběr této telemetrie od přidané hodnoty Kubecost. Vznikl tak projekt [OpenCost](https://www.opencost.io/) a to je to telemetrické jádro z KubeCost a současně specifikace metodologie a "API" [https://github.com/opencost/opencost/blob/develop/spec/opencost-specv01.md](https://github.com/opencost/opencost/blob/develop/spec/opencost-specv01.md). Doporučuji přečíst.

OpenCost tedy zajistí měření podle toho jak jsem to popsal v předchozím odstavci a navíc pro tři největší cloudy si přes jejich API umí vytáhnout finanční podklady, takže vám zobrazuje přímo peníze. V KubeCost máte možnost si přinést vlastní ceníky a i jinými způsoby to ovlivnit a předpokládám, že pro OpenCost to půjde taky, byť to zatím v dokumentaci nevidím (je to hodně hodně čerstvé - resp. to jádro z KubeCost je skvělé, stabilní a dlouho k dispozici, ale oddělení do samostatného projektu ještě trochu kulhá co do dokumentace). Dokonce tohle celé jde do CNCF a bylo před pár dny přijato jako CNCF Sandbox projekt a to je skvělá zpráva.

OpenCost jsem v clusteru nahodil a příslušné Helm šablony a parametry najdete na mém [GitHubu](https://github.com/tkubica12/azure-workshops/tree/main/d-aks-cost-management).

UI je skutečně pouze základní, ale ukazuje co je potřeba. Tady například v sumarizaci za namespace. 

[![](/images/2022/2022-12-19-19-02-28.png){:class="img-fluid"}](/images/2022/2022-12-19-19-02-28.png)

Pokud se podíváme do API, uvidíme podkladová čísla.

```bash
curl http://20.31.220.228:9090/allocation/compute \
  -d window=1d \
  -d step=1d \
  -d resolution=10m \
  -d aggregate=namespace \
  -d accumulate=false \
  -G | jq
```

```json
{
  "code": 200,
  "status": "success",
  "data": [
    {
      "__unmounted__": {
        "name": "__unmounted__",
        "properties": {
          "cluster": "L1-A",
          "container": "__unmounted__",
          "namespace": "__unmounted__",
          "pod": "__unmounted__"
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-18T18:04:36Z",
        "end": "2022-12-19T18:04:36Z",
        "minutes": 1440,
        "cpuCores": 0,
        "cpuCoreRequestAverage": 0,
        "cpuCoreUsageAverage": 0,
        "cpuCoreHours": 0,
        "cpuCost": 0,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 0,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 292057776128,
        "pvByteHours": 7009386627072,
        "pvCost": 0.357699,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 0,
        "ramByteRequestAverage": 0,
        "ramByteUsageAverage": 0,
        "ramByteHours": 0,
        "ramCost": 0,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.357699,
        "totalEfficiency": 0,
        "rawAllocationOnly": null
      },
      "grafana": {
        "name": "grafana",
        "properties": {
          "cluster": "L1-A",
          "node": "aks-default-35670873-vmss000000",
          "container": "grafana",
          "controller": "grafana",
          "controllerKind": "deployment",
          "namespace": "grafana",
          "pod": "grafana-589d5f4c8b-wphn8",
          "services": [
            "grafana"
          ],
          "providerID": "azure:///subscriptions/d3b7888f-c26e-4961-a976-ff9d5b31dfd3/resourceGroups/mc_d-kubecost_d-kubecost_westeurope/providers/Microsoft.Compute/virtualMachineScaleSets/aks-default-35670873-vmss/virtualMachines/0",
          "labels": {
            "app_kubernetes_io_instance": "grafana",
            "app_kubernetes_io_name": "grafana",
            "kubernetes_io_metadata_name": "grafana",
            "name": "grafana",
            "pod_template_hash": "589d5f4c8b"
          }
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-19T15:10:00Z",
        "end": "2022-12-19T18:00:00Z",
        "minutes": 170,
        "cpuCores": 0,
        "cpuCoreRequestAverage": 0,
        "cpuCoreUsageAverage": 0.000134,
        "cpuCoreHours": 0,
        "cpuCost": 0,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 0,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0.070833,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 0,
        "pvByteHours": 0,
        "pvCost": 0,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 0,
        "ramByteRequestAverage": 0,
        "ramByteUsageAverage": 57045362.120482,
        "ramByteHours": 0,
        "ramCost": 0,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.070833,
        "totalEfficiency": 0,
        "rawAllocationOnly": {
          "cpuCoreUsageMax": 0.0001341646533851292,
          "ramByteUsageMax": 57307136
        }
      },
      "ingress-nginx": {
        "name": "ingress-nginx",
        "properties": {
          "cluster": "L1-A",
          "node": "aks-default-35670873-vmss000000",
          "container": "controller",
          "controller": "ingress-nginx-controller",
          "controllerKind": "deployment",
          "namespace": "ingress-nginx",
          "pod": "ingress-nginx-controller-7d5fb757db-7d7v2",
          "services": [
            "ingress-nginx-controller-admission",
            "ingress-nginx-controller"
          ],
          "providerID": "azure:///subscriptions/d3b7888f-c26e-4961-a976-ff9d5b31dfd3/resourceGroups/mc_d-kubecost_d-kubecost_westeurope/providers/Microsoft.Compute/virtualMachineScaleSets/aks-default-35670873-vmss/virtualMachines/0",
          "labels": {
            "app_kubernetes_io_component": "controller",
            "app_kubernetes_io_instance": "ingress-nginx",
            "app_kubernetes_io_name": "ingress-nginx",
            "kubernetes_io_metadata_name": "ingress-nginx",
            "name": "ingress-nginx",
            "pod_template_hash": "7d5fb757db"
          }
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-19T15:10:00Z",
        "end": "2022-12-19T18:00:00Z",
        "minutes": 170,
        "cpuCores": 0.1,
        "cpuCoreRequestAverage": 0.1,
        "cpuCoreUsageAverage": 0.000128,
        "cpuCoreHours": 0.283333,
        "cpuCost": 0.01105,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 0.001283,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0.070833,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 0,
        "pvByteHours": 0,
        "pvCost": 0,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 94371840,
        "ramByteRequestAverage": 94371840,
        "ramByteUsageAverage": 77513444.240964,
        "ramByteHours": 267386880,
        "ramCost": 0.000477,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0.821362,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.082361,
        "totalEfficiency": 0.035244,
        "rawAllocationOnly": {
          "cpuCoreUsageMax": 0.00012827478624659585,
          "ramByteUsageMax": 81104896
        }
      },
      "kube-system": {
        "name": "kube-system",
        "properties": {
          "cluster": "L1-A",
          "namespace": "kube-system"
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-19T15:10:00Z",
        "end": "2022-12-19T18:00:00Z",
        "minutes": 170,
        "cpuCores": 1.588,
        "cpuCoreRequestAverage": 1.588,
        "cpuCoreUsageAverage": 0.003501,
        "cpuCoreHours": 4.499333,
        "cpuCost": 0.175474,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 0.002204,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 0,
        "pvByteHours": 0,
        "pvCost": 0,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 1237319680,
        "ramByteRequestAverage": 1237319680,
        "ramByteUsageAverage": 695693086.274084,
        "ramByteHours": 3505739093.333333,
        "ramCost": 0.006259,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0.562258,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.181733,
        "totalEfficiency": 0.021493,
        "rawAllocationOnly": null
      },
      "opencost": {
        "name": "opencost",
        "properties": {
          "cluster": "L1-A",
          "node": "aks-default-35670873-vmss000000",
          "controller": "opencost",
          "controllerKind": "deployment",
          "namespace": "opencost",
          "pod": "opencost-7c458684df-rpfmm",
          "providerID": "azure:///subscriptions/d3b7888f-c26e-4961-a976-ff9d5b31dfd3/resourceGroups/mc_d-kubecost_d-kubecost_westeurope/providers/Microsoft.Compute/virtualMachineScaleSets/aks-default-35670873-vmss/virtualMachines/0"
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-19T15:10:00Z",
        "end": "2022-12-19T18:00:00Z",
        "minutes": 170,
        "cpuCores": 0.02,
        "cpuCoreRequestAverage": 0.02,
        "cpuCoreUsageAverage": 0.00034,
        "cpuCoreHours": 0.056667,
        "cpuCost": 0.00221,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 0.016997,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0.070833,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 0,
        "pvByteHours": 0,
        "pvCost": 0,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 110000000,
        "ramByteRequestAverage": 110000000,
        "ramByteUsageAverage": 52131765.975904,
        "ramByteHours": 311666666.666667,
        "ramCost": 0.000556,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0.473925,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.0736,
        "totalEfficiency": 0.108902,
        "rawAllocationOnly": null
      },
      "prometheus": {
        "name": "prometheus",
        "properties": {
          "cluster": "L1-A",
          "namespace": "prometheus"
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-19T15:10:00Z",
        "end": "2022-12-19T18:00:00Z",
        "minutes": 170,
        "cpuCores": 0,
        "cpuCoreRequestAverage": 0,
        "cpuCoreUsageAverage": 0.001055,
        "cpuCoreHours": 0,
        "cpuCost": 0,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 0,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 16270346697.788233,
        "pvByteHours": 46099315643.73333,
        "pvCost": 0.002353,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 0,
        "ramByteRequestAverage": 0,
        "ramByteUsageAverage": 408684883.314494,
        "ramByteHours": 0,
        "ramCost": 0,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.002353,
        "totalEfficiency": 0,
        "rawAllocationOnly": null
      },
      "t01-a": {
        "name": "t01-a",
        "properties": {
          "cluster": "L1-A",
          "container": "nginx",
          "controllerKind": "deployment",
          "namespace": "t01-a"
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-19T15:30:00Z",
        "end": "2022-12-19T18:00:00Z",
        "minutes": 150,
        "cpuCores": 0.3,
        "cpuCoreRequestAverage": 0.3,
        "cpuCoreUsageAverage": 1e-05,
        "cpuCoreHours": 0.75,
        "cpuCost": 0.02925,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 3.3e-05,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0.0625,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 12827635657.386667,
        "pvByteHours": 32069089143.466667,
        "pvCost": 0.0019,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 167772160,
        "ramByteRequestAverage": 167772160,
        "ramByteUsageAverage": 13979639.399475,
        "ramByteHours": 419430400,
        "ramCost": 0.000749,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0.083325,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.094398,
        "totalEfficiency": 0.002112,
        "rawAllocationOnly": null
      },
      "t01-b": {
        "name": "t01-b",
        "properties": {
          "cluster": "L1-A",
          "container": "nginx",
          "controllerKind": "deployment",
          "namespace": "t01-b"
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-19T15:30:00Z",
        "end": "2022-12-19T18:00:00Z",
        "minutes": 150,
        "cpuCores": 0.65,
        "cpuCoreRequestAverage": 0.65,
        "cpuCoreUsageAverage": 1.1e-05,
        "cpuCoreHours": 1.625,
        "cpuCost": 0.063375,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 1.7e-05,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0.0625,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 10078856587.946667,
        "pvByteHours": 25197141469.866665,
        "pvCost": 0.001286,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 436207616,
        "ramByteRequestAverage": 436207616,
        "ramByteUsageAverage": 17506955.302796,
        "ramByteHours": 1090519040,
        "ramCost": 0.001947,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0.040134,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.129108,
        "totalEfficiency": 0.001212,
        "rawAllocationOnly": null
      },
      "t02-a": {
        "name": "t02-a",
        "properties": {
          "cluster": "L1-A",
          "node": "aks-pool2-18184209-vmss000000",
          "container": "nginx",
          "controllerKind": "deployment",
          "namespace": "t02-a",
          "providerID": "azure:///subscriptions/d3b7888f-c26e-4961-a976-ff9d5b31dfd3/resourceGroups/mc_d-kubecost_d-kubecost_westeurope/providers/Microsoft.Compute/virtualMachineScaleSets/aks-pool2-18184209-vmss/virtualMachines/0"
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-19T15:30:00Z",
        "end": "2022-12-19T18:00:00Z",
        "minutes": 150,
        "cpuCores": 0.816667,
        "cpuCoreRequestAverage": 0.816667,
        "cpuCoreUsageAverage": 1.3e-05,
        "cpuCoreHours": 2.041667,
        "cpuCost": 0.079625,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 1.6e-05,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0.0625,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 110867422467.41333,
        "pvByteHours": 277168556168.5333,
        "pvCost": 0.014144,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 163298235.733333,
        "ramByteRequestAverage": 163298235.733333,
        "ramByteUsageAverage": 17048801.626475,
        "ramByteHours": 408245589.333333,
        "ramCost": 0.000729,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0.104403,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.156998,
        "totalEfficiency": 0.000963,
        "rawAllocationOnly": null
      },
      "t02-b": {
        "name": "t02-b",
        "properties": {
          "cluster": "L1-A",
          "node": "aks-pool2-18184209-vmss000000",
          "container": "nginx",
          "controllerKind": "deployment",
          "namespace": "t02-b",
          "providerID": "azure:///subscriptions/d3b7888f-c26e-4961-a976-ff9d5b31dfd3/resourceGroups/mc_d-kubecost_d-kubecost_westeurope/providers/Microsoft.Compute/virtualMachineScaleSets/aks-pool2-18184209-vmss/virtualMachines/0"
        },
        "window": {
          "start": "2022-12-18T18:04:36Z",
          "end": "2022-12-19T18:04:36Z"
        },
        "start": "2022-12-19T15:30:00Z",
        "end": "2022-12-19T18:00:00Z",
        "minutes": 150,
        "cpuCores": 0.45,
        "cpuCoreRequestAverage": 0.45,
        "cpuCoreUsageAverage": 1.2e-05,
        "cpuCoreHours": 1.125,
        "cpuCost": 0.043875,
        "cpuCostAdjustment": 0,
        "cpuEfficiency": 2.7e-05,
        "gpuCount": 0,
        "gpuHours": 0,
        "gpuCost": 0,
        "gpuCostAdjustment": 0,
        "networkTransferBytes": 0,
        "networkReceiveBytes": 0,
        "networkCost": 0,
        "networkCostAdjustment": 0,
        "loadBalancerCost": 0.0625,
        "loadBalancerCostAdjustment": 0,
        "pvBytes": 10078856587.946667,
        "pvByteHours": 25197141469.866665,
        "pvCost": 0.001286,
        "pvs": null,
        "pvCostAdjustment": 0,
        "ramBytes": 134217728,
        "ramByteRequestAverage": 134217728,
        "ramByteUsageAverage": 10541403.087842,
        "ramByteHours": 335544320,
        "ramCost": 0.000599,
        "ramCostAdjustment": 0,
        "ramEfficiency": 0.07854,
        "sharedCost": 0,
        "externalCost": 0,
        "totalCost": 0.10826,
        "totalEfficiency": 0.001085,
        "rawAllocationOnly": null
      }
    }
  ]
}
```

Já myslím, že vstupy jsou to naprosto skvělé a takhle samo o sobě to je dostatečné pro to, kde to cítím jako primární použití - porozumění spotřebě v rámci týmů. Sofistikovanější věci typu alokace sdílených zdrojů už jsou na Kubecost nebo nějakou integraci s jiným cost management nástrojem (Azure Cost Management zatím vyčítat zdroje z OpenCost neumí ... moc doufám, že jednou umět bude).

# Datařina aneb megareporty pro všechny
Aktuálně vnímám Azure Cost Management jako optimální nástroj pro FinOps z pohledu sledování nákladů, budgeting, alerting a to všechno včetně sdílených AKS clusterů, pokud používáte nodepooly pro jednotlivé týmy. Mocné, přehledné a hlavně zadarmiko pro Azure. OpenCost je skvělý zdroj dat pro vnitřní účely týmu. Kubecost z něj dokáže vydolovat maximum, ale používat ho na správu celých nákladů v cloudu mi zas přijde nic moc. Určitě prostor pro zlepšení na všech frontách - a pokud vím nástroje v AWS a GCP jsou na tom podobně. Ve všech cloudech najdete návody jak Kubecost využívat (v případě Azure tady [https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/app-platform/aks/cost-governance-with-kubecost](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/app-platform/aks/cost-governance-with-kubecost)), ale o plné integraci do jejich nástrojů správy nákladů se zdá se mi všude zatím mlčí, i když se k plánům pár cloudů přihlásilo.

Nicméně - OpenCost má ještě jednu zajímavost. Všechny metriky dokáže vystrčit do Prometheus formátu, takže si je můžete pěkně sbírat (třeba s Azure Monitor for Prometheus) a se spotřebou si pohrát třeba v Azure Managed Grafana. Bohužel Azure Cost Management do něčeho takového přímo konektor nemá, ale data umí exportovat. Co chci ve finále říct je, že znám zákazníky, kteří si dělají reporty sami v PowerBI (přímo z Azure umíte údaje o nákladech dobře vytáhnout). Stačilo by tedy udělat si datovou pipeline a dostat údaje třeba do Parquet souborů v Azure Data Lake Storage a přes Synapse serverless SQL nebo Databricks Serverless SQL Warehouse si nasát do PowerBI data pro vaše vlastní reporty. Já si vystačím s Azure Cost Management, ale když máte silný datový tým, nebude to těžké, tak proč to neudělat. 

# FinOps a kam dál
Když to dnešní téma shrnu. Za mě je Azure Cost Management mocný a pokud správně tagujete zdroje je velmi užitečný i ve světě Kubernetes clusterů. Uděláte tam ty analýzy, které jsou nejzásadnější pro vaši finanční orientaci v prostředí a je samozřejmě optimální pro vnitřní potřebu týmů přidat OpenCost nebo KubeCost (a pokud chcete s ním jít dál, funguje velmi dobře - tudy se vydejte, pokud opravdu víte, že je ta granularita pro vás zásadní).

Jenže pro mě osobně FinOps není primárně o reportech, ale o finanční gramotnosti v cloudu. Ve schopnosti integrovat náklady do DevOps procesů, do architektury projektů, Infrastructure as Code, budgeting a alerting na finanční události (když se něco moc rozežere) a průběžné optimalizace s využitím jak technických prostředků (škálování, vypínání, right-sizing) tak těch obchodních (rezervace, savings plány, přenosy licencí). Nedávejme tedy rovnítko mezi FinOps a reporty, ale je to určitě dobrý začátek. **A za mě je zásadní, aby právě ty technické týmy měli přístup ke všem těmto reportům a nástrojům, protože ve světě cloudu nejvíc ušetříte tím, že to umíte po technické stránce efektivně používat. Spíš než sleva vám pomůže vědět co děláte.**

Zkuste si a budu moc rád, pokud mi nasdílíte svoje zkušenosti.