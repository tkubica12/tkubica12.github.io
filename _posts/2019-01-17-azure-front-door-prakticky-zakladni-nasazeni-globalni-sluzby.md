---
layout: post
status: publish
published: true
title: Azure Front Door prakticky - základní nasazení globální služby
tags:
- FrontDoor
- Networking
---
V minulém díle jsme se teoreticky seznámili s Azure Front Door Service a dnes už si ji vyzkoušíme prakticky. Začneme z nejjednodušších věcí a prozkoumáme jak to funguje. Na pokročilé záležitosti se podíváme zas příště.

# Připravíme si aplikaci
Po dnešní jednoduchý test potřebuji webovku v Evropě a USA. Nechce se mi dělat VM, připojovat se do ní a tak podobně. Současně nepotřebuji nějaké pokročilé aplikační řešení typu Application Service. Nejsnazší bude využít Azure Container Instances a jedním příkazem pustit a vybudovat primitivní web server.

```bash
az group create -n frontdoor -l westeurope
az container create -g frontdoor \
    --name myapp-eu \
    -l westeurope \
    --image ubuntu:latest \
    --ports 80 \
    --dns-name-label tomkubica123-eu \
    --command-line "bash -c 'apt update && apt install apache2 -y && echo westeurope > /var/www/html/index.html && service apache2 start && sleep infinity'"


az container create -g frontdoor \
    --name myapp-us \
    -l westus2 \
    --image ubuntu:latest \
    --ports 80 \
    --dns-name-label tomkubica123-us \
    --command-line "bash -c 'apt update && apt install apache2 -y && echo westus2 > /var/www/html/index.html && service apache2 start && sleep infinity'"
```

Vyzkoušejte, že aplikace nám naběhly a vrací buď westeurope nebo westus2.

```bash
curl tomkubica123-eu.westeurope.azurecontainer.io
curl tomkubica123-us.westus2.azurecontainer.io
```

# Nasadíme Azure Front Door
Pro dnešek si nasadíme Azure Front Door přes GUI. 

![](/images/2018/2018-12-29-09-47-41.png){:class="img-fluid"}

Čeká nás pěkný průvodce. Neprve vytvoříme frontend, tedy endpoint pro naše dveře.

![](/images/2018/2018-12-29-09-48-43.png){:class="img-fluid"}

Dám mu nějaké unikátní jméno zapnu cookie session perzistenci. Později samozřejmě budeme moci přidat i svou doménu.

![](/images/2018/2018-12-29-09-50-17.png){:class="img-fluid"}

Přidáme backend pool.

![](/images/2018/2018-12-29-09-51-18.png){:class="img-fluid"}

![](/images/2018/2018-12-29-09-52-10.png){:class="img-fluid"}

Přidáme první kontejner.

![](/images/2018/2018-12-29-09-53-12.png){:class="img-fluid"}

A druhý taky.

![](/images/2018/2018-12-29-09-53-56.png){:class="img-fluid"}

Výchozí nastavení health probe mi vyhovuje.

![](/images/2018/2018-12-29-09-54-44.png){:class="img-fluid"}

Nastavení balancování také nechám v defaultu. Důležitá je tolerance na rozdíly v latenci. Pokud je tam 0 ms, Front Door pošle uživatele na aktuálně nejrychlejší node. To je v mém případě to pravé, protože mám v každém regionu jen jednu instanci (nebo bych měl svůj balancovací mechanismus na úrovni regionu, třeba AKS nebo VMka s load balancerem). Pokud bych chtěl z Front Door adresovat přímo jednotlivé instance ve vícero počtech v jednom regionu nastavil bych tady nějakou toleranci. Tzn. odpověď za 20 ms a 22 ms bude brána jako totéž, pokud použiji třeba toleranci 5 ms. 

![](/images/2018/2018-12-29-09-57-55.png){:class="img-fluid"}

Jdeme do finále. Přidáme si směrovací pravidla.

![](/images/2018/2018-12-29-09-58-41.png){:class="img-fluid"}

Přidám jednoduché pravidlo směrující provoz na můj pool.

![](/images/2018/2018-12-29-10-00-23.png){:class="img-fluid"}

Protože moje aplikace běží jen na HTTP, přepnu se do Advanced záložky a řeknu, že na backend bude Front Door mluvit pouze přes HTTP.

![](/images/2018/2018-12-29-10-01-17.png){:class="img-fluid"}

Průvodce je opravdu šikovný. Odklepneme a podíváme se na výsledek.

# Vyzkoušíme z Prahy i z US
Nejprve vyzkouším přístup na službu ze svého počítače v Praze.

```bash
$ curl https://tomasapp.azurefd.net
westeurope
```

Dle očekávání odpovídá westeurope. Pojďme se ale mrknout na víc detailů.

