---
layout: post
status: draft
published: true
title: ARM šablony (2) - parametry, variables a Key Vault
tags:
- Automatizace
---
Dnes se pustíme do práce s parametry a proměnnými v rámci Azure šablon.

# Visual Studio Code jako pomůcka pro vytváření šablon
V dnešním díle doporučuji nainstalovat si Visual Studio Code a extension pro syntaxi ARM šablon.

![](/images/2019/2019-02-11-07-09-11.png){:class="img-fluid"}

S tímto rozšířením vám VS Code bude pomáhat se syntaxí, bude chápat strukturu šablony a napovídat. Kromě toho doporučuji ještě rozšíření, které umí automaticky formátovat JSON tak, aby vypadal vždy stejně.

![](/images/2019/2019-02-11-07-10-43.png){:class="img-fluid"}

V dalších dílech si ukážeme pomůcky pro práci s resources, ale to dnes ještě potřebovat nebudeme. Dnes se budeme držet základů - parametrů a proměnných.

# Šablona s proměnnou
Mějme následující šablonu (dám ji do souboru 02.json), která nasazuje dvě IP adresy. Je tam jedna věc, která se opakuje - location (Azure region). Pojďme ji přesunout do proměnné, takže pokud se někdy rozhodneme to změnit, nemusíme upravovat jednotlivé zdroje.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "variables": {
        "location": "westeurope"
    },
    "resources": [
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "myIP1",
            "apiVersion": "2016-03-30",
            "location": "[variables('location')]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        },
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "myIP2",
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

Pro nasazení budu používat Azure CLI, ale stejně tak můžete použít třeba PowerShell případně GUI.

Nejprve vytvořím Resource Group.
```bash
az group create -n myarm -l westeurope
```

Následně tam pošleme naší šablonu.
```bash
az group deployment create -g myarm --template-file 02.json
```

Nasazení se povedlo, máme tam dvě public IP adresy.

![](/images/2019/2019-02-11-07-22-28.png){:class="img-fluid"}

Podívejme se na deploymenty.

![](/images/2019/2019-02-11-07-22-59.png){:class="img-fluid"}

![](/images/2019/2019-02-11-07-23-22.png){:class="img-fluid"}

Šablony jsou idempotentní. Klidně ji tam pošlete znova a vše bude stále v pořádku.
```bash
az group deployment create -g myarm --template-file 02.json
```

# Parametr pro prefix jména
Možná chceme, aby název IP adresy obsahoval nějaký prefix, třeba dev-myIP1 nebo prod-myIP1. Tento prefix bude něco, co zadáváme při deploymentu jako parametr, takže pro nasazení v dev a prod nemusíme měnit šablonu samotnou. Dále si musíme smontovat výsledný název a na to použijeme funkci concat. Pro parametr nastavíme nějaké další věci. Typ parametru bude string a volitelně doplníme další věci. allowedValues nám umožní omezit výběr prefixů, takže při nasazování to musí být jedna z uvedených hodnot. Dále specifikujeme defaultValue, takže parametr není povinný - pokud neřekneme jinak, bude to tato hodnota. S defaulty buďte opatrní, ale já rád dávám šablony do stavu, kdy si nejzákladnější příklad člověk nasadí, aniž by musel hned odpovídat na mnoho otázek, viděl co to dělá a pak si tepr pohrál s parametry. Nakonec ještě použijeme metadata a description, které bude sloužit jako dokumentace co vlastně parametr znamená. Výsledek uložím do 03.json a vypadá nějak takhle:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "envPrefix": {
            "type": "string",
            "allowedValues": [
                "dev",
                "test",
                "prod"
            ],
            "defaultValue": "dev",
            "metadata": {
                "description": "Vyberte si prefix prostredi"
            }
        }
    },
    "variables": {
        "location": "westeurope"
    },
    "resources": [
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('envPrefix'), '-myIP1')]",
            "apiVersion": "2016-03-30",
            "location": "[variables('location')]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        },
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('envPrefix'), '-myIP2')]",
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

