---
layout: post
published: true
title: "Azure Defender (5): Ochrana serverové infrastruktury - EDR"
tags:
- Security
---
Dnešním dílem začneme témata v rámci Azure Defender zaměřená na virtuálky, tedy Linux a Windows serverové operační systémy ať už běží v Azure nebo je přes Azure Arc for Server napojíte odkudkoli. Pro ochranu Windows používá Azure Defender pod kapotou nástroj Microsoft Defender for Endpoints (dříve Defender ATP) a pro Linux funguje (zatím) napřímo - na oboje se dnes podíváme. Příště si pak ukážeme další vlastnosti pro serverovou infrastrukturu jako je adaptivní řízení povolených aplikací, síťový hardening, monitoring integrity souborů nebo aktivní práce s bezpečnostními logy.

# Microsoft Defender for Endpoints 
Azure Defender ve své ceně obsahuje i licenci pro Microsoft Defender for Endpoints, takže vaše Windows servery doporučuji chránit tímto způsobem, což přináší cloudový model placení, ale hlavně obrovské množství dalších bezpečnostních vlastností v celém Azure Defender. Řešení Microsoft Defender for Endpoints je nesmírně robustní a nemám aktuálně ambici ho v tomto článku rozebírat podrobně, ostatně je to spíše doménou mých kolegů zaměřených na M365. Pokud nástroj neznáte, nemusíte o něm vůbec vědět - funguje na pozadí a poskytuje informace do Azure Defender, kde můžete věci automatizovat. Na druhou stranu pokud nástroj dobře znáte (například protože ho používáte na koncové stanice v rámci Microsoft 365 balíčků), nic vám nebrání se připojit přímo do něj a využít ho naplno bez jakýchkoli omezení se všemi detaily.

Všechny starší Windows systémy jsou do řešení naloditelné automaticky přímo z Azure - stačí zapnout Azure Defender a tím se nainstalují potřební agenti a server se vám sám objeví v portálu Microsoft Defender Security Center.

[![](/images/2020/2020-12-02-09-59-48.png){:class="img-fluid"}](/images/2020/2020-12-02-09-59-48.png)

Pokud máte Windows Server 2019, tak tam už je tato technologie součástí samotného serveru. Azure Defender tak aktuálně neumí připojit OS automaticky, musíte v serveru pustit skript, který to udělá (samozřejmě pokud máte nějaké řešení centrální správy, tak to uděláte odtamtud).

Takhle třeba vypadá časový sled událostí v serveru. Všimněte si vysoké míry detailů. Do Azure Defender se propíše jen to nejdůležitější (útok ten a ten), ale tady najdete kompletní sled událostí.

[![](/images/2020/2020-12-02-10-00-26.png){:class="img-fluid"}](/images/2020/2020-12-02-10-00-26.png)

[![](/images/2020/2020-12-02-10-01-04.png){:class="img-fluid"}](/images/2020/2020-12-02-10-01-04.png)

Alerty Microsoft Defenderu jsou právě to, co se pak objevuje v Azure Defenderu.

[![](/images/2020/2020-12-02-10-01-18.png){:class="img-fluid"}](/images/2020/2020-12-02-10-01-18.png)

Nicméně tady se můžeme podívat na větší detail.

[![](/images/2020/2020-12-02-10-02-05.png){:class="img-fluid"}](/images/2020/2020-12-02-10-02-05.png)

Dokonce si můžu stáhnout podezřelý soubor pro hlubší analýzu.

[![](/images/2020/2020-12-02-10-02-38.png){:class="img-fluid"}](/images/2020/2020-12-02-10-02-38.png)

Data můžete vizualizovat také formou grafu.

[![](/images/2020/2020-12-02-09-59-04.png){:class="img-fluid"}](/images/2020/2020-12-02-09-59-04.png)

Myslím, že pokud provozujete Windows servery, je Azure Defender nejvýhodnější způsob jak k nim získat kompletní bezpečnost včetně licence mocného Microsoft Defender for Endpoints.

