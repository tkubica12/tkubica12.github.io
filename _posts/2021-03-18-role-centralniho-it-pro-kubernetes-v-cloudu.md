---
layout: post
title: Role centrálního IT pro Kubernetes v cloudu aneb přístup dvou zákazníků vycházejících z přesně opačných předpokladů
tags:
- Kubernetes
---
Chtěl bych si sepsat pár myšlenek kolem situace, kdy centrální IT tým nabízí služby ostatním v organizaci a přemýšlí, jak vyřešit Kubernetes v cloudu. Popíšu dva zákazníky - pana Bílého a pana Černého a v čem vidím problém a kam bych je směřoval. Mám možnost vidět dva zákazníky, kteří jdou po tomtéž, ale každý naprosto jinak. Nicméně - pro účely tohoto textu nutno poznamenat, že jakákoli podobnost je čistě náhodná a pokud se v tom kdokoli poznal, tak se vám to jen zdá (a omlouvám se - rozuzlení je dobré, slibuji)  :)

# Čeho chce pan Bílý i pan Černý dosáhnout
Oba vychází z rozumného předpokladu, že Kubernetes není jednoduchá technologie a chápou limity naivního "DevOps" ve stylu nechme vývojáře dělat všechno, DevOps přece je o tom, že každý všemu rozumí (aby nedošlo k nedorozumění - DevOps je pro mě důležitá věc, ale je to trochu složitější, než říct, že vývojáři už to na vizitce nemají a nasazují teď produkci). Pan Bílý i Černý oba chápou, že to není pro bezpečný a spolehlivý provoz reálné. Jinak řečeno je vhodné promyslet si pravidla hry a základní koncepty v řízení přístupů, bezpečnosti, síťovém zapojení, monitoringu a tak podobně. Možná se liší v míře svobody a kontroly, dramaticky ve způsobu realizace, ale tyto koncepty vnímají oba.

Co je tedy smyslem? Dát týmům Kubernetes tak, aby mohly být okamžitě produktivní, nemusely procházet mnoho slepých uliček (a že jich kolem této technologie bývá) a současně bylo minimalizované bezpečnostní a provozní riziko. Co to může znamenat prakticky?
- Existuje ověřená základní konfigurace clusteru (síťové řešení, vyladění OS parametrů je-li potřeba, break-the-glass klíče pro přístup do nodů apod.).
- Nejsou žádné superadmin účty bez pořádného ověřování, existuje single-sign-on, role, řízení přístupů, bezpečné způsoby přihlašování, správa privilegovaných přístupů.
- Tam, kde je nutné mít cluster propojený se zbytkem firemní sítě, je vsazen do prostředí a správně zabezpečen firewally apod.
- Vystrkávání do Internetu je do nějaké míry řízené a minimalizuje riziko data exfiltration nebo vytvoření nezabezpečeného vstupu do prostředí.
- Všechny události jsou logované a auditované.
- Nadstavby nad Kubernetes jsou nasazené podle best practice (autoškálování apod.) a jsou aktualizované (např. Ingress, ExternalDNS, Kured, Cert-manager, ...).
- Existují nadstavbové komponenty ověřené a podporované centrálním týmem - Ingress, autoscaler, service mesh, monitoring, ...
- Je připravena doporučená (ale nikoli jediná vynucená) cesta pro CI/CD - tedy například určím GitHub Actions a budou fungovat všechny prostupy, loginy a budou k dispozici příklady od centrálního týmu jak to používat.
- Bezpečnostní politiky v clusteru brání jeho uživatelům udělat zásadní bezpečnostní chyby.

