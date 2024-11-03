---
layout: post
title: 'Kubernetes prakticky: privátní AKS clustery'
tags:
- Kubernetes
- Networking
- Security
---
Za nejdůležitější bezpečnostní nastavení z pohledu přístupu administrátorů do vašeho AKS clusteru považuji určitě integraci na Azure Active Directory a s tím spojené silné přihlašování včetně možnosti více-faktoru, podmíněných přístupů a návazný RBAC. O tom jindy. Nicméně omezení vašeho clusteru po stránce síťové jako další stupeň bezpečnosti mi dává smysl a to ze tří důvodů:
- Zabetonování management přístupu jen do privátní sítě mě může zachránit v případech, kdy mám nevhodné zabezpečení přístupů (např. používám admin certifikát bez AAD integrace, uložím si ho ke svému repozitáři a omylem to šoupnu na veřejný GitHub)
- Vynucený routing do bezpečnostního prvku znemožní aplikačníkům omylem vystavit něco přímo do Internetu (možná si nasadí balancer s public IP, ale ta nebude fungovat)
- Důsledné řízení odchozího provozu znemožní nakaženému kódu vyvádět data ven, volat si pro instrukce nebo vytvořit reverse shell, přistupovat na public služby aniž by se o tom někdo dozvěděl

Jsou tu ale samozřejmě i nevýhody:
- Pokud s clusterem pracujete, potřebujete to dělat zevnitř - například přes VPN, nebo bastion/jump server, což nemusí být vždy praktické
- Deployment agent/server pro automatizaci musí být taky vevnitř, takže cloudové hosted CI/CD nody se nedobouchají a musíte použít svého agenta uvnitř sítě
- Každé zavolání externího public API (Google Maps, předpověď počasí, OpenData) musí být nakonfigurováno, což může zdržovat

Nevýhody dělají z vývojového prostředí peklo, ale výhody činí produkci bezpečnou a podle toho bych se řídil - do produkce privátně, do devu otevřeněji (připomínám - kvalitní identita jako je AAD je důležitější, než private vs. public interface, takže public endpoint nutně neznamená nezabezpečený endpoint).

# AKS Private Cluster - jak dnes funguje (a jak řeší některé nevýhody předchozí verze)
Řídící nody pro vás AKS nabízí jako službu a dodává vám je zdarma, což je skvělé. Na rozdíl od agent nodů (to kde běží vaše aplikace) tak ale nejsou uvnitř vašeho VNETu. Tím, že agent nody tam ale jsou, tak váš kód je pěkně na privátní síti a máte všechno hezky pod kontrolou. Jenže agent a řídící vrstva spolu musí mluvit a stejně tak vy, abyste mohli spravovat Kubernetes (třeba nasadit aplikaci).

## Problém 1 - řídící node občas potřebuje šťouchnout do agenta, něco mu poslat
Tohle by znamenalo, že by řídící node (PaaS běžící "v Internetu") musel mít otevřený port do vašich agent nodů a to se lidem nelíbí. AKS tým to vyřešil elegantně a celé to otočil. Agent node volá domů, vytváří tunel do řídícího node a ten drží nahoře. Tímto způsobem se dovnitř nic nemusí otvírat a stačí otevřít komunikaci směrem ven. Jsou to sice nestandardní porty (jeden je na TCP a druhý na UDP), což je ne vždy vítáno, ale obvykle to u bezpečáků projde. Ale nemusí být nadšeni (pak čtěte dál).

## Problém 2 - řídící vrstva je PaaS a je na public endpointu, ale vy to chcete dostat do VNETu
Tohle je vlastnost všech PaaS, které nabízejí nějaké služby pro vaše aplikace či uživatele - Azure SQL, Azure Blob Storage, Azure Service Bus a hromada dalších. Řešení tam znáte - Private Link a DNS integrace a stejný postup zvolilo AKS. Jenže je to o něco složitější, protože nejen vy přistupujete na Kubernetes API, ale dělají to i nody samotné, takže pokud se nedobouchají například proto, že vaše DNS řešení nebude vědět o private link záznamu, vytváření clusteru selže. To už dnes ale není problém (opět čtěte dále).

## Problém 3 - bezpečáci chtějí řídit veškerou outbound komunikaci
Pokud chcete plně řídit outbound a řídící nody by byly public FQDN, musíte tuto komunikaci na firewallu povolit. Jenže jaké FQDN váš cluster bude mít nevíte, dokud ho nevytvoříte a pokud ho ale rychle nenastavíte do vašeho firewallu, agent nody se nebouchají a nasazení clusteru selže. Mimo jiné proto je potřeba, aby řídící nody byly pro agenty dostupné vnitřkem přes private link, takže na firewallu se nemusí nic nastavovat.

