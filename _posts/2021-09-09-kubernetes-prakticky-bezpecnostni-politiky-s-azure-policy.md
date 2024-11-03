---
layout: post
published: true
title: "Kubernetes prakticky: bezpečnostní politiky s Azure Policy pro Azure Kubernetes Service i váš on-premises Kubernetes/OpenShift"
tags:
- Governance
- Security
- Kubernetes
---
Už desítky let si v IT rádi definujeme nějaké politiky, abychom si udrželi v systémech pořádek a bezpečnost. Jak si je budeme označovat, jak nastavovat jednotlivé parametry, jaké doporučené postupy volit pro zajištění bezpečnosti, vysoké dostupnosti nebo provozuschopnosti? Obvykle se to projevilo ve směrnicích, dokumentaci nebo školeních. Například - pokud je systém publikován přímo do Internetu, musí být před ním bezpečnostní prvek typu WAF. Pokud aplikace není systémového typu nesmí v OS běžet jako admin/root. Svět Kubernetes v tomhle není jiný - je tam spousta věci, co lze nastavit tak, že to nevyhovuje bezpečnostním předpokladům nebo potřebám na monitoring či inventarizaci. Naštěstí v prostředích jako je cloud a Kubernetes jste schopni tyto politiky formulovat "as code". Místo PDF a školení jsou auditované a případně vynucené technologicky. Jinak řečeno můžete zajistit, že systém nenechá administrátory dělat věci špatně.

Podívejme se dnes na Azure Policy, která je řešením pro politiky pro váš cloud (infrastrukturní i platformní služby), ale i VM a Kubernetes infrastrukturu napojenou odkudkoli (on-prem, jiný cloud, hosting) přes Azure Arc. Dnes se zaměřím na Kubernetes, kde je Azure Policy implementována přes standardní open source technologii OPA a Gatekeeper.

V dnešním díle využijeme hotové knihovny politik a příště půjdeme do větší hloubky a napíšeme si vlastní politiku.

# Příprava prostředí
Než se pustíme do politik, pojďme si vytvořit Azure Kubernetes Service a registr, do kterého stáhneme nějaký image.

```bash
# Create AKS
az group create -n aksdemo -l westeurope
az acr create -n tomaskubicaaksdemo -g aksdemo --sku Basic
az aks create -n aksdemo -g aksdemo -c 1 -a azure-policy -s Standard_B2s -x --attach-acr tomaskubicaaksdemo -y
az aks get-credentials -n aksdemo -g aksdemo 

# Import alpine image to ACR
az acr import -n tomaskubicaaksdemo --source docker.io/library/alpine:latest -t alpine:latest --force
```

To bychom měli, pusťme se do toho.

# Azure Policy pro Kubernetes
V katalogu Azure Policy definic najdete databázi připravených politik vhodných pro jednoduchou aplikaci na váš Kubernetes cluster a to jak Azure Kubernetes Service tak jakýkoli jiný Kubernetes/OpenShift běžící kdekoli a napojený do Azure přes Azure Arc. Podívejme co je pro Kubernetes k dispozici.

[![](/images/2021/2021-09-09-08-59-01.png){:class="img-fluid"}](/images/2021/2021-09-09-08-59-01.png)

Nahoďme pár politik na vyzkoušení. Začněme s "Kubernetes cluster should not allow privileged containers". Kromě nějakých systémových namespace skutečně není ani trochu vhodné, aby běžel kontejner jako privilegovaný - tím je defacto rootem s plnými právy na hostiteli, to nechceme.

[![](/images/2021/2021-09-09-09-25-56.png){:class="img-fluid"}](/images/2021/2021-09-09-09-25-56.png)

Vyberu si na jakém scope budu chtít politiku přiřadit. Můžu to udělat na root tenant (pak všechny clustery v celé organizaci včetně těch napojených přes Arc tuhle politiku dostanou), nebo jít na management group, subskripci, resource group nebo (a to poslední ne přes GUI, ale v CLI to jde) na konkrétní cluster.

