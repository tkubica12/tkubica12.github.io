---
layout: post
title: Service chaining síťových krabiček třetích stran v Azure síti s Gateway LB
tags:
- Networking
---
Azure nabízí výborné nativní síťové funkce jako je Application Gateway WAF, Front Door, Azure Firewall nebo Traffic Analytics (z NSG flow dat), ale někdy chcete dát přednost třetím stranám - ať z důvodu jednotnosti mezi prostředími, kvůli speciálním funkcím, certifikaci regulátora, využití už nakoupených licencích nebo lepším možnostem úprav specificky pro váš scénář. Jak ale zapojit takovou síťovou appliance (NVA) do provozu v Azure síti? Kromě tradiční metody přes routing máte dnes k dispozici i transparentní service chaining - a to je pro některé scénáře nesmírně zajímavé. Pojďme si vyzkoušet a pochopit, jak to funguje.

Všechny podklady k dnešnímu článku najdete na mém [GitHubu](https://github.com/tkubica12/azure-gateway-lb). Připravil jsem tři scénáře - webová farma bez bezpečnosti, webová farma s tradičním začleněním bezpečnosti přes routing a webová farma zabezpečená přes service chaining na Azure Gateway Load Balancer.

# Řešení přes routing a jeho limity
V první generaci řešení jste vzali NVA VM a dali jí dvě síťovky - vnější (s přiřazenou public IP) a vnitřní. Aplikační VM jste donutili routovat přes NVA tím, že jste v směrovacích pravidlech (UDR) zařídili vnitní IP NVA jako next-hop (tradičně navíc přes VNET peering, takže aplikace je ve spoke VNET a je napojena na centrální hub VNET). Nicméně v tuto chvíli když NVA umře, máte problém (a je teď jedno, jestli je to tím, že je nějaká nedostupnost AZ nebo software NVA zamrznul). Přidáte tedy druhou ve standby režimu a kolem toho postavíte skripty, které zařídí v případě nedostupnosti aktivní NVA změnu routingu (přepíší UDR na druhý box) a přesun public IP (odeberou z jedné NVA a přiřadí ke druhé). 

V druhé generaci přišel ke slovu balancing. Public adresy nebudeme dávat přímo na NVA, ale na Azure LB před ní a provoz buď rozhazovat na NVA (active/active) nebo směrovat na jedinou aktivní (tu, která odpovídá na health probe). Z vnitřního směru UDR potřebuje konkrétní next-hop vnitřní adresu, takže tam udělám pro změnu privátní Azure LB (bez public adresy) a ta funguje jako next-hop pro aplikační stroje. Nicméně pokud jedeme v active/active režimu, je tady problém, že rozhodnutí balancerů, které flow kam poslat, jsou nezávislá a tak by mohla vzniknout asymetrie - to se řeší tím, že NVA dělá SNAT směrem do vnitřní sítě (tzn. aplikace vidí jako zdrojovou IP adresu tu z konkrétní instance NVA, nikoli skutečnou public IP klienta, čímž se zajistí, že komunikace zpět poteče přes tu správnou instanci NVA). 

Později se přidal ještě Route Server, tedy přidal možnost sice nechat veřejný balancer s public IP, ale vnitřní balancer (fungující jako next-hop) nahradit dynamickým routingem s BGP a tak řešit redundanci (a dokonce i rozdělení zátěže, protože pak VNET podporuje ECMP).

V každém případě ale všechna tato řešení mají i určité nevýhody:
- Public IP vaší aplikace žije u síťového prvku, tedy obvykle mimo dosah aplikačního týmu. Jasně - v klasickém IT je to tak normální, ale pro cloud-native éru to může být omezující.
- Routing je zásadní a může se docela zkomplikovat, zejména při složitých hub and spoke topologiích, když se rozhodnete, že potřebujete víc kategorií NVA (jednu pro firewalling, jednu pro IPSec a routing nedej bože ještě s nějakým overlay do interní sítě mapovaným na VRFky ve firmě, jednu pro externí firewall) - to je pak docela síťové porno.
- NVA musí být aktivní součástkou sítě, musí minimálně routovat (někdy i NATovat, dělat proxy). To nemusí být vhodný režim pro některá síťová řešení jako je analýza nebo nahrávání provozu, L7 DDoS ochrana, IPS nebo transparentní firewall.

Ještě poznamenám, že appliance třetí strany může být také součást nasazení Azure Virtual WAN, nicméně samostatně ji neuvádím, protože jde defacto o více spravovanou a automatizovanou variantu využívající už popsaných postupů (route server, balancer, směrování).

# Azure Gateway Load Balancer
Nejnovější přírůstek do variant začlenění síťových krabiček jde cestou tunelování a naprosté transparentnosti. V budoucnu má sloužit jak pro north-south traffic (přístup na a z Internetu) tak pro east-west (např. mezi projekty, prostředími, do on-prem), ale zatím je k dispozici jen pro první možnost.

Základem je, že Azure na určitém místě sítě (konkrétně na public balanceru nebo síťovce s public adresou) dokáže provoz vzít, zabalit do tunelu (tedy ponechat pakety bez jakýchkoli změn) a tím doručit do vaší krabičky (nebo ještě lépe - současně dělá i balancing na celý cluster vašich krabiček s dodržením symetrie flow). Ta následně provoz vrátí do druhého tunelu, kterým to dojede přesně na to místo, z kterého se odbočka udělala a Azure pokračuje ve zpracování paketu jako by se nic nedělo. Jinak řečeno vaše appliance nemusí do paketů nijak zasahovat a vůbec není ve stejné síti! Na technický detail a reálnou ukázku se hned podíváme, ale zmiňme výhody:

- Public IP žije u aplikace, ne u síťařů.
- Architekturu aplikace není potřeba nijak měnit ani řešit složitý routing jako jsou UDR, peering nebo hub-and-spoke.
- Síťová appliance nejen, že může žít ve zcela izolovaném VNETu bez nutnosti je propojovat, ale dokonce i v jiné subskripci, v jiném regionu nebo i jiném tenantu. Umím si tak představit, že se v budoucnu objeví třeba i plně spravované služby třetích stran (bezpečnostní krabička as a service).
- Síťová appliance nepotřebuje nijak modifikovat pakety (routovat, NATovat), takže řešení je vhodné i pro transparentní filtraci, DDoS, nahrávání a analýzu provozu.

# Praktická zkouška
Na tomto [repo](https://github.com/tkubica12/azure-gateway-lb) jsem připravil tři scénáře webové farmy s balancerem - bez bezpečnosti, s tradičně řešeným NVA a s Azure Gateway Load Balancer.

Místo reálných NVA používám Linux mašinu s routingem a iptables pro NAT v případě tradičním a VXLAN a Bridge v případě GW LB. Všechno je v Bicep šablonách včetně instalace webu a konfigurace NVA přes cloud-init. Do virtálek na testy (třeba pro tcpdump) skáču přes sériový port, což je skvělý způsob, který už jde nejen z portálu, ale i přes Azure CLI, takže nepotřebuji žádný přístup zvenku, Bastion, jump ani nic takového.

## Varianta bez bezpečnosti
Jde spíše o referenční řešení pro srovnání po zavedení bezpečnosti co do nárůstu komplexity. Jde o public LB a za ním wenovou farmu, kterou pro zjednodušení dávám v jediné instanci VM, ale lze si jich tam samozřejmě představit bezpočet.

Ze směru zvenku:
Public LB -> VM s webem

Ze směru zevnitř:
VM s webem -> Public LB

## Tradiční bezpečnost
K původnímu řešení toho musím hodně přidat, konkrétně:
- Druhý VNET fungující jaku hub a v něm síťovou appliance
- Peering mezi VNETy a UDR pro vynucení routingu přes NVA
- Public IP se musí přesunout k NVA, která bude provoz nabírat a bude na ní DNAT (před aplikací bude teď LB s vnitřní adresou)
- Pro balancování bude Public IP NVA žít na jejím public balanceru a z pohledu NVA bude můj web poslouchat na portu 1001, na který budou mířit pravidla na public LB (klasické řešení typické třeba s F5 instalací v Azure - pokud potřebuji víc aplikací, použijí SNI na stejné adrese nebo přidám další public IP a její pravidla půjdou třeba na port 1002, kde NVA bude očekávat druhou appku).
- Jako next-hop ve směru zevnitř je interní LB v nastavení tzv. HA ports (tedy, že nabírá všechno a nepotřebuje pravidlo pro každý port)

Ze směru zvenku:
Public LB -> NVA -> Privátní LB aplikace přes VNET peering -> VM s webem

Ze směru zevnitř:
VM s webem -> Privátní LB NVA přes VNET peering -> NVA -> Outbound přes Public LB na NVA

Když se v šabloně podíváte (nva.bicep), tady je co musí NVA dělat na příkladu Linuxu:

```bash
# Enable routing
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -p

# Enable outbound SNAT (Internet access for VMs)
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/8 -o eth0 -j MASQUERADE

# Enable service - rewrite destination to app LB IP and rewrite source to self
sudo iptables -t nat -A PREROUTING -p tcp -m tcp --dport 1001 -j DNAT --to-destination 10.0.0.100:80
sudo iptables -t nat -A POSTROUTING -p tcp -d 10.0.0.100 --dport 80 -j MASQUERADE
```

## Service chaining
Srovnejme teď inspekci na NVA transparentním způsobem s Azure Gateway Load Balancer. Vycházíme z úplně původního řešení s public balancerem přímo před aplikací. Změní se jedno jediné políčko - reference na Azure GW LB, díky které se provoz odveze na inspekci.

Co vznikne na straně NVA:
- Jeden interní balancer v SKU Gateway Load Balancer, v jehož konfiguraci backendu je jedna věc navíc - definice tunelů. Ty jsou v Azure k dispozici na tradiční VXLAN (pro zajímavost - VXLAN je hodně rozšířená, ale Azure vnitřně používá NVGRE a bylo by bezpečnostní riziko nabízet stejný tunel na provider straně i pro uživatele... naopak AWS na provider straně používá VXLAN a proto podobná služba GW LB v jejich případě implementuje GENEVE, ne VXLAN ... a v GCP myslím tohle neumí, pokud ano, napiště mi).
- Separátní VNET pro NVA bez peeringu do sítě s webem
- Protože NVA jsou za interním balancerem, nemají přístup k Internetu. Já ho potřebuji (abych mohl stáhnout balíček a tak), takže jsem do řešení přidat NAT Gateway. Nicméně tím se nenechte mást - pro řešení jako takové není nutná.

Ze směru zvenku:
Public LB -> farma NVA -> Public LB (pokračuje kde přestal před odbočkou) -> VM s webem 

Ze směru zevnitř:
VM s webem -> Outbound přes Public LB aplikace -> farma NVA -> Outbound přes Public LB aplikace (pokračuje kde přestal)

Nejlépe je myslím vidět co se děje, když se podíváte na rozchození Linuxu v roli NVA. Potřebuji vytvořit tunel interface s VXLAN pro vstup a výstup a mezi nimi bude NVA dělat nějakou práci (inspekce, filtrování a cokoli takového), což v mém případě bude jen průtokáč přes Bridge (nicméně získávám vizibilitu - mohl bych pakety třeba nahrávat).

```bash
# Install bridge support
sudo apt update
sudo apt install bridge-utils -y

# Create VXLAN interfaces
sudo ip link add vxlan0 type vxlan id 900 dev eth0 dstport 10800 remote 10.1.0.100
sudo ip link set vxlan0 up
sudo ip link add vxlan1 type vxlan id 901 dev eth0 dstport 10801 remote 10.1.0.100
sudo ip link set vxlan1 up

# Create bridge
sudo brctl addbr br0
sudo brctl addif br0 vxlan0
sudo brctl addif br0 vxlan1
sudo ip link set br0 up
```

Doporučuji se připojit do NVA přes sériový port a zkusit si pochytat pár paketů v okamžiku, kdy přistupujete na web aplikace.

```bash
az serial-console connect -n nva1 -g gwlb-security-rg
sudo tcpdump -i vxlan0
```



Kdy Azure Gateway Load Balancer zvažovat? Vidím za sebe čtyři hlavní scénáře.

Pokud si chcete do Azure pořídit řešení některého z partnerů, které je vyloženě dělané jako "neviditelná" služba (analýza provozu, IPS, transparentní filtrace, DDoS), je tohle prakticky jediné rozumné řešení.

Druhý za mě svělý scénář je pro implementaci firewallu nebo reverse proxy ve firmách, kde chtějí jít cestou agilnějšího víc distribuovaného přístupu. Hub and spoke topologie nebo Virtual WAN jsou dnes jednoznačně nejčastějším režimem nasazování síťařiny a dávají obrovský smysl. Nicméně něco tak složitěho nemusí být dobré pro menší firmy, pro firmy hodně decentralizované (třeba investiční společnost nabízející společný Azure pro mnoho malých firem) nebo ty, které jedou čistý DevSecOps od A do Z.

Třetí situace, kterou tahle technologie otevírá, jsou bezpečnostní krabice jako služba, protože NVA může být klidně i v jiném tenantu, třeba u poskytovatele takové služby. Představuji si to třeba tak, jak ZScaler přinesl službu spravované cloudové HTTP proxy firmám - tentokrát ale místo nějakého software nebo nutných změn na straně OS odbočku k poskytovateli zajistí přímo Azure na úrovni sítě.

Čtvrtá situace je jednoduše to, že váš poskytovatel řešení přejde na tuto metodu. Tedy nebude to o nějaké změně nákupního modelu, procesů, rozdělení odpovědností nebo celkové architektuře. Ještě nevím jak tohle přesně vypadá, ale už mnoho dodavatelů jako je Cisco, F5, Fortinet, Check Point, Palo Alto nebo Citrix deklarovali podporu. Víc najdete [tady](https://azure.microsoft.com/en-us/blog/enhance-thirdparty-nva-availability-with-azure-gateway-load-balancer-now-in-preview/).

V každém případě service chaining je technologicky velmi zajímavý a očekávám, že v tomto a příštím roce uvidíme mnoho tradičních dodavatelů přecházejících na tenhle model jako přimární způsob integrace. V horizontu 2-3 let bych odhadoval nárůst plně spravovaných služeb síťové bezpečnosti ať už v nějaké nové generaci nativního produktu nebo od třetích stran jako budou sami dodavatelé (zvládne například F5 přechod na F5aaS v cloudu?), partneři (z prodejců síťařiny se stanou poskytovatelé služby) nebo noví žraloci (např. když to F5 nezvládne). Co myslíte vy?