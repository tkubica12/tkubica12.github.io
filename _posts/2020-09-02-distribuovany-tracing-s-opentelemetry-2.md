---
layout: post
published: true
title: "Distribuovaný tracing s OpenTelemetry, Python a Azure Monitor (2): další instrumentace, vizualizace a pokročilé query"
tags:
- Monitoring
- Apps
- OpenTelmetry
---
Minule jsme se dostali z aplikace bez jakékoli instrumentace až provozu v Kubernetes a sbírání dat obohacených o aplikační i infrastrukturní atributy v Azure Monitor Application Insights. Dnes budeme pokračovat a přidáme si trasování přístupu do databáze, uděláme si vlastní span, zkusíme auto-instrumentaci a naučíme se pracovat se surovými daty v Azure Monitor. 

# MySQL
Pomalá odpověď databáze je určitě jednou z častých příčin špatné uživatelské zkušenosti s aplikací a bez pořádného monitoringu se špatně odhaluje. Jasně, databázi na krofkách najdete snadno, ale identifikovat jaké byznysové funkce aplikace jsou dotčeny pomalým zpracováním určité kategorie dotazů, to tak triviální není. Přidejme teď do naší aplikace v proceduře processData přístup do MySQL. Dejme tomu, že procedura provádí nějakou relativně složitou operaci reprezentovanou time.sleep(0.2) a výsledek pak zapíše do databáze. Tento zápis by bylo dobré trasovat, protože se podepisuje na celkové odezvě aplikace.

Opět sáhneme po knihovně, která instrumentaci udělá za nás. Tady je výsledný kód:

```python
import flask
import requests
import os
import time
import pymysql
import random

# Import Open Telemetry tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor
from opentelemetry.ext.pymysql import PyMySQLInstrumentor

# Import Azure Monitor
from azure_monitor import AzureMonitorSpanExporter
from azure_monitor import AzureMonitorMetricsExporter
from azure_monitor.sdk.auto_collection import AutoCollection
from opentelemetry.ext.wsgi import OpenTelemetryMiddleware

# Gather configurations
appInsightsConnectionString = "InstrumentationKey=%s" % os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY')
mySqlHost = os.getenv('MYSQL_HOST')
mySqlPassword = os.getenv('MYSQL_PASSWORD')
mySqlUsername = os.getenv('MYSQL_USERNAME')

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
PyMySQLInstrumentor().instrument()

# Prepare database
conn = pymysql.connect(host=mySqlHost, user=mySqlUsername, password=mySqlPassword)
conn.cursor().execute('create database if not exists myotdb')
conn.select_db("myotdb") 
conn.cursor().execute('create table if not exists mytable (mynumber INT)')

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
    randomNumber = int(random.random()*100)
    try:
        conn.cursor().execute("insert into mytable values (%d)" % randomNumber)
        conn.commit()
    except Exception as e:
        print("Exeception occured:{}".format(e))
    return "Your integer is %d" % randomNumber

# Run Flask
app.run(host='0.0.0.0', port=8080, threaded=True)
```

MySQL pro jednoduchost udělám bez jakékoli perzistence nebo redundance jen jako jednoduchý Pod v Kubernetes.


```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  ports:
  - port: 3306
  selector:
    app: mysql
  clusterIP: None
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  selector:
    matchLabels:
      app: mysql
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - image: mysql:5.6
        name: mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: Azure12345678
        ports:
        - containerPort: 3306
          name: mysql
```

Docker image jsme publikoval s tagem clanek-v5 a musíme také přidat proměnné prostředí s heslem do MySQL.

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
          image: tkubica/opentelemetry:clanek-v5
          ports:
            - containerPort: 8080
          env:
            - name: MYSQL_HOST
              value: mysql
            - name: MYSQL_PASSWORD
              value: Azure12345678
            - name: MYSQL_USERNAME
              value: root
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
          image: tkubica/opentelemetry:clanek-v5
          ports:
            - containerPort: 8080
          env:
            - name: MYSQL_HOST
              value: mysql
            - name: MYSQL_PASSWORD
              value: Azure12345678
            - name: MYSQL_USERNAME
              value: root
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

Podívejme se na posbírané trasování. Máme tady čas spotřebovaný přístupem do MySQL a v atributech další údaje jako je SQL dotaz.

![](/images/2020/2020-08-06-20-03-43.png){:class="img-fluid"}

