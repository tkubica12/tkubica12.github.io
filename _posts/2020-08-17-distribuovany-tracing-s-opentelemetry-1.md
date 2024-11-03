---
layout: post
published: true
title: "Distribuovaný tracing s OpenTelemetry, Python a Azure Monitor (1): z ničeho až po monitoring mikroslužeb v Kubernetes"
tags:
- Monitoring
- Apps
- OpenTelmetry
---
Dnes si zcela prakticky vyzkoušíme přidat instrumentaci do Python aplikace a napojit Azure Monitor backend pro zpracování trasování. Budeme si přidávat vlastní atributy a nakonec rozjedeme mikroslužby v Kubernetes, kde si přes Downwards API obohatíme naše trasování o provozní informace z clusteru jako je jméno Podu, Nodu, limitu na CPU a paměť nebo výčet labels. Čeká nás toho hodně, takže u Kubernetes se pro dnešek zastavíme a příště si zkusíme instrumentovat další situace (například databáze) a ponoříme se do dat trochu hlouběji s vlastními query.

# Aplikace bez instrumentace
Mějme jednoduchou Python aplikaci, která vystavuje API / a /data s využitím frameworku Flask. Po zavolání na / aplikace použije requests knihovnu pro zavolání API /data (ve výchozím stavu sama na sebe, ale později to změníme). API /data je implementováno tak, že zavolá vnitřní proceduru na "zpracování", která vrátí nějaký výsledek a ten jde zpět k volající HTTP službě.

```python
import flask
import requests
import os
import time

# Create Flask object
app = flask.Flask(__name__)

# Flask routing
@app.route('/')
def init():
    response = requests.get(os.getenv('REMOTE_ENDPOINT', default="http://127.0.0.1:8080/data"))
    return "Response from data API: %s" % response.content.decode("utf-8") 

@app.route('/data')
def data():
    result = processData()
    return result

# Processing
def processData():
    time.sleep(0.2)
    return "This is your data"

# Run Flask
app.run(host='0.0.0.0', port=8080, threaded=True)
```

# Instrumentace pro Flask a Requests
Přidejme teď instrumentaci tak, abychom nemuseli spany definovat nijak sami. Naimportujeme tedy OpenTelemetry SDK pro Python a jako exportér zvolíme výpis na konzoli. Nic se nikam nebude posílat, jen vygenerovaný span vytiskneme, abychom si ho mohli prozkoumat.

```python
import flask
import requests
import os
import time

# Import Open Telemetry tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor

# Setup instrumentation with Console exporter
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

# Create Flask object
app = flask.Flask(__name__)

# Add automatic instrumentation
RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument_app(app)

# Flask routing
@app.route('/')
def init():
    response = requests.get(os.getenv('REMOTE_ENDPOINT', default="http://127.0.0.1:8080/data"))
    return "Response from data API: %s" % response.content.decode("utf-8") 

@app.route('/data')
def data():
    result = processData()
    return result

# Processing
def processData():
    time.sleep(0.2)
    return "This is your data"

# Run Flask
app.run(host='0.0.0.0', port=8080, threaded=True)
```

Spustím aplikaci a vygeneruji požadavek. Podívejme se jaké spany se pro mě automaticky vytvořily. Níže jsem změnil pořadí, protože na obrazovku se vytiskne span logicky při jeho ukončení, takže to jde v mém případě on vnitřních k vnějším - což jsem pro účely popisu obrátil.

Nejprve se tedy podívejme na první span, který nemá rodiče. SpanKind je typu SERVER, tedy byl to Flask, který v roli serveru tenhle požadavek přijal. Vidíme detaily jako ID trace a spanu a atributy, které pro nás byly dosazeny automaticky (podle nich pak můžeme v backendu filtrovat apod.). Nejsou připojeny žádné eventy (o logování jindy) ani nalinkované jiné spany (nemáme tu fan-in situaci, takže netřeba).

