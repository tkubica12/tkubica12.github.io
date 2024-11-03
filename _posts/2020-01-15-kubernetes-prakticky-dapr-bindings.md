---
layout: post
title: 'Kubernetes praticky: DAPR jako přenositelná aplikační platforma pro cloud-native aplikace - bindings'
tags:
- Kubernetes
- Serverless
- DAPR
---
V minulých dílech jsem popisoval proč DAPR a jeho základní architekturu a následně jsme si DAPR nasadili a prozkoumali služby state store a pub/sub. Dnes se zaměříme na binding.

# Binding a k čemu se může hodit
Minule jsme si ukázali dvě služby, u kterých zůstávají veškeré integrace v rámci DAPR. Jinak řečeno přes DAPR chci zapisovat do state store a přes DAPR z něj číst. Přes DAPR chci rozeslat zprávu dalším službám a přes DAPR ji dostat. Co když ale potřebujeme integrace do aplikací, které DAPR nepoužívají?

Představme si nejdřív situaci typu input binding. Sbíráme zprávy z IoT zařízení přes Azure Event Hub a tyto zařízení využívají MQTT protokol. To pro mě znamená do svého kódu pro zpracování těchto zpráv dát dependency na komunikaci s Event Hub, jeho SDK (nebo SDK nějakého generického protokolu). V jiném IoT projektu ale bude využita Kafka a jsme zase u toho - máme v kódu specifické SDK a horší přenositelnost. Input binding je o tom, že necháme DAPR poslouchat na tom externím systému, třeba Event Hub, a zprávy nám doručovat opět přes jednoduchý REST nebo gRPC call. V kódu nemáme specifickou dependency a přesto nenutíme okolní svět (IoT zařízení) používat DAPR.

Output binding je totéž, ale obráceně. Co když potřebujeme z kódu uložit něco do externího systému tak, aby na to mohla reagovat jiná aplikace, která ale DAPR nepoužívá. Tak například představme si datovou analytiku. Nějaký ETL systém, třeba Azure Data Factory, kouká do Azure Blob Storage a vybírá z něj JSON exporty, které pak následně dávkově analyzuje (třeba v Azure Databricks). Náš kód tak potřebuje SDK pro přihlášení a zápis do Azure Blob Storage. Ale v jiném cloudu to bude S3 a v on-premises třeba FTP a už se nám to větví - jiné SDK, jiné přihlašování apod. DAPR může zařídit komunikaci s tímto externím systémem a náš kód pošle do DAPR jen potřebná data na konzistentním DAPR API. Stejně tak to můžeme použít pro zaslání zprávy jiném systému (který nemá DAPR) přes nějakou frontu nebo event systém - Event Grid, Kafka, Service Bus, NAST, ...

# Output binding
Začněme příkladem výstupního svázání, protože to bude velmi jednoduché. Použijeme pod1.yaml z minulého dílu a posledně jsme také v DAPR udělali všechny další potřebné konfigurace, takže toto máme připraveno. Jen se podívejme na tento objekt.

{% raw %}
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: binding-blob
spec:
  type: bindings.azure.blobstorage
  metadata:
  - name: storageAccount
    value: {{ .Values.blob.storageAccount }}
  - name: storageAccessKey
    value: {{ .Values.blob.key }}
  - name: container
    value: {{ .Values.blob.container }}
```
{% endraw %}

Následně skočíme do Podu a pošleme POST volání na DAPR endpoint s na URI /bindings/binding-blob kde binding-blob je název mého bindingu (v mém případě Azure Blob Storage). V těle pošleme JSON řetězec (tento binding DAPRu není určen pro binární data typu filmečky).

```bash
kubectl apply -f pod1.yaml
kubectl exec -ti pod1 -- bash

curl -X POST http://localhost:3500/v1.0/bindings/binding-blob \
	-H "Content-Type: application/json" \
	-d '{ "metadata": {"blobName" : "myfile.json"}, 
      "data": {"mykey": "This is my value"}}'
exit
```

Podívejme se do storage accountu - najdeme tam soubor myfile.json s obsahem, který očekáváme.

```bash
export storageConnection=$(az storage account show-connection-string -n $storageaccount -g $resourceGroup --query connectionString -o tsv)
az storage blob list -c daprcontainer -o table --connection-string $storageConnection

kubectl delete -f pod1.yaml
```

# Input binding
Pro příklad vázání vstupu si vybereme Event Hub (opět máme konfiguračně připraveno z minulého dílu). Můžeme mrknout na šablonu této komponenty v helm chartu, který jsme nasazovali:

{% raw %}
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: binding-eventhub
spec:
  type: bindings.azure.eventhubs
  metadata:
  - name: connectionString
    value: {{ .Values.eventHub.connectionString }}
```
{% endraw %}

Stejně jako v minulém díle si pustíme python1.yaml:

```bash
kubectl apply -f python.yaml
kubectl exec -ti python1 -- python

# Paste Python app binding.py and generate some event in Event Hub
```

V něm spustíme kód, který bude vystavovat API pro příjem zpráv z input bindingu. URI obsahuje název bindingu tak, jak byl popsán v DAPR komponentě v minulém díle.

```python
import flask
from flask import request, jsonify
from flask_cors import CORS
import json
import sys

app = flask.Flask(__name__)
CORS(app)

@app.route('/binding-eventhub', methods=['POST'])
def a_subscriber():
    print(f'message: {request.json}', flush=True)
    return "OK", 200

app.run()
```

Vygenerujte zprávu v Event Hubu a uvidíte, že DAPR ji doručí do našeho kontejneru. Můžete například použít extension pro VS Code (summer.azure-event-hub-explorer).

V předchozím díle jsme si vyzkoušeli využití DAPR pro vyřešení problematiky zasílání zpráv a ukládání state v naší mikroslužbové aplikaci. Dnes jsme si ukázali binding, tedy situaci, kdy okolní svět potřebuje konkrétní implementaci (nepoužívá DAPR), ale my stále nechceme mít dependency na této implementaci. Integraci do implementace pro nás udělá DAPR a my tak opět nepotřebujeme specifické SDK do kódu.