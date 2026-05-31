---
format_version: 1
title: "Deep dive into AI agent observability with Microsoft Agent Framework - OpenTelemetry semantic conventions and using the OTEL collector"
subtitle: "OpenTelemetry semantic conventions, Microsoft Agent Framework, and why to put an OTEL Collector between app and backend."
slug: "ai-observability-1"
date: "2025-10-29"
language: "en"
source_language: "cs-CZ"
source_slug: "ai-observability-1"
translation: "machine"
translated_from_hash: "E29A0858D3C2DE828D1B1AED9A6B7FE61B86ACB315DD64C9436D1BAC4A8203A1"
translation_status: "current"
status: "experimental"
canonical_url: "/en/2025/ai-observability-1/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Deep dive into AI agent observability with Microsoft Agent Framework - OpenTelemetry semantic conventions and using the OTEL collector

AI agents and multi-agent workflows are more sensitive than classic CRUD APIs when it comes to debugging, cost, and security. Without good observability it is hard to understand why answers differ, where tokens disappear, or where latency grows.

You can find the full solution on [my GitHub](https://github.com/tkubica12/d-ai-maf-observability). The goal of the series is to show how to get the most from open standards, so you do not have to rewrite code when switching backends while still keeping data well cleaned and inexpensive.

::: group id="uvod" title="What we are building today"

::: card number="01" title="Episode map" default="open"
Microsoft Agent Framework is an excellent development kit for building AI agents and multi-agent solutions - from simple scenarios through orchestration workflows all the way to a full multi-agent approach inspired by Magentic or Group Chat topologies.

::: reveal title="Why Microsoft Agent Framework"
It can use OpenAI, Foundry including non-OpenAI models, Foundry agents, external agents over A2A, and custom solutions. In this series I focus on observability, and you can of course apply the conclusions to other frameworks such as Lang Graph.
:::
::: reveal title="Backends I will use"
We will build everything on open standards. For visualization backends we will use Aspire Dashboard, LangFuse, Prometheus with Grafana, and built-in Azure platform capabilities in AI Foundry and Application Insights.
:::
Today we will go step by step through code instrumentation and, most importantly, why I like placing OpenTelemetry Collector between the application and the monitoring solution.
:::
:::
::: group id="zaklady" title="Instrumentation basics"

::: card number="02" title="OpenTelemetry and semantic conventions for genAI" default="open"
OpenTelemetry supports adding arbitrary attributes to traces. In the past this caused confusion because OpenInference, LangFuse, and LangSmith named attributes differently. You had the standard, but ready-made reports, visualizations, and analyses did not work universally.

Today there are [semantic conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai). Microsoft follows them and extended them for multi-agent scenarios as well. Microsoft Agent Framework uses these conventions, making the data more portable across backends.

::: reveal title="Example of the result in tracing"
![Ukázka GenAI spanů podle OpenTelemetry semantic conventions](/images/2025/2025-10-27-16-23-20.png)
:::
:::
::: card number="03" title="Microsoft Agent Framework instrumentation" default="open"
Enabling observability in Microsoft Agent Framework je v základním režimu otázka jednoho importu a jednoho volání.

```python label="Enabling observability in Microsoft Agent Framework"
from agent_framework.observability import get_tracer, get_meter, setup_observability
setup_observability(
    enable_sensitive_data=enable_sensitive,
    otlp_endpoint=otlp_endpoint,
)
```

::: reveal title="Proč k tomu v demo aplikaci přidávám víc"
- I want dynamic custom attributes in spans for aggregations and searches: user id, session id, roles, experiment.
- I want custom attributes propagated into internal spans so backend filtering is easier, even though it increases data volume.
- Besides tracing, I send application logs and metrics, including my own.
- Beyond AI components, I instrument HTTP calls and access to Redis, SQL, or PostgreSQL through autoinstrumentation.
:::
:::
::: card number="04" title="Adding custom attributes" default="open"
With a baggage span processor this is not difficult. It also seems the context is sent in the HTTP header, so a called tool can pick up the attributes as well.

```python label="Propagating custom attributes through baggage"
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
::: group id="kolektor" title="OpenTelemetry Collector as an operational hub"

::: card number="05" title="Collector: routing, anonymization, filtering, and conversion" default="open"
This is where we will spend more time today. The OpenTelemetry SDK can export directly to backends, but OpenTelemetry Collector gives me one stable OTLP endpoint for the application and keeps operational logic outside the code.

::: callout type="rule" title="Why the collector"
I build agents once. Routing, anonymization, sampling, multiple backends, and conversions are tuned through quick iterations in the collector configuration, not by releasing the application.
:::
::: steps title="What I get from it"
1. **Separating the application from backends** - the application container knows one OTEL endpoint, while the collector handles authentication, target backends, and cluster differences.
2. **Multiple destinations at once** - I like Aspire Dashboard for quick troubleshooting and Application Insights for analytics and long-term retention.
3. **Transformation and anonymization** - the collector can filter attributes, remove conversation content, and send differently cleaned data to different teams.
4. **Performance and reliability** - the application hands telemetry to a nearby collector, which handles delivery, retries, and buffering.
5. **OTTL conversions and sampling** - I can rename attributes, enrich data, convert signals, and reduce costs by selecting traces intelligently.
:::
::: reveal title="Three practical output categories"
- **Enterprise logs in Azure** - auditability and operations, but without the actual message content.
- **AI observability logs** - full conversation content only for selected users or consented scenarios, typically for evaluations.
- **Dev logs** - masked identifiers, emails, IP addresses, and message content for everyday developer troubleshooting.
:::
::: reveal title="PII pseudonymization with OTTL"
For PII pseudonymization, OTTL can combine `set`, `delete_key`, `delete_matching_keys`, `replace_all_patterns`, and `SHA256()` hashing. In practice I would add a SALT from an environment variable so the hash better resists dictionary attacks.
:::
::: reveal title="Tail-based sampling as savings without blindness"
Sampling does not have to be just a percentage. Tail-based sampling keeps a trace in the collector for a while, looks at the outcome, and sends errors, slow requests, VIP users, and a small baseline sample. You pay less without losing the most important cases.

```yaml label="Tail-based sampling in the collector"
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
::: reveal title="Full OTEL Collector Helm template sample"
The great thing is that in AKS all of this can live in a ConfigMap and Kubernetes manifests. The application still sends to one OTLP endpoint, and the collector decides what goes where.

```yaml label="OTEL Collector Helm template in AKS"
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
- **Standardize attributes**: GenAI semantic conventions are the foundation for portable reports and backends.
- **Instrument sparingly but smartly**: basic MAF observability is enabled with one call; add your own context through baggage.
- **Put a collector between the application and backend**: keep routing, anonymization, sampling, and multiple outputs outside application code.
:::


::: closing
In the next part we will look at how this telemetry behaves in specific backend tools and what you can practically read from it for debugging, cost, and evaluations.
:::
