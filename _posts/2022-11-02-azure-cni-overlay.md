---
layout: post
published: true
title: Chcete Azure Kubernetes Service, ale máte málo IP adres? Použijte novou Azure CNI overlay.
tags:
- Networking
- Kubernetes
---
Jedním ze základních myšlenkových konceptů Kubernetu, v kterém ve své době řešil nepříjemnosti translace portů u většiny konkurence (Docker Swarm, Apache Mesos aka DC/OS, Service Fabric) byla přímá adresovatelnost Podů mezi sebou. Jinak řečeno každý Pod má svou IP adresu a navzájem se vidí. To je velmi přínosné, ale současně to klade nároky na síťovou implementaci. Původně jsem chtěl rozebírat jak to postupovalo v on-prem a nějaké historické záležitosti (VXLAN, VTEPy, podivnosti typu fabric extendery, ACI, VEPA s SR-IOV), ale zjistil jsem, že to mě vlastně už nezajímá - zaměřme se na to, jak to vypadá v cloudu.

# Tunelovat či netunelovat? 
Pody žijí uvnitř nodu typicky ve formě virtuální síťovky, resp. veth páru, který je jedním koncem napojen na sdílený síťový prvek v hostiteli (nejčastěji Linux bridge, někdy Open vSwitch, někdy třeba virtuální přepínač v ASIC síťové karty přes SR-IOV, nějakou eBPF implementaci apod.). Jak zajistit, aby Pody mohly komunikovat napřímo mezi sebou napříč nody?

První myšlenka možná bude směřovat na něco, co je ve finále dost chytré a účinné - pojďme si to celé vyřešit sami a postavit síť nad sítí s využitím tunelování, třeba VXLAN. Jenže v cloudu už se tuneluje - VNET je defacto routing doména a dataplane oddělený nějakým tunelem. Tunel v tunelu snižuje MTU, zvyšuje latenci, zesložiťuje řešení a celkově vzato v cloudu není dobré ho používat. To je důvod proč pokud vím žádný z velké trojky (AKS, EKS, GKE) nepoužil tunelování v žádné své supportované implementaci.

