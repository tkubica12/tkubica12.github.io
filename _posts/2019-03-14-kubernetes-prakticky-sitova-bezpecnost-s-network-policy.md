---
layout: post
status: draft
title: 'Kubernetes prakticky: síťová bezpečnost s Network Policy'
tags:
- Kubernetes
- Networking
---
Otevíráte uvnitř vaší sítě komunikaci jen odkud kam je to potřeba nebo jedete stylem "od vnějšku mě odděluje firewall, tak vevnitř může být klidně všechno se vším, tady si věříme"? Dnešní přístup k bezpečnosti vychází spíše z assume breach, tedy útočník se dříve či později dovnitř dostane. A když už tam je, co ho čeká? Neomezené síťové prostupy, zranitelné procesy běžící pod rootem, hesla uložená v konfiguračních souborech na disku nebo nešifrované protokoly posílající v čitelně podobě ne tokeny s krátkou platností, ale rovnou hesla? No, pak tedy jen doufejte ve štěstí.

Dobře - ale jak zajistit síťové prostupy jen tam kde je to potřeba v éře kontejnerů uvnitř Kubernetes? A jak to udělat způsobem, který nezlikviduje jeden z důvodů, proč kontejnery máte, tedy schopnost plně automatomatizovaného konzistentního nasazování aplikací a infrastruktury z vašeho CI/CD nástroje jako je Azure DevOps? Můžete nasadit service mesh jako je Istio nebo Linkerd 2, které toho dělají spoustu a mimo jiné i izolaci na síťové úrovni. Ale zejména první jmenované Istio je masakr co do složitosti provozu. Pokud ho naplno využijete, hurá do té časové investico do týmu, ale jestli vám jde o síťovou izolaci, je Istio moc velké (mraky nových CRDs, Envoy proxy v každém Podu a s tím spojený overhead, zátěž na management plane, přidaná latence do paketů apod.).

Podívejme se na nativní konstrukt v Kubernetes - Network Policy. Tu je ale třeba podepřít implementací. Do Azure Kubernetes Service právě v preview přichází Azure CNI implementace. S Azure CNI (nebo také pod názvem Advanced Networking) je každý Pod přímo součástí VNETu (má v něm IP) a nově je možné na tuto IP aplikovat filtraci stejnou technikou, jakou to NSG dělá pro síťové karty virtuálních mašin. Tyto funkce jsou implementovány přímo platformou (někdy dokonce ve speciálním FPGA hardware). Je to jednoduché, pro Kubernetes nativní a nemá skoro žádný dopad na výkon či latenci.

# Instalace AKS s podporou Network Policy

Protože je služba v preview a pokud vím zatím nemá tlačítko v GUI, musíme použít příkazovou řádku a před tím si tuto vlastnost zaregistrovat. Proveďte registraci feature, počkejte až bude zaristrována (mě trvalo pár minut) a pak přenačtěte resource providera.

```bash
az feature register --name EnableNetworkPolicy --namespace Microsoft.ContainerService
az feature list -o table --query "[?contains(name, 'Microsoft.ContainerService/EnableNetworkPolicy')].{Name:name,State:properties.state}"
az provider register --namespace Microsoft.ContainerService
```

Vytvořte AKS z příkazové řádky dle dokumentace na webu a použijte přepínač --network-policy azure a --network-plugin azure.

# Testovací prostředí

Pro ukázku síťových politik budu používat následující prostředí. V namespace ns1 postavím webový server a vystrčím na DNS použitím Service. Label identifikují tento server bude app=server. Dále si uděláme testovací stroje ve dvou barvách, které budou v labelu. Třetí testovací Pod s další barvou bude v namespace ns1.

Takhle vypadá můj předpis.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ns1
---
apiVersion: v1
kind: Namespace
metadata:
  name: ns2
---
kind: Pod
apiVersion: v1
metadata:
  name: server
  labels:
    app: server
  namespace: ns1
spec:
  containers:
    - name: nginx
      image: nginx
---
kind: Service
apiVersion: v1
metadata:
  labels:
    app: server
  name: server
  namespace: ns1
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: server
  type: ClusterIP
---
kind: Pod
apiVersion: v1
metadata:
  name: blueclient
  labels:
    color: blue
  namespace: ns1
spec:
  containers:
    - name: tutum
      image: tutum/curl
      command: ["tail"]
      args: ["-f", "/dev/null"]
---
kind: Pod
apiVersion: v1
metadata:
  name: redclient
  labels:
    color: red
  namespace: ns1
spec:
  containers:
    - name: tutum
      image: tutum/curl
      command: ["tail"]
      args: ["-f", "/dev/null"]
