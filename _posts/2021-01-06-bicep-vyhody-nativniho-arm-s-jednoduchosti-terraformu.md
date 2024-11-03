---
layout: post
title: Bicep - výhody nativní ARM automatizace s jednoduchostí ala Terraform
tags:
- Automatizace
---
Na tomto blogu jsem před pár měsíci popisoval obvyklé dilema všech nadšenců pro automatizaci v Azure. Mám použít nativní ARM šablony nebo Terraform, nástroj třetí strany? Oba světy mám moc rád, s oběma dosáhnete téhož a oba mají zásadní výhody oproti druhému. Teď ale přišla změna - open source projekt [Bicep](https://github.com/Azure/bicep) a ten si zachovává zásadní výhody nativního ARM, ale přibližuje jej stylu a pohodlnosti Terraformu. Zatím je v preview, ale vypadá opravdu dobře. Jak to mění moje [minulé srovnání](https://www.tomaskubica.cz/post/2020/arm-vs-terraform/)? Jak Bicep funguje a co dalšího má v plánu?

# Malé opáčko ARM vs Terraform
Pro detaily se prosím vraťte k mému [předchozímu článku](https://www.tomaskubica.cz/post/2020/arm-vs-terraform/), ale pojďme si základní vlastnosti shrnout.

**Proč ARM?**
- Je to nativní řešení, takže má vždycky ty nejnovější Azure funkce, dokonce i ty v preview či private preview. Jasně, věci v preview se nemají používat v produkci, ale v testu proč ne a s GA je chci hnedle posunout i do produkce. Nechci test stavět ručně jen proto, abych si vyzkoušel nové funkce a nechci čekat třeba i týdny či dokonce měsíce, než se nová funkce/atribut objeví v Terraformu.
- Protože je nativní, jeho bezpečnost a řídící systém je součást Azure. Nepotřebuji deployment server, nepotřebuji state file (jehož prozrazení má za následek odhalení všech hesel, pokud jsou použity) apod.
- Azure umí provést export zdrojů do ARM šablony a to čím dál tím lépe. Na konci většiny GUI průvodců je možnost stáhnout si výsledek jako šablonu, ale lze i nacvakat zdroje z GUI nebo CLI a jejich stav pak vyexportovat do šablony. To je hodně praktické zejména pokud ještě nemáte zažito, že úplně všechno, i to co neznáte, děláte od začátku šablonou (obvyklejší je, že nové věci děláte v GUI či CLI a když už víte co chcete, vytvoříte opakovatelnou šablonu).
- Pokud chcete tvořit nativní objekty v Azure Marketplace (ať už veřejném či interním), potřebujete ARM.

**Proč Terraform?**
- Syntaxe není JSON, který je krutý a neodpouští (jedna čárka navíc nebo chybějící složená závorka a už hledáte), ale příjemný a velmi přehledný jazyk. To umožňuje například krásně vytvářet řetězce bez nepřehledných funkcí typu concat (zkuste složit řetězec z několika elementů z nichž některé jsou statické, některé jsou proměnné a některé reference a vznikne vám dost dlouhý řádek).
- Terraform styl vede na odkazování objektů jeden na druhý, takže vám Terraform téměř vždy vygeneruje správné dependence a nemusíte je ručně řešit - to se opravdu hodí.
- Mám rád práci s moduly pro komplikovanější šablony, kdy chcete opakovaně použitelné komponenty a není nutné to nahrávat někam na storage, odkazovat a složitě troubleshootovat.
- Zvykl jsem si i bez použití modulů rozdělit zdroje do jednotlivých souborů. Často nestojím o modul (a předávání parametrů apod.), chci velkou šablonu, ale když má přes 1000 řádek, nerad v tom hledám. Terraform umožňuje jednoduše uložit šablonu ve více souborech (v jednom mám sítě, v druhém compute, ve třetím monitoring apod.) a při deploymentu je Terraform prostě a jednoduše složí dohromady - žádné starosti s parametry, prostě je to jen rozmontovaný file.
- Terraform má "ovladače" nejen na Azure, ale i AWS, GCP či některé privátní cloudy. Neznamená to, že jeden soubor pošlete do všech cloudů (to ani zdaleka ne - časté nepochopení), ale mám jeden jazyk, jeden systém.

**Pak jsou samozřejmě vlastnosti, které mají společné:**
- Deklarativní desired state model
- Plánování a what-if (řekni mi, co se chystáš změnit)
- Hotové moduly pro začlenění do CI/CD (např. GitHub Actions podporují krásně oboje) i testovací nástroje (byť tady je Terraform o něco dál)

# Projekt Bicep a základní myšlenky
Nejdřív název. Azure Resource Manager, zkratka ARM - anglicky ruka. Symbol přiložení ruky k dílu, symbol namakanosti atd. je biceps ... takže tak.

Co na ARMu bolí nejvíc? Podle mě určitě ten JSON a ne, náhrada za YAML nepomůže. Je to jistě otázka osobního vkusu, ale jestli vás vypeče chybějící složená závorka nebo chybějící mezera je asi vcelku jedno. Koneckonců jsou to jen datové formáty a my do toho potřebujeme dostat nějakou funkčnost. Extrémem by bylo použití standardního programovacího jazyka. To tým Bicep zvažoval (ostatně Brendan Burns, který má kromě role otce Kubernetes na starosti i ARM a další věci v Azure má tohle rád), ale pro neprogramátory by to vytvářelo bariéru. Proto jde Bicep cestou DSL a to je dost podobné Terraformu. Pokud jste přecijen banda vývojářů, která má na starost i celý provoz a bez Javascriptu nebo C# si neuvaříte ani kafe, koukněte na [Pulumi](https://www.pulumi.com/).

Klíčová myšlenka Bicep je ale v tom, že jde o transparentní abstrakci. Z Bicep šablony uděláte ARM šablonu a naopak z ARM šablony můžete vytvořit Bicep! Představte si to jako obousměrný kompilátor. To je zásadní rozhodnutí a má obrovské výhody:
- Bicep není nová generace ARMu. Azure je pořád ARM, takže není potřeba na nic přecházet, nic předělávat. Všechny vlastnosti Azure Resource Manager zůstávají v platnosti včetně mnoha lety prověřené stability, kvality i bezpečnosti. Můžete použít Bicep na jednoduší vytváření šablon, ale před samotným deploymentem se to stejně konvertuje na ARM.
- Bicep umí udělat i opak, tedy z ARM šablony vytvořit Bicep šablonu. Máte tak cestu jak z naklikaného vytvořit opakovatelné.
- Transparentní abstrakce znamená, že se nečeká na podporu něčeho v Bicep. Pokud má ARM nový zdroj nebo atribut v preview, klidně ho můžete v Bicep použít.
- DSL je podobné Terraformu, za mě tedy velmi přehledné a intuitivní včetně vytváření řetězců nebo odkazování jednoho zdroje na druhý (konečně nemusím všechny dependsOn řešit ručně).
- Bicep podporuje moduly, takže můžete projekt rozdělit na menší celky, aniž byste museli soubory nahrávat někam na storage a řešit kde jakou verzi máte a tak podobně.
- Zatím nepodporuje slepení vícero souborů bez modulů, ale podle všeho je to v plánu.
- Co mi připadá jako výborný tah je použití jednoduchých uvozovek pro řetězce (místo dvojitých) s tím, že dvojité uvozovky jsou tak standardní znak. Proč jsem tak nadšený? V šablonách docela často potřebujete JSON (typicky je to nějaký konfigurační objekt) vnořený jako hodnota atributu a to v ARMu znamená escapování uvozovek - Bicep tohle dělá za mě.
- Součástí je velmi dobrý tooling do VScode s kontrolou syntaxe, nápovědou, doplňováním.

Nicméně pozor - Bicep není v konečném režimu, dost možná dozná ještě nějakých důležitých změn, takže pro produkční nasazení zatím nepoužívejte. Nic vám sice nerozbije, ale možná budete muset šablony občas předělat, jak půjde vývoj dopředu, než se dosáhne stabilní verze. Ale je určitě ideální čas se s ním seznámit a poskytnout zpětnou vazbu týmu na GitHubu.

# Pár ukázek
Začněme třeba jednoduchou definicí IP adresy v Bicep.

```
resource vmIp 'Microsoft.Network/publicIPAddresses@2019-11-01' = {
  name: 'prod-vm-ip'
  location: resourceGroup().location
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}
```

Spustíme bicep, který nám vygeneruje ARM šablonu (samozřejmě v budoucích verzích očekávám víc možností, třeba že to rovnou nasadí apod.).

```bash
bicep build main.bicep
```

Výsledkem je tato ARM šablona.

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "functions": [],
  "resources": [
    {
      "type": "Microsoft.Network/publicIPAddresses",
      "apiVersion": "2019-11-01",
      "name": "prod-vm-ip",
      "location": "[resourceGroup().location]",
      "properties": {
        "publicIPAllocationMethod": "Static"
      }
    }
  ]
}
```

Montování řetězců nebo přidávání parametrů je velmi pohodlné.

```
param prefix string = 'prod'

resource vmIp 'Microsoft.Network/publicIPAddresses@2019-11-01' = {
  name: '${prefix}-vm-ip'
  location: resourceGroup().location
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}
```

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "prefix": {
      "type": "string",
      "defaultValue": "prod"
    }
  },
  "functions": [],
  "resources": [
    {
      "type": "Microsoft.Network/publicIPAddresses",
      "apiVersion": "2019-11-01",
      "name": "[format('{0}-vm-ip', parameters('prefix'))]",
      "location": "[resourceGroup().location]",
      "properties": {
        "publicIPAllocationMethod": "Static"
      }
    }
  ]
}
```

Myslím, že určitě přehlednější. 

V Bicep můžete samozřejmě používat stejné funkce jako v ARM, protože jde o transparentní řešení. Pojďme například smontovat řetězec s DNS jménem obsahujícím unikátní generovanou část řetězce.

```
param prefix string = 'prod'

resource vmIp 'Microsoft.Network/publicIPAddresses@2019-11-01' = {
  name: '${prefix}-vm-ip'
  location: resourceGroup().location
  properties: {
    publicIPAllocationMethod: 'Static'
    dnsSettings: {
      domainNameLabel: '${prefix}-ip-${uniqueString(resourceGroup().id)}'
    }
  }
}
```

Výsledkem je tohle:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "prefix": {
      "type": "string",
      "defaultValue": "prod"
    }
  },
  "functions": [],
  "resources": [
    {
      "type": "Microsoft.Network/publicIPAddresses",
      "apiVersion": "2019-11-01",
      "name": "[format('{0}-vm-ip', parameters('prefix'))]",
      "location": "[resourceGroup().location]",
      "properties": {
        "publicIPAllocationMethod": "Static",
        "dnsSettings": {
          "domainNameLabel": "[format('{0}-ip-{1}', parameters('prefix'), uniqueString(resourceGroup().id))]"
        }
      }
    }
  ]
}
```

Reference na atribut objektu je najednou opravdu snadná. Podívejme se třeba jak do výstupu dám IP adresu.

```
param prefix string = 'prod'

