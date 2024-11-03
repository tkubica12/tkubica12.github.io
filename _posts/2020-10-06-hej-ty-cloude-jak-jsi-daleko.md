---
layout: post
published: true
title: Hej ty cloude, jak jsi daleko? Test latence vybraných Azure regionů v Evropě. 
tags:
- Networking
- Compute
---
Azure má na rozdíl od ostatních globálních konkurentů v Evropě opravdu velké množství regionů. Jaké to jsou? A jak si mám vybrat ten pravý? Jsou rozdíly v cenách? Je ten nejblíž pro mě ideální?

# Kritéria výběru
Při výběru regionu může hrát roli několik faktorů. Jeden je však zřejmý - pokud už někde něco máte, je výhodné se toho místa držet. V enterprise firmách máte jistě vybudovánu landing zone, hub-and-spoke topogii s centrálně vyřešeným připojením do firemní sítě (Azure VPN, Azure Virtual WAN, Express Route), Azure Firewall a WAF, doménový řadič a další sdílené služby a dává smysl tyto náklady rozpustit do co největšího množství projektů. Jasně, regiony můžete mezi sebou propojit podle libosti, ale platíte pak za přenosy ven z regionu a také poplatek za globální VNET peering, pokud potřebujete takto roztáhnout privátní sítě. Typická enterprise globální firma tedy vybuduje jeden hub v Evropě, druhý v US a třetí v Asii a k těmto často přidá ještě malý na každém kontinentu pro DR. Ale tak to být nemusí. Možná jste globální herní firma nebo IoT řešení a potřebujete být co nejblíže hráčům a zařízením a pak design samozřejmě vypadá jinak, například je daleko víc distribuovaný.

Nicméně pojďme k těm dalším faktorům výběru zejména pokud jste na začátku:
- Lokalita z pohledu většiny těch, co budou služby využívat - tedy v případě ČR latence do konkrétního regionu.
- Lokalita z pohledu regulace a místní příslušnosti. EU samozřejmě není žádný problém, ale může být i potřeba pro konkrétní zemi a to dokonce i včetně případné DR lokality. Francouzi tak mohou použít region v Paříži a pro DR nasadit region v Marseille apod.
- Podpora zón dostupnosti. Hlavní regiony umožňují nasazení zón dostupnosti, tedy oddělených datových center pro maximální míru dostupnosti. Tak například Azure SQL Business Critical bude mít se zónami dostupnosti SLA 99,995% (vs. 99,99%) a sada VM přes zóny nabídne 99,99% (vs. 99,95% u availability setu).
- Rozsah služeb. Na každém kontinentu jsou klíčové regiony, kde jsou k dispozici všechny Azure služby a hardwarové konfigurace, zatímco v jiných regionech může být nabídka užší. Základní služby jako je compute, storage a networking jsou samozřejmě všude a klíčové platformní služby jako SQL, App Service nebo AKS v naprosté většině. Exotičtější záležitosti jako jsou některé AI služby, specializovaný hardware pro HPC nebo GPU modely a tak podobně v menších regionech být nemusí.
- Cena. Zatímco PaaS má stejné ceny po celém světě, základní komoditní služby IaaS mají rozdíly dané náklady v příslušné lokalitě.

# Azure regiony v Evropě
Základní, největší a nejdůležitější regiony jsou North Europe (Dublin) a West Europe (Amsterdam). Tyto mají maximální vybavenost, zóny dostupnosti a z toho pohledu bych je určitě doporučil - West Europe jako váš hlavní region, North Europe jako záložní.

V Německu se po vládních regionech (ty nebyly určeny pro věřejnost) relativně nedávno vybudovaly dva komerční regiony s tím, že ten hlavní je ve Frankfurtu (Germany West Central). Již brzy bude mít zóny dostupnosti a přestože je nový, je považován za další klíčový region. Dá se očekávat, že v průběhu příštích dvou let budou jeho schopnosti na úrovni West Europe a North Europe. Kromě toho je v Německu region Germany Central. Ten je určený pouze pro zákazníky, kteří běží v Germany West Central a potřebují DR lokalitu na území Německa (typicky vládní firmy).

