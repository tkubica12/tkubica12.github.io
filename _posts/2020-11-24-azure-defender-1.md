---
layout: post
published: true
title: "Azure Defender (1): Zabezpečte backendovou infrastrukturu v Azure, jiném cloudu či vlastním datovém centru"
tags:
- Security
---
Bezpečnost je opravdu téma dost rozsáhlé, tak bych hned na začátek měl říct, že v této sérii se budu zaměřovat na schopnost řídit bezpečnostní nastavení včetně promítnutí do compliance a detekcí hrozeb s aktivní ochranou infrastrukturních i platformních služeb nejen v Azure, ale i v AWS, Google nebo on-premises. Nebudeme se v této sérii přímo věnovat bezpečnostním technikám na úrovni sítě, aplikací, šifrování a ochraně dat a tak podobně, byť z pohledu řízení bezpečnostních principů se jich budeme dotýkat. Dále se nebudeme zabývat bezpečností na aplikační úrovni (to si necháme na jindy a to zejména s prostředky, které nabízí GitHub), ani identitou, koncovými zařízeními uživatelů ani zabezpečením dat a informací.

Dnes si dáme úvod do Azure Security Center a Azure Defender a v příštích dílech se zaměříme na podrobnosti jednotlivých součástek a ochran.

# Trocha buzzwordů pro orientaci
Neustálé vymýšlení nových zkratek a kategorií přehlednosti úplně neprospívá, ale zase když už je to venku a Gartner reporty je používají, měli bychom se na ně podívat. Principiálně se budeme věnovat dvěma oblastem dle Gartneru.

**Cloud Security Posture Management (CSPM)** - to je v Azure implementováno převážně pod názvem Azure Security Center a je to právě schopnost podívat se na infrastrukturu i platformní služby v cloudu a dát vám názor na kvalitu vašeho bezpečnostního nastavení. Máte vhodně vyřešené přihlašování, je zapnuté šifrování, sbíráte správně auditní logy z infrastrukturních i PaaS komponent, používáte bezpečné protokoly, máte vhodné nastavení sítě a není tato otevřenější, než je potřeba? K tomu přidejte ještě vynucení určitých politik, například v kontejnerizovaném světě Kubernetes mají provozáci zákaz běžet privilegovaně, nesmí stahovat neprověřené komponenty z internetu, uživatelé cloudu nesmí v produkci vytvářet zdroje mimo EU, na VM nesmí chybět nějaký EDR systém pro ochranu proti malware apod. 

**Cloud Workload Protection Platform (CWPP)** - to je v Azure součástí Azure Defender, který svoje výstupy reportuje do Azure Security Center pro jednotný přehled (ale případně i do dalších nástrojů dle potřeby). Jedná se o aktivní ochranu, tedy schopnost detekovat hrozby a reagovat na ně. Pokud CSPM je o kontrole podmínek hokejového hřiště (mantinely určují jeho přesnou velikost, čáry jsou dle předpisů, branky mají správné rozměry, led je kvalitní, hráči vstupují s helmou), tak CWPP se zabývá samotným zápasem (na hřišti se neobjevil medvěd, hráči nezvedají hokejku do úrovně obličeje, rozhodčí nefauluje bránkáře hostů). Do této kategorie tedy patří chování samotných serverů (EDR), dále chování databází, kontejnerových platforem, IoT systémů nebo samotných cloudů jako je Azure, AWS nebo Google. To všecno patří do CWPP, ale všimněte si, že jde o věci, které se dějí "na backendu" nebo možná jinak řečeno nejde přímo o dění v identitních systémech, uživatelských zařízeních, aplikacích nebo datech.

**Cloud Native Application Protection Platforms (CNAPP = CSPM+CWPP)** - spojení obou přístupů do jediného nástroje umožňuje zasazení do moderních konceptů DevSecOps, protože pokud CSPM podporuje definici a ověření politik automatizovaně (Policy as Code), tak se už v rámci vývoje a testovacích prostředí programovatelně vynutí dodržování bezpečnostních principů a následně se detekují hrozby a anomálie. Tím, že je vše v jednom řešení, které podporuje prostředky automatizace, dají se tyto procesy komplexně popsat a opakovatelně nasazovat a reagovat na situaci. Tak například detekované pokusy a útok hrubou silou na interface pro správu (třeba RDP nebo SSH) je možné jednak zastavit automatickým vytvořením síťového pravidla pro rychlé zablokování těchto portů v Azure síti do doby vyšetření incidentu a současně informaci využít pro založení preventivní politiky s přísnějším řízením síťových pravidel, použití bastion serveru nebo just-in-time access sítě. Azure Security Center a jeho součást Azure Defender jsou tak učebnicovým příkladem CNAPP. Nicméně nenechte se mást slovem cloud - principy z větší části platí i pro on-premises zdroje, které je možné do systému připojit.

