---
layout: post
published: true
title: Jak na Terraform pro Azure služby, které jsou zatím jen v Preview
tags:
- Automatizace
---
Terraform je skvělý a už samotný provider přidává určitou míru abstrakce nad běžné Azure API. To je někdy dobré, ale jindy zase ne - zejména, když díky tomu nemůžete nasadit novou funkci, která v providerovi Terraformu ještě není podporovaná. Jak se s takovou situací vypořádat? Jak kombinovat azurerm (provider s "přidanou hodnotou") a azapi (provider jako tenká vrstva přímo nad aktuálním API)? Jak postupuji já?

# Terraform azurerm, přidaná hodnota vs. podpora nejnovějších výstřelků Azure
Aktuálně je to dost ruční práce. Pokud se objeví nová verze API Azure (například nějaká nová funkce, nová služba apod.), musí se tato nejprve dostat do Go SDK a potom programátor azurerm tuto funkci přidá a to může nějakou dobu trvat. Principiálně se tak nikdy nestává pro preview funkce (proč pracovat na něčem, co se při GA může ještě změnit) a občas i pro běžně dostupné funkce musíte pár měsíců čekat. Zdá se, že podle posledního oznámení projektu Pandora se Hashicorp ve spolupráci s Microsoftem pouští do automatizovanějšího generování zdrojů z API specifikací, takže se vývoj možná zrychlí nebo se objeví něco jako varianta "resource s méně přidané hodnoty" - ještě nevím. Každopádně to zní trochu podobně jako provider AzApi a třeba to bude něco na půl cesty mezi těmito světy. AzApi je nadstavbou přímo nad Azure API, takže v něm jde úplně cokoli... ale není tam taková abstrakce, což někdy může přidělat práci. Předesílám, že stejnou cestou se vydala i konkurence Hashicorpu - Pulumi už dokonce jednoznačně preferuje generovanou variantu a o klasicky psané (Azure Classic provider) prohlašuje, že je na zrušení, Crossplane do jisté míry taky.

Chcete nějaký konkrétní příklad té přidané hodnoty? Vezměte si zdroje, které se vytvoří a následně k nim existuje nějaký klíč, který vznikne na straně Azure - třeba storage key, admin account v AKS a tak podobně. API vytvářející resource vám takové citlivé údaje nevrátí (kvůli RBAC). Je na to jiné API volání (jiný RBAC). Azurerm provider vás ale od toho nádherně odstíní - tyto další údaje vám dá dostupné jako referenci (resource azurerm_storage_account má atribut primary_access_key). 

Chcete další příklad? Když vytváříte Private Endpoint v Azure, tak k němu typicky chcete i zařídit, aby si resource automaticky řídil záznam v privátní DNS zóně, což se děje objektem DNS zone group. Azurerm vám to zjednoduší - přímo na resource private endpointu je blok private_dns_zone_group. V API nebo přes Bicep byste museli dělat další objekt (DNSZoneGroup). Někdy používá azurerm i trochu jiné pojmenování atributů, což většinou vede k lepší přehlednosti (ale někdy zas naopak vznikne zajímavé peklo, když v API se to jmenuje nějak, v Terraformu jinak a na tlačítku v portálu ještě jinak ... třeba u jednoho přepínače ve Virtual WAN na routovací tabulce).

Ostatně v mém dnešním příkladu to bude myslím pěkně vidět.

# Preview služba a jak postupovat
Chtěl jsem přes Terraform nasadit demo pro novou věc v preview - použití workload federated identity v AKS. Na webu je návod jak na to využívající CLI (typické pro preview - Bicep/ARM/AzApi je a referenční dokumentace k nim taky, ale nějaký pěkný příklad či návod ne a v GUI to ještě není).

## Feature registrace
První co je potřeba zařídit je registrace preview feature pro mou subskripci. To lze spravovat v Terraformu, ale mně se to moc nelíbí. Musíte použít resource azurerm_resource_provider_registration a dát skip automatické registrace v azurerm, čímž můžete řídit specifické preview feature. Jenže ty jsou řízeny na úrovni celé subskripce a v rámci resource manager cesty. Tzn. celý Azure Resource Manager provider musí žít v Terraformu - napříč projekty, napříč preview a to mi přišlo hodně kostrbaté. Za sebe doporučuji - je to jednorázová operace jen pro preview věci, navrhuji provést mimo Terraform třeba v CLI.

