---
layout: post
title: Jak jsem přešel z Wordpress na statické stránky Jekyll v Azure a proč
tags:
- Storage
- Networking
---
# Proč Wordpress
Když jsem někdy v roce 2012 začínal svůj první blog, potřeboval jsem něco jednoduchého, co mi zprovozní přímo poskytovatel a já se jen napojím a budu psát články. Víc jsem o tom nevěděl a vědět nechtěl. Zvolil jsem Wordpress.

Na konci 2016 jsem zakládal svůj hlavní osobní blog a říkal jsem si, že už to znám, a tak budu s Wordpressem pokračovat. Už v té době jsem ale věděl, že představa jednoduchosti se rozplynula hned, jak jsem si chtěl blog trochu přizpůsobit. Seznam pluginů začal boptnat a pokusy o zásah do PHP kódu končily tragicky. Ale o důvodech pro změnu později.

# Wordpress v Azure na konci 2016
Dnes bych neváhal a použil Wordpress pro WebApp for Linux (App Service) + Azure Database for MySQL (PaaS). Jenže to na konci 2016 k dispozici nebylo. Co s databází? Buď se dala přidat MySQL přímo do instance, ale to se mi vůbec nelíbilo z hlediska zálohování, dostupnosti apod. Dát to ven šlo, ale byla to služba třetí strany, která byla strašně drahá. Zvažoval jsem napojení Wordpress na Azure SQL Database (PaaS), ale to je speciální fork Wordpressu, u kterého jsem měl obavu co všechno v něm bude nebo nebude fungovat. U samotné App Service jsem se zas bál, že když použiji nějakou levnější variantu, bude pro mne možná omezující velikost storage (to se nepotvrdilo). Dnes u WebApp for Linux můžete namapovat Azure Files přímo k appce a získat tak víc prostoru, ale to dříve nešlo. U vyšších tierů je to OK (250 GB u Premium), ale u základních tam omezení je. Koukal jsem na možnost obrázky a jiné soubory tohoto typu dát mimo App Service a použít Blob storage. Je na to plugin, ale zdálo se mi, že kolem něj není dostatečně velká komunita a dělat to ručně se mi nechtělo.

Sečteno podtrženo - chci to levně a hodně jednoduše, takže jsem nakonec zvolil Bitnami image pro VMko (což se mi teda rozhodně nelíbí a svému mladšímu já bych za to vynadal) se strojem typu A. Levné a funkční.

# Nevýhody blogu na Wordpressu a moje cesta k optimalizacím
Po letech jsem přišel na následující věci, které mi vadí.

## Zálohování a databáze
Všechny mé články jsou v databázi a obrázky na disku. Abych dokázal obnovit blog jinde, musel bych mít archiv s obrázky, dump databáze a nainstalovat správnou verzi Wordpressu a v neposlední řadě i všechny použité pluginy. To už je docela dost a některá nastavení tam stejně nejsou, jako je http-to-https redirect a certifikát. Výsledkem bylo, že jsem dělal backupy přes Azure Backup pro celé VMko a také přes plugin zálohu obsahu, tedy DB, obrázky, pluginy.

## Rychlost

Vzhledem k tomu jak jednoduchý blog je mi doba načítání nepřipadala ideální. Povýšil jsem stroj na silnější konfiguraci, ale to nevedlo ke změně. Rozhodl jsem se tedy použít CDN a nainstaloval na to plugin v kombinaci s Azure CDN. Stáhl jsem asi 200ms, ale v tom to nebylo. Použil jsem tedy jiný plugin (WS Super Cache), který místo dynamického webu vyrenderuje statické prvky a tím zrychluje načítání. To dost pomohlo, ale začal jsem pochybovat o výhodách dynamického řešení, když to stejnak přepínám na statický obsah.

## Pluginy a udržitelnost

Seznam pluginů se zastavil někde u deseti. Plugin pro vkládání obrázků z clipboardu, plugin pro správné zobrazení kódu a YAML textů (pouhé pre nemělo dobré výsledky), zálohování, CDN, statická cache, https a tak dále. Navíc tady byly vizuální prvky. Člověk si stáhne šablonu, ale těch customizací nastavení musí udělat docela dost. A teď zjistíte, že některé pluginy se přestanou rozvíjet a novější verze Wordpressu nepodporují. Řešíte kdy co upgradovat, aby všechno fungovalo a vrácení do původního stavu, když se to nepovede, obvykle jednoduché není.

