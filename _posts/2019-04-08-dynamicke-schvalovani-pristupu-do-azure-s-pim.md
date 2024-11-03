---
layout: post
published: true
title: Dynamické schvalování přístupů do Azure s Privileged Identity Management
tags:
- Governance
- Security
---
Na svém notebooku občas potřebujete spustit proces, který je privilegovaný a nainstaluje nějaký software. To ale neznamená, že je dobrý nápad trvale pracovat pod účtem root nebo Administrator. Na privilegovaný účet eskalujete pouze v okamžiku, kdy je to vážně potřeba. Na to jsme všichni zvyklí, pojďme totéž dělat v Azure. Priviliged Identity Management je sudo pro cloud.

Vyzkoušejme si to na typickém případu produkčního prostředí. Zeptáte se vlastníka projektu kdo všechno tam má mít přístup a on se zamyslí, kdo by mohl něco takového potřebovat. Dá vám seznam 30 lidí. Obvykle s tím jsou dva následující problémy:
* Ne všichni potřebují přístup typu Owner nebo Contributor, protože se zabývají jen určitou oblastí - monitoring, zálohování apod. To vyřešíte s role-based-access-control.
* To, že občas vývojář potřebuje hasit potíže v produkci neznamená, že tam má mít přístup pořád. Pokud se přihlašuji jednou za měsíc na dvě hodiny, neměl bych mít přístup trvale. Zbytečně se zvyšuje potenciál úniku dat, havárií a jiných nepříjemných situací. To si dnes vyzkoušíme vyřešit s Azure Privileged Identity Management.

# Praktický příklad
Vyzkoušíme si velmi jednoduchý scénář. Mějme produkční zdroje a v mém případě budou ohraničeny Resource Group. Uživatel My User 1 tam v principu nemá co dělat, je to vývojář. Ale aplikaci nemáme dokonalou a občas mu potřebuji přístup dát pro hašení požárů.

Jako administrátor aktivuji PIM, kterému udělím práva přesouvat RBAC uživatelů podle procesů, které si nastavíme.

![](/images/2019/2019-04-07-19-47-28.png){:class="img-fluid"}

Podívejme se do production Resource Group. Uživatele My User 1 jsem tam přidal pouze v roli Reader, která mu běžně stačí.

![](/images/2019/2019-04-07-19-55-34.png){:class="img-fluid"}

Pojďme aktivovat PIM v této skupině zdrojů. Můžete jít ještě níž na úroveň individuálních zdrojů nebo naopak výš a rozhodovat se za celé subskripce nebo management group (skupiny subskripcí).

![](/images/2019/2019-04-07-20-14-23.png){:class="img-fluid"}

Seznam je prázdný - musíme totiž nejprve provést discovery zdrojů PIM nástrojem.

![](/images/2019/2019-04-07-20-15-54.png){:class="img-fluid"}

![](/images/2019/2019-04-07-20-16-25.png){:class="img-fluid"}

Klikneme na production Resource Group.

![](/images/2019/2019-04-07-20-17-33.png){:class="img-fluid"}

Podívejme se na dostupné role. Všimněte si, že tady je kompletní RBAC včetně custom rolí, pokud nějaké vytvoříme. Vytvoříme pravidla pro roli Contributor.

![](/images/2019/2019-04-07-20-19-20.png){:class="img-fluid"}

Prvním konceptem jsou eligible role, tedy o co má uživatel právo požádat. Aktivní role jsou ty, kdy administrátor na časově omezenou dobu Contributora povolil. Expired jsou ty, kdy čas vypršel a právo bylo odebráno.

![](/images/2019/2019-04-07-20-19-56.png){:class="img-fluid"}

Pojďme nejprve do nastavení rolí. Můžeme definovat pravidla pro přiřazení rolí, například jestli je nutné uvádět nějaké vysvětlení v žádosti nebo je vyžadováno více-faktorové ověření.

![](/images/2019/2019-04-07-20-21-11.png){:class="img-fluid"}

Důležitější pro mě teď bude nastavení aktivace, tedy schvalovací proces pro eligible uživatele. Můžeme definovat maximální dobu přiřazení práva, vyžadovat vysvětlení důvodu a já si zapnu požadavek na approval. I bez něj to může dávat smysl, protože máte evidenci kdo o co zažádal a jak to podložil, nicméně já chci i aktivní schválení.

![](/images/2019/2019-04-07-20-22-06.png){:class="img-fluid"}

Zvolil jsem administrátora admin@mujazure.tk, který musí tyto požadavky nejprve schválit.

![](/images/2019/2019-04-07-20-23-00.png){:class="img-fluid"}

Přidejme tedy uživatele, kteří mají možnost žádat o přiřazení role Contributor.

![](/images/2019/2019-04-07-20-23-39.png){:class="img-fluid"}

![](/images/2019/2019-04-07-20-24-41.png){:class="img-fluid"}

