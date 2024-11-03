---
layout: post
published: true
title: 'Postupné nasazování kanárků s Open Service Mesh a Flagger v Kubernetes'
tags:
- Kubernetes
---
Nová verze mikroslužby? Pojďme ji nasadit a poslat na ní 5% zákazníků (nebo vyberme beta testery podle headeru či cookie). Sbírejme si statistiku do monitoringu - neobjevují se u nové verze chyby (4xx, 5xx)? Jaká je doba odbavení dotazu, akceptovatelná? Pokud je v těchto ohledech vše v pořádku třeba po dobu dvou minut, přitočme - pošleme 10% zákazníků na novou verzi. Další dvě minuty sledujme monitoring - je to dobré? Přihoďme dalších 5%. Už jsme na 50% a stále všechny metriky říkají, že je vše ok? Překlopme to, pustíme novou verzi všem.

Jak tohle automatizovat a to ještě k tomu deklarativním způsobem? Dnes se podíváme na Flagger v kombinaci s Open Service Mesh v AKS.

# Progressive delivery v infrastruktuře vs. aplikaci
Laický popis včetně analogií kadeřnictví pro techniky jako je canary, green/blue nebo A/B testing jsem na tomto blogu už popisoval. Pro dnešní téma bude ale důležité srovnat si varianty infrastrukturního řešení vs. integrace do aplikace.

## Aplikační řešení - feature flags (feature toggles)
První cestou jak řešit postupné nasazování je zakomponováním této funkce přímo do aplikace. Ta si tak při startu zjistí svou konfiguraci v podobě feature flagů a zjistí, jaké funkce jsou aktivní nebo na jaký backend se obrací. Tohle má zásadní výhodu v tom, že kód aplikace už nové funkce obsahuje, jen nejsou pro uživatele vidět. To oceníte zejména, když kód běží na straně klienta a jeho aktualizace by byla velká nebo pomalá (XBOX hra, mobilní aplikace). Přes flagy oddělujete nasazení kódu od nasazení funkce - do lidí to dostanete už týden před tím a na tiskové konferenci doslova zmáčknete jedno tlačítko a rozsvítíte novou vlastnost na mobilech vašich zákazníků.

Tohle je myslím skvělé pro experimenty s novou aplikační funkcí, novými GUI prvky a tak nějak celkově na úrovni frontendu. Vede to na to, že takových flagů by mělo být relativně málo - jen pár beta-funkcí před jejich spuštění všem. Nezdá se mi to dobré řešení na změny v backendu, kdy jsou nové verze nasazované třeba několikrát týdně pro jednu mikroslužbu a těch může být například padesát. Ano - flag by mohl konfigurovat odlišné endpointy a takové věci, ale to už by bylo dost komplikované - navíc změna (přitáčení počtu uživatelů) progresivně v řádu minut je asi dost nereálná.

## Infrastrukturní řešení - chytré směrování
Jinou variantou je nasadit novou verzi vedle té původní a na chytrém směrovači řešit co se kam pošle - ať už náhodně procentem nebo headerem a tak podobně. To má následující výhody:
- Aplikace to nemusí nijak přímo podporovat, takže se to hodí i pro komponenty třetích stran, od externích dodavatelů nebo jiných týmů. To také snižuje riziko vzniku chyb kvůli úpravě aplikace nebo zvýšená složitost toho, že aplikace musí obsahovat současně starší i novou funkci (což může teoreticky vést na nějaké nechtěné interakce).
- Změna je okamžitá a nezávisí na uživateli ani aplikaci, takže je to vhodné pro progresivní nasazování s kroky v minutách.

Z toho pro mne plyne, že tento model je naprosto ideální pro časté progresivní nasazování "obyčejných" změn v backend mikroslužbách, kdy jednotlivé verze žijí vedle sebe krátkou dobu (minuty až jednotky dní). Feature flag je zase určitě lepší pro dlouhodobé projekty, kdy je jedna funkce selektivně rozsvěcována třeba v období několika měsíců (vývoj nové funkce), věci týkající se GUI a tak podobně. A ještě častá výhrada - samozřejmě tohle těžko udělat, když máte mezi verzemi migraci schématu a dat nějaké klasické relační databáze, protože děláte release jednou za půl roku. Tady mluvíme o mikroslužbách, kde je mnoho releasů a jen málo z nich mění podkladové datové struktury a možná dokonce i ty co tak činí, to dělají přes schema-less uložení v NoSQL a kompatibilitě dat mezi verzemi (appka po nějaký čas rozumí staré i nové struktuře, čili kód zná obě verze schématu, databáze umí uložit dokument v libovolné struktuře a konverze běží na pozadí).

