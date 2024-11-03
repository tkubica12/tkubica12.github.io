---
layout: post
title: 'Kubernetes praticky: DAPR jako přenositelná aplikační platforma pro cloud-native aplikace - state store a pub/sub'
tags:
- Kubernetes
- Serverless
- DAPR
---
V minulém díle jsem popisoval proč DAPR a jeho základní architekturu. Dnes si DAPR vyzkoušíme. Všechny soubory potřebné pro dnešní článek najdete na mém [GitHubu](https://github.com/tkubica12/kubernetes-demo/tree/master/dapr)

# Instalace DAPR
Instalace začíná tím, že si nainstalujeme DAPR CLI.

```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

Následně přes CLI nahodíme DAPR v AKS.

```bash
dapr init --kubernetes 
```

# Příprava backend služeb
Pro různé služby DAPRu potřebuju nějakou backend implementaci a v mém případě to budou Azure PaaS služby. Pojďme si (v bash) tyto služby zprovoznit. Konkrétně půjde o CosmosDB, Service Bus, Blob Storage a Event Hub.

```bash
export resourceGroup=akstemp

# Cosmos DB
export cosmosdbAccount=mujdaprcosmosdb
az cosmosdb create -n $cosmosdbAccount -g $resourceGroup
az cosmosdb sql database create -a $cosmosdbAccount -n daprdb -g $resourceGroup
az cosmosdb sql container create -g $resourceGroup -a $cosmosdbAccount -d daprdb -n statecont -p "/id"

# Service Bus
export servicebus=mujdaprservicebus
az servicebus namespace create -n $servicebus -g $resourceGroup
az servicebus topic create -n orders --namespace-name $servicebus -g $resourceGroup
az servicebus namespace authorization-rule create --namespace-name $servicebus \
  -g $resourceGroup \
  --name daprauth \
  --rights Send Listen Manage

# Blob Storage
export storageaccount=mujdaprstorageaccount
az storage account create -n $storageaccount -g $resourceGroup --sku Standard_LRS --kind StorageV2
export storageConnection=$(az storage account show-connection-string -n $storageaccount -g $resourceGroup --query connectionString -o tsv)
az storage container create -n daprcontainer --connection-string $storageConnection

# Event Hub
export eventhub=mujdapreventhub
az eventhubs namespace create -g $resourceGroup -n $eventhub --sku Basic
az eventhubs eventhub create -g $resourceGroup --namespace-name $eventhub -n dapreventhub --message-retention 1
az eventhubs eventhub authorization-rule create \
  -g $resourceGroup \
  --namespace-name $eventhub \
  --eventhub-name dapreventhub \
  -n daprauth \
  --rights Listen Send
```

DAPR bude nabízet jednotlivé služby mým aplikacím, ale musíme mu říct, kde najde backend implementaci. DAPR používá custom resource (CRD) s kind Component a v něm jsou konfigurační údaje pro každou komponentu. Do nich potřebujeme dosadit connection stringy do služeb, které jsme před chvilkou vytvořili. Aby to šlo jednoduše, udělal jsem z toho Helm šablonu a tu teď nasadíme.

```bash
cd dapr
helm upgrade dapr-components ./dapr-components --install \
  --set cosmosdb.url=$(az cosmosdb show -n $cosmosdbAccount -g $resourceGroup --query documentEndpoint -o tsv) \
  --set cosmosdb.masterKey=$(az cosmosdb keys list -n $cosmosdbAccount -g $resourceGroup --type keys --query primaryMasterKey -o tsv) \
  --set cosmosdb.database=daprdb \
  --set cosmosdb.collection=statecont \
  --set serviceBus.connectionString=$(az servicebus namespace authorization-rule keys list --namespace-name $servicebus -g $resourceGroup --name daprauth --query primaryConnectionString -o tsv) \
  --set blob.storageAccount=$storageaccount \
  --set blob.key=$(az storage account keys list -n $storageaccount -g $resourceGroup --query [0].value -o tsv) \
  --set blob.container=daprcontainer \
  --set eventHub.connectionString=$(az eventhubs eventhub authorization-rule keys list --namespace-name $eventhub -g $resourceGroup --eventhub-name dapreventhub --name daprauth --query primaryConnectionString -o tsv)
```

Pojďme se namátkou podívat jak jedna taková definice vypadá - třeba state store.

{% raw %}
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: dapr-state-cosmosdb
spec:
  type: state.azure.cosmosdb
  metadata:
  - name: url
    value: {{ .Values.cosmosdb.url }}
  - name: masterKey
    value: {{ .Values.cosmosdb.masterKey }}
  - name: database
    value: {{ .Values.cosmosdb.database }}
  - name: collection
    value: {{ .Values.cosmosdb.collection }}
```
{% endraw %}

V metadatech uvádíme název a v typu k jaké DAPR službě to patří - v našem případě state store.

# State store
První si vyzkoušíme ukládání nějakého stavu do key/value systému. Může jít o session state, obsah nákupního košíku, cache, aktuální stav uživatele (je online, je připraven v počítačové hře na další zápas apod.). V době psaní článku jsou jako backend implementace podporované Redis, Cosmos DB, Etcd, Consul, Cassandra, MongoDB, Memcached, Zookeeper, Cloud Firestore a Couchbase. My jsme při instalaci zvolili Cosmos DB.

Do clusteru pošlu Pod a všimněte si jeho anotací. Ty informují DAPR kontroler o tom, že chceme v tomto Podu využívat jeho služeb a také, že chceme jako jméno mít pod1.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: pod1
  annotations:
    dapr.io/enabled: "true"
    dapr.io/id: "pod1"
spec:
  containers:
    - name: ubuntu
      image: tkubica/mybox
      resources:
        requests:
          cpu: 10m
          memory: 32M
        limits:
          cpu: 100M
          memory: 128M
```

Pošleme do clusteru. Všimněte si, že DAPR vám do Podu sám přidal side-car kontejner.

```bash
kubectl apply -f pod1.yaml

kubectl describe pod pod1 | grep Image:
  Image:         tkubica/mybox
  Image:         docker.io/daprio/dapr:latest
```

Skočíme do kontejneru a vyzkoušíme si state store API. Žádné ověřování, žádná nutnost znát co je na backendu. Jednoduchý REST na uložení a jednoduchý REST na přečtení.

```bash
kubectl exec -ti pod1 -- /bin/bash
curl -X POST http://localhost:3500/v1.0/state \
  -H "Content-Type: application/json" \
  -d '[
        {
          "key": "00-11-22",
          "value": "Tomas"
        }
      ]'

