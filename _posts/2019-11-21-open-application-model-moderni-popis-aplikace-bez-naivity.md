---
layout: post
published: true
title: 'Open Application Model: moderní popis aplikace bez naivity' 
tags:
- Kubernetes
- Automatizace
---
DevOps není o všeználcích, role a odpovědnosti zůstávají, jen to celé funguje dokonale dohromady. Tak jak ve Phoenix Project vidíme připodobnění k lean manufacturing v továrnách, tak tam také nalezneme specializované roboty. Rozdíl je v tom, že to výborně jede dohromady - nehromadí se rozdělaná práce ve skladech, na nic se nečeká, na chyby se přichází včas. Aktuální stav cloud-native modelů pro popis aplikace je nesourodý mix echt infrastrukturních nastavení, aplikačně-provozních věcí i vývojářských zálěžitostí klidně v jediném souboru. To nepřeje realitě týmů, znalostem a zkušenostem jeho členů, bezpečnosti, compliance a ani modelům, kdy je vývoj oddělen od provozu (například když software prodáváte). Microsoft inicioval vznik specifikace Open Application Model, která se snaží na to jít jinak. A kromě toho vznikl RUDR - implementace OAM pro Kubernetes. Podívejme se dnes o co jde, proč a příště si to vyzkoušíme.

# DevOps bez supermanů

DevOps učí o spolupráci, full-stack inženýr je borec v inzerátech co umí všechno a svět je pak modřejší. Realita je ale taková, že i v rámci DevOps týmu máte jisté specializace a zejména v enterprise prostředí jsou dobré důvody pro rozdělení odpovědností. DevOps tým nemusí znamenat, že všichni dělají všechno (tedy jak to co umí, tak co moc neumí), ale že mezi vývojáři a provozem dochází ke každodennímu sdílení informací a funguje to dohromady. Navíc myšlenka, že co si nadrobím (rozuměj naprogramuji), to si také sním (rozuměj provozuji) nemusí být ani možná. Například proto, že jste v regulovaném segmentu a tyto role musíte držet oddělené z důvodu compliance. Nebo ten, kdo software píše a ten, kdo ho provozuje jsou jiné firmy - vývojová firma prodává svůj produkt, který si zákazníci provozují sami nebo zákazníci využívají služeb custom vývoje specializované firmy a ne vždy se ve světě smluv a kontraktů podaří nastolit pravou DevOps atmosféru (ale znám příklad, kdy se to povedlo i tak).

Skutečnost většinou vede na 3 základní role a právě ty OAM popisuje.

# Role v popisu a provozu aplikace

Z pohledu specifikace OAM existují 3 základní role.

- Vývojář (nebo také aplikační architekt) se kromě samotného vývoje zabývá popisem jednotlivých komponent (například mikroslužeb). Specifikuje jaké vstupní parametry se při nasazení mají předávat a jak (connection stringy, feature flagy apod.), kde je nějaký spustitelný artefakt (například Docker image), jaké porty služba nabízí (například REST API). Dále by měl vývojář říct, jaký typ aplikace to je - může běžet ve víc balancovaných instancích (klasický stateles web) nebo to musí být singleton (např. stavová služba), je to trvale běžící služba (třeba web) nebo jednorázový job a tak dále. Vývojář také může říct, že potřebuje zapisovat na disk. Nicméně vývojář neřeší jak budou tyto požadavky doručeny.
- Aplikační provozák má za úkol se věnovat konkrétní instanci aplikace, tedy tomu, jak se z hromady komponent stane fungující systém. Dosazuje hodnoty (connection stringy apod.), určuje způsob o formu škálování, způsob discovery služeb, síťový routing, canary release proces a tak podobně.
- Infrastrukturní provozák řeší low-level detaily implementace. Pokud komponenta potřebuje škálovat, vytvoří se například nový node a na něm se komponenta spustí nebo se použije nějaké serverless řešení jako jsou virtuální nody v AKS? Když se má implementovat traffic split jako service mesh, jakou implementaci použijeme - Istio nebo Linkerd nebo Consul Connect? A jak se bude implementovat Ingress? NGINX nebo Azure Application Gateway nebo Traefik?