Našlo by se toho samozřejmě víc, ale o to teď nejde. Zkrátka oba chtějí zjednodušit život uživatelům, nabídnout jim podporu a prošlapané cestičky a přitom zajistit bezpečnost, provozovatelnost a umožnit sdílení zkušeností napříč celou organizací. To je podle mě cesta, jak zůstane centrální IT relevantní pro novou éru:
- Připravuje best practice destilované ze všech projektů.
- Pomáhá navrhovat a konzultovat řešení.
- Zjednodušuje nasazení a adopci cloudu v organizaci.
- Chrání organizaci definicí a implementací bezpečnostních a provozních postupů.
- Nelikviduje DevOps a nediktuje týmům jak mají nasazovat svou aplikaci a nebrání tak inovacím - ale připravuje prozkoumaná funkční řešení pro rychlý začátek a nabízí konzultace, zkušenosti.

# Jak se na to dívá pan Bílý
Pan Bílý dokázal nalákat technický talent a má armádu velmi schopných lidí ochotných hrabat se v hlubokých detailech. Jeho strategií je nakoupit levné železo a nad tím si všechno postavit svépomocí nad open source projekty. Pan Bílý bude vždy mluvit o nutnosti totální kontroly a flexibility, protože jejich požadavky jsou unikátní a tu kontrolu prostě potřebují. Tohle typicky nemá "spočítané" - neví kolik ho stálo pár let něco ladit a kolik to přineslo (vs. normální standardní řešení), nemá představu kolik co stojí, protože se vždycky nakoupí velká hromada železa a od druhého dne už je přece zadarmo (tak sbírejme všechno sem i kdyby to nedávalo smysl, už tu bednu máme a kdyžtak přikoupíme). Vysoká míra specializace je u něj nutná - existují technologické týmy, které implementují věci jako Kubernetes pro ostatní. 

I přes obrovskou sílu lidského kapitálu si začíná pan Bílý uvědomovat, že tempo inovací nestačí. Začíná mu docházet, že to co tým několika lidí 3 roky buduje a uživatelé této platformy stále nejsou plně spokojeni, je v cloudu dostupné na tlačítko. Vedení to vnímá a chce to řešit, vydává se do cloudu.

První myšlenka u pana Bílého bude zachování všeho jak to je, jen to posunout do cloudu. Ideální představa je něco, za co má kompletní odpovědnost poskytoval, ale oni mají root access i do infrastruktury a OS a můžou si tam dělat naprosto cokoli s plnou flexibilitou - což samozřejmě zjišťují, že není reálné. Ve finále si tak chtějí koupit jen IaaS a jede se, ale to samozřejmě neřeší ten důvod, proč firma do cloudu jde. Prvotní představa je taková, že je potřeba všechno totálně ovládat a řídit si sami. Musíme. Jsme unikátní. Bez přímé kontroly to nelze. Hodně se objevují situace typu "tohle si napíšeme sami" a také se objevuje efekt, kterému říkám "usnout v knihovně". Jsem v situaci, kdy cloud ještě neumím, ale koukám po nejnovějších výstřelcích a chci je dělat, protože to je přece trend - je to touha (kterou mám rád a plně ji chápu) se učit, jít po něčem zajímavém. Ale přechod do cloudu v masivním měřítku znamená nutnost dělat věci jednoduše, obyčejně a dost nudně. Takové věci totiž zafungují a dotáhnou se do konce. Tak například na automatizaci mutli-cloud infrastruktury je strašně zajímavý projekt Crossplane nebo operátoři jednotlivých cloud poskytovatelů, ale také třeba Cluster API pro Kubernetes. Problém ale je, že je to naprosto nové, polovina cloud služeb tam zcela chybí a ty co tam jsou neumí nejnovější funkce, dokumentace je tragická, lidí co s tím mají zkušenost je pomálu. Na nový projekt, který si chci v cloudu vybudovat je skvělé to zkusit, ale vsadit na něco takového masivní migraci do cloudu není dobrý nápad. Zůstaňme u Terraform ... jasně, pro nás co se v tom pohybujeme delší dobu už nuda. Právě. Funkční, výborná podpora cloudových služeb, skvělá dokumentace, ověřené postupy, přednášky, zkušenosti. Vsadit na malou firmičku, malý projekt a pak se divit co v tom všechno nejde je chyba - do cloudu jdu pro služby a dynamické inovace, nemůžu si před to dát nějakou věcičku, která mi miliardy dolarů investic cloudových hráčů shodí ze stolu, protože je ještě nepodporuje. A naštěstí pan Bílý netrpí zas až tak velkou "lockin" paranoiou, která je jinak dost běžná (mno ještě toho trochu). Stavem, kdy se odmítám "uzamknout" k největším a nejstabilnějším firmám planety a raději se uzamknu k řešení postaveném firmou o pěti lidech (jejíž šance zmizet z planety a tím mi vytvořit zásadní technologický dluh, páč to budu muset předělat, je dramaticky větší) nebo si napíšu nějaké svoje udělátko a jsem locknutý k němu (moje zkušenost je, že lockin k tomu co jsem spáchal sám na sobě je ten nejhorší). Odlišujme "next-gen" a v něm zkoumejme nové trendy (u toho moc rád budu), ale pokud potřebuji něco v masivním měřítku vyřešit teď, nudná cesta do cloudu je ta správná.

