---
layout: post
published: true
title: "Azure Defender (2): Jaké je vaše bezpečnostní score a co můžete udělat pro jeho zlepšení"
tags:
- Security
---
Minule jsme si představili Azure Defender a konzoli Azure Security Center. V následujících třech dílech se zaměříme na správu a hodnocení vašeho prostředí co do bezpečnost, tedy na Cloud Security Posture Management. Dnes to bude bezpečnostní score, jak s ním pracovat, zakládat výjimky a hlavně jak ho doporučuji pojmout myšlenkově a procesně. V příštím díle si ukážeme integraci řešení do vašich procesů a nástrojů a pak se ponoříme více pod kapotu, pod kterou pracují na plné obrátky Azure Policy a ukážeme si jak je využít pro prevenci a také přijít s vlastními iniciativami a zařadit je do celkového CSPM obrázku. Jakmile si takto proběhneme CSPM, vrhneme se na aktivní ochranu a CWPP.

Znovu musím připomenout, že řešení je hybridní, tedy funguje i pro onpremises systémy připojené přes Azure Arc. To oceníte zejména u ochrany serverů, SQL serverů a Kubernetes clusterů běžících kdekoli. Pochopitelně ale u onpremises zdrojů nedokáže Azure Defender poradit s nastavením sítě apod., protože do toho nevidí.

# Bezpečnostní score a jak o něm přemýšlet
Herním prvkem celého Azure Defender je zobrazení bezpečnostního skóre. Vidíte údaje pouze za ty zdroje, ke kterým máte přístup, takže jednotlivé týmy mohou mít přístup do Azure Security Center aniž by viděly ostatní a současně bezpečnostní tým může vidět všechno. Pokud máte na danou subskripci Security Reader, vidíte doporučení, ale nemůžete dělat výjimky nebo měnit nastavení. Security Admin má plná práva. Všimněte si tedy že bezpečnostní tým pokud nechcete nemusí mít právo modifikovat samotné vaše zdroje.

[![](/images/2020/2020-11-30-06-10-48.png){:class="img-fluid"}](/images/2020/2020-11-30-06-10-48.png)

V detailech se pak dozvíme jednotlivé oblasti doporučení a konkrétní kroky, ale k tomu se ještě dostaneme.

[![](/images/2020/2020-11-30-06-12-30.png){:class="img-fluid"}](/images/2020/2020-11-30-06-12-30.png)

Jak doporučuji o score přemýšlet? Především tohle není provozní monitoring, aby k vašemu přežití muselo být všechno zelené. Pozakládat stovky výjimek jen abychom ukázali, že máme 100% není dobrý nápad. Určitě je vhodné aspirovat na co nejvyšší score, ale cesta k tomu někdy není jednoduchá. Může znamenat náklady na předělání zdrojů, změnu způsobu práce nebo pořízení nových služeb a přestože dlouhodobě se na 100% dostat chcete, není nutné nebo ani proveditelné této mety dosáhnout zítra. Klíčem je podle mě sledování trendu vašeho skóre. Pokud dlouhodobě stagnuje nebo dokonce klesá, není to dobrá zpráva. Snažte se třeba každý kvartál svoje score vylepšit a začínejte od doporučení s největší bodovou dotací. Azure Defender na základě bezpečnostních výzkumů a zkušeností dává každé kategorii jinou váhu, která je doporučením Microsoftu a pokud nemáte jiný názor, doporučuji jej následovat.

Jak se tedy dívat na výjimky a kudy vlastně do toho?
- Rozdělte si svá prostředí do subskripcí, ty sdružujte do Management Group a podle nich nastavujte přísnost vašich pravidel. Obvykle potkávám následující 4 kategorie aplikačních subskripcí:
    - Sandbox izolovaný od firemní sítě, kde obvykle nevidím nutnost bezpečnost řešit technicky, ale spíše z pohledu řízení nechť je všem jasné, že zákaznická data tu být nesmí stejně tak jako klíče a hesla do skutečných systémů.
    - Dev prostředí připojené do firemní sítě, ale bez zákaznických dat. V takovém případě bych nechal vývojářům určitou volnost, abych nesnižoval jejich produktivitu, takže například přímý přístup vývojáře do databáze z jeho notebooku bych toleroval apod. Nicméně vystrčení RDP s mašinou se slabým heslem do Internetu pro mě představuje problém, protože se může stát vstupním místem do firemní sítě. Základní pravidla pro bezpečnou komunikaci by tedy v těchto prostředích platit měla.
    - Neprodukční prostředí (test, UAT, preprod), kde už se často pracuje i se zákaznickými daty. To je pro mě signál pro přísnost podobnou produkci. V mnoha nastaveních bych preferoval stejná pravidla jako v produkci, takže například policy pro Kubernetes chci mít stejně (privilegované kontejnery, dostupné registry apod.), aby se tady už lidé chovali "produkčně" a nevznikal problém, že co tady otestuji pak v produkci nebude fungovat. Na druhou stranu co se týče přístupu do databáze chápu, že se tady musí někdy ladit a přístup z notebooku je produktivní. OK, ale pro všechny přístupy vyžaduji MFA a AAD účty, šifrování dat vlastním klíčem případně dynamické maskování sloupečků apod.
    - Produkční prostředí pak bude obsahovat nejsilnější politiky a tady už bez pardonu pokud bude potřeba přistupovat do systémů jako je databáze, tak pouze ze zabezpečeného bastion serveru (Privileged Access Workstation) a že je to pro lidi nepohodlné je mi fuk. Takové přístupy považuji za krizové řešení situace, nikoli něco, co se provádí rutinně, takže bezpečnost má přednost.
