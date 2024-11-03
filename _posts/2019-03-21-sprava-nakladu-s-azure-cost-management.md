---
layout: post
title: Správa nákladů s Azure Cost Management
tags:
- Governance
---
Máte neomezený rozpočet? Asi ne. Většina z nás musí náklady spravovat a ujišťovat se, že jsou prostředky vynaloženy účelně. V on-premises infrastruktuře je to velmi obtížné. Jak se dozvím skutečné náklady na nějaké řešení, když jde o komplexní nákladovou strukturu zahrnující datové centrum, chlazení, elektřinu, síť, servery, storage, software a licence, zabezpečení, ostrahu, rutinní opravy, výměny, patchování, správa hypervisorů a to zdaleka není všechno? Možná vím, kolik mě stojí celé IT, ale kolik mě stojí konkrétní projekt nebo aplikace? V Azure je situace o poznání jednodušší, protože prakticky za všechno platím podle reálné spotřeby. Využití Azure je samozřejmě o možnosti rychleji inovovat, získat přístup k nejnovějším technologiím, standardizovat, automatizovat či škálovat dle aktuálních potřeb. Současně je ale cloud příležitost pro na první pohled ne tak zřejmé věci. Tou první je schopnost udělat si vě věcech pořádek (vidím všechno v jednom systému a můžu si to řídit - a tím vidím myslím to jak to opravdu je, ne jak je to  bůh ví jak zdokumentováno v CMDB) a právě i získat skutečné náklady. Kolik projektů vypadalo nadějně, rok se pro ně nakupovalo železo a spousta lidí stavěla platformu, aby se mohlo začít, a ono se nezačlo, protože se byznysové zadání změnilo? A kolik zajímavých projektů se nikdy nezkusilo jednoduše proto, že přednost dostal jiný (a ten nedopadl)? Schopnost vidět a řídit náklady transparentně a okamžitě může mít zásadní vliv na řízení vašich inovací a rozvoj byznysu.

Jinak řečeno v cloudu mám vyčíslené náklady na všechno co používám, takže na rozdíl od běžné situace lokálního řešení vstupní data jsou více než bohatá. Jak se v nich ale vyznat a udělat si pořádek? Jak dát týmům a projektům budget a ten sledovat? Jak vím za co platím? Podívejme se dnes na Azure Cost Management.

# Azure Cost Management
Historicky existuje víc způsobů jak sledovat náklady. Pokud máte režim před kreditku, chodí vám faktura od Microsoftu. Pokud nakupujete přes CSP program, chodí vám účty od partnera. Pokud máte EA, máte nabito a v EA portálu vidíte náklady na jednotlivé subskripce. Dokonce i přímo v Azure se můžete podívat na náklady subskripce nebo Resource Group (pokud je nevidíte, možná potřebujete nastavit práva v EA portálu na AO a DO View Charges nebo máte CSP a náklady vidí váš partner). Ale to nemusí stačit na analýzu a plánování budgetů. Co rozpady za jednotlivé typy zdrojů, regiony, tagy? EA můžete napojit na PowerBI a tam jsou celkem rozumné reporty nebo si stáhnete (či vám partner pošle) CSV a vy si ho budete sami zpracovávat. Nic z toho ale není ideální.

To je důvod proč Microsoft koupil firmu Cloudyn, která se na správu nákladů v cloudu specializovala. Svoje prostředí můžete do Cloudyn napojit a pro správu nákladů v Azure je to zdarma. Nicméně nástroj je sice mocný, ale minimálně pro mě ne zrovna intuitivní.

Možná to je důvod proč v poslední době dochází k přepsání Cloudyn do podoby, která je přímo integrována v Azure portálu. Logika a engine je zachovaný, ale vizualizace (alespoň pro mě) o poznání příjemnější. Pojďme se na to dnes podívat.

# Analýza nákladů
Kolik jsem tedy už tenhle měsíc propálil?

![](/images/2019/2019-03-20-14-15-12.png){:class="img-fluid"}

Možná mě to zajímá za jiné období.

![](/images/2019/2019-03-20-14-15-47.png){:class="img-fluid"}

Pokud nechcete kumulativní pohled, můžeme se podívat, kolik utrácím každý den.

![](/images/2019/2019-03-20-14-16-42.png){:class="img-fluid"}

Nebo je libo raději sloupce?

![](/images/2019/2019-03-20-14-17-26.png){:class="img-fluid"}

Kromě celkového pohledu můžu chtít náklady sdružit podle nějaké struktury.

![](/images/2019/2019-03-20-14-18-12.png){:class="img-fluid"}

Takhle třeba vidím, za jaké typy služeb utrácím.

![](/images/2019/2019-03-20-14-18-51.png){:class="img-fluid"}

Nebo chcete pohled za jednotlivé Resource Group?

![](/images/2019/2019-03-20-14-19-57.png){:class="img-fluid"}

Pro mě může být důležité identifikovat konkrétní zdroje, které žerou nejvíc.

