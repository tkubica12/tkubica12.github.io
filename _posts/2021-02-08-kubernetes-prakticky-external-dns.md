---
layout: post
title: 'Kubernetes prakticky: automatizovaná integrace privátní i veřejné DNS'
tags:
- Kubernetes
- Networking
---
Při vystavování služeb běžících v Kubernetes clusteru ke konzumaci okolním světem, ať už v privátní síti nebo veřejně, bývá k vidění celá řada přístupů. Ty nejčastější jsou manuální konfigurace, wildcard záznamy, API management a nebo dnešní téma - automatické vytváření záznamů v DNS mimo cluster s projektem External DNS.

# Řešení DNS při vystavování služeb
Obvykle se potkávám s následujícími variantami řešení konfigurace DNS záznamů:
-  **Ruční nastavení** je ve velkých firmách poměrně časté zejména pro veřejné přístupy. Ve společnosti jsou zavedené bezpečnostní procesy, dochází ke konfiguraci prvků typu F5 či nastavení firewallů a s tím spojené konfigurace DNS serverů. Leckomu se to může zdát zpátečnické, na druhou stranu je takhle ale skutečně pod kontrolou, co se vystavuje. Špatně zabezpečený server vystavený ven bez vědomí bezpečnostního týmu se často stává pro útočníky důležitou vstupní branou do prostředí a tato úroveň kontroly tomu brání. Zda jsou "náklady" ve ztrátě flexibility, rychlosti a samostatnosti opodstatněné záleží případ od případu.
- **Wildcard** záznamy považuji za velmi praktické. Hvězdička na DNS serveru namíří všechno na Ingress a zbytek se děje tam. Ne vždy je to ale dobře přijímáno a to typicky ze dvou důvodů. Jednou z výhrad může být bezpečnost, kdy nejsou DNS dotazy pod explicitní kontrolou. Druhou jsou praktické důvody, protože celou hvězdičku namíříte jen na jeden endpoint (třeba Ingress), což vede na "obětování" této větve a to nemusí být vhodné, pokud je aplikační portfolio rozprostřené přes několik technologií. Například pokud používám strukturu api.appka.domena.cz, login.appka.domena.cz, catalog.appka.domena.cz apod. a tohle všechno je v Kubernetes, není určitě špatné namířit na něj *.appka.domena.cz a zbytek vyřešit tam. Ale co když část aplikace běží jinde? S hvězdičkou mohou být spojené i obtíže s automatizací získávání certifikátů.
- **API management** může s tímhle pomoci, protože jednou z jeho vlastností je vytvořit API gateway, která na jednotném endpointu (= snížení počtu různých DNS záznamů) může obsluhovat požadavky a směrovat na libovolné backendy a to jak uvnitř clusteru nebo i jinde. Dobrý příkladem je Azure API Management jehož datová část může být jak hostovaná tak provozovaná uvnitř Kubernetes clusteru.
- **Automatizace DNS** je téma dnešního článku a spočívá v poslouchání vznikajících Service a Ingress objektů v Kubernetes a vytvoří k nim automatizovaně DNS záznamy v externím systému mimo cluster samotný - například v Azure DNS, jiné cloudové DNS nebo v některém z podporovaných DNS serverů. Pro DevOps týmy nebo pokročilé SRE lidi výborná věc.

# Projekt External DNS
Projekt External DNS slouží k automatizaci DNS záznamů v externí DNS na základě poslouchání vzniku objektů Service a Ingress. Dělá to tak, že u objektu Service sleduje anotaci a u objektu Ingress kouká na políčko hostname. Díky tomu ví, jaké FQDN je požadováno. U objektu Service najde v Kubernetes databázi její přidělenou externí IP (typicky se tedy používá se service type LoadBalancer) a to bude potřebný A záznam do DNS serveru. U objektu Ingress zase najde políčko s IP adresou balanceru (což je typicky IP adresa Service vašeho Ingress kontroleru) - ne všechny kontrolery to tak dělají, ale External DNS funguje například s oblíbeným NGINX a Traefik. Jsou i tam i nějaké další varianty s konfigurací CNAME, ale to v mém scénáři nebudu potřebovat.

Z podporovaných implementací externí DNS je pro mě důležitá Azure DNS a Azure Private DNS, najdete i DNS Google a AWS, CloudFlare nebo DNS servery jako je PowerDNS, CoreDNS či Infoblox.

# Využití Azure DNS a Azure Private DNS
Pro účely externí DNS velmi doporučuji převést si své domény do Azure DNS. Je to jediná služba Azure, která má svém SLA 100% dostupnost. Jako platformní služba je také chráněna proti DDoS. Za každou zónu zaplatíte cirka 10 Kč měsíčně a za každých milion dotazů taky 10 Kč. Do Azure DNS vám bude External DNS zapisovat explicitní A záznamy s IP adresou vašeho Ingressu. Někdy můžete potřebovat nastavovat spíše CNAME a i to je s External DNS možné.