- Pokud chcete zakázat celé pravidlo ujistěte se, že je k tomu důvod. Příkladem je, že máte problematiku vyřešenou nějak jinak a možná toto pravidlo nahradíte svým jiným. Tak například Azure může křičet, že na každém VM má být ochrana endpointu. Vy ale používáte nástroj, který Azure nezná a nemůže vědět, že to řešíte jinak. To je ideální kandidát na zákaz pravidla nejlépe s doplněním vlastního.
- Pokud v jedné subskripci máte zdroje, které pravidlu nevyhovují a musí to tak být, vytvořte výjimku pouze na tento zdroj místo zrušení celého pravidla. 
- Jste-li v červeném a chápete, že je to problém, ale nemáte teď možnost to řešit, nechte to červené. Přelakovat vše na zeleno zrušením pravidel problém nevyřeší. Pokud po vás někdo chce 100% score od prvního dne, proberte to s ním a rozumějte nákladům na zvýšení score a potřebnému času. Snažte se společně maximalizovat přírůstek skóre tím, že se zaměříte na nejdůležitější aspekty a budete kontinuálně pracovat na zvyšování.

Ještě musím upozornit na jednu taktickou záležitost. Doporučení jsou sdružena do kategorií a body dostanete až když odstraníte všechny nedostatky v dané kategorii. Pokud máte v domě 8 oken a pro ochranu před zloději je potřebujete mít zavřená, nedává smysl vás chválit za to, že máte otevřené jen jedno. Secure score funguje stejně. Okna jsou kategorie a body dostanete až budou zavřena všechna, protože jistě budete těžko vysvětlovat pojišťovně, že má většinu škody zaplatit, protože jste přece zavřeli 7 oken z 8 a to je daleko lepší, než jich zavřít jen 5.

# Bezpečnostní doporučení, jejich odstranění a výjimky
Podívejme se na kategorie doporučení a jak s nimi pracovat.

[![](/images/2020/2020-11-30-06-44-06.png){:class="img-fluid"}](/images/2020/2020-11-30-06-44-06.png)

