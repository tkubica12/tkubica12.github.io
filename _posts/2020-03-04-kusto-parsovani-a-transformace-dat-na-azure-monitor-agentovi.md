---
layout: post
title: 'Kusto: Parsování a transformace dat na Azure Monitor agentovi'
tags:
- Kusto
- Monitoring
---
V minulém díle jsme si ukázali možnosti parsování a úpravy dat v okamžiku query. To má zásadní výhody, ale i nevýhody, a proto se dnes podíváme na druhou možnost - udělat to v agentovi blíže ke zdroji. V článku se zaměřím na Linux verzi, která se často používá nejen pro sběr ze serveru samotného (tak jak v případě Windows), ale často jako syslog agregátor pro sbírání logů z dalších systémů, síťových prvků a dalších zařízení.

Proč parsovat a transformovat v okamžiku query?
- Nemusíte se trápit s konfigurací agenta. Snadno vytvoříte další, v cloudu to bude doslova klikačka, v jiném prostředí jeden jednoduchý skript.
- Když se změní datový formát, nepřicházíte o data. Query vám sice možná vyhodí chybu (neexistující políčko apod.), ale data jsou uložena a opravením query se k nim lze vrátit. Pokud začne padat parsování na agentovi, data možná ani nedoručí.

Proč parsovat a transformovat přímo na agentovi?
- Možná váš systém generuje velké množství hlášek a dát je všechny do cloudu stojí peníze, ale nemůžete filtrovat jen na základě severity nebo facility apod. Zkrátka potřebujete sofistikovanější filtraci přímo na agentovi, třeba podle zdrojového systému, regexu nebo nějakého políčka v JSON.
- Data přijdou do Log Analytics už v cílové struktuře a přímo při ukládání se vhodně zaindexují, což následná query zjednoduší a zrychlí. Join třeba tří tabulek kdy každá je parsovaná v okamžiku query už je slušná zátěž a odpověď může trvat dost dlouho.

# Azure Monitor agent
Log Analytics agent (nebo také OMS agent, Azure Monitor agent - název se různě mění) je Linux komponenta, která na pozadí využívá Fluentd pro sběr logů a Collectd pro shromažďování telemetrie a bezpečným způsobem je odesílá do cloudu. Součástí je automatická aktualizace a agent některá svá nastavení může přijímat na základě konfigurace v Azure (například custom logy ze souboru, nastavení které severity a facility sbírat). Kromě toho se přes agent napojují další řešení jako je sběr detailů síťové komunikace (dependency agent) a tak podobně.

## Základní nasazení
Instalaci agenta a jeho napojení vyřeším v případě Azure VM přímo v GUI Log Analytics, ale i pro on-premises mašinu je to velmi jednoduché spuštění jednoho skriptu.

![](/images/2020/2020-02-11-20-22-24.png){:class="img-fluid"}

![](/images/2020/2020-02-11-20-23-08.png){:class="img-fluid"}

Agenty můžeme z pohledu nastavení severity sbírání a facility konfigurovat buď centrálně nebo ručně. Pro zjednodušení použiji centrální nastavení.

![](/images/2020/2020-02-11-20-26-02.png){:class="img-fluid"}

![](/images/2020/2020-02-11-20-26-29.png){:class="img-fluid"}

Následně se připojím do VM a vygeneruji syslog zprávu.

```bash
logger -p syslog.info Nazdar Azure!
```

Tu bych měl nalézt v Log Analytics.

![](/images/2020/2020-02-11-21-02-13.png){:class="img-fluid"}

## Jak to funguje
Mějme tento formát zprávy a pošleme ho do syslogu.

```bash
logger -p syslog.info alert=underAttack srcip=1.1.1.1 dstip=9.9.9.9 srcport=54223 dstport=80
logger -p syslog.info alert=justLogging srcip=1.1.1.2 dstip=9.9.9.9 srcport=55666 dstport=80
```

V Azure Monitor mám samozřejmě obě dvě.

![](/images/2020/2020-02-12-08-30-16.png){:class="img-fluid"}

Pojďme teď začít filtrovat na straně agenta. První co chci udělat je vypnout automatickou konfiguraci agenta z GUI, abych měl jistotu, že mi nic nebude měnit.

```bash
sudo su omsagent -c 'python /opt/microsoft/omsconfig/Scripts/OMS_MetaConfigHelper.py --disable'
```

