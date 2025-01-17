---
layout: post
published: true
title: Centrální řízení aplikačních konfigurací s Azure Application Configuration Service
tags:
- AppService
---
Konfigurace aplikace můžete řešit přímo v kódu třeba přes statickou proměnnou. Jejich změna znamená novou kompilaci, což není ideální. Proto konfigurace vytáhnete ven do souboru nebo proměnných prostředí, takže není nutné provádět build a stačí v provozu podhodit příslušý soubor nebo env a všechno jede. Tohle řešení má ale stále nějaké nevýhody:
* Každá komponenta nebo replika má svou nezávislou konfiguraci. Centrální řízení je problematické a obvykle ho řešíte v rámci CI/CD pipeline. To ale vede na to, že změna konfigurace znamená přenasazení a to může mít vliv na dostupnost.
* Předání konfigurace je závislé na prostředí, ve kterém kód běží. Možná musíte nakopírovat soubor do VM, zadat konfiguraci do env v definici kontejneru nebo ji tam namapovat jako Volume, v serverless světě musíte nastavení provést na úrovni platformy.
* U klientské strany nemáte prostředí tak dobře pod kontrolou ať už je to kód běžící v prohlížeči nebo Android či iOS nativní aplikace. Co s tím? Možná dáte konfigurace do balíčku samotného, ale jak pak řešit situaci, kdy různí zákazníci mají různě staré verze balíčku (což u HTML5 asi nehrozí, ale u nativní Android aplikace určitě ano)?
  
Všechny tyto situace vedou na zajímavé zjištění a to je, že konfigurace je součástí procesu nasazení. To má ale konsekvence například do způsobu uvolňování nových funkcí. Představte si, že novou funkci chcete oznámit na tiskové konferenci a hned nad jejím začátku ji zpřístupnit. Pokud to budete řešit nasazením, bude to nějakou dobu trvat - a pokud to třeba bude znamenat update na Androidu, je to docela dlouho. Navíc tu může být i riziko. Můžete ale funkci mít už nasazenou, ale schovanou. Typicky v konfiguraci bude feature flag a daná část aplikace se nebude zobrazovat, pokud je na false. Nebo chcete funkci uvolňovat postupně a armádu kódu chcete ovládat z centrálního místa. V jeden okamžik zapnout funkci na Maltě, druhý den v Evropě a nakonec v Americe. Řešením těchto a dalších situací může být vytažení konfigurací a feature flagů do centralizované služby. V podstatě jednoduché databáze, ale odlehčené s přístupem přes REST API nebo ještě lépe nějakým standarndím konfiguračním SDK. Například .NET Core má takové SDK a můžete chtít tuto serverovou variantu udělat tak, že nemusíte v kódu nic měnit.

Představme si ještě jednu situaci. Máme běžné uživatele a ty, kteří jsou ochotni vyzkoušet si nové věci před finálním spuštěním (nemluvím tady o test buildu pro testery se zapnutým extra logováním apod.). Chtěl bych, aby uživatel mohl kdykoli preview funkce zapnout, ale kdykoli je také vypnout. Pokud kvůli tomu musí instalovat jiný build, je to kostrbaté. Funkce by tedy mohla být součástí všech releasů, ale běžně ji GUI nezobrazí. Uživatel si může zapnout něco jako "enable preview features", kód se podívá do feature flagů a zjistí, co pro takovou situaci chceme zapnout za funkce. Na straně aplikace jedno přepínátko a přes feature flagy řídíme jaké preview funkce aktuálně jsou k dispozici. Mimochodem všimli jste si ve svém Outlook for Windows vpravo nahoře přepínátka Comming soon? U řadě jiných aplikací najdete něco podobného a neznamená to instalovat si jinou verzi. Obvykle budete mít dev a prod větev (to jsou různé buildy), ale v rámci prod větve může zákazník indikovat, zda chce vidět preview věci nebo ne. Není to tedy řešení pro přepracování core aplikace, ale pro preview funkcí nad ním.

Přesně to pro vás může udělat Azure Application Configuration Service.

A jak řešit citlivé informace, třeba connection string do databáze? Konfigurační služba je velmi bezpečná (šifruje data po cestě i na storage, řídí přístupy), ale to nejcitlivější dejte do Azure Key Vault. Jde o službu, která ve své Premium verzi může mít pod kapotou speciální hardwarově řešení (HSM), přistupuje k ní také přes API a je určená přesně na tohle. Doporučuji tedy tajnosti držet v tomto trezoru, zatímce konfigurační parametery v Application Configuration Service. A mimochodem token pro přístup do ní si aplikace může vyzvednout právě z Key Vaultu.

