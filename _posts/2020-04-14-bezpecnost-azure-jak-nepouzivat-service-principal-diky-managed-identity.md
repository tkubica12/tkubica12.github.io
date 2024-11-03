---
layout: post
published: true
title: 'Bezpečnost Azure: Jak nepoužívat Service Principal díky Managed Identity a zbavit se tak čekání na ticket u vašeho enterprise IT'
tags:
- Security
---
Jste enterprise firma a využíváte Azure? Pak je velká šance, že si nemůžete samostatně vytvářet účty service principal a potřebujete intervenci vašeho IT ... a ta dost možná trvá ... v lepších případech dny, jindy měsíc. Proč to tak bývá? Proč mít separátní tenant je fajn nápad, ale vhodný spíš jen pro vývoj? A jak můžete použít Managed Identity všude kde to jde a výrazně tak potřebu Service Principal účtů omezit pro dobro agility i bezpečnosti?

# Co je účet Service Principal
Klikání v Azure, čtení emailů, psaní zpráv na Teams nebo editace Word dokumentu sdíleného ve OneDrive - to všechno vyžaduje přihlášení vaším uživatelským účtem. Postaru jméno a heslo, ponovu jen jméno a bezheslové přihlášení (Windows Hello, autentizační aplikace na telefonu jištěná biometrikou apod.) a pro administrátory oboje (vícefaktorové ověření). Jenže co když potřebujete, aby se něco dělo "samo" a interaktivní přihlášení pak není možné. Samo znamená, že nějaká aplikace bude potřebovat nějakou identitu (a příslušnou autorizaci) k provádění něčeho "sama". Co to může být?
- Aplikací je Azure CLI skript, který spouštíte automatizovaně třeba v CI/CD pipeline
- Aplikací je účetnictví, které vás chce přihlásit a umožnit stáhnout Excel tabulky z vašeho OneDrive účtu
- Aplikací je SAP či ServiceNow, které využívají jednotného přihlášení přes AAD
- Aplikací je Azure Kubernetes Service cluster, který potřebuje automaticky měnit počty VM, nastavovat Azure Load Balancer nebo vytvářet a připojovat disky
- Aplikací je Azure Databricks nebo Azure ML Workspace, které potřebují vytvářet a bourat virtuální mašiny
- Aplikací je váš kód, který potřebuje přistupovat k Azure Key Vault, aby si vyzvedl certifikát
- Aplikací je váš kód, který se chce přihlásit do Azure SQL databáze
- Aplikací je Outlook, Word nebo Dynamics

U těchto aplikací musíme odlišit:
- Aplikace chce jen možnost ověřit interaktivně uživatele v AAD a všechna ostatní oprávnění bude řešit jménem uživatele (s jeho souhlasem nebo souhlasem jeho administrátora) - tomu se typicky říká aplikační registrace a ne service principal. Aplikace potřebuje mít nějaké heslo či certifikát, aby mohla zabezpečeně komunikovat s AAD (vyzvedávat si token například).
- Aplikace nebude vystupovat jménem uživatele, chce mít vlastní identitu a přímo k ní namapovaná práva. Tomu se pak typicky říká Service Principal a to je to, co nás teď primárně zajímá.

V moderním světě aplikace nikdy nevyužívá a nevidí heslo uživatele! Ostatně u password-less situací ani žádné heslo nemusí existovat. V zásadě pro aplikace pro koncové uživatele je vhodné co nejvíce používat delegovaná oprávnění jménem uživatele (uživatel se přihlásí v AAD a dá aplikaci souhlas s přístupem k nějakým zdrojům), nicméně pro nějaké hromadné dávkové zpracování na pozadí nebo právě pro příklady týkající se Azure samotného je service principal nutnost.

A tady je ten problém. Service Principal je účet, který má jméno (client_id) a heslo (client_secret) či certifikát. Heslo se dá "vykecat" a proto je důležité mít tyto účty pod kontrolou z pohledu přiřazení práv a rotace hesel. Účet Service Principal může být zneužit, takže bezpečnostní governance je tady rozhodně na místě.

