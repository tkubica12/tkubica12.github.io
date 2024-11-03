---
layout: post
published: true
title: Cloud-native Palo Alto firewall jako služba pro Azure Virtual WAN
tags:
- Security
- Networking
---
Pokud dnes stavíte síťové řešení v cloudu, doporučuji použít Azure Virtual WAN topologii, která nabízí jednodušší propojení a možnost globální architektury, což oceníte zejména, když máte vícero regionů. Jak ale s firewallem v hubu? Žádný problém. Buď použijete cloud-native firewall přímo od Azure (Azure Firewall) nebo některou z třetích stran, které společně s Microsoftem nabídli deployment jejich NVA (virtuální appliance) přímo do spravovaného hubu jako součást vWAN - například Check Point nebo Fortinet.

# Cloud-native vs. krabička
Azure Firewall cloudová služba, což přináší řadu zásadních výhod:
- Škáluje se to automaticky samo podle zátěže, nemusíte tedy řešit kolik a jakých licencí ani se strachovat, plánovat, dokupovat
- Model platby je za instanci a pak za přenesená data, takže platíte jen to, co opravdu aktuálně potřebujete
- Nic se neinstaluje, stačí to vytočit
- Veškeré upgrady a patchování se děje samo a stará se o to poskytovatel
- Je to součást Azure API, takže automatice celé síťařiny v jednom Terraform nebo Bicep manifestu je velmi snadná

Nicméně next-generation firewall třetí strany má taky svoje výhody - může to být víc funkcí, jednotná správa přes všechna prostředí, fakt, že už to máte z on-prem integrované do nějakého SIEMu, certifikace regulátora a tak podobně. Jenže pak typicky přijdete o výše zmíněné výhody cloud-native řešení.

Leda, že by třetí strana dodávající firewall tohle dokázala nabídnout jako službu, tedy velmi podobně jako Microsoft svůj Azure Firewall, a dalo se to rozjet v rámci vWAN. To by šlo, ne? A přesně to se děje - jako první s Palo Alto.

# Palo Alto Cloud NGFW s Azure Virtual WAN
Pohled do ceníku nám krásně ukáže, že se bavíme o cloud-native modelu doručování firewallu jako služby. Za běžící instanci zaplatíte dle jejich stránek 1095 USD měsíčně (Azure Firewall v podobných funkcích bude v SKU Standard, tedy 912 USD měsíčně), dále platíte za zpracovaná data 0.65 USD za 10 GB do 15TB a to se zlevňuje při velkých objemech až na 0,3 USD (Azure Firewall poplatek je 0,16 USD). Třetí položkou jsou příplatky za funkce jako je Advanced Threat Prevention, WildFire, URL filtering, DNS bezpečnost nebo centrální správa a ty se přes nějaké kredity počítají také z trafficu (na rozdíl od Azure Firewall, který pokročilé funkce řeší tierem - pořídíte dražší Premium instanci).

Palo Alto je tedy oproti Azure Firewall dražší, ale kombinace výhod řešení třetí strany, které už třeba používáte v centrále, a cloud-native modelu doručování je velmi zajímavá. Ano, škáluje to automaticky, neřešíte licence, platíte dle spotřeby, nic neinstalujete, upgraduje se to samo. Jediné, co mi zatím není jasné je míra automatizovatelnosti přes Terraform. Zdá se mi, že v AWS na to udělalo Palo Alto vlastního providera, ale v Azure šli cestou vytvoření Azure custom resource provider. Jinak řečeno zdá se mi, že část funkcionality dostali skutečně do Azure API. To by znamenalo, že Bicep nebo třeba AzApi pro Terraform by mělo umět nahodit ruleset s pravidly. 

# Proklikejme si to
V Azure Virtual WAN se mi objevilo nové tlačítko - nahození SaaS řešení.

[![](/images/2022/2023-05-05-07-45-03.png){:class="img-fluid"}](/images/2022/2023-05-05-07-45-03.png)

Vyberu si Palo Alto plán.

[![](/images/2022/2023-05-05-07-45-51.png){:class="img-fluid"}](/images/2022/2023-05-05-07-45-51.png)

[![](/images/2022/2023-05-05-07-46-51.png){:class="img-fluid"}](/images/2022/2023-05-05-07-46-51.png)

Nechám si vytvořit novou politiku a díky tomu myslím, že takto jsem schopen nastavovat pravidla přímo přes Azure. Alternativou je využít centrální správu z Panorama - určitě atraktivní volba pro ty, kteří nejsou zas až tak rozjetí s end-to-end Infrastructure as Code a chtějí řídit nastavení pro všechna prostředí tradičně.

[![](/images/2022/2023-05-05-07-47-53.png){:class="img-fluid"}](/images/2022/2023-05-05-07-47-53.png)

Politiku asociuji s nějakými pravidly.

[![](/images/2022/2023-05-05-08-13-23.png){:class="img-fluid"}](/images/2022/2023-05-05-08-13-23.png)

[![](/images/2022/2023-05-05-08-14-29.png){:class="img-fluid"}](/images/2022/2023-05-05-08-14-29.png)

[![](/images/2022/2023-05-05-08-15-00.png){:class="img-fluid"}](/images/2022/2023-05-05-08-15-00.png)




Vypadá to dobře a líbí se mi přístup, že dodavatelé specializovaných řešení už konečně i v oblasti síťových technologií začínají přicházet s plně cloud-native řešeními pro cloud. To, že zabalíte svůj produkt do virtuálky a prohlásíte to za cloudové řešení, mi nestačí. To že to je v cloudu neznamená, že se to chová cloudově. Přestože Palo Alto do detailu neznám, takže neumím posoudit jak dobré je to řešení, tak tehle model doručování služeb v Azure se mi opravdu líbí. Azure Virtual WAN není jen produkt či topologie, ale platforma. Díky vám, Palo Alto - kdo bude další, přátelé? A ano - koukám na vás, Fortineťáci a Check Pointéři. Zejména u Fortinetu, který podle všeho aktivně pracuje na VXLAN integraci přes Azure LB GW očekávám nějaká pěkná oznámení.