---
kind: Pod
apiVersion: v1
metadata:
  name: greenclient
  labels:
    color: green
  namespace: ns2
spec:
  containers:
    - name: tutum
      image: tutum/curl
      command: ["tail"]
      args: ["-f", "/dev/null"]
```

Ověřme si, že z Podů všech barev se můžeme připojit do serveru.

```bash
kubectl apply -f pods.yaml

kubectl exec blueclient -n ns1 -- curl -sI server.ns1 -m10
kubectl exec redclient -n ns1 -- curl -sI server.ns1 -m10
kubectl exec greenclient -n ns2 -- curl -sI server.ns1 -m10
```

# Vyzkoušejme různé politiky

Zatím tedy všichni můžou všude. Network Policy v Kubernetes funguje tak, že pokud žádná neexistuje (tedy k podu není žádná informace), pouští všechno. Jakmile se na něm objeví jakákoli politika, povoluje už jen to, co politika říká. Všimněte si není tady žádný deny, všechny politiky pouze povolují. Prvním naším úkolem tedy bude něco velmi běžného - potřebuji oddělit komunikaci mezi namespace. Mám několik prostorů pro vývoj a ty nechci, aby se viděli a zejména aby mohli komunikovat s testovacím či dokonce produkčním prostředím (pokud je ve stejném clusteru), kde už se dají najít citlivá data.

Síťová politika bude vypadat takhle:

```yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  namespace: ns1
  name: isolate-ns1
spec:
  podSelector:
    matchLabels: {}
  ingress:
  - from:
    - podSelector: {}
```

Co se tam děje? Předně politiku pouštíme pouze do namespace ns1. První součástí politiky je určení toho, na které Pody se bude aplikovat. My podSelector necháme prázdný, tedy aplikuje se na všechny Pody v namespace ns1. 

Politiky jsou dvojího typu. Ingress říká co smí mluvit do Podu, egress pak jakou komunikaci může Pod iniciovat směrem ven (pravidla jsou stavová). My začínáme s ingress. Co teda smí komunikovat s Pody, které jsme vybrali v selektoru? Můžeme si to vybrat podle labelu Podů, podle labelů namespace nebo podle IP rozsahů. Mohli bychom třeba říct, že povolujeme Pody s namespace, které mají nějaký label (třeba všechny namespace patřící do env=prod, pokud bychom je takto značili) nebo konkrétní Pody. My necháme selector from prázdný, takže se vyberou všechny Pody v rámci namespace, do kterého jsme politiku poslali. Čili ještě jednou - namespace je ns1, platnost politiky má prázdný selektor a platí proto na všechny Pody v ns1 a politika povoluje komunikaci z Podů označených prázdným selektorem, tedy ze všech v ns1. Očekáváme tedy, že modrý a červený Pod může na server (protože jsou ve stejném namespace), zatímco zelený Pod ne.

```bash
kubectl apply -f netPolicyIsolateNamespace.yaml

kubectl exec blueclient -n ns1 -- curl -sI server.ns1 -m10
kubectl exec redclient -n ns1 -- curl -sI server.ns1 -m10
kubectl exec greenclient -n ns2 -- curl -sI server.ns1 -m10
```

Funguje! Oddělili jsme namespace od ostatních. Pojďme teď ale přejít ke skutečnému assume breach a nepovolovat ani uvnitř namespace všechno se vším. Začneme tím, že vytvoříme základní politiku, která bude zakazovat jakýkoli ingress. Tedy dokud něco explicitně nepovolíme, všechno bude zakázané.

```yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  namespace: ns1
  name: no-ingress-ns1
spec:
  podSelector:
    matchLabels: {}
  policyTypes:
  - Ingress
```

Vymažeme původní politiku a pošleme tam novou.

```bash
kubectl delete -f netPolicyIsolateNamespace.yaml
kubectl apply -f netPolicyNoIngressWithinNamespace.yaml
```

Co se v politice děje tentokrát? Opět jdeme jen po jednom namespace a znovu máme selektor prázdný, takže se politika aplikuje na všechny Pody v ns1. Jenže tentokrát nemáme žádnou sekci from, tedy nepovolili jsme vůbec žádnou ingress komunikaci. Protože by Kubernetes nepoznal, že cílíme na Ingress (protože tam není sekce from), musíme mu to explictně říct atribute policyTypes.

Ujistíme se, že Pod žádné barvy teď na server komunikovat nemůže.

```bash
kubectl exec blueclient -n ns1 -- curl -sI server.ns1 -m10
kubectl exec redclient -n ns1 -- curl -sI server.ns1 -m10
kubectl exec greenclient -n ns2 -- curl -sI server.ns1 -m10
```

Dobrá, tak jsme zablokovali všechno. Pojďme teď být selektivnější ve výběru toho Podu, který smí se serverem komunikovat. 

Tohle je specifická politika.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: from-blue-only
  namespace: ns1
spec:
  podSelector:
    matchLabels:
      app: server
  ingress:
  - from:
    - podSelector:
        matchLabels:
          color: blue
    ports:
    - protocol: TCP
      port: 80
```

