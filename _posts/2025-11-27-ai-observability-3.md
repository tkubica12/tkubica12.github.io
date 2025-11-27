---
layout: post
published: true
title: Deep dive do observability AI agentů s Microsoft Agent Framework - tracing s open source nástroji Aspire Dashboard a LangFuse
tags:
- AI
- OpenTelemetry
- Monitoring
---
V prvním díle jsme probrali základní architekturu a důvody proč rád používám OpenTelemetry kolektor, abychom se minule mohli věnovat metrikám a jejich použití v Azure Monitor for Prometheus a Azure Managed Grafana. Dnes se ponoříme do trasování, nejdůležijší disciplíny pro observabilitu AI agentů, a začneme open source nástroji: Aspire Dashboard pro rychlý vývojářský pohled a Langfuse.

# Aspire Dashboard
OpenTelemetry požírá svět observability a já mu nesmírně fandím. Po mnoha letech kombinace proprietárních nástrojů a přístupů s alternativní zoologickou open source SDK přišlo OpenTelemetry a má ambici pod jeden protokol, jedno SDK a API, sjednotit metriky, logy i trasovaní. Existuje řada backendů, které dělají vizualizace a mají datovou perzistenci, ale pro rychlé vývojářské zhodnocení situace jsou všechny těžkopádné, pomalé a drahé nebo požírající příliš mnoho zdrojů. Proto .NET tým vyvinul **Aspire Dashboard**, jednoduché řešení běžící v jediné odlehčeném kontejneru, kde můžete rychle a téměř v reálném čase vizualizovat OpenTelemetry.

Tady vidíme trasování z multi-tenant řešení ve stylu Magentic v Microsoft Agent Framework. 

[![](/images/2025/2025-11-27-10-24-40.png){:class="img-fluid"}](/images/2025/2025-11-27-10-24-40.png)

V mém případě jsem zapnul i logování jednotlivých textů a odpovědí.

[![](/images/2025/2025-11-27-10-26-08.png){:class="img-fluid"}](/images/2025/2025-11-27-10-26-08.png)

Sbírám i vlastní atributy, například session ID, přihlášený uživatel, role uživatele, oddělení a tak podobně.

[![](/images/2025/2025-11-27-10-26-56.png){:class="img-fluid"}](/images/2025/2025-11-27-10-26-56.png)

Jak se ale můžete přesvědčit v prvním díle tohoto seriálu, můj Open Telemetry kolektor mám nastaven tak, že je schopen filtrovat některá pole a pro jiná udělat hash a tím zamaskovat původní informaci. Mám vytvořenou další instanci Aspire, do které z OTEL kolektoru posílám filtrované a anonymizované informace. Všimněte si, že obsah konverzace vůbec nemám, user ID je zamaskované, ale stále mám potřebné technické informace jako jsou časy a spotřeba tokenů.

[![](/images/2025/2025-11-27-10-29-12.png){:class="img-fluid"}](/images/2025/2025-11-27-10-29-12.png)

V tom je obrovská síla - mám jeden proud z agenta a v OTEL kolektoru ho rozposílám na různé systémy - Aspire v plné palbě, Aspire anonymizované, Langfuse, AI Foundry apod.

Takhle třeba vypadá volání nástroje.

[![](/images/2025/2025-11-27-10-32-24.png){:class="img-fluid"}](/images/2025/2025-11-27-10-32-24.png)

Pro rychlé  náhledy na monitoring data je Aspire Dashboard výborný - jednoduchý, malinkatý, rychlý.

# Langfuse
Hledáte nástroj na trasování, který by byl open source a přímo specializovaný na AI scénáře? Langfuse je velmi populární, ale bohužel ani ten není plně otevřený co do governance projektu (není pod CNCF ani Apache Foundation ani Linux Foundation) a jde spíše o MIT core (nemáte tedy garanci, že vývoj půjde směrem vyhovujícím komunitě ani že nemůže dojít ke změně licence k méně otevřené - viz co se stalo s MongoDB, MySQL, Elastic, Redis, CentOS, Terraform apod.). Nicméně řešení je to velmi dobré a pojďme se na něj podívat.

Hned z úvodní obrazovky je vidět, že Langfuse není jen observabilita, ale zasahuje i do oblasti evaluace, které se v tomto seriálu dotkneme později.

[![](/images/2025/2025-11-27-10-40-17.png){:class="img-fluid"}](/images/2025/2025-11-27-10-40-17.png)

[![](/images/2025/2025-11-27-10-40-37.png){:class="img-fluid"}](/images/2025/2025-11-27-10-40-37.png)

[![](/images/2025/2025-11-27-10-40-53.png){:class="img-fluid"}](/images/2025/2025-11-27-10-40-53.png)

Takhle vypadá konkrétní trasování - totéž, co jsme viděli u Aspire. Graficky je to jiné, ale principiálně základní informace jsou tam stejné.

[![](/images/2025/2025-11-27-10-41-59.png){:class="img-fluid"}](/images/2025/2025-11-27-10-41-59.png)

Nicméně některé věci už nejsou přímo v datech, ale jsou odvozené - výborná je kalkulace spotřeby tokenů v penězích.

[![](/images/2025/2025-11-27-10-42-40.png){:class="img-fluid"}](/images/2025/2025-11-27-10-42-40.png)

Samozřejmě opět můžeme hezky vidět samotnou konverzaci.

[![](/images/2025/2025-11-27-10-43-21.png){:class="img-fluid"}](/images/2025/2025-11-27-10-43-21.png)

[![](/images/2025/2025-11-27-10-43-39.png){:class="img-fluid"}](/images/2025/2025-11-27-10-43-39.png)

Langfuse napřímo parsuje některé známé parametry, například ID uživatele. Díky tomu rovnou dokáže dávat přehled uživatelů a jejich spotřeby tokenů.

[![](/images/2025/2025-11-27-10-44-49.png){:class="img-fluid"}](/images/2025/2025-11-27-10-44-49.png)

To potom rozklikneme a vidíme jednotlivá trasování, session apod.

[![](/images/2025/2025-11-27-10-45-18.png){:class="img-fluid"}](/images/2025/2025-11-27-10-45-18.png)

[![](/images/2025/2025-11-27-10-45-28.png){:class="img-fluid"}](/images/2025/2025-11-27-10-45-28.png)

Langfuse jde i do evaluací, ale to si rozebereme později. Můžete tak zachycenou konverzaci vzít, přidat ji do nějaké datové sady, anotovat, zkoušet v simulátoru a tak podobně.

[![](/images/2025/2025-11-27-10-47-15.png){:class="img-fluid"}](/images/2025/2025-11-27-10-47-15.png)


Za mě je Langfuse nejlepší trasovací nástroj zaměřený specificky na AI z kategorie těch open source. Přestože není plně otevřený co do governance, je to moje první volba pokud musím zůstat v self-managed světě. Jeho evaluační schopnosti rozebereme později a má taky svoje místo, byť projekty jako je DeepEval mu jsou velkou, byť trochu jinak zaměřenou, konkurencí.


Dnes jsme se tedy ponořili do open source variant - Aspire pro rychlý vývojářský náhled, Langfuse jako open source specializované řešení na AI. Další alternativy jsou v použití ne-specializovaných řešení určených pro vývojáře (univerzální systémy typu Azure Monitor Application Insights, Grafana Tempo, Dynatrace apod.) a v hostovaných řešeních zaměřených na AI scénáře. Na ty se podíváme příště - Azure Monitor a Azure AI Foundry. Co nabízí ve formě služby?
