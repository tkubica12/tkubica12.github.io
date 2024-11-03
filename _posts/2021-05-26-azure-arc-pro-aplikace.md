---
layout: post
published: true
title: "Azure vs. Google vs. AWS: Hybrid a multi-cloud řešení pro aplikace, serverless, data a AI - srovnání Azure Stack, Azure Arc, Google Anthos, AWS Outpost a Amazon RDS for VMware"
tags:
- Arc
---
Azure Arc myslím jednoznačně dominuje ostatním cloudovým hráčům co do hybridních a multi-cloud řešení. Google Anthos má podobnou strategii, ale reálné portfolio možností je znatelně menší. AWS v této hře dost pokulhává - z pohledu multi-cloudu zcela, nabízí hybridní přístup s Outpost, ale využívání PaaS mimo AWS samotné se omezuje jen na RDS nad Outpost a VMware. Co je u Azure Arc nového a jak se srovná s konkurencí? Níže je co se mi podařilo zjistit a je to osobní pohled - chytněte mě na LinkedInu či Twitteru, pokud mi něco důležitého uniklo.

# Azure Arc jako hybrid a multi-cloud control plane vs. Google a AWS
Azure Arc je technologie, které dokáže control plane Azure dostat i mimo hranice jeho vlastních datových center - tedy do jiných cloudů (Multi-cloud), zařízení distribuovaných co nejblíže systémů, které řídí (Edge) a do on-premises prostředí (Hybrid). Jinak řečeno vzít vybrané služby, které Azure umí udělat nad vlastní infrastrukturou a zpřístupnit i těm, co mají infrastrukturu jinde - například bezpečnost, monitoring, řízení, politiky, aplikační a serverless platformy, cloudové databázové systémy nebo machine learning. Azure Arc neřeší jak ta samotná infrastruktura vzniká - pokud chcete pomoci s nasazením infrastruktury u sebe, zaměřte se na rodinu Azure Stack - Azure Arc může běžet na ní (stejně jako nad jakoukoli jinou infrastrukturou).

Na tomto poli je z velké trojky největším konkurentem určitě Google Anthos. Myšlenka je tam velmi podobná, byť v exekuci a šíři služeb jsou zatím dost zásadní rozdíly, jak ještě uvidíte.

AWS v této oblasti nevyniká. Nejblíže k tomu má asi RDS pro VMware, ale to samozřejmě nijak nepodporuje Azure, Google ani vaše vlastní Edge prostředky (například v továrnách). 

Do všech oblastí teď nahlédněme trochu detailněji.

# Azure řešení pro stavbu on-premises infrastruktury vs. Google a AWS
Začněme mimo rámec Azure Arc - co může velká trojka udělat pro vaše on-premises prostředí, když chcete vybudovat infrastrukturu? Pokud chcete softwarové řešení, tedy mít velkou flexibilitu v použitém železe, je to Azure Stack HCI, které vám zajistí virtualizovanou infrastrukturu pro VM i Azure Kubernetes Service v GA. Varianta Azure Stack Hub je plně integrované řešení od železa po software (takový Apple v datovém centru) - přijede vám rozchozená benda, která navíc má vlastní cloudový zcela samostatný portál - je to tedy takový zmenšený osekaný Azure včetně již brzy Azure Kubernetes Service. Je tu i varianta Azure Stack Edge - menší Azure krabičky spravovatelné z cloudu, na kterých lze provozovat VM i Kubernetes.

Google Anthos v této oblasti dnes podporuje Anthos on bare metal, ale podle všeho jde jen o Kubernetes (nevyřeší vytváření a správu VM, na kterých stále stojí většina firemních aplikací). Můžete také použít GKE distribuci Kubernetes - nicméně z cenového hlediska to je docela vysoko (skoro až v rovinách Red Hat OpenShift) a přemýšlel bych, jestli dodavatel infrastrukturní části, bez které se stejně neobejdu, náhodou neumí Kubernetes bez příplatku nebo za lepších podmínek (VMware Tanzu, Azure Stack HCI).

AWS nabídka je postavena na Outpost - ten přináší základní ovládání pro VM a Kubernetes (EKS na AWS Outpost) a je koncipován podobně jako Azure Stack Hub (plně integrované řešení). Softwarová verze neexistuje, nicméně je ohlášena distribuce Kubernetu (EKS Anywhere).