[![](/images/2021/2021-09-09-09-28-29.png){:class="img-fluid"}](/images/2021/2021-09-09-09-28-29.png)

Dál mohu specifikovat parametry. Effect Deny říká, že přímo v Kubernetu dojde k odmítnutí Podu, který by chtěl být privilegovaný. Volba audit to povolí, ale bude křičet, že politika není v tomto clusteru compliant. Další volby umožňují dát výjimky na některé namespace (třeba kube-system, kde je něco takového reálně potřeba), nechat politiku spadnout na všechny ostatní nebo naopak explicitně říct namespace, na kterém se má aplikovat. Jste schopni i jít ještě detailněji například po labelech podů případně konkrétní kontejnery v Podech uvést jako výjimku.

[![](/images/2021/2021-09-09-09-30-49.png){:class="img-fluid"}](/images/2021/2021-09-09-09-30-49.png)

Podobným postupem přidám další politiky:
- **Kubernetes clusters should not allow container privilege escalation** - Pod sice nemusí běžet privilegovaný, ale může mít právo oprávnění krátkodobě eskalovat. Tohle používá například NGINX, když ho chcete nastartovat na portu 80 (v Linuxu porty <1024 vyžadují vyšší oprávnění). Touto politikou takové nastavení zakážeme.
- **Kubernetes cluster pods should use specified labels** - z inventárních a provozních důvodu nastavením povinnost používat nějaké labely - já jsem definoval, že Pod musí mít label "app".
- **Kubernetes cluster containers CPU and memory resource limits should not exceed the specified limits** - je velmi důležitou provozní praxí uvádět limity na spotřebované zdroje Podu, protože jinak vám chybná aplikace vyžere všechno. V této politice jsem nastavil, že limity musí být uvedeny a současně, že jednotlivý Pod nemůže mít nastaveno víc jak 100 milicore a 100Mi paměti (to je oboje hodně málo - jde jen o příklad na zkoušku)
- **Kubernetes cluster pods and containers should only run with approved user and group IDs** - by default se mnoho kontejnerů včetně populárního NGINX spouští pod uživatelem root. Přestože nejsou privilegované (nemají tedy plná práva na hostitele), běží na stroji jako root a to není dobrá bezpečnostní praxe. Případná chyba nebo zranitelnost container runtime umožňující potenciálně vyskočit z kontejneru znamená, že se na hostiteli objevíte jako root s plnými právy. Z preventivních důvodů tedy není běhání jako root uživatel vhodné. V pravidle jsem nastavil jako approved user slovo "MustRunAsNonRoot", tedy cokoli kromě root.
- **Kubernetes cluster containers should only use allowed images** - je dobrou praxí neumožňovat v produkci stahování kontejnerů z veřejných zdrojů jako je Docker hub, protože nemáte pod kontrolou, zda tam nejsou nějaké zranitelnosti a tak podobně. Bezpečný proces je vždy mít kontejnery v registru pod vaší kontrolou a to včetně scanování zranitelností. I když bude kontejner pocházet z veřejného zdroje, tak byste měli mít proces jako ho stáhnout, oscanovat a publikovat ve vašem interním repozitáři. V tomto pravidle jsem nastavil regex tak, že dostupný bude pouze můj Azure Container Registry, který jsme v předchozích krocích vytvořili. Můj regex vypadá takhle:  ^tomaskubicaaksdemo.azurecr.io/.+$

Po nastavení musím chvilku počkat - Azure pošle politiky do clusteru v průběhu 15 minut.

Připravil jsem příklad ve formě Helm šablony s několika deploymenty, u kterých jsou určitě problémy, které by měly naše politiky chytnout.

```bash
helm install policy-demo https://github.com/tkubica12/aks-demo/blob/master/helm/policies-demo-0.1.0.tgz?raw=true --set acrName=tomaskubicaaksdemo
```

