---
layout: post
published: true
title: Ty cloudy a přehřáté téma vendor lockinu aneb proč strach některých CIO nehraje v jejich prospěch
tags:
---
Včera jsem měl možnost vstoupit do konference Azure Business Club ukázkou Azure Arc pro multi-cloud a díky tomu jsem si poslechl diskusi významných CIO využívajících cloud. Hodně rezonovalo téma vendor lockin a upřímně řečeno jsem s některými nemohl souhlasit v názoru na nutnost a prostředky obrany. Téma vendor lockin v cloudu je podle mě značně přehřáté. Tady je pár myšlenek.

# Otazník první: Kolik mě stojí řešení lockinu tím, že použiji jen základní infrastrukturní a kontejnerové služby?
Tohle představuje podle mě asi největší náklady ušlé příležitosti ze všech popsaných otazníků. Co vás odlišuje od konkurence? Vaše aplikace, myšleno aplikační kód, tedy to co to dělá a vaše data včetně jejich zpracování, analýzy nebo nasazení strojového učení. Jinak řečeno aplikace a data mají samozřejmě vliv na vaší nákladovou stranu za IT, ale také přímý vliv na vaše příjmy v byznysu. Lepší mobilní aplikace, víc objednávek. Lepší vytěžení dat, lepší personalizace a větší útrata každého zákazníka. A co infrastruktura? Ta má vliv na vaše IT náklady, ne na příjmy v byznysu. Dává mi tedy větší smysl soustředit se na aplikace a data, kde můžu nejen šetřit, ale také vydělávat. 

Co mě tedy stojí prevence lockinu tím, že půjdu do infrastrukturních služeb? Takový Kubernetes je echt infrastruktura - není to platforma pro vývojáře, je komplexní a vyžaduje hodně času a investice do, a to je důležité, zvládnutí aspektů Kubernetu samotného. Místo namíření investic do aplikace a dat, které mohou vydělávat, posíláme lidi vstříc infrastruktuře - na úkor zkoumání serverless, kde bych se mohl soustředit jen na aplikační kód a nebabrat se v patchování, storage, balancování, síťařině, škálování nebo vysoké dostupnosti. To, že se budu soustředit na infrastrukturní služby jistě sníží lockin, ale stojí tato cena za to?

Navíc je tu ještě jeden aspekt. Moderní platformní služby jsou dnes hodně o "lockin" v pohodlí, ne technoogii. Jak může být něco lockin, když to získáte i v jiném cloudu nebo to můžete provozovat v on-premises? Samozřejmě nasadit to u sebe znamená vrátit se do doby, kdy řešíte jak třeba takovou databázi nainstalovat, zálohovat, patchovat a celkově udržet v chodu. Je to nepohodlné, ale vzniká nepohodlností lockin tak jak ho vnímáte jako něco nefér, něco co na vás někdo ušil, nebo vám spíše někdo nabídl pohodlnost a vám se zalíbila? 

# Otazník druhý: Vyřeším lockin tím, že si koupím službu někoho čtvrtého, kdo to umí provozovat ve všech třech hlavních cloudech?
Tohle mi přijde kouzelné. Lockin je jedna věc, ale ke komu je druhá. Mojí největší obavou by bylo, že ten hráč trh prostě opustí, produkt zavrhne, přestane inovovat a tak podobně. U  hráče jako je Microsoft nebo Amazon je takové riziko minimální (u Google vlastně taky velmi nízké, byť Google je proslulý zabíjením služeb, které nevydělávají). Z panické hrůzy před lockin k těmto bezpečným hráčům si najdu technologii firmy s dvaceti zaměstnanci, která ale umí provozovat svoje řešení nad všemi cloudy - tedy lockin udělám k ní. To jsem na vás vyzrál, vy Microsofti a jim podobní, že? Tak teď už jen, aby ta malá firmička nezkrachovala a nevytvořila mi technologický dluh. Stojí to za to?

# Otazník třetí: Když si to raději napíšu sám, nebude žádný lockin, že? 
Klasika. Lockin k někomu, kdo to dělá pro masivní portfolio zákazníků a realizuje tak výnosy z rozsahu a stabilitu z velkých čísel, nahradím lockinem sám k sobě. Často nejhorší lockin, co si dovedete představit. Jasně, teď je to priorita a má to podporu vedení. Vidí váš manažer i na příští rok? A co bude za tři roky? Nezmění se KPI nebo byznys strategie? Bohužel tyhle situace prakticky vždy vedou k tomu, že za dva roky je ten váš systém mimo realitu okolního světa, stojí víc peněz, než jsou manažeři ochotni investovat a buď se dáte do přechodu na něco jiného nebo se rozhodnete technologický dluh ignorovat, dokud se to nesesype celé. Je to jako dát si krabici s bordelem do chodby. Po čase si zvyknete se kolem ní protahovat, ale každé návštěvě bude jasné, že vám to fakt škodí.

