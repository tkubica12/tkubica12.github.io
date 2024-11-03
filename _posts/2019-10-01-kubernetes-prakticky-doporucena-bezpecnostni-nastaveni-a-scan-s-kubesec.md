---
layout: post
title: 'Kubernetes praticky: doporučená bezpečnostní nastavení a scan s kubesec.io'
tags:
- Kubernetes
- Security
---
Kontejnery nejsou typicky izolované na úrovni hypervisoru (ačkoli se v tomto směru objevují třeba kata containers nebo hyper-v containers, které to dělají), takže izolace probíhá na úrovni kernelu. Vaše aplikace v kontejnerech tedy reálně běží v kernelu hostitele. Opatrnost je tedy na místě. Dnes využijeme jednoduchý scanner best practice [kubesec.io](kubesec.io) a vyzkoušíme si provozovat kontejner bezpečněji.

# Výchozí situace aneb bezpečnost moc neřešíme
Mám následující webovou miniaplikaci napsanou v Go:

```go
package main

import (
   "github.com/go-martini/martini"
)

func main() {
  m := martini.Classic()

  m.Get("/", func() string {
    return "This app works!\n"
  })

  m.Run()
}
```

K tomu mám multi-stage Dockerfile, který nejprve provede build aplikace a binárku pak zapouzdří do výsledného kontejneru. Tímto procesem zajišťuji konzistentní build, malou velikost výsledného kontejneru, protože tam nejsou buildovací nástroje. Promiňte mi dnes tag latest (jdeme po bezpečnosti a nechci to komplikovat, ale z provozního hlediska je latest špatný nápad...ale o tom jindy).

```
FROM golang:stretch AS build
RUN apt-get update && apt-get install git -y && go get github.com/go-martini/martini
RUN mkdir /build 
ADD . /build/
WORKDIR /build 
RUN go build -o app .

FROM ubuntu:latest AS final
RUN apt-get update && apt-get install iputils-ping curl -y
COPY --from=build /build/app /app/
WORKDIR /app
CMD ["./app"]
```

Kontejner jsem poslal na Docker Hub pod názvem tkubica/app:root

Pro kubernetes jsem si připravil Service, ať můžeme zkoušet, že aplikace funguje.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: app-service
spec:
  type: LoadBalancer
  selector:
    app: myweb
  ports:
  - protocol: TCP
    port: 80
    targetPort: 12345
```

Definice Podu bude tato a uložím ji do souboru app.sec0.yaml.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: app
  labels:
    app: myweb
spec:
  containers:
    - name: app
      image: tkubica/app:root
      env:
      - name: PORT
        value: "12345"
      ports:
      - containerPort: 12345
```

Nasadím, vyzkouším a funguje. Ale s tím se dnes nespokojíme.

```bash
kubectl apply -f service.yaml
kubectl apply -f app.sec0.yaml

$ curl 40.74.17.88
This app works!
```

# Jak jsme na tom s bezpečností?

Kubesec.io nabízí jednoduchý scanner pro náš yaml předpis a řekne nám, jak jsme na tom z pohledu bezpečnostních best practice. Můžeme použít cloudový endpoint nebo si scaner nasadit jako kontejner či binárku (dá se tedy například začlenit do vaší CI/CD pipeline).

```
$ curl -X POST --data-binary @app.sec0.yaml https://v2.kubesec.io/scan
[
  {
    "object": "Pod/app.default",
    "valid": true,
    "message": "Passed with a score of 0 points",
    "score": 0,
    "scoring": {
      "advise": [
        {
          "selector": "containers[] .resources .requests .cpu",
          "reason": "Enforcing CPU requests aids a fair balancing of resources across the cluster"
        },
        {
          "selector": "containers[] .resources .limits .cpu",
          "reason": "Enforcing CPU limits prevents DOS via resource exhaustion"
        },
        {
          "selector": "containers[] .resources .requests .memory",
          "reason": "Enforcing memory requests aids a fair balancing of resources across the cluster"
        },
        {
          "selector": "containers[] .resources .limits .memory",
          "reason": "Enforcing memory limits prevents DOS via resource exhaustion"
        },
        {
          "selector": ".spec .serviceAccountName",
          "reason": "Service accounts restrict Kubernetes API access and should be configured with least privilege"
        },
        {
          "selector": "containers[] .securityContext .readOnlyRootFilesystem == true",
          "reason": "An immutable root filesystem can prevent malicious binaries being added to PATH and increase attack cost"
        },
        {
          "selector": ".metadata .annotations .\"container.seccomp.security.alpha.kubernetes.io/pod\"",
          "reason": "Seccomp profiles set minimum privilege and secure against unknown threats"
        },
        {
          "selector": "containers[] .securityContext .runAsNonRoot == true",
          "reason": "Force the running image to run as a non-root user to ensure least privilege"
        },
        {
          "selector": ".metadata .annotations .\"container.apparmor.security.beta.kubernetes.io/nginx\"",
          "reason": "Well defined AppArmor policies may provide greater protection from unknown threats. WARNING: NOT PRODUCTION READY"
        },
        {
          "selector": "containers[] .securityContext .runAsUser -gt 10000",
          "reason": "Run as a high-UID user to avoid conflicts with the host's user table"
        },
        {
          "selector": "containers[] .securityContext .capabilities .drop",
          "reason": "Reducing kernel capabilities available to a container limits its attack surface"
        },
        {
          "selector": "containers[] .securityContext .capabilities .drop | index(\"ALL\")",
          "reason": "Drop all capabilities and add only those required to reduce syscall attack surface"
        }
      ]
    }
  }
]
```