Podívejme se na ně podrobněji.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nolimits
spec:
  selector:
    matchLabels:
      app: nolimits
  template:
    metadata:
      labels:
        app: nolimits
    spec:
      containers:
      - name: container
        image: {{ .Values.acrName }}.azurecr.io/alpine:latest
        args:
          - "tail"
          - "-f"
          - "/dev/null"
        securityContext:
          allowPrivilegeEscalation: false
          runAsUser: 1000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ok
spec:
  selector:
    matchLabels:
      app: ok
  template:
    metadata:
      labels:
        app: ok
    spec:
      containers:
      - name: container
        image: {{ .Values.acrName }}.azurecr.io/alpine:latest
        resources:
          limits:
            memory: "32Mi"
            cpu: "50m"
        args:
          - "tail"
          - "-f"
          - "/dev/null"
        securityContext:
          allowPrivilegeEscalation: false
          runAsUser: 1000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: root
spec:
  selector:
    matchLabels:
      app: root
  template:
    metadata:
      labels:
        app: root
    spec:
      containers:
      - name: container
        image: {{ .Values.acrName }}.azurecr.io/alpine:latest
        resources:
          limits:
            memory: "32Mi"
            cpu: "50m"
        args:
          - "tail"
          - "-f"
          - "/dev/null"
        securityContext:
          allowPrivilegeEscalation: false
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wrongregistry
spec:
  selector:
    matchLabels:
      app: wrongregistry
  template:
    metadata:
      labels:
        app: wrongregistry
    spec:
      containers:
      - name: container
        image: nginx
        resources:
          limits:
            memory: "32Mi"
            cpu: "50m"
        args:
          - "tail"
          - "-f"
          - "/dev/null"
        securityContext:
          allowPrivilegeEscalation: false
          runAsUser: 1000
```

Tím se dostáváme k důležité věci - politiky jsou na Pody a jejich zaříznutí tedy proběhne v okamžiku, kdy se Pod vytváří. Naše definice ale dělá objekt typu Deployment a ten pod sebou vytváří ReplicaSet. Očekáváme tedy, že v Kubernetes neuvidíme běžící Pody co porušují pravidla a chybovou hlášku proč najdeme v ReplicaSetu.

```bash
$ kubectl get pods 
NAME                 READY   STATUS    RESTARTS   AGE
ok-c66c88bcf-fzpsc   1/1     Running   0          3m8s

$ kubectl get deploy
NAME            READY   UP-TO-DATE   AVAILABLE   AGE
nolimits        0/1     0            0           3m30s
ok              1/1     1            1           3m30s
root            0/1     0            0           3m30s
wrongregistry   0/1     0            0           3m30s

$ kubectl get rs
NAME                      DESIRED   CURRENT   READY   AGE
nolimits-567db544b8       1         0         0       3m53s
ok-c66c88bcf              1         1         1       3m53s
root-65b84f7b99           1         0         0       3m53s
wrongregistry-98c786dcc   1         0         0       3m53s

$ kubectl describe rs nolimits-567db544b8 | grep -A 100 Events
Events:
  Type     Reason        Age                    From                   Message
  ----     ------        ----                   ----                   -------
  Warning  FailedCreate  110s (x16 over 4m35s)  replicaset-controller  Error creating: admission webhook "validation.gatekeeper.sh" denied the request: [azurepolicy-container-limits-353b10954438e990aba4] container <container> has no resource limits

$ kubectl describe rs root-65b84f7b99 | grep -A 100 Events
Events:
  Type     Reason        Age                     From                   Message
  ----     ------        ----                    ----                   -------
  Warning  FailedCreate  2m25s (x16 over 5m10s)  replicaset-controller  Error creating: admission webhook "validation.gatekeeper.sh" denied the request: [azurepolicy-psp-allowed-users-groups-a46c42a0418762f6dfde] Container container is attempting to run without a required securityContext/runAsUser. Allowed runAsUser: {"ranges": [], "rule": "MustRunAsNonRoot"}