Vyzkoušejme si teď, jak by šablona vypadala v GUI (ale nebudeme ji tam posílat, jen se koukneme jak se to zobrazí). Přes + dejte template deployment a natáhněte náš soubor. Všimněte si, že GUI dává na výběr z omezených hodnot a také zobrazuje naší description.

![](/images/2019/2019-02-11-08-05-17.png){:class="img-fluid"}

![](/images/2019/2019-02-11-08-05-47.png){:class="img-fluid"}

Deployment si ale uděláme přes CLI. Pošleme to tam a necháme výchozí hodnotu parametru.

```bash
az group deployment create -g myarm --template-file 03.json
```

Funguje! Všimněme si ale jedné věci. Původní IP adresy tam zůstaly.

![](/images/2019/2019-02-11-08-07-48.png){:class="img-fluid"}

Jak to? ARM ve výchozím stavu používá opatrný režim, který není přesně podle učebnice desired state. Tím, že mají objekty jiné jméno jde vlastně o jiné objekty. ARM přidal dvě IP adresy definované v šabloně, ale pokud jsou v resource group zdroje, které v šabloně chybí, ARM je nechá být. Pro úvodní práci s desired state je to dobré bezpečnostní nastavení, abychom si omylem neumazali něco co potřebujeme tím, že tam pošleme třeba prázdnou šablonu. V okamžiku, kdy si ale dokonale zažijete celý mechanismus, doporučuji přejít na plně desired state řešení. Tedy co v šabloně už není, to se odmaže.

```bash
az group deployment create -g myarm --template-file 03.json --mode Complete
```

![](/images/2019/2019-02-11-08-12-07.png){:class="img-fluid"}

Jak specifikovat parametr? První možnost je přímo v příkazové řádce při deploymentu.

```bash
az group deployment create -g myarm \
    --template-file 03.json \
    --mode Complete \
    --parameters envPrefix=prod
```

![](/images/2019/2019-02-11-08-14-31.png){:class="img-fluid"}

Nevýhodou takového řešení je, že nemáte tento stav zaznamený ve svém version control systému, kam šablony patří, například v Azure Repos v rámci nástroje Azure DevOps. Proto můžete použité parametry také uložit do JSON souboru a ten použít při deploymentu. Vytvořte si tento soubor 03.parameters.json:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "envPrefix": {
            "value": "test"
        }
    }
}
```

Provedeme deployment a použijeme tento soubor s parametry.

```bash
az group deployment create -g myarm \
    --template-file 03.json \
    --mode Complete \
    --parameters @03.parameters.json
```

![](/images/2019/2019-02-11-08-19-53.png){:class="img-fluid"}

Do reálnosti příkladu nám chybí ještě jedna věc. Typicky máte nějakou jmennou konvenci, například prostředí-název-typzdroje. Prostředí máme jako parametr, název v těle resource. Přidejme ještě typ zdroje. To je něco, co nechci jako parametr, protože k tomu přistupuji stejně v testu i produkci. Nicméně jednou konvenci třeba budu chtít změnit. Ideálním kandidátem tedy bude variable. Může to vypadat nějak takhle (04.json):

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "envPrefix": {
            "type": "string",
            "allowedValues": [
                "dev",
                "test",
                "prod"
            ],
            "defaultValue": "dev",
            "metadata": {
                "description": "Vyberte si prefix prostredi"
            }
        }
    },
    "variables": {
        "location": "westeurope",
        "ipNameSuffix": "-ip"
    },
    "resources": [
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('envPrefix'), '-', 'myIP1', variables('ipNameSuffix'))]",
            "apiVersion": "2016-03-30",
            "location": "[variables('location')]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        },
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('envPrefix'), '-', 'myIP2', variables('ipNameSuffix'))]",
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

Pošleme to tam.

```bash
az group deployment create -g myarm \
    --template-file 04.json \
    --mode Complete \
    --parameters envPrefix=prod
