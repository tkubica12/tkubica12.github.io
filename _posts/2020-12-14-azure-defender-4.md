---
layout: post
published: true
title: "Azure Defender (4): Použití Azure Policy pro vynucení pravidel i vlastní bezpečnostní kontroly"
tags:
- Security
---
Azure Policy jsou velmi důležitým nástrojem pro Policy as Code v Azure a jsou pod kapotou Azure Security Center, ale používají se samostatně pro implementaci provozních politik nebo jako součást Azure Blueprint či v rámci DevSecOps. Dnes si vyzkoušíme pár jednoduchých politik a následně z nich poskládáme vlastní pravidla kontrolovaná v rámci Azure Security Center.

Jakých prostředků se Azure Policy může týkat?
- **Azure prostředí** - stav a nastavení jednotlivých zdrojů ať už jde o IaaS či PaaS.
- **Guest configuration v Azure i mimo něj (přes Arc)** - co je ve Windows nebo Linux nainstalováno, jak je OS nastaven apod. Tyto prostředky zatím podporují pouze auditní režim (nevynucují, ale sledují compliance).
- **Kubernetes politiky v Azure i mimo něj (přes Arc)** - AKS nebo jiný Kubernetes cluster napojený do Azure přes Arc získají nativní komponenty (OPA a Gatekeepeer), které jsou ovládané z Azure Policy a vztahují se na kontejnerové prostředí jako takové.

Při definici politiky se určí za jakých okolností se má provést a to se dělá pohledem do atributů zdroje. Na rozdíl od RBAC tedy granularita není v nějakých právech, ale v atributech zdroje. Tzn. právo vytvořit VM buď mám a nebo nemám a tím to končí. Ale zakázat vytváření VM s image Windows, VM běžící v USA nebo VM bez nastavení zálohování můžu v politice. Politika tedy nejprve definuje za jakých okolností se aplikuje a to je typicky dáno pohledem do atributů (typ je VM a políčko region obsahuje USA) a scope jejího přiřazení:
- **Tenant root** - politika je platná pro všechny zdroje tenantu
- **Management Group** - politika je platná pro management group, tedy pro všechny další vnořené management group a jejich subskripce
- **Subscription** - politika je platná pro konkrétní subskripci
- **Resource Group** - politika se vztahuje pouze na konkrétní resource group

V rámci scope je možné dělat výjimky (celá subskripce kromě resource group networking-rg apod.).

Pak už se dostává ke slovu akce - co se má stát, pokud zdroj splňuje výše uvedené podmínky. Každý požadavek, který dorazí na management API (je tedy jedno, zda zdroj vytváříte z portálu, CLI, ARM šablony nebo Terraform) je vůči politikám vyhodnocován v následujícím pořadí:
1. **Disabled** - pokud politika sice sedí na volání, ale je ve stavu disabled, dál už se jí nebudeme zabývat.
2. **Append nebo Modify** - politika může být Append a pak je jejím úkolem přidat nějaké klíče s hodnotami do volání, například vsunout seznam povolených zdrojových IP adres do platformní služby. Modify slouží k modifikaci hodnoty existujícího klíče, například zapnutí šifrování databáze nebo storage accountu. 
3. **Deny** - takový požadavek bude odmítnut. Deny akce je až po append a modify, protože tyto předchozí akce mohou požadavek změnit způsobem, který způsobí, že nevyhovují firemním požadavkům.
4. **Audit** - tato akce jednoduše zanese zdroj jako non-compliant. Proč je až po Deny? Nechcete mít hlášku dvakrát - jednou pro audit a následně pro odmítnutí, takže pořadí Deny a pak až Audit dává větší smysl. Časté nasazení je použití Audit na začátku, kdy ještě nevíte kudy přesně do toho a zejména pokud jde o už existující prostředí. Může jít o něco, kde nemáte problém udělit výjimku, ale chcete o těch situacích vědět - dost možná těchto auditních zkušeností využít v produkci pro přísnější Deny pravidla.
5. **AuditIfNotExists** - tato akce přichází ke slovu až po té, co je požadavek přijat a zpracovává se. Umožňuje provést audit jiného zdroje, než který vytváříte. Zdroje, který s ním souvisí a dává smysl ho kontrolovat. Typickým příkladem match části by byla VM a vy se chcete ujistit, že je u každé VM použita VM Extension třeba na nalodění do Azure Monitor. VM Extension je samostatný resource (v tomto případě subresource) a nemusí (nebo nemůže) být součástí původního requestu, na který reagujeme. 
6. **DeployIfNotExists** - stejně jako v předchozím případě je tento efekt spuštěn teprve po úspěšném přijetí požadavku. Slouží k tomu, aby bylo možné na základě původního requestu nasadit i jiné zdroje. Představme si třeba, že v produkční subskripci vyžadujete použití Private Endpoint pro storage account. Politika může reagovat (match) na vytváření storage accountu, ale nasazení privátního endpointu znamená vytvoření Private Link zdroje a zavedení záznamu do DNS zóny. To jsou dva úplně jiné zdroje - tam se modifikacemi requestu nikam nedostaneme. Tato politika zareaguje zhruba 15 po přijetí požadavku a nasadí ARM šablonu, která je součástí politiky. Tak se dá aktivovat Private Endpoint automaticky aniž by to uživatel udělal. Stejným způsobem funguje automatické nalodění VM do Azure Defender - je to politika, která čeká na request pro vytvoření VM a sama vytvoří zdroje VM Extension pro instalaci agentů.

