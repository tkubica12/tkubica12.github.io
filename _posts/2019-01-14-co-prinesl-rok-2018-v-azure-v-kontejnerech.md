---
layout: post
status: publish
published: true
title: Co přinesl rok 2018 v Azure v kontejnerech
tags:
- Compute
- Storage
---
Největší změny v kontejnerech v Azure v roce 2018? Práce na jednoduchém nasazování, platformně laděných funkcích a clusterless - kontejnery bez nutnosti mít pod nimi VM.

# Azure Container Instances - stavební blok clusterless kontejnerů

ACI nabízí možnost spustit kontejner přímo v Azure. Nepotřebujete žádné VMko, ani AKS, ani Service Fabric nebo App Service. Jednoduše pustíte kontejner rovnou v Azure. Podstatné je, že to nemá orchestrační funkce a nenahrazuje zmíněné vyšší systémy. ACI je tak stavební blok. Můžete ho využí v rámci svého CI/CD pro rychlé nahození buildovacích agentů nebo sjetí testů. Dá se použít samostatně pro rychlé zprovoznění třeba trial instance vaší aplikace pro zákazníka (třeba orchestrovaně přes Logic Apps vytvořit instanci, poslat zákazníkovi email s loginem, po 14 dnes prostředí zrušit a poslat mu poděkování apod.). Nebo může ACI sloužit jako stavební blok pro Kubernetes bez nodů.

Co přinesl rok 2018 pro ACI? V preview jsou dnes k dispozici kontejnery s podporou GPU, což je velmi zajímavé pro různé výpočetní úlohy a strojové učení. Pro mě asi nejvýznamnější je podpora spouštění kontejnerů v custom VNETu, což umožňuje jejich privátní komunikaci s dalšími objekty ve VNETu jako jsou kontejnery v AKS, virtuální mašiny nebo servisní endpointy pro PaaS. Hodně se pracovalo na integraci a monitoringu ACI. Přišla možnost vícekontejnerových instancí (něco jako Pod v Kubernetes), AAD identita přes Managed Service Identity, liveness probe pro detekci selhání aplikace či integrace logů do Azure Monitor. Přidala se podpora pro mapování Volume v podobě Azure Files, Git, Secret nebo Empty (pro sdílení v rámci vícekontejnerové instance).

# Azure Kubernetes Service - lepší monitoring, síťařina a clusterless

AKS v roce 2017 bylo ve znamení stabilizace, přípravy na nové funkce a architektury, clusterless, hlubší integrace do Azure apod.

AKS přinesla podporu pro custom VNET pod názvem Advanced Networking, což je implementace Azure CNI pluginu, který umisťuje kontejnery rovnou do VNETu (místo předchozího stavění nad pouze vnitřně routovatelnými adresami) a nabízí tak větší rychlost a už velmi brzy další výhody integrace (například implementaci Kubernetes Network Policy přímo prostředky VNETu). Velmi příjemné jsou možnosti monitoringu přímo do Azure, konkrétně sbírání a vizualizace metrik kontejnerů a sběr logů do Azure Monitor a to jak s vyhledávacím jazykem Kusto, tak napojení na realtime stream logů. 

Asi nejvýznamnější služba z pohledu budoucnosti AKS jsou Virtual Nodes (v preview). Jde o clusterless řešení, kdy máte virtuální node, který je nekonečný a neplatíte za něj, ale za kontejnery, které vytvoříte. nemusíte tak škálovat spodek AKS a jednoduše si vytvoříte tolik kontejnerů, kolik chcete. Pod kapotou řešení je napojení AKS na ACI.

V neposlední řadě došlo k mnoha architektonickým změnám, které připravují AKS na další funkce v roce 2019. Původní ACS-engine pokračuje dál pod názvem AKS-engine a ten vám umožňuje vytvořit si vlastní nespravované clustery a nasadit experimentální funkce, které v AKS podporované zatím nejsou. Najdete tam podporu Windows kontejerů, Kata containers (kontejnery izolované odlehčeným hypervisorem), síťové policy a mnoho dalších vychytávek. Od roku 2018 je také Kubernetes dostupný pro Azure Stack.

# Service Fabric Mesh - aplikační platforma s podporou kontejnerů a clusterless
Service Fabric je nejen kontejnerový orchestrátor pro Windows i Linux, dnes plně open source a technologie, na které je postaven samotý Azure, ale víc, než AKS, se zaměřuje i na funkce aplikační platformy. Kromě orchestrování kontejnerů tak nabízí i programátorské funkce jako jsou stavové služby (platforma na pozadí replikuje konstrukty mezi instancemi - třeba kolekce nebo fronty), velmi dobře řešené Volumy včetně těch replikovaných na úrovni clusteru (nízká latence) nebo speciální programovací modely typu Actor.