Pak je tu několik regionů, které jsou menší a z pohledu funkcí tak mohou některé pokročilé věci chybět, ale to podstatné, tedy získat infrastrukturu, aplikační a databázové služby v dané zemi perfektně splňují. Obvykle je jeden z regionů považovaný za hlavní a je otevřený všem zájemcům bez omezení. Druhý region ve stejné zemi je určen jako DR lokalita pro ty zákazníky, kteří něco takového potřebují a nemohou opustit hranice. Ve Spojeném království je to Londýn podporující zóny dostupnosti a Cardiff pro DR. Ve Franci je hlavní Paříž s podporou zón dostupnosti a jako DR Marseille. V Norsku můžete využít Oslo, kde jsou zóny dostupnosti v plánu pro rok 2021 a Stavenger jako DR region. Ve švýcarském Zurychu je region s plánem pro zóny dostupnosti v roce 2022 a Geneva pro DR.

Následují regiony, které jsou jednoznačně zaměřené primárně pro lokální vlády nebo instituce podobného typu. Jsou to menší regiony, které nemají další pár a seznam služeb je omezený, ale to nejčastější jako je IaaS, PaaS databáze a aplikační platformy typu WebApp nebo AKS tam budou. V tuto chvíli jsou ve výstavbě čtyři takové lokální projekty. Italské Miláno, v Polsku Varšava, ve Španělsku Mardid a včera oznámený region Řecko.

O čem lze spekulovat do budoucna? Menších lokálních regionů může ještě pár vzniknout v dalších státech. Můj odhad je, že během pěti let se v rámci Evropy ještě pár regionů rozsvítí. Dalším trendem jsou Azure Edge Zones. Jedná se o technologii Azure Stack Edge, která není plnohodným cloudem, ale je jakousi vystrčenou nohou Azure, kterou z cloudu ovládáte a můžete na ni dávat některé cloudové služby pro lokální zpracování dat třeba v oblasti IoT nebo AI. Tuto technologii můžete dát kamkoli, třeba do vaší továrny nebo autobusu. Slyšeli jste ale o 5G sítích? Nebo o specializovaných IoT sítích typu LoRa, NarrowBand nebo Sigfox? Co kdyby operátoři ve svých datových centrech, kde zakončují tyto své sítě blízko k zákazníkům a zařízením, ve spolupráci s Microsoft provozovali pár racků Azure Stack Edge, které můžete využít pro předzpracování dat pěkně ta tepla před odesláním do Azure nebo provoz lokálního ML modelu pro rychlou reakci na anomálie? Takhle vznikají Azure Edge Zones - zatím ve státech, ale totéž se dá očekávat v mnoha dalších lokalitách a ve finále lze takto "dokrýt" oblasti, ve kterých Azure region nemá nebo kde to dává smysl z pohledu komunikačních uzlů operátorů.

# Srovnání latence a ceny
Pojďme si udělat jednoduchý test - změříme latenci a srovnáme ceny v některých regionech. Pro test latence použijeme qperf - nástroje typu ping nemají dobrou vypovídací hodnotu. Nicméně ujasněme si - měříme jednosměrnou latenci, nikoli round trip time, tedy jak dlouho trvá přenos informace z jednoho místa do druhého. Ping měří RTT, tedy požadavek tam, odpověď zpět. Pro API nebo web bude důžité RTT, pro stream dat spíše jednosměrná latence. Mimochodem použití technologií jako HTTP/2 a Azure Front Door dokáže dramaticky zvýšit rychlost vašeho webu díky paralelizaci a optimalizaci. Důvod proč nepoužít ping a jen nevydělit dvěma je fakt, že ICMP protokol má v Microsoft síti nejnižší možnou prioritu a nepředstavuje reálný provoz - vzhledem k tomu, že nejbližší POP je v Praze, jde to z místa kde měřím do všech regionů Microsoft sítí (s pravděpodobností řekněme 99% - přecijen globální BGP síť může někdy zvolit i jinou trasu, ale je to velmi nepravděpodobné - pokud chcete mít jistotu, vystavte svoje aplikace na WAF přímo v POPu, tedy využijte službu Azure Front Door... ale to je jiné téma). Nicméně moje měření neberte moc kriticky - zahrnuje i domácí WiFi a jde spíš o pohled na řády, než sofistikované měření.