# Enterprise IT z pohledu těchto účtů
Identita je nový perimetr. Je to jeden z nejdůležitějších bezpečnostních nástrojů, který dnes máte. Historický akcent na filtrování paketů, síťové oddělení a firewalling je dnes přesouván na identitu, autorizaci a zero-trust model (neznamená to samozřejmě, že síťová bezpečnost už nedává žádný smysl, to určitě neplatí, ale není už primárním řešením bezpečnosti). Máme tu tedy registrace aplikací, které chtějí ověřovat identitu uživatelů a získávat od nich (nebo od administrátora) souhlas k využívání nějakých zdrojů (delegovaná oprávnění) a to určitě chceme rozumně řídit. Ale ještě víc pozornosti určitě potřebují aplikační identity, které samy o sobě získávají nějaká oprávnění - tedy service principal. Určitě budu chtít řídit životní cyklus, nenechávat živé ale už nepoužívané účty v systému. Rozhodně chci rotovat hesla či certifikáty, abych snížil dopady jejich případného úniku. Nepochybně budu velmi citlivý na jakákoli práva směrem k autentizačnímu systému (nastavování věcí v AAD), přístupu k osobním datům (emaily) a to zejména možnosti "ukrást identitu" pro šmejdění v asociovaných aplikacích nebo rybaření zevnitř.

Zkrátka nesprávně ošetřený Service Principal může znamenat velké riziko a proto bude všechno podléhat schválení bezpečnostního týmu. Výsledkem bude, že se z toho obvykle  stane proces s nějakým ticketem, který v lepším případě trvá dny, v horším klidně i měsíc. Pokud takový účet potřebujete jen pro automatizaci Azure infrastruktury, vytvoření AKS, Databricks, Azure ML a jiných platforem, je to z pohledu agility nepřijatelné. A co hesla do datových platforem? Uděláte správnou věc a budete pro vaše Azure SQL, Azure Database for MySQL nebo PostgreSQL či pro Azure Blob Storage používat AAD, i když čekáte na schválení každého účtu měsíc? Nebo se na to vykašlete a pojedete tradičním heslem nebo klíčem a na centárlní identitní systém se zanevřete?

Bojím se, že ztráta agility vede správce a programátory v Azure k chování, které bych z bezpečnostního hlediska nepreferoval:
- Používání méně bezpečných obyčejných hesel a klíčů namísto AAD (porušení konceptu jednoho identitního systému a roztříštěnost secrets)
- Používání jednoho Service Principal na víc věcí a přiřazení velkých oprávnění tomuto účtu (porušení least privilege a konkrétního účelu účtu)

# Úkrok stranou - separátní tenant, v čem je to dobré a kde je problém
Velmi častým řešením je minimálně pro vývoj vytvořit separátní AAD tenant s méně přísnými pravidly s tím, že v něm jsou jako guest (shadow account) přizvány lidské účty z hlavního tenantu. Přihlašovat se tedy můžu stále stejným účtem, ale v tomto tenantu je snadnější vytvořit service principal nebo aplikační registraci. Tím, že tyto přidané objekty mají platnost pouze v tomto tenantu (nefungují v tom hlavním) a v tomto tenantu nejsou ani produkční systémy, ani Office365, ani aplikace typu SAP či ServiceNow, nepředstavuje případné zneužití takové riziko.

Pokud je tento tenant určen pouze pro vývoj, připadá mi to jako dobré řešení. Nejde totiž jen o Azure jako takový, ale i o vývoj aplikací - ty určitě chci integrovat na AAD, takže si potřebuji zkoušet, vytvářet testovací uživatele a tak podobně - mít na to tenant dává velký smysl.

