---
layout: post
status: publish
published: true
title: 'Kubernetes prakticky: finty pro ovládaní aneb kdy CLI a kdy GUI a jaké'
tags:
- Kubernetes
---
Ovládání Kubernetes je velmi milé a přirozené a osobně toho hodně dělám přímo z příkazové řádky s použitíme kubectl. Podívejme se dnes na pár fintiček, které mám rád. A co GUI? Kubernetes nabízí svůj dashboard, ale AKS cluster má krásnou monitorovací záložku a je tu také plug-in do Visual Studio Code. Kdy co použít a co bych preferoval já?

# Kouzla s kubectl
Příkazová "rádka" Kubernetes je opravdu velmi mocná a nabízí mnoho zajímavostí pro troubleshooting a monitoring. Pojďme si ukázat pár mých oblíbených.

## Kontexty
Kubectl používá konfigurační soubor defaultně uložený v ~/.kube/config a v něm jsou informace o clusterech a kontextech. Můžete v něm sdružovat přístupové informace hned k několika clusterům. Po instalaci AKS jej můžete naplnit příkazem az aks get-credantials -n jmenoaks -g resourcegroup, což vám stáhne potřebné klíče a založí přístup pro AAD login, ve kterém jste přihlášeni (protože AKS má defaultně zapnoutou integraci RBAC s Azure Active Directory). Můžete také použít přepínač --admin a to vám stáhne administrátorský univerzální login (s tím opatrně, používejte raději AAD). Zajímavým konceptem jsou právě kontexty, tedy schopnost přepnout se na jiný cluster, jiného uživatele nebo jiný namespace.

Podívejme se jaké mám kontexty já.

```bash
$ kubectl config get-contexts
CURRENT   NAME               CLUSTER      AUTHINFO                           NAMESPACE
          akscluster         akscluster   clusterUser_aksgroup_akscluster
*         akscluster-admin   akscluster   clusterAdmin_aksgroup_akscluster
```

Mám tedy AAD login a admin login. Pracuji v default namespace a jako admin mám právo přistupovat i do jiných namespaců, ale musím to vždy explicitně říct.

Tak například v namespace default nemám nic a chci pracovat s Pody v namespace tomas. Abych to mohl udělat (práva na to mám) musím ale vždy používat přepínač definující namespace, když chci mimo defaultní.

```bash
$ kubectl get pods
No resources found.
$ kubectl get pods -n tomas
NAME      READY     STATUS    RESTARTS   AGE
mujpod    1/1       Running   0          49s
```
To je ale někdy otrava. Často zapomenu přepínač napsat a jsem jinde, než potřebuji. Pojďme tedy vytvořit kontext, který mě namíří rovnou do namespace tomas. Následně se do kontextu přepnu a nemusím dokola zadávat, že chci pracovat se zdroji v namespace tomas.

```bash
$ kubectl config set-context tomas --cluster akscluster --user clusterAdmin_aksgroup_akscluster --namespace tomas
Context "tomas" created.
$ kubectl config get-contexts
CURRENT   NAME               CLUSTER      AUTHINFO                           NAMESPACE
          akscluster         akscluster   clusterUser_aksgroup_akscluster
*         akscluster-admin   akscluster   clusterAdmin_aksgroup_akscluster
          tomas              akscluster   clusterAdmin_aksgroup_akscluster   tomas
$ kubectl config use-context tomas
Switched to context "tomas".
$ kubectl get pods
NAME      READY     STATUS    RESTARTS   AGE
mujpod    1/1       Running   0          3m
```

## Streaming
Často potřebuji sledovat co se děje, třeba jak se přidávají nebo odebírají Pody. Mohl bych dokola opakovat příkaz kubectl get pods (třeba watchem), ale to se mi moc nelíbí. Kubectl má možnost streamovat změny na obrazovku. Nevýhodou je, že se při tom rozpadne formátování, takže je to méně přehledné, nicméně vidím v reálném čase jaké změny se dějí. Na to je výborný přepínač -w