```json
{
    "name": "init",
    "context": {
        "trace_id": "0x8245c1994622804589714ec5057fc2c5",
        "span_id": "0x6edc8ba500170b74",
        "trace_state": "{}"
    },
    "kind": "SpanKind.SERVER",
    "parent_id": null,
    "start_time": "2020-08-05T07:35:18.091923Z",
    "end_time": "2020-08-05T07:35:18.380420Z",
    "status": {
        "canonical_code": "OK"
    },
    "attributes": {
        "component": "http",
        "http.method": "GET",
        "http.server_name": "0.0.0.0",
        "http.scheme": "http",
        "host.port": 8080,
        "http.host": "127.0.0.1:8080",
        "http.target": "/",
        "net.peer.ip": "127.0.0.1",
        "net.peer.port": 61299,
        "http.flavor": "1.1",
        "http.route": "/",
        "http.status_text": "OK",
        "http.status_code": 200
    },
    "events": [],
    "links": []
}
```

Kdo je dítě tohoto spanu? Je to tento span (všimněte si parent_id) a je typu CLIENT, protože tady moje aplikace vystupuje v roli klienta a přes Requests knihovnu se ptá nějakého serveru. Všimntěte si rovněž, že to dopladlo dobře a GET metoda vrátila kód 200, což se posílá v atributech. 
```json
{
    "name": "/data",
    "context": {
        "trace_id": "0x8245c1994622804589714ec5057fc2c5",
        "span_id": "0x5b991d18d3f45cb3",
        "trace_state": "{}"
    },
    "kind": "SpanKind.CLIENT",
    "parent_id": "0x6edc8ba500170b74",
    "start_time": "2020-08-05T07:35:18.145914Z",
    "end_time": "2020-08-05T07:35:18.372417Z",
    "status": {
        "canonical_code": "OK"
    },
    "attributes": {
        "component": "http",
        "http.method": "GET",
        "http.url": "http://127.0.0.1:8080/data",
        "http.status_code": 200,
        "http.status_text": "OK"
    },
    "events": [],
    "links": []
}
```

Tento span má ale také své dítě a to je zpracování na straně serveru. Ten v headerech dostal informace z rodiče a pokračuje dál, takže náš backend bude hezky schopen graf návazností poskládat. Tentokrát je to span typu SERVER, protože tohle je Flask, který na /data přijal zprávu. 

```json
{
    "name": "data",
    "context": {
        "trace_id": "0x8245c1994622804589714ec5057fc2c5",
        "span_id": "0x74e18f1875af07bc",
        "trace_state": "{}"
    },
    "kind": "SpanKind.SERVER",
    "parent_id": "0x5b991d18d3f45cb3",
    "start_time": "2020-08-05T07:35:18.149911Z",
    "end_time": "2020-08-05T07:35:18.352416Z",
    "status": {
        "canonical_code": "OK"
    },
    "attributes": {
        "component": "http",
        "http.method": "GET",
        "http.server_name": "0.0.0.0",
        "http.scheme": "http",
        "host.port": 8080,
        "http.host": "127.0.0.1:8080",
        "http.target": "/data",
        "net.peer.ip": "127.0.0.1",
        "net.peer.port": 61300,
        "http.flavor": "1.1",
        "http.route": "/data",
        "http.status_text": "OK",
        "http.status_code": 200
    },
    "events": [],
    "links": []
}
```

Možná vám tu něco chybí - jasně, jsou to údaje o této instanci. Jméno aplikace, hostname serveru a tak podobně. To je samozřejmě důležité, ale to není ve vlastním spanu, ale v jeho obálce. O tom už za chvilku.

# Napojíme Azure Monitor přes exportér
V Azure si založte Application Insights a získejte instrumentation key, který aplikaci předáme jako proměnnou prostředí. Pro zjednodušení budu stále používat jednoduchý odesílač, v praxi to asi není optimální a měl by tu být Batch exportér, který je v základu také k dispozici. Náš kód teď vypadá takhle:

```python
import flask
import requests
import os
import time

# Import Open Telemetry tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor

# Import Azure Monitor
from azure_monitor import AzureMonitorSpanExporter
from azure_monitor import AzureMonitorMetricsExporter
from azure_monitor.sdk.auto_collection import AutoCollection
from opentelemetry.ext.wsgi import OpenTelemetryMiddleware

# Gather configurations
appInsightsConnectionString = "InstrumentationKey=%s" % os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY')

# Setup instrumentation with Console exporter
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

# Add Azure Monitor exporter
exporterAzure = AzureMonitorSpanExporter(
    connection_string=appInsightsConnectionString
)
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(exporterAzure)
)

# Create Flask object
app = flask.Flask(__name__)

# Add automatic instrumentation
RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument_app(app)

# Flask routing
@app.route('/')
def init():
    response = requests.get(os.getenv('REMOTE_ENDPOINT', default="http://127.0.0.1:8080/data"))
    return "Response from data API: %s" % response.content.decode("utf-8") 

@app.route('/data')
def data():
    result = processData()
    return result

# Processing
def processData():
    time.sleep(0.2)
    return "This is your data"

# Run Flask
app.run(host='0.0.0.0', port=8080, threaded=True)
```

