---
layout: post
published: true
title: Image katalog pro vaše VM v Azure
tags:
- Compute
---
Vytvořit si vlastní image pro VM v Azure je jednoduché, ale jak si v tom udělat pořádek a distribuovat diskové obrazy do všech vašich regionů a sdílet je v rámci celého tenantu nebo dokonce i mimo něj? Na to se dnes podíváme s Shared Image Gallery v Azure.

# Managed Image
Postup vytvoření custom image z výchozího obrazu v Azure je například tento: 
1. Vytvoříte si VM s požadovaným OS
2. Nainstalujete co potřebujete
3. Provedete generalizaci OS (sysprep ve Windows a waagent v Linuxu), tedy odmazání user-specific věcí, unikátních identifikátorů, zkrátka přípravu na to, že při vytváření VM z tohoto obrazu se nově vytvoří uživatelský prostor (dle zadání v průvodci), vygeneruje nové ID stroje a tak podobně.
4. Vypněte a v GUI klikněte na Capture

V mém případě tohle už mám připraveno, ale je tu pár potíží:
* Jak efektivně nasdílet můj image do jiné subskripce? Nebo dokonce do jiného tenantu?
* Jak efektivně distribuovat tento image do dalších regionů, které používám?
* Jak se v tom vyznat, například seskupovat různé image podle nějakých kritérií?
* Jak image verzovat, přidávat nové varianty, ale moci zachovávat předchozí?

# Shared Image Gallery
Řešením zmíněných nedostatků je Shared Image Galery. Ta umožňuje sdílení napříč subskripcemi (a dokonce je možné nasdílet přes tenanty díky RBAC nebo přes kompletní sdílení do celého jiného tenantu aplikační registrací), seskupování, verzování a klonování do dalších regionů.

Vytvoříme novou galerii.

![](/images/2019/2019-05-12-17-09-41.png){:class="img-fluid"}

![](/images/2019/2019-05-12-17-11-02.png){:class="img-fluid"}

Přidejme novou definici.

![](/images/2019/2019-05-12-17-12-06.png){:class="img-fluid"}

![](/images/2019/2019-05-12-17-13-02.png){:class="img-fluid"}

Stejně jako u public Azure obrazů je součástí identifikace image jeho publisher, offer a SKU. Zvolme si jako publisher corpLinuxTeam, tedy Linuxáři v mé IT organizaci. Offer je nginx a SKU jeho konkrétní varianta, například nginx na Ubuntu 16.04 a k tomu můžeme nabízet třeba nginx na RHEL jako další SKU. Vedle toho bude corpLinuxTeam nabízet třeba offer Apache2, Tomacat apod. corpWindowsTeam se bude soustředit na přípravu Windows obrazů s předinstalovaným korporátním software pro zabezpečení a monitoring.

![](/images/2019/2019-05-12-17-16-09.png){:class="img-fluid"}

Pro svůj obraz definuji řetězec verze, v mém případě řekněme 1.0.0. Vybírám si hlavní region a zdrojový obraz (jde o můj Managed Image, který jsem si připravil dříve). U každého obrazu je kromě jeho verze také k dispozici tag latest. Pokud uživatel při vybírání image neuvede přesnou verzi, použije se latest. Takhle se chovají i public image, takže pokud zakládáte svůj Ubuntu, RHEL nebo Windows stroj jen v GUI, vyberete si třeba Windows Server 2019 a dostáváte latest (Microsoft asi tak jednou měsíčně přidává nové verze obrazů, které už obsahují poslední patche). Pokud z nějakého důvodu nechcete tento obraz dát do latest tagu, můžete ho vyjmout (například pracujete na nové generaci image 2.x.x, ale ještě není zralá pro nezkušené uživatale, kterým chcete pod latest dávat nejnovější 1.x.x větev).

![](/images/2019/2019-05-12-17-21-15.png){:class="img-fluid"}

Další otázkou je replikace. By default mám jednu zónově redundantní repliku v primárním regionu, tedy v mém případě West Europe. Mohu v něm mít replik víc - to je pro případ, že image je v mé firmě extrémně oblíben a používá se pro sestavování výpočetních clusterů o stovkách VM najednou. Vícero uložení rozloží zátěž na storage a urychlý sestavování takového clusteru. Co bude pro mě ale důležitější je přidání repliky do dalších regionů, které používám - v mém případě North Europe.

![](/images/2019/2019-05-12-17-23-25.png){:class="img-fluid"}

K obrazu mohu přidat nějaké další popisky nebo odkazy.

![](/images/2019/2019-05-12-17-24-54.png){:class="img-fluid"}

Nakonec můžeme ještě indikovat nějaká doporučení pro náš image. Nic z toho nebude vynuceno, ale bude zobrazeno jako doporučení (a podle vaší interní politiky může vést třeba k odmítnutí interní podpory, pokud není následováno). Pokud máte image s náročnou žravou aplikací a víte, že pokud se pustí na 1-corové mašině s minimem paměti a HDD disku nebude to vůbec dobré, můžete tady doporučit nějaké rozumné konfigurace.

![](/images/2019/2019-05-12-17-26-49.png){:class="img-fluid"}

Všechno je připraveno, image je v katalogu.

![](/images/2019/2019-05-12-19-58-01.png){:class="img-fluid"}

Kdo bude mít k image přístup? Všimněte si, že na záložce celé galerie, ale i konkrétního image a dokonce specifické verze najdete obvyklý Access control (IAM). Tam můžete řídit kdo má možnost co použít. Pro jednoduchost bych na začátek rozhodně doporučoval přístupy řešit na úrovni celé galerie, ať se v tom neztratíte. Toto řešení funguje v rámci vašeho tenantu. Pokud potřebujete zpřístupnit obraz i do jiného tenantu (například aplikační firma dodávající software potřebuje nabídnout image pro specifické zákazníky privátně a ne běžnou public cestou v marketplace), tak i to je možné: [https://docs.microsoft.com/en-us/azure/virtual-machines/linux/share-images-across-tenants](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/share-images-across-tenants)

Přidal jsem další verzi image.

![](/images/2019/2019-05-12-20-07-51.png){:class="img-fluid"}

![](/images/2019/2019-05-12-20-08-17.png){:class="img-fluid"}

Jak vypadá vytváření VM když kliknu na Create VM? Dialog je stejný jako vždy.

![](/images/2019/2019-05-12-20-09-16.png){:class="img-fluid"}

Když se podívám jaké obrazy mám k dispozici, uvidím tři zdroje - marketplace, moje Managed Images a Shared Image Galery.

![](/images/2019/2019-05-12-20-10-23.png){:class="img-fluid"}

![](/images/2019/2019-05-12-20-10-51.png){:class="img-fluid"}

Výborně. A kolik to všechno vlastně stojí? Služba jako taková je zdarma, ale platíte za storage a přenosy dat. Stejně jako běžný Managed Image platíte jeho uložení, což je poplatek jako Snapshot u Managed Disk, tedy pokud bude uložen na HDD v ZRS režimu, platíte u něj 0,05 USD za GB a to pouze z použitého místa (skutečná velikost, ne provisionovaná). Druhý náklad je za odchozí data, pokud se rozhodnete image replikovat ještě do dalších regionů.

A co takhle pravidelné vytváření imagů nějak automatizovat? Dobrý nápad - příště se společně podíváme na Azure Image Builder.




