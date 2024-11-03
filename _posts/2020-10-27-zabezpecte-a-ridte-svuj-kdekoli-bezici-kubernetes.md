---
layout: post
published: true
title: Zabezpečte a řiďte svůj kdekoli běžící Kubernetes z cloudu s Azure Arc
tags:
- Kubernetes
- Arc
---
Kubernetes je určitě novým základem pro provoz aplikací a řešením, nad kterým lze dál stavět a například do něj přinášet cloudové služby. Samotný Kubernetes ale není nic jednoduchého - určitě potřebuji ho nějak spravovat, monitorovat, sbírat logy, telemetrii, vytvářet bezpečnostní politiky a synchronizovat konfigurace. Ať už jde o Azure Kubernetes Service, AKS Engine v Azure Stack Hub, Kubernetes v Azure Stack HCI či Azure Stack Edge nebo váš vlastní cluster postavený v datovém centru s využitím OpenShift či VMware nebo jsou to K3s clustery z vašich IoT bran v továrnách, u všech těchto variant je centrální řízení hodně důležité. Přesně to vám nabízí Azure Arc for Kubernetes, který si dnes vyzkoušíme.

O tom co je Azure Arc už jsem psal před rokem: [Pohled na hybridní svět IT nově i s Azure Arc](https://www.tomaskubica.cz/post/2019/pohled-na-hybridni-svet-it-nove-s-azure-arc/)

# Co přináší Azure Arc for Kubernetes
Toto řešení umožňí napojit vaše kdekoli běžící clustery na Azure a promítnout je do portálu. To má myslím dost zásadní přínosy:
- Sběr logů ze všech kontejnerů na jedno místo s tím, že přístup k logům lze řídit přes jednotnou identitu AAD granulárně na základě clusterů a lze používat sofistikovaný jazyk Kusto (KQL) pro prohledávání logů
- Sběr telemetrie clusterů i kontejnerů a jejich vizualizace v portálu včetně možnosti napojení do Grafana (Azure Monitor je pak datový zdroj)
- Připravené Workbooky pro klíčové parametry - flexibilní vizualizace
- Alerting a spouštění workflow na základě událostí (např. Pody, které nemohou nastartovat nebo se dokola otáčí)
- Inventarizace - napojené clustery jsou další zdroj v Azure, takže patří do subskripce, resource group, mají tagy a jsou v nich informace o Kubernetes objektech a jejich historii
- Řízení bezpečnostních politik z jednoho místa s Azure Policy a to pohodlně a bez nutnosti znát komplikovaný Rego jazyk nebo se starat o nasazení Open Policy Agent s Gatekeeper
- Řízení základních konfigurací clusterů přes GitOps principy spravované přímo z Azure - nasazení a aktualizace systémových komponent (Ingress implementace, CRDs, aplikační platformy, ...) nebo základních aplikací (metoda "cluster volá domů a zjišťuje co má dělat")

Umím si představit, že v budoucnu některé vlastnosti, které umí AKS ale Arc for Kubernetes ještě ne, se objeví - třeba možnost pracovat s Kubernetes objekty z pěkného Azure GUI nebo RBAC do clusteru s integrací na single-sign-on v AAD (včetně MFA a dalších vychytávek) a RBAC konfigurace z GUI. Zatím to v Arc není, ale AKS ano a je možné, že se později objeví. Druhá sada funkcí může být v budoucnosti řešena přes Kubernetes Cluster API, tedy standardizované API pro ovládání podvozku clusteru. Pokud například VMware Tanzu nabídne cluster API, bude moci Azure řídit vznik clusterů a jejich škálování i v onpremises.

Za mě je těch výhod opravdu hodně a napojení všech clusterů do Azure mi dává zásadní smysl.

# Praktické nalodění Kubernetes do Azure Arc
Jdeme na to - nasazení ve finále není složité a dá se dost dobře automatizovat. Pokud máte tisíc clusterů z vašich IoT bran, ani to nebude problém.

## Příprava na straně Azure a postavení Kubernetes ve VM
Nejprve si zaregistruji nějaké providery.

```bash
az provider register --namespace Microsoft.PolicyInsights
az provider register --namespace Microsoft.Kubernetes
az provider register --namespace Microsoft.KubernetesConfiguration
```

Vytvoříme si Resource Group a virtuálku, v které zprovozním Kubernetes - samozřejmě může běžet kdekoli.

```bash
az group create -n kubernetes-rg -l westeurope
az vm create -n kubernetes-vm \
    -g kubernetes-rg \
    --image UbuntuLTS \
    --size Standard_B4ms \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --no-wait
```

Pro nalodění do Arc a Azure Policy bude cluster potřebovat účet v AAD (Service Principal) a limitovaná práva v subskripci. To si připravíme a také si uložíme login údaje.

```bash
# Vytvoreni SP
export CLIENT_SECRET=$(az ad sp create-for-rbac -n "http://tomasArcKubernetes" --skip-assignment --query password -o tsv)
export CLIENT_ID=$(az ad sp show --id "http://tomasArcKubernetes" --query appId -o tsv)
export TENANT_ID=$(az account show --query tenantId -o tsv) 

# Role pro Arc onboarding
az role assignment create \
    --role 34e09817-6cbe-4d01-b1a2-e0eac5743d41 \
    --assignee $CLIENT_ID \
    --scope /subscriptions/$(az account show --query id -o tsv) 

# Role pro policy
az role assignment create \
    --role 66bb4e9e-b016-4a94-8249-4c0511c2be84 \
    --assignee $CLIENT_ID \
    --scope /subscriptions/$(az account show --query id -o tsv) 
```

Dále si založíme Log Analytics workspace a vyexportujeme jeho údaje. Do workspace pak nasadíme Azure Monitor for Containers solution (tedy "vylepšíme" tento workspace o schopnost práce s kontejnery).

```bash
export WORKSPACE_NAME=tomasarckube123

az monitor log-analytics workspace create -n $WORKSPACE_NAME -g kubernetes-rg

export WORKSPACE_ID=$(az monitor log-analytics workspace show -n $WORKSPACE_NAME -g kubernetes-rg --query customerId -o tsv)
export WORKSPACE_RESOURCE_ID=$(az monitor log-analytics workspace create -n $WORKSPACE_NAME -g kubernetes-rg --query id -o tsv)
export WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys -n $WORKSPACE_NAME -g kubernetes-rg --query primarySharedKey -o tsv)

az deployment group create -g kubernetes-rg \
    -p workspaceResourceId=$WORKSPACE_RESOURCE_ID \
    -p workspaceRegion=westeurope \
    -u https://raw.githubusercontent.com/microsoft/Docker-Provider/ci_dev/scripts/onboarding/templates/azuremonitor-containerSolution.json
```

Perfektní. Všechny stažené údaje budu potřebovat ve VM, do které se připojím, tak se připravím příkazy pro jejich uložení, ať to netípám ručně.

```bash
echo export CLIENT_SECRET=\"$CLIENT_SECRET\" &&
echo export CLIENT_ID=\"$CLIENT_ID\" &&
echo export TENANT_ID=\"$TENANT_ID\" &&
echo export WORKSPACE_ID=\"$WORKSPACE_ID\" &&
echo export WORKSPACE_RESOURCE_ID=\"$WORKSPACE_RESOURCE_ID\" &&
echo export WORKSPACE_KEY=\"$WORKSPACE_KEY\"
```

## Instalace Kubernetes a nalodění do Azure
Připojme se teď do VM a skočme do privilegovaného uživatele a vložme údaje.

```bash
ssh $(az network public-ip show -n kubernetes-vmPublicIP -g kubernetes-rg --query ipAddress -o tsv)

sudo -i

# Vložíme export údajů do proměnných prostředí
```

Nainstalujeme zjednodušenou verzi Kubernetes - projekt K3s od Rancher, což nám teď rozhodně stačí. Je to velmi oblíbené řešení pro malé clustery na kraji jako jsou IoT brány.

```bash
curl -sfL https://get.k3s.io | sh -
```

Nainstalujeme Helm a namíříme ho na správnou konfiguraci.

```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

Dál budeme potřebovat Azure CLI a jeho extensions na připojení clusterů.

```bash
apt-get update
apt-get install -y ca-certificates curl apt-transport-https lsb-release gnupg
curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.asc.gpg > /dev/null
AZ_REPO=$(lsb_release -cs)
echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | tee /etc/apt/sources.list.d/azure-cli.list
apt-get update
apt-get install -y azure-cli

az extension add --name connectedk8s
az extension add --name k8sconfiguration
```

Zalogujeme se do Azure účtem service principal, co jsme vytvořili na začátku.

```bash
az login --service-principal -u $CLIENT_ID -p $CLIENT_SECRET --tenant $TENANT_ID
```

Nalodíme cluster do Azure Arc for Kubernetes a uložíme si resource ID, které vznikne.

```bash
az connectedk8s connect --name tomas-k3s --resource-group kubernetes-rg --tags logAnalyticsWorkspaceResourceId=$WORKSPACE_RESOURCE_ID
export clusterId=$(az connectedk8s show --name tomas-k3s --resource-group kubernetes-rg --query id -o tsv)
```

Nainstalujeme Azure Monitor for Containers

```bash
helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com/
helm repo update
helm upgrade -i azuremonitor incubator/azuremonitor-containers --set omsagent.secret.wsid=$WORKSPACE_ID,omsagent.secret.key=$WORKSPACE_KEY,omsagent.env.clusterId=$clusterId 
```

Nainstalujeme Azure Policy

```bash
helm repo add azure-policy https://raw.githubusercontent.com/Azure/azure-policy/master/extensions/policy-addon-kubernetes/helm-charts
helm repo update
helm upgrade -i azure-policy-addon azure-policy/azure-policy-addon-arc-clusters \
    --set azurepolicy.env.resourceid=$clusterId  \
    --set azurepolicy.env.clientid=$CLIENT_ID \
    --set azurepolicy.env.clientsecret=$CLIENT_SECRET \
    --set azurepolicy.env.tenantid=$TENANT_ID
```

# Cluster je v Azure
Můj cluster se promítl do Azure jako samostatný zdroj.

![](/images/2020/2020-10-13-08-59-49.png){:class="img-fluid"}

![](/images/2020/2020-10-13-09-00-08.png){:class="img-fluid"}

Jednotlivé funkční vlastnosti si rozebereme v příštích článcích, protože nejsou specifické pro Arc - platí i pro AKS.

Vidím řízení konfigurací, nasazení a aplikací clusteru GitOps způsobem.

![](/images/2020/2020-10-13-09-01-19.png){:class="img-fluid"}

Můžeme začít přiřazovat politiky, například omezení běhu pod rootem, přístupy na registry a tak podobně.

![](/images/2020/2020-10-13-09-02-50.png){:class="img-fluid"}

![](/images/2020/2020-10-13-09-02-30.png){:class="img-fluid"}

K dispozici je moc užitečný monitoring.

![](/images/2020/2020-10-13-09-03-31.png){:class="img-fluid"}

Možnost vytvářet alerty jako reakce na události.

![](/images/2020/2020-10-13-09-03-53.png){:class="img-fluid"}

Uloženy jsou logy z kontejnerů, inventář a události Kubernetu.

![](/images/2020/2020-10-13-09-05-02.png){:class="img-fluid"}

Využít můžeme i dalších připravených vizualizací ve formě workbooků.

![](/images/2020/2020-10-13-09-05-36.png){:class="img-fluid"}

![](/images/2020/2020-10-13-09-08-48.png){:class="img-fluid"}


Pokud už vás ukázka nebaví, můžete ji smazat.

```bash
ad sp delete -id "http://tomasArcKubernetes"
ad ad app delete -id "http://tomasArcKubernetes"
az group delete -n kubernetes-rg -y --no-wait
```


Azure Arc for Kubernetes dokáže zajistit řízení vašich clusterů ať už jsou kdekoli a množství funkcí se bude jistě dál rozšiřovat. Navíc nalodění clusterů do Azure bude základem pro využívání dalších služeb nad tím. Ať to budou služby datové jako je SQL nebo PostgreSQL nebo aplikační jako je Logic App, Azure Functions nebo API Management či z oblasti umělé inteligence jako je vision, custom vision, překlady, analýza textu, formulářů a mnoho dalších, hlavní hybridní platformou bude Kubernetes připojený do správy Azure. Pro cloudové věci použijte nativní cloudové služby od A do Z. Pokud ale musí váš cluster běžet pověšený na stromech Amazonské džungle (ať už doslova v pralese jako IoT brána nebo v AWS jako EKS), napojte ho do Azure přes Arc for Kubernetes a stavte nad tím.