resource vmIp 'Microsoft.Network/publicIPAddresses@2019-11-01' = {
  name: '${prefix}-vm-ip'
  location: resourceGroup().location
  properties: {
    publicIPAllocationMethod: 'Static'
    dnsSettings: {
      domainNameLabel: '${prefix}-ip-${uniqueString(resourceGroup().id)}'
    }
  }
}

output ip string = vmIp.properties.ipAddress
```

Což se přeloží jako:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "prefix": {
      "type": "string",
      "defaultValue": "prod"
    }
  },
  "functions": [],
  "resources": [
    {
      "type": "Microsoft.Network/publicIPAddresses",
      "apiVersion": "2019-11-01",
      "name": "[format('{0}-vm-ip', parameters('prefix'))]",
      "location": "[resourceGroup().location]",
      "properties": {
        "publicIPAllocationMethod": "Static",
        "dnsSettings": {
          "domainNameLabel": "[format('{0}-ip-{1}', parameters('prefix'), uniqueString(resourceGroup().id))]"
        }
      }
    }
  ],
  "outputs": {
    "ip": {
      "type": "string",
      "value": "[reference(resourceId('Microsoft.Network/publicIPAddresses', format('{0}-vm-ip', parameters('prefix')))).ipAddress]"
    }
  }
}
```