## Problém 4 - sdílené privátní DNS může znamenat i batch proces nebo ruční práci
AKS privátní cluster dřív pro každou instanci vytvářel svou vlastní DNS zónu a napojil ji do VNETu, kde sedí AKS. Jenže to není dobré v okamžiku, kdy nepoužíváte přímo Azure DNS, ale ve své hub síti máte vlastní DNS server. Ten v tuto chvíli o nové zóně neví (před tím neexistovala a nešla vytvořit dopředu), takže dokud to nevyřešíte (například skriptem nebo politikou, což nějakou dobu trvá), agent se nebouchá řídícího nodu a nasazení clusteru může selhat. Proto dnes AKS private cluster funguje tak, že do agent nodů nastaví DNS natvrdo do hosts file, takže i kdyby se vaše DNS integrace z nějakých důvodů opožďovala, clusteru to nevadí a naběhne. Uživatelé samozřejmě integraci DNS potřebují, ale agent nody ne (a potenciálně i uživatelé mohou používat hosts file, ale DNS integrace je určitě lepší nápad). Druhá příjemná novinka (ta je zatím v preview) je možnost dát AKS clusteru sdílenou Azure Private DNS zónu, takže si nevytváří náhodně novou. To umožňuje dopředu zařídit potřebné integrace (např. nalinkovat tuto Azure DNS na síť s vašim DNS serverem).

## Shrnuto jak to funguje
Výsledkem je dnes velmi funkční enterprise grade řešení, které uspokojí i tradičně stavěné bezpečnostní požadavky. Řídící nody jsou za private linkem a mají tedy adresu ve VNETu, kterou používá jak agent node tak vaši Kubernetes uživatelé. Agent nody mají DNS s IP zadrátované, takže nepotřebují funkční DNS na private link na to, aby se cluster úspěšně nasadil. Pro Kubernetes uživatele samozřejmě výrazně doporučuji jít cestou DNS integrace, což je dnes podstatně jednodušší díky možnosti vytvořit jednu sdílenou zónu a mít tak všechno propojené dopředu pro všechny i budoucí clustery.

# Vyzkoušejme prakticky
Nejprve si vytvořím privátní DNS zónu privatelink.westeurope.azmk8s.io (ta je pro AKS clustery ve West Europe).

```bash
az group create -n dns-zones-rg -l westeurope
az network private-dns zone create -g dns-zones-rg -n privatelink.westeurope.azmk8s.io
```

Vytvořím si VNET s pár subnety a DNS zónu do něj nalinkuji.

```bash
az group create -n networking-rg -l westeurope
az network vnet create -n my-net -g networking-rg --address-prefix 10.1.0.0/16
az network vnet subnet create --vnet-name my-net -g networking-rg -n aks-subnet --address-prefixes 10.1.0.0/24
az network vnet subnet create --vnet-name my-net -g networking-rg -n vm-subnet --address-prefixes 10.1.1.0/24
az network vnet subnet create --vnet-name my-net -g networking-rg -n AzureFirewallSubnet --address-prefixes 10.1.2.0/24
az network private-dns link vnet create -n aks-zone-link \
    -g dns-zones-rg \
    -z privatelink.westeurope.azmk8s.io \
    -e false \
    -v $(az network vnet show -n my-net -g networking-rg --query id -o tsv)
```

Vytvořím Azure Firewall a určím, že subnet aks-subnet bude veškerý outbound směrovat přes něj.

```bash
az extension add --name azure-firewall
az network firewall create -n fw -g networking-rg
az network public-ip create -n fw-ip -g networking-rg --allocation-method static --sku standard
az network firewall ip-config create -n fw-config \
    -g networking-rg \
    --firewall-name fw \
    --public-ip-address fw-ip \
    --vnet-name my-net
az network firewall update- n fw -g networking-rg

az network route-table create -n allToFw -g networking-rg --disable-bgp-route-propagation true
az network route-table route create -n default \
    -g networking-rg \
    --route-table-name allToFw \
    --address-prefix 0.0.0.0/0 \
    --next-hop-type VirtualAppliance \
    --next-hop-ip-address $(az network firewall ip-config show -g networking-rg -n fw-config --firewall-name fw --query privateIpAddress -o tsv)
az network vnet subnet update -n aks-subnet --vnet-name my-net -g networking-rg --route-table allToFw
```

Podle dokumentace teď nastavím outbound pravidla. Všimněte si všechno jsou http-based protokoly. Pro zjednodušení je v Azure Firewall k dispozici FQDN tag pro AKS, ale já zvolil výčet pro případ, že máte jiný firewall. Udělal jsem tři skupiny záznamů. Jednu pro AKS samotné, druhou pro aktualizace OS (pokud nepovolíte, nody nebudou stahovat update, ale při každém i minor upgradu AKS dostáváte čerstvé nody, které mají poslední aktualizace) a třetí pro Azure Monitor.