# Řešení v CI/CD vs. Flagger
V tomto článku se chci zaměřit na Flagger, který je mi dost sympatický tím, že z pohledu nasazení to stále děláte deklarativně. Logika progresivního přidávání, měření, vyhodnocení apod. je uvnitř Flagger, což berme jako operátor pro Kubernetes. Z pohledu CI/CD tedy jednoduše pošlete novou verzi objektu Deployment do Kubernetes (YAML, Helm, Kustomize) a to je celé. Alternativou mohou být Argo Rollouts, které rovněž běží přímo uvnitř clusteru. Nevýhodou ale je, že o tom jak jste daleko a jak moc je to zelené, se dozvíte z Flaggeru, ne pipeline.

Jinou možností je řídit cyklus ze CI/CD. Stage 1 a nastavíte 5% - v GitHub Actions na to je task, který to pro Open Service Mesh také umí. Co je ale na vás je monitoring a jeho vyhodnocení a poslání na další stage, kde dáte třeba 10%. Zkrátka bude to o dost víc práce v CI/CD, na druhou stranu tam progres pěkně uvidíte.

Osobně nejsem rozhodnut, ale pocitově se přikláním spíše k implementaci v clusteru. Ostatně klasický Kubernetes Deployment objekt má také nasazovací logiku v sobě a všichni to běžně používáme (udělá druhý ReplicaSet s novou verzí a postupně na něj odroluje) i bez pocitu, že bychom tohle celé měli vidět jako fáze v CI/CD. Flagger nebo Argo Rollouts jsou vlastně stejný koncept (řeknu nasaď a oni se o to postarají), jen toho umí výrazně víc.

# Jak Flagger funguje
Flagger nastavíme přes CRD a on pak sleduje náš Deployment objekt a vytvoří k němu Service. Ve skutečnosti vytvoří jeho kopii s názvem mojeappka-primary a na něj směřuje služba (nebo Ingress apod.) mojeappka a původní (ten váš) Deployment seškáluje do nuly. Pokud provedete na Deploymentu změnu (povýšíte verzi například), stane se z ní kanárek a Flagger nastaví nějaký směrovač tak, aby požadavky rozhodil dle vašeho nastavení, například 5% na novou verzi. K tomu použije různé implementace - tak například TrafficSplit v Service Mesh Interface (tedy například v Open Service Mesh nebo Linkerd), VirtualService v Istio, anotace v NGINX Ingress nebo třeba Traefik, Gloo, Contour, App Mesh nebo Skipper. Flagger následně kouká do Monitoringu a podporuje například Prometheus, Datadog, Dynatrace, New Relic a další včetně custom řešení. Nejjednodušší (a to použiji) je navázat se na Prometheus metriky vystavené service mesh nebo ingress implementací (query pro takové příklady nemusíte vymýšlet, jsou ve Flagger už zabudované), nicméně můžete se klidně napojit na něco byznysového (počty objednávek apod.). Podle vašeho nastavení pak bude postupně přitáčet až vás plně překlopí (nebo provede rollback, když metriky nebudou dobré).

# Vyzkoušíme Flagger, AKS a Open Service Mesh
Nejdřív nahodím AKS.

```bash
az group create -n aks -l westeurope
az aks create -n aks -g aks -c 1 -x -s Standard_B4s -y
az aks get-credentials -n aks -g aks --overwrite-existing
```

Nainstaluji Open Service Mesh. V době psaní článku jsem musel použít ruční instalaci, protože až ve verzi 1.0.0 RC2 bylo všechno potřebné - ve finále určitě bude jednodušší a výhodnější (například kvůli přímému supportu) použít AKS addon. Důležité je mít to i s Prometheus, protože o něj opřu Flagger.

```bash
system=$(uname -s)
release=v1.0.0-rc.2
curl -L https://github.com/openservicemesh/osm/releases/download/${release}/osm-${release}-${system}-amd64.tar.gz | tar -vxzf -
sudo mv ./${system}-amd64/osm /usr/bin/
rm -rf ./${system}-amd64

osm install \
    --set=osm.deployPrometheus=true \
    --set=osm.deployGrafana=true \
    --set=osm.deployJaeger=true \
    --set=osm.enablePermissiveTrafficPolicy=true
```

OSM zapnu na jednom namespace a také aktivuji sběr metrik.

```bash
osm namespace add default
osm metrics enable --namespace default
```

Nainstaluji Flagger.

```bash
kubectl apply -k https://github.com/fluxcd/flagger//kustomize/osm?ref=main
```

Nahodím aplikaci a "klienta" (ten bude představovat jiný Pod, který se mikroslužby app ptá - pokud bych chtěl řešit kanárka na ven vystrčeném API, bylo by to třeba s NGINX Ingress) a příslušné service mesh pravidlo.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app
  namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      serviceAccount: app
      containers:
      - name: app
        image: tkubica/web:python-1
        env:
        - name: PORT
          value: "80"
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: client
  namespace: default
