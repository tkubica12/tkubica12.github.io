---
layout: post
published: true
title: Začínáme s OpenTelemetry pro standardizovaný aplikační monitoring
tags:
- Monitoring
- Apps
- OpenTelmetry
---
Minule jsem se věnoval ucelenému pohledu na aplikační monitoring a dnes bych rád začal s OpenTelemetry - standardizovaným open source řešením jak z hlediska specifikace API, tak samotné implementace v podobě SDK. Na backendu můžete mít Azure Monitor, New Relic, Datadog, Dynatrace, X-Ray, Jaeger a spoustu dalších řešení.

OpenTelemetry je open source projekt řízený CNCF a jeho zakládajícími členy jsou Google, Microsoft, Dynatrace a Omnitron (dnes Splunk). Dnes každý backend co znám deklaruje podporu tomuto standardu a to včetně jmen, která na seznamu příspěvků k projektu (a nutno říct jako obvykle) chybí.

# Traces, metrics, logs
Minule jsme definovali svatou trojici aplikačního monitoringu - trasování, metriky a logy. Z pohledu OpenTelemetry má projekt dost jasný názor na první dvě zmíněné, ale v oblasti logů je teprve na začátku - ale k tomu se dostaneme.

## Trasování a propagace kontextu
API definuje TraceProvider (základní zapouzdření s konfigurací), Tracer a pak jednotlivé Spany. Každý span, tedy řekněme například zavolání nějaké downstream služby přes REST API, má definovanou strukturu, která zahrnuje jméno, span kontext, identifikátor rodiče (typicky ve formě jeho span kontextu), typ spanu (client, server, asynchronní producer či consumer) a pole s linky na jiné spany. Pojďmě se u některých zastavit.

Proč mít Link na jiné spany, které dokonce mouhou být z jiného trace? Jednou ze situací může být dávkové zpracování. Můj span vznikne na základě padesáti předchozích spanů a data zpracovává najednou a v jeho spanu tak chceme uvést souvislost s těmi předchozími - Link je dobré místo jak to udělat v takových fan-in situacích. 

Span kontext zahrnuje ID trace, ID spanu, volné pole Statetrace pro vstřikování dalších třeba proprietárních hodnot a standardní flagy, kde je zatím jen jeden - sampled (o tom později). Kontext a reference na rodičovský kontext musí mezi voláními putovat. V případě HTTP spojení je to definováno ve W3C specifikaci pro trace context na HTTP (specifikaci připravil Microsoft, Google a Dynatrace). Trochu složitější je to v situaci, kdy jde komunikace přes nějakou frontu, která může používat úplně jiné protokoly (AMQP, MQTT, Kafka). Tam si buď musíte poradit sami (předat si kontext v metadatech zprávy a v příjemci si ho vyzvednout a založit další span), spolehnout se na implementaci v příslušném SDK pro frontovací službu a to vzhledem k nedostatku standardizace může být trochu problém mimo nějaký ekosystém (Microsoft SDK pro Azure Service Bus asi může rozumně emitovat spany do Azure Monitor, ale jiné kombinace na tom budou hůř). W3C začíná standardizovat i v této oblasti, takže už existuje specifikace pro předávání kontextu v AMQP a MQTT a opět je u toho Microsoft, Google a Dynatrace, tak to snad dobře dopadne i z pohledu implementací.

## Sampling
Posílat kompletně celé trasování pro každé volání může být dost náročné na výpočetní prostředky i místo (a tím náklady) ve vašem backendu. Někdy tedy dává smysl netrasovat všechno, ale jen "něco". Sofistikovanost výběru zatím není nativně v OpenTelemetry nějak fascinující, ale o tom později. Podstatné je, že ta komponenta, která zakládá nový trace se může rozhodnout, jestli to udělá nebo ne na základě nějakého pravidla. Pokud se rozhodne, že pro tento request se nic trasovat nebude, musí tohle signalizovat dál nastavením příslušné hlavičky ve span kontextu. Downstream služby dostanou informaci, že rodič si nepřeje tohle někam dál posílat a totéž předají svým případným dětem. Jako služba tedy buď nedostanete na vstupu informaci vůbec žádnou a pak asi založíte nový trace (resp. zvážíte to svou sampler funkcí). Pokud na vstupu máte informaci, že rodič trasuje (flag record a sampled), uděláte totéž (nemůžete rozhodovat svým samplerem, to by pak půl informací chybělo) a pokud rodič říká neukládat, tak stejnou informaci předáte i svým dětem. 