Konfigurace agenta najdeme na cestě /etc/opt/microsoft/omsagend/cisloworkspace/conf a tam bude soubor omsagent.conf se základní konfigurací. V ní vidíme match záznamy, které zachytávají výsledek zpracování a konkrétně tento odesílá naše syslog hlášky:

```
<match oms.** docker.**>
  type out_oms
  log_level info
  num_threads 5
  run_in_background false

  omsadmin_conf_path /etc/opt/microsoft/omsagent/4e9c0d3b-fb64-496d-a699-2c80896616b1/conf/omsadmin.conf
  cert_path /etc/opt/microsoft/omsagent/4e9c0d3b-fb64-496d-a699-2c80896616b1/certs/oms.crt
  key_path /etc/opt/microsoft/omsagent/4e9c0d3b-fb64-496d-a699-2c80896616b1/certs/oms.key

  buffer_chunk_limit 15m
  buffer_type file
  buffer_path /var/opt/microsoft/omsagent/4e9c0d3b-fb64-496d-a699-2c80896616b1/state/out_oms_common*.buffer

  buffer_queue_limit 10
  buffer_queue_full_action drop_oldest_chunk
  flush_interval 20s
  retry_limit 10
  retry_wait 30s
  max_retry_wait 9m
</match>
```

Jak se tam dostanou? Match zachycuje tag oms.cokoli a ten se syslogem je konfigurovaný v souboru omsagent.d/syslog.conf:

```
<source>
  type syslog
  port 25224
  bind 127.0.0.1
  protocol_type udp
  tag oms.syslog
</source>

<filter oms.syslog.**>
  type filter_syslog
</filter>
```

No vida - posloucháme na podivném portu 25244 na loopback adrese a nabíráme to s tagem oms.syslog a následně využíváme nějaký připravený filtr s názvem filter_syslog (k tomu se za chvilku vrátíme). Ale kdo to ta tento podivný port vlastně posílá? K tomu se musíme podívat na rsyslog nastavení a konkrétně do souboru /etc/rsyslog.d/95-omsagent.conf:

```
syslog.=alert;syslog.=crit;syslog.=debug;syslog.=emerg;syslog.=err;syslog.=info;syslog.=notice;syslog.=warning @127.0.0.1:25224
```

Není vám to povědomé? Tohle je to nastavení, co jsme udělali v GUI. Zapnulo se sbírání hlášek facility syslog ve všech severitách a rsyslog je přesměrovává na loopback a port 25224 a právě na něm poslouhcá fluentd a potažo OMS agent. Takhle to tedy celé funguje a díky tomu můžeme využít plejádu dalších vlastností fluentd včetně jiných zdrojů (třeba tail souborů, API volání někam jinam třeba na /stats nějakého reverse proxy apod.), filtrací, parsování a transformací.

## Vlastní tabulka
Nejprve si začneme tyto informace posílat do separátní tabulky. Nebudeme nějak složitě selectovat zprávy (ale mohli bychom), prostě syslog budeme brát celý, jen ho pošleme do jiné tabulky (například scénář, kdy je tento agent určen výhradně ke sbírání logů z konkrétního firewallu). V souboru syslog nejprve změníme tagování z oms.syslog na oms.api.tomas.

syslog.conf tedy aktuálně bude vypadat takhle:

```
<source>
  type syslog
  port 25224
  bind 127.0.0.1
  protocol_type udp
  tag oms.api.tomas
</source>
```

Tím si hlášky ze syslogu tagujeme jinak a dáváme je do namespace api. Teď budeme potřebovat upravit match sekci v omsagent.conf a protože si chceme ukázat jednoduchou cestu, zmodifikujeme existující match. V sekci oms.** uděláme jednu drobnou, ale důležitou změnu. Type změníme z out_oms na out_oms_api. To způsobí, že místo do standardní tabulky bude agent data posílat do tabulky, jejíž název bude odpovídat tagu s přidaným _CL, tedy v mém případě očekávám vznik tabulky tomas_CL.

```
<match oms.** docker.**>
  type out_oms_api
  ...
</match>
```

Restartujeme agenta a zkusíme poslat nějaké zprávy. Protože se automaticky vytvoří nová tabulka, může i 10 minut trvat, než se to v GUI projeví (vytváří se nová struktura, indexy - pak už to bude podstatně rychlejší).

