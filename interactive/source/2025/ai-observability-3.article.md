---
format_version: 1
title: "Deep dive do observability AI agentů s Microsoft Agent Framework - tracing s open source nástroji Aspire Dashboard a Langfuse"
subtitle: "Tracing AI agentů přes Aspire Dashboard a Langfuse: rychlý vývojářský pohled, anonymizace přes kolektor a specializovaná AI observability."
slug: "ai-observability-3"
date: "2025-11-27"
language: "cs-CZ"
status: "experimental"
canonical_url: "/2025/ai-observability-3/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Deep dive do observability AI agentů s Microsoft Agent Framework - tracing s open source nástroji Aspire Dashboard a Langfuse

V prvním díle jsme probrali základní architekturu a důvody proč rád používám OpenTelemetry kolektor, abychom se minule mohli věnovat metrikám a jejich použití v Azure Monitor for Prometheus a Azure Managed Grafana. Dnes se ponoříme do trasování, nejdůležijší disciplíny pro observabilitu AI agentů, a začneme open source nástroji: Aspire Dashboard pro rychlý vývojářský pohled a Langfuse.

::: group id="open-source-tracing" title="Open source tracing pro AI agenty"

::: card number="01" title="Aspire Dashboard: rychlý vývojářský pohled" default="open"
OpenTelemetry požírá svět observability a já mu nesmírně fandím. Po mnoha letech kombinace proprietárních nástrojů a přístupů s alternativní zoologickou open source SDK přišlo OpenTelemetry a má ambici pod jeden protokol, jedno SDK a API, sjednotit metriky, logy i trasovaní. Existuje řada backendů, které dělají vizualizace a mají datovou perzistenci, ale pro rychlé vývojářské zhodnocení situace jsou všechny těžkopádné, pomalé a drahé nebo požírající příliš mnoho zdrojů. Proto .NET tým vyvinul **Aspire Dashboard**, jednoduché řešení běžící v jediné odlehčeném kontejneru, kde můžete rychle a téměř v reálném čase vizualizovat OpenTelemetry.

Tady vidíme trasování z multi-tenant řešení ve stylu Magentic v Microsoft Agent Framework. 

::: reveal title="Screenshot: přehled trace v Aspire"
![Přehled trace v Aspire Dashboard](/images/2025/2025-11-27-10-24-40.png)
:::
:::

::: card number="02" title="Aspire: plná telemetrie vs. anonymizovaný pohled"
V mém případě jsem zapnul i logování jednotlivých textů a odpovědí.

::: reveal title="Screenshot: texty a odpovědi v trace"
![Texty a odpovědi v Aspire trace](/images/2025/2025-11-27-10-26-08.png)
:::

Sbírám i vlastní atributy, například session ID, přihlášený uživatel, role uživatele, oddělení a tak podobně.

::: reveal title="Screenshot: vlastní atributy ve spanech"
![Vlastní atributy ve spanech Aspire Dashboardu](/images/2025/2025-11-27-10-26-56.png)
:::

Jak se ale můžete přesvědčit v prvním díle tohoto seriálu, můj Open Telemetry kolektor mám nastaven tak, že je schopen filtrovat některá pole a pro jiná udělat hash a tím zamaskovat původní informaci. Mám vytvořenou další instanci Aspire, do které z OTEL kolektoru posílám filtrované a anonymizované informace. Všimněte si, že obsah konverzace vůbec nemám, user ID je zamaskované, ale stále mám potřebné technické informace jako jsou časy a spotřeba tokenů.

::: reveal title="Screenshot: anonymizovaný Aspire pohled"
![Anonymizovaný Aspire pohled bez obsahu konverzace](/images/2025/2025-11-27-10-29-12.png)
:::

::: callout type="verdict" title="Síla kolektoru"
V tom je obrovská síla - mám jeden proud z agenta a v OTEL kolektoru ho rozposílám na různé systémy - Aspire v plné palbě, Aspire anonymizované, Langfuse, AI Foundry apod.
:::
:::

::: card number="03" title="Aspire: detail volání nástroje"
Takhle třeba vypadá volání nástroje.

::: reveal title="Screenshot: tool call v trace"
![Detail volání nástroje v Aspire trace](/images/2025/2025-11-27-10-32-24.png)
:::

Pro rychlé  náhledy na monitoring data je Aspire Dashboard výborný - jednoduchý, malinkatý, rychlý.

:::

