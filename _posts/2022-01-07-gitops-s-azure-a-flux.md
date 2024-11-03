---
layout: post
published: true
title: GitOps pro konzistentní stav všech vašich Kubernetes clusterů s Azure a Flux
tags:
- Kubernetes
- Automatizace
---
Pro řízení stavu infrastruktury možná (doufám) používáte Infrastructure as Code jako je Bicep nebo Terraform. Nasazování aplikací třeba řeší aplikační tým svou CI/CD pipeline s GitHub Actions přes Helm nebo Kustomize (nebo oboje). Dnes se ale zaměříme na to uprostřed, tedy ne komponenty typu AKS, EKS, GKE, Rancher, OpenShift, Tanzu, které jsou součástí spíše infra nasazení (Terraform), ale ani ne aplikační součástky. Mám na mysli například Ingress kontroler, KEDA scaler, applikační platformu (třeba DAPR), canary systém (Flagger, Argo Rollouts), cert-manager, External DNS, service mesh (když třeba chcete jiný, než který nabízí Kubernetes provider nativně), monitoring (pokud nepoužíváte nativní řešení cloudu), operátory pro platformy, které z nějakého důvodu nevyužijete jako službu v cloudu (Redis, MySQL, RabbitMQ) nebo pull-based CI/CD systém (Argo) či komponenty CI platformy (třeba self-hosted GitHub runnery v kontejnerech). 

# Tři vrstvy při používání Kubernetes pro aplikace
V zásadě potřebujeme vyřešit:
- Infrastrukturu a Kubernetes jako takový
- Případné nadstavbové věci v Kubernetu, které jsou potřebné k získání kompletní platformy pro provoz aplikace
- Aplikaci samotnou

## Infrastruktura a Kubernetes
Tuto část nejlépe vyřeší Infrastructure as Code nástroj a já se jí dnes zabývat nebudu. Poslední dobou mám hodně v oblibě hierarchická řešení s adresáři (viz třeba jak to dělá Kustomize nebo jak se to dá dělat s Terraformem) a dávalo by mi smysl, aby koncepty byly co nejpodobnější. Podstatné je, že Azure Kubernetes Service (služba v cloudu) a Azure Arc for Kubernetes (vrstva cloudového řízení libovolné on-prem či cloud distribuce) získává do svého API víc a víc nadstaveb ve formě addonů. Před lety jste v cloudu dostali holý cluster, kde jste pak všechno museli stavět nad tím na úrovni Kubernetes API, ale dnes vám ti nejlepší hráči nabízí spravované nadstavby jako v případě Azure:
- Azure Monitor (AKS i Arc)
- Open Service Mesh (AKS i Arc)
- Azure Key Vault Secrets Provider (AKS i Arc)
- Microsoft Defender for Cloud (AKS i Arc)
- Application Gateway Ingress Controller (jen AKS, protože AppGw je jen v Azure, nedává pro Arc smysl)
- GitOps (to nás nude dnes primárně zajímat)
- Azure Arc for Data Services - Azure SQL a PostgreSQL hyperscale
- Azure App Service on Azure Arc
- Event Grid on Kubernetes (Arc)
- Azure API Management on Azure Arc
- Virtual Nodes (AKS)
- Azure Policy (AKS i Arc)
- Confidential Computing (AKS)
- Azure ML for Azure Arc

## Podpůrné nástroje v Kubernetes
Přestože addony v AKS a Azure Arc nabízí dost široký výběr a pár dalších je jich v plánu přidat (např. DAPR a KEDA), tak některé komponenty si budete chtít instalovat vlastní nebo jimi nahradit některou v addonu (třeba z nějakého důvodu nechcete přímo podporovaný Open Service Mesh v addonu a preferujete Linkerd). Jak na to?
- Jedna možnost je převzít si cluster a nasadit tyto věci ručně - to nepreferuji.
- Pokud se cluster vytváří přes CI/CD, můžeme po dokončení nasazení infrastruktury přes GitHub Actions zavolat potřebné Helm/Kustomize příkazy.
- IaC nástroj nejprve nasadí AKS a pak se přes Kubernetes providera připojí do clusteru a nasadí YAMLy, Helm, Kustomize