$ kubectl describe rs wrongregistry-98c786dcc | grep -A 100 Events
Events:
  Type     Reason        Age                  From                   Message
  ----     ------        ----                 ----                   -------
  Warning  FailedCreate  5s (x17 over 5m34s)  replicaset-controller  Error creating: admission webhook "validation.gatekeeper.sh" denied the request: [azurepolicy-container-allowed-images-5d5177af08e6993fecfb] Container image nginx for container container has not been allowed.  
```

Skvělé, všechno funguje.

# Malinko pod kapotu - Open Policy Agent a Gatekeeper
V příštím díle si zkusíme napsat svou vlastní politiku, takže dnes jen naťukneme jak to vlastně funguje. Řešení je postaveno na projektu Open Policy Agent, což je generický systém pro implementaci kontrol (případně změn) v datových strukturách, což je velmi typické pro kontrolu politik. Používá k tomu speciální deklarativní jazyk Rego, který si rozebereme příště.

Kubernetes má schopnost před přijmutím požadavku z API serveru tento poslat někam na schválení, tedy vytvořit API volání a předat to někomu k vyjádření. Tím "někým" bude Gatekeeper, což je defacto OPA obalené pro potřeby používání v Kubernetes. Rego jazykem se vyhodnotí zda vyhovuje či ne a Kubernetu se vrátí stanovisko. Používají se šablony s parametry a ty jsou vidět jako samostatný resource v Kubernetes. Podívejme se na šablony a vypišme si tu, která implementuje třeba ty povolené image registry.


```bash
$ kubectl get constrainttemplates
NAME                                     AGE
k8sazureallowedcapabilities              21h
k8sazureallowedusersgroups               21h
k8sazureblockautomounttoken              21h
k8sazureblockdefault                     21h
k8sazureblockhostnamespace               21h
k8sazurecontainerallowedimages           21h
k8sazurecontainerallowedports            21h
k8sazurecontainerlimits                  21h
k8sazurecontainernoprivilege             21h
k8sazurecontainernoprivilegeescalation   21h
k8sazuredisallowedcapabilities           21h
k8sazureenforceapparmor                  21h
k8sazurehostfilesystem                   21h
k8sazurehostnetworkingports              21h
k8sazureingresshttpsonly                 21h
k8sazurepodenforcelabels                 92m
k8sazurereadonlyrootfilesystem           21h
k8sazureserviceallowedports              21h

$ kubectl describe constrainttemplates k8sazurecontainerallowedimages
Name:         k8sazurecontainerallowedimages
Namespace:
Labels:       managed-by=azure-policy-addon
Annotations:  azure-policy-definition-id-1: /providers/microsoft.authorization/policydefinitions/febd0533-8e55-448f-b837-bd0e06f16469
              constraint-template: https://store.policy.core.windows.net/kubernetes/container-allowed-images/v2/template.yaml
              constraint-template-installed-by: azure-policy-addon
API Version:  templates.gatekeeper.sh/v1beta1
Kind:         ConstraintTemplate
Metadata:
  Creation Timestamp:  2021-09-08T12:31:03Z
  Generation:          1
  Managed Fields:
    API Version:  templates.gatekeeper.sh/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:metadata:
        f:annotations:
          .:
          f:azure-policy-definition-id-1:
          f:constraint-template:
          f:constraint-template-installed-by:
        f:labels:
          .:
          f:managed-by:
      f:spec:
        .:
        f:crd:
          .:
          f:spec:
            .:
            f:names:
              .:
              f:kind:
            f:validation:
              .:
              f:openAPIV3Schema:
                .:
                f:properties:
                  .:
                  f:excludedContainers:
                    .:
                    f:items:
                      .:
                      f:type:
                    f:type:
                  f:imageRegex:
                    .:
                    f:type:
        f:targets:
    Manager:      azurepolicyaddon
    Operation:    Update
    Time:         2021-09-08T12:31:03Z
    API Version:  templates.gatekeeper.sh/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:status:
        .:
        f:byPod:
        f:created:
    Manager:         gatekeeper
    Operation:       Update
    Time:            2021-09-08T12:31:16Z
  Resource Version:  1571
  UID:               b0a859ea-d42d-4e7f-9218-31f9dcadd447
