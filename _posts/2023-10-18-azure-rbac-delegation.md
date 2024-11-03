---
layout: post
published: true
title: Azure RBAC delegace s omezením - samoobslužnost pro vaše Azure uživatele
tags:
- Governance
---
Kdo se v oblasti Azure governance pohybujete delší dobu, určitě znáte následující situaci, která v přísných enterprise podmínkách vede na ruční schvalovačky a ztrátu produktivity. Ta už ale má v preview velmi elegantní řešení, čtěte dál.

# Problém s klasickým RBAC v přísném enterprise prostředí
Typicky nechceme, aby běžný uživatel měl právo přiřazovat práva dalším uživatelům, protože by si tam například pozval své kamarádíčky a bůh ví co by tam dělali. Navíc co když začne dávat práva i sám sobě a následně odstraní některé komponenty, které jsou pro něj zapovězené, třeba Azure politiky nebo směrovací pravidla na subnetu. 

Proti tomu ale jde to, že chceme zejména pro aplikační komponenty používat bezheslové řešení a least privilege principy, tedy nasadit User Managed Identity. Aplikační komponenta, třeba kontejner v Azure Kubernetes Service, má přistupovat do Azure Cosmos DB? Nechť přímo pro tuto komponentu existuje Managed Identity, která má přístup právě jen do této jediné služby. Žádná hesla, klíče nebo tokeny, které se mohou rozkecat, zneužít, zapomenout odrotovat nebo omylem ponechat v Gitu či dokumentaci. Žádný univerzální účet Service Principal, který bylo od IT tak těžké získat, že s ním děláme úplně všechno úplně odevšad. Jenže to má háček - identitu vytvořím a musím k ní přiřadit příslušná práva. Aha - ale to my přece nesmíme. Takže ticket ... Terraform to pěkně vymlaskne a pak se zastaví a bude hezky čekat na někoho, kdo to odklepne? To není ideální.

Dosavadní přístupy k odlehčení toto problému zahrnují:
- Šéfovi týmu věříme. Ten dostane roli Owner a je odpovědný za řízení práv. Možná mu ale nevěříme zas až tolik, takže Owner je jen na scope, kde nemůže rozbít networking nebo politiky, takže například do nějaké Resource Group. To je určitě dobré, ale šéf pořád není ovladatelný přes Terraform provider a časté omezení scope na Resource Group vede k tomu, že místo členění zdrojů si všechno házíme na jednu hromadu. Ještě je tu varianta různých speciálních zámečků, například blokace některých requestů politikou (to ale není úplně logické a dobře spravovatelné) nebo přes deny assignmenty (ty ale zatím fungovaly výhradně s Azure Blueprints a ty jsou už pár let v preview).
- Práva řídíme přes GitOps nějakým Infrastructure as Code, takže tým si zažádá ve formě Pull Request a ono se to stane. To je určitě také dobré, ale opět to nelze udělat v jednom kroku v rámci Terraformu a navíc některé týmy nemusí být znalostně a procesně připravené na takovou variantu. Pro některé týmy je klikání v portálu produktivnější, protože mohou začít a získávají zkušenosti s cloudem místo toho, že je zavřete na Terraform a Git kurz a oni tam píšou kód na něco, co v životě neviděli.
- V rámci nějakého blueprintu (ať už Azure Blueprintu nebo Terraform modulu) aplikačnímu týmu připravíme "standardní" řešení s několika připravenými identitami včetně přiřazených práv na nejčastěji používané úkony - jednu na přístup ke Key Vault, druhou na vytváření AKS, třetí na přístup na data a tak podobně. Brzy ale zjistíme, že každý tým chce něco jiného, takže buď začneme dělat všechno univerzálnější a univerzálnější (vzdáváme se least privilege) nebo začneme vytvářet nějaké úžasné klikátko, kde si lidé při žádosti o subskripci mohou říct co jak tam chtějí (což je obtížně udržitelné a navíc se to pořád mění).