```bash
$ curl -v https://tomasapp.azurefd.net
* Rebuilt URL to: https://tomasapp.azurefd.net/
*   Trying 2620:1ec:bdf::10...
* TCP_NODELAY set
* Connected to tomasapp.azurefd.net (2620:1ec:bdf::10) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
* successfully set certificate verify locations:
*   CAfile: /etc/ssl/certs/ca-certificates.crt
  CApath: /etc/ssl/certs
* TLSv1.2 (OUT), TLS handshake, Client hello (1):
...
* ALPN, server accepted to use h2
* Server certificate:
*  subject: CN=*.azurefd.net
*  start date: Aug  9 18:40:53 2018 GMT
*  expire date: Aug  9 18:40:53 2020 GMT
*  subjectAltName: host "tomasapp.azurefd.net" matched cert's "*.azurefd.net"
*  issuer: C=US; ST=Washington; L=Redmond; O=Microsoft Corporation; OU=Microsoft IT; CN=Microsoft IT TLS CA 5
*  SSL certificate verify ok.
* Using HTTP2, server supports multi-use
* Connection state changed (HTTP/2 confirmed)
* Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
* Using Stream ID: 1 (easy handle 0x7ffff6df78e0)
> GET / HTTP/2
> Host: tomasapp.azurefd.net
> User-Agent: curl/7.58.0
> Accept: */*
>
* Connection state changed (MAX_CONCURRENT_STREAMS updated)!
< HTTP/2 200
< content-length: 11
< content-type: text/html
< last-modified: Sat, 29 Dec 2018 08:43:53 GMT
< accept-ranges: bytes
< etag: "b-57e252df5f047"
< x-ms-ref: 0hj8nXAAAAAA73Sp3FCoGSpTKT5wouQxoUFJHMDFFREdFMDQxNgA2YzczMWQ4MS02YTdmLTRlNmMtYjVjMC0yMzkxYjIxOGM4Mzk=
< date: Sat, 29 Dec 2018 09:33:57 GMT
<
westeurope
* Connection #0 to host tomasapp.azurefd.net left intact
```

Všimněte si následujícíh věcí. Moje stanice podporuje IPv6 a můj přístup na službu byl právě přes IPv6. Provoz je šifrovaný s TLS 1.2 přestože moje aplikace v kontejneru to nepodporuje. A také je použit protokol HTTP/2, který je velmi efektivní, a který samozřejmě můj kontejner také nepodporuje. Hodně práce tedy Front Door udělal za mne. Nicméně pokud klient nepodporuje, v pohodě to půjde přes HTTP 1.1 a IPv4:

```bash
$ curl -4 --http1.1 https://tomasapp.azurefd.net
westeurope
```

Podívejme se na jakou IP se připojujeme

```bash
$ dig tomasapp.azurefd.net

...
;; ANSWER SECTION:
tomasapp.azurefd.net.   1642    IN      CNAME   t-0001.t-msedge.net.
t-0001.t-msedge.net.    20      IN      CNAME   Edge-Prod-VIEr3.ctrl.t-0001.t-msedge.net.
Edge-Prod-VIEr3.ctrl.t-0001.t-msedge.net. 93 IN CNAME standard.t-0001.t-msedge.net.
standard.t-0001.t-msedge.net. 200 IN    A       13.107.246.10
...
```

Vyzkoušejme časy navázání TCP session, ať si ukážeme, že je skutečně terminována někde blíže, něž v Amsterdamu.

```bash
$ curl -w "Connect: %{time_connect} \n" http://tomasapp.azurefd.net
westeurope
Connect: 0.045188

$ curl -w "Connect: %{time_connect} \n" http://tomkubica123-eu.westeurope.azurecontainer.io
westeurope
Connect: 0.062140

$ curl -w "Connect: %{time_connect} \n" http://tomkubica123-us.westus2.azurecontainer.io
westus2
Connect: 0.254997
```

Vyzkoušejme teď jak by to vypadalo pro uživatele někde v US. Jeden z uzlů mi běží ve westus2, zkusím si tedy udělat "stanici" v centralus. Použijeme kontejner, to bude nejrychleji hotové. Až bude připraven, skočíme do jeho CLI.

```bash
az container create -g frontdoor \
    --name test-us \
    -l centralus \
    --image ubuntu:latest \
    --command-line "bash -c 'apt update && apt install curl dnsutils -y && sleep infinity'"

az container exec -g frontdoor --name test-us --exec-command "/bin/bash"
root@wk-caas-969b682f48844dea96f4f6ebddbc002d-14eae09b40c79031e18400:/#
```

Zopakujme předchozí testy. Všimněte si, že Front Door pro nás jako nejbližší instanci našel tu ve westus2. Znovu si ověříme, že Front Door je asi někde blíž, protože časy sestavení TCP jsou u Front Door lepší, než napřímo.

Odpověď dostáváme z westus2.

```bash
curl https://tomasapp.azurefd.net
westus2
```

Co se doby sestavení spojení týče, evidentně je Front Door opět někde blízko.

```bash
$ curl -w "Connect: %{time_connect} \n" http://tomasapp.azurefd.net
westus2
Connect: 0.018637

$ curl -w "Connect: %{time_connect} \n" http://tomkubica123-us.westus2.azurecontainer.io
westus2
Connect: 0.046173

$ curl -w "Connect: %{time_connect} \n" http://tomkubica123-eu.westeurope.azurecontainer.io
westeurope
Connect: 0.123466
```

Zajímavé bude podívat se na IP adresu. Všimněte si, že je stejná jako u přístupu z Prahy! Front Door totiž používá anycast.

```bash
dig tomasapp.azurefd.net
;; ANSWER SECTION:
tomasapp.azurefd.net.   1561    IN      CNAME   t-0001.t-msedge.net.
t-0001.t-msedge.net.    59      IN      CNAME   Edge-Prod-DALr3.ctrl.t-0001.t-msedge.net.
Edge-Prod-DALr3.ctrl.t-0001.t-msedge.net. 0 IN CNAME standard.t-0001.t-msedge.net.
standard.t-0001.t-msedge.net. 0 IN      A       13.107.246.10
```

Výborně. Funguje to krásně. V dalších dílech se podíváme trochu blíž na to jak se drží session, jak dělat pokročilejší URL rewrite pravidla nebo jak Front Door řeší caching statického obsahu.