curl http://localhost:3500/v1.0/state/00-11-22
"Tomas"
```

Jednoduché. Podívejme se, jak jsou data vidět přímo v Cosmos DB.

![](/images/2019/2019-12-04-05-36-30.png){:class="img-fluid"}

Všimněte si například, že id obsahuje nejen náš klíč (00-11-22), ale i jméno, které jsme uváděli v anotaci - v našem případě pod1. Můžete tak mít ve state store několik namespace podle potřeby. Také doporučuji vaší pozornosti etag. Psát do store můžete paralelně z několika Podů a co když se dva rozhodnou změnit stávající záznam a každý jinak. Vyhraje ten kdo dřív začal nebo ten kdo poslední končil? To si můžete v DAPR vybrat a on použije vhodné možnosti s ohledem na backend implementaci.

# Publish/Subscribe pattern
Stále častější patternem pro integraci mikroslužeb mezi sebou je pub/sub mítsto přímé komunikace. Takové řešení má bez nějakých složitostí přímo v sobě vyrovnání zátěže (fronta může působit jako buffer), výbornou metriku pro autoscaling služeb (délka nevyřízené fronty), nepotřebuji circuit breaker, protože na nic nečekám apod. První co vás v Azure napadne je Service Bus a to je určitě dobrá volba. Do kódu dáte SDK nebo použijite generické AMQP 1.0 a jedete. Ale jinde možná zvolíte jinou frontu - třeba jen Redis nebo naopak na druhé straně spektra Kafku. DAPR v době psaní článku podporuje Kafku, RabbitMQ, Azure Service Bus, Redis a NATS. Já si DAPR nastavil na Service Bus.

Budeme potřebovat dvě okna. V tom prvním bude odesílání zpráv.

```bash
kubectl apply -f pod1.yaml
kubectl exec -ti pod1 -- bash
```

V druhém okně si nahodíme Pod připravený pro Python kód. DAPR totiž funguje tak, že v okamžiku, kdy má pro příjemce zprávu, mu ji pošle na API, které aplikace vystaví. Jinak řečeno můj kód nemusí pollovat zprávy, vědět kam se napojit, autentizovat a tak dále. Místo toho vystaví endpoint a DAPR mu do něj naservíruje zprávu. Založme si Python Pod a skočme do interaktivního Python prostředí.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: python1
  annotations:
    dapr.io/enabled: "true"
    dapr.io/id: "python1"
    dapr.io/port: "5000"
spec:
  containers:
    - name: python
      image: python:3
      command: ["/bin/sh"]
      args: ["-c", "pip install flask flask_cors && tail -f /dev/null"]
      ports:
        - containerPort: 5000
      resources:
        requests:
          cpu: 10m
          memory: 32M
        limits:
          cpu: 100M
          memory: 512M
```

