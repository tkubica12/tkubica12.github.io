---
layout: post
title: 'Kubernetes prakticky: řízení přístupu (RBAC) s integrací na Azure Active Directory'
tags:
- Kubernetes
- Security
- Governance
---
Máte Azure Kubernetes Service a všichni do ní přistupujete pod sdíleným admin účtem? Tento postup pro produkčnější nasazení není vhodný a velmi doporučuji nasadit řízení přístupu (RBAC). Kde ale uživatelské účty vzít a zajistit maximální bezpečnost přístupů třeba včetně vícefaktorového ověřování? Azure Kubernetes Service můžete elegantně napojit na identitní systém Azure Active Directory a díky tomu zajistit nejen základní ověřování, ale i pokročilé funkce typu Advanced Identity Protection nebo Multi-factor Authentication. Dnes si to spolu vyzkoušíme.

# Vytvoření AKS clusteru s napojením na AAD
První co si musíme zajistit je integrace AKS s AAD. Tato funkcionalita je oddělená od standardního fungování clusteru, jinak řečeno AKS může běžet v jednom tenantu (a odtud vytvářet zdroje apod.) a přitom autentizace uživatelů může být i z jiného tenantu (obvykle ale namíříte uživatele na stejný tenant, jako váš Azure portál). Funguje to tak, že pro AKS vytvoříte aplikační registrace v AAD, seberete si potřebné identifikátory a klíče a použijete při vytváření clusteru.