# Prevence s jednoduchou Deny politikou
Jako příklad si vyzkoušíme jednoduchou Deny politiku omezující použitelné regiony například z důvodu compliance.

Založíme si pro účely zkoušení dvě resource group.

```bash
az group create -n policy -l westeurope
az group create -n nopolicy -l westeurope
```

Azure Policy přicházejí s obrovským seznamem připravených politik, takže nemusím pro tyto časté požadavky psát svoje vlastní definice - ale není to nic složitého, občas se hodí to umět. Každopádně já zvolil hotovou definici Allowed locations.

[![](/images/2020/2020-12-03-15-06-55.png){:class="img-fluid"}](/images/2020/2020-12-03-15-06-55.png)

Definice odpovídá mému zevrubnému popisu výše - nejdřív je match (kdy má zareagovat). V našem případě pro requesty vytvářející zdroj jakéhokoli typu (nemáme tady match na políčko type, které je častou součástí politik - ale ne v tomto případě), jejichž políčko location není ze seznamu povolených. Tento seznam je vyřešen jako parametr. To je velmi praktické - definice politiky Allowed locations tak nemá natvrdo nastavené regiony a je tedy univerzální - teprve při její aplikaci na nějaký scope tyto hodnoty vyplníme. V druhé část je efekt a to bude Deny.

Politiku teď přiřadím na nějaký scope. V mém prostředí nemám právo přiřadit na celý tenant nebo Management Group, ale je to samozřejmě možné. Můžu jít níž na úroveň subskripce a dokonce i Resource Group. Kromě toho lze udělat výjimky typu celá subskripce kromě resource group XY.

[![](/images/2020/2020-12-03-15-07-56.png){:class="img-fluid"}](/images/2020/2020-12-03-15-07-56.png)

Teď přijde na řadu vyplnit parametry politiky, v tomto případě seznam regionů, kde zvolím pouze West Europe.

[![](/images/2020/2020-12-03-15-08-16.png){:class="img-fluid"}](/images/2020/2020-12-03-15-08-16.png)

Následně můžu zkusit vytvořit storage v USA v resource group policy a nopolicy. Ta v resource group policy dle očekávání selže.

[![](/images/2020/2020-12-03-15-10-57.png){:class="img-fluid"}](/images/2020/2020-12-03-15-10-57.png)

[![](/images/2020/2020-12-03-15-11-42.png){:class="img-fluid"}](/images/2020/2020-12-03-15-11-42.png)

Krátká hláška v portálu není příliš detailní, připravte uživatele na to, že je vždy dobré se podívat do detailů zprávy. Z té vypadne JSON s velmi konkrétními detaily - důvodem selhání je zákaz politikou, vidíme konkrétní assignment, co se kontrolovalo, co se jako hodnota očekávalo vs. co tam bylo. Na tomto místě jedno doporučení - pro assignment dáváte jeho jméno. Pojmenování definice politiky by mělo vystihovat co dělá (v našem případě Allowed Locations je určitě fajn), ale pro název assignmentu (tady je vidět jako atribut policyAssignmentDisplayName) bych doporučoval doplnit detailnější popis/důvod. Tak například v tomto případě by se assignment mohl jmenovat třeba "Allow West Europe only in production environments".

