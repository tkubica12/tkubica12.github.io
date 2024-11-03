---
layout: post
title: 'Kubernetes praticky: vystavování aplikací s Ingress a Azure App Gateway (WAF)'
tags:
- Kubernetes
- Networking
- Security
---
Na tomto blogu už jsem ukazoval vystavování aplikací přes objekt Service a s využitím typu LoadBalancer vám Kubernetes ve spolupráci s Azure Load Balancer zajistí vystrčení ven z clusteru na private nebo public IP adresu. Nicméně to má své nevýhody. Adres může být zbytečně moc, neřeší to L7 funkce jako je TLS terminace, URL routing, session perzistence podle cookie a tak podobně. Pro tyto případy je k dispozici Ingress objekt a na tomto blogu si vyzkoušíme dvě implementace. NGINX nasazený uvnitř clusteru (univerzální řešení pro clustery běžící kdekoli) a také enterprise-grade nasazení přes Azure Application Gateway včetně Web Application Firewall.

# Ingress vs. Service
Kdy použít Ingress? Kdy Service? A kdy něco jiného, třeba API Management? A kdy používat reverse proxy ručně? A dá se to kombinovat?

## Varianta pouze Service
První možnost už známe - vystavení přes Service. Nevýhodou je, že jde o L4 řešení, takže nezískáme pokročilé funkce typu WAF, TLS terminaci nebo URL routing. Každou službu také musíme vystavit buď na jiném portu (a nestandardní porty jsou otrava, protože pak musíte řešit discovery na kterém portu vám API běží třeba přes SRV record v DNS) nebo na různých IP adresách (a mít pak hromadu mikroslužeb každou na jiné IP také není nejpohodlnější a čaká nás hodně DNS a CORS managementu).

Nicméně jsou situace, kdy je Service ideální. Například pokud nepoužíváte HTTP-based interface, ale nějaký binární TCP protokol jako jsou AMQP nebo MQTT nebo dokonce potřebujete UDP (real time systémy, media streaming nebo hry). Tím, že v cestě není reverse proxy také přináší Service nižší latence - zásadní pro real time aplikace.

## Varianta pouze Ingress
U klasického HTTP-based světa REST API může dávat smysl všechno řešit přes Ingress. Nad jednou public IP tak můžete provozovat hned několik služeb a směrovat na ně přes hostname nebo URL routing. Můžete narazit na to, že v enterprise prostředí nebude chuť spoléhat se na implementaci uvnitř clusteru, protože do toho bezpečnost pořádně neuvidí. Řešením může být právě implementace s Azure Application Gateway, která nabízí i WAF a enterprise přístup.

## Kombinace Service a ruční reverse proxy
Občas se ale stane, že bezpečnostní oddělení v enterprise firmě nedovolí dávat certifikáty do automatizovaného systému (většinou spíše ze strachu a neznalosti, ale může jít i o vnitřní předpisy apod.). V takovém případě můžete vystavovat služby přes objekt Service (na různých privátních IP nebo různých portech) a před tím mít reverse proxy v ruční správě bezpečnostního týmu - Azure App Gw, F5 a tak podobně. Není to nejagilnější řešení, ale někdy je pro úspěch projektu důležitější nejít proti zdi a napojit se na standardní procesy ve firmě (a případně je změnit později, až bude vaše aplikace tak důležitá pro byznys, že budete mít lepší vyjednávací pozici). Někdy se také kombinuje Ingress s ruční konfigurací na F5. To znamená dvě reverse proxy v řadě, což není ideální pro latenci, ale může to změnšit četnost změn potřebných v ručním systému a přispět k větší agilitě.

## Kombinace s Azure API Management
Reverse proxy typicky neřeší všechny aspekty potřebné pro mikroslužby, například transformaci volání, řízení přístupů z externího světa nebo dokumentaci API. Pro takové případy je vhodné použít Azure API Management. Způsobů jak ho do prostředí zapojit je hodně. Například Service -> API Management -> F5, Ingress -> API Management -> F5, Ingress -> API Management -> Internet apod.

# Azure Application Gateway (WAF)
Soustředit se budeme na v2 služby, která přinesla větší propustnost, rychlejší provádění změn konfigurace, bohatší možnosti machinace s provozem (přepisy hlaviček) a automatické škálování výkonu. K dispozici je jednak základní verze, ale hodně zajímavá je varianta s WAF funkcemi pro ochranu před útoky (OWASP pravidla). Jde o platformní službu, takže o redundanci a patchování se nemusíte starat, což je naprosto zásadní přidaná hodnota.

