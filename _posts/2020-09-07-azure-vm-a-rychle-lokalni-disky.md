---
layout: post
published: true
title: Azure VM a rychlé lokální disky - temp, ephemeral OS, NVMe i levnější varianty bez ničeho
tags:
- Compute
- Storage
---
Musím si k VM kupovat disk pro OS? K čemu je caching u OS disku? Jak fungují dočasné disky a jak jsou rychlé? Můžu mít megarychlé a velké lokální disky, pokud si chci sám nasadit nějaké distribuované datové řešení jako je Cassandra? Jaký je rozdíl mezi VM E8s_v4, E8as_v4 a E8ds_v4? Na to všechno se dneska mrkneme.

# Trocha teorie k lokálním diskům v Azure serverech
V Azure jsou (a to asi není překvapení) fyzické servery. Různé řady VM běží na různých serverech, které mají jinak namíchané charakteristiky a poměry různých zdrojů. Tak třeba jsou tu servery s hodně pamětí (poměr CPU:RAM je minimálně 1:8) jako jsou E a M, servery tak nějak akorát (D), servery s malou pamětí (F), servery s GPU, FPGA, specializovanými HPC procesory pro maximální compute výkon (HC) nebo maximální pásmo mezi CPU a RAM (HB) a tak podobně. Ze serveru si něco nechá Azure pro sebe (hypervisor, správa, SDN apod.) a zbytek se prodává. Ten výkon si můžete koupit celý (nejvyšší VM v řadě, tedy na typu železa), nebo půlku, čtvrtku, osminku a tak dále. Všechny zdroje serveru tak máte buď pro sebe (nejvyšší VM) nebo jejich adekvátní část, například půlku. A to se týká všeho. Půlku cores, půlku RAM, půlku temp disků, půlku cache, půlku síťového pásma, půlku storage IO.

V serverech je obvykle lokální storage, tedy taková, která není nijak redundantní (na rozdíl od Azure Disk, který se dá samozřejmě k VM připojit) a používá se pro dočasné věci. Je to jednak cache (naposledy přečtená data se drží v lokální cache, ale dá se to zapnout i pro zápisy, čímž ale hrozí ztráta dat) a jednak temp disky (v OS se použijí jako vyrovnávací paměť, temp tabulky databáze a tak podobně). Jak se to prakticky chová? A víte, že nově můžete cache zrušit a místo ní z ní vytvořit OS disk pro bootování místo použití vzdálené storage? Nebo že Azure začal nabízet i VM, které lokální disk nemají a jsou tak o něco levnější?

# Nahodíme si prostředí pro testování
Nejprve si založím pár serverů a následně je budeme zkoušet a komentovat co se děje.

```bash
az group create -n localdisk-rg -l northeurope
az network vnet create -n localdisk-net \
    -g localdisk-rg \
    --address-prefixes 10.0.0.0/16 \
    --subnet-name default \
    --subnet-prefixes 10.0.0.0/24

# Create v4 VM AMD-based
az vm create -n vm-amd \
    -g localdisk-rg \
    --image UbuntuLTS \
    --size Standard_E8as_v4 \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --nsg "" \
    --vnet-name localdisk-net \
    --subnet default \
    --storage-sku Premium_LRS \
    --no-wait


# Create v4 VM Intel-based
az vm create -n vm-intel \
    -g localdisk-rg \
    --image UbuntuLTS \
    --size Standard_E8ds_v4 \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --nsg "" \
    --vnet-name localdisk-net \
    --subnet default \
    --storage-sku Premium_LRS \
    --no-wait

# Create v4 VM with ephemeral OS disk
az vm create -n vm-intel-ephemeral \
    -g localdisk-rg \
    --image UbuntuLTS \
    --size Standard_E8ds_v4 \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --nsg "" \
    --vnet-name localdisk-net \
    --subnet default \
    --ephemeral-os-disk \
    --no-wait

# Create v4 VM Intel-based with no temp
az vm create -n vm-intel-notemp \
    -g localdisk-rg \
    --image UbuntuLTS \
    --size Standard_E8_v4 \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --nsg "" \
    --vnet-name localdisk-net \
    --subnet default \
    --storage-sku Standard_LRS \
    --no-wait

# Create L series
az vm create -n vm-nvme \
    -g localdisk-rg \
    --image UbuntuLTS \
    --size Standard_L8s_v2 \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --nsg "" \
    --vnet-name localdisk-net \
    --subnet default \
    --storage-sku Premium_LRS \
    --no-wait
```

