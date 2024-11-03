---
layout: post
title: Použití lokální storage v Azure Kubernetes Service
tags:
- Storage
- Kubernetes
---
Některé typy Azure VM nabízí poměrně dost lokální storage ve formě temp disků nebo dokonce extrémně výkonných NVMe storage karet v L-series mašinách. Dává smysl takové věci mít v AKS? Lze je nějak využít? A kdy bych naopak měl raději zvolit vzdálenou plně redundantní storage a třeba za lokální disky ve VM ušetřit (zvolit VM bez nich, která pak je o fous levnější)?

# Kdy může dávat lokální storage v AKS smysl?
Vždy tvrdím, že state je to nejsložitější a způsobuje to ty největší průšvihy, takže pokud můžete, pryč s ním do služby, ať se o to stará provider. Databáze jako služba, fronta jako služba, monitoring jako služba - to všechno tam najdete a s vysokými SLA. Když ale přecijen musíte state v Kubernetu mít, zvolte ideálně zónově redundantní storage, ať máte menší práci s přemýšlením o architektuře v případě výpadku AZ (tzn. ZRS disky, Azure Files ZRS). Když už potřebujete jít per-zóna, například protože potřebujete nejnižší možnou latenci, použijte třeba UltraSSD nebo NetApp Files pro maximální výkon. Kdy tedy může dávat smysl vyloženě lokální neredundantní storage?
- Vaše aplikace potřebuje vyztužit paměť pro dočasné výpočty, cache a tak podobně. To dává smysl - RAM je drahá, SSD o poznání levnější (a pomalejší). Ztráta těchto dat neznamená ztrátu primárních dat, "pouze" poteniálně zpomalení aplikace (než si třeba znovu vybuduje cache nebo než nažene čas ztracený tím, že mezivýpočty jsou pryč a musí začít znovu).
- Vaše aplikace, nebo spíše databázový systém, je optimalizovaná pro shared-nothing architekturu. Nepotřebuje žádnou vysoce dostupnou storage, stačí jí obyčejný compute s lokálním prostorem a ona si přes víc svých instancí dokáže data sama replikovat. To má potenciál úžasně narychlit čtení (data jsou na velmi rychlém lokálním disku, ne někde v síti) a obvykle i zápis (a to i v případě silně konzistentních systému typu synchronní replikace).

Není bez zajímavosti, že Azure SQL General Purpose je blíže variantě compute + LRS nebo ZRS storage (AZ-redundant je u Azure SQL GP aktuálně v preview), zatímco Azure SQL Business Critical je více shared nothing (4 nody a každý má svou vlastní ultrarychlou storage, replikuje se DB prostředky). To druhé je samozřejmě rychlejší...ale dražší. Ale jen tak pustit shared nothing v AKS bez dalšího přemýšlení a Hornbach náladou (udělej si sám)? To by mohla být dost chyba, pokud nevíte, co děláte.

# Proč je v cloudovém Kubernetu lokální storage o poznání méně používaná, než v lokálním prostředí?
V lokálním prostředí je celkem časté, že nody Kubernetes clusteru jsou opečovávané sněhové vločky - jsou mutable. Děláte jim tam aktualizace OS, aktualizace Kubernetu. Něco takového je náchylné na chyby a vůbec to neškáluje do rozměrů a požadavků na spolehlivost, kterou vyžadujete od cloudu. Proto AKS nody neoprašuje, ale zabijí a vytváří místo nich nové - s novějším image, novějším Kubernetem - jsou pro něj tyto nody immutable nebo dokonce je můžeme označit za ephemeral. Nezáleží na nich, jsou zaměnitelné za jiné. 

Tak - a do tohoto prostředí vy teď použijete lokální storage a najednou vám při každé aktualizaci clusteru (a tu byste měli dělat minimálně měsíčně, spíše častěji) tento pěkně propláchne všechna data. Jasně, dělá to pustupně, takže vám neumře všechno najednou, jenže:
- Při velkých objemech je ztráta dat docela zásah, který není problém podstoupit v případě nějakého výpadku jednou ročně, ale pravidelnost proplachování lokálních dat v cloudu vám rozhodně vyhovovat nemusí. Data se obvykle musí doreplikovat a co když to trvá několik hodin? Pokud si to nijak neošetříte, tak vám cluster bude vyměňovat nody tak zhruba po 5 minutách a to vůbec nemusíte stihnou dořešit data!
- Totéž se týká různých cache nebo mezivýpočtů - co když s propláchnutou cache má vaše aplikace desetinový výkon a zavlažit ji trvá 30 minut? A mezitím se cluster upgraduje a proplachuje a proplachuje?

