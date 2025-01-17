---
layout: post
title: 'Kubernetes praticky: vývoj a testování s DevSpaces'
tags:
- Kubernetes
---
Používáte architekturu mikroslužeb s Kubernetes? Z pohledu vývoje vás čeká jedna zajímavá výzva. Mikroslužby jsou samostatně nasaditelné jednotky, takže můžu testovat každou zvlášť. Na lokálním PC vývojáře si ten může hrát a před tím, než změnu publikuje, by si měl lokálně sjet základní testy včetně těch, které zavolají jeho API a kontrolují, že to nevrací nesmysly. Ještě lepší varianta mi přijde situace, kdy tyto testy nepřipravuje přímo majitel této mikroslužby, ale naopak její konzumenti. Jako vývojář dané služby si tak mohu u sebe sjet testy připravené mými "zákazníky" (analogie, kdy mikroslužba je vlastně samostatný produkt s životním cyklem mi přijde mentálně dost užitečná), konzumenty.

Jenže ono to nemusí být až tak čisté a jednoduché a občas je určitě dobré vidět svou službu v kontextu ostatních. Napadjí mne tři varianty jak to řešit:
- Postavím si celé prostředí u sebe na notebooku. To je ale dost komplikovaná záležitost. Musím získat verze všech mikroslužeb mých kolegů, přidat stavové služby (např. databáze). Bude pro mě dost náročné to připravit, udržovat a nároky na výkon mého notebooku budou dost vysoké.
- Další varianta je nechat to na CI/CD pipeline a počkat si na nasazení v testovacím prostředí. To ale znamená, že dám commit s nejistým výsledkem. Změn tohoto typu bude u různých služeb hodně a CI/CD pipeline nějakou dobu trvá, takže budu dost nepříjemně dlouho čekat. Navíc se v ní sejdou změny i od ostatních a co když se jejich mikroslužba zrovna rozbila a já tak nedostanu výsledky, které potřebuji.
- Také bychom mohli mít nějaký sdílený dev cluster a v něm rozběhané všechny mikroslužby s tím, že tu na které pracuji si nahradím svým kódem a ještě než udělám commit si ověřím, jak to funguje v kontextu ostatních. Jenže co když tímhle službu rozbiju a způsobím tím potíže kolegům?

Azure DevSpaces tento problém řeší velmi elegantně a vývojářům umožní otestovat si mikroslužbu v kontextu ostatních bez nutnosti stavět všechno na notebooku, bez strachu z rozbití prostředí ostatním a bez nutnosti čekat na CI/CD pipeline. Co tedy umožňují?
- V Dev AKS clusteru se rozjede baseline verze všech služeb, řekněme tedy jejich produkční verze.
- Změním kód své mikroslužby a začlením ji do clusteru tak, že pouze já tyto změny vidím. V clusteru bude baseline verze pro všechny, ale moje requesty budou směrovány na mnou modifikovanou verzi. Zkouším si v kontextu ostatních a přitom jsem jim nic nerozbil, protože jejich prostředí bude směrováno na baseline verzi služby. Tak si může každý pracovat se svými změnami a neovlivňovat celé prostředí.
- DevSpaces pouští můj kód v kontejneru, ve kterém ale běží napojení na debugger. Mohu tedy z Visual Studio nebo VS Code pracovat s breakpointy a hezky si to ladit, aniž bych zastavoval službu ostatním.
- DevSpaces umožňují buildování přímo v AKS. Při změně kódu tedy nemusím jít cestou znovuzabalení do kontejneru, jeho odeslání do registru a přenasazení služby, ale moje změna se pošle přímo do mé verze služby běžící v clusteru. Je to tedy podstatně rychlejší a přináší to lepší produktivitu vývojářů.

