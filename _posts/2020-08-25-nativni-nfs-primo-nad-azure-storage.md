---
layout: post
published: true
title: Nativní NFS přímo nad Azure Storage
tags:
- Storage
---
Pokud vaše aplikace potřebují sdílený share, určitě ho nebudete budovat sami - využijete platformní službu. Do preview teď přichází nová varianta s NFS a to bez nutnosti použít gateway nebo nějakou jinou konverzi. Pojďme vyzkoušet.

# Sdílený share v Azure
První dlouhá léta dostupnou a výbornou variantou jsou Azure Files postavené na SMB/CIFS. Je to plně POSIX implementace, podporuje i ACL s navázáním na vaše Active Directory, umí se synchronizovat s on-prem share přes Azure Files Sync a jsou pro ni drivery pro namapování jako Volume v Azure Kubernetes Service, Azure Container Instances nebo ve WebApp pro Linux. Díky variantě Premium se dá dostat i k řešení s SSD a použít pro náročné věci. Proč tedy vůbec přemýšlet o něčem jiném? Napadají mě tři důvody:
- Azure Files jsou cenově náročnější, než Blob Storage a to je ještě násobeno tím, že Blob Storage má kromě už tak levnějšího tieru Hot k dispozici i Cool a Archive, takže na uchování velkého množství málo přistupovaných dat mohou být Azure Files drahé.
- SMB/CIFS je v pohodě, ale některé starší systémy s tím třeba mají problém - NFS je zejména ve světě Linuxu přeci jen používanější varianta.
- Možná potřebujete přímé napojení na tyto data z analytických nástrojů jako je Azure Synapse nebo Azure Databricks a SMB není optimalizované pro takový způsob paralelizovaných přístupů.

Pro data lake, tedy ukládání dat pro potřeby dávkové analýzy, řešení existuje už dnes. Je to Azure Blob Storage se zapnutým hierarchickým režimem. To vám umožňuje využít úžasnou ekonomiku blobů a při tom mít hierarchii, řídit přístupy k souborům a přímo se napojovat přes HDFS z analytických nástrojů optimalizovaným způsobem. To si tedy můžeme odškrtnout jako "hotovo, jdeme dál".

Co když tedy potřebuji nutně NFS, například mám databázový systém a ten nepodporuje CIFS jako úložiště. Pro tyto účely doporučuji Azure NetApp Files. Výborná služba tam, kde potřebujete robustní výkon. Je finančně náročnější než blob a také je tam nějaká minimální kapacita k objednání (4TB), ale řešení je to výborné. Navíc v private preview se mluví i o NFSv4 pro Azure Files (tedy stavová POSIX compliant immplementace), ale to je asi ještě daleko.

Ale co ta situace, kdy vaše aplikace neumí Blob API, potřebujete share, ale současně jde o data, kde hledáte ekonomiku blobů. Nejde vám o pokročilé POSIX vlastnosti nebo granulární řízení přístupů (bohatě vám postačí NFSv3) - jen zkrátka chcete blob jako share. To uděláte buď implementací nějaké brány (kousku software, co se k vám tváří jako NFS a na backendu si to píše do blobu) nebo na stroji implementujete open source FUSE pro Blob (souborový systém v user space s blob jako backend). Oboje je ale takové samo domo a musíte se o to starat. Azure nabídne NFS jako nativní vlastnost blobu - žádná gateway, přímo ekonomika blobů co do uložení, jen (pravděpodobně - cena není ještě stanovena a odhaduji) dražší transakce. 

# Vyzkoušejme si NFS v Azure Blob Storage
Preview je zatím jen v Premium tier (standardní bude později) v pár regionech US, Kanadě a North Europe. Zatím nepodporuje autentizaci přes AAD, POSIX ACL, současný přístup přes NFS i běžné API, zamykání souborů a tak podobně - ale pracuje se na tom (některé body může Blob v budoucnu splnit, ale plnou POSIX compliance, aby to byl file system se vším všudy bych nečekal - proto se dělá i na NFSv4 pro Azure Files). 

Nejprve si musíme registrovat tuto feature. Jakmile vám začne psát Registered, přeregistrujte si storage resource providera.

```bash
az feature register --namespace Microsoft.Storage -n AllowNFSV3 
az feature register --namespace Microsoft.Storage -n PremiumHns  

az feature show --namespace Microsoft.Storage -n AllowNFSV3 --query properties.state
az feature show --namespace Microsoft.Storage -n PremiumHns --query properties.state

az provider register -n Microsoft.Storage
```

Připravím si VNET a testovací VMko.

```bash
az group create -n nfs-storage-rg -l eastus
az network vnet create -n my-vnet -g nfs-storage-rg --address-prefix 10.0.0.0/16
az network vnet subnet create -n sub1 --vnet-name my-vnet -g nfs-storage-rg --address-prefixes "10.0.0.0/21"
az vm create -n mojevm \
    -g nfs-storage-rg \
    --image UbuntuLTS \
    --size Standard_B1s \
    --authentication-type password \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --vnet-name my-vnet \
    --subnet sub1
```

Vytvořme si storage account v podporovaném regionu a podporovaného typu.

![](/images/2020/2020-07-28-19-45-07.png){:class="img-fluid"}

Protože aktuální preview NFS nepodporuje autentizaci, vyžaduje průvodce abychom přístup zavřeli na konkrétní VNET.

![](/images/2020/2020-07-28-19-45-51.png){:class="img-fluid"}

Nutným předpokladem pro podporu NFS je zapnutý hierarchický file system a pak můžeme zaškrtnout NFS.

![](/images/2020/2020-07-28-19-46-43.png){:class="img-fluid"}

Na závěr vytvořme nějaký kontejner.

![](/images/2020/2020-07-28-19-51-14.png){:class="img-fluid"}

Připojím se do Linux VM, nainstaluji NFS klienta, namountuji si tento share a nakopíruju tam nějaké soubory.

```bash
ssh tomas@$(az network public-ip show -n mojevmPublicIP -g nfs-storage-rg --query ipAddress -o tsv)

sudo apt install nfs-common -y
sudo mkdir -p /mnt/nfs
sudo mount -o sec=sys,vers=3,nolock,proto=tcp mojesupernfs.blob.core.windows.net:/mojesupernfs/nfs1 /mnt/nfs
sudo cp -r /usr/share/doc /mnt/nfs
```

Skvělé - jsou tam (na storage firewallu jsem si dal přístup pro svou IP, abych se mohl podívat zvenku).

![](/images/2020/2020-07-28-20-06-58.png){:class="img-fluid"}

Na tuhle funkci se moc těším. Pro nové aplikace doporučuji napojit se přímo na Blob API a pro ty stávající použít Azure Files jako SMB/CIFS share. Jsou ale okamžiky, kdy těch dat je opravdu velikánské množství a potřebuji ekonomiku a tierovací vlastnosti Blobů a přitom nechci měnit aplikace. Pak musím buď nějak složitě konvertovat nebo kopírovat na pozadí mezi Files a Blob nebo pokud běžím v Kubernetes použít nový CSI driver pro bloby. Přímá podpora NFS je jednoduché a příjemné řešení. Vyzkoušejte si.