Všimněte si, že vývojář může být někdo jiný, než ten, kdo pak aplikaci provozuje. Role infrastrukturního provozu může být centrální IT tým nebo platformní cloudová služba a ne tým, který řeší vývoj a nasazování aplikace.

# Jak Kubernetes mixuje role

Kubernetes objekty reflektují spíše technologické aspekty, než ty lidské. Často to vede na to, že se vývojáři začínají zabývat věcmi, s kterými nemají velkou zkušenost (a naopak to funguje zrovna tak). Tak například - co může být výstupem vývojáře jsem popisoval v předchozím odstavci. Kromě Docker kontejneru to v Kubernetes může vypadat na objekt Deployment. Jenže v něm se míchá popis komponenty (požadované vstupní parametry, image, URL k health probe) a aplikačně-provozní nastavení (jak často se kontroluje health probe, kolik replik má služba mít, jaký typ Volume se má použít, bezpečnostní pravidla provozu). Pokud chceme autoškálování, jehož použití a nastavení je rolí aplikačního provozu, tak nás Kubernetes nutí i do low-level infrastrukturních detailů - bude HPA koukat na heapster, Metric server, Prometheus konektor nebo se bude škálovat přes KEDA?

Na mnoha dalších příkladech zjistíte, že role jsou opravdu nepříjemně pomotané. Lidé se to snaží řešit oklikami. Parametrizují si deployment přes Helm a hlídají si kdo které parametry má řešit, ale takové podomácku vymyšlené systémy zaberou čas a každý DevOps tým (pokud máte různé pro různé aplikace) může dojít k jiným závěrům (což nepřispívá k přehlednosti).

# Chybějící koncept aplikace v Kubernetes

Ještě jeden aspekt tu je. Kubernetes není platforma pro vývojáře, je to infrastrukturní systém - orchestrátor kontenerů. Zabývá se nasazováním komponent a objektů (a jde mu to skvěle). Vaše aplikace je ale složena z hromady Deploymentů, Volumů, Secretů, ConfigMap, Service, Ingressů, Network Policy a tak dál. V Kubernetu ji nenajdete jako nějaký celkový objekt.

U jiných kontejnerových orchestrátorů takový objekt někdy existuje (třeba u Service Fabric nebo Cloud Foundry) a u nadstaveb typu OpenShift ho v jisté formě najdete taky. Dalo by se říct, že Helm je to ono, ale Helm je něco, co do Kubernetes přichází zvenčí. Je nesmírně užitečný, ale objekt "aplikace" žije jen mimo cluster, třeba ve vašem CI/CD nástroji. 

