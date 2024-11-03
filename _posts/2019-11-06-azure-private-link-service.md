---
layout: post
title: Privátní napojení vaší vlastní služby v SaaS stylu s Azure Private Link Service
tags:
- Security
- Networking
---
Před časem jsem popisoval a testoval službu Private Link, která vás může přímo z vašeho VNETu napojit do platformní služby v Azure. Zkoušel jsem Storage account a Azure SQL, ale chystá se i plejáda dalších služeb. Víte ale, že celá technologie není určena jen pro Azure PaaS, ale můžete ji použít i pro svoje vlastní služby, například pokud chcete nabídnout nějaké své řešení jako SaaS ostatním?

# Private Link Service a Private Endpoint
Private Endpoint vám umožňuje nasadit jakousi virtuální "proxy" přímo ve vašem VNETu. Vypadá to jako virtuální síťová karta, která má platnou adresu VNETu (dostupnou třeba i přes vaše VPN spojení či Express Route) a tunelem na Azure backbone vás doveze přímo k platformní službě.

Jak ale platformní služba dokáže takový tunel bezpečně rozpoznat a rozbalit? To bude asi tajemství kuchaře, že? Kdepak - něco takového si můžete zařídit i sami pro svou vlastní službu. Jmenuje se to Private Link Service a dnes si to vyzkoušíme.

Jaký je tedy jeden ze scénářů použití? Dejme tomu, že provozujete zajímavou aplikaci ve formě API, například machine learning model schopný identifikovat podezřelé nebo chybné faktury (nechcete se přece dostat do daňových potíží tím, že dokument je zfalšovaný nebo mu chybí nějaké náležitosti). Vaši zákazníci jsou v Azure a chtějí vaši službu, ale bezpečákům se nelíbí, že komunikujete přes "Internet". A už s vámi řeší nějaké VPN tunely a podobné složitosti, které jsou drahé a trvá dost dlouho, než se něco takového rozchodí. Co kdyby bylo možné se k vaší službě v Azure připojit přes Private Link? Jednoduše, rychle a bez složitých diskusí?

Možná vás ale stejný scénář osloví i v rámci firmy - třeba jste automobilka s relitivně nezávislými značkami a chcete v rámci skupiny nabídnout nějakou sdílenou službu, ale propojit všechno síťově je obtížné vzhledem k značné autonomii každé značky.

# Nastavíme stranu poskytovatele služby
Vyzkoušejme si stranu poskytovatele služby. Vytvoříme si resource group, VNET, v něm VM a v tom nainstaluji NGINX (to bude představovat naše "API").

```bash
az group create -n provider -l westcentralus
az network vnet create -g provider \
    -n providerNet \
    --address-prefix 10.0.0.0/16
az network vnet subnet create -g provider \
    --vnet-name providerNet \
    -n vmSubnet \
    --address-prefixes 10.0.0.0/24
az network nic create -n vmNic \
    -g provider \
    --vnet-name providerNet \
    --subnet vmSubnet
az vm create -n vm \
    -g provider \
    --image UbuntuLTS \
    --size Standard_B1s \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --nics vmNic
az vm run-command invoke -g provider \
    -n vm \
    --command-id RunShellScript \
    --scripts "sudo apt-get update && sudo apt-get install -y nginx"
```

Private Link se zakončuje na Azure LB Standard. Musíme jej tedy vytvořit a dát před naši službu - použiji interní LB, takže žádné public adresy se nekonají.

```bash
az network lb create -g provider \
    -n providerILB \
    --sku standard \
    --vnet-name providerNet \
    --subnet vmSubnet \
    --frontend-ip-name frontIp \
    --backend-pool-name backendPool
az network lb probe create -g provider \
    --lb-name providerILB \
    --name healthProbe \
    --protocol tcp \
    --port 80
az network lb rule create -g provider \
    --lb-name providerILB \
    --name httpRule \
    --protocol tcp \
    --frontend-port 80 \
    --backend-port 80 \
    --frontend-ip-name frontIp \
    --backend-pool-name backendPool \
    --probe-name healthProbe
az network nic ip-config update -n ipconfig1 \
    --nic-name vmNic \
    -g provider \
    --lb-name providerILB \
    --lb-address-pools backendPool
```

Výborně - teď stačí vytvořit Private Link Service. Resp. před tím musíme v subnetu zakázat network politiky, které v době psaní článku nejsou podporované.

```bash
az network vnet subnet update -g provider \
    --vnet-name providerNet \
    -n vmSubnet \
    --disable-private-link-service-network-policies true

az network private-link-service create -g provider \
    -n providerService \
    --vnet-name providerNet \
    --subnet vmSubnet \
    --lb-name providerILB \
    --lb-frontend-ip-configs frontIp \
    --location westcentralus
```

Máme připraveno. Protože zákazník bude v úplně jiném tenantu a o naší subskripci vůbec nic neví, potřebujete mu sdělit identifikátor služby. Ten najdeme třeba v GUI.

![](/images/2019/2019-11-03-20-23-12.png){:class="img-fluid"}

# Připojení na službu z jiného tenantu
Přesuňme se teď nejen do jiné subskripce, ale dokonce i do jiného tenantu. Vytvořím síť, VM (s veřejnou adresou ať se do ní jednoduše připojím a můžu private link otestovat) a v subnetu zakážu network policy.

```bash
az group create -n consumer -l westcentralus
az network vnet create -g consumer \
    -n consumerNet \
    --address-prefix 10.99.0.0/16
az network vnet subnet create -g consumer \
    --vnet-name consumerNet \
    -n vmSubnet \
    --address-prefixes 10.99.0.0/24
az vm create -n vm \
    -g consumer \
    --image UbuntuLTS \
    --size Standard_B1s \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --vnet-name consumerNet \
    --subnet vmSubnet \
    --nsg ""
az network vnet subnet update -g consumer \
    --vnet-name consumerNet \
    -n vmSubnet \
    --disable-private-link-service-network-policies true
```

Pojďme teď použít GUI. Přidáme si nový Private Endpoint.

![](/images/2019/2019-11-03-20-26-35.png){:class="img-fluid"}

![](/images/2019/2019-11-03-20-27-43.png){:class="img-fluid"}

Protože služba je ve zcela jiném tenantu, kam nemám přístup, zvolím připojení na základě aliasu a žádosti.

![](/images/2019/2019-11-03-20-29-08.png){:class="img-fluid"}

Dokončím průvodce.

Přeskočme teď na stranu providera. Vidím tady novou žádost o sestavení Private Linku.

![](/images/2019/2019-11-03-20-34-29.png){:class="img-fluid"}

Schválím.

Teď se přípojím do VM na straně konzumenta a podívám se na virtuální síťovku Private Endpointu ve svém VNETu. Vyzkoušejme curl na API providera.

```
tomas@vm:~$ curl 10.99.0.5
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
...
```

Funguje! Právě jsme službu providera v jednom tenantu připojili do VNETu konzumenta v jiném tenantu. To se může hodit, ne?