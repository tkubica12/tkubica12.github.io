---
layout: post
title: 'Kubernetes praticky: DAPR a telemetrie, logy i distribuovaný tracing'
tags:
- Kubernetes
- Serverless
- DAPR
---
DAPR vám může zajistit přímou i nepřímou komunikaci mezi komponentami aplikace (service invoke a pub/sub), triggery (input binding) na události mimo DAPR (např. IoT zprávy v Kafka či EventHub) i konektory (output binding) na systémy mimo DAPR (např. soubory v Blob či S3 nebo události v Kafka a tak podobně). To taky znamená, že by v něm mohlo být docela dost užitečných informací a to včetně schopnosti distribuovaného trasování, že? Jasně. Pojďme si to vyzkoušet.

# Distribuovaný tracing
Začneme tím nejzajímavějším - distribuovaným trasováním. Tady DAPR podporuje především standardní protokol OpenTelemetry, na který můžete napojit různé systémy pro ukládání a analýzu těchto dat. Jedním z nich je Azure Application Insights v Azure Monitor, další komerční řešení zahrnují Datadog nebo Dynatrace, v open source světě je to Jaeger a další. Kromě OpenTelemetry podporuje DAPR ještě formát pro Zipkin, který zdá se podporu OpenTelemetry napřímo zatím nemá.

Jak to funguje? Nejdřív potřebujeme v clusteru sbírat OpenTelemetry a posílat do Application Insights. Dle dokumentace jsem použil projekt local-forwarder, který ale už dále rozvíjen nebude. Budoucnost je OpenTelemetry collector, což je univerzální způsob s podporou různých backendů včetně Azure. Ten ale zatím co se týče Azure podpory je v alpha fázi, tak jsem zatím zůstal u local-forwarder, který je dobře dokumentovaný. Nahodil jsem a dal mu klíče do App Insights - to je všechno.

Následně v Kubernetes vytvořím DAPR CRD s konfigurací exporteru s tím, že URL směřuje na můj local-forwarder v clusteru.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: native
spec:
  type: exporters.native
  metadata:
  - name: enabled
    value: "true"
  - name: agentEndpoint
    value: "localforwarder-default.default.svc.cluster.local:50002"
```

Výborně - teď globálně zapnu exportování.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
spec:
  tracing:
    enabled: true
    expandParams: true
    includeBody: true
```

Zbývá na jednotlivých podech zapnout trasování použitím anotace dapr.io/config:

```yaml
      annotations:
        dapr.io/enabled: "true"
        dapr.io/id: "nodea"
        dapr.io/log-as-json: "true"
        dapr.io/config: "tracing"
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/"
```

Výborně. Teď už jen spustit aplikaci, udělat pár operací a obrázek v App Insights je na světě.

![](/images/2020/2020-04-20-12-31-27.png){:class="img-fluid"}

Podívejme se na některé detaily trochu blíž.
![](/images/2020/2020-04-20-12-32-38.png){:class="img-fluid"}

V datech můžu vyhledávat.
![](/images/2020/2020-04-20-12-34-22.png){:class="img-fluid"}

Takhle třeba najdu detail jedné z operací, konkrétně zpráva mezi nodea a subscribeorders.
![](/images/2020/2020-04-20-12-34-47.png){:class="img-fluid"}

![](/images/2020/2020-04-20-12-35-59.png){:class="img-fluid"}

Jako vždy můžu použít připravené workbooky a také si vytvořit vlastní.
![](/images/2020/2020-04-20-12-37-32.png){:class="img-fluid"}

![](/images/2020/2020-04-20-12-38-01.png){:class="img-fluid"}

# Logy
Co se týče logů, mohl bych použít Fluentd a cestu do Elastic Search + Kibana. Pro mě nejjednodušší určitě bude zapnutí logování do Azure Monitoru. To funguje samo o sobě, ale pro účely práce v Azure Monitor bude výborné zapnout logování ve formátu JSON, což se bude snadno parsovat. Stačí nastavit globálně při Helm instalaci (-set global.logAsJson=true) a následně přidat anotaci log-as-json u každé aplikace.

```yaml
      annotations:
        dapr.io/enabled: "true"
        dapr.io/id: "nodea"
        dapr.io/log-as-json: "true"
        dapr.io/config: "tracing"
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/"
```

V Kusto můžu rovnou v prvním příkazu provést parsing a mám rovnou každé políčko jako samostatný sloupec a hned se s tím výborně dělá. Snadno si pak připravím workbooky, alarmy a další vymoženosti Azure Monitoru.

![](/images/2020/2020-04-20-12-47-35.png){:class="img-fluid"}

# Telemetrie
A co nějaká základní telemetrie typu kolik mi to žeše, jak dlouho trvají requesty apod.? DAPR umí vystrkovat telemetrii ve formě API pro Prometheus. Stačí anotací uporoznit kolektor na sběr.

```yaml
      annotations:
        dapr.io/enabled: "true"
        dapr.io/id: "nodea"
        dapr.io/log-as-json: "true"
        dapr.io/config: "tracing"
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/"
```

Pro jednoduché vyzkoušení můžeme začít chytat do Promethea v clusteru, pro dlouhodobou práci s telemtrií jsem si ale nastavil Azure Monitor, aby logy sbíral on. Všechny tam jak vidno jsou.

![](/images/2020/2020-04-20-12-49-40.png){:class="img-fluid"}

Pro případ Prometheus + vizualizace v Grafaně jsou připravené i hezké hotové dashboardy.

Tady je základní pohled na sidecary.
![](/images/2020/2020-04-20-12-43-28.png){:class="img-fluid"}

Můžeme si prohlédnout http latenci.
![](/images/2020/2020-04-20-12-44-13.png){:class="img-fluid"}

Počty nahraných komponent.
![](/images/2020/2020-04-20-12-44-43.png){:class="img-fluid"}

Bezpečnostní operace - zejména mTLS mezi všemi instancemi DAPR.
![](/images/2020/2020-04-20-12-45-06.png){:class="img-fluid"}

Druhý dashboard se zaměřuje na systémové informace, tedy DAPR operátor, injector apod.
![](/images/2020/2020-04-20-12-45-40.png){:class="img-fluid"}

DAPR tedy nejen že zajistí mým aplikacím přenositelnost a jednoduchost, ale pro provoz také přináší další vhled. Vyzkoušejte si.
