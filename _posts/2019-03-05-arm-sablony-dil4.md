---
layout: post
status: draft
published: true
title: ARM šablony (4) - smyčky a podmínky
tags:
- Automatizace
---
Ve vašich šablonách je často velmi vhodné použít smyčky. Například v parametrech stanovíte počet komponent (třeba velikost clusteru) a šablona nasadí cluster požadované velikosti (například 1 node na devu, 3 nody v testu a 5 nodů v produkci). Často využívám parametrů typu objekt, přes který chci v šabloně iterovat. Nechci zadávat parametr subnet1Name, subnet1Range, subnet2Name, subnet2Range atd. Raději bych na vstupu měl pružnější JSON a v něm pole objektů name/range a iteroval přes něj. A co když potřebujete mít šablonu univerzální a podle parametrů se rozhodnout, které zdroje nasadit a které ne? Podívejme se dnes jak na to.

V první řadě - nezapomeňte proč to děláme. ARM šablona popisuje infrastrukturní architekturu aplikace - komponenty, služby a jejich propojení. Hledáme konzistenci prostředí od dev přes test do produkce. Hledáme schopnost testovat změny infrastruktury v testu a konzistentně je překlápět do produkce. Z toho důvodu potřebujeme jednotnou (!) ARM šablonu, kde rozdíly mezi dev/test/prod prostředími jsou dané rozdíly ve vstupních parametrech.

# Základy loopování

Smyčky lze použít na úrovni zdrojů, properties nebo variables. Pozor - nelze smyčkovat ve vnořených zdrojích. Na druhou stranu ale můžete smyčkovat přes vnořené šablony, ale o tom jindy. 

## Počet

Následující šablona má na vstupu počet IP adres, které má vytvořit.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "name": {
            "type": "string",
            "metadata": {
                "description": "IP address name"
            }
        },
        "environment": {
            "type": "string",
            "defaultValue": "PROD",
            "allowedValues": [
                "PROD",
                "QA",
                "TEST",
                "DEV"
            ],
            "metadata": {
                "description": "Environment in which IP address will be used"
            }
        },
        "count": {
            "type": "int",
            "defaultValue": 1,
            "metadata": {
                "description": "Number of IP addresses"
            }
        }
    },
    "variables": {
        "location": "[resourceGroup().location]"
    },
    "resources": [
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "copy": {
                "name": "multipleIPs",
                "count": "[parameters('count')]"
            },
            "name": "[concat(parameters('name'),'-',parameters('environment'),'-',copyIndex(1))]",
            "apiVersion": "2016-03-30",
            "location": "[variables('location')]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        }
    ],
    "outputs": {}
}
```

V tělé resource je použito copy a v něm dvě základní informace. Jméno smyčky (to je důležité, pokud budeme potřebovat vyplnit dependsOn na celé smyčce) a počet iterací. Při vytváření jména public IP adresy ho montujeme (concat) z jména, prostředí a čísla iterace.

ARM v podstatě dělá to, že ze smyček vybuduje finální ARM šablonu. Občas je dobré ujistit se, že se to rozbalilo jak očekáváte (příkaz validate). Tím můžeme začít a pak už tam šablonu pošleme.

```bash
az group create -n arm-rg -l westeurope

az group deployment validate -g arm-rg --template-file loop1.json \
    --parameters name=mojeip \
    --parameters environment=PROD \
    --parameters count=3

az group deployment create -g arm-rg --template-file loop1.json --mode Complete \
    --parameters name=mojeip \
    --parameters environment=PROD \
    --parameters count=3