# Proč použít Azure Application Configuration Service
Níže jsou důvody, proč jít touhle cestou:
* Konfiguraci držíte na centrálním systému a dokážete z jednoho místa ovlivňovat aplikace mimo technický release proces. Oddělujete tedy "obchodní release" od technického.
* Řešení slouží pro libovolné třídy aplikací - backend, frontend, HTML5, nativní appky.
* Funguje pro libovolný programovací jazyk - do řady z nich má SDK a tam kde není, lze použít REST API.
* Dá se použít ve všech prostředích - VM, kontejner, Azure Function a serverless, cloud, on-premises, telefon

# Vyzkoušejme si to

Vytvoříme App Configurat.

![](/images/2019/2019-05-14-13-53-44.png){:class="img-fluid"}

Tady máme výsledek.

![](/images/2019/2019-05-14-14-02-19.png){:class="img-fluid"}

Nejdřív se podívejme na feature flagy.

![](/images/2019/2019-05-14-14-02-55.png){:class="img-fluid"}

![](/images/2019/2019-05-14-14-03-50.png){:class="img-fluid"}

Na přehledové stránce můžeme krásně zapínat a vypínat jednotlivé flagy.

![](/images/2019/2019-05-14-16-55-13.png){:class="img-fluid"}

Feature flag je vlastně jen speciální variantou key/value páru. Pojďme si nějaké přidat.

![](/images/2019/2019-05-14-16-56-09.png){:class="img-fluid"}

V klíči můžeme používat znaky : nebo / pro nějakou hierarchickou organizaci. Label umožňuje další kategorizaci klíče, můžeme ho považovat za namespace. Tak například mohu mít Label prod vs. test nebo EU vs. US.

![](/images/2019/2019-05-14-16-58-44.png){:class="img-fluid"}

Výsledek může vypadat nějak takhle:

![](/images/2019/2019-05-14-17-00-07.png){:class="img-fluid"}

Pokud máte v současné době nastavení uložena v App Service nebo konfiguračním souboru, můžete je jednoduše importovat i exportovat.

![](/images/2019/2019-05-14-17-02-37.png){:class="img-fluid"}

Velmi zajímavá funkce, která pro mě ale zatím není dostupná, je generování události do Event Grid při změně konfigurace. Tímto se může vaše aplikace dozvědět o potřebě si informace načíst a přizpůsobit se. Na Event Grid se můžete napojit aplikačně nebo na jeho základě spustit Azure Function, Logic App, poslat webhook nebo založit zprávu v Storage Queue nebo Event Hub. Tohle mi přijde velmi užitečné.

# Využití v aplikaci
Nejsem žádný programátor, tak vás odkážu na příklady v dokumentaci, které jsou pro .NET Core, .NET Framework, Java Spring nebo REST API. Pro různé jazyky je dokonce pěkné SDK, aby se s tím opravdu dobře pracovalo.

Tak například pro feature flagy v .NET Core nemusí dělat if/else struktury, ale použijete IFeatureManager: [https://docs.microsoft.com/en-us/azure/azure-app-configuration/use-feature-flags-dotnet-core](https://docs.microsoft.com/en-us/azure/azure-app-configuration/use-feature-flags-dotnet-core).

V .NET Core existuje SDK pro dynamické "nasávání" konfigurací z různých zdrojů a to můžete použít i s touto službou: [https://docs.microsoft.com/en-us/azure/azure-app-configuration/enable-dynamic-configuration-aspnet-core](https://docs.microsoft.com/en-us/azure/azure-app-configuration/enable-dynamic-configuration-aspnet-core)

Další pohodlné SDK je k dispozici pro Java Spring: [https://github.com/Microsoft/spring-cloud-azure/tree/azure-config/spring-cloud-azure-starters/spring-cloud-starter-azure-config](https://github.com/Microsoft/spring-cloud-azure/tree/azure-config/spring-cloud-azure-starters/spring-cloud-starter-azure-config)

Pokud není pro váš jazyk nějaké takové SDK, vůbec to nevadí. Službu můžete používat přes REST API a jednoduše se dotazovat. Řešení je tak univerzální pro jakýkoli jazyk.


Potřebujete pro vaše aplikace na backendu v kontejneru, VM, PaaS, v browseru nebo v Androidu jednotným způsobem řešit centrálně konfigurace? Chcete oddělit obchodní release funkcí od technického nasazení? Podívejte se na velmi zajímavou službu Azure App Configuration. Zatím je v preview a v tuto chvíli zdarma, cenotvorba zatím nebyla oznámena. Vývojáři, vyzkoušejte.




