---
layout: post
title: 'Kubernetes praticky: bezpečné řešení přístupu například do Key Vault přes AAD Pod Identity'
tags:
- Kubernetes
- Security
---
Pokud chcete bezpečně řešit správu hesel, klíčů a certifikátů je vaší nejlepší volbou jejich uložení do Azure Key Vault a bezpečné vyzvedávání přímo aplikací. Místo použití Secret v Kubernetes se spolehnete na trezor, který je univerzální ať přistupujete odkudoli (Kubernetes, VM, WebApp, Functions, klient), je dokonale oddělen co do RBAC, který řešíte přes mocné nástroje Azure a AAD z pohledu řízení, auditovatelnosti apod. Trezor samotný je v Premium verzi implementován hardwarově na HSM zařízení a splňuje ty nejpřísnější požadavky.

Je tu ale jeden problém. Vůči trezoru se musíte ověřit. K tomu samozřejmě může posloužit účet Service Principal, ale jsme zase u toho, že jeho heslo musíte nějak rotovat a bezpečně doručovat aplikaci, aby mohla s Key Vault komunikovat. Pro WebApp a VM existuje lepší mechanismus - Managed Service Identity. V AAD vám vznikne účet VM, ale nemáte k němu heslo. Ten je svázaný s konkrétním VM nebo WebApp a zevnitř můžete zavolat speciální neroutovatelný endpoint 169.254.169.254. Na něj se dostanete jen zevnitř a je specificky pro váš stroj a pouze ten si z něj může vyzvednout časově omezený token pro přístup na Azure služby jako je Resource Manager nebo Azure Key Vault. Jak ale vyřešit něco podobného pro kontejnery?

# AAD Pod Identity
Přístup k identitě v rámci VM lze řešit buď systémovou identitou, která se vytvoří současně s VM, ale jde využít i user managed identitu. Tu si můžete založit sami a pro VM jen namapovat. Kdyby tedy existovala služba, která identity dostupné pro VM nějakým způsobem nabídne i Podům, bylo by to velmi užitečné. Ideálně ale tak, aby konkrétní identitu viděl jen ten Pod nebo skupina Podů, kterou chci. A nejlépe tak, aby mechanismus získávání tokenu byl stejný, jako s klasickou Managed Service Identity, aby můj kód fungoval stejně v kontejneru, WebApp i na VM.

