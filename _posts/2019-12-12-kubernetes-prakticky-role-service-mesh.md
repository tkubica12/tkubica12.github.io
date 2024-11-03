---
layout: post
title: 'Kubernetes praticky: role Service Mesh'
tags:
- Kubernetes
- Networking
- Security
- ServiceMesh
---
V poslední době je mnoho diskusí kolem konceptu Service Mesh a mnoho lidí se na něj dívá jako ná spásu světa. Něco na tom je, ale nic není zadarmo - roste složitost, latence a spotřeba zdrojů. Stojí to za to? Na to se dnes zkusím podívat.

A jak si mám vybrat implementaci? Budu se věnovat třem nejdiskutovanějším - Istio, Linkerd a Consul Connect. Připadá mi trochu jak před lety vybrat jestli půjdu do Kubernetes, DC/OS nebo Docker Swarm. V jednu chvíli tři dobře vypadající orchestrátory a pokud jste se vydali jedním ze směrů mimo Kubernetes, dnes pravděpodobně uvažujete o přechodu (nebo už jste ho dokončili). Naštěstí z dílny Microsot a dalších open source gigantů jako je Red Hat přichází standard Service Mesh Interface. Díky standardizaci způsobu ovládání libovolného service mesh (vrstva abstrakce implementace) vaše rozhodnutí nemusí být fatální a nebude to na předělávání všeho, když se rozhodnete pro změnu.

# Trubky vs. chytré trubky
Mám mít co nejhloupější trubky (síť), které se soustředí jen na výkon, stabilitu a jednoduchost a pokročilé funkce dávat do endpointů nebo mám jít cestou přidávání pokročilých funkcí do trubek, aby endpointy mohly být hloupé. To je téma, které se řeší posledních minimálně 50 let a řešení se různí ve vlnách. Jenže většinou to dopadlo systémem hloupých trubek. Pojďme si dát příklad proč.

V 80. letech zuřila válka mezi síťovými technologiemi a dva významní zástupci byli ATM a Ethernet. Ten první byly velmi chytré trubky, které podporovaly koncept spojení, zaručovaly kvalitu služby a celou řadu skvělých věcí. Proti tomu Ethernet byl značně primitivní, negarantoval úspěšný přenos a neměl koncept spojení, spíše bral pakety a šoupal je zleva doprava. Díky své složitosti bylo ATM drahé a mělo značné problémy s kompatibilitou mezi výrobci. Jednoduchý Ethernet byl levný a dobře kompatibilní a proto nakonec na celé čáře vyhrál. Jedním z aspektů bylo i to, že díky své ceně a jednoduchosti dramaticky rostla jeho rychlost (pokud přeskočíme první kroucenou dvoulinku tak první rozšířená implementace byla 10 Mbps, dnes naprosto běžně najdete 100 Gbps, už pár let je hotový standard na 400 Gbps a rychlejší se připravují), takže na problém jak řídit chytře provoz v síti se dal jednoduše přihodit 10x větší surový výkon a bylo. A takhle se to opakovalo s každým skokem.

Service Mesh jsou chytré trubky. Proč tentokrát můžou dávat smysl? 
- koncovým bodem není hardware, ale aplikace nejčastěji v kontejneru, tedy svět, který se dá rychle změnit či opravit
- Service Mesh je obvykle poměrně lokální, nemá ambici stát se Internetem a velmi často zůstává uvnitř Kubernetes clusteru nebo propojuje pár clusterů mezi sebou, ale všechny jsou ve správě stejného subjektu
- Service Mesh není optimální výkonnostní řešení, z toho pohledu je lepší inteligenci dát do koncového bodu (tedy do kódu aplikace), ale dnes bývá důležitější rychlost vývoje a nasazování na úkor výkonnostní optimalizace. Ostatně celý koncept mikroslužeb, kdy místo volání uvnitř jednoho procesu v monolitu teď voláte přes pomalejší a méně spolehlivou síť, není o výkonu, ale schopnosti rychle nasazovat a nebrzdit vývoj (a samozřejmě také o škálovatelnosti hodně velkých aplikací, kdy pro monolit neexistuje rozumně velký node a škálování výš je neúnosné - ale to je opravdu pro případy, kdy je vaše aplikace skutečně velká)