```bash
$ kubectl get pods -w
NAME                            READY     STATUS              RESTARTS   AGE
mujdeployment-896f9ffbc-5czr4   0/1       ContainerCreating   0          1s
mujdeployment-896f9ffbc-5ht46   0/1       ContainerCreating   0          1s
mujdeployment-896f9ffbc-bbz7z   0/1       ContainerCreating   0          1s
mujdeployment-896f9ffbc-fdb5q   0/1       ContainerCreating   0          2s
mujdeployment-896f9ffbc-whkwb   0/1       ContainerCreating   0          1s
mujpod                          1/1       Running             0          7m
mujdeployment-896f9ffbc-5ht46   1/1       Running   0         6s
mujdeployment-896f9ffbc-fdb5q   1/1       Running   0         7s
mujdeployment-896f9ffbc-whkwb   1/1       Running   0         23s
mujdeployment-896f9ffbc-5czr4   1/1       Running   0         23s
mujdeployment-896f9ffbc-bbz7z   1/1       Running   0         25s
```

## Wide
Nezapomínejte, že existuje přepínač -o wide, který přidá víc informací. Například u výpisu Podů vám ukáže, na kterém nodu běží.

```bash
$ kubectl get pods -o wide
NAME                            READY     STATUS    RESTARTS   AGE       IP              NODE
mujdeployment-896f9ffbc-5czr4   1/1       Running   0          1m        192.168.0.242   aks-nodepool1-38238592-2
mujdeployment-896f9ffbc-5ht46   1/1       Running   0          1m        192.168.0.160   aks-nodepool1-38238592-1
mujdeployment-896f9ffbc-bbz7z   1/1       Running   0          1m        192.168.0.233   aks-nodepool1-38238592-2
mujdeployment-896f9ffbc-fdb5q   1/1       Running   0          1m        192.168.0.240   aks-nodepool1-38238592-2
mujdeployment-896f9ffbc-whkwb   1/1       Running   0          1m        192.168.0.147   aks-nodepool1-38238592-1
mujpod                          1/1       Running   0          8m        192.168.0.117   aks-nodepool1-38238592-1
```

## Labely
Jak už určitě víte objektům lze dávat labely a můžeme si je zobrazit na výpisu.

```bash
$ kubectl get pods --show-labels
NAME                            READY     STATUS    RESTARTS   AGE       LABELS
dalsipod                        1/1       Running   0          38s       app=tomas
mujdeployment-896f9ffbc-5czr4   1/1       Running   0          3m        pod-template-hash=452959967,run=mujdeployment
mujdeployment-896f9ffbc-5ht46   1/1       Running   0          3m        pod-template-hash=452959967,run=mujdeployment
mujdeployment-896f9ffbc-bbz7z   1/1       Running   0          3m        pod-template-hash=452959967,run=mujdeployment
mujdeployment-896f9ffbc-fdb5q   1/1       Running   0          3m        pod-template-hash=452959967,run=mujdeployment
mujdeployment-896f9ffbc-whkwb   1/1       Running   0          3m        pod-template-hash=452959967,run=mujdeployment
mujpod                          1/1       Running   0          11m       run=mujpod
```

Konkrétní label (jeho key) můžeme také vypsat jako samostatný sloupeček.

```bash
$ kubectl get pods -L run
NAME                            READY     STATUS    RESTARTS   AGE       RUN
dalsipod                        1/1       Running   0          1m
mujdeployment-896f9ffbc-5czr4   1/1       Running   0          4m        mujdeployment
mujdeployment-896f9ffbc-5ht46   1/1       Running   0          4m        mujdeployment
mujdeployment-896f9ffbc-bbz7z   1/1       Running   0          4m        mujdeployment
mujdeployment-896f9ffbc-fdb5q   1/1       Running   0          4m        mujdeployment
mujdeployment-896f9ffbc-whkwb   1/1       Running   0          4m        mujdeployment
mujpod                          1/1       Running   0          11m       mujpod
```

Podle labelů se dá také vhodně filtrovat. Takhle třeba vypíšeme pouze Pody obsahující label run.

```bash
$ kubectl get pods -l run
NAME                            READY     STATUS    RESTARTS   AGE
mujdeployment-896f9ffbc-5czr4   1/1       Running   0          5m
mujdeployment-896f9ffbc-5ht46   1/1       Running   0          5m
mujdeployment-896f9ffbc-bbz7z   1/1       Running   0          5m
mujdeployment-896f9ffbc-fdb5q   1/1       Running   0          5m
mujdeployment-896f9ffbc-whkwb   1/1       Running   0          5m
mujpod                          1/1       Running   0          12m
```

