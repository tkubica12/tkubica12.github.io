---
layout: post
published: true
title: Hybridní DNS jako služba v Azure
tags:
- Networking
---
Většina velkých zákazníků buduje hybridní prostředí, jehož součástí je i schopnost přes DNS adresovat z cloudu do onprem a naopak včetně například přístupu z onprem na platformní služby s využitím Private Endpoint. Azure poměrně dlouho podporuje privátní DNS domény, ale do nedávna tyto nepodporovaly DNS forwarding - klíčovou vlastnost pro hybridní nasazení. Nezbývalo tedy než provozovat vlastní DNS server ve vaší landing zone.

Jak může Azure DNS resolver řešit problém elegantněji? A zůstávají i nadále nějaké důvody k provozování vlastního DNS řešení?

# Azure DNS resolver
Tahle vlastnost v Azure opravdu dlouho chyběla a konečně je k dispozici v preview. Možná se ptáte proč proboha něco tak elementárního trvá. Možná, stejně jako v nastavení AWS a GCP, považujete řešení za nějak kostrbaté (inbound, outbound endpointy a podobné věci). Jde totiž o to, že interní DNS v cloudu není "server" jak je běžné v onprem. Představte si jaké masivní problémy se škálovatelností by mohly vzniknout. Dál vezměte v úvahu i dostupnost - 60 regionů, mnoho z nich ve třech zónách dostupnosti, do toho obrovské množství zákazníků. Cloudoví hráči proto distribuují tuto službu přímo do hostitele - na každém z milionů fyzických serverů běží DNS služba. Proto ta její záhadná IP - 168.63.129.16 v Azure, 169.254.169.253 v AWS a 169.254.169.254 v GCP. Je to (z pohledu fyzické sítě) lokálně signifikantní adresa - běží všude a jaké tabulky má použít si řeší multi-tenant způsobem (každá zákaznická Private DNS zóna má "link" do VNETu, což přináší unikátní identifikátor tenantu/VNETu). No a právě s tím je spojena ta komplexita. Na tuhle adresu nemůžete z onprem namířit svůj forwarding a ani vám z této adresy nemůže forwarding přicházet. Řešením je tedy vytvořit endpointy přímo v zákaznickém VNETu (v podstatě nějaké providerem plně spravovan8 VMka nebo kontejnery pro konkrétního zákazníka), přes které dokáže Azure DNS služba forwardovat requesty do onprem (outbound endpoint) a také inbound endpoint, na kterém služba bude reagovat na dotazy přeposlané z onprem či ze spoke sítí. Víceméně ke stejnému řešení doiterovaly všechny tři cloudy.

# Kdy může stále dávat smysl vlastní DNS řešení
Interní DNS v cloudu není nějaký superserver, kde se dá snadno roztodivně manipulovat s requesty. Nečekejte tedy od interní cloudové DNS, že bude kdovíjak chytrá. Tady je tedy pár důvodů, které jsem v praxi zaznamenal, kdy budete chtít i dál svůj vlastní DNS server v cloudu:
- V klasickém Windows světě možná chcete roztáhnout Windows DNS do cloudu se vším všudy - doménovým řadičem, DNS službami a celé to konfigurovat přes GPO. Taková varianta má určitě výhody v konsolidaci a v tom, že je to známé řešení - proč ho tedy nevyužít a nedat do landing zone páreček Windows Serverů?
- Některé instituce, zejména banky, mohou používat komplexní DNS servery se speciálními bezpečnostními funkcemi. Třeba tam dělají sledování dotazů pro prevenci DNS tunneling, využívají reputačních služeb (známé škodlivé FQDN typu command and control servery) nebo chtějí dělat blacklisting či detailní DNS monitoring. To jednoduchá služba Azure Private DNS aktuálně nenabídne.
- Některé firmy mají zapeklitá prostředí plná workaroundů po různých akvizicích a podobných událostech a používají třeba F5 jako DNS server, na kterém přes iRules vytváří velmi komplexní pravidla pro DNS doctoring. Tak například z historických důvodů používají interně public IP adresy, které nevlastní (ano - i to se vám v praxi může stát u velké mezinárodní firmy ... jistě se poznali, tak se omlouvám za použití jejich příkladu :)  ) a pokud DNS vrátí něco kolizního, nějak to řeší. Další možnost je, že jejich forwarding politiky jsou podstatně složitější, než běžné členění podle zón (např. potřebují v rámci jedné zóny, třeba mojedomena.cz, posílat dotazy na záznamy začínající písmenem "a" na jiný server, než ty ostatní - jestli se vám zdá divné, tak věřte, že pokud máte třeba 50 000 zaměstanců, tak se v průběhu 20 let takových podivností nastřádá docela dost).

Mimochodem když mluvím o vlastním serveru, mám na mysli server běžící v cloudu, nikoli, že cloud namíříme na onprem server. Tím si koledujeme o potíže se zátěží, latencí a dostupnost cloudu je pak závislá na VPN či Express Route propojení (množství aplikací, které běží v cloudu celé a přináší hodnotu uživatelům a zákazníkům i bez VPN, se bude z pohledu trendu určitě spíše zvyšovat, než naopak).

