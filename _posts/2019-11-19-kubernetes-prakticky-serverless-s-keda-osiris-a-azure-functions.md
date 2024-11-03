---
layout: post
title: 'Kubernetes praticky: serverless s KEDA, Osiris a Azure Functions'
tags:
- Kubernetes
- Serverless
---
Serverless jako jsou Azure Functions přináší fascinující model tvorby a provozu aplikací, kdy se nestaráte o nic jiného, než váš kód a data. Pokud jste si před 10 lety zkoušeli v hlavě uspořádat co je to cloud, takhle ta představa možná vypadala. A pokud ne, tak by asi měla - zejména, pokud jste vývojář. Jenže tyto systémy jsou v cloudu a napsat to takovým způsobem znamená lockin ke konkrétnímu cloudu, zhoršenou exit strategii nebo nutnost připravovat různé varianty aplikace pro různá prostředí. Ale je to doopravdy tak? Nemusí. Podívejme se dnes na serverless "se servery".

# Co potřebuji pro svoje vlastní serverless
Minimálními požadavky na serverless budou určitě schopnost škálovat už od 0 (tedy pokud není žádný požadavek uživatele, neobsazuje můj kód žádné zdroje), schopnost škálovat podle potřeby (evet-driven, od instance kódu až po infrastrukturu) a mechanismus bindingu bezestavových služeb na perzistentní vrstvy přímo platformou. Samozřejmě k tomu by se hodil ještě monitoring, podpora v IDE, podpora CI/CD a tak dále, ale zůstaňme u základů.

## Platformu, která škáluje do nuly (startovací schopnost)
Pokud můj kód aktuálně není potřeba, neměl by zabírat žádné místo v paměti ani mít přidělené CPU. Jinak řečeno potřebujeme škálovat včetně nuly, nebo ještě jinak - mít schopnost nastartovat a vypnout. Platorma tedy musí například chápat, že určitá funkce zpracovává data z fronty. Platforma sama bude zjišťovat, jestli jsou ve frontě nějaké zprávy a pokud se objeví, musí být schopná váš kód rychle nahodit. Totéž třeba pro web přístup - platforma by se měla dozvědět, že se někdo snaží třeba načíst stránku a rychle nastartovat příslušý webík.

## Platformu, která škáluje podle potřeby
Kromě nahození a shození musí mít platforma škálování do šířky podle metriky, která je pro funkci klíčová. U event-driven to musí být právě o těch událostech (například délka nevyzvednuté fronty jako rozhodující parametr pro určení počtu běžících instancí), ne tradiční metriky typu zatížení CPU. Nahodit instance je jen začátek, ale ty typicky běží v nějakém clusteru s určitou kapacitou a ta může dojít. Potřebujeme tedy mít i schopnost zvětšit cluster, například v Kubernetes přidat nové nody (VM) a to relativně rychle a flexibilně.

## Platformu pro můj kód a jednoduché provázání na perzistentní vrstvy
Serverless zjednodušuje tvorbu aplikací tím, že provázanost na perzistentní vrstvy pro mě řeší platforma samotná a já se tak mohu soustředit na kód, který události zpracovává nebo generuje. Tak například funkce má reagovat na novou zprávu v Azure IoT Hub, tuto parsovat (třeba převést z avro na json) a uložit do Cosmos DB. Místo přemýšlení jak se o zprávě dozvědět, jak ji vyzvednout, jak se ověřovat nebo na jaké adrese co běží, dostane váš aplikační kód zprávu rovnou jako proměnnou. A když chci zapsat výsledek do Cosmos DB? Stačí mi buď jednoduše vrátit JSON jako návratovou hodnotu funkce (a platformě řeknu, že return value má prostě zapsat do Cosmos DB) nebo pokud toho vracím víc ji zapíšu do nějaké variable (například return context).

