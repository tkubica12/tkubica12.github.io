---
layout: post
title: Co se chystá ARM šablona udělat s vaším prostředím? Použijte what if.
tags:
- Automatizace
---
Pokročilí uživatelé Azure nasazují své prostředky deklarativním desired state způsobem. ARM je nativní řešení a z toho vyplývá řada zásadních výhod, ale klidně můžete použít i Terraform, nástroj třetí strany. Jednou z věcí, která mi na ARM dlouho chyběla bylo něco jako terraform plan, tedy jakési spuštění nanečisto. Co ARM udělá, když ho spustím? Co přidá, co smaže, co bude modifikovat a jak? Rád bych to věděl ještě před tím, než to opravdu udělá.

Dnes se tedy podíváme na novou funkci what if, která je aktuálně v preview. K tomu použijeme Azure CLI (ale můžete udělat i přes Powershell) a konkrétně nových příkazů az deployment group nebo az deployment sub (dřívější verze byla az group deployment vs. az deployment - nové řešení je konzistentnější a je z toho jasné, co je resource group scope a co subscription scope).

Mějme tedy následující šablonu:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "variables": {
        "location": "[resourceGroup().location]"
    },
    "resources": [
        {
            "type": "Microsoft.Network/virtualNetworks",
            "name": "mujnet",
            "comments": "Zalozeni virtualni site a subnetu",
            "apiVersion": "2017-06-01",
            "location": "[variables('location')]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "10.0.0.0/16"
                    ]
                },
                "subnets": [
                    {
                        "name": "sub1",
                        "properties": {
                            "addressPrefix": "10.0.0.0/24"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Network/networkInterfaces",
            "name": "nic1",
            "comments": "Zalozeni sitove karty",
            "apiVersion": "2017-06-01",
            "location": "[variables('location')]",
            "dependsOn": [
                "mujnet"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "subnet": {
                                "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', 'mujnet', 'sub1')]"
                            },
                            "privateIPAllocationMethod": "Static",
                            "privateIPAddress": "10.0.0.4",
                            "privateIPAddressVersion": "IPv4",
                            "primary": true
                        }
                    }
                ]
            }
        }
    ],
    "outputs": {}
}
```

Vytvořím resource group a zeptám se, co ARM plánuje udělat, když bych šablonu spustil.

```bash
az group create -n arm-test-rg -l westeurope
az deployment group what-if -g arm-test-rg --template-file whatif.json

Note: As What-If is currently in preview, the result may contain false positive predictions (noise).
You can help us improve the accuracy of the result by opening an issue here: https://aka.ms/WhatIfIssues.

Resource and property changes are indicated with this symbol:
  + Create

The deployment will update the following scope:

Scope: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg

  + Microsoft.Network/networkInterfaces/nic1 [2017-06-01]

      apiVersion:  "2017-06-01"
      id:          "/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg/providers/Microsoft.Network/networkInterfaces/nic1"
      location:    "westeurope"
      name:        "nic1"
      properties.ipConfigurations: [
        0:

          name:                                 "ipconfig1"
          properties.primary:                   true
          properties.privateIPAddress:          "10.0.0.4"
          properties.privateIPAddressVersion:   "IPv4"
          properties.privateIPAllocationMethod: "Static"
          properties.subnet.id:                 "/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg/providers/Microsoft.Network/virtualNetworks/mujnet/subnets/sub1"

      ]
      type:        "Microsoft.Network/networkInterfaces"

  + Microsoft.Network/virtualNetworks/mujnet [2017-06-01]

      apiVersion:               "2017-06-01"
      id:                       "/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg/providers/Microsoft.Network/virtualNetworks/mujnet"
      location:                 "westeurope"
      name:                     "mujnet"
      properties.addressSpace.addressPrefixes: [
        0: "10.0.0.0/16"
      ]
      properties.subnets: [
        0:

          name:                     "sub1"
          properties.addressPrefix: "10.0.0.0/24"

      ]
      type:                     "Microsoft.Network/virtualNetworks"

