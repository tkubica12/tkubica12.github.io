---
layout: post
title: 'Odlehčený jump server jako služba s Azure Bastion'
tags:
- Compute
- Monitoring
---
Pro produkční prostředí jsem zastáncem jump serverů pro zvýšení bezpečnosti správy serverů přes RDP a SSH. Dnes bych chtěl říct proč, jak se dá něco takového implementovat v Azure a vyzkoušel jednu z možností - Azure Bastion, odlehčený jump box jako služba.

# Koncept serverů bez managementu
Ještě než se pustím do jump serverů, tak bych chtěl doporučit aspirovat na servery, které žádný přímý management nemají. Když se podíváme na svět kontejnerů, tak ty něco takového do značné míry splňují. Do kontejneru nedáváte SSH nebo RDP přístup. Aplikace včetně všech dependencies zabalíte do kontejnerového obrazu a pokud potřebujete implementovat nějakou změnu, vytvoříte nový image, kterým ten původní nahradíte. Něco takového se dá dělat i s VM typicky s využitím Virtual Machine Scale Set a to buď z golden obrazů s využitím Shared Image Gallery nebo přes dotažení obsahu s VM Extensions a vytvořit tak immutable infrastrukturu (Phoenix servery). V takových případech pak pro běžnou práci přímý přístup nebudete používat. V případě, že chcete jet klasičtějším modelem mutable VM, tedy že do ní potřebujete přistupovat a měnit ji za chodu, můžete veškerá změnová řízení řešit přes desired state configuration management nástroj jako je Ansible, Chef, Puppet nebo PowerShell DSC. Jinak řečeno všechny změny budou automatizované a nasazované přes CI/CD pipeline z Azure DevOps, takže opět nebudete dávat přímý přístup pro administrátora - změny se dělají jen z Azure DevOps.

Nicméně tento přístup rozhodně není pro každého ani pro starší aplikace. Přistupovat do serveru tedy v praxi budeme často potřebovat. Jak to udělat bezpečně?

# Koncept privilegované pracovní stanice aka jump server
Pustit notebook vývojáře přímo do VM přes SSH nebo RDP je poměrně riskantní. Notebook nemusíte mít úplně pod kontrolou. Říkáte si, že schováte SSH/RDP za VPNku a je to. Jenže co když je na notebooku nějaká nepěknost, která pak využije VPN spojení pro dělání něčeho špatného, třeba zkusí louskat hesla? A co když právoplatný uživatel z neznalosti nebo schválně stáhne ze serveru citlivá data a protože jsou velká, dá je na ulozto.cz? A co když se útočník nějak zmocní jednoho ze serverů a má tak přímou komunikační linku do dalších?

Koncept privilegované stanice je o tom, že SSH/RDP bude možné pouze z jedné stanice třeba v cloudu, která bude pod přísnou kontrolou (audit, logování, zákaz odložení dat někam jinam). Uživatel se nemůže připojit přímo, ale skočí nejprve do této stanice a teprve odtud do serveru. Ano - je to docela nepohodlné, takže pro vývojové prostředí, kde nejsou ostrá data, je to možná neúměrná komplikace, která zpomaluje vývoj. Ale na produkci bychom měli upřednostňovat bezpečnost před pohodlím - na hraní přece máme Dev.

V zásadě mne tedy napadají 4 způsoby jak to řešit:
- Pořídíte si profesionální privileged workstation řešení. Tato mají velmi přísná omezení, dokážou z RDP session nahrávat video pro auditní účely a přichází s různými certifikacemi. Velmi bezpečné, ale relativně drahé.
- Postavíte si takový systém sami s využitím například Windows nebo jiného plnohodnotného OS. Sami si nadefinujete potřebné politiky třeba přes GPO v doméně, nainstalujete software podle potřeb vašich vývojářů (například Azure Data Studio), zakážete Internet (aby nešlo poslat data na ulozto.cz) a tak podobně. Před server bych doporučoval dát bránu, která místo přímého RDP spoje na jump vytvoří spojení přes HTML5 a umožní ověřování přes AAD včetně vícefaktorového ověřování, Identity Protection a Conditional Access (což je u přímého RDP do jumpu problém). To máte k dispozici jako službu díky Windows Virtual Desktop, na který se podíváme někdy příště.
- Nasadíte si odlehčené open source řešení pro přístup přes HTML5. Mám rád Apache Guacamole, které se umí integrovat na AAD a nahrávat videa, které ukládá do Azure Blob Storage.
- Pokud nejste nároční, chcete něco levného, rychlého a bez práce, použijte Azure Bastion - a to je téma dnešního článku

# Azure Bastion
Bastion umožňuje přístup k VM přes Internet, ale bezpečněji, než přímé vystavení SSH/RDP do světa, které nedoporučuji. Bastion je plně spravovaný jump server, na který se ověřujete přes AAD včetně vícefaktorového ověření přímo z vaší session v Azure Portal. Je to tedy velmi jednoduché, nepotřebujete VPN a dobré pro rychlou správu serverů bez čekání na sítě a jiné složitosti.

Nejprve vytvořím VNET a v něm jedno Windows a jedno Linux VM bez public IP. Také si připravím AzureBastionSubnet a na vm-subnet udělám NSG, které povoluje RDP/SSH přístup jen z AzureBastionSubnetu.

