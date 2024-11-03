---
layout: post
title: Federace tokenů GitHub Actions s Azure Active Directory pro přístup z vaší CI/CD do Azure bez hesel
tags:
- Automatizace
- Security
- AAD
- GitHub
---
V článku [Federace vnitřních Kubernetes identit s Azure Active Directory pro přístup k cloudovým službám bez hesel](https://www.tomaskubica.cz/post/2022/federace-kubernetes-identit-s-aad/) jsem ukazoval, jak lze využít federaci workload identit AAD v kombinaci s Kubernetes. Díky možnosti doručit kontejneru token Kubernetes identity a ten si směnit v AAD za token například pro Azure Key Vault nebo Azure SQL jsme vyřešili bezpečný přístup bez předávání hesel či certifikátů. Něco hodně podobného by se nám hodilo v CI/CD pipeline s GitHub Actions. Jak na to?

# Workload identity federation v Azure Active Directory a GitHub Actions
Z vaší CI/CD pipeline v GitHub Actions často potřebujete přihlášení do Azure Active Directory, například protože:
- Nasazujete zdroje (Infrastructure as Code) v Azure
- Nasazujete přes Helm/Kustomize do Kubernetes s AAD loginem
- Upgradujete schéma databáze v Azure SQL s AAD loginem
- Potřebujete přistoupit k trezoru na klíče, hesla či certifikáty v Azure Key Vault

To typicky uděláte tak, že vytvoříte účet Service Principal (zvláštní případ App Registration) a k ní bude nějaké heslo nebo certifikát, které použijete v GitHub Actions. Nicméně tím pádem musíte heslo v GitHubu držet a předávat do workerů a navíc toto má typicky relativně dlouhou platnost. Snad vás politiky donutily taková hesla minimálně jednou ročně měnit, lépe každé 3 měsíce, ale i to je dost dlouhá doba na jejich zneužití. Použití hesla nebo certifikátu tedy není ideální.

Druhou možností je využít v Azure koncept Managed Identity. To je samozřejmě skvělé - Azure vám bezpečným způsobem poskytne token, kód (Action) si ho snadno vyzvedne, žádných hesel netřeba, vše velmi bezpečné. Ale jedna potíž tu je - tohle samozřejmě funguje jen pro skutečně vaše zdroje ve smyslu infrastruktury - vaše VM nebo váš kontejner. Bezpečnostně je to sice výborné, ale musíte použít self-hosted agenty a s tím jsou spojené procesní náklady a praktické překážky. Využít agentů "as a service" je zkrátka daleko jednodušší (a levnější), ale ti pak nejsou ve vaší subskripci a nemůžou tak použít Managed Identity.

Novou třetí cestou je použití identity federation. GitHub funguje jako identitní provider a je schopen pro vaše repo/branch vystavit token a ten bezpečně předat agentovi. V AAD vytvoříme účet Service Principal, ale k němu se nebudeme prokazovat ani heslem, ani certifikátem, ale federovaným tokenem. Vytvoříme vztah důvěry - tento Service Principal věří tokenu vystavenému pro konkrétní GitHub repo/branch a GitHub Action si pak může svůj GitHub token vyměnit za AAD token a přihlásit se třeba do Azure.

Výborná věc - pojďme si vyzkoušet.

# Nastavíme a vyzkoušíme federaci GitHub Action s AAD pro přístup k Azure
Dnešní postup najdete také na mém [GitHubu](https://github.com/tkubica12/aad-workload-identity-demo/blob/main/GitHub.md) a Action využívající tohoto postupu [tady](https://github.com/tkubica12/aad-workload-identity-demo/actions).

Vytvoříme si účet Service Principal v AAD.

```bash
az ad sp create-for-rbac --name tomas1aad
```

Dál si vytvoříme resource group a tomuto účtu do ní dáme práva. Do tohoto místa budeme chtít přistupovat z GitHub Actions.

```bash
az group create -n githubdemo -l westeurope
az role assignment create --role "Contributor" \
  --assignee-object-id $(az ad sp list --display-name tomas1aad --query [0].objectId -o tsv) \
  -g githubdemo
```

Teď si nastavíme identitu mého GitHub repozitáře jako možný způsob ověření našeho Service Principal. Všimněte si hlavně políčka subject, kde je uvedeno konkrétně moje repo a main branch. 

```bash
export repo="tkubica12/aad-workload-identity-demo"
# export environment="azurecloud"
export APPLICATION_CLIENT_ID="$(az ad sp list --display-name tomas1aad --query '[0].appId' -otsv)"
export APPLICATION_OBJECT_ID="$(az ad app show --id ${APPLICATION_CLIENT_ID} --query objectId -otsv)"
cat <<EOF > body.json
{
  "name": "github-federated-credential",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:$repo:ref:refs/heads/main",
  "description": "GitHub federated credential",
  "audiences": [
    "api://AzureADTokenExchange"
  ]
}
EOF

az rest --method POST --uri "https://graph.microsoft.com/beta/applications/${APPLICATION_OBJECT_ID}/federatedIdentityCredentials" --body @body.json
rm body.json
```

Podívejme se teď na mojí GitHub Action.

```yaml
name: federatedIdentityDemo

on:
  workflow_dispatch:

jobs:
  demo:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - name: Azure Login
        uses: Azure/login@v1.4.3
        with:
          client-id: 3209dc01-519c-4705-8b68-e1acbfb7f2f8
          tenant-id: cac7b9c4-b5d4-4966-b6e4-39bef0bebb46
          subscription-id: 4fd63c38-a6be-4fb1-ac9e-ab1781af69ad
          
      - name: Test
        run: az group list -o table
```

Všimněte si akce Azure Login. Není tam žádné heslo ani certifikát! Tato akce tak pozná, že se má pokusit použít federovanou identitu. A to je všechno - vše potřebné pro mě udělala, můžu přistoupit do Azure. Samozřejmě pokud byste potřebovali přistoupit do něčeho jiného, než Azure managementu (například do Key Vault nebo SQL a tak podobně), nebude problém to zařídit, ale musíte si výměnu tokenů ošetřit sami.

[![](/images/2022/2022-02-26-18-54-08.png){:class="img-fluid"}](/images/2022/2022-02-26-18-54-08.png)


Používáte GitHub Actions ve spojení s Azure? Tato nová funkce je skvělá - hned jak na ní nebude nálepka "preview", což v době psaní článku ještě je, doporučuji všude používat.