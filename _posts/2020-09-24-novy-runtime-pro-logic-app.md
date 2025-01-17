---
layout: post
published: true
title: Nový runtime pro Logic App integrační platformu vám umožní ji běžet i v on-premises
tags:
- Serverless
---
Na konferenci Ignite tento týden bylo uvolněno preview novinky součásti Microsoft integrační platformy jako služba (iPaaS) - workflow nástroje Logic Apps. Ten v kombinaci se službami jako je Azure API Management, Service Bus nebo Event Grid nabízí kompletní integrační platformu v cloudu. A nebo i mimo něj? Nová generace Logic Apps mění technologii zabalení a spuštění procesu tak, že využívá serverless přístupy Azure Functions. To znamená nejen levnější a jednodušší integraci do VNETu, ale i možnost zabalit prostředí do kontejneru a provozovat kdekoli - včetně vašeho on-premises Kubernetes clusteru nebo i pouhé mašiny s Dockerem.

# Co umí Logic App
Logic App je událostně řízená serverless platforma. Na jejím startu tedy je nějaký trigger a těch platforma nabízí nativně velké množství. Může to být kalendář (pravidelné spouštění), zavolání http interface, událost v Microsoft světě (nová zpráva v Teams kanálu, nový email, nový soubor ve OneDrive nebo Blob storage, nová zpráva v Service Bus frontě, nový záznam v Dynamics365 a stovka dalších), ale i mimo něj, třeba v jiném cloudu (např. nová zpráva v Amazon SQS), komunikační či marketingové platformě (Adobe, Slack, nové video na YouTube), datové službě (Dropbox, Box) nebo SaaS aplikaci (ServiceNow, SAP, SFDC). Jakmile k události dojde, workflow se spustí a provádí jednotlivé akce včetně větvení a další pokročilé logiky. Každá akce je kostička, konektor, o který se vám Azure stará a jednoduše graficky v něm řeknete co potřebujete. Například odeslat email, vytvořit objednávku v SAPu, načíst kontakty z SFDC nebo Dynamics, založit incident v Jira či ServiceNow a tak podobně. Není to jen "generátor skriptů", protože Logic App je stavová, tedy po každém příkazu si zaznamená jak je daleko a případně se může odmlčet v čekání na nějaký vstup včetně lidského zásahu (čekám na reakci nadřízeného, který dostal email s pár tlačítky, kterými rozhodne co se má dít dál).

Logic App je profesionální součástí iPaaS a jako taková podporuje věci jako DevOps nasazování včetně canary releasování, detailní monitoring, bezpečnost a integraci s APIM a dalšími komponentami. Považujme ji za nástroj na kterém stavíte integrační služby pro aplikace a firemní procesy. Prakticky stejný engine je ale k dispozici i koncovým uživatelům v rámci Power platformy pod názvem Power Automate a může se tak stát součástí vašich aplikací vytvořených v Power Apps.

# Logic App, Visual Studio Code a deployment do Azure Functions Premium
Zásadní novinkou s novou Logic App je změna runtime prostředí, které je postavené na frameworku Azure Functions. Zásadní výhodou je možnost provozovat workflow ve standardní platformě Azure App Service nebo Azure Functions Premium. To co služba dříve neuměla (nebo to stálo strašné peníze) dnes snadno podědila v rámci zmíněných platforem. Tak například vaše workflow může využít integrace obou platforem do VNETu, takže přes VPNku můžete na privátní síti přistupovat k on-premises zdrojům. Podpora Private Link vám umožní vystavit API Logic App (trigger) do privátní sítě a provolávat tak Logic Appky vnitřně nebo z on-premises.

Nově je k dispozici nová generace krásného pluginu pro Visual Studio Code, který umožní vytvářet integrační workflow i bez Azure portálu a dělat lokální debugging.

![](/images/2020/2020-09-24-06-29-04.png){:class="img-fluid"}

V designeru přímo ve Visual Studio Code jsem si vytvořil jednoduché workflow. To čeká na zavolání, následně zavolá jiné API a jeho výsledek vezme, něco k němu přidá a to vrátí tomu, kdo workflow spustil. Skutečně velmi primitivní scénář.

![](/images/2020/2020-09-24-06-30-46.png){:class="img-fluid"}

Výborné je, že můžu zmáčknout F5 a Logic App spustit lokálně bez čehokoli v Azure.

![](/images/2020/2020-09-24-06-31-47.png){:class="img-fluid"}

Pak už jsem použil extension ve VS Code a nasadil toto workflow v Azure s využitím Azure Functions Premium.

![](/images/2020/2020-09-24-06-36-34.png){:class="img-fluid"}

V sekci workflow najdu vše potřebné a samozřejmě mohu procesy vytvářet přímo v portálu, VS Code nepotřebuji, pokud chci stejně provozovat Logic App v Azure (výhoda VS Code je v lokálním vývoji, debugging a napojení na Azure DevOps či jiné CI/CD prostředí).

![](/images/2020/2020-09-24-06-37-59.png){:class="img-fluid"}

![](/images/2020/2020-09-24-06-38-22.png){:class="img-fluid"}

![](/images/2020/2020-09-24-06-38-42.png){:class="img-fluid"}

Vezmu si URL a vyzkoušíme.

![](/images/2020/2020-09-24-06-39-28.png){:class="img-fluid"}

```bash
curl -X GET "https://mojeazurestacklapp.azurewebsites.net:443/api/lapp-stateless/triggers/manual/invoke?api-version=2020-05-01-preview&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=jGe3LmARutbCZdbnBw6sbGepcpIyGmojCaj-ASm4-z4"

Moje privatni API rika: <H1>Azure Stack demo Prague</H1>
```

Funguje to!