Když to  shrneme, tak by to řešila vlastně jednoduchá věc. Nechť můžu dát někomu roli User Access Manager, ale omezit jak s ní může nakládat. Jaké role smí přiřazovat a komu je smí přiřazovat. Jednoduché, že? Na papíře jistě ano a jde v zásadě o formu Attribute Based Access Control, v praxi to ale produktovému týmu dost dlouho trvalo udělat. Ale už to je.

# Nové řešení v preview - Azure RBAC delegace s omezeními
Úplně nejlepší bude si to jednoduše proklikat.

Mám tady jednu Resource Group a přiřadím do ní speciální práva svému uživateli.

[![](/images/2023/2023-10-17-14-48-00.png){:class="img-fluid"}](/images/2023/2023-10-17-14-48-00.png)

Role bude privilegovaná, konkrétně User Access Manager.

[![](/images/2023/2023-10-17-14-48-49.png){:class="img-fluid"}](/images/2023/2023-10-17-14-48-49.png)

Přidám svého uživatele.

[![](/images/2023/2023-10-17-14-49-35.png){:class="img-fluid"}](/images/2023/2023-10-17-14-49-35.png)

Teď můžu přidat další podmínky - to je nové.

[![](/images/2023/2023-10-17-14-50-12.png){:class="img-fluid"}](/images/2023/2023-10-17-14-50-12.png)

Můžu omezit pouze role, které může přiřazovat. To je hodně užitečné, protože mu dám třeba možnosti jako je role pro SQL, Cosmos DB, Azure storage, vytváření VM nebo něco takového. Nebude mít ale možnost třeba měnit networking nebo být Owner nebo něco takového. 

Další varianta je k tomu přidat i omezení na typ účtů, což zvolíme my a probereme později.

Třetí varianta je k rolím přidat vyloženě i výčet uživatelů, kterým lze role přiřazovat. Tohle je vhodné pro role pro skutečné lidi (uživatelské účty), například členy týmu. Vybrat si tam můžete i skupinu v Microsoft Entra ID (AAD).

[![](/images/2023/2023-10-17-14-51-24.png){:class="img-fluid"}](/images/2023/2023-10-17-14-51-24.png)

Já volím jen jednu roli Storage Blob Data Reader (čtecí přístup do Blob storage) a principal type pouze Service principals (což zahrnuje i managed identity). Můj uživatel tedy nebude schopen dávat tuto roli uživatelským účtům, jen "systémovým"-.

[![](/images/2023/2023-10-17-14-52-22.png){:class="img-fluid"}](/images/2023/2023-10-17-14-52-22.png)

To je celé, teď se naloguji jako uživatel a chci přidávat práva.

[![](/images/2023/2023-10-17-14-54-00.png){:class="img-fluid"}](/images/2023/2023-10-17-14-54-00.png)

Na výběr mám jen omezenou sadu rolí, v mém případě jen tu jednu.

[![](/images/2023/2023-10-17-15-41-45.png){:class="img-fluid"}](/images/2023/2023-10-17-15-41-45.png)

Vybrat managed identitu, pokud je v mém scope, což je aktuálně tato resource group, můžu.

[![](/images/2023/2023-10-17-14-59-40.png){:class="img-fluid"}](/images/2023/2023-10-17-14-59-40.png)

Nicméně uživatele žádné a to ani sám sebe.

[![](/images/2023/2023-10-17-15-00-45.png){:class="img-fluid"}](/images/2023/2023-10-17-15-00-45.png)


Myslím, že takhle na screenshotech je to velmi jasné a geniálně jednoduché. Trvalo to dlouho, ale v preview už můžete dát uživatelům možnost se obsloužit sami ať už klikáním nebo v rámci jejich automatizace a přitom nevytváříte bezpečnostní riziko. Doporučuji promyslet a změnit strategii v přístupu ke governance, pokud máte aktuálně velmi přísné podmínky, které snižují pohodlí a produktivitu vašich uživatelů.