```

![](/images/2019/2019-02-11-08-27-18.png){:class="img-fluid"}

# Předávání tajností
Při vytváření některých zdrojů musíme specifikovat i citlivé údaje, například heslo do Azure SQL, který šablona vytvoří. Určitě nebude dobré heslo mít přímo v těle šablony, protože ho každý uvidí. V šabloně by nikdy nemělo být něco tak citlivého jako je heslo, klíč nebo certifikát. První nápad tedy bude předávat heslo jako parametr. Mějme jednoduchou šablonu pro nasazení sql (strukturu resources zatím moc neřešme, k tomu se dostaneme jindy). Musím vysvětlit jednu věc, kterou potřebujeme. Název SQL serveru musí být unikátní globálně. Protože na názvu serveru by nám nemělo záležet, tak ať je klidně postaven z nějakého GUID. Pokud bychom v šabloně použili nějakou funkci "random" (která tedy neexistuje), máme problém. Tušíte jaký? Při každém spuštění by random vyšel jinak a ARM by tak vytvořil jiný (další) zdroj nebo v mode Complete by původní zrušil a vytvořil nový (takže bychom přišli o data). Porušili bychom idempotenci, ARM by se nedal spouštět víckrát. Potřebujeme tedy, abychom získali nějaký řetězec typu GUID, ale ten se neměnil (takže další spuštění zdroj nevyhodí ani nezaloží nový, ale provede update stávajícího, pokud je na něm třeba udělat změnu). ARM nabízí funkci uniqueString, která provede hash ze zadaného řetězce. Do této funkce vložíme jinou funkci, která vrácí plné ID naší resource group (tzn. bude v tom ID subskripce i resource group). Hash se tak vytvoří z něčeho, co je pro nás unikátní, ale pokaždé vyjde stejně. V jiné resource group či subskripci vznikne jiný řetězec, ale pokud je to stejná resource group a subskripce, bude to stejné - zajistíme tak idempotenci. 

Tohle je moje šablona sql01.json:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "sqlPassword": {
            "type": "string",
            "metadata": {
                "description": "Heslo pro vytvoreny SQL"
            }
        }
    },
    "variables": {
        "location": "westeurope",
        "sqlName": "[concat('sql-', uniqueString(resourceGroup().Id))]",
        "sqlLogin": "tomas"
    },
    "resources": [
        {
            "type": "Microsoft.Sql/servers",
            "name": "[variables('sqlName')]",
            "apiVersion": "2015-05-01-preview",
            "location": "[variables('location')]",
            "properties": {
                "administratorLogin": "[variables('sqlLogin')]",
                "administratorLoginPassword": "[parameters('sqlPassword')]",
                "version": "12.0"
            },
            "resources": [
                {
                    "type": "firewallRules",
                    "name": "AllowAllIps",
                    "apiVersion": "2015-05-01-preview",
                    "location": "[variables('location')]",
                    "dependsOn": [
                        "[variables('sqlName')]"
                    ],
                    "properties": {
                        "endIpAddress": "255.255.255.255",
                        "startIpAddress": "0.0.0.0"
                    }
                },
                {
                    "name": "mojedb",
                    "type": "databases",
                    "location": "[variables('location')]",
                    "apiVersion": "2015-01-01",
                    "dependsOn": [
                        "[variables('sqlName')]"
                    ],
                    "properties": {
                        "edition": "Basic",
                        "collation": "SQL_Latin1_General_CP1_CI_AS",
                        "requestedServiceObjectiveName": "Basic"
                    }
                }
            ]
        }
    ],
    "outputs": {}
}
```

Pošleme ji tam.

```bash
az group create -n sql -l westeurope
az group deployment create -g sql \
    --template-file sql01.json \
    --parameters sqlPassword=Azure12345678
```

Vypadá to dobře. Logický SQL server a Azure SQL databáze jsou založené.

