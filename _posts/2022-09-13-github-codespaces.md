---
layout: post
published: true
title: GitHub Codespaces - vývojářské prostředí od stroje po knihovny a kompilátor, které naběhne za 15 vteřin
tags:
- Compute
- GitHub
---
V [minulém díle](https://www.tomaskubica.cz/post/2022/microsoft-dev-box/) jsem popisoval Microsoft Dev Box jako variantu řešení některých častých potíží vývojářských notebooků. Také jsem zmiňoval, že vedle toho jsou Codespaces, které sice nejsou plnohodnotnou pracovní stanicí ve stylu pecko v cloudu, ale pro moderní vývoj jsou za mě ještě zajímavější - ale holt ne pro ty z vás, co vyvíjí tlustou appku s Windows GUI nebo potřebují grafické nástroje typu SQL Server Management Studio.

Mimochodem - mluvím sice primárně o stanicích vývojářů, ale totéž platí pro práci s ML nebo operations s Infrastructure as Code apod.

Připomeňme si ty situace zmíněné minule:

- Projekty se nafukují a nafukují, víc řádků, víc mikroslužeb a pořád chtějí více CPU, větší a rychlejší disky, víc paměti.
- Od nástupu developera do získání produktivního prostředí uběhne hodně času (objednání železa - a to v dnešní době může trvat opravdu dlouho, instalace v IT, rozchození prostředí).
- Některé věci jsou v jednom OS nesnášenlivé a vývojáři nakonec tráví velké množství času udržováním knihoven a funkčního prostředí zejména, pokud pracují na víc komponentách/projektech, kde každý má jiné požadavky.
- Noooo ale my tady jedeme ještě něco v on-prem, náš Git, CI/CD systém, do Azure leda přes VPN - jak to bezpečně připojit odkudkoli, když ti vývojáři nechtějí moc fyzicky chodit do práce?
- BYOD je sice výborný nápad, ale v našem striktně regulovaném sektoru nám to při auditech brutálně zavaří.
- Musíme řešit spoustu bezpečnostních a provozních problému - když někdo ztratí zařízení bojíme se o citlivá data nebo se mu rozbije a je sice skvělé, že máme od Dellu nějakou rychlou výmenu železa, ale ten vývojář stejně musí k nám do IT na obnovení dat a reinstalaci... a takový vlak z Brna do Prahy je zážitek.
- V mém městě nejsou lidi a po COVIDu už je práce z domova tak normální, že nabíráme i mezinárodní tým - to máme posílat notebooky poštou bůh ví kam?

Codespaces řadu těchto bodů nádherně řeší a kde opravdu excelují je ve schopnosti do doslova pár vteřin nahodit prostředí a přitom vás nenutit přenášet graficky obrázky a narážet na s tím spojená omezení (u horší linky nějaké rozčtverečkování, latence).

# Devcontainery - osvědčený život v kontejnerech i pro vaše pecko
Vezměme si třeba vývoj v Pythonu a to, že tady mnoho let vedle sebe existovala vzájemně nekompatibilní verze 2 a 3 a do toho jednotlivé knihovny a nesnášenlivost jejich verzí navzájem. Posunete verzi onoho a to má důsledky na potřebné verze něčeho jiného. A teď si vezměte, že děláte na víc projektech nebo potřebujete spustit mikroslužby kolegů u sebe a pokaždé jsou dependence jiné - a to i mezi vývojem a produkcí, takže musíte u sebe přepínat (jasně - od vývoje přes test do produkce cestuje konkrétní sada verzí, to je jasné, ale běžně potřebujete dělat na aplikaci 1.3 s dependencí 2.2 zatímco v produkci je aplikace 1.2 s dependencí 2.1 a to je v pořádku - špatně je testovat jeden kód na jiných dependencích, než jsou v produkci). OK, uděláte tedy venv - jenže to nezahrnuje verzi Pythonu. Tak zkusíte Anacondu, protože ta ano? Možná - ale co kolegové s .NET nebo Javou? Tam je všechno úplně jinak a navíc potřebujete mít s sebou i nějaké podpůrné nástroje - kompilátory, lintery a jiné další pomocníky. 

Tyto problémy při provozu aplikací přece řešíme kontejnery, ne? Proč tedy nepoužít totéž pro vývojové prostředí - proč patlat věci na svém notebooku přímo, když můžu tohle všechno zabalit do kontejneru, který se nahodí během okamžiku a žít v něm? To by bylo určitě skvělé, ale kontejner není moc pro uživatelské prostředí - jak v něm spustím Visual Studio Code a všechna jeho skvělá rozšíření? 

A teď to přijde - co kdyby Visual Studio Code dokázalo oddělit část, ve které vidíte obrazovku, reaguje na vaše vstupy, od části "serverové", ve které dochází k věcem jako je kompilace, generování kódu, ověřování syntaxe a tak podobně? A co kdyby dokonce tohle rozdělení bylo flexibilní, takže některé funkce (extensions) mohou běžet v lokálu a jiné vzdáleně a u řady z nich si můžete vybrat kde je chcete? To by mohlo zajistit, že věci nevyžadující nic speciálního od vašeho stroje a nemají tam dependenci (editor samotný, jednoduchý syntaktický pomocník) poběží u vás pro maximální pohodlí a nízkou latenci zatímco náročnější věci a ty, které mají konkrétní dependence, poběží vzdáleně (kompilace nebo nějaký sofistikovaný analyzátor kódu). A co kdyby ta lokální část byla napsaná tak, že to není klasická tlustá appka ale něco, co se dokáže spustit i přímo v browseru? Takže byste si mohli vybrat jestli tu lokální část chcete mít jako normální aplikaci nebo jen jako aplikace v okně prohlížeče (ale ani v jednom případě ne jako obrázky ze vzdáleného serveru - editor běží u vás)? To jsou Remote Containers ve Visual Studio Code.

# Připravme si devcontainer
Potřebujeme tedy specifika prostředí zabalit do formy kontejneru s tím, že Visual Studio Code se do něj připojí a umožní využívat jeho výpočetního výkonu, funkcí, knihoven, kompilací i souborového systému. Přidejme ještě další nápad - svázat to s repozitářem a předpisy pro jedno a více prostředí držet přímo v něm - u projektu. Zdrojáky vaší aplikace nebo Infrastructure as Code předpisů tak obsahují i definici vývojářské mašiny (nebo několika typů, to samozřejmě není problém). Není to nutné, ale dává to smysl - předpisy dáme do adresáře .devcontainer (případně uvnitř něj do adresářů pro různé typy "strojů").

Vytvořím adresář a přes command (CTRL + SHIFT + P) spustím průvodce vytvoření devcontaineru.

[![](/images/2022/2022-09-12-08-09-24.png){:class="img-fluid"}](/images/2022/2022-09-12-08-09-24.png)

Microsoft pro mě připravil dost hotových prostředí, takže nemusím všechno vymýšlet sám a starat se o to. 

[![](/images/2022/2022-09-12-08-10-24.png){:class="img-fluid"}](/images/2022/2022-09-12-08-10-24.png)

Já si připravuji takovou trochu opsáckou stanici, takže vyberu Ubuntu kontejner.

[![](/images/2022/2022-09-12-08-10-56.png){:class="img-fluid"}](/images/2022/2022-09-12-08-10-56.png)

Co to znamená? Jde o base image připravený Microsoftem - ale můžu si samozřejmě přinést i svůj startovací bod. Další skvělá zpráva je, že jsou pro mě připraveny další služby, které do kontejneru můžu dostat jednoduše vybráním - nemusím je psát do Dockerfile, už je to pro mě připraveno. V mém případě k základnímu image chci ještě Azure CLI, GitHub CLI, Terraform a Kubectl.

[![](/images/2022/2022-09-12-08-14-14.png){:class="img-fluid"}](/images/2022/2022-09-12-08-14-14.png)

Tady je vygenerovaný devcontainer.json. Obsahuje návod jak kontejner vyrobit (defacto odkaz na Dockerfile - na ten mrknem za chvilku), přidané features a možnost spouštění nějakých skriptů po nahození kontejneru případně trvalé forwardování portů (o tom taky později - dost důležité).

```json
// For format details, see https://aka.ms/devcontainer.json. For config options, see the README at:
// https://github.com/microsoft/vscode-dev-containers/tree/v0.245.2/containers/ubuntu
{
	"name": "Ubuntu",
	"build": {
		"dockerfile": "Dockerfile",
		// Update 'VARIANT' to pick an Ubuntu version: jammy / ubuntu-22.04, focal / ubuntu-20.04, bionic /ubuntu-18.04
		// Use ubuntu-22.04 or ubuntu-18.04 on local arm64/Apple Silicon.
		"args": { "VARIANT": "ubuntu-22.04" }
	},

	// Use 'forwardPorts' to make a list of ports inside the container available locally.
	// "forwardPorts": [],

	// Use 'postCreateCommand' to run commands after the container is created.
	// "postCreateCommand": "uname -a",

	// Comment out to connect as root instead. More info: https://aka.ms/vscode-remote/containers/non-root.
	"remoteUser": "vscode",
	"features": {
		"kubectl-helm-minikube": "latest",
		"terraform": "latest",
		"github-cli": "latest",
		"azure-cli": "latest"
	}
}
```

Dockerfile vypadá takhle.

```
# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.245.2/containers/ubuntu/.devcontainer/base.Dockerfile

# [Choice] Ubuntu version (use ubuntu-22.04 or ubuntu-18.04 on local arm64/Apple Silicon): ubuntu-22.04, ubuntu-20.04, ubuntu-18.04
ARG VARIANT="jammy"
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
```

Rozhodl jsem se ale něco přidat. Něco, co není ve startovacím image a ani neexistuje jako jednoduchá feature k zaškrtnutí - sqlcmd, příkazovou řádku pro SQL. Ta se zrovna instaluje trochu složitěji (musím přidat Microsoft repo a tak), ale všechno se dá snadno dohledat. Jednoduše jsem tedy přidal jeho instalaci do Dockerfile.

```
# Sqlcmd
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - &&\
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | tee /etc/apt/sources.list.d/msprod.list &&\
    apt-get update &&\
    ACCEPT_EULA=Y apt-get install -y mssql-tools unixodbc-dev &&\
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> /home/vscode/.bash_profile
```

To je celé - dám rebuild and reopen in container (na mém Windows stroji používám Rancher Desktop, který pro mě zajišťuje Linuxový Docker a lokální Kubernetes běžící ve Windows Subsystem for Linux). 

[![](/images/2022/2022-09-12-08-18-43.png){:class="img-fluid"}](/images/2022/2022-09-12-08-18-43.png)

[![](/images/2022/2022-09-12-08-25-23.png){:class="img-fluid"}](/images/2022/2022-09-12-08-25-23.png)

[![](/images/2022/2022-09-12-08-25-03.png){:class="img-fluid"}](/images/2022/2022-09-12-08-25-03.png)

Jsem připojen - nacházím se v kontejneru! Poznáme podle zeleného rámečku vlevo dole.

[![](/images/2022/2022-09-12-08-26-14.png){:class="img-fluid"}](/images/2022/2022-09-12-08-26-14.png)

Některé extensions běží u mě v lokálu, některé v kontejneru. Mimochodem pro naledění VS Code doporučuji Settings synchronizaci, takže každý uživatel si přinese svoje oblíbené barevné schéma či klávesové zkratky.

[![](/images/2022/2022-09-12-08-28-08.png){:class="img-fluid"}](/images/2022/2022-09-12-08-28-08.png)

To jsou devkontejnery - zadarmo, přímo u vás a krásně si připravíte různá plně oddělená prostředí a snadno je budete sdílet s ostatními. Výborná věc - a teď do toho pojďme zamíchat GitHub a cloud.

# GitHub Codespaces
Co kdyby teď ta serverová strana byl cloud? Něco, kde není problém si jednou vzít 32 core, protože jdu compilovat Javu a jindy mnohem menší stroj. A to všecho tak, aby to bylo propojené s GitHubem, kde můj projekt žije a vývojář jednoduše začal.

Pro toto repo nemám ještě Codespaces vytvořeno - tak to udělám.

[![](/images/2022/2022-09-12-08-31-01.png){:class="img-fluid"}](/images/2022/2022-09-12-08-31-01.png)

Kdybych měl image bez svých úprav, naskočil by za pár vteřin - my tam ale přidali své věci (sqlcmd), takže GitHub ho pro mě musí takhle napoprvé nejdřív vyrobit (pak už bude jen pár vteřin startovat).

[![](/images/2022/2022-09-12-08-33-55.png){:class="img-fluid"}](/images/2022/2022-09-12-08-33-55.png)

Trvalo to tak 2 minuty a je to nahoře a jsem připojen = přímo v browseru běží Visual Studio Code a přes synchronizaci nastavení si právě (protože mě zná z GitHubu) i stáhlo moje klávesové zkratky. 

[![](/images/2022/2022-09-12-08-36-23.png){:class="img-fluid"}](/images/2022/2022-09-12-08-36-23.png)

Uvnitř kontejneru jsou vyžádané nástroje jako je terraform nebo mnou přidaný sqlcmd.

[![](/images/2022/2022-09-12-08-39-01.png){:class="img-fluid"}](/images/2022/2022-09-12-08-39-01.png)

Nojo, ale když tam kóduji webovou aplikaci, určitě jí budu chtít vyzkoušet, ne? Já to nasimuluji tím, že v kontejneru nainstaluji NGINX (to normálně takhle nedělejte, co chcete mít jako součást Docker image pro každý start a všechny uživatele dejte do Dockerfile) a tím simuluji spuštění webové aplikace. Nicméně každá instance má i svou storage, která se neztrácí - i tak za mě nástroje patří do definice prostředí a všechno ostatní do Gitu. Ale pokud změníte nějaké soubory a ještě nejsou commitnuté a něco se stane, nevadí - storage je perzistentní. 

[![](/images/2022/2022-09-12-08-41-24.png){:class="img-fluid"}](/images/2022/2022-09-12-08-41-24.png)

Musím ho explicitně spustit jako root (nedělat - tohle jen opravdu simuluje mojí appku) a vidím, že lokálně běží.

[![](/images/2022/2022-09-12-08-43-27.png){:class="img-fluid"}](/images/2022/2022-09-12-08-43-27.png)

Já se tam ale chci dostat ze svého browseru. Co s tím? Stačí nahodit port forwarding a to buď věřejný (kolega se mi tam mrkne) nebo privátní. 

[![](/images/2022/2022-09-12-08-44-29.png){:class="img-fluid"}](/images/2022/2022-09-12-08-44-29.png)

[![](/images/2022/2022-09-12-08-44-58.png){:class="img-fluid"}](/images/2022/2022-09-12-08-44-58.png)

No a je to - funguje.

[![](/images/2022/2022-09-12-08-45-24.png){:class="img-fluid"}](/images/2022/2022-09-12-08-45-24.png)

Samozřejmostí je debugger s break pointy a další klasické záležitosti. Nelíbí se vám v prohlížeči? Žádný problém, jednoduše v zeleném bloku necháte otevřít Codespace z vašeho Visual Studio Code. 

# Moderní vývoj a jak to všechno hraje dohromady
Pokud si poskládáte tohle všechno dohromady vyjde z toho moc příjemné řešení pro vývojáře. Projekty žijí v GitHub repozitáři a u nich i definice vývojových prostředí. Vývojáři si mohou všechno rozjet u sebe a to včetně devcontainer pro případ, že třeba jedou vlakem bez připojení, ale stejně snadno a ještě lépe si mohou nahodit Codespaces v cloudu a využít adhoc silnou mašinu. Nový vývojář tak vystačí s obyčejným notebookem, ve kterém je prohlížeč a může během pár vteřin začít. Pokud jen přebíháte mezi projekty nemusíte trávit den instalací prostředí, prostě jen vlezete do jejich repozitáře a nahodíte Codespaces. Potřebujete se náhle připojit z dovolené? Do Codespaces není problém. Jakmile jste z vývojové části spokojeni (možná za přispění pomocníka GitHub Copilot, který to kódování s vámi umí pěkně táhnout), čeká vás silná CI/CD pipeline s GitHub Actions a správa změn, vylepšení i potíží s GitHub Issues, Discussions, Projects a dalšími vlastnostmi. No pak to celé vymlasknete do Azure, do kterého ani nemusíte držet heslo díky workload identity federation AAD s GitHub. No a pro služby jako jsou Azure Container Apps nebo Azure Static WebApps vám celé workflow umí Azure nacvakat sám ať máte něco do začátku. Zkuste si to.