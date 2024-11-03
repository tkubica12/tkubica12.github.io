---
layout: post
title: 'Kubernetes praticky: používání externí konfigurace v Azure App Configuration Service'
tags:
- Kubernetes
- Apps
---
Kubernetes přichází s prostředky správy aplikačních konfigurací s ConfigMap a správu tajností se Secrets. Tyto vlastnosti jsou pro Kubernetes specifické a možná máte potřebu univerzálnějšího řešení. Něčeho, co bude dostupné z AKS, ale i VM v Azure, Web App v Azure Stack, Azure Function, Javascript klienta v browseru, IoT zařízení nebo z nativní mobilní aplikace. Minule jsem popisoval jak využít AAD Pod Identity a ukládat tajnosti univerzálně do velmi bezpečného Azure Key Vault (ať už si budete vyzvedávat aplikačně nebo v případě AKS zvolíte Flex Volume).

Něco podobného existuje i pro aplikační konfigurace a feature flagy. Něco, co nabízí centrální správu konfigurací jako službu pro libovolnou platformu a kód běžící kdekoli. Více v [předchozím článku](https://www.tomaskubica.cz/post/2019/app-configuration-service/).

Pojďme se dnes podívat, jak využít tuhle službu z Azure Kubernetes Service.

# AAD Pod Identity
Postupujte dle předchozího článku pro nasazení [AAD Pod Identity](https://www.tomaskubica.cz/post/2019/kubernetes-prakticky-bezpecne-reseni-pristupu-do-key-vault/). Služba App Configuration sice dovoluje přihlášení přes klíč nebo účet service principal, když ale běžíme v Azure, proč nevyužít velmi bezpečné Managed Service Identity resp. AAD Pod Identity pro případ AKS. 

Nejdřív rozchoďte AAD Pod Identity včetně vytvoření User Managed identity myaccount1.

Dále přes Azure CLI vytvořím App Configuration a něco do ní uložím (ujistěte se, že máte aktuální CLI - příkazy jsou v něm teprve chvilku, dříve byly v extension).

```bash
az appconfig create -n tomasappconfig123 \
    -g aks \
    -l westeurope
az appconfig kv set -y --name tomasappconfig123 \
    --key myconfigkey1 \
    --value myvalue1
```

Své managed identitě musím dát přes RBAC právo přistupovat ke konfiguracím. To udělám takhle:

```bash
az role assignment create --role Contributor \
    --assignee-object-id $(az identity show -n myaccount1 -g aks --query principalId -o tsv) \
    --scope $(az appconfig show -g aks -n tomasappconfig123 --query id -o tsv)
```

Teď už nasadím "aplikační" Pod. V předchozím díle jsem si udělal AzureIdentity a AzureIdentityBInding, takže teď už rovnou nahodím Pod. Použiji image tkubica/mybox, což je rozšířený ubuntu obraz s přidanými věcmi typu Azure CLI, dig nebo curl.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: mybox
  labels:
    aadpodidbinding: identity1
spec:
  containers:
    - name: mybox
      image: tkubica/mybox
      resources:
        requests:
          cpu: 10m
          memory: 32M
        limits:
          cpu: 1
          memory: 256M
```

Nejsem vývojář, tak se nechci trápit s vytvářením nějakého kódu - odkazy na jednotlivá SDK najdete v předchozím článku. Raději využijeme Azure CLI pro jednoduchou ukázku. Jak se Azure CLI ověří s využitím managed identity? To je nesmírně jednuduché - uvidíte - a všimněte si, že samozřejmě nedochází k žádné nutnosti zadávat jméno či nějak předávat heslo. To je klíčová vlastnost MSI a AAD Pod Identity.

```bash
kubectl exec -ti -n app1 mybox -- bash
az login --identity
az appconfig kv list --name tomasappconfig123 --key myconfigkey1
```

A je to - funguje. Ukázali jsme si dvě věci. Připomenuli novou Azure App Configuration službu a našli další hezké použití pro AAD Pod Identity. Díky němu už umíme generovat token do Key Vault, ale i do ARM například pro přístup do App Configuration. Stejným způsobem můžeme přes tuto identitu řešit i další věci, třeba ovládat Azure. Představte si například, že uvnitř Kubernetu poběžíte nějakou orchestrační platformu, třeba Terraform pro nasazování infrastruktury nebo Jenkins a potřebujete jim dovolit nasazovat do Azure. Místo statického jména a hesla, problematiky jejich předávání a rotace, zvolíte (pokud to daná aplikace/platforma umožňuje) AAD Pod Identity / MSI.