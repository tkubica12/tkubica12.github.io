---
layout: post
published: true
title: Automatické vytváření diskových obrazů s Azure Image Builder
tags:
- Compute
---
Ať už máte strategii vytváření korporátních předinstalovaných image z procesních důvodů nebo jen potřebujete rychle budovat masivní clustery a šetřit čas CPU, automatizace přípravy diskových obrazů může být to pravé pro vás. Podívejme se jak Azure Image Builder dokáže celý proces automatizovat. Je postavený na open source nástroji Packer z dílny Hashicorp, který můžete samozřejmě používat i napřímo, ale díky Azure Image Builder je všechno integrované přímo do Azure platformy a nemusíte nic instalovat ani řešit přihlašování. Podívejme se dnes na to.

# Proč automatizovat vytváření image
Možná jste velká enterprise firma a máte strategii, že všechny image VM ve vaší organizaci musí obsahovat nějaká základní nastavení a software. Například chcete poladit OS pro přísnější zabezpečení, doinstalovat si vlastní nástroje pro endpoint protection, antivir nebo monitoring. Můžete to udělat ručně - pustíte VM v Azure, nainstalujete co potřebujete a vytvoříte z toho image a ten nasdílíte třeba v Azure Shared Image Gallery. Ale co dál? Po půl roce si váš uživatel pustí image a bude hodinu stahovat chybějící aktualizace. A co když je nová verze antiviru? A nová verze endpoint protection? Chcete každý váš image dvakrát do měsíce budovat znovu? Možná by dávalo smysl tento proces automatizovat. Připravit si řekněme skript, který pustí základní image, nainstaluje co potřebujete v nejnovějších verzích a nastaveních a vyexportuje to jako diskový obraz. Přesně tohle pro vás může zajistit Azure Image Builder.

Existuje ještě druhý důvod. Jste borci na automatizaci a rozchodit co potřebujete ve své VM pro vás není problém - máte na to třeba skript a ten umíte přes Azure VM Extensions automatizovaně pustit po startu. To má ale tři potíže:
* Co když to zapomenete přidat? V enterprise světě to může znamenat nepodporovaný stav OS.
* Co když v okamžiku běhu skriptu selže místo, z kterého si stahujete package a instalujete software? V takovém okamžiku vám to nedoběhne a můžete být ve stavu, že něco se nainstalovalo a něco ne. Težko předvídat kdy se něco takového stane, protože často repozitáře, z kterých stahujete, nemáte plně pod kontrolou.
* A co když instalace všeho potřebného trvá docela dlouho? Dejme tomu, že instalace nějakého software pro výpočty zabere 20 minut. V okamžiku, kdy vytváříte výpočetní cluster s 500 core, tak to znamená 20 minut těchto core, kdy je nevyužíváte pro něco užitečného. To v případě tak velkého řešení znamená velké náklady navíc. A je tu ještě druhý efekt - co když máte Virtual Machine Scale Set a z důvodu velkého množství požadavků klientů jste se rozhodli rychle přidat další nody. Díky pomalé instalaci bude trvat dost dlouho, než vám VM začne být užitečná a do té doby vaši uživatelé trpí.

Mimochodem právě ten druhý důvod se týkal i jedné služby v Azure - Azure Kubernetes Service. Ta dříve pustila prázdné VM a v mich instalovala Kubernetes. To jednak přidalo 5-10 minut do času instalace a navíc, pokud repozitáře měly nějaký problém, instalace nemusela doběhnout. AKS tým proto přešel na přebuildované diskové obrazy, kde jsou věci nainstalované a AKS už je spíše dokonfigurovává, než instaluje. To zvýšilo rychlost vytváření clusteru, rychlost škálování a zvýšilo spolehlivost.

