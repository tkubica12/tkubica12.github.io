---
layout: post
title: 'Azure Container Apps: serverless kontejnery jako budoucnost platformních služeb pro aplikace'
tags:
- AzureContainerApps
---
Jak dnes běžet moderní aplikace v Azure? Kubernetes je super, ale je složitý jak parní mlátička. Platformní služby jsou fajn, ale není to moc svazující, obtížně přenositelné mezi cloudy, proprietární a vyžadující změny v mé už tak pěkně do kontejneru zabalené službě? Možná to co hledáte jsou kontejnery jako služba - nechci znát ty příšerné detaily Kubernetu, chci dát cloudu své kontejnery a ať je pro mě běží. Nechci si ale nechat diktovat v jakém jazyce to píšu, z jakého image kontejnery odvozuji a nejde mi jen o hostování nějaké webovky, ale mikroslužeb včetně asynchronních součástek a workerů. Pokud hledáte právě tohle, musíte si vyzkoušet Azure Container Apps.

# Jak běhat kontejnery v Azure (a v jiných cloudech) - do příchodu Container Apps
Podívejme se na několik možností a jejich specifik:
- **Azure Kubernetes Service** - to je služba s neuvěřitelnou popularitou a její obdoby jsou i v ostatních cloudech (EKS, GKE). Univerzální, přenositelná, hodně flexibilní, cenově příjemná varianta. Jenže - hodně složitá. Učící křivka je skutečně dost strmá a od prvních pokusů do produkčního nasazení často uplyne i rok, pokud s tím tým teprve začíná. Tohle rozhodně není platforma pro vývojáře, pro rychlou migraci firmy do cloudu, pro možnost investovat maximum energie do toho, co je důležité pro byznys, tedy do samotné aplikace.
- **Kubernetes bez nodů** - co kdyby si cloud vzal na starost nody, ať tohle nemusíte řešit? Toho dosáhnete s AKS Virtual Nodes, kdy vám AKS na pozadí hází kontejnery do ACI, místo na skutečné nody. Trochu podobný je GKE Autopilot a připomíná to i AWS Fargate. Není to špatný krok - ale hlavní důvod komplexnosti Kubernetes nejsou nody, ale Kubernetes... takže to zdaleka není ultimátní řešení.
- **Azure Application Services** - klasický PaaS pro webovky, který dnes funguje i mimo Azure samotný díky Arc (přenositelnost tu tedy je). Alternativou u ostatních cloudů je třeba Google App Engine nebo AWS App Runner. Na webovky naprosto optimální platforma a svůj kód si můžete přinést i ve formě vlastního kontejneru. Nicméně pro mikroslužby, worker nody a další aspekty to nemusí být ideální - nemůžete například jednotlivé služby v clusteru (App Service Plan) škálovat nezávisle jednu na druhé, mít jednoduchou vznitřní komunikaci služeb mezi sebou s definicí které jsou dostupné zvenku, které jen interně apod. Dá se to tak použít (private linky a tak), ale máte pocit, že to je přiohnuté - platforma je prostě vymyšlená pro běh jednotlivých webovek nebo API serverů. Navíc neumí škálovat do nuly - nevypne se, když nemá co dělat.
- **Azure Functions** - plně optimalizované serverless řešení podobně jako Google Functions nebo AWS Lambda je určitě skvělou volbou, pokud řešíte malinkaté součástky kódu, které reagují na události. Pravidelné přetažení dat odněkud někam, zavolání funkce pro nějakou úpravu datové věty v rámci nějakého zpracování, provolání kódu když se stane nějaká událost, anomálie nebo přijde zpráva z IoT zařízení - skvělé příklady. Můžete si přinést i svůj kontejner, ale musíte mít nějaké předem definované SDK, základní image nebo psát kód v podporovaném jazyce. Funkce lze pouštět třeba i ve vlastním Kubernetes mimo Azure díky Arc. Napsat takhle klasickou aplikaci vede na stovky funkcí a velký masakr. Ano, je to ultimátní serverless s úžasnou škálovatelností, ale use case je docela vyhraněný a nezdá se, že by se rozšiřoval na generické mikroslužbové appky.