```

Výsledek je tady:

![](/images/2019/2019-03-01-06-13-38.png){:class="img-fluid"}

## Pole
Zadání čísla třeba pro velikost clusteru je perfektní, ale někdy bude spíš potřeba zakládat objekty rovnou s nějakým názvem, který uvedeme v parametru. Jinak řečeno na vstupu bychom měli pole názvů (pejsek, kočička, myška) a chceme vytvořit příslušný počet objektů s těmito jmény. Vyzkoušejme si to.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "names": {
            "type": "array",
            "metadata": {
                "description": "IP address name"
            }
        },
        "environment": {
            "type": "string",
            "defaultValue": "PROD",
            "allowedValues": [
                "PROD", "QA", "TEST", "DEV"
            ],
            "metadata": {
                "description": "Environment in which IP address will be used"
            }
        }
     },
    "variables": {
        "location": "[resourceGroup().location]"
     },
    "resources": 
    [
              {
                  "type": "Microsoft.Network/publicIPAddresses",
                  "copy": {
                      "name": "multipleIPs",
                      "count": "[length(parameters('names'))]"
                  },
                  "name": "[concat(parameters('names')[copyIndex()],'-',parameters('environment'))]",
                  "apiVersion": "2016-03-30",
                  "location": "[variables('location')]",
                  "properties": {
                      "publicIPAllocationMethod": "Dynamic"
                  }
              }
     ],
    "outputs": { }
  }
```

Tady mám soubor s parametry.

```json
{
    "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "names": {
            "value": [
                "firstIP",
                "secondIP",
                "thirdIP"
            ]
        },
        "environment": {
            "value": "TEST"
        }
    }
}
```

Pošleme to do Azure.

```bash
az group deployment create -g arm-rg --template-file loop2.json \
    --parameters @loop2.parameters.json --mode Complete
```

Tady je výsledek.

![](/images/2019/2019-03-01-06-23-27.png){:class="img-fluid"}

## Objekt

Často potřebuji komplexnější vstupní parametry a ideální je tak JSON struktura, typycky pole objektů. Například seznam virtuálek s názvem, velikostí a počtem disků. V mé ukázce jde o to, že chci předat seznam IP adres s jejich jménem. Šablona s příkladem je tady:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "ipsobject": {
            "type": "object",
            "metadata": {
                "description": "IP address object"
            }
        },
        "environment": {
            "type": "string",
            "defaultValue": "PROD",
            "allowedValues": [
                "PROD", "QA", "TEST", "DEV"
            ],
            "metadata": {
                "description": "Environment in which IP address will be used"
            }
        }
     },
    "variables": {
        "location": "[resourceGroup().location]"
     },
    "resources": 
    [
              {
                  "type": "Microsoft.Network/publicIPAddresses",
                  "copy": {
                      "name": "multipleIPs",
                      "count": "[length(parameters('ipsobject').ips)]"
                  },
                  "name": "[concat(parameters('ipsobject').ips[copyIndex()].name,'-',parameters('environment'))]",
                  "apiVersion": "2016-03-30",
                  "location": "[variables('location')]",
                  "properties": {
                      "publicIPAllocationMethod": "[parameters('ipsobject').ips[copyIndex()].allocation]"
                  }
              }
     ],
    "outputs": { }
  }
```

Soubor s parametry:

```json
{
    "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "ipsobject": {
            "value": {
                "ips": [
                    {
                        "name": "ip01",
                        "allocation": "Static"
                    },
                    {
                        "name": "ip02",
                        "allocation": "Static"
                    },
                    {
                        "name": "ip03",
                        "allocation": "Dynamic"
                    }
                ]
            }
        },
        "environment": {
            "value": "PROD"
        }
    }
}
```

Pošleme to tam.

```bash
az group deployment create -g arm-rg --template-file loop3.json \
    --parameters @loop3.parameters.json --mode Complete