Jinak řečeno - události ztráty dat jsou v cloudu daleko častější, protože Kubernetes nody jsou ephemeral a tak s tím počítejte. Žít se s tím určitě dá, ale vyžaduje to zvláštní zacházení a dost kontrolované prostředí. Když nic jiného měli byste v aplikaci používat startupProbe (nejen livenessProbe a readynessProbe) a otevřít je skutečně až po té, co je Pod kompletně rozchozený (doreplikovaná data, zavlažená cache) a to kombinovat s Pod disruption budgetem, abyste zastavili nekoordinovaný upgrade clusteru a vždy se počkalo. Jasně že to všechno jde, ale občas se potkám s trochu naivním přísupem, který tyhle věci nezohledňuje.

Není bez zajímavosti, že hodně referenčních architektur na služby, které jsou principiálně schopné shared-nothing architektury jako je Kafka, Cassandra nebo Elastic, celkem běžně pro Kubernetes nabízí oba přístupy a říkají, že pro jednodušší a spolehlivější operations je remote storage v cloudu dobrá věc, třeba [tady u Elastic](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-storage-recommendations.html). 

# Jaké řešení pro lokální storage zvolit, co jsou výhody a nevýhody
Všechny příklady, co jsem testoval, najdete na mém [GitHubu](https://github.com/tkubica12/cloud-storage-tests/blob/main/aks-local-storage/aks-local-storage.md)

## EmptyDir
Tohle je nejjednodušší způsob, jak využít lokální storage. 

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test
spec:
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
      - name: test
        image: ubuntu
        command: ["/bin/bash"]
        args: ["-c", "while true; do date | tee /path/$(date +'%s').txt; sleep 15; done"]
        volumeMounts:
          - mountPath: /path
            name: storage
      volumes:
        - name: storage
          emptyDir:
            sizeLimit: 1Gi
```

Takhle udělám jednoduchý deployment, který vytváří soubory ve storage a všechno funguje jak má. Nicméně to má nějaké nevýhody:
- sizeLimit implementace není "storagová" - jakmile jsem překročil velikost [https://github.com/tkubica12/aksLocalStorage#size-limit-test](https://github.com/tkubica12/aksLocalStorage#size-limit-test) tak vám to Pod normálně zabije. Storage prostor to ochrání, ale nemusí to být to, co čekáte z pohledu dostupnosti aplikace.
- Nemůžeme si nijak určit, na kterém zařízení to je - bude to na hlavním OS disku, což sebou nese tyto obtíže:
  - Pokud máte OS disk ve formě Azure Disk a zvolili jste malou velikost, máte i relativně malé IOPSy a propustnost. To tomu nodu obvykle moc nevadí, ale pokud vaše aplikace vyžere všechno IO, což se jí snadno podaří, může to i destabilizovat node.
  - Pokud máte OS disk ephemeral, tak výkonu je dostatek, to je fajn, ale zas tam typicky nemáte příliš velikosti a ephemeral disk má velikost danou typem stroje, nemůžete ho zvětšit.

## HostPath
Do Podu můžete namapovat adresář z hostitele, tedy i takový, který sedí na jiném fyzickém zařízení - například na NVMe kartě u L-series VM. To je určitě výborné, to chceme.

Nicméně musíme zajistit vytvoření file systému, mount, nasekání adresářů a to tak, aby se to stalo samo, když se node objeví (nezapomeňme - při upgradu AKS dostaneme jiný). To lze vyřešit privilegovaným DamemonSetem a já jsem zvolil initContainer. Důvod je ten, že potřebuji privilegia, ale nechci aby tam pak trvale běžel nějaký neukončený proces s vysokými právy. Ale jako Job to dát nemůžu, potřebuji to jako DaemonSet, ať se to spustí na každém nodu, ale ne pořád dokola. Řešením je privilegovaný initContainer, kterým naskriptuji založení FS a adresářů a po jeho ukončení naběhne vysející proces v container, který ale už není privilegovaný.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: prepare-nvme
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: prepare-nvme
  template:
    metadata:
      labels:
        app: prepare-nvme
    spec:
      initContainers:
        - name: ubuntu
          image: ubuntu
          securityContext:
            privileged: true
          command: ["/bin/sh"]
          args: ["-c", "mkfs.ext4 -E nodiscard /dev/nvme0n1; mount /dev/nvme0n1 /mynvme"]
          volumeMounts:
            - mountPath: /mynvme
              name: storage
              mountPropagation: "Bidirectional"
      containers:
        - name: donothing
          image: busybox
          command: ["/bin/sh"]
          args: ["-c", "while true; do sleep 60; done"]
      volumes:
        - name: storage
          hostPath:
            path: /mynvme
```

Pak už stačí nahodit Pod.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test
spec:
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
      - name: test
        image: ubuntu
        command: ["/bin/bash"]
        args: ["-c", "while true; do date | tee /path/$(date +'%s').txt; sleep 15; done"]
        volumeMounts:
          - mountPath: /path
            name: storage
      volumes:
        - name: storage
          hostPath:
            path: /mynvme
```

Je tady ale hromada nepříjemných konsekvencí:
- Nemůžu připustit, aby si někdo namapoval nějaký systémový adresář nebo tak něco, takže určitě musím udělat Azure Policy a kontrolovat to jen na vybrané cesty. hostPath se obecně považuje za bezpečnostní riziko, takže různé systémy typu Microsoft Defender for Containers budou řvát.
- Je to jak vidno všechno hodně ruční - musím vytvořit disky, adresáře a nemám moc dobrou kontrolu kde co je. Scheduler nebude moc chytrý a nedokáže poznat, na kterém node ten adresář je a kde ne, takže se to může zaseknout. Navíc se poměrně snadno stane, že si namapuji adresář, který má někdo jiný a vidím jeho data. Zkrátka je to trochu (dost) bordel.
- Limit velikosti nelze vynutit ... na druhou stranu to mám alespoň na jiném disku, tak ať se tam třeba pomlátí, node neohrozím - ale i to pomlácení může být pro mě dost problém. Scheduler navíc vůbec netuší kolik místa kde zbývá, takže mi klidně vznikne inferno na jednom nodu a na druhém bude prostor nevyužitý.

## Local Persistent Volume
Lokální volume je určitě bezpečnější a příčetnější řešení. První varianta je starat se o to ručně, tedy opět DaemonSetem připravit disk, adresáře, a bohužel i ručně nastavit Persistent Volume, který **musí** mít affinitu na konkrétní node.

Například takhle:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv1
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Recycle
  storageClassName: local-disk
  local:
    path: /mynvme/disk1
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostaname
          operator: In
          values:
          - node1
```

Už je to trochu lepší, zejména je tady koncept mapování jaký volume na kterém nodu je a scheduler je schopen s tím nějak pracovat, navíc je to bezpečnější. Ale nevýhod je pořád dost:
- Musím si ručně dost věcí připravit, například adresáře. To se dá vyřešit s Local Path Provisionerem ... ale to je zas další komponenta do hry.
- Persistent Volume musím vytvářet ručně a mít ho navázaný na konkrétní node. Po upgrade AKS se některé nody budou jmenovat jinak a musím to předělat.
- Storage limit nelze vynutit.

Nevýhody manuálního vytváření mým DaemonSetem jsem se pokusil odstranit něčím oficiálním - Local Persistent Volume Provisioner. Ten je fajn - dokáže automaticky objevit jednotlivá zařízení, udělat na nich file systém a sám vytvořit příslušné Persistent Volume, takže já už pak jen v aplikaci použiji storage class a PVC a ona se jich zmocní.

```yaml
---
# Source: provisioner/templates/provisioner.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-provisioner-config
  namespace: kube-system
data:
  storageClassMap: |
    local-disk:
       hostDir: /dev
       mountDir:  /dev
       blockCleanerCommand:
         - "/scripts/shred.sh"
         - "2"
       volumeMode: Filesystem
       fsType: ext4
       namePattern: nvme*
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: local-volume-provisioner
  namespace: kube-system
  labels:
    app: local-volume-provisioner
spec:
  selector:
    matchLabels:
      app: local-volume-provisioner
  template:
    metadata:
      labels:
        app: local-volume-provisioner
    spec:
      serviceAccountName: local-storage-admin
      nodeSelector:
        kubernetes.io/os: linux
      containers:
        - image: "mcr.microsoft.com/k8s/local-volume-provisioner:v2.4.0"
          name: provisioner
          imagePullPolicy: IfNotPresent
          args:
            - "--v=2"
          securityContext:
            privileged: true
          env:
            - name: MY_NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
          volumeMounts:
            - mountPath: /etc/provisioner/config
              name: provisioner-config
              readOnly: true
            - mountPath: /dev/
              name: local-disk
              mountPropagation: "HostToContainer"
      volumes:
        - name: provisioner-config
          configMap:
            name: local-provisioner-config
        - name: local-disk
          hostPath:
            path: /dev/

---
# Source: provisioner/templates/provisioner-service-account.yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  name: local-storage-admin
  namespace: kube-system

---
# Source: provisioner/templates/provisioner-cluster-role-binding.yaml

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: local-storage-provisioner-pv-binding
  namespace: kube-system
subjects:
  - kind: ServiceAccount
    name: local-storage-admin
    namespace: kube-system
roleRef:
  kind: ClusterRole
  name: system:persistent-volume-provisioner
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: local-storage-provisioner-node-clusterrole
  namespace: kube-system
rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: local-storage-provisioner-node-binding
  namespace: kube-system
subjects:
  - kind: ServiceAccount
    name: local-storage-admin
    namespace: kube-system
roleRef:
  kind: ClusterRole
  name: local-storage-provisioner-node-clusterrole
  apiGroup: rbac.authorization.k8s.io
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: local-disk
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
```

Pak už jen použiji StatefulSet a nahodím dvě instance a každá dostane svůj volume.

Platí, že máme lépe vyřešenou bezpečnost, scheduler je schopen pochopit která storage kde je, takže nedojde k zásekům typu Pod je přiřazen na node, ale ten adresář tam není a už i přípravné práce jsou řešeny automaticky. Ale stále jsou tu nevýhody:
- Tento model vytvoří PV z fyzického zařízení - pokud máme jednu NVMe kartu (třeba u VM L8s_v2), bude jedno PV. Určitě OK, když mám dedikovaný nodepool na nějaký storage workload nebo tak něco, ale nemáme vyhráno, pokud potřebuji něco granulárního (řezat NVMe pro různé aplikace).
- Provisioning je statický - Volume vznikne hned a jen se přiřazuje.
- Limit velikosti nelze vynutit.

## NativeStor (nadstavba TopoLVM)
TopoLVM je CSI driver, který využívá LVM a jejich orchestraci. Kromě toho umí držet topologické informace a je to jediná situace, kdy scheduler myslím ví, kolik místa kde zbývá a rozhoduje se podle toho (od verze Kubernetes 1.21). Navíc je to dynamický provisioning - LVM nevznikne dokud není potřeba. A ještě lépe - má velikostní omezení jaké si řeknete. A podporuje i resize operace. Zkrátka tohle je pro náročnější využívání lokální storage výborné řešení. Tedy - pokud bych měl jen TopoLVM, musím ještě zajistit přípravu zažízení - najít NVMe kartu, udělat nad ní Physical Volume a takové věci. Proto se mi líbí nadstavba NativeStor, což je operátor pro TopoLVM a tím se to ještě zjednoduší.

Nahodíme operátor.

```bash
kubectl apply -f https://raw.githubusercontent.com/alauda/nativestor/main/deploy/example/operator.yaml
kubectl apply -f https://raw.githubusercontent.com/alauda/nativestor/main/deploy/example/setting.yaml
```

Pak použijeme objekt TopolvmCluster a v něm definuji filtr na typ zařízení (chci jen nvme0n1, ne třeba temp disky) případně filtr na typ nodu a tak podobně.

```yaml
apiVersion: topolvm.cybozu.com/v2
kind: TopolvmCluster
metadata:
  name: topolvmcluster-sample
  namespace: nativestor-system
spec:
  topolvmVersion: alaudapublic/topolvm:2.0.0
  # certsSecret: mutatingwebhook
  storage:
    useAllNodes: true
    useAllDevices: false
    useLoop: false
    volumeGroupName: "nvme"
    className: "nvme"
    devices:
      - name: "/dev/nvme0n1"
        type: "disk"
```

Na nodech jsem si zkontroloval, že Physical Volume existuje.

```code
root@aks-nodepool1-19673502-vmss000006:/# pvdisplay
  --- Physical volume ---
  PV Name               /dev/nvme0n1
  VG Name               nvme
  PV Size               <1.75 TiB / not usable <4.34 MiB
  Allocatable           yes
  PE Size               4.00 MiB
  Total PE              457854
  Free PE               457598
  Allocated PE          256
  PV UUID               LLkkIs-wguA-Y1JW-kMq8-Nion-ySiH-ewcmyl
```

Nahodil jsem aplikaci a storage class.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: topolvm-provisioner-ssd
provisioner: topolvm.cybozu.com
parameters:
  "csi.storage.k8s.io/fstype": "xfs"
  "topolvm.cybozu.com/device-class": "nvme"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mystatefulset
spec:
  selector:
    matchLabels:
      app: test
  serviceName: test
  replicas: 2
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
      - name: test
        image: ubuntu
        command: ["/bin/bash"]
        args: ["-c", "while true; do date | tee /path/$(date +'%s').txt; sleep 15; done"]
        volumeMounts:
          - mountPath: /path
            name: storage
  volumeClaimTemplates:
  - metadata:
      name: storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: topolvm-provisioner-ssd
      resources:
        requests:
          storage: 1Gi
```

No vida - teprve v ten okamžik se mi vytvoří Persistent Volume v Kubernetu pro tyto dvě instance. Pohledem do nodu zjišťuji, že na něm řešení vytvořilo Logical Volume.

```
root@aks-nodepool1-19673502-vmss000006:/# lvdisplay
  --- Logical volume ---
  LV Path                /dev/nvme/860f2f01-0dc3-484f-bb3b-3268c9b90fd6
  LV Name                860f2f01-0dc3-484f-bb3b-3268c9b90fd6
  VG Name                nvme
  LV UUID                bsde3b-cPgk-6FKc-cyKG-bzZo-uOGJ-CjvnHc
  LV Write Access        read/write
  LV Creation host, time aks-nodepool1-19673502-vmss000006, 2022-02-08 06:57:02 +0000
  LV Status              available
  # open                 1
  LV Size                1.00 GiB
  Current LE             256
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:0
```

Výborně! A dokonce storage limit je pak logicky implementován a to tak jak si to představuji, tedy ve storage - žádné zabíjení procesu apod.

```bash
kubectl exec mystatefulset-0 -ti  -- bash
ls /path
    dd if=/dev/zero of=/path/file1 count=8000 bs=1048576
    dd: error writing '/path/file1': No space left on device
```

Toto řešení má tedy za mě maximum výhod pokud jde o lokální storage. Jestli jsou nevýhody, pak mě napadají tyhle:
- Pořád je to je jen lokální storage - všechny nevýhody v proplachování co jsem popisoval stále platí! Nezapomeňte, že pro statové workloady to možná opravdu pro vás nebude vhodné.
- Máte tu závislost na open source projektech, které sice mají nějaké hvězdičky na GitHubu, ale o nějakém SLA mluvit rozhodně nejde. Je tu potenciáln pro havárie, ztrátu dat, operační problémy, bezpečnostní zranitelnosti. Pro prostředí banky myslím i přes všechny výhody bude lepší pořídit Azure Disk i když ho použijete jen na dočasné věci bez vysokých nároků na redundanci.

Jaké máte s lokální storage v Kubernetu v cloudu zkušenosti vy? Nějaká doporučení, příběhy?