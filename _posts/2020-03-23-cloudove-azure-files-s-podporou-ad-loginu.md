---
layout: post
published: true
title: Cloudové Azure Files s podporou AD loginů
tags:
- Storage
---
Je velké množství způsobů jak v Azure cloudu ukládat data v okamžiku, kdy je potřebujete mít jako soubory. Je to například:
- Azure Blob Storage s FUSE driverem do Linuxu (vypadá pak jako share)
- Azure Blob Storage s hierarchickým namespace (HDFS)
- Azure Files jako SMB share
- Azure NetApp Files
- Připravuje se NFSv3 pro Azure Storage
- A dále nepřeberné množství IaaS variant
- V neposlední řadě jsou tu varianty pro koncové uživatele - OneDrive, Teams, Sharepoint apod.

Máte v Azure Windows VM jen proto, že na ní běží file share? To znamená musíte se o ni starat, patchovat, řešit infrastrukturu, přidávat disky když je potřeba kapacita, vymyslet redundanci a tak podobně. Platformní řešení je určitě o dost příjemnější. Jenže řada klasicky postavených řešení zkrátka potřebuje SMB file systém včetně ACL a dalších vlastností, které v Azure Files zatím přímo nebyly.

Jistým řešením je používat Azure Files Sync. Ten instalujete na normálním Windows Server a přes něj se připojují uživatelé (může běžet v cloudu i mimo něj), ten ale dokáže tierovat kapacitu do Azure Files a v nich si poznamenat ACL. Takže dokud přistupujete výhradně přes servery (může jich být víc), je ACL dodrženo a Azure Files jsou vlastně jen backend umožňující spolehlivé uložení dat včetně zónové či regionální redundance či Azure Backup pro zálohy. To je výborná věc pro lokální storage (cache) na pobočkách, ale přecijen by bylo skvělé mít Azure Files tak, aby uměly ACL napřímo a hotovo zejména pro věci odehrávající se uvnitř samotného cloudu (zpracování).

# Azure Files a AD přihlašování
Azure Files se standardně chovají tak, že se k nim přihlašujete bez konkrétní uživatelské identity (například klíčem). To je fajn pro aplikace, ale ne ideální pokud k souborům přistupují uživatelé nebo pokud do storage kouká víc aplikací a ACL je mechanismus díky kterému se nepomlátí. Samozřejmě hned bych namítl, že pro uživatele v cloudu jsou vhodnější technologie typu OneDrive nebo Teams a pro aplikace použití Blob storage s autentizací a autorizací přes AAD aplikační registraci ... ale to mluvíme o novějším světě. V enterprise je obrovské množství aplikací i uživatelů, kde je po nějakou dobu nutné řešit to klasičtěji.

Před časem se pro Azure Files objevila možnost přihlašování přes identity a to nejprve s využitím Azure Active Directory Domain Services služby. AAD DS je v podstatě AD server spravovaný Microsoftem, který vycucává identity z AAD a nabízí je ve vašem VNETu přes starší protokoly jako je Kerberos. Tato funkce Azure Files je už plně GA, nicméně použití AAD DS má určitá omezení (napříkad není dostupná pro federační scénář bez synchronizace hash). Relitivně nově je v preview možnost joinu do customer-managed AD serveru včetně toho v on-premises (samozřejmě za předpokladu, že je synchronizovaný do AAD). V zásadě tedy Azure Files potřebují AAD a k němu klasické AD s ním synchronizované a to buď to vaše vlastní (zdrojové, třeba v on-premises) nebo platformní (AAD DS).

# Situace bez AD integrace
Nejprve se podívejme, jak to vypadá v klasickém režimu, kdy integrace není nastavena. Vytvořil jsem storage account a share a získávám skript jak ho namapovat jako disk na svůj Windows server v AD doméně.

![](/images/2020/2020-03-19-07-20-12.png){:class="img-fluid"}

Všechno funguje, můžu pracovat se soubory, ale když se pokusím spravovat práva souborového systému a řídit v něm přístupy, dostanu chybovou hlášku. 

![](/images/2020/2020-03-19-07-23-08.png){:class="img-fluid"}

