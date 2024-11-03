---
layout: post
published: true
title: "Azure Defender (6): Ochrana serverové infrastruktury - sledování integrity systému"
tags:
- Security
---
Je fajn, když všechno zlé je odhaleno jako signatura nějakého malware nebo detekováním chování v rámci Azure Defender, ale váš systém může být ohrožen něčím naprosto cíleným, neznámým nebo třeba akcemi právoplatného správce.  Co s tím? Ručně dělat reverse engineering ponořeni v hexadecimálním editoru koukaje do assembly za současného sledování třeba Sysinternals Process Monitor pro zkoumání jaké kernelové volání se objevují je pro machry a já to neumím. Přesto bych rád, aby akce vedoucí k narušení integrity systému a provádění neočekávaných změn v kritických součástech souborového systému nebo registrech byly sledovány a dalo se zjišťovat co se změnilo, kdy a jak. Takové informace mi pomůžou zjistit, že se něco děje a získat detaily, informace použitelné pro nápravu situace, auditní stopu pro předání větším bezpečnostním expertům apod. Tohle pro mě Azure Defender udělá díky funkci File Integrity Monitoring.

Funkci File Integrity Monitoring jsem si zapnul.

[![](/images/2021/2021-01-08-08-28-41.png){:class="img-fluid"}](/images/2021/2021-01-08-08-28-41.png)

Ve výchozím nastavení sleduje Azure Defender změny v klíčových částech registrů a souborů ve Windows a Linux.

[![](/images/2021/2021-01-08-08-29-40.png){:class="img-fluid"}](/images/2021/2021-01-08-08-29-40.png)

[![](/images/2021/2021-01-08-08-29-56.png){:class="img-fluid"}](/images/2021/2021-01-08-08-29-56.png)

Začnu tím, že nastavím sběr obsahu souborů. Azure Defender monitoruje jejich integritu a obsah díky hash, ale pro forenzní účely nebo rekonstrukci co se dělo stojí za to si soubory nechat odkládat do Azure storage pokaždé, když bude zaznamenána jejich změna (nezapomeňte pak ale storage dobře chránit).

[![](/images/2021/2021-01-08-08-30-33.png){:class="img-fluid"}](/images/2021/2021-01-08-08-30-33.png)

Začněme nastavením sledování Windows registrů, kde kromě výchozích cest můžeme zapnout monitoring i jiných částí. Azure Defender dělá snapshot registrů každých 50 minut.

[![](/images/2021/2021-01-08-08-31-00.png){:class="img-fluid"}](/images/2021/2021-01-08-08-31-00.png)

Jak pro Windows tak pro Linux je možné sledovat klíčové soubory a přidávat svoje vlastní. To je důležité zejména pro Linux, kde je filozofie "všechno je file". Snapshot metadat a hash sledovaných souborů a adresářů se provádí každých 30 minut u Windows a 15 minut u Linuxu.

[![](/images/2021/2021-01-08-08-31-29.png){:class="img-fluid"}](/images/2021/2021-01-08-08-31-29.png)

Provedl jsem v OS změnu a přidal záznam do crontab. To samozřejmě nemusí být nic špatného, ale to že na serveru přibylo automatické spuštění nějakého procesu může samozřejmě indikovat snahu a zaperzistování útočníka apod. Tady jsou vidět nalezené rozdíly.

[![](/images/2021/2021-01-08-08-22-38.png){:class="img-fluid"}](/images/2021/2021-01-08-08-22-38.png)

Protože jsem nastavil nahrávání obsahu do Blob storage, můžeme se na soubory podívat. Aktuálně Azure Defender nezobrazuje rozdíly přímo ve svém GUI (ale pracuje se prý na tom), ale ve storage je můžu snadno najít.

[![](/images/2021/2021-01-08-08-23-32.png){:class="img-fluid"}](/images/2021/2021-01-08-08-23-32.png)

Všechny výsledky jsou k dispozici jako logy v Log Analytics workspace, takže k nim můžete běžně přistupovat, formulovat složité dotazy, využít automatizace reakcí na tyto události, streamovat záznamy do SIEM ať už Azure Sentinel nebo do nástrojů třetí strany přes připravené konektory (QRadar, ArcSight, Splunk apod.), vytvářet si vlastní vizualizace v Azure Workbooks nebo se na data napojit z externího vizualizačního nástroje jako je PowerBI či Grafana (oba mají hotové konektory). Takto vypadá pohled na surová data.

[![](/images/2021/2021-01-08-08-35-48.png){:class="img-fluid"}](/images/2021/2021-01-08-08-35-48.png)

Takhle si vypíšu soubory se změněnou hash.

[![](/images/2021/2021-01-08-08-36-31.png){:class="img-fluid"}](/images/2021/2021-01-08-08-36-31.png)

Pojďme si z dat vytvořit třeba časové grafy zobrazující množství změn ve sledovaných kategoriích.

[![](/images/2021/2021-01-08-08-43-19.png){:class="img-fluid"}](/images/2021/2021-01-08-08-43-19.png)

Jaké byly změny v registrech? Co se přidalo, vymazalo nebo změnilo?

[![](/images/2021/2021-01-08-08-44-02.png){:class="img-fluid"}](/images/2021/2021-01-08-08-44-02.png)

Vytvořme dotaz, který projde změny v registrech v části, kde jsou informace o nainstalovaném software.

[![](/images/2021/2021-01-08-08-49-32.png){:class="img-fluid"}](/images/2021/2021-01-08-08-49-32.png)


Takhle tedy funguje File Integrity Monitor v rámci Azure Defender, který je dostupný pro Linux i Windows a pro VM běžící jak v Azure, tak i mimo něj díky napojení přes Arc for Servers. Všechny změny systémových souborů můžete také jednoduše posílat do SIEM nástroje pro další korelaci, mimo jiné do Azure Sentinel. V kombinaci s dalšími prvky ochrany v rámci Azure Defender ať už je to EDR, trackování spouštěných aplikací, centrální sběr bezpečnostních logů nebo hardening sítě vzniká výborný balíček ochrany vašich serverů. Vyzkoušejte, nasaďte, chraňte se.