Ale, ale. Žádná slává, máme 0 bodů. Pojďme je postupně řešit. 

# Ochrana před DoS

Nejprve vyřeším requesty a limity, protože to nemá vliv na náš Dockerfile ani funkčnost aplikace a je škoda to nemít zapnuté. Je to jednak best practice provozní (ochrana před chybami aplikace a informace pro scheduler pro optimální rozložení zátěže v clusteru), ale i bezpečnostní - limit nás ochrání před potenciálním DoS útokem.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: app
  labels:
    app: myweb
spec:
  containers:
    - name: app
      image: tkubica/app:root
      env:
      - name: PORT
        value: "12345"
      ports:
      - containerPort: 12345
      resources:
        requests:
          cpu: 100m
          memory: 64M
        limits:
          cpu: 500m
          memory: 256M
```

Pošleme do clusteru a aplikace stále funguje.

```bash
kubectl delete pod app
kubectl apply -f app.sec1.yaml
```

Jaké máme score?

```
$ curl -X POST --data-binary @app.sec1.yaml https://v2.kubesec.io/scan
[
  {
    "object": "Pod/app.default",
    "valid": true,
    "message": "Passed with a score of 4 points",
    "score": 4,
    "scoring": {
      "advise": [
        {
          "selector": "containers[] .securityContext .readOnlyRootFilesystem == true",
          "reason": "An immutable root filesystem can prevent malicious binaries being added to PATH and increase attack cost"
        },
        {
          "selector": "containers[] .securityContext .runAsNonRoot == true",
          "reason": "Force the running image to run as a non-root user to ensure least privilege"
        },
        {
          "selector": ".spec .serviceAccountName",
          "reason": "Service accounts restrict Kubernetes API access and should be configured with least privilege"
        },
        {
          "selector": "containers[] .securityContext .runAsUser -gt 10000",
          "reason": "Run as a high-UID user to avoid conflicts with the host's user table"
        },
        {
          "selector": ".metadata .annotations .\"container.seccomp.security.alpha.kubernetes.io/pod\"",
          "reason": "Seccomp profiles set minimum privilege and secure against unknown threats"
        },
        {
          "selector": ".metadata .annotations .\"container.apparmor.security.beta.kubernetes.io/nginx\"",
          "reason": "Well defined AppArmor policies may provide greater protection from unknown threats. WARNING: NOT PRODUCTION READY"
        },
        {
          "selector": "containers[] .securityContext .capabilities .drop",
          "reason": "Reducing kernel capabilities available to a container limits its attack surface"
        },
        {
          "selector": "containers[] .securityContext .capabilities .drop | index(\"ALL\")",
          "reason": "Drop all capabilities and add only those required to reduce syscall attack surface"
        }
      ]
    }
  }
]
```

Lepší, pár bodíků nám přistálo. Pojďme dál. 

# Kontejnery bez root

Jeden z největších problémů, který tu máme je to, že kontejner provozujeme jako root. Ano, namespace nám dává slušnou míru izolace, protože kontejner nemáme puštěný jako privilegovaný (nemůže tedy sahat na hardware, má izolovaný souborový systém, oddělenou síť, takže nemůže odposlouchávat). Nicméně je to odjištěná zbraň - když si dáte ps aux na hostiteli, tak uvidíte, že proces v kontejneru skutečně běží jako root v hostiteli. Jakákoli chyba ať konfigurační nebo kernelu by tak měla fatální následky. Chceme tedy aplikaci neběžet pod rootem. Ideálně ještě zvolme nějaké vysoké UID, abychom nedali číslo, které už v hostiteli je. Pak totiž sice uvnitř kontejneru uvidíme nějaký název uživatele, ale v hostiteli poběží pod názvem, který má UID v hostiteli (a při nějakém "vyskočení" z kontejneru daném nějakou chybou zdědí jeho oprávnění - lepší, než root, ale stále ne co hledáme). K tomu musíme změnit Dockerfile takto:

```
FROM golang:stretch AS build
RUN apt-get update && apt-get install git -y && go get github.com/go-martini/martini
RUN mkdir /build 
ADD . /build/
WORKDIR /build 
RUN go build -o app .

