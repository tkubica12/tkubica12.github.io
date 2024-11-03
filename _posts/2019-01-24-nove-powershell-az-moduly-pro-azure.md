---
layout: post
status: publish
published: true
title: Nové PowerShell Az moduly pro ovládání Azure
tags:
- Automatizace
---
Máte rádi PowerShell pro ovládání Azure? Víte, že si ho můžete vzít do Windows, Linux i Mac? Používat ve Windows Subsystem for Linux nebo v Azure CloudShell? Máte pro správu jump server a nemůžete shodnout jak ho udělat, protože jeden chce Windows s PowerShell a druhý Linux s Azure CLI? Podívejte na novou generaci Azure modulů pro multi-platformní PowerShell Core 6.

Stávající AzureRM PowerShell moduly mají dependencies, které neumožňují je dobře portovat na jiné platformy, než Windows. Azure tým proto připravil přepracovanou verzi modulů s názvem Az, které kromě zkrácení příkazů přináší i přenositelnost na jiné platformy, protože podporují nejen klasický PowerShell 5, ale i multi-platformní PowerShell Core 6. Od této chvíle budou nové příkazy přinášeny už jen do těchto nových modulů, takže je ideální upgradovat.

# Instalace nového PowerShell Core 6
V rámci přechodu na Az moduly chci rovněž nasadit (ale nemusel bych) PowerShell Core - multiplatformní open source PowerShell, který běží jak v mém počítači s Windows 10, tak i v mém Linux Subsystem for Linux a také v Azure CloudShell. V době psaní článku je aktuální stabilní verze 6.1.1 a najdu ji na stránce s release na [GitHubu](https://github.com/PowerShell/PowerShell/releases). V případě Windows jednoduše stáhnu MSI balíček a nainstaluji. V Linuxu to pro Ubuntu 16.04 (na tom mi běží WSL ve Win10) uděláme takhle:

```bash
wget -q https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y powershell
```

Všimněte si, že ve Windows můžete mít klasický PowerShell 5 vedle nového PowerShell Core 6. Spouštíte jej jak v Linuxu tak ve Windows přes binárku pwsh.

![](/images/2018/2018-12-27-17-10-38.png){:class="img-fluid"}

![](/images/2018/2018-12-27-17-11-40.png){:class="img-fluid"}

A v Linuxu:

```bash
$ pwsh
PowerShell 6.1.1
Copyright (c) Microsoft Corporation. All rights reserved.

https://aka.ms/pscore6-docs
Type 'help' to get help.



PS /mnt/c/Users/tokubica/OneDrive - Microsoft/git>
```

# Instalace Az modulů

Pro starší AzureRM jsem si ponechal klasický PowerShell 5, takže nemusím nic odinstalovávat (ale pokud chcete dát Az "do pětky", musíte odebrat AzureRM) a můžu se tak vrhnout do instalace v PowerShell Core 6. Nechci instalovat jako admin, stačí mi pro aktuálního uživatele. Tohle udělám jak ve Windows, tak v Linuxu (repozitář je by default untrusted, tak jen odklepneme, že mu věříme).

```powershell
Install-Module -Name Az -AllowClobber -Scope CurrentUser
```

# Login, výběr subskripce a jedeme

Přihlásíme se do Azure (Login-AzAccount je alias na následující příkaz).

```powershell
Connect-AzAccount
```

Pokud máte víc subskripcí, vypište si je a nasměrujte se na tu, co chcete.

```powershell
Get-AzSubscription
Select-AzSubscription -SubscriptionName tokubica
```

Výborně. Můžeme si najít třeba seznam Resource Group.

```powershell
Get-AzResourceGroup
```

# Aliasy pro AzureRM

Určitě najdete spoustu blogů (včetně toho mého) a repozitářů s příklady a skripty pro AzureRM. Az moduly mají stejné přepínače a funkce, jen jiné hlavní jméno. Az proto umožňuje zapnout aliasy, takže jste schopni používat i starší názvy příkazů. Nicméně postupně začněte přecházet - nové commandy už na AzureRM nebudou. Tak například pokud se objeví nějaká nová služba v Azure, už dostane ovládání jen do Az (co se PowerShell týče ... jinak pro ARM, Azure CLI či SDK samozřejmě taky).

Například pokud si ve starém návodu najdeme tento příkaz na vypsání Resource Group, nebude fungovat.

```powershell
PS C:\Program Files\PowerShell\6> Get-AzureRmResourceGroup
Get-AzureRmResourceGroup : The term 'Get-AzureRmResourceGroup' is not recognized as the name of a cmdlet, function, script file, or operable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:1 char:1
+ Get-AzureRmResourceGroup
+ ~~~~~~~~~~~~~~~~~~~~~~~~
+ CategoryInfo          : ObjectNotFound: (Get-AzureRmResourceGroup:String) [], CommandNotFoundException
+ FullyQualifiedErrorId : CommandNotFoundException
```

Zapněme si aliasy a půjde to.

```powershell
Enable-AzureRmAlias
Get-AzureRmResourceGroup
```

Ťukání do GUI je skvělý začátek a dobrý způsob pro monitoring a zkoušení nových funkcí v Azure. Pro rutinní práci je ale rychlejší a opakovatelnější jít do jiných způsobů. Já preferuji desired state ARM šablony, ale to vyžaduje trochu víc práce a cviku. Skriptík je určitě výborný odrazový můstek z GUI do zrychlení častěji opakovaných úloh. 

A to nejlepší? Jestli máte rádi objektově orientovaný a samovysvětlující PowerShell nebo raději úžasnou rychlost, integrovatelnost a "nízkoznakovost" Azure CLI neříká vůbec nic o tom, kde to můžete použít! Oboje funguje ve Windows, Linux i Mac. Pro mne to znamená, že OS už není rozhodující pro určení stylu, s jakým chci s Azure pracovat. A to je myslím dobře.
