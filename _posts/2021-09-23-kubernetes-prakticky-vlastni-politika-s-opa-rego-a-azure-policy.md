---
layout: post
published: true
title: "Kubernetes prakticky: vytváření vlastních politik v rego jazyce s OPA a promítnutím do Azure Policy"
tags:
- Governance
- Security
- Kubernetes
---
Minule jsme si prošli Azure Policy pro kontejnery a ukázali si, jak lze pěkně z jednoho místa řešit governance pro Azure Kubernetes Service i pro libovolný Kubernetes běžící kdekoli připojený do Azure prostředí přes Azure Arc. Využili jsme databáze hotových politik a ukázali si, že pod kapotou jsou pravidla napsaná v jazyce Rego, vynucení politik řeší Open policy Agent nativně spravovaný v Kubernetu projektem Gatekeeper a to vše řízeno a reportováno centrálně v cloudu s Azure Policy. Co když ale potřebujete něco speciálního? Pojďme si dnes napsat a aplikovat vlastní politiku.

# OPA a jazyk Rego
Open Policy Agent je projekt, který je obecným řešením pro validaci (a v budoucnu i úpravu - "mutaci") nějaké datové struktury. OPA dokážete předložit JSON, pravidla napsaná v jazyce Rego a OPA řekne, jestli vyhovuje či ne. Typické použití je právě implementace politik v Kubernetes přes Admission Webhook, ale popsány jsou další příklady nasazení jako je validace Terraform plánu před jeho nasazením, kontrola REST volání nebo konfiguračních parametrů Envoy proxy. Principiálně ale lze kontrolovat jakoukoli datovou strukturu - nativní cloudovou šablonu, vaše vlastní konfigurační JSON soubory třeba pro aplikaci, konfigurační soubory síťových prvků (pokud jsou v deklarativním formátu) a tak podobně.