Spec:
  Crd:
    Spec:
      Names:
        Kind:  K8sAzureContainerAllowedImages
      Validation:
        openAPIV3Schema:
          Properties:
            Excluded Containers:
              Items:
                Type:  string
              Type:    array
            Image Regex:
              Type:  string
  Targets:
    Rego:  package k8sazurecontainerallowedimages

violation[{"msg": msg}] {
  container := input_containers[_]
  not input_container_excluded(container.name)
  not re_match(input.parameters.imageRegex, container.image)
  msg := sprintf("Container image %v for container %v has not been allowed.", [container.image, container.name])
}

input_containers[c] {
    c := input.review.object.spec.containers[_]
}
input_containers[c] {
    c := input.review.object.spec.initContainers[_]
}
input_container_excluded(field) {
    field == input.parameters.excludedContainers[_]
}

    Target:  admission.k8s.gatekeeper.sh
Status:
  By Pod:
    Id:                   gatekeeper-audit-5456bb46b6-bttpr
    Observed Generation:  1
    Operations:
      audit
      status
    Template UID:         b0a859ea-d42d-4e7f-9218-31f9dcadd447
    Id:                   gatekeeper-controller-58d7f44b9-2m2h4
    Observed Generation:  1
    Operations:
      webhook
    Template UID:         b0a859ea-d42d-4e7f-9218-31f9dcadd447
    Id:                   gatekeeper-controller-58d7f44b9-l4g5v
    Observed Generation:  1
    Operations:
      webhook
    Template UID:  b0a859ea-d42d-4e7f-9218-31f9dcadd447
  Created:         true
Events:            <none>
```

Všimněte si parametrů a Rego kódu. Z těchto šablon se pro vás vytvoří speciální typ resource v Kubernetes, v tomto případě k8sazurecontainerallowedimages.


```bash
$ kubectl get k8sazurecontainerallowedimages
NAME                                                        AGE
azurepolicy-container-allowed-images-5d5177af08e6993fecfb   94m
azurepolicy-container-allowed-images-5fcf68652eaee1c79c7d   21h

$ kubectl describe k8sazurecontainerallowedimages azurepolicy-container-allowed-images-5d5177af08e6993fecfb
Name:         azurepolicy-container-allowed-images-5d5177af08e6993fecfb
Namespace:
Labels:       managed-by=azure-policy-addon
Annotations:  azure-policy-assignment-id:
                /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/aksdemo/providers/Microsoft.Authorization/policyAssignments/8a55f11aaba...
              azure-policy-definition-id: /providers/Microsoft.Authorization/policyDefinitions/febd0533-8e55-448f-b837-bd0e06f16469
              azure-policy-definition-reference-id:
              azure-policy-setdefinition-id:
              constraint-installed-by: azure-policy-addon
              constraint-url: https://store.policy.core.windows.net/kubernetes/container-allowed-images/v2/constraint.yaml
