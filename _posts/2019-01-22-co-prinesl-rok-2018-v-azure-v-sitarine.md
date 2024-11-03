---
layout: post
status: draft
published: true
title: Co přinesl rok 2018 v Azure v síťařině
tags:
- Networking
---
Rok 2018 byl v oblasti síťařiny v Azure velmi plodný. Co všechno se do Azure přidalo za jediný rok?

## Plné rozšíření servisních endpointů
Na konci 2017 přišla zajímavá metoda integrace IaaS s PaaS na síťové úrovni. PaaS typicky běží na public endpointu a přístup z IaaS tak jde přes veřejné adresy. Service endpoint vytváří tunel mezi VNETem a PaaS službou. Ta nadále zůstává na public endpointu, ale IaaS se k ní protuneluje přímo z privátních adres a na PaaS službě je nově možnost zapnout filtr a například zakázat přísutp z Internetu. Během roku přišla tato podpora do Storage, SQL, SQL Data Warehouse, Azure Database for MySQL a PostgreSQL, Cosmos DB, Key Vault, Service Bus, Event Hub i Data Lake Storage.

## Nová integrace do VNETu pro Azure Container Instances a App Service
Networking tým přišel s novým způsobem integrace strojů běžících v ne-VM režimu do vašeho VNETu. Výsledkem je nová integrace App Service do backend služeb ve VNETu (místo původní integrace přes P2S VPNku) nebo možnost pouštět kontejnery z Azure Container Instance ve vašem VNETu.

## Azure SDN integrace přes Centainer Networking Interface
Do plné dostupnosti se dostala implementace kontejnerových driverů pro integraci do Azure SDN. Kontejnery tak mohou běžet přímo ve VNETu (nepotřebují overlay) a pokud vím chystají se i další integrace, jako je využití Azure SDN filtračních možností (to co používá NSG) pro implementaci pravidel pro kontejnery (Network Policy v Kubernetes například). Azure Kubernetes Service CNI implementaci používá pod názvem Advanced Networking.

## Azure Front Door Service
Asi nejzajímavější síťovou službou je pro mne Front Door. Jde o distribuovanou reverse proxy pro dynamický obsah a současně CDN tak, že tohle všechno běží v POPech Microsoft sítě, tedy na mnoha místech po světě (POP je třeba i v Praze). Používá anycast, globální balancing a podobné vychytávky. Vřele doporučuji prozkoumat.

## Microsoft CDN
Azure CDN nabízela (a stále to platí) implementaci Akamai nebo Verizon přímo integrovanou do Azure portálu. K této dvojici se nově přidala také Microsoft varianta. Pro Office365 nebo XBOX už vlastní CDNka existuje dlouho a nově je nabízena i pro externí zákazníky. Máte tak na výběr ze tří implementací Azure CDN a všechny v tieru Standard se ovládají přímo z Azure portálu stejným způsobem.

## Azure Firewall
Další výraznou novinkou je Azure Firewall. Zatímco NSG/ASG je distribuované řešení, Azure Firewall je centralizované řešení. Díky tomu můžete vytvářet centrální pravidla pro NAT (řídit odchozí provoz do Internetu na jednom místě) a tak podobně. Na rozdíl od virtuálních appliance třetích stran se chová Azure Firewall cloudovým modelem. Nejen, že se nestaráte o virtuální mašinky a jejich aktualizaci, ale platíte paušál podle času používání (jedna sazba - žádné výkonnostní tiery apod.) + poplatek za přenesená data. Azure Firewall vám pod kapotou škáluje jak je potřeba, ale vy to neřešíte. Příjemné je, že Azure Firewall podporuje pravidla podle FQDN, což je funkce, která u řady jiných řešení vyžaduje nákup různých advanced licencí.

## Azure Virtual WAN
Používáte Azure pro provoz služeb pro uživatele v centrále i na pobočkách? Z poboček můžete navázat VPN tunely do Azure. Co kdybyste ale mohli Microsoft síť využít i pro transit a komunikaci mezi pobočkami? Všechna místa napojíte do nejbližšího Azure a Microsoft síť je propojí mezi sebou. Přesně o tom je Azure Virtual WAN. Ale jak automatizovat nastavení všech zařízení? V tom Azure spolupracuje s předními dodavateli SD-WAN řešení, kde v době psaní článku najdete Barracuda, Check Point, Citrix, Netfoundry, Palo Alto, Riverbed a 128 Technology.

## ExpressRoute Direct
Jste mamutí zákazník a chcete 100 Gbps připojení do Azure? Chcete obejít všechny operátory a píchnout se do Microsoftí sítě napřímo? Od roku 2018 už je to možné.

## Transitivní ExpressRoute
Máte Express Route v Evropě a také jednu v USA pro tamní pobočky? Díky novince ExpressRoute Global Reach jste schopni dovolit i komunikaci poboček mezi sebou přes Microsoft síť. Typický scénář je, že v Evropě máte pobočky propojené servisním providerem, který vám současně zajišťuje Express Route do Azure. V USA ale tento provider nepůsobí nebo tam z různých důvodů máte jiného, který řeší tamní pobočky a americkou Express Route. Díky Global Reach můžete oba světadíly propojit přes Microsoft síť a využít tak svých investic do Express route i pro něco takového.

## NSG logy, Traffic Analysis
NSG logování se v roce 2018 dramaticky zlepšilo a ukazuje jak hit logy z pravidel tak session informace. V rámci Azure Monitor je k dispozici velmi pěkná analýza provozu vaší sítě.

## Azure Virtual Network vTAP
V rámci Azure Monitor (sekce Network Watcher) můžete odchytávat provoz s využitím agenta ve VM. V roce 2018 ale přišla do preview možnost kopírování provozu do analyzátoru přímo ve VNETu. To může sloužit pro troubleshooting, ale i pro dlouhodobé sledování provozu z pohledu bezpečnosti nebo analytiky s řešeními jako je FlowMon, Netscout, Big Switch Big Monitoring Fabric, Gigamon, RSA NetWitness, Vectra Cognito a další.

## Public IP Prefix
Potřebujete mít v Azure public adresy, které jsou předvídatelné a navazují na sebe, aby bylo jednoduché nastavit nějaká firewallová pravidla apod.? Od roku 2018 je možné si rezervovat nejen po jedné adrese, ale koupit si celý blok.

## Application Gateway v2
Reverse proxy a WAF v Azure získala na konci 2018 v preview novou generaci. Ta nově přináší autoškálování (dokáše sama měnit počet instancí podle zátěže), podporuje zónovou redundanci, má vyšší základní výkon a konfigurační změny se projevují podstatně rychleji, což je velmi příjemné. 

A co nás čeká v síťařině v roce 2019? Podle všeho se chystá ještě víc Enteprise integrací PaaS služeb do vašeho VNETu. První střípky přijdou už na jaře a určitě o tom budu psát. Rok 2018 byl pro síťařinu velmi silný, doporučuji prozkoumat všechny novinky, vyzkoušet a nasadit.