Resource changes: 2 to create.
```

Jasně. Zatím v resource group nic není, takže tohle je to, co ARM bude přidávat. Možná je to příliš detailu a stačí vám vědět, které zdroje se přidají, odeberou nebo změní.

```bash
az deployment group what-if -g arm-test-rg --template-file whatif.json -r ResourceIdOnly

Argument '--result-format' is in preview. It may be changed/removed in a future release.
This command is in preview. It may be changed/removed in a future release.
Note: As What-If is currently in preview, the result may contain false positive predictions (noise).
You can help us improve the accuracy of the result by opening an issue here: https://aka.ms/WhatIfIssues.

Resource and property changes are indicated with this symbol:
  + Create

The deployment will update the following scope:

Scope: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg

  + Microsoft.Network/networkInterfaces/nic1
  + Microsoft.Network/virtualNetworks/mujnet

Resource changes: 2 to create.
```

Pojďme tedy šablonu spustit a následně ještě mimo vlastní šablonu přidáme další zdroj do resource group navíc (k tomu proč se dostaneme).

```bash
az deployment group create -g arm-test-rg --template-file whatif.json
az network nic create -g arm-test-rg --vnet-name mujnet --subnet sub1 -n nic2
```

Výborně. Co nám řekne what-if funkce teď?

```bash
az deployment group what-if -g arm-test-rg --template-file whatif.json

Note: As What-If is currently in preview, the result may contain false positive predictions (noise).
You can help us improve the accuracy of the result by opening an issue here: https://aka.ms/WhatIfIssues.

Resource and property changes are indicated with these symbols:
  * Ignore
  = Nochange

The deployment will update the following scope:

Scope: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg

  * Microsoft.Network/networkInterfaces/nic2
  = Microsoft.Network/networkInterfaces/nic1 [2017-06-01]
  = Microsoft.Network/virtualNetworks/mujnet [2017-06-01]

Resource changes: 1 to ignore, 2 no change.
```

Ve zdrojích vnetu a nic1 není potřeba dělat žádné změny. V rámci preview ale občas narazíte na to, že vám what-if bude říkat, že nějaká políčka přidá. Do plné dostupnosti na tom tým prý bude intenzivně pracovat, není to totiž jednoduchá úloha. Tak například pokud uděláte NIC s IP adresou typu Dynamic, po jejím nasazení Azure adresu zvolí a ta bude vidět ve vráceném JSON z Azure. Jenže v půdovní šabloně logicky není a v rámci preview se to milně tváří jako změna. Vyčistit tyhle situace není zas tak jednoduché, protože v případě přiřazení typu Static takové políčko v šbloně mít musíte. Takže jsou to všechny nepovinné hodnoty (nemusíte je uvádět, vezme se default) nebo runtime hodnoty, které zatím mohou ukazovat změny, které ve skutečnosti změny nejsou. Ale to určitě vychytají.

Druhá položka je zajímavá, označená hvězdičkou a týká se nic2, kterou jsme přidali mimo tělo šablony. ARM říká, že ji bude ignorovat. To sedí, protože výchozí režim nasazování šablon je Incremental, tedy šablony modifikuje, přidává, ale pokud je v resource group něco, co šablona neobsahuje, neublíží tomu. Je to bezpečné pro začátečníky, na druhou stranu není to učebnicový desired state. Nicméně Terraform je taky inkrementální (tam je to spíše tím, že nečte nativní state v Azure, drží si jen svůj, takže o tom vlastně neví). Pokud ARM přepneme do plně desired state formy, kdy co není v šabloně nebude ani v realitě naší resource group, zdroj nic2 bude na odmazání.

```bash
az deployment group what-if -g arm-test-rg --template-file whatif.json --mode Complete

Note: As What-If is currently in preview, the result may contain false positive predictions (noise).
You can help us improve the accuracy of the result by opening an issue here: https://aka.ms/WhatIfIssues.

Resource and property changes are indicated with these symbols:
  - Delete
  = Nochange

The deployment will update the following scope:

Scope: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg

  - Microsoft.Network/networkInterfaces/nic2

      id:       "/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg/providers/Microsoft.Network/networkInterfaces/nic2"      location: "westeurope"
      name:     "nic2"
      type:     "Microsoft.Network/networkInterfaces"

  = Microsoft.Network/networkInterfaces/nic1 [2017-06-01]
  = Microsoft.Network/virtualNetworks/mujnet [2017-06-01]

