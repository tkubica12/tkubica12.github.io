---
layout: post
title: 'Azure Stack: napojení na Azure Monitor pro hybridní správu'
tags:
- Monitoring
- AzureStack
---
Azure Stack nabízí základní telemetrii na úrovni hostitele, ale ten je vhodné doplnit pokročilým monitoringem z velkého Azure. Azure Stack a jeho monitoring z Azure Monitor je tak vlastně jednou z nejčastějších ukázek skutečné hybridního přístupu. Pro hostování svého IaaS si přinesu vlastnosti cloudu k sobě ve formě Azure Stack a současně využijí masivních clusterů, strojového učení a pokročilé funkce velkého cloudu pro přidání monitoringu.

Pojďme se na to dnes podívat.

# Napojení Azure Stack na Azure Monitor
První krok je v Azure založit log analytics workspace a opsat si jeho ID a klíč.

![](/images/2019/2019-05-29-06-51-11.png){:class="img-fluid"}

V Azure Stack administrátorském portálu si do katalogu stáhněte Extension pro automatické napojení VM do Azure Monitor.

![](/images/2019/2019-05-29-06-53-06.png){:class="img-fluid"}

Při vytváření VM v tenant portálu Azure Stack zvolte přidání Extension. Tam si vybereme Azure Monitor a vyplníme údaje pro připojení (ID a klíč v Azure) a také nainstalujeme Dependency agenta (tam se nic nekonfiguruje, ale ten pro Azure Monitor zajištuje síťový monitoring například pro servisní mapu).

![](/images/2019/2019-05-29-06-55-43.png){:class="img-fluid"}

Vrátíme se do Azure a vytvoříme Automation account. Projděte pak sekce Inventory, Change Tracking a Update management a propojte Automation a log analytics workspace. Pak ještě zapněte, že do těchto řešení chcete automaticky naboardovat všechna VM, která se do tohoto log analytics workspace napojí.