Tím, že jsme ve standardizované platformě můžeme například integrovat běžící kód s VNETem.

![](/images/2020/2020-09-24-06-41-22.png){:class="img-fluid"}

VNET integrace znamená, že workflow vidí do VNETu a potažmo VPN či Express Route, takže můžu přistupovat konektory do lokálního prostředí, třeba volat nějaký systém na privátní adrese. Private Endpoint mi pomůže v opačném směru pro případ, kdy je trigger typu HTTP (Logic App se spouští zavoláním API třeba z aplikace, Event Grid a tak podobně) a dovolí mi tento interface namapovat do privátní adresy VNETu.

Mám také možnost řešit jak velké mašiny pod tím chci a to jak v mém případě Azure Functions Premium, tak běžný App Service plán.

![](/images/2020/2020-09-24-06-44-15.png){:class="img-fluid"}

Logicky totéž platí pro Scale Out a protože používám Azure Functions Premium, mohu nastavit minimální a maximální počty nodů. Protože Functions Premium plán vždy běží alespoň jednu instanci trvale netrpí problémem pomalého startu, protože alespoň tento node je k dispozici okamžitě.

![](/images/2020/2020-09-24-06-45-43.png){:class="img-fluid"}

Vezměte v úvahu, že tímto Logic App dědí i další funkce aplikačních platforem v Azure - například deployment sloty pro A/B testing či canary releasování.

![](/images/2020/2020-09-24-06-46-44.png){:class="img-fluid"}

# Zabalení do kontejneru a nasazení v Kubernetes mimo Azure
Azure Functions framework lze zabalit do kontejneru a ten pustit dokonce i mimo Azure. Možnosti triggerů pak jsou logicky dost omezené, ale http trigger fungovat bude, tak to vyzkoušejme. Vytvořil jsem dle návodu Dockerfile a celý projekt zbuildoval. Následně jsem svou Logic App pustil lokálně v kontejneru na notebooku.

```bash
❯ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                            NAMES
a5c1a4fbf00c        tkubica/lapp:v1     "/azure-functions-ho…"   20 hours ago        Up 13 hours         2222/tcp, 0.0.0.0:8080->80/tcp   vigilant_kalam
```

Rozdíl oproti lokální debuggingu mám v tom, že tentokrát jsem v Dockerfile vyplnil proměnnou AzureWebJobsStorage tak, že ukazuje na storage account v Azure místo lokálního simulátoru. Stav a další provozní informace si workflow ukládá tam a v tomto accountu také najdu host.json, ve kterém se dozvím master klíč. Díky němu se mohu běžícího kontejneru zeptat na SAS token pro volání triggeru.

```bash
curl -X POST "127.0.0.1:8080/runtime/webhooks/workflow/api/management/workflows/lapp-stateless/triggers/manual/listCallbackUrl?api-version=2019-10-01-edge-preview&code=FFX7h0GhdVEgCs/O5Bej7ulsaKU8lod1R88wJKWMnYonxQpuCuBsTA==" -d ''
```

A tím už mám URL triggeru včetně tokenu.

```bash
curl "http://127.0.0.1:8080/api/lapp-stateless/triggers/manual/invoke?api-version=2020-05-01-preview&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=enh0RWDMkHYe8UYhqrbe0hmCppf_L5Si9iwBYf53NBY"

Moje privatni API rika: <H1>Azure Stack demo Prague</H1>
```

Pefektní - moje Logic App běží v kontejneru na notebooku.

Dostat to do Kubernetes clusteru běžícího mimo Azure už nebyl problém.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: logic-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: logic-app
  template:
    metadata:
      labels:
        app: logic-app
    spec:
      containers:
      - name: logic-app
        image: tkubica/lapp:v1
        env:
        - name: WEBSITE_HOSTNAME
          value: lapp.aks.azurepraha.com
        ports:
        - containerPort: 80
          name: http
---
apiVersion: v1
kind: Service
metadata:
  name: logic-app
spec:
  ports:
  - port: 80
  selector:
    app: logic-app
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
    ingress.kubernetes.io/rewrite-target: /
  name: lapp-ingress
spec:
  rules:
    - host: lapp.aks.azurepraha.com
      http:
        paths:
          - path: /
            backend:
              serviceName: logic-app
              servicePort: 80
```


Oddělení Logic App od prostředí ve kterém běží je výborný další evoluční krok. Nově tak můžete Logic App provozovat v Azure s využitím serverless platformy Azure Functions Premium nebo ji zasadit do App Service Plan klasického typu vedle vašich WebApps a dalších aplikačních komponent. To dává obrovský smysl. Mimochodem Azure API Management už dnes také umí provozovat gateway v Kubernetes mimo Azure a dohromady tyto dvě služby společně s Event Grid či Service Bus vytváří mohutnou iPaaS. Jak může vývoj vypadat dál? Očekával bych, že se to stane součástí Azure Arc a dojde ke zjednodušení nasazení. Aktuálně musíte workflow do Kubernetes nasadit sami, ale umím si představit, že budete mít GUI na tvorbu workflow a pak jen řeknete kam ho chcete plácnout - nejdřív to může být další tlačítko ve VS Code (aktuálně tam je deployment do App Service a Functions), následně i Azure portál, ve kterém jsou už dnes vidět spravované Kubernetes clustery běžící kdekoli díky Azure Arc for Kubernetes. Z vašeho prostředí by se tak stalo jen další tlačítko, další místo, kde může Logic App běžet. Něco podobného dělá Azure Arc for Data Services s MS SQL a PostgreSQL. V lokálním kontejneru dnes funguje asi 10 Microsoft AI služeb a očekávám, že se do podobně hybridního režimu budou postupně dostávat další a další služby. 