API Version:  constraints.gatekeeper.sh/v1beta1
Kind:         K8sAzureContainerAllowedImages
Metadata:
  Creation Timestamp:  2021-09-09T08:16:44Z
  Generation:          1
  Managed Fields:
    API Version:  constraints.gatekeeper.sh/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:metadata:
        f:annotations:
          .:
          f:azure-policy-assignment-id:
          f:azure-policy-definition-id:
          f:azure-policy-definition-reference-id:
          f:azure-policy-setdefinition-id:
          f:constraint-installed-by:
          f:constraint-url:
        f:labels:
          .:
          f:managed-by:
      f:spec:
        .:
        f:enforcementAction:
        f:match:
          .:
          f:excludedNamespaces:
          f:kinds:
        f:parameters:
          .:
          f:excludedContainers:
          f:imageRegex:
    Manager:      azurepolicyaddon
    Operation:    Update
    Time:         2021-09-09T08:16:44Z
    API Version:  constraints.gatekeeper.sh/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:status:
        .:
        f:auditTimestamp:
        f:byPod:
        f:totalViolations:
    Manager:         gatekeeper
    Operation:       Update
    Time:            2021-09-09T08:26:27Z
  Resource Version:  103398
  UID:               cb154c2a-a8fc-45ca-ae52-84dc56ed6128
Spec:
  Enforcement Action:  deny
  Match:
    Excluded Namespaces:
      kube-system
      gatekeeper-system
      azure-arc
    Kinds:
      API Groups:

      Kinds:
        Pod
  Parameters:
    Excluded Containers:
    Image Regex:  ^tomaskubicaaksdemo.azurecr.io/.+$
Status:
  Audit Timestamp:  2021-09-09T09:46:24Z
  By Pod:
    Constraint UID:       cb154c2a-a8fc-45ca-ae52-84dc56ed6128
    Enforced:             true
    Id:                   gatekeeper-audit-5456bb46b6-bttpr
    Observed Generation:  1
    Operations:
      audit
      status
    Constraint UID:       cb154c2a-a8fc-45ca-ae52-84dc56ed6128
    Enforced:             true
    Id:                   gatekeeper-controller-58d7f44b9-2m2h4
    Observed Generation:  1
    Operations:
      webhook
    Constraint UID:       cb154c2a-a8fc-45ca-ae52-84dc56ed6128
    Enforced:             true
    Id:                   gatekeeper-controller-58d7f44b9-l4g5v
    Observed Generation:  1
    Operations:
      webhook
  Total Violations:  0
Events:              <none>
```

Tímto je politika aplikována a v clusteru běží kontroler a audit server.

```bash
$ kubectl get pods -n gatekeeper-system
NAME                                    READY   STATUS    RESTARTS   AGE
gatekeeper-audit-5456bb46b6-bttpr       1/1     Running   0          21h
gatekeeper-controller-58d7f44b9-2m2h4   1/1     Running   0          21h
gatekeeper-controller-58d7f44b9-l4g5v   1/1     Running   0          21h
```

A jak informace proudí mezi Azure a tímto systémem? Do dělá komponenta pro Azure Policy a tím se to celé spravuje a propojuje.

```bash
$ kubectl get pods -n kube-system | grep policy
azure-policy-7c9c6d8676-vt75q           1/1     Running   0          21h
azure-policy-webhook-7fc44c6cf9-86ltx   1/1     Running   0          21h
```

# Jak nasadit na Kubernetes mimo Azure
Na závěr si ještě ukažme jak totéž použít pro Kubernetes mimo Azure napojený přes Arc. Díky tomu jste schopni centrálně a jednoduše řídit bezpečnostní a provozní politiky ve všech vašich clusterech a prostředích jako je Azure, další cloud, hosting, on-premises nebo edge zařízení typu IoT, Azure Stack Hub / Azure Stack HCI / Azure Stack Edge a tak podobně.

Udělám to tak, že si postavím VM a do ní nainstaluji K3s - odlehčený Kubernetes. Ten nalodím do Azure Arc a do Azure Policy. Protože ho dávám do stejné resource group, politiky se tam automaticky promítnou.

```bash
# Create VM and install K3s
az vm create -n k3s -g aksdemo --size Standard_B2s --image UbuntuLTS --nsg "" --ssh-key-values ~/.ssh/id_rsa.pub --admin-username tomas
export ip=$(az network public-ip show -n k3sPublicIP -g aksdemo --query ipAddress -o tsv)
ssh $ip
    curl -sfL https://get.k3s.io | sh -
    sudo cp /etc/rancher/k3s/k3s.yaml  ~/k3s.yaml
    sudo chown tomas:tomas ~/k3s.yaml
    export KUBECONFIG=~/k3s.yaml
    kubectl get nodes