Některé tyto varianty mohou vést k horší spravovatelnosti, pokud se neudělají dobře - například nevznikne state s předpisem pro konkrétní nastavení clusteru a některé parametry žijí jako proměnné v CI/CD nebo tak. I když se ale věc udělá správně, může to být trochu těžkopádné a závislé na pipeline nebo infra nástroji. Se zvyšujícím se množstvím clusterů to může začít být nepřehledné a navíc pokud jde i o "edge" clustery, třeba nějaké IoT brány v autech, lodích, pobočkách nebo clustery v různých cloudech a hosting prostředích, nemusí mít takhle jednoduchou konektivitu z deployment agenta - ten se musí dostat na API server, ale co když ten je za firewallem (banka nebo státní správa není nadšená, když je řízení clusteru dostupné "přes Internet") nebo za nespolehlivým spojením, protože loď má Internet  jen v přístavu? Ale jak říkám - vůbec to není jen o parnících a jiných extrémech, i když máte 10 clusterů a kombinaci cloud s on-prem, vyplatí se vám promyslet i jiný přístup - pull-based řešení s GitOps.

## Aplikace
Určitě bych nedoporučoval ani ruční práci ani IaC nástroje (nasazovat aplikaci Terraformem považuji za zhůvěřilost), takže to budou principiálně dva hlavní přístupy - push z CI/CD nebo pull-based GitOps (kde samozřejmě CI/CD hraje taky zásadní roli, jen to finální "rozbalení co mám dělat" si udělá cluster sám). 

# Azure Arc / AKS GitOps s Flux, Kustomize a Helm
AKS a Arc (pro váš libovolný Kubernetes kdekoli) dokáže jako addon dopravit do vašeho clusteru Flux v2 a starat se vám o něj aniž byste museli do clusteru přistoupit (tedy přes Azure API to do clusteru nahodí - nemusíte se do něj proroutovat, přihlašovat a tak podobně). Flux následně bude koukat do repozitářů a pravidelně zjišťovat co má dělat. Na odkazu očekává objekty ve formátu Kustomize s tím, že Flux přináší další objekty jako je HelmRepo, HelmRelease a GitRepo, takže dokáže nejen nasazovat YAML objekty přes Kustomize, ale potažmo i spravovat vaše různé Helm releasy nebo přidávat objekty z jiných repozitářů.

