---
layout: post
title: 'Kubernetes prakticky: přímé a bezpečné ovládání z Azure portálu v reálném čase'
tags:
- Kubernetes
- Monitoring
---
Azure Monitor obsahuje podle mého názoru fantastické Insights, tedy Azure Monitor for Containers, které podporují jak Azure Kubernetes Service, tak clustery mimo Azure napojené přes Azure Arc for Kubernetes. Pro analytiku, reporting a dlouhodobý monitoring jsou myslím výborná volba a takhle dobrých nástrojů s kombinací pokročilého analytického jazyka, jednoduchého sbírání dat i metadat z clusteru, připravených vizualizací i možností si je udělat podle sebe na trhu tedy moc není. Přesto - při rychlém proklikávání vám může vadit, že se informace vykreslují třeba 2 vteřiny a že data co vidíte jsou třeba tak 2 minuty stará data. Jak říkám - Insights jsou pro analytiku a dlouhodobý monitoring, ne na rychlé proklikávání, kde očekáváte data v reálném čase nebo dokonce možnost objekt nejen vidět, ale modifikovat.

Právě proto přichází do Azure nový pohled, který kouká na cluster živě ... a to kouká myslím doslova, jak hned uvidíte. Něco takového se opravdu hodí:
- Kubectl byste rozhodně měli dobře znát, ale pro začátečníka je přecijen jednoduší klikat a nechcete přeci své méně zkušené kolegy k smrti vyděsit hned na začátku. Nicméně i pro zkušeného borce je GUI občas příjemné.
- A co Kubernetes Dashboard, standardní součást projektu? Defaultem je nepoužívat. Trpí bezpečnostními problémy a to velmi výraznými (není tam RBAC, musíte si sami vyřešit bezpečné vystavení ven apod.). Incident u elektrikářů z Tesla byl právě přes omylem vystrčený Kubernetes dashboard, z kterého si útočník prolistoval použité parametry u kontejnerů a vytáhl klíče ke storage a z té si pak stáhnul data.
- Můžete použít Azure Red Hat OpenShift dnes ve verzi 4.4, který pěkné GUI má a to včetně dobré bezpečnosti (a AAD integrace), ale je finančně o dost náročnější v porovnání s AKS. Hodnota navíc tam určitě je a může vám dávat velký smysl (katalog operátorů, integrované CI/CD, podpora service mesh nebo KNative apod.), ale jen kvůli GUI to asi nestačí.
- Řešení dalších dodavatelů mohou být pěkná, ale podporují RBAC s AAD včetně conditional access či vícefaktorovým ověřováním? Často ne ... a příklad Tesly následovat nechcete. A ne, omezení na privátní IP není řešením problému - nejsme v devadesátkách.

# Kubernetes Resources v Azure portálu - realtime GUI
K hezkým obrázkům se hned dostaneme, ale začnu jak Koumák (a budu doufat, že se Šmloulové dostali do všech generací, co tohle čtou). Když si zapnu debug v browseru a podívám se do portálu, zjišťuji skutečně, že ten Javascript přímo volá Kubernetes API. Opravdu to tedy je naživo!

Všimněte si URL a také faktu, že je tam Bearer token - do API se to hlásí přes AAD a tak bude fungovat kompletní RBAC a další důležité věci.
![](/images/2020/2020-08-05-07-19-42.png){:class="img-fluid"}

Je vidět, že browser dostává přímo odpověď z API a tu maluje na obrazovku.
![](/images/2020/2020-08-05-07-18-51.png){:class="img-fluid"}

Má to pár zajímavých důsledků:
- Pokud chcete kromě identitního permiteru řešit i síťové věci, můžete vytvořit AKS private cluster (což znamená využití Private Link), takže API je přístupné jen z vnitřní sítě. Pokud ale správně vyřešíte propagaci DNS záznamů a napojení své firmy, bude vám tohle fungovat třeba přes firemní VPNku.
- Řešení nemá žádnou proprietární závislost na AKS a dá se tedy s rozumnou mírou pravděpodobnosti očekávat budoucí podpora v Azure Arc for Kubernetes, tedy podobně jako Container Insights, logování nebo Azure Policy, které můžete mít i pro Kubernetes v on-premu, bude možné získat i tohle nové GUI, pokud bude API dostupné z počítače, kde běží browser. Ale to jen spekuluji.

# Vyzkoušíme nové GUI
Nejprve se podívám, jaké mám namespace.

![](/images/2020/2020-08-05-06-54-05.png){:class="img-fluid"}

Prohlédnout si můžu i YAML/JSON podobu.

![](/images/2020/2020-08-05-06-54-47.png){:class="img-fluid"}

Založím nový namespace s použitím YAML syntaxe (jasně - tady by třeba do budoucna bylo moc fajn mít přímo v GUI takovou možnost bez YAMLu).

![](/images/2020/2020-08-05-06-55-20.png){:class="img-fluid"}

