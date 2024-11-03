---
layout: post
published: true
title: Kubernetes pro velká data a strojové učení - proč AzureML nebo Apache Spark používá projekt Volcano?
tags:
- AI
- Kubernetes
---
Pokud ze světa infrastruktury a kontejnerů jako já nakouknete přes řeku k borcům od zpracování dat a strojového učení nejde se nevšimnout, že si tam hrají s virtuálkama, nad které si dávají Spark, Hadoop a podobné nástroje, které jim mají umožňit nahazovat jednotlivé úkoly nad takto spravovanou infrastrukturou. Mezitím svět aplikací vyhlásil vítěze kontejnerových válek a Kubernetes už je dnes tak normální, že je z něj nuda, která na anarchstický večírek už rozhodně nepatří. Jsou dataři zabetonovaní ve svém nebo tenhle Kubernetes zásadně ovlivňuje i jejich oblast? Evidentně ano, protože například projekty Apache Spark nebo AzureML dnes umí efektivně využívat Kubernetes jako podklad pro to, co dělají. Jen je museli trochu vylepšit. Jak to dělají a proč? Vyzkoušejme.

# Nehrab se v tom, jdi do managed
Kubernetes začíná být něco jako myčka nádobí. Někomu nadšeně říkat, že už jí taky máte asi neohromí. Jasně - jsou situace, kdy jsou lidé bez ní, třeba na horské chatě, z nějakého přesvědčení, z neochoty udělat změnu, v chudých poměrech nebo extrémních podmínkách. Nicméně začíná platit, že to má prakticky každý a vymýšlet svoje vlastní postupy na mytí nádobí asi nemá smysl a vlastně už ani snažit se postavit standardní myčku z komponent vlastními silami. Prostě sáhnete třeba do Azure a bum, je tam a jmenuje se Azure Kubernetes Service. Nicméně cílem je se najíst a k tomu je potřeba čisté nádobí, ne ladit jak mám mít myčku velkou, jaký program podle typu znečištění zvolit, jaké přípravky používat. Ještě lepší je se tedy soustředit na "core byznys" (tedy se najíst) a mytí mít celé jako službu, tedy použít Azure Container Apps. Pod kapotou je myčka (AKS) a pár dalších komponent (networking, škálovadlo, aplikační platforma, monitoring), ale to mi je celkem jedno - já se soustředím na to důležité, jídlo.

Stejným způsobem bych nahlížel na platformu pro trénování a využívání modelů strojového učení nebo pro přípravu, analýzu a úpravu dat. AzureML stejně jako Synapse mi připraví managed prostředky a já se soustředím na jídlo. Nicméně mohou být situace, kdy by nějaká znalost podkladové technologie a Kubernetes mohl být užitečný a to je v případě, že musím z nějakého důvodu mít hybridní řešení přes víc cloudů nebo přes cloud a on-prem nebo něco mít na edge apod. V takový moment dává smysl dát do všech těchto míst nějakou standardní myčku (Kubernetes) a nechat můj řídící systém, tedy v mém případě Azure ML, využívat myčky v jakémkoli prostředí jakéhokoli výrobce.

# Volcano jako nadstavba nad Kubernetes - proč ji potřebujeme
Kubernetes je v základu skvěle připravený na provozování mikroslužeb i stavových workloadů díky vlastnostem jako jsou Deployment, Statefulset, Horizontal Pod Autoscaler, ale jeho nabídka pro "run to completion" typy úloh je poměrně omezená. Ano, má koncept Job, ale to je víceméně všechno - není moc dobře vyladěn na dávkové spracování typické pro spouštění úloh patřící různým datovým procesům ať už je to zpracování dat nebo trénování. Je to znát zejména pokud má cluster sloužit pro víc jak jeden tým a model, což je ale obvykle žádoucí pro schopnost lépe využít zdroje. V památných kontejnerových válkách byla jedna ze stran reprezentována Apache Mesos (posléze DC/OS od Mesosphere), což byl dvou-úrovňový scheduler optimalizovaný na souběžný běh mikroslužeb i Big Data úloh (tenkrát hlavně Hadoop). Byl inspirovaný klasickým Google Borg schedulerem a v roce 2010 ho proslavilo použití v Twitteru, nicméně od roku 2015 je značně na ústupu. Vyhrála cesta jednodušší, přístupnější pro vývojáře a taková, která se poučila z mnoha chyb předchůdců a udělala například networking konečně správně - Kubernetes.

Co přidává projekt Volcano nad běžný Kubernetes? Tak například plánování Jobů v Kubernetu je "férové" napříč vlastně vším, ale to je problém. Tak například potřebujete přiřadit Jobu nějaké SLA postavené na maximální době čekání ve frontě. Představte si, že máte Joby, které mají pro vás stejnou prioritu, ale jedny jsou malé (co do nároků na zdroje) a druhé velké. Jdete na to férově, tak kouknete na první balík a fajn, pouštíte. Pak zkusíme třeba nějaký velký ale ouha, nevejde se nám do clusteru. Nevadí, pojďme na jiný a hele, tenhle malý by se vešel. Ve finále tak větší Job má daleko menší šanci se dostat ke slovu. Potřebujeme spíše, aby pokud už tam čeká moc dlouho dostal vyšší prioritu. Ale jen za takových okolností, protože nechceme dát obecně větší prioritu většímu Jobu, to zas nikdy nespustíme ty malé. A teď si představme, že Joby se nejlépe dělají paraleleně, což je typické pro mnoho úloh v datové oblasti. Čím víc instancí, tím líp. Příliš málo je ale problém. Potřebujeme tedy říct, že Job má mít minimum 5 replik, ale pokud bude místo, tak klidně 10. HPA pro dlouho běžící workloady něco podobného dělá, ale tady mluvíme o Jobech a navíc potřebujeme i schopnost preemption těch, co jsou "navíc", tedy musíme situaci přebalancovat. Celé to vede na to, že pro plánovač potřebujeme spouštět na základě kombinace fair-share, ale i podle namespace, vytvořit koncept front a nasazování v rámci fronty a taky vyřešit cross-queue scheduling. A do toho obvykle ještě vletí potřeba hierarchického frontování.

Při nasazování je v datové oblasti často důležitá topologie. Musíme vzít v úvahu například NUMA, tedy aby core přidelený Podu využíval paměť, která je přímo napojená na tento socket (dvou-socketové systémy mají dva procesory a dvě paměťové banky, ale jeden virtuální paměťový prostor - jenže pokud proces v socket 1 přistupuje k paměťové bance u socket 2, tak to jde přes inter-procesorovou sběrnici a je to pomalejší). Často je u úlohy nějaká hlava a k tomu workery a výkonnostně dává smysl, aby oboje bylo na stejném node, takže scheduler by měl efektivně využít přidělené nody, ale k nějakému počtu workerů na node vždy přihodit i hlavu. 

Volcano přímo podporuje některé datové frameworky, tak například je optimalizované pro Spark, kdy chápe co se po něm chce (v kombinaci se Spark Operator) a nedovolí, aby například vznikl Spark driver Pod řešící Spark Job, který se ale skládá s vícero task rolí a pro executor Pod už nezbyde místo, takže to celé bylo zbytečné. Volcano si rezervuje prostor tak, aby Spark dobře běžel, tedy má znalosti Sparku jako takového. Podobně je přímo připraven na TensorFlow (strojové učení) nebo MPI (High Performance Computing).

Nedávno Apache Spark oznámil, že od verze 3.3 je Volcano jejich výchozí scheduler na Kubernetu. Azure Machine Learning zas před časem oznámilo, že na Kubernetes clusterech už umí nejen inferencing, ale i training, a to i na clusterech mimo Azure - díky napojení přes Azure Arc můžete Azure ML využívat tak, že jednotlivé úlohy běží na vašem vlastním clusteru kdekoli.

# Nakoukněme co pod kapotou Azure ML s Kubernetes dělá
Nejdřív si vytvořím AzureML workspace, AKS cluster a zapnu audit logování, ať se můžeme podívat, jak do toho AzureML buší. Následně použijeme extension k přidání AzureML komponent do clusteru - v mém příkladu je to AKS, ale funguje to i s libovolným clusterem v on-prem nebo jiném cloudu (například OpenShift, Rancher, Tanzu, AKS on Azure Stack HCI, GKE, EKS) přes Azure Arc.

```bash
# Create Resource Group
az group create -n azureml -l westeurope

# Create Azure ML Workspace
az ml workspace create -n azureml -g azureml -l westeurope

# Create Log Analytics Workspace
az monitor log-analytics workspace create -n tomaskubicaaml12 -g azureml

# Create AKS
az aks create -n azuremlaks -c 3 -x -g azureml

# Enable audit logging (so we can see what AzureML is doing exactly)
az monitor diagnostic-settings create -n logs \
   --resource $(az aks show -n azuremlaks -g azureml --query id -o tsv) \
   --workspace $(az monitor log-analytics workspace show -n tomaskubicaaml12 -g azureml --query id -o tsv) \
   --logs '[
     {
       "category": "kube-audit-admin",
       "enabled": true,
       "retentionPolicy": {
         "enabled": false,
         "days": 0
       }
     }
   ]'

# Deploy AzureML extension
az k8s-extension create -n tomaskubicaaml \
    --extension-type Microsoft.AzureML.Kubernetes \
    --config enableTraining=True enableInference=True inferenceRouterServiceType=LoadBalancer allowInsecureConnections=True inferenceLoadBalancerHA=False \
    --cluster-type managedClusters \
    --cluster-name azuremlaks \
    -g azureml \
    --scope cluster

# Get AKS credentials
az aks get-credentials -n azuremlaks -g azureml
```

Podívejme co extension nasadila.

```bash
# What resources got AzureML extension deployed?
kubectl get pods -n azureml

NAME                                                     READY   STATUS      RESTARTS        AGE
aml-operator-6676d6c959-8kmcj                            1/1     Running     0               2m23s
amlarc-identity-controller-95d7cb964-d2lbj               1/1     Running     0               2m23s
amlarc-identity-proxy-597b94d56-j4mqx                    1/1     Running     0               2m22s
azureml-fe-v2-b8c86749f-4gfbw                            3/3     Running     0               2m23s
azureml-ingress-nginx-controller-5996df8ddd-rtkzl        1/1     Running     0               2m22s
cluster-status-reporter-55f9f744dd-jc5fp                 1/1     Running     0               2m22s
fluent-bit-dfhwl                                         1/1     Running     0               2m23s
fluent-bit-gnpz5                                         1/1     Running     0               2m23s
fluent-bit-vq72l                                         1/1     Running     0               2m23s
gateway-7b58dc99cd-c6c4s                                 1/1     Running     0               2m22s
healthcheck                                              0/1     Completed   0               3m15s
inference-operator-controller-manager-56d97d6445-8spg9   1/1     Running     1 (2m13s ago)   2m23s
metrics-controller-manager-794b997d78-872lm              1/1     Running     0               2m23s
prometheus-prom-prometheus-0                             2/2     Running     0               2m10s
relayserver-6995b6594d-2f4km                             1/1     Running     0               2m23s
relayserver-6995b6594d-t5zrj                             1/1     Running     0               2m23s
tomaskubicaaml-kube-state-metrics-785d98c5d5-dfbqc       1/1     Running     0               2m23s
tomaskubicaaml-prometheus-operator-6c978c7968-prsvl      1/1     Running     0               2m22s
volcano-admission-74f559c556-5l9np                       1/1     Running     0               2m23s
volcano-controllers-56894dd996-fl5qx                     1/1     Running     0               2m23s
volcano-scheduler-774bd78f4-cgsm4                        1/1     Running     0               2m23s
```

Vidím tam Volcano a monitoring nástroje a agenty (Prometheus, FluentBit). Dále je tam Azure ML operátor, který bude asi hlavní způsob přijímání požadavků z Azure ML a bude nahazovat Volcano zdroje, ale taky hotové modely přes Inference Operator. Další komponenta je síťařina - Ingress kontroler, primárně pro inferencing (vystavení modelů přes API). Zajímavá je gateway, což je evidentně API pro příjem zadání z Azure ML a Relay Server, což funguje v kombinaci s Azure Relay Service a tzv. Hybrid Connections. Díky tomu může AzureML komunikovat s clusterem aniž by se do něj muselo na firewallu otvírat nějaké inbound spojení. 

Počítám, že máme pár nových Custom Resource Definition.

```bash
# What Custom Resource Definitions are now in cluster?
kubectl get crds

NAME                                             CREATED AT
alertmanagerconfigs.monitoring.coreos.com        2022-07-12T05:51:00Z
alertmanagers.monitoring.coreos.com              2022-07-12T05:51:00Z
amljobs.amlarc.azureml.com                       2022-07-12T05:52:54Z
commands.bus.volcano.sh                          2022-07-12T05:52:54Z
extensionconfigs.clusterconfig.azure.com         2022-07-12T05:49:29Z
identities.amlarc.azureml.com                    2022-07-12T05:52:54Z
instancetypes.amlarc.azureml.com                 2022-07-12T05:52:54Z
jobs.batch.volcano.sh                            2022-07-12T05:52:54Z
metrics.amlarc.azureml.com                       2022-07-12T05:52:54Z
numatopologies.nodeinfo.volcano.sh               2022-07-12T05:52:54Z
onlinedeployments.amlarc.azureml.com             2022-07-12T05:52:54Z
onlineendpoints.amlarc.azureml.com               2022-07-12T05:52:54Z
podgroups.scheduling.volcano.sh                  2022-07-12T05:52:54Z
podmonitors.monitoring.coreos.com                2022-07-12T05:51:00Z
probes.monitoring.coreos.com                     2022-07-12T05:51:00Z
prometheuses.monitoring.coreos.com               2022-07-12T05:51:01Z
prometheusrules.monitoring.coreos.com            2022-07-12T05:51:00Z
queues.scheduling.volcano.sh                     2022-07-12T05:52:54Z
servicemonitors.monitoring.coreos.com            2022-07-12T05:51:00Z
thanosrulers.monitoring.coreos.com               2022-07-12T05:51:00Z
volumesnapshotclasses.snapshot.storage.k8s.io    2022-07-12T05:37:46Z
volumesnapshotcontents.snapshot.storage.k8s.io   2022-07-12T05:37:46Z
volumesnapshots.snapshot.storage.k8s.io          2022-07-12T05:37:46Z
```

AML Job, Volcano Job, Pod Groups, Queues ... vypadá to dobře.

Skvělé - připojím cluster.

```bash
# Create namespace for azureml workloads
kubectl create ns azureml-workloads

# Attach this cluster to Azure ML workspace
az ml compute attach -n k8s-compute \
  -g azureml \
  --workspace-name azureml \
  --type Kubernetes  \
  --resource-id $(az aks show -n azuremlaks -g azureml --query id -o tsv) \
  --identity-type SystemAssigned \
  --namespace azureml-workloads
```

V Azure ML teď půjdu do pipeline a vyberu si nějaký zabudovaný příklad.

[![](/images/2022/2022-07-12-11-40-17.png){:class="img-fluid"}](/images/2022/2022-07-12-11-40-17.png)

Compute namířím na připojený cluster.

[![](/images/2022/2022-07-12-11-40-33.png){:class="img-fluid"}](/images/2022/2022-07-12-11-40-33.png)

A pipeline spustím.

[![](/images/2022/2022-07-12-11-40-50.png){:class="img-fluid"}](/images/2022/2022-07-12-11-40-50.png)

Co se dělo? Udělal jsem si v Log Analytics query, kterým se podívám na pár zajímavých Create událostí v Kubernetu.

```bash
# Query audit logs
az monitor log-analytics query -w $(az monitor log-analytics workspace show -n tomaskubicaaml12 -g azureml --query customerId -o tsv) \
  -o table --analytics-query 'AzureDiagnostics 
  | where Category == "kube-audit-admin"
  | where log_s has "\"verb\":\"create\""
  | project TimeGenerated, parse_json(log_s)
  | project TimeGenerated, verb = log_s.verb, resource = log_s.objectRef.resource, name = log_s.objectRef.name
  | where resource !in ("subjectaccessreviews","storageclasses", "tokenreviews", "selfsubjectaccessreviews")
  | sort by TimeGenerated' > audit-logs.txt

TableName      TimeGenerated         Name                                                                     Resource                         Verb
-------------  --------------------  -----------------------------------------------------------------------  -------------------------------  ------
PrimaryResult  2022-07-12T06:37:52Z  generic-garbage-collector                                                serviceaccounts                  create
PrimaryResult  2022-07-12T06:37:52Z  resourcequota-controller                                                 serviceaccounts                  create
PrimaryResult  2022-07-12T06:35:40Z  amljobcontroller                                                         serviceaccounts                  create
PrimaryResult  2022-07-12T06:35:40Z  azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0              pods                             create
PrimaryResult  2022-07-12T06:35:39Z  amljobcontroller                                                         serviceaccounts                  create
PrimaryResult  2022-07-12T06:35:38Z  None                                                                     endpointslices                   create
PrimaryResult  2022-07-12T06:35:38Z  amlarcjob-8b2821ccdc9c9fb818502c0e69b96572                               metrics                          create
PrimaryResult  2022-07-12T06:35:38Z  azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572                       jobs                             create
PrimaryResult  2022-07-12T06:35:38Z  azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572                       networkpolicies                  create
PrimaryResult  2022-07-12T06:35:38Z  azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572                       services                         create
PrimaryResult  2022-07-12T06:35:38Z  azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh                   secrets                          create
PrimaryResult  2022-07-12T06:35:38Z  azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572                       endpoints                        create
PrimaryResult  2022-07-12T06:35:38Z  azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc                   configmaps                       create
PrimaryResult  2022-07-12T06:35:38Z  azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572                       podgroups                        create
PrimaryResult  2022-07-12T06:35:37Z  prometheus-prom-prometheus-0                                             pods                             create
PrimaryResult  2022-07-12T06:35:37Z  prom-prometheus                                                          serviceaccounts                  create
PrimaryResult  2022-07-12T06:35:37Z  prometheus-prom-prometheus-0.1701017457cc70da                            events                           create
PrimaryResult  2022-07-12T06:35:37Z  azureml-workloads-72888029582f8ccfc5724be3e41a13da-worker-0              pods                             create
PrimaryResult  2022-07-12T06:35:37Z  prometheus-prom-prometheus-0                                             pods                             create
PrimaryResult  2022-07-12T06:35:36Z  8b2821ccdc9c9fb818502c0e69b96572-imagepull-0-secrets                     secrets                          create
PrimaryResult  2022-07-12T06:35:36Z  8b2821ccdc9c9fb818502c0e69b96572-lifecycle                               configmaps                       create
PrimaryResult  2022-07-12T06:35:36Z  8b2821ccdc9c9fb818502c0e69b96572-ssh-keys                                secrets                          create
PrimaryResult  2022-07-12T06:35:36Z  8b2821ccdc9c9fb818502c0e69b96572                                         configmaps                       create
PrimaryResult  2022-07-12T06:35:36Z  8b2821ccdc9c9fb818502c0e69b96572-runtoken-secrets                        secrets                          create
PrimaryResult  2022-07-12T06:35:36Z  1cfc74aae33346e9b77672f82ab26790-viennaglobal.azurecr.io                 secrets                          create
PrimaryResult  2022-07-12T06:35:35Z  azureml-workloads-72888029582f8ccfc5724be3e41a13da                       jobs                             create
PrimaryResult  2022-07-12T06:35:35Z  None                                                                     endpointslices                   create
PrimaryResult  2022-07-12T06:35:35Z  azureml-workloads-72888029582f8ccfc5724be3e41a13da                       endpoints                        create
PrimaryResult  2022-07-12T06:35:35Z  azureml-workloads-72888029582f8ccfc5724be3e41a13da-ssh                   secrets                          create
PrimaryResult  2022-07-12T06:35:35Z  prometheus-prom-prometheus-5df95b4d54                                    controllerrevisions              create
PrimaryResult  2022-07-12T06:35:35Z  azureml-workloads-72888029582f8ccfc5724be3e41a13da                       networkpolicies                  create
PrimaryResult  2022-07-12T06:35:35Z  metrics-token                                                            secrets                          create
PrimaryResult  2022-07-12T06:35:35Z  azureml-workloads-72888029582f8ccfc5724be3e41a13da-svc                   configmaps                       create
PrimaryResult  2022-07-12T06:35:35Z  amlarcjob-72888029582f8ccfc5724be3e41a13da                               metrics                          create
PrimaryResult  2022-07-12T06:35:35Z  azureml-workloads-72888029582f8ccfc5724be3e41a13da                       podgroups                        create
PrimaryResult  2022-07-12T06:35:35Z  azureml-workloads-72888029582f8ccfc5724be3e41a13da                       services                         create
PrimaryResult  2022-07-12T06:35:33Z  72888029582f8ccfc5724be3e41a13da-runtoken-secrets                        secrets                          create
PrimaryResult  2022-07-12T06:35:33Z  72888029582f8ccfc5724be3e41a13da-imagepull-0-secrets                     secrets                          create
PrimaryResult  2022-07-12T06:35:33Z  72f05b4a9d3446e49a93eb6b8e6254c2-viennaglobal.azurecr.io                 secrets                          create
PrimaryResult  2022-07-12T06:35:33Z  72888029582f8ccfc5724be3e41a13da-ssh-keys                                secrets                          create
PrimaryResult  2022-07-12T06:35:33Z  72888029582f8ccfc5724be3e41a13da                                         configmaps                       create
PrimaryResult  2022-07-12T06:35:33Z  72888029582f8ccfc5724be3e41a13da-lifecycle                               configmaps                       create
PrimaryResult  2022-07-12T06:35:16Z  default                                                                  serviceaccounts                  create
PrimaryResult  2022-07-12T06:35:16Z  crbs-stable-356aea83-deployment-6bb9657b9f-gn847.1701016f8cd53f8d        events                           create
PrimaryResult  2022-07-12T06:35:16Z  crbs-stable-356aea83-deployment-6bb9657b9f-gn847                         pods                             create
PrimaryResult  2022-07-12T06:35:16Z  amljobcontroller-token-hvhwv                                             secrets                          create
PrimaryResult  2022-07-12T06:35:16Z  72888029582f8ccfc5724be3e41a13da                                         amljobs                          create
PrimaryResult  2022-07-12T06:35:16Z  amljobcontroller                                                         serviceaccounts                  create
```