```

Takhle vypadá výsledek.

![](/images/2019/2019-03-01-06-42-30.png){:class="img-fluid"}

# Konkrétní použití

Vyzkoušeli jsme si základní konstrukty a teď už se podívejme na šablony, které dělají něco reálnějšího.

## Webová farma

V prvním příkladu chci postavit webovou farmu z virtuálních strojů. Na vstupu chci jako parametr velikost farmy (počet VM) a šablona nechť nasadí síť, subnet, load balancer, síťovky zařazené v backend poolu a virtuální stroje. Tohle je výsledek:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "apiProfile": "2018-03-01-hybrid",
    "parameters": {
        "adminUsername": {
            "type": "string",
            "metadata": {
                "description": "Username for the Virtual Machine."
            },
            "defaultValue": "tomas"
        },
        "adminPassword": {
            "type": "securestring",
            "metadata": {
                "description": "Password for the Virtual Machine."
            }
        },
        "vmSize": {
            "type": "string",
            "defaultValue": "Standard_B1s",
            "metadata": {
                "description": "The size of the Virtual Machine."
            }
        },
        "replicas": {
            "type": "int",
            "defaultValue": 2,
            "metadata": {
                "description": "Number of web farm instances."
            },
            "allowedValues": [
                1,
                2,
                3,
                4,
                5
            ]
        }
    },
    "variables": {
        "vnetName": "tomas-net",
        "vnetPrefix": "10.0.0.0/16",
        "subnetName": "web-sub",
        "subnetPrefix": "10.0.1.0/24",
        "publicLbId": "[resourceId('Microsoft.Network/loadBalancers',variables('lbName'))]",
        "lbIpName": "web-lb-ip",
        "lbName": "web-lb",
        "asName": "web-as",
        "nicPrefix": "web-nic-",
        "vmPrefix": "web-vm-"
    },
    "resources": [
        {
            "name": "[variables('vnetName')]",
            "type": "Microsoft.Network/virtualNetworks",
            "apiVersion": "2015-06-15",
            "location": "[resourceGroup().location]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "[variables('vnetPrefix')]"
                    ]
                },
                "subnets": [
                    {
                        "name": "[variables('subnetName')]",
                        "properties": {
                            "addressPrefix": "[variables('subnetPrefix')]"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Compute/availabilitySets",
            "apiVersion": "2017-03-30",
            "name": "[variables('asName')]",
            "location": "[resourceGroup().location]",
            "sku": {
                "name": "Aligned"
            },
            "properties": {
                "platformFaultDomainCount": "3",
                "platformUpdateDomainCount": "3"
            }
        },
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[variables('lbIpName')]",
            "apiVersion": "2015-06-15",
            "location": "[resourceGroup().location]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            },
            "dependsOn": [
                "[variables('vnetName')]"
            ]
        },
        {
            "name": "[variables('lbName')]",
            "type": "Microsoft.Network/loadBalancers",
            "apiVersion": "2015-06-15",
            "location": "[resourceGroup().location]",
            "dependsOn": [
                "[variables('vnetName')]",
                "[variables('lbIpName')]"
            ],
            "properties": {
                "frontendIPConfigurations": [
                    {
                        "name": "frontend",
                        "properties": {
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses',variables('lbIpName'))]"
                            }
                        }
                    }
                ],
                "backendAddressPools": [
                    {
                        "name": "backend"
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(variables('nicPrefix'), copyIndex(1))]",
            "apiVersion": "2015-06-15",
            "location": "[resourceGroup().location]",
            "copy": {
                "name": "nicLoop",
                "count": "[parameters('replicas')]"
            },
            "dependsOn": [
                "[concat('Microsoft.Network/virtualNetworks/', variables('vnetName'))]",
                "[concat('Microsoft.Network/loadBalancers/', variables('lbName'))]"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAllocationMethod": "Dynamic",
                            "subnet": {
                                "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), variables('subnetName'))]"
                            },
                            "loadBalancerBackendAddressPools": [
                                {
                                    "id": "[concat(variables('publicLbId'), '/backendAddressPools/backend')]"
                                }
                            ]
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[concat(variables('vmPrefix'), copyIndex(1))]",
            "apiVersion": "2017-03-30",
            "location": "[resourcegroup().location]",
            "copy": {
                "name": "vmLoop",
                "count": "[parameters('replicas')]"
            },
            "dependsOn": [
                "nicLoop"
            ],
            "properties": {
                "availabilitySet": {
                    "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('asName'))]"
                },
                "hardwareProfile": {
                    "vmSize": "[parameters('vmSize')]"
                },
                "osProfile": {
                    "computerName": "[concat(variables('vmPrefix'), copyIndex(1))]",
                    "adminUsername": "[parameters('adminUsername')]",
                    "adminPassword": "[parameters('adminPassword')]"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "Canonical",
                        "offer": "UbuntuServer",
                        "sku": "16.04-LTS",
                        "version": "latest"
                    },
                    "osDisk": {
                        "caching": "ReadWrite",
                        "createOption": "FromImage"
                    }
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(variables('nicPrefix'), copyIndex(1)))]"
                        }
                    ]
                }
            }
        }
    ],
    "outputs": {}
}
```