# Příprava App Gw implementace
Nasazení má několik kroků, ale řadu z nich lze automatizovat ARM šablonou a některé použité technologie už jsem na tomto blogu rozebíral.

1. Použijte AKS v režimu Advanced Networking (Azure CNI). To způsobí, že Pody dostávají IP adresy přímo z VNETu a App Gw tak na ně může balancovat provoz napřímo bez dalšího balancingu uvnitř clusteru (to přináší jednak nižší latenci, ale také dovoluje naplno využít některé funkce App Gw jako je session cookie perzistence).
2. Ve VNETu vytvořte subnet pro App Gw.
3. Nainstalujte Helm.
4. Vytvořte statickou public IP a nasaďte App Gw v2 (doporučuji WAF variantu pro ochranu aplikace před zranitelnostmi). Pro pokusy si necháme k IP udělat i DNS záznam.
5. Kubernetes potřebuje App Gw automatizovaně ovládat. Vytvořte proto user managed identitu a nasaďte AAD Pod Identity.
6. Managed identitě dejte Contributor práva do App Gw a Reader práva do resource group

Příprava je hotová a můžeme nasadit ingress kontroler pro App Gw. V parametrech mu předáváme pod jakým účtem má volat Azure a také ho necháme reagovat na Ingress ve všech namespace (můžete také mít víc instancí v různých namespaces).

```bash
helm repo add application-gateway-kubernetes-ingress https://appgwingress.blob.core.windows.net/ingress-azure-helm-package/
helm repo update
helm install application-gateway-kubernetes-ingress/ingress-azure \
  --set appgw.subscriptionId=$(az account show --query id -o tsv) \
  --set appgw.resourceGroup=aks \
  --set appgw.name=appgw \
  --set kubernetes.watchNamespace="" \
  --set armAuth.type=aadPodIdentity \
  --set armAuth.identityResourceID=$(az identity show -n tomasManagedIdentity -g aks --query id -o tsv)  \
  --set armAuth.identityClientID=$(az identity show -n tomasManagedIdentity -g aks --query clientId -o tsv) \
  --set rbac.enabled=true
```

# Nasazení aplikace
Nejprve nasadíme aplikaci samotnou.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myweb-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myweb
  template:
    metadata:
      labels:
        app: myweb
    spec:
      containers:
      - name: myweb
        image: tkubica/web:1
        env:
        - name: PORT
          value: "80"
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 64M
          limits:
            cpu: 500m
            memory: 256M
```

Následně přidáme Service, ale typu ClusterIP (tedy bez vnější reprezentace). To děláme jednak pro zajištění směrování na službu v rámci clusteru a také na automatické udržování seznamu endpointů (IP adres Podů), které si bude kontroler vyčítat.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: myweb-service
spec:
  selector:
    app: myweb
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

Teď už můžeme nasadit Ingress. Všimněte si, že jde o Kubernetes objekt. Je to tedy univerzální předpis, který funguje s libovolnou implementací (App Gw, NGINX, Traefik, ...), jakýsi nejmenší společný jmenovatel. Implementačně závislé nadstavby lze řešit anotací, což v tuto chvíli nepoužijeme. Nicméně je tam jedna důležitá anotace, která říká, že chceme Ingress z provoznit na implementaci App Gw. V clusteru totiž můžete mít implementací víc (třeba App Gw a NGINX) a touto anotací rozhodujete, jakou chcete pro tento Ingress použít.

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
  name: myweb-appgw
spec:
  rules:
    - host: mujkube123.westeurope.cloudapp.azure.com
      http:
        paths:
          - path: /
            backend:
              serviceName: myweb-service
              servicePort: 80
```

Všimněte si, že jsem zadal host s DNS své public IP neprovádím žádný URL routing. Nicméně můžete například na stejném hostiteli poslat URL / na jednu lužbu a /images na jinou. Můžeme také na stejné IP kombinovat několik hostů (FQDN) s tím, že reverse proxy se bude rozhodovat podle host headeru.

Můžete si prohlédnout, co kontroler nastavil ve vaší Application Gateway. Aktuálně mě zajímá jak vypadá backend pool.

![](/images/2019/2019-07-30-07-58-59.png){:class="img-fluid"}

Jde přímo o IP adresy Podů. Díky Advanced Networking v AKS může App Gw balancovat provoz rovnou na Pody, protože ty mají reálné adresy z VNETu.

