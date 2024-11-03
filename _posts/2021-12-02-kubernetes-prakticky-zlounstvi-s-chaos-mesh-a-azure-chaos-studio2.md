---
layout: post
title: 'Kubernetes prakticky: zlounství s Chaos Mesh a Azure Chaos Studio'
tags:
- Kubernetes
---
Nedávno přišla do preview služba Azure Chaos Studio - řešení pro zlouny toužící po šíření chaosu ve svém vlastním prostředí. To, jak dokáže provádět a orchestrovat záškodnickou činnost na Azure službách a síťařině, ve virtuálkách (DNS problémy, zabíjení procesů, simulace síťových potíží) a Kubernetes se podíváme hned příště. Ještě před tím bych ale rád prošel open source projekt Chaos Mesh - komponentu, kterou Azure Chaos Studio používá pro Kubernetes.

Dnes tedy zkusíme Chaos Mesh napřímo a bude vám fungovat kdekoli i bez Azure. 

K čemu je to dobré? Typicky se potřebujete ujistit, že pocit "máme to redundantní, takže cajk" bude i skutečností, když se to opravdu stane. Možná se chcete ubezpečit, že jste schopni monitorovat situaci a sbíráte potřebné signály, takže umíte rychle identifikovat problém. V neposlední řadě je důležité zažít si to, například vidět, jak to vypadá, když vám chyba v jedné aplikace začne nekontrolovatelně požírat libovolné množství paměti, ke které se dostane. S orchestrací přes Azure Chaos Studio je to ideální začlenit do vaší CI/CD pipeline před nasazením do produkce (a mimochodem pro generování a měření provozu můžete použít novou Azure Load Testing Service).

# Chaos Mesh - instalace a ruční rozchození
Nejprve si nahodím Azure Kubernetes Service.

```bash
az group create -n chaosmesh -l westeurope
az aks create -n chaosmesh -g chaosmesh -c 1 -x -s Standard_B2ms 
az aks get-credentials -n chaosmesh -g chaosmesh
```

Nainstaluji projekt Chaos Mesh.

```bash
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update
kubectl create ns chaos
helm upgrade -i chaos-mesh chaos-mesh/chaos-mesh --namespace=chaos --version 2.0.3 --set chaosDaemon.runtime=containerd --set chaosDaemon.socketPath=/run/containerd/containerd.sock
```

Nasadím tyto aplikace.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp1
  template:
    metadata:
      labels:
        app: myapp1
    spec:
      containers:
      - name: myapp1
        image: nginx
        resources:
          limits:
            memory: "64Mi"
            cpu: "250m"
        ports:
        - containerPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp2
  template:
    metadata:
      labels:
        app: myapp2
    spec:
      containers:
      - name: myapp2
        image: nginx
        resources:
          limits:
            memory: "64Mi"
            cpu: "250m"
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: myapp1
spec:
  selector:
    app: myapp1
  ports:
  - port: 80
    targetPort: 80
```

To bychom měli, kapitán Chaos může nastoupit.

## Zabiják jehňátek (Podů)
První jednoduchá záškodnická akce bude o sestřelování Podů. Je dost důležité vědět, jak se vaše aplikace v takové situaci chová, protože k tomu bude běžně docházet při upgradech clusteru, havárii nodu a tak podobně. Celý test definujete jako CRD a obsahuje řadu zajímavých nastavení. Můžete střílet pouze jeden Pod, ale také hnedle několik a to buď fixní počet, fixní procento nebo náhodné procento se stanoveným maximem. Důležité je říct na koho se zaměříme, tedy určit selector. Já si vyberu podle namespace, ale použít můžete i label, což je skvělé pro případ, že potřebujete otestovat nějakou specifickou komponentu aplikace.

Takhle vypadá jednoduchý zabiják.


```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-killer
  namespace: default
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces:
      - default
```

Protože zatím jedeme napřímo bez nějaké orchestrace nad tím (tou by bylo Azure Chaos Studio), tak použiji rovnou pravidelné zabíjení každé dvě minuty.

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Schedule
metadata:
  name: pod-killer-schedule
spec:
  schedule: '*/2 * * * *'
  historyLimit: 2
  concurrencyPolicy: 'Allow'
  type: 'PodChaos'
  podChaos:
    action: pod-kill
    mode: one
    selector:
      namespaces:
        - default
```

Pošlu do clusteru a sleduji co se děje a ano, vidím Pody umírat co dvě minuty.