Čeho si všimnout? Smyček potřebuji několik. Tak například musím vytvořit příslušný počet síťových karet a také tento počet VM. Mrkněte na to, že VM má dependsOn na smyčce nicLoop. Také prozkoumejte jak z VM odkazuji na NIC. Protože vše pojmenováváme s indexem iterace, mohu v resource pro VM 1 v pohodě smontovat název NIC 1.

Pošleme to tam.

```bash
az group deployment create -g arm-rg --template-file loop4.json \
    --parameters adminPassword=Azure12345678 \
    --parameters replicas=3 \
    --mode Complete
```

Povedlo se, všechny zdroje máme nasazené.

![](/images/2019/2019-03-03-11-34-34.png){:class="img-fluid"}

Můžete si teď pustit šablonu znova a replicas změnit na jiné číslo, tedy přidat nebo odebrat (odebírání pouze s mode Complete) stroje z farmy. Tady jedna poznámka - můžete takto šablonu samozřejmě použít na škálování vaší aplikace, ale na to jsou k dispozici lepší metody. Pokud nutně potřebujete IaaS, tedy vlastní VMko, prozkoumejte raději Virtual Machine Scale Set. Navíc vždy doporučuji preferovat PaaS, pokud to jde - například Application Services (WebApp) má škálování v sobě nebo pokud nejde PaaS, tak CaaS - třeba Azure Kubernetes Service či Service Fabric a ty také umí pěkně škálovat.

## VM přes objektový parametr

V předchozím případě jsem stavěl webovou farmu. Stačí zadat počet a šablona vystaví příslušnou sadu identických VM přikrytých load balancerem. Následující šablona je ale trochu jiná. Pro svoje prostředí potřebuji vytvořit několik virtuálních strojů (nepotřebuji balancování apod. - pro jednoduchost), ale ne všechny stejné. Dejme tomu, že potřebuji dávat jim různé názvy a volit různé velikosti. To je dobrý příklad na použití objektu na vstupu. Předejme šabloně pole objektů, kdy každý objekt obsahuje name (jméno VM) a size (velikost VM).