**Shrnuto:**
Microsoft nabízí vertikálně integrované řešení včetně disconnected scénáře pro oblast od VM nahoru i softwarové řešení včetně hypervisoru a AKS. Google nemá nic pro svět VM, na kterém ale většina světa stále funguje a nabízí pouze software-only Kubernetes distribuci. AWS má vertikálně integrované řešení bez disconnected scénářů od VM nahoru a softwarové řešení je v přípravě, ale zahrnuje pouze Kubernetes, ne hypervisor. V této kategorii tedy za mne jednoznačně vede Microsoft, na druhé příčce AWS, Google asi poslední, protože vše co dělá jsou jen kontejnery a to je oproti ostatním málo.

# Azure Arc pro servery vs. Google a AWS
Servery a VM jsou a ještě dlouho budou zásadní realitou enterprise prostředí. Azure Arc pro servery umožňuje promítnou systémy běžící kdekoli (jiný cloud, on-premises, edge) do Azure a zajistit pro ně monitoring, logování, inventarizaci a governance, řízení přístupu (například k logům), bezpečnostní politiky, bezpečnostní dohled a detekci hrozeb nebo vzdálenou instalaci dalších rozšíření.

Google Anthos svět VM ignoruje - není součástí jeho strategie.

AWS nemá komparativní řešení jako je Azure Arc nebo Google Anthos. Ano, můžete nainstalovat monitorovací agenty, ale schopnost promítnout zdroj do cloudu pro funkce, které jsem zmínil, zatím chybí.

**Shrnuto:**
Microsoft má ucelené řešení pro správu, governance i bezpečnost virtuálek kdekoli (multi-cloud, hybrid, edge). Google nemá a AWS také ne. Toto kolo myslím Microsoft vyhrává, druhou příčku neumím vyhlásit.

# Azure Arc pro Kubernetes vs. Google a AWS
Azure Kubernetes Service má celou řadu velmi příjemných nadstaveb. Jde o oblast monitoringu (logy, metriky), řízení přístupů (autentizace přes Azure Active Directory včetně dynamické autorizace pro Privileged Identity Management), správu konfigurací (GitOps), bezpečnostní politiky (Azure Policy využívající Gatekeeper a OPA) nebo možnost instalovat do clusteru další rozšíření či hezké GUI. Co kdyby tohle bylo dostupné pro jakýkoli jiný Kubernetes běžící kdekoli? Třeba vaše on-premises clustery od VMware Tanzu, Red Hat OpenShift, Rancher nebo vlastní výroba nebo cloudové instance EKS či GKE? Azure Arc pro Kubernetes přesně tohle dělá - napojí váš cluster do Azure a tím získáte správu, bezpečnost, monitoring a další zmíněné vlastnosti.

Google Anthos je přímá konkurence a snaží se dosáhnout přesné téhož. Ano, podporuje AKS i EKS, ale také OpenShift nebo Rancher. Můžeme diskutovat šíři vlastností, kde v některých oblastech bude pokulhávat (za mne například bezpečnost), v jiných bude napřed (například services mesh - AKS podporuje Open Service Mesh v preview, ale Arc ještě ne).

AWS do závodu nenastoupil.

**Shrnuto:**
Za mne v tomto směru remíza mezi Microsoft a Google. AWS ani nenastoupilo.

# Azure Arc pro aplikační služby
Fascinující novinky z letošní Build konference přidávají hodně v oblasti aplikační. To považuji za naprosto zásadní. Kubernetes je nízkoúrovňová platforma - není to řešení pro vývojáře, pro platformní služby nebo serverless. K tomu má Kubernetes hodně daleko - to je výhoda, když chcete velkou flexibilitu a komplexita vám nevadí, ale pro většinu mých zákazníků by bylo lepší něco s větší produktivitou, větší mírou abstrakce. Ale to je lockin, zvolá jeden. Ale to není flexibilní, zakřičí druhý. Do jisté míry mají pravdu. Řešením by bylo tyto funkce dotáhnout do stavu, kdy jsou přidanou hodnotou nad Kubernetes a mohou tak běžet doslova vedle sebe v jednom clusteru služby PaaS i mnou spravované kontejnerové součástky. A co kdyby, když už jsme u toho, tenhle Kubernetes mohl být i mimo Azure? Přesně tak vypadá Arc pro aplikační služby.

