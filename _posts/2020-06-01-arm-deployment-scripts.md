---
layout: post
title: Potřebujete v rámci ARM šablony spouštět nějakou pokročilou logiku? Zkuste ARM deployment scripts.
tags:
- Automatizace
---
Následující téma je trochu kontroverzní. ARM nabízí deklarativní model vytváření zdrojů v Azure. Pokud potřebujete s vytvořenými zdroji něco dělat, například je naplnit daty, už to není starost ARMu - ten má jen vytvářet Azure zdroje. Tento další krok by měl udělat někdo jiný, například CI/CD pipeline v podobě GitHub Actions, Azure DevOps Pipeline a tak podobně, která na to bude mít buď nějaký skript či zavolá jiný systém typu Ansible. A co když potřebuji před nasazením zdroje nějaké chytré rozhodnutí, třeba kontaktovat IPAM a zjistit, jaké IP rozsahy jsou v rámci organizace volné? Tohle bych měl zase udělat před tím, že šablonu spustím a předat jí to jako parametr. Jenže jsou situace, kdy to sice není konceptuálně čisté, ale dávalo by smysl v rámci ARM šablony spustit i imperativní kód:
- Možná chcete něco malého a něco, co je hodně spojené s infrastrukturou - například ve storage accountu založit kontejner (ano - tohle ARM aktuálně neudělá, kontejner už je vnitřek), nasadit strukturu tabulek v SQL nebo nakopírovat bloby ze "skeletonového" accountu
- Třeba potřebujete vygenerovat certifikát
- Možná je nutné sáhnout do AAD, například vytvořit aplikační registraci a předat ji aplikaci (třeba přes Key Vault)
- Chybí vám vstupní údaje, potřebujete zjistit volné IP adresy pro VNET nebo získat licenci pro nějaký produkt třetí strany

Jak říkám - nejsem nadšený z toho, že to dáte do ARM šablony, ale jsou situace, kdy bych do toho šel:
- Šablona generuje nějaké vývojářské prostředí, které má kliknutím na webu rozjet všechno potřebné a ne vývojářům říct, že potřebují spoustu úkonů před a druhou spoustu po nasazení (například na rozdíl od produkce tu nejsou připravená tahadla ve formě dalších nástrojů jako jsou CI/CD pipeline, takže by to bylo dost ruční práce)
- Potřebujete vytvořit produktový balíček tak, aby všechno bylo zapouzdřeno jedním systémem integrovatelným přímo do Azure portálu:
  - Jste dodavatel software a chcete svůj produkt nabídnout v marketplace v Azure včetně trial/demo řešení, kdy to celé naběhne včetně testovacích dat a všeho potřebného
  - Jste IT organizace a chcete pro své interní uživatele nabídnout základní aplikace (koncept Managed Applications, tedy řekněme privátní marketplace), které mají naběhnout bez nutnosti řešit něco dalšího (například CMS nenaběhne, pokud se mu nezaloží struktura v DB)

# Příklad deployment scriptu s ARM
Vyzkoušejme si deployment skripty v následujícím příkladu. Představme si, že vytváříme storage account, ke kterému se bude přistupovat přes Internet z on-premises prostředí a pro zabezpečení potřebujeme do storage account firewallu dát whitelist pouze na jednu IP adresu (tu našeho on-premises prostředí). Protože ta se ale občas mění, budeme ji chtít dosadit dynamicky pokaždé, když šablonu spustíme, tedy jak při prvním nasazení, tak i při všech pozdějších dalších aplikacích. Vyřešíme to skriptem, který získá potřebnou IP adresu (například by kontaktoval nějaký IPAM či jiné API) a jako výstup tuto hodnotu vrátí. Následně vytvoříme (nebo upravíme existující) storage account a whitelist na tuto IP.

V dalším kroku budeme chtít provést upload jednoho souboru s daty do kontejneru ve storage accountu. Druhý skript tedy bude mít za úkol vytvořit kontejner v blob storage, stáhnout data z open data zdroje a nahrát je do accountu. Na rozdíl od whitelist adresy tohle nechceme spouštět při každém deploymentu šablony - jen jednou.

