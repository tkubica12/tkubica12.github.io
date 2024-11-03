---
layout: post
published: true
title: Azure Files Premium pro vaše náročnější aplikace potřebující sdílet data
tags:
- Storage
---
V Azure můžete ve své VM připojit vzdálený Azure Disk od pár stovek IOPS až po monstrózních 160 000 IOPS v Ultra SSD při latenci pod 1ms nebo použít lokální neredundantní NVMe storage v L-series řadách a získat IOPS v jednotkách milionů. Ale co když potřebujete data sdílet a přistupovat k nim třeba ze dvou instancí? Z pohledu aplikace toho Azure nabízí v této oblasti mnoho - Blob Storage, SQL, MySQL, PostgreSQL, CosmosDB s MongoDB API, Cassandra API, OData, Gremlin a mnoho dalších. To ale vyžaduje, aby aplikace příslušné API uměla používat.

Co když tedy chcete sdílenou storage, ale transparentně vůči aplikaci? Na to se dá použít vzdálený souborový systém a konkrétně PaaS služba (tzn. neřešíte podkladový OS, vysokou dostupnost a starání se o to) Azure Files (případně si uvnitř VM postavíte svojí softwarově definovanou storage nad Storage Spaces Direct). Jenže Azure Files až do teď byly skvělé pro práci s běžnými soubory, ale příliš pomalé na to, abyste do tohoto share nainstalovali i nějakou aplikaci. Ale teď už je v Preview Azure Files Premium - pojďme si otestovat, co dokáže. Nicméně nezapomínejme i na druhé omezení, které stále platí a to je, že ne všechny vlastnosti všech souborových systémů nad tím fungují. Zejména některé Linux vlastnosti jako jsou linky tam nedáte a pokud to aplikace vyžaduje, nebude možné to napřímo udělat (můžete ale ve Files uložit virtuální disk s ext4 a teprve ten si namapovat dovnitř Linuxu, ale i to má svá negativa u sdíleného scénáře).

# Příprava prostředí na test
Vytvořím si dva storage accounty. Jeden bude ve variantě Standard.

![](/images/2019/2019-05-19-18-19-34.png){:class="img-fluid"}

Druhý bude Premium. Nezapomeňte přepnout typu accountu na FileStorage.

![](/images/2019/2019-05-19-18-25-51.png){:class="img-fluid"}

Share budete vytvářet úplně stejně, jako v případě standardního share. Nicméně je tu jeden zásadní rozdíl. U Standard je velikost share jen horní limit, platíte jen za to, co reálně obsadíte. V případě Premium pro vás ale bude prostor a výkon vyhražen, platíte tedy za celý prostor, který si pro share alokujete. Jeho výkonnost bude 1 IOPS (s možností krátkodobě burstovat až na 3 IOPS) za každý 1GB storage a také za každých 10GB storage dostanete jeden MB/s propustnosti navíc nad rámec základního 100 MB/s (propustnost je rozdělena 60% read a 40% write).

Vytvořím si share o velikosti 500.

![](/images/2019/2019-05-19-18-30-17.png){:class="img-fluid"}

A také jeden s velikostí 1 TB.

![](/images/2019/2019-05-19-18-30-44.png){:class="img-fluid"}

Vytvořím si VM (já použil Standard D4s v3).

Nainstalujme si testovací utilitku fio a také cifs-utils pro namapování disku do Linux.

```bash
sudo apt update
sudo apt install -y cifs-utils fio
```

Podívejte se do GUI na heslo a namapujte všechny 3 shary do systému - jeden standardní 500 GB, jeden prémiový 500 GB a jeden prémiový 1 TB.

![](/images/2019/2019-05-19-18-39-26.png){:class="img-fluid"}