```bash
## AKS dependencies (service packages etc.)
az network firewall network-rule create -g $RG -f $FWNAME --collection-name 'aksfwnr' -n 'time' --protocols 'UDP' --source-addresses '*' --destination-fqdns 'ntp.ubuntu.com' --destination-ports 123

az network firewall application-rule create --target-fqdns mcr.microsoft.com \
   --collection-name AKS \
   --firewall-name fw \
   --name MicrosoftContainerRegistry  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24 \
   --priority 200 \
   --action Allow
az network firewall application-rule create --target-fqdns '*.data.mcr.microsoft.com' \
   --collection-name AKS \
   --firewall-name fw \
   --name MicrosoftContainerRegistryCDN  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24
az network firewall application-rule create --target-fqdns management.azure.com \
   --collection-name AKS \
   --firewall-name fw \
   --name AzureResourceManager  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24
az network firewall application-rule create --target-fqdns login.microsoftonline.com \
   --collection-name AKS \
   --firewall-name fw \
   --name AzureActiveDirectory  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24
az network firewall application-rule create --target-fqdns packages.microsoft.com \
   --collection-name AKS \
   --firewall-name fw \
   --name Packages  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24
az network firewall application-rule create --target-fqdns acs-mirror.azureedge.net \
   --collection-name AKS \
   --firewall-name fw \
   --name ComponentsCDN  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24

## OS updates
az network firewall application-rule create --target-fqdns security.ubuntu.com \
   --collection-name UbuntuUpdates \
   --firewall-name fw \
   --name Security  \
   --protocols Http=80 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24 \
   --priority 210 \
   --action Allow
az network firewall application-rule create --target-fqdns azure.archive.ubuntu.com \
   --collection-name UbuntuUpdates \
   --firewall-name fw \
   --name Repo  \
   --protocols Http=80 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24
az network firewall application-rule create --target-fqdns changelogs.ubuntu.com \
   --collection-name UbuntuUpdates \
   --firewall-name fw \
   --name Changelog  \
   --protocols Http=80 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24

## Azure Monitor for Containers
az network firewall application-rule create --target-fqdns dc.services.visualstudio.com \
   --collection-name AzureMonitor \
   --firewall-name fw \
   --name Telemetry  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24 \
   --priority 220 \
   --action Allow
az network firewall application-rule create --target-fqdns '*.ods.opinsights.azure.com' \
   --collection-name AzureMonitor \
   --firewall-name fw \
   --name Ingestion  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24
az network firewall application-rule create --target-fqdns '*.oms.opinsights.azure.com' \
   --collection-name AzureMonitor \
   --firewall-name fw \
   --name Authentication  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24
az network firewall application-rule create --target-fqdns '*.monitoring.azure.com' \
   --collection-name AzureMonitor \
   --firewall-name fw \
   --name Metrics  \
   --protocols Https=443 \
   -g networking-rg \
   --source-addresses 10.1.0.0/24
```

Vytvořím si teď AKS. Protože funkce vlastní privátní zóny je v preview, musíme si nainstalovat Azure CLI extension. Také nutno zmínit, že aktuálně tato varianta nepodporuje System Managed Identitu, tak použiji Service Principal (myslím, že v budoucnu bude fungovat minimálně i User Managed Identita).

```bash
# Install AKS preview extension to Azure CLI
az extension add --name aks-preview

# Create AKS private cluster
az group create -n aks-rg -l westeurope
az aks create -n myaks \
    -g aks-rg \
    -x \
    -c 1 \
    --service-principal $ARM_CLIENT_ID \
    --client-secret $ARM_CLIENT_SECRET \
    --network-plugin azure \
    --enable-private-cluster \
    --private-dns-zone $(az network private-dns zone show -g dns-zones-rg -n privatelink.westeurope.azmk8s.io --query id -o tsv) \
    --vnet-subnet-id $(az network vnet subnet show --vnet-name my-net -g networking-rg -n vm-subnet --query id -o tsv)
```

Výborně, cluster se rozjel Vytvořím si testovací VM ve VNETu, připojím se a vyzkouším. Podívám se na DNS odpověď, že se mi vrací privátní IP a pak se připojím přes kubectl do clusteru.

```bash
# Create testing VM
az group create -n vm-rg -l westeurope
az vm create -n myvm \
    -g vm-rg \
    --image UbuntuLTS \
    --size Standard_B1ms \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --public-ip-address myvm-ip \
    --public-ip-address-dns-name tomas-privateaks-test \
    --subnet $(az network vnet subnet show --vnet-name my-net -g networking-rg -n vm-subnet --query id -o tsv)

# Test private cluster
ssh tomas@$(az network public-ip show -n myvm-ip -g vm-rg --query ipAddress -o tsv)

## Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

## Login to Azure
az login
az account set -s mySubscription

## Test DNS
dig $(az aks show -n myaks -g aks-rg --query privateFqdn -o tsv) # Should return private IP
...
;; ANSWER SECTION:
myaks-aks-rg-a0f4a7-eb580bbf.privatelink.westeurope.azmk8s.io. 300 IN A 10.1.1.4
...

## Connect to Kubernetes
sudo az aks install-cli
az aks get-credentials -n myaks -g aks-rg --admin
kubectl get nodes
```

Všechno funguje, vyzkoušejte si. Nakonec zase všechno smažu.

```bash
# Destroy
az group delete -n dns-zones-rg -y --no-wait
az group delete -n networking-rg -y --no-wait
az group delete -n aks-rg -y --no-wait
az group delete -n vm-rg -y --no-wait
```


Nezapomeňte ve svém AKS clusteru používat AAD ověřování, správný RBAC a ideálně i Azure Policy. Pokud potřebujete například u produkčních clusterů zabetonovat networking, dnes jsme vyzkoušeli jak na to.