# Vlastní span
Zatím jsme využívali knihovny, které za nás prováděly instrumentaci pro použité frameworky jako bylo pymysql, Flask nebo Requests. V našem kódu je ale v proceduře processData nejen zápis do databáze, ale také nějaké náročnější zpracování dat, které simulujeme uspáním. Tato logika není samostatná REST služba, přesto má zásadní vliv na celkový čas zpracování a rád bych ji v trasování viděl. Je to tedy místo, kde si chci založit span tak jak sám potřebuji.

Výsledek je velmi jednoduchý:

```python
import flask
import requests
import os
import time
import pymysql
import random

# Import Open Telemetry tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.ext.requests import RequestsInstrumentor
from opentelemetry.ext.pymysql import PyMySQLInstrumentor

# Import Azure Monitor
from azure_monitor import AzureMonitorSpanExporter
from azure_monitor import AzureMonitorMetricsExporter
from azure_monitor.sdk.auto_collection import AutoCollection
from opentelemetry.ext.wsgi import OpenTelemetryMiddleware

# Gather configurations
appInsightsConnectionString = "InstrumentationKey=%s" % os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY')
mySqlHost = os.getenv('MYSQL_HOST')
mySqlPassword = os.getenv('MYSQL_PASSWORD')
mySqlUsername = os.getenv('MYSQL_USERNAME')

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
PyMySQLInstrumentor().instrument()

# Prepare database
conn = pymysql.connect(host=mySqlHost, user=mySqlUsername, password=mySqlPassword)
conn.cursor().execute('create database if not exists myotdb')
conn.select_db("myotdb") 
conn.cursor().execute('create table if not exists mytable (mynumber INT)')

# Get tracer
tracer = trace.get_tracer(__name__)

# Flask routing
@app.route('/')
def init():
    trace.get_current_span().set_attribute("order_id", "00123456")
    response = requests.get(os.getenv('REMOTE_ENDPOINT', default="http://127.0.0.1:8080/data"))
    return "Response from data API: %s" % response.content.decode("utf-8") 

@app.route('/data')
def data():
    # Custom span
    with tracer.start_as_current_span(name="processData"):
        result = processData()
    return result

# Processing
def processData():
    time.sleep(0.2)
    randomNumber = int(random.random()*100)
    try:
        conn.cursor().execute("insert into mytable values (%d)" % randomNumber)
        conn.commit()
    except Exception as e:
        print("Exeception occured:{}".format(e))
    return "Your integer is %d" % randomNumber

# Run Flask
app.run(host='0.0.0.0', port=8080, threaded=True)
```

V YAML souboru pro nasazení nebudu měnit nic, kromě image s tímto novým kódem, který mám na tagu clanek-v6.

Nasadíme, provoláme a ujistěme se, že v našem trasování teď máme další součástku.

![](/images/2020/2020-08-06-20-19-26.png){:class="img-fluid"}

# Kusto
Účelem dnešního článku není detailnější povídání o Kusto Query Language. O něm už jsem na tomto blogu psal a ještě budu, nicméně pojďme si jen krátce ukázat, že veškerá data máme k dispozici a můžeme si s nimi pohrát.

Takhle třeba dostanu requesty za posledních 5 dní.

```
requests
| where timestamp >= ago(5d)
```

![](/images/2020/2020-08-10-06-39-25.png){:class="img-fluid"}

![](/images/2020/2020-08-10-06-40-55.png){:class="img-fluid"}
![](/images/2020/2020-08-10-06-41-14.png){:class="img-fluid"}
![](/images/2020/2020-08-10-06-41-35.png){:class="img-fluid"}

Takhle může vypadat jednoduchá sumarizace úspěšných a neúspěšných requestů.

```
requests
| where timestamp >= ago(5d)
| summarize count() by success
| render piechart 
```

![](/images/2020/2020-08-10-06-43-31.png){:class="img-fluid"}

A co jejich vývoj v čase?

```
requests
| where timestamp >= ago(5d)
| summarize count() by bin(timestamp, 5m), success
| render timechart 
```

![](/images/2020/2020-08-10-06-45-42.png){:class="img-fluid"}

Pojďme spočítat průměrnou odezvu requestu podle Kubernetes nodu, aplikace a instance (Podu).

```
requests
| where timestamp >= ago(5d)
| where success == True
| extend node = tostring(customDimensions.kube_node_name)
| where node != ""
| summarize avg(duration) by node, cloud_RoleName, cloud_RoleInstance
```

![](/images/2020/2020-08-10-06-56-42.png){:class="img-fluid"}

