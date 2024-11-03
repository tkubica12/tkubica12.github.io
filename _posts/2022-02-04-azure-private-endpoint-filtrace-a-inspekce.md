---
layout: post
title: 'Azure Private Endpoint - co dělat, když bezpečnostní oddělení požaduje filtraci nebo inspekci komunikace?'
tags:
- Networking
- Security
---
Platformní služby se typicky dělí na ty, které dokáží fyzicky běžet uvnitř zákaznické sítě (Azure Database for MySQL/PostgreSQL Flexible Server, Application Gateway, App Service Environment, SQL MI apod.) a ty, které jsou hostované v prostředí Microsoftu a do své vnitřní sítě je připojíte technologií Private Endpoint (Azure SQL, Azure Monitor a Sentinel, Storage Account, AKS, Azure Container Registry, Service Bus, Cosmos DB a mnoho dalších). Považuji to za dobré zvýšení bezpečnosti a doporučuji používat. Jakmile je Private Endpoint ve vnitřní síti, doporučuji ho dát co nejblíže k projektu, který službu využívá, takže provoz nejde přes nějaké firewally a podobná zařízení. V moderní architektuře je instance služby typicky dedikovaná pro konkrétní projekt, takže z ostatních projektů nebo on-premises do ní přímý přístup úplně nepotřebuji a i kdyby ano, maximální důraz se v zero trust prostředí klade na autentizaci. Je daleko důležitější mít kvalitní authn a authz s Azure Active Directory, než si po staru hrát jen se síťovou bezpečností a při tom používat zastarý koncept jméno/heslo žijící ve službě.

Realita enterprise zákazníků je ale často taková, že chtějí i uvnitř projektu jemně segmentovat, filtrovat provoz nebo provádět jeho inspekci. Potíž je v tom, že Private Endpoint technologie aktuálně v GA nepodporuje tradiční řešení Azure sítí jako je NSG nebo UDR pro směrování přes firewall či inspekční zařízení. Požadavky ale splnit lze už dnes a podívejme se jak. Navíc se na vylepšeních pracuje a některá jsou v public preview, takže se podívejme i na ně.

# Filtrace s NSG
Network Security Group se aktuálně neaplikuje na provoz přicházející do Private Endpoint. Jste schopni samozřejmě zajistit filtrace na outbound z vašich serverů či kontejnerů, to není problém. Ale z pohledu jednoduchosti konfigurace byste možná preferovali NSG na vstupu do Private Linku. To je dnes možné v rámci public preview (v některých regionech, například v North Europe) a vyzkoušejme si to.