Pokud vás zajímá latence mezi regiony, nemusíte si to měřit sami - Azure to dělá za vás a výsledky pravidelně zveřejňuje: [https://docs.microsoft.com/en-us/azure/networking/azure-network-latency](https://docs.microsoft.com/en-us/azure/networking/azure-network-latency)

![](https://docs.microsoft.com/en-us/azure/networking/media/azure-network-latency/azure-network-latency.png){:class="img-fluid"}

Teď zpět k mému nepřesnému testu z domácí WiFiny. Vytvořím si mašiny v různých regionech.

```bash
az group create -n latency-test-rg -l westeurope

az vm create -n we-vm \
    --location westeurope \
    -g latency-test-rg \
    --image UbuntuLTS \
    --nsg "" \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --admin-username tomas \
    --size Standard_D2s_v3 \
    --no-wait

az vm create -n ne-vm \
    --location northeurope \
    -g latency-test-rg \
    --image UbuntuLTS \
    --nsg "" \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --admin-username tomas \
    --size Standard_D2s_v3 \
    --no-wait

az vm create -n ge-vm \
    --location germanywestcentral \
    -g latency-test-rg \
    --image UbuntuLTS \
    --nsg "" \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --admin-username tomas \
    --size Standard_D2s_v3 \
    --no-wait

az vm create -n sw-vm \
    --location switzerlandnorth \
    -g latency-test-rg \
    --image UbuntuLTS \
    --nsg "" \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --admin-username tomas \
    --size Standard_D2s_v3 \
    --no-wait

az vm create -n fr-vm \
    --location francecentral \
    -g latency-test-rg \
    --image UbuntuLTS \
    --nsg "" \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --admin-username tomas \
    --size Standard_D2s_v3 \
    --no-wait
```

Pak se vždycky do VM připojím, nainstaluji a spustím qperf server.

```bash
ssh $(az network public-ip show -n we-vmPublicIP -g latency-test-rg --query ipAddress -o tsv)

sudo apt update
sudo apt install qperf -y
qperf
```

Ze svého počítače provedu test.

```bash
qperf -t 60 -v $(az network public-ip show -n we-vmPublicIP -g latency-test-rg --query ipAddress -o tsv) tcp_lat
```

| Region | Latence | Vzdálenost | Cena Standard_D2s_v3 |
|-------|--------|---------|---------|
| West Europe | 12,5 ms | 810 km | 87,6 USD |
| North Europe | 20 ms | 1670 km | 78,1 USD |
| Germany West Central | 10 ms | 480 km | 84 USD |
| Switzerland North | 13 ms | 600 km | 105,1 USD |
| France Central | 14 ms | 1000 km | 81,8 USD |

Co bych volil já? I nadále bych doporučil West Europe. Z pohledu cen komoditních věcí jako jsou ty nejběžnější VM je sice trochu výš, ale má úplně všechny služby, varianty serverů a novinky jsou tam obvykle nejdřív. Pokud používáte hodně hrubé infrastruktury a zejména tam, kde vám o latenci vůbec nejde (statistické výpočty, zpracování dat, matematické modely a simulace, rendering), North Europe je dobrá volba. Můžete tak například vybudovat landing zone ve West Europe (hub-and-spoke topologie, firewall apod.) pro aplikace, platformní služby a datovou analytiku, ale statistické výpočty a rendering provozovat v North Europe, protože pro tyto úkony nepotřebujete budovat firewall, WAFku a celou landing zone v tomto regionu.

Pokud ještě Azure landing zone nemáte, uvažujte i o Germany West Central. Zóny dostupnosti budou prý velmi brzy. Projděte si seznam služeb ve srovnání s West Europe [tady](https://azure.microsoft.com/en-us/global-infrastructure/services/?regions=germany-west-central,europe-west,non-regional&products=all) a uvidíte, že rozdíly jsou hlavně v oblasti ML, AI a chybí i některé dílky datové analytiky, nejsou k dispozici některé specializované stroje zejména ty s GPU. Pokud ale primárně potřebujete lift-and-shift migraci datového centra do IaaS, použít aplikační platformy a databáze a případné věci kolem AI a datové analytiky není problém mít ve West Europe, protože tam pro vás latence nehraje zásadní roli (výsledkem je aplikační API nebo PowerBI report, ne neustálá komunikace tam a zpět mezi klientem a serverem), nemusí být Frankfurt vůbec špatná volba.

Shrnuto - pro maximální šíři služeb a dobrou latenci bych založil hlavní hnízdo ve West Europe. Pokud je pro mě cloud o batch zpracování, latenci neřeším a hlavně používám IaaS, North Europe bude nejlevnější. Pokud je latence to nejdůležitější, Něměcko má dobré ceny IaaS, rozumnou nabídku služeb, ale pro oblast AI a datové analytiky můžete narazit na funkční limity (alespoň zatím).