# Jak DevSpaces fungují
Nosnou myšlenkou je inteligentní směrování v clusteru na základě headeru. Nasazením baseline mikroslužeb dojde k vytvoření sdíleného root prostoru a public interface (frontend) je zvenku dostupný (kromě toho je možné použít i tunneling na localhost) a to tak, že v URL je název root devspace (např. default). Pokud chci jednu mikroslužbu změnit, vytvořím si nový devspace s tím hlavním v roli rodiče. V ten okamžik na public endpointech vznikne nové URL ve formátu jmenochild.s.jmenoroot.neco. Pokud se připojím na tohle URL, zajistí platforma vstřikování headeru identifikujícího můj child devspace a tento header bude můj kód přeposílat iv rámci volání uvnitř clusteru. Díky této hlavičce DevSpaces ví, co mají s provozem dělat. Pokud pro danou službu neexistuje mnou modifikovaná verze, bude se provoz směrovat do baseline prostoru. Pokud ale tato mikroslužba má mnou modifikovanou verzi, bude se směrovat na ni. Každý devspace tak může mít své vlastní verze vybraných služeb a vzájemně si tak neškodí.

Kromě toho DevSpaces pomáhají vývojářům s přípravou pro provoz v AKS. Generuje se výchozí Dockerfile i Helmová šablona. Můžete ji samozřejmě i změnit, ale pro jednoduché scénáře nemusí vývojáři pronikat do tajů Kubernetes.

Třetí vlastností je schopnost Visual Studio a VS Code kontejner spustit "otevřený" v tom smyslu, že se do běžícího systému napojí. To umožňuje jednoduše připojit debugger a také dochází ke kompilaci přímo v AKS. Změny kódu nebo statického obsahu se tak posílají přímo do kontejneru a jsou rychle k dispozici bez nutnosti jít přes kolečko buildování kontejneru, pushování do repoziotáře a přenasazování.

# Vyzkoušejme si DevSpaces
V prvním kroku budeme používat azds CLI, tedy nepotřebujeme žádnou integraci do IDE. Funkce v této kapitole tak použijí i ti, kteří chtějí kódovat v Notepadu nebo vi.

Nejdřív si musíme nasadit AKS. DevSpaces aktuálně nepodporují některé enterprise funkce jako je RBAC nebo policy, což u Dev clusteru ale nejspíš nevadí, nicméně rozhodně budeme (alespoň dnes) chtít pro DevSpaces dedikovaný Dev cluster.

