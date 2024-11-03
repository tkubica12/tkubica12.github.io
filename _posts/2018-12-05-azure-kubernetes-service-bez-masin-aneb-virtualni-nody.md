---
layout: post
status: publish
published: true
title: Azure Kubernetes Service bez mašin aneb virtuální nody
tags:
- Serverless
- Kubernetes
---
Kubernetes mám strašně rád, ale jedna věc mi v cloudu nesedí. Chápu, že ve vlastním datovém centru budu rád, že Kubernetes se postará o moje nody a pomůže mi na ně spravedlivě umisťovat kontejnery. To je skvělé. Ale cloud je přeci alespoň teoreticky neomezený zásobník zdrojů a platím jen za to, co používám. Chci si škálovat aplikační Pody a ne u toho přemýšlet, jak velký mám cluster pod tím a jak se mi to na nody poskládá. Azure Kubernetes Service vyřeší spoustu infrastrukturních otázek tím, že si povídá s Azure - síťařina, externí balancing, Volumy, servisní katalog (např. databáze), v budoucnu L7 proxy apod. Co kdyby ale AKS bylo tak cloudové, že mne nody nebudou vůbec zajímat co do jejich přítomnosti nebo sizingu a můžu se soustředit jen na Pody se svými aplikacemi? Právě to je v Azure Kubernetes Service od tohoto týdne v preview.

Předzvěstí této cesty jsou Azure Container Instances. Kontejnery, které pustíte přímo v cloudu bez nutnosti před tím vytvořit nějakou VM. Open source project Virtual Kubelet, který Microsoft tento týden (po asi roce práce a příspěvků komunity pro různá nasazení včetně AWS Fargate) věnoval do CNCF, umožní vytvářet virtuální nody v Kubernetes právě pro takové účely. Může to být ACI, může jít o virtuální nody reprezentující všechna vaše IoT zařízení (to v AKS a IoT Hub také Microsoft má), nebo integrace do Service Fabric Mesh (i to už existuje) či z Kubernetes můžete ovládat Azure Batch (platformu pro výpočty, například rendering filmů). Nicméně ACI mělo zásadní omezení v networkingu - podporovala pouze public IP a přestože na některé účely to nevadí, nebylo možné jej integrovat do síťových vlastností Kubernetes (Service, Ingress, ...).

To se ale změnilo - ACI dnes integraci do VNETu (v preview) umí a tak Azure Kubernetes Service mohla použít technologii u virtuálních nodů, o kterých si dnes povíme.

# Vytvoříme si nový AKS cluster s virtuálními nody

V portálu zahájím vytváření nového clusteru. Na první stránce nahoře zatím nic nového:
![](/images/2018/img_5c06c85930773.png){:class="img-fluid"}

Nicméně hned o kousek níže je nová možnost zapnout virtuální nody (v preview). Cluster nemůžeme mít zcela bez nodů (některé funkce řešení zprostředkovává i pro ACI Pody skutečný node - dobrý příklad je třeba NGINX Ingress nebo různé systémové nadstavby), ale k těm klasickým si přidáme virtuální.

![](/images/2018/img_5c06c8ba7d588.png){:class="img-fluid"}

Na další rozdíl v průvodci narazíte u networkingu. AKS tady mám v Advanced Networking režimu a mám tak konfigurovatelný VNET (v mém případě nový, ale může to být klidně už existující). Kromě subnetu pro normální nody je tu nově subnet pro virtuální nody, respektive privátní IP adresy pro Pody, které nebudou mít skutečný node, jen virtuální. Musí mít samostatný subnet, ale jsou součástí vašeho běžného VNETu.

![](/images/2018/img_5c06c9412f562.png){:class="img-fluid"}

Nic dalšího není potřeba, chvilku počkejme a podívejme se, jak se to používá.

# Nasadíme Pody ve virtuálním nodu

Jak to celé vypadá z pohledu uživatele AKS? Kromě běžných nodů se nám objeví node s názvem virtual-node-aci-linux. To "linux" je vodítko k tomu, že někdy později bude v možné mít i totéž pro Windows (jak ACI tak Virtual Kubelet to už podporuje a můžete to do AKS ručně přidat, takže předpokládám jde o integrace z pohledu privátního networkingu, které tam ještě nejsou hotové).

U nodu si všimněme, že má nastaven taint.

```yaml
$ kubectl describe node virtual-node-aci-linux
Name:               virtual-node-aci-linux
Roles:              agent
Labels:             alpha.service-controller.kubernetes.io/exclude-balancer=true
                    beta.kubernetes.io/os=linux
                    kubernetes.io/hostname=virtual-node-aci-linux
                    kubernetes.io/role=agent
                    type=virtual-kubelet
Annotations:        node.alpha.kubernetes.io/ttl=0
CreationTimestamp:  Tue, 04 Dec 2018 20:30:52 +0100
Taints:             virtual-kubelet.io/provider=azure:NoSchedule
```

