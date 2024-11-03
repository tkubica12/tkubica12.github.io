---
layout: post
title: 'Zkušenosti s Bicep pro Azure po pár měsících - na ARM už si nevzpomenu, Terraform v ohrožení'
tags:
- Kubernetes
---
V poslední době jsem pár svých demo projektů začal přepisovat do Bicep. Jsou to dost komplexní scénáře, na kterých se dobře ukázala síla Bicep a rád je srovnávám s Terraform, ve kterém také dost píšu. Jaké jsou zkušenosti? Stojí za to?

# Moje projekty nově v Bicep
Mám aktuálně 3 projekty na GitHubu, které aktivně píšu nebo přepisuji do Bicep. Jeden je nové demo na AKS a té infrastruktury je tam tak akorát, ale hodně se tam řádí se zapisováním různých věcí do Key Vaultu, je tam AKS, Private Link, hodně práce s identitami a rolemi. Druhý projektík je demo na Azure Defender. Tam jsou o dost jiné typy zdrojů, hodně infrastruktury, ale i jiných služeb. Třetí scénář je demo prostředí na komplexní networking - to je velká míra složitosti, všechny ty VNETy, peeringy, firewall, NSG, VPNky, různé exotické provázanosti a návaznosti.

Tady jsou odkazy:
- [https://github.com/tkubica12/aks-demo](https://github.com/tkubica12/aks-demo)
- [https://github.com/tkubica12/azure-networking-lab](https://github.com/tkubica12/azure-networking-lab)
- [https://github.com/tkubica12/azdefender-demo](https://github.com/tkubica12/azdefender-demo)

# Rozšíření do Visual Studio Code je myslím lepší, než pro Terraform
Stejně jako pro Terraform umí VS Code radit a doplňovat, ale pro Bicep je to opravdu vychytané. V zásadě pro mě téměř zmizela potřeba se dívat do dokumentace nebo kopírovat příklady. Co mě opravdu příjemně překvapilo je to, že editor napovídá nejen klíče, ale i hodnoty. To je pro mě hodně užitečné:

[![](/images/2021/2021-04-24-10-38-50.png){:class="img-fluid"}](/images/2021/2021-04-24-10-38-50.png)

Vysvětlivky při najetí na nějaký klíč také hodně pomáhají.

[![](/images/2021/2021-04-24-10-39-40.png){:class="img-fluid"}](/images/2021/2021-04-24-10-39-40.png)

Doplňovaní hodnot funguje překvapivě dobře a to i pro vnořené složitější objekty i včetně těch, kterou jsou ve skutečnosti reference.

[![](/images/2021/2021-04-24-10-41-07.png){:class="img-fluid"}](/images/2021/2021-04-24-10-41-07.png)

Dokonce pokud použijete moduly, chápe VS Code jaké vstupy jsou pro něj potřeba.

[![](/images/2021/2021-04-24-10-42-08.png){:class="img-fluid"}](/images/2021/2021-04-24-10-42-08.png)

[![](/images/2021/2021-04-24-10-42-27.png){:class="img-fluid"}](/images/2021/2021-04-24-10-42-27.png)

# Moduly jsou zásadní přínos jazyka oproti ARM
Na moduly jsem si hodně zvykl a používám je pořád. U Terraformu to dělám také, tam ale ještě využívám toho, že modul je adresář a všechny tf soubory v něm se použijí. To mi umožňuje rozdělit si zdroje do vícero souborů a přitom nemusím předávat parametry. To mám rád a v Bicep to nejde ... ale zjišťuji, že mi to vlastně už nevadí.

Odbočka k ARMu. Ten umožňoval moduly řešit jako vnořené šablony, ale z megasouboru zůstal pořád megasoubor, jen komplikovanější. Navíc domyslet jak to funguje s proměnnými, co se vidí a co nevidí, bylo složité. Čistší varianta s linkovanou šablonou, kde ty jsou v jiném souboru (tak jak teď Bicep moduly nebo podobně jako Terraform adresáře), byla strašlivě nepohodlná, protože Azure si je musel být schopen stáhnout. Udělat soubor, poslat do storage nebo Gitu, pustit, zjistit že nefunguje, opravit, poslat do storage ... to bylo peklo.

Moduly Bicepu jsou strašně jednoduché a postavené na souboru. Oproti Terraformu je to otázka vkusu, ale to, že je to odkaz na jediný soubor má své výhody (nemusím řešit adresářovou strukturu, ujišťovat se, že mám všechny soubory modulu na správném místě apod.) - je to opravdu jednoduché a přehledné. To, že si potřebuji předávat výstupy a parametry mě navádí na správné rozmyšlení co k sobě patří a jak to dělat opakovatelné. Jasně, s Terraformem to jde taky, ale Bicep mě k tomu ještě víc vede. 

# Práce s řetězci a escapování je bomba
Jak už jsem párkrát psal ohromně dlouhé concat funkce v ARMu jsou peklo. Terraform to řeší elegantně a Bicep taky - stačí do řetězce dát 'text${promenna/reference}dalsitext' a frčíme. Ale to, že tým vybral jednoduché uvozovky byl geniální tah. Dvojité uvozovky tak nemusíte escapovat a Bicep to udělá za vás při převodu na JSON ARMu. Můžete taky použít trojici jednoduchých uvozovek a máte víceřádkový vstup kde nemusíte escapovat ani jednoduché uvozovky. Tady je příklad, kde jsem to hodně ocenil, protože trápení s escapováním jsem mýval často. Zejména tady, kdy ho musím udělat dvakrát. Je to in-line skript v Bash, který dvojité uvozovky interpretuje a já je tam potřebuji - takže jedna únikovka. To celé je ale hodnota jednoho JSON políčka a skáčeme podruhé.

Tady je ten atribut (jde o DeploymentScript resource):

```
scriptContent: '''
  wget https://github.com/tkubica12/azure-networking-lab/blob/master/bicep/inspectionCert/interCA.pfx
  az keyvault certificate import -n cert --vault-name $kv -f cert.pfx --password Azure12345678
  echo {\"result\":[\"$(az keyvault certificate show -n cert --vault-name kv7xenisbevfvqg --query sid -o tsv)\"]} > $AZ_SCRIPTS_OUTPUT_PATH
'''
```

Docela čitelné. Proč u echo nepoužiji jednoduché uvozovky, abych nemusel vyskakovat dvojité? No protože uvnitř mám vnořený příkaz, který chci interpretovat. Takže buď si budu hrát s jednoduchýma a ukončím před $() a pak zas nahodím nebo odskočím dvojité - je to asi jedno. Každopádně že to bude uvnitř JSON se nemusím trápit - žádné vyskakování, můžu mít víc řádků a lepší čitelnost. 

Do čeho se to překládá?

```
"scriptContent": "      wget https://github.com/tkubica12/azure-networking-lab/blob/master/bicep/inspectionCert/interCA.pfx\r\n      az keyvault certificate import -n cert --vault-name $kv -f cert.pfx --password Azure12345678\r\n      echo {\\\"result\\\":[\\\"$(az keyvault certificate show -n cert --vault-name kv7xenisbevfvqg --query sid -o tsv)\\\"]} > $AZ_SCRIPTS_OUTPUT_PATH\r\n    ",
```
... a to je hnus, zejména {\\\"result\\\":[\\\"$( mě děsí a vybavuji si ty hodiny ladění takových výrazů.

Další situace - z hlavní šablony spouštím vnořenou a předávám jí parametry, které získávám výstupem z jiné šablony.

```
"parameters": {
  "jumpSubnetId": {
    "value": "[format('{0}/subnets/jumpserver-sub', reference(resourceId('Microsoft.Resources/deployments', 'networks'), '2019-10-01').outputs.hubNetId.value)]"
  },
  "hubSubnetId": {
    "value": "[format('{0}/subnets/sharedservices-sub', reference(resourceId('Microsoft.Resources/deployments', 'networks'), '2019-10-01').outputs.hubNetId.value)]"
  },
  "webSubnetId": {
    "value": "[format('{0}/subnets/sub1', reference(resourceId('Microsoft.Resources/deployments', 'networks'), '2019-10-01').outputs.spoke2NetId.value)]"
  },
  "webLbPoolId": {
    "value": "[reference(resourceId('Microsoft.Resources/deployments', 'networks'), '2019-10-01').outputs.webLbPoolId.value]"
  }
}
```

V Bicep rozhodně jednodušší.

```
params: {
  jumpSubnetId: '${networks.outputs.hubNetId}/subnets/jumpserver-sub' 
  hubSubnetId: '${networks.outputs.hubNetId}/subnets/sharedservices-sub' 
  webSubnetId: '${networks.outputs.spoke2NetId}/subnets/sub1' 
  webLbPoolId: networks.outputs.webLbPoolId
}
```

# DSL má znaky čitelnosti YAMLu s robustností JSONu
Bicep (podobně jako Terraform) má vlastní DSL. ARM používá JSON, Kubernetes YAML, takže s obojím mám za sebou dost odpracovaných hodin. YAML se výborně čte a dá se hezky komentovat, ale rozpadne se odsazení a všechno je zničené (copy and paste z PDFka nebo mailu a snadno se netrefím). Jinak řečeno formátování je spojeno se syntaxí. 

Oproti tomu JSON můžu mít rozpadnutý co do odsazení nebo řádkování a on pořád funguje. Snadno využiji funkci VS Code, která mi JSON zformátuje hezky tak, aby byl rozumně čitelný a konzistentní ve všech objektech a souborech. Jenže zapomenutá uvozovka nebo čárka dokáže hodně potrápit. Zkrátka syntaxe nestojí na formátování a mezerách, ale na konkrétních znacích - na mezerách nezáleží, takže mi ho VS Code dokáže upravit tak, že bude vypadat vždy stejně.

Bicep stejně jako Terraform je DSL, ve kterém na mezerách nezáleží, přesto je jeho čitelnost a schopnost odpouštět na vysoké úrovni (znáte JSON situaci seznam, kde musí být všechno až na poslední položku zakončeno čárkou - vy přidáte řádek a musíte tomu původně poslednímu čárku přidat, nakopírujete položku z jiného seznamu kde je uprostřed a vložíte na poslední místo nového a musíte čárku odmazat apod.).

Takhle může vypadat definice zdroje trochu rozvrtaná - nesmím odřádkovat key od value, ale jinak to není problém.

[![](/images/2021/2021-04-24-17-49-38.png){:class="img-fluid"}](/images/2021/2021-04-24-17-49-38.png)

Ve VS Code zmáčknu CTRL+ALT+F (Format Document) a ono se to samo udělá hezké.

[![](/images/2021/2021-04-24-17-50-33.png){:class="img-fluid"}](/images/2021/2021-04-24-17-50-33.png)

# Nějaké limity a nedostatky?
Pár jsem jich našel a pracuje se na nich.

Tak například moduly jasou za mně úžasné a jednoduché, ale není dořešené jejich vzdálené sdílení nebo nějaká forma repozitáře. Zkrátka fungují skvěle jako součást jednoho projektu, ale není dořešeno využití například modulu z Internetu aniž bych si ho k sobě nenakopíroval. Není to jednoduché rozhodnutí - přímý odkaz na Git je nebezpečný, pokud nevyřešíte verzování modulů a většinou to má být privátní a ne veřejný Git. Nějaký korporátní repozitář a stažení z něj? To bude asi nejlepší, ale i tak jsme zase u verzování a nutnosti si to postahovat a připravit před spuštěním (viz terraform init). Rozhodně ale tohle chybí, nicméně pracuje se na tom - zapojte se do diskuse:
- [https://github.com/Azure/bicep/issues/2128](https://github.com/Azure/bicep/issues/2128)
- [https://github.com/Azure/bicep/issues/660](https://github.com/Azure/bicep/issues/660)

Druhá potíž je, že díky tomu jak funguje ARM nemůžete referencovat sami sebe, tzn. máte objekt, který je ale ve skutečnosti složený a jednotlivé dílky na sebe musí mířit a tím pádem zahrnují ID mezi sebou. Není to cross-reference, to ne, je to uvnitř jednoho objektu, ale Bicep neumožňuje si id nebo jméno vzít - musím ho uvést. To bylo ok u ARM, kdy se to řešilo tak, že jméno třeba load-balanceru dáte do proměnné a s tou pracujete, ale v Bicep se máte raději odkazovat. Takže mám LB s nějaký jménem, v něm health probe a také LB pravidlo - a to potřebuje odkazovat na probe. V tento okamžik se musím vrátit do ARM stylu, použít funkci a zadat název LB - a to je Bicep antipattern.

```
  probe: {
    id: '${resourceId('Microsoft.Network/loadBalancers', 'web-lb')}/probes/lbprobe'
  }
```

Není to moc častá situace, ale stává se - chcete-li, zapojte se do diskuse:
- [https://github.com/Azure/bicep/issues/1852](https://github.com/Azure/bicep/issues/1852)

Zbývají atributy jsou spíše vlastností (nebo je tak chápu) a mě nevadí, ale je dobré o nich vědět:
- Bicep není samostatný systém, je to překladač do ARMu, takže nečekejte, že se naučí jen tak pracovat s jiným cloudem nebo jinou technologií sám osobě - na to potřebuje nějakou funkci v Azure, například Azure Arc, kterým lze řídit technologie v jiných prostředích, ale dělá to Azure, ne Bicep. A nasazovat nad Azure? Nad AKS můžete použít GitOps addon (v podstatě managed Flux) a nad čímkoli univerzální spuštění skriptu (ARM DeploymentScript). Nebo prostě po nasazení infrastruktury pokračujte dál v CI/CD, třeba GitHub Actions krásně navážou a začnou řešit věci nad Azure, třeba Helmem nasadí aplikace do Kubernetu, založí tabulky v DB a nahrají syntetická data nebo nahodí kód do Azure WebApp.
- Bicep má ARM styl životního cyklu zdrojů, tedy mazání jen například přes zrušení resource group. Pokud potřebujete řídit cyklus kompletně včetně mazání, použijte režim Complete - ostatně pokud jedete Kubernetes, tak tenhle učebnicový příklad deklarativnosti znáte - co není (např. pro resource group) deklarováno, nesmí existovat a bude zastřeleno.
- Bicep je deklarativní. Podporuje sice smyčky a kondicionály, takže v tomto se můžete vyřádit (ARM je umí taky), ale aktuálně neumožňuje použít reálný kód pro nějaké složité dopočítávání hodnot nebo nějaké nativní integrace (třeba na IPAM pro přidělení IP adres). Já to rád nemám, pokud chcete počítat, učiňte tak v CI/CD, zapište do souboru hodnot a ty předejte Bicep (nechcete přece nasadit něco s hodnotou, která je vypočítaná, ale nikde neuložená) - tzn. já to nepotřebuji. Pokud tomu ale holdujete, pak mrkněte na Pulumi nebo Farmer (ten je zaměřený čistě na ARM a .NET).

# Suma sumárum
Po pár intenzivnějších použitích je Bicep můj nejoblíbenější Infra as Code nástroj, protože:
- Pracuji s Azure, nepotřebuji většinou víc cloudů
- Mám plnou podporu všech vlastností Azure včetně těch v preview
- Konečně mám nativní nástroj, který je čitelný, jednoduchý a editor ho dokonale umí
- Můžu modularizovat, aniž bych nahrával soubory do storage a ztrácel čas

ARM u mě končí - už pro něj nemám žádný důvod (přesto občas sáhnout napřímo po jeho funkci se hodí, ale psát přímo v něm už ne).

Terraform mám pořád rád a budu ho používat i dál. Ze dvou důvodů už ale mám jen jeden. Tím prvním bylo, že to bylo o tolik jednodušší a čitelnější, než ARM - to padlo. Tím druhým důvodem, a ten pořád platí, je fakt, že Terraform je etalon Infra as Code nástrojů, je velmi dobrý a umí více cloudů a někteří zákazníci staví všechno na něm. 

Takže chci umět Bicep a Terraform - oboje - a chtěl bych vám doporučit totéž. Stavět multicloudovou IaaS chci určitě Terraformem. Řídit specifické Azure věci jako governance, bezpečnost, správa subskripcí nebo využívání specializovaných služeb v rovině PaaS (kde je to stejnak v každém cloudu dost jiné) chci s použitím Bicep.