![](/images/2019/2019-02-11-08-46-51.png){:class="img-fluid"}

Abych ověřil, že heslo funguje, použiji Query explorer v GUI. Tam se přihlásím a mělo by všechno proběhnout správně.

![](/images/2019/2019-02-11-08-57-00.png){:class="img-fluid"}

![](/images/2019/2019-02-11-08-57-15.png){:class="img-fluid"}

Na tomto místě poznámka - doporučuji využít integraci Azure SQL do Azure Active Directory. Je to velmi bezpečný způsob a například vaši administrátoři mohou pro připojení do databáze použít vícefaktorové ověření a single-sign-on. Ale to teď nechme stranou.

Připojení funguje, ale máme jeden problém. Podívejme se do Deploymentu a sekce Inputs.

![](/images/2019/2019-02-11-08-58-54.png){:class="img-fluid"}

![](/images/2019/2019-02-11-08-59-22.png){:class="img-fluid"}

Ale! Heslo je tam vidět. Kdokoli, kdo má právo Reader ho zobrazí. To určitě není dobře. Je to tím, že jsme v šabloně použili typ string. Pojďme to předělat na securestring.

Soubor sql02.json je skoro stejný, jen parametr ma jiný type.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "sqlPassword": {
            "type": "securestring",
            "metadata": {
                "description": "Heslo pro vytvoreny SQL"
            }
        }
    },
    "variables": {
        "location": "westeurope",
        "sqlName": "[concat('sql-', uniqueString(resourceGroup().Id))]",
        "sqlLogin": "tomas"
    },
    "resources": [
        {
            "type": "Microsoft.Sql/servers",
            "name": "[variables('sqlName')]",
            "apiVersion": "2015-05-01-preview",
            "location": "[variables('location')]",
            "properties": {
                "administratorLogin": "[variables('sqlLogin')]",
                "administratorLoginPassword": "[parameters('sqlPassword')]",
                "version": "12.0"
            },
            "resources": [
                {
                    "type": "firewallRules",
                    "name": "AllowAllIps",
                    "apiVersion": "2015-05-01-preview",
                    "location": "[variables('location')]",
                    "dependsOn": [
                        "[variables('sqlName')]"
                    ],
                    "properties": {
                        "endIpAddress": "255.255.255.255",
                        "startIpAddress": "0.0.0.0"
                    }
                },
                {
                    "name": "mojedb",
                    "type": "databases",
                    "location": "[variables('location')]",
                    "apiVersion": "2015-01-01",
                    "dependsOn": [
                        "[variables('sqlName')]"
                    ],
                    "properties": {
                        "edition": "Basic",
                        "collation": "SQL_Latin1_General_CP1_CI_AS",
                        "requestedServiceObjectiveName": "Basic"
                    }
                }
            ]
        }
    ],
    "outputs": {}
}
```

Pošleme ji tam.

```bash
az group deployment create -g sql \
    --template-file sql02.json \
    --parameters sqlPassword=Azure12345678
```

To už je rozhodně lepší.

![](/images/2019/2019-02-11-09-02-50.png){:class="img-fluid"}

# Předávání tajností přes Azure Key Vault
Předchozí příklad už je bezpečný a velmi rozumný, nicméně má stále nějaké nepříjemnosti:
* Co když potřebujeme oddělit člověka co provádí deployment od toho, kdo má na starost správu hesel? Chtěl bych aby bezpečák vytvořil heslo, které při deploymentu nemusí administrátor vidět. Prostě jen dá referenci na existující heslo, které spravuje někdo jiný.
* Jak se o heslu do databáze dozví moje aplikace? Mohl bych jí předat parametry pokud ji vytvářím také ARM šablonou, třeba u WebApp ji při zakládání uložím do jejích connection stringů. To bude určitě fungovat, ale co když je kód v platformě, která to neumožňuje, třeba VMku, kde je bezpečné předávání hesel obtížnější? Nebo co když dokonce běží mimo Azure, například jako Javascript kód na klientovi (jasně - frontend nemá co chodit do DB napřímo, ale může to být jiná tajnost, například šifrovací klíč nebo certifikát)?

Pokud to s tajnostmi začneme myslet hodně vážně, bude ideální je ukládat do trezoru Azure Key Vault. Ten bude mít ve správě bezpečák a aplikace si to z něj budou vyzvedávat. Totéž dokáže ARM. Můžeme vytvořit Key Vault a ARMu dát právo si z něj hesla vyzvedávat v okamžiku deploymentu. Infrastrukturu tak může nasadit někdo, kdo má právo zdroje založit, ale nemusí mít do Key Vaultu přístup.

Založme si tedy coby bezpečák Key Vault.

```bash
az group create -n mojetajnosti-rg -l westeurope
az keyvault create -n mujtrezor-kv  \
    -g mojetajnosti-rg \
    --enabled-for-template-deployment
