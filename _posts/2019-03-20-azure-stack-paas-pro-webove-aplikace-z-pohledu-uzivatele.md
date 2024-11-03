---
layout: post
title: 'Azure Stack: platformní služby pro webové aplikace s Application Services z pohledu uživatele'
tags:
- AppService
- AzureStack
---
V minulém díle jsme si ukázali jak vypadá platformní služba Application Services v Azure Stack z pohledu jeho administrátora. Co přináší tento PaaS uživatelům Azure Stacku, tedy vašim aplikačním týmům, provozu či interním zákazníkům?

# Založení prostředí pro webovou aplikaci
Nejprve si vytvořme prostředí pro naší webovou aplikaci.

![](/images/2019/2019-03-12-11-12-08.png){:class="img-fluid"}

Zakládáme novou webovou aplikaci. Tu musíme hostovat na nějakých zdrojích, tedy servisním plánu. Já už jeden založený mám, ale podívejme se, z čeho se tam vybírá.

![](/images/2019/2019-03-12-11-13-36.png){:class="img-fluid"}

Můj Azure Stack administrátor mi nabízí některé varianty ve sdíleném režimu. To pro mě znamená, že moje aplikace poběží sice izolovaně od ostatních týmů nebo interních zákazníků, ale bude sdílet stejné základní zdroje (servisní plán). Nicméně Azure Stack administrátor mi nabízí variantu Free (tam pro mě určitě připravil nějaká zásadní omezení ve výkonu apod.) a také režim Shared, který už po mě chce zaplatit cenou 100 Kč měsíčně, ale asi tam budu mít víc možností, třeba víc paměti pro mou aplikaci.

![](/images/2019/2019-03-12-11-16-10.png){:class="img-fluid"}

Mám tady také dražší dedikované varianty. V těch bude podkladové VM pro mě dedikované a nesdílím tak výkon s někým jiným.

![](/images/2019/2019-03-12-11-17-00.png){:class="img-fluid"}

Během chviličky je moje prostředí plně připraveno a mám výchozí URL, na které moje aplikace bude.

![](/images/2019/2019-03-12-11-18-42.png){:class="img-fluid"}

Aplikace běží, ale není v ní žádný můj kód, takže je prázdná.

![](/images/2019/2019-03-12-11-19-16.png){:class="img-fluid"}

# Doručení aplikačního kódu
Jak do aplikace dostaneme váš kód? Jednou z možností pro klasickou situaci je připojit se na speciální FTP, z kterého platforma sama nahrané soubory nainstaluje do prostředí.

![](/images/2019/2019-03-12-11-20-49.png){:class="img-fluid"}

![](/images/2019/2019-03-12-11-21-12.png){:class="img-fluid"}

Já budu chtít použít nějakou modernější techniku. Proto půjdu do části Deployment Options a podívám se, co je tam k dispozici.

![](/images/2019/2019-03-12-11-22-19.png){:class="img-fluid"}

Azure Stack administrátor pro mě nezpřístupnil úplně všechny možnosti (proto jsou zašedlé), ale pojďme si o nich něco povědět.

* Možnosti vhodné pro netechnické lidi - OneDrive, DropBox. Tato varianta bude sledovat soubory v těchto úložištích a jakmile se tam objeví něco nového automaticky provede nasazení aplikace. Pro instalaci vám tedy stačí myší přetáhnout soubory do svého OneDrive a to je všechno. Tato varianta není nijak profesionální, ale umožňuje doslova každému přidat třeba nový obrázek nebo kód, který mu poskytne vývojář.
* Jednorázový git clone. Tato varianta (External Repository) funguje s jakýmkoli version control systémem s podporou Git protokolu. Operace, kterou provádí je jednoduchý clone. V okamžiku kdy to odklepnete, stáhne se všechno z Gitu a nasadí.
* Lokální git. V této možnosti bude u vaší appky dostupný její vlastní git repozitář. Svoje zdrojové kódy upravíte a provedete git push, čímž je nahrajete do služby a ta následně provede jejich deployment.
* GitOps a integrace na GitHub nebo BitBucket. Tato varianta nastaví obousměrnou komunikaci, takže v okamžiku kdy se ve vámi zvolené větvi kódu objeví nějaká změna (nový commit), platforma to sama pozná a provede nasazení této verze.
* Nasazování z Visual Studio. K tomuto systému samozřejmě existuje API a toho využívá například Visual Studio, které přes technologii WebDeploy může natlačit kód do aplikace rovnou z vývojového nástroje.
* Integrace do CI/CD pipeline, například Azure DevOps. Profesionální řešení bude integrovat nasazování do vašeho CI/CD nástroje. Jak to udělat s cloudovou službou Azure DevOps (možná znáte pod starším názvem VSTS) se podíváme v samostatném dílu.

Já zvolím variantu prostého naklonování z Gitu.

![](/images/2019/2019-03-12-11-29-18.png){:class="img-fluid"}

Po chvilce moje aplikace běží.