```bash
sudo /opt/microsoft/omsagent/bin/service_control restart
logger -p syslog.info alert=underAttack srcip=1.1.1.1 dstip=9.9.9.9 srcport=54223 dstport=80
logger -p syslog.info alert=justLogging srcip=1.1.1.2 dstip=9.9.9.9 srcport=55666 dstport=80
```

![](/images/2020/2020-02-13-08-37-36.png){:class="img-fluid"}

![](/images/2020/2020-02-13-08-38-10.png){:class="img-fluid"}

Log Analytics získalo data a vytvořilo příslušné zaindexované sloupečky, jejichž název je původní název, podtržítko a identitikovaný typ (například s jako string). Výborně, vlastní tabulku máme a můžeme pokračovat.

## Parsování v agentovi
Agent nám aktuálně posílá data do separátní tabulky a to ve struktuře host, identita, čas apod. a pak message jako řetězec. Nicméně v mých zprávách je jasná struktura a pojďme ji teď vyřešit přímo v agentovi a posílat strukturovaně. Na tomto místě poznámka - budu dělat, jakože jiné hlášky mi sem nechodí. Pokud by tomu tak bylo, museli bychom přes selektory přiřazovat různé tagy různým typům hlášek a zpracovávat je filter pravidly každé jinak. Jde to, ale my dnes zkoušíme jednoduchý scénář, kdy náš agent má na starost sběr jen jednoho typu dat třeba z firewallu.

Soubor syslog.conf obohatíme o parse funkci, která bude reagovat na políčko message a použije regex. O něm se dočtete na mnoho místech v Internetu, takže nebudu vysvětlovat moc detailů, jen zmíním, že je to nesmírně mocný nástroj. My z něj zas tak moc nevyužijeme. Potřebujeme zachytit jednotlivá data a využít pojmenované groups, které budou znamenat vznik sloupečků tohoto jména.

Doporučuji si to nejprve odladit na nějakém online editoru. Došel jsem k tomuto regulárnímu výrazu:

```
.*alert=(?<alert>.*?)\s.*srcip=(?<srcip>.*?)\s.*dstip=(?<dstip>.*?)\s.*srcport=(?<srcport>.*?)\s.*dstport=(?<dstport>.*?)$
```

![](/images/2020/2020-02-13-08-49-34.png){:class="img-fluid"}

V kostce jak to funguje:
1. Najdi alert=
2. To co následuje bude to, co chceme vytáhnout (to dělají závorky) a pojmenovat alert (to dělají zobáčky)
3. Hledáme jakýkoli znak (tečka) libovolněkrát (hvězdička)
4. Dál v pořadí hledáme mezeru, ale ta už je mimo group (tu nechceme zachytit). Potřebujeme ale najít právě první v pořadí (to říká otazník) a mezera se zapisuje \s
5. Pak necháme libovolné znaky libovolněkrát (ačkoli je to vlastně zbytečné)
6. Zachytíme srcip
7. Zachytíme srcport
8. Zachytíme dstport, ale ten je poslední, takže na konci už nebude mezera, ale konec zprávy (dolar)

Rexex máme, hodíme si do syslog.conf. Bude to sekce filter typu parser a format je náš regex uzavřený do dopředných lomítek.

```
<source>
  type syslog
  port 25224
  bind 127.0.0.1
  protocol_type udp
  tag oms.api.tomas
</source>

<filter oms.api.**>
  @type parser
  key_name message
  format /.*alert=(?<alert>.*?)\s.*srcip=(?<srcip>.*?)\s.*dstip=(?<dstip>.*?)\s.*srcport=(?<srcport>.*?)\s.*dstport=(?<dstport>.*?)$/
</filter>
```

Restartujeme agenta a zkusíme poslat nějaké zprávy.

```bash
sudo /opt/microsoft/omsagent/bin/service_control restart
logger -p syslog.info alert=underAttack srcip=2.1.1.1 dstip=9.9.9.9 srcport=54223 dstport=80
logger -p syslog.info alert=justLogging srcip=2.1.1.2 dstip=9.9.9.9 srcport=55666 dstport=80
```

![](/images/2020/2020-02-13-09-09-08.png){:class="img-fluid"}

## Filtrování
Dejme tomu, že nechceme posílat jiné alerty, než underAttack. Můžeme přidat so syslog.conf další fázi filtrace.