# Praktické nasazení hybridního řešení
Vyzkoušel jsem následující scénář a vše zabalil do Bicep šablony, kterou si můžete stáhnout a celé si to taky nasadit [tady](https://github.com/tkubica12/azure-workshops/tree/main/d-dns-resolver)

Postavíme si Azure Virtual WAN s hubem, jednu síť na sdílené služby (tam dáme DNS resolver) a jeden spoke. Onprem nasimulujeme v Azure jako další VNET a místo VPN ho jednoduše napeerujeme do services sítě. V každé síti vytvoříme po jednom VMku a také v onprem založíme DNS server, kde bude Bind9 (onprem DNS server v našem příkladu). V Azure si vytvoříme Private DNS zónu pro servery (azure.mydomain.demo) přiřazenou na všechny spoke sítě (aby se každé VM v této zóně samo registrovalo). Resolver bude přes outbound interface přeposílat dotazy na onprem zónu (onprem.mydomain.demo) a přes inbound interface na něj budou směrovat jak dotazy z onprem DNS serveru tak z jednotlivých spoke sítí (to proto, abychom měli centrálně řízené zóny pro Private Endpointy PaaS služeb a ty byly dostupné i z onprem).

Celkově to vypadá takhle:

[![](/images/2022/2022-05-23-15-40-23.png){:class="img-fluid"}](/images/2022/2022-05-23-15-40-23.png)

Po nasazení šablony můžeme omrknout GUI resolveru. Politiky směrují dotazy na onprem.mydomain.demo na IP adresu onprem DNS serveru (10.99.1.10)

[![](/images/2022/2022-05-23-15-32-14.png){:class="img-fluid"}](/images/2022/2022-05-23-15-32-14.png)

[![](/images/2022/2022-05-23-15-33-25.png){:class="img-fluid"}](/images/2022/2022-05-23-15-33-25.png)

Tady je instalace Bind9 v onprem. V zásadě velmi jednoduchá konfigurace - server drží záznamy pro onprem.mydomain.demo a do inbound DNS resolveru v Azure forwarduje dotazy na azure.mydomain.demo. 

```bash
az serial-console connect -n onpremDnsVm -g dns
sudo -i
apt install -y bind9

cat << EOF > /etc/bind/db.onprem
\$TTL 60
@            IN    SOA  localhost. root.localhost.  (
                          2015112501   ; serial
                          1h           ; refresh
                          30m          ; retry
                          1w           ; expiry
                          30m)         ; minimum
                   IN     NS    localhost.
localhost       A   127.0.0.1
onpremvm.onprem.mydomain.demo.   A       10.99.0.4
EOF

cat << EOF > /etc/bind/named.conf.options
options {
        directory "/var/cache/bind";

        listen-on port 53 { any; };
        allow-query { any; };
        recursion yes;

        auth-nxdomain no;    # conform to RFC1035
};
EOF

cat << EOF > /etc/bind/named.conf.local
// onprem zone
zone "onprem.mydomain.demo" {
  type master;
  file "/etc/bind/db.onprem";
};

// forward to our Azure DNS resolver for cloud domains
zone "azure.mydomain.demo" {
        type forward;
        forwarders {10.1.1.4;};
};
zone "privatelink.blob.core.windows.net" {
        type forward;
        forwarders {10.1.1.4;};
};
EOF

systemctl restart bind9
```

Z onprem, který používá onprem DNS server 10.99.1.10, se krásně dobouchám na cloudvm.azure.mydomain.demo i na Private Endpoint.

```bash
az serial-console connect -n onpremVm -g dns

tomas@onpremVm:~$ dig cloudvm.azure.mydomain.demo

;; ANSWER SECTION:
cloudvm.azure.mydomain.demo. 10 IN      A       10.1.0.4


tomas@onpremVm:~$ dig ydpzynlb3ydfi.blob.core.windows.net

;; ANSWER SECTION:
ydpzynlb3ydfi.blob.core.windows.net. 60 IN CNAME ydpzynlb3ydfi.privatelink.blob.core.windows.net.
ydpzynlb3ydfi.privatelink.blob.core.windows.net. 9 IN A 10.1.0.5
```

Stejně tak když půjdu ze Spoke sítě, která používá Azure DNS forwarder inbound interface jako DNS server, se dostanu jak do Azure privátních zón včetně Private Endpointu, tak do onpremvm.onprem.mydomain.demo, která žije na mém onprem DNS serveru.

```bash
az serial-console connect -n spokeVm -g dns

tomas@spokeVm:~$ dig onpremvm.onprem.mydomain.demo

;; ANSWER SECTION:
onpremvm.onprem.mydomain.demo. 60   IN      A       10.99.0.4


tomas@spokeVm:~$ dig ydpzynlb3ydfi.blob.core.windows.net

;; ANSWER SECTION:
ydpzynlb3ydfi.blob.core.windows.net. 60 IN CNAME ydpzynlb3ydfi.privatelink.blob.core.windows.net.
ydpzynlb3ydfi.privatelink.blob.core.windows.net. 9 IN A 10.1.0.5
```



Myslím, že řada zákazníků se na tuhle službu docela těšila, protože hybridní DNS potřebuje skoro každý. Jasně, pokud máte speciální požadavky na manipulaci s requesty, používáte nějaké super bezpečnostní řešení či detailní monitoring DNS, nebo prostě jen chcete mít ve všech prostředích centrálně spravovaný systém typu Windows DNS role, můžete používat i dál. Ale musíte se o to starat - řešit tomu vysokou dostupnost, patching, kdo má do serveru přístup a jaký ... tam kde to jde, bych raději Azure DNS resolver, ať nic z toho není můj problém.