# Čtvrtá generace standarní mašiny - tentokrát s AMD procesorem
Nejoblíbenější řady VM v Azure jsou určitě D (poměr CPU:RAM 1:4) a memory optimized řada E (poměr 1:8, předchůdce se jmenoval D1x, tedy např. D12). v3 má buď procesor Intel Skylake 8171M nebo Intel Broadwell (E5-2567) a relativní výkonnost (ACU) je 160-190 (podle situace jsou tedy 1,6-1,9x výkonější, než originální řada A). Varianta E8_v3 (8 vCPU a 64GB RAM), slušný stroj třeba na databázi, vás vyjde na 394 EUR měsíčně (nebo 232 EUR při ročním závazku).

Nová generage v4 má z historického hlediska překvapivé rozdělení - a to na variantu postavenou na technologii AMD a jinou na Intelu.

Začněme příkladem Standard_E8as_v4, kde písmeno "a" značí AMD procesor, konkrétně AMD EPYC 7452. Tenhle procesor je na tom výkonnostně opravdu dobře a jeho relativní výkon (ACU) je 230-260. To je dramatické navýšení v desítkách procent a při tom je cena 374 EUR (nebo 220 EUR při ročním závazku), čili méně, než předchozí v3.

Ale vraťme se k tématu - jak je na tom s dočasným diskovým prostorem?

Připojím se do VM a podívejme se na disky. V cestě /mnt je dočasný disk o velmi příjemné velikosti 128G RAW kapacity.

```bash
ssh tomas@$(az network public-ip show -n vm-amdPublicIP -g localdisk-rg --query ipAddress -o tsv)

df -h
Filesystem      Size  Used Avail Use% Mounted on
...
/dev/sda1        29G  1.3G   28G   5% /
...
/dev/sdb1       126G   61M  120G   1% /mnt
...
```

Jakpak na tom je tento disk co do výkonu? Je lokální, takže očekávám nízkou latenci a slušné IOPSy. Nezapomínejte ale, že jde pouze o storage uvnitř té samé bedny - žádná redundance nebo něco takového. Pro svoje data použijte Azure Disk (nebo si data replikujte nějak sami mezi nody). Pro testování použijeme standardní fio a připravím si dvě konfigurace. Jednu synchronní, které bude vhodná pro změření latence a jednu asynchronní s více writery vhodnou pro otestování IOPSů. Použil jsem velikost bloku 8K, tedy nejdu po úplně maximálním IOPS, chci i rozumnou propustnost, proto kompromisní velikost bloku.

```bash
sudo apt update && sudo apt install fio -y

sudo -i

cat <<EOF >sync.ini
[global]
size=30g
direct=1
iodepth=1
ioengine=libaio
bs=8k
[writer1]
rw=randwrite
directory=/mnt
EOF

cat <<EOF >async.ini
[global]
size=5g
direct=1
iodepth=256
ioengine=libaio
bs=8k
[writer1]
rw=randwrite
directory=/mnt
[writer2]
rw=randwrite
directory=/mnt
[writer3]
rw=randwrite
directory=/mnt
[writer4]
rw=randwrite
directory=/mnt
EOF
```

Nejprve se podívejme na latenci. Pohled na 95-tý percencil ukazuje výborných 375 mikrosekund. To je skvělé, u remote storage to jen tak nedostanete, přiblížíte se s Ultra SSD, ale i Premium SSD je proti tomu líné (což je ale logické - tady píšeme bez jakékoli redundance jen na lokál).

