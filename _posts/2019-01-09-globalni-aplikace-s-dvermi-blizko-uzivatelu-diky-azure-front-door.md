---
layout: post
status: published
published: true
title: Globální aplikace s dveřmi blízko uživatelů díky Azure Front Door
tags:
- Networking
---
Jak udělat globální aplikaci tak, aby uživatel měl co nejlepší přístup z hlediska latence, pásma a stability spojení? Prozkoumejme Azure Front Door.

O čem dnes bude řeč? Microsoft aplikace běžící v Azure jako jsou Office365 nebo XBOX musí být nasazené co nejblíže uživatelům, ale přestože je seznam datových center Azure rozsáhlý, ne všude jsou. Nicméně Microsoft má ale v rámci své sítě víc míst, ve kterých se spojuje se světem a uživateli i mimo datová centra. V těchto POPech má Microsoft svou Content Delivery Network (cache), ale ještě něco navíc. Plně distribuovaný globální balancer postavený na anycastu, takže přes POP se akceleruje i dynamický obsah. Jak je to možné? Tato funkce po pěti letech provozu pro Office365 je nově v preview dostupná i pro vaše vlastní aplikace.

# Klasické řešení globální aplikace

Aplikace jako taková potřebuje být blízko uživatelům a s tím souvisí i její data. Kód i data tak potřebujeme mít ve více než jednom regionu a obsluhovat tamní uživatele. Někdy se dá sharding podle země nebo kontinentu udělat relativně jednoduše, jindy je nutná i datová globálnost a tam může přijít ke slovu Cosmos DB s podporou čtení i zapisování v různých regionech nad společnou datovou základnou. Nicméně to nechme stranou - mám webovou aplikaci a je nasazena v Evropě, US, Jižní Americe a Austrálii.

Jak směrovat uživatele na jemu nejbližší region? O to se může postarat Azure Traffic manager postavený na DNS protokolu. Udělá to dobře a jeho výhodou je, že přes něj následná komunikace nijak neproudí. Bez problémů tak mohu použít i zdroje mimo Azure, například Azure Stack v Rusku a vlastní VMware v Japonsku.

V rámci Evropy je ale určitě rozdíl mezi Prahou, Chorvatskem, Irskem, Německem a Portugalskem. Statický obsah určitě dáme k uživatelum blíž s využitím CDN.

Zbývá něco k řešení? Potíž je, že pro dynamický obsah, například API volání, se sestavuje spojení mezi klientem a datovým centrem, což je dlouhá vzdálenost přes občas nehostiný Internet:
* Pokud se klient často spojuje a nemůže si session držet, trvá to všechno dost dlouho (TCP handshake znamená jít vzdálenost 3x a 6x při HTTPS).
* Pokud mám hodně klientů v určité lokalitě, každý má svou TCP session.
* V některých místech například v Jižní Americe je kvalita komunikace přes Internet horší a spojení se častěji rozpadají.

Navíc jsou tady další aspekty. V každém regionu pravděpodobně nasadíme reverse proxy, abychom zajistili věci jako TLS terminaci, balancování se session perzistencí podle cookie či Web Application Firewall s OWASP pravidly. V případě nutnosti překlopit provoz se musíme spolehnout na DNS.
* Certifikáty musíme řešit na několika místech, v různých instancích reverse proxy. Certifikáty se dají bezpečně spravovat v Azure Key Vault, ale například Azure Application Gateway první generace používání Key Vaultu nepodporuje.
* Nastavení, pravidla WAFky a směrovací pravidla (URL rewrite, http-to-https redirect) musíme synchronizovat mezi všemi regiony například ARM šablonou v případě App Gateway nebo centrálním management nástrojem pro appliance třetích stran (např. F5).
* DNS pro překlopení provozu může dost dlouho trvat v závislosti na DNS infrastruktuře a cachování u operátorů, které nemáte pod svou kontrolou. Nemluvíme o vteřinách ani minutách, obvykle to bude na desítky minut.

Podívejme se jak tento scénář řešit s novou službou Azure Front Door Service.

