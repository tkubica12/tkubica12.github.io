---
layout: post
status: publish
published: true
title: Azure Front Door prakticky - routovací engine
tags:
- Networking
---
Služba Azure Front Door je vlastně reverse proxy s Web Application Firewall distribuovaná po celé planetě na POP místech Microsoft sítě včetně Prahy. Jedna konfigurace, 165 lokalit a uživatel se přes anycast dostane vždy na tu nejbližší, kde je jeho TLS session terminována. Dnes se podíváme na rules engine pro tvorbu složitějších směrovacích politik.

Nejprve si vytvoříme pár backendových aplikací. Použijeme httpbin (jednoduchá "appka", která například umí vrátit co jsme jí poslali) a to ve formě kontejnerových instancí s tím, že dvě produkční jsou v Evropě a v USA a k tomu testovací instance.

```bash
az group create -n front-door -l westeurope
az container create -g front-door \
    -n prod-tomasbin-eu \
    --image kennethreitz/httpbin \
    --ports 80 \
    --ip-address public \
    --dns-name-label prod-tomasbin-eu \
    -l westeurope 
az container create -g front-door \
    -n prod-tomasbin-us \
    --image kennethreitz/httpbin \
    --ports 80 \
    --ip-address public \
    --dns-name-label prod-tomasbin-us \
    -l eastus
az container create -g front-door \
    -n dev-tomasbin \
    --image kennethreitz/httpbin \
    --ports 80 \
    --ip-address public \
    --dns-name-label dev-tomasbin \
    -l westeurope
```

Vytvořme si Front Door, v něm základní směrovací politiku a dva backendy - jeden produkční obsahující instance v Evropě a USA a druhý testovací.

```bash
az extension add --name front-door
az network front-door create -n tomasfrontdoor123 \
    -g front-door \
    --backend-address prod-tomasbin-eu.westeurope.azurecontainer.io \
    --backend-host-header prod-tomasbin-eu.westeurope.azurecontainer.io \
    --protocol Http \
    --forwarding-protocol HttpOnly
az network front-door backend-pool backend add --address prod-tomasbin-us.eastus.azurecontainer.io \
    --backend-host-header prod-tomasbin-us.eastus.azurecontainer.io \
    --front-door-name tomasfrontdoor123 \
    --pool-name DefaultBackendPool \
    -g front-door  

az network front-door backend-pool create --address dev-tomasbin.westeurope.azurecontainer.io \
    --backend-host-header dev-tomasbin.westeurope.azurecontainer.io \
    --front-door-name tomasfrontdoor123 \
    --load-balancing DefaultLoadBalancingSettings \
    --name DevBackendPool \
    --probe DefaultProbeSettings \
    -g front-door 
```

V GUI jsem teď vytvořil pravidla v rules engine, ke kterým se hned dostaneme.

![](/images/2020/2020-06-17-06-09-05.png){:class="img-fluid"}

A tato pravidla přidal do své routing politiky.

![](/images/2020/2020-06-17-06-10-02.png){:class="img-fluid"}

Pojďme se teď na jednotlivá nastavení podívat. Nejprve tedy provoz, který žádnému zvláštnímu pravidlu nepodléhá. Pouštím ze svého počítače a tedy očekávám, že můj nejbližší Front Door v Praze pro mě vybere backend instanci v Evropě, která je nejblíž.

```bash
curl http://tomasfrontdoor123.azurefd.net/anything
{
  "args": {},
  "data": "",
  "files": {},
  "form": {},
  "headers": {
    "Accept": "*/*",
    "Connection": "Keep-Alive",
    "Host": "prod-tomasbin-eu.westeurope.azurecontainer.io",
    "User-Agent": "curl/7.68.0",
    "X-Azure-Clientip": "2a00:1028:919b:4256:8d6c:df37:3766:1688",
    "X-Azure-Fdid": "ee9655cc-dbc4-46d9-84e1-6aeeb112c01f",
    "X-Azure-Ref": "0hCT8XgAAAABvjSBaUKCcSZuP8KSgQRzlUFJHMDFFREdFMDYwOABlZTk2NTVjYy1kYmM0LTQ2ZDktODRlMS02YWVlYjExMmMwMWY=",
    "X-Azure-Requestchain": "hops=1",
    "X-Azure-Socketip": "2a00:1028:919b:4256:8d6c:df37:3766:1688",
    "X-Forwarded-Host": "tomasfrontdoor123.azurefd.net"
  },
  "json": null,
  "method": "GET",
  "origin": "2a00:1028:919b:4256:8d6c:df37:3766:1688",
  "url": "http://tomasfrontdoor123.azurefd.net/anything"
}
```

Z odzrcadleného header Host vidím, že jsem na produkční eu instanci. Když to samé udělám z VM, kterou si pustím někde v Americe, bude výsledek vypadat tak, že nejbližší tamní Front Door vyhodnotí jako pro mě nejvýhodnější instanci aplikaci v USA.

