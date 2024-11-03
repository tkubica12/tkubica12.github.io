---
layout: post
status: draft
title: 'Azure Stack: platformní služby pro webové aplikace s Application Services z pohledu administrátora'
tags:
- AppService
- AzureStack
---
Azure Stack nabízí PaaS pro webové aplikace a API, ve které uživatel jednoduše doručí do cloudu kód své aplikace a Application Services ho pro něj provozují. Starají se o nasazení, balancing, TLS terminaci, správu různých prostředí a releasů, umožňují jednoduché škálování, udržují podkladový OS a aplikační framework aktuální a uživatel se tak může zaměřit na aplikaci samotnou.

Ve velkém Azure jsou za App Services (WebApp, API app) velké clustery. Jak něco takového vypadá v Azure Stack a co jako jeho administrátor můžete a potřebujete dělat? Azure Stack vám také umožní podívat se pod pokličku toho, jak vlastně Application Services fungují. A tu nadzvedneme dnes i my.

# Základní architektura a fungování služby
Při instalaci Application Services musíte jako administrátor Azure Stack zajistit SQL databázi (tam si služba zapisuje různé provozní věci) a souborovou storage (ta se připojuje k jednotlivým aplikacím a tím získávají perzistentní úložiště pro svůj kód apod.).

Kromě těchto technologií potřebuje PaaS několik rolí. Mé neprodukční má menší počty instancí, ale role jsou stejné:

![](/images/2019/2019-03-11-20-13-25.png){:class="img-fluid"}

Každá z rolí by měla mít v produkčním nasazení minimálně 2 instance z důvodu redundance. Co ty role dělají a jak to funguje?

Controller je komponenta, která provádí řídící operace - například škálování výkonu apod. Další je Front End. Jde v zásadě o inteligentní reverse proxy. Platforma na těchto strojí terminuje TLS session klientů a směruje na správné běžící aplikace podle přiřazeného doménového jména. Další komponentou je Management, který zajišťuje implementaci toho, co vidíte v GUI nebo volání přes API. Vytvořit aplikaci, přidat node, naimportovat certifikát, to všechno je úlohou této vrstvy. Dále tu máme Publisher. Protože Application Services je PaaS, do které můžete nasazovat přímo kód některým z podporovaných způsobů (FTP, Git, GitHub, OneDrive, deploy z Visual Studio, deploy z Azure DevOps, Jenkins, ...), musí tam být něco, co váš kód přijme nebo zjistí, že je nová verze na GitHub, kterou si má stáhnout, a doručí ji do správného workeru případně zajistí kompilaci apod. Tohle všechno ukazuje jak moc přidané hodnoty v PaaS službách je. Nicméně v Azure je každý takový PaaS cluster (a těch je věřte opravdu hodně) tvořený ve velikosti přes 1000 VM, takže overhead podpůrných systémů se tam dobře rozpustí a cena zůstává velmi příjemná. Pokud chcete v Azure Stack mít PaaS pro jednu malou webovku, overhead bude o poznání větší. To nemůsí vůbec ničemu vadit, ale mějte na paměti, že produkční PaaS prostředí si logicky řekne o některé zdroje pro sebe samo.

Další jsou zde Web Worker nody, těch pak aplikace reálně běží. To kolik jich tu budete mít a jaké záleží na vaší strategii ohledně toho jaké tiery chcete nabídnout.

# Tiery
Ve výchozím nastavení nabízí Application Services v Azure Stack tyto tiery:

![](/images/2019/2019-03-11-20-22-15.png){:class="img-fluid"}