```json
{
    "status": "Failed",
    "error": {
        "code": "RequestDisallowedByPolicy",
        "target": "mojesuperstoragevus",
        "message": "Resource 'mojesuperstoragevus' was disallowed by policy. Policy identifiers: '[{\"policyAssignment\":{\"name\":\"Allowed locations\",\"id\":\"/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/policy/providers/Microsoft.Authorization/policyAssignments/6d22f71752114caabadf0a24\"},\"policyDefinition\":{\"name\":\"Allowed locations\",\"id\":\"/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c\"}}]'.",
        "additionalInfo": [
            {
                "type": "PolicyViolation",
                "info": {
                    "policyDefinitionDisplayName": "Allowed locations",
                    "evaluationDetails": {
                        "evaluatedExpressions": [
                            {
                                "result": "True",
                                "expressionKind": "Field",
                                "expression": "location",
                                "path": "location",
                                "expressionValue": "westus",
                                "targetValue": [
                                    "westeurope"
                                ],
                                "operator": "NotIn"
                            },
                            {
                                "result": "True",
                                "expressionKind": "Field",
                                "expression": "location",
                                "path": "location",
                                "expressionValue": "westus",
                                "targetValue": "global",
                                "operator": "NotEquals"
                            },
                            {
                                "result": "True",
                                "expressionKind": "Field",
                                "expression": "type",
                                "path": "type",
                                "expressionValue": "Microsoft.Storage/storageAccounts",
                                "targetValue": "Microsoft.AzureActiveDirectory/b2cDirectories",
                                "operator": "NotEquals"
                            }
                        ]
                    },
                    "policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c",
                    "policyDefinitionName": "e56962a6-4747-49cd-b67b-bf8b01975c4c",
                    "policyDefinitionEffect": "deny",
                    "policyAssignmentId": "/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/policy/providers/Microsoft.Authorization/policyAssignments/6d22f71752114caabadf0a24",
                    "policyAssignmentName": "6d22f71752114caabadf0a24",
                    "policyAssignmentDisplayName": "Allowed locations",
                    "policyAssignmentScope": "/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/policy",
                    "policyAssignmentParameters": {
                        "listOfAllowedLocations": {
                            "value": [
                                "westeurope"
                            ]
                        }
                    }
                }
            }
        ]
    }
}
```

Takhle jsme si vyzkoušeli preventivní politiku - některé věci jsou prostě zakázané a nelze je obejít.

# Použití politiky pro uvedení prostředí do požadovaného stavu
Vyzkoušejme si hezký příklad využití efektu DeployIfNotExists pro zapnutí diagnostických logů u Azure Key Vault. Je určitě dobrá praxe vyzvedávání klíčů, hesel a certifikátů z trezoru detailně logovat pro forenzní účely. Představme si, že toto chceme vynucovat. Tohle ale nezmůžeme jednoduchou append nebo modify politikou, protože to není obyčejný atribut zdroje Key Vault, ale separátní resource v Azure.

Najděte si politiku Deploy Diagnostic Settings for Key Vault to Log Analytics workspace.

[![](/images/2020/2020-12-03-15-16-34.png){:class="img-fluid"}](/images/2020/2020-12-03-15-16-34.png)

Takhle vypadá celý JSON. Uvádím proto, abychom si prohlédli strukturu a uvidíte, že to není nějak extrémně složité a politiky můžete vytvářet vlastní nebo stávající modifikovat. Na co se zaměřit?
- Všimněte si, že efekt je řešený jako parametr. To je myslím velmi praktické, protože v rámci assignmentu můžete parametrem politiku deaktivovat. Možná si říkáte, že to ji ani nemusím aplikovat, tak proč to řešit. Finta je v tom, že typicky neděláte politiky po jednom, ale spojíte je do celku jako iniciativu. Místo přidávání politik po jednom nebo vytváření nové iniciativy pro každou subskripci podle toho které politiky ze seznamu chci mít aktivní můžete takhle mít jednotnou iniciativu a při assignmentu pěkně parametrem povypínat co potřebujete. Možná vzpomínáte, že přesně tohle jsme v předchozích dílech udělali pro iniciativu Azure Security Center.
- Match se chytá na Key Vault a zjišťuje, jestli vnořený zdroj (diagnostické logování) je zapnutý.
- Následně je v těle politiky ARM šablona, která provede příslušná nastavení.

