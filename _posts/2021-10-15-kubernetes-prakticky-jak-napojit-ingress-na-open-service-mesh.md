---
layout: post
title: 'Kubernetes prakticky: jak napojit Ingress na Open Service Mesh se zapnutým mTLS (zero trust)'
tags:
- Kubernetes
- Networking
---
Použitím Open Service Mesh, který je k dispozici jako nativní addon do Azure Kubernetes Service, se dá krásně dostat na zero trust postavený na mTLS. Ale Ingress neparticipuje v service mesh - jak tedy zařídit, aby Ingress mohl mluvit se službou v service mesh aniž by tato musela vypnout explicitní kontrolu komunikace, tedy porušit zero trust?

# Zero trust
Nechci teď sáhodlouze popisovat koncepty a důsledky zero trust, to si necháme na jindy, takže jen to relevantní pro dnešní téma. Zero trust principiálně znamená "žádný implicitní trust, všechno je explicitní". Není například lepší a horší síť. Když potřebuji svěřit něco citlivého policistovi v civilu, asi to nezačnu jen tak někomu vykládat v metru - šance, že to policista v civilu opravdu je, by byla extrémně malá. Mám ale předpokládat, že když jsem v budově policie, stačí to rovnou na někoho vysypat? Takhle by fungoval implicitní trust - budova (například analogie interní sítě) ve mě vyvolává pocit důvěry a skutečně pravděpodobnost, že odchytnu někoho kdo mé informace zneužije je menší, ale jistotu rozhodně nemám (návštěvy, jiný personál apod.). Zero trust řešení by znamenalo, že nezačnu předávat informace dokud nebudou splněny explicitní podmínky - například že se mi prokáže svým průkazem a že náš rozhovor neuslyší někdo jiný.

V Kubernetes lze dosáhnout explicitního určení kdo s kým se smí bavit s využitím Network Policy. To je implementace s téměř nulovým vlivem na výkon a spotřebu zdrojů - na základě labelů nebo namespaců říkáte jaký Pod s kterým se smí bavit, ostatní komunikace je blokovaná. Pro řadu scénářů (za mě pro většinu) tohle stačí. Jenže Network Policy je pouze o IP adresách a portech - nerozumí komunikaci a nedokáže tak dělat chytřejší pravidla (definovat která API povolit, jaká slovesa typu GET, POST, DELETE nebo řídit přístup na venkovní služby podle FQDN). Navíc nechrání proti nějakému teoretickému odposlouchávání (nešifruje). Jasně, bezpečnostní vrstvu by mohla implementovat přímo aplikace, jenže to může být náročné koordinovat pokud máte různé týmy, různé programovací jazyky a knihovny nebo komponenty třetích stran, do kterých nelze sáhnout. Service mesh jako je Open Service Mesh tohle vyřešit umí.

# Open Service Mesh a mTLS
OSM podobně jako ostatní service mesh řešení implementuje mTLS tak, že zajistí distribuci certifikátů do Envoy sidecar v každém vašem Podu. Obvykle dojde ke svázání Kubernetes identity v podobě Service Account s certifikátem vystaveným pro tuto identitu a následně možnost v service mesh definovat která identita s kterou smí komunikovat. Tak například takhle vytvořím aplikace app1 a app2 a jejich identity.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app1
  namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1
spec:
  selector:
    matchLabels:
      app: app1
  template:
    metadata:
      labels:
        app: app1
    spec:
      serviceAccount: app1
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app1
spec:
  selector:
    app: app1
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app2
  namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app2
spec:
  selector:
    matchLabels:
      app: app2
  template:
    metadata:
      labels:
        app: app2
    spec:
      serviceAccount: app2
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app2
spec:
  type: ClusterIP
  selector:
    app: app2
  ports:
  - port: 80
    targetPort: 80