```bash
sudo mkdir /mnt/standard500
sudo mkdir /mnt/premium500
sudo mkdir /mnt/premium1000
sudo mount -t cifs //mojefiles.file.core.windows.net/mujsharestandard \
    /mnt/standard500 \
    -o vers=3.0,username=mojefiles,password="BRbGYX4JgMQcINuVBHmglAG8MeclevDWAm8f8KKVkpOiCRg9jHlj+jjAzzlGIH+h0bi9ByrXaz50qVvCpTLRCg==",dir_mode=0777,file_mode=0777,serverino
sudo mount -t cifs //mojefilespremium.file.core.windows.net/premiumshare500 \
    /mnt/premium500 \
    -o vers=3.0,username=mojefilespremium,password="hOWsXmsCE5R9I54/P58MIwp+lh2MKZN9gImEFlMpaR44F5Gkd/6jeRAHgNAlJ5HtwUVRW2QGei6FHKXXiOnysg==",dir_mode=0777,file_mode=0777,serverino
sudo mount -t cifs //mojefilespremium.file.core.windows.net/premiumshare1000 \
    /mnt/premium1000 \
    -o vers=3.0,username=mojefilespremium,password="hOWsXmsCE5R9I54/P58MIwp+lh2MKZN9gImEFlMpaR44F5Gkd/6jeRAHgNAlJ5HtwUVRW2QGei6FHKXXiOnysg==",dir_mode=0777,file_mode=0777,serverino
```

# Test latence
Pro změření latence použijeme asynchronní zápis, tedy čekáme po každém bloku na acknowledge, což nám dá nejpřesnější výsledky latence. Připravte si tři konfigurační soubory, jeden pro každý share, které budou stejné až na poslední řádek, který obsahuje konkrétní mount bod.

```
[global]
size=30g
direct=1
iodepth=1
ioengine=libaio
bs=8k

[writer1]
rw=randwrite
directory=/mnt/standard500
```

Pustíme testy.

```bash
fio --runtime 60 s500-latency.ini
fio --runtime 60 p500-latency.ini
fio --runtime 60 p1000-latency.ini
```

Standardní share ukázal následující latenci:

```
clat percentiles (usec):
    |  1.00th=[ 3163],  5.00th=[ 3294], 10.00th=[ 3425], 20.00th=[ 3556],
    | 30.00th=[ 3654], 40.00th=[ 3752], 50.00th=[ 3851], 60.00th=[ 3949],
    | 70.00th=[ 4047], 80.00th=[ 4228], 90.00th=[ 4621], 95.00th=[ 5473],
    | 99.00th=[11994], 99.50th=[17957], 99.90th=[30540], 99.95th=[32375],
    | 99.99th=[34341]
```

Premium share (bez ohledu na velikost, protože na latenci nemá vliv) vykázal na 50. percentilu latenci podobnou, ale i pouhé minutové měření jasně ukázalo rezervovaný a tedy vyrovnaný výkon. I na 99. percentilu je latence stále kolem 4 ms, zatímco u Standard už jsme na 12ms. Dají se tedy (podobně jako u Standard vs. Premium Azure Disk) očekávat větší výkyvy ve Standard accountu co do latence a zkrátka nemáte jistotu. Navíc Premium SSD, na kterých jsou Files Premium postavené, postupně prochází dalším zlepšováním latence a dá se očekávat příklon někam ke 2ms ještě letos.

```
clat percentiles (usec):
    |  1.00th=[ 3523],  5.00th=[ 3621], 10.00th=[ 3654], 20.00th=[ 3752],
    | 30.00th=[ 3785], 40.00th=[ 3818], 50.00th=[ 3884], 60.00th=[ 3916],
    | 70.00th=[ 3949], 80.00th=[ 4015], 90.00th=[ 4080], 95.00th=[ 4178],
    | 99.00th=[ 4359], 99.50th=[ 4490], 99.90th=[ 5080], 99.95th=[ 6390],
    | 99.99th=[12649]
```

# Test IOPS
Pro maximální IOPS použijeme stejné nastavení jako v předchozím testu, ale místo simulování legacy workloadu (který čeká na ACK po každém zápisu) nastavíme iodepth na 256. 

```
[global]
size=30g
direct=1
iodepth=256
ioengine=libaio
bs=8k

[writer1]
rw=randwrite
directory=/mnt/standard500
```

Totéž samozřejmě pro všechny tři share. Jaké jsou výsledky?

Standard Files reportují 1047 IOPS.

```
Jobs: 1 (f=1): [w(1)][100.0%][r=0KiB/s,w=8376KiB/s][r=0,w=1047 IOPS][eta 00m:00s
```

Premium, na rozdíl od Standard, mají provisionovaný výkon a to je 500 x 1, tedy 500 IOPS minimálně. Nicméně máme možnost burstovat až na 500 x 3 (mechanismus je popsaný na webu, ale zjednodušeně řečeno můžete hodinu denně jet na 1500 IOPS, nicméně výkon dostanete pouze, pokud je v Azure volno, ne garantovaně jako u základních IOPS).

