---
layout: post
published: true
title: "Azure Defender (7): Ochrana serverové infrastruktury - řízení povolených aplikací"
tags:
- Security
---
Je v pořádku, když váš doménový řadič těží Bitcoin, web server provozuje Metasploit či Nmap pro scanování a útočení a váš databázový server smaží Hydru ve snaze rozlousknout nějaká hesla slovníkovým útokem? Předpokládám, že asi ne. Azure Defender vám s funkcí Adaptive Application Controls dokáže poradit co na server patří a co ne díky umělé inteligenci, která bude vaše servery sledovat a pak učiní doporučení. Ty pak můžete jednoduše aplikovat na konkrétní systémy a když se na nich spustí něco jiného, dozvíte se o tom - a to jak pro Windows tak Linux. 

Spuštění procesu není jediný způsob jak v systému rozjet škodlivý kód. Útočník může zneužít dynamicky linkované knihovny (DLL) a spustit v nich nějakou funkci, což se v seznamu procesů neobjeví. Možná jeho útok poběží uvnitř nějakého frameworku, který musí být povolen (třeba webový server). Může se také pokusit modifikovat právoplatný proces a přibalit se k němu (jasně - dá se sledovat digitální podpis vydavatele a hash souboru, ale to u interně vyvinuté aplikace s častým nasazováním může být dost nepraktické) nebo použít nějakou fileless techniku z povolené aplikace (třeba Powershell či Python interpret) případně si data odnese využitím nějakého vzdáleného managementu (WMI, SNMP, ...). Nicméně to nesnižuje dopad opatření typu whitelisting, protože většina živých útočníků si nějaký nástroj zkusí spustit a tím vzniknou důležité stopy. Whitelisting aplikací tedy neznamená, že můžete vypnout ostatní ochrany serveru, ale smysl pro zvýšení bezpečnosti určitě má.

Možná si říkáte kdo by se chtěl trápit se sestavováním seznamu používaných aplikací - nemohl by to udělat robot? Mohl - ten robot je Azure Defender, který bude na vaše prostředí nějakou dobu koukat a pak sám navrhne jak to nastavit. Azure Defender aktuálně podporuje pouze auditní režim (nebrání spuštění aplikace), takže vám nic nerozbije a jeho použití je tak především o sběru důležitých informací. Samozřejmě vás napadne, že kromě alertu v Azure Defender by bylo možná dobré o události jako spuštění neschválené aplikace informovat SIEM. To samozřejmě můžete udělat díky přímé integraci do Azure Sentinel případně přes Event Hub integrace do nástrojů typu QRadar, ArcSight nebo Splunk.

# Sběr informací a učení
Azure Defender pro vás bude sbírat informace a tom, co se na serveru běžně spouští a bude se pár dní učit. Následně vám předloží svá doporučení.

[![](/images/2021/2021-01-15-09-09-55.png){:class="img-fluid"}](/images/2021/2021-01-15-09-09-55.png)

Doporučení budou nejen za jednotlivé servery, ale robot se je pokusí roztřídit do skupin, které vypadají na stejné nastavení.

[![](/images/2021/2021-01-15-09-11-01.png){:class="img-fluid"}](/images/2021/2021-01-15-09-11-01.png)

Tohle zjistil Azure Defender o mém Windows stroji a doporučuje aplikace k povolení.

[![](/images/2021/2021-01-15-09-12-26.png){:class="img-fluid"}](/images/2021/2021-01-15-09-12-26.png)

Také identifikoval další spouštěné aplikace, ale pro jejich whitelisting doporučuje je projít a promyslet to. To dává docela smysl, protože jedna z aplikací je tam Chocolatey, kterou ve Windows používám pro instalaci balíčků ve svém iniciačním skriptu. Možná následně už nechci, aby tento nástroj bylo běžné spouštět.

[![](/images/2021/2021-01-15-09-14-41.png){:class="img-fluid"}](/images/2021/2021-01-15-09-14-41.png)

Podívejme se na doporučení robota pro můj Linux stroj.

[![](/images/2021/2021-01-15-09-15-33.png){:class="img-fluid"}](/images/2021/2021-01-15-09-15-33.png)

