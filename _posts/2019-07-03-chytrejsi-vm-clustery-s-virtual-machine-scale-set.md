---
layout: post
published: true
title: Chytřejší VM clustery s Virtual Machine Scale Set
tags:
- Compute
---
Způsob práce s kontejnery stojí na plně automatizovaném řešení s orchestrací a immutable infrastrukturou, ale ne vždy je možné je použít nebo software není na takové prostředí připraven. Znamená to, že pak nezbývá než použít buď plně platformní služby (PaaS), které nemusí být tak univerzální a přiohnutelné nebo jít do klasického IaaS a dělat věci "standardně"? Vůbec ne - podívejme se na Virtual Machine Scale Set, který umožní nasazovat plné VM, ale chovat se k nim plně automatizovaně a podobně jako u kontejnerů.

# Proč použít Virtual Machine Scale Set
Za běžných okolností bych rozhodně doporučoval jít do platformních služeb (například Azure Application Services) nebo Azure Kubernetes Service. Mohou být ale situace, kdy to nejde nebo to není praktické:
* Možná váš kód potřebuje sáhnout hlouběji do OS a v takovém případě nemůže běžet v kontejneru. 
  * Potřebujete volat privilegovaná API nebo přímo přistupovat k hardware. To Kubernetes umožňuje pouze částečně (například už umí dobře řešit přístup na GPU čipy pro výpočty nebo machine learning, připravuje se blokový driver pro storage aby si kontejner mohl vytvořit vlastní file system apod.). Ale co třeba přístup k InfiniBand kartě u výpočetního clusteru? Nebo nutnost sáhnout do API hostitele, například ve Windows importovat vlastní kořenový certifikát do Windows Trust Store?
  * Někdy je nutné sáhnout do vizualizačních API, tedy do GUI komponent. Takové scénáře zahrnují různé formy VDI nebo automatizace testování grafické části aplikací.
  * Možná vyrábíte a testujete systémový software, který potřebuje přístup na úrovni plného OS. Příkladem může být třeba testování antiviru.
* Váš kód potřebuje extrémně nízké latence například pro High Frequency Trading nebo síťové appliance a přidaná vrstva síťových komponent OS (například síťový namespace, veth páry, Linux bridge, Open vSwitch) přidává zbytečnou latenci. Chcete co nejpřímější přístup k síti s SR-IOV nebo využívat DPDK instrukce pro práci s pakety.
* Váš workload vyžaduje scale-up nody s hodně pamětí a CPU. Pokud aplikace potřebuje 64 corů a 256GB paměti, některé výhody kontejnerů se ztrácí (na nodu ve finále bude stejně jen jeden).
* Budujete platformu nad kterou teprve následně poběží vaše aplikace, třeba v kontejnerech.

Některé z těchto bodů jsou důvody proč Azure sám používá VMSS jako podklad pod platformní služby. Dobrým příkladem je Azure Kubernetes Service (aplikační platforma), Azure Databricks (platforma pro datovou analytiku)nebo Azure Cyclecloud (platforma pro HPC). Když se podíváte do Azure Stack zjistíte, že PaaS platforma Application Services tam rovněž využívá VMSS. Z toho lze usuzovat, že i jiné PaaS služby ve velkém Azure využívají VMSS někde pod kapotou. Ostatně i řešení třetích stran při nasazení do Azure, které má zajistit škálování a autoškálování využívají právě VMSS - například F5, CheckPoint, Fortinet a další.

Za normálních okolností tedy doporučuji PaaS nebo kontejnery v AKS, ale jsou situace, kdy VM potřebujete a pak vám VMSS dá lepší metodu automatizace a škálování, než holé VM. Proto dává smysl se s ním seznámit.