Zabudované samplery jsou vždy ano, vždy ne a pravděpodobnost. Můžete tak říct, že záznam se začne s pravděpodobností třeba 1%. Náhodným výběrem máte šanci na férové statistické zastoupení událostí ve vzorku. Jiná řešení (a snad někdy v budoucnu i OpenTelemetry) mají další techniky jako je fixní sample (každý x-tý request) nebo (a to mi připadá jako výborná věc) adaptivní sampler, který zajistí např. alespoň 2 samply za vteřinu (takže i málo zatížené služby poskytují rozumná data a pokud se zatíží, začne se samplovat) a dokáže se na to dívat per rodič (takže jako služba zachytíte i trasy z upstream služby, která se volá výrazně méně, než jiná a přitom obě používají stejný downstream). Potenciálně si můžete představit další zajímavé techniky realizované až na kolektoru. Například je tak možné sbírat všechno, ale do backendu odesílat až nějaké vybrané zajímavé situace (když to trvá déle než vteřinu, když je počet vnořených spanů větší než 5 nebo když je někde v jakékoli odpovědi řetězce chyba 500 posílat všechno).

## Metriky
OpenTelemetry definuje API a SDK na sběr metrik včetně přidávání metadat ve formě atributů, což může být výhodné pro rozeznání třeba verzí aplikace a tak podobně. 

## Logy
Zatímco trasování a měření je v projektu už jasně zakotveno (ostatně vychází z předchozích zkušeností v OpenCensus a OpenTelemetry), s logy je to složitější. Formát trasování umožňuje ke spanu přidat pole events, což mohou být různé textové zprávy a fungovat vlastně jako logování. Projekt počítá s tím, že bude existovat mnoho aplikací, které budou chtít nadále využívat stávající logovací frameworky a má rozmyšlenu vzájemnou koexistenci nebo integraci přes exportér. Na druhou stranu má projekt názor na to, jak moderní logování může vypadat a tak tuto komponentu řeší jako volitelnou součást standardu. V každém případě v této oblasti zatím není pevně rozhodnuto. Co ale je k dispozici je definice datového modelu pro log. Ten definuje klasické součásti jako je jméno, tělo zprávy, severity a samozřejmě časové razítko. K tomu přidává aspekty typické pro OpenTelemetry, tedy resource, atributy (či chcete-li tagy), mapování na trace ID a span ID.

# Jak pošle OpenTelemetry data do mého monitorovacího systému?
OpenTelemetry je standardizovaný otevřený způsob jak data získávat a v jakém formátu s nimi pracovat (je to API i SDK), nicméně určitě je chceme namířit do nějakého systému pro jejich zpracování, vizualizaci, vyhledávání či strojové učení. V mém případě to bude jistě Azure Monitor, ale můžete třeba volit ZipKin, Jaeger, Datadog, Dynatrace, X-Ray a tak podobně. Jak tedy data poslat tak, aby mu cílový backend rozuměl?

## Exporter
První variantou může být použít exportéru konkrétního dodavatele, například Azure Monitor. To jak sbíráte různá data, generujete vlastní metriky nebo spany se nijak nemění a zůstává univerzální. Do OpenTelemetry SDK ale přidáte balíček konkrétního exportéru a přímo váš kód pak dokáže data posílat třeba do Azure Monitor. To má určitě výhody:
- Aplikace sama nemá žádné dependence. Jednoduše vezmete třeba její kontejner a pustíte v jakékoli platformě kdekoli na světě a v Azure Monitor se začnou objevovat vaše data. Je jedno, jestli jde o VM v on-premises, kontejner v Azure App Service for Linux, Azure Kubernetes Service, Azure Container Instances, řešení v nějakém jiném cloudu nebo třeba malý počítač přímo v továrně ať už je to Azure Stack Edge nebo průmyslové pecko.
- Každá instance aplikace je svou vlastní failure doménou. Moc nehrozí, že se data ztratí někde po cestě v nějakém překladači nebo že vypadne nějaká sbírací komponenta a přestane se monitorovat stovka instancí.