O něco méně jsem přesvědčen, že i produčkní Azure by měl mít separátní tenant. Mnoho organizací dává administrátorům "admin" účty, tedy ti mají dvojí identitu - uživatelskou a administrátorskou. Typickým argumentem bývá, že uživatel by měl pracovat s nejnižším možným oprávněním a k tomu mít silnější zabezpečení vyšších oprávnění - tedy odlišovat svou "user a root" podobu. Nejsem si jist, že to je v moderní době nutné, protože:
- Conditional access umožňuje mít různou úroveň přísnosti pro různé situace a aplikace. Každá aplikace (email, Teams, SAP, Dynamics365, Azure portál, AWS, Azure CLI, Azure DevOps, ...) může mít jinou, každá lokalita a prostředek připojení jinou, každá míra rizika přihlášení jinou apod. 
- Občasné privilegované přístupy by měl řešit Privileged Identity Management a ne separátní účty. Berme to jako sudo pro širší kontext identity.

Výhody jednotné identity z pohledu skutečného chování člověka (ML algoritmy), větší přehlednosti, lepší provázanosti na další politiky (například stav zařízení s Intune) řekl bych výrazně převyšují potenciální nevýhody a rizika, která jsou s modernějšími principy řešitelná bez dvojí identity.

Sumář za mě - separátní tenant pro vývojáře smysl dává, separátní tenant pro Azure produkci myslím si dnes už ne. Tam bych zůstával u toho "hlavního", tedy "skutečného". Problém zdlouhavého procesu získání Service Principal tedy odpadl u vývoje, ale v produkci je tady pořád a i tam je agilita potřeba a složitost správy může vést k častějším chybám a tím spojeným provozním i bezpečnostním komplikacím.

Pokud necháme stranou problém aplikační registrace (kde v produkci na to dává smysl proces přežít) - jak řešit účty pro zdroje v Azure aniž bychom museli trpět schvalovacím kolečkem, riskovali a měli starost s nepořádkem? Podívejme se na Managed Identity.

# Managed Identity jako cesta k menší potřebě získávat Service Principal
Hlavní finta spočívá v konceptu Managed Identity v Azure. Technicky vzato je to speciální případ Service Principal, který se ale v některých ohledech chová jinak.

První rozdíl - tento účet nemá a nemůže mít heslo ani certifikát! Není co vykecat. Jediné jak se dá takový účet použít je provozováním něčeho v Azure. Kód uvnitř Azure (například ve VM, kontejneru, App Service) může přes lokální API (tzn. neroutovatelné, nejde po síti, servíruje ho přímo hostitelská platforma lokálního serveru) získat token. Ne heslo, ale časově omezený token. Ověřením tedy není heslo, ale fakt, že tento kód běží uvnitř Azure a uvnitř konkrétního resource, který má tuto identitu namapovanou (k tomu se ještě dostaneme). Odpadá tedy problém jak kódu heslo předávat, protože žádné není (těm co správně říkáte, že na to je přece Key Vault musím namítnout, že i do Key Vault se musím ověřit - místo předávání klíčků od dvěří složitě svému Airbnb nájemci mu je schovám do trezoru...jenže teď mu musím předat klíčky od trezoru a problém jsme vlastně nevyřešili). Myslím, že tohle je výrazně bezpečnější. Pokud by nějaký útočník získal token, má časově omezenou platnost, takže nemůže potichu týdny pracovat na infiltraci mimo tento zdroj (z jiné VM nebo z jiné lokality). Jediná cesta je zmocnit se samotného kódu a škodit přímo z tohoto zdroje, což je obtížnější (vytípnout heslo a pak si jet ze své workstation je jednodušší). No i takový případ, který je určitě noční můrou, má v novém světě prevenci (nemluvě o schopnosti detekovat situaci - to je na jindy). Jednak životní cyklus identity vede na skutečný least privilege, k tomu zachvilku. Kontejnerový svět má další dvě krásné vlastnosti - aplikaci udělám stateless a file system read only, takže útočník si nepřinese svoje nástroje a navíc s každou verzí a opravou zahazuji ty staré, takže i pokud by si útočník mohl něco uložit, tak to tam za chvilku stejnak nebude. Mimochodem zdá se mi, že velké riziko se teď přesouvá právě do výrobny aplikací - do vaší CI/CD pipeline, protože to je pro útočníka perfektní místo pro podsunutí nějakých ošklivostí...ale to je zas na jindy (v kostce - Microsoft portfolio CI/CD nástrojů na to dost myslí, takže než si řeknete, že všechno přece poskládáte sami z open source, doporučuji problematiku bezpečnost zařadit jako prioritu - a ne, tím, že to dám do vnitřní sítě jsem to nevyřešil).