```bash
sudo fio --runtime 60 sync.ini
...
clat percentiles (usec):
     |  1.00th=[   68],  5.00th=[   76], 10.00th=[   86], 20.00th=[  124],
     | 30.00th=[  131], 40.00th=[  139], 50.00th=[  147], 60.00th=[  163],
     | 70.00th=[  184], 80.00th=[  221], 90.00th=[  297], 95.00th=[  375],
     | 99.00th=[  578], 99.50th=[  676], 99.90th=[  971], 99.95th=[ 1074],
     | 99.99th=[ 3785]
...
```

Jak dopadla propustnost? Naměřil jsem asi 16 000 IOPSů (všechny testy dělám zapisovací, tedy horší variantu) a to je hodně dobré.

```bash
sudo fio --runtime 60 async.ini
...
Jobs: 4 (f=4): [w(4)][100.0%][r=0KiB/s,w=128MiB/s][r=0,w=16.3k IOPS][eta 00m:00s]
...
```

# Čtvrtá generace v Intelovské verzi s posílenou temp storage
v4 je dostupná i v podobě Intel Cascade Lake Platinum 8272CL. Jeho relativní výkon v ACU je 195-210, tedy míň než u AMD verze, ale stále výrazně víc, než předchozí generace. E8ds_v4 vás vyjde na 426 EUR měsíčně (nebo 251 v ročním závazku) a je tedy dražší, než AMD a dokonce i o něco víc, něž předchozí generace. Proč bych tedy měl Intel vůbec zvolit? Index výkonnosti je pro běžné počítání, ale Intel procesory mají jiné rozšířené instrukční sady a je možné, že právě váš software jich dokáže dobře využívat. Tak například AVX-512 přináší speciální instrukce pro zpracování dlouhých vektorů (3D modelování, simulace). Klasické rozšířené instrukce jako jsou SSSE3 mají často u AMD svoje ekvivalenty, ale ne každý software je kompilován tak, že je dokáže naplno využít. Zkrátka co do hrubého výkonu a ceny za výkon má E8as_v4 asi navrch, ale možná pro vás bude Intel volba jistější nebo výkonější, pokud používá speciality. Konec konců při přepočtu ceny na výkon je pořád o dost levnější, než v3. 

Navíc tato řada má jinačí temp disky a to se nám dnes do tématu dost hodí. Tato verze má při stejném počtu jader a RAM 2,5x víc temp prostoru a to vůbec není málo.

```bash
ssh tomas@$(az network public-ip show -n vm-intelPublicIP -g localdisk-rg --query ipAddress -o tsv)

df -h
Filesystem      Size  Used Avail Use% Mounted on
...
/dev/sda1        29G  1.3G   28G   5% /
...
/dev/sdb1       295G   65M  280G   1% /mnt
...
```

Opět použijeme fio a změříme si latenci a výkon. Co se latence týče, je prakticky stejná jako u AMD verze.

```bash
sudo apt update && sudo apt install fio -y

sudo -i

cat <<EOF >sync.ini
[global]
size=30g
direct=1
iodepth=1
ioengine=libaio
bs=8k
[writer1]
rw=randwrite
directory=/mnt
EOF

cat <<EOF >async.ini
[global]
size=5g
direct=1
iodepth=256
ioengine=libaio
bs=8k
[writer1]
rw=randwrite
directory=/mnt
[writer2]
rw=randwrite
directory=/mnt
[writer3]
rw=randwrite
directory=/mnt
[writer4]
rw=randwrite
directory=/mnt
EOF

sudo fio --runtime 60 sync.ini
...
clat percentiles (usec):
     |  1.00th=[   62],  5.00th=[   67], 10.00th=[   71], 20.00th=[   82],
     | 30.00th=[  130], 40.00th=[  139], 50.00th=[  145], 60.00th=[  153],
     | 70.00th=[  163], 80.00th=[  184], 90.00th=[  223], 95.00th=[  269],
     | 99.00th=[  498], 99.50th=[  701], 99.90th=[ 1713], 99.95th=[ 2409],
     | 99.99th=[ 5080]
...
```

Ale co IOPS? Tak jak u kapacity, tak u IOPS je vidět citelně víc. Skoro 60 000 IOPS je velký rozdíl.