S vizualizací, syntaxí a doplňováním pomáhá plugin do Visual Studio Code.

![](/images/2020/2021-01-05-10-52-57.png){:class="img-fluid"}

Na závěr si zkusíme tři zdroje - VNET se subnety, síťovou kartu a k ní přidruženou public IP. Mezi těmito zdroji jsou dependence - NIC nelze vytvářet, dokud neexistuje VNET a public adresa. Tím, že mezi objekty se referencujeme jménem Bicep objektu, tak dokáže Bicep dependsOn vygenerovat sám. Kromě přidání dalších zdrojů jsem z location udělal proměnnou.

```
param prefix string = 'prod'

var location = resourceGroup().location

// Network
resource vnet 'Microsoft.Network/virtualnetworks@2015-05-01-preview' = {
  name: 'mynet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes:[
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'subnet1'
        properties: {
          addressPrefix: '10.0.0.0/24'
        }
      }
      {
        name: 'subnet2'
        properties: {
          addressPrefix: '10.0.1.0/24'
        }
      }
    ]
  }
}

// NIC
resource vmNic 'Microsoft.Network/networkInterfaces@2020-06-01' = {
  name: '${prefix}-vm-nic'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: '${vnet.id}/subnets/apps'
          }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: vmIp.id
          }
        }
      }
    ]
  }
}

// Public IP
resource vmIp 'Microsoft.Network/publicIPAddresses@2019-11-01' = {
  name: '${prefix}-vm-ip'
  location: location
  properties: {
    publicIPAllocationMethod: 'Static'
    dnsSettings: {
      domainNameLabel: '${prefix}-ip-${uniqueString(resourceGroup().id)}'
    }
  }
}

output ip string = vmIp.properties.ipAddress
```