Nebo Pody obsahující label run s hodnotou mujpod.

```bash
$ kubectl get pods -l run=mujpod
NAME      READY     STATUS    RESTARTS   AGE
mujpod    1/1       Running   0          12m
```

## Describe
Pokud chcete zjistit co se s kontejnerem děje, jak je nastaven a jaké události se ho týkají, použijte describe.

```bash
$ kubectl describe pod web-577694c698-5d6zh
Name:               web-577694c698-5d6zh
Namespace:          tomas
Priority:           0
PriorityClassName:  <none>
Node:               aks-nodepool1-38238592-1/192.168.0.105
Start Time:         Fri, 17 Aug 2018 08:38:36 +0200
Labels:             pod-template-hash=1332507254
                    run=web
Annotations:        <none>
Status:             Running
IP:                 192.168.0.177
Controlled By:      ReplicaSet/web-577694c698
Containers:
  web:
    Container ID:   docker://a28dc998bbd3de3f9b57c601478ec80c81a922db4672d47cdfbfbed7a2b7b763
    Image:          nginx:alpine
    Image ID:       docker-pullable://nginx@sha256:23e4dacbc60479fa7f23b3b8e18aad41bd8445706d0538b25ba1d575a6e2410b
    Port:           80/TCP
    Host Port:      0/TCP
    State:          Running
      Started:      Fri, 17 Aug 2018 08:38:42 +0200
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-wnj67 (ro)
Conditions:
  Type              Status
  Initialized       True
  Ready             True
  ContainersReady   True
  PodScheduled      True
Volumes:
  default-token-wnj67:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-wnj67
    Optional:    false
QoS Class:       BestEffort
Node-Selectors:  <none>
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
                 node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type    Reason     Age   From                               Message
  ----    ------     ----  ----                               -------
  Normal  Scheduled  49s   default-scheduler                  Successfully assigned tomas/web-577694c698-5d6zh to aks-nodepool1-38238592-1
  Normal  Pulled     44s   kubelet, aks-nodepool1-38238592-1  Container image "nginx:alpine" already present on machine
  Normal  Created    43s   kubelet, aks-nodepool1-38238592-1  Created container
  Normal  Started    43s   kubelet, aks-nodepool1-38238592-1  Started container
```

## Port-forwarding
Výborná věc je schopnost vytvořit síťový šifrovaný tunel mezi vašim počítačem a Podem nebo Service. Díky tomu můžete snadno ověřit co váš web server vlastně píše aniž by bylo nutné to dělat z jiného Podu nebo vystrčit službu ven. Lokálně přes 127.0.0.1 a přidělený port můžete s Pod nebo Service komunikovat.

```bash
$ kubectl get service,pod
NAME          TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/web   ClusterIP   192.168.6.236   <none>        80/TCP    2m

NAME                       READY     STATUS    RESTARTS   AGE
pod/web-577694c698-5d6zh   1/1       Running   0          2m
pod/web-577694c698-pvlrd   1/1       Running   0          2m
pod/web-577694c698-rhnns   1/1       Running   0          2m
$ kubectl port-forward pod/web-577694c698-5d6zh :80
Forwarding from 127.0.0.1:3902 -> 80
Forwarding from [::1]:3902 -> 80
Handling connection for 3902
Handling connection for 3902
^C$ kubectl port-forward service/web :80
Forwarding from 127.0.0.1:3914 -> 80
Forwarding from [::1]:3914 -> 80
```

## Edit
Někdy potřebuji rychle změnit nějaký parametr. Za normálních okolností bych byl zásadně pro úpravu YAML souboru, commit nové verze ve version control systému jako je GitHub nebo VSTS a pak ho do Kubernetes poslal. Ale pro vývoj či testování chce člověk občas něco rychlejšího. Kubectl edit otevře aktuální desired state objektu v editoru, vy uděláte změnu, vyskočíte a on ji aplikuje.

```bash
$ export EDITOR=nano
$ kubectl edit pod/web-577694c698-5d6zh
```