::: card number="04" title="Langfuse: specializovaný AI tracing" default="open"
Hledáte nástroj na trasování, který by byl open source a přímo specializovaný na AI scénáře? Langfuse je velmi populární, ale bohužel ani ten není plně otevřený co do governance projektu (není pod CNCF ani Apache Foundation ani Linux Foundation) a jde spíše o MIT core (nemáte tedy garanci, že vývoj půjde směrem vyhovujícím komunitě ani že nemůže dojít ke změně licence k méně otevřené - viz co se stalo s MongoDB, MySQL, Elastic, Redis, CentOS, Terraform apod.). Nicméně řešení je to velmi dobré a pojďme se na něj podívat.

Hned z úvodní obrazovky je vidět, že Langfuse není jen observabilita, ale zasahuje i do oblasti evaluace, které se v tomto seriálu dotkneme později.

::: reveal title="Screenshoty: úvodní Langfuse obrazovky"
![Langfuse přehled projektu](/images/2025/2025-11-27-10-40-17.png)
![Langfuse navigace k tracingu a evaluacím](/images/2025/2025-11-27-10-40-37.png)
![Langfuse pohled na observability a datasets](/images/2025/2025-11-27-10-40-53.png)
:::
:::

::: card number="05" title="Langfuse: konkrétní trace a tokenová ekonomika"
Takhle vypadá konkrétní trasování - totéž, co jsme viděli u Aspire. Graficky je to jiné, ale principiálně základní informace jsou tam stejné.

::: reveal title="Screenshot: konkrétní trace v Langfuse"
![Konkrétní trace v Langfuse](/images/2025/2025-11-27-10-41-59.png)
:::

Nicméně některé věci už nejsou přímo v datech, ale jsou odvozené - výborná je kalkulace spotřeby tokenů v penězích.

::: reveal title="Screenshot: náklady a tokeny"
![Kalkulace nákladů a tokenů v Langfuse](/images/2025/2025-11-27-10-42-40.png)
:::

Samozřejmě opět můžeme hezky vidět samotnou konverzaci.

::: reveal title="Screenshoty: obsah konverzace"
![Konverzace v Langfuse trace](/images/2025/2025-11-27-10-43-21.png)
![Detail zprávy v Langfuse trace](/images/2025/2025-11-27-10-43-39.png)
:::
:::

::: card number="06" title="Langfuse: uživatelé, session a evaluace"
Langfuse napřímo parsuje některé známé parametry, například ID uživatele. Díky tomu rovnou dokáže dávat přehled uživatelů a jejich spotřeby tokenů.

::: reveal title="Screenshot: přehled uživatelů"
![Přehled uživatelů a tokenové spotřeby](/images/2025/2025-11-27-10-44-49.png)
:::

To potom rozklikneme a vidíme jednotlivá trasování, session apod.

::: reveal title="Screenshoty: session a jednotlivé traces"
![Detail uživatele a sessions v Langfuse](/images/2025/2025-11-27-10-45-18.png)
![Jednotlivé traces v session](/images/2025/2025-11-27-10-45-28.png)
:::

Langfuse jde i do evaluací, ale to si rozebereme později. Můžete tak zachycenou konverzaci vzít, přidat ji do nějaké datové sady, anotovat, zkoušet v simulátoru a tak podobně.

::: reveal title="Screenshot: dataset a evaluace"
![Langfuse datasets a evaluace](/images/2025/2025-11-27-10-47-15.png)
:::


Za mě je Langfuse nejlepší trasovací nástroj zaměřený specificky na AI z kategorie těch open source. Přestože není plně otevřený co do governance, je to moje první volba pokud musím zůstat v self-managed světě. Jeho evaluační schopnosti rozebereme později a má taky svoje místo, byť projekty jako je DeepEval mu jsou velkou, byť trochu jinak zaměřenou, konkurencí.


Dnes jsme se tedy ponořili do open source variant - Aspire pro rychlý vývojářský náhled, Langfuse jako open source specializované řešení na AI. Další alternativy jsou v použití ne-specializovaných řešení určených pro vývojáře (univerzální systémy typu Azure Monitor Application Insights, Grafana Tempo, Dynatrace apod.) a v hostovaných řešeních zaměřených na AI scénáře. Na ty se podíváme příště - Azure Monitor a Azure AI Foundry. Co nabízí ve formě služby?


::: summary-grid
- **Aspire Dashboard**: malý, rychlý a výborný pro vývojářský pohled téměř v reálném čase.
- **Anonymizace**: stejný proud telemetrie lze přes OTEL kolektor poslat jednou plně a jednou očištěně.
- **Langfuse**: specializovaný AI observability nástroj s tracingem, tokenovou ekonomikou a vazbou na evaluace.
- **Volba nástroje**: Aspire na rychlý troubleshooting, Langfuse jako self-managed AI tracing varianta.
:::
:::

:::


::: closing
Další krok je podívat se na službové varianty - Azure Monitor a Azure AI Foundry.
:::
