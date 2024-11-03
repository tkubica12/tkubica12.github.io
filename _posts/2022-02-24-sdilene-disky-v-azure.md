---
layout: post
published: true
title: Sdílené disky v Azure s SCSI PR nabízí skutečné řešení pro starší shared-storage clustering
tags:
- Storage
---
Tradiční aplikace často využívají sdílenou storage pro vytvoření redundantních clusterů. Typicky například jeden node databáze je v read/write režimu a současně stejné blokové zařízení je dostupné v read-only režimu pro další uzel. Jak něco takového přenést do cloudu?

# Shared disky a I/O fencing
AWS a GCP sice dovolují připojení disku k více strojům, ale bez jakékoli koordinace - nepodporují I/O fencing. Tím je to nepoužitelné pro náš scénář, protože tradiční software vyžaduje podporu SCSI Persistent Reservation instrukcí, tedy koordinace přístupů přímo na raw úrovni. Bez toho můžete leda použít koordinaci nějakou přímou komunikací mezi nody, jinak hrozí ztráta dat a nekonzistence - zkrátka nemůžete na to jen tak hodit běžný souborový systém a doufat.

Azure u sdílených disků I/O fencing podporuje a dnes si to vyzkoušíme.

# Alternativy ke sdíleným diskům
Jaké máme další možnosti?
- Ideálně nepoužívat shared-storage architekturu, ale jít do shared-nothing. U moderních databází to je běžně dostupné, ve světě NoSQL je to často právě ta jediná varianta. Nicméně my mluvíme o tradiční aplikaci, kde taková změna znamená razantní zásah, takže to je mimo hru.
- Postavit si vlastní storage nad IaaS v cloudu, typicky na iSCSI protokolu, jako je Windows Storage Spaces, CEPH a další softwarově definované storage. Tím ale výrazně roste složitost a cena.
- Použít sdílený souborový systém, například Azure Files nebo Azure NetApp Files. Někdy ale software vyžaduje raw zařízení (nepodporuje koordinaci přes zámky v souborovém systému, chce I/O fencing) nebo má speciální souborový systém či atributy, které vaše NAS řešení nepodporuje. Jindy to zase třeba technicky funguje, ale není to výrobcem podporované. V neposlední řadě tu může být problém s výkonem, protože obvykle NAS bývá pomalejší, než bloková storage (nicméně pro extrémní výkony máte k dispozici Azure NetApp Files, což na rozdíl od jiných cloudů není jen softwarová appliance NetAppu, ale skutečně specializované klasické storage železo, takže rozdíl oproti třeba blokovému UltraSSD není velký).

# Shared disk vs. zónová redundance
Tyto dvě vlastnosti spolu nutně nesouvisí, ale mohou být hodně užitečné dohromady. Pokud potřebujete tradiční cluster v Azure s brutálním storage výkonem, použijete UltraSSD, který podporuje shared režim. Pokud vám ale stačí výkon podobný Premium SSD, pak je tu varianta kombinace shared režimu s Premium SSD ZRS a pak můžete dát nody clusteru do různých zón dostupnosti a vytvořit tak vlastně klasický metro-cluster se sdílenou storage. 

