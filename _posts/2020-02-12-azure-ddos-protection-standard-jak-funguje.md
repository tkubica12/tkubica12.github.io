---
layout: post
title: 'Azure DDoS Protection Standard: jak funguje a proč si pořídit'
tags:
- Networking
- Security
---
Azure má k dispozici DDoS ochranu s celkovou kapacitou přes 30 Tbps, což je minimálně 10x víc, než dosud nejsilnější zaznamenaný útok. Jak vás může chránit, jak funguje a proč si pořídit?

Důležitým věcem typu jaký je rozdíl mezi volumetrickým, protokolovým a aplikačním útokem nebo co zahrnuje Azure DDoS Protection Basic (ochrana zdarma) vs. Azure DDoS Protection Standard už jsme se věnoval před nějakým časem a můžete se k tomu vrátit zde: [https://www.tomaskubica.cz/post/2018/azure-ddos-ochrana-pro-vase-aplikace/](https://www.tomaskubica.cz/post/2018/azure-ddos-ochrana-pro-vase-aplikace/). Dnes půjdeme do větších podrobností jak to celé vlastně funguje a proč si to pořídit.

# Jak to funguje
Azure DDoS Standard chrání public IP adresy, které si vytvoříte v rámci IaaS prostředí (PaaS služby mají typicky vlastní DDoS ochranu). Nejčastěji to bude IP adresa vaší Azure Application Gateway, Azure Firewall, bezpečnostního prvku třetí strany (F5, CheckPoint, Fortinet, Cisco, ...), Load Balanceru nebo přímo VM s public IP.

Základem pro zabránění útoku je čištění protékající komunikace. V oblasti aplikačních útoků to obvykle uděláte tak, že veškerá komunikace prochází nějakým zařízením, které hledá aplikační útoky. Dobrým příkladem je Azure Application Gateway ve WAF SKU. Pro volumetrické útoky tahle strategie není vhodná, protože jejich hlavní vlastností je brutální zátěž. Azure je samozřejmě připojen do internetu o několik řádů rychleji, než 30 Tbps, které představuje jeho DDoS kapacita. Typicky tedy potřebujete provoz nechat proudit napřímo, ale sbírat mnoho telemetrických údajů a identifikovat anomálie představující útoky. Jakmile takovou najdete, potřebujete odklonit provoz z přímé trubky na cestu přes scrubbing center, tedy DDoS "bednu" (v uvozovkách proto, že v případě Azure jde o masivně distribuovaný globální systém). Touto telemetrií je typicky IPFIX (NetFlow) ze síťových prvků. Z nich Azure ví, kolik každá IP adresa v Azure dostává paketů a bytů, z jakých IP adres, na jakých portech apod. Je tedy možné na základě těchto informací detekovat neobvyklé chování - neobvykle víc klientů, neobvykle větší provoz a tak podobně. Toto nastavení je tedy skutečně na základě velmi speciálního machine learningu a nemusíte nastavovat a ladit nic ručně. Azure se učí, jak vypadá typický provoz vaší aplikace a predikuje jak bude vypadat následující minutu na základě historického chování a jiných vychytávek daných dlouhodobu zkušeností Microsoftu s tímto typem ochrany (Office365 nebo XBOX jsou chráněny stejně). Díky tomu je Azure schopen velmi rychle identifikovat potenciální útok (logicky do 60 vteřin) a zařídit odklonění provozu přes DDoS "krabičku" (to zvládne za pár vteřin). Velmi rychle tedy začne mitigace problému. A co když je IP adresa vytvořená čerstvě? Pak se Azure pokusí hranici rozumně odhadnout na základě vašeho chování na ostatních IP a podle typu IP (jestli je to load balancer s několik VM za ním nebo jen jednotlivé VM apod.) a na ML-based nastavení přejde zhruba po dvou týdnech.

Výborně, takhle se tedy identifikuje podezřelé zvýšení provozu nebo změna jeho struktury a komunikace se odkloní přes DDoS scrubbing centrum. Prvotní odklonění je na lokální úrovni. Každý Azure region disponuje vlastní DDoS ochranou a primární reakce na útok je mitigace tam, kde služba je (tedy v regionu, kde IP máte). Pokud ale útok pokračuje a je masivní, rozhodne se Azure DDoS Standard automaticky začít globální mitigaci. Tedy pokud útok například vychází z nakažených chytrých žárovek v Jižní Americe a na východním pobřeží severní, začne Azure tento provoz odkloňovat přes DDoS ochranu právě v těchto místech - tedy začne útok mitigovat blíže k jeho zdroji. Díky tomu je celková kapacita ochrany Azure skutečně součtem všech DDoS center a díky tomu se s každým přidaným regionem neustále zvyšuje.

Máme odkloněno, co se bude dít dál? Provoz teď proudí přes systém, který je schopen dělat chytřejší rozhodnutí a do provozu zasahovat. Tak například pokud se někdo pokouší zahltit server novými TCP spojeními, může odpovědět jménem serveru (a ubezpečit se, že klient opravdu touží spojení sestavit, tedy bude v sekvenci pokračovat), může heuresticky koukat na čísla sekvence v TCP hlavičce, analyzovat počty spojení z konkrétních adres nebo portů a omezovat je na rozumnou hodnotu a samozřejmě korelovat informace s threat intelligence, tedy znalostí odhalených špatných hráčů v Internetu. Seznam opatření je pochopitelně širší a Azure DDoS Standard zákazníkům je poskytován pod NDA. Tento mechanismus tedy začne zahazovat komunikaci, která je škodlivá s minimálním dopadem na komunikaci, která je platná (vaši zákazníci přistupující k aplikacím).

Azure DDoS Standard na rozdíl od jiných řešení (například někteří lokální provideři) má následující vlastnosti z pohledu kapacity:
- Celková kapacita je násobně větší, než největší dosud zaznamenané globální útoky. 30 Tbps ochranu si sami neuděláte.
- Tato služba nedělá blackholing. Lokální řešení typicky při velké zátěži přistoupí k přesměrování provozu do černé díry, tedy nestíhají vyhodnocovat (čistit) provoz a začnou ho zahazovat celý, tedy včetně vašich skutečných zákazníků pokoušejících se objednat si produkt.
- Mitigace probíhá tak dlouho, jak je potřeba - pár hodin i pár dnů, nejsou zde omezení.
- Mitigace nemá žádná omezení na počet aplikací, IP adres nebo ochranných akcí
- Azure má SLA s finančním závazkem, že DDoS ochrana je funkční minimálně 99,99% času (ve skutečnosti se ovšem drží na 100%), nejde tedy o nějaké řešení skládající se z jedné krabičky, ale skutečně globální distribuovaná ochrana.

# Co očekávat, když dojde k útoku
V první řadě veškeré telemetrické informace a mitigační reporty získáte bez ptaní rovnou v Azure portálu. U lokálních řešení je dost typické, že tyto reporty pro vás generují ručně a posílají emailem. Azure je samozřejmě plně automatizovaný a tohle všechno je k dispozici v portálu včetně:
- Telemetrie (kolik provozu je, kolik je mitigováno, kolik filtrováno, jaké jsou treasholdy apod.)
- Flow exporty (jak vypadá váš provoz a kdy začala mitigace)
- Analytické reporty
  
![](/images/2020/2020-02-12-07-24-37.png){:class="img-fluid"}

![](/images/2020/2020-02-12-07-24-55.png){:class="img-fluid"}

Tato data lze streamovat do Azure Monitor, Azure Sentinel (SIEM), objevuje se jako alert v Azure Security Center Standard, můžete ukládat do storage nebo přes Event Hub streamovat do SIEM systémů třetích stran jako je QRadar nebo Splunk.

Když jste pod útokem může být potřeba komunikovat s odborníky na DDoS a případně s nimi customizovat mitigaci či jinak spolupracovat na vyřešení útoku. Zákazníci s koupeným Azure DDoS Protection Standard mohou v portálu založit DDoS ticket vážnosti A a kategorie under attack - DDoS inženýr se vám ozve do 15 minut od založení ticketu (tempo obvyklé pro premier podporu, ale pro DDoS je součástí ceny služby).

![](/images/2020/2020-02-12-07-36-55.png){:class="img-fluid"}

# Jak se to platí a kolikrát to musím koupit
O cenách jsem psal v minulém článku, ale rád bych se věnoval některým častým otázkám. Zapnutí DDoS ochrany znamená pořídit si DDoS plán za fixní cenu cca 2500 EUR měsíčně. Tato cena zahrnuje 100 public IP adres (obvykle stačí, protože typicky publikujete aplikace přes nějakou WAF nebo firewall), ale dají se přikoupit další. Podstatné je, že tento plán je pro celého tenanta. V rámci této ceny můžete tedy DDoS zapnout na neomezeném množství VNETů (rozhodující jsou počty public IP, ne VNETů), neomezeném množství subskripcí a v jakémkoli počtu regionů. DDoS plán tedy kupujete jen jednou. Pořizuje se v rámci nějaké subskripce a na ní potom padá účtování této fixní sazby. Obvykle tedy dává smysl to pořídit z centrální hub subskripce. 

Druhá část poplatku je za přenos dat, která ale obvykle bude o řád menší. Do této metriky se započítává pouze odchozí provoz (nebylo by fér počítat přicházející, protože zejména v okamžiku útoku to bude opravdu hodně). Backendová komunikace (třeba plnění datového skladu) bývá typicky řešeno po interní síti (VPN, Express Route), takže na public IP jsou skutečně typicky pouze vaše aplikace, takže traffic poplatek nebude nijak zásadní. 1 TB vyjde asi na 43 EUR. Z pohledu účtování přísluší tyto poplatky IP adrese v její subskripci. Fixní náklad jde tedy do subskripce, kde byl plán založen, ale poplatky za traffic jsou v těch subskripcích, ve kterých se vyskytují příslušné chráněné IP adresy.

Cena tedy může na první pohlad vypadat vysoká, ale chrání celý váš tenant - všechny jeho subskripce, všechny regiony a 100 IP adres v základu.



Pokud jste enterprise firma a vaše klíčové aplikace běží v Azure, nevidím důvod, proč si Azure DDoS Protection Standard nepořídit. Úroveň ochrany je nesmírně vysoková a něco takového si postavit v on-premises je extrémně nákladné a složité. Pokud jste v lokálním hostingu, zvažte migraci do Azure se zapnutou DDoS ochranou - myslím, že výrazně posílíte bezpečnost své aplikace.