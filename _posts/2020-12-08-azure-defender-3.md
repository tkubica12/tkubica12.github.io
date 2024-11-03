---
layout: post
published: true
title: "Azure Defender (3): Integrace bezpečnostních doporučení do vašich procesů a nástrojů"
tags:
- Security
---
Minule jsme ponořili do bezpečnostního skóre, jak se dívat na doporučení a jak k tomu můžete přistupovat. Dnes si ukážeme, že Azure Portál není jediný způsob jak se výsledky analýzy zabývat. Jak automatizovaně reagovat, rozdávat úkoly, dělat si vlastní vizualizace nebo integrovat vaše nástroje?

# Nativní automatizace s Logic App
Velmi mocným řešením pro integraci do vašich systémů a procesů jsou určitě nativní Logic App - cloud-native serverless orchestrační (iPaaS) platforma v Azure. Tu je možné spouštět ručně v rámci procházení doporučení nebo ji vyvolávat automaticky při nalezení nového doporučení. 

Na ukázku jsem si připravil jednoduchou Logic App.

[![](/images/2020/2020-11-30-13-23-51.png){:class="img-fluid"}](/images/2020/2020-11-30-13-23-51.png)

Jejím smyslem je podívat se na doporučení a vytáhnout si zdroj v Azure, kterého se týká a následně z jeho ID vyparsovat číslo subskripce a název resource group. S těmito informacemi využiji zabudovanou komponentu pro načtení informací o resource group, abych zjistil jaké tagy na ní jsou.

[![](/images/2020/2020-11-30-13-25-10.png){:class="img-fluid"}](/images/2020/2020-11-30-13-25-10.png)

Ve svém prostředí používám tag Owner, který obsahuje email člověka odpovědného za daný zdroj. Na tuto adresu budu chtít odeslat email s tímto doporučením a prosbou o nápravu.

[![](/images/2020/2020-11-30-13-26-04.png){:class="img-fluid"}](/images/2020/2020-11-30-13-26-04.png)

Výsledek vypadá nějak takhle:

[![](/images/2020/2020-11-30-13-26-30.png){:class="img-fluid"}](/images/2020/2020-11-30-13-26-30.png)

Já jsem vyvolal Logic App jako připravenou akci ručně.

V Logic App můžete využít obrovské množství konektorů do nejrůznějších nástrojů. Jste tak schopni jako komunikační platformu použít i Teams nebo Slack, založit incident k řešení v Service Now či Jira, zapsat něco do databáze či souboru - na výběr jsou stovky hotových konektorů a pokud by vám nějaký chyběl, není problém přidat si vlastní. A pokud jsou vaše komponenty uvnitř firemní sítě, díky Integration Services Environment či nové schopnost běžet Logic App v engine Azure Functions Premium můžete tyto spouštět integrované do VNETu a volat nějaké onpremises API.

Logic App také může odstartovat automaticky hned jak se doporučení vytvoří (o reakci na hrozby nalezené aktivní obranou si povíme jindy).

[![](/images/2020/2020-11-30-13-48-27.png){:class="img-fluid"}](/images/2020/2020-11-30-13-48-27.png)

# Doporučení jako datový zdroj
Doporučení si můžete stáhnout jako CSV soubor pro další zpracování.

[![](/images/2020/2020-11-30-13-49-17.png){:class="img-fluid"}](/images/2020/2020-11-30-13-49-17.png)

Výsledky scanování, doporučení a regulatorní reporty jsou jako datový zdroj dostupné v Azure Resource Explorer a můžete se na ně ptát mocným Kusto jazykem (KQL).

[![](/images/2020/2020-11-30-13-52-41.png){:class="img-fluid"}](/images/2020/2020-11-30-13-52-41.png)

K dispozici jsou i detailní výsledky vulnerability assessmentů.

[![](/images/2020/2020-11-30-13-56-58.png){:class="img-fluid"}](/images/2020/2020-11-30-13-56-58.png)

# Streaming doporučení jako událostí do jiných nástrojů
Události (threat detection - k těm se dostaneme později), doporučení a skóre lze kontinuálně exportovat jako proud dat a to buď do nějakého Log Analytics Workspace nebo do Event Hub. První může posloužit k tomu, že se na jedno centrální místo dostanou všechny hlášky ze všech prostředí a subskripcí pro nějakou 3rd party vizualizaci (k tomu se dostaneme). Event Hub je pak ideální pro integrace SIEM řešení třetích stran s tím, že řada výrobců včetně Splunk, QRadar, Rapid7 nebo ArcSight má tyto integrace hotové a snadno se tak Azure Defender napojí na SIEM ať už Azure Sentinel nebo nástroj třetí strany.

