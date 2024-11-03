---
layout: post
title: Federace vnitřních Kubernetes identit s Azure Active Directory pro přístup k cloudovým službám bez hesel
tags:
- Kubernetes
- Security
- AAD
---
Předávat aplikacím nějaké tajnosti jako jsou hesla nebo certifikáty je vždy docela nepohodlné, zejména, když nechcete prasit a dodržujete bezpečnostní hygienu (pravidelná rotace, nikdy neuloženo v Gitu nebo na disku, nikdy nezalogováno nebo odesláno do crash dumpu). Ve zdrojích běžících v Azure ve vašem tenantu to lze elegantně řešit přes Managed Identity (byť pro Kubernetes s některými omezeními viz dále) - žádná hesla ani certifikáty, ale můžete si vyzvednou časově omezený token. Aplikaci nemusím vůbec nic předávat a i kdyby to ta někde zalogovala, bezpečnostní dopad není tak velký, protože token má krátkou platnost (teď si nevybavuji jestli hodinu, 8 nebo 24 hodin, ale víc určitě ne) - než se k němu někdo potenciálně dostane, už dost možná neplatí (na rozdíl od situace se zalogovaným heslem k účtu, které i ti docela poctiví točí tak jednou za rok). Ale co když neběžím v Azure - například mám část aplikace v on-premise, někde blízko místa potřeby (třeba uvnitř výdejního boxu nebo na ropné plošině) nebo v jiném cloudu? Tam samozřejmě služba Managed Identity není resp. v AWS a Google je, ale samozřejmě nevydává Azure tokeny, ale AWS resp. Google, což pro autentizaci do služby typu Azure Key Vault nebo Azure SQL není k ničemu .... nebo je? Kubernetes má také vnitřního providera identit a můžete ho využít ve formě Service Accountů, ale zase - je vám to platné při ověřování vůči třeba Azure Blob Storage? Je, čtěte dál.

# Managed Identity a kdy ji používat
Fungování Managed Identity popisovat nebudu, to už jsem na tomto blogu párkrát udělal. Její použití začalo poměrně dávno pro zdroje typu VM nebo WebApp, kdy pro tento zdroj vznikla systémová identita (současně se zrodem zdroje), ale postupně se přidala user-managed identita (životní cyklus je oddělený od zdrojů a k těm je přiřazujete) a podpora se rozšířila na mnoho platofmrních služeb včetně databází (ve smyslu, že DB engine samotný se touto identitou může prokazovat například když z vnitřku databáze taháte dodatečná data z Blob storage), Data Factory, strojového učení a v neposlední řadě AKS. Velké množství platformních služeb dnes dovoluje se k nim přihlašovat AAD identitou včetně varianty Managed Identity, takže máte podporu jak na straně klientské (váš kód ve VM, v Kubernetu, WebAppce, vaše pipeliny v Datafactory nebo Synapse apod.) tak na serverové (různé databáze, fronty, storage atd.).

# Managed Identity v Azure Kubernetes Service
AKS běží nad VM a s tím je spojený jeden problém - Pody by mohly přistupovat k metadata službě nodu, ale to obvykle není co chcete - spíše potřebujete různým Podům dávat různé identity a to tak, aby se nedostaly k těm, co jim nepatří. Projekt a následně spravovaný addon do AKS AAD Pod Idenity tohle vyřešil a vystavěl uvnitř clusteru vlastní službu na metadata, které je kompatibilní s tím co dává Azure pro VM (takže nemusíte měnit kód) a nabídl ji Podům s tím, že na pozadí si o tokeny říká přes metadata službu nodu (která mimochodem z důvody kompatibility běží na stejné známé adrese 169.254.169.254, čímž se to trochu komplikuje). To funguje velmi dobře a hlavně - nemusíte měnit kód mezi tím, když běžíte v Azure Function, App Service, kontejneru v Kubernetu nebo jen tak ve VM. Nicméně metadataslužba sice podporuje i velké množství identit v jediném VM, ale není na use case s masivním počtem identit a jejich časou obměnou stavěná. Proto u velkých nodů, kde budete chtít stovky identit a pořád je přidávat a ubírat, můžete narazit na prodlevy a výkonnostní obtíže. Navíc podpora pro Windows nody je problematická (resp. není) a z logiky věci tohle nefunguje na clusterech mimo Azure, například těch připojených přes Azure Arc for Kubernetes.