```bash
az container create -g front-door \
    -n tomasclient-us \
    --image tkubica/mybox \
    -l eastus2 

az container exec -g front-door \
    -n tomasclient-us \
    --container-name tomasclient-us \
    --exec-command "/bin/bash"

curl http://tomasfrontdoor123.azurefd.net/anything
```

```json
{
  "args": {},
  "data": "",
  "files": {},
  "form": {},
  "headers": {
    "Accept": "*/*",
    "Connection": "Keep-Alive",
    "Host": "prod-tomasbin-us.eastus.azurecontainer.io",
    "User-Agent": "curl/7.58.0",
    "X-Azure-Clientip": "13.68.73.120",
    "X-Azure-Fdid": "ee9655cc-dbc4-46d9-84e1-6aeeb112c01f",
    "X-Azure-Ref": "0yCX8XgAAAAD7KmBRlxZpTLFfOLBGVUHhQk4zRURHRTExMTUAZWU5NjU1Y2MtZGJjNC00NmQ5LTg0ZTEtNmFlZWIxMTJjMDFm",
    "X-Azure-Requestchain": "hops=1",
    "X-Azure-Socketip": "13.68.73.120",
    "X-Forwarded-Host": "tomasfrontdoor123.azurefd.net"
  },
  "json": null,
  "method": "GET",
  "origin": "13.68.73.120",
  "url": "http://tomasfrontdoor123.azurefd.net/anything"
}
```

První příklad bude reagovat na přítomnost nějakého headeru a na základě toho upravíme směrování. Konkrétně v případě, že uvidím header Tester nastavený na true, chci místo produkčního backendu použít testovací.

![](/images/2020/2020-06-17-06-35-11.png){:class="img-fluid"}

Vyzkoušíme, funguje.

```bash
curl http://tomasfrontdoor123.azurefd.net/anything -H "Tester: true"
{
  "args": {},
  "data": "",
  "files": {},
  "form": {},
  "headers": {
    "Accept": "*/*",
    "Connection": "Keep-Alive",
    "Host": "dev-tomasbin.westeurope.azurecontainer.io",
    "Tester": "true",
    "User-Agent": "curl/7.68.0",
    "X-Azure-Clientip": "2a00:1028:919b:4256:8d6c:df37:3766:1688",
    "X-Azure-Fdid": "ee9655cc-dbc4-46d9-84e1-6aeeb112c01f",
    "X-Azure-Ref": "06SX8XgAAAACK7HwVAQ/yT7SdyrdfZ53RUFJHMDFFREdFMDYyMQBlZTk2NTVjYy1kYmM0LTQ2ZDktODRlMS02YWVlYjExMmMwMWY=",
    "X-Azure-Requestchain": "hops=1", 
    "X-Azure-Socketip": "2a00:1028:919b:4256:8d6c:df37:3766:1688",
    "X-Forwarded-Host": "tomasfrontdoor123.azurefd.net"
  },
  "json": null,
  "method": "GET",
  "origin": "2a00:1028:919b:4256:8d6c:df37:3766:1688",
  "url": "http://tomasfrontdoor123.azurefd.net/anything"
}
```

Podívejme se na další příklad, který jsem připravil. Dejme tomu, že chceme reagovat na něco v cestě, query nebo nějaké jiné části requestu (já použiji query) a pokud obsahuje slovo super, tak chci provést redirect na jinou stránku.

![](/images/2020/2020-06-17-11-03-06.png){:class="img-fluid"}

```bash
curl http://tomasfrontdoor123.azurefd.net/anything?super=yeah -v
*   Trying 2620:1ec:bdf::10:80...
* TCP_NODELAY set
* Connected to tomasfrontdoor123.azurefd.net (2620:1ec:bdf::10) port 80 (#0)
> GET /anything?super=yeah HTTP/1.1
> Host: tomasfrontdoor123.azurefd.net
> User-Agent: curl/7.68.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 302 Found
< Location: https://www.microsoft.com/?super=yeah
< Server: Microsoft-IIS/10.0
< X-Azure-Ref: 0ySb8XgAAAAAucEGfPZ1vQrSWyqaYSpyrUFJHMDFFREdFMDQxNwBlZTk2NTVjYy1kYmM0LTQ2ZDktODRlMS02YWVlYjExMmMwMWY=
< Date: Wed, 01 Jul 2020 06:01:45 GMT
< Content-Length: 0
< 
* Connection #0 to host tomasfrontdoor123.azurefd.net left intact
```

URL rewrite je standardní součástí jednoduché Front Door směrovacího pravidla, ale to funguje jen tak, že vezme něco z URL a provede rewrite na jinou cestu. S použitím rules engine získáváme mnoho dalších možností - opět to může být cesta, hlavička, query a tak podobně. Nastavil jsem pravidlo, která kouká do User-Agent a v případě mobilního klienta provede URL rewrite, ale jiné nechá bez povšimnutí. Tím pádem by mi odkaz na "/neco" měl vrátit chybu 404 (taková stránka neexistuje), ale v případě mobilního klienta bude všechno natvrdo přepsáno na /anything.