Zajímavé. Vytváří se objekty tříd amljob, následně to AML operátor nahazuje do Volcano a přidává podgroups a následně z nich nahazuje Pody pro jednotlivé kroky mojí pipeline.

Koukám na definici amljob.


```yaml
apiVersion: amlarc.azureml.com/v1alpha1
kind: AmlJob
metadata:
  creationTimestamp: "2022-07-12T06:35:16Z"
  generation: 1
  name: 72888029582f8ccfc5724be3e41a13da
  namespace: azureml-workloads
  resourceVersion: "25364"
  uid: b41d8fe4-2d5d-45f4-9fb0-d0b5d10461ce
spec:
  job:
    jobId: 72888029582f8ccfc5724be3e41a13da
    name: 72888029582f8ccfc5724be3e41a13da
    options:
      commonRuntimeJobSpec: 
      ...
```

Je tam toho strašně moc - commonRuntimeJobSpec je base64, tak ho rozkóduju:

```json
{
    "version": "2",
    "spec": {
        "name": "927f61e0-8999-4082-a685-d0c0a02b466e",
        "execution": {
            "container": {
                "image": {
                    "fully_qualified_name": "mcr.microsoft.com/azureml/curated/designer:42",
                    "registry_url": "mcr.microsoft.com"
                },
                "shm_size": "2g",
                "cap_add": [],
                "ulimit": [],
                "device": [],
                "env": [],
                "volume": []
            },
            "environment_variables": {
                "EXAMPLE_ENV_VAR": "EXAMPLE_VALUE",
                "AZUREML_PARAMETER_Node_Count": "1",
                "AZUREML_PARAMETER_Solution_method": "Ordinary Least Squares",
                "AZUREML_PARAMETER_Create_trainer_mode": "SingleParameter",
                "AZUREML_PARAMETER_Learning_rate": "0.1",
                "AZUREML_PARAMETER_Number_of_epochs_over_which_algorithm_iterates_through_examples": "10",
                "AZUREML_PARAMETER_L2_regularization_term_weight": "0.001",
                "AZUREML_PARAMETER_Range_for_learning_rate": "0.025; 0.05; 0.1; 0.2",
                "AZUREML_PARAMETER_Range_for_number_of_epochs_over_which_algorithm_iterates_through_examples": "1; 10; 100",
                "AZUREML_PARAMETER_Range_for_L2_regularization_term_weight": "0.001; 0.01; 0.1",
                "AZUREML_PARAMETER_Should_input_instances_be_normalized": "True",
                "AZUREML_PARAMETER_Decrease_learning_rate_as_iterations_progress": "True",
                "AZUREML_PARAMETER_L2_regularization_weight": "0.001",
                "AZUREML_PARAMETER_Include_intercept_term": "True",
                "AZUREML_PARAMETER_Random_number_seed": "",
                "MLFLOW_EXPERIMENT_ID": "e4360b71-5ba4-4789-8e0c-ab040462cc06",
                "MLFLOW_EXPERIMENT_NAME": "tomasexperiment",
                "MLFLOW_RUN_ID": "927f61e0-8999-4082-a685-d0c0a02b466e",
                "MLFLOW_TRACKING_URI": "azureml://westeurope.api.azureml.ms/mlflow/v1.0/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml",
                "MLFLOW_TRACKING_TOKEN": "eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw",
                "DATASET_MOUNT_BLOCK_BASED_CACHE_ENABLED": "true",
                "DATASET_RSLEX_UPLOAD": "true",
                "AZUREML_DATASET_FILE_OUTPUTS": "Untrained_model"
            },
            "phases": [
                {
                    "coordinated_start": false,
                    "nodes": [
                        0
                    ],
                    "commands": {
                        "command": {
                            "executable": {
                                "type": "Spawn",
                                "success_return_code": {
                                    "zero": {}
                                },
                                "program": "/azureml-envs/azureml_64165a26e38451d868d732a63dec2783/bin/python",
                                "args": [
                                    "-u",
                                    "-c",
                                    "\nimport json\nimport os\nimport os.path\nimport runpy\nimport sys\nimport traceback\n\nclass NoopContextManager:\n    def __enter__(self):\n        pass\n\n    def __exit__(self, *args, **kwargs):\n        pass\n\nclass ErrorHandlerContextManager:\n    def __init__(self, inner_cm):\n        self.inner_cm = inner_cm\n\n    def __enter__(self):\n        return ErrorHandlerContextManager.do_op_and_write_error(lambda: self.inner_cm.__enter__(), 'UserExecution.context_manager.enter')\n\n    def __exit__(self, exc_type, exc_value, traceback):\n        if exc_value:\n            write_error('UserExecution.script', 'UserError', exc_value, 'NonCompliant')\n        return ErrorHandlerContextManager.do_op_and_write_error(lambda: self.inner_cm.__exit__(exc_type, exc_value, traceback), 'UserExecution.context_manager.exit')\n\n    @staticmethod\n    def do_op_and_write_error(op, error_code):\n        try:\n            return op()\n        except Exception as e:\n            write_error(error_code, 'SystemError', e, 'Compliant')\n            raise\n\ndef write_error(code, category, error, compliant):\n    try:\n        error_path = os.environ.get('_AZUREML_CR_ERROR_JSON_FILE')\n        dir = os.path.dirname(error_path)\n        os.makedirs(dir, exist_ok=True)\n        with open(error_path, 'x') as f:\n            f.write(json.dumps(to_cr_error(code, category, error, compliant)))\n    except:\n        pass\n\ndef to_cr_error(code, category, error, compliant):\n    known_errors = [\n        'BaseException', 'SystemExit', 'KeyboardInterrupt', 'GeneratorExit', 'Exception', 'StopIteration', 'StopAsyncIteration',\n        'ArithmeticError', 'FloatingPointError', 'OverflowError', 'ZeroDivisionError', 'AssertionError', 'AttributeError',\n        'BufferError', 'EOFError', 'ImportError', 'ModuleNotFoundError', 'LookupError', 'IndexError', 'KeyError', 'MemoryError',\n        'NameError', 'UnboundLocalError', 'OSError', 'BlockingIOError', 'ChildProcessError', 'ConnectionError', 'BrokenPipeError',\n        'ConnectionAbortedError', 'ConnectionRefusedError', 'ConnectionResetError', 'FileExistsError', 'FileNotFoundError',\n        'InterruptedError', 'IsADirectoryError', 'NotADirectoryError', 'PermissionError', 'ProcessLookupError', 'TimeoutError',\n        'ReferenceError', 'RuntimeError', 'NotImplementedError', 'RecursionError', 'SyntaxError', 'IndentationError', 'TabError',\n        'SystemError', 'TypeError', 'ValueError', 'UnicodeError', 'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeTranslateError',\n        'Warning', 'DeprecationWarning', 'PendingDeprecationWarning', 'RuntimeWarning', 'SyntaxWarning', 'UserWarning',\n        'FutureWarning', 'ImportWarning', 'UnicodeWarning', 'BytesWarning', 'EncodingWarning', 'ResourceWarning', 'IOError',\n        'EnvironmentError'\n    ]\n    exc_type, exc_val, exc_traceback = sys.exc_info()\n    stack_trace = ''.join(strip_stack_of_azureml_layers(exc_type, exc_val, exc_traceback))\n    exception_type = type(error).__name__\n    known_error = exception_type in known_errors\n    exception_type_compliance = 'Compliant' if known_error else compliant\n\n    cr_error = {\n        'code': code,\n        'category': category,\n        'message': { compliant: str(error) },\n        'details': [\n            {\n                'name': 'StackTrace',\n                'value': { compliant: stack_trace }\n            },\n            {\n                'name': 'ExceptionType',\n                'value': { exception_type_compliance: exception_type }\n            },\n        ]\n    }\n\n    try:\n        from azureml.exceptions import AzureMLException, UserErrorException\n        if isinstance(error, UserErrorException):\n            cr_error['category'] = 'UserError'\n        if isinstance(error, AzureMLException):\n            cr_error['details'][1]['value'] = { 'Compliant': exception_type }\n    except:\n        pass\n\n    return cr_error\n\n# Copied from context manager injector\ndef strip_stack_of_azureml_layers(exc_type, exc_val, exc_traceback):\n    \"\"\"\n        The actual traceback that gets printed when the exception is in the user code is:\n\n        Traceback(most recent call last) :\n            File 'azureml-setup/context_manager_injector.py', line 161, in <module>\n                execute_with_context(cm_objects, options.invocation)\n            File 'azureml-setup/context_manager_injector.py', line 91, in execute_with_context\n                runpy.run_path(sys.argv[0], globals(), run_name= '__main__')\n            File '<USERPROFILE>\\AppData\\Local\\Continuum\\Miniconda3\\envs\\cli_dev\\lib\\runpy.py', line 263, in run_path\n                pkg_name = pkg_name, script_name = fname)\n            File '<USERPROFILE>\\AppData\\Local\\Continuum\\Miniconda3\\envs\\cli_dev\\lib\\runpy.py', line 96, in _run_module_code\n                mod_name, mod_spec, pkg_name, script_name)\n            File '<USERPROFILE>\\AppData\\Local\\Continuum\\Miniconda3\\envs\\cli_dev\\lib\\runpy.py', line 85, in _run_code\n                exec(code, run_globals)\n            File 'bad_import.py', line 5, in <module>\n                import thisdoesnotexist\n        ModuleNotFoundError: No module named 'thisdoesnotexist'\n\n        however we strip the first 5 layers to give the user a traceback that only contains the user code as part of it\n    \"\"\"\n    traceback_as_list = traceback.format_exception(exc_type, exc_val, exc_traceback)\n    reversed_traceback_list = reversed(traceback_as_list)\n    reversed_trimmed_stack = []\n    # currently the innermost runpy stack occurs inside runpy.py in _run_code and inside the exec(code, run_globals) function\n    # if that changes then the regular stack will be printed\n    keywords_in_innermost_runpy_stack_frame = ['runpy.py', '_run_code', 'exec(code, run_globals)']\n    error_is_in_user_code = False\n    for stack_frame in reversed_traceback_list:\n        if all([keyword in stack_frame for keyword in keywords_in_innermost_runpy_stack_frame]):\n            error_is_in_user_code = True\n            break\n        reversed_trimmed_stack.append(stack_frame)\n    if error_is_in_user_code:\n        # Find the first index of 'Traceback (most recent call last):' in reversed list and append the cause exceptions\n        # This will handle users using 'from with raise' when raising exception\n        reversed_traceback_as_list = traceback_as_list[::-1]\n        traceback_indexes = [idx for idx,stack_frame in enumerate(reversed_traceback_as_list)\n                             if 'Traceback (most recent call last):' in stack_frame]\n        if len(traceback_indexes) > 0:\n            reversed_trimmed_stack.extend(reversed_traceback_as_list[traceback_indexes[0]:])\n\n    return list(reversed(reversed_trimmed_stack))\n\ndef set_tags_for_mlflow_run():\n    # Prepare MLflow integration if supported\n    try:\n        from azureml.core.run import Run\n        from azureml.mlflow import _setup_remote\n        run = Run.get_context() \n        _setup_remote(run)\n    except Exception:\n        return\n\ndef main():\n    # This used to be done in a context_managers.py and context_manager_injector.py where it will add current working\n    # directory and the script's directory to sys.path respectively.\n    # We want to make sure the script's directory is added to the start of sys.path so that it is searched\n    # first and the current working directory is added to the end so that it is searched last.\n    sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[1])))\n    sys.path.append(os.getcwd())\n\n    try:\n        # The Run import below is only needed to avoid circular dependency import issue\n        # in the context manager's exit calls\n        from azureml.core import Run\n        from azureml._history.utils.context_managers import SendRunKillSignal\n\n        # Only do this check if AzureML is used\n        if sys.version_info.major != 3 or sys.version_info.minor < 5:\n            raise RuntimeError(f'Python version {str(sys.version_info)} is not supported. Please use python>=3.5')\n\n        # The SendRunKillSignal context manager is misleadingly named. It is actually used to flush metrics of\n        # all the RunHistoryFacade instances. The way it does that is the RunHistoryFacade's constructor registers\n        # a clean up handler that calls flush on the metrics client it has, the handler itself is registered to\n        # a class variable of the RunHistoryFacade class. The SendRunKillSignal context manager's exit method\n        # calls the RunHistoryFacade._kill class method which goes and calls the all of the registered exit handlers\n        # which in turn flushes the metrics. The code below is copied from the run history context manager code.\n        send_kill_signal = not os.environ.get('AZUREML_DISABLE_RUN_KILL_SIGNAL')\n        kill_signal_timeout = float(os.environ.get('AZUREML_RUN_KILL_SIGNAL_TIMEOUT_SEC', '300'))\n        context = SendRunKillSignal(send_kill_signal, kill_signal_timeout)\n    except ImportError:\n        context = NoopContextManager()\n    except RuntimeError:\n        raise\n    except Exception as e:\n        print(f'Warning: Failed to setup Azure Machine Learning system code due to `{e}`. Your job will proceed but if you notice any issues, please contact Azure Support with this exception message.', file=sys.stderr)\n        context = NoopContextManager()\n        \n    set_tags_for_mlflow_run()\n\n    context = ErrorHandlerContextManager(context)\n    with context:\n        # when we invoke with `python -c program args`, sys.argv[0] will be -c, args will be the rest (i.e. sys.argv[1:])\n        expanded_argv = []\n        for arg in sys.argv[1:]:\n            arg = os.path.expandvars(arg)\n            expanded_argv.append(arg)\n        sys.argv = expanded_argv\n        runpy.run_path(sys.argv[0], globals(), run_name='__main__')\n\nif __name__ == '__main__':\n    try:\n        main()\n    except SystemExit as ex:\n        # Copied from context manager injector\n        exc_type, exc_val, exc_traceback = sys.exc_info()\n        print(''.join(strip_stack_of_azureml_layers(exc_type, exc_val, exc_traceback)), file=sys.stderr)\n        if ex.code is not None:\n            sys.exit(ex.code)\n    except Exception as ex:\n        # Copied from context manager injector\n        exc_type, exc_val, exc_traceback = sys.exc_info()\n        print(''.join(strip_stack_of_azureml_layers(exc_type, exc_val, exc_traceback)), file=sys.stderr)\n        sys.exit(1)\n",
                                    "urldecode_invoker.py",
                                    "python",
                                    "-m",
                                    "azureml.studio.modulehost.module_invoker",
                                    "--module-name=azureml.studio.modules.ml.initialize_models.regressor.linear_regressor.linear_regressor",
                                    "--untrained-model",
                                    "$AZURE_ML_OUTPUT_Untrained_model",
                                    "--solution-method=%22Ordinary+Least+Squares%22",
                                    "--l2-regularization-weight=0.001",
                                    "--include-intercept-term=True"
                                ]
                            },
                            "stdout": "user_logs/std_log.txt"
                        }
                    }
                }
            ]
        },
        "lifecycler": {
            "name": "lifecycler",
            "version": "stable",
            "config": {
                "enable_termination_signal_handling": true
            }
        },
        "capabilities": [
            {
                "name": "data-capability",
                "version": "stable",
                "config": [
                    {
                        "to": "azuremldatastore://workspaceblobstore/azureml/927f61e0-8999-4082-a685-d0c0a02b466e/Untrained_model",
                        "name": "Untrained_model",
                        "mode": "mount",
                        "environment_names": [
                            "Untrained_model",
                            "AZURE_ML_OUTPUT_Untrained_model"
                        ],
                        "options": {
                            "is_single_file": false,
                            "register_dataset": {
                                "properties": {
                                    "azureml.pipelineRunId": "f4a6c5eb-1feb-49ff-9429-4ec15b15393c",
                                    "azureml.pipelineRun.moduleNodeId": "4b199015",
                                    "azureml.pipelineRun.outputPortName": "Untrained_model"
                                }
                            }
                        }
                    }
                ]
            },
            {
                "name": "cs-capability",
                "version": "stable",
                "config": {
                    "context_managers": [],
                    "snapshot": "[{\"Id\":\"e5d61572-7dea-47b3-9538-221a88fcd381\",\"PathStack\":[\".\"],\"SnapshotEntityId\":null,\"SnapshotAssetId\":null}]"
                }
            },
            {
                "name": "hosttools-capability",
                "version": "stable",
                "config": {
                    "dirs": [
                        {
                            "relative_path": "user_logs",
                            "environment_name": "AZUREML_CR_HT_CAP_user_logs_PATH",
                            "streamable": true
                        },
                        {
                            "relative_path": "azureml-logs",
                            "environment_name": "AZUREML_CR_HT_CAP_azureml_logs_PATH",
                            "streamable": true
                        },
                        {
                            "relative_path": "outputs",
                            "environment_name": "AZUREML_CR_HT_CAP_outputs_PATH",
                            "streamable": false
                        },
                        {
                            "relative_path": "logs",
                            "environment_name": "AZUREML_CR_HT_CAP_logs_PATH",
                            "streamable": true
                        }
                    ],
                    "metrics": {
                        "enabled": true,
                        "polling_interval_sec": 30,
                        "send_to_history_interval_sec": 60
                    },
                    "use_block_blob_in_blob_streamer": true,
                    "log_filtering_policy": null
                }
            }
        ],
        "azureml_context": {
            "subscription_id": "a0f4a733-4fce-4d49-b8a8-d30541fc1b45",
            "resource_group": "azureml",
            "workspace_name": "azureml",
            "workspace_id": "10400c14-9477-41ad-a935-e963d851654b",
            "service_endpoint": "https://westeurope.api.azureml.ms",
            "discovery_endpoint": "https://westeurope.api.azureml.ms/discovery",
            "experiment_name": "tomasexperiment",
            "experiment_id": "e4360b71-5ba4-4789-8e0c-ab040462cc06",
            "root_run_id": "f4a6c5eb-1feb-49ff-9429-4ec15b15393c",
            "run_id": "927f61e0-8999-4082-a685-d0c0a02b466e",
            "run_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw",
            "run_history_service_endpoint": "https://westeurope.api.azureml.ms",
            "data_container_id": "dcid.927f61e0-8999-4082-a685-d0c0a02b466e",
            "run_uuid": "72f05b4a-9d34-46e4-9a93-eb6b8e6254c2"
        },
        "compute_context": {
            "cluster_name": "k8s-compute",
            "node_id": {
                "Literal": ""
            }
        },
        "observability_config": {
            "collector": {
                "exporter": {
                    "appinsights": {
                        "instrumentation_key": "fca5a4c9-adb4-44ae-bece-69e2cc91ff66"
                    }
                }
            },
            "logger": {
                "appinsights": {
                    "instrumentation_key": "fca5a4c9-adb4-44ae-bece-69e2cc91ff66",
                    "level": "info",
                    "enabled": true
                },
                "file": {
                    "extension": "log",
                    "level": "info",
                    "enabled": true
                }
            }
        },
        "bootstrapper_config": {
            "version": "stable",
            "config": {
                "capabilities_registry": {
                    "registry": {
                        "url": "viennaglobal.azurecr.io",
                        "username": "vienna-global-reader",
                        "password": "5889T4YAGWD=L2G=bmvy3pfwGRVoGUN6"
                    },
                    "regional_tag_prefix": true
                },
                "resource_constraints": {
                    "cpu_shares": 6144,
                    "reserved_mem_mb": 650,
                    "sys_cpu_shares": 1024,
                    "sys_reserved_mem_mb": 500
                },
                "disk_thresholds": {
                    "disk_free_before_job_mb": 1500,
                    "disk_free_after_job_mb": 5000
                },
                "image_cache_config": {
                    "cache_size_mb": 2000,
                    "purge_after_job_completion": false
                },
                "enable_pre_job_cleanup": false
            }
        }
    }
}
```

Zajímavé - tohle je předpřipravený job (a kontejner a tak podobně). Pokud si budu dělat svoje vlastní kroky, mohu je postavit na managed image nebo si klidně udělat svůj vlastní a v něm jednotlivé kroky a skripty spouštět. Velmi univerzální, velmi mocné, líbí se mi to. 

Volcano Job je poměrně jednoduchý, protože to spouštím jen jako jednu instanci.

```yaml
apiVersion: scheduling.volcano.sh/v1beta1
kind: PodGroup
metadata:
  annotations:
    volcano.sh/task-topology-affinity: worker
  creationTimestamp: "2022-07-12T06:35:35Z"
  generation: 3
  labels:
    jobId: 72888029582f8ccfc5724be3e41a13da
  name: azureml-workloads-72888029582f8ccfc5724be3e41a13da
  namespace: azureml-workloads
  ownerReferences:
  - apiVersion: batch.volcano.sh/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: Job
    name: azureml-workloads-72888029582f8ccfc5724be3e41a13da
    uid: 96e3e3e2-f8c9-4f5e-9225-d41308c9a8ed
  resourceVersion: "26363"
  uid: bdf9fc47-d294-47be-a2c9-d50bfcd97866
spec:
  minResources: {}
  minTaskMember:
    worker: 1
  queue: default
status:
  conditions:
  - lastTransitionTime: "2022-07-12T06:36:47Z"
    reason: tasks in gang are ready to be scheduled
    status: "True"
    transitionID: 76ebd086-ee6c-404a-a50e-6965afc88ab8
    type: Scheduled
  phase: Running
```