Pro vnitřní použití nasadíme variantu Azure Private DNS a i pro tu má External DNS implementaci. Doporučoval bych následující architekturu:
- V Azure si v centrální hub síti nahoďte svůj vlastní DNS server (Linux či Windows, v redundanci)
- Tento DNS server bude dělat forwarding do onpremises a do Azure Private DNS a vaše spoke VNETy budou tento váš DNS server používat (přes něj se tedy dostanou jak do onpremises tak do všech Azure Private DNS)

Následně mě napadají dvě varianty, jak se zónami pracovat:
- Jednotný model, například azure.firma.cz a v této zóně se bude odehrávat všechno, tedy jak registrace VM, tak External DNS ze všech clusterů (to už dnes není problém, protože External DNS si do TXT record poznamenává, jak záznam vznikl, aby se vzájemně nepřepisovali). Nevýhodou takového modelu ale je, že sladit se názvech, aby si jednotlivé týmy nešlapaly na ruce, je na vás.
- Model více zón se mi libí víc. Udělal bych například azure.firma.cz a v něm zapnul automatickou registraci pro VM, takže vznikne třeba ad1.azure.firma.cz. Pak bych pro aplikace v Kubernetes udělal samostatnou zónu, třeba app1.firma.cz a app2.firma.cz, s vypnutou registrací a záznamy v nich bude vytvářet External DNS na základě publikovaných Service nebo Ingress objektů.

# Více Ingress kontrolerů pro vystavování do privátní a veřejné sítě
Rozeberme scénář, kdy jde o firmu bez potřeby ruční kontroly vystavování ven, která chce řídit jak interní tak veřejné služby přímo přes Kubernetes objekty. Pokud bych chtěl použít Ingress kontroler uvnitř clusteru, zvolil bych například nginx nebo Traefik ve dvou instancích. Jednu nainstaluji tak, že má service type Load Balancer bez anotací, takže běží na veřejné IP. Druhou instanci vytvořím s jiným názvem ingress class a v anotacích specifikuji interní load balancer. Díky tomu budu umět při definici Ingress pro aplikaci jednoduše vybrat, jestli se má publikovat interně nebo veřejně.

Pokud k tomuhle přidám dvě instance External DNS, jednu napojenou na Azure Private DNS zóny a druhou na Azure DNS public zóny, dostanu řešení, které je plně automatizované použitím Kubernetes objektů.

Přesně takový scénář si teď vyzkoušíme.

# Praktické nasazení
V následujícím scénáři použiji externí a interní NGINX Ingress, privátní DNS zónu pro VM, privátní DNS pro aplikaci v clusteru a jednu veřejnou zónu.

Nejprve si vytvořím networking, privátní DNS zónu (tu public už mám připravenou) a AKS cluster.

```bash
# Create networking
az group create -n networking-rg -l westeurope
az network vnet create -n my-net -g networking-rg --address-prefix 10.1.0.0/16
az network vnet subnet create --vnet-name my-net -g networking-rg -n aks-subnet --address-prefixes 10.1.0.0/24
az network vnet subnet create --vnet-name my-net -g networking-rg -n vm-subnet --address-prefixes 10.1.1.0/24

# Create Private DNS zone for Kubernetes services/ingresses and for virtual machines
az network private-dns zone create -g networking-rg -n services.mydomain.cz
az network private-dns zone create -g networking-rg -n vm.mydomain.cz
az network private-dns link vnet create -n services-zone-link \
    -g networking-rg \
    -z services.mydomain.cz \
    -e false \
    -v $(az network vnet show -n my-net -g networking-rg --query id -o tsv)
az network private-dns link vnet create -n vm-zone-link \
    -g networking-rg \
    -z vm.mydomain.cz \
    -e true \
    -v $(az network vnet show -n my-net -g networking-rg --query id -o tsv)

# Create AKS
az group create -n aks-rg -l westeurope
az aks create -n aks \
    -g aks-rg \
    -x \
    -c 1 \
    -s Standard_B2ms \
    --network-plugin azure \
    --vnet-subnet-id  $(az network vnet subnet show --vnet-name my-net -g networking-rg -n aks-subnet --query id -o tsv) \
    --service-cidr 192.168.5.0/24 \
    --dns-service-ip 192.168.5.100
az aks get-credentials -n aks -g aks-rg --overwrite-existing 

# Grant AKS access to networking for creating internal LB
az role assignment create --role "Network Contributor" \
    --assignee $(az aks show -n aks -g aks-rg --query identity.principalId -o tsv)  \
    -g networking-rg
```

Pro nasazení privátního Ingress použiji tento values soubor:

```yaml
controller:
  ingressClass: nginx-internal
  service:
    loadBalancerIP: 10.1.0.100
    annotations:
      service.beta.kubernetes.io/azure-load-balancer-internal: "true"
```

Nasadím interní Ingress.

```bash
kubectl create namespace ingress-internal
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm upgrade -i nginx-ingress-internal ingress-nginx/ingress-nginx -n ingress-internal -f ingressValues.yaml
```

Dále vytvoříme klasický externí NGINX Ingress.

```bash
kubectl create namespace ingress-external
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm upgrade -i nginx-ingress-external ingress-nginx/ingress-nginx -n ingress-external --set controller.ingressClass=nginx-external
```

V dalším kroku si připravím konfigurační soubor pro External DNS s využitím managed identity.

```json
{
  "tenantId": "mojeTenantId",
  "subscriptionId": "mojeSubscriptionId",
  "resourceGroup": "networking-rg",
  "useManagedIdentityExtension": true
}
```

Nasadím RBAC pravidla a dvě instance External DNS - jednu pro interní a druhou pro externí záznamy a všimněte si filtrace podle FQDN.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: external-dns
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRole
metadata:
  name: external-dns
rules:
- apiGroups: [""]
  resources: ["services","endpoints","pods"]
  verbs: ["get","watch","list"]
- apiGroups: ["extensions","networking.k8s.io"]
  resources: ["ingresses"] 
  verbs: ["get","watch","list"]
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["list"]
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: external-dns-viewer
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: external-dns
subjects:
- kind: ServiceAccount
  name: external-dns
  namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns
spec:
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: external-dns
  template:
    metadata:
      labels:
        app: external-dns
    spec:
      serviceAccountName: external-dns
      containers:
      - name: external-dns
        image: k8s.gcr.io/external-dns/external-dns:v0.7.3
        args:
        - --source=service
        - --source=ingress
        - --domain-filter=services.mydomain.cz
        - --provider=azure-private-dns
        - --azure-resource-group=networking-rg 
        - --azure-subscription-id=mojeSubscriptionId
        volumeMounts:
        - name: azure-config-file
          mountPath: /etc/kubernetes
          readOnly: true
      volumes:
      - name: azure-config-file
        secret:
          secretName: azure-config-file
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns-public
spec:
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: external-dns-public
  template:
    metadata:
      labels:
        app: external-dns-public
    spec:
      serviceAccountName: external-dns
      containers:
      - name: external-dns
        image: k8s.gcr.io/external-dns/external-dns:v0.7.3
        args:
        - --source=service
        - --source=ingress
        - --domain-filter=tomaskubica.net
        - --provider=azure
        - --azure-resource-group=shared-services
        - --azure-subscription-id=mojeSubscriptionId
        volumeMounts:
        - name: azure-config-file
          mountPath: /etc/kubernetes
          readOnly: true
      volumes:
      - name: azure-config-file
        secret:
          secretName: azure-config-file
```

Dám AKS identitě práva na svoje DNS zónu a pošlu nasazení External DNS do clusteru.

```bash
# Grant AKS managed identity access to DNS zones
az role assignment create --role "Private DNS Zone Contributor" \
    --assignee $(az aks show -n aks -g aks-rg --query identityProfile.kubeletidentity.clientId -o tsv)  \
    --scope $(az network private-dns zone show -g networking-rg -n services.mydomain.cz --query id -o tsv)
az role assignment create --role "Reader" \
    --assignee $(az aks show -n aks -g aks-rg --query identityProfile.kubeletidentity.clientId -o tsv)  \
    -g networking-rg
az role assignment create --role "Private DNS Zone Contributor" \
    --assignee $(az aks show -n aks -g aks-rg --query identityProfile.kubeletidentity.clientId -o tsv)  \
    --scope $(az network dns zone show -g shared-services -n tomaskubica.net --query id -o tsv)
az role assignment create --role "Reader" \
    --assignee $(az aks show -n aks -g aks-rg --query identityProfile.kubeletidentity.clientId -o tsv)  \
    -g shared-services

# Deploy External DNS
kubectl create secret generic azure-config-file --from-file=azure.json
kubectl apply -f externalDns.yaml
```

Nasadím teď jednoduchý webík.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myweb-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myweb
  template:
    metadata:
      labels:
        app: myweb
    spec:
      containers:
      - name: myweb
        image: tkubica/web:1
        env:
        - name: PORT
          value: "80"
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 64M
          limits:
            cpu: 500m
            memory: 256M
```