# Co umí Azure v oblasti definování vašeho hřiště
Azure Security Center pro prostředky Azure nabízí zdarma řešení pro vyhodnocování bezpečnostních nastavení, řízení ve formě bezpečnostního skóre, automatizované reakce včetně přenastavení nevhodně vytvořených zdrojů nebo možnost definice auditovaných i vynucených politik. Za příplatek k tomu přidává pohled do AWS a GCP a také on-premises servery. 

[![](/images/2020/2020-11-23-19-14-17.png){:class="img-fluid"}](/images/2020/2020-11-23-19-14-17.png)

Tak například moje serverless funkce je nastavena tak, že podporuje i nešifrovaný přenos.

[![](/images/2020/2020-11-23-19-15-46.png){:class="img-fluid"}](/images/2020/2020-11-23-19-15-46.png)

Můžu si přečíst v čem je problém a jak ho mohu napravit.

[![](/images/2020/2020-11-23-19-16-28.png){:class="img-fluid"}](/images/2020/2020-11-23-19-16-28.png)

V tomto případě můžu nápravu sjednat jedním tlačítkem.

[![](/images/2020/2020-11-23-19-17-13.png){:class="img-fluid"}](/images/2020/2020-11-23-19-17-13.png)

Další velkou oblastí je definice politik, které se mohou týkat nastavení Azure, Kubernetes, operačních systémů a nebo platformních služeb. 

[![](/images/2020/2020-11-23-19-19-00.png){:class="img-fluid"}](/images/2020/2020-11-23-19-19-00.png)

Co se s nimi dá dělat? Tady je pár příkladů:
- V této subskripci se smí vytvářet pouze prostředky na území EU
- Pro VM je možné použít pouze korporátem dodané hardened image
- V operačním systému (Linux, Windows) musí být nainstalovaná ta a ta bezpečnostní aplikace
- V Kubernetes clusteru se nesmí stahovat z Internetových repozitářů nebo spouštět privilegované kontejnery
- Zdroje v Azure podléhají firemní struktuře tagů a jejich názvosloví
- Platformní služby mají zapnuté auditní logy do centrálního systému
- Platformní služby mají zakázaný přístup z Internetu, nelze je používat bez Private Endpoint (Private Link)

Uživatele placené verze pak mají přístup k reportům seskupeným podle regulatorních standardů jako je PCI DSS nebo ISO 27001.

[![](/images/2020/2020-11-23-19-25-55.png){:class="img-fluid"}](/images/2020/2020-11-23-19-25-55.png)

V dalších dílech se na tyto vlastnosti podíváme podrobněji.

# Jak umí Azure hlídat hráče a dění na ploše
Azure Defender je placená služba a je k dispozici pro hybridní scénáře jako jsou VM běžící kdekoli nebo IoT systémy, ale zahrnuje i inteligentní ochranu platformních služeb jako jsou databáze.

## Ochrana VM
Pro virtuálky běžící kdekoli (mašiny mimo Azure připojíte přes Azure Arc for Servers) toho nabízí Azure Defender hodně.
- EDR (ochrana serverů proti malware a dalším zranitelnostem) díky zahrnutí Microsoft Defender for Endpoints do služby Azure Defender. Její součástí je tedy licence pro EDR, automatické zprovoznění a integrace do Azure Security Center.
- Předplacený prostor pro bezpečnostní logy v ceně balíčku (500MB denně per server), takže můžete provádět hunting, vizualizace a další operace přes mocný dotazovacíjazyk (KQL). Mimochodem prostor můžete využít i pro Azure Sentinel (tzn. už máte zaplacen "datový poplatek", stačí vám přikoupit Sentinel část pro vaše VMka).
- Vulnerability scanner je v ceně služby a technologicky je pod kapotou Qualys.
- Adaptivní řízení aplikací funguje tak, že se Azure Defender po dobu 14 dní učí jaké procesy běžně na VM existují a následně doporučí jejich whitelistování. V případě Windows využívá funkci App Locker a dokáže tak nejen detekovat, ale i přímo bránit spuštění neschválené aplikace, u Linux to funguje také, ale v tomto případě v režimu detekce.
- File integrity monitor se zaměřuje na kritické systémové a aplikační soubory, služby nebo záznamy v registrech a audituje jejich změny.
- Pokud je ve VM nainstalovaný Docker projede si Azure Defender jeho shodu s doporučeními CIS Docker Benchmark.
- Fileless attack detection je komplementární k EDR a pro operační systém Windows scanuje paměť serveru a hledá v ní různé toolkity a další škodlivé aplikace.
- Azure Defender se napojuje na Linux auditd a logy vhodnocuje. Dokáže tak například detekovat pokusy a spuštění reverse shell, modifikaci kernel modulů nebo spuštění hackerských nástrojů.
- Adaptivní řízení sítě na rozdíl od předchozích funkcí funguje pouze pro VM v Azure, protože využívá informací z Azure sítě pro navržení přísnějších firewall pravidel. Systém se učí a následně vám doporučuje kroky k utažení šroubů.
- Ještě jedna funkce je k dispozici pouze v Azure - Just-in-time access, protože funguje na principu otevření například management portů v Azure síti až na vyžádání právoplatného uživatele. Síť tedy zcela blokuje třeba SSH či RDP, dokud si ho oprávněný uživatel na časově omezenou dobu neodemkne.