---
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
      serviceAccount: client
      containers:
        - name: client
          image: tkubica/mybox
---
kind: TrafficTarget
apiVersion: access.smi-spec.io/v1alpha3
metadata:
  name: access-app1-to-app2
spec:
  sources:
  - kind: ServiceAccount
    name: client
    namespace: default
  destination:
    kind: ServiceAccount
    name: app
    namespace: default
  rules:
  - kind: HTTPRouteGroup
    name: routes1
    matches:
    - all-gets
---
kind: HTTPRouteGroup
apiVersion: specs.smi-spec.io/v1alpha4
metadata:
  name: routes1
spec:
  matches:
  - name: all-gets
    pathRegex: ".*"
    methods:
      - GET
```

Teď si deklarativně nastavím kanárka. Bude navázaný na Deployment app, analýza metrik bude probíhat každých 30 vteřin. Začínám na 5% a postupuji po 5% až do 50%, kdy to překlopím celé. Požaduji request success rate na 99% v okně 1 minuta a maximální latenci 500 ms v okně 30 vteřin. Ještě bych mohl navázat Horizontal Pod Autoscaler a webhooky (zasílat někam informace - třeba do chatu v Teams).

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: app
  namespace: default
spec:
  provider: osm
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  progressDeadlineSeconds: 60
  service:
    port: 80
    targetPort: 80
  analysis:
    interval: 30s
    threshold: 5
    maxWeight: 50
    stepWeight: 5
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 30s
```

Po chvilce vidím, že můj Deployment app je seškálovaný na nulu a ve skutečnosti aplikace běží v app-primary.

```bash
kubectl get deploy
NAME                READY   UP-TO-DATE   AVAILABLE   AGE
app                 0/0     0            0           80s
app-primary         3/3     3            3           37s
```

Podívejme se na Service. Flagger mi vytvořil rovnou tři. Například app-canary směřuje vždy na kanárka - to vám umožní sem generovat syntetický provoz, pokud chcete. To je další zajímavá vlastnost Flaggeru - můžete nastavit, že zavolá generátor provozu nasměrovaný čistě na novou verzi. Někdy totiž nemusíte chtít tam pustit vlastně žádné uživatele, ale nastavit Flagger jako A/B test s tím, že na novou verzi jde jen generátor. To já ale v tomto příkladě nedělám.

```bash
kubectl get service
NAME          TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE
app           ClusterIP   10.0.170.41   <none>        80/TCP    89s
app-canary    ClusterIP   10.0.61.31    <none>        80/TCP    119s
app-primary   ClusterIP   10.0.83.37    <none>        80/TCP    119s
```

Vše je připraveno - pojďme teď nasadit novou verzi. Žádné speciality, žádné nástroje - prostě a jednoduše jakýmkoli vám příjemným způsobem změňte Deployment.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app
  namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      serviceAccount: app
      containers:
      - name: app
        image: tkubica/web:python-2
        env:
        - name: PORT
          value: "80"
        ports:
        - containerPort: 80
```

Sledujme jak to postupuje a simulujme uživatele. Nejdřív posíláme 5%.

```bash
kubectl get canary app
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   5        2021-11-20T13:08:57Z

client=$(kubectl get pod -l app=client -o jsonpath="{.items[0].metadata.name}")
while true; do kubectl exec -ti $client -c client -- curl app; done
Version 1: app-primary-7b54c49db8-nmttj
Version 1: app-primary-7b54c49db8-nmttj
Version 2: app-787fd8ff8c-r72wb
Version 1: app-primary-7b54c49db8-4k2hg
Version 1: app-primary-7b54c49db8-nmttj
Version 1: app-primary-7b54c49db8-l6fw5
Version 1: app-primary-7b54c49db8-l6fw5
Version 1: app-primary-7b54c49db8-4k2hg
Version 1: app-primary-7b54c49db8-4k2hg
Version 1: app-primary-7b54c49db8-l6fw5
Version 1: app-primary-7b54c49db8-nmttj
Version 1: app-primary-7b54c49db8-l6fw5
Version 1: app-primary-7b54c49db8-4k2hg
Version 1: app-primary-7b54c49db8-nmttj
Version 1: app-primary-7b54c49db8-l6fw5
Version 1: app-primary-7b54c49db8-4k2hg
Version 1: app-primary-7b54c49db8-4k2hg
```

Je vidět jak se postupně přitáčí. Všimněte si "Version 2" se objevuje stále častěji a také vidíme, že Version 2 je servírována z podů v Deplomentu app, zatímco stávající verze jde z app-primary. Po pár iteracích jsem na 20%.

```bash
kubectl get canary app
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   20       2021-11-20T13:10:57Z