Zdá se tedy, že Service Mesh a jeho hodnota pro rychlost a spolehlivost vývoje a nasazování je životaschopný i přes jeho jasné nevýhody ve větší spotřebě zdrojů a méně optimálního výkonnostního naladění (přidáváte "hopy" do komunikace).

Nicméně pozor na jednu věc. Service Mesh je pro svět synchronní komunikace přes REST či gRPC. Dost možná pro robustnost svých aplikací jdete jinou cestou - nepřímé vázání přes fronty a patterny typu pub/sub, event sourcing či CQRS. Na nic z toho vám Service Mesh nepomůže a možná je přechod z přímých volání na jiné patterny to, co vaši aplikaci posune dopředu víc, než nasazení Service Mesh. Tak to zvažte.

# Co service mesh přináší
Service Mesh dokáže na úrovni trubek věci, které byste jinak museli řešit v kódu třeba použitím nějakého SDK. Takové řešení je specifické pro daný programovací jazyk, změna SDK znamená rekompilaci a vývojáři přináší složitost, která je může brzdit. Service Mesh tyto funkce vyřeší bokem, mimo váš kód a to typicky tak, že je nasazen jako sidecar ve vašem Podu. Váš aplikační kontejner tak má vedle sebe chytrého souseda, přes kterého komunikuje ven a ten soused pro něj řeší spoustu důležitých věcí. Je to jednak v oblasti práce s trafficem (retry, cirtuit breaker, canary, A/B testing), dále v zabezpečení (šifrování komunikace mezi službami) a vizibilitě (monitoring co s čím komunikuje a jak).

## Kouzla s trafficem
Mikroslužby komunikují po sítí a ta občas nefunguje nebo se cílová služba zakucká a chvilku nejede. Do své aplikace tedy potřebujete retry logiku. Pokud to nevyjde, chcete to zkusit to znova, ale ne tak, že mombradujete službu jak to jde - ta má problém a miliarda retry ji zrovna nepomáhá se z toho oklepat, takže chcete typicky implementovat nějaký exponenciální backoff mechanismus.

Někdy je ale cílová služba opravdu dole a timeoutování není pro uživatele příjemné. Mikroslužby mají další úžasnou vlastnost - pokud jedna nefunguje, rozbije se jen funkce, kterou má mikroslužba nastarost a je možné, že vaše aplikace může žít i bez ní. Tak například se vám rozbije služba search ve vaší aplikaci, nicméně zákazník může dál procházet katalog podle kategorií, objednávat, platit a tak dále. Ale když zkusí vyhledat, točí se mu kolečko a po minutě to hodí error a to není pěkné. Chcete tedy circuit breaker. Jestli služba fakt nefunguje, tak nemá cenu čekat na timeout a řekneme uživateli rovnou, že search aktuálně nefunguje (třeba zašedneme tlačítko a dáme tam informaci s omlouvou, že search aktuálně nejede). Circuit breaker tedy začne rovnou vracet informaci o nedostupnosti a GUI se tomu může přizpůsobit. Čas od času to chcete zkusit pro náhodně vybraného uživatele, jestli už se služba náhodou nerozjela a pokud ano, otevřít bránu a znovu funkcionalitu nabízet v GUI. Je to podobné jako potenciálně v navigačním software. Pokud zjistíte zácpu, nebudete tamtudy posílat řidiče. Ale když se to dokonale povede, jak zjistíte, že už tam zácpa není? Dá se občas nějakého nešťastníka obětovat, poslat ho tamtudy a změřit si to. Tři mušketýři - jeden za všechny, všichni za jednoho.

Canary release je další typický požadavek. Chcete nasadit novou verzi, ale ne najednou, raději postupně. Nejdřív na 1% uživatelů a pak se uvidí. Pokud se jedná o API dostupné zvenku, můžete to udělat na reverse proxy, ale co když chcete pozvolna změnit API uvnitř Kubernetes clusteru? Můžete použít prostředky Kubernetu, ale ty nejsou ideální. Tak například udělát druhý deployment s novou verzí a Service objekt bude selektovat oba deploymenty. To je fajn, ale poměr staré vs. nové bude daný počtem replik Podů. Takže udělat to půl na půl je v pohodě, ale 1% nového by znamenalo mít 99 replik původního a to nedává smysl. Service Mesh dokáže oddělit deployment charekteristiky (počet replik) od rozhodnutí o směrování.