Podívejte se prosím na [můj GitHub](https://github.com/tomas-iac/common-kubernetes) - tam celý příklad je.

Ve stylu Kustomize rozdělím repo do adresářů a to v následujících vrstvách.

## Vrstva nultá - komponenty
Ve svém příkladu jsem se rozhodl nedělat specifické komponenty, protože nic zas tak složitého nemám a navíc moje clustery jsou principiálně stejné co do použitých komponent. Nicméně pokud bych potřeboval, udělám si adresář /components a v něm bude složitější komponenta žít a bude použitelná v různých bases.

## Vrstva první - base
V adresáři /base mám potřebné objekty a samozřejmě taky kustomization.yaml, který na ně ukazuje (případně si nabírá komponenty z jiného adresáře či repa). Mám tam definici namespace (to je jednoduchý YAML z Kubernetu) a pak cert-manager, nginx-ingress a KEDA, které všechny nasazuji z Helmu (a k němu příslušejícímu Helm repozitáři). Takhle třeba vypadá předpis pro nasazení NGINX Ingressu Helmem:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta1
kind: HelmRepository
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
spec:
  interval: 2m0s
  url: https://kubernetes.github.io/ingress-nginx
---
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
spec:
  chart:
    spec:
      chart: ingress-nginx
      sourceRef:
        kind: HelmRepository
        name: ingress-nginx
      version: 3.29.0
  interval: 1m0s
```

Co tedy tato vrstva dělá? Dává dohromady komponenty, v mém případě jsou představovány pouhými YAML soubory (ale mohly by to být další Kustomize adresáře/repa viz nultá vrstva), které potřebuji pro všechny svoje Kubernetes clustery. kustomization.yaml jednoduše odkazuje na příslušné soubory:

```yaml
resources:
- namespaces.yaml
- cert-manager.yaml
- keda.yaml
- nginx-ingress.yaml
```

## Vrstva druhá - prostředí
Jednotlivé komponenty v base jsou v nějakých verzích, mohou obsahovat nějaké anotace, tagy, labely, počty replik a tak podobně. Tohle mohou být parametry, které chci mít jiné v produkci (/environments/prod) a ve stagingu (/environments/staging). Jakmile bude nová verze Ingress kontroleru, nejdřív ji chci nasadit ve staging a v produkci nechat starší verzi, dokud si neověřím, že ta nová funguje. Totéž platí pro naprosto libovolný parametr jakéhokoli vstupního souboru. Kustomize funguje na principu patchování, takže v base nemusím definovat žádné další pojmenované parametry a vytvářet vlastní abstrakce, Kustomize prostě řeknu, že na cestě alfa.beta.klic1 chci přepsat hodnotu na true. Můžu tedy přepsat něco z Kubernetes objektu nebo v mém případě values v HelmRelease.

Můj kustomization.yaml vypadá takhle:

```yaml
resources:
- ../../base

patchesStrategicMerge:
- cert-manager.yaml
- keda.yaml
- nginx-ingress.yaml
```

V mém jednoduchém případě jsou komponenty prod i staging clusterů principiálně stejné, ale pokud bych chtěl, můžu do resources přidat něco nad rámec base - třeba pro prod a staging nasadit kubecost pro granulární řízení nákladů, ale do dev clusterů to nedávat. Kde se ale můj prod od staging rozchází je v některých parametrech objektů a to je vyřešeno patchováním. Takhle vypadá patch pro NGINX Ingress:

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
spec:
  chart:
    spec:
      version: 4.0.11
```

Všimněte si, že obsahuje pouze ty věci, co objekt přesně identifikují (jméno, kind a tak) a pak už jen to co chci změnit - a to je v mém případě verze. V adresáři staging to bude podobné, ale verze bude třeba 4.0.12, protože zrovna na staging testuji novější variantu.

Dnes jdu po jednoduchosti, proto jsou mé patche primitivní - vlastně si jen hraju s číslem verze. Kustomize mi ale umožní měnit cokoli, generovat secrets a configMap, přidávat objekty (třeba i ze vzdálených repozitářů) a tak podobně. K tomu se vrátíme někdy příště.

## Vrstva třetí - cluster
Zatím jsme vytvořili základní seznam věcí pro cluster (a ty jsme mohli ještě odkazovat přes komponenty, pokud by ty byly složitější) a nad tím varianty pro jednotlivá prostředí. To nestačí? Možná budou věci, které jsou specifické pro konkrétní cluster a v mém případě to je síťové nastavení NGINX ingressu. Potřebuji ho nasměrovat do konkrétního subnetu (ten se teoreticky může jmenovat pokaždé jinak) a řekněme, že z důvodu podpory některých starších aplikací a systémů pro něj chci definovat IP adresu staticky. Protože každý cluster je logicky v jiné síti, bude taky tato statická IP adresa u každého clusteru jiná. V praxi to mohou být další specifické vlastnosti clusteru - třeba ten pro kolegy dataře na strojové učení potřebuje nějaký plugin na Azure ML (a je jeden, takže zatím nedává smysl z něj dělat nějakou univerzální abstrakci), ten na pobočce chce ConfigMap s GPS souřadnicemi a ten v jiném cloudu musí mít trochu jiné anotace pro Ingress, aby tam fungoval.

kustomization.yaml jednoduše odkazuje na produkční variantu clusteru, ale opět bychom mohli přidat objekty (včetně Helm chartů, vzdálených repozitářů i Kustomize adresářů) specifické pro tento cluster. Obsahuje jediný patch na Ingress.

```yaml
resources:
- ../../environments/prod

patchesStrategicMerge:
  - nginx-ingress.yaml
```

Patch vypadá takhle - přidává values pro Helm s věcmi specifickými pro tento cluster:

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
spec:
  values:
    controller:
      service:
        loadBalancerIP: 10.0.1.10
        annotations:
          service.beta.kubernetes.io/azure-load-balancer-internal: "true"
          service.beta.kubernetes.io/azure-load-balancer-internal-subnet: "lb-subnet"
```

Všimněte si - neříkám verzi. Ta v mém případě není něco, co chci řešit per konkrétní cluster, ale to je nastavení per prostředí, tedy pro celou skupinu clusterů. Ale současně vidíte, že kdyby došlo na nějakou krizi a takovou výjimku jsem potřeboval, nebyl by problém to zařídit.

# GitOps doplněk pro Azure Kubernetes Service a Azure Arc for Kubernetes
Ať už máte svůj vlastní cluster kdekoli připojený přes Azure Arc nebo využíváte AKS, můžete zapnout podporu pro GitOps. V ten okamžik vám Azure zajistí správné nalodění Flux v2 projektu a jeho komponent, spojení a jeho správu. Následně můžeme do clusteru přes Azure API (tzn. přes příkazovou řádku, GUI v portálu, API volnání, Bicep šablonu a tak podobně) přidat jednotlivé konfigurace, tedy napojení na repozitáře. To je perfektní, protože jestli jste někdy zkoušeli automatizovat vytvoření Flux v2 v clusteru třeba Terraformem, není to úplně jednoduché, čitelné a hlavně musí mít váš deployment server přímý přístup do clusteru, což nemusí být síťově možné (cluster je ve vnitřní síti a CI/CD je v cloudu nebo cluster je za firewallem technologické sítě apod.).

Nejprve si založím tři clustery (pro účely ukázky jen přes CLI).

```bash
# Create resource group
az group create -n aks -l westeurope

# Create VNETs
az network vnet create -n project1-prod-vnet -g aks --address-prefixes 10.0.0.0/16
az network vnet subnet create -n aks-subnet -g aks --vnet-name project1-prod-vnet --address-prefix 10.0.0.0/24
az network vnet subnet create -n lb-subnet -g aks --vnet-name project1-prod-vnet --address-prefix 10.0.1.0/24
az network vnet create -n project1-staging-vnet -g aks --address-prefixes 10.1.0.0/16
az network vnet subnet create -n aks-subnet -g aks --vnet-name project1-staging-vnet --address-prefix 10.1.0.0/24
az network vnet subnet create -n lb-subnet -g aks --vnet-name project1-staging-vnet --address-prefix 10.1.1.0/24
az network vnet create -n project2-prod-vnet -g aks --address-prefixes 10.2.0.0/16
az network vnet subnet create -n aks-subnet -g aks --vnet-name project2-prod-vnet --address-prefix 10.2.0.0/24
az network vnet subnet create -n lb-subnet -g aks --vnet-name project2-prod-vnet --address-prefix 10.2.1.0/24

# Create clusters
az identity create -n aks-identity -g aks
az role assignment create --role Contributor -g aks --assignee $(az identity show -n aks-identity -g aks --query clientId -o tsv)

az aks create -n project1-prod-aks \
    -c 1 \
    -s Standard_B2ms \
    -g aks \
    -x \
    --network-plugin azure \
    --vnet-subnet-id $(az network vnet subnet show -n aks-subnet -g aks --vnet-name project1-prod-vnet --query id -o tsv) \
    --service-cidr 172.16.0.0/22 \
    --dns-service-ip 172.16.0.10 \
    --assign-identity $(az identity show -n aks-identity -g aks --query id -o tsv) \
    --assign-kubelet-identity $(az identity show -n aks-identity -g aks --query id -o tsv) \
    -y --no-wait
az aks create -n project1-staging-aks \
    -c 1 \
    -s Standard_B2ms \
    -g aks \
    -x \
    --network-plugin azure \
    --vnet-subnet-id $(az network vnet subnet show -n aks-subnet -g aks --vnet-name project1-staging-vnet --query id -o tsv) \
    --service-cidr 172.16.0.0/22 \
    --dns-service-ip 172.16.0.10 \
    --assign-identity $(az identity show -n aks-identity -g aks --query id -o tsv) \
    --assign-kubelet-identity $(az identity show -n aks-identity -g aks --query id -o tsv) \
    -y --no-wait
az aks create -n project2-prod-aks \
    -c 1 \
    -s Standard_B2ms \
    -g aks \
    -x \
    --network-plugin azure \
    --vnet-subnet-id $(az network vnet subnet show -n aks-subnet -g aks --vnet-name project2-prod-vnet --query id -o tsv) \
    --service-cidr 172.16.0.0/22 \
    --dns-service-ip 172.16.0.10 \
    --assign-identity $(az identity show -n aks-identity -g aks --query id -o tsv) \
    --assign-kubelet-identity $(az identity show -n aks-identity -g aks --query id -o tsv) \
    -y --no-wait
```

Následně přes CLI nastavím příslušné konfigurace. V mém případě je to typ managedClusters (tedy AKS), pokud by to bylo vaše Tanzu, Azure Stack, OpenShift, Rancher nebo nějaká cloudová služba, použijete po jeho připojení přes Azure Arc typ connectedClusters.

```bash
# Setup GitOps configurations
## Get CLI extensions
az extension update -n k8s-configuration
az extension update -n k8s-extension

## Create baseline cluster config
az k8s-configuration flux create -c project1-prod-aks \
    -n baseline \
    -g aks \
    --namespace gitops \
    -t managedClusters \
    --scope cluster \
    -u https://github.com/tomas-iac/common-kubernetes.git \
    --branch main  \
    --interval 60s \
    --kustomization name=infra path=/clusters/project1-prod-aks prune=true sync_interval=60s retry_interval=60s
az k8s-configuration flux create -c project1-staging-aks \
    -n baseline \
    -g aks \
    --namespace gitops \
    -t managedClusters \
    --scope cluster \
    -u https://github.com/tomas-iac/common-kubernetes.git \
    --branch main  \
    --interval 60s \
    --kustomization name=infra path=/clusters/project1-staging-aks prune=true sync_interval=60s retry_interval=60s
az k8s-configuration flux create -c project2-prod-aks \
    -n baseline \
    -g aks \
    --namespace gitops \
    -t managedClusters \
    --scope cluster \
    -u https://github.com/tomas-iac/common-kubernetes.git \
    --branch main  \
    --interval 60s \
    --kustomization name=infra path=/clusters/project2-prod-aks prune=true sync_interval=60s retry_interval=60s
```

Co stalo? V první řadě začal Azure spravovat instance Flux v2 a jeho komponent v clusteru.

```bash
$ kubectl get pods -n flux-system
NAME                                       READY   STATUS    RESTARTS   AGE
fluxconfig-agent-7d966db6f6-jgb25          2/2     Running   0          105m
fluxconfig-controller-7899bfd9d8-7pvfw     2/2     Running   0          105m
helm-controller-5bb76c785f-rwztd           1/1     Running   0          105m
kustomize-controller-566f499cb5-s5rpf      1/1     Running   0          105m
notification-controller-684fcff747-474p9   1/1     Running   0          105m
source-controller-6576b645b4-lc4sg         1/1     Running   0          105m
```

V GUI už to krásně vidím.

[![](/images/2021/2022-01-06-17-00-35.png){:class="img-fluid"}](/images/2021/2022-01-06-17-00-35.png)

[![](/images/2021/2022-01-06-17-01-20.png){:class="img-fluid"}](/images/2021/2022-01-06-17-01-20.png)

Moje Kustomizace je zaznamenána.

[![](/images/2021/2022-01-06-17-05-06.png){:class="img-fluid"}](/images/2021/2022-01-06-17-05-06.png)

Vidím i stav jednotlivých objektů.

[![](/images/2021/2022-01-06-17-05-43.png){:class="img-fluid"}](/images/2021/2022-01-06-17-05-43.png)

Jak to vypadá v clusteru? Azure vytvořil objekt kustomization.

```bash
$ kubectl describe kustomization -n gitops
Name:         baseline-infra
Namespace:    gitops
Labels:       clusterconfig.azure.com/is-managed=true
              clusterconfig.azure.com/name=baseline
              clusterconfig.azure.com/namespace=gitops
              clusterconfig.azure.com/operation-id=e6e8895b-79ac-4ac1-8524-14b000b866a9
Annotations:  reconcile.fluxcd.io/requestedAt: 2022-01-06T14:15:23.866407876Z
API Version:  kustomize.toolkit.fluxcd.io/v1beta2
Kind:         Kustomization
Metadata:
  ...
Spec:
  Force:     false
  Interval:  1m0s
  Patches:
    Patch:
- op:   add
  path: /spec/chart/spec/sourceRef
  value: {"name": "baseline", "namespace": "gitops", "kind": "GitRepository"}

    Target:
      Annotation Selector:  clusterconfig.azure.com/use-managed-source=true
      Group:                helm.toolkit.fluxcd.io
      Kind:                 HelmRelease
  Path:                     /clusters/project2-prod-aks
  Prune:                    true
  Retry Interval:           1m0s
  Service Account Name:     baseline-sa
  Source Ref:
    Kind:       GitRepository
    Name:       baseline
    Namespace:  gitops
  Timeout:      10m0s
Status:
  Conditions:
    Last Transition Time:  2022-01-06T16:06:13Z
    Message:               Applied revision: main/56b62001e832ac33ea21310011fa746b2012ccc7
    Reason:                ReconciliationSucceeded
    Status:                True
    Type:                  Ready
  Inventory:
    Entries:
      Id:                     _cert-manager__Namespace
      V:                      v1
      Id:                     _ingress-nginx__Namespace
      V:                      v1
      Id:                     _keda-system__Namespace
      V:                      v1
      Id:                     cert-manager_cert-manager_helm.toolkit.fluxcd.io_HelmRelease
      V:                      v2beta1
      Id:                     ingress-nginx_ingress-nginx_helm.toolkit.fluxcd.io_HelmRelease
      V:                      v2beta1
      Id:                     keda-system_keda_helm.toolkit.fluxcd.io_HelmRelease
      V:                      v2beta1
      Id:                     cert-manager_cert-manager_source.toolkit.fluxcd.io_HelmRepository
      V:                      v1beta1
      Id:                     ingress-nginx_ingress-nginx_source.toolkit.fluxcd.io_HelmRepository
      V:                      v1beta1
      Id:                     keda-system_keda_source.toolkit.fluxcd.io_HelmRepository
      V:                      v1beta1
  Last Applied Revision:      main/56b62001e832ac33ea21310011fa746b2012ccc7
  Last Attempted Revision:    main/56b62001e832ac33ea21310011fa746b2012ccc7
  Last Handled Reconcile At:  2022-01-06T14:15:23.866407876Z
  Observed Generation:        1
Events:
  Type    Reason  Age                   From                  Message
  ----    ------  ----                  ----                  -------
  Normal  info    10s (x104 over 104m)  kustomize-controller  (combined from similar events): Reconciliation finished in 1.578988476s, next run in 1m0s
```

a také fluxconfig.

```bash
$ kubectl describe fluxconfig -n gitops
Name:         baseline
Namespace:    gitops
Labels:       <none>
Annotations:  <none>
API Version:  clusterconfig.azure.com/v1alpha1
Kind:         FluxConfig
Metadata:
  ...
Spec:
  Correlation Id:  33d7c696-2f8f-4810-beb8-82761bc04887
  Git Repository:
    Ref:
      Branch:       main
    Sync Interval:  1m0s
    Timeout:        10m0s
    URL:            https://github.com/tomas-iac/common-kubernetes.git
  Kustomizations:
    Force:           false
    Name:            infra
    Path:            /clusters/project2-prod-aks
    Prune:           true
    Retry Interval:  1m0s
    Sync Interval:   1m0s
    Timeout:         10m0s
    Validation:      none
  Operation Id:      e6e8895b-79ac-4ac1-8524-14b000b866a9
  Protected Parameters Secret Ref:
    Name:       baseline-protected-parameters
  Scope:        cluster
  Soft Delete:  false
  Source Kind:  GitRepository
Status:
  Dataplane Status:
    Is Synced With Azure:     true
    Last Synced Time:         2022-01-06T16:07:24.549Z
  Last Config Update Time:    2022-01-06T14:15:23Z
  Last Source Synced Time:    2022-01-06T14:23:27Z
  Last Succeeded Generation:  1
  Last Succeeded Kustomizations:
    baseline-infra
  Last Synced Commit:  main/56b62001e832ac33ea21310011fa746b2012ccc7
  Managed Statuses:
    Git Repository:
      Compliance State:  Compliant
      Conditions:
        Last Transition Time:  2022-01-06T14:15:24Z
        Message:               Fetched revision: main/56b62001e832ac33ea21310011fa746b2012ccc7
        Reason:                GitOperationSucceed
        Status:                True
        Type:                  Ready
      Message:                 Resource is Ready
    Kustomizations:
      gitops/baseline-infra:
        Child Statuses:
          Bucket:
          Git Repository:
          Helm Chart:
          Helm Release:
            cert-manager/cert-manager:
              Compliance State:  Compliant
              Conditions:
                Last Transition Time:  2022-01-06T14:16:18Z
                Message:               Release reconciliation succeeded
                Reason:                ReconciliationSucceeded
                Status:                True
                Type:                  Ready
                Last Transition Time:  2022-01-06T14:16:18Z
                Message:               Helm install succeeded
                Reason:                InstallSucceeded
                Status:                True
                Type:                  Released
              Helm Release Properties:
                Helm Chart:             cert-manager/cert-manager-cert-manager
                Last Release Revision:  1
              Message:                  Resource is Ready
            ingress-nginx/ingress-nginx:
              Compliance State:  Compliant
              Conditions:
                Last Transition Time:  2022-01-06T14:16:39Z
                Message:               Release reconciliation succeeded
                Reason:                ReconciliationSucceeded
                Status:                True
                Type:                  Ready
                Last Transition Time:  2022-01-06T14:16:39Z
                Message:               Helm install succeeded
                Reason:                InstallSucceeded
                Status:                True
                Type:                  Released
              Helm Release Properties:
                Helm Chart:             ingress-nginx/ingress-nginx-ingress-nginx
                Last Release Revision:  1
              Message:                  Resource is Ready
            keda-system/keda:
              Compliance State:  Compliant
              Conditions:
                Last Transition Time:  2022-01-06T14:16:12Z
                Message:               Release reconciliation succeeded
                Reason:                ReconciliationSucceeded
                Status:                True
                Type:                  Ready
                Last Transition Time:  2022-01-06T14:16:12Z
                Message:               Helm install succeeded
                Reason:                InstallSucceeded
                Status:                True
                Type:                  Released
              Helm Release Properties:
                Helm Chart:             keda-system/keda-system-keda
                Last Release Revision:  1
              Message:                  Resource is Ready
          Helm Repository:
            cert-manager/cert-manager:
              Compliance State:  Compliant
              Conditions:
                Last Transition Time:  2022-01-06T14:15:27Z
                Message:               Fetched revision: b02f4b205646019ae5c4b42678803fd03714376e
                Reason:                IndexationSucceed
                Status:                True
                Type:                  Ready
              Message:                 Resource is Ready
            ingress-nginx/ingress-nginx:
              Compliance State:  Compliant
              Conditions:
                Last Transition Time:  2022-01-06T14:15:27Z
                Message:               Fetched revision: b8e89a4b3980f0e41425c3ccce4bf068ff45fe46
                Reason:                IndexationSucceed
                Status:                True
                Type:                  Ready
              Message:                 Resource is Ready
            keda-system/keda:
              Compliance State:  Compliant
              Conditions:
                Last Transition Time:  2022-01-06T14:15:27Z
                Message:               Fetched revision: 5cc2041544864e538b568ae446f6be49dbae4427
                Reason:                IndexationSucceed
                Status:                True
                Type:                  Ready
              Message:                 Resource is Ready
          Kustomization:
        Compliance State:  Compliant
        Conditions:
          Last Transition Time:  2022-01-06T16:07:15Z
          Message:               Applied revision: main/56b62001e832ac33ea21310011fa746b2012ccc7
          Reason:                ReconciliationSucceeded
          Status:                True
          Type:                  Ready
        Message:                 Resource is Ready
  Observed Generation:           1
  Provisioning State:            Succeeded
Events:                          <none>
```

Flux si stáhl potřebné Kustomizace a nainstaloval tak objekt HelmRepository a HelmRelease - ty pak používá jiná jeho komponenta, Helm operátor, k nasazení chartu.

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  creationTimestamp: "2022-01-06T14:04:33Z"
  finalizers:
  - finalizers.fluxcd.io
  generation: 1
  labels:
    clusterEnvironment: prod
    kustomize.toolkit.fluxcd.io/name: baseline-infra
    kustomize.toolkit.fluxcd.io/namespace: gitops
  name: ingress-nginx
  namespace: ingress-nginx
  resourceVersion: "46386"
  uid: b5e598eb-a671-4114-b7d4-7f40f7ad984b
spec:
  chart:
    spec:
      chart: ingress-nginx
      reconcileStrategy: ChartVersion
      sourceRef:
        kind: HelmRepository
        name: ingress-nginx
      version: 4.0.11
  interval: 1m0s
  values:
    controller:
      service:
        annotations:
          service.beta.kubernetes.io/azure-load-balancer-internal: "true"
          service.beta.kubernetes.io/azure-load-balancer-internal-subnet: lb-subnet
        loadBalancerIP: 10.0.1.10
status:
  conditions:
  - lastTransitionTime: "2022-01-06T14:05:46Z"
    message: Release reconciliation succeeded
    reason: ReconciliationSucceeded
    status: "True"
    type: Ready
  - lastTransitionTime: "2022-01-06T14:05:46Z"
    message: Helm install succeeded
    reason: InstallSucceeded
    status: "True"
    type: Released
  helmChart: ingress-nginx/ingress-nginx-ingress-nginx
  lastAppliedRevision: 4.0.11
  lastAttemptedRevision: 4.0.11
  lastAttemptedValuesChecksum: 2e47d9a2b13f7c173771d8c790d7e1790763cf0f
  lastReleaseRevision: 1
  observedGeneration: 1
```

Výsledkem je, že máme všechno krásně nasazené.

[![](/images/2021/2022-01-06-17-13-11.png){:class="img-fluid"}](/images/2021/2022-01-06-17-13-11.png)

[![](/images/2021/2022-01-06-17-13-34.png){:class="img-fluid"}](/images/2021/2022-01-06-17-13-34.png)

[![](/images/2021/2022-01-06-17-13-59.png){:class="img-fluid"}](/images/2021/2022-01-06-17-13-59.png)

[![](/images/2021/2022-01-06-17-14-39.png){:class="img-fluid"}](/images/2021/2022-01-06-17-14-39.png)

# GitOps a jak to rozvíjet dál
Mno a co když potřebujeme udělat nějakou změnu, třeba vyřešit zranitelnost zrovna nalezenou v NGINX kontroleru ve všech našich clusterech od cloudů přes on-prem až po IoT brány u zákazníků? Teď to přijde - změníte soubory v Gitu a to je celé, už jen čekáte. A že nějaký cluster zrovná není dostupný? To nevadí, hned jak bude, zjistí si co je nového a zařídí se podle toho. 

Kam se vydáme v příštích článcích?
- Co kdyby stejnou metodou olizování desired state repozitáře a řešení jakýchkoli rozporů vůči realitě postupoval i Infrastructure as Code systém? Tedy ne, že musím něco spustit, do něčeho šťouchnout, ale že si i IaC volá domů, aby se ubezpečila, že je ve správném stavu? Jasně - bude fajn si projít Crossplane a získat tak zabudovanou rekoncilaci místo nutnosti řešit kdy co mám spustit. Nebo zkusit Terraform Cloud Operator? Nebo Azure Service Operator?
- Možná ale budeme chtít zůstat u běžného řešení Infrastrcture as Code - jak nakombinovat Bicep nebo Terraform s dnes vyzkoušeným řešením, aby to dobře zapadalo do sebe?
- Proč takhle nezkusit řešit i aplikace? Příště bychom se měli pobavit o Flux vs. Argo a na oba se podívat.
- Chybí nám tu dnes samozřejmě ta procesní stránka GitOpsu - review, schvalovačky, testy, diskuse, pull requesty a všechny tyhle srandy. Není to jen o "Gitu", ale GitHub Actions tady také hrají nemalou roli. To, že se z Actions nevolá "helm install" neznamená, že nejsou potřeba. Určitě budeme chtít dělat úkony typu otestování změn v šablonách, cvičné nasazení, zpětná vazba autorům změn na základě nějakého policy engine, analýzy manifestů nebo i reálných testů (nasadíme cluster včetně těch věcí typu ingress a cert-manager, pošleme tam aplikaci co ho využívá a zkusíme na ni přistoupit - jestli tahle změna nic nerozbila, mělo by to fungovat).
- Monorepo mi připadá určitě fajn v případě společné konfigurace Kubernetes clusterů a ve finále by v něm klidně mohlo žít i IaC. Když ale přidáme vlastoručně vyrobené komponenty a naše aplikace, měli bychom se pobavit o řešení ve více repozitářích - například typicky appka per repo, separátní repo na některé komponenty a tak podobně.
- A co když budou potřeba nějaké secrets, třeba komponenta neumí Azure Pod Idenitity (managed identity) a potřebujeme jí dodat nějaký klíč či heslo? Určitě se v budoucnu musíme podívat na dvě alternativy - refencování Azure Key Vault (to bych preferoval) či jiného trezoru nebo použítí sealed secrets.
- Pokud tohle použiji pro aplikace, jak pak bude vypadat CI/CD? A budu schopen se v pipe nějak dozvědět jestli se nasazení podařilo?

GitOps a pull-based řešení asi není něco, co potřebujete hned do začátku vaší cesty - přecijen nejdřív byste měli umět aplikace a infrastrukturu navrhovat, nasazovat, monitorovat. Jak se ale bude modernější část vašeho IT rozšiřovat, budete možná hledat větší efektivitu a přijde čas na GitOps. Nebo tím důvodem bude provozní model, kdy jako centrální tým připravujete a spravujete prostředí pro aplikační týmy - jste tedy interním produktovým týmem, který vezme komponenty typu AKS, ACR, SQL, Defender, Azure Monitor, GitHub apod. a dá je dohromady do udržitelného řešení padnoucího na specifické potřeby vaší firmy. Pak dost možná zjistíte, že GitOps potřebujete co nejdřív. No a pokud používáte Kubernetes i mimo krásné a spolehlivé prostředí cloudu a běžíte ho na stožárech, ve sklepech, v přístrojové desce, vašich výdejních boxech nebo kioskách s vachrlatým připojením, tohle téma by pro vás mělo být extrémně důležité.