Šablona je tady - vstupní objekt se jmenuje vmsObject.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "apiProfile": "2018-03-01-hybrid",
    "parameters": {
        "adminUsername": {
            "type": "string",
            "metadata": {
                "description": "Username for the Virtual Machine."
            },
            "defaultValue": "tomas"
        },
        "adminPassword": {
            "type": "securestring",
            "metadata": {
                "description": "Password for the Virtual Machine."
            }
        },
        "vmsObject": {
            "type": "object",
            "metadata": {
                "description": "Object with VMs information."
            }
        }
    },
    "variables": {
        "vnetName": "tomas-net",
        "vnetPrefix": "10.0.0.0/16",
        "subnetName": "sub",
        "subnetPrefix": "10.0.1.0/24",
        "nicSuffix": "-nic",
        "vmSuffix": "-vm"
    },
    "resources": [
        {
            "name": "[variables('vnetName')]",
            "type": "Microsoft.Network/virtualNetworks",
            "apiVersion": "2015-06-15",
            "location": "[resourceGroup().location]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "[variables('vnetPrefix')]"
                    ]
                },
                "subnets": [
                    {
                        "name": "[variables('subnetName')]",
                        "properties": {
                            "addressPrefix": "[variables('subnetPrefix')]"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('vmsObject').vms[copyIndex()].name, variables('nicSuffix'))]",
            "apiVersion": "2015-06-15",
            "location": "[resourceGroup().location]",
            "copy": {
                "name": "nicLoop",
                "count": "[length(parameters('vmsObject').vms)]"
            },
            "dependsOn": [
                "[concat('Microsoft.Network/virtualNetworks/', variables('vnetName'))]"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAllocationMethod": "Dynamic",
                            "subnet": {
                                "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), variables('subnetName'))]"
                            }
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[concat(parameters('vmsObject').vms[copyIndex()].name, variables('vmSuffix'))]",
            "apiVersion": "2017-03-30",
            "location": "[resourcegroup().location]",
            "copy": {
                "name": "vmLoop",
                "count": "[length(parameters('vmsObject').vms)]"
            },
            "dependsOn": [
                "nicLoop"
            ],
            "properties": {
                "hardwareProfile": {
                    "vmSize": "[parameters('vmsObject').vms[copyIndex()].size]"
                },
                "osProfile": {
                    "computerName": "[parameters('vmsObject').vms[copyIndex()].name]",
                    "adminUsername": "[parameters('adminUsername')]",
                    "adminPassword": "[parameters('adminPassword')]"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "Canonical",
                        "offer": "UbuntuServer",
                        "sku": "16.04-LTS",
                        "version": "latest"
                    },
                    "osDisk": {
                        "caching": "ReadWrite",
                        "createOption": "FromImage"
                    }
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('vmsObject').vms[copyIndex()].name, variables('nicSuffix')))]"
                        }
                    ]
                }
            }
        }
    ],
    "outputs": {}
}
```

Takhle bude vypadat můj soubor s parametry a definicí mých strojů.

```json
{
    "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "vmsObject": {
            "value": {
                "vms": [
                    {
                        "name": "web",
                        "size": "Standard_B1s"
                    },
                    {
                        "name": "app",
                        "size": "Standard_A1"
                    },
                    {
                        "name": "db",
                        "size": "Standard_B1ms"
                    }
                ]
            }
        }
    }
}
```

Pošleme to tam. Začneme od začátku a předchozí resource group smažeme.

```bash
az group delete -n arm-rg -y
az group create -n arm-rg -l westeurope
az group deployment create -g arm-rg --template-file loop5.json \
    --parameters adminPassword=Azure12345678 \
    --parameters @loop5.parameters.json \
    --mode Complete