V tabulce dependencies máme například náš mysql a jeho databázové dotazy. Co kdybychom si vypsali četnost jednotlivých dotazů? V tom bude jeden problém - v logu vidíme i zapisované hodnoty a těch bude dost. Ideální by bylo nějak data zredukovat a hledat spíše kategorie hlášek. Ať ty dotazy nějaký robot proběhne a ty co jsou hodně podobné považuje za jednu kategorii. Na mém málo vytříbeném vzorku dat to nebude úplně ono, ale přece to zkusme.

```
dependencies
| where timestamp >= ago(5d)
| where target == "mysql"
| extend statement = tostring(customDimensions["db.statement"])
| reduce by statement
```

![](/images/2020/2020-08-10-07-13-14.png){:class="img-fluid"}

Do složitějších věcí se pouštět nebudeme, dnes to není o Kusto. Nicméně zkusme hodit nějaký výčet nápadů co s tím můžete dělat:
- Hledat anomálie jako je nerovnoměrný výsledek tam, kde čekáme rovnoměrný (např. výpočet směrodatné odchylky, kterou čekáme velmi malou) například průměrná odezva by měla být stejná dle Kubernetes Nodu, Podu a tak podobně. Pokud nějaká instance má parametry výrazně mimo hodnoty ostatních instancí, možná je s ní něco špatně.
- Zkoumat kontribuci jednotlivých komponent vzhledem k celkové latenci při zvyšování zátěže při testu, tedy zjistit kde je primární limit konkrétního sizingu aplikace (DB odezva, konkrétní mikroslužba apod.)
- Korelovat aplikační telemetrii s jinými informacemi přes Kusto jazyk:
  - Infrastrukturní logy a telemetrie
  - Byznys informace napojené do Kusto (velikost objednávky, maržovost, upsell a crosssell úspěšnost, počet hvězdiček apod.)
- Analyzovat chování různých verzí aplikace pro canary releasování a A/B testing
- Měřit dopad chyb a problémů na uživatelskou bázi vzhledem k přihlášenému uživateli (počet zasažených uživatelů, počet zasažených uživatelů premium nebo VIP služby)
- Predikovat load a využít k plánovanému škálování (jako doplněk k autoscalingu)
- Počítat SLO metriky typu komponovaný koeficient uživatelské zkušenosti (telemetrie a chybovost kritických součástí aplikace, např. funkce přihlášení, nalezení produktu, objednávka, platba)

# Workbook
Kromě nativního GUI a vlastních dotazů můžeme data vizualizovat ještě Workbooky. V prostředí jich už je pár hotových.

![](/images/2020/2020-08-10-09-04-44.png){:class="img-fluid"}

![](/images/2020/2020-08-10-09-05-45.png){:class="img-fluid"}
![](/images/2020/2020-08-10-09-06-03.png){:class="img-fluid"}

Založme si nový vlastní workbook.

![](/images/2020/2020-08-10-09-07-46.png){:class="img-fluid"}

Přidáme text.

![](/images/2020/2020-08-10-09-08-23.png){:class="img-fluid"}

Přidáme parametr - v našem případě půjde o výběr časového rozmezí.

![](/images/2020/2020-08-10-09-11-22.png){:class="img-fluid"}

Přidáme prvek typu query a použijeme jeden z dotazů, co jsme si formulovali dříve. Jedinou změnou je, že pro selekci času použijeme výše uvedený parametr.

![](/images/2020/2020-08-10-09-15-16.png){:class="img-fluid"}

Pojďme si to graficky trochu vylepšit. Přidáme seskupovací prvek, ukážeme hodnoty přepočítané na rozumné řády automaticky a obravíme výsledky.

![](/images/2020/2020-08-10-09-17-28.png){:class="img-fluid"}
![](/images/2020/2020-08-10-09-20-28.png){:class="img-fluid"}

Takhle to pak vypadá.

![](/images/2020/2020-08-10-09-20-59.png){:class="img-fluid"}

V nastaveních můžeme ještě povolit věci jako export tlačítko do Excelu, spuštění query v novém okně nebo přišpendlení na dashboard.

![](/images/2020/2020-08-10-09-21-38.png){:class="img-fluid"}

![](/images/2020/2020-08-10-09-22-08.png){:class="img-fluid"}

S workbooky se toho dá dělat samozřejmě daleko víc, ale to bude obsahem jiného seriálu na tomto blogu.