# Otazník čtvrtý: Musím se bránit lockinu, protože jinak mi zdražíte, no ne?
Manažeři si živě pamatují doby licencí a vysoko maržových krabic. Nejdůležitější je vztah s obchodníkem, protože pak vyjednám slevu 70%. Licence nebo storage mi prodají se super slevou, ale až budu navyšovat jádra nebo přidávat disky do pole, osolej mě. Obávám se však, že cloud byznys funguje jinak.

Znalost šetří víc než sleva. Pokud jsem schopen dobře predikovat svoje potřeby a pořídit si rezervované instance, dostanu na ně takovou slevu, o jaké se vám v obchodním jednání o cloudových cenách nebude ani zdát. Vyjednávání ovlivňuje třeba jednotky procent, ale rezervace vám dají třeba 60%. Nebo na to můžu jít jinak - optimalizovat svou technickou architekturu. Proč mám platit za trvale běžící zdroje, když je nepotřebuji trvale konstantně využívat. Serverless má jednoznačně větší jednotkovou cenu přepočítanou na tik procesorového času, než třeba VM. Jasně. Ale moje měsíční efektivita využití CPU bude zcela běžně na úrovni 2-5% u VM a třeba 20-40% u běžné kontejnerizace (beru někoho, kdo má znalosti na úrovni řekněme jen jednoho roku provozu produkčního workloadu v Kubernetes). V serverless jdou vaše náklady ze 100% do reálné spotřeby - vyšší jednotková cena se tedy i tak může dost vyplatit, když nejste schopni stejnou efektivitu dosáhnout na VMku (a konkurujete těm nejlepším na světě - 1000 nejlepších lidí na planetě na technologii X půjde pracovat do Microsoftu, Amazonu, Googlu, Facebooku, Netflixu apod., protože kromě nejlepších podmínek si užijí i výzvu, škálu a rozvoj, který jim pravděpodobně dopřát nemůžete). Jinak řečeno vaším největším nástrojem snížení nákladů jsou technické schopnosti a architektura, ne obědy s obchodníkem. Technické zdroje, které vám může dát vendor k dispozici na konzultace, mají možná větší finanční cenu, než si uvědomujete.

Sleva z obchodního jednání je tedy méně důležitá, než dřív, ale roli samozřejmě hraje. K tomu přidejme to, že se v tomhle byznysu katalogové ceny obvykle nezvyšují. U licencí se to stává. Oracle investoři začnou remcat, že ten jejich cloud nemá úspěch a vyřeší se to zdražením licencí a hned dobré finanční výsledky investory uklidní (i když product mix zůstane legacy, ale který investor řeší, co bude za pět let). Reálně tedy - katalogová cena se nezvyšuje, největší dopad na cenu mají technické aspekty a plošná sleva není závratně velká. Ve finále se tedy hraje jen o tu plošnou slevu, jejíž důležitost je úplně jinde, než za dob necloudových. V rámci vyjednávání se ale sleva bude asi odvíjet primárně od výše vašeho závazku (utratím s vámi tolik a tolik v průběhu tří let) a z růstu (moje spotřeba cloudu vzroste o 50% každý rok). Silná vyjednávací pozice ve smyslu já nemám lockin a můžu přejít jinam jistě roli hraje, ale celková velikost a růst taky. 

Shrnuto - absence lockinu mojí pozici zas tak moc nevylepší. Primární zdroje úspor jsou znalosti a ceny se nezvyšují, takže hrajeme jen o relativně malou slevu, ve které ale kromě schopnosti odejít hraje zásadní roli i velikost závazku a růst. Přínosy obrany před lockinem tak obávám se nevyvažují náklady tím vzniklé (viz první otazník).

# Je tedy vendor locking to hlavní pro multi-cloud?
Za mě ne. Tím driverem by měla být spíš schopnost udržet se ve střehu, mít přehled a vědět tak, že mám i jiné možnosti (slavná BATNA - Best Alternative to Negotiated Agreement). Mít schopnost využít unikátních vlastností jiných cloudů, třeba díky regionu v oblasti, kde ostatní nejsou, kvůli službě co ostatní nemají, licenční výhodnosti, podpoře češtiny v AI službách, dostupnosti technických lidských zdrojů apod. Jasně, je i opravdu hodně zásadních nevýhod multi-cloud, ale o těch tento článek není. 

Není to tedy o hledání nejmenšího společného jmenovatele a tím pádem škrtnutí inovací, kvůli kterým bych měl do cloudu jít. 



Vendor lockin je něco, co je přirozené a podle mě platí, že:
- je rozdíl v tom ke komu nebo čemu lockin dělám
- lockin sám k sobě je taky lockin a to dost podstatný
- lockin není ano/ne, ale škála, tedy může působit trochu, středně i hodně, podle toho co a jak použiji
- lockin v pohodlnosti není apriori nežádoucí nebo nefér
- lockin má i zásadní přínosy, ty je vhodné chápat a započítat
- lockin má v dnešní době menší podíl na vašich nákladech, tím nejdůležitějším jsou v cloudu znalosti