```

Tady je výsledek:

![](/images/2019/2019-03-03-11-46-14.png){:class="img-fluid"}

# Složitější případ s využitím podmínek, smyček a montování variables

Ne vždycky je všechno ideální a snadné, ale dá se zabojovat a dát to dohromady. Předchozí šablona je příjemná, ale co kdybychom do vstupního parametru chtěli ještě vždy říct, jestli mašiná má mít i public IP nebo si vystačí s privátní? To je o poznání složitější, než se na první pohled zdá.

Nejprve si uveďme šablonu a parametry a pak to rozvedeme.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "apiProfile": "2018-03-01-hybrid",
    "parameters": {
        "adminUsername": {
            "type": "string",
            "metadata": {
                "description": "Username for the Virtual Machine."
            },
            "defaultValue": "tomas"
        },
        "adminPassword": {
            "type": "securestring",
            "metadata": {
                "description": "Password for the Virtual Machine."
            }
        },
        "vmsObject": {
            "type": "object",
            "metadata": {
                "description": "Object with VMs information."
            }
        }
    },
    "variables": {
        "vnetName": "tomas-net",
        "vnetPrefix": "10.0.0.0/16",
        "subnetName": "sub",
        "subnetPrefix": "10.0.1.0/24",
        "nicSuffix": "-nic",
        "vmSuffix": "-vm",
        "ipSuffix": "-ip",
        "nicProperties-public": {
            "copy": [
                {
                    "name": "ips",
                    "count": "[length(parameters('vmsObject').vms)]",
                    "input": {
                        "privateIPAllocationMethod": "Dynamic",
                        "subnet": {
                            "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), variables('subnetName'))]"
                        },
                        "publicIPAddress": {
                            "id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(parameters('vmsObject').vms[copyIndex('ips')].name, variables('ipSuffix')))]"
                        }
                    }
                }
            ]
        },
        "nicProperties-private": {
            "copy": [
                {
                    "name": "ips",
                    "count": "[length(parameters('vmsObject').vms)]",
                    "input": {
                        "privateIPAllocationMethod": "Dynamic",
                        "subnet": {
                            "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), variables('subnetName'))]"
                        }
                    }
                }
            ]
        }
    },
    "resources": [
        {
            "name": "[variables('vnetName')]",
            "type": "Microsoft.Network/virtualNetworks",
            "apiVersion": "2015-06-15",
            "location": "[resourceGroup().location]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "[variables('vnetPrefix')]"
                    ]
                },
                "subnets": [
                    {
                        "name": "[variables('subnetName')]",
                        "properties": {
                            "addressPrefix": "[variables('subnetPrefix')]"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('vmsObject').vms[copyIndex()].name, variables('ipSuffix'))]",
            "condition": "[equals(parameters('vmsObject').vms[copyIndex()].ipType,'public')]",
            "copy": {
                "name": "publicIpLoop",
                "count": "[length(parameters('vmsObject').vms)]"
            },
            "apiVersion": "2016-03-30",
            "location": "[resourcegroup().location]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        },
        {
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('vmsObject').vms[copyIndex()].name, variables('nicSuffix'))]",
            "apiVersion": "2015-06-15",
            "location": "[resourceGroup().location]",
            "copy": {
                "name": "nicLoop",
                "count": "[length(parameters('vmsObject').vms)]"
            },
            "dependsOn": [
                "[concat('Microsoft.Network/virtualNetworks/', variables('vnetName'))]"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": "[variables(concat('nicProperties-', parameters('vmsObject').vms[copyIndex()].iptype)).ips[copyIndex()]]"
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[concat(parameters('vmsObject').vms[copyIndex()].name, variables('vmSuffix'))]",
            "apiVersion": "2017-03-30",
            "location": "[resourcegroup().location]",
            "copy": {
                "name": "vmLoop",
                "count": "[length(parameters('vmsObject').vms)]"
            },
            "dependsOn": [
                "nicLoop"
            ],
            "properties": {
                "hardwareProfile": {
                    "vmSize": "[parameters('vmsObject').vms[copyIndex()].size]"
                },
                "osProfile": {
                    "computerName": "[parameters('vmsObject').vms[copyIndex()].name]",
                    "adminUsername": "[parameters('adminUsername')]",
                    "adminPassword": "[parameters('adminPassword')]"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "Canonical",
                        "offer": "UbuntuServer",
                        "sku": "16.04-LTS",
                        "version": "latest"
                    },
                    "osDisk": {
                        "caching": "ReadWrite",
                        "createOption": "FromImage"
                    }
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('vmsObject').vms[copyIndex()].name, variables('nicSuffix')))]"
                        }
                    ]
                }
            }
        }
    ],
    "outputs": {}
}
```

Tady jsou parametry.

```json
{
    "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "vmsObject": {
            "value": {
                "vms": [
                    {
                        "name": "web",
                        "size": "Standard_B1s",
                        "ipType": "public"
                    },
                    {
                        "name": "app",
                        "size": "Standard_A1",
                        "ipType": "private"
                    },
                    {
                        "name": "db",
                        "size": "Standard_B1ms",
                        "ipType": "private"
                    }
                ]
            }
        }
    }
}
```

