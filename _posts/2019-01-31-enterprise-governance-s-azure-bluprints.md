---
layout: post
status: publish
title: Enterprise governance s Azure Blueprints pro všechny vaše subskripce
tags:
- Security
- Governance
---
Azure nabízí výborné prostředky pro řízení vašeho cloudu z pohledu přístupů, politik a governance obecně. Tohle všechno můžete zabalit do blueprintu a řídit jeho aplikaci na celý váš enrollment - jednotlivé vaše země, dceřinky, organizační celky i samotné subskripce. Podívejme se dnes na Azure Blueprints a koncepty, které využívá jako je Management Group, Azure Policy, Azure RBAC nebo Azure Resource Manager šablony.

# Potřeba governance a enterprise model
Ve větších firmách se používá EA model nákupu Azure, kdy máte jednu smlouvu (enrollment) a v EA portálu můžete spravovat svoje subskripce. Dokážete tak pro projekty vytvářet jejich separátní subskripce. Práva pro jejich vytváření můžete také delegovat a celkový balík peněz v enrollmentu rozdělovat do departementů, například poboček v zemích, po značkách, dceřinkách apod. Jak ale na tyto věci navázat nějaké techničtější politiky a nastavení?

Jakmile založíte pro projekt subskripci, často se v enterprise firmách musí udělat následující kroky:
* Nastavit ownera subskripce, typicky nějakého vlastníka projektu
* Založit přístupy pro role podpůrných týmů, například Network Contributor za síťové oddělení, Backup Contributor pro lidi řešící zálohování, Reader pro možnosti monitorování
* Nastavit klíčové politiky, které se musí třeba pro produkční prostředí dodržovat. Třeba nutnost používat image VM předpřipravené IT týmem, zákaz používání regionů, ve kterých není vybudována Express Route linka, nutnost používat pouze šifrované disky, nutnost zapnout auditní záznamy na databázi, vynucení nějaké struktury tagování či povinné začlenění do bezpečnostního monitoringu s Azure Security Center
* Příprava základních zdrojů, které v každé subskripci mají mít a které vyžadují koordinaci centrálního týmu. Typicky vytvoření VNETu s nastavením peeringu do hub subskripce se sdílenými zdroji (propojení do on-premises, AD řadič, DNS server), založení Azure Monitor účtu pro sbírání logů v subskripci nebo vytvoření subnetů a směrovacích pravidel pro posílání provozu na Azure Firewall či řešení třetí strany.

Všechny tyto kroky se dají naskriptovat a automatizovat. Nově je ale k dispozici Azure Blueprint, který dokáže elegantně všechny tyto automatizace spojit do jednoho řešení a hlavně je ukládat, verzovat a nasazovat přímo z portálu.

# Management Group
Ve velkém nasazení často potřebujete řešit nějaké politiky ne na každé subskripci zvlášť, ale za celou skupinu. Použití hierarchie tak jak je v EA portálu (enrollment, departementy) by ale nemuselo být ideální. Finanční a vlastnická hierarchie (EA portál) často neodpovídá technickým požadavkům a hierarchii. Mnohdy vypadá jinak a hlavně může vyžadovat i vícero stupňů větvení (např. CZ a SK, dále dcera1 a dcera2, dále finance a marketing, dále produkce a test apod.). Hierarchie pro správu politik, řízení přístupu do portálu nebo nasazování zdrojů by tak měla být flexibilnější a nezávislá na EA struktuře.

Přesně to řeší Management Group. Musíte mít jednu hlavní (root), následně libovolnou hierarchii skupin a dole v nich subskripce. Pro dnešní ukázku to budu také využívat.

Nejdřív si vytvořím základní kořen Management Group

![](/images/2019/2019-01-30-17-07-56.png){:class="img-fluid"}

![](/images/2019/2019-01-30-17-08-51.png){:class="img-fluid"}

První skupina se může přidávat pár minut. Pojďme zadat další skupinu Finance a následně skupinu Marketing.

![](/images/2019/2019-01-30-17-09-58.png){:class="img-fluid"}

Teď bych potřeboval skupinu Finance i Marketing zařadit do základní skupiny mojeFirma.

![](/images/2019/2019-01-30-17-12-06.png){:class="img-fluid"}

Výsledek bude vypadat nějak takhle.

![](/images/2019/2019-01-30-17-13-23.png){:class="img-fluid"}