Jak to vypadá v Application Insights?

![](/images/2020/2020-08-05-09-55-39.png){:class="img-fluid"}

Všimněte si, že SpanKind SERVER je v GUI charakterizován jako request zatímco SpanKind CLIENT jako dependency (to dává docela smysl, ale nezapomeňte, že tohle je terminologie Azure Monitor a v jiných řešení se to může ukazovat jinak). Také se podívejte, jak přidaným atributům Azure Monitor krásně rozumí a ukazuje například response code. 

Rozklikněte nějakou z událostí a podívejme se na časovou osu a detailní atributy.

![](/images/2020/2020-08-05-09-57-54.png){:class="img-fluid"}

Ve stadardních atributech si můžete zobrazit víc - třeba cloud role a cloud instance. Zatím tam máme jméno souboru a hostname a ještě dnes možná budeme mít touhu to změnit, uvidíte. 

![](/images/2020/2020-08-05-09-59-03.png){:class="img-fluid"}

Také tam jsou custom atributy a těm základním GUI přímo rozumí. Za chvilku si řekneme, že nemusí být špatné si tam přidat svoje.

Prozkoumáme také záložku Performance, z které je jasné, že atributům Azure Monitor rozumí a dokáže s nimi pracovat. Znamená to také, že vám budou fungovat workbooky i custom query do zdrojových dat. S tím se dá dělat strašně moc, ale k tomu se dostaneme asi v některém z dalších článků.

![](/images/2020/2020-08-05-10-00-53.png){:class="img-fluid"}

# Přidáme si vlastní atribut do spanu
V aplikaci máte možná i nějakou další informaci, která by se hodně hodila. Něco, podle čeho bude výborné vyhledávat aniž bychom to museli nějak korelovat s logy. Co třeba ID přihlášeného uživatele, session ID, produktové číslo, které zrovna zpracováváme, číslo objednávky? Cokoli vás napadne můžete vložit jako custom atribut aniž bychom poškodili automatickou instrumentaci. Přidejme tedy order_id jako atribut (použiji hodnotu natvrdo, v realitě si to jistě umíte představit).

```python
import flask
import requests
import os
import time

# Import Open Telemetry tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor

# Import Azure Monitor
from azure_monitor import AzureMonitorSpanExporter
from azure_monitor import AzureMonitorMetricsExporter
from azure_monitor.sdk.auto_collection import AutoCollection
from opentelemetry.ext.wsgi import OpenTelemetryMiddleware

# Gather configurations
appInsightsConnectionString = "InstrumentationKey=%s" % os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY')

# Setup instrumentation with Console exporter
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

# Add Azure Monitor exporter
exporterAzure = AzureMonitorSpanExporter(
    connection_string=appInsightsConnectionString
)
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(exporterAzure)
)

# Create Flask object
app = flask.Flask(__name__)

# Add automatic instrumentation
RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument_app(app)

# Flask routing
@app.route('/')
def init():
    trace.get_current_span().set_attribute("order_id", "00123456")
    response = requests.get(os.getenv('REMOTE_ENDPOINT', default="http://127.0.0.1:8080/data"))
    return "Response from data API: %s" % response.content.decode("utf-8") 

@app.route('/data')
def data():
    result = processData()
    return result

# Processing
def processData():
    time.sleep(0.2)
    return "This is your data"

# Run Flask
app.run(host='0.0.0.0', port=8080, threaded=True)
```

Atribut najdeme v GUI.

![](/images/2020/2020-08-05-10-08-18.png){:class="img-fluid"}

Můžeme podle něj vyhledávat buď jednoduše přes všechna pole

![](/images/2020/2020-08-05-10-10-33.png){:class="img-fluid"}

nebo přes složitější filtraci.

![](/images/2020/2020-08-05-10-12-29.png){:class="img-fluid"}

Filtr můžete rovněž použít na dalších záložkách při ladění výkonu nebo řešení neúspěšných volání.