# Grafana
Vizualizace zabudované v portálu nejsou jedinou metodou jak dostat data na hezkou obrazovku. Můžete je napojit do mocného PowerBI, kde se dají výborně kombinovat s dalšími zdroji a nativně podporují různé enterprise vlastnosti včetně bezpečného přihlášení. Dalším oblíbeným nástrojem pro vizualizaci je Grafana, která nabízí konektor na Azure Monitor jako datový zdroj.

Nahoďme si Grafana na zkoušeku jako kontejner v Azure.

```bash
az group create -n ot -l westeurope
az container create -g ot -n grafana --image grafana/grafana --ports 3000 --ip-address Public
```

Přidáme Azure Monitor datový zdroj.

![](/images/2020/2020-08-11-07-44-42.png){:class="img-fluid"}

Grafana bude do Azure Monitor Application Insights sahat přes API klíč, tak si ho vygenerujeme.

![](/images/2020/2020-08-11-07-45-45.png){:class="img-fluid"}

Nastavíme napojení a můžeme vytvořit graf s přístup do metrik. V těch najdeme základní telemetrii a jednoduše se s ní pracuje ať už ve workbooku nebo Grafaně.

![](/images/2020/2020-08-11-07-50-25.png){:class="img-fluid"}

Stejně jako ve workbooku můžete svoje složitější vyhledávací a analytické potřeby vyřešit vlastním Kusto dotazem do systému.

# Alert
Na posbírané metriky a události můžete automatizovaně reagovat a to buď jednoduše na Metrics nebo i složitěji přes Kusto dotazy. Dá se tak reagovat prakticky na cokoli jakkoli.

Vytvořme nový alert na základě jednoduchých metrik, v mém případě v kategorii dependence a zajímá mě MySQL.

![](/images/2020/2020-08-11-07-24-38.png){:class="img-fluid"}

Můžu nastavit nějaké číslo, kdy chci spustit akci, ale já použil dynamické řešení. Azure bude analyzovat minulé časové řady a detekovat anomálie.

![](/images/2020/2020-08-11-07-26-09.png){:class="img-fluid"}

V závislosti na nastavení citlivosti můžu kouknout na aktuální historická data a prohlédnout si spočítané pásmo a kde by v minulosti alert vznikl (což sedí - ona špička je perf test co jsem dělal). V mém případě je to jednoduché "rovné" pásmo, ale v realitě uvidíte, že se ML naučí běžné špičky během dne, během pracovních dní vs. víkendů a tak podobně.

![](/images/2020/2020-08-11-07-27-03.png){:class="img-fluid"}

Co se má stát? Pustíme si action group, kde se dá připravit hned několik různých akcí.

![](/images/2020/2020-08-11-07-27-32.png){:class="img-fluid"}

Vytvořím novou action group.

![](/images/2020/2020-08-11-07-27-59.png){:class="img-fluid"}

Můžu zadat jednoduchou notifikaci například na vlastníka zdroje nebo email, SMS apod.

![](/images/2020/2020-08-11-07-28-22.png){:class="img-fluid"}

Pokročilejší akce zahrnují vyvolání automatizace jako je runbook (PowerShell nebo Python skript), Azure Function (libovolný kód třeba v Java, Node, Python nebo C#), přímá ITSM integrace, Webhook nebo Logic App (orchestrační workflow nástroj s tisícovkou různých konektorů třeba do Teams, Slack, Jira, ServiceNow a dalších systémů).

![](/images/2020/2020-08-11-07-29-05.png){:class="img-fluid"}




Nevěřili byste (no, vlastně spíš ano) kolik vídám lidí, co si stále ředstavují monitoring aplikace jako grafík zatížení CPU, spotřebu paměti a v lepším případě počet requestů za vteřinu. V posledních dvou dílech jsem takové z vás doufám přesvědčil, že aplikační monitoring je dnes úplně jinde a zaměřuje se na měření uživatelské zkušenosti, trasování s vhledem do příčin a důsledků s jejich vývojem v čase i korelaci se byznysovými metrikami. Příště bychom se měli podívat na to, jak s využitím OpenTelemetry kromě trasování vytáhnout i nějaké naše vlastní metriky přímo z aplikace, promluvit si o push vs. pull metrik a jak může OpenTelemetry SDK sjednotit jejich generování ať už je chcete tlačit třeba do Azure Monitor pro korelaci, strojové učení a globální pohled a současně táhnout z Prometheus třeba pro účely automatizace škálování uvnitř clusteru.