Co se stane? V této politice je selektor app=server, takže se bude aplikovat jen na Pody, které mají tento label (já mám jen jeden). Co smí s Podem mluvit? V sekci from použijeme selektor na color=blue a ještě specifikujeme konkrétní port 80, žádný jiný. Výsledkem bude, že na Pody s labelem app=server mohou přistupovat pouze Pody s labelem color=blue a to pouze na TCP portu 80. Vyzkoušejme si to.

```bash
kubectl apply -f netPolicyBlue.yaml

kubectl exec blueclient -n ns1 -- curl -sI server.ns1 -m10
kubectl exec redclient -n ns1 -- curl -sI server.ns1 -m10
kubectl exec greenclient -n ns2 -- curl -sI server.ns1 -m10
```

Dle očekávání modrý prochází, ostatní ne.

Kromě ingress pravidel můžeme použít i egress. Nejprve se ujistěme, že modrý i červený Pod se dostane na www.microsoft.com a to jak po http (80) tak přes https (443).

```bash
kubectl exec blueclient -n ns1 -- curl -sI http://www.microsoft.com -m10
kubectl exec blueclient -n ns1 -- curl -sI https://www.microsoft.com -m10
kubectl exec redclient -n ns1 -- curl -sI http://www.microsoft.com -m10
kubectl exec redclient -n ns1 -- curl -sI https://www.microsoft.com -m10
```

Všechno prochází. Možná mám ale potřebu omezit Podům možnost komunikovat ven tam, kde k tomu není žádný důvod. Kontejnerový obraz obsahuje to co potřebuji a v tomto světě se neupgraduje běžíí kontejner, ale vytvoří se místo něj jiný. Jinak řečeno u kontejneru obvykle nepotřebuji, aby měl přístup do Internetu a stahoval si odtamtud nějaké aktualizace. Pokud by se útočník Podu zmocnil, může si posílat data ven někam na svoje FTP apod. a proč to nechat otevřené, když to není potřeba? Můžeme tedy definovat egress a omezit protokoly nebo IP rozsahy, na které chceme Podu dovolit komunikovat.

Moje politika vypadá takhle:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: red-egress
  namespace: ns1
spec:
  podSelector:
    matchLabels:
      color: red
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
    ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
    - port: 443
      protocol: TCP
```

Pro červené pody dovoluji DNS komunikaci (na tu nezapomeňte, bez ní se skoro nic neobejde), povoluji port 443 (https) a to na cokoli (nicméně můj cidr může zahrnovat pouze nějakou součást VNETu, on-premises stroje za VPNkou apod.). Vyzkoušejme si.

```bash
kubectl apply -f netPolicyRedEgress443only.yaml

kubectl exec blueclient -n ns1 -- curl -sI http://www.microsoft.com -m10
kubectl exec blueclient -n ns1 -- curl -sI https://www.microsoft.com -m10
kubectl exec redclient -n ns1 -- curl -sI http://www.microsoft.com -m10
kubectl exec redclient -n ns1 -- curl -sI https://www.microsoft.com -m10
```

Výsledek? Modrým to prochází v pohodě, protože na ně jsme žádnou egress politiku dosud neaplikovali. A červení? http nefunguje, https ano, tedy přesně podle očekávání.


Osobně doporučuji držet se pravidel nejmenšího možného oprávnění a předpokládání průniku. Pokud se k vám útočník dostane, ať to nemá lehké a správné interní omezení sítě je důležitou součástí celé strategie. Důležité je, že je pro vás díky AKS implementaci k dispozici. Pro ovládání a nastavování můžete využít konstruktů, které jsou pro Kubernetes zásadní jako jsou labely. Dokážete tak politiky udržovat (nemusíte uvádět IP adresy) a nasazovat současně s ostatními zdroji Kubernetes. Navíc pro tento účel vám postačí Network Policy, která je jednoduchý a nativní prostředek s přímo cloudem řešenou implementací pro nízkou latenci, jednoduchost a malý overhead. Přestože Istio nebo Linkerd 2 jsou skvělé, zvažte jestli jít komplexity takového šelmostroje, když možná hledáte jen network policy.