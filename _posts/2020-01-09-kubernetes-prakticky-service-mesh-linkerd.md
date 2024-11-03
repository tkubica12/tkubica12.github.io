---
layout: post
title: 'Kubernetes praticky: Service Mesh zaměřený na rychlost a efektivitu - Linkerd'
tags:
- Kubernetes
- Networking
- ServiceMesh
---
Než se pustíme do Linkerd, rád bych připomenul předchozí článek, který se zamýšlí nad rolí service mesh, jestli to vůbec potřebuji a jaké výhody a nevýhody přináší. V rámci pokračování tématu se budu věnovat třem implementacím a dopustím se v úvodu velmi hrubého a nepřesného zjednodušení:
- Istio, které je zaměřeno na maximální množství funkcí, umí toho strašně moc, ale znamená velký overhead, spotřebu zdrojů a zvýšenou latenci - trochu riskantní se může jevit, že to není oficiální CNCF projekt (může zavánět vendor tlačenou záležitostí)
- Linkerd, které je zaměřeno na maximální efektivitu a rychlost, nízkou zátěž, nízkou přidanou latenci, ale umí toho o dost méně - nicméně je to jediný z těchto tří, který je oficiální CNCF projektem
- Consul Connect, který nejen marketingově, ale i prakticky dobře funguje v propojení Kubernetes a VM-based technologií, clusterů a service discovery přes všechny platformy a cloudy pro distribuované aplikace (pokud chcete jednu "síť nad všemi cloudy a onpremises od fyzických serverů po kontejnery, tohle může být řešení)
- Service Mesh Interface (SMI) není žádná implementace, jen vrstva abstrakce (API) přinášející společného jmenovatele pro potenciálně všechny implementace (něco jako Ingress pro L7 balancing, CNI pro síťové implementace apod.)

Dnes se chci podívat Linkerd.

Objekty, které budu používat, najdete na mém [Githubu](https://github.com/tkubica12/kubernetes-demo/tree/master/linkerd)

# Základní rozchození
Linkerd je skutečně odlehčená implementace a nenarve nám do clusteru desítky custom resourců a hromadu komponent. Je to vlastně docela jednoduché. Nejdřív si nainstaluje linkerd CLI.

```bash
export LINKERD_VERSION=stable-2.6.0
curl -sLO "https://github.com/linkerd/linkerd2/releases/download/$LINKERD_VERSION/linkerd2-cli-$LINKERD_VERSION-linux"
sudo -E mv linkerd2-cli-$LINKERD_VERSION-linux /usr/bin/linkerd
```

Teď si Linkerd nainstalujeme. Výhodou je, že tady není žádná magie (instalačka na tlačítko, která vám tam nacpe hodně věcí a nevíte pořádně co) a CLI vygeneruje přímo konkrétní objekty. Nejprve si můžeme dát check, že v clusteru nám nic nechybí a máme potřebná práva.

```bash
linkerd check --pre

kubernetes-api
--------------
√ can initialize the client
√ can query the Kubernetes API

kubernetes-version
------------------
√ is running the minimum Kubernetes API version
√ is running the minimum kubectl version

pre-kubernetes-setup
--------------------
√ control plane namespace does not already exist
√ can create Namespaces
√ can create ClusterRoles
√ can create ClusterRoleBindings
√ can create CustomResourceDefinitions
√ can create PodSecurityPolicies
√ can create ServiceAccounts
√ can create Services
√ can create Deployments
√ can create CronJobs
√ can create ConfigMaps
√ no clock skew detected

pre-kubernetes-capability
-------------------------
√ has NET_ADMIN capability
√ has NET_RAW capability

pre-linkerd-global-resources
----------------------------
√ no ClusterRoles exist
√ no ClusterRoleBindings exist
√ no CustomResourceDefinitions exist
√ no MutatingWebhookConfigurations exist
√ no ValidatingWebhookConfigurations exist
√ no PodSecurityPolicies exist

linkerd-version
---------------
√ can determine the latest version
‼ cli is up-to-date
    is running version 2.6.0 but the latest stable version is 2.6.1
    see https://linkerd.io/checks/#l5d-version-cli for hints

Status check results are √
```

Všechno je krásně zelené (teda až na to, že v době psaní článku už byla verze 2.6.1, ale to mi nevadí).

Co Linkerd vlastně instaluje? To se snadno dozvím, protože příkaz linkerd install jednoduše vygeneruje YAML soubory s potřebnými objekty (a může přijmout parametry pro doladění nastavení deploymentu jako je zapnutí/vypnutí mTLS šifrování a tak podobně). Prohlédl jsem si, jsem s tím OK a můžu je pipou poslat na deployment.

```bash
linkerd install | kubectl apply -f -
```

Co se nám tu objevilo? Pár Podů a jeden custom resource pro Linkerd a jeden pro Service Mesh Interface (Linkerd se rozhodl jednu z novějších funkcí implementovat rovnou podle SMI API).

```bash
$ kubectl get pods -n linkerd
NAME                                     READY   STATUS    RESTARTS   AGE
linkerd-controller-58ffd7f6fc-qjqdx      3/3     Running   0          10m
linkerd-destination-66db5b65bb-wjzk5     2/2     Running   0          10m
linkerd-grafana-798796985d-tnj86         2/2     Running   0          10m
linkerd-identity-5947579677-qmljv        2/2     Running   0          10m
linkerd-prometheus-5544b6b998-smp6x      2/2     Running   0          10m
linkerd-proxy-injector-b98487456-2qzt9   2/2     Running   0          10m
linkerd-sp-validator-d65c5dbf5-7hlcf     2/2     Running   0          10m
linkerd-tap-68b9fcfbfd-xtmhk             2/2     Running   0          10m
linkerd-web-6978b746df-vjq9x             2/2     Running   0          10m

$ kubectl get crd
NAME                                    CREATED AT
healthstates.azmon.container.insights   2020-01-01T13:54:11Z
serviceprofiles.linkerd.io              2020-01-07T11:22:54Z
trafficsplits.split.smi-spec.io         2020-01-07T11:22:54Z
```

Linkerd má i docela pěkné GUI.

```bash
linkerd dashboard
Linkerd dashboard available at:
http://localhost:50750
Grafana dashboard available at:
http://localhost:50750/grafana
Opening Linkerd dashboard in the default browser
Failed to open Linkerd dashboard automatically
Visit http://localhost:50750 in your browser to view the dashboard
```

![](/images/2020/2020-01-07-14-43-05.png){:class="img-fluid"}

![](/images/2020/2020-01-07-14-44-13.png){:class="img-fluid"}

Metriky rovněž vizualizuje připravenými dashboardy v Grafaně.

![](/images/2020/2020-01-07-14-45-26.png){:class="img-fluid"}

# Retry jako služba
Ve světě mikroslužeb už nejsou volání mezi komponentami součást jednoho procesu nebo prostředí, ale běhají po síti. Čas od času se pakety prostě ztratí nebo se daná služba nějak zaškobrtne, protože se zrovna škáluje, restartuje nebo něco podobného. Pokud hned po prvním neúspěchu vyhodíme error, asi to nebude optimální - měli bychom implementovat retry (a možná doplnit o circuit breaker, tedy "vyhlášení nedostupnosti").

Nasadíme si dvě služby - jednu client (ta bude jen pro zkoušení) a druhou službu s názvem retry. Vypadají takhle:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: client-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: client
  template:
    metadata:
      annotations:
        linkerd.io/inject: enabled
      labels:
        app: client
    spec:
      containers:
        - name: client
          image: tkubica/mybox
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retry-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: retry
  template:
    metadata:
      annotations:
        linkerd.io/inject: enabled
      labels:
        app: retry
    spec:
      containers:
      - name: retry-backend
        image: tkubica/retry-backend
        ports:
        - containerPort: 80
---
kind: Service
apiVersion: v1
metadata:
  name: retry-service
spec:
  selector:
    app: retry
  ports:
  - protocol: TCP
    name: http
    port: 80
    targetPort: 80
```

Nasadíme do clusteru. Všimněte si, že jsem definoval Pody s jedním kontejnerem, ale výpis ukazuje dva.

```bash
$ kubectl get pods
NAME                                READY   STATUS            RESTARTS   AGE
client-deployment-7d8567d9-94vtk    0/2     PodInitializing   0          47s
retry-backend-7c7c7dcf7c-9vm5p      0/2     Init:0/1          0          33s
retry-backend-7c7c7dcf7c-kbmx5      0/2     PodInitializing   0          32s
retry-backend-7c7c7dcf7c-kvpr9      0/2     PodInitializing   0          32s
```

Startují mi kontejnery, ale je tam číslovka 2. To je sidecar, ve které sedí reverse proxy našeho service mesh. Ještě jsem chytil jednu zajímavost - na výpisu je vidno, že je použit init kontejner. Ten se používá k tomu, že potřebujeme způsobit, že náš aplikační kontejner při komunikaci ven projde přes reverse proxy. Nechceme nijak upravovat aplikaci a předělávat ji na loopback nebo něco takového, takže potřebujeme pozměnit iptables. Init kontejner se o to postará, ale pozor - to vyžaduje privilegia navíc. Pokud je váš cluster bezpečnostně hodně utažen, může to selhat. Ostatně proto service mesh implementace pracují na řešení se zapouzdřením potřebných modifikací do CNI pluginu celého clusteru.

Já už mám Pody nahoře a skutečně tak Linkerd přihodil reverse proxy sidecar.

Takhle vypadá přidaný init kontejner, který si říká o práva navíc (NET_ADMIN a NET_RAW)

```yaml
initContainers:
  - args:
    - --incoming-proxy-port
    - "4143"
    - --outgoing-proxy-port
    - "4140"
    - --proxy-uid
    - "2102"
    - --inbound-ports-to-ignore
    - 4190,4191
    image: gcr.io/linkerd-io/proxy-init:v1.2.0
    imagePullPolicy: IfNotPresent
    name: linkerd-init
    resources:
      limits:
        cpu: 100m
        memory: 50Mi
      requests:
        cpu: 10m
        memory: 10Mi
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        add:
        - NET_ADMIN
        - NET_RAW
      privileged: false
      readOnlyRootFilesystem: true
      runAsNonRoot: false
      runAsUser: 0
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: FallbackToLogsOnError
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-rtg8n
      readOnly: true
```

A tady vidím sidecar.

```yaml
containers:
  - image: tkubica/retry-backend
    imagePullPolicy: Always
    name: retry-backend
    ports:
    - containerPort: 80
      protocol: TCP
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-rtg8n
      readOnly: true
  - name: linkerd-proxy
    env:
        ...
    image: gcr.io/linkerd-io/proxy:stable-2.6.0
    imagePullPolicy: IfNotPresent
    livenessProbe:
      failureThreshold: 3
      httpGet:
        path: /metrics
        port: 4191
        scheme: HTTP
      initialDelaySeconds: 10
      periodSeconds: 10
      successThreshold: 1
      timeoutSeconds: 1
    ports:
    - containerPort: 4143
      name: linkerd-proxy
      protocol: TCP
    - containerPort: 4191
      name: linkerd-admin
      protocol: TCP
    readinessProbe:
      failureThreshold: 3
      httpGet:
        path: /ready
        port: 4191
        scheme: HTTP
      initialDelaySeconds: 2
      periodSeconds: 10
      successThreshold: 1
      timeoutSeconds: 1
    resources: {}
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsUser: 2102
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: FallbackToLogsOnError
    volumeMounts:
    - mountPath: /var/run/linkerd/identity/end-entity
      name: linkerd-identity-end-entity
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-rtg8n
      readOnly: true
  dnsPolicy: ClusterFirst
  enableServiceLinks: true
```

Retry je moje miniaturní aplikace, jejíž zdrojáky najdete na mém GitHubu. V zásadě jí jako parametr předáme pravděpodobnost selhání. Pokud ji předám failRate=50 je to půl na půl, že mi vrátí normální výsledek (200) nebo proces havaruje a celý kontejner půjde dolu. Zkusím z client Podu přistoupit na retry službu a měl bych mít 50% šanci, že nedostanu žádnou odpověď a Pod umře.

```bash
export clientPod=$(kubectl get pods -l app=client -o jsonpath="{.items[0].metadata.name}")
kubectl exec $clientPod -c client -- curl -vs -m 30 retry-service?failRate=50
```

Teď pošleme do AKS konfiguraci, která zapne retry. Výsledkem by mělo být, že Linkerd mi session podrží a bude to zkoušet a doufejme, že zkusí další Pod a tam už to vyjde a pokud i ten umře, tak další a tak pořád dokola. Celkový limit mám 30 vteřin, tak je tu určitě i pravděpodobnost, že mám prostě velkou smůlu, ale měl bych vidět, že často odpověď dostanu, i když mezitím pár Podů popadalo (pokud v praxi vaše pody crashnou s pravděpodobností 50%, tak máte vážnější problém).

```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  creationTimestamp: null
  name: retry-service.default.svc.cluster.local
  namespace: default
spec:
  retryBudget:
    retryRatio: 0.2
    minRetriesPerSecond: 10
    ttl: 30s
  routes:
  - condition:
      method: GET
      pathRegex: /
    name: GET /
    isRetryable: true
```

Pošleme do clusteru a vyzkoušíme.

```bash
kubectl apply -f retryProfile.yaml
kubectl exec $clientPod -c client -- curl -vs -m 30 retry-service?failRate=50
```

Někdy přijde odpověď hned, máme štěstí. Někdy jde Pod do kolenou, ale session drží a dostaneme odpověď od jiného Podu.

# Load balancing
Standardní Kubernetes balancing (Service) je L4 řešení postavené na iptables nebo ipvs a typicky tak nabízí hash-based balancing nebo round robin. To nemusí být optimální a lepší by byl balancing typ least connection, který by bral v úvahu reálné aktuální počty spojení do každého uzlu. Ale to možná není ten největší problém - tím je HTTP/2 a něm postavené gRPC. Zatímco klasické HTTP/1.x je blokující (pošlu request a čekám na odpověď a dokud nepřijde, nic dalšího tam posílat nebudu), HTTP/2 umí krásně multi-plexovat různé requesty do jediného TCP spojení. Výsledek je, že klasické řešení vygeneruje několik TCP spojení a ty se dají na L4 balancovat (mají například jiný zdrojový TCP port), ale HTTP/2 je držák a z pohledu L4 není co balancovat. Řešením je vstoupit do komunikace na vyšších vrstvách, tedy L7 - proxy. Linkerd terminuje HTTP session z jedné strany a samo si navazuje HTTP spojení na druhou stranu. Na tu druhou stranu tak může sestavit HTTP/2 do každého běžícího Podu a sama proxy se teď může chytře rozhodovat co kudy pošle. Jinak řečeno díky service mesh je nejen balancing obecně efektivnější, ale řeší i situace s HTTP/2 (na kterém je postaveno gRPC), které normální Kubernetes "rozbijou".

# Canary podle procent
Klasickým problémem Kubernetes Service/Deployment je to, že o podílu distribuce provozu rozhoduje počet Podů (například máte service se selektorem na label app=mojeapp a 3-nodový deploment s labelem app=mojeapp,release=current a 1-nodový s app=mojeapp,release=canary - tedy canary dostává 25% provozu, ale zkuste si spočítat kolik CPU/RAM vás bude stát chtít jen 1% provozu na canary).

Takhle vypadá samotný deployment obou verzí služby a k tomu udělejme dvě separátní Service pro každou verzi a také jednu společnou.

```yaml
apiVersion: apps/v1beta2
kind: Deployment
metadata:
  name: myweb-deployment-v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myweb
      version: v1
  template:
    metadata:
      annotations:
        linkerd.io/inject: enabled
      labels:
        app: myweb
        version: v1
    spec:
      containers:
      - name: myweb
        image: tkubica/web:1
        env:
        - name: PORT
          value: "80"
        ports:
        - containerPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myweb-deployment-v2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myweb
      version: v2
  template:
    metadata:
      annotations:
        linkerd.io/inject: enabled
      labels:
        app: myweb
        version: v2
    spec:
      containers:
      - name: myweb
        image: tkubica/web:2
        env:
        - name: PORT
          value: "80"
        ports:
        - containerPort: 80
---
kind: Service
apiVersion: v1
metadata:
  name: myweb-service
  labels:
    app: myweb
spec:
  selector:
    app: myweb
  ports:
  - protocol: TCP
    name: http
    port: 80
    targetPort: 80
---
kind: Service
apiVersion: v1
metadata:
  name: myweb-service-v1
  labels:
    app: myweb
    version: v1
spec:
  selector:
    app: myweb
    version: v1
  ports:
  - protocol: TCP
    name: http
    port: 80
    targetPort: 80
---
kind: Service
apiVersion: v1
metadata:
  name: myweb-service-v2
  labels:
    app: myweb
    version: v2
spec:
  selector:
    app: myweb
    version: v2
  ports:
  - protocol: TCP
    name: http
    port: 80
    targetPort: 80
```

Pokud teď zkusíme službu myweb-service, bude 25% šance, že dostaneme v2. My ale chceme míň - jen 10%. Nastavme tedy TrafficSplit (Service Mesh Interface objekt, který Linkerd implementace využívá).

```yaml
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: myweb-service
spec:
  service: myweb
  backends:
  - service: myweb-service-v1
    weight: 900m
  - service: myweb-service-v2
    weight: 100m
```

Vyzkoušejme a dostaneme zhruba 10% v2.

```bash
export clientPod=$(kubectl get pods -l app=client -o jsonpath="{.items[0].metadata.name}")
kubectl exec $clientPod -c client -- bash -c 'while true; do curl -s myweb-service; echo; done'

$ kubectl exec $clientPod -c client -- bash -c 'while true; do curl -s myweb-service; echo; done'
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 65e343a5-0c98-49c5-ac62-f17a290cec77
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 012dc087-0875-4f3d-92a3-6f3ddde95d1e
Version 1: server id 012dc087-0875-4f3d-92a3-6f3ddde95d1e
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 65e343a5-0c98-49c5-ac62-f17a290cec77
Version 1: server id 012dc087-0875-4f3d-92a3-6f3ddde95d1e
Version 2: server id 0b3a99c7-3a8c-4f38-abbc-6b9a2ead9a4f
Version 1: server id 65e343a5-0c98-49c5-ac62-f17a290cec77
Version 2: server id d8ffaea9-1d04-4095-a030-b4f3052ff523
Version 1: server id 012dc087-0875-4f3d-92a3-6f3ddde95d1e
Version 1: server id 65e343a5-0c98-49c5-ac62-f17a290cec77
Version 2: server id 5da9e4df-d639-49a4-92b2-6a007b27c748
Version 1: server id 012dc087-0875-4f3d-92a3-6f3ddde95d1e
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 2: server id 0b3a99c7-3a8c-4f38-abbc-6b9a2ead9a4f
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
Version 1: server id 65e343a5-0c98-49c5-ac62-f17a290cec77
Version 1: server id 35457bc8-647e-4c44-b495-6f063173cda7
```

# Šifrování a ověřování mikroslužeb mezi sebou
Linkerd pro nás automaticky zařídil šifrování provozu mezi mikroslužbami. Je samozřejmě otázka do jaké míry je to pro vás zásadní, ale v rámci zero trust přístupu můžete auditory ohromit tím, že každá vaše mikroslužba má svůj vlastní vystavený certifikát, jejich komunikace uvnitř clusteru jsou vzájemně těmito certifikáty ověřené a vše je šifrováno přes TLS. Ve finále tak nody vašeho Kubernetes clusteru mohou být propojeny veřejným hotspotem mcdonalds a jste stále v pohodě.

Jak to ověříme? Využijeme schopnosti Linkerd reportovat provoz. Zapnu si TAP v příkazové řádce a z client Podu spustím curl na myweb a podíváme se, co jsme chytili.

```bash
export clientPod=$(kubectl get pods -l app=client -o jsonpath="{.items[0].metadata.name}")
linkerd tap pod/$clientPod -o json
kubectl exec $clientPod -c client -- curl -s myweb-service
```

Dostávám opravdu velmi detailní informace a v nich vidím, že Linkerd zapnul tls šifrování.

```json
{
  "source": {
    "ip": "192.168.1.4",
    "port": 50224,
    "metadata": {
      "control_plane_ns": "linkerd",
      "deployment": "client-deployment",
      "namespace": "default",
      "pod": "client-deployment-7d8567d9-94vtk",       
      "pod_template_hash": "7d8567d9",
      "serviceaccount": "default",
      "tls": "loopback"
    }
  },
  "destination": {
    "ip": "192.168.1.41",
    "port": 80,
    "metadata": {
      "control_plane_ns": "linkerd",
      "deployment": "myweb-deployment-v1",
      "namespace": "default",
      "pod": "myweb-deployment-v1-6dbf9565c8-4rqw7",   
      "pod_template_hash": "6dbf9565c8",
      "server_id": "default.default.serviceaccount.identity.linkerd.cluster.local",
      "service": "myweb-service-v1",
      "serviceaccount": "default",
      "tls": "true"
    }
  },
  "routeMeta": null,
  "proxyDirection": "OUTBOUND",
  "responseInitEvent": {
    "id": {
      "base": 31,
      "stream": 62
    },
    "sinceRequestInit": {
      "nanos": 1619402
    },
    "httpStatus": 200,
    "headers": [
      {
        "name": "date",
        "valueStr": "Wed, 08 Jan 2020 17:21:40 GMT"    
      },
      {
        "name": "content-length",
        "valueStr": "57"
      },
      {
        "name": "content-type",
        "valueStr": "text/plain; charset=utf-8"        
      }
    ]
  }
}
```

# Vizibilia
Linkerd dokáže vizualizovat komunikační toky uvnitř Kubernetes clusteru. Tak například TAP z předchozího příkazu, byť s menší mírou detailu, najdu pohodlně i v GUI.

![](/images/2020/2020-01-08-18-11-33.png){:class="img-fluid"}

Můžu v reálném čase sledovat nejdůležitější toky mezi pody, deploymenty, službami nebo namespace.

![](/images/2020/2020-01-08-18-25-26.png){:class="img-fluid"}

Co ověřit si, jak je na tom Traffic Split, který jsme před chvilkou nakonfigurovali? Vrací obě verze návratové hodnoty 200 nebo je tu určitá míra selhání? Jaké jsou tam latence?

![](/images/2020/2020-01-08-18-26-20.png){:class="img-fluid"}

Co si třeba zobrazit Pody a jejich síťové statistiky?

![](/images/2020/2020-01-08-18-26-50.png){:class="img-fluid"}

Kliknutím na ikonku Grafany se dostanu do podrobnější vizualizace například konkrétního Podu.

![](/images/2020/2020-01-08-18-27-54.png){:class="img-fluid"}

![](/images/2020/2020-01-08-18-28-30.png){:class="img-fluid"}

![](/images/2020/2020-01-08-18-29-13.png){:class="img-fluid"}

V neposlední řadě může Linkerd sloužit jako exportér distribuovaného trasování. Bohužel v této oblasti je mnoho formátů (včetně standardizovaného OpenTelemetry pod křídly CNCF), ale i různé jiné formáty a vizualizace (App Insights, Zipkin, Jeager, Emojivoto, OpenCensus, OpenTracing). Je to široké téma, které si necháme na jindy - ale je vhodné na tomto místě zmínit, že Linkerd v procesu trasování může participovat.


Dnes jsme si vyzkoušeli Linkerd. Service Mesh pro Kubernetes, jehož hlavními výhodami jsou:
- Nízká spotřeba zdrojů
- Nízká přidaná latence
- Jednoduchost
- Nativní podpora SMI API
- Projekt dohlížený CNCF

Příště se vrhneme na Isto a zaměříme se na funkce, s kterými jde dál, než jakýkoli jiný současný service mesh.