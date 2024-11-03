---
layout: post
published: true
title: Azure Firewall Basic - levnější bráška pro malá prostředí nebo distribuované IT
tags:
- Networking
- Security
---
Azure Firewall přináší cloud-native způsobem L4-L7 služby pro síťovou bezpečnost a je velmi oblíbený jak u klasické hub-and-spoke architektury tak ve formě "secured hub" v novějším Azure Virtual WAN řešení. Funguje nejen pro L4 segmentaci, ale i jako transparentní proxy s FQDN pravidly, URL pravidly, outbound TLS inspekcí, IDPS, reputační službou nebo kategorizací obsahu (funkčně podle zvoleného tieru). Škáluje sám, čili se nafukuje a sfukuje podle potřeby, což je něco, co je u firewallů třetích stran obecně dost problém. Navíc - a to je za mě zásadní výhoda - zapadá do celého rámce automatizace, takže to celé můžete ovládat Bicepem, Terraformem nebo Pulumi end-to-end. To je pro moderní řešení, kdy prioritizujete schopnosti vertikální integrace před horizontální, naprosto zásadní a výrazně to převyšuje nad potřebou mít "jednotnou" správu všech firewallů...ale jenom firewallů (horizontální integrace). Pro úspěch automatizace je v dnešním světě myslím zásadně potřeba akcentovat integraci vertikální, tedy všechno, co aplikace nebo business funkce potřebuje ke svému provozu. Celá "jednotnost" je v moderní organizaci k ničemu, když pro nasazení aplikace potřebuju 20 různých "jednotných" nástrojů pro různá sila (na OS, na firewall, na proxy, na storage, na compute, na zálohování, na monitoring, ...). To považuji za problém - ne to, že pro aplikaci v on-prem mám jiné systémy, než pro cloud. Dokud jsem schopen vertikálně automatizovat aplikaci jako takovou - proto mám raději nativní firewall, protože do toho jednoduše zapadá tak, jako nativní backup nebo monitoring. Vertikální integrace jednoduše bez složitého lepení.

zatím všechno fajn - žádné licence, platím základní poplatek cirka 950 EUR za Standard a 1330 EUR měsíčně za Premium a k tomu poplatek za traffic 0,017 EUR za GB (takže se vůbec nemusím starat o to jak má firewall škálovat - tím, že platím za přenesená data je to starost Microsoftu a Standard verze umí vyškálovat až na 30 Gbps a Premium dokonce 100 Gbps). To je myslím určitě pravda tam, kde je Azure Firewall součástí landing zone větší firmy a je centrálním místem konfigurace prostupů mezi projekty (subskripcemi) a bránou do Internetu. Jenže - co když potřebuji firewallů spoustu nebo jsem menší firma?

# K čemu Basic tier
Za sebe vidím 3 zásadní důvody proč dává smysl přidat levnější Basic tier:
- Někdy potřebujete mít ad-hoc testovací prostředí a firewall tam dává smysl, ale musí to být levnější. Velká klasická test prostředí budou typicky napojena na centrální systémy, ale sandboxy, ad-hoc prostředí na měsíc pro nějaké projektíky a tak podobně možná jsou schválně izolované od firemní sítě a přesto i tam je vhodné řídit přístupy na Internet z bezpečnostních důvodů (to, že nemám připojení na onprem síť neznamená, že v mém workloadu není nic zajímavého pro útočníka - třeba data, klíče, certifikáty, kód).
- Možná jste malá firma a chcete do začátku něco levnějšího, ale už to tam mít - tedy mít "cílovou architekturu" hned od začátku a upgradovat na Standard model až to bude dávat finanční smysl.
- Možná potřebujete do svého světa přidat prvky distribuovaného IT - to není neobvyklé a může to dávat smysl. Může se jednat o regionální aplikaci, hrdinský tým, partnerské řešení nebo akvizici.