# Onboard to Arc
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az extension add --name connectedk8s
az login
az account set -s tokubica
wget https://get.helm.sh/helm-v3.6.3-linux-amd64.tar.gz
tar xvf helm-v3.6.3-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/bin
az connectedk8s connect -n k3s -g aksdemo

# Onboard Azure Policy
az provider register --namespace 'Microsoft.PolicyInsights'
export secret=$(az ad sp create-for-rbac -n tomaskubicaarc --role "Policy Insights Data Writer (Preview)" --scopes $(az connectedk8s show -n k3s -g aksdemo --query id -o tsv) --query password -o tsv)
export client=$(az ad sp list --display-name tomaskubicaarc --query [0].appId -o tsv)
export tenant=$(az ad sp list --display-name tomaskubicaarc --query [0].appOwnerTenantId -o tsv)
export clusterId=$(az connectedk8s show -n k3s -g aksdemo --query id -o tsv)
helm repo add azure-policy https://raw.githubusercontent.com/Azure/azure-policy/master/extensions/policy-addon-kubernetes/helm-charts
helm install azure-policy-addon azure-policy/azure-policy-addon-arc-clusters \
    --set azurepolicy.env.resourceid=$clusterId \
    --set azurepolicy.env.clientid=$client \
    --set azurepolicy.env.clientsecret=$secret \
    --set azurepolicy.env.tenantid=$tenant
```

Výborně - příprava hotová. Přesvěčme se, že Azure Policy a Gatekeeper se v clusteru objevili, uvidíme naládované šablony a politky a že všechno funguje stejně jako v Azure.


```bash
tomas@k3s:~$ kubectl get pods -A
NAMESPACE           NAME                                             READY   STATUS      RESTARTS   AGE
kube-system         metrics-server-86cbb8457f-blr6c                  1/1     Running     0          21h
kube-system         local-path-provisioner-5ff76fc89d-8h9rq          1/1     Running     0          21h
kube-system         coredns-7448499f4d-2w4j2                         1/1     Running     0          21h
kube-system         helm-install-traefik-crd-2nbs2                   0/1     Completed   0          21h
kube-system         helm-install-traefik-645jq                       0/1     Completed   1          21h
kube-system         svclb-traefik-7fxqp                              2/2     Running     0          21h
kube-system         traefik-97b44b794-wdf49                          1/1     Running     0          21h
azure-arc           flux-logs-agent-bd5659f94-mz4cd                  1/1     Running     0          21h
azure-arc           config-agent-c9f8d7577-99gdk                     2/2     Running     0          21h
azure-arc           cluster-metadata-operator-77d878d65c-xcwsd       2/2     Running     0          21h
azure-arc           resource-sync-agent-5c547cd6-tdnb9               2/2     Running     0          21h
azure-arc           controller-manager-5b99f7b9df-rvxj2              2/2     Running     0          21h
azure-arc           kube-aad-proxy-65b7d9d658-klndw                  2/2     Running     0          21h
azure-arc           metrics-agent-675566f58f-nvhr2                   2/2     Running     0          21h
azure-arc           clusteridentityoperator-578c88fb78-twkpk         2/2     Running     0          21h
azure-arc           extension-manager-74fcdd97b-99vgv                2/2     Running     0          21h
azure-arc           clusterconnect-agent-6d894d44b-nnbt2             3/3     Running     0          21h
kube-system         azure-policy-b7bbccddf-zq6h9                     1/1     Running     0          20h
gatekeeper-system   gatekeeper-controller-manager-777d6d87df-8qm5t   1/1     Running     0          20h
gatekeeper-system   gatekeeper-audit-74cd7c4844-jwkwb                1/1     Running     0          20h
kube-system         azure-policy-webhook-766cb45df4-pvvdf            1/1     Running     0          20h
gatekeeper-system   gatekeeper-controller-manager-777d6d87df-68754   1/1     Running     0          20h