```

OSM nastavím tak, aby vyžadovalo explicitní definování všech komunikací (osm install --set OpenServiceMesh.enablePermissiveTrafficPolicy=false) a povolím komunikaci z app1 do app2 pro všechny GET operace. Krásný zero trust.

```yaml
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
---
kind: TrafficTarget
apiVersion: access.smi-spec.io/v1alpha3
metadata:
  name: access-app1-to-app2
spec:
  sources:
  - kind: ServiceAccount
    name: app1
    namespace: default
  destination:
    kind: ServiceAccount
    name: app2
    namespace: default
  rules:
  - kind: HTTPRouteGroup
    name: routes1
    matches:
    - all-gets
```

# Problém Ingress vs. service mesh
Co když ale app2 má být dostupná zvenku? Teoreticky bych ji mohl začlenit do service mesh, tedy získat pro klienta příslušné klientské a serverové certifikáty, říct jakým certifikátům jakých služeb má věřit a zařídit si ručně to, co se děje uvnitř mesh automaticky. V případě OSM nebo Linkerd tohle ještě není podporovaný scénář (Consul Connect nebo Istio takovou podporu už mají), ale stejně to neřeší většinu situací, protože:
- Klientem může být třetí strana, například zákazník, partner
- Klient nemusí být vůbec vhodný pro takové hrátky, třeba mobilní aplikace
- Klient může být jiný tým a koordinace by byla složitější
- Klienta možná nepůjde změnit, je to legacy systém
- Klientů může být strašně moc a distribuce certifikátů k nim může být náročná

Pravděpodobně tedy spíše použijeme Ingress (nebo API Management gateway). Uživatel/klient je terminován na Ingress a z něj jde provoz do aplikací v clusteru. Pokud ale aplikace má OSM se zero trust, tak musí Ingressu věřit, ale zařadit Ingress do service mesh stejným způsobem jako ostatní aplikace je obtížně (mít proxy se sidecar proxy není moc dobrý nápad). Jak to udělat, abych nemusel na OSM zapínat, že pokud přichází provoz ze systému mimo mesh, tak ho prostě pustím (implicit trust)?

# IngressBackend CRD v Open Service Mesh
Open Service Mesh tuhle situaci řeší povolením HTTP komunikace jen z konkrétních podů, kde Ingress běží místo otevření všeho pro všechno (místo permissive mode). Pokud ale nechcete cuknout z plně šifrované cesty, tak dovoluje i připravit certifikát pro Ingress a cestu mezi ingress a service mesh zabezpečit mTLS stejně jako komunikaci uvnitř mesh. Abych si to vyzkoušel, tak bych nejprve rád viděl jak to funguje ručně z curl a pak přidáme opravdový Ingress.

Pozor - potřebuji OSM v 0.10 nebo vyšší a v době psaní článku byl managed addon v AKS stále ve verzi 0.9, takže jsem OSM nahodil ručně stažením CLI a instalací:

```
osm install --set OpenServiceMesh.enablePermissiveTrafficPolicy=false
```

## HTTP varianta simulovaná s curl
Připravím si namespace ext, ve kterém nebude zapnutý service mesh a pošlu do něj Pody. Současně mám v namespace default, kde je OSM zapnutý, instalovanou app1 a app2, které jsem uváděl výše.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ext
  namespace: ext
spec:
  selector:
    matchLabels:
      app: ext
  template:
    metadata:
      labels:
        app: ext
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: ext
  namespace: ext
spec:
  selector:
    app: ext
  ports:
  - port: 80
    targetPort: 80
```

Skočím do podu v ext a zkusím odtud curl http://app2.default. Dle očekávání to nefunguje - komunikuji mimo mesh a nemám permisivní mode. Neexistuje explicitní povolení, zamítnuto.

Aniž bych dával ext do meshe chci teď explicitně povolit http přístup z ext mimo mesh do app2 v mesh. Zdrojem bude Service ext a cílem backend app2 bez mTLS.

```yaml
kind: IngressBackend
apiVersion: policy.openservicemesh.io/v1alpha1
metadata:
  name: http
  namespace: default
spec:
  backends:
  - name: app2
    port:
      number: 80
      protocol: http
    tls:
      skipClientCertValidation: true 
  sources:
  - kind: Service
    namespace: ext
    name: ext
```