```json
{
  "properties": {
    "displayName": "Deploy Diagnostic Settings for Key Vault to Log Analytics workspace",
    "policyType": "BuiltIn",
    "mode": "Indexed",
    "description": "Deploys the diagnostic settings for Key Vault to stream to a regional Log Analytics workspace when any Key Vault which is missing this diagnostic settings is created or updated.",
    "metadata": {
      "version": "1.0.0",
      "category": "Monitoring"
    },
    "parameters": {
      "effect": {
        "type": "String",
        "metadata": {
          "displayName": "Effect",
          "description": "Enable or disable the execution of the policy"
        },
        "allowedValues": [
          "DeployIfNotExists",
          "Disabled"
        ],
        "defaultValue": "DeployIfNotExists"
      },
      "profileName": {
        "type": "String",
        "metadata": {
          "displayName": "Profile name",
          "description": "The diagnostic settings profile name"
        },
        "defaultValue": "setbypolicy_logAnalytics"
      },
      "logAnalytics": {
        "type": "String",
        "metadata": {
          "displayName": "Log Analytics workspace",
          "description": "Select Log Analytics workspace from dropdown list. If this workspace is outside of the scope of the assignment you must manually grant 'Log Analytics Contributor' permissions (or similar) to the policy assignment's principal ID.",
          "strongType": "omsWorkspace",
          "assignPermissions": true
        }
      },
      "metricsEnabled": {
        "type": "String",
        "metadata": {
          "displayName": "Enable metrics",
          "description": "Whether to enable metrics stream to the Log Analytics workspace - True or False"
        },
        "allowedValues": [
          "True",
          "False"
        ],
        "defaultValue": "False"
      },
      "logsEnabled": {
        "type": "String",
        "metadata": {
          "displayName": "Enable logs",
          "description": "Whether to enable logs stream to the Log Analytics workspace - True or False"
        },
        "allowedValues": [
          "True",
          "False"
        ],
        "defaultValue": "True"
      }
    },
    "policyRule": {
      "if": {
        "field": "type",
        "equals": "Microsoft.KeyVault/vaults"
      },
      "then": {
        "effect": "[parameters('effect')]",
        "details": {
          "type": "Microsoft.Insights/diagnosticSettings",
          "name": "[parameters('profileName')]",
          "existenceCondition": {
            "allOf": [
              {
                "field": "Microsoft.Insights/diagnosticSettings/logs.enabled",
                "equals": "[parameters('logsEnabled')]"
              },
              {
                "field": "Microsoft.Insights/diagnosticSettings/metrics.enabled",
                "equals": "[parameters('metricsEnabled')]"
              }
            ]
          },
          "roleDefinitionIds": [
            "/providers/microsoft.authorization/roleDefinitions/749f88d5-cbae-40b8-bcfc-e573ddc772fa",
            "/providers/microsoft.authorization/roleDefinitions/92aaf0da-9dab-42b6-94a3-d43ce8d16293"
          ],
          "deployment": {
            "properties": {
              "mode": "incremental",
              "template": {
                "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                  "resourceName": {
                    "type": "string"
                  },
                  "location": {
                    "type": "string"
                  },
                  "logAnalytics": {
                    "type": "string"
                  },
                  "metricsEnabled": {
                    "type": "string"
                  },
                  "logsEnabled": {
                    "type": "string"
                  },
                  "profileName": {
                    "type": "string"
                  }
                },
                "variables": {},
                "resources": [
                  {
                    "type": "Microsoft.KeyVault/vaults/providers/diagnosticSettings",
                    "apiVersion": "2017-05-01-preview",
                    "name": "[concat(parameters('resourceName'), '/', 'Microsoft.Insights/', parameters('profileName'))]",
                    "location": "[parameters('location')]",
                    "dependsOn": [],
                    "properties": {
                      "workspaceId": "[parameters('logAnalytics')]",
                      "metrics": [
                        {
                          "category": "AllMetrics",
                          "enabled": "[parameters('metricsEnabled')]",
                          "retentionPolicy": {
                            "enabled": false,
                            "days": 0
                          }
                        }
                      ],
                      "logs": [
                        {
                          "category": "AuditEvent",
                          "enabled": "[parameters('logsEnabled')]"
                        }
                      ]
                    }
                  }
                ],
                "outputs": {}
              },
              "parameters": {
                "location": {
                  "value": "[field('location')]"
                },
                "resourceName": {
                  "value": "[field('name')]"
                },
                "logAnalytics": {
                  "value": "[parameters('logAnalytics')]"
                },
                "metricsEnabled": {
                  "value": "[parameters('metricsEnabled')]"
                },
                "logsEnabled": {
                  "value": "[parameters('logsEnabled')]"
                },
                "profileName": {
                  "value": "[parameters('profileName')]"
                }
              }
            }
          }
        }
      }
    }
  },
  "id": "/providers/Microsoft.Authorization/policyDefinitions/bef3f64c-5290-43b7-85b0-9b254eef4c47",
  "type": "Microsoft.Authorization/policyDefinitions",
  "name": "bef3f64c-5290-43b7-85b0-9b254eef4c47"
}
```
Pojďme pokračovat v přiřazení politiky.