tomas@k3s:~$ kubectl get crd | grep gatekeeper
configs.config.gatekeeper.sh                                       2021-09-08T13:46:12Z
constraintpodstatuses.status.gatekeeper.sh                         2021-09-08T13:46:12Z
constrainttemplates.templates.gatekeeper.sh                        2021-09-08T13:46:12Z
constrainttemplatepodstatuses.status.gatekeeper.sh                 2021-09-08T13:46:12Z
k8sazureingresshttpsonly.constraints.gatekeeper.sh                 2021-09-08T13:49:01Z
k8sazurecontainerallowedimages.constraints.gatekeeper.sh           2021-09-08T13:49:03Z
k8sazurecontainernoprivilege.constraints.gatekeeper.sh             2021-09-08T13:49:04Z
k8sazurecontainerallowedports.constraints.gatekeeper.sh            2021-09-08T13:49:05Z
k8sazurereadonlyrootfilesystem.constraints.gatekeeper.sh           2021-09-08T13:49:06Z
k8sazureallowedcapabilities.constraints.gatekeeper.sh              2021-09-08T13:49:08Z
k8sazurehostfilesystem.constraints.gatekeeper.sh                   2021-09-08T13:49:09Z
k8sazurecontainernoprivilegeescalation.constraints.gatekeeper.sh   2021-09-08T13:49:11Z
k8sazureenforceapparmor.constraints.gatekeeper.sh                  2021-09-08T13:49:12Z
k8sazurehostnetworkingports.constraints.gatekeeper.sh              2021-09-08T13:49:13Z
k8sazureblockdefault.constraints.gatekeeper.sh                     2021-09-08T13:49:14Z
k8sazureblockhostnamespace.constraints.gatekeeper.sh               2021-09-08T13:49:16Z
k8sazureblockautomounttoken.constraints.gatekeeper.sh              2021-09-08T13:49:17Z
k8sazuredisallowedcapabilities.constraints.gatekeeper.sh           2021-09-08T13:49:18Z
k8sazureserviceallowedports.constraints.gatekeeper.sh              2021-09-08T13:49:20Z
k8sazurecontainerlimits.constraints.gatekeeper.sh                  2021-09-08T13:49:21Z
k8sazureallowedusersgroups.constraints.gatekeeper.sh               2021-09-08T13:49:23Z
k8sazurepodenforcelabels.constraints.gatekeeper.sh                 2021-09-09T08:04:02Z

tomas@k3s:~$ helm install policy-demo https://github.com/tkubica12/aks-demo/blob/master/helm/policies-demo-0.1.0.tgz?raw=true --set acrName=tomaskubicaaksdemo
NAME: policy-demo
LAST DEPLOYED: Thu Sep  9 09:59:27 2021
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

tomas@k3s:~$ kubectl describe rs root-65b84f7b99 | grep -A 100 Events
Events:
  Type     Reason        Age                 From                   Message
  ----     ------        ----                ----                   -------
  Warning  FailedCreate  21s (x14 over 64s)  replicaset-controller  Error creating: admission webhook "validation.gatekeeper.sh" denied the request: [denied by azurepolicy-psp-allowed-users-groups-a46c42a0418762f6dfde] Container container is attempting to run without a required securityContext/runAsUser. Allowed runAsUser: {"ranges": [], "rule": "MustRunAsNonRoot"}
```

A je to - všechno funguje i na libovolném Kubernetes/OpenShift napojeném přes Azure Arc.