# Jak by to řešil pan Černý
Pan Černý je klasik. Na všechno je process. Každá komponenta má jasný nakoupený support, smlouvu, sankce. Všemu předchází nekonečné diskuse, studie proveditelnosti, návrhy v různých úrovních detailu, schvaluje se každou chvíli něco někde. Pan Černý je enterprise a nutno uznat, že přísné bezpečnostní politiky stojí za tím, že nikdy ve své historii neměl vážný únik dat. Díky tomu ale tato firma není zrovna nejrychlejší v IT inovacích. Vývojáři a vlastníci byznys aplikací potřebují cloud, od své IT organizace dostávají reakční dobu v řádu let, ne minut. Eskalují a firma se rozhodne jít do cloudu a skutečně nikoli nevýznamnou část tam po pár letech dostane. Všechno je velmi svázané, velmi přísné a centrální IT všechno obalí důkladným procesem. Přestože je firma významným uživatelem cloudu a projekt je úspěšný, vnitřně se nezměnila. Ani organizačně a vlastně ani technicky. Tohle vedení vidí a musí to řešit. Reorganizace, nůž na krk. A v této situaci potřebuje centrální IT nabídnout organizaci Kubernetes v cloudu. Zatím se soustředili na vyřešení síťového a bezpečnostního prostředí, IaaS a napojení platformních služeb do sítě, ale Kubernetes je komplikovaný a v zabetonovaném prostředí out-of-the-box prostě nefunguje, musí se to vymyslet. Z Kubernetes se má stát služba centrálního IT - to je to jediné, v čem si jsou s panem Bílým podobní.

Jak pan Černý implementuje služby? Nejdřív potřebuje zadání a požadavky, následně udělá několik úrovní designu, proběhne si několik schválení, provede velké množství rozhodnutí jaké nástroje používat (bude mít tendenci místo nativních na kliknutí dostupných nástrojů v cloudu použít to, co už tímhle kolečkem prošlo - jejich onprem backup, monitoring, alerting, SIEM, automation, ....), zaškolí supportní týmy (síťaři, provozáci, bezpečáci, ...) a pak službu zařadí do svého katalogu (doslova - místo, kde si řeknete o službu a ona se vám v cloudu připraví). Samozřejmě si uvědomuje, že automatizace je nutná a také s tím počítá. Uživatel zadá požadavek, systém zjistí, jestli na to má budget, aby mu mohli účtovat, a na pozadí se to v cloudu vytvoří a oni dostanou klíče ke službě.