Azure Application Services (WebApp) je přesně ta služba, která umožní rychlé a jednoduché nasazování, canary release, A/B testing nebo green/blue deployment či komplexní autoškálování podle metriky i kalendáře a to všechno jednoduše, přímo z IDE a bez nutnosti mastit YAMLy jeden za druhým. A co událostně řízený model a nestarat se o infrastrukturu vůbec, tedy použít Azure Functions? Oboje umí Azure Arc  nabídnout do AKS, EKS, GKE, OpenShift a tak podobně. Tím ale nekončím. Pokud mám moderní událostně řízený kód, dávalo by smysl mít integrační komponentu a nejlépe typu push (místo tradičního pull do fronty) a proto je Azure Event Grid dostupný i pro Azure Arc. Určitě přijde na řadu i potřeba řídit a směrovat API, řešit dokumentaci, provolávání, fasádu, bezpečnost a další vychytávky - Azure API Management je pro Azure Arc k dispozici. No a nakonec možná potřebujete stavové workflow a nejlépe ho naklikat, takže využijete Azure Logic App běžící díky Azure Arc ve vašem Kubernetes clusteru kdekoli na světě a v jakémkoli cloudu.

Google Anthos se nepochybně snaží o totéž. Aktuálně popisuje podporu pro Cloud Run a bez překvapení je stavěn nad KNative, což bychom měli považovat za serverless přístup. Jenže pozor - tohle je deklarováno jen pro GKE (tedy uznejme body za hybrid s GKE on-prem, ale multi-cloud se zatím nekoná). Navíc z pohledu jednoduchosti pro vývojáře si myslím, že je to o něco složitější, protože montování kontejnerů je dost na vás. Zkrátka primárním alternativa k Azure Application Services je App Engine, ne Cloud Run (ten ale můžeme připodobnit k Azure Functions, pokud je použijete s přinesením vlastního kontejneru, což samozřejmě lze). Další komponenty ať už alternativa k API Managementu (Apigee) nebo workflow řešení nemají v Anthos přímou podporu. Apigee gateway do něj jistě ručně dostanete, ale ne jako integrované řešení v rámci Anthos. 

A jak AWS? Do závodu opět nenastoupilo.

**Shrnuto:**
Microsoft je za mne po těchto oznámeních jednoznačně nejdál a činí řešení přístupnější pro vývojáře a všechny, kdo chtějí přejít do světa cloud-native plynuleji. Máte plnou sílu Kubernetes, dostanete servereless, ale i platformy s vyšší mírou abstrakce pro rychlou produktivitu. Google Anthos je v závěsu, ale za mne solidní druhá příčka a má i svoje výhody (třeba to, že service mesh je součástí), nicméně fakt, že Cloud Run je pro GKE, ale ne pro multi-cloud ukazuje, že v architektuře jsou některé rozdíly, které znemožňují Googlu postupovat rychle. AWS opět nenastoupilo.

# Azure Arc pro datové a AI služby
Další fascinující kategorie jsou datové a AI služby. Přímo v Azure Arc jsou dnes řešeny tři. První dvě jsou databáze pracující cloudovým modelem - pružné licencování, automatické aktualizace, jednoduché vytočení a škálování a to vše běžící v libovolném Kubernetes kdekoli. Jsou to Azure SQL a Azure Database pro PostgreSQL Hyperscale (Citus). Zajímavé je, že control plane je nasazen opravdu přímo v Kubernetu, takže i při výpadku spojení s cloudem vše funguje a podporován je i disconnected scénář (jinak řečeno nepotřebuje být připojeni do Azure, můžete jen off-line zasílat podklady k účtování - to může být důležité pro státní správu). Tyto databáze běží v kontejnerech. Třetí službou je Azure Machine Learning. Tato platforma umožňuje v cloudu vytvářet a spravovat modely strojového učení (MLOps), graficky vytvářet funkce a pracovat s daty, používat notebooky a k tomu potřebuje infrastrukturu pro samotné výpočty. Díky Azure Arc pro ML si můžete svůj Kubernetes cluster jako je EKS, GKE, OpenShift nebo VMware Tanzu napojit do Azure ML a pracovat s ním. Kromě těchto přímo integrovaných Azure Arc služeb je možné použít velké množství kognitivních služeb ve formě kontejnerů běžících kdekoli, například analýzu textu, syntézu řeči, rozpoznávání obličejů či rozeznávání a kategorizace obrázků a objektů. Lze předpokládat, že v budoucnu bude pro jednodušší nasazování a správu těchto služeb toto portfolio začleněno také do Azure Arc.

