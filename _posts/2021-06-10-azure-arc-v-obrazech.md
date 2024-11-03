---
layout: post
published: true
title: Azure Arc v obrazech místo 1000 slov - hybridní a multi-cloud řešení prakticky
tags:
- Arc
---
O Azure Arc už jsem tu mnohokrát psal a detaily některých novinek jako jsou aplikační služby nad Arc (App Service nebo Azure Functions pro váš Kubernetes cluster běžící kdekoli) se podíváme detailněji někdy příště. Dnes nám půjde o náhled na základní rámec a tentokrát v obrazech - z GUI zdá se mi člověku rychle dojde co to vlastně dělá.

Mějme VM v Digital Ocean.

[![](/images/2021/digitalocean-vm.gif){:class="img-fluid"}](/images/2021/digitalocean-vm.gif)

Podívejme se co se s ní dá dělat v Azure Arc.

[![](/images/2021/arc-servers.gif){:class="img-fluid"}](/images/2021/arc-servers.gif)

A co z bezpečnostního hlediska? Nachází tam Azure Defender nějaké zranitelnosti?

[![](/images/2021/defender-vmvulnerability.gif){:class="img-fluid"}](/images/2021/defender-vmvulnerability.gif)

Vytvořím si spravovaný Kubernetes v Google Cloud (GKE).

[![](/images/2021/GKE.gif){:class="img-fluid"}](/images/2021/GKE.gif)

Napojíme do Azure Arc a podívejme se, co s ním můžu dělat.

[![](/images/2021/arc-kubernetes-management.gif){:class="img-fluid"}](/images/2021/arc-kubernetes-management.gif)

Určitě se bude hodit i centrální monitoring všech clusterů.

[![](/images/2021/arc-kubernetes-monitoring.gif){:class="img-fluid"}](/images/2021/arc-kubernetes-monitoring.gif)

Neměl bych podcenit ani bezpečnost, takže použiji Azure Defender.

[![](/images/2021/defender-kubernetes.gif){:class="img-fluid"}](/images/2021/defender-kubernetes.gif)

Tím jsme napojili hybridní, edge a multi-cloud infrastrukturu do Azure Arc. Teď nad ní začneme nasazovat platformní služby Azure. Prvním krokem bude vytvořit své vlastní "regiony", moje datová centra, ostatní cloudy, minipočítače v továrnách nebo Azure Stack instalace.

[![](/images/2021/arc-custom-location.gif){:class="img-fluid"}](/images/2021/arc-custom-location.gif)

Pojďme do nového regionu nasadit aplikace v PaaS - Azure App Service.

[![](/images/2021/arc-webapp.gif){:class="img-fluid"}](/images/2021/arc-webapp.gif)

To se v cluster v Google projeví takto.

[![](/images/2021/gke-appservice.gif){:class="img-fluid"}](/images/2021/gke-appservice.gif)

Zkusme totéž pro serverless - Azure Function.

[![](/images/2021/arc-functions.gif){:class="img-fluid"}](/images/2021/arc-functions.gif)

Mezi aplikacemi často potřebujeme distribuovat triggery a události. Co kdybychom použili Azure Event Grid v našem novém "regionu"?

[![](/images/2021/arc-eventgrid.gif){:class="img-fluid"}](/images/2021/arc-eventgrid.gif)

Což v Google clusteru vidím takhle.

[![](/images/2021/gke-eventgrid.gif){:class="img-fluid"}](/images/2021/gke-eventgrid.gif)

No a celé to aplikačně zastřešme centrálně spravovaným leč plně hybridně/multi-cloud řešeným API managementem.

[![](/images/2021/arc-apim.gif){:class="img-fluid"}](/images/2021/arc-apim.gif)

Gateway se samozřejmě objeví v mém Google clusteru.

[![](/images/2021/gke-apim.gif){:class="img-fluid"}](/images/2021/gke-apim.gif)

A co nasadit v mém novém regionu databázi? Třeba Azure SQL Managed Instance nebo Azure Database for PostgreSQL Hyperscale?

[![](/images/2021/arc-sqlmi.gif){:class="img-fluid"}](/images/2021/arc-sqlmi.gif)

Vidím, že v Google clusteru mi databáze jede pěkně v redundanci.

[![](/images/2021/gke-sql.gif){:class="img-fluid"}](/images/2021/gke-sql.gif)

Multi-cloud přístup vyžaduje i řídit bezpečnostní doporučení v těchto cloudech.

[![](/images/2021/defender-multicloud.gif){:class="img-fluid"}](/images/2021/defender-multicloud.gif)

Stejně tak je ale důležité hlídat co se děje, objevovat hrozby, chránit servery a tak podobně.

[![](/images/2021/defender-threatprotectionmulticloud.gif){:class="img-fluid"}](/images/2021/defender-threatprotectionmulticloud.gif)

No a nad tím vším postavím bezpečnostní řešení SIEM a SOAR s Azure Sentinel. Tam se sbíhá všechno včetně identit, koncových zařízení, bezpečnostních produktů Microsoft 365 i třetích stran a samozřejmě i třeba informace z AWS. Ale to už je jiný příběh o budování bezpečnostního centra a skutečně ucelený pohled na prostředí, Azure Arc je jen jedním z mnoha zdrojů vstupních informací do Azure Sentinel.