# Jak VMSS funguje a kde je dostupný
VMSS začíná tím, že vytvoříte model. Jde v zásadě o předpis říkající takhle vypadá moje VM (OS image, sizing, automatizační skripty v VM Extensions) a takto je automaticky zařazeno do volitelného balancingu s Azure LB nebo Application Gateway. Dál jen řeknete kolik takových identických VM má ve VMSS být, což aktuálně může být 0-1000. Jste tedy schopni změnit číslo na 0 a běžící stroje efektivně odstranit (přestat platit), aniž byste museli smazat VMSS model. Na druhé straně spektra je 1000 VM vytvořených v jediném kroku a v jediném API volání (pozn. výchozí VMSS má limit 100 VM, pokud chcete víc, musíte vytvořit VMSS v režimu větší škálovatelnosti). Pokud potřebujete sestavit masivní výpočetní cluster je to rozhodně nejefektivnější cesta (při takových počtech narazíte jinak na rate limit API a budete muset vytváření VM dávkovat, takže to bude nejakou dobu trvat - pokud se začátkem výpočtu musíte počkat na naběhnutí všech nodů bavíme se o vyhozené hodině třeba 32000 cores, což jsou velké náklady). Počet požadovaných VM změníte jedním příkazem - změnou čísla s počtem. A ten příkaz dokonce ani není potřeba, protože jste schopni nastavit autoscaling, kdy VMSS bude počet samo měnit podle nějakého parametru (třeba zatížení CPU), takže po dokončení výpočtu vám cluster zmenší. Ještě zajímavější může být škálování podle délky fronty třeba v Service Bus (pak dává smysl i škálování na nulu). Pokud jednotlivé výpočetní úlohy zadáváte přes frontu, bude vám VMSS zvětšovat cluster podle potřeby, aby výpočet proběhl co nejrychleji.

Další zajímavou výhodou VMSS je schopnost změnit model běžícího VMSS. Ve výchozím stavu se vašim VM nic nestane, jen vám bude GUI říkat, že model se změnil. Můžete také nastavit automatický upgrade, takže VMSS samo změnu provede. Pokud máte LB s health probe můžete také použít nastavení rolling upgrade, kdy bude VMSS měnit instance postupně (pár jich překlopí na nový model a až začne aplikace reagovat pokračuje s dalšími). Co můžete v modelu změnit? Například základní image nebo VM extension (automatizační skript). Pokud bude vydán nový image obsahující aktualizace, můžete si nechat automaticky cluster přetvořit (takže místo patchování instancí je zahodíte a uděláte nové z novějšího image - přesně jak byste to dělali s kontejnery). Aplikace tam dostanete buď tak, že si vytvoříte custom image vždy s novou verzí (to je podobné světu kontejnerů) nebo je nasadíte automaticky na holý OS (třeba přes VM extension nebo nějakým externím mechanismem) případně kombinací obojího (např. máte custom OS se základním nainstalovaným software, který po startu dokonfigurujete - takhle se chová třeba AKS).

Kde bude VMSS instance vytvářet? Musí to být ve stejném regonu, ale nikoli nezbytně ve stejné zóně dostupnosti. VMSS tedy dovoluje automatické rozházení clusteru do availability zón.

V neposlední řadě může VMSS použít Low-priority VM. Jsou to VM jako každé jiné, ale dostáváte je ze zbytkové kapacity datového centra. Někdy jich dostanete hodně, někdy jen trochu, někdy žádnou a kdykoli vám ji mohou sebrat. Proč bych něco takového chtěl? Protože dostanu na tento způsob práce dramatickou slevou (u Linux mašiny někam k 80% dolu). Pokud provádím nějaké zpracování dat či výpočet, který trvá 10 hodin per-node, není to dobrý nápad (pokud o VM přijdu po 9 hodinách a musím výpočet zahodit a začít znova, tak moc neušetřím). Nicméně pokud jsou jednotlivé úlohy krátké, dává to smysl, pokud nepotřebuji celkovou práci dokončit v jasně ohraničeném čase (nevím kolik VM kdy dostanu, takže nevím, jak dlouho to budu počítat - ale to někdy nemusí vadit).

# Vyzkoušejme si VMSS na příkladu

Vytvoříme si prostředí s Azure SQL, VNET, Service Endpoint a VMSS.

