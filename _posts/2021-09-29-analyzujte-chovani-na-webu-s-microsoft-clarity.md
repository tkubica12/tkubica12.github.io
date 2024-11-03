---
layout: post
title: 'Analyzujte chování uživatelů na webu s Microsoft Clarity - navždy zdarma'
tags:
- Monitoring
---
Zvykl jsem si na to, že s Google Analytics získám poměrně detailní informace o využívání mého blogu čtenáři. Ale to jsem dosud nevěděl o Microsoft Clarity - nástroj, který je zdarma a připadá mi naprosto skvělý, skoro magie. Musel jsem ho na blog přidat a tady je výsledek.

# Microsoft Clarity
Jde on online řešení pro analýzu uživatelů vaší webové aplikace. Podobně jako Google Analytics ho integrujete jednoduše tím, že do stránek vložíte jednoduchý Javascript kód (já jsem to udělal do šablony Jekyll, kterým stránky generuji). Clarity nabízí nádherné GUI a místo klasických statistik, na které jsem zvyklý, ukazuje a analyzuje chování uživatelů formou, kdy tomu dobře rozumím i bez čtení textu. 

Tady jsou hlavní tři oblasti, které dělá:
- Analyzuje chování uživatelů a hledá v něm zajímavé události - například naštvané ťukání na grafický prvek na obrazovce, který evidentně nedělá to, co si uživatel myslel, že dělat bude.
- Nahrává session co do pohybu po stránce (klikání, scrollování) a pak vám tyto session umožňuje doslova přehrát - je úžasné se podívat jak se vám uživatel po stránce pohybuje.
- Ukáže vám heatmapy - kde se na stránce nejčastěji kliká a jak se scrolluje. Kolik lidí doscrolluje článek až dolu a kolik procent skončí v půlce?

A to nejlepší? Microsoft Clarity je zdarma a podle webu bude navždy zdarma. Není to "freemium", kdy jakmile chcete něco pokročilejšího, hodně zaplatíte (například jako když v Google Analytics chcete opravdu dělat analytics) ani časově omezená nabídka. Přitom řešení plně odpovídá požadavkům GDPR. Více najdete tady [https://clarity.microsoft.com/](https://clarity.microsoft.com/)

# Robot analyzuje chování
U mě se toho na webu samozřejmě zas tak moc neděje, přesto je statistika zajímavá:

[![](/images/2021/2021-09-24-08-45-11.png){:class="img-fluid"}](/images/2021/2021-09-24-08-45-11.png)

Když se podívám na live demo (což je analýza sebe sama - jsou to data pro stránku Microsoft Clarity), najdu toho víc. Tady je "zběsilé klikání".

[![](/images/2021/2021-09-24-08-47-57.png){:class="img-fluid"}](/images/2021/2021-09-24-08-47-57.png)

Kliknutím na vybranou zajímavou situaci se nastaví filtry, takže vidím údaje těch, co zběsile klikají - odkud jsou, z jakého prohlížeče apod.

[![](/images/2021/2021-09-24-08-49-00.png){:class="img-fluid"}](/images/2021/2021-09-24-08-49-00.png)

No a můžeme se také podívat na záznam. 

# Nahrávání session
Co uživatelé na mém blogu dělají? Pojďme si někoho vybrat a podívat se.

[![](/images/2021/clarity1.gif){:class="img-fluid"}](/images/2021/clarity1.gif)

To je úžasné - podívejme se na nějaký bohatší web v live demo.

[![](/images/2021/clarity2.gif){:class="img-fluid"}](/images/2021/clarity2.gif)

[![](/images/2021/2021-09-24-09-00-12.png){:class="img-fluid"}](/images/2021/2021-09-24-09-00-12.png)

Výborné je, že máte velké možnosti vyhledávání - třeba vás zajímají nahrávky z nějaké kombinace určité části webu, typu zařízení nebo detekovaného chování (například zběsilé klikání na něco co nijak nereaguje).

[![](/images/2021/2021-09-24-09-01-50.png){:class="img-fluid"}](/images/2021/2021-09-24-09-01-50.png)

# Heatmapy
Pojďme teď vizualizovat pro nějaký článek jak uživatelé scrollují - evidentně někteří z vás nečtou do konce :)

[![](/images/2021/2021-09-24-09-03-51.png){:class="img-fluid"}](/images/2021/2021-09-24-09-03-51.png)

Totéž lze udělat s klikáním - tady na příkladu live demo.

[![](/images/2021/2021-09-24-09-06-54.png){:class="img-fluid"}](/images/2021/2021-09-24-09-06-54.png)

Opět platí, že si to můžete filtrovat. Na co se nejčastěji kliká v USA vs. v České Republice? Je rozdíl v klikání mezi uživateli Windows a Mac?



Za mě - Microsoft Clarity je úžasný nástroj a to, že je zdarma, je výborná zpráva. Moc se mi líbí, že se nemusím ponořit do tabulek, grafů a statistik a porozumět jim Všechno je krásně vizualizované - zajímavé pro mě vybrané události, kam mi lidé klikají, jak scrollují a nahrávky jak to reálně vypadá. Podle mě z toho, že koukáte uživateli virtuálně přes rameno zrovna v momentě, kdy vaší aplikace využívá, se dozvíte strašně moc. Vyzkoušejte to - je to zadáčo.