O pokročilejších možnostech schedulingu už jsem na tomto blogu psal. V zásadě taint je černý puntík, který odrazuje Pody, které mají výchozí konfiguraci. Pouze ty Pody, které mají specifickou toleraci na tento černý puntík, mohou na tento node přistát.

Udělám si tedy následující deployment. Použiji jednoduchý nodeSelector (už bych neměl - pokud používáte, začněte si zvykat spíše na nodeAffinity), abych Pody namířil na virtuální node a také Podům dám toleranci na taint.

Pošleme to tam a podíváme se, jaké IP naše Pody mají. Ano - jsou to IP z mého VNETu!

```bash
$ kubectl get pods -o wide
NAME                  READY     STATUS    RESTARTS   AGE       IP           NODE
web-c946577f8-8tgcw   1/1       Running   0          1m        10.241.0.6   virtual-node-aci-linux
web-c946577f8-vggg6   1/1       Running   0          4m        10.241.0.5   virtual-node-aci-linux
```

Azure Container Instances pro jednotlivé Pody najdete v MC resource group.

![](/images/2018/img_5c06d8a619626.png){:class="img-fluid"}

# Funguje síťařina? Zkusme Service i mix skutečných a virtuálních nodů

Zdá se, že Pody skutečně mají IP adresy z VNETu. Vyzkoušejme, že fungují síťové koncepty a nasaďme Kubernetes Service s virtuální IP adresou a zvolíme službu publikovanou ven z clusteru, ale na privátní IP adrese. Služba má jako selector label app: web (proč ne také klíč node, který v deploymentu mám, vám už určitě došlo nebo dojde o pár řádků později).

```yaml
kind: Service
apiVersion: v1
metadata:
  name: web-service
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
spec:
  selector:
    app: web
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80</pre>
```

Služba je nastavena.

```bash
$ kubectl get svc
NAME              TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
kubernetes        ClusterIP      10.0.0.1       <none>        443/TCP        41m
web-service       LoadBalancer   10.0.246.208   10.240.0.97   80:30997/TCP   11m
```

Vyzkouším a opravdu funguje tak jak má.

Jsou Pody na virtuálních uzlech ze síťového hlediska stejné, jako na běžných nodech? Jinak řečeno mohu svou službu běžet v několika instancích na běžných nodech, ale v případě potřeby navýšit výkon přidáním další instance na virtuálním nodu? To totiž dává dost smysl. Autoškálování samotného clusteru (přidávání/ubírání nodů) je totiž relativně pomalé a je to otrava. Platil bych si raději stabilní nody a špičky vykryl přes ACI.

Pošlu tam tedy jiný deployment, který bude "běžný", tedy nebude mít toleraci na virtuální node, takže přistane na normálních. S mým prvním deploymentem má společný jeden label (app: web), který je v selectoru Service, takže bych měl vidět, jak mi pod jednou virtuální IP odpovídají Pody z běžných i virtuálních nodů.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-classic
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
      node: classic
  template:
    metadata:
      labels:
        app: web
        node: classic
    spec:
      containers:
      - name: web
        image: tkubica/web:1
        env:
        - name: PORT
          value: "80"
        ports:
        - containerPort: 80
```

Funguje - Service korektně balancuje provoz na Pody na normálních nodech i virtuálním nodu.

# Kde má virtuální node limity?

Je pochopitelné, že simulovaný node a implementace ACI bude mít některé limity oproti standardnímu nodu. Vyzkoušejme si jaké to jsou.

Exec do kontejneru je možný - důležitá věc pro troubleshooting i health probes. Logy jsou také integrované, takže příkaz kubectl logs funguje. Třetí z mých oblíbených diagnostických příkazů kubectl port-forward ale v tuto chvíli nechodí.

Nejzásadnější omezení jsou ale Volume. Virtuální node nemá žádný svůj filesystem a nepodporuje vytvoření Volume s mapováním do svého FS. To je nutné pro předávání například ConfigMap přes Volume - na virtuálních nodech můžete použít jen environmentální proměnnou. Virtuální nody aktuálně nepodporují ani externí Volume a to jak Azure Disk tak Azure Files. S tímto je tedy určitě nutné počítat.

Nicméně služba je aktuálně v preview a vývoj na projektu Virtual Kubelet v rámci CNCF i vývoj ACI a AKS jde rychle dopředu, takže určitě přijdou mnohá vylepšení.

Budoucnost Kubernetes v cloudu je určitě bez-nodová, ale ještě je potřeba nějaký kus ujít. Nicméně už dnes máte tuto možnost v preview na vašem Azure Kubernetes Service a pokud se vypořádáte s absencí Volume dostanete skutečnou elasticitu a platíte podle kontejnerů, ne virtuálních mašin nodů. Doporučuji mít cluster s běžným nody třídy D nebo E a ty si zarezervovat (předplatit a získat tak slevu). Otázka zbývá jak pak burstovat při zátěži nebo vyřešit clustery, které jsou potřeba jen občas. Klasické řešení je autoscaling Podů a k tomu autoscaling podvozku, ale použití nodeless má pro takový scénář naprosto zásadní výhody. Zkuste si to!
