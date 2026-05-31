---
format_version: 1
title: "Deep dive do observability AI agentů s Microsoft Agent Framework - OpenTelemetry semantic conventions a použití OTEL kolektoru"
subtitle: "OpenTelemetry semantic conventions, Microsoft Agent Framework a proč dát mezi aplikaci a backend OTEL Collector."
slug: "ai-observability-1"
date: "2025-10-29"
language: "cs-CZ"
status: "experimental"
canonical_url: "/2025/ai-observability-1/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Deep dive do observability AI agentů s Microsoft Agent Framework - OpenTelemetry semantic conventions a použití OTEL kolektoru

AI agenti a multi-agentní workflow jsou pro debugging, nákladovost a bezpečnost citlivější než klasické CRUD API. Bez dobré observability jen těžko zjistíte, proč se odpovědi liší, kam mizí tokeny nebo kde roste latence.

Celé řešení najdete na [mém GitHubu](https://github.com/tkubica12/d-ai-maf-observability). Cílem série je ukázat, jak dostat maximum z otevřených standardů, abyste nemuseli přepisovat kód při změně backendu a zároveň měli data kvalitně očištěná a levná.

::: group id="uvod" title="Co dnes stavíme"

::: card number="01" title="Mapa dílu" default="open"
Microsoft Agent Framework je výborný vývojový kit pro tvorbu AI agentů a multi-agentních řešení - od jednoduchých scénářů přes orchestrační workflow až po plný multiagent přístup po vzoru Magentic nebo Group Chat topologií.

::: reveal title="Proč právě Microsoft Agent Framework"
Umí používat OpenAI, Foundry včetně non-OpenAI modelů, Foundry agenty, externí agenty přes A2A, ale i vlastní řešení. V této sérii se zaměřím na observabilitu a závěry z ní můžete samozřejmě aplikovat i na jiné frameworky jako Lang Graph.
:::
::: reveal title="Backendy, které budu používat"
Všechno budeme stavět na otevřených standardech. Jako vizualizační backendy využijeme Aspire Dashboard, LangFuse, Prometheus s Grafanou, ale i zabudované funkce Azure platformy v AI Foundry a Application Insights.
:::
Dnes si postupně probereme instrumentaci kódu a hlavně proč rád používám OpenTelemetry Collector mezi aplikací a monitorovacím řešením.
:::
:::
::: group id="zaklady" title="Základy instrumentace"

::: card number="02" title="OpenTelemetry a sémantické konvence pro genAI" default="open"
OpenTelemetry podporuje přidávání jakýchkoli atributů do trasování. V minulosti to vytvářelo zmatek, protože OpenInference, LangFuse nebo LangSmith pojmenovávaly atributy různě. Standard jste sice měli, ale hotové reporty, vizualizace a analýzy nefungovaly univerzálně.

Dnes existují [semantic conventions pro GenAI](https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai). Microsoft je dodržuje a rozšířil je i pro multi-agent scénáře. Microsoft Agent Framework tyto konvence používá, takže data jsou přenositelnější mezi backendy.

::: reveal title="Ukázka výsledku v trasování"
![Ukázka GenAI spanů podle OpenTelemetry semantic conventions](/images/2025/2025-10-27-16-23-20.png)
:::
:::
::: card number="03" title="Instrumentace Microsoft Agent Frameworku" default="open"
Zapnutí observability v Microsoft Agent Framework je v základním režimu otázka jednoho importu a jednoho volání.

```python label="Zapnutí observability v Microsoft Agent Framework"
from agent_framework.observability import get_tracer, get_meter, setup_observability
setup_observability(
    enable_sensitive_data=enable_sensitive,
    otlp_endpoint=otlp_endpoint,
)
```

::: reveal title="Proč k tomu v demo aplikaci přidávám víc"
- Chci do spanů integrovat vlastní dynamické atributy pro agregace a vyhledávání: user id, session id, role, experiment.
- Chci vlastní atributy propisovat i do vnitřních spanů, aby se mi na backendu lépe filtrovalo, i když tím zvyšuji objem dat.
- Kromě tracingu posílám aplikační logy a metriky, včetně vlastních.
- Vedle AI komponent instrumentuji HTTP volání a přístupy do Redis, SQL nebo PostgreSQL přes autoinstrumentaci.
:::
:::
::: card number="04" title="Rozšíření o vlastní atributy" default="open"
S využitím baggage span procesoru to není těžké. Navíc se zdá, že kontext odchází i v HTTP headeru, takže se atributů lze chytit například v zavolaném nástroji.

```python label="Propisování vlastních atributů přes baggage"
# Add BaggageSpanProcessor to automatically propagate baggage to all spans
from opentelemetry import trace as trace_api
tracer_provider = trace_api.get_tracer_provider()
if hasattr(tracer_provider, 'add_span_processor'):
    baggage_processor = BaggageSpanProcessor()
    tracer_provider.add_span_processor(baggage_processor)
    logger.info("BaggageSpanProcessor registered for automatic context propagation")

from opentelemetry import baggage, context

ctx = context.get_current()
ctx = baggage.set_baggage("user.id", user_context.get("user.id", "unknown"), ctx)
ctx = baggage.set_baggage("session.id", user_context.get("session.id", "unknown"), ctx)
ctx = baggage.set_baggage("organization.department", user_context.get("organization.department", "unknown"), ctx)
roles = user_context.get("user.roles", [])
if roles:
    ctx = baggage.set_baggage("user.roles", ",".join(roles), ctx)
token = context.attach(ctx)
```
:::
:::
::: group id="kolektor" title="OpenTelemetry kolektor jako provozní rozbočovač"

::: card number="05" title="Kolektor: routing, anonymizace, filtrace a konverze" default="open"
Tady se dnes zastavíme déle. OpenTelemetry SDK umí exportéry přímo do backendů, ale OpenTelemetry Collector mi dává jeden stabilní OTLP endpoint pro aplikaci a provozní logiku mimo kód.

::: callout type="rule" title="Proč kolektor"
Buildím agenty jednou. Routing, anonymizaci, sampling, více backendů i převody ladím rychle iteracemi v konfiguraci collectoru, ne releasem aplikace.
:::
::: steps title="Co tím získám"
1. **Oddělení aplikace od backendů** - kontejner aplikace zná jeden OTEL endpoint a kolektor řeší autentizaci, cílové backendy i rozdíly mezi clustery.
2. **Více destinací najednou** - pro rychlý troubleshooting mám rád Aspire Dashboard, pro analytiku a dlouhodobé uložení třeba Application Insights.
3. **Transformace a anonymizace** - kolektor umí filtrovat atributy, odstraňovat obsah konverzací a posílat rozdílně očištěná data různým týmům.
4. **Výkon a spolehlivost** - aplikace odloží telemetrii blízkému kolektoru a ten řeší doručení, retry i bufferování.
5. **OTTL konverze a sampling** - umím přejmenovávat atributy, obohacovat data, převádět signály a snižovat náklady chytrým výběrem trace.
:::
::: reveal title="Tři praktické kategorie výstupů"
- **Enterprise logy v Azure** - auditovatelnost a provoz, ale bez samotného obsahu zpráv.
- **AI observability logy** - plný obsah konverzací jen pro vybrané uživatele nebo souhlasy, typicky pro evaluace.
- **Dev logy** - zamaskované identifikátory, emaily, IP adresy i obsah zpráv pro běžný vývojářský troubleshooting.
:::
::: reveal title="PII pseudonymizace přes OTTL"
Pro PII pseudonymizaci umí OTTL kombinovat `set`, `delete_key`, `delete_matching_keys`, `replace_all_patterns` a hashování `SHA256()`. V praxi bych přidal SALT z env proměnné, aby hash lépe odolával slovníkovým útokům.
:::
::: reveal title="Tail-based sampling jako úspora bez slepoty"
Sampling nemusí být jen procento. Tail-based sampling drží trace chvíli v kolektoru, podívá se na výsledek a pošle například chyby, pomalé požadavky, VIP uživatele a malý baseline vzorek. Platíte méně, ale neztratíte nejdůležitější případy.

```yaml label="Tail-based sampling v kolektoru"
processors:
  tail_sampling:
    decision_wait: 30s          # jak dlouho držím buffery
    num_traces: 50000           # cílové množství in-memory
    expected_new_traces_per_sec: 200
    policies:
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: slow
        type: latency
        latency:
          threshold_ms: 2000    # nad 2s vždy zachovat
      - name: vip_users
        type: string_attribute
        string_attribute:
          key: user.is_vip
          values: ["true"]
      - name: baseline_sample
        type: probabilistic
        probabilistic:
          hash_seed: 22
          sampling_percentage: 5

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, batch]
      exporters: [otlp, azuremonitor]
```
:::
::: reveal title="Celá ukázka Helm šablony OTEL kolektoru"
Výborné je, že tohle všechno lze v AKS držet v ConfigMap a Kubernetes manifestech. Aplikace pak stále posílá na jeden OTLP endpoint a kolektor rozhoduje, co kam odejde.

```yaml label="Helm šablona OTEL kolektoru v AKS"
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "maf-demo.fullname" . }}-otel-collector-config
  labels:
    {{- include "maf-demo.labels" . | nindent 4 }}
    app.kubernetes.io/component: otel-collector
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318

    processors:
      batch:
        timeout: 5s
        send_batch_size: 1024
      memory_limiter:
        check_interval: 1s
        limit_mib: 512
      
      # Transform processor for anonymization - strips PII and sensitive data
      transform/anonymize:
        error_mode: ignore
        trace_statements:
          - context: span
            statements:
              # Pseudonymize user.id using SHA256 for consistent hashing
              - set(attributes["user.id"], SHA256(attributes["user.id"])) where attributes["user.id"] != nil
              # Remove VIP status - boolean flag considered PII
              - delete_key(attributes, "user.is_vip")
              - delete_key(attributes, "user.roles")
              # Pseudonymize department for correlation while protecting identity
              - set(attributes["organization.department"], SHA256(attributes["organization.department"])) where attributes["organization.department"] != nil
              # Pseudonymize session and thread IDs
              - set(attributes["session.id"], SHA256(attributes["session.id"])) where attributes["session.id"] != nil
              - set(attributes["thread.id"], SHA256(attributes["thread.id"])) where attributes["thread.id"] != nil
              # Strip tool arguments and results - may contain sensitive data
              - delete_key(attributes, "tool.arguments")
              - delete_key(attributes, "tool.result")
              # Strip GenAI input/output messages - contains user queries and LLM responses
              - delete_key(attributes, "gen_ai.input.messages")
              - delete_key(attributes, "gen_ai.output.messages")
              - delete_key(attributes, "gen_ai.prompt")
              - delete_key(attributes, "gen_ai.completion")
              - delete_key(attributes, "gen_ai.request.model")
              - delete_key(attributes, "gen_ai.response.model")
              # Strip any other GenAI content using pattern matching
              - delete_matching_keys(attributes, "gen_ai\\..*\\.content")
              - delete_matching_keys(attributes, "gen_ai\\..*messages.*")
              # Redact common PII patterns in remaining string attributes
              - replace_all_patterns(attributes, "value", "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b", "EMAIL_REDACTED")
              - replace_all_patterns(attributes, "value", "\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b", "PHONE_REDACTED")
              - replace_all_patterns(attributes, "value", "\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b", "CARD_REDACTED")
          - context: resource
            statements:
              # Pseudonymize user.id in resource attributes
              - set(attributes["user.id"], SHA256(attributes["user.id"])) where attributes["user.id"] != nil
              # Remove VIP status from resource
              - delete_key(attributes, "user.is_vip")
              - delete_key(attributes, "user.roles")
              # Pseudonymize department in resource
              - set(attributes["organization.department"], SHA256(attributes["organization.department"])) where attributes["organization.department"] != nil
              # Pseudonymize session in resource
              - set(attributes["session.id"], SHA256(attributes["session.id"])) where attributes["session.id"] != nil
        
        log_statements:
          - context: log
            statements:
              # Pseudonymize user identifiers in logs
              - set(attributes["user.id"], SHA256(attributes["user.id"])) where attributes["user.id"] != nil
              # Remove sensitive log attributes
              - delete_key(attributes, "user_message")
              - delete_key(attributes, "response")
              - delete_key(attributes, "tool_name")
              - delete_key(attributes, "arguments")
              - delete_key(attributes, "result")
              - delete_key(attributes, "user.is_vip")
              - delete_key(attributes, "user.roles")
              # Pseudonymize department and session
              - set(attributes["organization.department"], SHA256(attributes["organization.department"])) where attributes["organization.department"] != nil
              - set(attributes["session.id"], SHA256(attributes["session.id"])) where attributes["session.id"] != nil
              # Redact PII patterns in log body if it's a string
              - replace_all_patterns(attributes, "value", "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b", "EMAIL_REDACTED") where IsString(body)
              - replace_all_patterns(attributes, "value", "\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b", "PHONE_REDACTED") where IsString(body)
          - context: resource
            statements:
              # Pseudonymize user.id in resource attributes for logs
              - set(attributes["user.id"], SHA256(attributes["user.id"])) where attributes["user.id"] != nil
              # Pseudonymize department in resource for logs
              - set(attributes["organization.department"], SHA256(attributes["organization.department"])) where attributes["organization.department"] != nil
        
        metric_statements:
          - context: datapoint
            statements:
              # Pseudonymize user identifiers in metrics
              - set(attributes["user.id"], SHA256(attributes["user.id"])) where attributes["user.id"] != nil
              # Remove VIP status from metrics
              - delete_key(attributes, "user.is_vip")
              # Pseudonymize department in metrics
              - set(attributes["organization.department"], SHA256(attributes["organization.department"])) where attributes["organization.department"] != nil
          - context: resource
            statements:
              # Pseudonymize user.id in resource attributes for metrics
              - set(attributes["user.id"], SHA256(attributes["user.id"])) where attributes["user.id"] != nil
              # Remove VIP status from resource for metrics
              - delete_key(attributes, "user.is_vip")
              # Pseudonymize department in resource for metrics
              - set(attributes["organization.department"], SHA256(attributes["organization.department"])) where attributes["organization.department"] != nil

    exporters:
      # Console exporter for troubleshooting
      debug:
        verbosity: detailed
        sampling_initial: 5
        sampling_thereafter: 200
      
      # OTLP exporter for Aspire Dashboard
      otlp:
        endpoint: {{ include "maf-demo.fullname" . }}-aspire-dashboard:18889
        tls:
          insecure: true
      
      # OTLP exporter for Anonymized Aspire Dashboard
      otlp/anonymized:
        endpoint: {{ include "maf-demo.fullname" . }}-aspire-dashboard-anon:18889
        tls:
          insecure: true
      
      # Azure Monitor exporter for Application Insights
      # Supports traces and logs (metrics not supported by App Insights OTLP ingestion)
      azuremonitor:
        connection_string: {{ .Values.appInsights.connectionString | quote }}
      
      # Langfuse OTLP exporter for LLM observability
      # Exports traces to Langfuse via HTTP/protobuf protocol
      otlphttp/langfuse:
        endpoint: {{ .Values.langfuse.endpoint | default "http://langfuse-web.langfuse.svc.cluster.local:3000/api/public/otel" | quote }}
        headers:
          Authorization: {{ .Values.langfuse.authorization | default "Basic " | quote }}
      
      # Prometheus Remote Write exporter for Azure Monitor Prometheus
      # Uses sidecar container for Azure AD token management
      # The sidecar listens on localhost:8081 and injects the Authorization header
      prometheusremotewrite:
        endpoint: "http://localhost:8081/api/v1/write"
        tls:
          insecure: true
        resource_to_telemetry_conversion:
          enabled: true

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [otlp, azuremonitor, otlphttp/langfuse]
        
        # Anonymized trace pipeline - strips PII before sending to anonymized dashboard
        traces/anonymized:
          receivers: [otlp]
          processors: [memory_limiter, transform/anonymize, batch]
          exporters: [otlp/anonymized]
        
        metrics:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [otlp, prometheusremotewrite]
        
        # Anonymized metrics pipeline
        metrics/anonymized:
          receivers: [otlp]
          processors: [memory_limiter, transform/anonymize, batch]
          exporters: [otlp/anonymized]
        
        logs:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [otlp, azuremonitor]
        
        # Anonymized logs pipeline
        logs/anonymized:
          receivers: [otlp]
          processors: [memory_limiter, transform/anonymize, batch]
          exporters: [otlp/anonymized]
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "maf-demo.fullname" . }}-otel-collector
  labels:
    {{- include "maf-demo.labels" . | nindent 4 }}
    app.kubernetes.io/component: otel-collector
    azure.workload.identity/use: "true"
  annotations:
    azure.workload.identity/client-id: {{ .Values.agent.clientId }}
    azure.workload.identity/tenant-id: {{ .Values.agent.tenantId }}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "maf-demo.fullname" . }}-otel-collector
  labels:
    {{- include "maf-demo.labels" . | nindent 4 }}
    app.kubernetes.io/component: otel-collector
spec:
  replicas: 1
  selector:
    matchLabels:
      {{- include "maf-demo.otelCollectorSelectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "maf-demo.otelCollectorSelectorLabels" . | nindent 8 }}
        azure.workload.identity/use: "true"
    spec:
      serviceAccountName: {{ include "maf-demo.fullname" . }}-otel-collector
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector-contrib:{{ .Values.otelCollector.tag }}
        ports:
        - containerPort: 4317  # OTLP gRPC
          name: otlp-grpc
          protocol: TCP
        - containerPort: 4318  # OTLP HTTP
          name: otlp-http
          protocol: TCP
        - containerPort: 8888  # Metrics
          name: metrics
          protocol: TCP
        - containerPort: 8889  # Prometheus metrics
          name: prometheus
          protocol: TCP
        volumeMounts:
        - name: config
          mountPath: /etc/otelcol-contrib
          readOnly: true
        resources:
          {{- toYaml .Values.otelCollector.resources | nindent 10 }}
      # Sidecar container for Azure Monitor Prometheus remote write authentication
      # This container obtains Azure AD tokens using workload identity and proxies
      # Prometheus remote write requests with the Authorization header injected
      - name: prom-remotewrite
        image: mcr.microsoft.com/azuremonitor/containerinsights/ciprod/prometheus-remote-write/images:prom-remotewrite-20250814.1
        imagePullPolicy: Always
        ports:
        - name: rw-port
          containerPort: 8081
          protocol: TCP
        env:
        - name: INGESTION_URL
          value: {{ .Values.prometheus.remoteWriteEndpoint | quote }}
        - name: LISTENING_PORT
          value: "8081"
        - name: IDENTITY_TYPE
          value: "workloadIdentity"
        - name: CLUSTER
          value: {{ .Values.clusterName | default "aks-cluster" | quote }}
        livenessProbe:
          httpGet:
            path: /health
            port: rw-port
          initialDelaySeconds: 10
          timeoutSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: rw-port
          initialDelaySeconds: 10
          timeoutSeconds: 10
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 200m
            memory: 128Mi
      volumes:
      - name: config
        configMap:
          name: {{ include "maf-demo.fullname" . }}-otel-collector-config
---
apiVersion: v1
kind: Service
metadata:
  name: {{ include "maf-demo.fullname" . }}-otel-collector
  labels:
    {{- include "maf-demo.labels" . | nindent 4 }}
    app.kubernetes.io/component: otel-collector
spec:
  type: ClusterIP
  ports:
    - port: 4317
      targetPort: otlp-grpc
      protocol: TCP
      name: otlp-grpc
    - port: 4318
      targetPort: otlp-http
      protocol: TCP
      name: otlp-http
    - port: 8888
      targetPort: metrics
      protocol: TCP
      name: metrics
  selector:
    {{- include "maf-demo.otelCollectorSelectorLabels" . | nindent 4 }}
```
:::
:::
:::
::: summary-grid
- **Standardizujte atributy**: GenAI semantic conventions jsou základ pro přenositelné reporty a backendy.
- **Instrumentujte málo, ale chytře**: základní MAF observability zapnete jedním voláním, vlastní kontext přidejte přes baggage.
- **Dejte mezi aplikaci a backend kolektor**: routing, anonymizaci, sampling a více výstupů držte mimo aplikační kód.
:::


::: closing
V dalším díle se podíváme, jak se taková telemetrie chová v konkrétních backendových nástrojích a co z ní jde prakticky vyčíst pro debugging, náklady a evaluace.
:::