```yaml
kind: Namespace
apiVersion: v1
metadata:
  name: vote-app
  labels:
    name: vote-app
```

Vložím, uložím.

![](/images/2020/2020-08-05-06-56-35.png){:class="img-fluid"}

Nový namespace je tam.

![](/images/2020/2020-08-05-06-57-08.png){:class="img-fluid"}

Pojďme teď nasadit aplikaci. Je škoda, že zatím nelze YAML s objekty namířit na konkrétní namespace (obdoba --namespace v kubectl), takže musíme dát namespace přímo do definice.

![](/images/2020/2020-08-05-06-57-40.png){:class="img-fluid"}

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: azure-vote-back
  namespace: vote-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: azure-vote-back
  template:
    metadata:
      labels:
        app: azure-vote-back
    spec:
      nodeSelector:
        "beta.kubernetes.io/os": linux
      containers:
      - name: azure-vote-back
        image: redis
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 250m
            memory: 256Mi
        ports:
        - containerPort: 6379
          name: redis
---
apiVersion: v1
kind: Service
metadata:
  name: azure-vote-back
  namespace: vote-app
spec:
  ports:
  - port: 6379
  selector:
    app: azure-vote-back
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: azure-vote-front
  namespace: vote-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: azure-vote-front
  template:
    metadata:
      labels:
        app: azure-vote-front
    spec:
      nodeSelector:
        "beta.kubernetes.io/os": linux
      containers:
      - name: azure-vote-front
        image: microsoft/azure-vote-front:v1
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 250m
            memory: 256Mi
        ports:
        - containerPort: 80
        env:
        - name: REDIS
          value: "azure-vote-back"
---
apiVersion: v1
kind: Service
metadata:
  name: azure-vote-front
  namespace: vote-app
spec:
  type: LoadBalancer
  ports:
  - port: 80
  selector:
    app: azure-vote-front
```

Založím dva deploymenty (backend a frontend) a dvě služby, z toho jedna s externím přístupem.

![](/images/2020/2020-08-05-07-00-27.png){:class="img-fluid"}

Hotovo, mám tam svoje Deploymenty.

![](/images/2020/2020-08-05-07-01-20.png){:class="img-fluid"}

Můžu jeden z nich rozkliknout a podívat se na detaily jako jsou labely, anotace, replicasety a tak podobně.

![](/images/2020/2020-08-05-07-01-45.png){:class="img-fluid"}

YAML můžu taky přímo odtud editovat (něco, co v produkci nedělejte - od toho je CI/CD), tak pojďme zvětšin množství replik.

![](/images/2020/2020-08-05-07-02-34.png){:class="img-fluid"}

Hned jak to udělám, objekt nateče do Kubernetes API a hned vidím dva nové Pody ve stavu vytváření.

![](/images/2020/2020-08-05-07-03-29.png){:class="img-fluid"}

Podívám se teď na Pod blíže. Můžu prozkoumat jaké jsou v něm kontejnery, jaké mé labely apod.

![](/images/2020/2020-08-05-07-03-51.png){:class="img-fluid"}

Co se Podem už podařilo? Stáhnul se image? Je nastartováno?

![](/images/2020/2020-08-05-07-04-08.png){:class="img-fluid"}

Na totéž se můžu podívat z hlediska vývoje v čase. Kdy se co s Podem dělo?

![](/images/2020/2020-08-05-07-04-31.png){:class="img-fluid"}

Insights mi přecijen dají více informací a to i v historickém kontextu a je fajn, že proklik do jich je přímo u Podu.

![](/images/2020/2020-08-05-07-05-58.png){:class="img-fluid"}

Co Service objekty? Frontend má veřejnou IP, co na ni kliknout?

![](/images/2020/2020-08-05-07-06-35.png){:class="img-fluid"}

![](/images/2020/2020-08-05-07-06-51.png){:class="img-fluid"}

Smažme teď celý namespace, už ho nepotřebujeme
![](/images/2020/2020-08-05-07-07-21.png){:class="img-fluid"}

![](/images/2020/2020-08-05-07-07-52.png){:class="img-fluid"}

![](/images/2020/2020-08-05-07-08-26.png){:class="img-fluid"}



Myslím, že nové živé GUI je výborný začátek a perfektní doplněk k existujícím Insights. Skvělé by bylo, kdyby se v budoucnu objevila třeba podpora pro management Helm nasazení nebo nějaká šoupátka pro začátečníky (třeba změna počtu replik na Deploymentu). Každopádně věci jako je bezpečnost clusteru s Azure Policy (přes OPA a Gatekeeper), sběr logů a telemetrie, vizualizace a reporting, alerting nebo právě nové živé GUI se vám můžou hodit nejen pro AKS, ale i Kubernetes běžící mimo Azure. Napojte si ho do Azure přes Azure Arc - řada z těchto věcí už tam běží.