Celý postup jsem popsal [tady](https://github.com/tkubica12/kubernetes-demo/blob/master/docs/devspaces.md) a zdrojáky aplikace vychází z příkladů v oficiální dokumentaci a mám je uložené [zde](https://github.com/tkubica12/kubernetes-demo/tree/master/devspaces)

Vytvořme si AKS cluster a zapněme DevSpaces.

```bash
az group create --name devspaces --location westeurope
az aks create -g devspaces \
  -n aksdevspaces \
  --location westeurope \
  --disable-rbac \
  -x \
  -c 2 \
  -s Standard_B2ms
az aks use-dev-spaces -g devspaces -n aksdevspaces
```

Teď budeme pracovat s DevSpaces CLI. Skočíme do adresáře frontend a necháme si vygenerovat potřebné soubory - DevSpaces konfiguraci, Dockerfile a Helm charty.

```bash
cd frontend
azds prep --public
azds up -d
```

DevSpaces vytvoří kontejner a napíšou vám public URL, na které náš frontend běží. V mém případě ve formátu názevrootdevspace.služba.něco.weu.azds.io

Otevřu si v browseru a dostávám hlášky z frontend části v AKS a k tomu undefined (protože backend služba ještě neběží).

![](/images/2019/2019-07-29-09-10-01.png){:class="img-fluid"}

Připravíme a nahodíme si backend. Tentokrát u azds prep nepoužiji --public, protože tato služba má být viditelná pouze uvnitř clusteru.

```bash
cd backend
azds prep
azds up -d
```

Jakmile se všechno vytvoří a nasadí, začne mi web vracet zprávu i z backendu.

![](/images/2019/2019-07-29-09-13-22.png){:class="img-fluid"}

Považujme tyto služby za baseline - produkční verze. Pokud by se produkční verze změnila, stačí dát znovu azds up a DevSpaces ji přenasadí. Já ale teď potřebuji modifikovat backend, ale tak, že to ostatním nerozbiju. Založím si tedy child devspace s názvem tomas.

```bash
azds space select --name tomas
```

Jdu do server.js své backend služby a změním zprávu na v2. Následně svůj kód pošlu do clusteru, ale tentokrát ve svém tomas devspace.

```bash
azds up -d
```

Ověřím si, že baseline služby jsou netknuté a stále vrací v1.

![](/images/2019/2019-07-29-09-15-18.png){:class="img-fluid"}

Podívejme se, co se děje v AKS. Backend mám v Kubernetes namespace default i tomas. Nicméně protože jsme zatím přistupovali na root devspace, byli jsme směrování na baseline verzi backendu.

```bash
$ kubectl get pods --all-namespaces
NAMESPACE     NAME                                       READY   STATUS    RESTARTS   AGE
azds          azds-image-prepull-n4dxc                   1/1     Running   0          134m
azds          azds-image-prepull-sqznr                   1/1     Running   0          134m
azds          azds-webhook-deployment-5c47c9f94d-c8sgx   1/1     Running   0          134m
azds          azds-webhook-deployment-5c47c9f94d-wt4n4   1/1     Running   0          134m
azds          tiller-deploy-655f9d988f-rhq7w             1/1     Running   0          134m
azds          traefik-765c5bb9ff-gtr8k                   1/1     Running   0          134m
default       backend-78d5b6bb94-wc4cz                   2/2     Running   0          5m7s
default       frontend-7cdd984b8b-rdqxn                  2/2     Running   0          56m
kube-system   coredns-696c56cf6f-7njr7                   1/1     Running   0          143m
kube-system   coredns-696c56cf6f-ttkpq                   1/1     Running   0          147m
kube-system   coredns-autoscaler-bc55cb685-8mtqq         1/1     Running   0          147m
kube-system   heapster-645c76696d-s2gdt                  2/2     Running   0          143m
kube-system   kube-proxy-c5t2q                           1/1     Running   0          143m
kube-system   kube-proxy-gczvc                           1/1     Running   0          144m
kube-system   kubernetes-dashboard-574465bdbd-swjln      1/1     Running   1          147m
kube-system   metrics-server-5b7d5c6f8d-rnvcc            1/1     Running   0          147m
kube-system   tunnelfront-988596864-2c9cq                1/1     Running   0          147m
tomas         backend-7dd674fb55-jmg78                   2/2     Running   0          54s
```

Jak si jako vývojář prohlédnu svůj devspace? Nejdřív získám URL frontendu.

```bash
azds list-uris
```

Vidím URI ve formátu názevchilddevspace.s.názevrootdevspace.služba.něco.weu.azds.io

Tento web mi vrací zprávu z mnou modifikované verze backendu.

![](/images/2019/2019-07-29-09-23-29.png){:class="img-fluid"}

DevSpace už nepotřebuji? Vymažu.

```bash
azds space remove --name tomas -y
azds space select --name default
```

Služba v default devspace mi běží normálně dál. Nicméně pokud chceme, můžeme všechny poslat dolu.

```bash
azds down
cd ../frontend
azds down
```

# Napojení na prostředí vývojáře
Zatím jsme nevyužívali integraci do IDE. Nejsem vývojář, tak jen naťuknu. Do VS Code nebo Visual Studio si můžeme nainstalovat DevSpaces extension a vygenerovat napojení.

![](/images/2019/2019-07-29-09-28-15.png){:class="img-fluid"}

Tohle nám přidá napojení debuggeru a možnost nastartovat svou mikroslužbu přes F5 tlačítko. Kromě toho vznikne propojení, které nám bude přímo do IDE streamovat logy a pokud provedeme změnu kódu, automaticky ji do AKS natlačí bez nutnosti čekat na celé kolečko redeploy (je to tedy o dost rychlejší než asds up).


Kubernetes samotný je infrastrukturní nástroj, ale díky Azure DevSpaces se rázem stává velmi příjemný, pohodlný a produktivní i pro vývojáře bez nutnosti pronikat do všech tajů tohoto orchestrátoru. A teď považte, že to je všechno v AKS zdarma. Za VS Code neplatíte. Za DevSpaces v Azure taky ne. A dokonce ani za AKS. Platíte jen cenu vašich AKS VM. Nemusíte investovat do nadstaveb nad Kubernetes, stačí ho provozovat v Azure Kubernetes Service a vše je pro vás připraveno. Vyzkoušejte si to.