sudo fio --runtime 60 async.ini
...
Jobs: 4 (f=4): [w(4)][100.0%][r=0KiB/s,w=462MiB/s][r=0,w=59.2k IOPS][eta 00m:00s]
...

Pokud tedy potřebujete lokální data a dobrém objemu a výkonu, tahle mašina vám dá silné moderní CPU, dobrou cenu a velmi slušnou a docela velkou lokální storage v ceně stroje.

# Cache a OS disk
Pro účely hned dalšího tématu bychom měli prozkoumat cache. Část SSD disků v serveru je dedikovaná pro cache, která je mezi vzdáleně připojenou storage (tedy Azure Disk) a vaším VM. Zejména pokud jde o disk typu HDD, může to znamenat brutální rozdíl. Pro datové disky se nedoporučuje cache zapínat. Čtecí cache se používá na OS disku a sdílí propustnost (u velkých SSD datových disků tak může být kontraproduktivní) a zapisovací cache může znamenat ztrátu dat.

Ve výchozím stavu je na OS disku cache zapnuta v režimu read/write. Jak to vyzkoušíme? Zkusme použít fio a testovat zápis. Ten tak půjde čistě do cache (pokud ta nebude menší, než OS disk, což v mém případě není) a bude to tak velmi rychlé. Při čtení by první kouknutí do souboru bylo pomalé, ale to další už rychlé, pokud ho z cache nevytlačilo něco čerstvějšího.

```bash
cat <<EOF >sync-os.ini
[global]
size=5g
direct=1
iodepth=1
ioengine=libaio
bs=8k
[writer1]
rw=randwrite
directory=/
EOF

cat <<EOF >async-os.ini
[global]
size=1g
direct=1
iodepth=256
ioengine=libaio
bs=8k
[writer1]
rw=randwrite
directory=/
[writer2]
rw=randwrite
directory=/
[writer3]
rw=randwrite
directory=/
[writer4]
rw=randwrite
directory=/
EOF

sudo fio --runtime 60 sync-os.ini
...
clat percentiles (usec):
     |  1.00th=[   40],  5.00th=[   42], 10.00th=[   43], 20.00th=[   45],
     | 30.00th=[   46], 40.00th=[   48], 50.00th=[   51], 60.00th=[   57],
     | 70.00th=[   68], 80.00th=[   91], 90.00th=[  145], 95.00th=[  251],
     | 99.00th=[  685], 99.50th=[  889], 99.90th=[ 1631], 99.95th=[ 1876],
     | 99.99th=[ 2835]
...

sudo fio --runtime 60 async-os.ini
...
Jobs: 2 (f=2): [w(1),_(2),w(1)][100.0%][r=0KiB/s,w=469MiB/s][r=0,w=60.1k IOPS][eta 00m:00s]
...
```

Úžasné. 250 mikrosekund na 95-tém percentilu a zase kolem 60 000 IOPS. Je tedy jasné, že cache využívá ten samý hardware, jako dříve testovaný temp disk. Nicméně ne vždy data v cache budou (třeba při čtení) - pro představu co by znamenalo ji zcela vypnout? To jsem v portále udělal a můžeme měřit. Použitý disk je Premium SSD o velikosti 32GB, tedy P4, který nabízí garantovaný výkon 120 IOPS s možností burstingu na 3500 IOPS.

```bash
sudo fio --runtime 60 sync-os.ini
...
clat percentiles (usec):
     |  1.00th=[ 2245],  5.00th=[ 2311], 10.00th=[ 2343], 20.00th=[ 2376],
     | 30.00th=[ 2409], 40.00th=[ 2442], 50.00th=[ 2474], 60.00th=[ 2507],
     | 70.00th=[ 2540], 80.00th=[ 2606], 90.00th=[ 2704], 95.00th=[ 2868],
     | 99.00th=[ 3556], 99.50th=[ 4047], 99.90th=[ 5997], 99.95th=[ 7504],
     | 99.99th=[ 9634]
...

sudo fio --runtime 60 async-os.ini
...
Jobs: 4 (f=4): [w(4)][100.0%][r=0KiB/s,w=27.3MiB/s][r=0,w=3499 IOPS][eta 00m:00s]
...
```