## Offline příprava a editor

Situace kdy nejsem online jsou opravdu vzácné, ale nastávají. Článek je nejlepší připravovat přímo ve Wordpress editoru, protože přenášet ho z jiného je práce navíc. Většinou mi online nevadí, ale editor ano. Mám ve Visual Studio Code oblíbené klávesové zkratky a různé vychytávky.

## Aktualizace a bezpečnost

Upřímně řečeno aktualizace OS jsem velmi flákal, ale použil jsem alespoň Just-in-time access v Azure Security Center, aby bylo SSH ve výchozím stavu zakázané. Nicméně zranitelnosti samotného OS jsem moc neopravoval. Dál se člověk má starat o Wordpress. Ten jsem občas aktualizoval, ale někdy se to nějakým pluginům nelíbilo.

# Jekyll jako generátor statického obsahu

GitHub Pages a Azure dokumentace jsou krásnou ukázkou využití generátoru statického obsahu. Zdrojové články lze psát v čistém Markdown, takže jsou univerzální a čitelné jakýmkoli způsobem. Navíc se dají držet ve version control systému pro jeden zdroj pravdy mezi různými zařízeními, ale u větších projektů i mezi členy týmu. Pokud by nás bylo na blog víc, určitě bychom skvěle využili konstruktů typu pull request nebo branch pro významné změny apod. Všechno co můj blog obsahuje, tedy články, obrázky, tagy i definice vzhledu je jen sada normálních souborů v Gitu.

Pro hostování nepotřebuji compute, nikde neběží serverový kód - ani ve VM, ani v App Service, kontejneru nebo Function. Potřebuji jen podávat statický obsah a to už dnes umí samotná storage (viz dále). To také znamená, že se nikam nedá přihlásit, nepotřebuji patchovat OS, databázi ani CMS.

Statický obsah dokáže být velmi rychlý, nezdržují mne přístupy do databáze.