```bash
kubectl get pod -w

NAME                      READY   STATUS    RESTARTS   AGE
myapp1-64749fd6db-dcddx   1/1     Running   0          35m
myapp1-64749fd6db-mfdcq   1/1     Running   0          37m
myapp1-64749fd6db-mrvrq   1/1     Running   0          37m
myapp2-84c8c6487d-tlbpx   1/1     Running   0          37m
myapp2-84c8c6487d-vwlwd   1/1     Running   0          37m
myapp2-84c8c6487d-xlmrc   1/1     Running   0          37m
myapp2-84c8c6487d-vwlwd   1/1     Terminating   0          37m
myapp2-84c8c6487d-vwlwd   1/1     Terminating   0          37m
myapp2-84c8c6487d-q4j6p   0/1     Pending       0          0s
myapp2-84c8c6487d-q4j6p   0/1     Pending       0          0s
myapp2-84c8c6487d-q4j6p   0/1     ContainerCreating   0          0s
myapp2-84c8c6487d-q4j6p   1/1     Running             0          3s
myapp1-64749fd6db-mrvrq   1/1     Terminating         0          39m
myapp1-64749fd6db-mrvrq   1/1     Terminating         0          39m
myapp1-64749fd6db-s2mz7   0/1     Pending             0          0s
myapp1-64749fd6db-s2mz7   0/1     Pending             0          0s
myapp1-64749fd6db-s2mz7   0/1     ContainerCreating   0          0s
myapp1-64749fd6db-s2mz7   1/1     Running             0          2s
```

Samozřejmě jak vidno mám víc replik a Kubernetes nahazuje nové Pody. V tento moment je to samozřejmě potřeba kombinovat s nějakým monitoringem - potřebuji vidět, jestli takové záškodnictví má dopad na uživatele. Představte si například ideální stav, že tohle celé je součást automatizovaného testu na základě pull requestu. Aplikace se nasadila v testovacím prostředí a teď se do ní buší (třeba z Azure Load Testing Service). Sbírá se telemetrie (třeba Azure Monitor) a ta bude kritériem pro přijmutí pull requestu nebo posunutí CI/CD pipeline do dalšího stage. Pokud se v nové verzi někomu podařilo zanést nějakou změnu s nežádoucím dopadem na dostupnost (například není tam minimální počet replik větší než jedna nebo ukončený Pod nekorektně uzavře data, takže jeho náhrada nenaběhne), je šance, že ji takhle chytíme. V každém případě držíme všechny zúčastněné ve střehu.

## Práce pod tlakem
Jak se bude vaše aplikace nebo dokonce celý cluster chovat při tlaku na CPU nebo paměť? Například pokud používáte velký overcommit (rozdíl mezi resource requests a resource limits) co se stane, když někdo začne zdroje opravdu hodně požírat (nemáte requests tak nízko, že to bude nakonec problém, protože to ve skutečnosti není minimum nutné pro běh)? Jak se bude aplikace chovat, když se objeví memory leak (simulovaný chaosem ve formě požrání paměti) a repliku zabije OOMKiller nebo když se zvedne zátěž CPU o 50% (poznáte to a přidáte repliku)? Jak ovlivní přetížení CPU schopnost vaší aplikace logovat - budete schopni zjistit, že se to stalo? Jak ovlivní jeden špatný Pod ostatní (například nedojde k nějaké evakuaci jiných na jiné nody a případné negativní efekty s tím spojené)?

Vyzkouším tenhle jednoduchý stresor, tentokrát změřený na jeden Pod z těch s určitým labelem.

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: stressor
  namespace: default
spec:
  mode: one
  selector:
    labelSelectors:
      'app': 'myapp1'
  stressors:
    memory:
      workers: 1
      size: '256MB'
    cpu:
      workers: 2
      load: 30
```

Po chvilce vidím, že mi zátěž opravdu vyrostla.

```bash
kubectl top pods

NAME                      CPU(cores)   MEMORY(bytes)   
myapp1-795f487f4b-8nzg4   0m           3Mi
myapp1-795f487f4b-fq8kd   0m           3Mi
myapp2-5b6ddc77d-mj82c    0m           3Mi
myapp2-5b6ddc77d-qfhqr    0m           3Mi

