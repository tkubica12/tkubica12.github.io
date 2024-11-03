---
layout: post
published: true
title: Kudy posílat odchozí provoz z Azure do Internetu aneb LB vs. VNET NAT vs. Azure FW
tags:
- Networking
---
Před asi dvěma lety se v oblasti IaaS zahájila změna v Azure z implicitního řešení odchozího provozu (Azure LB Basic apod.) do více předvídatelného a řiditelného modelu. To je myslím pozitivní, ale všechno je dobré si víc rozmyslet. A to dnes uděláme a vyzkoušíme jednu novinku v této oblasti - Virtual Network NAT.

# Co je odchozí provoz
Nejdřív si řekněme co vlastně budeme řešit. Jsou dvě základní kategorie provozu podle směru. Inbound je to, co zahajuje někdo mimo Azure a přistupuje k nějaké aplikaci či službě, typicky přes veřejnou IP adresu. Ta bude přiřazena třeba přímo k síťové kartě VM, k load balanceru, k síťové virtuální krabičce jako je Azure Firewall nebo reverse proxy typu Azure Application Gateway.

My se dnes ale bavíme o outbound. Jde o provoz, který vznikl ve VM, ta ho iniciuje. Může jít o stažení balíčku z Internetu, odeslání dat na nějaký venkovní endpoint, zavolání nějakého API pro stažení předpovědi počasí a tak podobně.

# Varianty řešení odchozího provozu
Rozlišoval bych pět variant řešení odchozího provozu.

## Public IP na NIC
Můžete vytvořit Public IP a svázat ji se síťovou kartou VM a v ten okamžik bude nejen inbound provoz chodit tudy, ale i outbound. Místo SNAT tady bude docházet k IP NAT 1:1 (nebude se šachovat s porty, pouze se privátní IP prohazuje s public IP), takže nehrozí žádné vyčerpání volných portů a tak podobně. Na druhou stranu aplikaci byste asi neměli vystavovat takhle napřímo z bezpečnostních důvodů.

## Implicitní SNAT
Pro pohodlí začátačníků zůstává stále v platnosti implicitní SNAT. Pokud tedy vytvoříte VM ve VNETu a tato VM nebude mít veřejnou IP adresu, Azure zajistí odchozí provoz sám a zdarma. Provede tedy SNAT (resp. PNAT, tedy pro každou session) a to tak, že nebudete nikdy dopředu vědět jaká zdrojová IP to je a ta se bude pořád měnit. Pro stahování balíčků je to samozřejmě jedno, ale pokud přistupujete na nějaký externí systém, často vám tady bude chybět předvídatelnost (protistrana si chce třeba dát whitelist na vaší IP). Nezapomeňte taky, že pokud použijete Azure LB Standard na privátní adrese (bez veřejky), přestane tento implicitní SNAT fungovat a protože na LB není veřejka, jste bez Internetu! Musíte SNAT zajistit explicitně (na rozdíl od LB Basic).

## Azure Virtual Network NAT
Novinkou, kterou si dnes vyzkoušíme, je VNET NAT brána. Je to explicitní řešení pro SNAT, které svážete s konkrétními subnety. Má přednost před volbami typu IP na síťovce nebo LB s outbound pravidly a může obsahovat 1 až 16 IP adres (někdy jich potřebujete víc, pokud máte strašně moc odchozích session a 64k portů by vám bylo málo) a těch 16 IP může být Public IP Prefix (koupíte si z Azure celý blok, takže whitelisting bude stále velmi jednoduchý). Všechno co v subnetu bude, VM, AKS, ACI, bude na odchozím provozu NATováno na tyto IP. Každý subnet může mít jinou bránu. Dostáváte tak velmi dobře pod kontrolu odkud pod jakou IP co odchází. VNET NAT ale není zadarmo, platíte zde asi 32 USD měsíčně za její existenci + asi 45 USD za přenesený TB. 

VNET NAT je skvělý ke kontejnerům - umožní vám například řešit odchozí provoz z AKS. Nepotřebujete tak Azure LB s public IP před clusterem nebo můžete mít nodepooly v různých subnetech a dávat jim jinou odchozí adresu a takhle si řídit co odkud odchází (přes Kubernetes Node Affinity). To jsou scénáře, které dosud byly možné pouze s použitím firewallu.