Vezmu ta doporučení všechna a kliknutím na tlačítko Audit z nich udělám sledovací pravidla a na ty se podíváme blíže.

[![](/images/2021/2021-01-15-09-17-11.png){:class="img-fluid"}](/images/2021/2021-01-15-09-17-11.png)

# Nastavení a rozpoznání aplikace
Po kliknutí na tlačítko Audit mi Azure Defender založil dvě skupiny aplikačních pravidel. Podívejme se nejprve na ty Linuxové.

[![](/images/2021/2021-01-15-09-23-53.png){:class="img-fluid"}](/images/2021/2021-01-15-09-23-53.png)

Přidám si pravidlo, že binárka /opt/myapp/starter je v pohodě, pokud ji pustí uživatel tomas.

[![](/images/2021/2021-01-15-09-26-36.png){:class="img-fluid"}](/images/2021/2021-01-15-09-26-36.png)

V případě Windows můžete kontrolovat seznam vydavatelů, tedy kdo aplikaci podepsal.

[![](/images/2021/2021-01-15-09-32-05.png){:class="img-fluid"}](/images/2021/2021-01-15-09-32-05.png)

Podobně jako v Linuxu můžeme označit aplikace podle cesty.

[![](/images/2021/2021-01-15-09-32-37.png){:class="img-fluid"}](/images/2021/2021-01-15-09-32-37.png)

# Vznik události
Připojil jsem do svých VM a spustil tam nějaké neschválené aplikace. Podívejme se na výsledné alerty v Azure Defender.

[![](/images/2021/2021-01-16-09-29-04.png){:class="img-fluid"}](/images/2021/2021-01-16-09-29-04.png)

Podívejme se na detaily - uživatel root spustil proces find. To samozřejmě nemusí být nic vážného, ale pokud něco takového není očekávané, někdo v serveru vyhledával soubory včetně systémových. 

Co s tím uděláme? Kliknutím na tlačítko Take action si můžeme přečíst doporučené kroky.

[![](/images/2021/2021-01-16-09-34-30.png){:class="img-fluid"}](/images/2021/2021-01-16-09-34-30.png)

Pokud bychom věděli, že jsou naplánované operace a změnová řízení, které vygenerují velké množství takových hlášek, můžeme chtít dočasně vypnout vznik alertů. Samozřejmě to můžeme udělat u zdroje, tedy v konfiguraci Adaptive Application Controls, ale to může být mnoho skupin a nastavení a dočasné filtrování v Azure Defender bude jednodušší a udržíme si informace (hlášky v logu budou, jen alerty se nezvednou).

[![](/images/2021/2021-01-16-09-38-22.png){:class="img-fluid"}](/images/2021/2021-01-16-09-38-22.png)

Jak už víme, na události lze mít připravené automatizační kroky v Logic App a spustit je buď operátorem nebo automatizovaně. Může jít například o automatizační proceduru, která zjistí podle tagu v Azure kdo je vlastníkem stroje a pošle mu email s informací a podezřelé aplikaci. Něco podobného jsme už v předchozích dílech řešili, příklad naleznete tam.

[![](/images/2021/2021-01-16-09-40-30.png){:class="img-fluid"}](/images/2021/2021-01-16-09-40-30.png)

V neposlední řadě je tu možnost poslat alerty do nadřazeného SIEMu jako je Azure Sentinel pro pokročilejší a širší korelaci, hunting, globální automatizaci, threat intelligence a další bezpečnostní postupy.



Azure Defender s Adaptive Application Controls jsou dobrý způsob, jak ve stabilním produkční prostředí získávat informace a spouštění aplikací, které nejsou nutné pro běh aplikace nebo běžnou operativu. S vytvářením seznamu vám pomůže robot a posbírané události jsou další klíčové střípky informací do bezpečnostní skládanky. Opět platí, že tato funkce Azure Defender není omezena na VM v cloudu a můžete ji použít na stroje v libovolném prostředí ať už je to vaše vlastní serverovna, hosting nebo jiný cloud, díky napojení přes Azure Arc for Servers.