Podle mě dobře čitelné a s možností komentářů. Výsledný ARM vypadá takhle:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "prefix": {
      "type": "string",
      "defaultValue": "prod"
    }
  },
  "functions": [],
  "variables": {
    "location": "[resourceGroup().location]"
  },
  "resources": [
    {
      "type": "Microsoft.Network/virtualnetworks",
      "apiVersion": "2015-05-01-preview",
      "name": "mynet",
      "location": "[variables('location')]",
      "properties": {
        "addressSpace": {
          "addressPrefixes": [
            "10.0.0.0/16"
          ]
        },
        "subnets": [
          {
            "name": "subnet1",
            "properties": {
              "addressPrefix": "10.0.0.0/24"
            }
          },
          {
            "name": "subnet2",
            "properties": {
              "addressPrefix": "10.0.1.0/24"
            }
          }
        ]
      }
    },
    {
      "type": "Microsoft.Network/networkInterfaces",
      "apiVersion": "2020-06-01",
      "name": "[format('{0}-vm-nic', parameters('prefix'))]",
      "location": "[variables('location')]",
      "properties": {
        "ipConfigurations": [
          {
            "name": "ipconfig1",
            "properties": {
              "subnet": {
                "id": "[format('{0}/subnets/apps', resourceId('Microsoft.Network/virtualnetworks', 'mynet'))]"
              },
              "privateIPAllocationMethod": "Dynamic",
              "publicIPAddress": {
                "id": "[resourceId('Microsoft.Network/publicIPAddresses', format('{0}-vm-ip', parameters('prefix')))]"
              }
            }
          }
        ]
      },
      "dependsOn": [
        "[resourceId('Microsoft.Network/publicIPAddresses', format('{0}-vm-ip', parameters('prefix')))]",
        "[resourceId('Microsoft.Network/virtualnetworks', 'mynet')]"
      ]
    },
    {
      "type": "Microsoft.Network/publicIPAddresses",
      "apiVersion": "2019-11-01",
      "name": "[format('{0}-vm-ip', parameters('prefix'))]",
      "location": "[variables('location')]",
      "properties": {
        "publicIPAllocationMethod": "Static",
        "dnsSettings": {
          "domainNameLabel": "[format('{0}-ip-{1}', parameters('prefix'), uniqueString(resourceGroup().id))]"
        }
      }
    }
  ],
  "outputs": {
    "ip": {
      "type": "string",
      "value": "[reference(resourceId('Microsoft.Network/publicIPAddresses', format('{0}-vm-ip', parameters('prefix')))).ipAddress]"
    }
  }
}
```

Odstraním teď komentáře a zkusím zjistit komplexitu obou souborů:
- 63 vs. 87 řádků
- 1337 vs. 2627 znaků
- Nemusím sám řešit dependsOn
- Nemusím používat a znát některé funkce jako je concat, resourceId, reference nebo format
- Nemám šílenosti typu uzavření 4 kulatých závorek (podívejte na value outputs u ARM šablony)

Díky jednoduchým závorkám není nutné escapovat vnořený JSON, což se celkem často hodí.

```
var json = '{"mojePoleObjektu":[{"klic1":"hodnota1"},{"klic2":"hodnota2"}]}'
```

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "functions": [],
  "variables": {
    "json": "{\"mojePoleObjektu\":[{\"klic1\":\"hodnota1\"},{\"klic2\":\"hodnota2\"}]}"
  },
  "resources": []
}
```

