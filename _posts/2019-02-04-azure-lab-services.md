---
layout: post
status: draft
published: true
title: Pořádáte školení, hackathon nebo testujete? Získejte prostředí s Azure Lab Services.
tags:
- Automatizace
---
Získat prostředí v Azure je samozřejmost, ale jak si to automatizovat (třeba zapínat podle kalendáře), mít předinstalované věci ve VM, řídit přístupy a to všechno tak, aby to pochopil i člověk neznalý Azure? Jasně - custom Image, ARM šablony, nějaká orchestrace třeba přes Logic Apps. Ale to je všechno pro začátečníka docela složité. Podívejme se dnes na Azure Lab Services. Krásné zjednodušení tohoto scénáře pro všechny bez nutnosti znát Azure, skriptování, šablony ... a dokonce se obejdete i bez angličtiny.

# Azure Lab Services
Aktuálně v preview máte k dispozici Azure Lab Services. V něm si velmi snadno připravíte "školící místnost", upravíte OS a přidáte si tam váš software a následně pošlete link s pozvánkou pro účastníky. Zdroje platíte dle reálné spotřeby a můžete si otevřít kalendář a naplánovat v které dny a v jakém čase má být lab zapnutý. To všechno i pro laiky - v češtině a bez děsivého množství možností (je na to speciální portál, kde nic jiného není).

Nejdřív si v Azure portálu najdeme Lab Services a vytvoříme si účet.

![](/images/2019/2019-02-02-09-35-21.png){:class="img-fluid"}

![](/images/2019/2019-02-02-09-36-24.png){:class="img-fluid"}

V rámci tohoto lab účtu můžeme přidat oprávněné administrátory, kteří mají právo různé laby vytvářet a modifikovat. Používá se k tomu běžný RBAC tak jak na všechno ostatní v Azure - tedy prává kdo co může řešíte v Access Control záložce a autentizace je přes Azure Active Directory. My nic měnit nemusíme (budu na to sám), tak můžeme rovnou kliknout na odkaz vedoucí do zjednodušeného portálu pro lab služby.

![](/images/2019/2019-02-02-09-40-30.png){:class="img-fluid"}

Hned na mě vyběhne možnost založit první lab, což také udělám.

![](/images/2019/2019-02-02-09-41-49.png){:class="img-fluid"}

Jak velký budu chtít stroj? Žádné složitosti - malý, střední nebo velký?

![](/images/2019/2019-02-02-09-43-06.png){:class="img-fluid"}

Jaký OS? Zase nic složitého - pár variant Linux, Windows 10, SQL a Windows Data Center, což bude moje volba.

![](/images/2019/2019-02-02-09-44-47.png){:class="img-fluid"}

Můžeme dál. Budeme zadávat heslo pro přístup do stroje.

![](/images/2019/2019-02-02-09-45-26.png){:class="img-fluid"}

![](/images/2019/2019-02-02-09-46-27.png){:class="img-fluid"}

... a teď máme čas na kávičku...

![](/images/2019/2019-02-02-09-46-54.png){:class="img-fluid"}

# Připravíme si image pro lab
Dalším krokem je úprava image - například instalace software, který budete v rámci výuky nebo testování používat. Nastartujeme si základní stroj.

![](/images/2019/2019-02-02-10-10-27.png){:class="img-fluid"}

Připojíme se ke stroji přes RDP.

![](/images/2019/2019-02-02-10-12-51.png){:class="img-fluid"}

Do stroje jsem nainstaloval nějakou aplikaci, v mém případě Chrome. Mám hotovo, jdeme dál.

![](/images/2019/2019-02-02-10-17-02.png){:class="img-fluid"}

Jsme připraveni, můžeme lab publikovat.

![](/images/2019/2019-02-02-10-19-09.png){:class="img-fluid"}

![](/images/2019/2019-02-02-10-19-55.png){:class="img-fluid"}

![](/images/2019/2019-02-02-10-34-35.png){:class="img-fluid"}

# Použijeme náš nový lab
Náš labík je pěkně připraven, ale vypnutý (aktuálně nic nestojí).

![](/images/2019/2019-02-02-10-44-21.png){:class="img-fluid"}

Můžeme přidat uživatele - účastníky kurzu, studenty, testery.

![](/images/2019/2019-02-02-10-45-44.png){:class="img-fluid"}

![](/images/2019/2019-02-02-10-47-12.png){:class="img-fluid"}

Možná máte omezený rozpočet nebo chcete férové podmínky pro všechny a tak se rozhodnete omezit množství času, kterou může každý uživatel využívat lab. Jedná se o maximální čas v rámci samoobsluhy, tedy že si uživatel pouští lab sám. Kromě toho můžeme mít lab spuštěný v průběhu výuky dle rozvrhu, což se do tohoto času nepočítá.

![](/images/2019/2019-02-02-10-50-48.png){:class="img-fluid"}

Teď už můžeme studentům rozeslat registrační link.

![](/images/2019/2019-02-02-10-52-57.png){:class="img-fluid"}

![](/images/2019/2019-02-02-10-53-18.png){:class="img-fluid"}

Po registraci jako administrátor vidím, že uživatel ji provedl.

![](/images/2019/2019-02-02-10-55-38.png){:class="img-fluid"}

Takhle to vypadá v portálu uživatele. Stiskneme tlačítko nastartování mašiny.

![](/images/2019/2019-02-02-10-55-59.png){:class="img-fluid"}

V administrátorském přehledu vidím, že kapacita mého labu jsou 2 počítače. Jeden je aktuálně vypnutý a druhý startuje s tím, že byl přiřazen uživateli Tomas Kubica (to je můj soukromý login, ne administrátorský).

![](/images/2019/2019-02-02-10-57-30.png){:class="img-fluid"}

Každému uživateli jsem dal 10 hodin, po které si může lab kdykoli pustit. Kromě toho ale kurz nebo školení probíhá s instrukturem v učebně a na toto období chci stroje nastartovat všechny. Vytvoříme si tedy plán.

![](/images/2019/2019-02-02-11-03-25.png){:class="img-fluid"}

Náš kurz budeme mít každé pondělí a středu od 8:00 do 10:00 a to až do června.

![](/images/2019/2019-02-02-11-04-19.png){:class="img-fluid"}



Azure je perfektní prostředí pro vaše školení, kurzy, školní výuku nebo připravené testovací scénáře. Nicméně naučit se Azure ovládat vyžaduje nějakou časovou investici a učitel statistiky nebo instruktor SAPu možná IT technologiím vůbec nerozumí. Azure Lab Services jsou geniálně jednoduché prostředí kompletně v češtině a stojí za vyzkoušení. Kromě toho existují také DevTest Labs, podobný systém zaměřený víc na ruční testování software a podle všeho se chystají další šablony a nadstavbová řešení.