Mohu udělat dvě věci - buď rovnou oprávnění přiřadit (Active) nebo jen dát možnost o něj žádat (Eligible).

![](/images/2019/2019-04-07-20-25-29.png){:class="img-fluid"}

Zvolil jsem eligible a mohu omezit časový úsek přiřazení této možnosti. To že je někdo eligible tak nemusí být nekonečné, ale časově omezené třeba po dobu projektu.

![](/images/2019/2019-04-07-20-25-54.png){:class="img-fluid"}

Přihlásím se teď jako My User 1.

![](/images/2019/2019-04-07-20-28-14.png){:class="img-fluid"}

Podívám se do resource group a jsem tam pouze Reader.

![](/images/2019/2019-04-07-20-30-33.png){:class="img-fluid"}

Ale vznikla mi potřeba získat Contributora. Jdu do Privileged Identity Management a kliknu na My Roles.

![](/images/2019/2019-04-07-20-33-10.png){:class="img-fluid"}

Vidím, že jsem eligible - kliknu tedy na aktivaci.

![](/images/2019/2019-04-07-20-34-22.png){:class="img-fluid"}

Stačí mi jedna hodina. Všimněte si, že platnost mohu také odložit například pokud plánujeme odstávku na víkend a chci to mít schválené dopředu. Také uvedu důvod své žádosti.

![](/images/2019/2019-04-07-20-40-16.png){:class="img-fluid"}

Přepneme se zpět k administrátorovi a tam na nás čeká něco ke schválení.

![](/images/2019/2019-04-07-20-41-59.png){:class="img-fluid"}

![](/images/2019/2019-04-07-20-43-10.png){:class="img-fluid"}

Jako My User 1 bych měl vidět, že můj požadavek byl schválen.

![](/images/2019/2019-04-07-20-43-56.png){:class="img-fluid"}

Jako My User 1 se teď podívám do nastavení production Resource Group a už jsem Contributor.

![](/images/2019/2019-04-07-20-45-02.png){:class="img-fluid"}

Teď můžu provádět co je potřeba. Po hodině se můj přístup zase zruší. Já jsem ale skončil dřív, tak si oprávnění sám odeberu hned.

![](/images/2019/2019-04-07-20-46-00.png){:class="img-fluid"}

Jako administrátor si mohu prohlédnout audit komu jsem co schválil.

![](/images/2019/2019-04-07-20-48-56.png){:class="img-fluid"}

K dispozici mám i konkrétní akce, které uživatel v průběhu zásahu prováděl a to nejen na úrovni PIM, ale především co dělal se zdroji - něco v Azure smazal, přidal, upravil?

![](/images/2019/2019-04-07-20-49-30.png){:class="img-fluid"}

# Co k tomu potřebuji a co se s tím dá dál dělat
PIM je součást Azure Active Directory ve verzi P2 a velmi doporučuji si ji pořídit a to nejen kvůli PIM, který považuji za zásadní bezpečnostní prostředek pro váš život s Azure, ale v P2 najdete i mnoho dalších zajímavých funkcí jako jsou dynamické skupiny, Identity Protection, více-faktorové ověřování a další vychytávky.

PIM může reagovat nad libovolnou rolí a protože těch je je dnes přes 100 a můžete si definovat i svoje vlastní, dokážete být velmi granulární. Tak například:
* Jedna z rolí umožňuje řídit just-in-time access v nastavení NSG (firewallu) v rámci Azure Security Center. RDP nebo SSH přístup k mašině je tak by default zakázaný a přes Azure Security Center si ho můžete krátkodobě odemknout. Tato funkce ovšem nemá schvalovací kolečko, ale to můžeme vyřešit přes PIM - můžete být eligible na právo žádat o just-in-time access.
* Pokud jedete na Linux VM a zapnete si jejich integraci s AAD, přístup dovnitř je řešen také RBAC rolí. Přes PIM jste tak schopni řídit žádosti o přístup do Linux OS.
* Jestli na vaší aplikaci pracuje dodavatel mimo vaši firmu, může být PIM skvělý způsob jak spravovat přístupy dodavatelů velmi přehledně a bezpečně. Nechcete dávat nic natvrdo, protože pak na to často zapomenete a dodavatel má i nadále práva, byť už na projektu dávno nepracuje.
* Jedna z rolí v Azure umožňuje přístup do VM sériovou konzolí, což je výborná věc pro řešení krizových situací, kdy VM přestane reagovat na RDP nebo SSH. Trvalý přístup na konzoli může být ale bezpečnostní riziko, takže co kdyby i administrátor projektu tato práva neměl trvale a žádal si o ně?

Uvedené možnosti jsou mimo cloud dosažitelné velmi obtížně. Tím, že v Azure je všechno softwarově definované a automatizovatelné můžete si prostředí vymazlit o poznání bezpečnější, než svět tradičního IT. Zkuste si to. AAD P2 opravdu stojí za to a můžete si ho vyzkoušet v 30 denním trial.


