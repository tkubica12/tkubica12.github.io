---
layout: post
title: 'Dedikované servery v Azure, na kterých běží Azure ... pro klid vašich byrokratů?'
tags:
- Compute
---
Ne každá firma nebo subjekt státní správy je mentálně připravena na Infrastructure as a Service v public cloudu, protože například z historických či jiných důvodů požaduje, aby virtuální stroje běžely na fyzickém serveru, který je dedikovaný právě pro vás. Toho v Azure můžete dosáhnout použitím isolated typu VM, což je největší model VM dané řady, například Standard_E64is_v3. To je ale už hodně velký server a možná potřebujete raději několik menších. Navíc i přestože jste v ten okamžik na fyzickém serveru garantovaně sami, neznamená to, že při havárii fyzického nodu nebudete přesunuti na jiný (i když i tam pochopitelně budete sami). Navíc nedostanete nějaké unikátní číslo hardware, které si zanesete do evidence a ani to nemusí stačit licenčním hrám pro některé typy software, které virtualizaci jako licenční rozhraní neuznávají. Nově ale tyto situace můžete řešit v Azure s konceptem Dedicated Host.

# Co je Dedicated Host vs. bare metal služby
Nová služba Dedicated Host není bare metal řešení. Není to tak, že dostanete fyzický server a o virtualizaci se musíte starat sami (to by bylo spíše podobné službě VMware v Azure nebo dedikovaný hardware pro SAP). Dedicated Host znamená, že si zaplatíte kompletně celý hardwarový server ve vteřinové sazbě, ale na něm běží normálně Azure. Můžete na něj tedy umisťovat VM různých velikostí v rámci dané řady a za VM samotné už neplatíte. 

Tak například si koupíte dedicated host řady Dsv3. Tento fyzický stroj má 40 fyzických core a 256GB paměti, takže pokud váš licenční software neuznává virtualizaci, tohle bude jeho ohraničení (nikoli celý Azure). Tento server vás bude stát asi 3,40 EUR za hodinu. V něm máte k dispozici 64 vCore, v rámci kterých si můžete pouštět Azure VM o velikostech od největší D64s_v3 až po nejmenší D2s_v3 do jeho maximální kapacity. Tak například můžete si v něm spustit 1x D32s_v3 + 1x D16s_v3 + 3x D4s_v3 + 2x D2s_v3.

# Vyzkoušejme Dedicated Host
Nejdřív si založíme Host Group.

![](/images/2019/2019-08-05-12-29-53.png){:class="img-fluid"}

Půjde o skupinu zakoupených hostitelů. V rámci této skupiny můžete říct kolik chcete zón dostupnosti, tedy řekněme racků. Můžu chtít servery u sebe nebo rozprostřít přes skupinu racků. Také tady říkáme, do jaké zóny dostupnosti (řekněme datového centra, budovy v rámci regionu) chceme server umístit.

![](/images/2019/2019-08-05-12-32-08.png){:class="img-fluid"}

Dále si pořídím dedikovaného hostitele.

![](/images/2019/2019-08-05-12-33-08.png){:class="img-fluid"}

Vyberu si server typu Ds_v3 a bude součástí skupiny mojeZelezo. Tento server bude ve fault doméně 1. Starší Windows a SQL licence berou tento typ řešení za outsourcing, novější nikoli - a právě pro ty nechybí možnost přenést si licence přes AHUB.

![](/images/2019/2019-08-05-12-35-21.png){:class="img-fluid"}

Tímto jsme si tedy vytvořili jeden fyzický server v zóně dostupnosti 1 a fault doméně 1. Mohli bychom přidat další a dát ho do fault domény 2. 

Podívejme se na tento objekt. Najdeme tam unikátní identifikátor hardware, který můžeme předat byrokratům.

![](/images/2019/2019-08-05-12-42-28.png){:class="img-fluid"}

Vytvořím si VM standardním postupem a zvolím typ stroje z řady Ds_v3 a zónu dostupnosti 1 (kde na mě čeká můj dedikovaný server).

![](/images/2019/2019-08-05-12-46-22.png){:class="img-fluid"}

Změna mě čeká až na záložce Advanced.

![](/images/2019/2019-08-05-12-39-00.png){:class="img-fluid"}

Vybereme předem zakoupený fyzický server.

![](/images/2019/2019-08-05-12-47-12.png){:class="img-fluid"}

VM naběhne standardním způsobem a všechno funguje zcela normálně. Jen za tuto VM už neplatím, protože jsem investoval do dedikovaného hostitele. Ostatně na něm informaci o své instanci uvidím:

![](/images/2019/2019-08-05-12-49-42.png){:class="img-fluid"}

Protože jsem vypnul automatické přesunutí na jiný server v případě havárie stávajícího, bude mě Microsoft informovat o nutnosti to udělat a následně, až to schválím, se dozvím svůj nový jednoznačný identifikátor fyzického serveru. Pokud automatické přesunutí zapnu, stane se to samo a o novém čísle se rovněž dozvím.

V době psaní článku je tato služba v Preview, takže ještě nemá definované SLA a má některá omezení, například není možné si výkon zarezervovat třeba na rok a získat slevu. Nicméně to se určitě v dohledné době objeví.

# Kdy Dedicated Host použít?

Za normálních okolností bych tento režim nepoužíval. Klasické řešení s platbou za každou VM je obvykle finančně výhodnější (platím jen za to, co aktuálně potřebuji a nemám před sebou problém jak co nejlépe využít zakoupené kapacity), flexibilnější (nejsem vázán na konkrétní generaci hardware a VM řadu), nicméně budou situace, kdy po dedicated host sáhnete:
* Pro vaše účetnictví, smluvy, zákonné požadavky či interní směrnice je nutné přistupovat k problému po serverech, ne po VM
* Vaše bezpečnostní směrnice znemožňují použít sdíleného hostitele, byť jsou VM velmi dobře izolované a výkon pinovaný
* Software, který používáte, vyžaduje zalicencování fyzických cores a neuznává virtualizaci jako rozhraní

Pro některé resorty státní správy tak může být dedicated host rozumné řešení, kdy využíváte plnohodnotnou IaaS v Azure a přitom dostojíte některým požadavkům na vás kladeným. V kombinaci s dalšími prostředky jako je šifrování disků vlastním klíčem, Azure Policy, RBAC, dedicated HSM a jiné technologie v oblasti governance vám tak může dedicated host pomoci odblokovat cloudovou cestu.




