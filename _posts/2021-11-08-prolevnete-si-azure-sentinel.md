---
layout: post
published: true
title: Prolevněte si Azure Sentinel s Fluent Bit, Blobem a Azure Data Explorer
tags:
- Security
- Monitoring
---
Kritické bezpečnostní informace je ideální sbírat do Azure Sentinel, SIEM řešení nové generace zrozené v cloudu. Ať už jde o bezpečnostní logy, detekované anomálie a incidenty z různých nástrojů, podezřelá přihlášení a tak podobně - to všechno je skvělé mít v jedné analytické platformě a nad tím provádět v téměř reálném čase analýzu, automatickou reakci, strojové učení, detekci anomálií, normalizaci dat, korelaci událostí nebo sestavovat profil chování uživatele či zařízení. Pak jsou ale ještě logy, které jsou obrovské, velmi detailní, ale pro SIEM nástroj zbytečně drahé. Je určitě výborné mít nejenom bloknuté komunikace ze sítě, ale i přehled o statistikách všech session na všech místech sítě. Je fajn mít nejen seznam EDR systémem zablokovaných uživatelských akcí na jeho notebooku, ale ukládat i list všech akcí. Je nepochybně přínosné mít v SIEM záznamy o nebezpečných událostech ve světě Office 365 jako je nastavování práv, mazání schránek a týmů, zvaní třetích stran, ale někdy nemusí být špatné i vědět kdo s kým měl Teams hovor a jak dlouho trval. Problém je, že zatímco ty první části vět jsou přímočaré co do jejich bezpečnostní hodnoty, tak ty druhé jsou spíše data vhodná pro forezní audit, dokazování a post mortem. Ale hlavně - dat druhého typu bývá o řád víc. Mám tedy data, která nemá smysl near-real-time analyzovat s rychlým přístupem, spíše je potřebuji někde odložit a párkrát do roka se do některých z nich podívám. Dát je tedy všechny přímo do Azure Sentinel nemusí být optimální z hlediska poměru ceny a přínosu.

# Levné úložiště s možností hydratace do analytické databáze pod Azure Sentinel
Co kdybychom tedy kritické bezpečnostní informace posílali do Sentinel na vyhodnocení, ale podrobné nízkoúrovňové věci pro forenzní část ukládali co nejlevněji, tedy do Azure Blob storage? Pak musíme vyřešit dvě otázky - jak data do blobů dostat a jak získat schopnost se na ně dotazovat stejným analytickým způsobem jako v Azure Sentinel.

## Fluent Bit jako cesta do Blobu
Psát si vlastní skripty na přenášení věcí do blobů se mi rozhodně nechce. Zkoumal jsem tedy hotová řešení pro přijímání a odesílání logů a telemetrie - FluentD a Logstash. Oba jsou "velké" robustní projekty s hromadou konektorů, ale přímá podpora Microsoftu tam nebyla zas tak aktivní. Pak jsem se zaměřil na minimalistické alternativy (super tenké nástroje vhodné i jako sidecar do Podu v Kubernetu) / doplňky (dají se použít jako zdroje pro dříve zmíněné velké brášky) - Fluent Bit a Beats. Pro Fluent Bit přímo Microsoft napsal konektor na bloby i Log Analytics. Fluent Bit je prťavý - má zhruba o dva řády menší spotřebu paměti, než FluentD nebo Logstash díky tomu, že je dost holý a napsaný v C++ (na rozdíl od Ruby použitého ve FluentD).

Scénář, který jsem chtěl prozkoumat je integrace klasického syslogu. Tedy chci, aby kolektor poslouchal jako syslog server a co mu přijde posílal do blobu. To je ideální třeba pro logy ze síťových prvků nebo pro napojení na stávající agregační syslog, který by to sem přeposílal. Vstupních pluginů má Fluent Bit samozřejmě víc - třeba metriky z CollectD a StatsD, zprávy z MQTT, tail souboru nebo žurnál ze Systemd. Má i věci jako obohacovadlo Kubernetes, filtrace, Lua, multiline skládání (typicky třeba pro víceřádkové exceptions z aplikace). 