![](/images/2020/2020-07-02-08-29-00.png){:class="img-fluid"}

```bash
curl http://tomasfrontdoor123.azurefd.net/neco
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.</p>

curl http://tomasfrontdoor123.azurefd.net/neco -H "User-Agent: Mozilla/5.0 (Linux; Android 10; SM-G960F)"
{
  "args": {},
  "data": "",
  "files": {},
  "form": {},
  "headers": {
    "Accept": "*/*", 
    "Connection": "Keep-Alive",
    "Host": "prod-tomasbin-eu.westeurope.azurecontainer.io",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G960F)",
    "X-Azure-Clientip": "88.102.208.149",
    "X-Azure-Fdid": "ee9655cc-dbc4-46d9-84e1-6aeeb112c01f", 
    "X-Azure-Ref": "0mHr9XgAAAACU+nTTkS92Sbzsmg3/lZoFUFJHMDFFREdFMDQxNABlZTk2NTVjYy1kYmM0LTQ2ZDktODRlMS02YWVlYjExMmMwMWY=",
    "X-Azure-Requestchain": "hops=1",
    "X-Azure-Socketip": "88.102.208.149",
    "X-Forwarded-Host": "tomasfrontdoor123.azurefd.net"
  },
  "json": null,
  "method": "GET",
  "origin": "88.102.208.149",
  "url": "http://tomasfrontdoor123.azurefd.net/anything/neco"
}
```

Další věc, kterou můžeme dělat na základě pokročilejších pravidel je nastavovat cachování. Představme si třeba, že chceme mít odlišné nastavení cache v závislosti na konkrétní informace v cestě a současně na základě headeru. Následující pravidlo říká, že pokud se v cestě vyskytuje bytes a současně je header doCache nastaven na true, chceme odpověď cachovat po dobu jedné minuty bez ohledu na query parametry.

![](/images/2020/2020-07-08-07-05-01.png){:class="img-fluid"}

Vyzkoušejme. Pokud se vám stane, že zopakujete request s doCache header napoprvé rychle po sobě a dostanete jinou odpověď, tak se neděste - Front Door není jen jedna bednička, ale masivní distribuovaný systém, takže má prvky eventuální konzistence (to ale u cache určitě nevadí a je to běžné i ve všech CDN systémech apod.).

```bash
curl http://tomasfrontdoor123.azurefd.net/bytes/5 -s -H "doCache: false" | base64
U1GJXpI=

curl http://tomasfrontdoor123.azurefd.net/bytes/5 -s -H "doCache: false" | base64
zw7seBg=

curl http://tomasfrontdoor123.azurefd.net/bytes/5 -s -H "doCache: true" | base64
9lKxIhk=

curl http://tomasfrontdoor123.azurefd.net/bytes/5 -s -H "doCache: true" | base64
9lKxIhk=
```

Jako poslední příklad si vyzkoušíme reakci na posílaný obsah. Front Door může koukat i do samotných dat. Nastavme si pravidlo, že pokud v datech najde slovo ahoj, přidá do odpovědi speciální header.

![](/images/2020/2020-07-08-07-11-45.png){:class="img-fluid"}

Vyzkoušejme.

```bash
curl -X POST http://tomasfrontdoor123.azurefd.net/post -d '{"message": "ahoj"}' -H "Content-Type: application/json" -o /dev/null -s -v
*   Trying 2620:1ec:bdf::10:80...
* TCP_NODELAY set
* Connected to tomasfrontdoor123.azurefd.net (2620:1ec:bdf::10) port 80 (#0)
> POST /post HTTP/1.1
> Host: tomasfrontdoor123.azurefd.net
> User-Agent: curl/7.68.0
> Accept: */*
> Content-Type: application/json
> Content-Length: 19
>
} [19 bytes data]
* upload completely sent off: 19 out of 19 bytes
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Content-Length: 893
< Content-Type: application/json
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Credentials: true
< X-Azure-Ref: 0xFQFXwAAAADwPlgTPnBMQYYB1ymcDt+XUFJHMDFFREdFMDcxOABlZTk2NTVjYy1kYmM0LTQ2ZDktODRlMS02YWVlYjExMmMwMWY=
< ByloTamAhoj: true
< Date: Wed, 08 Jul 2020 05:08:19 GMT
<
{ [893 bytes data]
* Connection #0 to host tomasfrontdoor123.azurefd.net left intact
```

Tak to byla pokročilá pravidla s Azure Front Door. Chytrý engine, který jednou nastavíte a on běží na 165 místech planety a vaši uživatelé se vždy pobaví s tím, co je jim nejblíž a on pak pro ně zvolí tu nejlepší cestu k backendu.