Pokud tedy z nějakého důvodu chcete tunelování, musíte si přinést svůj vlastní CNI plugin a o ten se sami starat (nedostanete přímo na něj podporu - ani v jednom cloudu). Mrknout můžete sem: [https://learn.microsoft.com/en-us/azure/aks/use-byo-cni](https://learn.microsoft.com/en-us/azure/aks/use-byo-cni).

# Přímo v síti nebo v overlay?
Protože v cloudu už softwarově definovaná síť je, dává velký smysl ji využít - tedy dát Pody na úroveň VM. Proč mít ve hře další vrstvu virtualizace, když by se mohlo podařit koncept virtuální síťovky virtuálky roztáhnout i na virtuální síťovku Podu. Přesně to se stalo ve všech třech implementacích - AKS (Azure CNI aka advanced networking), EKS (Amazon VPC CNI) i GKE (VPC-native cluster). Na příkladu AKS má tohle zajímavé výhody:

- North-south traffic jde napřímo - Pod si může povídat s VM nebo platformní databází bez nutnosti nějakého NATování na IP adresu nodu, takže to přináší nejoptimálnější výkon.
- Potenciálně jsou síťové schopnosti providera dostupné i pro Pody, třeba co do implementace L4 pravidel jako jsou Network Security Group nebo sběr flow informací pro monitoring.
- L7 balancing z Azure Application Gateway funguje napřímo (gateway má přímo Pody jako backend pool, což má nižší latenci, než otáčet to přes Ingress implementaci uvnitř clusteru).

Nicméně je s tím spojena jedna častá a v enterprise nenáviděná vlastnost - spotřeba IP adres. Pro privátní využití je dle rfc1918 k dispozici téměř 18 000 000 adres, tak to by mělo stačit i na kontejnery... jenže z historických důvodů vám stávající enterprise firma bude dělat problémy získat tisíce IP jen pro jeden z vašich AKS clusterů. Stále trvám na tom, že to jen byrokratický problém, protože adres je prostě dost, ale to nemění nic na tom, že to pro váš projekt může znamenat stopku či zdržení.

Co s tím? Mohli bychom Podům dát IP adresy, jejichž rozsahy budou sloužit pouze pro daný cluster a nebudou dostupné zvenku. Díky tomu bychom mohli u každého clusteru používat stejné a výrazně tak šetřit. Jak to ale udělat? V případě AKS (Kubenet aka basic networking) a GKE (route-based cluster) se na to jde tak, že Pody používají VNET pro přenos paketů, ale v rozsazích, které VNET oficiálně nezná a tedy neroutuje nikam do světa (nepropaguje je do směrovacích tabulek jiných subnetů či peerovaných VNETů). Aby ale věděl co má s pakety dělat, tak se nainstalují specifické routovací tabulky. V případě AKS to funguje tak, že každý node clusteru dostane určitý range IP adres a v User Defined Route se nastaví směrování, že tyto adresy se mají posílat na tento node. To ale znamená pár nepříjemností:

- AKS musí mít přístup k UDR - už to samo o sobě může znamenat problém, protože v rámci governance se často chce tohle uzamknout jen pro síťaře.
- Každá změna v nodech (například přiškálování) znamená nutnost uzaložení daších záznamů v UDR - AKS tak do UDR často hrabe.
- U zákazníků se často UDR používá k nastavení směrování provozu přes firewall a optimálně přes Infrastructure as Code. Takže objekt chcete držet v Terraformu, jenže AKS vám do něj hrabe a přetahují se mezi sebou.
- Škálování je omezeno počtem záznamů v UDR, které je dnes maximálne 400. Pár jich může vyčerpat firma pro své účely (například nastavení výjimek na control plane služeb - třeba použití service tagů může znamena hned několik obsazených řádků, protože služba potřebuje klidně třeba deset záznamů pod kapotou), pokud použijete dual-stack síť (IPv4 + IPv6), tak si to hnedle vydělte dvěma. Zkrátka většina zákazníků nemá s pár stovkami nodů problém, ale jsou i tací, co potřebují větší clustery (maximum AKS samotného je dnes 5000 nodů per cluster).
- Hrabání do UDR má i vliv na rychlost škálování a různé krajní situace. To je například důvod, proč není podporované mít dva clustery v tomto režimu ve stejném subnetu (potažmo tedy ve stejném UDR), byť by to technicky šlo, ale hadání se clusterů mezi sebou o přístup k UDR nefunguje spolehlivě.

Pochopitelně jsou tu i další aspekty - north-south trafic musí být NATován na nodu, což přidává nějakou latenci, nefunguje Application Gateway jako Ingress kontroler, nejdou použít vlastnosti nativní síťové platformy, takže pro network policy nezbývá, než nasadit Calico (které není přímo supportované Microsoftem narozdíl od nativní implementace) a tak podobně. 

Tolik tedy ke stávající situaci - no a nově přichází nová varianta. Azure CNI overlay, která řeší problém nedostatku IP adres a současně odstraňuje mnohé (ale ne všechny) nedostatky Kubenetu. Ale nepřeskakujme.

# Azure CNI a evoluce k oddělené síti pro Pody
Jedním z důvodů velké žravosti IP adres bylo u Azure CNI to, že alokace adres na Nody byla statická. Pokud jste například řekli, že chcete maximálně 50 Podů na node, tak cluster při svém vzniku natvrdo alokoval IP adresy pro jednotlivé Nody. Pokud jste tedy možná na jednom nodu běželi 40 Podů a na druhém jen 15 Podů, tak jste zabrali minimálně 100 adres. 

Azure networking později přišel se zajímavým vylepšením, kdy dokázal oddělit virtuální síťovky VM od virtuálních síťovek Podů. To umožnilo mnoho zajímavých konceptů, které jsou jedním z důvodů proč takový Azure Database for PostgreSQL Flexible Server umí pěkně běžet přímo v síti zákazníka a přitom nevyžaduje žádné výjimky na UDR pro komunikaci s control plane. Ale vraťme se k AKS. Oddělením Podů od Nodů se stane to, že Pod subnet se začne dynamicky obsazovat podle potřeby. Zmizelo tedy vázání IP k jednotlivým nodům, vše je dynamické, takže daleko efektivněji využívané. To rozhodně pomohlo - ale pořád platí, že co Pod, to spotřebovaná IP adresa.

# Azure CNI overlay - šetří IP adresy bez většiny omezení Kubenetu
Pojďme si ty popsané události a inovace proložit v čase a dojdeme k tomu, co dnes přichází do preview pod názvem Azure CNI overlay. Co jsme potřebovali v Kubenetu? Dali jsme Podům jiné IP adresy, takové, které nejsou směrovatelné v rámci okolní sítě. Nicméně tím bylo nutné modifikovat routovací tabulky a byl to takový trochu hack. Když teď lze dát Pody do jiné sítě, proč neudělat nějakou, která bude určená jen pro Pody? Nebude se routovat někam jinam. Samozřejmě tady je nutno vyřešit to, že v případě Azure CNI Pody komunikují se sítěmi přímo, takže to teď nepůjde (stejně jako u Kubenetu). Komunikace north-south musí jít přes Node, který udělá NAT. Víceméně právě takhle je to postavené v Azure CNI overlay. Pody žijí v jakémesi "VNETu", tedy jejich virtuální síťovky jsou přímo na úrovni Azure sítě propojeny mezi sebou (tím je vyřešen east-west provoz) a současně north-south teče přes nody. To znamená:

- Podobně jako u Azure CNI lze pro Pody využít různých funkcí a akcelerací na úrovni Azure, třeba síťové politiky apod.
- Podobně jako u Kubenetu se nespotřebovávají IP adresy skutečného VNETu
- Podobně jako u Azure CNI není potřeba nějak modifikovat ten skutečný VNET - měnit jeho UDR či jakkoli jinak do něj zasahovat
- Stejně jako u Azure CNI i u Kubenetu se nepoužívá další vrstva enkapsulace do nějakého tunelu (na rozdíl třeba od bring your own CNI s VXLANou), takže east-west traffic je rychlý a bez přidané latence

Zbývá tedy jen pár nevýhod v porovnání s Azure CNI - není zde přímá adresovatelnost Podů komunikujících mimo cluster, tedy north-south traffic. Ten musí jít přes NAT v Node, což s sebou nese nějakou drobnou zátěž a latenci (a potažmo tím nefunguje aktuálně App Gateway jako Ingress, protože ta adresuje Pody přímo). Pro maximální škálovatelnost a výkon tak i nadále využívejte Azure CNI, ale pokud jsou pro vás IP adresy skutečně problém, nová Azure CNI Overlay je myslím skvělá volba (na rozdíl od Kubenetu, který do enterprise prostředí není optimální kvůli modifikacím UDR).

# Jak si vyzkoušet
Připravil jsem Terraform, který nahodí celé testovací prostředí - AKS v tomto režimu, networking s Azure Firewall a Azure Container Instance, přes kterou otestujeme odchozí IP adresu. Celý předpis a návod najdete tady: [https://github.com/tkubica12/azure-workshops/tree/main/d-aks-cni-overlay](https://github.com/tkubica12/azure-workshops/tree/main/d-aks-cni-overlay).

Můžete si tam dokázat, že provoz z Podů skutečně k okolnímu světu (v mém případě httpbin v ACI) dorazí pod IP adresou Nodu. Dále jsem v privilegovaném kontextu s host networkingem odchytil pakety na nodu, abych se přesvědčil, že komunikace Podů je skutečně přímá (žádné NAT ani jinak změněné adresy) a že nevyužívá nějaký tunel (žádná VXLAN nebo něco podobného).

Zkuste si taky.


Pokud jste enterprise a stále tvrdíte, že je málo IP adres, myslím, že Azure CNI Overlay je to pravé řešení pro vás. Odstraňuje některé neduhy Kubenetu a pokud skutečně nemůžete plné Azure CNI použít, je to volba pro vás. Aktuálně je v preview, tak bych s produkcí ještě chvilku počkal, ale čas zkoušet to a připravit se je právě teď.