## Imperativní příkazy
Zásadně doporučuji používat deklarativní model konfigurace, tedy všechny objekty dávat do YAML souborů a ty posílat do Kubernetes příkazem kubectl apply -f. Někdy ale potřebujete velmi rychle něco spustit jen tak na zkoušení a na to jsou dobré imperativní příkazy. Navíc pokud se chystáte na zkoušku CKA, tak tam nebudete mít možnost kopírovat rozsáhlé YAML soubory do prostředí. Vypisovat je ručně je fakt na dlouho a času není nekonečně, takže na CKA zkoušku je velmi dobré znát i imperativní příkazy.

Takhle se například spustí jednoduchý Pod. Musíte dát --restart Never (tedy říkáte, že váš Pod nevyžaduje žádnou další péči typu, že by ho někdo restartoval nebo přesouval když umře Node).

```bash
$ kubectl run mujpod --restart Never --image nginx:alpine
pod "mujpod" created
$ kubectl get pod
NAME      READY     STATUS              RESTARTS   AGE
mujpod    0/1       ContainerCreating   0          4s
```

Přes kubectl run můžeme také vytvořit Deployment ve výchozím stavu s jednou replikou, ale můžeme specifikovat víc.

```bash
$ kubectl run mojepody --image nginx:alpine --replicas 3
deployment.apps "mojepody" created
$ kubectl get pods
NAME                        READY     STATUS              RESTARTS   AGE
mojepody-845bc575df-6jsln   0/1       ContainerCreating   0          5s
mojepody-845bc575df-9qbpf   0/1       ContainerCreating   0          5s
mojepody-845bc575df-g2l8r   0/1       ContainerCreating   0          5s
mujpod                      1/1       Running             0          1m
```

Přímo s kubectl run můžeme také definovat port, který má být v Podu otevřený. A nejen to. Pokud použijeme navíc přepínač expose, kubectl nám rovnou vytvoří Service.

```bash
$ kubectl run web1 --image nginx:alpine --port 80 --expose
service "web1" created
deployment.apps "web1" created

$ kubectl get pod,service
NAME                            READY     STATUS    RESTARTS   AGE
pod/mojepody-845bc575df-6jsln   1/1       Running   0          3m
pod/mojepody-845bc575df-9qbpf   1/1       Running   0          3m
pod/mojepody-845bc575df-g2l8r   1/1       Running   0          3m
pod/mujpod                      1/1       Running   0          5m
pod/web1-7dfd7b9658-mrkzl       1/1       Running   0          9s

NAME           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/web1   ClusterIP   192.168.4.135   <none>        80/TCP    9s
```

Pokud chceme mít Service trochu víc pod kontrolou, například chceme ji definovat jako typ LoadBalancer (dát ji public IP například) nebo ji dát jiné jméno, můžeme to rozdělit a využít kubectl expose.

```bash
$ kubectl run web2 --image nginx:alpine --port 80
deployment.apps "web2" created

$ kubectl expose deploy/web2 --port 80 --target-port 80 --type LoadBalancer --name mywebservice
service "mywebservice" exposed

$ kubectl get pod,service
NAME                            READY     STATUS    RESTARTS   AGE
pod/mojepody-845bc575df-6jsln   1/1       Running   0          6m
pod/mojepody-845bc575df-9qbpf   1/1       Running   0          6m
pod/mojepody-845bc575df-g2l8r   1/1       Running   0          6m
pod/mujpod                      1/1       Running   0          7m
pod/web1-7dfd7b9658-mrkzl       1/1       Running   0          2m
pod/web2-8f75d4946-44256        1/1       Running   0          1m

NAME                   TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/mywebservice   LoadBalancer   192.168.5.241   <pending>     80:32479/TCP   19s
service/web1           ClusterIP      192.168.4.135   <none>        80/TCP         2m
```

## Output do yaml
U CKA zkoušky mi moc nevyhovalo probírat se všemi přepínači v imperativních příkazech, běžně používám spíše YAML. Velmi dobré tedy pro mě bylo využít imperativních příkazů pouze k vybudování potřebného skeletonu, který jsem si pak upravil. Využívám na to přepínač --dry-run (věci se nepošlou do Kubernetes) a -o yaml. Ten obsahuje víc věcí, než je potřeba (třeba creationTimeStamp), ale ty si vymažu.