Největší slabinou tohoto přístupu je, že to pan Černý staví stejně, jako by měl koupit nějakou bednu a tu pět let provozovat a nabízet ostatním. Bedna musí být u mě - takže všechny Kubernetes clustery potřebujeme do své vlastní subskripce a nikoho tam nepustíme, oni dostanou jen login do Kubernetu. Jedině tak to udržíme pod kontrolou. Stejně jako by to byla bedna to potřebujeme teď pořádně vymyslet. Rok si mákneme a pak to 5 let provozujeme = po roce máme hotovo, tady to předáme provoznímu týmu. Supportnímu týmu potřebujeme vytvořit návod. Když bedna svítí zeleně, je to OK. Když svítí oranžově, udělej tyhle tři kroky, aby se to zlepšilo. Když svítí červeně, volej výrobce, s kterým musíme dohodnout právně neprůstřelnou smlouvu. Co uživatelé s bednou dělají neřeš, to je "aplikační problém". Musím vůbec říkat, že to v cloudu není optimální přístup? Že řízení a politiky nejsou o tom urvat si to k sobě (a tím příšerně zesložitit napojení na další služby i účtování)? Že cloud se mění každý měsíc a zásadní redesign bych měl dělat dvakrát ročně, abych využil nejnovějších vlastností a vlastně nikdy nebudu hotov, abych to někomu předal? A že opravování světýlek udělá Microsoft, já spíš potřebuji rozumět tomu jak se to používá a pomoci uživatelům to správně ovládat a navrhnout případně pomáhat s eskalací na poskytovatele?

# Jaká je cesta, kam to směrovat
V první řadě považuji za problematické mít jako scope Kubernetes. To je platforma poměrně nízkoúrovňová, není to řešení zaměřené na vyšší míru abstrakce a akcelerace delivery pro vývojáře a byznys. Někdy ta flexibilita za to hodně stojí (nižší náklady, lepší optimalizace, neomezené možnosti), jindy je lepší použít něco výše (serverless s Azure Functions například). Ale vraťme se ke Kubernetes.

Myslím, že pan Bílý i Černý se potřebují vydat podobným směrem.
- Využít AKS a jeho managed vlastností nejenom z pohledu Kubernetu, ale i dalších technologií:
    - Autentizace, SSO a podmíněné přístup s AAD
    - RBAC přes Azure API s možností Privileged Access Managementu
    - Pod identity pro přístupy Podů ke službám v Azure
    - Managed Ingress s Azure Application Gateway
    - Azure Monitor for Containers pro logování a telemetrii
    - Azure Policy pro definici a enforcement bezpečnostních pravidel
    - Volitelně managed Open Service Mesh
    - CSI SecretsClass pro Azure Key Vault
    - Volume drivery
- Připravit základní base konfiguraci clusteru v rámci Azure API
    - Volba síťařiny a začlenění do sítě
    - Volba přístupu na API server např. pře private link
    - Volba OS customizace, je-li potřeba (např. zvednout fs watchers)
    - Naladění cluster autoscaler a doporučené nodepooly
    - Doporučené postupy pro aktualizace, upgrady, pod disruption budget
    - Nastavení RBAC a základních systémových namespace
- Připravit nadstavby nad Kubernetes (jsou-li potřeba) nasazované přes Kubernetes API, například
    - External DNS napojená na Azure Private DNS
    - 3rd party Ingress
    - API Management (např. Azure APIM self-hosted gateway)
    - KEDA autoscaler
    - Cert-manager
    - Kured