![](/images/2020/2020-08-05-10-15-27.png){:class="img-fluid"}

# Posuňme aplikaci do Kubernetes
Z kódu vidíte, že aplikace může volat /data v jiné službě, takže si můžeme v Kubernetes udělat dvě služby, které volají jednu na druhou a podívat se, jak se s tím Azure Monitor Application Insights vypořádá.

Nejprve byste měli mít requests.txt na instalaci potřebných knihoven. Ten můj je o krok napřed a jsou tam nějaké věci navíc, ale to nevadí.

```
flask
requests
pymysql == 0.9.3
opentelemetry-sdk == 0.10b0
opentelemetry-ext-flask == 0.10b0
opentelemetry-ext-requests == 0.10b0
opentelemetry-ext-prometheus == 0.10b0
opentelemetry-ext-wsgi == 0.10b0
opentelemetry-ext-pymysql == 0.10b0
opentelemetry-azure-monitor == 0.4b0
```

Pak potřebujeme Dockerfile.

```Dockerfile
FROM python:3

WORKDIR /app
COPY . ./
RUN pip3 install -r requirements.txt

EXPOSE 8080
CMD [ "python", "./app.py" ]
```

Já už jsem build provedl a najdete ho na Docker Hub jako tkubica/opentelemetry:clanek-v1.

Připravím si tedy Kubernetes a pošlu do něj dva deploymenty se službami tak, aby ťukali jeden do druhého.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opentelemetry-app1
  labels:
    app: opentelemetry-app1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: opentelemetry-app1
  template:
    metadata:
      labels:
        app: opentelemetry-app1
    spec:
      containers:
        - name: opentelemetry-app1
          image: tkubica/opentelemetry:clanek-v1
          ports:
            - containerPort: 8080
          env:
            - name: APPINSIGHTS_INSTRUMENTATIONKEY
              value: <YOUR-KEY>
            - name: REMOTE_ENDPOINT
              value: "http://opentelemetry-app2:8080/data"
          resources:
            requests:
                cpu: 10m
                memory: 16M
            limits:
                cpu: 100M
                memory: 128M
---
kind: Service
apiVersion: v1
metadata:
  name: opentelemetry-app1
  labels:
    app: opentelemetry-app1
spec:
  type: LoadBalancer
  selector:
    app: opentelemetry-app1
  ports:
  - protocol: TCP
    name: http
    port: 8080
    targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opentelemetry-app2
  labels:
    app: opentelemetry-app2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: opentelemetry-app2
  template:
    metadata:
      labels:
        app: opentelemetry-app2
    spec:
      containers:
        - name: opentelemetry-app2
          image: tkubica/opentelemetry:clanek-v1
          ports:
            - containerPort: 8080
          env:
            - name: APPINSIGHTS_INSTRUMENTATIONKEY
              value: <YOUR-KEY>
            - name: REMOTE_ENDPOINT
              value: "http://opentelemetry-app1:8080/data"
          resources:
            requests:
                cpu: 10m
                memory: 16M
            limits:
                cpu: 100M
                memory: 128M
---
kind: Service
apiVersion: v1
metadata:
  name: opentelemetry-app2
  labels:
    app: opentelemetry-app2
spec:
  type: LoadBalancer
  selector:
    app: opentelemetry-app2
  ports:
  - protocol: TCP
    name: http
    port: 8080
    targetPort: 8080