# Alerty, Windows a Linux
Jak už padlo, pro Windows se Azure Defender zaměřuje na integraci s Microsoft Defender for Endpoints, ale pro Linux používá vlastní engine (alespoň v době psaní článku). Ten je postaven na analýze Linux logů, zejména auditd, které řešení sbírá a analyzuje (o tom, jak můžete analyzovat bezpečnostní logy z Windows i Linux sami si řekneme příště). Pokud vás zajímá co Azure Defender umí odchytit, můžete se podívat na stále rostoucí seznam v [dokumentaci](https://docs.microsoft.com/en-us/azure/security-center/alerts-reference#alerts-linux). Zahrnuje podezřelé postupy, příkazy, downloady, nástroje, detekované brute force útoky a tak podobně.

Vytvořil jsem automatizované testovací prostředí pro Azure Defender a najdete ho na mém GitHubu: [https://github.com/tkubica12/azdefender-demo](https://github.com/tkubica12/azdefender-demo)

Takhle vypadá seznam alertů:

[![](/images/2021/2021-01-06-13-03-11.png){:class="img-fluid"}](/images/2021/2021-01-06-13-03-11.png)

V simulovaných útocích (v repozitáři je najdete) jsem dosáhl těchto alertů:

Úspěšný útok na RDP (tedy např. neúspěšné pokusy následované úspěšným v rychlém sledu a ze stejné lokality).
[![](/images/2021/2021-01-06-09-12-48.png){:class="img-fluid"}](/images/2021/2021-01-06-09-12-48.png)

Pokus obejít AppLocker ve Windows.
[![](/images/2021/2021-01-06-09-13-56.png){:class="img-fluid"}](/images/2021/2021-01-06-09-13-56.png)

Podezřelý SVCHOST proces ve Windows.
[![](/images/2021/2021-01-06-09-14-48.png){:class="img-fluid"}](/images/2021/2021-01-06-09-14-48.png)

Potenciální použití útočného skriptu v Linux.
[![](/images/2021/2021-01-06-09-15-30.png){:class="img-fluid"}](/images/2021/2021-01-06-09-15-30.png)

Spuštění reverse shell s nc v Linuxu.
[![](/images/2021/2021-01-06-09-16-10.png){:class="img-fluid"}](/images/2021/2021-01-06-09-16-10.png)

Microsoft Defender for Endpoints reakce na spuštění malware.
[![](/images/2021/2021-01-06-09-16-49.png){:class="img-fluid"}](/images/2021/2021-01-06-09-16-49.png)

# Automatizace reakce na incidenty
Pro příklad si ukážeme jak by šlo reagovat na alert síťově, tedy nějakým způsobem napadenou VM izolovat třeba modifikací bezpečnostních pravidel v Network Security Group. Tady je pár příkladů, jak to použít:
- Zákaz komunikace pro IP adresu útočníka (inbound pravidlo) - například při odhalení pokusů o brute force útok na RDP nebo SSH.
- Odstřihnutí VM od Internetu (outbound pravidlo) - například při odhalení komunikace s command and control serverem, pokusu o vytvoření reverse shell a tak podobně. Můžeme chtít nechat VM zatím v provozu (jde o kritickou aplikaci a o útoku ještě nejsme plně přesvědčeni), ale znemožnit komunikaci s okolním světem (v ten okamžik třeba nepůjde stahovat aktualizace, což na krátkou dobu nevadí a současně se tím ustřihne komunikační kanál pro exfiltraci dat nebo napojení na řídící uzel)
- Udělení penalizace - při nízko-prioritním alertu možná nechceme IP adresu potenciálního útočníka natrvalo blokovat, protože nejde o nic vážného a může to být planý poplach. Nicméně dávalo by nám smysl případný útok zpomalit (a tím útočníka odradit), ale nevytvořit si hromadu práce s odblokováváním zakázaných IP, protože je situace poměrně častá a není závažná. Můžeme nasadit workflow, které IP zablokuje na 15 minut a pak se toto pravidlo samo odebere.
- Odříznutí správy kromě bastion serveru - zatímco v produkčním prostředí budu často přísný a veškeré přístupy na management rozhraní serverů budou výhradně ze zabezpečené privilegované stanice (bastion / jump), v neprodukčních prostředích to zpomaluje vývojáře a toto snížení produktivity mi za to nestojí (nejsou tam ostrá data). Ať tam tedy chodí napřímo. Nicméně bastion může i tak existovat a pokud Azure Defender detekuje něco podezřelého na VM, můžeme v ten okamžik zakázat veškeré RDP/SSH kromě bastion serveru a odeslat vývojářům zprávu, že se tam něco děje a že do vyřešení musí přistupovat přes bastion.

Vyzkoušíme si první scénář - izolace útočníkovo IP adresy modifikací NSG a odeslání notifikace na můj email (v praxi bychom například tento email načetli z tagů třeba resource group tak, jak jsem to ukazoval v [předchozích dílech](https://www.tomaskubica.cz/post/2020/azure-defender-3/)).

Aktuálně je moje NSG nastaveno tak, že sice nepovoluje RDP z Internetu, ale nijak ho neomezuje ve vnitřní síti. To přináší riziko, že kdokoli zevnitř, včetně nakaženého počítače nebo serveru mi do toho může bušit a snažit se šířit. To je jeden z důvodů, proč pro produkci doporučuji rozhodně tyto přístupy omezit jen na bastion server, nicméně chápu, jak nepohodlné to je. Mám tady tedy poměrně častý setup - RDP z Internetu je samozřejmě zakázáno, ale ve vnitřní síti je povoleno.

[![](/images/2021/2021-01-07-06-53-49.png){:class="img-fluid"}](/images/2021/2021-01-07-06-53-49.png)

Všimněte si, že první pravidlo mi začíná až prioritou 200 právě proto, abych mohl využít čísla 100-199 pro automatizační účely.

Takhle vypadá LogicApp, která si převezme údaje z Alertu, vytípá si z toho potřebné parametry jako je identifikátor VM a IP adresa útočníka a následně si je uloží do proměnných pro větší přehlednost. Kompletní zdroj najdete na mém [GitHubu](https://github.com/tkubica12/azdefender-demo). Potom si načtu podrobnosti o VM, abych zjistil jaké je na ní NSG a to následně modifikuji a odešlu email s upozorněním.

[![](/images/2021/2021-01-07-06-57-02.png){:class="img-fluid"}](/images/2021/2021-01-07-06-57-02.png)

Takhle pak vypadá vytvoření bezpečnostního pravidla. Všimněte si, že pro modifikaci NSG není v LogicApp aktuálně konkrétní konektor, ale to vůbec nevadí, protože můžu takhle přímo volat jakékoli API.

[![](/images/2021/2021-01-07-06-58-36.png){:class="img-fluid"}](/images/2021/2021-01-07-06-58-36.png)

Nejdříve zkusíme ruční spuštění automatizace. To je scénář, kdy procházíme alerty a můžeme využít připravených workflow na základě uvážení. Tak třeba bych u incidentu s RDP útokem mohl mít workflow pro pouhé poslání upozornění bez restrikce, jiné pro izolaci útočníka (tak jak si vyzkoušíme), jiné pro kompletní zákaz RDP kromě bastion serveru a čtvrté pro totální izolaci VM nebo její vypnutí.

[![](/images/2021/2021-01-07-07-03-27.png){:class="img-fluid"}](/images/2021/2021-01-07-07-03-27.png)

[![](/images/2021/2021-01-07-07-03-52.png){:class="img-fluid"}](/images/2021/2021-01-07-07-03-52.png)

[![](/images/2021/2021-01-07-07-04-27.png){:class="img-fluid"}](/images/2021/2021-01-07-07-04-27.png)

V historii LogicApp vidím, že úspěšně proběhla.

[![](/images/2021/2021-01-07-07-05-19.png){:class="img-fluid"}](/images/2021/2021-01-07-07-05-19.png)

A skutečně - útočníkova IP je blokovaná:

[![](/images/2021/2021-01-07-07-06-05.png){:class="img-fluid"}](/images/2021/2021-01-07-07-06-05.png)

V našem jednoduchém příkladě by další odhalený útočník tenhle záznam přepsal, takže bych do LogicApp musel přidat logiku na nalezení dalšího čísla priority v pořadí a tak podobně, ale to už si určitě dokážete představit. Ostatně smyslem povídání o Azure Defender je pochopit bezpečnostní koncepty, na detaily tvorby LogicApp se podíváme někdy jindy (a pár článků už tu na toto téma mám).

Připravená workflow, o kterých administrátor rozhodne kdy jaké spustit jsou určitě fajn, ale pro některé typy útoků a reakcí budeme chtít tyto vyvolat automaticky. Možná i pokud se bojíte automatizovat restriktivní kroky nemělo by vás to zastavit v nastavení automatizované reakce typu odeslání emailu či Teams zprávy vlastníkovi zdroje, informování nadřízeného nebo přeposlání incidentu do jiného systému. Lze tak kombinovat workflow pouštěná automaticky s workflow pouštěnými ručně administrátorem. Pojďme si naši předchozí reakci plně automatizovat.

[![](/images/2021/2021-01-07-07-10-52.png){:class="img-fluid"}](/images/2021/2021-01-07-07-10-52.png)

[![](/images/2021/2021-01-07-07-12-46.png){:class="img-fluid"}](/images/2021/2021-01-07-07-12-46.png)

[![](/images/2021/2021-01-07-07-13-06.png){:class="img-fluid"}](/images/2021/2021-01-07-07-13-06.png)

Máme vytvořeno - příště už bude Azure Defender reagovat sám.

[![](/images/2021/2021-01-07-07-13-42.png){:class="img-fluid"}](/images/2021/2021-01-07-07-13-42.png)



Dnes jsme viděli jak můžete chránit operační systémy Windows a Linux s Azure Defender a jak automaticky reagovat na události. U serverové infrastruktury zůstaneme i v příštích několika dílech a zaměříme se na další funkce jako je kontrola integrity klíčových souborů, adaptivní řízení povolených aplikací nebo hardening síťového zabezpečení.


