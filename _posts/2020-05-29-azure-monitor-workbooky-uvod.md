---
layout: post
title: 'Azure Monitor Workbooky - úvod'
tags:
- Monitoring
---
Azure Monitor nabízí workbooky jako moc pěknou metodu vizualizace dat. Jak funguje? Co umí? Jak si to můžu přizpůsobit a jak udělat svoje vlastní? Dnes se pustíme do úvodu a od příště budeme zkoušet prakticky vytvářet workbooky, tak snad se vám to bude hodit do vašich projektů a prostředí.

# Azure Monitor Workbooky vs. jiné vizualizace
Je spousta nástrojů na vizualizaci monitorovacích dat a rozhodně tady nebudu dělat nějaké hloubkové srovnání. Přesto je řada nástrojů v Azure, v Microsoft portfoliu a v open source komunitě, které nějakou viualizaci dělají a umí použít Azure Monitor jako datovou základnu. Jaké jsou rozdíly a podle čeho si vybrat?

## Workbooky
Co je workbook? Jde o interaktivní vizualizační platformu, která je zaměřená nejen na telemetrii, ale i logy. Dokážete tak v jednom místě ukazovat informace z různých domén monitoringu. Třeba seznam VM, jejich telemetrie a chybová hlášky z těchto VM. Interaktivnost vězí v tom, že můžete na jeden vizualizační prvek kliknout a tím ovlivnit informace prezentované v ostatních (například označit VM, která ukazuje velkou zátěž a získat tak podrobnšjší grafy a ERROR logy z ní). 

![](/images/2020/2020-05-05-09-46-29.png){:class="img-fluid"}

## Log Analytics
Přímo Log Analytics nabízí jednoduchou vizualizační platformu pro rychlé zobrazení výsledků a pro použití v dashboardech (viz dále). 

![](/images/2020/2020-05-05-09-53-07.png){:class="img-fluid"}

## Metrics

Azure platforma sbírá telemetrii do Metrics v rámci Azure Monitor. Typicky si můžete vybrat, zda data dostávat do Log Analytics nebo do Metrics. První jmenovaná je perfektní pro dlouhodobou analýzu, korelace a složitější machine learning modely, ale Metrics jsou jednoduché a rychlé - výborné pro rychlou orientaci (ostatně proto je Workbooky také podporují, jak uvidíme později). Metriky mají vizualizační možnosti a dají se přišpendlit na dashboard.

![](/images/2020/2020-05-05-09-56-03.png){:class="img-fluid"}

## Dashboardy v Azure

Zejména pro telemetrii, rychlý přehled a umístění na obrazovku na zdi můžete použít dashboardy v Azure. Jde v podstatě o plochu, kam umístíte obrázky z Log Analytics a Metrics. Dashboard není tak interaktivní a hodí se zejména pro telemetrii.

![](/images/2020/2020-05-05-09-58-02.png){:class="img-fluid"}

## OMS pohrobek

Před nějakou dobou vznikal jiný framework pro interaktivní reporting v Azure, který měl doplnit dashboardy (ty jsou od začátku spíše koukací, než investigativní). Nicméně tento projekt už se nerozvíjí a kompletně se přešlo na workbooky. Stále se s ním ale můžete někde potkat, tak uvádím i zde.

![](/images/2020/2020-05-05-10-08-08.png){:class="img-fluid"}

## Notebooky (Jupyter)
Ve světě datové analýzy jsou velmi rozšířené Jupyter notebooky, tedy primárně kombinace textu a kódu. Moje zkušenost s provozáky zatím nenaznačuje, že by takový způsob práce preferovali, ale lidé s datovým nebo vývojářským zázemím k tomu mají docela blízko a může jim takový styl vyhovovat nejlépe. Je to v podstatě kombinace dokumentace s ukázkami kódu pro vyhledávání a analýzu dat, kde ale nemusíte text někam kopírovat a pouštět, ale přímo z dokumentu vyvoláte konkrétní příkazy a vidíte integrované výsledky. Azure Notebooks (postavené na Jupyter technologii) jsou hostované prostředí pro tyto dokumenty a podporují KQL konektor do Azure Data Explorer nebo právě Log Analytics. Zejména v bezpečnostní analýze to dává velký smysl, a právě proto je součástí Azure Sentinel řada připravených notebooků.

![](/images/2020/2020-05-08-10-25-34.png){:class="img-fluid"}

## Grafana
Pokud jste ponořeni v open source světě, pak určitě znáte Grafana pro vizualizaci telemetrie. Velmi rozšířený nástroj, díky čemuž řada open source projektů nabízí hotové dashboardy a na webu najdete mnoho příkladů a návodů. Azure Monitor může sloužit jako datový zdroj pro Grafana a to jak v části Metrics tak Log Analytics. To má dva zajímavé příklady použití:
- Můžete vzít Azure Monitor jako backend prostředí pro všechnu vaší telemetrii a logy. Sbírat data můžete agentem, ale Azure Monitor umožňuje třeba sbírání Prometheus exportů nebo OpenTelemetry dat. Získáte spolehlivý backend s neomezenou škálou a přitom dál používáte Grafana pro vizualizace.
- Můžete vzít data z Azure Monitor a data z dalších systémů podporovaných v Grafana a vše vizualizovat na jednom místě.