```

Nahodíme a měli bychom mít dvě služby a v každé dvě instance. Zjistím si externí IP první služby a párkrát jí provolám. Load-balancer by mě měl rozhazovat na instance a podívejme se na výsledek v Azure Monitor Application Insights.

Takhle vypadá moje aplikační mapa:

![](/images/2020/2020-08-05-12-37-54.png){:class="img-fluid"}

Evidentně nám tady něco nehraje. Čtyři instance odpovídají, ale jsou to dvě rozdílné služby. Stopa určitě vede k názvu služby, který je app.py, tedy vychází z názvu souboru a v tom bude problém.

Když se podívám do dat, je Cloud Role, tedy název služby, app.py. Cloud Instance je hostname, což odpovídá jménu Podu - to je fajn, ale službu potřebujeme určitě přejmenovat.

![](/images/2020/2020-08-05-12-40-15.png){:class="img-fluid"}

Nicméně řešení funguje, ale musíme trochu vylepšit ta data. A co kdyby se nám podařilo tam přidat kromě správného názvu i nějaké další informace z hlediska Kubernetes, třeba na kterém jsme Node? Pojďme na to.

# Přidáme si vlastní název a Kubernetes atributy
Azure Monitor exportér můžeme nakrmit vlastními metadaty a jednak změnit Cloud Role název (to bude důležité), což se děje ve vnějším obalu, ale také by nebylo špatné přidat vlastní atributy do každého spanu (kromě těch specifický pro nějaký konkrétní span) s informací z Kubernetu. Funguje to tak, že exportér si provolává interface, v kterém můžeme tyto věci modifikovat. Navrhuji je tam dosadit z proměnných prostředí, protože díky Kubernetes Downward API jsme schopni do nich předávat informace z clusteru typu název Podu, Nodu nebo Labels.

Z pohledu aplikace tohle všechno posbíráme z proměnných prostředích, kam to doručíme. Je tu jedna výjimka - labels. Těch může být několik a Kubernetes to má jako odřádkované key=value, takže to se do proměnné prostředí dát nedá. Použijeme tedy soubor, prolistujeme a pro každý řádek s labelem vytvoříme custom atribut.

Celý kód je tady:

```python
import flask
import requests
import os
import time

# Import Open Telemetry tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor

# Import Azure Monitor
from azure_monitor import AzureMonitorSpanExporter
from azure_monitor import AzureMonitorMetricsExporter
from azure_monitor.sdk.auto_collection import AutoCollection
from opentelemetry.ext.wsgi import OpenTelemetryMiddleware

# Gather configurations
appInsightsConnectionString = "InstrumentationKey=%s" % os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY')

# Setup instrumentation with Console exporter
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

# Exporter metadata configuration
def azure_monitor_metadata(envelope):
    envelope.tags['ai.cloud.role'] = os.getenv('APP_NAME')
    envelope.data.base_data.properties['app_version'] = os.getenv('APP_VERSION')
    envelope.data.base_data.properties['kube_pod_name'] = os.getenv('POD_NAME')
    envelope.data.base_data.properties['kube_node_name'] = os.getenv('NODE_NAME')
    envelope.data.base_data.properties['kube_namespace'] = os.getenv('POD_NAMESPACE')
    envelope.data.base_data.properties['kube_cpu_limit'] = os.getenv('CPU_LIMIT')
    envelope.data.base_data.properties['kube_memory_limit'] = os.getenv('MEMORY_LIMIT')
    # Read labels
    f = open("/podinfo/labels")
    for line in f:
        key,value = line.partition("=")[::2]
        envelope.data.base_data.properties['labels.%s' % key] = value.replace('"', '')
    return True

# Add Azure Monitor exporter
exporterAzure = AzureMonitorSpanExporter(
    connection_string=appInsightsConnectionString
)
exporterAzure.add_telemetry_processor(azure_monitor_metadata)
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(exporterAzure)
)

# Create Flask object
app = flask.Flask(__name__)

# Add automatic instrumentation
RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument_app(app)

# Flask routing
@app.route('/')
def init():
    trace.get_current_span().set_attribute("order_id", "00123456")
    response = requests.get(os.getenv('REMOTE_ENDPOINT', default="http://127.0.0.1:8080/data"))
    return "Response from data API: %s" % response.content.decode("utf-8") 

@app.route('/data')
def data():
    result = processData()
    return result

# Processing
def processData():
    time.sleep(0.2)
    return "This is your data"