```bash
$ kubectl run mypod2 --replicas 3 --image nginx:alpine --dry-run -o yaml > file.yaml
$ cat file.yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    run: mypod2
  name: mypod2
spec:
  replicas: 3
  selector:
    matchLabels:
      run: mypod2
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        run: mypod2
    spec:
      containers:
      - image: nginx:alpine
        name: mypod2
        resources: {}
status: {}
```

Podobně je občas fajn se kouknout na běžící věci v YAML formátu. Kubectl describe je fajn, ale je jinak formátovaný a jakmile si na YAML zvyknete, může to být pro vás jednodušší.

```yaml
$ kubectl get pod mujpod -o yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: 2018-08-17T06:49:18Z
  labels:
    run: mujpod
  name: mujpod
  namespace: tomas
  resourceVersion: "2530414"
  selfLink: /api/v1/namespaces/tomas/pods/mujpod
  uid: a9aff891-a1e9-11e8-a783-f6acfd690be3
spec:
  containers:
  - image: nginx:alpine
    imagePullPolicy: IfNotPresent
    name: mujpod
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-wnj67
      readOnly: true
...
```

## Logy
Z kubectl můžete koukat na logy v Podech (stderr a stdout). Můžeme použít tail a navíc si zobrazit logy ne starší než jednu hodinu.

```bash
kubectl logs mujpod --tail 100 --since 1h -n kube-system
```

Nabízí se i další zajímavé filtrace. Například přes -l si můžete vypsat logy ze všech Podů vyhovujících nějakému labelu. Můžete také koukat ne na pod, ale třeba deploy/mujdeployment a také streamovat logy s přepínačem -f.

## Skok do kontejneru
Jeden z nejčastějších úkonů při ladění aplikací je možnost vlézt dovnitř do kontejneru a odtamtud něco zkusit. Rozjíždět kvůli tomu SSH v kontejneru je zbytečně složité a není to dobrá bezpečností praktika. Do produkce to nepatří a když si na to zvyknete v Dev/Testu znamená to, že budete muset mít jiný obraz pro test a produkci, což popírá jednu z hlavních výhod kontejnerů (tedy že jsou stejné od testu až do produkce). Lepší je tedy odskočit si do Podu přes kubectl exec.

```bash
$ kubectl exec -it mujpod -- sh
/ #
```

## Autocomplete v Bash
Pokud si nevezmete na pomoc nějaké GUI je vypisování názvu například Podů docela nepříjemné zejména pokud jsou součástí deploymentu a tím pádem je jejich jméno lidsky složité. Kubectl ale umí vygenerovat autocomplete skripty pro bash. Stačí je načíst do vaší session (nebo to udělat pokaždé v bashrc). Pak napíšu kubectl get pod mojep a zmáčknu tabulátor. Bash mi doplní co se doplnit dá (je unikátní). Velmi dobrá pomůcka.

```bash
$ source <(kubectl completion bash)
$ kubectl get pod mojepody-845bc575df-
```

## Nápověda
Kubectl explain obsahuje v zásadě dokumentaci Kubernetes API, kterou máte k dispozici i bez brouzdání Internetem.

```plaintext
$ kubectl explain pod
KIND:     Pod
VERSION:  v1

DESCRIPTION:
     Pod is a collection of containers that can run on a host. This resource is
     created by clients and scheduled onto hosts.

FIELDS:
   apiVersion   <string>
     APIVersion defines the versioned schema of this representation of an
     object. Servers should convert recognized schemas to the latest internal
     value, and may reject unrecognized values. More info:
     https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

   kind <string>
     Kind is a string value representing the REST resource this object
     represents. Servers may infer this from the endpoint the client submits
     requests to. Cannot be updated. In CamelCase. More info:
     https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

   metadata     <Object>
     Standard object's metadata. More info:
     https://git.k8s.io/community/contributors/devel/api-conventions.md#metadata

   spec <Object>
     Specification of the desired behavior of the pod. More info:
     https://git.k8s.io/community/contributors/devel/api-conventions.md#spec-and-status

   status       <Object>
     Most recently observed status of the pod. This data may not be up to date.
     Populated by the system. Read-only. More info:
     https://git.k8s.io/community/contributors/devel/api-conventions.md#spec-and-status

$ kubectl explain pod.spec.volumes.azureDisk
KIND:     Pod
VERSION:  v1

RESOURCE: azureDisk <Object>

DESCRIPTION:
     AzureDisk represents an Azure Data Disk mount on the host and bind mount to
     the pod.

     AzureDisk represents an Azure Data Disk mount on the host and bind mount to
     the pod.

FIELDS:
   cachingMode  <string>
     Host Caching mode: None, Read Only, Read Write.

   diskName     <string> -required-
     The Name of the data disk in the blob storage

   diskURI      <string> -required-
     The URI the data disk in the blob storage

   fsType       <string>
     Filesystem type to mount. Must be a filesystem type supported by the host
     operating system. Ex. "ext4", "xfs", "ntfs". Implicitly inferred to be
     "ext4" if unspecified.

   kind <string>
     Expected values Shared: multiple blob disks per storage account Dedicated:
     single blob disk per storage account Managed: azure managed data disk (only
     in managed availability set). defaults to shared

   readOnly     <boolean>
     Defaults to false (read/write). ReadOnly here will force the ReadOnly
     setting in VolumeMounts.
```