# Vyzkoušíme shared disk
Všechny potřebné soubory a skripty najdete na mém [GitHubu](https://github.com/tkubica12/cloud-storage-tests).

Vytvoříme dvě VM v různých zónách, disk a připojíme ho k oběma.

```bash
# Create Resource Group
az group create -n shareddisk -l westeurope

# Create diagnostics storage account (for serial consol access)
export storage=tomasstore$RANDOM
az storage account create -n $storage -g shareddisk

# Create VNET
az network vnet create -n shareddisknet -g shareddisk --address-prefixes 10.0.0.0/16 --subnet-name default --subnet-prefixes 10.0.0.0/24

# Create VM in zone 1
az vm create -n z1 \
    -g shareddisk \
    --image UbuntuLTS \
    --size Standard_D2as_v4 \
    --boot-diagnostics-storage $storage \
    --zone 1 \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --nsg "" \
    --public-ip-address "" \
    --ephemeral-os-disk \
    --vnet-name shareddisknet \
    --subnet default

# Create VM in zone 2
az vm create -n z2 \
    -g shareddisk \
    --image UbuntuLTS \
    --size Standard_D2as_v4 \
    --boot-diagnostics-storage $storage \
    --zone 2 \
    --admin-username tomas \
    --admin-password Azure12345678 \
    --authentication-type password \
    --nsg "" \
    --public-ip-address "" \
    --ephemeral-os-disk \
    --vnet-name shareddisknet \
    --subnet default

# Create disk
az disk create -n shareddisk -g shareddisk --size-gb 32 --sku Premium_ZRS --max-shares 2

# Attach disk to VM
az vm disk attach --vm-name z1 -n shareddisk -g shareddisk 
az vm disk attach --vm-name z2 -n shareddisk -g shareddisk 
```

Nebudu instalovat žádný clustering software (např. pacemaker, Windows Server Failover Cluster), chci si to vyzkoušet nízkoúrovňově. Musím upozornit, že aby se mi nad tím dobře testovalo, použil jsem běžný souborový systém ext4, ale to jen, abych tam viděl soubory. Bez clusteru to není vhodné - I/O fencing sice zabrání nějakému poškození dat na disku, ale žurnálovací souborový systém z toho bude poměrně zmatený. Ale jak říkám - jde mi o vyzkoušení zámků na raw zařízení, to je účel dnešního testu, ne mít funkční clusterovaný souborový systém (třeba ocfs2, gfs2).

V první VM si nejprve přes SCSI PR instrukce udělám registraci a rezervaci disku pro zápis (nechám pro ostatní možnost čtení).

```bash
# Connect to z1
az serial-console connect -n z1 -g shareddisk

# Install SCSI utils
sudo apt update
sudo apt install sg3-utils -y

# Make registration and reservation
sudo sg_persist /dev/sdc  # No reservation keys exist
sudo sg_persist --out --register --param-sark=abc123 /dev/sdc  # Register key abc123
sudo sg_persist --out --reserve --param-rk=abc123 --prout-type=7 /dev/sdc  # Reserve disk for writing
sudo sg_persist -r /dev/sdc  # Check reservation

# Create partition, file system, mount and write data
sudo fdisk /dev/sdc <<EOF
n
p
1
1


w
EOF
sudo mkfs.ext4 /dev/sdc1
sudo mkdir /shareddisk
sudo mount /dev/sdc1 /shareddisk
sudo touch /shareddisk/z1.txt
```

Připojím se do druhého stroje a pokusím se číst.

```bash
# Connect to zě
az serial-console connect -n z2 -g shareddisk

# Install SCSI utils
sudo apt update
sudo apt install sg3-utils -y

# Check SCSI reservation
sudo sg_persist /dev/sdc 
sudo sg_persist -r /dev/sdc  # Resource is reservd
sudo sg_persist --out --reserve --param-rk=abc123 --prout-type=7 /dev/sdc  # FAIL, write access is reserved for z1

# Try to mount and read
sudo mkdir /shareddisk
sudo mount -o ro /dev/sdc1 /shareddisk   # FAIL, z2 is not registered

: `
[46305.386143] blk_update_request: I/O error, dev sdc, sector 10536 op 0x1:(WRITE) flags 0x800 phys_seg 1 prio class 0
[46305.393763] Buffer I/O error on dev sdc1, logical block 1061, lost async page write
[46305.398541] blk_update_request: I/O error, dev sdc, sector 10408 op 0x1:(WRITE) flags 0x800 phys_seg 1 prio class 0
[46305.402387] Buffer I/O error on dev sdc1, logical block 1045, lost async page write
[46305.502572] blk_update_request: I/O error, dev sdc, sector 2048 op 0x1:(WRITE) flags 0x800 phys_seg 5 prio class 0
[46305.506451] Buffer I/O error on dev sdc1, logical block 0, lost async page write
[46305.513296] Buffer I/O error on dev sdc1, logical block 1, lost async page write
[46305.518111] Buffer I/O error on dev sdc1, logical block 2, lost async page write
[46305.523047] Buffer I/O error on dev sdc1, logical block 3, lost async page write
[46305.528296] Buffer I/O error on dev sdc1, logical block 4, lost async page write
[46305.532626] blk_update_request: I/O error, dev sdc, sector 76072 op 0x1:(WRITE) flags 0x800 phys_seg 1 prio class 0
[46305.532745] Buffer I/O error on dev sdc1, logical block 9253, lost async page write
[46305.549268] EXT4-fs (sdc1): error loading journal
`
```

To nedopadlo dobře i když jsem chtěl jen číst, přitom disk mám správně připojený. Tady přišel ke slovu právě I/O fencing - nemám k disku registraci, která by odpovídala klíčem té z prvního stroje, takže přístup k zařízení mi je odmítnut. Mašina z1 si vzala exkluzivní právo na zápis, ale pokud budu také zaregistrovaný, měl bych být schopen číst.

```bash
# Make SCSI registration
sudo sg_persist --out --register --param-sark=abc123 /dev/sdc  # Register key abc123

# Try to mount again and rad
sudo mount -o ro /dev/sdc1 /shareddisk   # SUCCESS
sudo ls /shareddisk   # read works
```

Zkusme namountovat disk pro zápis a něco tam poslat. Jak jsem už zmiňoval žurnálovací systém nám dá chvilku pocit, že to jde, ale po chvíli uvidíme hlášky o selhání zařízení. Uživatelská zkušenost ale není to co teď řešíme (v praxi je u shared-storage vždy přítomen nějaký clustering software a clusterovaný souborový systém, který se o takové věci postará).

```bash
# Remount as read/write and try to write
sudo umount /shareddisk
sudo mount /dev/sdc1 /shareddisk
sudo touch /shareddisk/z2.txt   # Write will eventually fail

: `
[46412.758813] sd 3:0:0:0: [sdc] tag#43 FAILED Result: hostbyte=DID_ERROR driverbyte=DRIVER_OK
[46412.758813] sd 3:0:0:0: [sdc] tag#43 CDB: Write(10) 2a 00 00 01 29 28 00 00 08 00
[46412.758813] blk_update_request: I/O error, dev sdc, sector 76072 op 0x1:(WRITE) flags 0x800 phys_seg 1 prio class 0
[46412.762383] Buffer I/O error on dev sdc1, logical block 9253, lost async page write
[46412.773441] JBD2: recovery failed[46412.773446] EXT4-fs (sdc1): error loading journal
`
```

Výborně - selhává. Připojím se do první mašiny a uvolním zapisovací rezervaci.

```bash
# Make sure z1 was not able to write
sudo ls /shareddisk

# Release write lock
sudo sg_persist --out --release --param-rk=abc123 --prout-type=7 /dev/sdc
sudo sg_persist -r /dev/sdc  # Check reservation
```

V druhém VM si teď můžu vzít exkluzivní právo na zápis.

```bash
# Unmount
sudo umount /shareddisk

# Make reservation
sudo sg_persist --out --reserve --param-rk=abc123 --prout-type=7 /dev/sdc  # Reserve disk for writing

# Mount
sudo mount /dev/sdc1 /shareddisk
sudo touch /shareddisk/z2-B.txt   # SUCCESS
```

SCSI PR toho umí samozřejmě víc - například je tam vyřešena možnost, že první stroj zmizí a je potřeba jeho rezervaci zlomit a rozjet jiný node.

Tolik tedy ke sdíleným diskům v Azure pro přenos tradiční workloadů. Příště se podíváme na to, jak mohou sdílené disky v kombinaci se ZRS přinést zajímavé výhody pro Azure Kubernetes Service - konkrétně vyšší rychlost přepojení disků a zónovou redundanci bez nevýhod NASky.