```
$ kubectl get pods -o wide
NAME                                              READY   STATUS    RESTARTS   AGE    IP              NODE                                NOMINATED NODE   READINESS GATES
myweb-deployment-7cd8bbd97c-6xlbm                 1/1     Running   0          89m    192.168.0.66    aks-nodepool1-32669429-vmss000000   <none>           <none>
myweb-deployment-7cd8bbd97c-nmvn5                 1/1     Running   0          89m    192.168.0.127   aks-nodepool2-32669429-vmss000000   <none>           <none>
myweb-deployment-7cd8bbd97c-txb4j                 1/1     Running   0          89m    192.168.0.22    aks-nodepool1-32669429-vmss000000   <none>           <none>
```

# Certifikáty a HTTPS
Jednou z klíčových vlastností reverse proxy je terminace TLS. Certifikáty nechceme cpát přímo do aplikací. Ingress tohle umí. TLS certifikát se uloží do Kubernetes Secret a kontroler ho odtamtud vezme a dopraví do App Gw a k tomu samozřejmě nastaví potřebná pravidla. Velmi zajímavá je kombinace s projekte cert-manager, který vám umí zajistit automatické vystavování a obnovování certifikátů třeba u Let's encrypt.

Nejprve si namíříme DNS A záznam na mojí Application Gateway v doméně, kterou vlastním a spravuji v Azure DNS.

```bash
export appgwip=$(az network public-ip show -n appgw-ip -g aks --query ipAddress -o tsv)
az network dns record-set a add-record -a $appgwip -n appgw -g shared-services -z azure.tomaskubica.cz
az network dns record-set a add-record -a $appgwip -n "*.appgw" -g shared-services -z azure.tomaskubica.cz
```

Následně si rozhodíme cert-manager.

```bash
kubectl apply -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.8/deploy/manifests/00-crds.yaml

kubectl create namespace cert-manager
kubectl label namespace cert-manager certmanager.k8s.io/disable-validation=true
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install \
  --name cert-manager \
  --namespace cert-manager \
  --version v0.8.0 \
  jetstack/cert-manager
```

Cert-manager podporuje různé implementace jako je ACME protokol (to používá právě Let's encrypt), Venafi, Hashicorp Vault, self-signed nebo vlastní "miniautoritu". My použijeme ACME. Do clusteru pošleme následující objekt.

```yaml
apiVersion: certmanager.k8s.io/v1alpha1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: mujemail@neco.cz
    privateKeySecretRef:
      name: letsencrypt-prod
    http01: {}
```

Takhle bude vypadat náš Ingress.

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    certmanager.k8s.io/cluster-issuer: letsencrypt-prod
  name: myweb-appgw
spec:
  rules:
    - host: appgw.azure.tomaskubica.cz
      http:
        paths:
          - path: /
            backend:
              serviceName: myweb-service
              servicePort: 80
  tls:
    - hosts:
      - appgw.azure.tomaskubica.cz
      secretName: tls-secret
```

Anotací jsme upozornili cert-manager, že má pro nás vyjednat certifikát. Ten ho uloží do secret tls-secret, kde si ho Ingress vyzvedne a kontroler zajistí jeho nahození do Application Gateway.

Podívejme se na konfiguraci, která na Application Gateway vznikla.

Takhle vypadá Listener.

![](/images/2019/2019-07-30-08-11-38.png){:class="img-fluid"}

Takhle Health Probe (backend máme na portu 80).

![](/images/2019/2019-07-30-08-12-28.png){:class="img-fluid"}

Tady je vygenerované pravidlo.

![](/images/2019/2019-07-30-08-12-54.png){:class="img-fluid"}

App Gw podporuje automatické škálování, takže počet jejích jednotek si můžete nechat měnit dynamicky podle zátěže. Také můžete zapnout podporu HTTP/2, což může zajímavě zrychlit vaše aplikace zejména u složitějších webů.

![](/images/2019/2019-07-30-08-14-20.png){:class="img-fluid"}


Ingress je velmi užitečný objekt v Kubernetes a dnes jsme si ukázali jeho implementaci s Azure Application Gateway. To přináší platformní vlastnosti, takže o dostupnost, škálování a patching bezpečnostního prvku se nemusím starat, mohu z toho brát logy a analyzovat bezpečnost v Azure Security Center a následně v Azure Sentinel (SIEM) a zapnout WAF pro větší ochranu mých aplikací. Pokud potřebujete mít jednotnou implementaci pro clustery v Azure, Azure Stack i v jiných prostředích, můžete reverse proxy nasadit přímo uvnitř clusteru s NGINX implementací (ale pak se o ni i starat). Na to se podíváme příště.