Občas také nechcete release testovat na běžných lidech, ale zkoušíte nějaké A/B varianty. Například B má být použité pro vaše testovací uživatele, kteří se mohou prokázat třeba nastavením headeru. Chcete udělat pravidlo, že paket s header release: beta bude směrován na B verzi služby.

Co je alternativou pro Service Mesh? Buď tyto funkce dát přímo do kódu s využitím nějakých SDK nebo méně používat přímá volání a jít do jiných patternů přes fronty.

## Security
Vaši bezpečáci možná přijdou s konceptem zero trust. Je jasné, že externě dostupná API máte zabezpečená přes TLS a to buď přímo v kódu, nebo lépe s využitím například Azure API Management. Co když ale chcete šifrovat i uvnitř clusteru nebo i mezi clustery pro volání interních API nevystavených ven? Správa certifikátů a generování unikátního pro každou službu tak, aby na HTTPS používaly mutual certificate autentizaci je hodně náročné. Service Mesh tohle může udělat za vás. O tom, která služba s kterou smí komunikovat, tak můžete rozhodovat v Service Mesh.

Jaká je alternativa? Vnitřní šifrování nedělat nebo alespoň nepoužívat unikátní certifikát pro každou službu a soustředit se jen na vystrčená API přes API Management. Pokud potřebuji síťovou mikrosegmentaci, můžu to udělat s Network Policy, což je funkce Kubernetes, která je daleko (daleko!) méně náročná na spotřebu zdrojů, nepotřebuje sidecar a tak podobně.

## Vizibilita a monitoring
Protože jdou všechny pakety přes sidecar proxy u každého aplikačního kontejneru, lze na tom místě koukat do provozu a získat tak vizibilitu. To považuji za nejvíc přeceňovanou vlastnost Service Mesh a hned řeknu proč.

Alternativou je použít aplikační monitoring přes SDK, například Azure Application Insights. Tím získáme stejné informace, ale hromadu dalších. Tak například můžete korelovat události už od Javascriptového frontendu (to Service Mesh samozřejmě nevidí) až po volání do databáze včetně její reakční doby a konkrétního SELECT dotazu (to Service Mesh taky nechytí). Aplikační monitoring je ve světě mikroslužeb naprosto zásadní a bez něj bych nic nedělal, takže vizibilitu bych řešil raději takhle pořádně.

# Tak moment - potřebuji to tedy nebo ne?
Rozhodnutí nechám na vás, ale zdá se mi důležité vnímat přínosy i nevýhody a nenasadit to jen proto, že se mi to zdá cool.

Podle mě dobrý kandidát na Service Mesh vypadá takhle:
- Potřebuje zero trust s mTLS mezi každou vnitřní službou - nestačí mu security uvnitř řešit jen síťově (network policy) a šifrování zvenku dělat na ingress nebo API Management
- Má velké množství mikroslužeb a v nich mnoho různých programovacích jazyků, takže cesta implementace retry či circuit breaker přes knihovny je komplikovaná a složitá
- Potřebuje velmi rychle nasadit řešení a programátoři se musí soustředit čistě na byznys logiku, ne provozní aspekty aplikace
- Část aplikace provozuje mimo Kubernetes a potřebuje řešení fungující mezi clustery i mezi technologiemi
- Má silný operations tým zvládající vzniklou komplexitu v infrastruktuře
- Nevadí mu zvýšené nároky na zdroje (více CPU, RAM, větší latence)
- Naprostá většina interakcí je REST/gRPC

Špatný kandidát se myslím pozná takhle:
- Pro vizibilitu potřebuje víc a stejně bude využívat APM jako je Application Insights
- Má relativně konzistentní programátorské zázemí a práce s knihovnami není vážný problém
- Většina integrací je přes publish/subscribe pattern
- Má co dělat s nabíráním znalostí Kubernetes, není v tom ještě expert a operations tým není nebo je malý
- Potřebuje nasazovat software v různých prostředích (například software prodává) a nemůže si dovolit mít dependency na Service Mesh, protože na to cílové prostředí není připraveno (zákazník Service Mesh nechce, nasazuje v Raspberry a nemá na to výkon, využívá Kubernetes jako službu a nechce nad něj sám dávat ne-defaultní komponenty apod.)

V příštím díle se podrobněji podíváme na standard Service Mesh Interface a srovnáme si tři implementace - Istio, Linkerd a Consul Connect. V dalších dílech si pak rozjedeme SMI a jednotivé Service Mesh implementace prakticky.