Azure Container Apps je nová a za mne velmi zajímavá možnost - neřešíte infrastrukturu a složitosti Kubernetu, současně máte jeho flexibilitu co do používání libovolných kontejnerů a workerů a přitom máte serverless řešení, které umí škálovat do nuly. Tohle je cesta, která bude mnoha lidem vyhovovat. AWS přímou alternativu nemá (Fargate je spíš clusterless šelmostroj a App Runner je zase spíš PaaS a neškáluje do nuly), u Google k tomu má nejblíž Cloud Runner. Container Apps mají pod kapotou Kubernetes + KEDA + DAPR zatímco Cloud Runner tam má Kubernetes + KNative s Istio. 

Obrovská síla je v použitých komponentách tam kdesi uvnitř. KEDA umožňuje serverless chování nejen pro webové aplikace, ale i workery čtoucí z fronty apod. Škálovat lze na základě všeho možného - to je přímo vlastnost KEDA. A pro funkce připomínající aplikační platformu je tu DAPR, který nabídne věci jako service discovery a retry, state store, messaging mezi službami, externí triggery a outputy (včetně podpory jiných cloudů a on-prem technologií) nebo actor model.

To všechno si projedeme později - zkusme začít jednoduše a pomalu. Prostě si pojďme něco naklikat, k detailům se vrátíme jindy.

# Nejlépe vyzkoušet - pár kliknutím udělám to, co by jinak vyžadovalo masivní znalosti Kubernetes a jeho ekosystému
Dnes zůstaneme o jednoduchého klikacího průvodce. Vytvořím novou službu service1.

[![](/images/2021/2021-11-25-08-27-50.png){:class="img-fluid"}](/images/2021/2021-11-25-08-27-50.png)

Nemám ještě žádný Container App Environment - založíme. Jde o prostředí, ve kterém se moje služby mohou vidět mezi sebou - berme to třeba něco jako clsuter nebo namespace.

[![](/images/2021/2021-11-25-08-28-30.png){:class="img-fluid"}](/images/2021/2021-11-25-08-28-30.png)

[![](/images/2021/2021-11-25-08-28-59.png){:class="img-fluid"}](/images/2021/2021-11-25-08-28-59.png)

Průvodce je zjednodušený, ale dovolí mi buď nahodit quickstart příklad nebo rovnou můj kontejner. Já mám jeden, který na request vrací verzi a hostname.

[![](/images/2021/2021-11-25-08-30-45.png){:class="img-fluid"}](/images/2021/2021-11-25-08-30-45.png)

Moje aplikace není worker, který jen běží na pozadí a třeba zpracovává nějaké události z fronty, takže chci aby byla dostupná síťově. Můžu vybrat zda pouze interně (v rámci služeb, které jsou ve stejném Container App Environment) nebo zvenku (třeba frontend) - integrace do vlastního VNETu je v plánu a prý bude brzy.

[![](/images/2021/2021-11-25-08-58-59.png){:class="img-fluid"}](/images/2021/2021-11-25-08-58-59.png)

Po chvilce aplikace běží.

[![](/images/2021/2021-11-25-09-14-55.png){:class="img-fluid"}](/images/2021/2021-11-25-09-14-55.png)

```bash
$ while true; do curl https://service1.blueforest-ad25e2a0.northeurope.azurecontainerapps.io/; sleep 1; done
Version 1: service1--qzgja8c-c6c9d7569-v26dw
Version 1: service1--qzgja8c-c6c9d7569-v26dw
Version 1: service1--qzgja8c-c6c9d7569-v26dw
```

Logy se nám sbírají.

[![](/images/2021/2021-11-25-09-17-12.png){:class="img-fluid"}](/images/2021/2021-11-25-09-17-12.png)