# Řešení s Azure Front Door Service

Toto řešení je v podstatě distribuovaná reverse proxy. V každém POPu Microsoft sítě (v preview neběží služba ještě na úplně všech, ale celkový seznam POPů najdete v dokumentaci pro [Azure CDN by Microsoft](https://docs.microsoft.com/en-us/azure/cdn/cdn-pop-locations) a jeden z nich je v Praze) běží vaše proxy. Centrálně nastavujete v Azure portálu a veškerá pravidla se natlačí do všech POPů.

Začněme od backendu. Jako u každého L7 balanceru řeknete Azure Front Door službě seznam vašich backend instancí. Health probe kontroluje nejen dostupnost, ale také měří latenci a směrovací algoritmus můžete zapnout na rozhodování podle latence. To je velmi zajímavé. Instance v POPu třeba v Praze si bude sledovat latenci k backend instancím v Amsterdamu, Dublinu, Brazílii i Austrálii a použije ten, co reaguje nejrychleji. Každý POP tak bude mít svá vlastní měření a docházet ke svým závěrům.

Azure Front Door funguje jako reverse proxy, tedy terminuje TCP session a TLS uživatele a navazuje své vlastní TCP spojení na balancovanou službu v regionech. Díky tomu je session klienta navázána na krátkou vzdálenost, což je rychlé a spolehlivé a navíc počet session mezi klienty a Front Door nemusí být stejný, jako počet session do vašeho API či webu v Azure. Jinak řečeno vícero klienských session je terminováno na proxy a ta může použít třeba jednu sdílenou session na backend.

Tím, že je Front Door reverse proxy vám umožní dělat TLS terminaci, URL rewrite a jiné komplexní politiky, cookie session perzistenci, WAF pravidla nebo konvertovat protokoly (například uživatelům nabídnout HTTP/2 nebo IPv6 endpoint).

Front Door tedy dokáže akcelerovat aplikační provoz díky split TCP, směrování na nejbližší místo, použití Microsoft sítě pro backend provoz apod. Ale co statický obsah? Front Door nabízí i služby podobné CDN. Dokáže tedy dělat caching statického obsahu a optimalizační kouzla typu komprese.

Zbývá poslední věc. Front Door tedy v každém POPu umí krásně vybrat vhodný backend v Azure, ale jak klient najde nejbližší POP? Zase přes DNS jako u traffic manageru? Tentokrát ne. DNS balancing je sice použit pro failover celé služby pro případ katastrofální havárie Front Door instance, ale není nasazen jako běžný mechanismus posílání klienta na nejbližší POP. Pro to je použit anycast. Ten je jednak přesnější (DNS dotazy nepřicházejí do DNS balancerů přímo z klientů, ale z jejich DNS serverů) a netrpí cachováním.

Ještě jedna poznámka - Azure Front Door je globální služba a nepodporuje integraci do VNETu, podobně jako něco takového není možné pro CDN. Pravděpodobně tedy pokud máte v každém regionu vícero instancí compute zdrojů, budete ho do Front Door zařazovat přes nějaký regionální balancovací mechanismus, spíše než napířmo přes veřejné IP. Jinak řečeno pokud je to ve VM nebo kontejneru v AKS, použijete v regionu například Azure LB. PaaS služby typu Application Service to mají přímo v sobě a jednotlivé instance service plánu jsou balancované automaticky.

Shrňme vlastnosti Azure Front Door Service
* Distribuované řešení běžící současně na mnoha POPech
* Centrální konfigurace celého systému
* Platební model, kdy neplatíte za počet lokalit, ale paušál + provoz
* TCP a TLS terminace přímo v POPech pro split TCP
* Za POPem jdete po spolehlivé Microsoft síti, ne přes Internet
* Caching a akcelerace provozu podobně jako u CDN (statický obsah, komprese, HTTP/2)
* Bezpečnost (základní OWASP WAFka)
* Konverze protokolů (podpora HTTP/2, IPv6)
* Směrovací pravidla včetně URL rewrite

Příště už si Azure Front Door Service vyzkoušíme prakticky.