## Stavba šablon
Aby se dobře pracovalo se všemi návaznostmi a odečítám hodnot přes refernce funkce včetně výstupů ze skriptů apod. bylo nejjednodušší vydat se cestou atomárních ARM šablon a jejich provázání přes master šablonu. Ta vypadá takhle:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "utcValue": {
            "type": "string",
            "defaultValue": "[utcNow()]"
        }
    },
    "variables": {
        "templatesBaseUrl": "https://raw.githubusercontent.com/tkubica12/infra-as-code-on-azure/master/arm-deploy-script-resource/",
        "storageAccountName": "[uniqueString(resourceGroup().Id)]",
        "identityName": "[concat('identity-', uniqueString(resourceGroup().Id))]",
    },
    "resources": [
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2019-10-01",
            "name": "createScriptIdenitity",
            "properties": {
                "mode": "Incremental",
                "templateLink": {
                    "uri": "[concat(variables('templatesBaseUrl'), 'createScriptIdentity.json')]",
                    "contentVersion": "1.0.0.0"
                },
                "parameters": {
                    "identityName": {
                        "value": "[variables('identityName')]"
                    }
                }
            }
        },
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2019-10-01",
            "name": "getWhitelistIp",
            "dependsOn": [
                "createScriptIdenitity"
            ],
            "properties": {
                "mode": "Incremental",
                "templateLink": {
                    "uri": "[concat(variables('templatesBaseUrl'), 'getWhitelistIp.json')]",
                    "contentVersion": "1.0.0.0"
                },
                "parameters": {
                    "identityName": {
                        "value": "[variables('identityName')]"
                    },
                    "utcValue": {
                        "value": "[parameters('utcValue')]"
                    }
                }
            }
        },
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2019-10-01",
            "name": "createStorageAccount",
            "dependsOn": [
                "getWhitelistIp"
            ],
            "properties": {
                "mode": "Incremental",
                "templateLink": {
                    "uri": "[concat(variables('templatesBaseUrl'), 'createStorageAccount.json')]",
                    "contentVersion": "1.0.0.0"
                },
                "parameters": {
                    "whitelistIp": {
                        "value": "[reference('getWhitelistIp').outputs.ip.value]"
                    },
                    "storageAccountName": {
                        "value": "[variables('storageAccountName')]"
                    }
                }
            }
        },
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2019-10-01",
            "name": "uploadData",
            "dependsOn": [
                "createStorageAccount"
            ],
            "properties": {
                "mode": "Incremental",
                "templateLink": {
                    "uri": "[concat(variables('templatesBaseUrl'), 'uploadData.json')]",
                    "contentVersion": "1.0.0.0"
                },
                "parameters": {
                    "identityName": {
                        "value": "[variables('identityName')]"
                    },
                    "storageAccountName": {
                        "value": "[variables('storageAccountName')]"
                    }
                }
            }
        }
    ]
}
```

Provolává tedy s přihlédnutím k potřebným návaznostem jednotlivé nalinkované šabony.

Podívejme se na první z nich - přípravu identit. Jde o to, že skript, který pustíme, možná bude potřebovat přistupovat do Azure a k tomu bude použita managed identita. Takovou ale musíme nejprve vytvořit a přidělit jí nějaká práva. To dělám v této šabloně, která vytvoří účet a dá mu contributor práva na resource group, kam ji nasazujeme.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "identityName": {
            "type": "string"
        }
    },
    "variables": {
        "contributorRoleId": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Authorization/roleDefinitions/', 'b24988ac-6180-42a0-ab88-20f7382dd24c')]"
    },
    "resources": [
        {
            "type": "Microsoft.ManagedIdentity/userAssignedIdentities",
            "apiVersion": "2018-11-30",
            "name": "[parameters('identityName')]",
            "location": "[resourceGroup().location]"
        },
        {
            "type": "Microsoft.Authorization/roleAssignments",
            "apiVersion": "2018-09-01-preview",
            "name": "[guid(concat(resourceGroup().id, 'contributor'))]",
            "dependsOn": [
                "[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', parameters('identityName'))]"
            ],
            "properties": {
                "roleDefinitionId": "[variables('contributorRoleId')]",
                "principalId": "[reference(resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', parameters('identityName')), '2018-11-30').principalId]",
                "scope": "[resourceGroup().id]",
                "principalType": "ServicePrincipal"
            }
        }
    ]
}
```

Další v pořadí bude vytažení IP adresy z nějakého API, třeba IPAM apod. Půjde tedy už o skript. Tomu můžeme předávat hodnoty proměnných prostředí i argumenty ke skriptu. Samotný kód může být buď takhle inline nebo předaný odkazem na shell soubor. Použiji Linux variantu, pro kterou ARM deployment skript automaticky použije kontejner s azure-cli. K dispozici je také Windows verze s PowerShell moduly pro Azure. Všimněte si, že atribut forceUpdateTag má hodnotu aktuálního času (taková finta - v šabloně ji nemůžete běžně použít, protože není idempotentní - povolena je pouze jako default hodnota parametru, jak jsem udělal). Jde o to, že ARM je desired state, takže se podívá, jestli realita odpovídá stavu popsanému šablonou. U skriptu to ale znamená pouze prověřit, že se nezměnil třeba kód samotného skriptu, ale nebude zkoumat jeho výsledek. Tím pádem nepozná, pokud už by teď vracel jinou IP. Tímto způsobem bude atribut forceUpdateTag při každém spuštění jiný a skript se pustí pokaždé, což chci.