Měl jsem štěstí, dostal jsem rovnou těch 3500 IOPS, protože evidentně bylo volno a měl jsem nastřádáno (o tomto mechanismu napíšu někdy jindy). Každopádně rozdíl je dost vidět. Pokud by tento disk byl Standard HDD, očekávejme IOPS méně jak 500 a latence na 95-tém percentilu bude asi přes 5ms.

Jak to souvisí s dnešním tématem? Čtěte dál.

# Ephemeral OS disk
V předchozím případě jsme si dokázali, že pokud zapneme read/write cache, dostaneme se na úžasnou rychlost temp disku. Pokud bude velikost cache odpovídat velikosti disku (což u Linux s 32GB platí už od docela malých strojů alespoň v řadě E a naše E8 nebude mít problém ani s 128GB Windows), mohl OS žít vlastně jen v cache, pokud vlastně nepotřebujeme žádná data na tomto disku mít perzistentní. A to je hlavní myšlenka ephemeral disků pro OS. Proč si platit Azure Disk pro OS (i když jde o dost malou částku) a bootovat z pomalejší storage, když by se třeba dalo image nakopírovat rovnou do cache, bootovat velmi rychle lokálně a za Azure Disk neplatit. Dostanu rychleji bootující stroj, výkonný root file systému (aniž bych musel něco přemapovat na temp) a nižší cenu. Kdy by se něco takového hodilo? Pro prakticky všechny plně automatizované systémy, do kterých se ručně nesahá a jejichž state v OS se nemění (potřebná změna se roluje jako nový image podobně jako u kontejnerů). Kubernetes node, node pro nějaký batch výpočet, node renderující snímek 3D filmu a tak podobně. Proto třeba Azure Kubernetes Service dnes v preview tuto možnost nabízí.

Takovou VM jsme si na začátku vytvořili - stačil k tomu jediný přepínač. Můžeme si ověřit, že máme jak OS bez Azure Disk, tak nám stále zůstal celý temp (prostor se použil z cache, ne temp disku). Otestujeme výkon a je stále stejně dobrý.

```bash
ssh tomas@$(az network public-ip show -n vm-intel-ephemeralPublicIP -g localdisk-rg --query ipAddress -o tsv)

df -h
Filesystem      Size  Used Avail Use% Mounted on
...
/dev/sda1        29G  1.3G   28G   5% /
...
/dev/sdb1       295G   65M  280G   1% /mnt
...

sudo apt update && sudo apt install fio -y

sudo -i

cat <<EOF >sync-os.ini
[global]
size=5g
direct=1
iodepth=1
ioengine=libaio
bs=8k
[writer1]
rw=randwrite
directory=/
EOF

cat <<EOF >async-os.ini
[global]
size=1g
direct=1
iodepth=256
ioengine=libaio
bs=8k
[writer1]
rw=randwrite
directory=/
[writer2]
rw=randwrite
directory=/
[writer3]
rw=randwrite
directory=/
[writer4]
rw=randwrite
directory=/
EOF

sudo fio --runtime 60 sync-os.ini
...
clat percentiles (usec):
     |  1.00th=[  106],  5.00th=[  153], 10.00th=[  161], 20.00th=[  174],
     | 30.00th=[  186], 40.00th=[  200], 50.00th=[  221], 60.00th=[  243],
     | 70.00th=[  277], 80.00th=[  326], 90.00th=[  420], 95.00th=[  529],
     | 99.00th=[  840], 99.50th=[  988], 99.90th=[ 1827], 99.95th=[14746],
     | 99.99th=[30802]
...

sudo fio --runtime 60 async-os.ini
...
Jobs: 4 (f=4): [w(4)][88.9%][r=0KiB/s,w=474MiB/s][r=0,w=60.6k IOPS][eta 00m:01s]
...
```

Nutno říct, že ephemeral OS je plně k dispozici a v preview je další novinka v této oblasti - použití i prostoru z temp disku jako místa pro OS. Jde o to, že ty nejmenší typy VM nemusí mít dostatečně velkou cache na celý OS, ale přitom temp disk by na to stačil. V preview je možné temp obětovat a použít ho na OS taky.