Hlavní novinkou v preview je Service Fabric Mesh. Nová generace řešení, která je plně spravována a plně clusterless. O řešení samotné se vůbec nestaráte, nemáte žádné nody a platíte jen za instance kontejnerů. Nasazování aplikací je přes ARM šablony, takže máte jednotný systém pro deployment aplikační části i třeba platformních databází. Mesh varianta navíc přináší lepší síťové řešení, než předchozí Service Fabric model, zejména podporu Envoy proxy pro funkce typu L7 gateway, která je zabudována v řešení.

V neposlední řadě přišla podpora klasického Service Fabric pro Azure Stack, což umožňuje velmi elegantní a přesto cloudově orientované řešení pro on-premises. Pokud máte jiné on-premises prostředí můžete nainstalovat Serice Fabric ručně nebo nově s využitím BOSH.

Přemýšlíte o clusterless a hledáte co bude nejlevnější? Přesně to Microsoft nechce komplikovat a ACI, clusterless AKS i Service Fabric Mesh jsou v tomto sjednocené. Clusterless kontejner stojí pokaždé stejně, takže při výběru se můžete soustředit na požadované vlastnosti, cena je stejná.

# Azure Container Registry - lepší automatizace a bezpečnost

Registr kontejnerových obrazů je zásadní součástka celého řešení a v roce 2018 se objevila řada vylepšení. Za nejvýznamnější považuji podporu Tasků. Je to možnost do registru obrazy nejen ukládat, ale také je tam vytvářet a to včetně multi-step. Můžete tak například reagovat na webhook z Gitu v okamžiku commitu nového kódu a ACR zahájí automatický build nového kontejneru včetně podpory víc kroků (například vezmeme buildovací kontejner s plným SDK, ve kterém připravíme binárky a ty pak použijeme pro přípravu aplikačního kontejneru).

Dalšími novinkami byla podpora Helm repozitářů (velmi užitečné pro nasazování aplikací v Kubernetes), geo-replikace obrazů mezi regiony a podpora pro bezpečné ukládání (Docker Content Trust), tedy podepisování obrazů a RBAC model kdo smí podepsané obrazy v organizaci publikovat.

# Kontejnery v dalších Azure službách

Mnoho dalších služeb v Azure kontejnery už v roce 2018 podporovalo nebo se to naučilo. Samozřejmě App Service na Linuxu je postaveno přímo na kontejnerech, ale nově se přidala podpora mapování Volume, implementace Easy Auth, vícekontejnerové nasazení (s podporou formátu Compose i Kubernetes pod) a také podpora pro tuto technologii v privátní podobě služby (App Service Environment). Widnows verze App Service už také podporuje Windows kontejnery jako prostředek distribuce aplikací.

Nesmírně zajímavým použitím kontejnerů je Azure IoT Edge, tedy možnost z cloudu spravovat a připravovat funkce, které pak běží lokálně v IoT zařízení. V něm je Azure platforma a Docker a funkce jsou zabaleny do kontejnerů. Podporuje to custom kontejnery (třeba logika pro vyčítání ze senzorů), Azure Functions framework nebo pokročilé služby typu Stream Analytics, Machine Learning nebo si v Edge pustít Microsoft SQL v kontejneru.

Export modelů strojového učení i kognitivních služeb do kontejnerů pro jejich nasazení nebo trénování v prostředích vaší volby je další klíčovou novinkou 2018 a ukázkou univerzálnosti kontejnerů. Pokud chcete kontejnery použít pro High Performance Computing, můžete použít AKS a ACI, tedy mainstreamové technologie. V HPC komunitě ale existují i alternativní řešení jako je Singularity. Kromě využití standardního Kubernetes pro HPC tak můžete využít open source Batch Shipyard pro Docker či Singularity orchestraci kontejnerů nad Azure Batch. Další specifické HPC řešení Azure CycleCloud dnes také podporuje kontejnery.


Kontejnery zaznamenávají obrovský vzestup a rok 2018 byl pro Azure velmi plodný. Přesto očekávám, že zejména v oblasti clusterless řešení pro orchestrátory a v přidaných funkcí nad tím jako jsou identity, service mesh a další prohlubování integrace to bude v tomto roce 2019 ještě zajímavější. Takže je myslím na co se těšit.


