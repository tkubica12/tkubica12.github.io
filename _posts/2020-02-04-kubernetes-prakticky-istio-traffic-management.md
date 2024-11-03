---
layout: post
title: 'Kubernetes praticky: nejmocnější Service Mesh část 2 - traffic management'
tags:
- Kubernetes
- Networking
- ServiceMesh
---
Minule jsme si prošli základní věci typu retry, circuit breaker a dnes se pustíme do pokročilého směrování provozu. Budeme pokračovat s prostředím z minula, kdy Istio jako takové mám zprovozněno a pustili jsme si dva deploymenty, každý v jiné verzi.

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
```

Kromě toho nasadíme další Pod, z kterého to budeme zkoušet.

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
      labels:
        app: client
    spec:
      containers:
        - name: client
          image: tkubica/mybox
```

# Canary release
Pokud teď budeme z client Podu přistupovat na aplikaci, budeme dostávat odpovědi v poměru, v jakém jsou počty Podů - mám 3 nové verze, 3 staré verze, takže to bude půl na půl.

```bash
export clientPod=$(kubectl get pods -l app=client -o jsonpath="{.items[0].metadata.name}")
kubectl exec $clientPod -c client -- bash -c 'while true; do curl -s myweb-service; echo; done'

Version 1: server id e307911d-5f12-47ec-a158-cb828fbe418a
Version 1: server id 2b1960d8-bf7d-47cb-bf4a-eb3ca464a6dd
Version 1: server id b47cb71c-6fda-47d7-8a51-5648b9572179
Version 2: server id c285cc5d-f18d-4403-8149-42328f16af08
Version 1: server id 2b1960d8-bf7d-47cb-bf4a-eb3ca464a6dd
Version 2: server id c2e141cb-ae05-41e0-bcf8-c250e83c351d
Version 2: server id c2e141cb-ae05-41e0-bcf8-c250e83c351d
Version 1: server id 2b1960d8-bf7d-47cb-bf4a-eb3ca464a6dd
Version 2: server id d4f8f350-543d-4d82-af84-da75766931dc
Version 1: server id b47cb71c-6fda-47d7-8a51-5648b9572179
Version 2: server id c2e141cb-ae05-41e0-bcf8-c250e83c351d
Version 1: server id 2b1960d8-bf7d-47cb-bf4a-eb3ca464a6dd
Version 1: server id 2b1960d8-bf7d-47cb-bf4a-eb3ca464a6dd
```

Co když ale budu chtít poslat 1% provozu na v2 - to bych musel mít 99 replik v1 a to je nesmysl. Istio nám umožňuje oddělit toto rozhodnutí od počtu instancí. Založíme si objekt VirtualService a zvolíme váhy pro směrování na v1 a v2. Ty se vzali kde? V objektu DestinationRule nadefinujeme jejich mapování na label.

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: istio-canary
spec:
  hosts:
  - myweb-service
  http:
  - route:
    - destination:
        host: myweb-service
        subset: v1
      weight: 90
    - destination:
        host: myweb-service
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: istio-canary
spec:
  host: myweb-service
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

Pošleme do clusteru a zkusíme přístupy. Měli bychom teď vidět v1 daleko častěji.

```bash
kubectl apply -f canary10percent.yaml
kubectl exec $clientPod -c client -- bash -c 'while true; do curl -s myweb-service; echo; done'

Version 1: server id 2b1960d8-bf7d-47cb-bf4a-eb3ca464a6dd
Version 1: server id b47cb71c-6fda-47d7-8a51-5648b9572179
Version 1: server id e307911d-5f12-47ec-a158-cb828fbe418a
Version 1: server id 2b1960d8-bf7d-47cb-bf4a-eb3ca464a6dd
Version 1: server id e307911d-5f12-47ec-a158-cb828fbe418a
Version 1: server id e307911d-5f12-47ec-a158-cb828fbe418a
Version 1: server id e307911d-5f12-47ec-a158-cb828fbe418a
Version 2: server id c285cc5d-f18d-4403-8149-42328f16af08
Version 1: server id 2b1960d8-bf7d-47cb-bf4a-eb3ca464a6dd
Version 1: server id e307911d-5f12-47ec-a158-cb828fbe418a
Version 1: server id e307911d-5f12-47ec-a158-cb828fbe418a
```

Výborně. Dáme politiku zase pryč.