# AAD workload identity federace a její scénáře
Pro vaše aplikace a skripty, které se mají ověřovat vůči zdrojům zabezpečeným přes AAD, potřebujete typicky vytvořit účet vhodný pro automatizaci (tedy například bez MFA) - Service Principal. Jde defacto o zvláštní případ Application Registration (ta může reprezentovat i multi-tenantní objekt, zatímco SP je registrace striktně single-tenant). Totéž na pozadí používá i Managed Identity, která je vlastně speciálním případ Service Principal, který má další restrikce (nemůže být použit pro autentizaci mimo Azure, například do Office365 nebo SAP, nemůžete pro něj vytvořit heslo či certifikát, protože to si spravuje Managed Identity sama za vás a nepustí vás k tomu).

Service Principal musí aplikaci ověřit a to udělá buď heslem nebo certifikátem (v případě Managed Identity takový certifikát existuje a je uvnitř služby, rotuje se každých 45 dní a vy ho neuvidíte - dostáváte jen hotové tokeny). Princip workload identity federace spočívá v tom, že by se mohl SP prokázat ne heslem nebo certifikátem, ale tokenem nějaké identitní služby (OIDC provider), kterou explicitně povolíte a to včetně toho jak má vypadat subject. Jinak řečeno místo hesla budu mít token jiného identitní providera, který si v AAD dokážu vyměnit za AAD token. Moje aplikace tedy nemá žádné heslo ani do AAD ani ke "svému" identity providerovi, ale je schopna získat od něj časově omezený token a ten následně (díky nastavené důvěře mezi konkrétním providerem, subjectem a Service Principal účtem) vyměnit za AAD token. Kdy to tedy dává smysl?
- Kubernetes má vlastního OpenID Connect providera a může vystavovat token pro jednotlivé Service Accounty, které vytvoříte, a tokeny doručit aplikaci (přes Volume). Schopnost vyměnit token pro konkrétní Service Account za AAD token pro konkrétní Service Principal nám umožní získat AAD token třeba do databáze bez jakýchkoli hesel.
- Podpobný koncept můžeme použít v GitHub Actions. Pokud nejedete self-hosted agenty (což je nepohodlné), běží tito v nějakém prostředí, ve kterém nemůžete použít Managed Identitu pro váš tenant (protože to prostě neběží u vás). Protože GitHub funguje jako OIDC provider, může vystavit tokeny pro jednotlivé repozitáře a jejich branche, takže bychom je pak mohli vyměnit za AAD token. GitHub Actions by se pak přihlásily do Azure bez hesla do Azure.
- Kdykoli máte svůj kód někde, kde je místní identitní provider schopný pro vás zajistit tokeny bez hesel a vy potřebujete odtamtud přistupovat na zdroje chráněné AAD, dává federace workload identit smysl. Může jít například o aplikací běžící v AWS, která využívá přístup do Synapse v Azure.

V aktuálním preview je jedno omezení - funguje to zatím jen pro Service Principal v čisté podobě, zatím ne pro Managed Identity. Vytvoříte tedy SP v AAD, dáte mu práva dle svých potřeb (do subskripce, do SQL databáze, do Azure Key Vault apod.) a to federujete s OIDC providerem. Nemůžete ale udělat Managed Identitu a tu federovat s OIDC providerem (zatím), což pro scénáře mimo Azure asi není tak zásadní přínos, ale je pro použití tohoto přístupu jako náhradu AAD Pod Identity v AKS a rozšíření řešení do Arc for Kubernetes.