```bash
# Create Resource Group
az group create -n web-rg -l westeurope

# Create VNET
az network vnet create -g web-rg \
    -n mynet \
    -l westeurope \
    --address-prefix 10.0.0.0/16

# Create subnet with SQL Service Endpoint
az network vnet subnet create -g web-rg \
    --vnet-name mynet \
    -n web \
    --address-prefixes 10.0.0.0/24 \
    --service-endpoints Microsoft.Sql

# Create Azure SQL
az sql server create -l westeurope \
    -g web-rg \
    -n mujsqlsrv987 \
    -u tomas \
    -p Azure12345678

# Create VNET rule
az sql server vnet-rule create --server mujsqlsrv987 \
    --name vnetEndpoint \
    -g web-rg \
    --subnet web \
    --vnet-name mynet

# Create database
az sql db create -g web-rg \
    -s mujsqlsrv987 \
    -n todo \
    -e Basic 

# Create VMSS
az vmss create -n webscaleset \
    -g web-rg \
    --image "Canonical:UbuntuServer:18.04-LTS:18.04.201905290" \
    --instance-count 2 \
    --vm-sku Standard_B1ms \
    --admin-username labuser \
    --admin-password Azure12345678 \
    --authentication-type password \
    --public-ip-address web-lb-ip \
    --subnet $(az network vnet subnet show -g web-rg --name web --vnet-name mynet --query id -o tsv) \
    --lb web-lb \
    --upgrade-policy-mode Manual
```

Vytváříme tedy VMSS se dvěma instancemi. Image specifikujeme přesně a schválně používám starší verzi Ubuntu image. V průběhu vytváření se může stát zajímavá věc. VMSS by default bude někdy provisionovat víc serverů, než kolik jste řekli (ale nebojte se, neplatíte za ně). Proč? Při vytváření 100 VM se může stát, že některé budou rychleji, než jiné. Protože VMSS je určeno pro co nejrychlejší provisioning clusteru, zadá VMSS nastartování raději většího množství VM a vezme ty, co budou alokovány jako první.

![](/images/2019/2019-07-03-08-26-32.png){:class="img-fluid"}

Naše VMSS by mělo být spuštěné a využívá poslední model.

![](/images/2019/2019-07-03-08-28-06.png){:class="img-fluid"}

Zatím nám ve VM ale neběží žádná aplikace. Nejprve se na to připravme tím, že nastavíme health probe a LB rules na balanceru.

```bash
az network lb probe create -g web-rg \
    --lb-name web-lb \
    --name webprobe \
    --protocol Http \
    --path '/' \
    --port 80
az network lb rule create -g web-rg \
    --lb-name web-lb \
    --name myHTTPRule \
    --protocol tcp \
    --frontend-port 80 \
    --backend-port 80 \
    --frontend-ip-name loadBalancerFrontEnd \
    --backend-pool-name web-lbBEPool \
    --probe-name webprobe
```

K instalaci aplikace použiji VM Extension v podobně Linux Custom Script. Ten na nodu nainstaluje dotnet SDK, stáhne aplikační kód, rozbalí a zajistí jeho spuštění přes systemd. Skript i kód mám uložen veřejně na GitHub, v praxi bychom asi použili storage account s klíčem pro bezpečný přístup. Skriptu jako argument předám login údaje pro svůj SQL, aby ho aplikace mohla využít. Poznámka - používám Linux Bash. Pokud spouštíte z PowerShell konzole ve Windows musíte " znaky nahradit za \".

```bash
az vmss extension set --vmss-name webscaleset \
    --name CustomScript \
    -g web-rg \
    --version 2.0 \
    --publisher Microsoft.Azure.Extensions \
    --protected-settings '{"commandToExecute": "bash installapp-v1.sh mujsqlsrv987.database.windows.net tomas Azure12345678"}' \
    --settings '{"fileUris": ["https://raw.githubusercontent.com/azurecz/azuretechacademy-hybridit-labs-day2/master/scripts/installapp-v1.sh"]}'
```

Tímto jsme updatovali model VMSS, ale protože máme upgrade politiku na Manual, nezměnilo se nic na VM. Proveďme teď manuálně upgrade rovnou na všech instancích.

![](/images/2019/2019-07-03-08-38-32.png){:class="img-fluid"}

![](/images/2019/2019-07-03-08-41-56.png){:class="img-fluid"}

Až upgrade proběhne, připojme se na public IP balanceru a najdeme tam jednoduchou TODO aplikaci a můžeme přidat nějaký záznam, který se zaperzistuje v Azure SQL.

![](/images/2019/2019-07-03-08-42-53.png){:class="img-fluid"}

