---
layout: post
published: true
title: Microsoft Dev Box - virtuální pecko pro vývojáře a kdy použít vs. GitHub Codespaces, Windows365 nebo Azure Virtual Desktop
tags:
- Compute
---
Počítače vývojářů, časté téma hovorů v IT. Tady je pár opakujících se situací:
- Projekty se nafukují a nafukují, víc řádků, víc mikroslužeb a pořád chtějí více CPU, větší a rychlejší disky, víc paměti.
- Od nástupu developera do získání produktivního prostředí uběhne hodně času (objednání železa - a to v dnešní době může trvat opravdu dlouho, instalace v IT, rozchození prostředí).
- Některé věci jsou v jednom OS nesnášenlivé a vývojáři nakonec tráví velké množství času udržováním knihoven a funkčního prostředí zejména, pokud pracují na víc komponentách/projektech, kde každý má jiné požadavky.
- Noooo ale my tady jedeme ještě něco v on-prem, náš Git, CI/CD systém, do Azure leda přes VPN - jak to bezpečně připojit odkudkoli, když ti vývojáři nechtějí moc fyzicky chodit do práce?
- BYOD je sice výborný nápad, ale v našem striktně regulovaném sektoru nám to při auditech brutálně zavaří.
- Musíme řešit spoustu bezpečnostních a provozních problému - když někdo ztratí zařízení bojíme se o citlivá data nebo se mu rozbije a je sice skvělé, že máme od Dellu nějakou rychlou výmenu železa, ale ten vývojář stejně musí k nám do IT na obnovení dat a reinstalaci... a takový vlak z Brna do Prahy je zážitek.
- V mém městě nejsou lidi a po COVIDu už je práce z domova tak normální, že nabíráme i mezinárodní tým - to máme posílat notebooky poštou bůh ví kam?

Dva hlavní přístupy k řešení této situace z dílny Microsoft jsou GitHub Codespaces a Microsoft Dev Box, ale podobných výsledků dosáhnete i s Azure Virtual Desktop, Windows365 nebo s dalšími compute službami v Azure. Proveďme základní srovnání a pak se vrhneme do Dev Box (a příště do Codespaces).
- **GitHub Codespaces** jsou pro mě jednoznačně nejvíc sexy řešení, které s sebou nese i kompletní vystavení celého prostředí nesmírně rychle, dynamicky, plně automatizovaně a moderně. Navíc nestojí na nějakém přenášení obrázků, IDE běží na mém počítači (ať už jako Visual Studio Code aplikace nebo jako kód v browseru). Tohle je boží pro vývoj mikroslužeb, API i webů a obecně věcí, které jsou Linuxově zaměřené a celé takové prostředí umí běžet v kontejneru (na tom to je celé postaveno). Určitě to tedy není univerzální řešení - nebudeme mít grafické tlusté aplikace, nejrůznější nástroje pro práci s daty, libovolná IDE, vývojové nástroje, administrační tooly, lokální namapované fileshare. Navíc v současné době se Codespaces neumí integrovat do vnitřní sítě (ale pracuje se na tom), takže na vývoj klasických zabetonovaných on-prem věcí to není optimální. Na druhou stranu nepotřebujete nad tím žádné další licence a platí se dle spotřeby (času běžícího prostředí).
- **Microsoft Dev Box** je tenká nadstavba nad Windows365, která vám přináší plně virtualizovaný Windows 11 stroj včetně věcí jako je WSL pro Linux vývoj, libovolné aplikace ať už je to velké Visual Studio, IntelliJ, Eclipse, Office sada, SQL Management Studio, Oracle věcičky nebo cokoli dalšího, s podporou vývoje grafických aplikací a tak podobně. Pro enterprise firmy další dobré zprávy - integrované s joinem do domény (buď Azure AD nebo hybrid join), spravované s MEM (ex-Intune) a integrované do VNETu a síťového prostředí včetně toho hybridního. Je to tedy abych tak řekl plná palba - uvnitř samozřejmě můžete použít WSL a pracovat dál třeba s Devcontainery (technologie, která je pod kapotou Codespaces). Pro používání potřebujete licence (takové ty F3/E3 a tak), takže to dává smysl hlavně, když je ve firmě stejně máte. Spotřeba zdrojů se platí za čas.
- **Windows365** je pod kapotou Dev Boxů, ale neumožňuje tak pěknou samoobslužnost (aby si vývojář sám vytvořil pecko a řídil si jeho životní cyklus), má slabší možnosti customizace OS a nemá k dispozici silné vývojářské mašiny (pro Dev Box se plánuje např. 32-core stroj, pro Windows365 ne). Hlavní rozdíl je ale v obchodním modelu - tady platíte měsíčně za uživatele bez ohledu na to jak moc službu využívá, ale v DevBox platíte po hodinách. To se někdy vyplatí, někdy ne.
- **Azure Virtual Desktop** je kompletní VDI řešení, u kterého se ovšem o stroje musíte starat sami. Takže ano - je možné customizovat image, dát je do MEM správy, zařadit do domény, používat různé velikosti, ale to všechno je na vás. Pokud máte AVD pro svoje uživatele tak jako tak, nebude to problém - ale pokud vám jde jen o vývojáře, možná bude lepší něco o co se ani zdaleka tak starat nemusíte.
- **Další compute služby** jsou určitě taky varianta - nahodit VM v Azure a starat se o něj samozřejmě můžete, ale bude na vás už nejen správa mašin, ale i řízení bezpečnost a přihlašování (třeba rozjet MFA bude netriviální) a řada dalších úkonů.

