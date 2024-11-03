---
layout: post
status: publish
published: true
title: Vyhledávání vašich zdrojů s Azure Resource Graph
tags:
- Compute
---
Cloud umožňuje mít ve vašich zdrojích opravdu pořádek. Díky hierarchickým strukturám i horizontálnímu tagování libovolnými metadaty se sám o sobě může stát takovou jednoduchou CMDB. Co když máte hned několik subscription a potřebujete nějaké pokročilé vyhledávání přes celý váš cloud? Podívejme se na Azure Resource Graph.

Přímo v portálu je vylepšená záložka All resources, která umí poměrně elegantně filtrovat. Někdy ale potřebujete ještě zajímavější dotazy a možná dokonce nějakým programovatelným způsobem - Azure CLI, PowerShell nebo API volání. Azure nabízí dotazovací jazyk Kusto, který můžete znát z produktů jako je Azure Monitor Log Analytics, Application Insights nebo nově i jako samostatné databázové řešení Azure Data Explorer. Stejný engine je k dispozici pro vyhledávání v databázi vašich nasazených zdrojů v Azure.

Na webu je několik příkladů a nad nimi jsem si zkusil postavit něco dalšího. Tak například pokud potřebujete vyexportovat všechny zdroje co máte nasazené do tabulky, json nebo yaml, můžete zavolat tohle:

```bash
az graph query -q "" -o json > file
```

Je možné, že v době kdy článek čtete, není ještě příkaz graph nativní součástí Azure CLI. Můžete si ho ale nainstalovat jako extension:

```bash
az extension add -n resource-graph
```

Syntaxe dotazovacího jazyka dovoluje například filtraci, řazení nebo sumarizaci. Toho využiji třeba pro dotaz jaké typy strojů a v jakých počtech mám v Azure nasazené přes všechny subscription, kam mám přístup.

```bash
az graph query -o table -q \
    "where type =~ 'Microsoft.Compute/virtualMachines' 
    | summarize pocet=count() by velikost=tostring(properties.hardwareProfile.vmSize)
    | order by pocet"

Pocet    Velikost
-------  ----------------
31       Standard_DS1_v2
10       Standard_A1
9        Standard_A2
7        Standard_DS2_v2
7        Standard_B2s
...
```

Dále mne zajímalo, jaké standardní image mám nasazené, v jaké verzi a jakých počtech.

```bash
az graph query -o table -q \
    "where type =~ 'Microsoft.Compute/virtualMachines' 
    | summarize pocet=count() by sku=tostring(properties.storageProfile.imageReference.sku), 
        offer=tostring(properties.storageProfile.imageReference.offer)
    | order by pocet"

Offer                         Pocet    Sku
----------------------------  -------  -------------------------------------
WindowsServer                 31       2016-Datacenter
UbuntuServer                  19       16.04-LTS
UbuntuServer                  9        14.04.5-LTS
WindowsServer                 9        2012-R2-Datacenter
SQL2017-WS2016                3        Enterprise
UbuntuServer                  3        18.04-LTS
ubuntuserver                  2        16.04-LTS
RHEL                          2        6.8
RHEL                          2        7.3
...
```

A co si třeba spočítat celkovou velikost všech managed disků za jednotlivé subskripce?

```bash
az graph query -o table -q \
    "where type =~ 'Microsoft.Compute/disks'
    | summarize celkem=sum(toint(properties.diskSizeGB)) by subscriptionId
    " 

Celkem    SubscriptionId
--------  ------------------------------------
787       cenzura-1234-1234-1234-000000000001
2736      cenzura-1234-1234-1234-000000000002
15768     cenzura-1234-1234-1234-000000000003</pre>
<p>Nebo vypsat všechny managed disky, které nejsou připojeny k běžícímu nebo vypnutému stroji? Použiji funkci project, kterou si vyberu jen jeden sloupeček.</p>
<pre class="EnlighterJSRAW" data-enlighter-language="null">az graph query -o table -q \
    "where type =~ 'Microsoft.Compute/disks' and managedBy =~ ''
    | project name
    "
```

Další užitečné příklady jsou tady: [https://docs.microsoft.com/en-us/azure/governance/resource-graph/samples/starter](https://docs.microsoft.com/en-us/azure/governance/resource-graph/samples/starter)

Azure Resource Graph je zajímavý vyhledávací jazyk, kterým můžete procházet svoje zdroje v Azure. Hledat je podle tagů, vlastností, počítat, agregovat. To se může někdy docela hodit.