# Ale já ten temp disk nechci
Až doteď temp disk prostě v každé Azure VM byl, protože v naprosté většině případů to dává smysl. Nicméně celkově vzato té storage v serveru není zrovna málo, takže to logicky generuje nějaké náklady. Zajímavou novinkou u Intel varianty v4 generace je přítomnost verze bez temp disku. Model E8_v4 a E8s_v4 (první nepodporuje Premium SSD, druhý ano - stojí stejně). Zaplatíte za ně 374 EUR (220 EUR v roční rezervaci), čili stejně jako AMD verze. Za variantu bez písmene "d", které nově reprezentuje přítomnost temp disku, tedy zaplatíte méně.

Vyzkoušejme, že tam opravdu není.

```bash
ssh tomas@$(az network public-ip show -n vm-intel-notempPublicIP -g localdisk-rg --query ipAddress -o tsv)

df -h
Filesystem      Size  Used Avail Use% Mounted on
udev             32G     0   32G   0% /dev
tmpfs           6.3G  684K  6.3G   1% /run
/dev/sda1        29G  1.3G   28G   5% /
tmpfs            32G     0   32G   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs            32G     0   32G   0% /sys/fs/cgroup
/dev/sda15      105M  3.6M  101M   4% /boot/efi
tmpfs           6.3G     0  6.3G   0% /run/user/1000
...
```

# Lokální storage vyhnaná do extrému s L řadou
Na závěr zmiňme ještě jednu variantu, jak získat dostatek lokální storage, ale tentokrát o daleko větším objemu a mnohem brutálnějším výkonu. Jde o rodinu VM v Azure, které kromě standardního temp disku nabízí i přímý přístup k NVMe storage a to až do VM s 19,2 TB storage s 3 800 000 IOPS na čtení. Pro srovnání použijeme opět variantu s 8 vCPU, 64GB RAM a navíc jedno NVMe zařízení s kapacitou 1,92 TB o čtecím výkonu 400 000 IOPS. CPU na rozdíl od předchozích variant není zdaleka tak rychlé, je to AMD EPYC 7551 s indexem výkonnosti (ACU) 150-175. Cena je 458 EUR měsíčně (292 EUR v roční rezervaci).

Do VM se připojím a podívám se zařízení. Následně musím NVMe naformátovat, namountovat a spustím zapisovací test. Latence je díky NVMe a přímému namapování na hardware naprosto šílená - 78 mikrosekund na 95-tém percentilu. Z pohledu IOPS pro zápis (horší varianta) jsem se i bez velkých optimalizací v OS dostal na 261 000 IOPS.