# Microsoft Dev Box
Pro účely opakovatelného dema jsem vše automatizoval do jedné Bicep šablony zde: [https://github.com/tkubica12/azure-workshops/tree/main/d-devbox](https://github.com/tkubica12/azure-workshops/tree/main/d-devbox).

Na vrcholku se mi nasadí Dev Center.

[![](/images/2022/2022-09-05-13-48-29.png){:class="img-fluid"}](/images/2022/2022-09-05-13-48-29.png)

V něm je přidána síťová integrace.

[![](/images/2022/2022-09-05-13-51-05.png){:class="img-fluid"}](/images/2022/2022-09-05-13-51-05.png)

Kromě fyzické sítě je součástí nastavení také způsob join do domény - v mém případě krásně moderně s Azure Active Directory přímo, ale můžete použít i hybrid join (pak je vyžadován síťový přístup do AD a joinovací kredence).

[![](/images/2022/2022-09-05-14-10-03.png){:class="img-fluid"}](/images/2022/2022-09-05-14-10-03.png)

Definoval jsem dva devboxy - řekněme typy vývojářských strojů. Ty mohou mít různé image nebo velikosti strojů. Třeba jeden pro vývojáře a jiný pro DB adminy.

[![](/images/2022/2022-09-05-13-52-22.png){:class="img-fluid"}](/images/2022/2022-09-05-13-52-22.png)

Řízení práv a možností určovat kdo kde co může vytvořit se děje na úrovni projektů.

[![](/images/2022/2022-09-05-13-53-57.png){:class="img-fluid"}](/images/2022/2022-09-05-13-53-57.png)

Určím, které typy strojů jsou v projektu k dispozici a také přes RBAC řídím kdo si může stroj vytvořit. 

[![](/images/2022/2022-09-05-13-55-19.png){:class="img-fluid"}](/images/2022/2022-09-05-13-55-19.png)

Pak už se jako vývojář připojím na specializovaný portál [https://devbox.microsoft.com](https://devbox.microsoft.com) a založím si stroj dle svých preferencí.

[![](/images/2022/2022-09-05-10-46-28.png){:class="img-fluid"}](/images/2022/2022-09-05-10-46-28.png)

A je to, dva už mi běží.

[![](/images/2022/2022-09-05-10-46-52.png){:class="img-fluid"}](/images/2022/2022-09-05-10-46-52.png)

Buď z RDP klienta nebo přímo z browseru se na svůj stroj dostanu a ano, skutečně je v mé vnitnří síti!

[![](/images/2022/2022-09-05-10-45-48.png){:class="img-fluid"}](/images/2022/2022-09-05-10-45-48.png)

To ostatně vidím i přímo ve svém VNETu.

[![](/images/2022/2022-09-05-14-00-44.png){:class="img-fluid"}](/images/2022/2022-09-05-14-00-44.png)

Jak už padlo Dev Box pod kapotou využívá Windows365 a je tak vlastně jeho nadstavbou a specializovanou variantou pro vývojáře. Dokonce stroje vidím v [https://windows365.microsoft.com](https://windows365.microsoft.com) konzoli.

[![](/images/2022/2022-09-05-10-47-11.png){:class="img-fluid"}](/images/2022/2022-09-05-10-47-11.png)

Stroje jsou spravovány přes portfolio Microsoft365. Takhle je vidíme v AAD jako AAD joined zařízení.

[![](/images/2022/2022-09-05-10-49-37.png){:class="img-fluid"}](/images/2022/2022-09-05-10-49-37.png)

Takhle v Microsoft Endpoint Manager (Intune).

[![](/images/2022/2022-09-05-14-06-16.png){:class="img-fluid"}](/images/2022/2022-09-05-14-06-16.png)

Odtud pak lze samozřejmě řídit všechny další bezpečnostní aspekty co se na stroji smí, co ne a nalodit Defender for Endpoints a tak podobně.


Microsoft Dev Box považuji za pokračování VDI pro vývojáře - něco co existuje mnoho let, v některých situacích na to vývojáři nadávají (přenášení obrázků na pomalé lince není ideální), ale jindy jsou moc rádi, že něco takového existuje a dostanou se tam kam potřebují (zejména pro dočasnou práci a kontraktory je to výborná věc). Předpřipravené řešení odstraňuje řadu bolístek - je krásně spravováno, obsloužíte se sami bez ticketů a emailů, nemusíte se patlat s hromadou infrastruktury okolo, rovnou v tom máte všechny enterprise vychytávky typu domain join a moderní správu přes MEM a přitom to vývojáře nijak nebolí. Codespaces zase pro mě mají úžasnou hodnotu v tom, že s sebou nesou nádherně automatizované prostředí pro mikroslužby naintegrované přímo na repozitář a kontejnerové technologie (i prvotní vytvoření stroje je na pár minut, spouštění vypnutého trvá do minuty). Skvěle se s tím pracuje a IDE běžící u mě je zásadní výhoda.

Nesrovnávejte tedy jen náklady za nákup notebooku, provoz obyčejné VM v Azure a tyto dvě služby - ty samozřejmě vyjdou dráž. To kouzlo je v tom, že jste okamžitě produktivní, je to celé velmi bezpečné by default. Kde začít? Za mě tam, kde máte sezónní pracovníky, externisty, vzdálené přístupy. Rozdíl mezi tady klikneš a do pár minut máš kompletní prostředí aplikace (Codespaces) nebo do 30 minut kompletní plně vybavenou vývojářskou stanici (Dev Box) vs. řetězec objednáme, přijde do IT, tam nainstalujeme, potřebuješ VPN a heslo přijde SMSkou, po měsíci co tě platíme začneš konečně něco dělat a za týden končí stáž a dostaneme zpět drahý notebook s nadrobenou tatrankou v klávesnici, je podle mě dost zásadní. Zkuste si to!