Co tedy ve skriptu dělám? Pro vyzkoušení práce s env a argumenty je vypíšu na obrazovku. Následně si zjistím přesveřejnou IP svého blogu (to nám k ničemu není, ale simuluji tady ten proces zavolání někam přes API nebo získání informací nějakým způsobem jako je DNS dotaz) a výsledek potřebuji naformátovat jako JSON a uložit do souboru $AZ_SCRIPTS_OUTPUT_PATH. To je místo, které ARM deployment scripts vezme jako výchoí hodnotu. Tímto způsobem tedy můžeme předat nějaké informace dál, což přesně pořebujeme. Výstup ze skriptu ještě zadám jako výstup celé šablony, abychom si mohli hodnotu přečíst v master template.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "utcValue": {
            "type": "string",
            "defaultValue": "[utcNow()]"
        },
        "identityName": {
            "type": "string"
        }
    },
    "variables": {
    },
    "resources": [
        {
            "type": "Microsoft.Resources/deploymentScripts",
            "apiVersion": "2019-10-01-preview",
            "name": "getWhitelistIp",
            "location": "[resourceGroup().location]",
            "kind": "AzureCLI",
            "identity": {
                "type": "UserAssigned",
                "userAssignedIdentities": {
                    "[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', parameters('identityName'))]": {
                    }
                }
            },
            "properties": {
                "forceUpdateTag": "[parameters('utcValue')]",
                "AzCliVersion": "2.0.80",
                "timeout": "PT10M",
                "arguments": "mujarg1 mujarg2",
                "environmentVariables": [
                    {
                        "name": "MUJ_ENV",
                        "value": "mojeHodnota"
                    }
                ],
                "scriptContent": "apk add bind-tools; echo Ahojky, argumenty jsou $1 a $2, MUJ_ENV je $MUJ_ENV; host -4 tomaskubica.cz; ip=$(host -4 tomaskubica.cz | awk '{ print $NF }'); jq -n --arg ip $ip '{ip:$ip}' > $AZ_SCRIPTS_OUTPUT_PATH; cat $AZ_SCRIPTS_OUTPUT_PATH",
                "cleanupPreference": "OnSuccess",
                "retentionInterval": "P1D"
            }
        }
    ],
    "outputs": {
        "ip": {
            "value": "[reference('getWhitelistIp').outputs.ip]",
            "type": "string"
        }
    }
}
```

Další šablona je velmi jednoduchá - vytvoříme storage account a do firewallu dáme whitelist na zjištěnou IP adresu, kterou předáváme jako parametr (master šablona ji vezme z výstupu šablony s deployment skriptem zjišťujícím IP adresu).

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "whitelistIp": {
            "type": "string"
        },
        "storageAccountName": {
            "type": "string"
        }
    },
    "variables": {},
    "resources": [
        {
            "type": "Microsoft.Storage/storageAccounts",
            "name": "[parameters('storageAccountName')]",
            "apiVersion": "2017-06-01",
            "location": "[resourceGroup().location]",
            "sku": {
                "name": "Standard_LRS"
            },
            "kind": "Storage",
            "properties": {
                "networkAcls": {
                    "bypass": "AzureServices",
                    "virtualNetworkRules": [
                    ],
                    "ipRules": [
                        {
                            "value": "[parameters('whitelistIp')]",
                            "action": "Allow"
                        }
                    ],
                    "defaultAction": "Deny"
                }
            }
        }
    ]
}
```