[![](/images/2020/2020-12-03-15-17-40.png){:class="img-fluid"}](/images/2020/2020-12-03-15-17-40.png)

Politika bude nasazovat ARM šablonu a musí mít nějaký účet, pod kterým to udělá. Tady vám Azure nabízí zařízení managed identity s least privileged RBAC.

[![](/images/2020/2020-12-03-15-18-11.png){:class="img-fluid"}](/images/2020/2020-12-03-15-18-11.png)

Nasaďme si Key Vault.

[![](/images/2020/2020-12-03-15-19-33.png){:class="img-fluid"}](/images/2020/2020-12-03-15-19-33.png)

Jak vidno, diagnostické logy nejsou zapnuté.

[![](/images/2020/2020-12-03-15-20-35.png){:class="img-fluid"}](/images/2020/2020-12-03-15-20-35.png)

Nicméně asi po deseti minutách se situace změnila.

[![](/images/2020/2020-12-03-15-30-58.png){:class="img-fluid"}](/images/2020/2020-12-03-15-30-58.png)

Důkazy činnosti politiky najdeme v Activity logu. Všimněte si, že v rámci deploymentu bylo identifikováno, že bude potřeba provést akci deployIfNotExists. To se také o pár minut později stalo a ARM šablona nastavení vytvořila. Za pozornost také stojí, že to nebylo pod mojí identitou, ale managed identitou, kterou má politika. 

[![](/images/2020/2020-12-03-15-32-34.png){:class="img-fluid"}](/images/2020/2020-12-03-15-32-34.png)