## Azure Load Balancer Standard
Azure LB je nejčastěji používaný pro inbound - jednu veřejnou IP chcete balancovat na backend pool. Nicméně Azure LB Standard podporuje i outbound pravidla, takže můžete dobře řídit i to, pod jakou IP bude odcházet provoz iniciovaný přímo z VM za balancerem. U varianty Standard už máte velkou flexibilitu backendů, takže se dělá třeba kombinace Azure LB Standard s privátní adresou pro dvě frontend VM interní aplikace a pak ještě Azure LB Standard s public IP, do kterého dáte všechny VM a jedete přes něj odchozí provoz do Internetu. Takové řešení je málo intuitivní a VNET NAT to řešeí elegantněji, nicméně stále platí, že zejména u Standard LB s public adresou můžete chtít tuto použít i pro odchozí provoz a řešit to outbound pravidly. LB Standard stojí asi 18 USD za svou existenci a jen 5 USD za přenesený TB, takže je to určitě levnější varianta.

Nicméně Azure LB nemůžete použít pro některé situace s kontejnery, zejména Azure Container Instances nebo Azure Kubernetes Service s Azure CNI (Advanced Networking). AKS LB má na backendu pouze nody, ale kontejnery přímo ne.

Nicméně LB sechová jinak, než VNET NAT brána. LB je decentralizovaný, takže k NAT dochází přímo v hostiteli, čímž nelze postupovat plně synchronizovaně a dynamicky si přidělovat porty. Z toho důvodu jsou NAT porty napevno alokovány na nody. Pokud dáte do LB 100 VM a každé dáte 500 portů alokaci (zdrojové porty použité pro PAT), mohou vám porty dojít (protože jedna jich potřebuje strašně moc, tedy víc jak 500 spojení na stejnou cílovou IP v Internetu, druhá ne - ale není obvyklé na tohle narazit, protože většinou máte rozdílné destination IP a tam se porty používají opakovaně). VNET NAT je dražší, protože přes ní reálně data protékají a ona je tak schopna porty alokovat dynamicky. Pro masivní počty odchozích session je tak VNET NAT určitě lepší volba.

## Azure Firewall či jiná appliance
Pátá varianta je vzít funkci SNAT a udělat ji na nějakém boxíku mimo Azure SDN síť. Takovou virtuální replikovanou krabičkou je Azure Firewall, ale i NGFW třetí strany. V tomto scénáři musíte modifikovat směrovací tabulky (UDR - Route Table) a provoz směřující do Internetu posílat třeba na Azure Firewall. Ten je schopen provést SNAT, ale nabízí výbornou kontrolu. Na rozdíl od všech ostatních variant je Azure Firewall jedno místo, které můžete použít k řízení odchozích pravidel a to včetně FQDN záznamů, reputační služby (threat intelligence) a poslouží i pro DNAT (vystavení) či interní zónování. Je to tedy řekl bych jiná liga co do vlastností. To se ale projevuje i na ceně, která je asi 912 USD měsíčně + 16 USD za přenesený TB.

Do scénáře změny routingu samozřejmě patří nejen Azure Firewall či NGFW v Azure, ale i prohnání přes krabičku v on-premises ... ale to považuji za nevhodný design, maximálně pro nějaké začátky, než máte v Azure více aplikací a začne dávat smysl tam vybudovat i "perimetr".

# PaaS služby a odchozí provoz - šetřete se Service Endpointy
PaaS služby jsou by default outbound komunikace (třeba SQL databáze) a pokud neřeknete jinak, budou procházet jedním z pěti výše uvedených řešeních. To může znamenat nějaké náklady. TB dat stojí 45 USD v VNET NAT, 5 USD v LB a 16 USD v Azure Firewall. I v případě appliance třetí strany to má velký vliv - ta obvykle není placená tak cloudově jako Azure FW (který škáluje automaticky a kromě fixní sazby doplácíte dle využívání) a musíte si pořizovat core licence. Prohnat tím PaaS služby může znamenat nákup licencí navíc.