## Kde vzít tělo volání
Datový model API je dobře zdokumentovaný a obsahuje přímo snippety pro Terraform AzApi: [https://learn.microsoft.com/en-us/azure/templates/](https://learn.microsoft.com/en-us/azure/templates/). Já v tomto případě spíše využiju toho, že dokumentace této novinky [https://learn.microsoft.com/en-us/azure/aks/learn/tutorial-kubernetes-workload-identity](https://learn.microsoft.com/en-us/azure/aks/learn/tutorial-kubernetes-workload-identity) využívá preview extension do Azure CLI. Rád tedy odposlouchávám - zapnu debug a podívám se co přesně CLI volá. V Linux to chytám do souboru ale pozor, debug jde do stderr (ne stdout), tak ať to přesměrujete správně (2> tzn. 1 je stdout a to je by default a číslicí 2 říkám, že chci do souboru i stderr).

```bash
az aks create -g myResourceGroup \
    -n myAKSCluster \
    --node-count 1 \
    --enable-oidc-issuer \
    --enable-workload-identity \
    --generate-ssh-keys \
    --debug 2> debug.log
```

Tím jsem dostal co potřebuji a můžu vykrást. V AzApi zdroji se zadává parent_id, což v mém případě je resource group (do ní se AKS nasazuje).

```
resource "azapi_resource" "aks" {
  type      = "Microsoft.ContainerService/managedClusters@2022-07-02-preview"
  name      = "d-aks-federated-identity"
  location  = azurerm_resource_group.main.location
  parent_id = azurerm_resource_group.main.id
  identity {
    type         = "SystemAssigned"
    identity_ids = []
  }
  body = jsonencode({
    properties = {
      addonProfiles = {}
      agentPoolProfiles = [
        {
          count               = 1
          name                = "default"
          orchestratorVersion = "1.23.8"
          osDiskSizeGB        = 128
          osDiskType          = "Managed"
          osSKU               = "Ubuntu"
          osType              = "Linux"
          type                = "VirtualMachineScaleSets"
          vmSize              = "Standard_B2ms"
          mode                = "System"
        }
      ]
      dnsPrefix               = "d-aks-federated-identity"
      enablePodSecurityPolicy = false
      enableRBAC              = true
      kubernetesVersion       = "1.23.8"
      networkProfile = {
        dnsServiceIP     = "10.0.0.10"
        dockerBridgeCidr = "172.17.0.1/16"
        loadBalancerProfile = {
          managedOutboundIPs = {
            count = 1
          }
        }
        loadBalancerSku = "Standard"
        networkPlugin   = "kubenet"
        outboundType    = "loadBalancer"
        podCidrs = [
          "10.244.0.0/16"
        ]
        serviceCidrs = [
          "10.0.0.0/16"
        ]
      }
      nodeResourceGroup = "MC_d-aks-federated-identity"
      oidcIssuerProfile = { # Here we enable OpenID Connect
        enabled = true
      }
      securityProfile = {
        workloadIdentity = {
          enabled = true # Here we enable workload identity ("helpers" so platform will provide token exchange and enbale injection of metadata proxy service sidecar)
        }
      }
      storageProfile = {
        blobCSIDriver = {
          enabled = false
        }
        diskCSIDriver = {
          enabled = true
          version = "v1"
        }
        fileCSIDriver = {
          enabled = true
        }
        snapshotController = {
          enabled = true
        }
      }
    }
    sku = {
      name = "Basic"
      tier = "Free"
    }
  })

  response_export_values = [
    "properties.oidcIssuerProfile.issuerURL"
  ]
}
```

## Export výstupu
Budu potřebovat ještě jeden preview zdroj a do něj musím dosadit něco z AKS zdroje - konkrétně issuerURL. Toho jsem dosáhl výše použitým response_export_values (můžete tam dát i * a pak se vyexportuje úplně všechno, co Azure API vrátilo jako response). Jak to zpracuji? Výstup najdu jako json string na cestě ```azapi_resource.aks.output```, takže to dekóduju ```jsondecode(azapi_resource.aks.output)``` a můžu jít na konkrétní hodnotu ```jsondecode(azapi_resource.aks.output).properties.oidcIssuerProfile.issuerURL```. Celé to pak vypadá takhle:

```
resource "azapi_resource" "identity1" {
  type      = "Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2022-01-31-preview"
  name      = "aks-federated-identity"
  parent_id = azurerm_user_assigned_identity.identity1.id
  body = jsonencode({
    properties = {
      audiences = [
        "api://AzureADTokenExchange"
      ]
      issuer  = jsondecode(azapi_resource.aks.output).properties.oidcIssuerProfile.issuerURL
      subject = "system:serviceaccount:default:identity1"
    }
  })
}
```

## Volání operací a vytahávání jejich výstupu
AzApi umí jednu zajímavou věc, která v azurerm není. Dokáže zavolat libolnou API operaci. O co jde? Třeba start či stop VMka - ale opatrně s tím, imperativní věci do deklarativního konceptu nepatří. Mimo to ale jsou i operace pro privilegované věci, tedy vytažení třeba klíče či hesla. Přesně to potřebuji - musím se dostat na přihlašovací údaje do Kubernetu (certifikát a tak). Azurerm mi tohle exportuje, AzApi ale ne, protože tohle není v běžné odpovědi API (jak už jsem výše vysvětloval). Co s tím?

Takhle si zavolám operaci listClusterAdminCredential a seberu si co vrátila.

```
data "azapi_resource_action" "aks_credentials" {
  type                   = "Microsoft.ContainerService/managedClusters@2022-07-02-preview"
  resource_id            = azapi_resource.aks.id
  action                 = "listClusterAdminCredential"
  response_export_values = ["*"]
}
```

Výsledek bude zase string ```data.azapi_resource_action.aks_credentials.output``` a pojdmě ho dekódovat jako JSON a dostat se na příslušná data, což je obsah kubeconfig souboru ```jsondecode(data.azapi_resource_action.aks_credentials.output).kubeconfigs[0].value```, který je ale zakódovaný v base64. To potřebuju dekódovat - mno a protože tady ještě zdaleka nekončím udělám si z toho jako mezistupeň local proměnnou, ať ten řádek není tak dlouhý a nepřehledný.

```
locals {
  kubeconfig = base64decode(jsondecode(data.azapi_resource_action.aks_credentials.output).kubeconfigs[0].value)
}
```

Skvělé - tohle už je YAML soubor a já ho potřebuju dál parsovat. Jednoduché to bude s host položkou.

```
locals {
  kubeconfig = base64decode(jsondecode(data.azapi_resource_action.aks_credentials.output).kubeconfigs[0].value)
  host = yamldecode(local.kubeconfig).clusters[0].cluster.server
}
```

A co klíče a certifikáty? Ty tam jsou taky, jen jsou zakódované v base64, takže abych se dostal na čistý PEM (který je tedy paradoxně další vnořená base64, ale to už je jedno) tak to proženeme dekódováním. Tohle je výsledek.

```
locals {
  kubeconfig = base64decode(jsondecode(data.azapi_resource_action.aks_credentials.output).kubeconfigs[0].value)
  cluster_ca_certificate = base64decode(yamldecode(local.kubeconfig).clusters[0].cluster.certificate-authority-data)
  client_certificate = base64decode(yamldecode(local.kubeconfig).users[0].user.client-certificate-data)
  client_key = base64decode(yamldecode(local.kubeconfig).users[0].user.client-key-data)
  host = yamldecode(local.kubeconfig).clusters[0].cluster.server
}
``` 

A to pak můžu už vesele použít pro konfiguraci Kubernetes providera.

```
provider "kubernetes" {
  host                   = local.host
  client_certificate     = local.client_certificate
  client_key             = local.client_key
  cluster_ca_certificate = local.cluster_ca_certificate
}
```


Myslím, že tohle byl neobvykle složitý příklad - většinou je to všechno hrozně jednoduché. Pustím Azure CLI, vykradu co dělá a hotovo. Tady jsem musel exportovat výstupy, udělat privilegované volání na klíče a pak jsem tu měl docela dlouhý řetězec parsování. Berte to jako "worst case" scénář - a i ten je hratelný.

Používáte Terraform, ale něco vám v něm chybí? Chcete i pro preview funkce automatizovat? Kombinací "usedlých" věcí v azurerm provideru s vykrytím toho co neumí přes AzApi provider se dá dostat do cíle. A za mě docela elegantně a bez poškození deklarativních principů. Jsou nějaké jiné alternativy jak to do Terraformu narvat? Jsou, ale za mě horší:
- Zavolat ARM šablonu z Terraformu - nicméně zdroje které nasadí pak Terraform nezná. Neumí je odmazat a tak podobně, to se mi nelíbí. AzApi tohle všechno dělá správně - drží state.
- Zavolat Azure CLI z lokálního stroje přes local-exec - nedeklarativní a ještě závislé na lokálním stroji co to spouští. Občas použiji pro věci, pro které prostě a jednoduše žádný provider není (třeba nastavování dataplane Synapsu) - ale to můj dnešní příklad nebyl, to bylo normální Azure API a AzApi je tak lepší volba.
- Odstanit závislost na lokálním stroji (alternativu k local-exec) zabalením do skriptu v kontejnerovém image a spouštění jako jobu v Azure Container Instance. Může být fajn pro nějaké dataplane operace (naplnění databáze například), ale jako alternativa k chybějícímu API volání nic moc.

Jak to řešíte vy? Borci od Pulumi jsou na něco ala AzApi hodně zvyklí, kdo jede Bicep nebo API tak k tomu taky snadno najde cestu. Pokud znáte jen Terraform azurerm, je tam jisté pohodlí navíc, které je vykoupené zpožděním za vývojem v Azure a AzApi vás bude zpočátku trochu bolet. Ale filozofická - kde mají být abstrakce? V providerovi nebo v modulech? Osobně myslím, že provider má být generovaný nad API a abstrakci mají přinášet až moduly. Podobně jako u Crossplane vztah Managed Resource vs. Composite Resource, kde se řeší totéž - psaný provider-azure vs. generovaný provider-jet-azure a nebo v Pulumi ručně psaný Azure Classic vs. generovaný Azure Native (tam už jednoznačně doporučují ten generovaný).