# Specifikace OAM
Jak tedy Open Aplication model naplňuje rozdělení rolí při popisu aplikace? Podrobnosti najdete na [https://github.com/oam-dev/spec](https://github.com/oam-dev/spec)

## Komponenty
Vývojář nebo aplikační architekt pracuje s definicí komponent. Syntaxe je podobná Kubernetes YAMLům, ale OAM necílí jen na Kubernetes, ale i jiné typy provozování služeb (IoT, serverless). 

- parameters - v nich vývojář konfigurační volby komponenty jako je connection string do databáze, nějaká nastavení, secrets. Podstatné je, že se definuje typ parametru, nějaký dokumentační popis a také možnost specifikovat default hodnotu (doporučení vývojáře).
- workloadType - typ komponenty, o tom blíže později
- osType a arc - zda je to Linux či Windows a například amd64 vs. armv7 apod.
- containers - specifikace kontejneru jako je image, env klíče, resources, health probes a tak podobně. Některé věci může chtít vývojář dát natvrdo, jiné chce načítat z parametrů. Resources nejsou jen zákadní koncepty jak je znáte z Kubernetes (CPU a RAM), ale i GPU, Volume a ExtendedResource (místo pro další rozšíření za rámec specifikace - například pro deployment do IoT zařízení tady může být přístup na konkrétní GPIO port apod.)
- workloadSettings - dodatečná nastavení mimo specifikaci, typicky pro aplikace nevyužívající kontejnery

Zajímavý je workloadType, kterým vývojář říká, jak se s danou komponentou dá pracovat. Ve specifikaci jsou základní typy v namespace core.oam.dev, ale i rozšiřitelné typy, které jsou specifické pro vendora. Tak například pokud je komponenta navázaná na specifické řešení typu serverless, může to být určeno zde. Komponenta také může být něco jiného, než váš vlastní kód. Třeba databáze, Redis cache nebo fronta a jako vývojář říkáte chci Microsoft SQL a je na dalších rolí vybrat konkrétní implementaci. core.oam.dev obsahuje tři základní typy komponent - Server (něco trvale běží a nabízí službu na nějakém portu), Worker (něco trvale běží, ale nenabízí endpoint ostatní, spíše si získává zadání z fronty a pracuje) a Job (něco je spuštěno v reakci na něco a po ukončení zpracování se zastaví). Všechny tři mají buď tuto variantu (tedy deklarují podporu active/active instancí) nebo variantu singleton (jde o nějakou stavovou službu s přísnou konzistencí, takže jen jedna musí být aktivní současně).

## Aplikační provoz - definice aplikační konfigurace 
Prvním důležitým objektem je definice aplikace ve smyslu kolekce komponent. Jde vlastně o seznam komponent (definic) a jejich založení (instance). Kromě jednoho seznamu můžete využít i další "scope". Dva základní jsou Network a Health, ale existuje ještě Quota, Identity případně další.
- Network scope říká je se které skupiny komponent budou chovat síťově. Které budou v oddělených subnetech, které se vystaví pro přístup zvenku a tak podobně.
- Health scope mluví o tom, jak se má měřit dostupnost skupiny komponent. Například jak často se má dělat health probe, jaký je timeout, kolikrát musí upadnout, než se to začne řešit. Obsahuje ale i informace pro upgrade proceduru, tedy kolik procent a jakých komponent může být maximálně nedostupné nebo definice komponent, které jsou nutnou podmínkou pro zdraví celého scope.
- Quota scope říká, jaké má daná skupina komponent provozní limity z pohledu spotřeby CPU, RAM, storage a tak podobně.
- Identity scope definuje, jaké identity má mít skupina komponent k dispozici. Například v Azure by to byla schopnost získat managed identity a použít ji třeba pro přístup do Azure Key Vault nebo SQL databáze přes AAD login.

Dalším důležitým konceptem jsou Traits. Ty rozšiřují základní workloadType o podrobnější vlastnosti, které už nejsou práce vývojáře, ale aplikačního provozu. Trait může být třeba manualScaler (jednoduše počet replik), ale i autoScaler (rámec škálování, na jakou metriku a jak reagovat), ingress (tuto instanci chci vystavit na nějaké venkovní URL) a tak podobně. Představte si třeba, že byste mohli tímto určovat binding serverless řešení (tedy tato funkce se má spustit, když se objeví nové zpráva ve frontě).

Samozřejmě u každé použité komponenty vyplníte hodnoty parametrů.

Každá změna komponent nebo nastavení vede na vznik nového release.

## Infrastrukturní provoz
Infra není v OAM popsána, resp. je to právě udělané tak, aby specifikace byla nezávislá na konkrétní implementaci a umožňila správně oddělit infrastrukturní rozhodnutí od aplikačních. Bude vaše Ingress implementace postavena na Azure Application Gateway, NGINX ingress kontroleru, Traefik nebo OpenShift routingu? Autoškálování bude používat HPA a Prometheus nebo metriky z Azure Application Insights nebo to bude KEDA? Nebo bude infrastruktura nějaká cloudová PaaS, kdy vám je jedno co pod tím je, když to vyhovuje OAM specifikaci? Nebo jde o IoT a Docker/Kubernetes se do vašich mikrokontrolerů nevejde, takže komponenty a jejich izolaci a běh řešíte jinak, ale stále to umí OAM specifikaci? Přesně to je jeden z cílů OAM.


Dost možná se to na první přečtení může zdát trochu složité, ale po pár dnech přemýšlení mi to přijde logické a jasné. Hned příště se podíváme na RUDR - implementaci OAM pro Kubernetes a vyzkoušíme si to na pár příkladech. Hned to bude jasnější.