Vrátím se do Podu a curl na http://app2.default bude fugovat, ale na nic jiného v mesh ne. Velmi jednoduché. Stačí tedy rozchodit jakoukoli Ingress implementaci, která má dataplane uvnitř clusteru - NGINX, Contour, Traefik - z jejich pohledu tam nebude vidět rozdíl a já přes IngressBackend jen zajistím explicitní povolení pro všechny služby v mesh, které mají být přístupné i z Ingressu. Trochu potíž to bude tam, kde dataplane není uvnitř Kubernetu, třeba s Ingress pro Azure Application Gateway. Navíc skvěle šifruju od klienta do Ingress a od frontend služby do backendů (vnitřek mesh), ale ten spoj mezi tím vším je bez šifrování - to je možná škoda, když už jsem zašel takhle daleko.

## HTTPS varianta simulovaná s curl
OSM od verze 0.10 dokáže připravit certifikáty pro Ingress, tedy pro něj udělat to, co dělá pro své ovečky uvnitř mesh. Tyto certifikáty pak mohou být způsob, jakým si app2 ověří právoplatnost dotazu - source tedy už nebude jen Service (tzn. síťová informace odkud to přiteklo), ale i (případně "nebo") klientský certifikát.

Nejdřív tedy změním konfiguraci OSM tak, aby připravila certifikát pro Ingress a dala ho do namespace ext. To se udělá změnou CRD meshconfig - nahodím to jako kubectl patch.

```
kubectl patch meshconfig osm-mesh-config -n osm-system --type=merge -p '{
   "spec": {
      "certificate": {
         "ingressGateway": {
            "secret": {
               "name": "osm-nginx-client-cert",
               "namespace": "ext"
            },
            "subjectAltNames": [
               "ingress-nginx.ext.cluster.local"
            ],
            "validityDuration": "24h"
         }
      }
   }
}' 
```

Secret s certifikáty si teď natáhnout do ext podu, takže změním jeho definici takhle:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ext
  namespace: ext
spec:
  selector:
    matchLabels:
      app: ext
  template:
    metadata:
      labels:
        app: ext
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
        volumeMounts:
        - name: certvolume
          mountPath: "/certs"
          readOnly: true
      volumes:
      - name: certvolume
        secret:
          secretName: osm-nginx-client-cert
```

Výborně. Teď smažu původní IngressBackend a udělám nový vyžadující mTLS a ověření certifikátem. Zvolil jsem variantu, kdy zdroj ověřuji jen certifikátem a už ne zdrojovým podem (přes Service) - pro interní Ingress bude lepší použít oboje (já si ale později chtěl i pohrát s variantou mimo cluster jako je Azure Application Gateway).

```yaml
kind: IngressBackend
apiVersion: policy.openservicemesh.io/v1alpha1
metadata:
  name: https
  namespace: default
spec:
  backends:
  - name: app2
    port:
      number: 80
      protocol: https
    tls:
      skipClientCertValidation: false
  sources:
  - kind: AuthenticatedPrincipal
    name: ingress-nginx.ext.cluster.local
```

Naskočím teď do ext Podu, kde mám namapovaný secret s certifikátem. Použiji curl a zkusím se na službu připojit (port 80, ale https) a nebudu ověřovat serverovou stranu - na zkoušku.

```
curl -k -v https://app2.default:80 --cacert /certs/ca.crt --cert /certs/tls.crt --key /certs/tls.key