Druhý zásadní rozdíl je životní cyklus. Identity sice najdete v Enteprise Applications sekci v AAD, ale životní cyklus je řízen v Azure. Existují dva základní typy. SystemManaged identita je přímo spojena s konkrétním zdrojem. Uděláte třeba VM a tato získá svou vlastní identitu (s nulovou autorizací). Takže pokud chcete z této VM přistupovat do Azure SQL, přidáte identitu toho VM příslušnou roli. Jakmile VM smažete, zlikviduje se i tato identita, takže se vám všechno samo čistí. Občas můžete potřebovat jednu identitu sdílet ve víc zdrojích (třeba ve dvou VM) nebo mít identit víc (odlišné pro různé služby - jednu na přístup do Key Vault, jinou na přihlášení do storage). Pak použijete UserManaged. Tu si založíte jako resource v Azure, takže jasně vidíte kde je a se smazáním třeba resource group smažete i ji. Obě řešení vedou k pořádku, protože si nemusíte nikde složitě evidovat co k čemu patří. Jednoduchost vytváření a mazání také vede na správné chování - používání speciálních identit pro každou činnost místo snahy zúročit měsíční čekání na service principal tím, že bude kontributorem celé subskripce a používán všude dokola.

Třetí rozdíl je v možnostech autorizace. Managed Identity je pouze pro Azure zdroje - nelze ji přiřadit práva do jiných aplikací typu Office365, Dynamics365, SAP, ServiceNow apod. To myslím bezpečáky "velkého tenantu" oprávněně uklidní, protože potenciál zneužití tím ještě  klesá.

# Na co lze použít Managed Identity
Seznam služeb připravených na tento model se neustále rozrůstá. Aktuálně je to zhruba takhle:
- Do vašeho kódu si můžete načíst ve VM, App Service, AKS Podu, Function, Logic App
- AKS nově podporuje tyto identity pro své fungování (tzn. ovládání sítě, disků, monitoringu, ...), takže na AKS už od minulého týdne nepotřebujete service principal
- Datové služby Azure SQL, Azure Database for MySQL a PostgreSQL i Azure Blob podporují přihlášení přes AAD, takže váš kód může použít Managed Identity pro přihlášení k nim
- Automatizační skripty ve VM můžete autentizovat přes Managed Identity - funguje s Azure CLI, PowerShell, Terraform, Ansible
- Azure DataFactory (zatím pouze SystemManaged)
- Azure API Management (SystemManaged v GA, UserManaged v preview)
- Azure Container Instances (v Preview)
- Messaging služby Event Hub a Service Bus podporují AAD ověřování, váš kod tedy může použít Managed Identity
- Vyzvedávání tajností z Key Vault

Jak vidno, některé služby služby ještě na seznamu nejsou (DataBricks, CosmosDB), ale i tak je seznam už dost dlouhý a bude se určitě rozšiřovat. 


Za mne - určitě prozkoumejte Managed Identity a přejděte na ně všude kde to jde. Je to rozhodně bezpečnější, než běžný Service Principal a vaše agilita nebude trpět ani při používání "velkého" tenantu. Máte si také pomoci separátním tenantem? Pro vývoj mi to smysl dává, ale zůstal bych jen tam. Všechno ostatní bych řešil jednotnou identitou a nasadil moderní prostředky její ochrany (Conditional Access, Privileged Identity Management, ...) místo modelu dvojí identity a s tím spojená rizika (včetně ztížené korelační vizibility pro ML algoritmy a SIEM nebo znesnadnění svázaní dalších politik typu Intune). Máte jiný názor? Dejte mi vědět na LinkedIn!