```
<source>
  type syslog
  port 25224
  bind 127.0.0.1
  protocol_type udp
  tag oms.api.tomas
</source>

<filter oms.api.**>
  @type parser
  key_name message
  format /.*alert=(?<alert>.*?)\s.*srcip=(?<srcip>.*?)\s.*dstip=(?<dstip>.*?)\s.*srcport=(?<srcport>.*?)\s.*dstport=(?<dstport>.*?)$/
</filter>


<filter oms.api.**>
  @type grep
  <regexp>
    key alert
    pattern underAttack
  </regexp>
</filter>
```

Restartujeme službu a zkusíme tam posla pár hlášek.

```bash
sudo /opt/microsoft/omsagent/bin/service_control restart
logger -p syslog.info alert=underAttack srcip=2.1.1.1 dstip=9.9.9.9 srcport=54223 dstport=80
logger -p syslog.info alert=justLogging srcip=2.1.1.2 dstip=9.9.9.9 srcport=55666 dstport=80
logger -p syslog.info alert=underAttack srcip=3.1.1.1 dstip=9.9.9.9 srcport=54223 dstport=80
logger -p syslog.info alert=justLogging srcip=3.1.1.2 dstip=9.9.9.9 srcport=55666 dstport=80
logger -p syslog.info alert=underAttack srcip=4.1.1.1 dstip=9.9.9.9 srcport=54223 dstport=80
logger -p syslog.info alert=justLogging srcip=4.1.1.2 dstip=9.9.9.9 srcport=55666 dstport=80
```

Povedlo se, už vidíme jen ty underAttack.

![](/images/2020/2020-02-13-14-37-31.png){:class="img-fluid"}

# Další možnosti s fluentd
Fluentd je poměrně mocný nástroj a nechci jít do dalších podrobností, ostatně ani je nemám vyzkoušené. Ale možná zmiňme pár dalších zajímavostí:
- Existuje zdroj typu exec, tedy spouštění nějakého příkazu nebo skriptu a posílání výsledků dál - tak například můžete přes curl sbírat data z nějakého endpointu
- Fluentd může poslouchat na nějakém portu a přijímat třeba JSON data
- Obsahuje parsery na formáty tyu JSON nebo CSV
- Má zajímavé pluginy, které například dokáží detekovat multi-line exceptions a smontovat je do jediné hlášky (to je klasický problém výjimek aplikace, které do logu napíšu callstack a mají to odřádkované, což se pak objeví jako jednotlivé hlášky)
- Vstupem může být tail, tedy hlášky, které zapisuje aplikace do souboru. K tomu nemusíte dělat nastavení ručně, je na to podpora přímo v Azure portálu (custom log) a ta vám konfiguraci umí vygenerovat.

JSON parser jsem například použil pro integraci ESET bezpečnostního centra do Azure Sentinel: [https://github.com/tkubica12/eset-smc-azure-sentinel](https://github.com/tkubica12/eset-smc-azure-sentinel)


# Alternativní možnosti
Bez dalších detailů zmíním, že jsou i další možnosti jak data dostat do Azure Monitor:
- Existuje output plugin do Logstash, takže pokud jedete v něm (například protože máte zmáknutý ELK stack), může to být dobrá cesta [https://github.com/yokawasa/logstash-output-azure_loganalytics](https://github.com/yokawasa/logstash-output-azure_loganalytics)
- Další možnost je Logic App konektor. Díky němu můžeme naklikat workflow pro získání dat, zpracování a export do Azure Monitor. Tak například můžete ze systému odesílat logy jako soubor na Azure Files share a mít Logic App, která pravidelně kontroluje nové soubory a ty zpracuje, odešle do Azure Monitor a vyčistí. Konektor je popsaný zde: [https://docs.microsoft.com/en-us/connectors/azureloganalyticsdatacollector/](https://docs.microsoft.com/en-us/connectors/azureloganalyticsdatacollector/)
- API také můžeme používat napřímo, třeba PowerShell skriptem jste schopni vzít nějaká data a odeslat je do Azure Monitor nebo začlenit přímo do vaší aplikace (pro tyto účely bych ale preferoval SDK Application Insights - nicméně třeba nejde o aplikaci v pravém slova smyslu, ale spíš nějakou utilitku, skript, ETL platformu apod.)