# Kubernetes s federovanou workload identitou
Všechno najdete taky na mém [GitHubu](https://github.com/tkubica12/aad-workload-identity-demo)

Co použijeme? Abychom nemuseli v aplikaci řešit nějaké složitosti (například zažádat o vydání tokenu na základě Service Principal, ale pro specifickou audience pro potřeby výmeny v AAD) použijeme projekt, který to pro nás udělá a Kubernetes token v potřebném formátu nám hodí do souborového systému kontejneru. Jak už padlo aktuálně potřebujeme na straně AAD použít Service Principal, nicméně Managed Identita je na brzké roadmapě.

V rámci AKS je možnost použití OIDC providera v preview, to si musíme zaregistrovat.

```bash
az feature register --name EnableOIDCIssuerPreview --namespace Microsoft.ContainerService
az feature list -o table --query "[?contains(name, 'Microsoft.ContainerService/EnableOIDCIssuerPreview')].{Name:name,State:properties.state}"  # wait for Registered
az provider register --namespace Microsoft.ContainerService
az extension add --name aks-preview --upgrade -y
```

Vytvoříme AKS.

```bash
az group create -n aks -l westeurope
az aks create -n aks -g aks -c 1 -s Standard_B2s -x --enable-oidc-issuer
```

Založím AAD identitu (Service Principal).

```bash
az ad sp create-for-rbac --name tomas1aad
```

Vytvořím Azure Key Vault (to bude AAD autentizovaná služba, ke které budu přistupovat) a dám svému SP práva číst tajnosti.

```bash
az keyvault create -n tomas1aadkeyvault \
  -g aks \
  --enable-rbac-authorization \
  --default-action Allow

az role assignment create --role "Key Vault Secrets Officer" \
  --assignee-object-id $(az ad signed-in-user show --query objectId -otsv) \  # Myself - to be able to create secret
  --scope $(az keyvault show -n tomas1aadkeyvault -g aks --query id -otsv)

az keyvault secret set -n mysecret --vault-name tomas1aadkeyvault --value mysecretvalue

az role assignment create --role "Key Vault Secrets User" \
  --assignee-object-id $(az ad sp list --display-name tomas1aad --query [0].objectId -o tsv) \
  --scope $(az keyvault show -n tomas1aadkeyvault -g aks --query id -otsv)
```

Nainstaluji projekt, který mi usnadní získání Kubernetes tokenu vhodného pro směnu.

```bash
export AZURE_TENANT_ID="$(az account show --query tenantId -otsv)"
helm repo add azure-workload-identity https://azure.github.io/azure-workload-identity/charts
helm repo update
helm install workload-identity-webhook azure-workload-identity/workload-identity-webhook \
   --namespace azure-workload-identity-system \
   --create-namespace \
   --set azureTenantID="${AZURE_TENANT_ID}"
```

V Kubernetu vytvořím Service Account a přes anotace a label mu zapnu generování vyměnitelných tokenů.

```bash
export APPLICATION_CLIENT_ID="$(az ad sp list --display-name tomas1aad --query '[0].appId' -otsv)"
export SERVICE_ACCOUNT_ISSUER=$(az aks show -n aks -g aks --query "oidcIssuerProfile.issuerUrl" -o tsv)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: ${APPLICATION_CLIENT_ID}
  labels:
    azure.workload.identity/use: "true"
  name: tomas1kube
  namespace: default
EOF
```

Výborně. Teď u svého Service Principal (mimochodem všimněte si jeho heslo jsem si nikam nezapisoval - nepotřebuji) řeknu, že je možné se vůči němu prokázat také tokenem z mého Kubernetes clusteru (issuer) a mého konkrétního Service Accountu (subject).

```bash
export APPLICATION_CLIENT_ID="$(az ad sp list --display-name tomas1aad --query '[0].appId' -otsv)"
export APPLICATION_OBJECT_ID="$(az ad app show --id ${APPLICATION_CLIENT_ID} --query objectId -otsv)"
cat <<EOF > body.json
{
  "name": "kubernetes-federated-credential",
  "issuer": "${SERVICE_ACCOUNT_ISSUER}",
  "subject": "system:serviceaccount:default:tomas1kube",
  "description": "Kubernetes service account federated credential",
  "audiences": [
    "api://AzureADTokenExchange"
  ]
}
EOF

az rest --method POST --uri "https://graph.microsoft.com/beta/applications/${APPLICATION_OBJECT_ID}/federatedIdentityCredentials" --body @body.json
rm body.json
```

Tím máme hotovo a můžu nasadit "aplikaci".

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: testpod
  namespace: default
spec:
  serviceAccountName: tomas1kube
  containers:
    - image: ubuntu
      name: mycontainer
      command: ['tail', '-f', '/dev/null']
EOF
```

Připojím se do Podu a podívám se na dva tokeny.

```bash
kubectl exec -ti testpod -- bash
cat /var/run/secrets/kubernetes.io/serviceaccount/token
cat /var/run/secrets/tokens/azure-identity-token 
```

Ten první je standardní Kubernetes token pro vnitřní potřebu, což je vidět z jeho audience (ukazuji zde v dekódovaném stavu):

```json
{
  "aud": [
    "https://oidc.prod-aks.azure.com/25da173c-6b43-4f93-9c41-6cc688dea1ff/"
  ],
  "exp": 1676374730,
  "iat": 1644838730,
  "iss": "https://oidc.prod-aks.azure.com/25da173c-6b43-4f93-9c41-6cc688dea1ff/",
  "kubernetes.io": {
    "namespace": "default",
    "pod": {
      "name": "testpod",
      "uid": "4f5edc59-911b-4d46-a534-af1c19fb1815"
    },
    "serviceaccount": {
      "name": "tomas1kube",
      "uid": "c83f100a-1443-4bec-89ad-9d6e67e844e6"
    },
    "warnafter": 1644842337
  },
  "nbf": 1644838730,
  "sub": "system:serviceaccount:default:tomas1kube"
}
```

Ten druhý je ale specificky vystavený pro účely směny s AAD. Koukněte na aud (určeno pro směnu s AAD), iss (identifikace tohoto Kubernetes clusteru) a sub (tam je vidět jméno mého Service Account).

```json
{
  "aud": [
    "api://AzureADTokenExchange"
  ],
  "exp": 1644842330,
  "iat": 1644838730,
  "iss": "https://oidc.prod-aks.azure.com/25da173c-6b43-4f93-9c41-6cc688dea1ff/",
  "kubernetes.io": {
    "namespace": "default",
    "pod": {
      "name": "testpod",
      "uid": "4f5edc59-911b-4d46-a534-af1c19fb1815"
    },
    "serviceaccount": {
      "name": "tomas1kube",
      "uid": "c83f100a-1443-4bec-89ad-9d6e67e844e6"
    }
  },
  "nbf": 1644838730,
  "sub": "system:serviceaccount:default:tomas1kube"
}
```

Výborně - teď můžeme zavolat AAD, prokázat se tímto tokenem a požádat o token vystavený pro scope Azure Key Vaultu.

```bash
apt update
apt install jq -y

scope="https%3A%2F%2Fvault.azure.net%2F.default"
output=$(curl -X POST \
    "https://login.microsoftonline.com/$AZURE_TENANT_ID/oauth2/v2.0/token" \
    -d "scope=$scope&client_id=$AZURE_CLIENT_ID&client_assertion=$(cat $AZURE_FEDERATED_TOKEN_FILE)&grant_type=client_credentials&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer")

echo $output | jq -r .access_token | iconv -f ascii -t UTF-16LE > token
```

Dekódovaný token, co jsem dostal od AAD, vypadá takhle:

```json
{
  "aud": "https://vault.azure.net",
  "iss": "https://sts.windows.net/cac7b9c4-b5d4-4966-b6e4-39bef0bebb46/",
  "iat": 1644833800,
  "nbf": 1644833800,
  "exp": 1644837700,
  "aio": "E2ZgYFjzoyNpn/GNXrbtM9n0H3g1AgA=",
  "appid": "2ced0f74-1f9a-4456-94d9-d54a069fa687",
  "appidacr": "2",
  "idp": "https://sts.windows.net/cac7b9c4-b5d4-4966-b6e4-39bef0bebb46/",
  "oid": "7ed01f19-8c08-4802-a20c-7a351169a76c",
  "rh": "0.ATsAxLnHytS1Zkm25Dm-8L67RjmzqM-ighpHo8kPwL56QJM7AAA.",
  "sub": "7ed01f19-8c08-4802-a20c-7a351169a76c",
  "tid": "cac7b9c4-b5d4-4966-b6e4-39bef0bebb46",
  "uti": "KSqMh5G1nUOknVwujUUxAA",
  "ver": "1.0"
}
```

S tímto tokenem už můžu do Azure Key Vault a přečíst si secret!

```bash
curl https://tomas1aadkeyvault.vault.azure.net//secrets?api-version=7.2 \
  -H "Authorization: Bearer $(cat ./token)"

  {"value":[{"id":"https://tomas1aadkeyvault.vault.azure.net/secrets/mysecret","attributes":{"enabled":true,"created":1644833715,"updated":1644833715,"recoveryLevel":"Recoverable+Purgeable","recoverableDays":90},"tags":{"file-encoding":"utf-8"}}],"nextLink":null}
```

Takhle krásně vidíme na jakých principech stojí AAD workload identity federation. Vůči AAD účtu se můžu prokázat nejen jménem nebo certifikátem, ale i časově omezeným tokenem vystaveným jiným OIDC providerem, v našem případě konkrétním Kubernetes clusterem. Jaký vývoj lze očekávat do budoucna? Počítám, že brzy přibude podpora pro Managed Identitu, nejen Service Principal, což bude dobré pro scénáře s AKS. AAD Pod Identity, která dnes využívá metadata službu, bude postupně nahrazena v2 variantou postavenou na tom, co jste právě viděli. A v ten okamžik ji očekávám nejen jako addon do AKS, ale i do Arc for Kubernetes, takže to bude fungovat i na vašich clusterech v on-premises. Následně si myslím, že jednotlivé addony dalších služeb se naučí s tímto mechanismem nativně pracovat ať už to bude CSI Secret Store driver, KEDA, DAPR nebo Azure Monitor for Containers.

Příště se podíváme na použití tohoto postupu v GitHub Actions a pak, pokud se zadaří, i na use case s jiným cloudem - u Google, který používá OAuth tak jako Azure by to nemuselo být těžké, instance identita u AWS bude horší vzhledem k používání HMAC podpisů místo standardních metod a OIDC providera. Uvidíme.



