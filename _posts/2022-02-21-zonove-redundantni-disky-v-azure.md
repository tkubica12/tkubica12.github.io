---
layout: post
published: true
title: Zónově redundantní disky v Azure
tags:
- Storage
---
Máte dvě datová centra na opačných koncích Prahy, mezi nimi optiku a storage pole nastavené na synchronní replikaci. Nad tím běží nalevo vaše aplikace a pokud to celé vlevo začne hořet, pustíte to vpravo, protože synchronní replika storage vám tam dává nulové RPO. Poznáváte se v téhle klasické, dnes už trochu zastaralé, architektuře? V cloudové terminologii máte dvě zóny dostupnosti a mezi nimi synchronní repliku storage. Dá se takové řešení přenést do cloudu?

# Řešení, když není zónově replikovaná bloková storage (Azure dříve, AWS dodnes)
Azure Disk LRS nebo AWS EBS nepodporují synchronní repliku přes zóny, takže mám následující alternativy:
- Možná má můj cloudový poskytovatel souborovou storage, která zónovou replikaci podporuje - třeba Azure Files ZRS
  - Může být problém s výkonem pro některé aplikace - jasně, latence je spojená s replikací v zónách a to platí i případně pro zónový disk (na druhou stranu vrstva FS je implementována jako nějaká brána a ta sama o sobě také přidává nějakou latenci), ale vzdálený FS může trpět na metadata operace a pokud ho nakrmíte hromadou malých souborů může být výkon dost problém (ve srovnání s blokovým řešením a FS řízeném v compute).
  - Ne všechny aplikace budou v pohodě s omezeními konkrétního systému - mohou vyžadovat speciální file systém, speciální atributy a někdy dokonce naprosto trvají na raw zařízení.
- Použiji software pro replikaci (například Azure Site Recovery) nebo správu snapshotů (disk LRS, ale snapshot může být ZRS a z něj lze vytvořit disk v jiné zóně):
  - Tohle vede na nenulové RPO, takže ztrátu nějakých dat. To je dost možná v pořádku při výpadku celého regionu (velmi nízká pravděpodobnost), ale pro kritickou aplikaci bych reakci na výpadek "jen" zóny dostupnosti očekával spíše nulové RPO.
  - Naskriptovat si pravidelné snapshoty a práci s nimi je značně nepohodlné a na druhou stranu specializovaný software (Azure Site Recovery, Zerto, Commvault, ...) může přinášet náklady a komplexitu.
- Vyrobím si sám z VM a disků v různých zónách s použitím Microsoft Storage Spaces Direct, ONTAP od NetAppu, CEPH apod. 
  - To přináší vysokou složitost, náročnou správu, potenciální problémy a vyšší náklady (mám dost infrastruktury navíc)

Samozřejmě tady nepočítám čtvrtou cestu, kterou je naučit to řešení replikaci na úrovni software, třeba shared-nothing architekturu, protože zadání bylo převod původního řešení, ne jeho přepracování.

# Použití ZRS disků v Azure
Azure podporuje zónově redundantní disky pro tiery Standard SSD a Premium SSD ve vybraných regionech (ale jak North Europe tak West Europe k nim patří). Proč myslíte, že nejsou k dispozici pro Ultra SSD? Je to logické - ty jsou optimalizované pro maximální výkon a nízkou latenci, což je při synchronní replice mezi zónami (kde může být vzdálenost i desítky kilometrů) protimluv. Jak se podepíše replikace přes datová centra ve výkonnosti disku? To si pojďme vyzkoušet.