![](/images/2019/2019-03-12-13-20-10.png){:class="img-fluid"}

# Škálování
Aktuálně moje aplikace běží v dedikovaném tieru na mnou vybrané velikosti a počet worker nodů v mém servisním plánu je jeden. Co když potřebuji svůj výkon zvýšit, protože o aplikaci je zájem? Ideální je scale-out metoda, tedy zvýšení počtu worker nodů. To najdeme v nastavení a je tam šoupátko, které mi umožní říct si víc nodů, pokud je dal administrátor Azure Stacku k dispozici.

![](/images/2019/2019-03-12-13-24-59.png){:class="img-fluid"}

Co se stane pokud kliknete na save? V Azure Stack má administrátor přednastartované worker nody, které nejsou ještě nikomu přiřazené. Pokud si je přes zmíněné šoupátko koupíte, Azure Stack vám je rychle alokuje (takže čekáte jen chviličku), nahodí na nich vaše aplikace a začne na ně balancovat provoz.

Pokud jste zjistili, že vaše aplikace naráží na limity třeba paměti, možná budete potřebovat scale-up, tedy zvednout velikost worker nodu (pokud je vám Azure Stack administrátor nabízí). Stránka je stejná, jako když jste servisní plán zakládali - svoje rozhodnutí tedy můžete změnit.

![](/images/2019/2019-03-12-13-33-29.png){:class="img-fluid"}

# Nasazování přes deployment sloty
Máte produkční webovou aplikaci a připravujete novou verzi. Možná ji chcete nejprve vidět běžet v pilotním provozu a poslat do produkce až se rozhodnete. Mohli bychom udělat druhou WebApp a v ní běžet novou verzi, ale platforma nabízí pro tento scénář pohodlnější řešení s mnoha funkcemi navíc - deployment sloty. 

Přidejme si ke své produkční aplikaci deployment slot, který nazvu staging.

![](/images/2019/2019-03-12-13-37-27.png){:class="img-fluid"}

![](/images/2019/2019-03-12-13-38-39.png){:class="img-fluid"}

Pokud na slot klikneme, uvidíme, že to je vlastně další WebApp na své vlastní URL, ale je provázaná s tou produkční, jak za chvíli uvidíme.

![](/images/2019/2019-03-12-13-39-24.png){:class="img-fluid"}

Appka ve staging má (stejně jako ta produkční) možnost definovat různá aplikační nastavení, které si vaše aplikace čte (u .NET přes konfigurační kolekci, u ostatní jazyků přes proměnné prostředí).

![](/images/2019/2019-03-12-13-41-09.png){:class="img-fluid"}

Typická nastavení budou connection stringy do databází, klíče, konfigurační parametry. Všimněte si, že u nastavení si můžete vybrat zda je svázané s aplikací nebo slotem. Jak za chvilku uvidíte nasazování produkce se dá udělat tak, že sloty přehodíte - to co je ve staging bude teď produkce a naopak. Některá nastavení určitě chcete mít svázaná se slotem - například connection string do produkční databáze. Takže cokoli přistane v produkčním slotu má vždycky koukat na produkční data. Na druhou stranu můžete mít k v2 aplikaci ve staging slotu nějaké nastavení, které je v produkci jiné a v okamžiku, kdy v2 překlopíte do produkce tak chcete, aby toto nastavení bylo překlopeno taky. Tak tedy toto nastavení bude vztažené k aplikaci, ne slotu.

![](/images/2019/2019-03-12-13-46-59.png){:class="img-fluid"}

Jak tedy nasadíte aplikaci do produkce? Nová verze běží ve staging slotu, produkce v hlavním slotu. Pojďme je tedy prohodit.

![](/images/2019/2019-03-12-13-49-49.png){:class="img-fluid"}

![](/images/2019/2019-03-12-13-50-05.png){:class="img-fluid"}

Co se stane? Azure Stack prohodí routing na load balanceru a tím prohodí vaše URL (stagin za produkční a produkční za staging). Aby si aplikace mohla načíst změněné parametry a připojit se do databáze, Azure Stack ji z těchto důvodů restartuje. Podstatné ale je, že jediný výpadek je způsobený restartem aplikace - nic se nikam neinstaluje, žádná další zdržení váš nečekají. Ale co když, říkáte si, aplikace ze staging nenaběhe, protože po načtení nastavení z produkčního slotu spadne na neošetřenou chybu? Buď rychle uděláte stejnou operaci znova (bývalá produkce je teď ve staging slotu, takže to můžeme zase prohodit) nebo použijete funkce Swap with preview (v tom případě se nejdřív aplikuje produkční nastavení na staging, takže si můžete zkontrolovat, že vám to naběhlo a samotné překlopení uživatelů je na další kliknutí, když máte jistotu).

Někdy jsou změny mezi verzemi vaší aplikace malé a není problém, když někdo bude používat v1 a někdo v2. V ten okamžik nemusíte nasazovat novou verzi najdenou, ale dá se říct, že zatím chcete jen třeba 5% provozu posílat do staging a sledovat, jak se to uživatleům chová. Pak přitočit, ještě přitočit a nakonec přejít uplně. Toto opatrné nasazování do produkce je v některých případech ideální scénář.