FROM ubuntu:latest AS final
RUN groupadd -r standardgroup && useradd --no-log-init -u 12000 -r -g standardgroup standarduser
RUN apt-get update && apt-get install iputils-ping curl -y
USER standarduser
COPY --chown=standarduser:standardgroup --from=build /build/app /app/
WORKDIR /app
CMD ["./app"]
```

Buildujeme tedy pod rootem (což je často potřeba), ale to nevadí. Ve výsledném kontejneru nejprve vytvoříme uživatele, ještě pod rootem nainstalujeme ping a curl (normálně tam nemají co dělat, je to jen pro naše zkoušení) a pak se přepneme do kontextu uživatele. U nás je to jednoduché - máme jedinou binárku, ale u složitějších řešení typu nginx nebo Java aplikace toho budete muset udělat víc. Výsledný kontejner jsem nahrál na Docker Hub pod názvem tkubica/app:user.

Nicméně tím, že běžíme jako standardní uživatel nemůžeme bindovat síťové porty <1024. To by nám ale nemělo vadit - na portu 80 bude Service, takže běžíme na portu 12345 a nic se neděje.

Ještě uděláme jednu výbornou věc. Filesystem přepneme na read only. Případný útočník si tak nic neuloží a různé rootkity budou dost zmatené, když si nazapíšou ani do /tmp. Pokud v aplikaci potřebujete někam zapisovat, dejte si tento adresář jako Volume, ať může zbytek souborového systému být read only.

YAML teď vypadá takhle:

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: app
  labels:
    app: myweb
spec:
  containers:
    - name: app
      image: tkubica/app:user
      env:
      - name: PORT
        value: "12345"
      ports:
      - containerPort: 12345
      resources:
        requests:
          cpu: 100m
          memory: 64M
        limits:
          cpu: 500m
          memory: 256M
      securityContext:
        readOnlyRootFilesystem: true
        runAsNonRoot: true
        runAsUser: 12000
```

Nasadím přes kubectl apply a aplikace funguje. Proskenujeme si teď předpis v kubesec.

```
$ curl -X POST --data-binary @app.sec2.yaml https://v2.kubesec.io/scan
[
  {
    "object": "Pod/app.default",
    "valid": true,
    "message": "Passed with a score of 7 points",
    "score": 7,
    "scoring": {
      "advise": [
        {
          "selector": ".spec .serviceAccountName",
          "reason": "Service accounts restrict Kubernetes API access and should be configured with least privilege"
        },
        {
          "selector": ".metadata .annotations .\"container.seccomp.security.alpha.kubernetes.io/pod\"",
          "reason": "Seccomp profiles set minimum privilege and secure against unknown threats"
        },
        {
          "selector": ".metadata .annotations .\"container.apparmor.security.beta.kubernetes.io/nginx\"",
          "reason": "Well defined AppArmor policies may provide greater protection from unknown threats. WARNING: NOT PRODUCTION READY"
        },
        {
          "selector": "containers[] .securityContext .capabilities .drop",
          "reason": "Reducing kernel capabilities available to a container limits its attack surface"
        },
        {
          "selector": "containers[] .securityContext .capabilities .drop | index(\"ALL\")",
          "reason": "Drop all capabilities and add only those required to reduce syscall attack surface"
        }
      ]
    }
  }
]
```

No vida. Zlepšujeme se. 

# Linux Capabilities

Zajímají mě teď doporučení ohledně Linux capabilities. Neběžíme přece pod rootem, tak žádné nemáme (mimochodem pokud jako bežný user aplikace opravdu běžet nemůže jsou capabilities způsob jak root opravdu významně omezit i tak). Vypišme si capabilities běžícího kontejneru.

```
$ kubectl exec app grep Cap /proc/1/status
CapInh: 00000000a80425fb
CapPrm: 0000000000000000
CapEff: 0000000000000000
CapBnd: 00000000a80425fb
CapAmb: 0000000000000000
```

