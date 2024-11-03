---
layout: post
title: 'Azure Stack: databázové služby'
tags:
- AzureStack
- SQL
---
V Azure máte k dispozici plně spravovaný SQL, který pro vás připravuje Microsoft. Jdete do portálu, vytvoříte si ho a během chvilky dostanete login do databáze. Microsoft zajišťuje SLA, zálohování, patching a tak podobně. V Azure Stack v tuto chvíli není SQL, o který by se staral Microsoft, přesto můžete svým zákazníkům nabídnout podobnou službu pro SQL a MySQL. O databáze se staráte vy jako provozovatel, ale vaši uživatelé mohou jednoduše a automatizovaně získat přístup do databáze přímo z portálu. Jak to funguje?

Základem je, že jako poskytovatel provozujete SQL nebo MySQL. To můžete dělat buď v Azure Stack, ale klidně i vedle v tradičním IT. Do Azure Stack nainstalujete resource provider, který umožňuje vašim uživatelům jednoduše získat přístup na kliknutí. Nabízíte tak databázi s vaší přidanou hodnotou (správa, zálohování apod.) s tím, že pro uživatele je to transparentní, jednoduché na získání a rychle k dispozici. Například se můžete rozhodnout použít stávající SQL cluster v tradičním IT a nabízet přístup do něj, současně také vytvořit třeba neredundantní SQL přímo v Azure stack a ten nabízet jako nižší SKU třeba pro vývojáře nebo dev/test prostředí nebo klidně ze šablony zrovoznit AlwaysOn cluster přímo v Azure Stack.

Než se pustíme do detailů zmiňme ještě další možnosti. IaaS šablonu pro zprovoznění SQL, MySQL nebo jiné databáze v Azure Stack můžete stáhnout přes marketplace a uživatelům nabídnout. Na rozdíl od PaaS přístupu tady ale po instalaci oni přebírají odpovědnost za život serveru (patchování apod.). Ještě je tu jedna velmi jednuduchá a plně PaaS databáze - Storage Table. Pro jednoduché tabulky přístupné přes HTTP API (na principu OData) mohou vaši zákazníci použít tu (jsou s ní spojeny jen storage poplatky, za databázi samotnou nic neplatíte).

# Jak to vlastně funguje?
Do vašeho SQL dáte administrátorský přístup resource provideru v Azure. Podívám se do svého SQL a ten je v tuto chvíli prázdný.

![](/images/2019/2019-03-12-20-25-16.png){:class="img-fluid"}

Jako uživatel jdu do portálu a chci si založit SQL databázi.

![](/images/2019/2019-03-12-20-25-53.png){:class="img-fluid"}

Na výběr mohu mít různá SKU, které mi provozovatel Azure Stack nabídl - třeba dražší s vysokým SLA a levnější s menším SLA.

![](/images/2019/2019-03-12-20-27-16.png){:class="img-fluid"}

Jako uživatel si vytvořím svůj vlastní login a název databáze.

![](/images/2019/2019-03-12-20-28-10.png){:class="img-fluid"}

Co se po kliknutí tlačítka Create v SQL stane? Resource provider se do ní připojí, vytvoří novou databázi, nový login a tyto dva propojí.

![](/images/2019/2019-03-12-20-29-39.png){:class="img-fluid"}

Jako uživatel pak vidím svůj login jako objekt v portálu.
![](/images/2019/2019-03-12-20-33-52.png){:class="img-fluid"}

A také se dozvím na jaké adrese SQL běží, resp. konektivitu pro mě zprostředkovává resource provider samotný. Teď už tedy mohu začít DB využívat.

![](/images/2019/2019-03-12-20-34-55.png){:class="img-fluid"}

Azure Stack pro vás aktuálně neřeší kompletní správu vašich SQL a MySQL databází tak, jako to je v Azure. Na druhou stranu chrání vaše investice, protože můžete využít stávajícího SQL/MySQL prostředí a modernizovat přístup k němu. 

Chcete nabízet SQL přímo v Azure Stack? Žádný problém. K dispozici máte komplexní šablonu, která vytvoří AlwaysOn cluster a zjednoduší vám tak iniciální deployment a monitoring.