V aplikaci je také připraven endpoint /api/version, který vrátí verze 1 a také ukáže, z kterého nodu odpověď přišla. Nepoužívejme z browseru, protože ten si drží session (a neuvidíme tak balancing). Pokud jedete z PowerShell (Invoke-WebRequest nebo Invoke-RestMethod) použijte přepínač -DisableKeepAlive. Linux curl by default žádnou session nedrží, takže uvidíme odpovědi od obou instancí.

```bash
curl http://40.115.17.173/api/version
Version 1 from websc345c000002

curl http://40.115.17.173/api/version
Version 1 from websc345c000003
```

Výborně. Pojďme teď aktualizovat VMSS model tím, že změníme extension tak, že bude instalovat novou verzi aplikace (ale image OS zůstane stejný).

```bash
az vmss extension set --vmss-name webscaleset \
    --name CustomScript \
    -g web-rg \
    --version 2.0 \
    --publisher Microsoft.Azure.Extensions \
    --protected-settings '{"commandToExecute": "bash installapp-v2.sh mujsqlsrv987.database.windows.net tomas Azure12345678"}' \
    --settings '{"fileUris": ["https://raw.githubusercontent.com/azurecz/azuretechacademy-hybridit-labs-day2/master/scripts/installapp-v2.sh"]}'
```

Tentokrát si vyzkoušíme upgrade instancí jednu po druhé. Aktualizujte jen jednu.

![](/images/2019/2019-07-03-08-45-18.png){:class="img-fluid"}

![](/images/2019/2019-07-03-08-46-24.png){:class="img-fluid"}

Aplikace nám stále jede, nicméně podívejme se na její verzi.

```bash
curl http://40.115.17.173/api/version
Version 2 from websc345c000002

curl http://40.115.17.173/api/version
Version 1 from websc345c000003
```

Pojďme teď updatovat VMSS model tak, že použijeme novější verzi image. Očekáváme tedy, že při upgradu VMSS staré VM zahodí, naběhne nové z nových image a spustí extension. Pokud bychom to chtěli bezvýpadkově, provedeme rolling upgrade nebo budeme ručně updatovat jednu po druhé. Pro zjednodušení to udělám s výpadkem a rovnou provedu upgrade všech instancí.

```bash
az vmss update -n webscaleset \
    -g web-rg \
    --set virtualMachineProfile.storageProfile.imageReference.version=18.04.201906271

az vmss update-instances --instance-ids '*' \
    -n webscaleset \
    -g web-rg
```

Po chvilce budeme mít aplikaci na novějším image.

Pojďme teď zvýšit výkon clusteru a přeškálovat na 3 instance.

![](/images/2019/2019-07-03-08-55-25.png){:class="img-fluid"}

![](/images/2019/2019-07-03-09-03-14.png){:class="img-fluid"}

Běžíme na třech instancích, ale zátěž aplikace je malá. Nastavme automatické škálování tak, že minimum bude 2 (z důvodu redundance). 

![](/images/2019/2019-07-03-08-58-03.png){:class="img-fluid"}

Přidáme škálovací pravidlo podle metriky CPU. Bude to metrika přímo VM, ale můžeme použít i jiný resource jako je Service Bus fronta.

![](/images/2019/2019-07-03-09-04-02.png){:class="img-fluid"}

![](/images/2019/2019-07-03-09-04-27.png){:class="img-fluid"}

Pokud je zátěž malá odeberu node.

![](/images/2019/2019-07-03-09-06-43.png){:class="img-fluid"}

Pokud moc velká, node přidám. Nastavím a uložím.

![](/images/2019/2019-07-03-09-07-14.png){:class="img-fluid"}

Teď nezbývá, než 5 minut čekat. Po této době uvidím příslušnou událost a jedeme na 2 strojích.

![](/images/2019/2019-07-03-09-13-56.png){:class="img-fluid"}

![](/images/2019/2019-07-03-09-14-09.png){:class="img-fluid"}

Virtual Machine Scale Set vám umožní pracovat s plnohodnotným VM se vším všudy bez omezení danými kontejnery nebo PaaS řešením. To je důvod, proč VMSS volí provideři síťových řešení v Azure nebo proč jej využívají platformní služby. Pokud máte podobné potřeby, vyzkoušejte si to.