[https://docs.microsoft.com/en-us/azure/aks/azure-ad-integration](https://docs.microsoft.com/en-us/azure/aks/azure-ad-integration)

Já mám cluster vytvořený, takže můžeme jít dál.

# Nasazení rolí a oprávnění
Nejprve se do cluster připojím administrátorským účtem. Jeho údaje získám tak, že mám právo na AKS resource v Azure a zavolám následující příkaz s přepínačem --admin.

```bash
az aks get-credentials -n aks -g aks --admin
```

Jako administrátor založím dva namespace a ověřím, že mám plná práva, například na vypsání Podů ze všech namespace včetně systémových.

```bash
kubectl create namespace app1
kubectl create namespace app2
kubectl get pods --all-namespaces
```

Nejprve si založíme specifické RBAC role. Mám dva namespace s app1 a app2. Pro každou aplikaci si chci vytvořit dvě role - jednu, která může zapisovat objekty typu Pod, Service, Deployment, Configmap a Ingress a druhou, která může to samé jenom číst. Žádná z těchto rolí ale nemá další práva, například nemůže vytvářet a měnit Secret, nicméně potřebuji, aby je operátor mohl používat (tedy využít při nasazení).

Moje sada rolí bude vypadat nějak takhle:

```yaml
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: app1
  name: app1Operator
rules:
- apiGroups: ["*"] 
  resources:
    - pods
    - services
    - deployments
    - configmaps 
    - ingress
  verbs:
    - get
    - watch
    - list
    - create
    - delete
- apiGroups: ["*"] 
  resources:
    - secrets
  verbs:
    - get
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: app1
  name: app1Reader
rules:
- apiGroups: ["*"] 
  resources:
    - pods
    - services
    - deployments
    - configmaps 
    - ingress
  verbs:
    - get
    - watch
    - list
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: app2
  name: app2Operator
rules:
- apiGroups: ["*"] 
  resources:
    - pods
    - services
    - deployments
    - configmaps 
    - ingress
  verbs:
    - get
    - watch
    - list
    - create
    - delete
- apiGroups: ["*"] 
  resources:
    - secrets
  verbs:
    - get
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: app2
  name: app2Reader
rules:
- apiGroups: ["*"] 
  resources:
    - pods
    - services
    - deployments
    - configmaps 
    - ingress
  verbs:
    - get
    - watch
    - list
```

Všimněte si formátu. Vytváříme Role a ta musí být svázána s konkrétním namespace, definujeme které objekty a jaké příkazy na nich dovolujeme.

Dále chci roli pro bezpečáka, který bude mít na starost správu Secret. To nebudu chtít zvlášť pro jednotlivé namespace, ale roli pro celý cluster, takže použiji typ ClusterRole.

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: secretsOperator
rules:
- apiGroups: ["*"] 
  resources:
    - secrets
  verbs:
    - get
    - watch
    - list
    - create
    - delete
```

To je definice rolí a my teď potřebujeme provést jejich svázání s autentizačním systémem, tedy konkrétním uživatelem nebo bezpečnostní skupinou. Objekt se jmenuje RoleBinding resp. ClusterRoleBinding a typ je buď User (tam použijeme konkrétní UPN uživatele) nebo Group (v tom případě nemůžeme použít název skupiny, ale její unikátní object ID, které najdete ve vašem AAD). V mém případě mám uživatele usr1, usr2 a usr3 s tím, že uživatel usr3 je součástí bezpečnostní skupiny, jejíž ID použiji. Moje vázání vypadá takhle:

```yaml
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: app1OperatorBinding
  namespace: app1
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: "usr1@mujazure.tk"
roleRef:
  kind: Role
  name: app1Operator
  apiGroup: rbac.authorization.k8s.io
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: app2OperatorBinding
  namespace: app2
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: "usr2@mujazure.tk"
roleRef:
  kind: Role
  name: app2Operator
  apiGroup: rbac.authorization.k8s.io
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: app1ReaderBinding
  namespace: app1
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: "usr2@mujazure.tk"
roleRef:
  kind: Role
  name: app1Reader
  apiGroup: rbac.authorization.k8s.io
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: app2ReaderBinding
  namespace: app2
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: "usr1@mujazure.tk"
roleRef:
  kind: Role
  name: app2Reader
  apiGroup: rbac.authorization.k8s.io
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: secretsOperatorBinding
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: "64a413b4-1376-4e18-8718-d8c053f5d019"
roleRef:
  kind: ClusterRole
  name: secretsOperator
  apiGroup: rbac.authorization.k8s.io
```

Teď stačí jen tyto objekty aplikovat.

```bash
kubectl apply -f customRoles.yaml
kubectl apply -f customRolesBindings.yaml
```

# Ověřme si funkčnost definovaných přístupů
Pojďme si teď naše přístupy vyzkoušet. Pro jednoduchost odstraním původní soubor s přihlášením a načtu si ho znova s tím, že tentokrát přepínač --admin nepoužiji. To znamená, že můj config soubor pro kubectl nemá informaci a konkrétním uživateli a ví, že bude potřeba se přihlásit přes AAD.

```bash
rm ~/.kube/config
az aks get-credentials -n aks -g aks
```

Zkusíme co se bude dít, pokud se pokusíme vytvořit Deployment v namespace app1.

```bash
kubectl run nginx --image nginx -n app1
```

![](/images/2019/2019-04-23-10-51-15.png){:class="img-fluid"}

![](/images/2019/2019-04-23-10-51-57.png){:class="img-fluid"}

Přihlásím se jako usr1@mujazure.tk. Všimněte si, že díky interaktivnímu přihlášení přes browser zafungují všechny vlastnosti AAD jako je vícefaktorové ověření, identity protection, conditional access apod.

![](/images/2019/2019-04-23-10-52-57.png){:class="img-fluid"}

![](/images/2019/2019-04-23-10-53-30.png){:class="img-fluid"}

Výborně, Pod běží!

```bash
$ kubectl get pods -n app1
NAME                    READY     STATUS    RESTARTS   AGE
nginx-dbddb74b8-6jk5v   1/1       Running   0          1h
```

Co kdybychom si vytvořili Deployment v namespace app2? Nemám na to práva.

```bash
$ kubectl run nginx --image nginx -n app2
Error from server (Forbidden): deployments.extensions is forbidden: User "usr1@mujazure.tk" cannot create resource "deployments" in API group "extensions" in the namespace "app2"
```

A co když se pokusíme vytvořit Secret? Dle očekávání také nemám práva.

```bash
$ echo -n 'admin' > ./username
$ kubectl create secret generic username --from-file=./username -n app1
Error from server (Forbidden): secrets is forbidden: User "usr1@mujazure.tk" cannot create resource "secrets" in API group "" in the namespace "app1"
```

Pojďme se teď přihlásit jako usr2. V mém souboru config je v tuto chvíli nacachován token usr1, aby se nemusel přihlašovat pořád dokola. Abych se ho zbavil, vymažu celý config a stáhnu si ho znovu. Přihlásím se jako usr2 a zkusím vytvořit Deployment v app1 namespace, totéž v app2 namespace a také vylistuji Pody v app1. Co očekáváme? usr2 má zapisovací právo do app2, ale do app1 má pouze čtecí - vytvořit Pod by tedy jít nemělo, ale přečíst si je ano.

```bash
$ rm ~/.kube/config

$ az aks get-credentials -n aks -g aks
Merged "aks" as current context in /home/tomas/.kube/config

$ kubectl run nginx2 --image nginx -n app1
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code C9TDNLFZ9 to authenticate.
Error from server (Forbidden): deployments.extensions is forbidden: User "usr2@mujazure.tk" cannot create resource "deployments" in API group "extensions" in the namespace "app1"

$ kubectl run nginx2 --image nginx -n app2
deployment.apps "nginx2" created

$ kubectl get pods -n app1
NAME                    READY     STATUS    RESTARTS   AGE
nginx-dbddb74b8-6jk5v   1/1       Running   0          1h

$ kubectl get pods -n app2
NAME                     READY     STATUS    RESTARTS   AGE
nginx2-cc5f746cb-mfnvp   1/1       Running   0          24s
```

Jak tedy s těmi Secret? Znova vygumuji config soubor a přihlásím se tentokrát jako usr3@mujazure.tk, který je členem skupiny, která má právo vytvářet Secret objekty.

```bash
$ rm ~/.kube/config

$ az aks get-credentials -n aks -g aks
Merged "aks" as current context in /home/tomas/.kube/config

$ echo -n 'admin' > ./username

$ kubectl create secret generic username --from-file=./username -n app1
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code CNYJHGTD5 to authenticate.
secret "username" created
```

Výborně, založení Secret se povedlo. Jaké práva na něj má usr1@mujazure.tk? Uživatel může udělat operace get nad secret ve svém namespace (ale ne v ostatních). To znamená, že je schopen si i heslo přečíst! I pokud bychom mu get přístup nedali, může se k němu dostat, pokud má právo spustit Pod (namapuje si heslo dovnitř a vytiskne do konzole). Obecně pokud potřebujeme heslo v kódu, tak logicky kdo má přístup ke kódu, má i přístup k secret. Výjimkou jsou situace s použitím confidential computingu v Azure (podepsaný kód s dešifrováním SGX instrukcemi až v procesoru, takže i obsah paměti je šifrovaný) nebo uložení klíče do Azure Key Vault Premium (HSM), kdy ten pro vás zajistí šifrovací operace (například podpis), aniž by klíč opustil tento hardware. 

Přesto dává smysl Secret oddělit tak, že pouze oprávněná osoba je může generovat (a zabránit tak například použití slabých hesel), přidělovat do jednotlivých namespace (každý vidí jen to co potřebuje pro svou práci, ale ne víc) a můžete i použít RBAC pro přístup jen ke konkrétním Secret. Můžete také interaktivní přístup vývojáře oddělit (či zcela znemožnit) od privilegovanějšího nasazování. Tak například vývojář může mít do produkčního prostředí přístup pouze na úrovni čtení logů (například z Azure Monitor) a samotné nasazování je plně automatizované CI/CD pipeline v Azure DevOps, které použije různé účty service principal pro různé aplikace a namespaces. Nemáte tedy v CI/CD nástroji jeden admin účet na celý cluster, ale přístupy zvlášť (s nastaveným RBAC) pro jednotlivé namespaces (aplikace), které pak můžete často rotovat. Azure DevOps RBAC zase umožní těm co nasazují využít hotového spojení do AKS, aniž by se dostali ke konkrétním credentials do clusteru (což zabrání potažmo vidět Secret). Samotné tajnosti (a vytváření Secrets v Kubernetes) pak můžete řešit prostředky Azure DevOps, který na to má funkce (řízení přístupu k tajnostem v Azure DevOps, ze kterých vznine Secret v Kubernetes) nebo je řešit mimo pipeline účtem pro bezpečáka nebo přes Azure Key Vault.

Pokud byste potřebovali jít v oddělenosti Secrets dál a za hranice jedné platformy (například sjednotit práci s nimi pro kontejnery, PaaS, IaaS, Android, ...), doporučuji použít Azure Key Vault. Tam je zcela oddělená správa už na úrovni Azure a Premium verze dokonce ukládá tajnosti do hardwarového systému (HSM). K trezoru se dá přistoupit přímo z aplikace, ale velmi zajímavá je možnost využití Managed Service Identity funkce Azure ve spolupráci s AAD Pod identity a Key Vault FlexVolume. Ale o tom někdy příště, dnes jsem se chtěl zaměřit jen na RBAC v rámci clusteru a napojení do AAD.

Azure Kubernetes Service nabízí myslím velmi dobrý RBAC pro autorizaci vašich operátorů a pro autentizaci elegantně využívá Azure Active Directory. Systém, na kterém stojí váš přístup do Azure portálu, Office365, Dynamics365 a dalších i vlastních systémů. Systém, který je synchronizovaný s vaším klasickým světem Active Directory. Systém, který jde v bezpečnosti mnohem dál, než jen jednoduché ověření díky podpoře multi-factor autentizace, identity protection, podmíněné přístupy včetně integrace do Intune (tedy v jakém stavu je notebook operátora).

Vyzkoušejte si to.



