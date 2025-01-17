---
layout: post
title: 'Azure Stack: serverless s Azure Functions'
tags:
- Serverless
---
Co si takhle koupit servery v balíku Azure Stack a pak běžet appky bez serverů? Možná se to zdá divné, ale dává to smysl, protože serverless je o tom, že se o servery a jejich škálování nestarám a soustředím se na logiku. Azure Functions jsou platformní služba, kterou v Azure Stack můžete mít. Podívejme se jak vypadá.

# Rozdíly mezi Functions v Azure a v Azure Stack
Zásadní výhodou Functions v Azure je jejich takřka nekonečné a rychlé škálování, což je dané obrovskou kapacitou a elasticitou Azure. V Azure Stack máte jednotky fyzických serverů, takže se dají očekávat jistá omezení. Tím zásadním z pohledu škálování dnes je to, že PaaS v Azure Stack zatím nepodporuje autoškálování podkladových zdrojů. Azure Functions můžete podobně jako v Azure pustit v consumption modelu (pak běží na shared nodech) nebo dedikovaně v Service Plan. V první variantě budou Functions schopné si dynamicky vytvářet instance podle potřeby, ale to vše pouze v mezích  shared zdrojů (počtu VM), které Azure Stack operátor alokoval. Je tedy na něm, aby v případě velkého zájmu zákazníků na shared služby zvýšil počet jejich instancí. Není to nic složitého (instance jsou Virtual Machine Scale Set a stačí jen změnit číslo jejich počtu a udělá se to samo), ale nějakou dobu to trvá a operátor se musí rozhodnout to udělat. Pokud nasadíte Functions do dedikovaného plánu, tak ani tam aktuálně (ale připravuje se to) není autoscaling, takže v případě potřeby si musíte sami plán zvětšit (ale jak jsem psal na tomto webu dříve, funguje to tak, že operátor Azure Stack má pro zákazníky připravený pool nastartovaných zdrojů a vy si je přivlastníte přes portál - nicméně narozdíl od Azure jsou zde logicky kapacitní omezení a Azure Stack operátor asi nebude mít připraven nekonečný počet VM).

Druhým rozdílem je to, že Azure Stack zatím pracuje na Functions v1, zatímco v Azure je v1 i v2. 

# Input a Output binding do Azure Stack i Azure
Podobně jako v Azure můžete kromě triggerů přidávat i Input a Output binding, například pro jednoduché zapsání do storage queue. V rámci GUI v Azure Stack si snadno vyberete storage account v Azure Stack a průvodce vám sám vytvoří spojení. Možná se vám ale hodí Output binding do storage ve velkém Azure (například chcete data přijímat a generovat v Azure Stack, zpracovávat je přes Functions v Azure Stack, ale výsledek zpracování zapsat do storage v public Azure pro využití nějakého sofistikovanější processingu typu Azure Databricks). To uděláme tak, že půjdeme do Application Settings ve Functions a založíme nový záznam. Do něj vložíme connection string na storage ve velkém Azure:

![](/images/2019/2019-06-20-16-01-16.png){:class="img-fluid"}

Následně v Output bindings můžeme toto nastavení vybrat.

![](/images/2019/2019-06-20-16-02-08.png){:class="img-fluid"}

Tímto způsobem mohou tedy vaše Functions psát jak do Azure Stack, tak do Azure.

# Functions v Azure Stack
Z pohledu způsobu práce je Azure Stack prakticky stejný jako Azure. 

![](/images/2019/2019-06-20-16-26-11.png){:class="img-fluid"}

Co se týče napojení vývojových nástrojů, tak tam, kde nástroj podporuje Functions v1 vám to bude fungovat. Pod svým účtem ve Visual Studio 2019 vidím jak svoje Azure subskripce, tak prostředí Azure Stack. Mohu tedy nasazovat do Web App v Azure i Azure Stack, Cloud Explorer ukáže zdroje v Azure a tak podobně.

![](/images/2019/2019-06-20-16-27-38.png){:class="img-fluid"}

Následně můžete vzít svůj Functions projekt a poslat ho do Azure Stack přímo z vývojového prostředí.

![](/images/2019/2019-06-20-16-41-48.png){:class="img-fluid"}

![](/images/2019/2019-06-20-16-42-31.png){:class="img-fluid"}

![](/images/2019/2019-06-20-16-42-53.png){:class="img-fluid"}


Vyzkoušejte svět serverless s Azure Functions. Můžete je provozovat v Azure, v Azure Stack nebo je nasazovat do IoT Edge platformy. Pro budoucnost si můžete vyzkoušet i Azure Functions s využitím KEDA projektu pro Kubernetes, třeba v Azure Kubernetes Service. ALe to už je na jiný článek někdy příště.