Zásadní tedy je popsat rozdíl mezi shared a dedicated. Pokud zákazníkům nabídnete tier shared, asi bude vhodné jim na něj dát nižší cenu. Jejich aplikace bude umístěna do worker nodů, kde jejich výkon bude zákazník sdílet s několika dalšími. Procesy jsou od sebe izolované, takže se samozřejmě vzájemně nijak nevidí, nemohou si vyžrat paměť, ale přecijen o CPU a další zdroje se dělí. Způsob izolace najdete popsaný v dokumentaci: [https://github.com/projectkudu/kudu/wiki/Azure-Web-App-sandbox](https://github.com/projectkudu/kudu/wiki/Azure-Web-App-sandbox)

Vraťme se tedy k rolím a zaměříme se na shared.

![](/images/2019/2019-03-11-20-27-08.png){:class="img-fluid"}

![](/images/2019/2019-03-11-20-27-31.png){:class="img-fluid"}

Pokud vidíte, že o váš shared tier je opravdu velký zájem, můžete jejich počet zvětšit. Zatímco v Azure je za tím robot se strojovým učením, v Azure Stack je tato kapacitní úloha na vás. Protože vše je nasazeno jako tzv. Scale Set, stačí jen změnit počet a Azure zajistí provisioning dalšího workeru.

![](/images/2019/2019-03-11-20-29-15.png){:class="img-fluid"}

![](/images/2019/2019-03-11-20-30-02.png){:class="img-fluid"}

Nicméně od shared tieru by neměl váš zákazník očekávat prediktivní výkony, protože v něm běží aplikace i vašich další zákazníků. U dedikovaného to ale bude jinak.

Co je dedikovaný tier? V tento moment chcete pro zákazníka alokovat jeden a více jeho vlastních workerů. Na nich běží jen aplikace zákazníka, nikoho jiného. Pro cloudové škálování je nejlepší mít nody co nejmenší a škálovat přidáváním jejich počtu. Na druhou stranu jsou aplikace (například některé klasické Java appky), kde aby se to vůbec rozběhlo, potřebujete min 4GB RAM, jinak to nemá cenu. Zákazník by tedy mohl mít možnost zvolit si z různých základních velikostí workeru. Ve výchozím stavu jsou v Application Services navrženy tři:

![](/images/2019/2019-03-11-20-33-05.png){:class="img-fluid"}

Ale tady je rozdíl oproti velkému Azure. Tam má volbu typů strojů na starost Microsoft, ale tady jste to vy - administrátor Azure Stacku. Pokud vám to dává nějaký smysl (mě ne), můžete klidně zákazníkům nabídnout webový worker node s 64 core a 128 GB paměti.

![](/images/2019/2019-03-11-20-34-51.png){:class="img-fluid"}

Něco takového v Azure není možné a tady vám dává Azure Stack flexibilitu navíc.

Nicméně - jak vlastně dedikované nody fungují? V okamžiku, kdy je někdo chce, tak se vytvoří VM a začne se do něj všechno instalovat? To by se vám jako uživatelům nelíbilo. Když potřebujete vyškálovat výkon očekáváte, že to bude trvat maximálně minutku či dvě, ne deset. Ve skutečnosti je to tak, že musíte pustit počet workerů dle vaší volby a ty budou nastartované a plně připravené. Nicméně nejsou alokovány žádnému zákazníkovi. V okamžiku, kdy si zákazník vytvoří tzv. Service Plan nebo vyškáluje stávající, platforma nepřiřazenou VM vezme a alokuje ji uživateli. Proto je to tak rychlé.

Pro vás jako provozovatele cloudu je to ale důležité správně chápat. V Azure je díky obrovské škále možné nabízet poměrně dost typů a klidně si je držet přednastartované, protože se ví, že se prodají (a mimochodem ty co čekají a neprodali se může Azure využívat pro serverless s Azure Functions...chytré, ne?). Ale co u vás? Aby uživatelé mohli v pohodě vytvářet servisní plány a zvětšovat si je podle potřeby měli byste mít cluster o rozumné volné velikosti. Neprodané stroje jsou váš overhead. Když nabídnete deset typů strojů máte takový overhead 10x. Bude tedy dávat smysl nabízet jen jednu či dvě konfigurace, pokud váš Azure Stack není specificky zaměřen jen na App Services.

Mimochodem na worker node můžete nainstalovat i vlastní systémový software - v Azure nemyslitelné.

![](/images/2019/2019-03-11-21-00-30.png){:class="img-fluid"}

# SKU
Mluvili jsme o tom, jak to funguje na backendu. A co uvidí vaši uživatelé v portálu?

![](/images/2019/2019-03-11-20-42-17.png){:class="img-fluid"}

Ve výchozím stavu je to Free, Shared a Dedicated (ve kterém je na výběr ze tří velikostí). Tohle ale můžete libovolně změnit. Například tady vytvářím novou nabídku Premium, v GUI ji chci mít zelenou barvou a půjde o dedicated worker ve dvou velikostech.

![](/images/2019/2019-03-11-20-44-29.png){:class="img-fluid"}

Na rozdíl od Azure, kde rozhodnutí přijímá Microsoft, je u Azure Stacku na vás, jaké služby a limity chcete v rámci svého portfolia nabídnout. Například úžasná funkce deployment slots (o tom příště, až budeme rozebírat uživatelský pohled na věc) je u Azure dostupná jen u Standard a výše, ne u Basic, Shared nebo Free. To je obchodní rozhodnutí, ale v Azure Stack můžete mít názor jiný a klidně to zapnout na Free tieru. Podívejme se na nastavení funkcí.

![](/images/2019/2019-03-11-20-46-13.png){:class="img-fluid"}

Povolíme v tomto tieru WebSockety? Může si uživatel dát vlastní doménu? Chceme jeho CPU nějak omezovat? Povolíme mu IP SSL nebo může mít jen SNI (nebo žádné https)?

![](/images/2019/2019-03-11-20-47-36.png){:class="img-fluid"}

Omezíme maximální paměť? Jak dlouhý bude timeout? Kolik deployment slotů můžeme použít?

![](/images/2019/2019-03-11-20-48-57.png){:class="img-fluid"}

Chceme nějak omezit maximální škálu (například levnější varianta může škálovat jen do 3 workerů, zatímco dražší třeba na 10)? Nebo množství WebApp v jednom servisním plánu?

![](/images/2019/2019-03-11-20-50-07.png){:class="img-fluid"}

Ještě brutálnější granularitu najdete u kvót. Omezovat můžete opravdu kde co.

![](/images/2019/2019-03-11-20-50-58.png){:class="img-fluid"}

![](/images/2019/2019-03-11-20-51-14.png){:class="img-fluid"}

![](/images/2019/2019-03-11-20-51-50.png){:class="img-fluid"}

Nemusíte se v tom hrabat. Využijte navržené výchozí tiery a je to. Pokud si ale chcete službu poladit a nastavit unikátně, máte fantastické možnosti.

# Ceny
Chcete uživatelům signalizovat kolik je jaký plán bude stát? I to můžete nastavit.

![](/images/2019/2019-03-11-20-53-54.png){:class="img-fluid"}

Jak to všechno pak vypadá, když uživatel vytváří webovou appku?

![](/images/2019/2019-03-11-20-54-59.png){:class="img-fluid"}

Všimněte si co se stane, když v Azure Stack nemáte volné zdroje pro dedikované workery. Uživatel je informován, že aktuálně nejsou.

![](/images/2019/2019-03-11-20-56-07.png){:class="img-fluid"}

# Integrace deployment služeb
Jednou z klíčových vlastností PaaS je schopnost snadno nasazovat aplikace. Pokud chcete integrovat Bitbucket, GitHub nebo OneDrive budete potřebovat registraci Azure Stack v těchto službách. Získané údaje musíte jako administrátor zadat a pak se uživatelům tato možnost otevře.

![](/images/2019/2019-03-11-21-02-01.png){:class="img-fluid"}

# Upgrady
S každou další verzí App Service získáváte i všechny potřebné patche podkladového OS. Funguje to tak, že Azure Stack přidá worker z nejnovějšího image, přesune na něj aplikaci, jednoho stávajícího ubere a takhle pokračuje, až je aktualizováno všechno. Protože je provoz terminovaný na proxy (Front End), v průběhu updatu neuvidíte výpadky a 404 chyby, většinou maximálně trochu prodloužené latence, když proxy musí provést resend vašeho dotazu na nový worker.

# Jak to pak vypadá?
Z uživatelského hlediska si platformu představíme příště, ale když už jsme ztrávili tolik času detaily na backendu, ukažme si alespoň něco. Uživatel si vytvoří WebApp a ta je okamžitě k dispozici a poslouchá na výchozí URL.

![](/images/2019/2019-03-11-21-06-10.png){:class="img-fluid"}

Nasazovat můžu přímo kód třeba z Gitu nebo použít mnoho dalších způsobů.

![](/images/2019/2019-03-11-21-06-45.png){:class="img-fluid"}

Můžu přidat deployment sloty a jednoduše získat různá prostředí typu dev, test, staging, prod.

![](/images/2019/2019-03-11-21-07-18.png){:class="img-fluid"}

Můžu si zvolit jaká prostředí a v jakých verzích chci provozovat.

![](/images/2019/2019-03-11-21-07-57.png){:class="img-fluid"}

Můžu škálovat výkon, přidávat rozšíření, testovat v produkci a dělat canary release a je toho ještě hodně. Na to všechno se podíváme příště.

Azure Stack vám může odkrýt co to znamená PaaS služba. Opravdu PaaS není jen jednoduché VMko, ale velmi zajímavý a promakaný systém. V Azure Stack mu vidíte pod kapotu a nejen to - můžete sáhnout do jeho konfigurace a upravit je svým potřebám. Chcete levný sdílený plán, ale s podporou deployment slotů? Nebo brutální worker s velikánskou pamětí? Azure Stack administrátor je za kormidlem.