![](/images/2019/2019-03-20-14-20-48.png){:class="img-fluid"}

Pokud používáte u zdrojů tagy, dá se seskupovat podle nich. V tagu můžete mít cokoli - nákladové středisko, typ prostředí (dev/test/prod), jméno aplikace, projekt.

![](/images/2019/2019-03-20-14-22-12.png){:class="img-fluid"}

Další variantou je zvolit Meter, tedy konkrétní jednotky měření. V následujícím výpisu tak vidím, kolik mě stojí disky typu s20.

![](/images/2019/2019-03-20-14-23-32.png){:class="img-fluid"}

Kromě seskupování můžeme použít i filtraci. Tak například jak vypadá spotřeba pro vyjmenované resource groupy?

![](/images/2019/2019-03-20-14-24-30.png){:class="img-fluid"}

![](/images/2019/2019-03-20-14-25-06.png){:class="img-fluid"}

Filtrů můžu dát několik. Například náklady za vyjmenované resource groupy, ale pouze za výpočetní výkon.

![](/images/2019/2019-03-20-14-26-09.png){:class="img-fluid"}

Filtrovat můžeme i podle dalších parametrů jako jsou tagy nebo třeba konkrétní Meter. V následujícím výpisu vidím kolik mě stojí stroje typu e16.

![](/images/2019/2019-03-20-14-27-26.png){:class="img-fluid"}

Zatím se dívám na jednu konkrétní subskripci, ale scope může být větší. Třeba několik subskripcí, které zvolím (a do kterých mám přístup na úrovni billing práva) nebo hierarchickou skupinu subskripcí (Management Group - o těch už jsem tu psal).

![](/images/2019/2019-03-20-14-29-02.png){:class="img-fluid"}

Grafy jsou skvělé, ale někdy potřebujete jít po detailu. Přepněme si nástroj na zobrazení seznamu zdrojů a jejich nákladů v tabulce. I v rámci tohoto výpisu můžeme filtrovat.

![](/images/2019/2019-03-20-14-30-53.png){:class="img-fluid"}

# Export
Zpracovávate data nějak dál nebo je chcete uchovávat? Je možné zapnout exportování.

![](/images/2019/2019-03-20-14-31-53.png){:class="img-fluid"}

Založím si exportovací job.

![](/images/2019/2019-03-20-14-32-27.png){:class="img-fluid"}

Exporty se budou dávat do storage accountu.

![](/images/2019/2019-03-20-14-33-22.png){:class="img-fluid"}

A co export, ale filtrovaný? I to je možné. Nastavte si filter dle potřeby a klikněte na tlačítko Export.

![](/images/2019/2019-03-20-14-35-07.png){:class="img-fluid"}

# Budgety a alerty
Dost možná budete chtít pro projekty přiřadit nějaký budget a sledovat, jestli se do něj vejdou. K tomu slouží sekce Budgets.

![](/images/2019/2019-03-20-14-36-27.png){:class="img-fluid"}

Při zakládání budgetu můžete říct kolik peněz a jak často mu chcete přidělit, případně kdy projekt končí. Nicméně je důležité zdůraznit, že budgety fungují na úrovni subskripce. Nemůžete tedy vytvořit budget jen pro nějakou Resource Group.

![](/images/2019/2019-03-20-14-37-19.png){:class="img-fluid"}

Alerty nebo překročení budgetu nezpůsobí automaticky nějaké zastavení služeb. můžete si nastavit kdy co se má stát (procentuální bloky) a kromě emailu lze použít i Action Group, která je společná s Alertovacím systémem celého Azure.

![](/images/2019/2019-03-20-14-39-19.png){:class="img-fluid"}

Action Group je velmi mocná, protože jste schopni například spustit Logic App. To je komplexní orchestrační řešení s mnoha existujícími konektory a jste schopni v něm namodelovat i velmi pokročilou logiku.

![](/images/2019/2019-03-20-14-40-19.png){:class="img-fluid"}

Chcete nějaký příklad? Logic App má konektor do různých komunikačních nástrojů jako je MS Teams nebo Slack a také integrace do ITSM nástrojů, třeba ServiceNow nebo PagerDuty. Nasazovat můžete i ARM šablony nebo ARM operace, kterými se dá třeba vypnout virtuální stroj! Představme si třeba, že při překročení budgetu spustíte workflow, které pošle email managerovi s informací a v něm budou dvě tlačítka: Vynadat a Smazat. Pokud šéf klikne na Vynadat, spustí se část workflow, která rozešle emaily s výhrůžkami. Pokud klikne na smazat, spustí se ARM operace nebo Azure Automation skript, který zastaví všechna VM v dané subskripci nebo jim to rovnou smaže.


Chcete mít náklady pod kontrolou a vědět kolik vás co stojí? Azure je ideální způsob jak toho dosáhnout. Díky Azure Cost Management si můžete dělat i sofistikované analýzy, plánovat rozpočet pro projekty a automaticky reagovat na jejich překročení. Vyzkoušejte si!