Pojďme teď přesunout dvě mé subskripce. Jednu do Finance, druhou do Marketing.

![](/images/2019/2019-01-30-17-14-08.png){:class="img-fluid"}

![](/images/2019/2019-01-30-17-14-39.png){:class="img-fluid"}

# Vytvořme si Azure Blueprint

Založíme si první blueprint.

![](/images/2019/2019-01-30-18-24-03.png){:class="img-fluid"}

Dáme mu nějaký název, popisek a také určíme, kde má být tento objekt uložen. Jde o to kde ty předpisy budou a potažmo kdo je může modifikovat (s tím kam se aplikují to nemá nic společného). Typicky to bude přímo na root úrovni, ale umím si představit, že u situací typu holding bude možná každý člen holdingu chtít tyto věci mít zcela autonomní.

Teď do svého blueprintu potřebujeme založit potřebné artefakty, tedy definice co vlastně chceme.

![](/images/2019/2019-01-30-18-26-47.png){:class="img-fluid"}

Všimněte si jaké kategorie máme v nabídce. Policy je Azure Policy, o kterých jsem už na tomto blogu psal. Jde o pravidla, která chceme vynutit v našem prostředí - zákaz používání některých zdrojů, například VM bez network security group, vynucení použití konkrétních imagů, omezení provozu jen na určité regiony apod. Druhé jsou role, tedy RBAC. To umožňuje říkat kdo co smí v subskripci dělat. Třetí je ARM šablona na úrovni subskripce, což umožňuje automatizovat vytváření některých zdrojů i na úrovni subskripce (například nastavení Azure Security Center). Poslední je vytvoření Resource Group.

![](/images/2019/2019-01-30-18-28-20.png){:class="img-fluid"}

Začněme tedy s Role assignment. V tuto chvíli to necháme jednoduché - v subskripci chceme mít Ownera (například skupinu v AD). Konkrétního uživatele nebo skupinu tady ale specifikovat nebudeme, protože to třeba chceme u každé subskripce jinak a blueprint má být univerzální. Hodnotu vyplníme až v okamžiku aplikace blueprintu na nějakou subskripci.

![](/images/2019/2019-01-30-18-29-23.png){:class="img-fluid"}

Dál si nastavíme nějakou Azure Policy. V seznamu je dnes asi 150 připravených politik a několik iniciativ (sdružení vícero politik), ale můžete si vytvářet i svoje vlastní.

![](/images/2019/2019-01-30-18-36-20.png){:class="img-fluid"}

První co jsem vybral je politika vyžadující šifrování v blob storage. Zkrátka nebude možné vytvořit storage bez šifrování nebo u existující šifrování vypnout.

![](/images/2019/2019-01-30-18-37-08.png){:class="img-fluid"}

Druhá politika bude omezovat množství dostupných regionů. Řekněme, že děláme blueprint pro subskripce primární využívající IaaS a ty potřebují privátní spojení do on-premises. Pro takovýto typ subskripcí má IT vybudovanou Express Route linku jen do omezeného výčtu regionů a nechce umožnit vytváření VM v jiných. Konkrétní seznam regionů budeme ovšem zadávat až v okamžiku přiřazení blueprintu k nějaké subskripci.

![](/images/2019/2019-01-30-19-10-59.png){:class="img-fluid"}

Dále si v blueprintu chceme předepsat založení nějaké Resource Group. Tentokrát půjde o něco, co chci skutečně pokaždé stejně, takže pro změnu hodnoty zadáme přímo v definici blueprintu. Půjde o resource group určenou pro založení síťařiny.

![](/images/2019/2019-01-30-19-21-27.png){:class="img-fluid"}

Blueprint obsahuje Resource Group a v ní můžeme zakládat další artefakty.

![](/images/2019/2019-01-30-19-22-03.png){:class="img-fluid"}

Pojďme nastavit přísupová pravidla (RBAC) pro tuto konkrétní Resource Group. Rád bych, aby síťařský tým měl na tyto zdroje přístup v roli Network Contributor. Není to na úrovni subskripce, jen pro tuto specifickou Resource Group to tak chci. Rovnou vyplním například AD skupinu správců sítě (v mém případě dávám ale jen user1).

![](/images/2019/2019-01-30-19-23-13.png){:class="img-fluid"}