```bash
# Create Resource Group
az group create -n bastion-test-rg -l westeurope

# Create networks
az network vnet create -n myvnet -g bastion-test-rg --address-prefix "10.0.0.0/16"
az network vnet subnet create -n vm-subnet \
    --vnet-name myvnet \
    -g bastion-test-rg \
    --address-prefixes "10.0.0.0/24"
az network vnet subnet create -n AzureBastionSubnet  \
    --vnet-name myvnet \
    -g bastion-test-rg \
    --address-prefixes "10.0.1.0/24"

# Create vm-subnet NSG
az network nsg create -g bastion-test-rg -n vm-nsg
az network nsg rule create -g bastion-test-rg \
    --nsg-name vm-nsg \
    -n allowManagementFromBastion \
    --priority 100 \
    --source-address-prefixes "10.0.1.0/24" \
    --source-port-ranges '*' \
    --destination-address-prefixes '*' \
    --destination-port-ranges 3389 22 \
    --access Allow \
    --protocol Tcp \
    --description "Allow RDP and SSH from Bastion only"
az network nsg rule create -g bastion-test-rg \
    --nsg-name vm-nsg \
    -n denyManagement \
    --priority 110 \
    --source-address-prefixes '*' \
    --source-port-ranges '*' \
    --destination-address-prefixes '*' \
    --destination-port-ranges 3389 22 \
    --access Deny \
    --protocol Tcp \
    --description "Deny all other management traffic"

# Create AzureBastionSubnet NSG
az network nsg create -g bastion-test-rg -n bastion-nsg
az network nsg rule create -g bastion-test-rg \
    --nsg-name bastion-nsg \
    -n allowHttpsFromInternet \
    --priority 100 \
    --source-address-prefixes '*' \
    --source-port-ranges '*' \
    --destination-address-prefixes '*' \
    --destination-port-ranges 443 \
    --access Allow \
    --protocol Tcp \
    --description "Allow HTTPS to Bastion from Internet"
az network nsg rule create -g bastion-test-rg \
    --nsg-name bastion-nsg \
    -n allowBastionManagement \
    --priority 110 \
    --source-address-prefixes GatewayManager \
    --source-port-ranges '*' \
    --destination-address-prefixes '*' \
    --destination-port-ranges '*' \
    --access Allow \
    --protocol Tcp \
    --description "Allow Bastion management"
az network nsg rule create -g bastion-test-rg \
    --nsg-name bastion-nsg \
    -n allowBastionManagement \
    --priority 100 \
    --source-address-prefixes '*' \
    --source-port-ranges '*' \
    --destination-address-prefixes AzureCloud \
    --destination-port-ranges '*' \
    --access Allow \
    --protocol Tcp \
    --direction Outbound \
    --description "Allow outbound to Azure management"
az network nsg rule create -g bastion-test-rg \
    --nsg-name bastion-nsg \
    -n allowManagementInVnet \
    --priority 110 \
    --source-address-prefixes '*' \
    --source-port-ranges '*' \
    --destination-address-prefixes VirtualNetwork \
    --destination-port-ranges 3389 22 \
    --access Allow \
    --protocol Tcp \
    --direction Outbound \
    --description "Allow management within VNET"
az network nsg rule create -g bastion-test-rg \
    --nsg-name bastion-nsg \
    -n denyInternetOutbound \
    --priority 120 \
    --source-address-prefixes '*' \
    --source-port-ranges '*' \
    --destination-address-prefixes Internet \
    --destination-port-ranges '*' \
    --access Deny \
    --protocol Tcp \
    --direction Outbound \
    --description "Deny outbound Internet"

# Apply NSGs on subnets
az network vnet subnet update -n vm-subnet  \
    --vnet-name myvnet \
    -g bastion-test-rg \
    --network-security-group vm-nsg
az network vnet subnet update -n AzureBastionSubnet  \
    --vnet-name myvnet \
    -g bastion-test-rg \
    --network-security-group bastion-nsg

# Create Windows VM
az vm create -n win-vm \
    -g bastion-test-rg \
    --public-ip-address "" \
    --image Win2019Datacenter \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --nsg "" \
    --public-ip-address "" \
    --vnet-name myvnet \
    --subnet vm-subnet

# Create Linux VM
az vm create -n linux-vm \
    -g bastion-test-rg \
    --public-ip-address "" \
    --image UbuntuLTS \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --nsg "" \
    --public-ip-address "" \
    --vnet-name myvnet \
    --subnet vm-subnet
```

Pojďme teď do portálu. Vyberu si jednu z VM a kliknu na službu Bastion a vytvořím ji v připraveném subnetu.

![](/images/2019/2019-10-16-10-50-51.png){:class="img-fluid"}

Připojíme se z portálu přes Azure Bastion. Dostaneme se tam, ověřeni jsme bezpečně a přitom VM nemá public IP ani nedovoluje RDP komunikaci odjinud, než z Azure Bastion subnetu.

![](/images/2019/2019-10-16-10-57-29.png){:class="img-fluid"}

A jsme tam - přes prohlížeč.

![](/images/2019/2019-10-16-10-58-53.png){:class="img-fluid"}

Totéž funguje i pro náš Linux server.

![](/images/2019/2019-10-16-10-59-31.png){:class="img-fluid"}

![](/images/2019/2019-10-16-11-00-16.png){:class="img-fluid"}

Pokud hledáte rychlé a jednoduché řešení, jak se odkudkoli dostat bezpečně do VM v Azure, vyzkoušejte Azure Bastion. Nepotřebujete dávat VM public adresu, nepotřebujete být na VPNce, nepotřebujete se starat o jump server. Možná pro produkci půjdete do sofistikovanějšího řešení, ale ve vývoji či přípravě protypů je to neuvěřitelně pohodlné a můžete rychle začít (v některých firmách může nějakou dobu trvat, než se udělá VPNka, prostupy, dají vám přístup). Zkuste si to. Kombinace Azure Cloud Shell (tlačítko nahoře v portálu nebo shell.azure.com) pro "jump" na ovládání Azure z CLI/PowerShell a Bastion pro jump do VM je mocná kombinace, jak přes HTTPS vyřešit všechno.