Začněme od toho jednoduššího - vytvoření public IP jen pro ty VM, u kterých je uveden ipType public. Protože public IP je samostatný resource, dá se použít podmíněné nasazení. Jednoduše smyčkujeme nad polem objektů, ale reálně nasadíme pouze ty iterace, kdy se ipType=public.

```json
"condition": "[equals(parameters('vmsObject').vms[copyIndex()].ipType,'public')]"
```

Co je komplikovanější je přiřazení public IP k síťové kartě. To není žádný samostatný objekt, ale parametr síťové karty. Tam kondicionál použít nemůžeme. Jak něco takového řešit? Vzpomínáte si na díl, ve kterém jsem ukazoval použití "velikosti trička"? Na základě parametru velikosti řešení (S, M, L) jsme montovali příslušné atributy. Uděláme tedy to, že celé properties v nastavení NIC budeme mít jako variable. V přiřazení variable jako hodnoty v resource síťovky použijeme pro jméno variable concat s políčkem ipType. Pokud je v první iteraci ipType=public, tak u síťovky použijeme na properties hodnotu proměnné nicProperties-public[0]. U druhé iterace, kde je v parametrech private, se použije nicProperties-private[1] a tak dále.

```json
"properties": "[variables(concat('nicProperties-', parameters('vmsObject').vms[copyIndex()].iptype)).ips[copyIndex()]]"
```

Výborně - podle parametru public nebo private si vybereme proměnnou obsahující celé properties a ta jednou bude mít jen privátní IP a jindy zase i tu veřejnou. Protože ale jedeme síťovky v cyklu, musíme vytvořit pole objektů pro naše nicProperties variables. Využijeme možnosti loop na úrovni variables. 

```json
"nicProperties-public": {
            "copy": [
                {
                    "name": "ips",
                    "count": "[length(parameters('vmsObject').vms)]",
                    "input": {
                        "privateIPAllocationMethod": "Dynamic",
                        "subnet": {
                            "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), variables('subnetName'))]"
                        },
                        "publicIPAddress": {
                            "id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(parameters('vmsObject').vms[copyIndex('ips')].name, variables('ipSuffix')))]"
                        }
                    }
                }
            ]
        },
        "nicProperties-private": {
            "copy": [
                {
                    "name": "ips",
                    "count": "[length(parameters('vmsObject').vms)]",
                    "input": {
                        "privateIPAllocationMethod": "Dynamic",
                        "subnet": {
                            "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), variables('subnetName'))]"
                        }
                    }
                }
            ]
        }
```

Všimněte si, že v tomto kroku sestavíme kompletní pole možností pro obě proměnné. nicProperties-public bude mít záznam pro všechna VM tak jak jdou po sobě a nicProperties-private taky.

Pošleme to do Azure.

```bash
az group deployment create -g arm-rg --template-file loop6.json \
    --parameters adminPassword=Azure12345678 \
    --parameters @loop6.parameters.json \
    --mode Complete
```

A tady máme výsledek:

![](/images/2019/2019-03-03-11-52-01.png){:class="img-fluid"}

![](/images/2019/2019-03-03-11-52-31.png){:class="img-fluid"}

Vidíte, že tohle už je trochu komplikovanější, ale i přes to, že ARM šablona není žádný programovací jazyk, má dost konstruktů na to tohle zvládnout. A proč že jsme to vlastně dělali? Chceme šablonu maximálně univerzální. Mimochodem podobné situace bude dost možná zajímavé vyřešit linkovanou či vnořenou šablonou - na což se brzy také podíváme.

Vytvářejte šablony, které jsou univerzální a použitelné beze změny jejich těla od dev přes test, staging až do produkce. Konstrukty typu loop nebo condition vám k tomu určitě pomůžou. Tak pojďte do toho... přece nebudete kolegům do produkce posílat 100-stránkové PDF plné screenshotů z GUI kde stejnak na straně 79 jeden krok zapomenou a nebude to fungovat :)