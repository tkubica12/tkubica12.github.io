---
layout: post
published: true
title: Azure Arc pro datové služby aneb cloudová databáze ve vašem vlastním Kubernetes
tags:
- SQL
- PostgreSQL
- Kubernetes
- Arc
---
Jaká je hybridní strategie Microsoftu a o čem je Arc? O tom jsem psal v článku [Pohled na hybridní svět IT nově i s Azure Arc](https://www.tomaskubica.cz/post/2019/pohled-na-hybridni-svet-it-nove-s-azure-arc/) před rokem. Dnes už jsou k dispozici první komponenty řešení a tak se na ně společně podíváme. Začneme tématem myslím velmi zajímavým - datové cloudové služby provozované ve vašem Kubernetes clusteru, tedy Azure Arc for Data Services.

Na rozdíl od Azure Arc for Servers jsou hybridní datové služby v preview a neočekávám, že jsou těsně před spuštěním. Jak uvidíte lze si vyzkoušet základní stavební bloky řešení, ale z pohledu pohodlnosti nasazení a propojení s cloudem v preview většina věcí chybí. Přesto myslím velmi přínosné si vyzkoušet a začít se s konceptem seznamovat, protože očekávám, že třeba tak za půl roku se může řešení dostat do produkčního stádia ... a to uteče jak voda.

# Připomeňme co je Azure Arc for Data Services
Smyslem řešení je nabídnout cloudové datové služby způsobem, kdy běží na Kubernetes clusteru, který jim dáte. Může to být samozřejmě AKS v Azure, ale nedává to moc smysl, když tam je stejná služba jako plný PaaS, tedy se všemi SLA, masivní škálovatelností, více možnostmi včetně globální replikace a bez starání se infrastrukturu a její zabezpečení. Když ale jde o on-premises prostředí, hosting nebo jiný cloud, proč místo tradičního nasazení databáze nevyužít cloudový model? To platí o verzi SQL (kupujete službu, ne nějakou konkrétní verzi - engine je trvale aktuální), automatickém patchování, nafunkování a sfukování výkonu, monitoringu z cloudu i licencování podle aktuálního používání místo nákupu klíčku na 3 roky.

# Aktuální a budoucí způsoby provisioningu a správy
Budoucí stav jsem viděl v jednom demíčku na Ignite konferenci a spočívá v tom, že Kubernetes cluster se do Azure napojí přes Azure Arc for Kubernetes a při vytváření Azure SQL si kromě regionu můžu vybrat svůj on-prem Kubernetes cluster. To pro představu co Arc znamená je naprosto ideální, ale tento režim v rámci preview ještě není.

To co je k vyzkoušení je režim bez přímého napojení, tedy řešení nevyžadující trvalé spojení s Azure. Umím si představit, že i to bude scénář plně validní pro některé zákazníky. Jde tedy o to vytočit příslušné zdroje v Kubernetes, k čemuž je potřeba nainstalovat control plane celého systému Azure for Data services a následně control plane služeb (dnes SQL a PostgreSQL) a ty pak nahodí komponenty samotné databáze. Já v dnešním článku, protože jsem člověk spíš od Kubernetu než od dat, použiji přímé nahození Kubernetes prostředky. Pro dataře je ale možné systém rozjet přímo z datového notebooku v Azure Data Studio případně s využitím příkazové řádky azdata. 

Po vytvoření těmito metodami zatím Azure o vaší databázi nic vědět nebude. Metadata a metriky musíte v rámci preview nahrát do Azure ručně spuštěním CLI příkazu - ale to je mi prozatím jedno, zajímá mě hlavně jak to funguje pod kapotou a do finálního uvedení se tyhle věci jistě vyřeší.

# Instalace kontroleru (přes Kubernetes objekty)
Nejprve musíme založit custom zdroje (CRD), tedy rozšířit Kubernetes API o nové objekty popisující datové služby Azure Arc.

```bash
kubectl create -f https://raw.githubusercontent.com/microsoft/azure_arc/master/arc_data_services/deploy/yaml/custom-resource-definitions.yaml

customresourcedefinition.apiextensions.k8s.io/datacontrollers.arcdata.microsoft.com created
customresourcedefinition.apiextensions.k8s.io/postgresql-11s.arcdata.microsoft.com created
customresourcedefinition.apiextensions.k8s.io/postgresql-12s.arcdata.microsoft.com created
customresourcedefinition.apiextensions.k8s.io/sqlmanagedinstances.sql.arcdata.microsoft.com created
```

Další komponentou, kterou Arc potřebuje je bootstraper. To je jednoduchý Pod, který spusťme v dedikovaném namespace.

```bash
kubectl create namespace arc
kubectl create -n arc -f https://raw.githubusercontent.com/microsoft/azure_arc/master/arc_data_services/deploy/yaml/bootstrapper.yaml

    serviceaccount/sa-mssql-controller created
    role.rbac.authorization.k8s.io/role-bootstrapper created
    rolebinding.rbac.authorization.k8s.io/rb-bootstrapper created
    replicaset.apps/bootstrapper created
```

Dále budeme potřebovat vytvořit jméno a heslo pro kontroler, které uložíme jako Kubernetes Secret.

```bash
printf tomas > ./username
printf Azure12345678 > ./password
kubectl create secret generic controller-login-secret -n arc \
  --from-file=./username \
  --from-file=./password
rm ./username ./password
```

V Azure si připravím resource group.

```bash
az group create -n arc-resources -l westeurope
```

Datový kontroler nahodíme definováním speciálního resource datacontroller. V následujícím YAML budete muset možná změnit pár údajů jako je číslo subskripce nebo název resource group či region. 

```yaml
apiVersion: arcdata.microsoft.com/v1alpha1
kind: datacontroller
metadata:
  generation: 1
  name: arc
spec:
  credentials:
    controllerAdmin: controller-login-secret
    serviceAccount: sa-mssql-controller
  docker:
    imagePullPolicy: Always
    imageTag: public-preview-sep-2020
    registry: mcr.microsoft.com
    repository: arcdata
  security:
    allowDumps: true
    allowNodeMetricsCollection: true
    allowPodMetricsCollection: true
    allowRunAsRoot: false
  services:
  - name: controller
    port: 30080
    serviceType: LoadBalancer
  - name: serviceProxy
    port: 30777
    serviceType: LoadBalancer
  settings:
    ElasticSearch:
      vm.max_map_count: "-1"
    azure:
      connectionMode: Indirect
      location: westeurope
      resourceGroup: arc-resources
      subscription: mojesubscriptionid
    controller:
      displayName: arc
      enableBilling: "True"
      logs.rotation.days: "7"
      logs.rotation.size: "5000"
  storage:
    data:
      accessMode: ReadWriteOnce
      className: default
      size: 15Gi
    logs:
      accessMode: ReadWriteOnce
      className: default
      size: 10Gi
```

Aplikuji YAML a můžeme sledovat, jak se kontroler vytváří s využitím perzistentních volume a StatefulSet.

```bash
kubectl apply -f datacontroller.yaml -n arc
```

Podívejme se, co v Kubernetes vzniklo. Jsou tady Pody, které mají na starost řízení, monitoring a logování celého Azure Arc for Data services.

![](/images/2020/2020-10-12-10-30-30.png){:class="img-fluid"}

Služby jsou nasazeny jako StatefulSet, tedy stavové služby s vysokou dostupností a perzistencí, což poznáme i podle toho, že si řešení vzalo perzistentní Volume z Azure.

![](/images/2020/2020-10-12-10-31-23.png){:class="img-fluid"}

![](/images/2020/2020-10-12-10-31-43.png){:class="img-fluid"}

![](/images/2020/2020-10-12-10-31-57.png){:class="img-fluid"}

Poznamenejme si i vystavené služby, protože na nich najdeme ovládací API i monitoring.

![](/images/2020/2020-10-12-10-45-08.png){:class="img-fluid"}

Kontroler si můžeme připojit do Azure Data Studio.

![](/images/2020/2020-09-30-14-55-08.png){:class="img-fluid"}

![](/images/2020/2020-09-30-15-16-07.png){:class="img-fluid"}

![](/images/2020/2020-09-30-15-16-55.png){:class="img-fluid"}

# SQL Managed Instance v Kubernetes
Kontroler máme připraven, vyzkoušejme si nahodit Microsoft SQL. Můžeme to udělat z Azure Data Studio.

![](/images/2020/2020-09-30-15-17-15.png){:class="img-fluid"}

Já ale znovu použiji přímé nasazení přes Kubernetes objekty. 

Jako Secret si připravím heslo pro svou databázi. 

```bash
printf "tomas" > ./username
printf "Azure12345678" > ./password
kubectl create secret generic tomsql-login-secret -n arc \
  --from-file=./username \
  --from-file=./password
rm ./username ./password
```

Databázová služba je dostupná je speciální typ zdroje sqlmanagedinstance. 

```yaml
apiVersion: sql.arcdata.microsoft.com/v1alpha1
kind: sqlmanagedinstance
metadata:
  name: sql
spec:
  limits:
    memory: 4Gi
    vcores: "4"
  requests:
    memory: 2Gi
    vcores: "2"
  service:
    type: LoadBalancer
  storage:
    backups:
      className: default
      size: 5Gi
    data:
      className: default
      size: 5Gi
    datalogs:
      className: default
      size: 5Gi
    logs:
      className: default
      size: 1Gi
```

```bash
kubectl apply -f sql.yaml -n arc
```

Databázový engine používá StatefulSet.

![](/images/2020/2020-10-12-11-13-28.png){:class="img-fluid"}¨

![](/images/2020/2020-10-12-11-13-51.png){:class="img-fluid"}

Pro perzistenci dat je použit Volume a SQL lze publikovat jako službu ať už interně nebo v mém případě i externě.

![](/images/2020/2020-10-12-11-14-53.png){:class="img-fluid"}

![](/images/2020/2020-10-12-11-15-29.png){:class="img-fluid"}


Také se můžeme na naši SQL Managed Instance podívat v Azure Data Studio.

![](/images/2020/2020-09-30-15-32-05.png){:class="img-fluid"}

![](/images/2020/2020-09-30-15-32-56.png){:class="img-fluid"}

![](/images/2020/2020-09-30-15-33-22.png){:class="img-fluid"}


Logy jsou dostupné zatím přes Grafana, tedy můžete si je prohlédnout i bez Azure. V budoucnu budou automaticky posílány do Azure, kde budete moci celý systém řídit a vizualizovat. 

https://52.236.17.112:30777/grafana

![](/images/2020/2020-09-30-15-27-23.png){:class="img-fluid"}

![](/images/2020/2020-09-30-15-27-40.png){:class="img-fluid"}

Totéž se týká logů, které můžete lokálně prohlížet v Kibana.

https://52.236.17.112:30777/kibana

![](/images/2020/2020-09-30-15-30-14.png){:class="img-fluid"}

# Azure Database for PostgreSQL Hyperscale
Druhou službou v preview Azure Arc for Data services je Azure implementace scale-out PostgreSQL postavená na Citus technologii. Jde tedy o více databázových instancí, které si rozdělý data mezi sebou a přinesou tak vysoký výkon a hlavně škálovatelnost, takže jste schopni vyřešit miliardy řádků nebo podporu multi-tenantní aplikace jako jsou SaaS služby, které chcete svým zákazníkům nabídnout.

Nejprve si opět připravíme heslo do databáze.

```bash
printf "Azure12345678" > ./password
kubectl create secret generic tompsql-login-secret -n arc \
  --from-file=./password
rm ./password
```

Znovu se bude jednat o speciální Custom Resource Definition, které Azure Arc for Data services kontroler porozumí.

```yaml
apiVersion: arcdata.microsoft.com/v1alpha1
kind: postgresql-12
metadata:
  generation: 1
  name: tompsql
spec:
  engine:
    extensions:
    - name: citus
  scale:
    shards: 3
  scheduling:
    default:
      resources:
        limits:
          cpu: "4"
          memory: 4Gi
        requests:
          cpu: "1"
          memory: 2Gi
  service:
    type: LoadBalancer
  storage:
    backups:
      className: default
      size: 5Gi
    data:
      className: default
      size: 5Gi
    logs:
      className: default
      size: 1Gi
```

Pošleme do clusteru.

```bash
kubectl apply -f psql.yaml -n arc
```

Nahodí se StatefulSet a několik instancí databáze s disky.

![](/images/2020/2020-10-12-11-38-03.png){:class="img-fluid"}

![](/images/2020/2020-10-12-11-38-28.png){:class="img-fluid"}

![](/images/2020/2020-10-12-11-39-33.png){:class="img-fluid"}

Koukneme kde služba běží a můžeme se připojit z Azure Data Studio.

![](/images/2020/2020-10-12-11-40-11.png){:class="img-fluid"}

![](/images/2020/2020-09-30-19-15-31.png){:class="img-fluid"}

![](/images/2020/2020-09-30-19-16-18.png){:class="img-fluid"}

![](/images/2020/2020-09-30-19-18-49.png){:class="img-fluid"}

![](/images/2020/2020-09-30-19-19-26.png){:class="img-fluid"}

Případně kouknout na telemetrii v Grafana.

![](/images/2020/2020-09-30-19-23-11.png){:class="img-fluid"}

# Vysoká dostupnost
Všimněte si, že aktuálně řešení nabízí schopnost recovery při havárii, ale je tam určité riziko. Mířím na to, že v preview je databáze v jedné compute instanci a má připojený perzistentní disk. V případě havárie nodu se databáze spustí jinde, data se připojí a engine se znovu rozjede. To samozřejmě nějakou dobu trvá a je tady určitě riziko, že v Kubernetes clusteru nebude dostatečná kapacita pro spuštění Podu někde jinde. Není to pravděpodobné, ale stát se to může. To co jsem si dnes vyzkoušel je zárodek nižší tieru služby - něco jako general purpose.

V plánu je i vyšší varianta služby, která bude používat replikační technologii na úrovni databáze (například AlwaysOn v případě SQL) a půjde tak o tři běžící instance každá se svou kopií dat (shared nothing architektura). Tohle řešení nabídne ještě lepší dostupnost a méně dopadů věcí typu upgrade verze databáze a tak podobně. Tento pokročilejší tier, třeba se bude nazývat business critical, si vyzkoušíme hned jak bude v rámci preview k dispozici.




Azure Arc for Data services je pro mě nesmírně zajímavá služba pro hybridní situace. Stále platí, že databázi je nejlépe komplet přenechat profesionálům, tedy pořídit si jí jako platformní službu v cloudu. Pokud ale skutečně musí běžet u mě, v mé továrně, ropné plošině, v mém kamionu, pobočce, na poli či v lese, stačí mi Kubernetes cluster na to, abych Azure databázové služby rozjel. Vyzkoušet si to v preview se zatím neobroušenými hranami můžete už dnes.