Efektivní capabilities jsou samé nuly a to je co chceme. Nicméně Linux historicky potřeboval vyřešit jeden problém. Běžný uživatel občas potřebuje spustit všem známé důvěryhodné aplikace, které potřebují vyšší oprávnění. Jednou takovou je ping, protože ten potřebuje CAP_NET_RAW. To mám kvůli pingu být nucen být root? Pro pohodlí se tyto důvěryhodné aplikace dají ve file systému ozačit setuid bitem. To způsobí, že mohou mít více oprávnění, než uživatel, který je spouští. Zkusme si, že ping, který tento bit má nastaven, opravdu funguje.

```
$ kubectl exec app ping 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.046 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.029 ms
```

Představme si teď ale, že nám někdo podstrčí image, kde je nějaká jiná "aplikace" s nastaveným setuid. Kontejner hezky jedeme bez roota, ale pokud útočník umí spustit aplikace s setuid bitem, tak ta dostane vyšší oprávnění. Pojďme tedy jakékoli možnosti eskalace zakázat a nechat všechno běžet s nulovými capabilities.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: app
  labels:
    app: myweb
spec:
  containers:
    - name: app
      image: tkubica/app:user
      env:
      - name: PORT
        value: "12345"
      ports:
      - containerPort: 12345
      resources:
        requests:
          cpu: 100m
          memory: 64M
        limits:
          cpu: 500m
          memory: 256M
      securityContext:
        readOnlyRootFilesystem: true
        runAsNonRoot: true
        runAsUser: 12000
        capabilities:
          drop:
            - all
```

Kubesec je spokojenější.

```
$ curl -X POST --data-binary @app.sec3.yaml https://v2.kubesec.io/scan
[
  {
    "object": "Pod/app.default",
    "valid": true,
    "message": "Passed with a score of 9 points",
    "score": 9,
    "scoring": {
      "advise": [
        {
          "selector": ".spec .serviceAccountName",
          "reason": "Service accounts restrict Kubernetes API access and should be configured with least privilege"
        },
        {
          "selector": ".metadata .annotations .\"container.seccomp.security.alpha.kubernetes.io/pod\"",
          "reason": "Seccomp profiles set minimum privilege and secure against unknown threats"
        },
        {
          "selector": ".metadata .annotations .\"container.apparmor.security.beta.kubernetes.io/nginx\"",
          "reason": "Well defined AppArmor policies may provide greater protection from unknown threats. WARNING: NOT PRODUCTION READY"
        }
      ]
    }
  }
]
```

Pošleme tam Pod a ověříme si, že ani ping už nefunguje.

```bash
$ kubectl delete pod app
pod "app" deleted

$ kubectl apply -f app.sec3.yaml
pod/app created

$ kubectl exec app ping 127.0.0.1
ping: socket: Operation not permitted
```

# Service Account
Zbývají nám tři doporučení. Seccomp a apparmor jsou alfa vlastnosti, které nedáme. Ale je tu zmínka o Service Accountu a to si pojďme rozebrat.

Věc se má tak, že Kubernetes občas potřebuje, aby Pody mohly mluvit na Kubernetes API. Je logické, že když nasadíte nějakou komponentu typu Ingress kontroler, Service Catalog, Service Mesh nebo Flex Volume tak potřebují ovládat Kubernetes. Výchozí stav je takový, že Kubernetes vytvoří token pro uživatele s názvem "default" a ten vám namapuje do kontejneru jako Secret v souboru. A na to si dejme pozor.

Účet default nemá ve výchozím stavu clusteru žádná práva. Co když ale nějakým trikem přiměju administrátora, aby na účet default dal třeba binding na cluster admin roli? Nějaký hezký článeček nebo ještě lépe definice schovaná v Helm chartu pro nějakou úžasnou aplikaci, kdy administrátor nasadí a nekouká co je uvnitř. Pojďme to teď schválně udělat - účtu default přiřadíme cluster admin práva.

```yaml
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: defaultaccount-clusterrolebinding
subjects:
- kind: ServiceAccount
  name: default
  namespace: default
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: ""
```

Pošlete do clusteru přes kubectl apply. Pojďme teď skočit do našeho Podu. V souborovém systému najdeme token pro účet default a s ním můžeme začít mluvit k Kubernetes API serveru.

```
$ kubectl apply -f clusterRoleForDefaultAccount.yaml
clusterrolebinding.rbac.authorization.k8s.io/defaultaccount-clusterrolebinding configured