# Audit nastavení OS
Azure Policy dokáže díky agentovi pro Azure VM i VM běžící kdekoli napojeným přes Azure Arc kontrolovat i stav nastavení operačního systému. V případě Windows to dělá přes PowerShell DSC a v [dokumentaci](https://docs.microsoft.com/en-us/azure/governance/policy/how-to/guest-configuration-create-group-policy) najdete i konverzní nástroj z GPO do DSC. U Linuxu se jako kontrolní engine používá Chef InSpec a agent zajišťuje jeho konfiguraci a spouštění (pro předávání parametrů a vynucení spouštění používá DSC pro Linux).

Guest politiky si můžete připravit kompletně svoje vlastní, ale já to dnes dělat nebudu. Nicméně vše potřebné k takovému počinu najdete v [dokumentaci](https://docs.microsoft.com/en-us/azure/governance/policy/how-to/guest-configuration-create-linux)

My pro dnešek využijeme jedné z hotových politik a jen si pohrajeme s jejími parametry. Najděte si definici Audit Linux machines that don't have the specified applications installed.

[![](/images/2020/2020-12-03-20-35-27.png){:class="img-fluid"}](/images/2020/2020-12-03-20-35-27.png)

Budeme chtít auditovat všechny VM, na kterých chybí jedna zásadní, kritická a pro bezpečnost nepostradatelná aplikace - cowsay (pro Windows čtenáře co ji neznají - vtip se vysvětlí o pár řádků níže).

[![](/images/2020/2020-12-03-20-36-00.png){:class="img-fluid"}](/images/2020/2020-12-03-20-36-00.png)

Nejprve si vytvořím jednu VM bez této aplikace a použiji VM Extension pro instalaci GuestConfiguration agenta.

```bash
az vm create -n linux-vm -g policy --image UbuntuLTS --admin-username tomas
az vm extension set -g policy --vm-name linux-vm -n ConfigurationForLinux --publisher Microsoft.GuestConfiguration --version 1.9.0
```

U druhé VM se o instalaci postarám. Na to si vytvořím do souboru tento skript.

```bash
cat > script.sh << EOF
#!/bin/bash
sudo apt update
sudo apt install -y cowsay
EOF
```

Následně založím VM linux2-vm a tento skript ji poskytnu do cloud-init (custom-data), takže se po spuštění VM cowsay nainstaluje. Následně také nalodím GuestConfiguration agenta přes extension.

```bash
az vm create -n linux2-vm -g policy --image UbuntuLTS --admin-username tomas --custom-data script.sh
rm script.sh
az vm extension set -g policy --vm-name linux2-vm -n ConfigurationForLinux --publisher Microsoft.GuestConfiguration --version 1.9.0
```

Ověřme si, že cowsay tam je. Myslím, že i Windows orientování budou souhlasit, že jde o nadmíru užitečnou aplikaci.

```
tomas@linux2-vm:~$ cowsay Azure Policy je suprkůl!
 __________________________
< Azure Policy je suprkůl! >
 --------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

```

Po nějaké době se podívejme na compliance vůči politikám. Dle očekávání jedna z VM je v pohodě, druhá není.

[![](/images/2020/2020-12-08-12-51-28.png){:class="img-fluid"}](/images/2020/2020-12-08-12-51-28.png)

linux-vm nesplňuje požadavky - nemá nainstalováno cowsay.

[![](/images/2020/2020-12-08-12-52-10.png){:class="img-fluid"}](/images/2020/2020-12-08-12-52-10.png)


# Vlastní politika jako vstup do Azure Security Center
Azure Policy, kterou jsme před chvilkou viděli v akci, může být vstupem do série doporučení v rámci Azure Security Center. Funguje to tak, že soubor politik musím zařadit do iniciativy (sdružení politik) a tuto určit jako novou vlastní bezpečnostní zásadu. Pokud chceme, aby v rámci Security Center byla vidět i speciální políčka typu náročnost na vyřešení, typ útoku apod., budeme muset použít [API](https://docs.microsoft.com/en-us/rest/api/securitycenter/assessmentsmetadata/createinsubscription#examples). Pro náš příklad vystačíme bez speciálních atributů a provedeme všechno z GUI.

V Azure Security Center půjdeme do politik a vybereme subskripci.

[![](/images/2020/2020-12-11-12-09-48.png){:class="img-fluid"}](/images/2020/2020-12-11-12-09-48.png)

Kliknu na přidání vlastní iniciativy.

[![](/images/2020/2020-12-11-12-10-21.png){:class="img-fluid"}](/images/2020/2020-12-11-12-10-21.png)

Vytvořím novou.

[![](/images/2020/2020-12-11-12-10-48.png){:class="img-fluid"}](/images/2020/2020-12-11-12-10-48.png)

Přidám jedinou politiku - stejnou jako před tím.

[![](/images/2020/2020-12-11-12-12-36.png){:class="img-fluid"}](/images/2020/2020-12-11-12-12-36.png)

Přiřadíme na subskripci.

[![](/images/2020/2020-12-11-12-13-17.png){:class="img-fluid"}](/images/2020/2020-12-11-12-13-17.png)

[![](/images/2020/2020-12-11-12-14-03.png){:class="img-fluid"}](/images/2020/2020-12-11-12-14-03.png)

Tato politika je teď součástí doporučení Azure Security Center. Protože jsme nevyplnili žádná metadata, patří do custom skupiny za 0 bodů, nicméně to mi nevadí - podstatné je, že v reportu je a svítí červeně.

[![](/images/2020/2020-12-11-20-41-44.png){:class="img-fluid"}](/images/2020/2020-12-11-20-41-44.png)


Dnes jsme tedy probrali Azure Policy, které jsou pod kapotou compliance části Azure Security Center a využili je k definování vlastních pravidel. V příštím díle už se pustíme do aktivní části Azure Defender a začneme s ochranou operačních systémů (EDR apod.), sítí, později přidáme ochranu platformních služeb, začlenění do procesů včetně DevSecOps a ve finále navážeme celé řešení na Azure Sentinel, tedy SIEM/SOAR nástroj. 