Všechny potřebné soubory a skripty najdete na mém [GitHubu](https://github.com/tkubica12/cloud-storage-tests).


# Praktická zkouška
Nejprve si vytvořím infrastrukturu - virtuálku v zóně 1 s diagnostickým storage accountem (ať k tomu můžu seriákem a nepotřebuji řešit sítě), jeden ZRS a jeden LRS disk (oba Premium SSD 1TB) a připojím je k VM.

```bash
# Create Resource Group
az group create -n zrs -l westeurope

# Create diagnostics storage account (for serial consol access)
export storage=tomasstore$RANDOM
az storage account create -n $storage -g zrs

# Create VM in zone 1
az vm create -n z1 \
    -g zrs \
    --image UbuntuLTS \
    --size Standard_D4as_v4 \
    --boot-diagnostics-storage $storage \
    --zone 1 \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --nsg "" \
    --public-ip-address "" \
    --ephemeral-os-disk 

# Create ZRS disk
az disk create -n zrsdata -g zrs --size-gb 1024 --sku Premium_ZRS 

# Create LRS disk in zone 1
az disk create -n lrsdata -g zrs --size-gb 1024 --sku Premium_LRS --zone 1

# Attach disks to VM
az vm disk attach --vm-name z1 -n zrsdata -g zrs 
az vm disk attach --vm-name z1 -n lrsdata -g zrs 
```

Skočím do mašiny a oba disky si připravím, namountuji a stáhnu si z mého GitHubu připravené konfigurační soubory pro fio (storage test nástroj).

```bash
az serial-console connect -n z1 -g zrs

# Prepare ZRS disk
sudo fdisk /dev/sdc <<EOF
n
p
1
1


w
EOF
sudo mkfs.ext4 /dev/sdc1
sudo mkdir /zrsdisk
sudo mount /dev/sdc1 /zrsdisk

# Prepare LRS disk
sudo fdisk /dev/sdd <<EOF
n
p
1
1


w
EOF
sudo mkfs.ext4 /dev/sdd1
sudo mkdir /lrsdisk
sudo mount /dev/sdd1 /lrsdisk

# Download fio configs
git clone https://github.com/tkubica12/cloud-storage-tests.git

# Install fio
sudo apt-get -y update
sudo apt-get install fio -y
```

Jaký je rozdíl v latenci a IOPS mezi LRS a ZRS? 

```bash
cd ./cloud-storage-tests/zone-redundant-disks
sudo fio --runtime 30 zrssyncread.ini   # 4,3 ms
sudo fio --runtime 30 zrssyncwrite.ini  # 3,2 ms
sudo fio --runtime 30 zrsasyncread.ini  # 5140 IOPS
sudo fio --runtime 30 zrsasyncwrite.ini # 5180 IOPS
sudo fio --runtime 30 lrssyncread.ini   # 2,2 ms
sudo fio --runtime 30 lrssyncwrite.ini  # 1,3 ms
sudo fio --runtime 30 lrsasyncread.ini  # 5140 IOPS
sudo fio --runtime 30 lrsasyncwrite.ini # 5140 IOPS
```

Zajímavé. Všimněte si, že ZRS má dle očekávání horší latenci (replikace přes různé zóny), ale není to nic tragického. Nicméně pokud rozjedete asynchronní operace uvidíte, že z pohledu IOPSů v nich není rozdíl.

Disk jsem odpojil a přepojil ho do nové VM v zóně 2. Tady je postup a výsledky.

```bash
# Create VM in zone 2
az vm create -n z2 \
    -g zrs \
    --image UbuntuLTS \
    --size Standard_D4as_v4 \
    --boot-diagnostics-storage $storage \
    --zone 2 \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --nsg "" \
    --public-ip-address "" \
    --ephemeral-os-disk 

# Try to attach ZRS and LRS disk
az vm disk detach --vm-name z1 -n zrsdata -g zrs 
az vm disk detach --vm-name z1 -n lrsdata -g zrs 
az vm disk attach --vm-name z2 -n zrsdata -g zrs  # SUCCESS: ZRS disk can be attached in any zone
az vm disk attach --vm-name z2 -n lrsdata -g zrs  # FAIL: LRS disk is bound to zone 1

# Connect to VM
az serial-console connect -n z2 -g zrs

# Prepare ZRS disk
sudo fdisk /dev/sdc <<EOF
n
p
1
1


w
EOF

sudo mkdir /zrsdisk   # Do not make FS (this is done already), just mount it
sudo mount /dev/sdc1 /zrsdisk

# Download fio configs
git clone https://github.com/tkubica12/cloud-storage-tests.git

# Install fio
sudo apt-get -y update
sudo apt-get install fio -y

# Run tests and compare with latency in zone 1
cd ./cloud-storage-tests/zone-redundant-disks
sudo fio --runtime 30 zrssyncread.ini   # 2,2 ms
sudo fio --runtime 30 zrssyncwrite.ini  # 3,2 ms
sudo fio --runtime 30 zrsasyncread.ini  # 5180 IOPS
sudo fio --runtime 30 zrsasyncwrite.ini # 5180 IOPS
```

Tentokrát jsou parametry latence ještě lepší, pro čtení dokonce odpovídají LRS. Obecně se dá očekávat, že v zápisu bude ZRS vždy pomalejší (plná konzistence znamená čekat na všechny zóny), ale při čtení rozdíl od LRS někdy vůbec nepoznáte.

Zkusím ještě zónu 3, který je v mém případě je zdá o něco dál, ale i tak jsem spokojen - latence jsou rozumné a v IOPSech jsem stále na tomtéž jako s LRS pro zápis i pro čtení (asynchronní operace - nečekám po každém bloku na ACK, ale zapisuji víc bloků najednou).

```bash
sudo fio --runtime 30 zrssyncread.ini   # 3,2 ms
sudo fio --runtime 30 zrssyncwrite.ini  # 4,8 ms
sudo fio --runtime 30 zrsasyncread.ini  # 5180 IOPS
sudo fio --runtime 30 zrsasyncwrite.ini # 5180 IOPS
```

Možná máte tedy aplikaci, která neumí běžet v nějakém clusteru s replikací na úrovni aplikace/databáze, potřebuje blokové disky a na cloud není ideálně připravena. S použitím ZRS disků ji mohu v Azure provozovat - běžím VM v zóně 1, disk je ZRS. S nulovým RPO jsem ho schopen použít pro VM v zóně 2, pokud by jednička hořela. Otázka samozřejmě je, za jak dlouho VM vyrobím (tedy jaké budu mít RTO) ... a to lze výrazně snížit, pokud už tam bude a překlopí se sama. To bych ale potřeboval další vlastnost tradiční infrastruktury - sdílené disky a SCSI persistent reservation instrukce, které bude ovládat nějak clusterovací software (díky tomu druhá VM rychle pozná, že první nežije a začne používat její disk i pro zápis). Nebo místo clusteru by to mohl být jiný Kubernetes node v jiné zóně, který v případě výpadku rozběhne ten stejný Pod a připojí mu bleskově stejná data. A ví te co? Přesně tohle Azure umí taky - sdílené disky a to včetně SCSI PR (dost důležitá věc, která obvykle jinde chybí) a jejich kombinace se ZRS diskem je náramně zajímavá. Na to se vrhneme příště.