$ kubectl exec -ti app /bin/bash
standarduser@app:/app$ export header="Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)"
standarduser@app:/app$ curl -k -H "$header" https://aks-33zzj5uvr5jfa-736f4ae8.hcp.westeurope.azmk8s.io:443/api/v1/namespaces/default/pods
{
  "kind": "PodList",
  "apiVersion": "v1",
  "metadata": {
    "selfLink": "/api/v1/namespaces/default/pods",
    "resourceVersion": "170509"
  },
  "items": [
    {
      "metadata": {
        "name": "app",
        "namespace": "default",
        "selfLink": "/api/v1/namespaces/default/pods/app",
        "uid": "a9bfab57-a610-4ab3-b1c7-c31711f2cff7",
        "resourceVersion": "170164",
        "creationTimestamp": "2019-09-30T18:27:44Z",
        "labels": {
          "app": "myweb"
        },
        "annotations": {
          "kubectl.kubernetes.io/last-applied-configuration": "{\"apiVersion\":\"v1\",\"kind\":\"Pod\",\"metadata\":{\"annotations\":{},\"labels\":{\"app\":\"myweb\"},\"name\":\"app\",\"namespace\":\"default\"},\"spec\":{\"containers\":[{\"env\":[{\"name\":\"PORT\",\"value\":\"12345\"}],\"image\":\"tkubica/app:user\",\"imagePullPolicy\":\"Always\",\"name\":\"app\",\"ports\":[{\"containerPort\":12345}],\"resources\":{\"limits\":{\"cpu\":\"500m\",\"memory\":\"256M\"},\"requests\":{\"cpu\":\"100m\",\"memory\":\"64M\"}},\"securityContext\":{\"capabilities\":{\"drop\":[\"all\"]},\"readOnlyRootFilesystem\":true,\"runAsNonRoot\":true,\"runAsUser\":12000}}]}}\n"
        }
      },
      "spec": {
  ...
  ```

Oulala. Pokud se útočník nějak zmocní Podu, má teď přístup do control plane (nebo právoplatný uživatel, který má RBAC jen na neprodukční namespace takto získal přístup bez těchto limitů)... ono vypsat si seznam Podů je jen takové zlobení, ale změnit hodnoty všech Secrets a dát do nich útočníkova hesla a klíče je hodně zlé. Jasně - je to možné jen, když účtu default dáme nevhodný RBAC, ale proč takové riziko podstupovat.

Vyřešme to tak, že vytvoříme service account s názvem noaccess, vypneme na něm automatické mountování tokenu a explicitně ho přiřadíme Podu.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: noaccess
  namespace: default
automountServiceAccountToken: false
```

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: app
  labels:
    app: myweb
spec:
  serviceAccountName: noaccess
  containers:
    - name: app
      image: tkubica/app:user
      env:
      - name: PORT
        value: "12345"
      ports:
      - containerPort: 12345
      resources:
        requests:
          cpu: 100m
          memory: 64M
        limits:
          cpu: 500m
          memory: 256M
      securityContext:
        readOnlyRootFilesystem: true
        runAsNonRoot: true
        runAsUser: 12000
        capabilities:
          drop:
            - all
```

Můžete si vyzkoušet, že teď už v Podu žádný token k nalezení není. A ještě navíc uvádíme explicitně účet (v našem případě noaccess), takže je to předvídatelné a přehledné. Jak vypadá naše score?

```
$ curl -X POST --data-binary @app.sec4.yaml https://v2.kubesec.io/scan
[
  {
    "object": "Pod/app.default",
    "valid": true,
    "message": "Passed with a score of 12 points",
    "score": 12,
    "scoring": {
      "advise": [
        {
          "selector": ".metadata .annotations .\"container.seccomp.security.alpha.kubernetes.io/pod\"",
          "reason": "Seccomp profiles set minimum privilege and secure against unknown threats"
        },
        {
          "selector": ".metadata .annotations .\"container.apparmor.security.beta.kubernetes.io/nginx\"",
          "reason": "Well defined AppArmor policies may provide greater protection from unknown threats. WARNING: NOT PRODUCTION READY"
        }
      ]
    }
  }
]
```

To není zlé. Tím pro dnešek končíme a snad se nám podařilo bezpečnost významně zlepšit. Jasně - u složitějších Java aplikací s tím bude trochu víc práce, ale vyplatí se. Sami pak zjistíte jak řada populárních image na Docker Hub tyto koncepty nedodržuje (třeba oblíbený nginx ... ale třeba jeho verze od Bitnami to dělá správně).

Na příště chci u bezpečnosti ještě chvíli zůstat a podívat se na kontejnerové obrazy a práci s nimi. A také se určitě k dostaneme k vynucení těchto pravidel přes Azure Policy.