NAME                      CPU(cores)   MEMORY(bytes)   
myapp1-795f487f4b-8nzg4   251m         49Mi
myapp1-795f487f4b-fq8kd   0m           3Mi
myapp2-5b6ddc77d-mj82c    0m           3Mi
myapp2-5b6ddc77d-qfhqr    0m           3Mi
```

## Nakousnutý drát
V síťové komunikaci se může stát ledacos. Pokud jste byli zvyklí na monolit, kde veškeré komunikace mezi komponentami byly v rámci procesu (takže buď všechno funguje rychle, vyrovnaně a spolehlivě nebo to celé žuchne a nefunguje vůbec nic), s mikroslužbami v Kubernetes clusteru to bude o poznání veselejší. Teoreticky může dojít k nějakému odstřihnutí služby od sítě (třeba omyl v síťovém pravidlu apod.), v síti (například ve firewallu třetí strany, přes který komunikujete ven) nebo v síťovém stacku hostitele může třeba dojít k nějakým potížím (zvýšená latence, zahozené pakety, změna pořadí paketů) nebo je přetížený spoj (jede to, ale pomalu). To všechno umí Chaos Mesh nasimulovat - je vaše aplikace schopná se z toho oklepat? Má retry? Má circuit breaker? Jste schopni to monitoringem zjistit? Tohle všechno jsou vždy velmi nepříjemné věci k řešení - když něco nefunguje, je to často jednodušší zjistit a vyřešit, než když to jede nějak divně.

Skočil jsem do jednoho Podu a změřil jak dlouho trvá curl na nějakou službu v Internetu (použil jsem ipconfig.io).

```bash
kubectl exec -ti $(kubectl get pods -l app=myapp1 -o jsonpath="{.items[0].metadata.name}") -- bash
    time curl ipconfig.io
    20.76.144.79

    real    0m0.209s
    user    0m0.012s
    sys     0m0.000s
```

Teď dotoho vpustíme trochu chaosu.

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: delay
spec:
  action: delay
  mode: all
  selector:
    namespaces:
      - default
    labelSelectors:
      app: myapp1
  delay:
    latency: '500ms'
    jitter: '0ms'
```

Ono latence 500ms, pche, řeknete si. Jenže ono sestavit takové TCP spojení (a pak třeba nad tím ještě TLS) je několikrát tam a zpět, takže ono se to docela nasčítá.

```bash
kubectl exec -ti $(kubectl get pods -l app=myapp1 -o jsonpath="{.items[0].metadata.name}") -- bash
    time curl ipconfig.io
    20.76.144.79

    real    0m3.886s
    user    0m0.007s
    sys     0m0.007s
```

## Ta služba se snad zbláznila
Chaos Mesh dokáže ještě jednu hezkou věc - může zafungovat jako http proxy a způsobit nejen chaos infrastrukturní, ale i aplikační (je tam zatím omezení jen na http komunikaci, https neumí, takže pro externí věci asi problém, nicméně vnitřní volání v clusteru jsou často ještě http a někomu to nevadí nebo to vyřeší použitím service mesh). Co když mi API najednou začne vracet nesmysly? Chaos Mesh umí přes svou proxy modifikovat odpověď služby (vyměnit nějaké políčko, třeba do pole, kde se čeká číslo dát řetězec) nebo poslat vlastní body. Co s tím tazatel udělá? Nedojde k nějakému zhroucení nebo dokonce poškození dat?

Z jednoho Podu pošlu dotaz na aplikaci myapp1, kde je holý NGINX.

```bash
kubectl exec -ti $(kubectl get pods -l app=myapp2 -o jsonpath="{.items[0].metadata.name}") -- curl http://myapp1
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
...
```

Jdu aplikovat HTTP chaos a přeplácnout body svým (zakódováno v base64).

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: HTTPChaos
metadata:
  name: http-patch
  namespace: default
spec:
  mode: all
  selector:
    namespaces:
      - default
    labelSelectors:
      app: myapp1
  target: Response
  port: 80
  # method: GET
  # path: /json
  replace:
    body: eyJpcCI6ICJqZWpkYVRvaGxlSmVTdHJpbmcifQ==
  duration: 2m
```

Zeptám se znova.

```bash
kubectl exec -ti $(kubectl get pods -l app=myapp2 -o jsonpath="{.items[0].metadata.name}") -- curl http://myapp1
{"ip": "jejdaTohleJeString"}
```

## Další vlastnosti Chaos Mesh
Chaos Mesh umí ještě další akce. Je tam celá kategorie kolem File IO - to jsem na první dobrou nerozchodil, ale někdy se k tomu vrátím. To by mělo simulovat věci jako je odmítnutí IO k souboru, zvýšená latence a tak podobně. To se reálně může snadno stát - například pokud místo dedikovaného storage (třeba PVC s diskem nebo Azure Files) použijete emptyDir, kdy to běží na stejném disku i pro ostatní Pody. Je tu i možnost simulovat chyby Linux kernelu (to je ve výchozím stavu vypnuté - tohle může mít dost vliv na celý cluster), speciální věci pro JVM, manipulace s časem nebo chyby DNS (přetížení nebo pomalejší reakce DNS je často zdrojem obtížně zjistitelných chyb, takže pocvičit se v tom nebude špatné).

Chaos Mesh má i docela povedené GUI nebo možnost definovat celá workflow. Pokud vám jde jen o Kubernetes, určitě velmi dobře použitelné.

Já ale budu chtít všechny tyhle skvělé funkce dostat do kontextu Azure Chaos Studia, abych mohl přímo z Azure experimenty řídit a využívat chaosu i přes agenty ve VM nebo v cloudové platformě jako takové. Jdu na to, uslyšíme se příště.