Abychom dokázali v OPA něco dělat, bude potřeba alespoň trošku pochopit jazyk Rego, ve kterém se to píše. Osobně jsem s ním strávil několik hodin a základy jsem nějak pobral, ale rozhodně stát se skutečně znalým by vyžadovalo o dost větší časovou investici. Osvědčilo se mi pohrát si s jazykem na stránkách [https://play.openpolicyagent.org/](https://play.openpolicyagent.org/). Za nejzásadnější pro prozření se u mě ukázalo uvědomění si, že jazyk je primárně o práci s množinami. Je to deklarativní model, ne imperativní programovací jazyk. 

Po dvou hodinách experimentování jsem došel k tomuto základnímu příkladu:

```
package play

violation[{"msg": msg, "details": {}}] {
    not input.message
	msg := "Message must be configured"
}

violation[{"msg": msg, "details": {}}] {
    input.message != "world"
	msg := "Message must be world"
}

violation[{"msg": msg, "details": {}}] {
    not input.items
	msg := "Items list must be included"
}

violation[{"msg": msg, "details": {}}] {
    input.items[_].name == ""
	msg := "Empty item name not allowed"
}

violation[{"msg": msg, "details": {}}] {
    input.items[_].name == "NA"
	msg := "Item must not be NA"
}

violation[{"msg": msg, "details": {}}] {
    not bookExists
	msg := "Book must be included in items"
}

bookExists(){
	input.items[_].name == "book"
}

violation[{"msg": msg, "details": {}}] {
	count(input.items) != count(itemsWithStock)
	msg := "Stock must be included with all items"
}

itemsWithStock[a] = array {
	  array = input.items[a]
  	  array.stock != ""
}
```

A vstupní JSON, který to kontroluje jsem průběžně měnil a zkoumal co to dělá, ale vypadá do začátku nějak takhle:

```json
{
    "message": "world",
    "items": [
        {
            "name": "paper",
            "stock": 5
        },
        {
            "name": "book",
            "stock": 5
        },
        {
            "name": "NA"
        }
    ]
}
```

Pojďme rozebrat jednotlivé sekce. Každá violation (to není klíčové slovo nebo příkaz, jmenovat se to může jakkoli) je soupis pravidel, tedy (kromě nějakých pomocných operací) soupis jednoho a více řádků, které vrací true nebo false. Jakmile jeden z nich vrátí true, tak se pravidlo chytne a vypíše hlášku (v mém případě msg) a později v implementaci třeba v Kubernetes může zastavit deployment zdroje.

Začneme pěkně popořadě.

```
violation[{"msg": msg, "details": {}}] {
    not input.message
	msg := "Message must be configured"
}
```

Tohle jednoduché pravidlo zjišťuje existenci klíče "message" v JSONu. input.message vrací true pokud tam je, takže mě zajímá opak, přidám slovo not. 

```
violation[{"msg": msg, "details": {}}] {
    input.message != "world"
	msg := "Message must be world"
}
```

Tato validace ověřuje, že message obsahuje slovo world. Pokud tam bude cokoli jiného, hodí hlášku. Představte si například, že je to nějaké políčko u resource říkající úroveň zabezpečení a nabývá hodnot None, Basic, Advanced a vaše politika chce zakázat cokoli, co není Advanced.

```
violation[{"msg": msg, "details": {}}] {
    not input.items
	msg := "Items list must be included"
}
```

Tohle už umíme - ujišťuji se, že existuje klíč items.

```
violation[{"msg": msg, "details": {}}] {
    input.items[_].name == ""
	msg := "Empty item name not allowed"
}
```

Items je pole objektů. Tohle pravidlo říká, že v tomto poli objektů pokud se vyskytuje některý s klíčem name, tento klíč nesmí mít prázdnou hodnotu. Ale pozor - tohle netvrdí, že každý objekt musí mít klíč name. Není to cyklus, který by v takovém případě havaroval, protože saháme na klíč, který tam není. Spíše jsme řekli - z množiny všech items objektů mi vyber hodnoty všech name klíčů, které se v ní vyskytují. Pokud se kterákoli z nich rovná prázdné hodnotě, vrať true (tedy error zprávu). Pro index jsem použil podtržítko, protože mě nezajímá, který ten objekt nevyhovuje mému zadání. V pokročilejších scénářích ale můžu chtít vrátit konkrétní index a pak místo podtržítka použijete proměnnou a v té se pak bude index nacházet.

```
violation[{"msg": msg, "details": {}}] {
    input.items[_].name == "NA"
	msg := "Item must not be NA"
}
```

Variací na totéž je pravidlo, které se ozve, pokud je jakýkoli výskyt atributu name v poli objektů items roven NA. Chtěl jsem si tím uvědomit, jak musím později udělat opak.

```
violation[{"msg": msg, "details": {}}] {
    not bookExists
	msg := "Book must be included in items"
}

bookExists(){
	input.items[_].name == "book"
}
```

Tímto pravidlem říkám, že v seznamu items musí být alespoň jeden s názvem book. První intuitivní pokus byl dát rovnou do pravidla statement input.items[_].name != "book" v domnění, že je to opak předchozího příkladu, ale to dělá něco úplně jiného. Takovým zápisem říkám, že vracím true (vyhodím hlášku), jakmile existuje byť jen jeden item, který není book. Ve skutečnosti tedy potřebuji ==, které reaguje na alespoň jeden výskyt book a výsledek negovat. To nelze udělat přímo ve statementu a musí se použít funkce. Mám tedy funkci, která vrací true, pokud je v items alespoň jedna kniha a výstup této funkce v pravidlu převrátím, takže pokud tam kniha je, výsledkem je false, tedy nejde o violation - je to ok, pustíme to, žádná hláška.

```
violation[{"msg": msg, "details": {}}] {
	count(input.items) != count(itemsWithStock)
	msg := "Stock must be included with all items"
}

itemsWithStock[a] = array {
	  array = input.items[a]
  	  array.stock != ""
}
```

Poslední příklad chce ověřit, že ve všech items se vyskytuje klíč stock. Ověřovat existenci stock jsem se samozřejmě nejdřív pokusil jednoduše zápisem not input.items[_].stock, ale to zas dělá něco jiného. Tenhle zápis zjistí, že existuje alespoň jedna item s klíčem stock (vrátí true) a já ji převrátím přes not - takže stačí aby jen jediný item měl atribut stock a pravidlo by vyhovovalo a to není co potřebuji. Řešení je vytvořit funkci, která nejprve vezme všechny items do množiny s názvem array (v ten okamžik je obsah identický) a následně na ní zavolá array.stock != "", tedy vznikne podmnožina items, u kterých platí, že stock je definován. V pravidle pak kontroluji velikost obou množin. Pokud items je jiný počet, než takto odfiltrovaných items, tak existují položky bez definovaného stock.

Pro dobrou znalost Rego bych musel ještě o dost dál, ale prozatím to takhle stačí. Základní myšlenka je, že jde o jazyk pro práci s datovou strukturou a funguje na principu množin nebo chcete-li query. To je pro účely OPA myslím velmi dobrý přístup - ubrání vás to od runtime chyb, které by se daly čekat u imperativního přístupu viz příklad projíždění pole ve smyčce s očekáváním, že je tam atribut name, ale on tam jednoho dne být nemusí a pokud to není ošetřeno, spadne to. 

# Zhmotnění pravidla do šablony a její využití v Azure Policy
Databáze pravidel v rámci Azure Policy pokrývá myslím naprostou většinu běžných scénářů, nicméně napadl mě jeden, který tam není. Představme si, že máme cluster s několik node pooly a máme potřebu, aby určitý namespace vždy dával Pody na konkrétní sadu nodů. Proč?
- Potřebuji hodně striktní pravidla pro odchozí provoz do Internetu a věci, které se tam konzumují mají proměnlivé IP adresy, potřeboval bych FQDN pravidla. To vyloučí jednoduchou Network Policy a směřuje k service mesh, ale ten třeba nechci použít (složitost, latence, overhead). Mohu ale udělat speciální nody (například v samostatném subnetu) a umístit workload na ně, takže na firewallu budu vědět odkud to přišlo a podle toho nastavím politiky.
- Potřebuji pro nějaký workload větší izolaci - nestačí mi izolace na úrovni kernelu, potřebuji to dát na skutečně samostatné VM v cloudu. Například jsem se už dvakrát potkal s tím, že aplikace byla provozována pro zákazníka (SaaS) a ten měl mít možnost zasáhnout do zpracování dat přidáním vlastní funkce ve formě kontejneru. Vy provozujete SaaS a zákazník vám v ní pustí svůj kontejner, to je určitě bezpečnostní hrozba. Jedním ze způsobů snížení rizika může být oddělení takového kontejneru do samostatného nodu (izolace na úrovni hypervisoru, ne jen kernelu), který je síťově izolován od zbytku vaší infrastruktury.
- Potřebuji v clusteru drahé nody s GPU na výpočty nebo AI a k tomu obyčejné nody na aplikace a chci garantovat, že nějaký vývojář nebude omylem vyžírat pro obyčejnou aplikaci kapacitu drahého GPU nodu.

Existuje funkce PodNodeSelector, ale ta je stále v alpha stavu a to už od v1.5, takže pro produkční prostředí nebo managed clustery typicky není dostupná nebo vhodná. Zkusme jiné řešení.

Určitě vás (velmi správně) napadne, že na tohle jsou přece taint, tolerace a nodeAffinity. Přesně tak! Jenže tohle vyžaduje "dobrou víru" - jsou to způsoby jak nastavit, aby to dělalo co potřebujete, ne, aby to zabránilo někomu dělat to, co nechcete. Pokud v rámci clusteru potřebujete pokrýt riziko, že někdo omylem nebo schválně pravidla poruší, bude vhodné tohle doplnit politikou. Vytvořme tedy politiku, která bude kontrolovat, že objekt Pod má nastavenou nodeAffinity a že v seznamu match pravidel je přesně to co chceme. To mi pak umožní tohle nasadit na konkrétní namespace a mám jistotu, že nebudou moci pustit Pod na jiných nodech, než které chci já - i když si nastaví affinitu jinak, zapnou tolerace apod. 

V Rego něco takového vypadá takhle:

```
package k8snodeaffinity

# Check nodeAffinity rule exist
violation[{"msg": msg, "details": {}}] {
    not input.review.object.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0]
    msg := "Pods must be assigned to specific nodepool using spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms.matchExpressions containing  {\"key\": \"type\", \"operator\": \"In\", \"values\": [\"protected\"]}; found no matchExpressions"
}

# Check nodeAffinity rule contains required match expression
violation[{"msg": msg, "details": {}}] {
    nodeMatch := input.review.object.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[i].matchExpressions[i]
    not nodeMatch == {"key": "type", "operator": "In", "values": ["protected"]}
    msg := sprintf("Pods must be assigned to specific nodepool using spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms.matchExpressions containing  {\"key\": \"type\", \"operator\": \"In\", \"values\": [\"protected\"]}; found `%v`", [nodeMatch])
}
```

Label nodu tam mám natvrdo jako type:protected. Řekněme, že type natvrdo nechám, ale hodnotu bych rád univerzální. Vytvořím constraint template a použiji proměnou - při aplikaci šablony se zeptám na pole možných hodnot pro node label type.

```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8snodeaffinity
spec:
  crd:
    spec:
      names:
        kind: K8sNodeAffinity
      validation:
        openAPIV3Schema:
          properties:
            nodeLabels:
              type: array
              items: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8snodeaffinity

        # Check nodeAffinity rule exist
        violation[{"msg": msg, "details": {}}] {
          not input.review.object.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0]
          msg := "Pods must be assigned to specific nodepool using spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms.matchExpressions containing  {\"key\": \"type\", \"operator\": \"In\", \"values\": [\"protected\"]}; found no matchExpressions"
        }

        # Check nodeAffinity rule contains required match expression
        violation[{"msg": msg, "details": {}}] {
          nodeMatch := input.review.object.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[i].matchExpressions[i]
          not nodeMatch == {"key": "type", "operator": "In", "values": input.parameters.nodeLabels}
          msg := sprintf("Pods must be assigned to specific nodepool using spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms.matchExpressions containing  {\"key\": \"type\", \"operator\": \"In\", \"values\": [\"protected\"]}; found `%v`", [nodeMatch])
        }
```

Tuto šablonu teď buď uložím někam na Internet (to je můj případ - je na mém GitHubu) nebo ji překóduji do base64 a použiji v těle definice Azure Policy. To naštěstí nemusím vymýšlet - vzal jem Visual Studio Code, plugin pro Azure Policy a nechal si to vygenerovat.


```json
{
  "properties": {
    "policyType": "Custom",
    "mode": "Microsoft.Kubernetes.Data",
    "displayName": "Require Pods to run on specified Nodes",
    "description": "This policy checks for nodeAffinity rules to specify required labels nodes must have configured. This is typically used to make sure namespace Pods are always allocated to specific NodePool.",
    "policyRule": {
      "if": {
        "field": "type",
        "in": [
          "Microsoft.ContainerService/managedClusters"
        ]
      },
      "then": {
        "effect": "[parameters('effect')]",
        "details": {
          "templateInfo": {
            "sourceType": "PublicURL",
            "url": "https://raw.githubusercontent.com/tkubica12/aks-demo/master/customPolicy/nodeAffinityConstraintTemplate.yaml"
          },
          "apiGroups": [
            "*"
          ],
          "kinds": [
            "Pod"
          ],
          "namespaces": "[parameters('namespaces')]",
          "excludedNamespaces": "[parameters('excludedNamespaces')]",
          "labelSelector": "[parameters('labelSelector')]",
          "values": {
            "nodeLabels": "[parameters('nodeLabels')]"
          }
        }
      }
    },
    "parameters": {
      "effect": {
        "type": "String",
        "metadata": {
          "displayName": "Effect",
          "description": "'audit' allows a non-compliant resource to be created or updated, but flags it as non-compliant. 'deny' blocks the non-compliant resource creation or update. 'disabled' turns off the policy."
        },
        "allowedValues": [
          "audit",
          "deny",
          "disabled"
        ],
        "defaultValue": "audit"
      },
      "excludedNamespaces": {
        "type": "Array",
        "metadata": {
          "displayName": "Namespace exclusions",
          "description": "List of Kubernetes namespaces to exclude from policy evaluation."
        },
        "defaultValue": [
          "kube-system",
          "gatekeeper-system",
          "azure-arc"
        ]
      },
      "namespaces": {
        "type": "Array",
        "metadata": {
          "displayName": "Namespace inclusions",
          "description": "List of Kubernetes namespaces to only include in policy evaluation. An empty list means the policy is applied to all resources in all namespaces."
        },
        "defaultValue": []
      },
      "labelSelector": {
        "type": "Object",
        "metadata": {
          "displayName": "Kubernetes label selector",
          "description": "Label query to select Kubernetes resources for policy evaluation. An empty label selector matches all Kubernetes resources."
        },
        "defaultValue": {},
        "schema": {
          "description": "A label selector is a label query over a set of resources. The result of matchLabels and matchExpressions are ANDed. An empty label selector matches all resources.",
          "type": "object",
          "properties": {
            "matchLabels": {
              "description": "matchLabels is a map of {key,value} pairs.",
              "type": "object",
              "additionalProperties": {
                "type": "string"
              },
              "minProperties": 1
            },
            "matchExpressions": {
              "description": "matchExpressions is a list of values, a key, and an operator.",
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "key": {
                    "description": "key is the label key that the selector applies to.",
                    "type": "string"
                  },
                  "operator": {
                    "description": "operator represents a key's relationship to a set of values.",
                    "type": "string",
                    "enum": [
                      "In",
                      "NotIn",
                      "Exists",
                      "DoesNotExist"
                    ]
                  },
                  "values": {
                    "description": "values is an array of string values. If the operator is In or NotIn, the values array must be non-empty. If the operator is Exists or DoesNotExist, the values array must be empty.",
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  }
                },
                "required": [
                  "key",
                  "operator"
                ],
                "additionalProperties": false
              },
              "minItems": 1
            }
          },
          "additionalProperties": false
        }
      },
      "nodeLabels": {
        "type": "Array",
        "metadata": {
          "displayName": "Node labels array",
          "description": "Array of labels of node that Pods must be assigned to"
        }
      }
    }
  }
}
```

Policy mi umožní při assignmentu zvolit na který namespace a případně pod labely se politika aplikuje a současně se tam objevil i vstupní parametr z mé šablony (pole hodnot pro label type na nodech).

Definici jsem přidal do Azure Policy.

[![](/images/2021/2021-09-08-10-11-10.png){:class="img-fluid"}](/images/2021/2021-09-08-10-11-10.png)

Politiku přiřadím na scope dle potřeby - například konkrétní cluster ať už AKS nebo Arc nebo třeba univerzálně pro všechny clustery v organizaci.

[![](/images/2021/2021-09-08-10-16-13.png){:class="img-fluid"}](/images/2021/2021-09-08-10-16-13.png)

[![](/images/2021/2021-09-08-10-17-23.png){:class="img-fluid"}](/images/2021/2021-09-08-10-17-23.png)

Po několika minutách si mohu ověřit, že Azure Policy v clusteru založila příslušnou šablonu, CRD i jeho výskyt.

```
$ kubectl get constrainttemplate
NAME                                     AGE
k8sazureallowedcapabilities              28h
k8sazureallowedusersgroups               28h
k8sazureblockautomounttoken              28h
k8sazureblockdefault                     28h
k8sazureblockhostnamespace               28h
k8sazurecontainerallowedimages           28h
k8sazurecontainerallowedports            28h
k8sazurecontainerlimits                  28h
k8sazurecontainernoprivilege             28h
k8sazurecontainernoprivilegeescalation   28h
k8sazuredisallowedcapabilities           28h
k8sazureenforceapparmor                  28h
k8sazurehostfilesystem                   28h
k8sazurehostnetworkingports              28h
k8sazureingresshttpsonly                 28h
k8sazurepodenforcelabels                 26h
k8sazurereadonlyrootfilesystem           28h
k8sazureserviceallowedports              28h
k8snodeaffinity                          25h

$ kubectl describe constrainttemplate k8snodeaffinity
Name:         k8snodeaffinity
Namespace:
Labels:       managed-by=azure-policy-addon
Annotations:  azure-policy-definition-id-1:
                /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/providers/microsoft.authorization/policydefinitions/b0d0c4b8-ef88-4d83-817e-786327bbb6...
              constraint-template: https://raw.githubusercontent.com/tkubica12/aks-demo/master/customPolicy/nodeAffinityConstraintTemplate.yaml
              constraint-template-installed-by: azure-policy-addon
API Version:  templates.gatekeeper.sh/v1beta1
Kind:         ConstraintTemplate
Metadata:
  Creation Timestamp:  2021-09-07T07:17:24Z
  Generation:          1
  Managed Fields:
    API Version:  templates.gatekeeper.sh/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:metadata:
        f:annotations:
          .:
          f:azure-policy-definition-id-1:
          f:constraint-template:
          f:constraint-template-installed-by:
        f:labels:
          .:
          f:managed-by:
      f:spec:
        .:
        f:crd:
          .:
          f:spec:
            .:
            f:names:
              .:
              f:kind:
            f:validation:
              .:
              f:openAPIV3Schema:
                .:
                f:properties:
                  .:
                  f:nodeLabels:
                    .:
                    f:items:
                    f:type:
        f:targets:
    Manager:      azurepolicyaddon
    Operation:    Update
    Time:         2021-09-07T07:17:24Z
    API Version:  templates.gatekeeper.sh/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:status:
        .:
        f:byPod:
        f:created:
    Manager:         gatekeeper
    Operation:       Update
    Time:            2021-09-07T07:17:25Z
  Resource Version:  126018
  UID:               05f84ed7-9d50-4804-9817-fcc3be70a792
Spec:
  Crd:
    Spec:
      Names:
        Kind:  K8sNodeAffinity
      Validation:
        openAPIV3Schema:
          Properties:
            Node Labels:
              Items:  string
              Type:   array
  Targets:
    Rego:  package k8snodeaffinity

# Check nodeAffinity rule exist
violation[{"msg": msg, "details": {}}] {
  not input.review.object.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0]
  msg := "Pods must be assigned to specific nodepool using spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms.matchExpressions containing  {\"key\": \"type\", \"operator\": \"In\", \"values\": [\"protected\"]}; found no matchExpressions"
}

# Check nodeAffinity rule contains required match expression
violation[{"msg": msg, "details": {}}] {
  nodeMatch := input.review.object.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[i].matchExpressions[i]
  not nodeMatch == {"key": "type", "operator": "In", "values": input.parameters.nodeLabels}
  msg := sprintf("Pods must be assigned to specific nodepool using spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms.matchExpressions containing  {\"key\": \"type\", \"operator\": \"In\", \"values\": [\"protected\"]}; found `%v`", [nodeMatch])
}

    Target:  admission.k8s.gatekeeper.sh
Status:
  By Pod:
    Id:                   gatekeeper-audit-5456bb46b6-zzbmq
    Observed Generation:  1
    Operations:
      audit
      status
    Template UID:         05f84ed7-9d50-4804-9817-fcc3be70a792
    Id:                   gatekeeper-controller-58d7f44b9-2g296
    Observed Generation:  1
    Operations:
      webhook
    Template UID:         05f84ed7-9d50-4804-9817-fcc3be70a792
    Id:                   gatekeeper-controller-58d7f44b9-kvgfl
    Observed Generation:  1
    Operations:
      webhook
    Template UID:  05f84ed7-9d50-4804-9817-fcc3be70a792
  Created:         true
Events:            <none>

$ kubectl get crd
NAME                                                               CREATED AT
configs.config.gatekeeper.sh                                       2021-09-07T03:44:00Z
constraintpodstatuses.status.gatekeeper.sh                         2021-09-07T03:44:00Z
constrainttemplatepodstatuses.status.gatekeeper.sh                 2021-09-07T03:44:00Z
constrainttemplates.templates.gatekeeper.sh                        2021-09-07T03:44:00Z
k8sazureallowedcapabilities.constraints.gatekeeper.sh              2021-09-07T03:47:30Z
k8sazureallowedusersgroups.constraints.gatekeeper.sh               2021-09-07T03:47:24Z
k8sazureblockautomounttoken.constraints.gatekeeper.sh              2021-09-07T03:47:39Z
k8sazureblockdefault.constraints.gatekeeper.sh                     2021-09-07T03:47:25Z
k8sazureblockhostnamespace.constraints.gatekeeper.sh               2021-09-07T03:47:28Z
k8sazurecontainerallowedimages.constraints.gatekeeper.sh           2021-09-07T03:47:24Z
k8sazurecontainerallowedports.constraints.gatekeeper.sh            2021-09-07T03:47:37Z
k8sazurecontainerlimits.constraints.gatekeeper.sh                  2021-09-07T03:47:41Z
k8sazurecontainernoprivilege.constraints.gatekeeper.sh             2021-09-07T03:47:35Z
k8sazurecontainernoprivilegeescalation.constraints.gatekeeper.sh   2021-09-07T03:47:43Z
k8sazuredisallowedcapabilities.constraints.gatekeeper.sh           2021-09-07T03:47:34Z
k8sazureenforceapparmor.constraints.gatekeeper.sh                  2021-09-07T03:47:46Z
k8sazurehostfilesystem.constraints.gatekeeper.sh                   2021-09-07T03:47:25Z
k8sazurehostnetworkingports.constraints.gatekeeper.sh              2021-09-07T03:47:32Z
k8sazureingresshttpsonly.constraints.gatekeeper.sh                 2021-09-07T03:47:48Z
k8sazurepodenforcelabels.constraints.gatekeeper.sh                 2021-09-07T06:17:25Z
k8sazurereadonlyrootfilesystem.constraints.gatekeeper.sh           2021-09-07T03:47:37Z
k8sazureserviceallowedports.constraints.gatekeeper.sh              2021-09-07T03:47:28Z
k8snodeaffinity.constraints.gatekeeper.sh                          2021-09-08T03:45:38Z

$ kubectl get k8snodeaffinity
NAME                                               AGE
azurepolicy-k8snodeaffinity-4fd8b43de76ea5c3cb7e   4h31m

$ kubectl describe k8snodeaffinity azurepolicy-k8snodeaffinity-4fd8b43de76ea5c3cb7e 
Name:         azurepolicy-k8snodeaffinity-4fd8b43de76ea5c3cb7e
Namespace:
Labels:       managed-by=azure-policy-addon
Annotations:  azure-policy-assignment-id:
                /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/resourceGroups/akspolicy/providers/Microsoft.Authorization/policyAssignments/be7098902...
              azure-policy-definition-id:
                /subscriptions/a0f4a733-4fce-4d49-b8a8-d30541fc1b45/providers/Microsoft.Authorization/policyDefinitions/b0d0c4b8-ef88-4d83-817e-786327bbb6...
              azure-policy-definition-reference-id:
              azure-policy-setdefinition-id:
              constraint-installed-by: azure-policy-addon
API Version:  constraints.gatekeeper.sh/v1beta1
Kind:         K8sNodeAffinity
Metadata:
  Creation Timestamp:  2021-09-08T03:48:05Z
  Generation:          2
  Managed Fields:
    API Version:  constraints.gatekeeper.sh/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:metadata:
        f:annotations:
          .:
          f:azure-policy-assignment-id:
          f:azure-policy-definition-id:
          f:azure-policy-definition-reference-id:
          f:azure-policy-setdefinition-id:
          f:constraint-installed-by:
        f:labels:
          .:
          f:managed-by:
      f:spec:
        .:
        f:enforcementAction:
        f:match:
          .:
          f:excludedNamespaces:
          f:kinds:
        f:parameters:
          .:
          f:nodeLabels:
    Manager:      azurepolicyaddon
    Operation:    Update
    Time:         2021-09-08T03:48:05Z
    API Version:  constraints.gatekeeper.sh/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:status:
        .:
        f:auditTimestamp:
        f:byPod:
        f:totalViolations:
    Manager:         gatekeeper
    Operation:       Update
    Time:            2021-09-08T06:56:01Z
  Resource Version:  149265
  UID:               5aa0a522-41b7-482a-9a0f-2c065080f6cc
Spec:
  Enforcement Action:  deny
  Match:
    Excluded Namespaces:
      kube-system
      gatekeeper-system
      azure-arc
    Kinds:
      API Groups:
        *
      Kinds:
        Pod
  Parameters:
    Node Labels:
      protected
Status:
  Audit Timestamp:  2021-09-08T08:15:58Z
  By Pod:
    Constraint UID:       5aa0a522-41b7-482a-9a0f-2c065080f6cc
    Enforced:             true
    Id:                   gatekeeper-audit-5456bb46b6-zzbmq
    Observed Generation:  2
    Operations:
      audit
      status
    Constraint UID:       5aa0a522-41b7-482a-9a0f-2c065080f6cc
    Enforced:             true
    Id:                   gatekeeper-controller-58d7f44b9-2g296
    Observed Generation:  2
    Operations:
      webhook
    Constraint UID:       5aa0a522-41b7-482a-9a0f-2c065080f6cc
    Enforced:             true
    Id:                   gatekeeper-controller-58d7f44b9-kvgfl
    Observed Generation:  2
    Operations:
      webhook
  Total Violations:  0
Events:              <none>
```

Pošlu do clusteru tento Pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  labels:
    mylabel: myapp
spec:
  containers:
  - name: myapp
    image: nginx
```

Dostávám chybu - dle očekávání.

```
Error from server ([azurepolicy-k8snodeaffinity-4fd8b43de76ea5c3cb7e] Pods must be assigned to specific nodepool using spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms.matchExpressions containing  {"key": "type", "operator": "In", "values": ["protected"]}; found no matchExpressions): error when creating "pod.yaml": admission webhook "validation.gatekeeper.sh" denied the request: [azurepolicy-k8snodeaffinity-4fd8b43de76ea5c3cb7e] Pods must be assigned to specific nodepool using spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms.matchExpressions containing  {"key": "type", "operator": "In", "values": ["protected"]}; found no matchExpressions
```

Totéž u tohoto Podu.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  labels:
    mylabel: myapp
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: type
                operator: In
                values: ["notsecured"]
  containers:
  - name: myapp
    image: nginx
```

Ale tento projde naší politikou bez problému.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  labels:
    mylabel: myapp
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: type
                operator: In
                values: ["protected"]
  containers:
  - name: myapp
    image: nginx
```

Všechno tedy funguje jak má. Pokud stejně jako já vystačíte se základní databází pravidel pro Kubernetes v Azure Policy, bude všechno jednoduché a můžete tak krásně řídit všechny svoje clustery jak v cloudu, tak v on-premises nebo na IoT zařízeních díky Azure Arc. Pokud potřebujete něco speciálního, také to není problém - budete se muset trochu ponořit do jazyka Rego, ale jak jsme dnes vyzkoušeli nic vám v tom nebrání a i vaše vlastní šablony budou žít v rámci Azure Policy. Jinak řečeno vaše zvláštní požadavky se zhmotní v definici Azure Policy, s kterou pak může pracovat i váš kolega, který o Rego nikdy neslyšel a slyšet nechce.