```bash
kubectl delete -f canary10percent.yaml
```

# A/B testing
Dalším případem chytrého směrování bude A/B testing. O tom kdo dostane v2 nechceme nechat rozhodovat náhodu, ale pošleme tam třeba provoz beta uživatelů. Pokud by šlo o v2 nějakého externě přístupného API, vystačíme s Ingress objektem, ale mohou být případy, kdy to potřebujeme u vnitřního volání (tedy externí API neměníme, ale to jaké vnitřní API volá ano). Istio umožňuje tohle udělat podle cookie. Dejme tomu, že mobilní aplikace dává uživatelům možnost zapnout "preview" funkce, což způsobí, že každé volání bude mít přidanou sušenku usertype=tester a všechna API volání budou tuto hodnotu mezi sebou přeposílat. 

Nejdříve tedy nastavíme VirtualService takhle:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: istio-canary
spec:
  hosts:
  - myweb-service
  http:
  - match:
    - headers:
        cookie:
          regex: "^(.*?;)?(usertype=tester)(;.*)?$"
    route:
      - destination:
          host: myweb-service
          subset: v2
  - route:
    - destination:
        host: myweb-service
        subset: v1
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: istio-canary
spec:
  host: myweb-service
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

Pošleme do clusteru a vyzkoušíme. Bez sušenky dostávám v1, se správnou cookie v2.

```bash
kubectl apply -f canaryCookie.yaml
kubectl exec $clientPod -c client -- curl -s myweb-service
Version 1: server id b47cb71c-6fda-47d7-8a51-5648b9572179

kubectl exec $clientPod -c client -- curl -s --cookie "usertype=tester" myweb-service
Version 2: server id c285cc5d-f18d-4403-8149-42328f16af08
```

# Provoz odcházející z Istio
V běžné Kubernetes instalaci máte k dispozici Network Policy (například v AKS je Azure implementace nebo Calico), která vám umožní podle labelů přiřazovat politiky jednotlivým Podům a to včetně omezování komunikace směrem ven. Můžete tak například zakázat odchozí provoz na public IP. Nicméně dost možná potřebujete pravidla řešit trochu detailněji, třeba stavově nebo podle FQDN.

První možností je nechat to až na něco za Kubernetem, například Azure Firewall, na kterém se dají řešit nejen L4 pravidla, ale i FQDN záznamy. To je určitě dobré v tom, že si to pod správu vezme síťový nebo bezpečnostní tým a přes Azure Policy / RBAC bude jasné, že provozovatelé AKS nebudou moci firewall obejít.

Možná ale chcete i tuto problematiku řešit identickým způsobem přes Kubernetí YAML objekty. Vyzkoušíme si to.

Nejdřív skočíme do jednoho z Podů a ubezpečíme se, že odchozí provoz do Internetu normálně jede.

```bash
kubectl exec $clientPod -c client -- curl -vs httpbin.org/ip

*   Trying 34.230.193.231...
* TCP_NODELAY set
* Connected to httpbin.org (34.230.193.231) port 80 (#0)
> GET /ip HTTP/1.1
> Host: httpbin.org
> User-Agent: curl/7.58.0
> Accept: */*
>
< HTTP/1.1 200 OK
< date: Fri, 31 Jan 2020 11:18:32 GMT
< content-type: application/json
< content-length: 33
< server: envoy
< access-control-allow-origin: *
< access-control-allow-credentials: true
< x-envoy-upstream-service-time: 181
<
{ [33 bytes data]
* Connection #0 to host httpbin.org left intact
{
  "origin": "52.149.111.103"
}
```

Je to tak. Pojďme teď změnit výchozí nastavení Istio tak, že je blokované úplně všechno, dokud něco nepovolíme. To uděláme modifikací ConfigMap jedné z Istio komponent.

```bash
kubectl get configmap istio -n istio-system -o yaml | sed 's/mode: ALLOW_ANY/mode: REGISTRY_ONLY/g' | kubectl replace -n istio-system -f -
```

Zkusme to ještě jednou. Tentokrát už to nejde, dostáváme chybu 502.

```bash
kubectl exec $clientPod -c client -- curl -vs httpbin.org/ip

*   Trying 3.232.168.170...
* TCP_NODELAY set
* Connected to httpbin.org (3.232.168.170) port 80 (#0)
> GET /ip HTTP/1.1
> Host: httpbin.org
> User-Agent: curl/7.58.0
> Accept: */*
>
< HTTP/1.1 502 Bad Gateway
< location: http://httpbin.org/ip
< date: Fri, 31 Jan 2020 11:20:05 GMT
< server: envoy
< content-length: 0
<
* Connection #0 to host httpbin.org left intact
```