*   Trying 10.0.138.32...
* TCP_NODELAY set
* Expire in 200 ms for 4 (transfer 0x564d51574fb0)
* Connected to app2.default (10.0.138.32) port 80 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
* successfully set certificate verify locations:
*   CAfile: /certs/ca.crt
  CApath: /etc/ssl/certs
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Request CERT (13):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Certificate (11):
* TLSv1.3 (OUT), TLS handshake, CERT verify (15):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
* ALPN, server did not agree to a protocol
* Server certificate:
*  subject: O=Open Service Mesh; CN=app2.default.cluster.local
*  start date: Oct 14 06:04:11 2021 GMT
*  expire date: Oct 15 06:04:11 2021 GMT
*  issuer: C=US; L=CA; O=Open Service Mesh; CN=osm-ca.openservicemesh.io
*  SSL certificate verify ok.
> GET / HTTP/1.1
> Host: app2.default:80
> User-Agent: curl/7.64.0
> Accept: */*
>
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* old SSL session ID is stale, removing
< HTTP/1.1 200 OK
< server: envoy
< date: Thu, 14 Oct 2021 06:54:40 GMT
< content-type: text/html
< content-length: 615
< last-modified: Tue, 07 Sep 2021 15:21:03 GMT
< etag: "6137835f-267"
< accept-ranges: bytes
< x-envoy-upstream-service-time: 0
<
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
* Connection #0 to host app2.default left intact
```

Bez použití certifikátu mám smůlu, mesh ověřuje, že se prokazuji tím správným.


```
* TLSv1.3 (IN), TLS alert, unknown (628):
* OpenSSL SSL_read: error:1409445C:SSL routines:ssl3_read_bytes:tlsv13 alert certificate required, errno 0
* Closing connection 0
curl: (56) OpenSSL SSL_read: error:1409445C:SSL routines:ssl3_read_bytes:tlsv13 alert certificate required, errno 0
```

## Ingress řešení s HTTPS - například nginx varianta
Všechno jsme si vyzkoušeli s curl, pojďme ho vyměnit za skutečný Ingress. Použít mohu jakoukoli implementaci, která bude šifrovat provoz směrem na backend a prokazovat se certifikátem, který máme v Secret. V dokumentaci je popsaný Contour a NGINX. První zmiňovaný je zajímavý v tom, že je postaven na Envoy (stejně jako Open Service Mesh), což může přinést konzistenci monitoringu, troubleshootingu a bohatosti funkcí. Využívá proprietární definice směrování (vlastní CRD - což můžete brát jako výhodu i nevýhodu) a tak třeba umí dobře vyřešit sdílení různými týmy. NGINX je klasika - velmi často nasazovaný, řízený klasickým Ingress objektem, netřeba se učit nic nového. Vyzkoušel jsem právě s NGINX. Pokud dáte přednost Contour, nabízí OSM, že ho pro vás i nainstaluje jako součást Open Service Mesh.

Nainstaluji NGINX Ingress kontroler.

```
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx -n ext
```

Na definici IngressBackend nepotřebuji nic měnit. Nahodím tedy rovnou Ingress a použiji anotace pro dokonfigurování TLS do backendu. Říkám, že chci do backendu přešifrovat do HTTPS, použít host header souhlasící se službou (přes konfigurační snippet), namířím na secret s certifikátem a zapnu ověřování.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app2
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_ssl_name "app2.default.cluster.local";
    nginx.ingress.kubernetes.io/proxy-ssl-secret: "ext/osm-nginx-client-cert"
    nginx.ingress.kubernetes.io/proxy-ssl-verify: "on"
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app2
            port:
              number: 80
```

Připojím se zvenku a ano - funguje to! Samozřejmě já jsem zvenku dal jen http, takže v praxi bych teď ještě přidal TLS na vstupu Ingressu, ale to už není nic nového.



Zero trust frčí a tam kde to s ním myslí hodně vážně a to i uvnitř Kubernetes clusterů, tam je Open Service Mesh dobrou volbou, jak to vyřešit a nemít s tím zas tak moc práce. Propojení vnějšího světa, ingresu a mesh je dost důležitá součást, tohle musí hrát dohromady. A hraje, zkuste si to. Teď bych ještě moc rád, kdyby se to objevilo out-of-the-box připravené s Ingress kontrolerem pro Application Gateway. Budu to sledovat a až to přijde, dám vědět.