Google oznámil dostupnost některých kognitivních služeb jako je text-to-speech, ale to jsou jen kontejnery spuštěné jinde podobně jako Azure kognitivky. Zajímavější je určitě Bigquery Omni pro Anthos, ale podle všeho je tam dost technologický háček - na rozdíl od datových služeb Azure Arc tohle zdá se není postaveno na Kubernetu. Specificky zmiňují podporu jen AWS a Azure přijde. Tahle nekonzistence v architektuře stojí za povšimnutí. Cloud Run má asi nějakou dependenci na GKE a proto neběží v multi-cloud. Bigquery zas asi mluví s infrastrukturou nějak jinak a tak místo univerzálního control plane má dependenci na konkrétním cloudu. Nicméně Bigquery umí distribuovat a dotazovat data mezi cloudy - a to je hodně zajímavé, žádné jiné řešení v této kapitole něco takového neumí.

AWS na rozdíl od Azure Arc přináší databázovou technologii v podobě klasických virtuálek. Tím, že nestaví nad Kubernetes, musí architektura explicitně podporovat nějaké IaaS řešení a tím je aktuálně AWS Outpost a VMware, ne multi-cloud (neumí Azure ani Google) nebo jiné on-premises konfigurace (RHEV, Hyper-V). Jde o RDS pro Outpost nebo VMware a podporuje MySQL, PostgreSQL a Microsoft SQL. V případě rozpadnutí spojení sice databáze běží dál, ale nemůžete je spravovat - na rozdíl od Azure Arc pro datové služby neumožňuje ovládání trvale odpojený scénář např. pro air-gapped armádní vybavení. 

**Shrnuto:**
Vybrat nejlepšího bude v této kategorii opravdu obtížné. Amazon RDS for VMware je jako jediné z těchto řešení plně GA a to je dost zásadní informace. Na druhou stranu je to řešení "předchozí generace", není to kontejnerizovaný systém a má pouze omezenou podporu on-premises řešení (Outpost a VMware) a nulovou podporu pro multi-cloud. To jsou zásadní body dolu a navíc ze strategického hlediska je AWS podle mě zatím dost mimo. Microsoft Azure Arc je myslím nejdál co do architektury a univerzálnosti - datové služby podporují libovolný Kubernetes - OpenShift, Tanzu, Azure Stack s AKS, GKE, EKS, Rancher a tak podobně. To ostatní nemají. Kromě databází má v preview i Azure Machine Learning. Z těchto hledisek je to jasná jednička, ale jestli chci něco produkčního právě dnes, RDS tam už je ... ale stačí to? A Google? Anthos jde podle mě správným směrem, ale Bigquery je tam zasazeno spíš marketingově než architektonicky. Takové slepence už dnes vedou na zmatek - jasně, celé je to Anthos, ale tohle funguje jen tady zatímco něco jiného funguje zase jen jinde. Na druhou stranu je ale Bigquery řešení distribuované - data se mohou přelévat mezi cloudy, to Azure Arc nedělá - DB je buď tam nebo tam. Google cesta v terminologii Microsoftu by byla nabízet CosmosDB přes Azure Arc a začlenit do společné instance - a to Microsoft zatím neumí. Kdo vyhrál tedy nevím:
- Pokud to má být v GA, pak AWS - ale není to multi-cloud a je to takové "po startu"
- Pokud to má být univerzální hybrid a multi-cloud, pak určitě Microsoft - ale není to GA a není to replikace dat mezi cloudy
- Pokud to má být distribuované řešení mezi cloudy, pak určitě Google - ale není to GA, není to pro on-premises a nesedí to moc se zbytkem

# Pojďme to shrnout a vyhlásit celkového vítěze
Podle mě je jednoznačné, že Microsoft je nejdál v naprosté většině kategorií. Správná strategie, správná exekuce, velké investice a silná podpora jak hybrid tak multi-cloud. Google má za mě správnou strategii z aplikačního pohledu, ale o dost horší exekuci, nedostatečnou hybridní story (všechno prostě není kontejner) a za mě nedostatečnou datovou strategii, ve které je vidět dohánění marketingovými slepenci a že to dělá jiný tým. AWS podle mě šokujícím způsobem zaspalo. Multi-cloud nulový, hybrid je spíše pro nalákání do cloudu, než pro dodávání Amazon služeb do on-premises (od dob RDS pro VMware se neděje vlastně nic).

Pro hybrid a multi-cloud technologie bych volil Azure. Něco mi uniklo?