[![](/images/2020/2020-11-30-14-11-26.png){:class="img-fluid"}](/images/2020/2020-11-30-14-11-26.png)

Já jsem například nechal data přeposílat do Log Analytics workspace a všechny alerty tak vidím na jednom místě co do datové základny (GUI Azure Security Center zvládne totéž a poskládá obraz ze všech workspace, pokud ale s daty chci pracovat v nějakém externím systému, je určitě jednoduší je dostat do jedné tabulky).

[![](/images/2020/2020-11-30-14-49-52.png){:class="img-fluid"}](/images/2020/2020-11-30-14-49-52.png)

# Azure Workbooky
Produktový tým ve spolupráci s komunitou připravil několik hezkých příkladů dalších vizualizací ve formě workbooků.

Workbooky najdete na [GitHubu](https://github.com/Azure/Azure-Security-Center/tree/master/Secure%20Score/PowerBI-SecureScoreReport)

Tady například vizualizace určená pro podporu soutěžení mezi týmy.

[![](/images/2020/2020-11-30-14-45-20.png){:class="img-fluid"}](/images/2020/2020-11-30-14-45-20.png)

Níže je také jiný pohled na Qualys data.

[![](/images/2020/2020-11-30-14-47-41.png){:class="img-fluid"}](/images/2020/2020-11-30-14-47-41.png)

[![](/images/2020/2020-11-30-14-48-00.png){:class="img-fluid"}](/images/2020/2020-11-30-14-48-00.png)


# Vizualizace v Power BI
Azure pro vás připravil také velmi dobré dashboardy v PowerBI, které ukazují nejen aktuální stav, ale také vývoj vašeho skóre v čase.

Jak je nainstalovat, napojit a upravit najdete v návodu na [GitHubu](https://github.com/Azure/Azure-Security-Center/tree/master/Secure%20Score/PowerBI-SecureScoreReport)

[![](/images/2020/2020-11-30-14-31-33.png){:class="img-fluid"}](/images/2020/2020-11-30-14-31-33.png)

[![](/images/2020/2020-11-30-14-33-25.png){:class="img-fluid"}](/images/2020/2020-11-30-14-33-25.png)

# Vizualizace v Grafana
Protože všechna potřebná data jsou streamovatelná do Log Analytics workspace, můžeme využít oficiálního Grafana konektoru do Azure Monitor, který je k dispozici jako core balíček. Umožňuje napojit se na datové zdroje jako jsou Azure Metrics, Log Analytics nebo Application Insights a vizualizovat tak můžete provozní data i údaje ze Security Center.

[![](/images/2020/2020-11-30-15-13-03.png){:class="img-fluid"}](/images/2020/2020-11-30-15-13-03.png)

S daty si už pohrajte dle vašich potřeb.

[![](/images/2020/2020-11-30-15-24-47.png){:class="img-fluid"}](/images/2020/2020-11-30-15-24-47.png)

# Přístup přes API
Security Center nabízí bohaté a přehledné API, takže nebude problém se programovatelně napojit naprosto z čehokoli.

[https://docs.microsoft.com/en-us/rest/api/securitycenter/](https://docs.microsoft.com/en-us/rest/api/securitycenter/)

[![](/images/2020/2020-11-30-14-20-42.png){:class="img-fluid"}](/images/2020/2020-11-30-14-20-42.png)

Přímo z portálu si můžete všechna API vyzkoušet.

[![](/images/2020/2020-11-30-15-30-44.png){:class="img-fluid"}](/images/2020/2020-11-30-15-30-44.png)

Pokud je alfa a omega vašeho života Azure portál, v Security Center najdete všechno potřebné co do sledování stavu vaší bezpečnosti. Pokud ale potřebujete řešení integrovat do dalších nástrojů a procesů není to díky otevřenosti řešení žádný problém. Nativní integrační platforma Logic App je připravena na vaše workflow s hotovou podporou pro stovky řešení třetích stran. Vlastní vizualizace, Grafana, export dat různými způsoby, Power BI i API pak nabídnou řešení v zásadě jakékoli integrační nebo vizualizační potřeby. Doporučení máme a začlenit je do firmy umíme. Příště si projdeme Azure Policy, která je pod kapotou toho všeho, a necháme ji nám pomoci s preventivní ochranou prostředí a využijeme ji i pro vlastní pravidla do CSPM.