Nad aplikací teď použiji na ukázku tři objekty Service. Dvě služby jsou externí z pohledu clusteru s tím, že jedna z nich je v rámci VNETu (privátní) a druhá na veřejné IP. Nepoužívám tedy Ingress (L7 balancer). Takové řešení mi může přinášet větší výkon a podporuje i non-http protokoly, třeba UDP provoz. Hostname, na který bude moje External DNS reagovat, řeknu formou anotace. Třetí služba je typu ExternalName, tedy neprovádí žádný balancing uvnitř clusteru, ale použiji jí pro ukázku vytvoření CNAME.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: myweb-service-ext-private
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
    external-dns.alpha.kubernetes.io/hostname: s1.services.mydomain.cz
spec:
  selector:
    app: myweb
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
---
kind: Service
apiVersion: v1
metadata:
  name: myweb-service-ext-public
  annotations:
    external-dns.alpha.kubernetes.io/hostname: s1.tomaskubica.net
spec:
  selector:
    app: myweb
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
---
kind: Service
apiVersion: v1
metadata:
  name: s2-to-s1-cname
  annotations:
    external-dns.alpha.kubernetes.io/hostname: s2.tomaskubica.net
spec:
  externalName: s1.tomaskubica.net
  type: ExternalName
```

Zkusíme současně i druhou možnost - publikaci přes Ingress. Jeden bude mířit na kontroler s privátní IP a druhý na ten s veřejnou.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: myweb-service
spec:
  selector:
    app: myweb
  type: ClusterIP
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
---
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: myweb-ingress-internal
  annotations:
    kubernetes.io/ingress.class: nginx-internal
spec:
  rules:
  - host: intapp.services.mydomain.cz
    http:
      paths:
      - backend:
          serviceName: myweb-service
          servicePort: 80
        path: /
---
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: myweb-ingress-external
  annotations:
    kubernetes.io/ingress.class: nginx-external
spec:
  rules:
  - host: extapp.tomaskubica.net
    http:
      paths:
      - backend:
          serviceName: myweb-service
          servicePort: 80
        path: /
```

Podívejme se na výsledek. Takhle vypadá veřejná zóna tomaskubica.net.

![](/images/2021/2021-02-07-16-04-16.png){:class="img-fluid"}

A tohle je privátní zóna services.mydomain.cz
![](/images/2021/2021-02-07-16-05-08.png){:class="img-fluid"}

Klidně si teď můžeme všechno vyzkoušet z VM v Azure.

```bash
# Test
az group create -n vm-rg -l westeurope
az vm create -n test-vm \
    -g vm-rg \
    --size Standard_B1ms \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --subnet  $(az network vnet subnet show --vnet-name my-net -g networking-rg -n vm-subnet --query id -o tsv) \
    --public-ip-address vm-ip \
    --image UbuntuLTS

ssh tomas@$(az network public-ip show -n vm-ip -g vm-rg --query ipAddress -o tsv)
    # Internal Ingress
    dig intapp.services.mydomain.cz
    ;; ANSWER SECTION:
    intapp.services.mydomain.cz. 300 IN     A       10.1.0.100

    curl intapp.services.mydomain.cz
    Version 1: server id ea630f7d-d3ed-490c-adef-57b4ad68caf0

    # External Ingress
    dig extapp.tomaskubica.net
    ;; ANSWER SECTION:
    extapp.tomaskubica.net. 300     IN      A       51.145.177.91

    curl extapp.tomaskubica.net
    Version 1: server id ea630f7d-d3ed-490c-adef-57b4ad68caf0

    # Internal Service
    dig s1.services.mydomain.cz
    ;; ANSWER SECTION:
    s1.services.mydomain.cz. 300     IN      A       10.1.0.35

    curl s1.services.mydomain.cz
    Version 1: server id ea630f7d-d3ed-490c-adef-57b4ad68caf0

    # External Ingress
    dig s1.tomaskubica.net
    ;; ANSWER SECTION:
    s1.tomaskubica.net. 300     IN      A       20.76.9.50

    curl s1.tomaskubica.net
    Version 1: server id ea630f7d-d3ed-490c-adef-57b4ad68caf0

    # External CNAME
    dig s2.tomaskubica.net
    ;; ANSWER SECTION:
    s2.tomaskubica.net.     300     IN      CNAME   s1.tomaskubica.net.
    s1.tomaskubica.net.     299     IN      A       20.76.9.50

    curl s2.tomaskubica.net
    Version 1: server id ea630f7d-d3ed-490c-adef-57b4ad68caf0
```

Chcete automatizovat vnitřní a vnější DNS záznamy současně s nasazováním aplikace a to oboje Kubernetes způsobem, tedy například s využitím Helm šablon a hotových konektorů v CI/CD nástrojích jako jsou GitHub Actions nebo Azure DevOps? Podívejte se na projekt External DNS a jeho schopnost ovládat DNS v Azure. Není to jediná cesta, ale pro řadu z vás určitě hodně zajímavá. Vyzkoušejte si to.