![](/images/2019/2019-03-12-14-04-04.png){:class="img-fluid"}

# Vlastní doména a certifikát
Výchozí URL aplikace je velmi příjemná pro testování a rychlý začátek, ale produkční prostředí určitě budete chtít nastavit vlastní doménu a certifikát. Funguje to prakticky stejně jako v Azure. Své doménové jméno musíte do platformy přidat.

![](/images/2019/2019-03-12-14-09-18.png){:class="img-fluid"}

Vaše doménové jméno musíte ověřit a také nastavit externí DNS tam, kde svoje jméno spravujete. Může to být přes CNAME nebo A záznam.

![](/images/2019/2019-03-12-14-10-48.png){:class="img-fluid"}

Následně přidejte SSL.

![](/images/2019/2019-03-12-14-12-48.png){:class="img-fluid"}

# Zálohování
Webovou aplikaci je ideální nasazovat z version control a ten mít zálohovaný. Nicméně ne vždy to tak je, možná máte hromadu statického obsahu co ve version control není, zkrátka někdy můžete chtít zálohovat obsah vaší WebApp. To Azure Stack umožňuje.

![](/images/2019/2019-03-12-14-14-58.png){:class="img-fluid"}

Zálohování bude probíhat do Storage Account (Blob storage). Můžete zálohu posílat do Azure třeba do geo-redundantní storage (takže vaše data jsou například ve třech synchronních kopiích v West Europe a dalších 3 kopiích v North Europe) nebo ji namířit na Storage Account ve stejném či jiném Azure Stack.

![](/images/2019/2019-03-12-14-16-29.png){:class="img-fluid"}

# Autentizace
Autentizaci můžete pochopitelně řešit vaším aplikačním kódem a je to tak v pořádku. Platfroma vám s tím ale může pomoci. Pokud chcete ověřovat uživatele přes Microsoft AAD (firemní identitu), Google, Facebook apod., stačí v aplikaci mít login tlačítko pro jednotlivé scénáře a přesměrovat uživatele na Application Services (například na /.auth/login/aad), které následně zajistí autentizaci v cílené službě a vaše aplikace si může přečíst informace o přihlášeném uživateli (například v headeru nebo na URL služby, myslím že je to něco jako /.auth/me).

![](/images/2019/2019-03-12-14-22-52.png){:class="img-fluid"}

Zajímavé je, že tuto jednoduchou autentizaci můžete nasadit i bez jakékoli podpory ve vaší aplikaci. Tak například máte testovací verzi veřejné webové stránky, která žádnou autentizaci nepoužívá. Potřebujete ji ukázat v rámci firmy a to včetně připojení z mobilu přes 4G, ale nechcete, aby ji zatím viděl někdo jiný. V platformě můžete zapnout ověřování a jakýkoli uživatel, který se pokusí cokoli zobrazit, bude nejprve protažen autentizací. Aniž byste jakkoli změnili kód vaší aplikace, uvidí ji jen uživatel z interního AAD adresáře.

![](/images/2019/2019-03-12-14-23-19.png){:class="img-fluid"}

# Extensions
Microsoft i řada třetích stran nabízí připravené komponenty pro vaše webové aplikace a najdete je v sekci Extensions.

![](/images/2019/2019-03-12-14-29-35.png){:class="img-fluid"}

# Další vlastnosti a troubleshooting
Podívejme se v krátkosti na další vlastnosti platformní služby v Azure Stack.

Možná se potřebujete rychle připojit na konzoli a zjistit co se děje.

![](/images/2019/2019-03-12-14-24-48.png){:class="img-fluid"}

Třeba potřebujete pokročilejší debugging informace.

![](/images/2019/2019-03-12-14-25-25.png){:class="img-fluid"}

![](/images/2019/2019-03-12-14-25-54.png){:class="img-fluid"}

Ne že bych to doporučoval, ale pro nějakou rychlou změnu aplikace v dev prostředí se vám může hodit online editor.

![](/images/2019/2019-03-12-14-27-29.png){:class="img-fluid"}

![](/images/2019/2019-03-12-14-28-00.png){:class="img-fluid"}

Dostanete se i k diagnostickým logům a můžete si je stáhnout z FTP.

![](/images/2019/2019-03-12-14-30-11.png){:class="img-fluid"}

Pro vaše API aplikace můžete nastavovat CORS nebo přidat Open API specifikaci.

![](/images/2019/2019-03-12-14-31-00.png){:class="img-fluid"}


Takhle tedy vypadá platformní služba Application Service ve vašem Azure Stack. Ve srovnáním s tradičním světem infrastruktury a virtuální mašin vám přináší obrovské pohodlí a zabudované funkce, které dramaticky zjednodušují jejich provoz a údržbu. Vyzkoušejte si je - ať už v Azure Stack nebo v Azure.