- Vytvořit bezpečnostní politiky a aplikovat na všechny clustery
- Automatizovat vytváření clusterů s využitím GitOps - clustery budou v subskripcích uživatelů, nikoli mimo ni
    - Použít Terraform pro vytvoření modulu a následně v Git spravovat zhmotnění modulů pro všechny clustery (tzn. centrální state pro celou firmu, jeden zdroj pravdy)
    - Otevřené řešení tak, že lídři týmů mohou dělat pull requesty (tzn. vytvořit nový cluster - pokud vědí jak na to, pokud ne, udělá to tým za ně) a jasný proces jak IT schválí (udělá merge)
    - Na pull requests sjet testy (minimálně udělat terraform plan a vyplivnou chyby a problémy), na merge spustit Terraform (udělat rekoncilaci)
    - V rámci Terraform řešit všechno, co se dělá Azure API a naboardovat cluster do pull-based GitOps (např. Flux s využitím AKS addonu)
    - Clustery budou volat "domů" a automaticky provádět rekoncilaci a to do dvou adresářů v Gitu - common a per-cluster
        - Common adresář bude obsahovat Kubernetes objekty pro všechny clustery - například 3rd party Ingress apod., takže změna stavu zde se automaticky projeví na všech clusterech (např. upgrade ingress na novější verzi)
        - Per-cluster adresář pokud jsou potřeba speciální nastavení per-cluster (tady beru pro nastavení infra nadstaveb, ne samotný release aplikací - ale i to je možné, jen myslím, že by IT tým neměl mluvit lidem do toho, jak budou nasazovat aplikace, ale pull based GitOps je jistě jedna ze zajímavých variant)

Je to samozřejmě poměrně komplikované a neberte jako výčet, spíš náčrt, příklad. Podstatné je, že centrální tým hraje roli toho, kdo připravuje designové principy, moduly, šablony a má na starost držet state clusterů, bezpečnostní politiky a tak podobně. Všimněte si, že tohle všechno je možné i přímo v subskrici uživatele, což umožňuje efektivně řešit billing, síťové propoje typu Private Link na PaaS služby, RBAC pravidla a další věci. Současně platí, že se využívá abstrakce nabídnuté cloudem - Azure API zajistí nejen hotový Kubernetes, ale jeho celý životní cyklus, monitoring, bezpečnost, sítařinu, nadstavby a mnoho dalšího - byl by nesmysl toho nevyužít a montovat si clustery nad IaaS a roky se trápit tím, jak dosáhnout toho, co AKS už umí. Výnosy z rozsahu - za AKS stojí armáda hodně chytrých lidí, k největším hráčům planety to samozřejmě ty nejschopnější hodně táhne. Podle mě není reálné říkat si, že budu o tolik chytřejší než oni, že je lepší si to postavit sám (= co do toho já vložím za energii se mi vrátí v podobě nižších nákladů a nebo rychlejšího time-to-market). Zejména, když AKS je zdarma - master nody neplatíte (můžete si k nim SLA, ale stojí míň než jedno VMko) a worker nody nemají žádný příplatek, platíte cenu běžného VM. 

# Kdo bude úspěšnější? Pan Bílý nebo pan Černý?
To je otázka, která mně často napadá a nejsem si jist. Pan Bílý má rozhodně podstatně lepší technické předpoklady stát se Site Reliability Engineer (SRE), který se věnuje primárně automatizaci a neustálému zlepšování služeb (než každodennímu hašení požárů) a také konzultační jednotkou (Cloud Competency Center), ke které se bude celá firma obracet pro radu. Ale je u něj velké riziko, že znovu ztratí pojem o tom, co je pro firmu důležité - vrátí se k řešení technických detailů a vychytávek bez zřetele na to co firmu posouvá dopředu a co ne, co jí umožňuje se odlišit od konkurence - budou to spíš její aplikace a zpracování dat, než její schopnost vypotit v infrastruktuře věci, na které je tlačítko v cloudu. A pan Černý? Jeho výhodou určitě je, že ví co znamená využít službu třetí strany, nedělá zbrklé výstřelky a co rozchodí je schopen kvalitně a dlouhodobě podporovat. Překoná ale svůj technologický dluh? Pan Černý má o dost větší rozdíl mezi svou aktuální realitou a svou budoucností co do technologie. 

Jak pan Bílý tak pan Černý mají před sebou myslím hodně práce. Každý má dost jinou výchozí situaci, jiná rizika, ale ve finále si myslím, že řešení situace je pro ně dost podobné a věřím, že to dokážou. Zdá se mi, že pattern pro centrální IT funguje u obou velmi podobně i přes to, že jsou hodně rozdílní. A co myslíte vy? A jakou barvu má vaše firma?