Pojďme si některé scénáře vzít trochu podrobněji. Představme si situace, kdy centrální řešení je příliš kostrbaté nebo pomalé. Tak například centrální tým nemá pořádnou automatizaci, změny pravidel jsou na ticket a klikají se ručně, což může být v pohodě pro většinu workloadů v cloudu, ale ne pro všechny. Nebo dokonce to, že mají něco společného s vaší sítí, ani není žádoucí.
- Hrdinský tým, který je hodně daleko v automatizaci, dělá něco co je generátor peněz pro firmu a centrální IT na ně rychlostně nestačí - to není nic neobvyklého. Pokud je to opravdu pro firmu tak důležité, je možné, že tento tým získá určitou míru autonomie a pravidla pro přístupy na Internet si tak mohou řešit sami svými nástroji v rámci deploymentu (ostatně by to měla být i dobrá zpráva pro IT, které tak může později přebírat tyto zkušenosti pionýrů pro vylepšování a automatizaci centrálního prostředí). Protože jde jen o pár API v Internetu a oddělení jump serverů od aplikáčů, není potřeba masivní výkon ani Premium funkce - jen levný plně automatizovatelný firewall.
- Zákaznické nebo školící prostředí vznikne ad-hoc a to třeba jako součást automatického procesu. Ráno školitel na něco klikne nebo zákazník si na webu vyžádá trial instanci a něco se roztočí. Není čas na ticket a ruční ťukání. Co kdyby si prostředí vytočilo i svůj firewall a nastavilo vše potřebné zejména vůči Internetu?
- U globální firmy možná máte aplikaci, která potřebuje být v určitém regionu (komunikovat odtamtud), protože to místní partneři či zákazníci vyžadují. Potřebujete tedy řídit provoz do Internetu přímo tam - ale to znamená vybudovat plnotučný hub v této lokalitě? To může být dost nákladné - prolevnit příslušné komponenty se hodí.
- Co když jde o subsripci, ve které vám partner provozuje software jako službu? Nejde o běžný SaaS přes Internet, ale něco vám na míru, něco, co chcete mít ve svém Azure z důvodu sbírání bezpečnostních logů, využití levnějších cen z vaší enterprise smlouvy a tak podobně. Bezpečně to propojíte se svou firemní sítí, ale proč máte tomuto partnerovi řídit přístupy na věci v Internetu (patche, API apod.)? To je jeho starost a jeho odpovědnost a víte jak to chodí - pořád chtějí něco měnit, nevědí pořádně co a vždy to svádí na vás. Ať mají svůj malý firewall.
- PoC je jistě další příklad - nechceme se zdržovat (nebo riskovat) nastavováním centrálního firewallu (jde o to s co nejmenšími náklady a časovou investicí zjistit, jestli aplikaci chceme nebo ne), ale firewall tam mít chceme (protože se to musí odladit i pravidly na něm - ty pak v pozdější fázi projektu budou žít na tom centrálním, ale zkoušet to bez něj by nemělo vypovídací hodnotu nebo nebylo bezpečné).

# Na kolik to vyjde a co to umí
Po funkční stránce je tier Basic velmi podobný tieru Standard, chybí jen pár věcí - nelze mít jako DNS proxy, reputační služba neumí provoz zařezávat, jen alertovat, není ani základní web content filtering. Samozřejmě logicky nejsou funkce Premium (outbound TLS inspekce, IDPS, URL filtering).

[![](/images/2022/2022-10-05-09-51-11.png){:class="img-fluid"}](/images/2022/2022-10-05-09-51-11.png)

[![](/images/2022/2022-10-05-09-51-59.png){:class="img-fluid"}](/images/2022/2022-10-05-09-51-59.png)

Nejzásadnější omezení je ve výkonu - Basic dokáže maximálně 250 Mbps! Na to nezapomínejte. Pro přístupy na Internet nebo vnitřní segmentaci jump boxů nebo správy je to často dostatečné, ale není to na nějaké velké datové přenosy, masivní stahování a tak podobně.

Sazba za firewall je cirka 300 EUR měsíčně, ale je výrazně vyšší poplatek za přenesená data (0,068 EUR vs. 0,017 EUR). Při hodně přenesených datech už máte lepší mít rovnou Standard (vychází mi to na cirka 13 TB měsíčně).

```
300 + 0,068x = 950 + 0,017x
x = 12 745
```

Mimochodem - nemluvím teď sice o use case pro Basic tier, ale mohou být extrémní situace, kdy použijete pro workload jeho vlastní firewall, abyste ušetřili za VNET peering poplatky. Představme si, že aplikace udělá 200 TB měsíčně (to je samozřejmě hodně, ale jsou situace, kdy se to dá čekat - třeba distribuce nějakých balíčku apod. - pochopitelně pokud se vás něco takového týká, rozhodně to směřujte do CDN a netlačte to firewallem...pokud to jde, což nemusí jít vždy). Poplatek za zpracovaná data na firewallu je pak 3400 EUR a VNET peering ze spoke do hub vyjde na 2200 EUR. Pokud dám druhý firewall přímo do subskripce workloadu, zaplatím sice 1000 EUR za další instanci firewallu, ale ušetřím za VNET peering a je to celkově levnější. Dosazení do rovnice říká, že se to láme někde kolem 91 TB.


To je tedy Azure Firewall Basic, který právě přišel do preview. Pro moje ad-hoc prostředí na hraní je to výborná věc stejně, jako pro exotičtější situace popsané v tomto článku. Pro použití v enterprise landing zone stejně zůstanete u Standard nebo Premium. 