# Join Azure Files do domény
Přestože AAD DS integrace je v GA a dostupná prakticky ve všech regionech, preview integrace do klasického AD ještě není všude a chybí ve West Europe - použil jsem tedy region France Central.

V rámci rozchození integrace potřebujeme začlenit Azure Files do domény a také nakonfigurovat patřičným způsobem storage account. To pro nás uděla PowerShell modul, který budeme spouštět v nějakém Windows serveru, který je začleněn do domény a pod účtem, který má jednak právo udělat join a jednak je v Azure povolen jako Contributor pro náš storage account (bude tam muset něco ponastavovat). Ještě si můžete vybrat zda se má registrace v AD udělat jako servisní účet nebo computer account (já zvolil účet počítače).


```powershell
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Currentuser
Invoke-WebRequest `
    -Uri https://github.com/Azure-Samples/azure-files-samples/releases/download/v0.1.1/AzFilesHybrid.zip `
    -Outfile AzFilesHybrid.zip
Expand-Archive AzFilesHybrid.zip -DestinationPath .
.\CopyToPSPath.ps1 

Import-Module -name AzFilesHybrid
Connect-AzAccount

Select-AzSubscription -SubscriptionId "<your-subscription-id-here>"

join-AzStorageAccountForAuth -ResourceGroupName "<resource-group-name-here>" `
    -Name "<storage-account-name-here>" `
    -DomainAccountType "<ServiceLogonAccount|ComputerAccount>" `
    -OrganizationalUnitName "<ou-name-here>"
```

Dále potřebujeme uživatelům, kteří mají mít možnost s share pracovat toto právo udělit i na úrvni RBAC v Azure. Nepotřebujeme je pouštět do Azure samotného (tedy do control plane), nepotřebují vidět storage account, ale zařadíme je jako roli na data plane. Jde o Storage File Data SMB Share následovaný buď Reader (čtení souborů), Contributor (čtení, zápis, delete), Elevated Contributor (nastavování NTFS permissions).

Udělal jsem to takhle:

![](/images/2020/2020-03-19-13-01-55.png){:class="img-fluid"}

Přihlásil jsem se do Windows VM jako user1 a otevřel ```\\mojefiles.file.core.windows.net\mujshare```. Hned naběhlo okno bez přihlášení - SSO zafungovalo. Vytvořím dva soubory a u soubor1.txt odstřihnu všechny přístupy kromě user1.

![](/images/2020/2020-03-19-13-15-29.png){:class="img-fluid"}

Přihlásím se jako user2 a do soubor1.txt se nedostanu.

![](/images/2020/2020-03-19-13-17-30.png){:class="img-fluid"}

Do soubor2.txt ano.

![](/images/2020/2020-03-19-13-18-00.png){:class="img-fluid"}

Nicméně právo modifikovat ACL nemám - nejsem totiž Elevated Contributor.


Výborně! Pozor ale na jednu věc - tohle všechno platí pro klasický přístup přes SMB. Pokud dáte uživateli právo na storage account (control plane), bude schopen user2 stáhnout i soubor1.txt přes Azure portál. Enforcement ACL platí tedy pro standardní Windows metodu přístupu, ne připojení přes storage API v Azure (NTFS o něm nic neví a není ve hře). Ale jak jsem psal - user2 nemusí mít vůbec žádný přístup do Azure a tento zdroj mu z pohledu resources vůbec nedáme, přistupuje jen přes SMB.

Jsem zastáncem použití Blob Storage a aplikační registrace v AAD pro řešení souborů v aplikacích a SaaS prostředků typu Teams nebo OneDrive pro spolupráci nad soubory z pohledu uživatelů. Nicméně klasický sharing je velmi rozšířený systém a má v sobě mnoho užitečných vlastností, které jsou administrátory firem dobře zvládnuté, takže dává smysl ho naplno využívat i v cloudu. Místo vytváření serverů a starání se o ně doporučuji využít PaaS - Azure Files. A pokud přemýšlíte jak postavit most mezi on-premises prostředím poboček a hostingu a Azure cloudem, přidejte si službu Azure Files Sync.