Jsou ale zřejmé i nevýhody:
- Exportér je in-process a je součástí buildu. Pokud chcete vyměnit backend, musíte překompilovat (nebo počítat se všemi variantami v kódu). To nemusí vadit u interního vývoje (jak často budu měnit backend pro monitoring), ale pokud jste dodavatelé software pro víc zákazníků, každý může chtít něco jiného.
- Pokud je potřeba data agregovat, musí to dělat aplikační proces (u některých jazyků to ani dobře nejde - třeba PHP), retry (při výpadku spojení s backendem), bufferování nebo šifrování taky. 
- Možná by exportér dokázal data nějak obohatit na základě informací z podkladového prostředí (např. na kterém hostiteli instance běží, v jaké zóně dostupnosti, v jakém regionu, pokud jde o edge na jakém místě v továrně apod.) a ne vždy takové údaje bude mít proces k dispozici (většina moderních řešení nabízí buď nějakou metadata službu jako Azure pro VMka nebo možnost vkládat údaje jako proměnné prostředí jako Kubernetes - ale ne vždy je budu umět použít, ne vždy tam budou a ne vždy tam bude všechno co hledám). 

## Collector
Exportér můžete nastavit do univerzálního formátu OTLP a posílat do instance kolektoru. V procesu aplikace tedy generujete spany a metriky, ale jejich výstup posíláte někam jinam, na separátní proces - kolektor. Ten dokáže přijímat data v nativním OTLP formátu, ale podporuje i jiné vstupy (např. OpenCensus, Zipkin či Jaeger, pokud máte z minulosti tyto implementace), v pipeline dokáže provádět nějakou logiku (třeba agregaci) a následně posílat do koncového systému přes exportér. Tato komponenta je tedy překladiště, které si vezme za úkol napojení na backend, buffering nebo agregaci, možná i obohacení dat o další topologické informace (jméno Podu apod.), takže nemusíte nic měnit v kódu, když se rozhodnete něco z toho nahradit. Kolektorů může být mnoho (běží jako sidecar uvnitř Podu - oddělili jste tak exportér od hlavního procesu pro potřeby přidělování zdrojů a výměnu exportéru bez nutnosti buildovat aplikaci, ale stále nemusíte nic posílat po síti nebo řešit vysokou dostupnost), ale možná bude efektivnější mít třeba na každém Kubernetes nodu jen jeden (Daemonset), takže spotřebováváte míň zdrojů a nemusíte přenasazovat Pody při změně na kolektoru, ale stále naposílat nic mimo samotný node, ale můžete ve finále zvolit i plně centralizovanou architekturu s jediným kolektorem na celé řešení. To je na vás. 

V čem je výhoda?
- Nemusíte dělat nový build při změně backendu.
- Máte univerzální aplikační kontejner a jiný monitoring v různých prostředích.
- Některé funkce odebíráte z aplikačního procesu a snižujete tak jeho zátěž a riziko.
- Potenciálně efektivnější alokace zdrojů (vykonaná práce je pořád stejná, ale její vyčlenění umožňuje oddělit limity zdrojů a snížit tak prostor alokovaný "pro jistotu")
- Větší prostor pro předzpracování dat (obohacení, agregace, ...)
- Možnost sjednotit řešení pro aplikace instrumentované různými způsoby (OpenCensus, Jaeger, Zipkin)

Jsou tu samozřejmé i nevýhody:
- Čím větší centralizace, tím větší zpoždění dat, variabilita zpoždění, velikost výpadku monitoringu při chybě.
- Větší zátěž sítě (virtuální v nodu nebo mezi nimi), protože se data posílají nadvakrát.

## Dává smysl používat oboje?
Podle mě někdy ano. Víte, že jeden z exportérů pro metriky je Prometheus? Můžu tak mít jediný mechanismus na vytváření metrik na aplikační úrovni a použít exportér do Promethea in-process (tzn. rozsvítí se u mě ještě jeden http port a na něm budou metriky vystavené pro pull z Promethea) - nemusím řešit specifické knihovny na Prometheus. Uvnitř Kubernetes clusteru to budu sbírat do Promethea, který ale nemám na dlouhodobé uložení, dohled a strojové učení, na to mám něco jako službu s širším záběrem - třeba Azure Monitor. Nicméně Prometheus je blízko a bude mít malé zpoždění, takže se nebudu trápit s jeho perzistencí, ale použiji metriky na škálování Podů v HPA nebo KEDA. A co dlouhodobější a ucelenější pohled? Buď budu přes Azure Monitor sbírat Prometheus (to není problém pro AKS nebo clustery on-prem napojené přes Azure Arc) nebo použiji Azure Monitor exportér na kolektoru pro push model, který můžu v jiných clusterech třeba vyměnit za New Relic.