Podrobnější návod je tady: (https://docs.microsoft.com/en-us/azure-stack/user/vm-update-management)[https://docs.microsoft.com/en-us/azure-stack/user/vm-update-management]

Teď ještě vybereme co chceme logovat a sbírat.

![](/images/2019/2019-05-29-07-41-08.png){:class="img-fluid"}

# Monitoring a telemetrie
Telemetrije je systémem sbírána a jsou pro vás připraveny základní workbooky, které si můžete libovolně upravovat nebo vytvářet vlastní.

![](/images/2019/2019-05-29-07-12-09.png){:class="img-fluid"}

![](/images/2019/2019-05-29-07-09-14.png){:class="img-fluid"}

Připravena je podpora různých agregací od průměru přes percentily.

![](/images/2019/2019-05-29-07-09-53.png){:class="img-fluid"}

Vybírat můžete celou řadu čitačů.

![](/images/2019/2019-05-29-07-10-37.png){:class="img-fluid"}

![](/images/2019/2019-05-29-07-10-52.png){:class="img-fluid"}

![](/images/2019/2019-05-29-07-11-19.png){:class="img-fluid"}


# Logy
Logy ze syslog a Events ve Windows, které jsme v konfiguraci zapnuli, shromažďujeme do databáze, ve které je vše indexované a dají se dělat různé hledání v reálném čase i pokročilé transformace. V tomto prostoru jsou jak všechny logy, tak telemetrické údaje a můžete na základě nich dělat výstupy, grafy či reagovat spuštěním různých alertů včetně integrace do ITSM nástrojů, push notifikací do mobilní aplikace Azure, email či komplexní workflow v Logic App (například zprávu do Teams, Slacku, Service Now apod.).

![](/images/2019/2019-05-29-07-06-14.png){:class="img-fluid"}

# Update management, Inventory, Change tracking
Jak jsme na tom s patchováním?

![](/images/2019/2019-05-29-07-13-17.png){:class="img-fluid"}

![](/images/2019/2019-05-29-07-13-55.png){:class="img-fluid"}

Pokud chcete, můžete aktualizace plánovat a řídit odtud a to jak pro Windows tak pro Linux.

![](/images/2019/2019-05-29-07-14-59.png){:class="img-fluid"}

V inventáři zjistíme kde co a v jakých verzích máme nainstalované.

![](/images/2019/2019-05-29-07-16-07.png){:class="img-fluid"}

Můžeme sledovat klíčové soubory a záznamy v registrech.

![](/images/2019/2019-05-29-07-16-38.png){:class="img-fluid"}

Zkoumat na jakých strojích jaké služby a Linux daemony máme spuštěné.

![](/images/2019/2019-05-29-07-17-11.png){:class="img-fluid"}

V sekci Change tracking pak tyto informace najdete s časovým kontextem, tedy kdy co se na kterém stroji změnilo, což se velmi hodí pro troubleshooting problémů a přehlednost.

![](/images/2019/2019-05-29-07-18-07.png){:class="img-fluid"}

![](/images/2019/2019-05-29-07-19-35.png){:class="img-fluid"}

# Service map a monitoring síťového provozu
Azure Monitor sbírá informace o síťovém provozu a jste tak schopni vizualizovat s kým si vaše jednotlivé VM v Azure Stack povídají, na jakých portech, s jakou odezvou a ztrátovostí a rozkreslit tuto mapu závislostí až na jednotlivé procesy v OS, které provoz generují.

![](/images/2019/2019-05-29-07-03-16.png){:class="img-fluid"}

Kromě této vizualizace si můžeme prohlédnout i připravené workbooky na další analýzu.

![](/images/2019/2019-05-29-07-45-16.png){:class="img-fluid"}

Tak například tady vidíme odchozí provoz a všimněte si, že řešení také koreluje údaje s reputační databází a dokáže identifikovat komunikaci na nevhodné systémy v Internetu, třeba Command and Control servery botnetů apod.

![](/images/2019/2019-05-29-07-46-30.png){:class="img-fluid"}

Pro identifikaci případných bezpečnostních problémů se mi může hodit report kam že to moje servery vlastně komunikují.

![](/images/2019/2019-05-29-07-47-22.png){:class="img-fluid"}

Selhávají nějaká spojení?

![](/images/2019/2019-05-29-07-48-01.png){:class="img-fluid"}

Nebo jak vypadal provoz v Azure Stacku nebo konkrétní VM včera vs. dnes?

![](/images/2019/2019-05-29-07-48-51.png){:class="img-fluid"}

![](/images/2019/2019-05-29-07-49-03.png){:class="img-fluid"}

# Automatizace
Díky automation accountu můžeme ve strojích pravidelně spouštět PowerShell nebo Python skripty například pro nějaké rutinní úlohy (čištění disku, rotace logů) nebo instalace software. Také můžeme udržovat OS v přesně daném desired state s využitím PowerShell DSC, což funguje pro Windows, ale dá se použít i pro Linux. Pro naboardování VM v Azure Stack proveďte kroky popsané tady: [https://docs.microsoft.com/en-us/azure/automation/automation-dsc-onboarding#physicalvirtual-windows-machines-on-premises-or-in-a-cloud-other-than-azureaws](https://docs.microsoft.com/en-us/azure/automation/automation-dsc-onboarding#physicalvirtual-windows-machines-on-premises-or-in-a-cloud-other-than-azureaws)

![](/images/2019/2019-05-29-07-22-15.png){:class="img-fluid"}

![](/images/2019/2019-05-29-07-24-07.png){:class="img-fluid"}

![](/images/2019/2019-05-29-07-25-09.png){:class="img-fluid"}

# Alerting
Potřebujete na základě překročení normálu generovat nějaký Alert? V rámci Azure Monitor klikneme na Alerts a nastavíme si jeden třeba na CPU VM v našem Azure Stacku.

![](/images/2019/2019-05-29-07-51-29.png){:class="img-fluid"}

Velmi zajímavá možnost je kromě fixní hodnoty použít i strojové učení. Alert pak analýzou časových řad stanoví co je běžná zátěž a naučí se běžné patterny hodiny, dne či týdne a informovat vás bude v okamžiku, kdy je situace značně nestandardní.

![](/images/2019/2019-05-29-07-53-33.png){:class="img-fluid"}

Modrá vizualizace jsou skutečné hodnoty a to červené spočítané horní a dolní pásmo normálu. Alert dostanu v okamžiku, kdy se hodnota dostane mimo toto dynamicky stanovované pásmo.

![](/images/2019/2019-05-29-07-54-26.png){:class="img-fluid"}

Události můžete filtrovat, protože třeba za některých okolností nechcete, aby se alarm vyvolal - například v průběhu maintenance okna. Akce je definována jako Action group.

![](/images/2019/2019-05-29-07-56-18.png){:class="img-fluid"}

Můžete odeslat email, push notifikaci do Azure mobilní aplikace, integrovat ITSM nástroj, posílat webhook a všechny ostatní věci vyřešíte přes Azure automation (například možnost v serveru pustit skript) nebo Logic App workflow s připravenými konektory na Office365, Teams, Slack, Wordpress, PageDuty, Service Now a mnoho dalších řešení.



Azure Monitor je velmi silný nástroj pro pokročilý monitoring a analýzu a je to časté hybridní řešení, kdy on-premises svět (Hyper-V, VMware, Azure Stack) napojíte na Azure Monitor. Pro zákazníky využívající Azure Stack je ale integrace nejsilnější - onboarding je zjednodušení a získáváte úplně maximum.