Celý skript je [tady](https://gist.githubusercontent.com/tkubica12/cbb54b0c425be2ee3210ea08b6f687d7/raw/4a3f3f4d1f57ca4a74bf0a72d548fc40da50e825/privateEndpointFiltering.sh)

Tady jsou "přípravné práce".

```bash
# Register preview feature
az feature register --namespace Microsoft.Network -n AllowPrivateEndpointNSG
az feature show --namespace Microsoft.Network -n AllowPrivateEndpointNSG  # Wait until Registered
az provider register -n Microsoft.Network

# Create resource group
az group create -n plink -l northeurope

# Create NSG
az network nsg create -g plink -n plink-nsg 
az network nsg rule create -g plink \
    --nsg-name plink-nsg \
    -n filterip \
    --priority 200 \
    --source-address-prefixes 10.0.0.4/32 \
    --destination-port-ranges 80 443 \
    --access Deny \
    --protocol Tcp

# Create VNET
az network vnet create -g plink -n plink --address-prefix 10.0.0.0/16
az network vnet subnet create -g plink --vnet-name plink -n vm --address-prefixes 10.0.0.0/24
az network vnet subnet create -g plink --vnet-name plink -n plink --address-prefixes 10.0.1.0/24 --disable-private-endpoint-network-policies true --nsg plink-nsg

# Create diagnostic storage account (for serial console access)
az storage account create -n tomasplinkstore77534 -g plink --sku Standard_LRS

# Create target storage account (for private endpoint test) and upload file
az storage account create -n tomastarget7754235 -g plink --sku Standard_LRS
az storage container create -n test --public-access blob --account-name tomastarget7754235
echo "This is my test content" > data.txt
az storage blob upload --account-name tomastarget7754235 --container-name test --file data.txt -n data.txt
rm data.txt

# Create source VM
az vm create -n sourcevm \
    -g plink \
    --image UbuntuLTS \
    --size Standard_B1s \
    --authentication-type password \
    --boot-diagnostics-storage tomasplinkstore77534 \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --nsg "" \
    --public-ip-address "" \
    --vnet-name plink \
    --subnet vm \
    --no-wait

# Create private endpoint and DNS zone
az network private-endpoint create \
    -n plink \
    -g plink \
    --vnet-name plink \
    --subnet plink \
    --private-connection-resource-id $(az storage account show -n tomastarget7754235 -g plink --query id -o tsv) \
    --group-id blob \
    --connection-name plinkconnection  

az network private-dns zone create -n privatelink.blob.core.windows.net -g plink

az network private-dns link vnet create \
    -g plink \
    --zone-name privatelink.blob.core.windows.net \
    --name dnslink \
    --virtual-network plink \
    --registration-enabled false

az network private-endpoint dns-zone-group create \
   -g plink \
   --endpoint-name plink \
   --name group \
   --private-dns-zone privatelink.blob.core.windows.net \
   --zone-name privatelink.blob.core.windows.net
```

Připojím se do své VM a zkusím přistoupit na storage za private endpointem. Prochází to, což ukazuje, že NSG není pro Private Endpoint aplikováno.

```bash
# Connect to source VM and test connection
az serial-console connect -n sourcevm -g plink
curl https://tomastarget7754235.blob.core.windows.net/test/data.txt # Works! Inbound NSGs are not enforced
```

Zapneme si preview funkci, která nám dovolí zapnout vynucení politik na private endpointech. Vyzkoušíme a ano, provoz se blokuje - NSG funguje.

```bash
# Enable network policies for private endpoints (in preview)
az network vnet subnet update -g plink --vnet-name plink -n plink --disable-private-endpoint-network-policies false

# Connect to source VM and test connection
az serial-console connect -n sourcevm -g plink
curl https://tomastarget7754235.blob.core.windows.net/test/data.txt # BLOCKED by NSG
```

# Inspekce v síťovém prvku, například Azure Firewall nebo appliance třetí strany
Někteří zákazníci vyžadují kontrolu tohoto provozu ve svém zařízení. Osobně nejsem zastáncem provádění nějaké inspekce třeba databázového provozu. Vychází to z tradičního prostředí s jednou gigantickou databází uprostřed, ale v moderním světě mikroslužeb, kde má každá svojí DB, frontu a tak podobně, tak je takováto strategie myslím neudržitelná a zbytečná. Nicméně cloud není jen o nejnovějších aplikacích, takže na tento požadavek narazíte a je relevantní vědět, jak ho řešit.

Musíme se dotknout dvou základních obtíží:
- Private Endpoint vytváří /32 záznam v routovací tabulce, který pak má přednost před méně specifickými záznamy. Pokud máte Private Endpoint ve stejném VNETu (což je nejčastější), tak to znamená při každém vytvoření PE udělat specifický záznam v UDR. To je trochu nepraktické a navíc UDR má limit 400 záznamů.
  - První řešení je vytvořit automatizaci, která to zajistí
  - Druhé řešení je oddělit PE do jiného VNETu, dedikovaného spoke, takže jeho /32 routy se nezpropagují do ostatních spoke
  - Třetí řešení je v preview, kdy tyto /32 záznamy nemají přednost před záznamy třeba na úrovni celého subnetu, např. /24
- Private Endpoint pro návratový provoz neumí ctít custom routovací tabulku UDR
  - Aktuálně jediné řešení je zajistit SNAT na inspekčním zařízení, čímž se zajistí, že i návratový provoz jde přes firewall/NVA
  - Žádné public preview, které by chování měnilo, v době psaní článku k dispozici není (ale pracuje se na tom)

Vyzkoušejme. Celý skript je [tady](https://gist.githubusercontent.com/tkubica12/da293a1d5d679032aac95232ef03bd83/raw/afe00f85bc9130ceaf1800c499395edee78c0048/privateEndpointInspection.sh)

Nejprve přípravné práce.

```bash
# Register preview feature
az feature register --namespace Microsoft.Network -n AllowPrivateEndpointNSG
az feature show --namespace Microsoft.Network -n AllowPrivateEndpointNSG  # Wait until Registered
az provider register -n Microsoft.Network

# Create resource group
az group create -n plink -l northeurope

# Create UDRs
az network route-table create -g plink -n source
az network route-table route create -g plink \
    --route-table-name source \
    -n plinkSubnetViaNva \
    --next-hop-type VirtualAppliance \
    --address-prefix 10.0.1.0/24 \
    --next-hop-ip-address 10.0.2.4
az network route-table create -g plink -n plink
az network route-table route create -g plink \
    --route-table-name plink \
    -n sourceViaNva \
    --next-hop-type VirtualAppliance \
    --address-prefix 10.0.0.0/24 \
    --next-hop-ip-address 10.0.2.4

# Create VNET
az network vnet create -g plink -n plink --address-prefix 10.0.0.0/16
az network vnet subnet create -g plink --vnet-name plink -n vm --address-prefixes 10.0.0.0/24 --route-table source
az network vnet subnet create -g plink --vnet-name plink -n plink --address-prefixes 10.0.1.0/24 --disable-private-endpoint-network-policies true --route-table plink
az network vnet subnet create -g plink --vnet-name plink -n nva --address-prefixes 10.0.2.0/24

# Create diagnostic storage account (for serial console access)
az storage account create -n tomasplinkstore77534 -g plink --sku Standard_LRS

# Create target storage account (for private endpoint test) and upload file
az storage account create -n tomastarget7754235 -g plink --sku Standard_LRS
az storage container create -n test --public-access blob --account-name tomastarget7754235
echo "This is my test content" > data.txt
az storage blob upload --account-name tomastarget7754235 --container-name test --file data.txt -n data.txt
rm data.txt

# Create source VM
az vm create -n sourcevm \
    -g plink \
    --image UbuntuLTS \
    --size Standard_B1s \
    --authentication-type password \
    --boot-diagnostics-storage tomasplinkstore77534 \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --nsg "" \
    --public-ip-address "" \
    --vnet-name plink \
    --subnet vm \
    --no-wait

# Create NVA
az vm create -n nva \
    -g plink \
    --image UbuntuLTS \
    --size Standard_B1s \
    --authentication-type password \
    --boot-diagnostics-storage tomasplinkstore77534 \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --nsg "" \
    --public-ip-address "" \
    --vnet-name plink \
    --subnet nva \
    --no-wait

# Create private endpoint and DNS zone
az network private-endpoint create \
    -n plink \
    -g plink \
    --vnet-name plink \
    --subnet plink \
    --private-connection-resource-id $(az storage account show -n tomastarget7754235 -g plink --query id -o tsv) \
    --group-id blob \
    --connection-name plinkconnection  

az network private-dns zone create -n privatelink.blob.core.windows.net -g plink

az network private-dns link vnet create \
    -g plink \
    --zone-name privatelink.blob.core.windows.net \
    --name dnslink \
    --virtual-network plink \
    --registration-enabled false

az network private-endpoint dns-zone-group create \
   -g plink \
   --endpoint-name plink \
   --name group \
   --private-dns-zone privatelink.blob.core.windows.net \
   --zone-name privatelink.blob.core.windows.net
```

Připojím se do zdrojové VM, abych mohl zkoušet provoz a taky do NVA, ve kterém nastavím routování. Žádné pakety ale nevídím, traffic nepřichází.

```bash
# Connect to source VM, configure routing and test connection
az serial-console connect -n sourcevm -g plink
curl https://tomastarget7754235.blob.core.windows.net/test/data.txt 

# Connect to NVA, configure routing and check whether traffic flows to NVA
az serial-console connect -n nva -g plink
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -p
sudo tcpdump port 443 -n  # No traffic visible!
```

Důvodem je první problém, který jsem zmiňoval - /32 záznam má přednost, takže to jde ze zdroje napřímo.

```bash
# Reason is private endpoint installed /32 route that takes precedence
# List effective routes on source VM
az network nic show-effective-route-table -n sourcevmVMNic -g plink -o table
: '
Source    State    Address Prefix    Next Hop Type      Next Hop IP
--------  -------  ----------------  -----------------  -------------
...
User      Active   10.0.1.0/24       VirtualAppliance   10.0.2.4
Default   Active   10.0.1.4/32       InterfaceEndpoint
'
```

První varianta řešení je přidat specifické /32 do UDR.

```bash
# Solution 1 (GA) - add specific /32 route to UDR
az network route-table route create -g plink \
    --route-table-name source \
    -n specificEndpoint \
    --next-hop-type VirtualAppliance \
    --address-prefix 10.0.1.4/32 \
    --next-hop-ip-address 10.0.2.4

az network nic show-effective-route-table -n sourcevmVMNic -g plink -o table
: '
Source    State    Address Prefix    Next Hop Type      Next Hop IP
--------  -------  ----------------  -----------------  -------------
...
User      Active   10.0.1.0/24       VirtualAppliance   10.0.2.4
User      Active   10.0.1.4/32       VirtualAppliance   10.0.2.4
Default   Invalid  10.0.1.4/32       InterfaceEndpoint
'
```

Druhá možnost je v preview zapnout network poliky, což změní chování v tabulce.

```bash
# Solution 2 (preview) - enable network policies on plink subnet allows for whole subnet route (/24 in my case) to override all /32s
# This is important in large environments as UDRs are limited to 400 routes and also operational overhead with adding /32s is significant
az network vnet subnet update -g plink --vnet-name plink -n plink --disable-private-endpoint-network-policies false

az network nic show-effective-route-table -n sourcevmVMNic -g plink -o table
: '
Source    State    Address Prefix    Next Hop Type      Next Hop IP
--------  -------  ----------------  -----------------  -------------
...
User      Active   10.0.1.0/24       VirtualAppliance   10.0.2.4
Default   Invalid  10.0.1.4/32       InterfaceEndpoint
'
```

Tím jsme zajistili, že pakety dorazily do NVA. Jenže komunikace stále nefunguje.

```bash
# Connect to NVA and check whether traffic flows to NVA
az serial-console connect -n nva -g plink
sudo tcpdump port 443 -n  # Incomming packets are visible, but no returning traffic - orivate endpoint does not currently support UDRs!
```

Důvodem je, že Private Endpoint při návratové komunikaci neumí využít UDR, které jsme na plink subnet dali. Aktuálně podpora takového chování není ani v public preview. Řešením je na NVA provádět SNAT, takže zdrojová IP se změní na IP NVA, takže PE nepotřebuje žádné změny v routingu a všechno funguje.

```bash
# In order for returning traffic to flow via NVA we need to do SNAT on NVA
# UDRs on private endpoints are currently not supported (even no public preview available)
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/8 -d 10.0.1.4/32 -o eth0 -j MASQUERADE
sudo tcpdump port 443 -n
```

V případě Azure Firewall dosáhnete tohoto výsledku například použitím aplikačních pravidel, protože ty jsou transparentní proxy (Azure Firewall vystupuje vůči PE jako klient). To je možné pro všechny HTTPS protokoly a MS SQL. Pro jiné protokoly, například AMQP v Service Bus nebo MySQL ve standard server, můžete použít SNAT ve vnitřních adresách, což Azure Firewall taky podporuje (nastavíte subnety private linku pro private SNAT funkci firewallu).


Používejte Private Endpointy, dává mi to obrovský smysl. To samo o sobě by pro většinu z nás mělo stačit v kombinaci s pokročilým ověřováním přes AAD či Managed Identity. Pokud chcete jít ještě dál, další krok by mohla být mikrosegmentace s použitím NSG. Vyzkoušeli jsme si dnes preview, které tohle umožňuje i na vstupu, což je určitě pohodlnější. Na druhou stranu stejnak pokud jedete třeba uvnitř AKS, tak tam budete mikrosegmentaci řešit třeba s network policy nebo service mesh a stejně pak pro vás bude výhodnější to dělat jako outbound pravidlo a tohle preview nepotřebujete. Pro tradiční workloady ale dává NSG na vstupu do PE určitě smysl, vyzkoušejte si. Inspekci provozu bych já standardně nedělal, ale pokud ji vyžadujete a jde o tradičnější workload, šel bych cestou dedikovaného spoke pro PE a použití SNAT nebo aplikačních pravidel. Uvnitř stejného VNETu musíte řešit /32 záznamy což není praktické, ale nové preview vám s tím pomůže. 