# KEDA, Osiris a Azure Functions
Project KEDA znamená Kubernetes-based Event Driven Autoscaling a najdete ho na [GitHubu](https://github.com/kedacore/keda). Odstartovala ho spolupráce Microsoft a Red Hat a jeho záměrem je vytvořit v Kubernetes platformu, která škáluje na základě eventů a to až do nuly. Funguje to tak, že KEDA se napojí na eventy (například frontu) a na základě těchto informací přináší telemetrii pro standardní Horizontal Pod Autoscaler v Kubernetes (škálování on 1 nahoru) a současně řeší škálování do nuly, tedy nahazuje či shazuje Deploymenty. KEDA podporuje celou řadu eventů - hromadu služeb v Azure, ale i AWS a on-premises (například generická Kafka).

![](/images/2019/2019-11-17-09-23-21.png){:class="img-fluid"}

Vhodným doplňkem projektu KEDA je komponenta Osiris. Ta se stará o škálování do nuly pro HTTP-based funkce, tedy ty, které se mají probouzet a škálovat na základě počtu HTTP dotazů. Funguje to podobně, ale Osiris musí u web služby, která je uspaná (scale to zero), nastavit svůj vlastní endpoint, aby zjistil, že se někdo snaží na ni dobouchat a nahodil včas Deployment. I tento projekt samozřejmě najdete na [GitHubu](https://github.com/deislabs/osiris).

Třetí je aplikační framework a my se zaměříme na Azure Functions. Runtime hostitele najdeme na [GitHubu](https://github.com/Azure/azure-functions-host/) stejně jako některé další komponenty jako je CLI apod. Tohle už je aplikační platforma, která řeší věci typu binding na službu, triggery a tak podobně.

# A jaký je rozdíl oproti dalším projektům, třeba OpenFaaS, Kubeless nebo Knative?
V této oblasti se toho děje opravu hodně. Projekty OpenWhisk a OpenFaaS se snaží vyřešit všechny aspekty naráz a nemají závislost na Kubernetes, takže se dají použít i ve světě VM (samozřejmě s drastickým omezením celkové autoškálovatelnosti), což ale může zesložiťovat jejich provoz a škálování v Kubernetes. Kubeless jde podobný směrem, ale více se zaměřuje na integraci s Kubernetes - na druhou stranu pokud vím stále nemá škálování od nuly, což je u serverless zásadní. Knative je integrovaný do Kubernetes a soustředí se hlavně na routing zpráv a škálování na nulu, nicméně má dependency na Istio service mesh, což vede na víc jak 100 CRDs a je to masakr. Nicméně Knative projekt zdá se pochopil, že hard dependence na Istio není dobrá věc a tak pracuje na podpoře Service Mesh Interface (tedy vrstvě abstrakce nad service mesh implementací, která tak může být vyměnitelná...ale o tom jindy). Ještě je tu Fission a Fn, ale o těch moc moc nevím a nezdá se mi, že je o nich tolik slyšet.

Microsoft k tomu přistupuje po vrstvách a to mi přijde rozumné. Event-driven serverless model nativní pro Kubernetes ale bez dependence na jiné nadstavby? KEDA. Totéž pro http-based? Osiris. Serverless framework z pohledu aplikačního? Azure Functions. Klasická Linux filozofie - dělat jednu věc a tu pořádně. To se mi líbí. Azure Functions jsou přecijen zaměřené hodně na Azure a aktuálně nepodporují binding například AWS služeb, ale KEDA, jako event-driven škálovací komponenta, ano. Zkrátka vyberete si v dané vrstvě to, co potřebujete.

# Serverless event-driven příklad (worker funkce vyzvedávající z fronty)
Nejdřív si nainstalujeme Azure Functions pro lokální vývoj a správu: [https://github.com/azure/azure-functions-core-tools#installing](https://github.com/azure/azure-functions-core-tools#installing)

Teď si vytvořím adresář a inicializuji novou Function s tím, že ji budu chtít balit do Dockeru.

```bash
mkdir keda-test
cd keda-test

func init . --docker --worker-runtime node --language javascript

# Vytvoříme novou funkci. Dostaneme na výběr s několika triggerů.
func new

Select a template:
Azure Blob Storage trigger
Azure Cosmos DB trigger
Durable Functions activity
Durable Functions HTTP starter
Durable Functions orchestrator
Azure Event Grid trigger
Azure Event Hub trigger
HTTP trigger
IoT Hub (Event Hub)
Azure Queue Storage trigger
SendGrid
Azure Service Bus Queue trigger
Azure Service Bus Topic trigger
Timer trigger
```

Použil jsem Azure Queue Storage trigger.

Vytvořme si storage account a frontu.

```powershell
export storageName="myuniquekedastorage"
az storage account create --sku Standard_LRS -g cp-aks -n $storageName
export connectionString=$(az storage account show-connection-string --n $storageName --query connectionString -o tsv)
az storage queue create -n myqueue --connection-string $connectionString
```

Provedeme teď nastavení lokálního prostředí Functions. Nejdřív otevřeme local.settings.json a jako hodnotu připravené AzureWebJobsStorage použijeme connection string získaný výše. Dál v adresáři funkce najdeme soubor function.json, kde je popsaný trigger. U něj je jméno fronty (tam zadám myqueue) a connection string, který budu referencovat na proměnnou AzureWebJobsStorage.

Poslední věc. Azure Functions si při budování runtime (například sestavení kontejneru) potřebují nainstalovat příslušné komponenty (můžeme jim klidně říkat drivery). Modifikujeme host.json soubor takto:

```json
{
    "version": "2.0",
    "extensionBundle": {
        "id": "Microsoft.Azure.Functions.ExtensionBundle",
        "version": "[1.*, 2.0.0)"
    }
}
```

Teď můžeme otestovat funkci lokálně. Spustíme ji a přes Storage Explorer vytvoříme novou zprávu. Funkce ji zpracuje.

```bash
func start


                  %%%%%%
                 %%%%%%
            @   %%%%%%    @
          @@   %%%%%%      @@
       @@@    %%%%%%%%%%%    @@@
     @@      %%%%%%%%%%        @@
       @@         %%%%       @@
         @@      %%%       @@
           @@    %%      @@
                %%
                %

Azure Functions Core Tools (2.7.1846 Commit hash: 458c671341fda1c52bd46e1aa8943cb26e467830)
Function Runtime Version: 2.0.12858.0
[17.11.2019 8:57:31] Building host: startup suppressed: 'False', configuration suppressed: 'False', startup operation id: '34b868d6-deb0-4bf2-afe5-87a9ea775d24'
[17.11.2019 8:57:33] Reading functions metadata
[17.11.2019 8:57:33] 0 functions found
[17.11.2019 8:57:36] Initializing Warmup Extension.
[17.11.2019 8:57:36] Initializing Host. OperationId: '34b868d6-deb0-4bf2-afe5-87a9ea775d24'.
[17.11.2019 8:57:36] Host initialization: ConsecutiveErrors=0, StartupCount=1, OperationId=34b868d6-deb0-4bf2-afe5-87a9ea775d24
...
[17.11.2019 8:57:41] [17.11.2019 9:01:18] Job host started

```

Zpráva se zpracuje - funguje nám to. Pojďme teď tuto Azure Function nasadit v Kubernetes. 

Nejdřív si nainstalujeme do Kubernetes clusteru KEDA (instalátor nám rovněž nasadí i příbuzný projekt Osiris). To můžeme udělat buď přes Helm, Kubernetes YAML nebo pohodlně přímo z Functions CLI.

```bash
func kubernetes install --namespace keda
```

Jak na instalaci funkce samotné? Stačí se zalogovat do mého Azure Container Registry a spustit func CLI pro deployment do Kubernetes. To způsobí build Docker image lokálně (můžete se mrknout na Dockerfile, pokud chcete) a následně to nasadí do Kubernetes. Jednoduché!

```bash
cd keda-test/
export registryName="cpacrbn7n3upudvjcq"
az acr login -n $registryName

func kubernetes deploy --name keda-test \
    --registry $registryName".azurecr.io" \
    --max-replicas 10 \
    --cooldown-period 30
```

Po chvilce se podívám a nemám žádný Pod.

```bash
kubectl get pods
No resources found in default namespace.
```

Vytvořím zprávu ve frontě - Pod naskočí.

```bash
kubectl get pods
NAME                        READY   STATUS    RESTARTS   AGE
keda-test-df9ff55d6-pgrg4   1/1     Running   0          14s
```

Pokud bych teď vygeneroval velké množství zpráv, bude naskakovat další pro urychlení zpracování (KEDA poskytuje telemetrii pro HPA, které to zařídí) a samozřejmě pokud by došla kapacita clusteru, zafunguje AKS cluster autoscaler a přidá Node (nebo ideálně ještě kombinovat s AKS Virtual Nodes, kdy kontejnery poběží přímo v Azure bez nutnosti mít pod nimi Azure VM).

# Serverless HTTP-based příklad (REST API)
V případě funkcí, které reagují na HTTP volání, využijeme komponentu Osiris. Už ji máme v clusteru nasazenou, protože func CLI instaluje oboje najednou.

Stejně jako minule založíme adresář pro funkci postavenou na Javascriptu a vytvoříme novou s HTTP trigger.

```powershell
mkdir keda-webapi
cd keda-webapi

func init . --docker --worker-runtime node --language javascript

# Create new Azure Function and select HTTP Trigger
func new

Select a template:
Azure Blob Storage trigger
Azure Cosmos DB trigger
Durable Functions activity
Durable Functions HTTP starter
Durable Functions orchestrator
Azure Event Grid trigger
Azure Event Hub trigger
HTTP trigger
IoT Hub (Event Hub)
Azure Queue Storage trigger
SendGrid
Azure Service Bus Queue trigger
Azure Service Bus Topic trigger
Timer trigger
```

Funkci zabalíme do kontejneru a nasadíme do AKS tímto příkazem:

```bash
func kubernetes deploy --name keda-webapi \
    --registry $registryName".azurecr.io" \
    --max-replicas 10 
```

Počkejme teď 5 minut (výchozí doba škálování do nuly) a žádný Pod nám neběží. Zjistíme si ale IP adresu Service.

```bash
kubectl get pods
No resources found in default namespace.

kubectl get service
NAME               TYPE           CLUSTER-IP    EXTERNAL-IP    PORT(S)        AGE
keda-webapi-http   LoadBalancer   10.0.17.82    52.149.72.46   80:31350/TCP   40h
kubernetes         ClusterIP      10.0.0.1      <none>         443/TCP        41h
```

Pro zajímavost. Jak to funguje? Osiris modifikuje službu tak, že když není nasazen žádný Pod, tak jí nedá selektor a ručně do ní přidá svůj vlsatní endpoint. Díky tomu se dozví, že někdo službu chce a může začít startovat příslušný Pod.

```bash
kubectl describe service keda-webapi-http
Name:                     keda-webapi-http
Namespace:                default
Labels:                   <none>
Annotations:              kubectl.kubernetes.io/last-applied-configuration:
                            {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{"osiris.deislabs.io/deployment":"keda-webapi-http","osiris.deislabs.io/enab...
                          osiris.deislabs.io/deployment: keda-webapi-http
                          osiris.deislabs.io/enabled: true
                          osiris.deislabs.io/selector: eyJhcHAiOiJrZWRhLXdlYmFwaS1odHRwIn0=
Selector:                 <none>
Type:                     LoadBalancer
IP:                       10.0.17.82
LoadBalancer Ingress:     52.149.72.46
Port:                     <unset>  80/TCP
TargetPort:               80/TCP
NodePort:                 <unset>  31350/TCP
Endpoints:                10.240.0.49:5000
Session Affinity:         None
External Traffic Policy:  Cluster
Events:                   <none>

get pods --all-namespaces -o wide | grep 10.240.0.49
keda          osiris-osiris-edge-activator-b459b848f-hkkbs               1/1     Running   0          41h   10.240.0.49   aks-nodepool1-52496067-vmss000001   <none>           <none>
```

Otevřu teď prohlížeč a namířím na public IP služby. Uvidím, že Pod rychle naběhne - většinou do deseti vteřin, takže browser to ani nestihne vzdát.

```bash
kubectl get pods
NAME                                READY   STATUS    RESTARTS   AGE
keda-webapi-http-6cc57ccb68-hqj5q   2/2     Running   0          16s
```

Tak jsme si vyzkoušel serverless v Kubernetes a Azure Functions. Serverless v Azure tak můžete provozovat tak, jak se na cloud sluší - kompletně platformně a platit jen za jednotlivá spuštění funkce případně jít do Azure Functions Premium, které vám umožní zbavit se slow-start problému (vypnout uspávání) nebo integrovat funkce do VNETu. Nicméně pokud potřebujete stejné Azure Functions provozovat v on-premises, v jiném cloudu nebo v IoT zařízeních, jde to. Nejste zamčeni a díky projektům KEDA a Osiris můžete mít z Kubernetes serverless provozek pro funkce jako služba postavené na Azure Functions i jiných aplikačních platformách.