```bash
ssh tomas@$(az network public-ip show -n vm-nvmePublicIP -g localdisk-rg --query ipAddress -o tsv)

lsblk
NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda       8:0    0   80G  0 disk
└─sda1    8:1    0   80G  0 part /mnt
sdb       8:16   0   30G  0 disk
├─sdb1    8:17   0 29.9G  0 part /
├─sdb14   8:30   0    4M  0 part
└─sdb15   8:31   0  106M  0 part /boot/efi
sr0      11:0    1  628K  0 rom
nvme0n1 259:0    0  1.8T  0 disk

sudo -i

mkfs.ext4 -E nodiscard /dev/nvme0n1
mkdir /mnt/nvme
mount /dev/nvme0n1 /mnt/nvme

apt update && apt install fio -y

cat <<EOF >sync.ini
[global]
size=30g
direct=1
iodepth=1
ioengine=libaio
bs=8k
[writer1]
rw=randwrite
directory=/mnt/nvme
EOF

cat <<EOF >async.ini
[global]
size=30g
direct=1
iodepth=512
ioengine=libaio
bs=4k
[writer1]
rw=randwrite
directory=/mnt/nvme
[writer2]
rw=randwrite
directory=/mnt/nvme
[writer3]
rw=randwrite
directory=/mnt/nvme
[writer4]
rw=randwrite
directory=/mnt/nvme
[writer5]
rw=randwrite
directory=/mnt/nvme
[writer6]
rw=randwrite
directory=/mnt/nvme
[writer7]
rw=randwrite
directory=/mnt/nvme
[writer8]
rw=randwrite
directory=/mnt/nvme
[writer9]
rw=randwrite
directory=/mnt/nvme
[writer10]
rw=randwrite
directory=/mnt/nvme
[writer11]
rw=randwrite
directory=/mnt/nvme
[writer12]
rw=randwrite
directory=/mnt/nvme
[writer13]
rw=randwrite
directory=/mnt/nvme
[writer14]
rw=randwrite
directory=/mnt/nvme
[writer15]
rw=randwrite
directory=/mnt/nvme
[writer16]
rw=randwrite
directory=/mnt/nvme
EOF

sudo fio --runtime 60 sync.ini
...
clat percentiles (usec):
     |  1.00th=[   34],  5.00th=[   35], 10.00th=[   36], 20.00th=[   38],
     | 30.00th=[   40], 40.00th=[   42], 50.00th=[   43], 60.00th=[   44],
     | 70.00th=[   48], 80.00th=[   53], 90.00th=[   65], 95.00th=[   78],
     | 99.00th=[  121], 99.50th=[  147], 99.90th=[ 1123], 99.95th=[ 1287],
     | 99.99th=[ 1401]
...

sudo fio --runtime 60 async.ini
...
Jobs: 16 (f=16): [w(16)][100.0%][r=0KiB/s,w=1021MiB/s][r=0,w=261k IOPS][eta 00m:00s]
...
```


Doufám, že se mi dnes podařilo trochu vysvětlit dočasnou storage dřímající přímo v serverech, jejíž poměrnou část najdete v ceně většiny VM (kromě nejnovější varianty bez ní). Ukázali jsme si jak je výkonná, jak funguje cache a že můžete mít i VM bez jakéhokoli Azure Disk. Vyzkoušeli jsme i brutální výkon NVMe v L řadě. Nezapomeňte, že dočasná storage není redundantní a počítejte s tím. Kdy se vám může hodit?
- Máte úlohu, kdy zpracováváte relativně hodně dat a potřebujete k nim z CPU co nejrychlejší přístup. Dát je všechna do paměti je dost drahé (v řadě M mluvíme o jiných cenách), ale mít je ve vzdálené storage zase příliš pomalé. Taková L-series mašinka je výborný kompromis pro úlohy, kdy data neustále přistupujete a měníte v rámci výpočtu.
- Nasadíte vlastní systém replikace dat, takže redundanci si zajistíte sami. Za mě - použijte raději hotovou službu s velkým výkonem, třeba CosmosDB pro strukturovaná data, Azure NetApp Files nebo Azure Avere vFXT pro HPC. Ale jestli z nějakého důvodu opravdu chcete vlastní Cassandra cluster nebo Gluster file systém, temp disky nebo dokonce L-series mašiny budou výborná volba.
- Máte potřebu výkonné dočasné storage - např. takový velký JOIN v relační databázi může snadno vytéct z možností RAM a dočasný pracovní prostor a vysokém výkonu bude hodně znát. Velikost a rychlost temp disků může být váš důvod, proč v E v4 sáhnout po Intelovské verzi.
- Jedete bezestavový workload jako jsou batch worker nody, na konkrétní výpočet sestavený Spark nebo bezestavové nody Kubernetes clusteru. Pak se vám může hodit neplatit za OS disk a jet z lokální storage a navíc získat rychlejší boot i o dost rychlejší disky bez práce (třeba EmptyDir Volume v Kubernetes).

Na druhou stranu nezapomeňte, že Azure má pro vás vždy hodně služeb s přidanou hodnotou v oblasti ukládání dat:
- Použijte PaaS - CosmosDB, Data Explorer, Avere, NetApp Files, SQL Business Critical, SQL/PostgreSQL Hyperscale, ...
- Použijte UltraSSD - dostanete výborný výkon a přitom jde stále o vzdálenou storage s plnou redundancí

