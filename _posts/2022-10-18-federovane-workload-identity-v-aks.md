---
layout: post
published: true
title: Federované workload identity v AKS - preview bezpečného řešení pro autentizaci služeb bez hesel
tags:
- Security
- Kubernetes
---
Federovaná identita je skvělý nový způsob bezpečného využívání služeb bez hesel. Pro prostředky běžící ve VM v Azure (a to včetně některých platformních služeb, které jsou sice v Microsoftem spravovaných VM, ale platí to pro ně taky) můžete používat Managed Identity. Nicméně ta je obtížně přenosná do jiných technologií - zejména pokud běžíte v kontejnerech nebo dokonce mimo Azure, třeba v on-premises či jiném cloudu. Pro Azure Kubernetes Service existuje Pod Identity, která zprostředkovává přístup do Managed Identity ve worker nodech, ale má potíže se škálovatelností a proto je stále a už navždy v preview. Federovaná identita je pro takové scénáře lepší varianta - flexibilní, multi-cloudová a hybridní, škálovatelná.

O použití federovaných identit už jsem psal tady: [https://www.tomaskubica.cz/post/2022/federace-kubernetes-identit-s-aad/](https://www.tomaskubica.cz/post/2022/federace-kubernetes-identit-s-aad/)

Od té doby se stalo pár příjemných věcí:
- Federace už je k dispozici nejen pro AAD Service Principal účty (které sa zakládají s právy v AAD), ale i User Managed Identity - tedy objekty řízené a zakládané v Azure, které mají AAD jako backend, ale uživatel nepotřebuje do AAD přístup. Tyto účty nemají viditelné heslo nebo certifikát a ani se tam nedá nastavit.
- Nadstavba pro AKS je k dispozici nativně - nemusí tam nic sami instalovat nebo nastavovat.
- Nově si můžete nechat pro kontejner nasadit sidecar, která přináší klasický metadata endpoint - tedy chová se vám to pak celé stejně, jako ve VM nebo App Service. Jinak řečeno všechna SDK (třeba pro SQL, storage), která podporují managed identity, chodí i v Podu s touto sidecar.

Kontext k čemu to všechno prosím hledejte v [předchozím článku](https://www.tomaskubica.cz/post/2022/federace-kubernetes-identit-s-aad/)

# Zapnutí AKS s federovanou identitou
Celý zdroj (Terraform šablony) najdete na mém [GitHubu](https://github.com/tkubica12/azure-workshops/tree/main/d-aks-federated-identity).

Nejprve si nahodím AKS, u kterého zapneme dvě preview funkce - vydávání OIDC tokenů (to je standardní vlastnost Kubernetu) a specificky workload identitu (to je jakési rozšíření pro Azure).

```
oidcIssuerProfile = {
    enabled = true
}
securityProfile = {
    workloadIdentity = {
        enabled = true
    }
}
```

To je co se AKS týče všechno - krásně jednoduché.

Dál si připravím User Managed Identitu, dám jí RBAC na to co potřebuji a zapnu federaci. Managed identita je to naprosto standardní a její RBAC na přístup k datům ve storage rovněž.

```
// User managed identity
resource "azurerm_user_assigned_identity" "identity1" {
  name                = "identity1"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

resource "azurerm_role_assignment" "main" {
  role_definition_name = "Storage Blob Data Reader"
  scope                = azurerm_storage_account.main.id
  principal_id         = azurerm_user_assigned_identity.identity1.principal_id
}
```

Pro zapnutí federace použiji AzApi providera (AzureRm to zatím nenabízí) - případně Bicep, API či CLI. Čeho si všímat? Audience je api://AzureADTokenExchange, tedy je to určené pro výměnu tokenu třetí strany za token AAD (tohle je stejné třeba i pro GitHub integraci apod.). Issuer, tedy vydavatel tokenu, je tohle moje konkrétní AKS a jeho unikátní issuerURL. Subject je důležitý - je to svázání na konkrétní Kubernetes identitu, čili Service Account (v mém případě se jmenuje identity1 a je v namespace default).

```

// Federation with my AKS
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

To je za Azure všechno - teď ještě vytvořit tento Service Account jako objekt v Kubernetu. Může to být samozřejmě přes kubectl, Kustomize, Helm (ideálně přes GitOps s Flux v2 nebo ArgoCD) - v mém případě, pro mě dost netradičně, přestože nejsem toho velkým příznivcem, to tam vysmahnu přímo Terraformem. Všimněte si dvou věcí. Anotace odkazuje na ClientID mé Managed Identity a label signalizuje, že chci využít workload identity nadstavbu (aby pro mě připravila token a nemusel jsem všechno dělat ručně).

```
// Kubernetes account mapped to user managed identity
resource "kubernetes_service_account" "identity1" {
  metadata {
    name      = "identity1"
    namespace = "default"

    annotations = {
      "azure.workload.identity/client-id" = azurerm_user_assigned_identity.identity1.client_id
    }

    labels = {
      "azure.workload.identity/use" = "true"
    }
  }
}
```

Skvělé - teď už to jen použít.

# Použití federované identity z kontejneru
Nasaďme si jednoduchoučký Pod na hraní - dnes použiji nahození Kubernetes objektu Terraformem. Zajímavé jsou jen dvě věci. Všimněte si přiřazeného Service Account - tedy tomuto Podu dávám specifickou Kubernetí identitu (mno a jasně - to je ta, co je provázaná s Managed Identitou). Je z toho zřejmé, že můžu jednu provázanou identitu použít u víc kontejnerů v tomto namespace, ale taky klidně může mít každý Pod svou vlastní. Druhá věc jsou anotace, kterými (a není to pro funkčnost nutné) nechávám ke kontejneru přihodit ještě sidecar, která bude simulovat tradiční metadata endpoint tak, aby fungovala klasická SDK.

```
resource "kubernetes_pod" "main" {
  metadata {
    name = "client"

    annotations = {
      "azure.workload.identity/inject-proxy-sidecar" = "true"
      "azure.workload.identity/proxy-sidecar-port"   = "8080"
    }
  }

  spec {
    service_account_name = kubernetes_service_account.identity1.metadata[0].name

    container {
      image = "nginx:latest"
      name  = "client"
    }
  }
}
```

Dobrá tedy, Pod jede. Skočím dovnitř a mezi env najdu něco zajímavého.

```bash
AZURE_TENANT_ID=d6af5f85-2a50-4370-b4b5-9b9a55bcb0dc
AZURE_FEDERATED_TOKEN_FILE=/var/run/secrets/azure/tokens/azure-identity-token
AZURE_AUTHORITY_HOST=https://login.microsoftonline.com/
AZURE_CLIENT_ID=4b9a2ebe-21b3-45c8-b496-645579fb4a6d
```

Jde o Kubernetes token připravený k výměně (audience je tedy api://AzureADTokenExchange) a další údaje, které k výměně potřebuji (URL na AAD, client ID a tenant ID). Když do souboru s tokenem podívám a rozkóduji ho, tak vypadá takhle.

```json
{
  "aud": [
    "api://AzureADTokenExchange"
  ],
  "exp": 1665119266,
  "iat": 1665115666,
  "iss": "https://westeurope.oic.prod-aks.azure.com/d6af5f85-2a50-4370-b4b5-9b9a55bcb0dc/83300708-be1e-4990-87f8-a9f61c9c23de/",
  "kubernetes.io": {
    "namespace": "default",
    "pod": {
      "name": "client",
      "uid": "fc8f0666-f5b4-4288-98f4-aeca90793eba"
    },
    "serviceaccount": {
      "name": "identity1",
      "uid": "96077ed0-4ab7-43a6-9694-156583a3188b"
    }
  },
  "nbf": 1665115666,
  "sub": "system:serviceaccount:default:identity1"
}
```

Můžeme tedy přistoupit k jeho výměně za AAD token, s kterým pak můžeme vyrazit za službou - v mém případě do Blob storage.

Takhle si u AAD vyměním token. Všimněte si, že jako scope mám storage.azure.com (to je služba, pro kterou token chci vystavit). Stejně tak může být jako scope management.azure.com (když chci na Azure API), ale i Key Vault, Azure SQL, Azure Database for PostgreSQL, CosmosDB a tak podobně.

```bash
apt update
apt install jq -y

scope="https://storage.azure.com/.default"
output=$(curl -X POST \
    "https://login.microsoftonline.com/$AZURE_TENANT_ID/oauth2/v2.0/token" \
    -d "scope=$scope&client_id=$AZURE_CLIENT_ID&client_assertion=$(cat $AZURE_FEDERATED_TOKEN_FILE)&grant_type=client_credentials&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer")

token=$(echo $output | jq -r .access_token)
```

S AAD tokenem už pak vesele pro obsah Blobu.

```bash
# Use token to access file on storage
export BLOB_URL="https://wjqnugbhtdxymeaf.blob.core.windows.net/container/file.txt"
curl -H "Authorization: Bearer $token" \
     -H "x-ms-version: 2020-04-08" \
    $BLOB_URL
```

Tohle tedy byla jakási ruční cesta - výmenu tokenu si zařídím já sám. Nicméně pokud mám hotovu aplikaci, kde využívám SDK s podporou metadata endpointu (třeba SQL SDK apod.), tak to očekává, že si token vyzvedne z metadata endpointu tak, jako u Managed Identity ve VM. Díky anotaci jsem si nechala nasadit ke svému kontejneru sidecar, která zachytává provoz na magickou adresu 169.254.169.254 a zachová se tak jak potřebuji - kód tedy bude spokojen.

```bash
export STORAGE_ACCOUNT_URL="https://wjqnugbhtdxymeaf.blob.core.windows.net"
token2=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/identity/oauth2/token?resource=$STORAGE_ACCOUNT_URL&client_id=$AZURE_CLIENT_ID" | jq -r '.access_token')
```

A teď je to stejné - s tokenem vesele ke službě.

```bash
# Use token to access file on storage
export BLOB_URL="https://wjqnugbhtdxymeaf.blob.core.windows.net/container/file.txt"
curl -H "Authorization: Bearer $token2" \
     -H "x-ms-version: 2020-04-08" \
    $BLOB_URL
```

Krásně funguje.


Zbavte se hesel a klíčů, používejte managed identitu a pokud možno už přecházejte na tu federovanou. Je sice v preview, ale na rozdíl od pod identity se z něj za čas dostane do GA. Funguje skvěle, je bezpečná, škálovatelná a hlavně není jen pro AKS - předpokládám, že bude i součástí Azure Arc for Containers (pro Kubernety v onprem a jiných cloudech) a technologicky ji dáte i bez Arcu na libovolný Kubernetes s OIDC providerem. V zásadě tedy jakýkoli přístupný OIDC provider se tak může stát zdrojem ověření pro vaše federované identity - Kubernetes, GitHub nebo klidně Google.