Resource changes: 1 to delete, 2 no change.
```

Šablonu teď upravíme. Změníme síť tak, že přidáme subnet a také vytvoříme nic3. JSON vypadá nějak takhle:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "variables": {
        "location": "[resourceGroup().location]"
    },
    "resources": [
        {
            "type": "Microsoft.Network/virtualNetworks",
            "name": "mujnet",
            "comments": "Zalozeni virtualni site a subnetu",
            "apiVersion": "2017-06-01",
            "location": "[variables('location')]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "10.0.0.0/16"
                    ]
                },
                "subnets": [
                    {
                        "name": "sub1",
                        "properties": {
                            "addressPrefix": "10.0.0.0/24"
                        }
                    },
                    {
                        "name": "sub2",
                        "properties": {
                            "addressPrefix": "10.0.1.0/24"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Network/networkInterfaces",
            "name": "nic1",
            "comments": "Zalozeni sitove karty",
            "apiVersion": "2017-06-01",
            "location": "[variables('location')]",
            "dependsOn": [
                "mujnet"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "subnet": {
                                "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', 'mujnet', 'sub1')]"
                            },
                            "privateIPAllocationMethod": "Static",
                            "privateIPAddress": "10.0.0.4",
                            "privateIPAddressVersion": "IPv4",
                            "primary": true
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Network/networkInterfaces",
            "name": "nic3",
            "comments": "Zalozeni sitove karty",
            "apiVersion": "2017-06-01",
            "location": "[variables('location')]",
            "dependsOn": [
                "mujnet"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "subnet": {
                                "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', 'mujnet', 'sub2')]"
                            },
                            "privateIPAllocationMethod": "Static",
                            "privateIPAddress": "10.0.1.4",
                            "privateIPAddressVersion": "IPv4",
                            "primary": true
                        }
                    }
                ]
            }
        }
    ],
    "outputs": {}
}
```

Pusťme si what if analýzu.

```bash
az deployment group what-if -g arm-test-rg --template-file whatif-v2.json

Note: As What-If is currently in preview, the result may contain false positive predictions (noise).
You can help us improve the accuracy of the result by opening an issue here: https://aka.ms/WhatIfIssues.

Resource and property changes are indicated with these symbols:
  + Create
  ~ Modify
  * Ignore
  = Nochange

The deployment will update the following scope:

Scope: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg

  + Microsoft.Network/networkInterfaces/nic3 [2017-06-01]

      apiVersion:  "2017-06-01"
      id:          "/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg/providers/Microsoft.Network/networkInterfaces/nic3"
      location:    "westeurope"
      name:        "nic3"
      properties.ipConfigurations: [
        0:

          name:                                 "ipconfig1"
          properties.primary:                   true
          properties.privateIPAddress:          "10.0.1.4"
          properties.privateIPAddressVersion:   "IPv4"
          properties.privateIPAllocationMethod: "Static"
          properties.subnet.id:                 "/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/arm-test-rg/providers/Microsoft.Network/virtualNetworks/mujnet/subnets/sub2"

      ]
      type:        "Microsoft.Network/networkInterfaces"

  ~ Microsoft.Network/virtualNetworks/mujnet [2017-06-01]
    ~ properties.subnets: [
      + 1:

          name:                     "sub2"
          properties.addressPrefix: "10.0.1.0/24"

      ]

  * Microsoft.Network/networkInterfaces/nic2
  = Microsoft.Network/networkInterfaces/nic1 [2017-06-01]

Resource changes: 1 to create, 1 to modify, 1 to ignore, 1 no change.
```

ARM má zásadní výhody díky tomu, že je nativní součástí Azure (o srovnání s Terraform si můžete přečíst na mém blogu) a velmi doporučuji všem Azure uživatelům se s ním seznámit. Jednou z jeho nevýhod byla právě absence "plan" režimu a nový what-if v preview tuto vlastnost konečně přináší. Má to zatím ještě nějaké mouchy, ale rozhodně je to funkce, na kterou jsem se moc těšil a používání ARM šablon hodně zjednoduší.