# Run Flask
app.run(host='0.0.0.0', port=8080, threaded=True)
```

Jak tedy předáme do aplikace údaje z Kubernetes clusteru? Můžeme použít Downwards API, které nám dovolí načítat o Podu informace jak z metadat (název, labels), tak ze spec a dalších políček.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opentelemetry-app1
  labels:
    app: opentelemetry-app1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: opentelemetry-app1
  template:
    metadata:
      labels:
        app: opentelemetry-app1
        environment: prod
    spec:
      containers:
        - name: opentelemetry-app
          image: tkubica/opentelemetry:clanek-v2
          ports:
            - containerPort: 8080
          env:
            - name: APP_NAME
              value: OpenTelmetryApp-1
            - name: APP_VERSION
              value: "1.0.0"
            - name: APPINSIGHTS_INSTRUMENTATIONKEY
              value: 7077d0fa-6b42-4ab9-bf03-5635f40af136
            - name: REMOTE_ENDPOINT
              value: "http://opentelemetry-app2:8080/data"
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            - name: CPU_LIMIT
              valueFrom:
                resourceFieldRef:
                  containerName: opentelemetry-app
                  resource: limits.cpu
            - name: MEMORY_LIMIT
              valueFrom:
                resourceFieldRef:
                  containerName: opentelemetry-app
                  resource: limits.memory
          volumeMounts:
          - name: podinfo
            mountPath: /podinfo
            readOnly: true
          resources:
            requests:
                cpu: 10m
                memory: 16M
            limits:
                cpu: 100M
                memory: 128M
      volumes:
      - name: podinfo
        downwardAPI:
          items:
            - path: "labels"
              fieldRef:
                fieldPath: metadata.labels
---
kind: Service
apiVersion: v1
metadata:
  name: opentelemetry-app1
  labels:
    app: opentelemetry-app1
spec:
  type: LoadBalancer
  selector:
    app: opentelemetry-app1
  ports:
  - protocol: TCP
    name: http
    port: 8080
    targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opentelemetry-app2
  labels:
    app: opentelemetry-app2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: opentelemetry-app2
  template:
    metadata:
      labels:
        app: opentelemetry-app2
        environment: prod
    spec:
      containers:
        - name: opentelemetry-app
          image: tkubica/opentelemetry:clanek-v2
          ports:
            - containerPort: 8080
          env:
            - name: APP_NAME
              value: OpenTelmetryApp-2
            - name: APP_VERSION
              value: "1.0.0"
            - name: APPINSIGHTS_INSTRUMENTATIONKEY
              value: 7077d0fa-6b42-4ab9-bf03-5635f40af136
            - name: REMOTE_ENDPOINT
              value: "http://opentelemetry-app1:8080/data"
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            - name: CPU_LIMIT
              valueFrom:
                resourceFieldRef:
                  containerName: opentelemetry-app
                  resource: limits.cpu
            - name: MEMORY_LIMIT
              valueFrom:
                resourceFieldRef:
                  containerName: opentelemetry-app
                  resource: limits.memory
          volumeMounts:
          - name: podinfo
            mountPath: /podinfo
            readOnly: true
          resources:
            requests:
                cpu: 10m
                memory: 16M
            limits:
                cpu: 100M
                memory: 128M
      volumes:
      - name: podinfo
        downwardAPI:
          items:
            - path: "labels"
              fieldRef:
                fieldPath: metadata.labels
---
kind: Service
apiVersion: v1
metadata:
  name: opentelemetry-app2
  labels:
    app: opentelemetry-app2
spec:
  type: LoadBalancer
  selector:
    app: opentelemetry-app2
  ports:
  - protocol: TCP
    name: http
    port: 8080
    targetPort: 8080
```

Podívejme do Azure Monitor Application Insights. Výborně, názvy jsou teď jak potřebuji a vpravo si všimněte všech našich custom atributů. Jsou tam jak věci z Kubernetes, které jsme přidali pro všechny spany, tak i speciální atribut order_id, který jsme si přidali k jednomu konkrétnímu spanu.

![](/images/2020/2020-08-05-15-46-47.png){:class="img-fluid"}

Díky tomu očekávam, že grafická mapa bude vykreslena správně.

![](/images/2020/2020-08-05-15-49-20.png){:class="img-fluid"}

Můžeme jít třeba do sekce Performance a filtrovat podle Cloud Role (což je aplikační služba) a dál podle Cloud Instance (v našem případě konkrétní replika, tedy Pod).

![](/images/2020/2020-08-05-15-50-20.png){:class="img-fluid"}

Výborné ale je, že můžeme samozřejmě filtrovat i podle ostatních atributů. Analyzovat můžu výkonnost s ohledem na konkrétní Kubernetes Node, v konkrétním namespace nebo pro určité labels (třeba produkce vs. canary vs. dev).

![](/images/2020/2020-08-05-15-51-10.png){:class="img-fluid"}

Pro dnešek se na tomhle místě zastavíme a příště budeme v trasování pokračovat. Přidáme si další instrumentace třeba pro volání do databáze a zkusíme si přístup ke stejným datům přes query (Kusto) s možností podle toho vytvořit třeba nějaký Alert nebo vizualizaci ve Workbooku.