Pokud použijete Service Endpoint, přemostíte tato řešení a komunikace poteče do PaaS napřímo a je naprosto zdarma. Takže rozhodně vyjde levněji, než posílání přes VNET NAT, LB nebo Azure FW a to zejména pokud se bavíme o masivních transferech jako je load dat do datového skladu. 

Service Endpoint jde napřímo, ale stále mají pakety public IP jako destinaci a těm, co tohle vadí, doporučuji použít Private Link (v GA už dnes pro mnoho služeb a pro další v preview). Ten sice není zadarmo, ale pokud použijete Private Link blízko u aplikace na přímou, ale privátní komunikaci, finančně stále vyjde levněji, než některé varianty popsané výše, protože jeho existence stojí asi 6,5 USD a TB dat vyjde na 10 USD (data protékající Azure FW nebo VNET NAT jsou dražší).

# Vyzkoušejme Azure Virtual Network NAT
Pustíme se do testu nové funkce VNET NAT. Zajímavé je, že ta má přednost před IP na síťovce i IP na balanceru, ale současně tyto nerozbíjí pro inbound. Vyzkoušíme si následující nastavení:
- VNET a v něm dva subnety
- Do každého subnetu dáme VNET NAT s jinou IP (odchozí provoz ze sub1 půjde z jiné IP, než provoz ze sub2)
- V sub1 uděláme VM, která bude mít na NIC public IP a současně bude zařazena v LB Standard s public IP
- V sub2 uděláme VM s public IP

Pojďme na to:

```bash
# Create resource group
az group create -n networking -l westeurope

# Create VNET
az network vnet create -n mynet -g networking --address-prefix 10.0.0.0/16

# Create public IPs
az network public-ip create -n natip1 -g networking --sku Standard
az network public-ip create -n natip2 -g networking --sku Standard
az network public-ip create -n lbip -g networking --sku Standard
az network public-ip create -n vm1ip -g networking --sku Standard
az network public-ip create -n vm2ip -g networking --sku Standard

# Create NAT gateways
az network nat gateway create -n mynat1 \
    -g networking \
    --public-ip-address natip1
az network nat gateway create -n mynat2 \
    -g networking \
    --public-ip-address natip2

# Create subnet NSG
az network nsg create -n mynsg -g networking
az network nsg rule create --nsg-name mynsg \
    -g networking \
    -n SSH \
    --destination-port-ranges 22 \
    --access Allow \
    --protocol TCP \
    --priority 200
az network nsg rule create --nsg-name mynsg \
    -g networking \
    -n HTTP \
    --destination-port-ranges 80 \
    --access Allow \
    --protocol TCP \
    --priority 210

# Create subnets with NAT
az network vnet subnet create -n sub1 \
    --vnet-name mynet \
    -g networking \
    --nat-gateway mynat1 \
    --address-prefixes 10.0.1.0/24 \
    --network-security-group mynsg
az network vnet subnet create -n sub2 \
    --vnet-name mynet \
    -g networking \
    --nat-gateway mynat2 \
    --address-prefixes 10.0.2.0/24 \
    --network-security-group mynsg

# Create LB
az network lb create -n mylb \
    -g networking \
    --sku Standard \
    --public-ip-address lbip \
    --backend-pool-name backend

az network lb probe create -n httpProbe \
    -g networking \
    --lb-name mylb \
    --protocol Http \
    --port 80 \
    --path "/"

az network lb rule create -n http \
    -g networking \
    --lb-name mylb \
    --protocol Tcp \
    --frontend-port 80 \
    --backend-port 80 \
    --backend-pool-name backend \
    --probe-name httpProbe

# Create NIC for balanced VM, but with public IP also
az network nic create -n vm1nic \
    -g networking \
    --vnet-name mynet \
    --subnet sub1 \
    --lb-name mylb \
    --lb-address-pools backend \
    --public-ip-address vm1ip

# Create VM
az vm create -n vm1 \
    -g networking \
    --image UbuntuLTS \
    --size Standard_B1ms \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --nics vm1nic \
    --storage-sku Standard_LRS

# Create VM in sub2
az vm create -n vm2 \
    -g networking \
    --image UbuntuLTS \
    --size Standard_B1ms \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --storage-sku Standard_LRS \
    --public-ip-address vm2ip \
    --vnet-name mynet \
    --subnet sub2
```

