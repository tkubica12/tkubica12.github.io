---
layout: post
published: true
title: "Update - náklady na můj blog v Azure a apex doména"
tags:
- Networking
- Storage
---
Před časem jsem popsal jak jsem na svém blogu přešel z dynamického obsahu ve Wordpress na statický obsah generovaný z Jekyll. Stránky servíruji ze Storage Account a https zajišťuji přes Azure CDN. Dnes chci popsat novinku - podporu apex domény (tomaskubica.cz) přes Azure DNS a CDN, což mi řeší problém, který jsem před tím musel dělat přesměrováním s Azure Functions. Dále se chci podívat na náklady.

# Apex doména
CDN systémy typicky potřebují v DNS serveru CNAME, ale ten dle standardu není možný pro apex doménu (resp. omezení se týká nemožnosti mít CNAME v kombinaci s jinými záznami a NS na apexu mít musím) - www.tomaskubica.cz je v pohodě, ale pro tomaskubica.cz CNAME neudělám. Musel jsem to řešit tím, že jsem měl Azure Function, která mi dovoluje odkázat se přes A záznam a v ní jsem prováděl 301 redirect na www.tomaskubica.cz. To je ale trochu nepraktické. Od minulého týdne už je ale možné do CDN dát i apex doménu díky nové vlastnosti Azure DNS Alias.

Vypadá to takhle - do DNS zadáte A záznam, ale nebude za ním konkrétní IP adresa, ale nějaká z podporovaných služeb v Azure a tou je nově právě Azure CDN ať už ji máte ve variantě Microsoft, Akamai nebo Verizon.

![](/images/2019/2019-04-08-07-05-48.png){:class="img-fluid"}

Služba vám vytvoří i verifikační záznamy, takže CDN nemá problém ověřit doménu a vygenerovat pro vás certifikát.

![](/images/2019/2019-04-08-07-06-51.png){:class="img-fluid"}

# Redirect na www
Ve svém Azure CDN Premium jsem už od začátku prováděl redirect z http na https. Nově jsem se rozhodl přidat ještě redirect z tomaskubica.cz na www.tomaskubica.cz. Není to sice nutné, ale na blogu mám uvedenu www formu a přišlo mi to tak hezčí.

![](/images/2019/2019-04-08-07-10-34.png){:class="img-fluid"}

![](/images/2019/2019-04-08-07-10-52.png){:class="img-fluid"}

![](/images/2019/2019-04-08-07-11-16.png){:class="img-fluid"}

# Náklady na můj blog
Zajímalo mne, kolik vlastně za svůj statický blog platím. Náklady jsou neuvěřitelně nízké. Největší položka je za CDN, ve které je schovaná naprostá většina odchozího provozu a také mám jako součást služby certifikát. Vychází to na asi 0,25 USD měsíčně. Další v pořadí je náklad na Azure DNS, který mám 0,10 USD. Třetí je poplatek za storage, který je díky relativně malé velikosti stránek (250 MB) asi 0,07 USD. Další náklady jsou odchozí provoz, ale ty jsou zcela zanedbatelné, protože naprostá většina jde přes CDN. Výsledek? Pohodlně se vejdu do jednoho dolaru, resp. jsem zatím tak na půlce.