Pojďme teď vytvořit ServiceEntry, která povolí přístup na endpoint httpbin.org, ale ne třeba na ifconfig.io.

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: httpbin-ext
spec:
  hosts:
  - httpbin.org
  ports:
  - number: 80
    name: http
    protocol: HTTP
```

Pošleme to do clusteru a uvidíme, že httpbin.org nám funguje, ale ifconfig.io ne.

```bash
kubectl create -f serviceEntry.yaml
kubectl exec $clientPod -c client -- curl -vs httpbin.org/ip

*   Trying 3.232.168.170...
* TCP_NODELAY set
* Connected to httpbin.org (3.232.168.170) port 80 (#0)
> GET /ip HTTP/1.1
> Host: httpbin.org
> User-Agent: curl/7.58.0
> Accept: */*
>
{
  "origin": "52.149.111.103"
}
< HTTP/1.1 200 OK
< date: Fri, 31 Jan 2020 12:14:58 GMT
< content-type: application/json
< content-length: 33
< server: envoy
< access-control-allow-origin: *
< access-control-allow-credentials: true
< x-envoy-upstream-service-time: 208
<
{ [33 bytes data]
* Connection #0 to host httpbin.org left intact

kubectl exec $clientPod -c client -- curl -vs ifconfig.io

* Rebuilt URL to: ifconfig.io/
*   Trying 104.24.122.146...
* TCP_NODELAY set
* Connected to ifconfig.io (104.24.122.146) port 80 (#0)
> GET / HTTP/1.1
> Host: ifconfig.io
> User-Agent: curl/7.58.0
> Accept: */*
>
< HTTP/1.1 502 Bad Gateway
< location: http://ifconfig.io/
< date: Fri, 31 Jan 2020 12:15:25 GMT
< server: envoy
< content-length: 0
<
* Connection #0 to host ifconfig.io left intact
```

# Provoz přicházející do Istio
Když chci vystavit nějakou http-based službu ven, použiji Ingress - standardizovaný způsob definice takového požadavku, který na backendu může mít různé implementace jako je Nginx, Traefik, Azure Application Gateway a tak podobně. Linkerd service mesh se s Ingress kombinuje, Istio ale nabízí svou vlastní alternativu. Z pohledu sběru telemetrie, vizualizace nebo troubleshootingu může dávat smysl mít i tyto potřeby pokryté jedním systémem. Pokud bych si na Istio vytvořil dependenci ve všech clusterech a řešeních, preferoval bych využít Istio kompletně. Na druhou stranu pokud většina mých aplikací a clusterů musí být univerzální i bez Istio, pak bych zůstal u Ingress.

Vymažeme si předchozí VirtualService a použijeme novou bez canary směrování a referencí na gateway.

```bash
kubectl delete virtualservice istio-canary
kubectl create -f gateway.yaml
```

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: istio-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "myweb-service.domain.com"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: gateway-service
spec:
  hosts:
  - myweb-service.domain.com
  gateways:
  - istio-gateway
  http:
  - route:
    - destination:
        host: myweb-service
```

Principiálně je to vlastně stejně jako Ingress. Vyzkoušíme.

```bash
export istioGwIp=$(kubectl get service istio-ingressgateway -n istio-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -i $istioGwIp -H "Host:myweb-service.domain.com"

HTTP/1.1 200 OK
date: Fri, 31 Jan 2020 13:10:41 GMT
content-length: 57
content-type: text/plain; charset=utf-8
x-envoy-upstream-service-time: 27
server: istio-envoy

Version 2: server id d4f8f350-543d-4d82-af84-da75766931dc
```


Dnes jsme si vyzkoušeli chytré směrování provozu mezi službami z pohledu kanárků i A/B testování a ukázali si jak kontrolovat provoz dovnitř a ven z clusteru. Canary je ideální automatizovat například s použitím Flagger, na což se brzy také podíváme. V oblasti service mesh bych se chtěl ještě vrhnout na distribuovaný tracing a prozkoumat jaké možnosti integrace různých prostředí s kontejnery i bez nabízí třetí zajímavý hráč - Consul Connect.