Referenční list všech doporučení je v [dokumentaci](https://docs.microsoft.com/en-us/azure/security-center/recommendations-reference)

Takhle třeba vypadá bodově vysoce hodnocená kategorie zranitelností.

[![](/images/2020/2020-11-30-06-45-55.png){:class="img-fluid"}](/images/2020/2020-11-30-06-45-55.png)

Některá doporučení mají i tlačítko na rychlé vyřešení problému.

[![](/images/2020/2020-11-30-06-49-13.png){:class="img-fluid"}](/images/2020/2020-11-30-06-49-13.png)

Na logiku jak rychlé vyřešení funguje se můžu podívat - jde typicky o ARM šablonu, která například v tomto případě zajistí nalodění Kubernetes do Azure Policy.

[![](/images/2020/2020-11-30-06-50-23.png){:class="img-fluid"}](/images/2020/2020-11-30-06-50-23.png)

Můžu tedy clustery označit a kliknout na Remediate.

[![](/images/2020/2020-11-30-06-50-59.png){:class="img-fluid"}](/images/2020/2020-11-30-06-50-59.png)

Ještě je tam tlačítko Trigger Logic App, které slouží pro automaticky nebo v tomto případě manuálně spuštěné vlastní workflow - o tom se pobavíme v příštím díle detailněji.

Některá doporučení jsou velmi komplexní a jejich řešení vám zabere jistě víc času. Tak například takhle vypadají zranitelnosti odhalené zabudovaným Qualys v rámci Azure Defender.

[![](/images/2020/2020-11-30-06-52-54.png){:class="img-fluid"}](/images/2020/2020-11-30-06-52-54.png)

[![](/images/2020/2020-11-30-06-53-21.png){:class="img-fluid"}](/images/2020/2020-11-30-06-53-21.png)

[![](/images/2020/2020-11-30-06-53-39.png){:class="img-fluid"}](/images/2020/2020-11-30-06-53-39.png)

U těchto zranitelností můžete chtít vytvářet výjimky. Například se chcete zabývat jen těmi kritickými.

[![](/images/2020/2020-11-30-07-31-50.png){:class="img-fluid"}](/images/2020/2020-11-30-07-31-50.png)

Postupně se do Azure Defender zavádí i možnost jednoduše nechat vynutit některé nastavení proaktivně politikou (Azure Policy se budeme do detailu věnovat příště).

[![](/images/2020/2020-11-30-07-35-45.png){:class="img-fluid"}](/images/2020/2020-11-30-07-35-45.png)

[![](/images/2020/2020-11-30-07-36-03.png){:class="img-fluid"}](/images/2020/2020-11-30-07-36-03.png)

Představme si dále, že v produkci jsou management porty pravidlem v NSG uzamčeny jen pro přístup z jump serveru (bastion) a pro něj používáte specializované řešení ve formě VM. Je logické, že tato VM musí mít porty otevřené ne snad nutně do Internetu, ale do vnitřní sítě určitě. Nebude tedy pravidlu na přísné zamykání vyhovovat a je rozhodně kandidátem na výjimku.

[![](/images/2020/2020-11-30-07-41-42.png){:class="img-fluid"}](/images/2020/2020-11-30-07-41-42.png)

[![](/images/2020/2020-11-30-07-42-36.png){:class="img-fluid"}](/images/2020/2020-11-30-07-42-36.png)

Kromě zranitelností nalezených Azure Defender Qualys enginem doporučuje systém i některé best practice bezpečnostních nastavení operačních systémů.

[![](/images/2020/2020-11-30-07-56-13.png){:class="img-fluid"}](/images/2020/2020-11-30-07-56-13.png)

Ukažme si příklad celkového pravidla, které ve vašem prostředí můžete chtít zcela odebrat. Pro zabezpečení vašeho prostředí je rozhodně doporučeno použít Azure Firewall - nativní cloud-native řešení, nicméně v rámci multi-cloud strategie a jednotné správy jste třeba rozhodnuti používat firewally Fortinet, CheckPoint, Cisco a tak podobně. Toto pravidlo tedy pro vás není relevantní - je validní používat centrální firewall, ale vyřešili jste to nástrojem třetí strany. Pojďme tedy zakázat celé pravidlo. Pod kapotou jsou Azure Policy, kterým se budeme detailněji věnovat příště. Nejdříve se podíváme jaká pravidla máme kde aplikována.

[![](/images/2020/2020-11-30-08-00-09.png){:class="img-fluid"}](/images/2020/2020-11-30-08-00-09.png)

[![](/images/2020/2020-11-30-08-00-33.png){:class="img-fluid"}](/images/2020/2020-11-30-08-00-33.png)

Politika je přiřazena Security Centerem, ale mohu do ní libovolně sáhnout. Dává například smysl ji přiřadit spíše na úrovni management group, pokud je používáte. Jde to i druhým směrem - pokud nedodržujete typickou architekturu s vícero subskripcemi (například z důvodu, že jste malá firma s jednou subskripcí placenou kreditkou) můžete odebrat politiku ze subskripce a přiřadit ji per resource group a řešit rozdíly na této úrovni. Další možností je, že máte v subskripci speciální resource group, kde potřebujete některé kontroly zcela vypnout. Pak můžete modifikovat assignment na úrovni subskripce tak, že resource group bude výjimka a na její úrovni si přiřadit politiku upravenou jinak.

[![](/images/2020/2020-11-30-08-02-34.png){:class="img-fluid"}](/images/2020/2020-11-30-08-02-34.png)

Tento assignment můžeme modifikovat a v parametrech jsou atributy každého pravidla.

[![](/images/2020/2020-11-30-08-04-25.png){:class="img-fluid"}](/images/2020/2020-11-30-08-04-25.png)

[![](/images/2020/2020-11-30-08-04-52.png){:class="img-fluid"}](/images/2020/2020-11-30-08-04-52.png)

# Regulatorní pohled
Doporučení a nalezené zranitelnosti lze nahlížet také ve struktuře dané standardy pro regulatorní nařízení. To může být velmi praktické.

[![](/images/2020/2020-11-30-08-10-39.png){:class="img-fluid"}](/images/2020/2020-11-30-08-10-39.png)

Kromě těch, co jsou zapnuté automaticky, lze přidat i další - například HIPAA pro zákazníky ze zdravotnictví.

[![](/images/2020/2020-11-30-08-11-46.png){:class="img-fluid"}](/images/2020/2020-11-30-08-11-46.png)

[![](/images/2020/2020-11-30-08-12-07.png){:class="img-fluid"}](/images/2020/2020-11-30-08-12-07.png)

[![](/images/2020/2020-11-30-08-12-32.png){:class="img-fluid"}](/images/2020/2020-11-30-08-12-32.png)

Takhle vypadá report na ISO 27001.

[![](/images/2020/2020-11-30-08-13-06.png){:class="img-fluid"}](/images/2020/2020-11-30-08-13-06.png)


Dnes jsme si vyzkoušeli práci s bezpečnostním skóre, doporučeními, jejich správou a pohledem na regulatorní opatření. Příště se budeme soustředit na integraci řešení do vašich procesů a nástrojů a pak nás čeká více detailů o Azure Policy a možnosti vytváření vlastních pravidel pro Azure Security Center.