![](/images/2020/2020-05-08-11-29-55.png){:class="img-fluid"}

## Power BI
Ultimátní vizualizační nástroj z dílny Microsoftu je určitě Power BI. Není specificky zaměřený, takže si budete muset dát trochu víc práce s vytvořením vizualizací pro potřeby provozních nebo bezpečnostních dat. Co je ale zásadní přínos je fakt, že můžete napojit neuvěřitelné množství datových zdrojů včetně různých databází, datových skladů, open data nebo API endpointů. Do jednoho prostředí tak dostanete data jakéhokoli typu včetně těch obchodních. Pokud potřebujete korelovat jednotlivé změny v aplikacích, aplikační SLA z pohledu jejich přínosu pro byznys (průměrná velikost objednávky, zisk, obrat), tak Power BI je určitě ta správná csta.

![](/images/2020/2020-05-08-10-32-07.png){:class="img-fluid"}

![](/images/2020/2020-05-08-10-38-33.png){:class="img-fluid"}

# Datové zdroje
Jaké zdroje Workbooky podporují?

![](/images/2020/2020-05-08-10-41-32.png){:class="img-fluid"}

Jsou to především Metrics a query. Pokud jde o různé parametry, tak ty mohou být statické i dynamické (tvořené z query). Co se query týče, tohle jsou možné zdroje:

![](/images/2020/2020-05-08-10-42-52.png){:class="img-fluid"}

Nejčastěji samozřejmě Log Analytics, ale zajámavý je resource explorer (dotazy nad zdroji v Azure - ideální třeba pro parametry či inventarizaci), Data Explorer (vaše vlastní instance engine, kam můžete dávat co chcete), ale třeba i custom endpoint query, což je možnost zavolat nějaké externí API.

# Vizualizační prvky
Způsobů zobrazení dat je opravdu hodně a budeme si je v této série různě zkoušet. Pár příkladů je tady:

![](/images/2020/2020-05-08-10-46-27.png){:class="img-fluid"}

![](/images/2020/2020-05-08-10-46-43.png){:class="img-fluid"}

![](/images/2020/2020-05-08-10-46-59.png){:class="img-fluid"}

![](/images/2020/2020-05-08-10-47-17.png){:class="img-fluid"}

![](/images/2020/2020-05-08-10-47-33.png){:class="img-fluid"}

![](/images/2020/2020-05-08-10-47-47.png){:class="img-fluid"}

# Scope
Workbook má tu zajímavou vlastnost, že nemusí být omezen na jeden Log Analytics workspace. Scope můžete definovat jako celou subscripci, skupinu subsckripcí, konkrétní resources nebo log analytics workspace. Na data tedy můžete nahlížet víceméně jakkoli. Důležité je, že pro zobrazení dat na ně musí mít uživatel právo. Můžete tak mít jeden workbook, ale přitom v něm každý vidí něco jiného, podle toho, jak je nastaven jeho RBAC.

# Instance vs. šablona
Můžete si vytvořit vlastní workbook a ten sdílet s ostatními. Také lze vzít nativní workbook připravený přímo lidmi od Azure (ano - všechny zdroje jsou k dispozici, přesně vidíte, jak je to udělané) a upravit si ho. Vzniká ale zajímavý problém. Jak to udělat, aby se každý dostal k připravenému workbooku, ale přitom aby v něm mohl udělat změny pro sebe, aniž by to rozvrtal ostatním? Tohle workbooky řeší konceptem šablon.

Všechny předem připravené workbooky mají fialovou barvu a jsou to šablony. kdokoli si je může zobrazit.

![](/images/2020/2020-05-08-10-52-55.png){:class="img-fluid"}

Otevřel jsem jeden z nich, udělal v něm změnu a tu si uložil ve své subskripci. Tento workbook je ted zelený - už je to konkrétní instance.

![](/images/2020/2020-05-08-10-54-33.png){:class="img-fluid"}

Tento změněný workbook můžu sdílet s ostatními. Ale oni také mohou otevřít fialový a vidí původní verzi a můžou si v něm udělat změnu podle svých představ.

V praxi tedy pokud vytváříte nějaký workbook, který se má stát základním pohledem ve vaší organizaci, doporučuji jej nasadit jako template (fialovou verzi). Každý ve firmě se tak k němu dostane a přitom každý má možnost si udělat svoje vlastní úpravy, aniž by to rozbil ostatním.


Tohle jsou Workbooky - moderní řešení vizualizace provozních a bezpečnostních dat. Interaktivní systém, upravitelné texty včetně dokumentace nebo doporučených postupů, kombinace telemetrie a logů, dotazy obsahující machine learning funkce, pěkné a praktické vizualizace, výborné možnosti parametrizace a vše včetně řízení přístupu k datům, takže každý vidí jen to, co vidět má. Příště si začneme pár pohledu vytvářet.