```bash
kubectl apply -f python.yaml
kubectl exec -ti python1 -- python
```

Do něj teď vložíme následující kód. Ten vystavuje 2 API - jedno je /dapr/subscribe, kterým informuje DAPR o tom, jaké topic chce přijímat. Druhé je /orders, kde orders je právě název topicu. Tyto endpointy poběží na portu 5000 a v python.yaml jsme o tom DAPR informovali.


```python
import flask
from flask import request, jsonify
from flask_cors import CORS
import json
import sys

app = flask.Flask(__name__)
CORS(app)

@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    return jsonify(['orders'])

@app.route('/orders', methods=['POST'])
def a_subscriber():
    print(f'orders: {request.json}', flush=True)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

app.run()
```

Aplikace se rozeběhla a je vidět, že se jí DAPR hned na něco ptá - většinou to nikam nevedlo (k dalším službám se totiž ještě dostaneme), ale /dapr/subscribe našel.

```
* Serving Flask app "__main__" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
127.0.0.1 - - [04/Dec/2019 05:13:42] "GET /dapr/config HTTP/1.1" 404 -
127.0.0.1 - - [04/Dec/2019 05:13:42] "GET /dapr/subscribe HTTP/1.1" 200 -
127.0.0.1 - - [04/Dec/2019 05:13:43] "OPTIONS /binding-blob HTTP/1.1" 404 -
127.0.0.1 - - [04/Dec/2019 05:13:43] "OPTIONS /binding-eventhub HTTP/1.1" 404 -
```

V druhém okně s pod1 pošleme jednoduchý POST do topic orders. Všimněte si, že ten ještě neexistuje a i Service Bus je zcela prázdný.

```bash
curl -X POST http://localhost:3500/v1.0/publish/orders \
	-H "Content-Type: application/json" \
	-d '{
       	     "orderCreated": "ABC01"
      }'
```

Hned se podívejte do okna s Python a v logu vidím, že do něj DAPR šťouchnul a zprávu mu předal.

```
orders: {'id': '7a074991-84cd-405b-8b37-94614ff9db7e', 'source': 'pod1', 'type': 'com.dapr.event.sent', 'specversion': '0.3', 'datacontenttype': 'application/json', 'data': {'orderCreated': 'ABC01'}}
127.0.0.1 - - [04/Dec/2019 05:16:01] "POST /orders HTTP/1.1" 200 -
```

V Service Bus vidím, že DAPR založil topic orders.

![](/images/2019/2019-12-04-06-17-33.png){:class="img-fluid"}

Je tu i python1 jako subscriber.

![](/images/2019/2019-12-04-06-18-14.png){:class="img-fluid"}

No a skutečně přes Service Bus jedna zpráva proběhla.

![](/images/2019/2019-12-04-06-19-02.png){:class="img-fluid"}



Dnes jsme měli dost práce se setupem, tak se na další služby, které DAPR nabízí, podíváme v příštím dále. Dnes jsme viděli jak jednoduše se dá ukládat state do key/value systému bez jakékoli dependence na technické implementaci napozadí. Totéž jsme si vyzkoušeli s posíláním zpráv mezi Pody s využitím pub/sub patternu. Tady nejen že mám jednoduché REST rozhraní, ale DAPR přímo sám aktivně předává zprávy příjemci - ten je tedy nemusí pollovat, DAPR do něj šťouchne. Příště tedy vzhůru na další DAPR služby - zejména binding je úžasná věc a zkusíme i další. V mezičase si nainstalujte DAPR v AKS a začněte zkoušet.