Abychom změnili škálování, uděláme novou revizi aplikace.

[![](/images/2021/2021-11-25-09-19-09.png){:class="img-fluid"}](/images/2021/2021-11-25-09-19-09.png)

Parametry kontejneru nechám stejné.

[![](/images/2021/2021-11-25-09-29-42.png){:class="img-fluid"}](/images/2021/2021-11-25-09-29-42.png)

Aplikace je řekněme asynchronní, takže klidně se může uspat, ať za ní neplatím - nastavím tedy škálování od nula do tří instancí.

[![](/images/2021/2021-11-25-09-21-18.png){:class="img-fluid"}](/images/2021/2021-11-25-09-21-18.png)

Na základě čeho škálovat? Může to být počet HTTP requestů, délka Azure Queue, CPU nebo custom metrika (pod kapotou je KEDA s širokou podporou různých vstupů). Já pro příklad zvolím počet requestů s cílem mít jen jeden per instanci (ať se dobře simuluje škálování).

[![](/images/2021/2021-11-25-09-23-22.png){:class="img-fluid"}](/images/2021/2021-11-25-09-23-22.png)

Poslední v záložce je DAPR a to si necháme na jindy. To je velmi mocná záležitost umožňující aplikaci se jednoduše napojit na události venku (triggery),  posílat výstupy do podporovaných komponent (Azure Blob, S3, různé fronty), provolávat bezpečně služby mezi sebou (včetně retry), nasadit actor model, ukládat state nebo si posílat zprávy mezi komponentami. Víc informací najdete i tady na mém blogu: [https://www.tomaskubica.cz/tag/dapr/](https://www.tomaskubica.cz/tag/dapr/).

[![](/images/2021/2021-11-25-09-25-02.png){:class="img-fluid"}](/images/2021/2021-11-25-09-25-02.png)

Revize mám nastavené tak, že jich může být víc aktivních současně (tzn. teď mi běží oba Pody) - nicméně provoz jde ze 100% na novou revizi.

[![](/images/2021/2021-11-25-09-33-32.png){:class="img-fluid"}](/images/2021/2021-11-25-09-33-32.png)

Starou revizi mohu deaktivovat - k tomu jak použít víc revizí současně se ještě vrátíme.

Začnu generovat trochu víc přístupů a vidím, že mi odpovědi chodí ze tří instancí.

```bash
$ while true; do curl https://service1.blueforest-ad25e2a0.northeurope.azurecontainerapps.io/; sleep 0.2; done
Version 1: service1--rev2-76d8fc447-8lrdr
Version 1: service1--rev2-76d8fc447-8lrdr
Version 1: service1--rev2-76d8fc447-4clq9
Version 1: service1--rev2-76d8fc447-lkjzl
Version 1: service1--rev2-76d8fc447-lkjzl
Version 1: service1--rev2-76d8fc447-8lrdr
Version 1: service1--rev2-76d8fc447-lkjzl
Version 1: service1--rev2-76d8fc447-lkjzl
Version 1: service1--rev2-76d8fc447-lkjzl
Version 1: service1--rev2-76d8fc447-4clq9
Version 1: service1--rev2-76d8fc447-4clq9
Version 1: service1--rev2-76d8fc447-8lrdr
Version 1: service1--rev2-76d8fc447-8lrdr
```

To potvrzuje i GUI.

[![](/images/2021/2021-11-25-09-36-04.png){:class="img-fluid"}](/images/2021/2021-11-25-09-36-04.png)

Přístupy vypnu a počkám pár minut - řešení se seškálovalo na nula instancí.

[![](/images/2021/2021-11-25-09-42-52.png){:class="img-fluid"}](/images/2021/2021-11-25-09-42-52.png)

Perfektní, teď tedy vůbec neplatím. Zkusme za jak dlouho se Pod rozsvítí.

```bash
time curl https://service1.blueforest-ad25e2a0.northeurope.azurecontainerapps.io/
Version 1: service1--rev2-76d8fc447-9hnt2

real    0m20.679s
user    0m0.035s
sys     0m0.001s
```

Takže zhruba 20 vteřin - to není špatné na kontejnerovou platformu. Samozřejmě takové Azure Functions zvládnou studený start výrazně rychleji, jsou na to dělané. Ale na kontejnerovou platformu je 20 vteřin z neplatím nic na platím jednu instanci docela fajn. Pokud potřebuji rychlejší reakci, škáloval bych dolu pouze do jedné instance s tím, že z finančního hlediska pokud tato nepřijímá žádná requesty, je účtována ze slevou (v podstatě dál platíte stejný poplatek za paměť, ale pokud nedostáváte žádné requesty na službu s jednou instancí máte CPU za dramaticky nižší cenu).

Vývojáři připravili novou verzi aplikace, pojďme ji nasadit jako novou revizi.

[![](/images/2021/2021-11-25-09-48-22.png){:class="img-fluid"}](/images/2021/2021-11-25-09-48-22.png)

Nahozeno, ale 100% provozu směřuje na původní v1 (v rev2 podobě, přidávali jsme tam to škálování).

[![](/images/2021/2021-11-25-09-50-18.png){:class="img-fluid"}](/images/2021/2021-11-25-09-50-18.png)

Co kdybych se teď na to v2 podíval ještě před tím, než ji vypustím mezi lidi? Revize je aktivní, takže někde běží ne?

[![](/images/2021/2021-11-25-09-51-05.png){:class="img-fluid"}](/images/2021/2021-11-25-09-51-05.png)

Má svou speciální URL a mohu tedy udělat A/B testing - pošlu pár známým tohle URL, ať se mrknou, jak se jim nová verze líbí.

```bash
$ curl https://service1--v2.blueforest-ad25e2a0.northeurope.azurecontainerapps.io/
Version 2: service1--v2-888866986-pln5g
```

Vypadá senzačně - co ji opatrně pustit mezi lidi, řekněme třeba 10%?

[![](/images/2021/2021-11-25-09-52-57.png){:class="img-fluid"}](/images/2021/2021-11-25-09-52-57.png)

```bash
$ while true; do curl https://service1.blueforest-ad25e2a0.northeurope.azurecontainerapps.io/; sleep 0.2; done
Version 1: service1--rev2-76d8fc447-zznkq
Version 2: service1--v2-888866986-pln5g
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
Version 2: service1--v2-888866986-pln5g
Version 1: service1--rev2-76d8fc447-zznkq
Version 1: service1--rev2-76d8fc447-zznkq
```

Jsem spokojený, starou verzi jdu deaktivovat.

[![](/images/2021/2021-11-25-09-55-51.png){:class="img-fluid"}](/images/2021/2021-11-25-09-55-51.png)


Takhle tedy vypadají Azure Container Apps, které jsou čerstvě v preview. Příště se podíváme na větší detaily, například jak nasazovat přes YAML, Bicep nebo z CI/CD, jak škálovat na základně externích metrik a používat serverless přístup nejen pro http, ale i workery, vyzkoušíme si v kombinaci s DAPR a budeme sledovat, jak se bude platforma dál rozvíjet a kdy co se objeví. Zkusím si udělat i nějakou finanční rozvahu - kolik je příplatek za serverless, jak vypadá optimální business case vs. provozování v jiné variantě apod.

Mám za to, že platformy, které vám dají flexibilitu vlastních kontejnerů, jednoduchost, přívětivost pro vývojáře i provoz a přitom vás nenutí věnovat se infrastruktuře a spletitým technikáliím Kubernetes a návazných projektů, jsou budoucnost cloudového nasazování aplikací. Beru to jako určitou reinkarnaci klasických PaaS řešení - krása a jednoduchost, ale tentokrát bez ztráty flexibility, přenositelnosti a bez diktátu jak a v čem mám svoje aplikace psát.