# Kubernetes Dashboard
Řeknu vám to rovnou. Kubernetes Dashboard mě nanadchnul. Není tam nic převratně užitečného, není zabezpečený (autentizace, šifrování) a já ho moc nepoužívám. V clusteru ovšem běží jako interní service (ale nepublikujte si ho ven na public adresu z bezpečnostních důvodů, leda třeba přes zabezpečený Ingress a na něm si vyřeště nějakou rozumnou autentizaci třeba integrací ingress na AAD, což najdete na mém GitHubu).

Pokud máte v clusteru zapnutý RBAC (což je v AKS default) musíte pro Dashboard zařídit nejdřív práva.

```bash
kubectl create clusterrolebinding kubernetes-dashboard \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:kubernetes-dashboard
```

Připojit se do něj můžete před port-forward na service případně použít příkaz az aks browse.

```bash
$ kubectl port-forward service/kubernetes-dashboard 12345:80 -n kube-system
Forwarding from 127.0.0.1:12345 -> 9090
Forwarding from [::1]:12345 -> 9090
```

![](/images/2018/img_5b7676595d6b3.png){:class="img-fluid"}

Když ale pominu děravou bezpečnost dělá GUI to co má a dá se s ním v pohodě pracovat.

# Azure Kubernetes Service health a logování
AKS jako přidanou hodnotu nabízí monitoring a logování přímo do Azure, což si při vytváření clusteru můžete zapnout.

Takhle vypadá přehledová obrazovka vašeho clusteru.

![](/images/2018/img_5b76784a4c71e.png){:class="img-fluid"}

Můžeme kouknout na Nody a co na nich běží (mc znamená milicore a 1000 mc je tedy jeden core).

![](/images/2018/img_5b7678c20adce.png){:class="img-fluid"}

Sledovat můžeme minimum, maximum, průměr nebo percentily.

![](/images/2018/img_5b76790bcc6db.png){:class="img-fluid"}

Totéž lze sledovat z pohledu paměti.

![](/images/2018/img_5b76794174adf.png){:class="img-fluid"}

Zkoumat můžeme samozřejmě i jednotlivé Pody.
![](/images/2018/img_5b767965a7e11.png){:class="img-fluid"}

Všimněte si tlačítka nahoře, které nás přesune do Log Analytics a předformuluje vyhledávací dotaz, abychom viděli logy z tohoto Podu.

![](/images/2018/img_5b767a51204f6.png){:class="img-fluid"}

Podívat se ale můžeme klidně i na všechny logy najednou.

![](/images/2018/img_5b767a7424f13.png){:class="img-fluid"}