Dobré je, že i na bezpečnost se myslelo a kromě různých ověřovacích klíčů mi to nahodilo i síťovou izolaci.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  creationTimestamp: "2022-07-12T06:35:38Z"
  generation: 1
  name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572
  namespace: azureml-workloads
  ownerReferences:
  - apiVersion: batch.volcano.sh/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: Job
    name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572
    uid: deddaa33-8044-438c-9095-46a604ae5b61
  resourceVersion: "25661"
  uid: 166af83e-5d7d-4d75-b88b-4b8eb373e82b
spec:
  ingress:
  - from:
    - podSelector:
        matchLabels:
          volcano.sh/job-name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572
          volcano.sh/job-namespace: azureml-workloads
  podSelector:
    matchLabels:
      volcano.sh/job-name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572
      volcano.sh/job-namespace: azureml-workloads
  policyTypes:
  - Ingress
```

Výsledný Pod je docela složitý, ale dává smysl.

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/1cfc74aae33346e9b77672f82ab26790-execution-wrapper: unconfined
    scheduling.k8s.io/group-name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572
    volcano.sh/job-name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572
    volcano.sh/job-version: "0"
    volcano.sh/queue-name: default
    volcano.sh/task-spec: worker
    volcano.sh/template-uid: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker
  creationTimestamp: "2022-07-12T06:35:39Z"
  labels:
    controller: aml-operator
    gpu-request: "0"
    jobId: 8b2821ccdc9c9fb818502c0e69b96572
    jobRole: worker
    jobScale: regular
    jobsource: aml
    mainContainers: 1cfc74aae33346e9b77672f82ab26790-lifecycler
    ml.azure.com/billing-category: azureml-training
    ml.azure.com/compute: k8s-compute
    ml.azure.com/resource-group: azureml
    ml.azure.com/run-id: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    ml.azure.com/scrape-metrics: "true"
    ml.azure.com/subscription-id: a0f4a733-4fce-4d49-b8a8-d30541fc1b45
    ml.azure.com/workspace: azureml
    role: worker
    run: 8b2821ccdc9c9fb818502c0e69b96572
    type: job
    userName: amluser
    vcName: amldefaultvc
    volcano.sh/job-name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572
    volcano.sh/job-namespace: azureml-workloads
    volcano.sh/queue-name: default
    volcano.sh/task-spec: worker
  name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0
  namespace: azureml-workloads
  ownerReferences:
  - apiVersion: batch.volcano.sh/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: Job
    name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572
    uid: deddaa33-8044-438c-9095-46a604ae5b61
  resourceVersion: "25928"
  uid: d757cf06-18fd-44a5-b228-9242177515c1
spec:
  automountServiceAccountToken: true
  containers:
  - command:
    - /bin/bash
    - /training-identity-sidecar/run.sh
    env:
    - name: AMLARC_NUM_GPU_PER_WORKER
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AML_JOB_ID
      value: 8b2821ccdc9c9fb818502c0e69b96572
    - name: POD_UID
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.uid
    - name: AMLARC_NUM_PS
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AMLARC_ROLE_INDEX_REGEX
      value: '[a-zA-Z0-9\-]*-([a-zA-Z[]*)-([0-9[]*)'
    - name: AZUREML_OBO_CANARY_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sL2V4cGVyaW1lbnROYW1lL3RvbWFzZXhwZXJpbWVudC9ydW5JZC84OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjkiLCJhY2NvdW50aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJ3b3Jrc3BhY2VJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsInByb2plY3RpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImRpc2NvdmVyeSI6InVyaTovL2Rpc2NvdmVyeXVyaS8iLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDciLCJvaWQiOiIzZTEzMWZiZS0zNDU0LTRiMGMtODRhZi03NDVhYjE3NmQzNGQiLCJpc3MiOiJhenVyZW1sIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3LyIsImV4cCI6MTY1OTMzNTI2MCwiYXVkIjoiYXp1cmVtbCJ9.LgInzjMVeUO-1vcr-hrK4KeYNvWlAI3rTwaTimQ9OmJcCYopbWYWg8_aVwUKvKa3goqoZJgs2UEUwgv19r_cyL-BR8v-4opIRJh68ZLUBJYPuVRK_qRQdM7OkJdU2PZugiBFYGSicG40xE1I80LjdnEcrJHRVQ0-UFNJvaWtu-HHpV_aKedQNClO4jZb9Dfoax63ZHw4C4e2f9GV7JTQ1v18SlXlyEHR8iSRg9p-cDnmiktBkctYs2VMIU_k57hNtq5fJS5zBetjlA9wYIHzOAER2CefogBWSXxBhGKTRlDX-ovIz3j9JE2H5BuNNhm2yEcucrB8oROVgGF2zcb-vQ
    - name: AZUREML_OBO_ENABLED
      value: "True"
    - name: OBO_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: MSI_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: EXIT_FILE
      value: /pod-lifecycle/$(POD_UID).exit
    - name: VC_WORKER_HOSTS
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_HOSTS
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VC_WORKER_NUM
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_NUM
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VK_TASK_INDEX
      value: "0"
    - name: VC_TASK_INDEX
      value: "0"
    image: mcr.microsoft.com/azureml/amlarc/docker/training-identity-sidecar:1.1.6
    imagePullPolicy: Always
    lifecycle:
      postStart:
        exec:
          command:
          - /bin/bash
          - /training-identity-sidecar/ready.sh
    livenessProbe:
      exec:
        command:
        - /bin/bash
        - -c
        - /pod-lifecycle/lifecycle_script.sh training-identity-sidecar
      failureThreshold: 3
      initialDelaySeconds: 3
      periodSeconds: 10
      successThreshold: 1
      timeoutSeconds: 1
    name: training-identity-sidecar
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: FallbackToLogsOnError
    volumeMounts:
    - mountPath: /tmp/runtoken
      name: runtoken
    - mountPath: /pod-lifecycle
      name: lifecycle-cm
    - mountPath: /etc/volcano
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - mountPath: /root/.ssh
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
      subPath: .ssh
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-vpq6k
      readOnly: true
  - env:
    - name: AMLARC_NUM_GPU_PER_WORKER
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AML_JOB_ID
      value: 8b2821ccdc9c9fb818502c0e69b96572
    - name: POD_UID
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.uid
    - name: AMLARC_NUM_PS
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AMLARC_ROLE_INDEX_REGEX
      value: '[a-zA-Z0-9\-]*-([a-zA-Z[]*)-([0-9[]*)'
    - name: AZUREML_OBO_CANARY_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sL2V4cGVyaW1lbnROYW1lL3RvbWFzZXhwZXJpbWVudC9ydW5JZC84OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjkiLCJhY2NvdW50aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJ3b3Jrc3BhY2VJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsInByb2plY3RpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImRpc2NvdmVyeSI6InVyaTovL2Rpc2NvdmVyeXVyaS8iLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDciLCJvaWQiOiIzZTEzMWZiZS0zNDU0LTRiMGMtODRhZi03NDVhYjE3NmQzNGQiLCJpc3MiOiJhenVyZW1sIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3LyIsImV4cCI6MTY1OTMzNTI2MCwiYXVkIjoiYXp1cmVtbCJ9.LgInzjMVeUO-1vcr-hrK4KeYNvWlAI3rTwaTimQ9OmJcCYopbWYWg8_aVwUKvKa3goqoZJgs2UEUwgv19r_cyL-BR8v-4opIRJh68ZLUBJYPuVRK_qRQdM7OkJdU2PZugiBFYGSicG40xE1I80LjdnEcrJHRVQ0-UFNJvaWtu-HHpV_aKedQNClO4jZb9Dfoax63ZHw4C4e2f9GV7JTQ1v18SlXlyEHR8iSRg9p-cDnmiktBkctYs2VMIU_k57hNtq5fJS5zBetjlA9wYIHzOAER2CefogBWSXxBhGKTRlDX-ovIz3j9JE2H5BuNNhm2yEcucrB8oROVgGF2zcb-vQ
    - name: AZUREML_OBO_ENABLED
      value: "True"
    - name: OBO_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: MSI_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: AZUREML_CR_LIFECYCLER_CONFIG
      value: eyJwaGFzZXMiOlt7ImNvb3JkaW5hdGVkX3N0YXJ0IjpmYWxzZSwibm9kZXMiOlswXSwiY29tbWFuZHMiOnsiY29tbWFuZCI6eyJleGVjdXRhYmxlIjp7InR5cGUiOiJTcGF3biIsInByb2dyYW0iOiIvYXp1cmVtbC1lbnZzL2F6dXJlbWxfNjQxNjVhMjZlMzg0NTFkODY4ZDczMmE2M2RlYzI3ODMvYmluL3B5dGhvbiIsImFyZ3MiOlsiLXUiLCItYyIsIlxuaW1wb3J0IGpzb25cbmltcG9ydCBvc1xuaW1wb3J0IG9zLnBhdGhcbmltcG9ydCBydW5weVxuaW1wb3J0IHN5c1xuaW1wb3J0IHRyYWNlYmFja1xuXG5jbGFzcyBOb29wQ29udGV4dE1hbmFnZXI6XG4gICAgZGVmIF9fZW50ZXJfXyhzZWxmKTpcbiAgICAgICAgcGFzc1xuXG4gICAgZGVmIF9fZXhpdF9fKHNlbGYsICphcmdzLCAqKmt3YXJncyk6XG4gICAgICAgIHBhc3NcblxuY2xhc3MgRXJyb3JIYW5kbGVyQ29udGV4dE1hbmFnZXI6XG4gICAgZGVmIF9faW5pdF9fKHNlbGYsIGlubmVyX2NtKTpcbiAgICAgICAgc2VsZi5pbm5lcl9jbSA9IGlubmVyX2NtXG5cbiAgICBkZWYgX19lbnRlcl9fKHNlbGYpOlxuICAgICAgICByZXR1cm4gRXJyb3JIYW5kbGVyQ29udGV4dE1hbmFnZXIuZG9fb3BfYW5kX3dyaXRlX2Vycm9yKGxhbWJkYTogc2VsZi5pbm5lcl9jbS5fX2VudGVyX18oKSwgJ1VzZXJFeGVjdXRpb24uY29udGV4dF9tYW5hZ2VyLmVudGVyJylcblxuICAgIGRlZiBfX2V4aXRfXyhzZWxmLCBleGNfdHlwZSwgZXhjX3ZhbHVlLCB0cmFjZWJhY2spOlxuICAgICAgICBpZiBleGNfdmFsdWU6XG4gICAgICAgICAgICB3cml0ZV9lcnJvcignVXNlckV4ZWN1dGlvbi5zY3JpcHQnLCAnVXNlckVycm9yJywgZXhjX3ZhbHVlLCAnTm9uQ29tcGxpYW50JylcbiAgICAgICAgcmV0dXJuIEVycm9ySGFuZGxlckNvbnRleHRNYW5hZ2VyLmRvX29wX2FuZF93cml0ZV9lcnJvcihsYW1iZGE6IHNlbGYuaW5uZXJfY20uX19leGl0X18oZXhjX3R5cGUsIGV4Y192YWx1ZSwgdHJhY2ViYWNrKSwgJ1VzZXJFeGVjdXRpb24uY29udGV4dF9tYW5hZ2VyLmV4aXQnKVxuXG4gICAgQHN0YXRpY21ldGhvZFxuICAgIGRlZiBkb19vcF9hbmRfd3JpdGVfZXJyb3Iob3AsIGVycm9yX2NvZGUpOlxuICAgICAgICB0cnk6XG4gICAgICAgICAgICByZXR1cm4gb3AoKVxuICAgICAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGU6XG4gICAgICAgICAgICB3cml0ZV9lcnJvcihlcnJvcl9jb2RlLCAnU3lzdGVtRXJyb3InLCBlLCAnQ29tcGxpYW50JylcbiAgICAgICAgICAgIHJhaXNlXG5cbmRlZiB3cml0ZV9lcnJvcihjb2RlLCBjYXRlZ29yeSwgZXJyb3IsIGNvbXBsaWFudCk6XG4gICAgdHJ5OlxuICAgICAgICBlcnJvcl9wYXRoID0gb3MuZW52aXJvbi5nZXQoJ19BWlVSRU1MX0NSX0VSUk9SX0pTT05fRklMRScpXG4gICAgICAgIGRpciA9IG9zLnBhdGguZGlybmFtZShlcnJvcl9wYXRoKVxuICAgICAgICBvcy5tYWtlZGlycyhkaXIsIGV4aXN0X29rPVRydWUpXG4gICAgICAgIHdpdGggb3BlbihlcnJvcl9wYXRoLCAneCcpIGFzIGY6XG4gICAgICAgICAgICBmLndyaXRlKGpzb24uZHVtcHModG9fY3JfZXJyb3IoY29kZSwgY2F0ZWdvcnksIGVycm9yLCBjb21wbGlhbnQpKSlcbiAgICBleGNlcHQ6XG4gICAgICAgIHBhc3NcblxuZGVmIHRvX2NyX2Vycm9yKGNvZGUsIGNhdGVnb3J5LCBlcnJvciwgY29tcGxpYW50KTpcbiAgICBrbm93bl9lcnJvcnMgPSBbXG4gICAgICAgICdCYXNlRXhjZXB0aW9uJywgJ1N5c3RlbUV4aXQnLCAnS2V5Ym9hcmRJbnRlcnJ1cHQnLCAnR2VuZXJhdG9yRXhpdCcsICdFeGNlcHRpb24nLCAnU3RvcEl0ZXJhdGlvbicsICdTdG9wQXN5bmNJdGVyYXRpb24nLFxuICAgICAgICAnQXJpdGhtZXRpY0Vycm9yJywgJ0Zsb2F0aW5nUG9pbnRFcnJvcicsICdPdmVyZmxvd0Vycm9yJywgJ1plcm9EaXZpc2lvbkVycm9yJywgJ0Fzc2VydGlvbkVycm9yJywgJ0F0dHJpYnV0ZUVycm9yJyxcbiAgICAgICAgJ0J1ZmZlckVycm9yJywgJ0VPRkVycm9yJywgJ0ltcG9ydEVycm9yJywgJ01vZHVsZU5vdEZvdW5kRXJyb3InLCAnTG9va3VwRXJyb3InLCAnSW5kZXhFcnJvcicsICdLZXlFcnJvcicsICdNZW1vcnlFcnJvcicsXG4gICAgICAgICdOYW1lRXJyb3InLCAnVW5ib3VuZExvY2FsRXJyb3InLCAnT1NFcnJvcicsICdCbG9ja2luZ0lPRXJyb3InLCAnQ2hpbGRQcm9jZXNzRXJyb3InLCAnQ29ubmVjdGlvbkVycm9yJywgJ0Jyb2tlblBpcGVFcnJvcicsXG4gICAgICAgICdDb25uZWN0aW9uQWJvcnRlZEVycm9yJywgJ0Nvbm5lY3Rpb25SZWZ1c2VkRXJyb3InLCAnQ29ubmVjdGlvblJlc2V0RXJyb3InLCAnRmlsZUV4aXN0c0Vycm9yJywgJ0ZpbGVOb3RGb3VuZEVycm9yJyxcbiAgICAgICAgJ0ludGVycnVwdGVkRXJyb3InLCAnSXNBRGlyZWN0b3J5RXJyb3InLCAnTm90QURpcmVjdG9yeUVycm9yJywgJ1Blcm1pc3Npb25FcnJvcicsICdQcm9jZXNzTG9va3VwRXJyb3InLCAnVGltZW91dEVycm9yJyxcbiAgICAgICAgJ1JlZmVyZW5jZUVycm9yJywgJ1J1bnRpbWVFcnJvcicsICdOb3RJbXBsZW1lbnRlZEVycm9yJywgJ1JlY3Vyc2lvbkVycm9yJywgJ1N5bnRheEVycm9yJywgJ0luZGVudGF0aW9uRXJyb3InLCAnVGFiRXJyb3InLFxuICAgICAgICAnU3lzdGVtRXJyb3InLCAnVHlwZUVycm9yJywgJ1ZhbHVlRXJyb3InLCAnVW5pY29kZUVycm9yJywgJ1VuaWNvZGVEZWNvZGVFcnJvcicsICdVbmljb2RlRW5jb2RlRXJyb3InLCAnVW5pY29kZVRyYW5zbGF0ZUVycm9yJyxcbiAgICAgICAgJ1dhcm5pbmcnLCAnRGVwcmVjYXRpb25XYXJuaW5nJywgJ1BlbmRpbmdEZXByZWNhdGlvbldhcm5pbmcnLCAnUnVudGltZVdhcm5pbmcnLCAnU3ludGF4V2FybmluZycsICdVc2VyV2FybmluZycsXG4gICAgICAgICdGdXR1cmVXYXJuaW5nJywgJ0ltcG9ydFdhcm5pbmcnLCAnVW5pY29kZVdhcm5pbmcnLCAnQnl0ZXNXYXJuaW5nJywgJ0VuY29kaW5nV2FybmluZycsICdSZXNvdXJjZVdhcm5pbmcnLCAnSU9FcnJvcicsXG4gICAgICAgICdFbnZpcm9ubWVudEVycm9yJ1xuICAgIF1cbiAgICBleGNfdHlwZSwgZXhjX3ZhbCwgZXhjX3RyYWNlYmFjayA9IHN5cy5leGNfaW5mbygpXG4gICAgc3RhY2tfdHJhY2UgPSAnJy5qb2luKHN0cmlwX3N0YWNrX29mX2F6dXJlbWxfbGF5ZXJzKGV4Y190eXBlLCBleGNfdmFsLCBleGNfdHJhY2ViYWNrKSlcbiAgICBleGNlcHRpb25fdHlwZSA9IHR5cGUoZXJyb3IpLl9fbmFtZV9fXG4gICAga25vd25fZXJyb3IgPSBleGNlcHRpb25fdHlwZSBpbiBrbm93bl9lcnJvcnNcbiAgICBleGNlcHRpb25fdHlwZV9jb21wbGlhbmNlID0gJ0NvbXBsaWFudCcgaWYga25vd25fZXJyb3IgZWxzZSBjb21wbGlhbnRcblxuICAgIGNyX2Vycm9yID0ge1xuICAgICAgICAnY29kZSc6IGNvZGUsXG4gICAgICAgICdjYXRlZ29yeSc6IGNhdGVnb3J5LFxuICAgICAgICAnbWVzc2FnZSc6IHsgY29tcGxpYW50OiBzdHIoZXJyb3IpIH0sXG4gICAgICAgICdkZXRhaWxzJzogW1xuICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgICduYW1lJzogJ1N0YWNrVHJhY2UnLFxuICAgICAgICAgICAgICAgICd2YWx1ZSc6IHsgY29tcGxpYW50OiBzdGFja190cmFjZSB9XG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgICduYW1lJzogJ0V4Y2VwdGlvblR5cGUnLFxuICAgICAgICAgICAgICAgICd2YWx1ZSc6IHsgZXhjZXB0aW9uX3R5cGVfY29tcGxpYW5jZTogZXhjZXB0aW9uX3R5cGUgfVxuICAgICAgICAgICAgfSxcbiAgICAgICAgXVxuICAgIH1cblxuICAgIHRyeTpcbiAgICAgICAgZnJvbSBhenVyZW1sLmV4Y2VwdGlvbnMgaW1wb3J0IEF6dXJlTUxFeGNlcHRpb24sIFVzZXJFcnJvckV4Y2VwdGlvblxuICAgICAgICBpZiBpc2luc3RhbmNlKGVycm9yLCBVc2VyRXJyb3JFeGNlcHRpb24pOlxuICAgICAgICAgICAgY3JfZXJyb3JbJ2NhdGVnb3J5J10gPSAnVXNlckVycm9yJ1xuICAgICAgICBpZiBpc2luc3RhbmNlKGVycm9yLCBBenVyZU1MRXhjZXB0aW9uKTpcbiAgICAgICAgICAgIGNyX2Vycm9yWydkZXRhaWxzJ11bMV1bJ3ZhbHVlJ10gPSB7ICdDb21wbGlhbnQnOiBleGNlcHRpb25fdHlwZSB9XG4gICAgZXhjZXB0OlxuICAgICAgICBwYXNzXG5cbiAgICByZXR1cm4gY3JfZXJyb3JcblxuIyBDb3BpZWQgZnJvbSBjb250ZXh0IG1hbmFnZXIgaW5qZWN0b3JcbmRlZiBzdHJpcF9zdGFja19vZl9henVyZW1sX2xheWVycyhleGNfdHlwZSwgZXhjX3ZhbCwgZXhjX3RyYWNlYmFjayk6XG4gICAgXCJcIlwiXG4gICAgICAgIFRoZSBhY3R1YWwgdHJhY2ViYWNrIHRoYXQgZ2V0cyBwcmludGVkIHdoZW4gdGhlIGV4Y2VwdGlvbiBpcyBpbiB0aGUgdXNlciBjb2RlIGlzOlxuXG4gICAgICAgIFRyYWNlYmFjayhtb3N0IHJlY2VudCBjYWxsIGxhc3QpIDpcbiAgICAgICAgICAgIEZpbGUgJ2F6dXJlbWwtc2V0dXAvY29udGV4dF9tYW5hZ2VyX2luamVjdG9yLnB5JywgbGluZSAxNjEsIGluIDxtb2R1bGU+XG4gICAgICAgICAgICAgICAgZXhlY3V0ZV93aXRoX2NvbnRleHQoY21fb2JqZWN0cywgb3B0aW9ucy5pbnZvY2F0aW9uKVxuICAgICAgICAgICAgRmlsZSAnYXp1cmVtbC1zZXR1cC9jb250ZXh0X21hbmFnZXJfaW5qZWN0b3IucHknLCBsaW5lIDkxLCBpbiBleGVjdXRlX3dpdGhfY29udGV4dFxuICAgICAgICAgICAgICAgIHJ1bnB5LnJ1bl9wYXRoKHN5cy5hcmd2WzBdLCBnbG9iYWxzKCksIHJ1bl9uYW1lPSAnX19tYWluX18nKVxuICAgICAgICAgICAgRmlsZSAnPFVTRVJQUk9GSUxFPlxcQXBwRGF0YVxcTG9jYWxcXENvbnRpbnV1bVxcTWluaWNvbmRhM1xcZW52c1xcY2xpX2RldlxcbGliXFxydW5weS5weScsIGxpbmUgMjYzLCBpbiBydW5fcGF0aFxuICAgICAgICAgICAgICAgIHBrZ19uYW1lID0gcGtnX25hbWUsIHNjcmlwdF9uYW1lID0gZm5hbWUpXG4gICAgICAgICAgICBGaWxlICc8VVNFUlBST0ZJTEU+XFxBcHBEYXRhXFxMb2NhbFxcQ29udGludXVtXFxNaW5pY29uZGEzXFxlbnZzXFxjbGlfZGV2XFxsaWJcXHJ1bnB5LnB5JywgbGluZSA5NiwgaW4gX3J1bl9tb2R1bGVfY29kZVxuICAgICAgICAgICAgICAgIG1vZF9uYW1lLCBtb2Rfc3BlYywgcGtnX25hbWUsIHNjcmlwdF9uYW1lKVxuICAgICAgICAgICAgRmlsZSAnPFVTRVJQUk9GSUxFPlxcQXBwRGF0YVxcTG9jYWxcXENvbnRpbnV1bVxcTWluaWNvbmRhM1xcZW52c1xcY2xpX2RldlxcbGliXFxydW5weS5weScsIGxpbmUgODUsIGluIF9ydW5fY29kZVxuICAgICAgICAgICAgICAgIGV4ZWMoY29kZSwgcnVuX2dsb2JhbHMpXG4gICAgICAgICAgICBGaWxlICdiYWRfaW1wb3J0LnB5JywgbGluZSA1LCBpbiA8bW9kdWxlPlxuICAgICAgICAgICAgICAgIGltcG9ydCB0aGlzZG9lc25vdGV4aXN0XG4gICAgICAgIE1vZHVsZU5vdEZvdW5kRXJyb3I6IE5vIG1vZHVsZSBuYW1lZCAndGhpc2RvZXNub3RleGlzdCdcblxuICAgICAgICBob3dldmVyIHdlIHN0cmlwIHRoZSBmaXJzdCA1IGxheWVycyB0byBnaXZlIHRoZSB1c2VyIGEgdHJhY2ViYWNrIHRoYXQgb25seSBjb250YWlucyB0aGUgdXNlciBjb2RlIGFzIHBhcnQgb2YgaXRcbiAgICBcIlwiXCJcbiAgICB0cmFjZWJhY2tfYXNfbGlzdCA9IHRyYWNlYmFjay5mb3JtYXRfZXhjZXB0aW9uKGV4Y190eXBlLCBleGNfdmFsLCBleGNfdHJhY2ViYWNrKVxuICAgIHJldmVyc2VkX3RyYWNlYmFja19saXN0ID0gcmV2ZXJzZWQodHJhY2ViYWNrX2FzX2xpc3QpXG4gICAgcmV2ZXJzZWRfdHJpbW1lZF9zdGFjayA9IFtdXG4gICAgIyBjdXJyZW50bHkgdGhlIGlubmVybW9zdCBydW5weSBzdGFjayBvY2N1cnMgaW5zaWRlIHJ1bnB5LnB5IGluIF9ydW5fY29kZSBhbmQgaW5zaWRlIHRoZSBleGVjKGNvZGUsIHJ1bl9nbG9iYWxzKSBmdW5jdGlvblxuICAgICMgaWYgdGhhdCBjaGFuZ2VzIHRoZW4gdGhlIHJlZ3VsYXIgc3RhY2sgd2lsbCBiZSBwcmludGVkXG4gICAga2V5d29yZHNfaW5faW5uZXJtb3N0X3J1bnB5X3N0YWNrX2ZyYW1lID0gWydydW5weS5weScsICdfcnVuX2NvZGUnLCAnZXhlYyhjb2RlLCBydW5fZ2xvYmFscyknXVxuICAgIGVycm9yX2lzX2luX3VzZXJfY29kZSA9IEZhbHNlXG4gICAgZm9yIHN0YWNrX2ZyYW1lIGluIHJldmVyc2VkX3RyYWNlYmFja19saXN0OlxuICAgICAgICBpZiBhbGwoW2tleXdvcmQgaW4gc3RhY2tfZnJhbWUgZm9yIGtleXdvcmQgaW4ga2V5d29yZHNfaW5faW5uZXJtb3N0X3J1bnB5X3N0YWNrX2ZyYW1lXSk6XG4gICAgICAgICAgICBlcnJvcl9pc19pbl91c2VyX2NvZGUgPSBUcnVlXG4gICAgICAgICAgICBicmVha1xuICAgICAgICByZXZlcnNlZF90cmltbWVkX3N0YWNrLmFwcGVuZChzdGFja19mcmFtZSlcbiAgICBpZiBlcnJvcl9pc19pbl91c2VyX2NvZGU6XG4gICAgICAgICMgRmluZCB0aGUgZmlyc3QgaW5kZXggb2YgJ1RyYWNlYmFjayAobW9zdCByZWNlbnQgY2FsbCBsYXN0KTonIGluIHJldmVyc2VkIGxpc3QgYW5kIGFwcGVuZCB0aGUgY2F1c2UgZXhjZXB0aW9uc1xuICAgICAgICAjIFRoaXMgd2lsbCBoYW5kbGUgdXNlcnMgdXNpbmcgJ2Zyb20gd2l0aCByYWlzZScgd2hlbiByYWlzaW5nIGV4Y2VwdGlvblxuICAgICAgICByZXZlcnNlZF90cmFjZWJhY2tfYXNfbGlzdCA9IHRyYWNlYmFja19hc19saXN0Wzo6LTFdXG4gICAgICAgIHRyYWNlYmFja19pbmRleGVzID0gW2lkeCBmb3IgaWR4LHN0YWNrX2ZyYW1lIGluIGVudW1lcmF0ZShyZXZlcnNlZF90cmFjZWJhY2tfYXNfbGlzdClcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgaWYgJ1RyYWNlYmFjayAobW9zdCByZWNlbnQgY2FsbCBsYXN0KTonIGluIHN0YWNrX2ZyYW1lXVxuICAgICAgICBpZiBsZW4odHJhY2ViYWNrX2luZGV4ZXMpID4gMDpcbiAgICAgICAgICAgIHJldmVyc2VkX3RyaW1tZWRfc3RhY2suZXh0ZW5kKHJldmVyc2VkX3RyYWNlYmFja19hc19saXN0W3RyYWNlYmFja19pbmRleGVzWzBdOl0pXG5cbiAgICByZXR1cm4gbGlzdChyZXZlcnNlZChyZXZlcnNlZF90cmltbWVkX3N0YWNrKSlcblxuZGVmIHNldF90YWdzX2Zvcl9tbGZsb3dfcnVuKCk6XG4gICAgIyBQcmVwYXJlIE1MZmxvdyBpbnRlZ3JhdGlvbiBpZiBzdXBwb3J0ZWRcbiAgICB0cnk6XG4gICAgICAgIGZyb20gYXp1cmVtbC5jb3JlLnJ1biBpbXBvcnQgUnVuXG4gICAgICAgIGZyb20gYXp1cmVtbC5tbGZsb3cgaW1wb3J0IF9zZXR1cF9yZW1vdGVcbiAgICAgICAgcnVuID0gUnVuLmdldF9jb250ZXh0KCkgXG4gICAgICAgIF9zZXR1cF9yZW1vdGUocnVuKVxuICAgIGV4Y2VwdCBFeGNlcHRpb246XG4gICAgICAgIHJldHVyblxuXG5kZWYgbWFpbigpOlxuICAgICMgVGhpcyB1c2VkIHRvIGJlIGRvbmUgaW4gYSBjb250ZXh0X21hbmFnZXJzLnB5IGFuZCBjb250ZXh0X21hbmFnZXJfaW5qZWN0b3IucHkgd2hlcmUgaXQgd2lsbCBhZGQgY3VycmVudCB3b3JraW5nXG4gICAgIyBkaXJlY3RvcnkgYW5kIHRoZSBzY3JpcHQncyBkaXJlY3RvcnkgdG8gc3lzLnBhdGggcmVzcGVjdGl2ZWx5LlxuICAgICMgV2Ugd2FudCB0byBtYWtlIHN1cmUgdGhlIHNjcmlwdCdzIGRpcmVjdG9yeSBpcyBhZGRlZCB0byB0aGUgc3RhcnQgb2Ygc3lzLnBhdGggc28gdGhhdCBpdCBpcyBzZWFyY2hlZFxuICAgICMgZmlyc3QgYW5kIHRoZSBjdXJyZW50IHdvcmtpbmcgZGlyZWN0b3J5IGlzIGFkZGVkIHRvIHRoZSBlbmQgc28gdGhhdCBpdCBpcyBzZWFyY2hlZCBsYXN0LlxuICAgIHN5cy5wYXRoLmluc2VydCgwLCBvcy5wYXRoLmRpcm5hbWUob3MucGF0aC5hYnNwYXRoKHN5cy5hcmd2WzFdKSkpXG4gICAgc3lzLnBhdGguYXBwZW5kKG9zLmdldGN3ZCgpKVxuXG4gICAgdHJ5OlxuICAgICAgICAjIFRoZSBSdW4gaW1wb3J0IGJlbG93IGlzIG9ubHkgbmVlZGVkIHRvIGF2b2lkIGNpcmN1bGFyIGRlcGVuZGVuY3kgaW1wb3J0IGlzc3VlXG4gICAgICAgICMgaW4gdGhlIGNvbnRleHQgbWFuYWdlcidzIGV4aXQgY2FsbHNcbiAgICAgICAgZnJvbSBhenVyZW1sLmNvcmUgaW1wb3J0IFJ1blxuICAgICAgICBmcm9tIGF6dXJlbWwuX2hpc3RvcnkudXRpbHMuY29udGV4dF9tYW5hZ2VycyBpbXBvcnQgU2VuZFJ1bktpbGxTaWduYWxcblxuICAgICAgICAjIE9ubHkgZG8gdGhpcyBjaGVjayBpZiBBenVyZU1MIGlzIHVzZWRcbiAgICAgICAgaWYgc3lzLnZlcnNpb25faW5mby5tYWpvciAhPSAzIG9yIHN5cy52ZXJzaW9uX2luZm8ubWlub3IgPCA1OlxuICAgICAgICAgICAgcmFpc2UgUnVudGltZUVycm9yKGYnUHl0aG9uIHZlcnNpb24ge3N0cihzeXMudmVyc2lvbl9pbmZvKX0gaXMgbm90IHN1cHBvcnRlZC4gUGxlYXNlIHVzZSBweXRob24+PTMuNScpXG5cbiAgICAgICAgIyBUaGUgU2VuZFJ1bktpbGxTaWduYWwgY29udGV4dCBtYW5hZ2VyIGlzIG1pc2xlYWRpbmdseSBuYW1lZC4gSXQgaXMgYWN0dWFsbHkgdXNlZCB0byBmbHVzaCBtZXRyaWNzIG9mXG4gICAgICAgICMgYWxsIHRoZSBSdW5IaXN0b3J5RmFjYWRlIGluc3RhbmNlcy4gVGhlIHdheSBpdCBkb2VzIHRoYXQgaXMgdGhlIFJ1bkhpc3RvcnlGYWNhZGUncyBjb25zdHJ1Y3RvciByZWdpc3RlcnNcbiAgICAgICAgIyBhIGNsZWFuIHVwIGhhbmRsZXIgdGhhdCBjYWxscyBmbHVzaCBvbiB0aGUgbWV0cmljcyBjbGllbnQgaXQgaGFzLCB0aGUgaGFuZGxlciBpdHNlbGYgaXMgcmVnaXN0ZXJlZCB0b1xuICAgICAgICAjIGEgY2xhc3MgdmFyaWFibGUgb2YgdGhlIFJ1bkhpc3RvcnlGYWNhZGUgY2xhc3MuIFRoZSBTZW5kUnVuS2lsbFNpZ25hbCBjb250ZXh0IG1hbmFnZXIncyBleGl0IG1ldGhvZFxuICAgICAgICAjIGNhbGxzIHRoZSBSdW5IaXN0b3J5RmFjYWRlLl9raWxsIGNsYXNzIG1ldGhvZCB3aGljaCBnb2VzIGFuZCBjYWxscyB0aGUgYWxsIG9mIHRoZSByZWdpc3RlcmVkIGV4aXQgaGFuZGxlcnNcbiAgICAgICAgIyB3aGljaCBpbiB0dXJuIGZsdXNoZXMgdGhlIG1ldHJpY3MuIFRoZSBjb2RlIGJlbG93IGlzIGNvcGllZCBmcm9tIHRoZSBydW4gaGlzdG9yeSBjb250ZXh0IG1hbmFnZXIgY29kZS5cbiAgICAgICAgc2VuZF9raWxsX3NpZ25hbCA9IG5vdCBvcy5lbnZpcm9uLmdldCgnQVpVUkVNTF9ESVNBQkxFX1JVTl9LSUxMX1NJR05BTCcpXG4gICAgICAgIGtpbGxfc2lnbmFsX3RpbWVvdXQgPSBmbG9hdChvcy5lbnZpcm9uLmdldCgnQVpVUkVNTF9SVU5fS0lMTF9TSUdOQUxfVElNRU9VVF9TRUMnLCAnMzAwJykpXG4gICAgICAgIGNvbnRleHQgPSBTZW5kUnVuS2lsbFNpZ25hbChzZW5kX2tpbGxfc2lnbmFsLCBraWxsX3NpZ25hbF90aW1lb3V0KVxuICAgIGV4Y2VwdCBJbXBvcnRFcnJvcjpcbiAgICAgICAgY29udGV4dCA9IE5vb3BDb250ZXh0TWFuYWdlcigpXG4gICAgZXhjZXB0IFJ1bnRpbWVFcnJvcjpcbiAgICAgICAgcmFpc2VcbiAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGU6XG4gICAgICAgIHByaW50KGYnV2FybmluZzogRmFpbGVkIHRvIHNldHVwIEF6dXJlIE1hY2hpbmUgTGVhcm5pbmcgc3lzdGVtIGNvZGUgZHVlIHRvIGB7ZX1gLiBZb3VyIGpvYiB3aWxsIHByb2NlZWQgYnV0IGlmIHlvdSBub3RpY2UgYW55IGlzc3VlcywgcGxlYXNlIGNvbnRhY3QgQXp1cmUgU3VwcG9ydCB3aXRoIHRoaXMgZXhjZXB0aW9uIG1lc3NhZ2UuJywgZmlsZT1zeXMuc3RkZXJyKVxuICAgICAgICBjb250ZXh0ID0gTm9vcENvbnRleHRNYW5hZ2VyKClcbiAgICAgICAgXG4gICAgc2V0X3RhZ3NfZm9yX21sZmxvd19ydW4oKVxuXG4gICAgY29udGV4dCA9IEVycm9ySGFuZGxlckNvbnRleHRNYW5hZ2VyKGNvbnRleHQpXG4gICAgd2l0aCBjb250ZXh0OlxuICAgICAgICAjIHdoZW4gd2UgaW52b2tlIHdpdGggYHB5dGhvbiAtYyBwcm9ncmFtIGFyZ3NgLCBzeXMuYXJndlswXSB3aWxsIGJlIC1jLCBhcmdzIHdpbGwgYmUgdGhlIHJlc3QgKGkuZS4gc3lzLmFyZ3ZbMTpdKVxuICAgICAgICBleHBhbmRlZF9hcmd2ID0gW11cbiAgICAgICAgZm9yIGFyZyBpbiBzeXMuYXJndlsxOl06XG4gICAgICAgICAgICBhcmcgPSBvcy5wYXRoLmV4cGFuZHZhcnMoYXJnKVxuICAgICAgICAgICAgZXhwYW5kZWRfYXJndi5hcHBlbmQoYXJnKVxuICAgICAgICBzeXMuYXJndiA9IGV4cGFuZGVkX2FyZ3ZcbiAgICAgICAgcnVucHkucnVuX3BhdGgoc3lzLmFyZ3ZbMF0sIGdsb2JhbHMoKSwgcnVuX25hbWU9J19fbWFpbl9fJylcblxuaWYgX19uYW1lX18gPT0gJ19fbWFpbl9fJzpcbiAgICB0cnk6XG4gICAgICAgIG1haW4oKVxuICAgIGV4Y2VwdCBTeXN0ZW1FeGl0IGFzIGV4OlxuICAgICAgICAjIENvcGllZCBmcm9tIGNvbnRleHQgbWFuYWdlciBpbmplY3RvclxuICAgICAgICBleGNfdHlwZSwgZXhjX3ZhbCwgZXhjX3RyYWNlYmFjayA9IHN5cy5leGNfaW5mbygpXG4gICAgICAgIHByaW50KCcnLmpvaW4oc3RyaXBfc3RhY2tfb2ZfYXp1cmVtbF9sYXllcnMoZXhjX3R5cGUsIGV4Y192YWwsIGV4Y190cmFjZWJhY2spKSwgZmlsZT1zeXMuc3RkZXJyKVxuICAgICAgICBpZiBleC5jb2RlIGlzIG5vdCBOb25lOlxuICAgICAgICAgICAgc3lzLmV4aXQoZXguY29kZSlcbiAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGV4OlxuICAgICAgICAjIENvcGllZCBmcm9tIGNvbnRleHQgbWFuYWdlciBpbmplY3RvclxuICAgICAgICBleGNfdHlwZSwgZXhjX3ZhbCwgZXhjX3RyYWNlYmFjayA9IHN5cy5leGNfaW5mbygpXG4gICAgICAgIHByaW50KCcnLmpvaW4oc3RyaXBfc3RhY2tfb2ZfYXp1cmVtbF9sYXllcnMoZXhjX3R5cGUsIGV4Y192YWwsIGV4Y190cmFjZWJhY2spKSwgZmlsZT1zeXMuc3RkZXJyKVxuICAgICAgICBzeXMuZXhpdCgxKVxuIiwidXJsZGVjb2RlX2ludm9rZXIucHkiLCJweXRob24iLCItbSIsImF6dXJlbWwuc3R1ZGlvLm1vZHVsZWhvc3QubW9kdWxlX2ludm9rZXIiLCItLW1vZHVsZS1uYW1lPWF6dXJlbWwuc3R1ZGlvLm1vZHVsZXMuZGF0YXRyYW5zZm9ybS5tYW5pcHVsYXRpb24uc2VsZWN0X2NvbHVtbnMuc2VsZWN0X2NvbHVtbnMiLCItLXJlc3VsdHMtZGF0YXNldCIsIiRBWlVSRV9NTF9PVVRQVVRfUmVzdWx0c19kYXRhc2V0IiwiLS1kYXRhc2V0PSRBWlVSRU1MX0RBVEFSRUZFUkVOQ0VfRGF0YXNldCIsIi0tc2VsZWN0LWNvbHVtbnM9JTI1N0IlMjUyMmlzRmlsdGVyJTI1MjIlMjUzQXRydWUlMjUyQyUyNTIycnVsZXMlMjUyMiUyNTNBJTI1NUIlMjU3QiUyNTIyZXhjbHVkZSUyNTIyJTI1M0FmYWxzZSUyNTJDJTI1MjJydWxlVHlwZSUyNTIyJTI1M0ElMjUyMkFsbENvbHVtbnMlMjUyMiUyNTdEJTI1MkMlMjU3QiUyNTIyZXhjbHVkZSUyNTIyJTI1M0F0cnVlJTI1MkMlMjUyMnJ1bGVUeXBlJTI1MjIlMjUzQSUyNTIyQ29sdW1uTmFtZXMlMjUyMiUyNTJDJTI1MjJjb2x1bW5zJTI1MjIlMjUzQSUyNTVCJTI1MjJub3JtYWxpemVkLWxvc3NlcyUyNTIyJTI1NUQlMjU3RCUyNTVEJTI1N0QiXSwic3VjY2Vzc19yZXR1cm5fY29kZSI6eyJ6ZXJvIjp7ImFkZGl0aW9uYWxfY29kZXMiOltdfX19LCJzdGRlcnIiOm51bGwsInN0ZG91dCI6InVzZXJfbG9ncy9zdGRfbG9nLnR4dCJ9fX1dLCJleGVjdXRpb25fZW52aXJvbm1lbnQiOlt7Im5hbWUiOiJBWlVSRU1MX0FSTV9QUk9KRUNUX05BTUUiLCJ2YWx1ZSI6InRvbWFzZXhwZXJpbWVudCJ9LHsibmFtZSI6IkFaVVJFTUxfQVJNX1JFU09VUkNFR1JPVVAiLCJ2YWx1ZSI6ImF6dXJlbWwifSx7Im5hbWUiOiJBWlVSRU1MX0FSTV9TVUJTQ1JJUFRJT04iLCJ2YWx1ZSI6ImEwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NSJ9LHsibmFtZSI6IkFaVVJFTUxfQVJNX1dPUktTUEFDRV9OQU1FIiwidmFsdWUiOiJhenVyZW1sIn0seyJuYW1lIjoiQVpVUkVNTF9DUl9BWlVSRU1MX0NPTlRFWFQiLCJ2YWx1ZSI6IntcInN1YnNjcmlwdGlvbl9pZFwiOlwiYTBmNGE3MzMtNGZjZS00ZDQ5LWI4YTgtZDMwNTQxZmMxYjQ1XCIsXCJyZXNvdXJjZV9ncm91cFwiOlwiYXp1cmVtbFwiLFwid29ya3NwYWNlX25hbWVcIjpcImF6dXJlbWxcIixcIndvcmtzcGFjZV9pZFwiOlwiMTA0MDBjMTQtOTQ3Ny00MWFkLWE5MzUtZTk2M2Q4NTE2NTRiXCIsXCJzZXJ2aWNlX2VuZHBvaW50XCI6XCJodHRwczovL3dlc3RldXJvcGUuYXBpLmF6dXJlbWwubXNcIixcImRpc2NvdmVyeV9lbmRwb2ludFwiOlwiaHR0cHM6Ly93ZXN0ZXVyb3BlLmFwaS5henVyZW1sLm1zL2Rpc2NvdmVyeVwiLFwiZXhwZXJpbWVudF9uYW1lXCI6XCJ0b21hc2V4cGVyaW1lbnRcIixcImV4cGVyaW1lbnRfaWRcIjpcImU0MzYwYjcxLTViYTQtNDc4OS04ZTBjLWFiMDQwNDYyY2MwNlwiLFwicm9vdF9ydW5faWRcIjpcImY0YTZjNWViLTFmZWItNDlmZi05NDI5LTRlYzE1YjE1MzkzY1wiLFwicnVuX2lkXCI6XCI4OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjlcIixcInJ1bl90b2tlblwiOlwiZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklrVXlRVEJGTlRVMlJUTkRORFpGUWpnM1FUQTRSVEpGTVRCRU1ERkJRMEpEUTBVeU4wUXlSVE1pTENKMGVYQWlPaUpLVjFRaWZRLmV5SnliMnhsSWpvaVEyOXVkSEpwWW5WMGIzSWlMQ0p6WTI5d1pTSTZJaTl6ZFdKelkzSnBjSFJwYjI1ekwyRXdaalJoTnpNekxUUm1ZMlV0TkdRME9TMWlPR0U0TFdRek1EVTBNV1pqTVdJME5TOXlaWE52ZFhKalpVZHliM1Z3Y3k5aGVuVnlaVzFzTDNCeWIzWnBaR1Z5Y3k5TmFXTnliM052Wm5RdVRXRmphR2x1WlV4bFlYSnVhVzVuVTJWeWRtbGpaWE12ZDI5eWEzTndZV05sY3k5aGVuVnlaVzFzSWl3aVlXTmpiM1Z1ZEdsa0lqb2lNREF3TURBd01EQXRNREF3TUMwd01EQXdMVEF3TURBdE1EQXdNREF3TURBd01EQXdJaXdpZDI5eWEzTndZV05sU1dRaU9pSXhNRFF3TUdNeE5DMDVORGMzTFRReFlXUXRZVGt6TlMxbE9UWXpaRGcxTVRZMU5HSWlMQ0p3Y205cVpXTjBhV1FpT2lJd01EQXdNREF3TUMwd01EQXdMVEF3TURBdE1EQXdNQzB3TURBd01EQXdNREF3TURBaUxDSmthWE5qYjNabGNua2lPaUoxY21rNkx5OWthWE5qYjNabGNubDFjbWt2SWl3aWRHbGtJam9pTnpKbU9UZzRZbVl0T0RabU1TMDBNV0ZtTFRreFlXSXRNbVEzWTJRd01URmtZalEzSWl3aWIybGtJam9pTnpReU5HWmlOR010TldVNVppMDBOV05rTFRsbU4yUXRORFV6WkRRMU5qVTFaVGMxSWl3aWNIVnBaQ0k2SWpFd01ETkNSa1pFT1VSRE0wSTJPVVlpTENKcGMzTWlPaUpoZW5WeVpXMXNJaXdpWVhCd2FXUWlPaUpVYjIxaGN5QkxkV0pwWTJFaUxDSmxlSEFpT2pFMk5UazBNamc0TlRJc0ltRjFaQ0k2SW1GNmRYSmxiV3dpZlEuY0hubnBvSV9FSGpLbi11NlktWHpfQnJzaVp0S3M1Mzd1ekgySE05ZjROckYyVkpWdDExSHFjZkFjVm9tSFVabDZpVGU1Vy1DSlJoRW90QU9hSGV5VC1uck0zYXRXRTNtYlpFSjI2LW5CaWRiUTY4bzItSGZQY0lyOTJhUGpxamNubk1iY0J5enRCZklGWGlRakNwRTRqN1F6Rk5oZXdxTTlqQTc0czlkTUo4M2puSXJBa0V6VUxDc21LTnNFdjdOZzlzZUtFLWRSeVNQeUhaMlFscXM2MlFlX2V3WHJIVzhvdWZhMWd6ZVVWZEpxeGV5c3lvTWhMOVYySnl1d1E4OEdyNU9YUTNKVU4wb3RFN1l1dDZjaDZlSXdERUNNS2JmRm0tZnJQUXJiUUk3d3dFOFJxckZORXV0YUI5bW9DVHZzTXdIQmNlRTBnVFpTWXlZWUNZWnB3XCIsXCJydW5faGlzdG9yeV9zZXJ2aWNlX2VuZHBvaW50XCI6XCJodHRwczovL3dlc3RldXJvcGUuYXBpLmF6dXJlbWwubXNcIixcImRhdGFfY29udGFpbmVyX2lkXCI6XCJkY2lkLjg5YTAxZGE1LTkwN2YtNDJhNi05NmU0LThkMmU2YTIyYzg2OVwiLFwicnVuX3V1aWRcIjpcIjFjZmM3NGFhLWUzMzMtNDZlOS1iNzc2LTcyZjgyYWIyNjc5MFwifSJ9LHsibmFtZSI6IkFaVVJFTUxfQ1JfQ09NUFVURV9DT05URVhUIiwidmFsdWUiOiJ7XCJjbHVzdGVyX25hbWVcIjpcIms4cy1jb21wdXRlXCIsXCJub2RlX2lkXCI6e1wiRW52aXJvbm1lbnRWYXJpYWJsZVwiOlwiUE9EX05BTUVcIn0sXCJ2bV9pZFwiOm51bGwsXCJydW5fYXR0ZW1wdF9jb3VudFwiOjEsXCJncHVfY291bnRcIjowLFwidm1fc2l6ZVwiOm51bGwsXCJyZWFkYWJsZV9jbHVzdGVyX25hbWVcIjpudWxsLFwidm1fcHJpb3JpdHlcIjpudWxsLFwidXNlX3ZuZXRfb3JfcHJpdmF0ZV9saW5rXCI6ZmFsc2V9In0seyJuYW1lIjoiQVpVUkVNTF9DUl9DT1JSRUxBVElPTl9JRCIsInZhbHVlIjoiODlhMDFkYTUtOTA3Zi00MmE2LTk2ZTQtOGQyZTZhMjJjODY5In0seyJuYW1lIjoiQVpVUkVNTF9DUl9ESVNUUklCVVRFRF9DT05GSUciLCJ2YWx1ZSI6IntcInJhbmtcIjpcIlZLX1RBU0tfSU5ERVhcIixcImhvc3RfbGlzdFwiOltcImF6dXJlbWwtd29ya2xvYWRzLThiMjgyMWNjZGM5YzlmYjgxODUwMmMwZTY5Yjk2NTcyLXdvcmtlci0wLmF6dXJlbWwtd29ya2xvYWRzLThiMjgyMWNjZGM5YzlmYjgxODUwMmMwZTY5Yjk2NTcyLmF6dXJlbWwtd29ya2xvYWRzLnN2Yy5jbHVzdGVyLmxvY2FsXCJdLFwicmVtb3RlX2dycGNcIjp7XCJUY3BcIjp7XCJsaWZlY3ljbGVyX3BvcnRcIjoxMzMzMyxcImV4ZWN1dG9yX3BvcnRcIjoxMzMzNH19fSJ9LHsibmFtZSI6IkFaVVJFTUxfQ1JfVEVMRU1FVFJZX0NPTkZJRyIsInZhbHVlIjoie1wiY29sbGVjdG9yXCI6e1wicmVjZWl2ZXJcIjpudWxsLFwiZXhwb3J0ZXJcIjp7XCJhcHBpbnNpZ2h0c1wiOntcImluc3RydW1lbnRhdGlvbl9rZXlcIjpcImZjYTVhNGM5LWFkYjQtNDRhZS1iZWNlLTY5ZTJjYzkxZmY2NlwifSxcImphZWdlclwiOm51bGwsXCJ0aW1lb3V0X21pbGxpc1wiOm51bGwsXCJsZXZlbFwiOm51bGx9fSxcImxvZ2dlclwiOntcImNvbnNvbGVcIjpudWxsLFwiYXBwaW5zaWdodHNcIjp7XCJpbnN0cnVtZW50YXRpb25fa2V5XCI6XCJmY2E1YTRjOS1hZGI0LTQ0YWUtYmVjZS02OWUyY2M5MWZmNjZcIixcImxldmVsXCI6XCJpbmZvXCIsXCJlbmFibGVkXCI6dHJ1ZX0sXCJmaWxlXCI6e1wiZXh0ZW5zaW9uXCI6XCJsb2dcIixcImxldmVsXCI6XCJpbmZvXCIsXCJlbmFibGVkXCI6dHJ1ZX19LFwibm9kZV9yYW5rXCI6XCJWS19UQVNLX0lOREVYXCIsXCJub2RlX2lkXCI6bnVsbCxcImRpc2FibGVfc2Vuc2l0aXZlX3NjcnViXCI6bnVsbH0ifSx7Im5hbWUiOiJBWlVSRU1MX0RBVEFTRVRfRklMRV9PVVRQVVRTIiwidmFsdWUiOiJSZXN1bHRzX2RhdGFzZXQifSx7Im5hbWUiOiJBWlVSRU1MX0RJU0NPVkVSWV9TRVJWSUNFX0VORFBPSU5UIiwidmFsdWUiOiJodHRwczovL3dlc3RldXJvcGUuYXBpLmF6dXJlbWwubXMvZGlzY292ZXJ5In0seyJuYW1lIjoiQVpVUkVNTF9FWFBFUklNRU5UX0lEIiwidmFsdWUiOiJlNDM2MGI3MS01YmE0LTQ3ODktOGUwYy1hYjA0MDQ2MmNjMDYifSx7Im5hbWUiOiJBWlVSRU1MX0VYUEVSSU1FTlRfU0NPUEUiLCJ2YWx1ZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sL2V4cGVyaW1lbnRzL3RvbWFzZXhwZXJpbWVudCJ9LHsibmFtZSI6IkFaVVJFTUxfUEFSQU1FVEVSX05vZGVfQ291bnQiLCJ2YWx1ZSI6IjEifSx7Im5hbWUiOiJBWlVSRU1MX1BBUkFNRVRFUl9TZWxlY3RfQ29sdW1ucyIsInZhbHVlIjoiJTdCJTIyaXNGaWx0ZXIlMjIlM0F0cnVlJTJDJTIycnVsZXMlMjIlM0ElNUIlN0IlMjJleGNsdWRlJTIyJTNBZmFsc2UlMkMlMjJydWxlVHlwZSUyMiUzQSUyMkFsbENvbHVtbnMlMjIlN0QlMkMlN0IlMjJleGNsdWRlJTIyJTNBdHJ1ZSUyQyUyMnJ1bGVUeXBlJTIyJTNBJTIyQ29sdW1uTmFtZXMlMjIlMkMlMjJjb2x1bW5zJTIyJTNBJTVCJTIybm9ybWFsaXplZC1sb3NzZXMlMjIlNUQlN0QlNUQlN0QifSx7Im5hbWUiOiJBWlVSRU1MX1JPT1RfUlVOX0lEIiwidmFsdWUiOiJmNGE2YzVlYi0xZmViLTQ5ZmYtOTQyOS00ZWMxNWIxNTM5M2MifSx7Im5hbWUiOiJBWlVSRU1MX1JVTl9ISVNUT1JZX1NFUlZJQ0VfRU5EUE9JTlQiLCJ2YWx1ZSI6Imh0dHBzOi8vd2VzdGV1cm9wZS5hcGkuYXp1cmVtbC5tcyJ9LHsibmFtZSI6IkFaVVJFTUxfUlVOX0lEIiwidmFsdWUiOiI4OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjkifSx7Im5hbWUiOiJBWlVSRU1MX1JVTl9UT0tFTiIsInZhbHVlIjoiZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklrVXlRVEJGTlRVMlJUTkRORFpGUWpnM1FUQTRSVEpGTVRCRU1ERkJRMEpEUTBVeU4wUXlSVE1pTENKMGVYQWlPaUpLVjFRaWZRLmV5SnliMnhsSWpvaVEyOXVkSEpwWW5WMGIzSWlMQ0p6WTI5d1pTSTZJaTl6ZFdKelkzSnBjSFJwYjI1ekwyRXdaalJoTnpNekxUUm1ZMlV0TkdRME9TMWlPR0U0TFdRek1EVTBNV1pqTVdJME5TOXlaWE52ZFhKalpVZHliM1Z3Y3k5aGVuVnlaVzFzTDNCeWIzWnBaR1Z5Y3k5TmFXTnliM052Wm5RdVRXRmphR2x1WlV4bFlYSnVhVzVuVTJWeWRtbGpaWE12ZDI5eWEzTndZV05sY3k5aGVuVnlaVzFzSWl3aVlXTmpiM1Z1ZEdsa0lqb2lNREF3TURBd01EQXRNREF3TUMwd01EQXdMVEF3TURBdE1EQXdNREF3TURBd01EQXdJaXdpZDI5eWEzTndZV05sU1dRaU9pSXhNRFF3TUdNeE5DMDVORGMzTFRReFlXUXRZVGt6TlMxbE9UWXpaRGcxTVRZMU5HSWlMQ0p3Y205cVpXTjBhV1FpT2lJd01EQXdNREF3TUMwd01EQXdMVEF3TURBdE1EQXdNQzB3TURBd01EQXdNREF3TURBaUxDSmthWE5qYjNabGNua2lPaUoxY21rNkx5OWthWE5qYjNabGNubDFjbWt2SWl3aWRHbGtJam9pTnpKbU9UZzRZbVl0T0RabU1TMDBNV0ZtTFRreFlXSXRNbVEzWTJRd01URmtZalEzSWl3aWIybGtJam9pTnpReU5HWmlOR010TldVNVppMDBOV05rTFRsbU4yUXRORFV6WkRRMU5qVTFaVGMxSWl3aWNIVnBaQ0k2SWpFd01ETkNSa1pFT1VSRE0wSTJPVVlpTENKcGMzTWlPaUpoZW5WeVpXMXNJaXdpWVhCd2FXUWlPaUpVYjIxaGN5QkxkV0pwWTJFaUxDSmxlSEFpT2pFMk5UazBNamc0TlRJc0ltRjFaQ0k2SW1GNmRYSmxiV3dpZlEuY0hubnBvSV9FSGpLbi11NlktWHpfQnJzaVp0S3M1Mzd1ekgySE05ZjROckYyVkpWdDExSHFjZkFjVm9tSFVabDZpVGU1Vy1DSlJoRW90QU9hSGV5VC1uck0zYXRXRTNtYlpFSjI2LW5CaWRiUTY4bzItSGZQY0lyOTJhUGpxamNubk1iY0J5enRCZklGWGlRakNwRTRqN1F6Rk5oZXdxTTlqQTc0czlkTUo4M2puSXJBa0V6VUxDc21LTnNFdjdOZzlzZUtFLWRSeVNQeUhaMlFscXM2MlFlX2V3WHJIVzhvdWZhMWd6ZVVWZEpxeGV5c3lvTWhMOVYySnl1d1E4OEdyNU9YUTNKVU4wb3RFN1l1dDZjaDZlSXdERUNNS2JmRm0tZnJQUXJiUUk3d3dFOFJxckZORXV0YUI5bW9DVHZzTXdIQmNlRTBnVFpTWXlZWUNZWnB3In0seyJuYW1lIjoiQVpVUkVNTF9TRVJWSUNFX0VORFBPSU5UIiwidmFsdWUiOiJodHRwczovL3dlc3RldXJvcGUuYXBpLmF6dXJlbWwubXMifSx7Im5hbWUiOiJBWlVSRU1MX1dPUktTUEFDRV9JRCIsInZhbHVlIjoiMTA0MDBjMTQtOTQ3Ny00MWFkLWE5MzUtZTk2M2Q4NTE2NTRiIn0seyJuYW1lIjoiQVpVUkVNTF9XT1JLU1BBQ0VfU0NPUEUiLCJ2YWx1ZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIn0seyJuYW1lIjoiREFUQVNFVF9NT1VOVF9CTE9DS19CQVNFRF9DQUNIRV9FTkFCTEVEIiwidmFsdWUiOiJ0cnVlIn0seyJuYW1lIjoiREFUQVNFVF9SU0xFWF9VUExPQUQiLCJ2YWx1ZSI6InRydWUifSx7Im5hbWUiOiJFWEFNUExFX0VOVl9WQVIiLCJ2YWx1ZSI6IkVYQU1QTEVfVkFMVUUifSx7Im5hbWUiOiJNTEZMT1dfRVhQRVJJTUVOVF9JRCIsInZhbHVlIjoiZTQzNjBiNzEtNWJhNC00Nzg5LThlMGMtYWIwNDA0NjJjYzA2In0seyJuYW1lIjoiTUxGTE9XX0VYUEVSSU1FTlRfTkFNRSIsInZhbHVlIjoidG9tYXNleHBlcmltZW50In0seyJuYW1lIjoiTUxGTE9XX1JVTl9JRCIsInZhbHVlIjoiODlhMDFkYTUtOTA3Zi00MmE2LTk2ZTQtOGQyZTZhMjJjODY5In0seyJuYW1lIjoiTUxGTE9XX1RSQUNLSU5HX1RPS0VOIiwidmFsdWUiOiJleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWtVeVFUQkZOVFUyUlRORE5EWkZRamczUVRBNFJUSkZNVEJFTURGQlEwSkRRMFV5TjBReVJUTWlMQ0owZVhBaU9pSktWMVFpZlEuZXlKeWIyeGxJam9pUTI5dWRISnBZblYwYjNJaUxDSnpZMjl3WlNJNklpOXpkV0p6WTNKcGNIUnBiMjV6TDJFd1pqUmhOek16TFRSbVkyVXROR1EwT1MxaU9HRTRMV1F6TURVME1XWmpNV0kwTlM5eVpYTnZkWEpqWlVkeWIzVndjeTloZW5WeVpXMXNMM0J5YjNacFpHVnljeTlOYVdOeWIzTnZablF1VFdGamFHbHVaVXhsWVhKdWFXNW5VMlZ5ZG1salpYTXZkMjl5YTNOd1lXTmxjeTloZW5WeVpXMXNJaXdpWVdOamIzVnVkR2xrSWpvaU1EQXdNREF3TURBdE1EQXdNQzB3TURBd0xUQXdNREF0TURBd01EQXdNREF3TURBd0lpd2lkMjl5YTNOd1lXTmxTV1FpT2lJeE1EUXdNR014TkMwNU5EYzNMVFF4WVdRdFlUa3pOUzFsT1RZelpEZzFNVFkxTkdJaUxDSndjbTlxWldOMGFXUWlPaUl3TURBd01EQXdNQzB3TURBd0xUQXdNREF0TURBd01DMHdNREF3TURBd01EQXdNREFpTENKa2FYTmpiM1psY25raU9pSjFjbWs2THk5a2FYTmpiM1psY25sMWNta3ZJaXdpZEdsa0lqb2lOekptT1RnNFltWXRPRFptTVMwME1XRm1MVGt4WVdJdE1tUTNZMlF3TVRGa1lqUTNJaXdpYjJsa0lqb2lOelF5TkdaaU5HTXROV1U1WmkwME5XTmtMVGxtTjJRdE5EVXpaRFExTmpVMVpUYzFJaXdpY0hWcFpDSTZJakV3TUROQ1JrWkVPVVJETTBJMk9VWWlMQ0pwYzNNaU9pSmhlblZ5Wlcxc0lpd2lZWEJ3YVdRaU9pSlViMjFoY3lCTGRXSnBZMkVpTENKbGVIQWlPakUyTlRrME1qZzROVElzSW1GMVpDSTZJbUY2ZFhKbGJXd2lmUS5jSG5ucG9JX0VIaktuLXU2WS1Yel9CcnNpWnRLczUzN3V6SDJITTlmNE5yRjJWSlZ0MTFIcWNmQWNWb21IVVpsNmlUZTVXLUNKUmhFb3RBT2FIZXlULW5yTTNhdFdFM21iWkVKMjYtbkJpZGJRNjhvMi1IZlBjSXI5MmFQanFqY25uTWJjQnl6dEJmSUZYaVFqQ3BFNGo3UXpGTmhld3FNOWpBNzRzOWRNSjgzam5JckFrRXpVTENzbUtOc0V2N05nOXNlS0UtZFJ5U1B5SFoyUWxxczYyUWVfZXdYckhXOG91ZmExZ3plVVZkSnF4ZXlzeW9NaEw5VjJKeXV3UTg4R3I1T1hRM0pVTjBvdEU3WXV0NmNoNmVJd0RFQ01LYmZGbS1mclBRcmJRSTd3d0U4UnFyRk5FdXRhQjltb0NUdnNNd0hCY2VFMGdUWlNZeVlZQ1lacHcifSx7Im5hbWUiOiJNTEZMT1dfVFJBQ0tJTkdfVVJJIiwidmFsdWUiOiJhenVyZW1sOi8vd2VzdGV1cm9wZS5hcGkuYXp1cmVtbC5tcy9tbGZsb3cvdjEuMC9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIn1dLCJleGVjdXRvcl9hZGRyZXNzIjoiMC4wLjAuMDoxMzMzNCIsImxpZmVjeWNsZXJfYWRkcmVzcyI6IjAuMC4wLjA6MTMzMzMiLCJlcnJvcl9maWxlIjoiL3RtcC9henVyZW1sL2NyL2ovMWNmYzc0YWFlMzMzNDZlOWI3NzY3MmY4MmFiMjY3OTAvY2FwL2xpZmVjeWNsZXIvd2QvdGVybWluYXRpb24tbG9nIiwiZGlzdHJpYnV0ZWRfY29uZmlnIjp7InJhbmsiOiJWS19UQVNLX0lOREVYIiwiaG9zdF9saXN0IjpbImF6dXJlbWwtd29ya2xvYWRzLThiMjgyMWNjZGM5YzlmYjgxODUwMmMwZTY5Yjk2NTcyLXdvcmtlci0wLmF6dXJlbWwtd29ya2xvYWRzLThiMjgyMWNjZGM5YzlmYjgxODUwMmMwZTY5Yjk2NTcyLmF6dXJlbWwtd29ya2xvYWRzLnN2Yy5jbHVzdGVyLmxvY2FsIl0sInJlbW90ZV9ncnBjIjp7IlRjcCI6eyJsaWZlY3ljbGVyX3BvcnQiOjEzMzMzLCJleGVjdXRvcl9wb3J0IjoxMzMzNH19fSwibGlmZWN5Y2xlcl9jb25maWciOnsiZW5hYmxlX3Rlcm1pbmF0aW9uX3NpZ25hbF9oYW5kbGluZyI6dHJ1ZX19
    - name: AZUREML_ARM_WORKSPACE_NAME
      value: azureml
    - name: AZUREML_ARM_SUBSCRIPTION
      value: a0f4a733-4fce-4d49-b8a8-d30541fc1b45
    - name: AZUREML_ARM_PROJECT_NAME
      value: tomasexperiment
    - name: AZUREML_DISCOVERY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms/discovery
    - name: AZUREML_RUN_HISTORY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_WORKSPACE_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml
    - name: AZUREML_CR_AZUREML_CONTEXT
      value: '{"subscription_id":"a0f4a733-4fce-4d49-b8a8-d30541fc1b45","resource_group":"azureml","workspace_name":"azureml","workspace_id":"10400c14-9477-41ad-a935-e963d851654b","service_endpoint":"https://westeurope.api.azureml.ms","discovery_endpoint":"https://westeurope.api.azureml.ms/discovery","experiment_name":"tomasexperiment","experiment_id":"e4360b71-5ba4-4789-8e0c-ab040462cc06","root_run_id":"f4a6c5eb-1feb-49ff-9429-4ec15b15393c","run_id":"89a01da5-907f-42a6-96e4-8d2e6a22c869","run_token":"eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw","run_history_service_endpoint":"https://westeurope.api.azureml.ms","data_container_id":"dcid.89a01da5-907f-42a6-96e4-8d2e6a22c869","run_uuid":"1cfc74aa-e333-46e9-b776-72f82ab26790"}'
    - name: AZUREML_WORKSPACE_ID
      value: 10400c14-9477-41ad-a935-e963d851654b
    - name: AZUREML_EXPERIMENT_ID
      value: e4360b71-5ba4-4789-8e0c-ab040462cc06
    - name: AZUREML_RUN_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_EXPERIMENT_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml/experiments/tomasexperiment
    - name: AZUREML_ROOT_RUN_ID
      value: f4a6c5eb-1feb-49ff-9429-4ec15b15393c
    - name: AZUREML_RUN_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw
    - name: AZUREML_ARM_RESOURCEGROUP
      value: azureml
    - name: AZUREML_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_CR_COMPUTE_CONTEXT
      value: '{"cluster_name":"k8s-compute","node_id":{"EnvironmentVariable":"POD_NAME"},"vm_id":null,"run_attempt_count":1,"gpu_count":0,"vm_size":null,"readable_cluster_name":null,"vm_priority":null,"use_vnet_or_private_link":false}'
    - name: AZUREML_CR_DISTRIBUTED_CONFIG
      value: '{"rank":"VK_TASK_INDEX","host_list":["azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0.azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572.azureml-workloads.svc.cluster.local"[],"remote_grpc":{"Tcp":{"lifecycler_port":13333,"executor_port":13334}}}'
    - name: AZUREML_CR_TELEMETRY_CONFIG
      value: '{"collector":{"receiver":null,"exporter":{"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66"},"jaeger":null,"timeout_millis":null,"level":null}},"logger":{"console":null,"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66","level":"info","enabled":true},"file":{"extension":"log","level":"info","enabled":true}},"node_rank":"VK_TASK_INDEX","node_id":null,"disable_sensitive_scrub":null}'
    - name: AZUREML_CR_GRPC_ADDRESS_BASE
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
    - name: AZUREML_CR_DATA_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/data-capability:0
    - name: AZUREML_CR_DATA_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
    - name: AZUREML_CR_DATA_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-data-capability
    - name: AZUREML_CR_CS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/cs-capability:0
    - name: AZUREML_CR_CS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
    - name: AZUREML_CR_CS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-cs-capability
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/hosttools-capability:0
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-hosttools-capability
    - name: AZUREML_CR_EXECUTION_WORKING_DIR_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
    - name: AZUREML_DATASET_FILE_OUTPUTS
      value: Results_dataset
    - name: AZUREML_PARAMETER_Select_Columns
      value: '%7B%22isFilter%22%3Atrue%2C%22rules%22%3A%5B%7B%22exclude%22%3Afalse%2C%22ruleType%22%3A%22AllColumns%22%7D%2C%7B%22exclude%22%3Atrue%2C%22ruleType%22%3A%22ColumnNames%22%2C%22columns%22%3A%5B%22normalized-losses%22%5D%7D%5D%7D'
    - name: DATASET_MOUNT_BLOCK_BASED_CACHE_ENABLED
      value: "true"
    - name: AZUREML_PARAMETER_Node_Count
      value: "1"
    - name: DATASET_RSLEX_UPLOAD
      value: "true"
    - name: AZUREML_CR_CORRELATION_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_CR_LIFECYCLER_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
    - name: POD_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.name
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.namespace
    - name: POD_IP
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: status.podIP
    - name: NODE_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: spec.nodeName
    - name: VC_WORKER_HOSTS
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_HOSTS
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VC_WORKER_NUM
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_NUM
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VK_TASK_INDEX
      value: "0"
    - name: VC_TASK_INDEX
      value: "0"
    image: viennaglobal.azurecr.io/cap/lifecycler/installed:westeurope-stable
    imagePullPolicy: Always
    name: 1cfc74aae33346e9b77672f82ab26790-lifecycler
    resources: {}
    securityContext:
      privileged: true
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: FallbackToLogsOnError
    volumeMounts:
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-a3ec5951
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-b678f70c
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-77bc0027
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-ddcb583f
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-e3108668
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-72150f7f
    - mountPath: /etc/podinfo
      name: podinfo
    - mountPath: /etc/volcano
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - mountPath: /root/.ssh
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
      subPath: .ssh
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-vpq6k
      readOnly: true
  - env:
    - name: AMLARC_NUM_GPU_PER_WORKER
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AML_JOB_ID
      value: 8b2821ccdc9c9fb818502c0e69b96572
    - name: POD_UID
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.uid
    - name: AMLARC_NUM_PS
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AMLARC_ROLE_INDEX_REGEX
      value: '[a-zA-Z0-9\-]*-([a-zA-Z[]*)-([0-9[]*)'
    - name: AZUREML_OBO_CANARY_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sL2V4cGVyaW1lbnROYW1lL3RvbWFzZXhwZXJpbWVudC9ydW5JZC84OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjkiLCJhY2NvdW50aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJ3b3Jrc3BhY2VJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsInByb2plY3RpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImRpc2NvdmVyeSI6InVyaTovL2Rpc2NvdmVyeXVyaS8iLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDciLCJvaWQiOiIzZTEzMWZiZS0zNDU0LTRiMGMtODRhZi03NDVhYjE3NmQzNGQiLCJpc3MiOiJhenVyZW1sIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3LyIsImV4cCI6MTY1OTMzNTI2MCwiYXVkIjoiYXp1cmVtbCJ9.LgInzjMVeUO-1vcr-hrK4KeYNvWlAI3rTwaTimQ9OmJcCYopbWYWg8_aVwUKvKa3goqoZJgs2UEUwgv19r_cyL-BR8v-4opIRJh68ZLUBJYPuVRK_qRQdM7OkJdU2PZugiBFYGSicG40xE1I80LjdnEcrJHRVQ0-UFNJvaWtu-HHpV_aKedQNClO4jZb9Dfoax63ZHw4C4e2f9GV7JTQ1v18SlXlyEHR8iSRg9p-cDnmiktBkctYs2VMIU_k57hNtq5fJS5zBetjlA9wYIHzOAER2CefogBWSXxBhGKTRlDX-ovIz3j9JE2H5BuNNhm2yEcucrB8oROVgGF2zcb-vQ
    - name: AZUREML_OBO_ENABLED
      value: "True"
    - name: OBO_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: MSI_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: AZUREML_CR_DATA_CAPABILITY_CONFIG
      value: '[{"environment_names":["AZUREML_DATAREFERENCE_Dataset","AZURE_ML_INPUT_Dataset"[],"from":"azuremldatareference://azureml_globaldatasets/GenericCSV/Automobile_price_data_(Raw)","mode":"mount","name":"Dataset","options":{"cache_size_buffer_mb":500,"force_folder":true}},{"environment_names":["Results_dataset","AZURE_ML_OUTPUT_Results_dataset"[],"mode":"mount","name":"Results_dataset","options":{"is_single_file":false,"register_dataset":{"properties":{"azureml.pipelineRun.moduleNodeId":"47566002","azureml.pipelineRun.outputPortName":"Results_dataset","azureml.pipelineRunId":"f4a6c5eb-1feb-49ff-9429-4ec15b15393c"}}},"to":"azuremldatastore://workspaceblobstore/azureml/89a01da5-907f-42a6-96e4-8d2e6a22c869/Results_dataset"}]'
    - name: AZUREML_ARM_WORKSPACE_NAME
      value: azureml
    - name: AZUREML_ARM_SUBSCRIPTION
      value: a0f4a733-4fce-4d49-b8a8-d30541fc1b45
    - name: AZUREML_ARM_PROJECT_NAME
      value: tomasexperiment
    - name: AZUREML_DISCOVERY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms/discovery
    - name: AZUREML_RUN_HISTORY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_WORKSPACE_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml
    - name: AZUREML_CR_AZUREML_CONTEXT
      value: '{"subscription_id":"a0f4a733-4fce-4d49-b8a8-d30541fc1b45","resource_group":"azureml","workspace_name":"azureml","workspace_id":"10400c14-9477-41ad-a935-e963d851654b","service_endpoint":"https://westeurope.api.azureml.ms","discovery_endpoint":"https://westeurope.api.azureml.ms/discovery","experiment_name":"tomasexperiment","experiment_id":"e4360b71-5ba4-4789-8e0c-ab040462cc06","root_run_id":"f4a6c5eb-1feb-49ff-9429-4ec15b15393c","run_id":"89a01da5-907f-42a6-96e4-8d2e6a22c869","run_token":"eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw","run_history_service_endpoint":"https://westeurope.api.azureml.ms","data_container_id":"dcid.89a01da5-907f-42a6-96e4-8d2e6a22c869","run_uuid":"1cfc74aa-e333-46e9-b776-72f82ab26790"}'
    - name: AZUREML_WORKSPACE_ID
      value: 10400c14-9477-41ad-a935-e963d851654b
    - name: AZUREML_EXPERIMENT_ID
      value: e4360b71-5ba4-4789-8e0c-ab040462cc06
    - name: AZUREML_RUN_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_EXPERIMENT_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml/experiments/tomasexperiment
    - name: AZUREML_ROOT_RUN_ID
      value: f4a6c5eb-1feb-49ff-9429-4ec15b15393c
    - name: AZUREML_RUN_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw
    - name: AZUREML_ARM_RESOURCEGROUP
      value: azureml
    - name: AZUREML_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_CR_COMPUTE_CONTEXT
      value: '{"cluster_name":"k8s-compute","node_id":{"EnvironmentVariable":"POD_NAME"},"vm_id":null,"run_attempt_count":1,"gpu_count":0,"vm_size":null,"readable_cluster_name":null,"vm_priority":null,"use_vnet_or_private_link":false}'
    - name: AZUREML_CR_DISTRIBUTED_CONFIG
      value: '{"rank":"VK_TASK_INDEX","host_list":["azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0.azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572.azureml-workloads.svc.cluster.local"[],"remote_grpc":{"Tcp":{"lifecycler_port":13333,"executor_port":13334}}}'
    - name: AZUREML_CR_TELEMETRY_CONFIG
      value: '{"collector":{"receiver":null,"exporter":{"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66"},"jaeger":null,"timeout_millis":null,"level":null}},"logger":{"console":null,"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66","level":"info","enabled":true},"file":{"extension":"log","level":"info","enabled":true}},"node_rank":"VK_TASK_INDEX","node_id":null,"disable_sensitive_scrub":null}'
    - name: AZUREML_CR_GRPC_ADDRESS_BASE
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
    - name: AZUREML_CR_DATA_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/data-capability:0
    - name: AZUREML_CR_DATA_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
    - name: AZUREML_CR_DATA_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-data-capability
    - name: AZUREML_CR_CS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/cs-capability:0
    - name: AZUREML_CR_CS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
    - name: AZUREML_CR_CS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-cs-capability
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/hosttools-capability:0
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-hosttools-capability
    - name: AZUREML_CR_EXECUTION_WORKING_DIR_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
    - name: AZUREML_DATASET_FILE_OUTPUTS
      value: Results_dataset
    - name: AZUREML_PARAMETER_Select_Columns
      value: '%7B%22isFilter%22%3Atrue%2C%22rules%22%3A%5B%7B%22exclude%22%3Afalse%2C%22ruleType%22%3A%22AllColumns%22%7D%2C%7B%22exclude%22%3Atrue%2C%22ruleType%22%3A%22ColumnNames%22%2C%22columns%22%3A%5B%22normalized-losses%22%5D%7D%5D%7D'
    - name: DATASET_MOUNT_BLOCK_BASED_CACHE_ENABLED
      value: "true"
    - name: AZUREML_PARAMETER_Node_Count
      value: "1"
    - name: DATASET_RSLEX_UPLOAD
      value: "true"
    - name: AZUREML_CR_CORRELATION_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_CR_LIFECYCLER_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
    - name: POD_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.name
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.namespace
    - name: POD_IP
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: status.podIP
    - name: NODE_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: spec.nodeName
    - name: VC_WORKER_HOSTS
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_HOSTS
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VC_WORKER_NUM
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_NUM
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VK_TASK_INDEX
      value: "0"
    - name: VC_TASK_INDEX
      value: "0"
    image: viennaglobal.azurecr.io/cap/data-capability/installed:westeurope-stable
    imagePullPolicy: Always
    name: 1cfc74aae33346e9b77672f82ab26790-data-capability
    resources: {}
    securityContext:
      privileged: true
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: FallbackToLogsOnError
    volumeMounts:
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-a3ec5951
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-b678f70c
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-77bc0027
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-ddcb583f
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-e3108668
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-72150f7f
    - mountPath: /etc/podinfo
      name: podinfo
    - mountPath: /etc/volcano
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - mountPath: /root/.ssh
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
      subPath: .ssh
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-vpq6k
      readOnly: true
  - env:
    - name: AMLARC_NUM_GPU_PER_WORKER
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AML_JOB_ID
      value: 8b2821ccdc9c9fb818502c0e69b96572
    - name: POD_UID
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.uid
    - name: AMLARC_NUM_PS
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AMLARC_ROLE_INDEX_REGEX
      value: '[a-zA-Z0-9\-]*-([a-zA-Z[]*)-([0-9[]*)'
    - name: AZUREML_OBO_CANARY_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sL2V4cGVyaW1lbnROYW1lL3RvbWFzZXhwZXJpbWVudC9ydW5JZC84OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjkiLCJhY2NvdW50aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJ3b3Jrc3BhY2VJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsInByb2plY3RpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImRpc2NvdmVyeSI6InVyaTovL2Rpc2NvdmVyeXVyaS8iLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDciLCJvaWQiOiIzZTEzMWZiZS0zNDU0LTRiMGMtODRhZi03NDVhYjE3NmQzNGQiLCJpc3MiOiJhenVyZW1sIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3LyIsImV4cCI6MTY1OTMzNTI2MCwiYXVkIjoiYXp1cmVtbCJ9.LgInzjMVeUO-1vcr-hrK4KeYNvWlAI3rTwaTimQ9OmJcCYopbWYWg8_aVwUKvKa3goqoZJgs2UEUwgv19r_cyL-BR8v-4opIRJh68ZLUBJYPuVRK_qRQdM7OkJdU2PZugiBFYGSicG40xE1I80LjdnEcrJHRVQ0-UFNJvaWtu-HHpV_aKedQNClO4jZb9Dfoax63ZHw4C4e2f9GV7JTQ1v18SlXlyEHR8iSRg9p-cDnmiktBkctYs2VMIU_k57hNtq5fJS5zBetjlA9wYIHzOAER2CefogBWSXxBhGKTRlDX-ovIz3j9JE2H5BuNNhm2yEcucrB8oROVgGF2zcb-vQ
    - name: AZUREML_OBO_ENABLED
      value: "True"
    - name: OBO_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: MSI_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: AZUREML_CR_CS_CAPABILITY_CONFIG
      value: '{"context_managers":[],"snapshot":"[{\"Id\":\"fc4a4324-6587-4219-91b9-109298ed4ad9\",\"PathStack\":[\".\"],\"SnapshotEntityId\":null,\"SnapshotAssetId\":null}]"}'
    - name: AZUREML_ARM_WORKSPACE_NAME
      value: azureml
    - name: AZUREML_ARM_SUBSCRIPTION
      value: a0f4a733-4fce-4d49-b8a8-d30541fc1b45
    - name: AZUREML_ARM_PROJECT_NAME
      value: tomasexperiment
    - name: AZUREML_DISCOVERY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms/discovery
    - name: AZUREML_RUN_HISTORY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_WORKSPACE_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml
    - name: AZUREML_CR_AZUREML_CONTEXT
      value: '{"subscription_id":"a0f4a733-4fce-4d49-b8a8-d30541fc1b45","resource_group":"azureml","workspace_name":"azureml","workspace_id":"10400c14-9477-41ad-a935-e963d851654b","service_endpoint":"https://westeurope.api.azureml.ms","discovery_endpoint":"https://westeurope.api.azureml.ms/discovery","experiment_name":"tomasexperiment","experiment_id":"e4360b71-5ba4-4789-8e0c-ab040462cc06","root_run_id":"f4a6c5eb-1feb-49ff-9429-4ec15b15393c","run_id":"89a01da5-907f-42a6-96e4-8d2e6a22c869","run_token":"eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw","run_history_service_endpoint":"https://westeurope.api.azureml.ms","data_container_id":"dcid.89a01da5-907f-42a6-96e4-8d2e6a22c869","run_uuid":"1cfc74aa-e333-46e9-b776-72f82ab26790"}'
    - name: AZUREML_WORKSPACE_ID
      value: 10400c14-9477-41ad-a935-e963d851654b
    - name: AZUREML_EXPERIMENT_ID
      value: e4360b71-5ba4-4789-8e0c-ab040462cc06
    - name: AZUREML_RUN_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_EXPERIMENT_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml/experiments/tomasexperiment
    - name: AZUREML_ROOT_RUN_ID
      value: f4a6c5eb-1feb-49ff-9429-4ec15b15393c
    - name: AZUREML_RUN_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw
    - name: AZUREML_ARM_RESOURCEGROUP
      value: azureml
    - name: AZUREML_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_CR_COMPUTE_CONTEXT
      value: '{"cluster_name":"k8s-compute","node_id":{"EnvironmentVariable":"POD_NAME"},"vm_id":null,"run_attempt_count":1,"gpu_count":0,"vm_size":null,"readable_cluster_name":null,"vm_priority":null,"use_vnet_or_private_link":false}'
    - name: AZUREML_CR_DISTRIBUTED_CONFIG
      value: '{"rank":"VK_TASK_INDEX","host_list":["azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0.azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572.azureml-workloads.svc.cluster.local"[],"remote_grpc":{"Tcp":{"lifecycler_port":13333,"executor_port":13334}}}'
    - name: AZUREML_CR_TELEMETRY_CONFIG
      value: '{"collector":{"receiver":null,"exporter":{"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66"},"jaeger":null,"timeout_millis":null,"level":null}},"logger":{"console":null,"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66","level":"info","enabled":true},"file":{"extension":"log","level":"info","enabled":true}},"node_rank":"VK_TASK_INDEX","node_id":null,"disable_sensitive_scrub":null}'
    - name: AZUREML_CR_GRPC_ADDRESS_BASE
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
    - name: AZUREML_CR_DATA_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/data-capability:0
    - name: AZUREML_CR_DATA_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
    - name: AZUREML_CR_DATA_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-data-capability
    - name: AZUREML_CR_CS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/cs-capability:0
    - name: AZUREML_CR_CS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
    - name: AZUREML_CR_CS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-cs-capability
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/hosttools-capability:0
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-hosttools-capability
    - name: AZUREML_CR_EXECUTION_WORKING_DIR_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
    - name: AZUREML_DATASET_FILE_OUTPUTS
      value: Results_dataset
    - name: AZUREML_PARAMETER_Select_Columns
      value: '%7B%22isFilter%22%3Atrue%2C%22rules%22%3A%5B%7B%22exclude%22%3Afalse%2C%22ruleType%22%3A%22AllColumns%22%7D%2C%7B%22exclude%22%3Atrue%2C%22ruleType%22%3A%22ColumnNames%22%2C%22columns%22%3A%5B%22normalized-losses%22%5D%7D%5D%7D'
    - name: DATASET_MOUNT_BLOCK_BASED_CACHE_ENABLED
      value: "true"
    - name: AZUREML_PARAMETER_Node_Count
      value: "1"
    - name: DATASET_RSLEX_UPLOAD
      value: "true"
    - name: AZUREML_CR_CORRELATION_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_CR_LIFECYCLER_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
    - name: POD_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.name
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.namespace
    - name: POD_IP
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: status.podIP
    - name: NODE_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: spec.nodeName
    - name: VC_WORKER_HOSTS
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_HOSTS
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VC_WORKER_NUM
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_NUM
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VK_TASK_INDEX
      value: "0"
    - name: VC_TASK_INDEX
      value: "0"
    image: viennaglobal.azurecr.io/cap/cs-capability/installed:westeurope-stable
    imagePullPolicy: Always
    name: 1cfc74aae33346e9b77672f82ab26790-cs-capability
    resources: {}
    securityContext:
      privileged: true
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: FallbackToLogsOnError
    volumeMounts:
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-a3ec5951
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-b678f70c
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-77bc0027
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-ddcb583f
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-e3108668
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-72150f7f
    - mountPath: /etc/podinfo
      name: podinfo
    - mountPath: /etc/volcano
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - mountPath: /root/.ssh
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
      subPath: .ssh
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-vpq6k
      readOnly: true
  - env:
    - name: AMLARC_NUM_GPU_PER_WORKER
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AML_JOB_ID
      value: 8b2821ccdc9c9fb818502c0e69b96572
    - name: POD_UID
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.uid
    - name: AMLARC_NUM_PS
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AMLARC_ROLE_INDEX_REGEX
      value: '[a-zA-Z0-9\-]*-([a-zA-Z[]*)-([0-9[]*)'
    - name: AZUREML_OBO_CANARY_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sL2V4cGVyaW1lbnROYW1lL3RvbWFzZXhwZXJpbWVudC9ydW5JZC84OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjkiLCJhY2NvdW50aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJ3b3Jrc3BhY2VJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsInByb2plY3RpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImRpc2NvdmVyeSI6InVyaTovL2Rpc2NvdmVyeXVyaS8iLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDciLCJvaWQiOiIzZTEzMWZiZS0zNDU0LTRiMGMtODRhZi03NDVhYjE3NmQzNGQiLCJpc3MiOiJhenVyZW1sIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3LyIsImV4cCI6MTY1OTMzNTI2MCwiYXVkIjoiYXp1cmVtbCJ9.LgInzjMVeUO-1vcr-hrK4KeYNvWlAI3rTwaTimQ9OmJcCYopbWYWg8_aVwUKvKa3goqoZJgs2UEUwgv19r_cyL-BR8v-4opIRJh68ZLUBJYPuVRK_qRQdM7OkJdU2PZugiBFYGSicG40xE1I80LjdnEcrJHRVQ0-UFNJvaWtu-HHpV_aKedQNClO4jZb9Dfoax63ZHw4C4e2f9GV7JTQ1v18SlXlyEHR8iSRg9p-cDnmiktBkctYs2VMIU_k57hNtq5fJS5zBetjlA9wYIHzOAER2CefogBWSXxBhGKTRlDX-ovIz3j9JE2H5BuNNhm2yEcucrB8oROVgGF2zcb-vQ
    - name: AZUREML_OBO_ENABLED
      value: "True"
    - name: OBO_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: MSI_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_CONFIG
      value: '{"dirs":[{"environment_name":"AZUREML_CR_HT_CAP_user_logs_PATH","relative_path":"user_logs","streamable":true},{"environment_name":"AZUREML_CR_HT_CAP_azureml_logs_PATH","relative_path":"azureml-logs","streamable":true},{"environment_name":"AZUREML_CR_HT_CAP_outputs_PATH","relative_path":"outputs","streamable":false},{"environment_name":"AZUREML_CR_HT_CAP_logs_PATH","relative_path":"logs","streamable":true}],"log_filtering_policy":null,"metrics":{"enabled":true,"polling_interval_sec":30,"send_to_history_interval_sec":60},"use_block_blob_in_blob_streamer":true}'
    - name: AZUREML_ARM_WORKSPACE_NAME
      value: azureml
    - name: AZUREML_ARM_SUBSCRIPTION
      value: a0f4a733-4fce-4d49-b8a8-d30541fc1b45
    - name: AZUREML_ARM_PROJECT_NAME
      value: tomasexperiment
    - name: AZUREML_DISCOVERY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms/discovery
    - name: AZUREML_RUN_HISTORY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_WORKSPACE_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml
    - name: AZUREML_CR_AZUREML_CONTEXT
      value: '{"subscription_id":"a0f4a733-4fce-4d49-b8a8-d30541fc1b45","resource_group":"azureml","workspace_name":"azureml","workspace_id":"10400c14-9477-41ad-a935-e963d851654b","service_endpoint":"https://westeurope.api.azureml.ms","discovery_endpoint":"https://westeurope.api.azureml.ms/discovery","experiment_name":"tomasexperiment","experiment_id":"e4360b71-5ba4-4789-8e0c-ab040462cc06","root_run_id":"f4a6c5eb-1feb-49ff-9429-4ec15b15393c","run_id":"89a01da5-907f-42a6-96e4-8d2e6a22c869","run_token":"eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw","run_history_service_endpoint":"https://westeurope.api.azureml.ms","data_container_id":"dcid.89a01da5-907f-42a6-96e4-8d2e6a22c869","run_uuid":"1cfc74aa-e333-46e9-b776-72f82ab26790"}'
    - name: AZUREML_WORKSPACE_ID
      value: 10400c14-9477-41ad-a935-e963d851654b
    - name: AZUREML_EXPERIMENT_ID
      value: e4360b71-5ba4-4789-8e0c-ab040462cc06
    - name: AZUREML_RUN_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_EXPERIMENT_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml/experiments/tomasexperiment
    - name: AZUREML_ROOT_RUN_ID
      value: f4a6c5eb-1feb-49ff-9429-4ec15b15393c
    - name: AZUREML_RUN_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw
    - name: AZUREML_ARM_RESOURCEGROUP
      value: azureml
    - name: AZUREML_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_CR_COMPUTE_CONTEXT
      value: '{"cluster_name":"k8s-compute","node_id":{"EnvironmentVariable":"POD_NAME"},"vm_id":null,"run_attempt_count":1,"gpu_count":0,"vm_size":null,"readable_cluster_name":null,"vm_priority":null,"use_vnet_or_private_link":false}'
    - name: AZUREML_CR_DISTRIBUTED_CONFIG
      value: '{"rank":"VK_TASK_INDEX","host_list":["azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0.azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572.azureml-workloads.svc.cluster.local"[],"remote_grpc":{"Tcp":{"lifecycler_port":13333,"executor_port":13334}}}'
    - name: AZUREML_CR_TELEMETRY_CONFIG
      value: '{"collector":{"receiver":null,"exporter":{"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66"},"jaeger":null,"timeout_millis":null,"level":null}},"logger":{"console":null,"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66","level":"info","enabled":true},"file":{"extension":"log","level":"info","enabled":true}},"node_rank":"VK_TASK_INDEX","node_id":null,"disable_sensitive_scrub":null}'
    - name: AZUREML_CR_GRPC_ADDRESS_BASE
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
    - name: AZUREML_CR_DATA_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/data-capability:0
    - name: AZUREML_CR_DATA_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
    - name: AZUREML_CR_DATA_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-data-capability
    - name: AZUREML_CR_CS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/cs-capability:0
    - name: AZUREML_CR_CS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
    - name: AZUREML_CR_CS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-cs-capability
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/hosttools-capability:0
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-hosttools-capability
    - name: AZUREML_CR_EXECUTION_WORKING_DIR_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
    - name: AZUREML_DATASET_FILE_OUTPUTS
      value: Results_dataset
    - name: AZUREML_PARAMETER_Select_Columns
      value: '%7B%22isFilter%22%3Atrue%2C%22rules%22%3A%5B%7B%22exclude%22%3Afalse%2C%22ruleType%22%3A%22AllColumns%22%7D%2C%7B%22exclude%22%3Atrue%2C%22ruleType%22%3A%22ColumnNames%22%2C%22columns%22%3A%5B%22normalized-losses%22%5D%7D%5D%7D'
    - name: DATASET_MOUNT_BLOCK_BASED_CACHE_ENABLED
      value: "true"
    - name: AZUREML_PARAMETER_Node_Count
      value: "1"
    - name: DATASET_RSLEX_UPLOAD
      value: "true"
    - name: AZUREML_CR_CORRELATION_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_CR_LIFECYCLER_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
    - name: POD_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.name
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.namespace
    - name: POD_IP
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: status.podIP
    - name: NODE_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: spec.nodeName
    - name: VC_WORKER_HOSTS
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_HOSTS
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VC_WORKER_NUM
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_NUM
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VK_TASK_INDEX
      value: "0"
    - name: VC_TASK_INDEX
      value: "0"
    image: viennaglobal.azurecr.io/cap/hosttools-capability/installed:westeurope-stable
    imagePullPolicy: Always
    name: 1cfc74aae33346e9b77672f82ab26790-hosttools-capability
    resources: {}
    securityContext:
      privileged: true
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: FallbackToLogsOnError
    volumeMounts:
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-a3ec5951
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-b678f70c
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-77bc0027
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-ddcb583f
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-e3108668
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
      mountPropagation: Bidirectional
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-72150f7f
    - mountPath: /etc/podinfo
      name: podinfo
    - mountPath: /etc/volcano
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - mountPath: /root/.ssh
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
      subPath: .ssh
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-vpq6k
      readOnly: true
  - command:
    - bash
    - -c
    - set -o pipefail; bash /amlarc-scripts/bootstrap_common_runtime.sh 2>&1; /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd/execution-wrapper
    env:
    - name: AMLARC_NUM_GPU_PER_WORKER
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AML_JOB_ID
      value: 8b2821ccdc9c9fb818502c0e69b96572
    - name: POD_UID
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.uid
    - name: AMLARC_NUM_PS
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AMLARC_ROLE_INDEX_REGEX
      value: '[a-zA-Z0-9\-]*-([a-zA-Z[]*)-([0-9[]*)'
    - name: AZUREML_OBO_CANARY_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sL2V4cGVyaW1lbnROYW1lL3RvbWFzZXhwZXJpbWVudC9ydW5JZC84OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjkiLCJhY2NvdW50aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJ3b3Jrc3BhY2VJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsInByb2plY3RpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImRpc2NvdmVyeSI6InVyaTovL2Rpc2NvdmVyeXVyaS8iLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDciLCJvaWQiOiIzZTEzMWZiZS0zNDU0LTRiMGMtODRhZi03NDVhYjE3NmQzNGQiLCJpc3MiOiJhenVyZW1sIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3LyIsImV4cCI6MTY1OTMzNTI2MCwiYXVkIjoiYXp1cmVtbCJ9.LgInzjMVeUO-1vcr-hrK4KeYNvWlAI3rTwaTimQ9OmJcCYopbWYWg8_aVwUKvKa3goqoZJgs2UEUwgv19r_cyL-BR8v-4opIRJh68ZLUBJYPuVRK_qRQdM7OkJdU2PZugiBFYGSicG40xE1I80LjdnEcrJHRVQ0-UFNJvaWtu-HHpV_aKedQNClO4jZb9Dfoax63ZHw4C4e2f9GV7JTQ1v18SlXlyEHR8iSRg9p-cDnmiktBkctYs2VMIU_k57hNtq5fJS5zBetjlA9wYIHzOAER2CefogBWSXxBhGKTRlDX-ovIz3j9JE2H5BuNNhm2yEcucrB8oROVgGF2zcb-vQ
    - name: AZUREML_OBO_ENABLED
      value: "True"
    - name: OBO_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: MSI_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: AMLUSER_GROUPS
    - name: HOST_LIST
      value: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0.azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572.azureml-workloads.svc.cluster.local
    - name: AZUREML_CR_EXECUTOR_CONFIG
      value: eyJleGVjdXRpb25fd29ya2luZ19kaXIiOiIvdG1wL2F6dXJlbWwvY3Ivai8xY2ZjNzRhYWUzMzM0NmU5Yjc3NjcyZjgyYWIyNjc5MC9leGUvd2QiLCJleGVjdXRvcl9hZGRyZXNzIjoiMC4wLjAuMDoxMzMzNCIsImxpZmVjeWNsZXJfYWRkcmVzcyI6IjAuMC4wLjA6MTMzMzMiLCJkaXN0cmlidXRlZF9jb25maWciOnsicmFuayI6IlZLX1RBU0tfSU5ERVgiLCJob3N0X2xpc3QiOlsiYXp1cmVtbC13b3JrbG9hZHMtOGIyODIxY2NkYzljOWZiODE4NTAyYzBlNjliOTY1NzItd29ya2VyLTAuYXp1cmVtbC13b3JrbG9hZHMtOGIyODIxY2NkYzljOWZiODE4NTAyYzBlNjliOTY1NzIuYXp1cmVtbC13b3JrbG9hZHMuc3ZjLmNsdXN0ZXIubG9jYWwiXSwicmVtb3RlX2dycGMiOnsiVGNwIjp7ImxpZmVjeWNsZXJfcG9ydCI6MTMzMzMsImV4ZWN1dG9yX3BvcnQiOjEzMzM0fX19LCJ1c2VfbXBpX3JzaF9hZ2VudCI6bnVsbCwiZGVidWdfbW9kZSI6bnVsbCwiZXhlY3V0b3JfY29uZmlnIjpudWxsfQ==
    - name: MLFLOW_RUN_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: MLFLOW_TRACKING_URI
      value: azureml://westeurope.api.azureml.ms/mlflow/v1.0/subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml
    - name: MLFLOW_EXPERIMENT_NAME
      value: tomasexperiment
    - name: EXAMPLE_ENV_VAR
      value: EXAMPLE_VALUE
    - name: MLFLOW_TRACKING_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw
    - name: MLFLOW_EXPERIMENT_ID
      value: e4360b71-5ba4-4789-8e0c-ab040462cc06
    - name: AZUREML_ARM_WORKSPACE_NAME
      value: azureml
    - name: AZUREML_ARM_SUBSCRIPTION
      value: a0f4a733-4fce-4d49-b8a8-d30541fc1b45
    - name: AZUREML_ARM_PROJECT_NAME
      value: tomasexperiment
    - name: AZUREML_DISCOVERY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms/discovery
    - name: AZUREML_RUN_HISTORY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_WORKSPACE_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml
    - name: AZUREML_CR_AZUREML_CONTEXT
      value: '{"subscription_id":"a0f4a733-4fce-4d49-b8a8-d30541fc1b45","resource_group":"azureml","workspace_name":"azureml","workspace_id":"10400c14-9477-41ad-a935-e963d851654b","service_endpoint":"https://westeurope.api.azureml.ms","discovery_endpoint":"https://westeurope.api.azureml.ms/discovery","experiment_name":"tomasexperiment","experiment_id":"e4360b71-5ba4-4789-8e0c-ab040462cc06","root_run_id":"f4a6c5eb-1feb-49ff-9429-4ec15b15393c","run_id":"89a01da5-907f-42a6-96e4-8d2e6a22c869","run_token":"eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw","run_history_service_endpoint":"https://westeurope.api.azureml.ms","data_container_id":"dcid.89a01da5-907f-42a6-96e4-8d2e6a22c869","run_uuid":"1cfc74aa-e333-46e9-b776-72f82ab26790"}'
    - name: AZUREML_WORKSPACE_ID
      value: 10400c14-9477-41ad-a935-e963d851654b
    - name: AZUREML_EXPERIMENT_ID
      value: e4360b71-5ba4-4789-8e0c-ab040462cc06
    - name: AZUREML_RUN_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_EXPERIMENT_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml/experiments/tomasexperiment
    - name: AZUREML_ROOT_RUN_ID
      value: f4a6c5eb-1feb-49ff-9429-4ec15b15393c
    - name: AZUREML_RUN_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw
    - name: AZUREML_ARM_RESOURCEGROUP
      value: azureml
    - name: AZUREML_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_CR_COMPUTE_CONTEXT
      value: '{"cluster_name":"k8s-compute","node_id":{"EnvironmentVariable":"POD_NAME"},"vm_id":null,"run_attempt_count":1,"gpu_count":0,"vm_size":null,"readable_cluster_name":null,"vm_priority":null,"use_vnet_or_private_link":false}'
    - name: AZUREML_CR_DISTRIBUTED_CONFIG
      value: '{"rank":"VK_TASK_INDEX","host_list":["azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0.azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572.azureml-workloads.svc.cluster.local"[],"remote_grpc":{"Tcp":{"lifecycler_port":13333,"executor_port":13334}}}'
    - name: AZUREML_CR_TELEMETRY_CONFIG
      value: '{"collector":{"receiver":null,"exporter":{"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66"},"jaeger":null,"timeout_millis":null,"level":null}},"logger":{"console":null,"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66","level":"info","enabled":true},"file":{"extension":"log","level":"info","enabled":true}},"node_rank":"VK_TASK_INDEX","node_id":null,"disable_sensitive_scrub":null}'
    - name: AZUREML_CR_GRPC_ADDRESS_BASE
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
    - name: AZUREML_CR_DATA_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/data-capability:0
    - name: AZUREML_CR_DATA_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
    - name: AZUREML_CR_DATA_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-data-capability
    - name: AZUREML_CR_CS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/cs-capability:0
    - name: AZUREML_CR_CS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
    - name: AZUREML_CR_CS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-cs-capability
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/hosttools-capability:0
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-hosttools-capability
    - name: AZUREML_CR_EXECUTION_WORKING_DIR_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
    - name: AZUREML_DATASET_FILE_OUTPUTS
      value: Results_dataset
    - name: AZUREML_PARAMETER_Select_Columns
      value: '%7B%22isFilter%22%3Atrue%2C%22rules%22%3A%5B%7B%22exclude%22%3Afalse%2C%22ruleType%22%3A%22AllColumns%22%7D%2C%7B%22exclude%22%3Atrue%2C%22ruleType%22%3A%22ColumnNames%22%2C%22columns%22%3A%5B%22normalized-losses%22%5D%7D%5D%7D'
    - name: DATASET_MOUNT_BLOCK_BASED_CACHE_ENABLED
      value: "true"
    - name: AZUREML_PARAMETER_Node_Count
      value: "1"
    - name: DATASET_RSLEX_UPLOAD
      value: "true"
    - name: AZUREML_CR_CORRELATION_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_CR_LIFECYCLER_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
    - name: POD_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.name
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.namespace
    - name: POD_IP
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: status.podIP
    - name: NODE_NAME
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: spec.nodeName
    - name: NVIDIA_VISIBLE_DEVICES
    - name: VC_WORKER_HOSTS
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_HOSTS
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VC_WORKER_NUM
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_NUM
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VK_TASK_INDEX
      value: "0"
    - name: VC_TASK_INDEX
      value: "0"
    image: mcr.microsoft.com/azureml/curated/designer:42
    imagePullPolicy: Always
    name: 1cfc74aae33346e9b77672f82ab26790-execution-wrapper
    resources:
      limits:
        cpu: 600m
        memory: "1610612736"
      requests:
        cpu: 600m
        memory: "1610612736"
    securityContext:
      capabilities:
        add:
        - SYS_ADMIN
        - IPC_LOCK
        - SYS_PTRACE
        - SYS_CHROOT
        - AUDIT_WRITE
      privileged: false
      runAsUser: 0
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: FallbackToLogsOnError
    volumeMounts:
    - mountPath: /amlarc-hosts
      name: amlarc-hosts
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-a3ec5951
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-b678f70c
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-77bc0027
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-ddcb583f
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-e3108668
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-72150f7f
    - mountPath: /etc/podinfo
      name: podinfo
    - mountPath: /dev/shm
      name: 1cfc74aae33346e9b77672f82ab26790-execution-wrapper-shm
    - mountPath: /amlarc-runtime
      name: amlarc-runtime
    - mountPath: /amlarc-scripts
      name: amlarc-scripts
      readOnly: true
    - mountPath: /etc/volcano
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - mountPath: /root/.ssh
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
      subPath: .ssh
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-vpq6k
      readOnly: true
  dnsPolicy: ClusterFirst
  enableServiceLinks: true
  hostAliases:
  - hostnames:
    - 1cfc74aae33346e9b77672f82ab26790-data-capability
    - 1cfc74aae33346e9b77672f82ab26790-cs-capability
    - 1cfc74aae33346e9b77672f82ab26790-hosttools-capability
    - 1cfc74aae33346e9b77672f82ab26790-lifecycler
    - 1cfc74aae33346e9b77672f82ab26790-execution-wrapper
    ip: 127.0.0.1
  hostname: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0
  imagePullSecrets:
  - name: 1cfc74aae33346e9b77672f82ab26790-viennaglobal.azurecr.io
  - name: 8b2821ccdc9c9fb818502c0e69b96572-imagepull-0-secrets
  initContainers:
  - args:
    - cp $AZUREML_CR_EXECUTION_WRAPPER_BIN_PATH/* /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd;
      ls -al /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
    command:
    - /bin/sh
    - -c
    env:
    - name: AMLARC_NUM_GPU_PER_WORKER
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AML_JOB_ID
      value: 8b2821ccdc9c9fb818502c0e69b96572
    - name: POD_UID
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.uid
    - name: AMLARC_NUM_PS
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AMLARC_ROLE_INDEX_REGEX
      value: '[a-zA-Z0-9\-]*-([a-zA-Z[]*)-([0-9[]*)'
    - name: AZUREML_OBO_CANARY_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sL2V4cGVyaW1lbnROYW1lL3RvbWFzZXhwZXJpbWVudC9ydW5JZC84OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjkiLCJhY2NvdW50aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJ3b3Jrc3BhY2VJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsInByb2plY3RpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImRpc2NvdmVyeSI6InVyaTovL2Rpc2NvdmVyeXVyaS8iLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDciLCJvaWQiOiIzZTEzMWZiZS0zNDU0LTRiMGMtODRhZi03NDVhYjE3NmQzNGQiLCJpc3MiOiJhenVyZW1sIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3LyIsImV4cCI6MTY1OTMzNTI2MCwiYXVkIjoiYXp1cmVtbCJ9.LgInzjMVeUO-1vcr-hrK4KeYNvWlAI3rTwaTimQ9OmJcCYopbWYWg8_aVwUKvKa3goqoZJgs2UEUwgv19r_cyL-BR8v-4opIRJh68ZLUBJYPuVRK_qRQdM7OkJdU2PZugiBFYGSicG40xE1I80LjdnEcrJHRVQ0-UFNJvaWtu-HHpV_aKedQNClO4jZb9Dfoax63ZHw4C4e2f9GV7JTQ1v18SlXlyEHR8iSRg9p-cDnmiktBkctYs2VMIU_k57hNtq5fJS5zBetjlA9wYIHzOAER2CefogBWSXxBhGKTRlDX-ovIz3j9JE2H5BuNNhm2yEcucrB8oROVgGF2zcb-vQ
    - name: AZUREML_OBO_ENABLED
      value: "True"
    - name: OBO_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: MSI_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: AZUREML_ARM_WORKSPACE_NAME
      value: azureml
    - name: AZUREML_ARM_SUBSCRIPTION
      value: a0f4a733-4fce-4d49-b8a8-d30541fc1b45
    - name: AZUREML_ARM_PROJECT_NAME
      value: tomasexperiment
    - name: AZUREML_DISCOVERY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms/discovery
    - name: AZUREML_RUN_HISTORY_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_WORKSPACE_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml
    - name: AZUREML_CR_AZUREML_CONTEXT
      value: '{"subscription_id":"a0f4a733-4fce-4d49-b8a8-d30541fc1b45","resource_group":"azureml","workspace_name":"azureml","workspace_id":"10400c14-9477-41ad-a935-e963d851654b","service_endpoint":"https://westeurope.api.azureml.ms","discovery_endpoint":"https://westeurope.api.azureml.ms/discovery","experiment_name":"tomasexperiment","experiment_id":"e4360b71-5ba4-4789-8e0c-ab040462cc06","root_run_id":"f4a6c5eb-1feb-49ff-9429-4ec15b15393c","run_id":"89a01da5-907f-42a6-96e4-8d2e6a22c869","run_token":"eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw","run_history_service_endpoint":"https://westeurope.api.azureml.ms","data_container_id":"dcid.89a01da5-907f-42a6-96e4-8d2e6a22c869","run_uuid":"1cfc74aa-e333-46e9-b776-72f82ab26790"}'
    - name: AZUREML_WORKSPACE_ID
      value: 10400c14-9477-41ad-a935-e963d851654b
    - name: AZUREML_EXPERIMENT_ID
      value: e4360b71-5ba4-4789-8e0c-ab040462cc06
    - name: AZUREML_RUN_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_EXPERIMENT_SCOPE
      value: /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/azureml/providers/Microsoft.MachineLearningServices/workspaces/azureml/experiments/tomasexperiment
    - name: AZUREML_ROOT_RUN_ID
      value: f4a6c5eb-1feb-49ff-9429-4ec15b15393c
    - name: AZUREML_RUN_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sIiwiYWNjb3VudGlkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwid29ya3NwYWNlSWQiOiIxMDQwMGMxNC05NDc3LTQxYWQtYTkzNS1lOTYzZDg1MTY1NGIiLCJwcm9qZWN0aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJkaXNjb3ZlcnkiOiJ1cmk6Ly9kaXNjb3Zlcnl1cmkvIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3Iiwib2lkIjoiNzQyNGZiNGMtNWU5Zi00NWNkLTlmN2QtNDUzZDQ1NjU1ZTc1IiwicHVpZCI6IjEwMDNCRkZEOURDM0I2OUYiLCJpc3MiOiJhenVyZW1sIiwiYXBwaWQiOiJUb21hcyBLdWJpY2EiLCJleHAiOjE2NTk0Mjg4NTIsImF1ZCI6ImF6dXJlbWwifQ.cHnnpoI_EHjKn-u6Y-Xz_BrsiZtKs537uzH2HM9f4NrF2VJVt11HqcfAcVomHUZl6iTe5W-CJRhEotAOaHeyT-nrM3atWE3mbZEJ26-nBidbQ68o2-HfPcIr92aPjqjcnnMbcByztBfIFXiQjCpE4j7QzFNhewqM9jA74s9dMJ83jnIrAkEzULCsmKNsEv7Ng9seKE-dRySPyHZ2Qlqs62Qe_ewXrHW8oufa1gzeUVdJqxeysyoMhL9V2JyuwQ88Gr5OXQ3JUN0otE7Yut6ch6eIwDECMKbfFm-frPQrbQI7wwE8RqrFNEutaB9moCTvsMwHBceE0gTZSYyYYCYZpw
    - name: AZUREML_ARM_RESOURCEGROUP
      value: azureml
    - name: AZUREML_SERVICE_ENDPOINT
      value: https://westeurope.api.azureml.ms
    - name: AZUREML_CR_COMPUTE_CONTEXT
      value: '{"cluster_name":"k8s-compute","node_id":{"EnvironmentVariable":"POD_NAME"},"vm_id":null,"run_attempt_count":1,"gpu_count":0,"vm_size":null,"readable_cluster_name":null,"vm_priority":null,"use_vnet_or_private_link":false}'
    - name: AZUREML_CR_DISTRIBUTED_CONFIG
      value: '{"rank":"VK_TASK_INDEX","host_list":["azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-worker-0.azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572.azureml-workloads.svc.cluster.local"[],"remote_grpc":{"Tcp":{"lifecycler_port":13333,"executor_port":13334}}}'
    - name: AZUREML_CR_TELEMETRY_CONFIG
      value: '{"collector":{"receiver":null,"exporter":{"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66"},"jaeger":null,"timeout_millis":null,"level":null}},"logger":{"console":null,"appinsights":{"instrumentation_key":"fca5a4c9-adb4-44ae-bece-69e2cc91ff66","level":"info","enabled":true},"file":{"extension":"log","level":"info","enabled":true}},"node_rank":"VK_TASK_INDEX","node_id":null,"disable_sensitive_scrub":null}'
    - name: AZUREML_CR_GRPC_ADDRESS_BASE
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
    - name: AZUREML_CR_DATA_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/data-capability:0
    - name: AZUREML_CR_DATA_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
    - name: AZUREML_CR_DATA_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-data-capability
    - name: AZUREML_CR_CS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/cs-capability:0
    - name: AZUREML_CR_CS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
    - name: AZUREML_CR_CS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-cs-capability
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_ADDRESS
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc/hosttools-capability:0
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
    - name: AZUREML_CR_HOSTTOOLS_CAPABILITY_HOST
      value: 1cfc74aae33346e9b77672f82ab26790-hosttools-capability
    - name: AZUREML_CR_EXECUTION_WORKING_DIR_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
    - name: AZUREML_DATASET_FILE_OUTPUTS
      value: Results_dataset
    - name: AZUREML_PARAMETER_Select_Columns
      value: '%7B%22isFilter%22%3Atrue%2C%22rules%22%3A%5B%7B%22exclude%22%3Afalse%2C%22ruleType%22%3A%22AllColumns%22%7D%2C%7B%22exclude%22%3Atrue%2C%22ruleType%22%3A%22ColumnNames%22%2C%22columns%22%3A%5B%22normalized-losses%22%5D%7D%5D%7D'
    - name: DATASET_MOUNT_BLOCK_BASED_CACHE_ENABLED
      value: "true"
    - name: AZUREML_PARAMETER_Node_Count
      value: "1"
    - name: DATASET_RSLEX_UPLOAD
      value: "true"
    - name: AZUREML_CR_CORRELATION_ID
      value: 89a01da5-907f-42a6-96e4-8d2e6a22c869
    - name: AZUREML_CR_LIFECYCLER_PATH
      value: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
    - name: VC_WORKER_HOSTS
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_HOSTS
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VC_WORKER_NUM
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_NUM
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VK_TASK_INDEX
      value: "0"
    - name: VC_TASK_INDEX
      value: "0"
    image: viennaglobal.azurecr.io/exe/execution-wrapper/installed:westeurope-stable
    imagePullPolicy: Always
    name: 1cfc74aae33346e9b77672f82ab26790-execution-wrapper-init
    resources: {}
    securityContext:
      privileged: false
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/.grpc
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-a3ec5951
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/data-capability/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-b678f70c
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/cs-capability/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-77bc0027
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/hosttools-capability/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-ddcb583f
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/exe/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-e3108668
    - mountPath: /tmp/azureml/cr/j/1cfc74aae33346e9b77672f82ab26790/cap/lifecycler/wd
      mountPropagation: HostToContainer
      name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-72150f7f
    - mountPath: /etc/volcano
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - mountPath: /root/.ssh
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
      subPath: .ssh
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-vpq6k
      readOnly: true
  - command:
    - sh
    - /amlarc-init/init.sh
    env:
    - name: AMLARC_NUM_GPU_PER_WORKER
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AML_JOB_ID
      value: 8b2821ccdc9c9fb818502c0e69b96572
    - name: POD_UID
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.uid
    - name: AMLARC_NUM_PS
      value: "0"
    - name: AMLARC_NUM_WORKER
      value: "1"
    - name: AMLARC_ROLE_INDEX_REGEX
      value: '[a-zA-Z0-9\-]*-([a-zA-Z[]*)-([0-9[]*)'
    - name: AZUREML_OBO_CANARY_TOKEN
      value: eyJhbGciOiJSUzI1NiIsImtpZCI6IkUyQTBFNTU2RTNDNDZFQjg3QTA4RTJFMTBEMDFBQ0JDQ0UyN0QyRTMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlIjoiQ29udHJpYnV0b3IiLCJzY29wZSI6Ii9zdWJzY3JpcHRpb25zL2EwZjRhNzMzLTRmY2UtNGQ0OS1iOGE4LWQzMDU0MWZjMWI0NS9yZXNvdXJjZUdyb3Vwcy9henVyZW1sL3Byb3ZpZGVycy9NaWNyb3NvZnQuTWFjaGluZUxlYXJuaW5nU2VydmljZXMvd29ya3NwYWNlcy9henVyZW1sL2V4cGVyaW1lbnROYW1lL3RvbWFzZXhwZXJpbWVudC9ydW5JZC84OWEwMWRhNS05MDdmLTQyYTYtOTZlNC04ZDJlNmEyMmM4NjkiLCJhY2NvdW50aWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJ3b3Jrc3BhY2VJZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsInByb2plY3RpZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImRpc2NvdmVyeSI6InVyaTovL2Rpc2NvdmVyeXVyaS8iLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDciLCJvaWQiOiIzZTEzMWZiZS0zNDU0LTRiMGMtODRhZi03NDVhYjE3NmQzNGQiLCJpc3MiOiJhenVyZW1sIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3LyIsImV4cCI6MTY1OTMzNTI2MCwiYXVkIjoiYXp1cmVtbCJ9.LgInzjMVeUO-1vcr-hrK4KeYNvWlAI3rTwaTimQ9OmJcCYopbWYWg8_aVwUKvKa3goqoZJgs2UEUwgv19r_cyL-BR8v-4opIRJh68ZLUBJYPuVRK_qRQdM7OkJdU2PZugiBFYGSicG40xE1I80LjdnEcrJHRVQ0-UFNJvaWtu-HHpV_aKedQNClO4jZb9Dfoax63ZHw4C4e2f9GV7JTQ1v18SlXlyEHR8iSRg9p-cDnmiktBkctYs2VMIU_k57hNtq5fJS5zBetjlA9wYIHzOAER2CefogBWSXxBhGKTRlDX-ovIz3j9JE2H5BuNNhm2yEcucrB8oROVgGF2zcb-vQ
    - name: AZUREML_OBO_ENABLED
      value: "True"
    - name: OBO_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: MSI_ENDPOINT
      value: http://127.0.0.1:12342/token
    - name: VC_WORKER_HOSTS
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_HOSTS
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VC_WORKER_NUM
      valueFrom:
        configMapKeyRef:
          key: VC_WORKER_NUM
          name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - name: VK_TASK_INDEX
      value: "0"
    - name: VC_TASK_INDEX
      value: "0"
    image: mcr.microsoft.com/azureml/amlarc/docker/init-container:1.1.6
    imagePullPolicy: Always
    name: init
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /amlarc-runtime
      name: amlarc-runtime
    - mountPath: /amlarc-scripts
      name: amlarc-scripts
    - mountPath: /etc/volcano
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    - mountPath: /root/.ssh
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
      subPath: .ssh
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-vpq6k
      readOnly: true
  nodeName: aks-nodepool1-12594117-vmss000001
  preemptionPolicy: PreemptLowerPriority
  priority: 0
  restartPolicy: Never
  schedulerName: volcano
  securityContext: {}
  serviceAccount: amljobcontroller
  serviceAccountName: amljobcontroller
  subdomain: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572
  terminationGracePeriodSeconds: 30
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  - effect: NoSchedule
    key: node.kubernetes.io/memory-pressure
    operator: Exists
  volumes:
  - configMap:
      defaultMode: 420
      items:
      - key: hostfile
        path: hostfile
      - key: cluster_spec
        path: cluster_spec
      name: 8b2821ccdc9c9fb818502c0e69b96572
    name: amlarc-hosts
  - emptyDir: {}
    name: 89a01da5-907f-42a6-96e4-8d2e6a22c869
  - downwardAPI:
      defaultMode: 420
      items:
      - fieldRef:
          apiVersion: v1
          fieldPath: metadata.labels
        path: labels
      - fieldRef:
          apiVersion: v1
          fieldPath: metadata.annotations
        path: annotations
    name: podinfo
  - emptyDir:
      medium: Memory
      sizeLimit: "2147483648"
    name: 1cfc74aae33346e9b77672f82ab26790-execution-wrapper-shm
  - emptyDir: {}
    name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-72150f7f
  - emptyDir: {}
    name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-77bc0027
  - emptyDir: {}
    name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-a3ec5951
  - emptyDir: {}
    name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-b678f70c
  - emptyDir: {}
    name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-ddcb583f
  - emptyDir: {}
    name: 89a01da5-907f-42a6-96e4-8d2e6a22c869--tmp-azureml-cr-j-e3108668
  - emptyDir: {}
    name: amlarc-scripts
  - emptyDir: {}
    name: amlarc-runtime
  - configMap:
      defaultMode: 511
      name: 8b2821ccdc9c9fb818502c0e69b96572-lifecycle
    name: lifecycle-cm
  - name: runtoken
    secret:
      defaultMode: 420
      secretName: 8b2821ccdc9c9fb818502c0e69b96572-runtoken-secrets
  - configMap:
      defaultMode: 420
      name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
    name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-svc
  - name: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
    secret:
      defaultMode: 384
      items:
      - key: id_rsa
        path: .ssh/id_rsa
      - key: id_rsa.pub
        path: .ssh/id_rsa.pub
      - key: authorized_keys
        path: .ssh/authorized_keys
      - key: config
        path: .ssh/config
      secretName: azureml-workloads-8b2821ccdc9c9fb818502c0e69b96572-ssh
  - name: kube-api-access-vpq6k
    projected:
      defaultMode: 420
      sources:
      - serviceAccountToken:
          expirationSeconds: 3607
          path: token
      - configMap:
          items:
          - key: ca.crt
            path: ca.crt
          name: kube-root-ca.crt
      - downwardAPI:
          items:
          - fieldRef:
              apiVersion: v1
              fieldPath: metadata.namespace
            path: namespace
status:
  conditions:
  - lastProbeTime: null
    lastTransitionTime: "2022-07-12T06:35:57Z"
    status: "True"
    type: Initialized
  - lastProbeTime: null
    lastTransitionTime: "2022-07-12T06:35:40Z"
    message: 'containers with unready status: [training-identity-sidecar 1cfc74aae33346e9b77672f82ab26790-lifecycler
      1cfc74aae33346e9b77672f82ab26790-data-capability 1cfc74aae33346e9b77672f82ab26790-cs-capability
      1cfc74aae33346e9b77672f82ab26790-hosttools-capability 1cfc74aae33346e9b77672f82ab26790-execution-wrapper]'
    reason: ContainersNotReady
    status: "False"
    type: Ready
  - lastProbeTime: null
    lastTransitionTime: "2022-07-12T06:35:40Z"
    message: 'containers with unready status: [training-identity-sidecar 1cfc74aae33346e9b77672f82ab26790-lifecycler
      1cfc74aae33346e9b77672f82ab26790-data-capability 1cfc74aae33346e9b77672f82ab26790-cs-capability
      1cfc74aae33346e9b77672f82ab26790-hosttools-capability 1cfc74aae33346e9b77672f82ab26790-execution-wrapper]'
    reason: ContainersNotReady
    status: "False"
    type: ContainersReady
  - lastProbeTime: null
    lastTransitionTime: "2022-07-12T06:35:40Z"
    status: "True"
    type: PodScheduled
  containerStatuses:
  - image: viennaglobal.azurecr.io/cap/cs-capability/installed:westeurope-stable
    imageID: ""
    lastState: {}
    name: 1cfc74aae33346e9b77672f82ab26790-cs-capability
    ready: false
    restartCount: 0
    started: false
    state:
      waiting:
        reason: PodInitializing
  - image: viennaglobal.azurecr.io/cap/data-capability/installed:westeurope-stable
    imageID: ""
    lastState: {}
    name: 1cfc74aae33346e9b77672f82ab26790-data-capability
    ready: false
    restartCount: 0
    started: false
    state:
      waiting:
        reason: PodInitializing
  - image: mcr.microsoft.com/azureml/curated/designer:42
    imageID: ""
    lastState: {}
    name: 1cfc74aae33346e9b77672f82ab26790-execution-wrapper
    ready: false
    restartCount: 0
    started: false
    state:
      waiting:
        reason: PodInitializing
  - image: viennaglobal.azurecr.io/cap/hosttools-capability/installed:westeurope-stable
    imageID: ""
    lastState: {}
    name: 1cfc74aae33346e9b77672f82ab26790-hosttools-capability
    ready: false
    restartCount: 0
    started: false
    state:
      waiting:
        reason: PodInitializing
  - image: viennaglobal.azurecr.io/cap/lifecycler/installed:westeurope-stable
    imageID: ""
    lastState: {}
    name: 1cfc74aae33346e9b77672f82ab26790-lifecycler
    ready: false
    restartCount: 0
    started: false
    state:
      waiting:
        reason: PodInitializing
  - image: mcr.microsoft.com/azureml/amlarc/docker/training-identity-sidecar:1.1.6
    imageID: ""
    lastState: {}
    name: training-identity-sidecar
    ready: false
    restartCount: 0
    started: false
    state:
      waiting:
        reason: PodInitializing
  hostIP: 10.224.0.5
  initContainerStatuses:
  - containerID: containerd://e52fd60f40ac5987160bf63098ba14b0efa68a49c62b9a7241d36bf4959f5ca6
    image: viennaglobal.azurecr.io/exe/execution-wrapper/installed:westeurope-stable
    imageID: viennaglobal.azurecr.io/exe/execution-wrapper/installed@sha256:08e6b8d3cc056f2ab0a379b6c16bc672faa9a1435e33dbd05d0d949bee3a8ff4
    lastState: {}
    name: 1cfc74aae33346e9b77672f82ab26790-execution-wrapper-init
    ready: true
    restartCount: 0
    state:
      terminated:
        containerID: containerd://e52fd60f40ac5987160bf63098ba14b0efa68a49c62b9a7241d36bf4959f5ca6
        exitCode: 0
        finishedAt: "2022-07-12T06:35:42Z"
        reason: Completed
        startedAt: "2022-07-12T06:35:42Z"
  - containerID: containerd://02c4518a2e85078f5ab5acb1f1bc60e7e732a45a2540fc3869ed1e7b718b37e2
    image: mcr.microsoft.com/azureml/amlarc/docker/init-container:1.1.6
    imageID: mcr.microsoft.com/azureml/amlarc/docker/init-container@sha256:3f64fa8d8c40abfef7336f256a96851f58f5b561abc800e000b43b12bb14e079
    lastState: {}
    name: init
    ready: true
    restartCount: 0
    state:
      terminated:
        containerID: containerd://02c4518a2e85078f5ab5acb1f1bc60e7e732a45a2540fc3869ed1e7b718b37e2
        exitCode: 0
        finishedAt: "2022-07-12T06:35:52Z"
        reason: Completed
        startedAt: "2022-07-12T06:35:52Z"
  phase: Pending
  podIP: 10.244.1.14
  podIPs:
  - ip: 10.244.1.14
  qosClass: Burstable
  startTime: "2022-07-12T06:35:40Z"
```

Všimněte si třeba ML_FLOW nastavení, kterými si AzureML sbírá metriky modelu a model samotný.


Do větší úrovně detailu asi teď nemá cenu chodit a nebylo to cílem. Přijde mi velmi zajímavé zjistit, že to co se v Azure ML děje je evidentně složité a dobře promyšlené a díky dnešní standardizaci jako je Kubernetes API a následně Volcano se dá takhle složitý šelmostroj rozběhat nad připojenými clustery nejen z Azure, ale odudkoli. Pokud se vám nechce s ničím babrat, použijte managed nody a hotovo, to dává obrovský smysl ... ale pokud potřebujete hybridní přístup nebo vás prostě jen zajímá co se tam děje, takhle se tomu dá pod kapotu nádherně nahlédnout. A ten motor vypadá skvěle.