az keyvault secret set -n sqlPassword \
    --vault-name mujtrezor-kv \
    --value Azure12345678
```

Výborně. Zjistěme si teď ID našeho secret.

```bash
az keyvault show -n mujtrezor-kv -g mojetajnosti-rg --query id -o tsv
```

Vytvořme si soubor sql02.parameters.json a změňte si v něm ID tak, ať odpovídá tomu vašemu.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "sqlPassword": {
            "reference": {
                "keyVault": {
                    "id": "/subscriptions/000-111-2222/resourceGroups/mojetajnosti-rg/providers/Microsoft.KeyVault/vaults/mujtrezor-kv"
                },
                "secretName": "sqlLogin"
            }
        }
    }
}
```

Proveďme teď deployment SQL znovu s tím, že nebudeme zadávat heslo ze CLI, ale použijeme výše uvedený soubor. Tím zajistíme, že ARM si vytáhne heslo z trezoru. Udělat to může i uživatel, který nemá do trezoru přístup - ARM jako takový jsme autorizovali přepínačem --enabled-for-template-deployment při vytváření trezoru.

```bash
az group deployment create -g sql \
    --template-file sql02.json \
    --parameters @sql02.parameters.json
```

A je to. Velmi bezpečný způsob jak spravovat tajnosti v Azure a to jak pro deployment tak následně pro přístup z aplikace.

# Šablona pro velikosti trička
Poslední, co ještě v tomto díle musím zmínit je koncept tvorby šablon podle velikosti trička. V zásadě jde o to, že potřebujete nějak řešit sizing. Podle počtu očekávaných odbavených requestů nebo podle typu prostředí (test je výkonnostně snížen oproti produkci) potřebujete vybrat správné parametry pro jednotlivé služby. Vzniká ale dost stupňů volnosti. SKU databáze, SKU virtuálních strojů a ve finále to může být třeba 50 parametrů. Chcete je všechny nabídnout pro konfiguraci při nasazení a dát je jako parameters? Uff, to bude teda docela nepřehledné. Chcete je schovat jako variable? Pak ale nemůžete stejnou šablonu použít od testu do produkce, pokud v různých prostředích chcete různý sizing. Kudy do toho?