Přesně tohle řeší projekt [AAD Pod Identity](https://github.com/Azure/aad-pod-identity)

Vyzkoušejme si to.

# Instalace a příprava
Nejprve nainstalujeme tento projekt do clusteru. Ten využívá custom resource definic a zavádí tak nové objekty do vašeho AKS.

```bash
kubectl create -f https://raw.githubusercontent.com/Azure/aad-pod-identity/master/deploy/infra/deployment-rbac.yaml
```

Následně si založíme identitu. Výborné je, že nemusíme jít do AAD a tam něco řešit a také to, že tato identita bude vidět jako resource v Azure. Pokud jste AKS vytvořili bez vlastního service principal, založte tuto identitu v MC_* skupině. Můžete ji umístit i jinam, ale pak nezapomeňte na tuto jinou resource group přiřadit AKS účtu práva Managed Identity Operator.

```bash
az identity create -g aks -n mujaccount1
```

Tento objekt pak najdete v portálu.

![](/images/2019/2019-06-06-07-25-03.png){:class="img-fluid"}

Následně vytvoříme v AKS objekt typu AzureIdentity, který tuto identitu v AAD reprezentuje v clusteru. Výchozí nastavení umožní s touto identitou pracovat v celém clusteru (tedy rozhodovat se, jakému Podu ji přiřadím), ale já jsem použil anotaci, aby byla identita přiřaditelná jen v konkrétním namespace. Identitu musíme identitikovat přes GUID a ClientID, tak si výsledný YAML vytvořím v Linuxu takhle.

```bash
cat > identity1.yaml << EOF
apiVersion: "aadpodidentity.k8s.io/v1"
kind: AzureIdentity
metadata:
  name: identity1
  annotations:
    aadpodidentity.k8s.io/Behavior: namespaced
spec:
  type: 0
  ResourceID: $(az identity show -g aks -n mujaccount1 --query id -o tsv)
  ClientID: $(az identity show -g aks -n mujaccount1 --query clientId -o tsv)
EOF
```

Dál vytvoříme binding, tedy objekt AzureIdentityBinding. V zásadě svážeme tuto identitu s nějakým selektorem, tedy jménem, které budeme používat k přiřazení identity k Podům. 

```yaml
apiVersion: "aadpodidentity.k8s.io/v1"
kind: AzureIdentityBinding
metadata:
  name: identity1-binding
spec: 
  AzureIdentity: identity1
  Selector: identity1
```

Pošleme to do clusteru a přípravu máme hotovou.

```bash
kubectl create namespace app1
kubectl apply -f identity1.yaml -n app1
kubectl apply -f identity1Binding.yaml -n app1
```

# Vyzkoušíme identitu v Podu
Připravme si následující Pod. Všimněte si labels, tak totiž říkáme, jestli a případně jako identitu má mít Pod k dispozici.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: ubuntu
  labels:
    aadpodidbinding: identity1
spec:
  containers:
    - name: ubuntu
      image: tutum/curl
      command: ["tail"]
      args: ["-f", "/dev/null"]
      resources:
        limits:
          cpu: 1
          memory: 256M
```

Nahodíme Pod a až naběhne, vyzkoušíme zavolání API tak, jako bychom to dělali u Managed Service Identity. V rámci atributu resource řekneme, na co chceme token získat. Já použiji Resource Manager. Pokud bych pak identitě v Azure přiřadil na nějaký zdroj, resource group či subskripci RBAC oprávnění, mohl bych z Podu třeba nastavovat Azure DNS, ověřovat se proti Azure Files a tak podobně.

```bash
kubectl apply -f podIdentity.yaml -n app1

kubectl exec -ti ubuntu -n app1 -- curl http://169.254.169.254/metadata/identity/oauth2/token?resource=https://management.azure.com

{"access_token":"BLABLABLA-swSNWjW5WzgbYaRyjheWboO3BIpMQKfeljoNbhTkwk9ubnQZDxBMVSbOFZcsAUKuwzPoE2oVqF6NlzSM8KJVw3bwlcSZqQdxYg4a36KFSzbCeuCG4Aw7iyJLi7RgxskB085jIOrKd7dmtT9zivnGTUHRdgjSjWKI0BQSRYJkdTKrTmlTN9MZzT48mPpPhvfcsY2kJlIy1M4w","refresh_token":"","expires_in":"28799","expires_on":"1559829685","not_before":"1559800585","resource":"https://management.azure.com","token_type":"Bearer"}
```

A máme to. V access_token je časově omezený token a můžeme volat nějaká Azure Resource Manager API.

# Příklad s vyzvedáváním hesla z Azure Key Vault
Asi nejtypičtější příklad využití těchto identit je vyzvedávání tajností z Azure Key Vault. Těmi může být secret, klíč nebo certifikát. Key Vault dokáže tajnosti verzovat nebo u certifikátů zajišťovat jejich obměnu. 

Založíme si nový trezor, v něm vytvoříme secret tajnost s nějakou hodnotou a nastavíme přístupovou politiku tak, že na začátku vytvořená identita bude mít právo si secret přečíst (ale jiná práva nemá - jen číst secret a ani nemá práva v Resource Manager, takže trezor ani nevidí).

```bash
export keyvaultname=mujtrezor
az keyvault create -n $keyvaultname -g aks
az keyvault secret set -n tajnost --vault-name $keyvaultname --value superheslo
az keyvault set-policy -n $keyvaultname \
    --object-id $(az identity show -g aks -n mujaccount1 --query principalId -o tsv) \
    --secret-permissions get 
```

Připojím se do Podu a nainstaluji jq, abych mohl pohodlně parsovat JSON. Tentokrát požádám o token ne na Resource Manager, ale na přístup do Key Vault. Pak už s příslušným tokenem jen mohu zavolat Key Vault API a secret si vyzvednu (já použiji ručně curl, ale existují samozřejmě příklady do různých programovacích jazyků).

```bash
kubectl exec -ti ubuntu -n app1 -- bash
apt update && apt install jq -y
export token=$(curl -s http://169.254.169.254/metadata/identity/oauth2/token?resource=https://vault.azure.net | jq -r '.access_token')
curl -H "Authorization: Bearer ${token}" https://mujtrezor.vault.azure.net/secrets/tajnost?api-version=7.0

{"value":"superheslo","id":"https://mujtrezor.vault.azure.net/secrets/tajnost/6de2fb2ee0da4178a224614540cbbea5","attributes":{"enabled":true,"created":1559676819,"updated":1559676819,"recoveryLevel":"Purgeable"},"tags":{"file-encoding":"utf-8"}}
```

A máme to! Vyzvedli jsme si heslo z trezoru a vůči němu se neověřovali heslem service principal, ale přes Managed Service Identity dostali jen časově omezený token. A to všechno tak, že kdo smí něco takového udělat si řídíme na úrovni jednotlivých Podů, tedy nativně pro AKS. Vyzkoušejte si to a zvažte přechod na držení citlivých informací velmi bezpečně v Azure Key Vault.