Je to nesmírně mocný engine Log Analytics, který můžete využít i pro logování z VM, platformních služeb a je i pod kapotou aplikačního monitoringu Application Insights. Povídání o něm do tohoto článku nepatří, ale můžete si ho například vyzkoušet zdarma na adrese [https://docs.loganalytics.io](https://docs.loganalytics.io)

Protože jsou všechny metriky v Azure Log Analytics, můžete je snadno navázat na alertovací schopnosti Azure. Díky tomu můžete při nějaké události odeslat email, SMS, zavolat webhook do jiného systému, automaticky založit ticket v některých ITSM nástrojích jako je Service Now nebo dokonce vyvolat spuštění Logic Apps - orchestrátoru, ve kterém můžete dělat složitá flow a využít jeho integrace na Microsoft svět (například nasadit ChatOps s Microsoft Teams) a třetí strany (SFDC, Service Now, SAP, Wordpress, Twillio, Slack a hromada dalších).

# Kubernetes plugin pro Visual Studio Code
Tím se dostáváme k nástrojům blíže vývojářům. Tam je jedna zásadní věc a to Azure DevSpaces, což je obrovské téma na samostatný článek. Dnes se v přehledu monitorovacích možností omezme na monitoring (spíše než automatické nasazování a debugging v AKS clusteru) a to s využitím extension pro open sourcové Visual Studio Code.

Plugin naleznete přímo v katalogu a instalace je záležitostí několika vteřin.

![](/images/2018/img_5b767c66b7afa.png){:class="img-fluid"}

Plugin se pak podívá do vašeho konfiguračního souboru pro kubectl a hned bude fungovat.

![](/images/2018/img_5b767c9eaae06.png){:class="img-fluid"}

Můžeme se podívat na namespace a přepínat se mezi nimi (a nepotřebujeme ani vytvářet kontexty).

![](/images/2018/img_5b767dc5e40cd.png){:class="img-fluid"}

Takhle se třeba podíváme na Nody a co na nich běží. Přes pravé tlačítko se dostaneme k dalším možnostem.

![](/images/2018/img_5b767d2a0cf8a.png){:class="img-fluid"}

Tak například Desribe jednoduše vyvolá příkaz kubectl describe ve vašem okně, takže se s ním nemusíte vypisovat (zejména ladit správná jména a tak).

![](/images/2018/img_5b767d672de0e.png){:class="img-fluid"}

Pokud se třeba podíváme na Pody a dvakrát ťukneme na nějaký z nich, otevře se nám v okně ve formě YAML souboru (tohle mám strašně rád).

![](/images/2018/img_5b767e1ddf0f8.png){:class="img-fluid"}

Podívejte se co všechno vám nabízí pravé tlačítko.

![](/images/2018/img_5b767e428bcfe.png){:class="img-fluid"}

Můžete Pod vymazat a nebo třeba vypsat či streamovat jeho logy. To plugin udělá zase v okně příkazové řádky, takže formát výstupu vám bude důvěrně známý.

![](/images/2018/img_5b767e8697b74.png){:class="img-fluid"}

Můžete jednoduše zahájit port forwarding nebo skočit do terminálu přímo v Podu. Použije se kubectl exec, ale to zase nemusíte řešit a vypisovat - vám se jednoduše otevře terminálové okno a jste přímo uvnitř Podu.

![](/images/2018/img_5b767ed7c4b1a.png){:class="img-fluid"}

Všimněte si ještě jedné zásadní věci - tento plugin na rozdíl od Dashboardu pracuje i s Helm šablonami, což jak si řekneme někdy později je zásadní nástroj pro reálnou práci s Kubernetes.

o ale stále není všechno. Tento pluginy přináší i porozumění struktuře Kubernetes YAML souborů. Podívejme se na to. Napsal jsem spec: a zmáčknul CTRL+mezerník.

![](/images/2018/img_5b76803445a68.png){:class="img-fluid"}

Přesně tak. Intellisense pro Kubernetes, který vám radí co můžete použít a kontroluje pro vás syntaktickou správnost vašich YAML souborů.


Co tedy kdy používat? Myslím, že je rozhodně dobré naučit se efektivně pracovat s kubectl. Bude se vám to hodit jak v praxi tak třeba při CKA zkoušce, kde nic jiného nedostanete. A co GUI? Pro operations věci (mám cluster a v něm běží aplikace), kdy chci sledovat jaké je zatížení, jestli je všechno v pořádku a prohrabávat se logy, když dělám troubleshooting, tak tam doporučuji Azure portál. Pro práci na vytváření Kubernetes či Helm šablon a na ladění (vývojové a testovací prostředí), tak tam preferuji plugin do Visual Studio Code. Souvisí to i se schopností řešit tam další věci jako je buildování kontejnerů či práce s Azure Container Registry. Ostatně Azure DevSpaces pro AKS, což je výborná integrace pro vývojáře včetně remote debuggingu, na kterou se podíváme někdy příště, se používá právě Visual Studio Code nebo velké Visual Studio.