Jako další artefakt použijeme ARM šablonu, která vytvoří nějaké zdroje v Azure. Je to má oblíbená oblast a šablona může být velmi chytrá a komplexní, ale pro dnešní ukázku se držme jednoduchého příkladu. Budu chtít založit VNET (v praxi bych měl i vyřešit peering do hub VNETu a tak podobně). Šablona bude vypadat nějak takhle (na vstupu má parametr networkRange).

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "networkRange": {
            "type": "string",
            "metadata": {
                "description": "Network range"
            }
        }
    },
    "variables": {
        "vnetName": "westeurope-net"
    },
    "resources": [
        {
            "type": "Microsoft.Network/virtualNetworks",
            "name": "[variables('vnetName')]",
            "apiVersion": "2017-06-01",
            "location": "[resourceGroup().location]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "[parameters('networkRange')]"
                    ]
                }
            }
        }
    ]
}
```

Vložíme tuto šablonu jako artefakt.

![](/images/2019/2019-01-30-19-31-50.png){:class="img-fluid"}

V šabloně jsou parametry a ty opět budeme chtít dodat až při aplikaci blueprintu na subskripci.

![](/images/2019/2019-01-30-19-32-21.png){:class="img-fluid"}

Uložme si teď svůj blueprint.
![](/images/2019/2019-01-30-19-32-58.png){:class="img-fluid"}

# Publikování a přiřazení blueprintu
Blueprint je připraven, můžeme ho publikovat.

![](/images/2019/2019-01-30-19-33-43.png){:class="img-fluid"}

Přidáme číslo verze a popis verze.

![](/images/2019/2019-01-30-19-34-20.png){:class="img-fluid"}

Pojďme teď blueprint aplikovat.

![](/images/2019/2019-01-30-19-35-21.png){:class="img-fluid"}

Zvolím jednu ze svých subscription a verzi blueprintu.

![](/images/2019/2019-01-30-19-36-20.png){:class="img-fluid"}

Výchozí nastavení nepřidává na nasazené objekty zámečky, takže vytvořené věci je možné v subscription upravit dle standardního RBAC (takže např. Owner může změnit cokoli). Pokud by nám to vadilo, tak si buď pohrajeme s RBAC aby projektový tým nebyl Owner, ale měl nižší oprávnění, nebo si necháme udělat zámečky. Ty způsobí že ani Owner nemůže nastavení definovaná blueprintem změnit (jediná cesta by byla změnit blueprint a na to jsou jiná práva, běžný Owner subskripce nemusí stačit, pokud nechceme).

![](/images/2019/2019-01-30-19-36-50.png){:class="img-fluid"}

Při vytváření blueprintu jsme některé parametry chtěli vyplňovat až při přiřazení blueprintu subskripci. Tady jsou. User2 bude Owner a povolíme jen dva **evropské** regiony.

![](/images/2019/2019-01-30-19-37-57.png){:class="img-fluid"}

Dále určíme network rozsah.

![](/images/2019/2019-01-30-19-38-34.png){:class="img-fluid"}

Pozorujme průběh nasazení bluprintu.

![](/images/2019/2019-01-30-19-40-17.png){:class="img-fluid"}

Hotovo - blueprint je aplikován
![](/images/2019/2019-01-30-19-42-10.png){:class="img-fluid"}

# Vyzkoušejme
Podívejme se teď do subskripce a ubezpečme se, že blueprint zafungoval. Nacházím, dle předpokladu, resource group network-westeurope-rg a v ní vytvořený VNET.

![](/images/2019/2019-01-30-19-43-18.png){:class="img-fluid"}

Podívám se na RBAC pro tuto skupinu. Vidím, že User1 je Network Contributor tak, jak jsme specifikovali pro tuto skupinu. Dále vidíme, že User2 je Owner pro celou subscription.

![](/images/2019/2019-01-30-19-44-57.png){:class="img-fluid"}

A co Azure Policy? Je vytvořena?

![](/images/2019/2019-01-31-05-41-41.png){:class="img-fluid"}

Můžu se pokusit politiku porušit a nasadit zdroj v neschváleném regionu a tento selže.

![](/images/2019/2019-01-31-05-43-28.png){:class="img-fluid"}


Jste velká organizace a chcete mít Azure plně pod kontrolou? Nabízíte Azure do holdingu, concernu či dceřinek? Azure Blueprint je výbornou metodou zastřešení a nasazení klíčových komponent governance jako je Azure Policy, Role-based-access-control nebo vytváření zákadních zdrojů.