Aby měl blog tagování, stránkování, generovaný RSS feed nebo sitemap pro roboty, potřebujeme tento obsah generovat. Zvolil jsem nejrozšířenější generátor [jekyll](http://jekyllrb.com). Použil jsem šablonu Clean Blog (Bootstrap pro Jekyll) a pár pluginů. Paginate v2 pro stránkování, feed pro vytvoření RSS souboru jekyll/tagging pro tagy (na blogu jim říkám témata). Rozhodl jsem se používat výhradně tagy místo kategorií. Zdá se totiž, že Jekyll nepodporuje příslušnost článku ve vícero kategoriích, což mi vadí. Na vytvoření stránky témat stačil je takhle jednoduchý kód:

{% raw %}
```
<div class="tag-cloud">
<h3>Všechna témata:</h3>
{% assign tags = site.tags | sort %}
{% for tag in tags %}
    <span class="site-tag">
        <a href="/tag/{{ tag | first | slugify }}.html"
            style="font-size: {{ tag | last | size  |  times: 4 | plus: 80  }}%">
                {{ tag[0] | replace:'-', ' ' }}&nbsp;({{ tag | last | size }})
        </a>
    </span>
{% endfor %}
</div>
```
{% endraw %}

Chtěl jsem u článku zobrazit nabídku dalších podobných. To Jekyll sám o sobě nemá ideálně řešené, ale našel jsem si příklad jednoduchého kódu, který najde články podle podobnosti na základě tagů:

{% raw %}
```
{% assign maxRelated = 5 %}

{% assign minCommonTags =  1 %}

{% assign maxRelatedCounter = 0 %}

{% for post in site.posts %}

    {% assign sameTagCount = 0 %}
    {% assign commonTags = '' %}

    {% for tag in post.tags %}

    {% if post.url != page.url %}
        {% if page.tags contains tag %}
        {% assign sameTagCount = sameTagCount | plus: 1 %}
        {% capture tagmarkup %} <span class="label label-default">{{ tag }}</span> {% endcapture %}
        {% assign commonTags = commonTags | append: tagmarkup %}
        {% endif %}
    {% endif %}
    {% endfor %}

    {% if sameTagCount >= minCommonTags %}
    <div>
    <h5><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}{{ commonTags }}</a></h5>
    </div>
    {% assign maxRelatedCounter = maxRelatedCounter | plus: 1 %}
    {% if maxRelatedCounter >= maxRelated %}
        {% break %}
    {% endif %}
    {% endif %}

{% endfor %}
```
{% endraw %}

A pak už pod článkem stačilo dát:
{% raw %}
```
        {% if related_posts != empty %}
        <hr>
        <div class="clearfix" id="related-posts">
        <h3>Podobné příspěvky</h3>
        <ul>
            {% for p in related_posts %}
            <li>
                <a href="{{ p.url }}" data-score="{{ p.score }}">{{ p.title }}</a>
            </li>
            {% endfor %}
        </ul>
        </div>
        {% endif %}

        {% include related.html %}
```
{% endraw %}

Mimochodem v mém případě je to zbytečně, ale celé sestavení webu se dá krásně automatizovat v rámci CI/CD. Nebo buildovat kontejnerem - může to vypadat nějak takhle. Postavíte si kontejner s Jekyll, jeho pluginy a azcopy pro nakopírování do storage.

```
FROM ubuntu

RUN apt update && apt install ruby-full build-essential zlib1g-dev git liblttng-ust0 libcurl3 libicu60 libunwind8 libuuid1 libssl1.0.0 libkrb5-3 rsync -y
RUN gem install jekyll bundler jekyll-feed jekyll-sitemap jekyll-paginate-v2 jekyll-tagging
COPY buildSite.sh azcopy ./
RUN chmod +x /buildSite.sh /azcopy
CMD ["./buildSite.sh"]
```

Skript by měl v sobě něco takového:

```bash
#!/bin/bash

# Clone site repo
git clone https://$gitUser:$gitPassword@$gitRepo

# Build site
cd /tomaskubica.cz
bundle install
bundle exec jekyll build
cd /_site

# Upload site
container='$web'

## Upload everything except images and overwrite if exists
for item in $(ls -1)
do
    if [ $item != images ]
    then
        /azcopy cp "./$item" "https://$storageAccount.blob.core.windows.net/$container$sas" --recursive=true --fromTo localBlob
    fi
done

## Upload images and do not overwrite if exists
/azcopy cp "./images/" "https://$storageAccount.blob.core.windows.net/$container$sas" --recursive=true --fromTo localBlob --overwrite=false

```

# Hostování webu bez serverů a instancí
Pro hostování statického obsahu jsem zvolil Azure Blob Storage, která to umí přímo servírovat uživatelům.

![](/images/2018/2018-12-25-21-41-33.png){:class="img-fluid"}

Obsah vygenerovaný Jekyllem jednoduše nahrajeme do kontejneru $web

![](/images/2018/2018-12-25-21-50-12.png){:class="img-fluid"}

Tohle řešení má slabinu. Můžu sice přidat svou vlastní doménu tomaskubica.cz, ale ne pro https (tedy Azure Blob Storage neumí nahrát vlastní certifikát). To je omezení, které je i u jiných objektových ukládání dat bohužel celkem běžné, ale zásadně mi nevadí, protože stejnak chci před storage dostat CDN. A dokonce právě až ta CDN bude mít mojí doménu.

Jakou CDN si v Azure vybrat? Narazil jsem na jeden pro mne důležitý požadavek - chci, aby to dělalo http-to-https redirect a to zatím žádná z variant CDN v režimu Standard (Microsoft, Akamai, Verizon) nenabízí. Mohl bych redirect mít až za CDN, ale tam ho zas nepodporuje Azure Blob Storage (můžu zakázat http, ale to nezpůsobí odpovídání přes 301, ale jen výstražnou stránku o vypnutém http). V mém případě tedy musím jít do Azure CDN Premium by Verizon. Předpokládám, že v budoucnu se to bude dát řešit i jinými způsoby. Moje redirect pravidlo vypadá takhle:

![](/images/2018/2018-12-25-21-53-00.png){:class="img-fluid"}

Kromě toho jsem si pohrál s cachovacími pravidly. U obrázku nečekám žádné změny a nechal jsem je platné po dobu 30 dní. Soubory typu css a js nebudu měnit často a nechám je platné 1 den. Všechno ostatní chci staré maximálně 5 minut. Jde totiž o to, že po publikaci nového článku by ho nikdo neviděl. V Azure CDN Verizon Premium jsem jako první dvě pravidla dal match na URL Path Extension a v Features použil jednak Force Internal Max-Age (maximální stáří, než se CDN doptá storage na poslední verzi) a taky External Max-Age (co chci aby CDN posílala klientům z důvodu cachování v browseru) - pro png jpg jpeg dávám 30 dní a pro js css dávám 1 den. Poslední pravidlo je match na Always a nastavuje obě hodnoty právě na těch 5 minut.

![](/images/2018/2018-12-27-16-57-03.png){:class="img-fluid"}

Ale pojďme k jedné nepříjemnosti a jedné skvělé výhodě. Jak přiřadit vlastní doménu? Azure CDN aktuálně podporuje pouze CNAME a ten, jak je dáno DNS standardem, nelze založit pro holou doménu (např. tomaskubica.cz), pouze pro subdoménu jako je www.tomaskubica.cz. CDN nemá nějakou IP adresu, na kterou bychom mohli namířit A záznam (což chápu, že je z důvodu redundance problematické) a ani nepodporuje anycast (což by bylo ideální řešení). Navíc můj DNS poskytovatel ani Azure DNS (do které jsem si doménu před časem převedl) nepodporuje exotické záznamy typu ANAME, které to můžou řešit (ale taky ne ideálně, protože CDNku mohou mást z hlediska lokace uživatele). Nicméně teď to pozitivní - certifikát pro vás zajišťuje Azure sám! Nemusíte se trápit jeho enrollmentem, nemusíte za něj platit, je to součástí služby jako takové a to je velmi příjemné.

![](/images/2018/2018-12-25-22-00-05.png){:class="img-fluid"}

Poslední co tedy musím vyřešit je holá doména tomaskubica.cz. Nejjednodušší se mi jeví využít Azure Functions Proxy, která jednoduchý 301 redirect krásně zajistí. V zásadě vytvoříme Azure Function, v ní proxy a můžete rovnou do advanced editoru a dát tam soubor proxies.json:

```json
{
    "$schema": "http://json.schemastore.org/proxies",
    "proxies": {
        "permanent redirect": {
            "matchCondition": {
                "methods": [
                    "GET",
                    "POST",
                    "DELETE",
                    "HEAD",
                    "PATCH",
                    "PUT",
                    "OPTIONS",
                    "TRACE"
                ],
                "route": "/{*restOfPath}"
            },
            "responseOverrides": {
                "response.statusCode": "301",
                "response.headers.Location": "https://www.tomaskubica.cz/{restOfPath}"
            }
        }
    }
}
```

Pak přiřaďte custom domain, což právě podporuje i IP adresu, tedy A záznam a tím holou doménu. Ještě se musí vytvořit certifikát. Svou function jsem umístil na existující Service Plan typu Standard, protože chci zapnout Always On (consumption based plán může způsobovat studený start a nechci nechat uživatele čekat přes 10 vteřin)... nicméně pokud všem říkáte www.doména.cz a podporu doména.cz potřebujete jen pro výjimečné případy, klidně stačí i consumption varianta.

# V čem by se to mohlo zlepšit
Především z hlediska nasazení bych moc rád dospěl k situaci, kdy CDNka i v základu bez custom pravidel umí http-to-https redirect a současně podporuje holé domény třeba přes anycast. Obě věci jsou ve veřejné roadmapě zmíněny, tak doufám, že se brzy dočkám možnosti je zapnout a situaci si zjednodušit.

Druhé na co se chystám je přidání dynamických prvků, ale mimo můj blog. Konkrétně koukám na možnost vyhledávání na webu (zjevný nedostatek statického řešení) a experimentuji s Azure Search. Tato služba dokáže moc pěkně zaindexovat full text hledání včetně mnoha pokročilých možností a nabízí API, na které bych mohl přistupovat přímo z klientského Javascriptu. Zatím to ještě nemám, ale první pokusy ukazují, že to půjde. Až rozlousknu, napíšu jak na to.