Tohle je Premium s 500 GB:

```
Jobs: 1 (f=1): [w(1)][100.0%][r=0KiB/s,w=11.7MiB/s][r=0,w=1500 IOPS][eta 00m:00s]
```

A tohle Premium s 1000 GB, kde očekávám minimálně 1000 IOPS s burstem ke 3000 IOPS.

```
Jobs: 1 (f=1): [w(1)][100.0%][r=0KiB/s,w=23.7MiB/s][r=0,w=3029 IOPS][eta 00m:00s]
```

# Test propustnosti
Pro maximální propustnost bych měl použít velké bloky, délku fronty vzhledem k velkým blokům nepřehánět (32) a vícero paralelních zapisovačů. Konfigurační soubor vypadá takhle:

```
[global]
size=30g
direct=1
iodepth=32
ioengine=libaio
bs=1024k

[writer1]
rw=randwrite
directory=/mnt/standard500
[writer2]
rw=randwrite
directory=/mnt/standard500
[writer3]
rw=randwrite
directory=/mnt/standard500
[writer4]
rw=randwrite
directory=/mnt/standard500
```

S propustností u Premium je to tak, že minimálně dostanete pro čtení 60 MB/s + 6 MB/s za každých 100GB velikosti a pro zápis 40 MB/s a 4 MB/s za každých 100GB velikosti. U 1TB Premium share tedy očekávám minimálně 80 MB/s na zápisu a 120 MB/s na čtení (GUI ukazuje součet obou). Minima se v testech potvrdila, nicméně provoz na síťové kartě už byl hodně znát. Nezapomínejte, že na rozdíl od disků spotřebovává tato komunikace přidělený výkon síťové karty, což vás může zejména u malých VM limitovat.

# Extrémní situace a další možnosti 

Nejvyšší velikost share ve variantě Premium je 100 TiB, což vám přináší možnost využít 100k IOPS a propustnosti 6200 MiB/s čtení, 4100 MiB/s zápis. Vzhledem k síťové komunikaci to ale těžko získáte v jediné VM (v takovém případě sáhněte spíše po UltraSSD). Nicméně pokud máte storage pro výpočetní či datovou úlohu, na kterou masivně a paralelně přistupuje stovka výpočetních uzlů, Azure Files premium dobře poslouží i v takové situaci. Pokud by vám i tohle bylo málo, pro HPC scénáře se podívejte na Avere v Azure (specializovaná cache pro HPC od Avere, který se stal loni součástí Microsoftu).

Možná nechcete specializované řešení pro HPC, ale přesto chcete jít ještě dál a navíc jste možná zákazníkem NetApp, který je specialista na podobné systémy. Pak se podívejte na službu Azure NetApp Files, která může jít výkonnostně do extrémů typu 300k IOPS (https://cloud.netapp.com/blog/azure-netapp-files-performance-so-good-youll-think-youre-on-premises)[https://cloud.netapp.com/blog/azure-netapp-files-performance-so-good-youll-think-youre-on-premises]

# Kdy použít?

Možná potřebujete aplikaci, která využívá sdílených disků a jinou možnost nepodporuje (například staré verze SQL). Dřív jste si museli postavit výkonnou storage sami, třeba nahodit VM s Premium SSD a v nich udělat Storage Spaces Direct a tuto storage nabídnout aplikaci nebo jiné VM. Azure Files Premium už mají slušný výkon a možná pro vaši situaci postačí. Další výhoda je v tom, že storage se k VM dá připojit velmi rychle a to může být zajímavé pro vysokou dostupnost v rámci Azure Kubernetes Service (podpora Azure Files Premium by měla přijít s verzí 1.14). Přepojení disku při havárii nodu trvá dlouho, ale u Azure Files je to raz dva. Třetí příklad může být sdílený obsah webu, který je nesmysl dávat do každé VM nebo kontejneru. Lepší samozřejmě je použít Blob storage (mimochodem i ta má nově Premium variantu) a aplikaci na to připravit, ale co když to neumí? Azure Files ji namapujete do adresáře tak, že nebude nutné ji předělávat a přesto bude mít share dostatečný a předvídatelný výkon.