# Packer
Pokud potřebujete automatizovat vytváření image v různých prostředích a cloudech, vřele doporučuji nástroj Packer z dílny Hashicorp: [https://www.packer.io/](https://www.packer.io/)

Můžete vytvořit nejen automatizační skripty, ale použít i další techniky jako je Chef apod. Zdrojový image a "cloudový driver" umožňuje stejnou akci zopakovat jak v Azure, Azure Stacku, tak i v jiných cloudech nebo VMware. Jedním předpise v Packeru tak můžete připravit konzistentní diskové obrazy ve všech vašich prostředích.

# Azure Image Builder
Image Builder je integrované řešení v Azure, které má pod kapotou právě Packer. Díky této integraci nemusíte řešit na jaké mašině Packer pouštět nebo jak pro něj vytvářet servisní účty. Definici automatizace nahrajete do Azure přes ARM šablonu. Tato služba je zatím v preview, takže si musíme registrovat příslušného resource providera a ne všechno je ještě plně dostupné v příkazové řádce nebo portálu. Nicméně je to plně funkční, tak se podívejme jak na to.

Nejdřív si zaregistrujte funkci VirtualMachineTemplatePreview a ověřte, že ji máte ve stavu Registrered (u mě to trvalo tak 10 minut).

```bash
az feature register --namespace Microsoft.VirtualMachineImages --name VirtualMachineTemplatePreview
az feature show --namespace Microsoft.VirtualMachineImages --name VirtualMachineTemplatePreview | grep state
```

Když to proběhne, přeregistrujte si resource providera a ověřte, že je ve stavu Registered.

```bash
az provider register -n Microsoft.VirtualMachineImages
az provider show -n Microsoft.VirtualMachineImages | grep registrationState
```

Připravme si Resource Group, ve které budeme chtít provozovat Image Builder. Aby tento nástroj mohl udělat co potřebuje, musíme mu k tomu dát práva. Přiřadíme tedy "uživateli" Azure Virtual Machine Image Builder práva na úrovni Contributor do této Resource Group (můžete udělat i z GUI v záložce Access control).

```bash
az group create -n myimages -l eastus2
az role assignment create \
    --assignee cf32a0cc-373c-47c9-9156-0db11f6a6dfc \
    --role Contributor \
    --scope $(az group show -n myimages --query id -o tsv)
```

Prohlédněte si přiřazený účet.

![](/images/2019/2019-05-12-21-19-47.png){:class="img-fluid"}

Podívejme se teď na definici naší automatizace. Jde o ARM šablonu a v ní má Image Builder tři základní sekce.
* Source ukazuje na zdrojový image. Může to být prázdný obraz z Azure Marketplace, existující Managed Image nebo obraz z katalogu Shared Image Gallery (o tom jsem psal posledně).
* Customize sekce obsahuje vaše konfigurační skripty. V rámci preview je k dispozici Shell pro Linux, PowerShell pro Windows a Restart pro Windows (můžete tedy například pustit skript, otočit VM a ta až se znova vrátí do ní pustit další skript). Další varianty, které Packer má, zatím k dispozici nejsou.
* Distribute říká kam chcete výsledný image umístit a v jaké formě. Já pro jednoduchost použiji běžný Managed Image, ale v rámci organizace bude výhodnější poslat obraz rovnou do Shared image Gallery tak, jak jsem popisoval na tomto blogu nedávno.

V rámci preview je služba dostupná jen v některých regionech v US, zvolíme tedy eastus2.

```json
{
    "type": "Microsoft.VirtualMachineImages/imageTemplates",
    "apiVersion": "2019-05-01-preview",
    "location": "eastus2",
    "dependsOn": [],
    "properties": {
        "buildTimeoutInMinutes": 80,
        "source": {
            "type": "PlatformImage",
            "publisher": "Canonical",
            "offer": "UbuntuServer",
            "sku": "18.04-LTS",
            "version": "18.04.201903060"
        },
        "customize": [
            {
                "type": "Shell",
                "name": "Upgrade_and_add_banner",
                "inline": [
                    "sudo apt update",
                    "sudo apt upgrade -y",
                    "sudo apt install -y figlet",
                    "sudo figlet Azure | sudo tee /etc/motd"
                ]
            }
        ],
        "distribute": [
            {
                "type": "ManagedImage",
                "imageId": "/subscriptions/VASECISLOSUBSKRIPCE/resourceGroups/myimages/providers/Microsoft.Compute/images/mujimage",
                "location": "eastus2",
                "runOutputName": "tomasCustomImage123",
                "artifactTags": {
                    "source": "azVmImageBuilder",
                    "baseosimg": "ubuntu1804"
                }
            }
        ]
    }
}
```

Výborně - pošleme tento předpis do naší Resource Group.

```bash
az resource create \
    --resource-group myimages \
    --properties @imagebuilder.json \
    --is-full-object \
    --resource-type Microsoft.VirtualMachineImages/imageTemplates \
    -n imageAutomat
```

Tento typ zdroje zatím nemá svou vizualizaci v GUI, ale můžete ho najít jako běžný resource.

![](/images/2019/2019-05-13-16-34-01.png){:class="img-fluid"}

Teď můžeme automatizaci odstartovat.

```bash
az resource invoke-action \
     --resource-group myimages \
     --resource-type  Microsoft.VirtualMachineImages/imageTemplates \
     -n imageAutomat \
     --action Run 
```

Co se bude dít? Azure Image Builder vytvoří novou Resource Group a v ní VM s příslušným startovacím image. Hned jak naběhne, připojí se a provede požadované akce. Následně udělá generalizaci obrazu a vyexportuje ho jako image.

![](/images/2019/2019-05-13-16-34-51.png){:class="img-fluid"}

Průběh práce Packeru se loguje do storage accountu v této Resource Group.

![](/images/2019/2019-05-13-16-35-46.png){:class="img-fluid"}

Výsledkem našeho snažení je hotový diskový obraz.

![](/images/2019/2019-05-13-17-29-55.png){:class="img-fluid"}

Uchvátily vás možnosti kontejnerů, kdy přes Dockerfile automaticky připravíte Docker image, který se uloží do repozitáře a používá dle potřeby, ale vaše prostředí není na kontejnery připraveno? Podobný koncept lze nasadit i s VM díky kombinaci Azure Image Builder a Azure Shared Image Gallery. Vyzkoušejte si to.