Jdeme do finále - stáhneme data a nahrajeme je do storage. Tady jsem musel použít dvě pomůcky. Tou první je, že storage account mám za firewallem a má whitelist jen na on-prem adresu, ne na to, co náhodně dostane kontejner ve skriptu. Ten ale má Azure CLI i potřebná práva, takže na začátku skriptu si firewall otevřu a na konci zase zavřu (technika, kterou můžete použít třeba v CI/CD pipeline, když potřebujete něco provést z agenta hostovaného Microsoftem jako v případě Azure DevOps Pipelines nebo GitHub Actions a nechce se vám starat se o vlastního agenta ve VNETu). S tím souvisí to, že pár vteřin trvá, než se změna aplikuje, takže následující příkazy jsem musel obalit do retry logiky.

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "identityName": {
            "type": "string"
        },
        "storageAccountName": {
            "type": "string"
        }
    },
    "variables": {},
    "resources": [
        {
            "type": "Microsoft.Resources/deploymentScripts",
            "name": "uploadData",
            "apiVersion": "2019-10-01-preview",
            "location": "[resourceGroup().location]",
            "kind": "AzureCLI",
            "identity": {
                "type": "UserAssigned",
                "userAssignedIdentities": {
                    "[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', parameters('identityName'))]": {
                    }
                }
            },
            "properties": {
                "forceUpdateTag": "1",
                "AzCliVersion": "2.0.80",
                "timeout": "PT10M",
                "arguments": "http://opendata.iprpraha.cz/CUR/ZPK/ZPK_O_Kont_TOitem_b/S_JTSK/ZPK_O_Kont_TOitem_b.json",
                "environmentVariables": [
                    {
                        "name": "AZURE_STORAGE_ACCOUNT",
                        "value": "[parameters('storageAccountName')]"
                    },
                    {
                        "name": "AZURE_RESOURCE_GROUP",
                        "value": "[resourceGroup().name]"
                    },
                    {
                        "name": "AZURE_STORAGE_KEY",
                        "value": "[listKeys(resourceId('Microsoft.Storage/storageAccounts', parameters('storageAccountName')), '2017-06-01').keys[0].value]"
                    }
                ],
                "scriptContent": "wget $1 -O data.json; 
                                    az storage account update -g $AZURE_RESOURCE_GROUP -n $AZURE_STORAGE_ACCOUNT --default-action Allow;
                                    n=0; until [ $n -ge 10 ]
                                    do az storage container create -n mojedata 2>&1 && break;
                                    n=$((n+1)); sleep 10;
                                    done;
                                    n=0; until [ $n -ge 10 ]
                                    do az storage blob upload -f ./data.json -c mojedata -n data.json 2>&1 && break;
                                    n=$((n+1)); sleep 10;
                                    done;
                                    az storage account update -g $AZURE_RESOURCE_GROUP -n $AZURE_STORAGE_ACCOUNT --default-action Deny;",
                "cleanupPreference": "OnSuccess",
                "retentionInterval": "P1D"
            }
        }
    ]
}
```

## Praktické nasazení a jak to funguje
Deployment skripty pod kapotou používají Azure Container Instances, které se dle vašeho nastavení po úspěšném provedení zase smažou (i pokud ne, tak stačí, že doběhnou, abyste přestali platit). 

![](/images/2020/2020-05-24-20-24-54.png){:class="img-fluid"}

![](/images/2020/2020-05-24-20-25-49.png){:class="img-fluid"}

Master šablona provola všechny linkované.

![](/images/2020/2020-06-01-06-34-28.png){:class="img-fluid"}

Skripty vidíme jako resource.

![](/images/2020/2020-06-01-06-31-22.png){:class="img-fluid"}

V logu vidíme, že předávání argumentů i proměnných prostředí funguje. Ve skriptu jsem si také vypsal výsledný JSON, abych viděl, jak výstup vypadá.

![](/images/2020/2020-06-01-06-32-37.png){:class="img-fluid"}

ARM mu porozuměl, vidím ho v seznamu výstupů skriptu.

![](/images/2020/2020-06-01-06-33-11.png){:class="img-fluid"}

A rovněž ve výstupu této linkované šablony.

![](/images/2020/2020-06-01-06-33-47.png){:class="img-fluid"}

Následně proběhl skript uploadující data a ty také nacházím ve storage accountu.

![](/images/2020/2020-06-01-06-36-17.png){:class="img-fluid"}


Potřebujete při budování své infrastruktury s ARM řešit věci, které tam principiálně nejdou jako je kontaktovat nějaké API pro zjištění informací nebo operace na úrovni data plane typu nahrání dat do databáze? Řešil bych orchestrátorem, který bude tahat za ARM šablony i další nástroje pro další úkony ať je to build aplikace, kontejneru, spuštění testů nebo infrastrukturní věci typu získání informací z jiného systému nebo nahrání testovacích dat. Takovým řešením může být Azure DevOps Pipelines nebo GitHub Actions. Pokud ale potřebujete nebo preferujete vyřešit to celé ze samotného ARMu, nové ARM deployment scripts si s tím poradí. Vyzkoušejte si.