Vypišme si všechny veřejné IP.

```bash
# List all public IPs
az network public-ip list -g networking -o table

Name    ResourceGroup    Location    Zones    Address        AddressVersion    AllocationMethod    IdleTimeoutInMinutes    ProvisioningState
------  ---------------  ----------  -------  -------------  ----------------  ------------------  ----------------------  -------------------      
lbip    networking       westeurope           51.138.50.215  IPv4              Static              4                       Succeeded
natip1  networking       westeurope           51.138.50.107  IPv4              Static              4                       Succeeded
natip2  networking       westeurope           51.138.50.201  IPv4              Static              4                       Succeeded
vm1ip   networking       westeurope           51.138.51.1    IPv4              Static              4                       Succeeded
vm2ip   networking       westeurope           51.138.51.19   IPv4              Static              4                       Succeeded
```

Nejdřív se připojíme do vm1 použitím její public IP na NIC. Tím si ověříme, že tato pro inbound funguje (odpovědi k nám přichází z této IP) i když je VM za balancerem a i když máme na subnetu VNET NAT. Až budeme vevnitř, tak zjistíme, z jaké IP jde outbound traffic (ipconfig.io je stránka a API, které vrátí naší zdrojovou adresu). Všimněte si, že je to natip1.

```bash
# Connect to vm1 via its public IP
ssh tomas@$(az network public-ip show -n vm1ip -g networking --query ipAddress -o tsv)

# Test outbound ip from vm1
curl ipconfig.io
51.138.50.107
```

Na vm1 nainstalujeme web server a zkusíme se připojit přes Azure LB Standard. Funguje. Znamená to tedy, že inbound přes LB není nijak rozbitý, odpovědi přichází z lbip.

```bash
# Install web server in vm1 and test LB connectivity
sudo apt update
sudo apt install nginx -y
exit

curl -I $(az network public-ip show -n lbip -g networking --query ipAddress -o tsv)
HTTP/1.1 200 OK
Server: nginx/1.14.0 (Ubuntu)
Date: Tue, 17 Mar 2020 17:38:36 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 17 Mar 2020 14:18:12 GMT
Connection: keep-alive
ETag: "5e70dc24-264"
Accept-Ranges: bytes

```

Teď ještě vyzkoušíme, že outbound provoz z vm2 půjde z natip2.

```bash
# Connect to vm2 via its public IP
ssh tomas@$(az network public-ip show -n vm2ip -g networking --query ipAddress -o tsv)

# Test outbound ip from vm2
curl ipconfig.io
51.138.50.201
```

Jak vidíte VNET NAT umožní dostat věci dobře pod kontrolu. Oceníte to zejména v situacích, kdy komunikujete přes Internet s protistranou, která vyžaduje whitelisting IP adres nebo používáte privátní LB Standard a řešíte kudy s odchozím provozem do Internetu.

Na závěr ale poznámka k redundanci. VNET NAT není zónově redundantní služba. Je zone-aware. Můžete jako já výše použít nastavení bez určení zóny a také můžete zónu stanovit. VNET NAT je vysoce dostupné řešení, ale ne až na úroveň automatického překlápění v případě havárie zóny. Měli byste tedy o tom přemýšlet a pro VM v různých zónách zajistit i různé NAT brány v zónovém nastavení. V tomto ohledu je Azure LB nebo Azure Firewall jednodušší cesta k zónové redundanci.


Shrňme si to. Za mne je ideální pro outbound provoz použít Azure Firewall, protože získáte kontrolu nejen nad síťařinou (co odkud jde), ale bude automaticky zónově redundantní a můžete dobře řídit bezpečnostní pravidla včetně FQDN. Ta investice se myslím vyplatí pokud provozujete prostředí v nízkých jednotkách regionů. Pokud máte globální systém s hrstkou malých komponent v 30 regionech, nemusí dávat Azure Firewall finančně smysl - tam bych outbound řešil jinak a to implicitně (zdarma), na Azure LB (pokud není masivní co do počtu session na jednu destinaci a počtu VM) a u větších počtů VM bych zvážil VNET NAT.