Kompletní seznam alertů najdete v dokumentaci pro [Windows](https://docs.microsoft.com/en-us/azure/security-center/alerts-reference#alerts-windows) a [Linux](https://docs.microsoft.com/en-us/azure/security-center/alerts-reference#alerts-linux).

## Ochrana databází
Azure Defender dokáže chránit platformní databáze Azure SQL, Azure Cosmos DB, Azure Database for PostgreSQL a MySQL a v preview také SQL ve VM (tedy včetně těch běžících mimo Azure). 

První funkcí je vulnerability assessment, kdy Azure Defender zkoumá zranitelnosti dané neoptimální konfigurací (ano - patří tedy spíše do CSPM, ale protože je placený v rámci Azure Defender, nechal jsem ho v této části). Jde například o nesprávné použití privilegovaných účtů, příliš velká oprávnění pro guest role a tak podobně. Hodně zajímavá je automatická klasifikace sloupečků s cílem identitikovat ty obsahující citlivé údaje nebo podléhající GDPR a následně assesment navrhuje jejich vyšší zabezpečení, například přes funkci Always Encrypted nebo Dynamic Data Masking.

Druhá část řešení se zabývá kontinuální ochranou a sleduje přístupy do databáze. Dokáže odhalit pokusy o SQL injection, brute force útok na heslo, podezřelá přihlášení nebo neobvyklé datové dotazy a operace (například použití jiné destinace než obvykle pro export dat, což může indikovat, že nejde o běžnou zálohu, a zcizení dat).

Seznam dosavadních alertů pro SQL je v [dokumentaci](https://docs.microsoft.com/en-us/azure/security-center/alerts-reference#alerts-sql-db-and-warehouse).

## Azure Defender for IoT
Ochrana IoT je velké téma a nejde jen o běžnou součást Azure Defender, ale ucelené řešení využívající akvizici firmy CyberX. Jde o soubor technologií využívající komponenty zabudované v samotném IoT jako jsou bezpečnostní čipy Azure Sphere nebo bezpečnostní vlastnosti Azure IoT SDK řízené z IoT Hubu, ale také bezagentové senzory využívající odposlechu samotného síťového provozu (SPAN porty apod.). Senzory lze řídit z cloudu, ale i z on-premises řídícího systému, takže řešení je možné použít i pro IoT systém izolované od jiných sítí (air-gap).

## Ochrana platformních služeb - Kubernetes, App Service, Key Vault a dalších
Azure Defender dokáže zvýšit bezpečnost platformních služeb v Azure. Konkrétně jde o tyto možnosti:
- **Kubernetes** - systém sleduje chování celého clusteru a detekuje podezřelé situace jako je spuštění privilegovaného kontejneru, vytvoření nové uživatelské role s vysokými právy, kontejner s namapovaným souborovým systémem hostitele apod.
- **Docker** - Azure Defender sleduje chování hostitele a umí detekovat například SSH server běžící v kontejneru a další podezřelé situace.
- **App Service** - platformní služba pro provoz aplikací zvládne po zařazení pod Azure Defender detekovat pokusy o útoky na web a CMS systémy (Wordpress, Joomla, Drupal), PHP soubory v nevhodným adresářích, curl s výstupem na disk, fileless útoky, podezřelý SVCHOST a celou řadu dalších.
- **Key Vault** - Azure Defender dokáže detekovat podezřelé přístupy k trezoru například z anononymizovaných IP, neobvyklé vyčítání klíčů (použitý účet standardně čte nějaký secret a najednou si sekvenčně získává všechny), podezřelou změna přístupové politiky apod.
- **Síťové události** - konkrétně podezřelé situace zjištěné z Microsoft routerů (přístupy na SSH/RDP vašich serverů z anonymizovaných IP apod.), hlášky z Azure DDoS Protection Standard nebo z Azure Web Application Firewall (např. Front Door nebo Application Gateway).
- **Blob storage** - Azure Defender odhalí neobvyklé přístupy ke storage a také scanuje uložené soubory a hledá v nich malware.
- **Azure Container Registry** - s využitím Qualys technologie registr scanuje obrazy Docker kontejnerů a to jak adhoc při jejich vytvoření a tak pravidelně opakovaně a reportuje zjištěné zranitelnosti.

## Ochrana samotných 
Z pohledu CWPP je nově v preview detekce hrozeb ve voláních Azure Resource Manager, což je control plane Azure. Odhaluje anomálie jako je přístup k vašemu Azure z neobvyklé země, z anonymizované IP, s nereálným přemístěním v daném čase, podezřelé operace provedené účtem, který už dlouho k Azure nepřistupoval nebo podezřelé machinace s RBAC.

Nově je v preview také integrace s AWS Security Hub a GCP Security Command, takže do Azure Security Center můžete dostat i data z těchto dalších cloudů. Kromě toho samozřejmě Azure Defender pro servery, SQL ve VM nebo Docker funguje ať už tyto běží v jakémkoli cloudu nebo on-premises.

# Automatizace a reakce na zjištění
Azure Defender dokáže na alerty reagovat spuštěním automatizačních worflow, které si doslova nakreslíte případně obohatíte o vlastní kód. Základem jsou Logic App. Orchestrační nástroj se stovkami připravených kontektorů do Microsoft produktů (Office, AAD, Sharepoint, Teams, SQL, Blob storage, ....) i řešení třetích stran (Service Now, Adobe, SAP, SalesForce, ...) vám umožní reagovat jakkoli a používá se i u Azure Sentinel (SIEM/SOAR řešení, do kterého se Azure Defender dá jedním kliknutím integrovat). Pokud tedy Sentinel nepoužíváte a potřebujete reagovat už v Azure Defender, jde o stejnou technologii automatizace. Uvedu pár příkladů co s tím můžete dělat:
- Pokud dojde k útoku na SSH a RDP na VM, můžete odeslat vlastníkovi serveru, kterého zjistíte z tagu, jeho nadřízenému (to zjistíte z AAD) a bezpečákům email, že k tomu došlo s tlačítky "ano, víme o tom" a "to je nečekané". Pokud odpoví, že to byli oni, napíšete tto do poznámky incidentu a zavřete ho. Pokud to nečekali, nastavíte Network Security Group tak, že zablokuje veškeré tyto přístupy a založíte incident v Service Now s požadavkem na důkladné prošetření.
- Azure Defender detekuje v blob storage malware. Pošlete zprávu do Teams dotčenému aplikačnímu týmu a soubor z tohoto accountu nakopírujete do jiného, do kterého má přístup jen bezpečnostní tým. Původní soubor smažete a informaci pošlete bezpečnostnímu týmu k řešení.
- Azure Defender zjistí přístup do VM z podezřelé adresy a následný pokus a spuštění malware. Tato VM je v onpremises. V reakci na tuto událost spoustíte vlastní konektor, který se připojí přes API do vašeho firewallu a zablokuje přístup této venkovní IP do firmy. Současně založí incident v Service Now. Po uplynutí 24 hodin automaticky pravidlo vymaže.


Azure Defender je řešení, které doporučuji využít alespoň pro všechny předprodukční a produkční IaaS a PaaS systémy v Azure, ale zvažte jej i pro on-premises (nebo jiné cloudy) a to zejména pro Windows servery (díky mocné síle Microsoft Defender for Endpoint pod kapotou - nicméně zásadní hodnotu vidím i pro Linux díky Qualys analýzám, update managementu, hledání hrozeb analýzou auditd a sběrem bezpečnostních logů) nebo i některá vývojová prostředí (zejména pokud nejsou striktně oddělena od produkce nebo používají zákaznická data). Tam byste neměli zůstat bez EDR a místo nákupu samostatného řešení (jako je třeba Microsoft Defender for Endpoints v licenci pro servery) můžete stejný nástroj získat v rámci balíku Azure Defender a dostat tak logy na jedno místo, získat Qualys vulnerability scanner a další vychytávky. Předplacený prostor na data vám také prolevní případné nasazení Azure Sentinel nad Azure Defender a získáte tak cloud-native SIEM/SOAR řešení. V příštích dílech seriálu si aspekty Azure Defender vyzkoušíme podrobněji.