## Z Blobu do analytiky s Kusto jazykem
V druhém kroku chci mít schopnost použít Kusto - mocný analytický jazyk, na kterém je postaven Azure Sentinel, Azure Monitor i hunting v naprosté většině Microsoft Defender produktů. Napadají mě tři varianty použití:
- Blob můžu připojit jako externí tabulku přímo z Log Analytics workspace nebo z vlastního Azure Data Explorer clusteru. Takové připojení bude samozřejmě hodně pomalé, ale na druhou stranu okamžitě k dispozici. Bude ideální, pokud mám nějaký relativně malý konkrétní blob, ve kterém potřebuji něco parsovat a najít.
- Ad-hoc vytvoření Azure Data Explorer clusteru a ingesting potřebných dat. Data mi tedy leží na levné blob storage a pokud potřebuji něco vyšetřit nebo vyfiltrovat pro policii, nahodím ADX (Azure Data Explorer) cluster a spustím nacucnutí dat (a půjdu se vyspat). Ráno budu mít všechna data krásně zavlažená - živá s možností rychlé analytiky, zkoumání, hraní si. Až získám co potřebuji, tak to po pár dnech smažu - náklady udržím krásně pod kontrolou. K ADX můžu přistupovat i ze Sentinel UI i psát Kusto query kombinující obě úložiště (dělat joiny a další operace).
- Mohl bych nechat ADX vytvořený trvale a automaticky ho nechat dososávat data průběžně. Proč to pak vůbec řešit a nemít úplně všechno v Sentinelu a jeho Log Analytics workspace? Ten je optimalizovaný na aktivní použití a časté dotazy - hodně výpočetní výkonu, velké a rychle cache atd. Váš ADX můžete postavit s jinou strategií - narvat tam co nejvíc dat, ale s minimální cache i compute výkonem. Výsledek nebude vhodný na to, co dělá Sentinel (pravidelné masivní analytické dotazy pro detekci anomálií a vytváření incidentů), ale dostatečný na dohledání konkrétních dat, po kterých jdete. Pohrajte si s [kalkulačkou](https://dataexplorer.azure.com/AzureDataExplorerCostEstimator.html)  - dejte hot data jen na jeden den a uvidíte jak příjemně to vyjde. 

## Praktická zkouška
Vytvořme si VM.

```bash
az group create -n fluentbit -l westeurope
az network nsg create -n fluentbit -g fluentbit 
az network nsg rule create -n ssh -g fluentbit --nsg-name fluentbit --priority 120 --source-address-prefixes $(curl ifconfig.io) --destination-port-ranges 22 
az vm create -n fluentbit \
    -g fluentbit \
    --image Canonical:0001-com-ubuntu-server-focal:20_04-lts:latest \
    --size Standard_B1s \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --nsg fluentbit \
    --public-ip-address fluentbit
```

Dále potřebujeme storage account.

```bash
echo storageName=tomstorage$RANDOM > .env
source .env
az storage account create -n $storageName -g fluentbit --sku Standard_LRS
echo storageKey=$(az storage account keys list -n $storageName -g fluentbit --query [0].value -o tsv) >> .env
scp .env tomas@$(az network public-ip show -n fluentbit -g fluentbit --query ipAddress -o tsv):
```

Připojím se do VM, nainstaluji a zprovozním Fluent Bit.

```bash
ssh tomas@$(az network public-ip show -n fluentbit -g fluentbit --query ipAddress -o tsv)
source .env
wget -qO - https://packages.fluentbit.io/fluentbit.key | sudo apt-key add -
echo deb https://packages.fluentbit.io/ubuntu/focal focal main | sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get install td-agent-bit -y
cat << EOF > td-agent-bit.conf 
[SERVICE]
    flush     1
    log_level info
    Parsers_File parsers.conf

[INPUT]
    Name     syslog
    Parser   syslog-rfc5424
    Listen   0.0.0.0
    Port     514
    Mode     udp

[OUTPUT]
    name                  azure_blob
    match                 *
    account_name          $storageName
    shared_key            $storageKey
    path                  collector1
    container_name        logs
    auto_create_container on
    tls                   on
EOF
    
sudo mv ./td-agent-bit.conf /etc/td-agent-bit/
sudo service td-agent-bit restart
sudo service td-agent-bit status
```

Pojďme vygenerovat pár syslog zpráv - dost podobných tomu, co se objevuje u firewallů a síťových prvků.

```bash
ssh tomas@$(az network public-ip show -n fluentbit -g fluentbit --query ipAddress -o tsv)
logger -n 127.0.0.1 srcIp=1.2.3.4 dstIp=5.4.3.2 dstPort=80 action=allow
logger -n 127.0.0.1 srcIp=1.2.3.4 dstIp=5.4.3.2 dstPort=8080 action=deny
logger -n 127.0.0.1 srcIp=2.2.3.4 dstIp=5.4.3.2 dstPort=443 action=allow
logger -n 127.0.0.1 srcIp=2.2.3.4 dstIp=5.4.3.2 dstPort=88 action=allow
logger -n 127.0.0.1 srcIp=3.2.3.4 dstIp=5.4.3.2 dstPort=80 action=allow
logger -n 127.0.0.1 srcIp=3.2.3.4 dstIp=5.4.3.2 dstPort=443 action=allow
logger -n 127.0.0.1 srcIp=1.2.3.4 dstIp=9.4.3.2 dstPort=3389 action=deny
logger -n 127.0.0.1 srcIp=1.2.3.4 dstIp=9.4.3.2 dstPort=443 action=allow
logger -n 127.0.0.1 srcIp=1.2.3.4 dstIp=9.4.3.2 dstPort=80 action=deny
```

Můžete se přesvědčit, že jsou data v blobu. Pojďme teď vytvořit Azure Data Explorer cluster a databázi.

```bash
az extension add -n kusto
az kusto cluster create -n tomasadx123 -g fluentbit --sku name="Dev(No SLA)_Standard_E2a_v4" capacity=1 tier="Basic" --public-network-access "Enabled"
az kusto database create --cluster-name tomasadx123 --database-name mydb -g fluentbit --read-write-database soft-delete-period=P365D hot-cache-period=P31D location=westeurope
```

Nejprve zkusíme napojit jako externí tabulku.

[![](/images/2021/2021-11-03-14-13-30.png){:class="img-fluid"}](/images/2021/2021-11-03-14-13-30.png)

Zvolím jméno.

[![](/images/2021/2021-11-03-18-48-59.png){:class="img-fluid"}](/images/2021/2021-11-03-18-48-59.png)

Na storage accountu vygeneruji SAS URL s právy Read a List.

[![](/images/2021/2021-11-03-18-50-49.png){:class="img-fluid"}](/images/2021/2021-11-03-18-50-49.png)

Přidám jako zdroj.

[![](/images/2021/2021-11-03-18-51-23.png){:class="img-fluid"}](/images/2021/2021-11-03-18-51-23.png)

Zvolím formát JSON.

[![](/images/2021/2021-11-03-18-52-07.png){:class="img-fluid"}](/images/2021/2021-11-03-18-52-07.png)

Udělám pár modifikací scématu - smažu @timestamp sloupeček (máme tam time, to stačí).

[![](/images/2021/2021-11-03-18-54-17.png){:class="img-fluid"}](/images/2021/2021-11-03-18-54-17.png)

Změním sloupeček pri (syslog priorita) na decimal.

[![](/images/2021/2021-11-03-18-55-13.png){:class="img-fluid"}](/images/2021/2021-11-03-18-55-13.png)

Tabulka je vytvořena.

[![](/images/2021/2021-11-03-18-55-49.png){:class="img-fluid"}](/images/2021/2021-11-03-18-55-49.png)

Můžeme číst data.

[![](/images/2021/2021-11-03-18-56-28.png){:class="img-fluid"}](/images/2021/2021-11-03-18-56-28.png)

Zkusme napsat komplexnější query. Nejprve si parsujeme syslog zprávu regexem a nad následnými dynamickými sloupci uděláme filtr.

```
external_table("myexternaltable") 
| project srcIp = extract(@"srcIp=(.*?)\s", 1, message),
  dstIp = extract(@"dstIp=(.*?)\s", 1, message),
  dstPort = extract(@"dstPort=(.*?)\s", 1, message),
  action = extract(@"action=(.*?)$", 1, message)
| where action == "allow"
```

[![](/images/2021/2021-11-03-18-59-33.png){:class="img-fluid"}](/images/2021/2021-11-03-18-59-33.png)

Druhou cestou bude natlačení dat přímo do ADX.

[![](/images/2021/2021-11-03-19-01-33.png){:class="img-fluid"}](/images/2021/2021-11-03-19-01-33.png)

Vyberu nové jméno tabulky.

[![](/images/2021/2021-11-03-19-02-11.png){:class="img-fluid"}](/images/2021/2021-11-03-19-02-11.png)

Jako zdroj použiji blob kontejner.

[![](/images/2021/2021-11-03-19-03-44.png){:class="img-fluid"}](/images/2021/2021-11-03-19-03-44.png)

Jako v předchozím případě zvolím formát JSON, vymažu @timestamp a změním pri na decimal.

[![](/images/2021/2021-11-03-19-04-44.png){:class="img-fluid"}](/images/2021/2021-11-03-19-04-44.png)

Chvilku počkáme, až se tam data nahrají.

[![](/images/2021/2021-11-03-19-05-21.png){:class="img-fluid"}](/images/2021/2021-11-03-19-05-21.png)

A teď už k nim můžu přistupovat Kusto jazykem.

```
['myingestedtable'] 
| project srcIp = extract(@"srcIp=(.*?)\s", 1, message),
  dstIp = extract(@"dstIp=(.*?)\s", 1, message),
  dstPort = extract(@"dstPort=(.*?)\s", 1, message),
  action = extract(@"action=(.*?)$", 1, message)
| where action == "allow"
```

[![](/images/2021/2021-11-03-19-06-24.png){:class="img-fluid"}](/images/2021/2021-11-03-19-06-24.png)

Samozřejmě jde jen o jednoduché PoC, pro praxi by to chtělo promyslet jak dělat třeba rotace blobů (do jednoho se vejde 190 TB, což je dost, ale spíše jde o nějakou přehlednost a vytváření třeba souborů per hodina a tak podobně) a spoustu dalších detailů. Nicméně zkoumání mi přineslo následující zjištění:
- Fluent Bit vypadá moc pěkně, je krásně minimalistický a podporuje výstup do Azure Blob i třeba do Log Analytics
- Azure Data Explorer je krásně jednoduchý na vytvoření, všechny kroky půjde jednoduše automatizovat (je to PaaS, nic se složitě neinstaluje)
- Azure Data Explorer může vycházet i cenově zajímavě nejen pro ad-hoc cluster pro konkrétní analytický úkol, ale i běžet trvale. Tajemství je v tom, že Sentinel a Log Analytics jsou optimalizované na vysoký výkon, ale ADX si můžu udělat s minimální cache a velkým poměrem storage k CPU (tedy udělat ho možná relativně pomalý, ale levný - pro občasné nahlížení to je možná to co potřebuji)
- Kombinace Sentinel pro kritická bezpečnostní data a levného blobu na forenzní data s možností hydratace do ADX s Kusto jazykem mi přijde velmi příjemný cenový kompromis.