Řešením je kompromis. Zjednodušte šablonu tak, že připravíte nějaký standardní sizing ve velikostech S, M, L a XL. To je to, co si volíte při deploymentu. Tyto velikosti se budou přes variables promítat do konkrétního sizingu. Snížíte stupně volnosti, zjednodušíte to, ale přesto necháte možnost zvolit si jak velké to řešení má být. Já pro zjednodušení použiji jen velikost S a M.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "sqlPassword": {
            "type": "securestring",
            "metadata": {
                "description": "Heslo pro vytvoreny SQL"
            }
        },
        "sizing": {
            "type": "string",
            "allowedValues": [
                "S",
                "M"
            ],
            "metadata": {
                "description": "Velikost prostredi: S - small, M - middle"
            }
        }
    },
    "variables": {
        "location": "westeurope",
        "sqlName": "[concat('sql-', uniqueString(resourceGroup().Id))]",
        "sqlLogin": "tomas",
        "S-size": {
            "sqlEdition": "Basic",
            "sqlRequestedServiceObjectiveName": "Basic",
            "containerCpu": 1,
            "containerRam": 1
        },
        "M-size": {
            "sqlEdition": "Standard",
            "sqlRequestedServiceObjectiveName": "S0",
            "containerCpu": 2,
            "containerRam": 2
        },
        "size": "[concat(parameters('sizing'), '-size')]"
    },
    "resources": [
        {
            "type": "Microsoft.Sql/servers",
            "name": "[variables('sqlName')]",
            "apiVersion": "2015-05-01-preview",
            "location": "[variables('location')]",
            "properties": {
                "administratorLogin": "[variables('sqlLogin')]",
                "administratorLoginPassword": "[parameters('sqlPassword')]",
                "version": "12.0"
            },
            "resources": [
                {
                    "type": "firewallRules",
                    "name": "AllowAllIps",
                    "apiVersion": "2015-05-01-preview",
                    "location": "[variables('location')]",
                    "dependsOn": [
                        "[variables('sqlName')]"
                    ],
                    "properties": {
                        "endIpAddress": "255.255.255.255",
                        "startIpAddress": "0.0.0.0"
                    }
                },
                {
                    "name": "mojedb",
                    "type": "databases",
                    "location": "[variables('location')]",
                    "apiVersion": "2015-01-01",
                    "dependsOn": [
                        "[variables('sqlName')]"
                    ],
                    "properties": {
                        "edition": "[variables(variables('size')).sqlEdition]",
                        "collation": "SQL_Latin1_General_CP1_CI_AS",
                        "requestedServiceObjectiveName": "[variables(variables('size')).sqlRequestedServiceObjectiveName]"
                    }
                }
            ]
        },
        {
            "type": "Microsoft.ContainerInstance/containerGroups",
            "name": "appContainer",
            "apiVersion": "2018-10-01",
            "location": "[variables('location')]",
            "properties": {
                "containers": [
                    {
                        "name": "nginx",
                        "properties": {
                            "image": "nginx",
                            "resources": {
                                "requests": {
                                    "cpu": "[variables(variables('size')).containerCpu]",
                                    "memoryInGb": "[variables(variables('size')).containerCpu]"
                                }
                            }
                        }
                    }
                ],
                "osType": "Linux",
                "restartPolicy": "Never"
            }
        }
    ],
    "outputs": {}
}
```

Všimněte si hlavní finty. Použijeme parametr, na základě kterého smontujeme název proměnné (to se děje ve variable size), kterou použijeme. Resources tak použijí buď proměnnou S-size nebo M-size. Tato proměnná je typu object a obsahuje konfigurační parametry pro sizing databáze i aplikačního kontejneru.

Vyzkoušíme si (pozn.: Azure Container Instances neumožňuje změny v počtu CPU za chodu, takže tyto hodnoty nelze ARM šablonou jednoduše updatovat, ale na nasazení je to OK - většina ostatních zdrojů včetně třeba VM to umí, ale nechtěl jsem sekci resources mít příliš komplikovanou, protože ji budeme řešit někdy příště).

```bash
az group deployment create -g sql \
    --mode Complete \
    --template-file sql03.json \
    --parameters sqlPassword=Azure12345678 \
    --parameters sizing=S
```

Pro dnešek stačí. Podívali jsme se na používaní parametrů a proměnných v ARM šablonách. Vaším cílem by mělo být vytvářet šablony, které jsou dobře udržovatelné, jednoduché na nasazení, ale přitom konfigurovatelné tak, že mezi jednotlivými deploymenty do různých prostředí není nutné šablonu upravovat. Pohrajte si s tím a posuňte se z obtížně opakovatelného klikání v GUI do deklarativního modelu desired state.