# Automatická instrumentace
Monitoring můžete do vaší aplikace implementovat na patřičných místech přímým použitím OpenTelemetry SDK. Dokážete tak přesně určovat kdy co a jak se bude reportovat a strukturu si volíte zcela podle sebe. Například pokud máte uvnitř kódu funkci pro nějaké složité zpracování dat z disku, můžete ji obalit spanem aniž jde o nějaké síťově viditelné volání či externí API. Většina vašich potřeb se ale bude předpokládám točit kolem HTTP volání jiných mikroslužeb, přístupů do databáze a zasílání zpráv do front. Nešlo by zařídit, abych nemusel ručně programovat span pokaždé, když k něčemu takovému dojde?

Mohl. A to buď využitím instrumentační knihovny přímo v kódu nebo dokonce automatickou instrumentací bez jakékoli změny kódu.

## Instrumentační knihovny
První variantou jak si práci usnadnit je použít instrumentační knihovnu pro nějaký framework, který ve své aplikaci používám. Tak například vystavuji svá API přes Flask v Pythonu nebo Express v Node? Přistupuji do MySQL přes pymysql? Volám vzdálená API přes requests knihovnu? V těchto případech nemusím volání obalovat vlastním spanem, instrumentační knihovna pro daný framework to dokáže udělat za mě.

Jak to dělá? Typicky využije buď patch nebo hook. První příklad je requests knihovna v Pythonu, pro kterou se (bohužel) musí použít patch. Instrumentační knihovna v zásadě způsobí (a jako neprogramátor se tady mohu dopouštět nějaké nepřesnosti), že v kódu nevoláte requests přímo, ale ve skutečnosti nějaký wrapper. Ten zajistí nahození spanu, předání do requests a pak ukončení spanu s dosazením výsledku. Druhá varianta je využít hook mechanismu, který framework může nabízet. V případě Python je to situace s Flask. Instrumentační knihovna se napojí na jeho hook před a po zpracování požadavku a díky tomu dokáže zajistit vytvoření spanu.

Jaká je výhoda?
- Dokážete velmi rychle instrumentovat aplikaci, která využívá některé z podporovaných frameworků a knihoven, což bude většina.
- Nevzdáváte se možnosti přidat vlastní spany, atributy a metriky pro maximalizaci přínosů monitoringu.

Jsou nějaké nevýhody?
- Stále platí, že musíte změnit kód aplikace. Nijak drasticky, protože do samotných funkcí, kde se něco děje, nemusíte nijak sahat, ale potřebujete zdrojáky a možnost do nich sáhnout.

## Automatická instrumentace bez změny kódu
Řada hostujících platforem nebo přímo jazyků a frameworků umožňuje před samotným spuštěním kódu ovlivnit jeho runtime prostředí. Například Python má, pokud tomu správně rozumím, zabudovanou funkci, kdy při startu aplikace umí natáhnout specifické site konfigurace, tedy vlastně pustit nějaký kód, který ale není součástí aplikace. Podle všeho tento kód může udělát právě totéž co instrumentační knihovna, tedy navázat telemetrie na hook třeba Flasku. Něco na ten způsob je podle všeho dostupné třeba na Tomcat pro Java nebo IIS pro .NET. Těmito technikami dokážete agenta telemetrie vytáhnout z kódu aplikace do něčeho vedle, ale dost blízko na to no, aby to umělo přidat telemetrii do použitých frameworků.

Jaká je výhoda?
- Získáváte trasování a telemetrii aniž byste museli měnit kód.

Jsou nějaké nevýhody?
- Možnosti customizace jsou omezené.
- Prostředí kam nasazujete musí podporovat tuto metodu, takže se snižuje univerzálnost použití.
- Vás framework nebo knihovna musí být přímo podporovaná protento způsob instrumentace.


Dnes jsme se hlouběji podívali do OpenTelemetry a příště už bude na čase si to vyzkoušet. Použiji Python implementaci a Azure Monitor jako backend. Připravte se, brzy začínáme.