Jak se pozná transparentnost Bicepu? Jak bicep binárka tak VScode plugin vám řeknou, když něco neodpovídá aktuální specifikaci, tedy že atribut neexistuje nebo api verze je neplatná apod. Nicméně jsou to pouze varování. Pokud jste třeba v private preview, definice není k dispozici nebo tak něco, nic vám nebrání Bicep použít (to je zásadní rozdíl od Terraformu, kde dokud podpora není vytvořena, máte smůlu). Přesuňme se do roku 2022, který třeba přinese nový atribut "nesmysl".

```
resource vnet 'Microsoft.Network/virtualnetworks@2022-05-01-preview' = {
  name: 'mynet'
  location: location
  properties: {
    nesmysl: 'ahoj'
    addressSpace: {
      addressPrefixes:[
        '10.0.0.0/16'
      ]
    }
  }
}
```

Bicep sice varuje, ale ARM, pokud na tom trváte, vytvoří (ten samozřejmě nebude fungovat). Díky tomu vás nic neomezuje, nemusíte čekat, až někdo podporu dodělá.

```json
    {
      "type": "Microsoft.Network/virtualnetworks",
      "apiVersion": "2022-05-01-preview",
      "name": "mynet",
      "location": "[variables('location')]",
      "properties": {
        "nesmysl": "ahoj",
        "addressSpace": {
          "addressPrefixes": [
            "10.0.0.0/16"
          ]
        },
      }
    }
```

Jsou ještě oblasti, kde finální rozhodnutí nepadlo a je to tak skvělá příležitost pro vás zapojit se do diskuse. Pro mě jsou tam určitě dvě dost zajímavá témata:
- Jak řešit víceřádkové hodnoty? Z jednoho pohledu bych rád, abych mohl řetězec napsat přes víc řádků, zejména pokud jde o JSON tak, aby byl dobře čitelný, nicméně při vytvoření ARM budu budu chtít konce řádků a mezery odstranit, aby to byl čistý JSON. Jenže někdy jindy můžu potřebovat, aby ten řetězec naopak přesně dodržel řádky i mezery - například cloud-init pro Linux, který je YAML. Ideálně tedy aby to umělo oboje (formáty mohou být třeba jednoduché uvozovky, trojité uvozovky, závináč před uvozovkou apod.) - zatím není rozhodnuto jak na to, zapojte se do diskuse.
- Jak řešit vícero souborů - to je pro mě dost důležité. Ano, už lze členit šablony do modulů, ale to je hlavně pro jejich samostatnost a musím si předávat parametry apod. Já mám rád, když můžu i jednu nemodularizovanou šablonu rozházet do vícero souborů a i to se v projektu diskutuje.



Sečteno podtrženo - z hlavních nevýhod ARMu Bicep krásně odstraňuje syntaktickou složitost, nekompromisnost JSONu, nutnost pořád řešit dependence nebo složitěji modularizovat přes linkované šablony. Přesto má stále všechny výhody ARMu. Myslím, že je to dost zásadní projekt a očekávám, že během pár měsíců se zastabilizuje. Terraform si určitě ponechává svou unikátnost v podpoře dalších cloudů a velmi propracovaný troubleshooting a testování v rámci CI/CD. Rozhodnutí je na vás, ale pokud je automatizace vaše téma, určitě Bicep vyzkoušejte a podílejte se na jeho vývoji třeba názorem v diskusi na GitHubu.