client=$(kubectl get pod -l app=client -o jsonpath="{.items[0].metadata.name}")
while true; do kubectl exec -ti $client -c client -- curl app; done
Version 1: app-primary-7b54c49db8-4k2hg
Version 1: app-primary-7b54c49db8-nmttj
Version 1: app-primary-7b54c49db8-nmttj
Version 2: app-787fd8ff8c-8twnd
Version 2: app-787fd8ff8c-8twnd
Version 1: app-primary-7b54c49db8-l6fw5
Version 1: app-primary-7b54c49db8-l6fw5
Version 2: app-787fd8ff8c-r72wb
Version 2: app-787fd8ff8c-r72wb
Version 1: app-primary-7b54c49db8-4k2hg
Version 1: app-primary-7b54c49db8-nmttj
Version 1: app-primary-7b54c49db8-nmttj
Version 1: app-primary-7b54c49db8-4k2hg
Version 1: app-primary-7b54c49db8-nmttj
Version 1: app-primary-7b54c49db8-l6fw5
Version 1: app-primary-7b54c49db8-4k2hg
Version 2: app-787fd8ff8c-f6dxm
Version 1: app-primary-7b54c49db8-l6fw5 
Version 2: app-787fd8ff8c-8twnd 
Version 2: app-787fd8ff8c-r72wb 
```

Metriky jsou stále v pořádku, tak to postupuje dál a dál - po 5%.

```bash
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   15       2021-11-20T13:10:27Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   15       2021-11-20T13:10:27Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   20       2021-11-20T13:10:57Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   20       2021-11-20T13:10:57Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   20       2021-11-20T13:10:57Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   25       2021-11-20T13:11:27Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   25       2021-11-20T13:11:27Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   25       2021-11-20T13:11:27Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   30       2021-11-20T13:11:57Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   30       2021-11-20T13:11:57Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   30       2021-11-20T13:11:57Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   35       2021-11-20T13:12:27Z
NAME   STATUS        WEIGHT   LASTTRANSITIONTIME
app    Progressing   35       2021-11-20T13:12:27Z
```

Po 50% už povyšujeme na finální variantu. Všimněte si, že teď už Version 2 žije v Deploymentu app-primary. Deployment app je znovu seškálován na nulu a jsme připraveni obdržet další verzi pro postupné nasazení.

```bash
NAME   STATUS      WEIGHT   LASTTRANSITIONTIME
app    Promoting   0        2021-11-20T13:14:27Z

NAME   STATUS       WEIGHT   LASTTRANSITIONTIME
app    Finalising   0        2021-11-20T13:14:57Z

NAME   STATUS      WEIGHT   LASTTRANSITIONTIME
app    Succeeded   0        2021-11-20T13:15:27Z

client=$(kubectl get pod -l app=client -o jsonpath="{.items[0].metadata.name}")
while true; do kubectl exec -ti $client -c client -- curl app; done
Version 2: app-primary-56884997bf-ngl4n
Version 2: app-primary-56884997bf-zns7r
Version 2: app-primary-56884997bf-z2lfq
Version 2: app-primary-56884997bf-ngl4n
Version 2: app-primary-56884997bf-z2lfq
Version 2: app-primary-56884997bf-zns7r
Version 2: app-primary-56884997bf-ngl4n
Version 2: app-primary-56884997bf-zns7r
Version 2: app-primary-56884997bf-z2lfq
Version 2: app-primary-56884997bf-zns7r
Version 2: app-primary-56884997bf-zns7r
Version 2: app-primary-56884997bf-ngl4n
Version 2: app-primary-56884997bf-ngl4n
Version 2: app-primary-56884997bf-z2lfq
Version 2: app-primary-56884997bf-zns7r 
Version 2: app-primary-56884997bf-ngl4n 
```


Pro každodenní pozvolné nasazování je Flagger skvělá varianta a myšlenkově směřuji právě k tomu mít takovou funkci jako vlastnost "clusteru". Na druhou stranu provést to samé imperativně v CI/CD také jde a GitHub Actions mají Kubernetes akci, která něco podobného (i když trochu jednoduššího) umí. Pro dlouho žijící beta verze nových vlastností nebo GUI komponenty jsou zas určitě lepší feature flagy třeba s využitím služby Azure Application Configuration Service. No a pro "velké verzování" externích API pak zas můžete sáhnout po API managementu.

Ve finále si umím představit, že použijete tohle všechno. Feature flagy pro nové funkce, API management pro velké změny externích API a kanárky přes service mesh či ingress pro každodenní rolování malých verzí a pro backend volání uvnitř clusteru. Zkuste si to a dejte vědět, co vám zabralo.