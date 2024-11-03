---
layout: post
published: true
title: "Confidential Computing - zabezpečení dat při jejich používání, kdy ani root systému nemá šanci je rozlousknout"
tags:
- Security
- Compute
---
Všichni jsme jistě stokrát slyšeli o tom, že mám šifrovat "data in fly" a "data at rest", tedy používat pouze bezpečné šifrované protokoly pro komunikaci a šifrovat disk, souborový systém nebo databázovou storage. Nicméně pokud chceme s daty něco dělat, například něco počítat, analyzovat nebo vyhledávat, potřebujeme, aby se nějaký kód k datům dostal. Zřídka chceme data v IT jen ukládat, hlavním smyslem použití počítačů je práce s nimi. Aby kód s daty mohl pracovat, musí si je natáhnout do paměti v jejich původní, tedy nezašifrované podobě. Cokoli aplikace přijme šifrovaně nebo načte z šifrovaného disku potřebuje mít v paměti rozšifrované - alespoň ten kousek s kterým jdete pracovat. A to je slabé místo. Pokud mám do systému plná práva, mohl bych si vypsat celou paměť a citlivá data takto najdu. Šlo by s tím něco udělat?

# Řešení s asistencí hardware vs. speciální kryptografie
Zatím jsem slyšel o dvou velmi zajímavých řešeních tohoto "problému" (v uvozovkách proto, že je s nám od vzniku prvních počítačů, takže to neberme jako nějakou tragickou věc, ale že zkrátka bylo potřeba nejdřív vyřešit spoustu větších bezpečnostních potíží).

To první, o kterém to dnes hlavně bude, využívá asistenci hardwaru. Četli jste o vzniku izolace prováděných instrukcí v CPU? Ty nejprve přinesly například privilegovaný režim, který umožnil do ringů oddělit kód kernelu od uživatelské aplikace. Později (kolem roku 2005) bylo díky AMD-V a VT-X instrukcím možné dopřát virtuálním mašinám pocit, že jejich jádro běží v privilegovaném režimu, přestože to tak plně nebylo a procesor chránil hostitele. Co kdyby procesor získal speciální vlastnosti, kde by dokázal při načtení dat z paměti tyto rozšifrovat teprve v okamžiku jejich zpracování konkrétním procesem, který je navíc podepsaný a tím je ověřena jeho integrita? Pak by ani administrátor neměl možnost se k datům dostat a to ani pokud si provede kompletní dump paměti. Výhodou je vysoký výkon a obrovská flexibilita - takhle lze běžet vlastně cokoli. Nevýhodou je závislost na konkrétní generaci hardware a potenciální náchylnost ke side-channel útokům (o tom později).

Druhá možnost je kryptografická - homomorfní šifrování. Jde o speciální typ šifry, kdy je možné provádět validní operace na zašifrovaných datech. Mozek mi tedy nebere jak je to možné, ale znamená to, že ten kdo data zpracovává jim nemusí rozumět. Mějme příklad jednoduché šifry (nebude homomorfní) kdy 1=4, 2=3, 3=5 ... 6=7(substituce). Zašifruji údaj 1 a pak údaj 2 a dostávám v zašifrované podobě 4 a 3. Pokud teď provedu zpracování zašifrovaných dat jako je součet, bude to 4+3=7 a to vrátím majiteli dat. Ten rozšifruje a dostane výsledek 6. Jenže 1+2 není 6. Tato šifra tedy není homomorfní, abych mohl čísla sečíst, musím si to nejdřív rozšifrovat. Microsoft se i této oblasti velmi věnuje a vyvinul proto [knihovnu SEAL](https://github.com/Microsoft/SEAL).

# Confidential Computing a Trusted Execution Environment
Představme si, že uvnitř procesoru je zvláštní černá skříňka, jejíž dvířka nemůže ani administrátor serveru otevřít. Do této krabičky můžeme umístit nějaký kód, kterému věříme a jeho integritu si ověříme podpisem. Data, která zpracovává jsou v paměti v zašifrované podobě, takže jsou nečitelná pro všechny, kromě procesu uvnitř skříňky. Pro ten je černá bedýnka rozšifruje do vnitřních paměťových prostor procesoru, dovnitř skříňky. Tou skříňkou je Trusted Execution Environment (TEE) nebo také secure enclave. U Intelu jde o SGX funkce, u AMD o SEV a ARM má TrustZone.

Bezpečné enklávy zatím trpí kapacitním omezením (myslím, že podporují 128MB paměti), takže to ještě není univerzální řešení pro všechno. Nicméně to může být jen otázka času a investic, které zdá se výrobci hardware dost dělají.

# K čemu to využít?
Zmiňme pár typických příkladů a k některým se někdy příště vrátíme.
- Situace, kdy nevěříte administrátorovi serveru. Microsoft jistě má kredibilitu a všechny potřebné certifikace a audity, takže v tomto směru nebývá problém, ale nejvyšší třída špionážních dat je možná tak ostrá, že ani tohle nestačí. Confidential Computing může být odpověď. Cloud vaše data zpracovává a přitom je nikdo jiný nemůže rozlousknout, protože k nim má přístup pouze váš podepsaný kód (pokud podpis nesedí, enkláva data nedá), ne OS nebo admin. Tuto kategorii příkladů můžeme ještě rozvést:
    - Příkladem takové služby může být Azure SQL (zmiňuje schválně, protože to je první PaaS služba, která to od tohoto týdne v preview umí). Data zašifrujete klíčem přímo v aplikaci při ukládání (podobně jako u Always Encrypted), čímž obvykle vyřadíte vyšší funkce databáze (těžko vám udělá průměr sloupečku, když ho nevidí), ale pokud engine dokáže běžet uvnitř enklávy, můžete mu klíče svěřit a využít SQL dotazy aniž by OS, admin nebo hardwarový správce měli šanci data vidět.
    - Další ukázkou mohou být confidential kontejnery, kdy nechcete nic předělávat a některé mikroslužby chcete běžet v enklávě.
    - Možná si to aplikačně vyřešíte sami a potřebuje od cloudu principiálně jen železo s podporou TEE.
- Vícero subjektů, kteří si nesmí vidět do karet, potřebují spočítat společný výsledek.
    - Typický příklad jsou zdravotní záznamy z různých zemí, kdy nějaká Machine Learning úloha nad celou datovou sadou může pomoci lidstvu, ale neexistuje subjekt, kterému by všichni věřili a data mu poskytli. Takhle musí věřit algoritmu, kódu, který to spočítá a žádný jiný člověk nebo jiný kód surová data neuvidí a přesto výpočet proběhne a výsledky (ty neobsahují zdrojová data) pomohou všem.
    - Stejný scénář se týká Blockchain, kde si nikdo nevěří. Díky tomu si musí navzájem všechno dokazovat jako například použitím Proof of Work, kdy zapsat blok znamená investovat obrovský výpočetní výkon (za který, když budete první hotovi, vyhrajete odměnu), aby nebylo možné vybudovat paralelní realitu, ve které jste peníze neposlali (a přitom už máte zboží v kapse), protože počítat tak rychle, abyste odčinili několik bloků dozadu rychleji, než ostatní prodlužují řetězec je takřka nemožné (pokud nemáte 51% výpočetní síly blockchainu). To ale snižuje výkon (obrat transakcí se o několik řádů nedá srovnat s platbami kartou, mimo jiné proto Bitcoin nemůže fungovat jako VISA) a je to neekologické. Confidential Consortium je varianta, kdy si sice nikdo nevěří, ale věří podepsanému kódu v TEE. To zjednoduší práci blockchain sítě a dramaticky zvedne její výkon, přitom zůstávají pozitivní vlastnosti blockchain (například decentralizace).
    - Jako třetí případ uvedu detekci finančních útoků, kdy každá banka má svůj systém, ale zločinec může své kroky maskovat používáním mnoha transakcí v různých bankách. Pro jeho detekci by to chtělo koukat se na to globálně, za všechny banky, což ale naráží na osobní a/nebo obchodní údaje. Pokud by všechny banky mohly nasypat data na jedno místo, aniž by tato data někdo reálně mohl číst kromě procesu, který bude detekovat podezřelé operace, pomohlo by to.

# Side-channel útoky a jejich eliminace
Ve světě bezpečnosti mají zajímavé místo útoky zaměřené na nepřímé získání informací. Systém je dostatečně bezpečný, aby neodhaloval data a nenechal se zmást, ale zpracování dotazů za sebou zanechává stopy, které je teoreticky možné rozklíčovat a nepřímo získat informace. 

Klasický příklad je slepá SQL injection. Jsou situace, kdy nejste schopni získat odpověď serveru, ale jste schopni dotaz formulovat tak, že kontroluje platnost či neplatnost nějakého výroku s tím, že aplikace třeba v obou případech vyhodí chybu, ale odpověď databáze trvá rozdílnou dobu. Má username 5 znaků a pokud ano, udělej něco, co dlouho trvá. Pokud máte reakci rychle, nemá pět znaků, pokud pomalu, tak má. S trochou automatizace a trpělivosti se můžete po mnoha a mnoha dotazech k užitečným datům dostat.

Podobnými principy se dá útočit na další oblasti včetně samotného hardware. Tak například náročnost zpracování se odráží ve vytvořeném teple - to lze měřit a pokud nějaké dotazy teplo vyrábí a druhé ne, dá se to změřit i bez hesla do serveru. Další typická věc je cache, protože z ní jsou data dostupná rychleji (představme si hypoteticky, že uživatel A navštívil webový server a prohlédl si nějaké obrázky, které si pak server uložil do cache - pak se připojí uživatel B a nechá si zobrazovat obrázky jeden po druhém a u těch co se načtou rychle může vyvodit, že je uživatel A viděl; jasně, tenhle příklad je jistě neprůkazný a speciální, ale k odhalení nějaké informace zde určitě došlo a kousek po kousku může vést k infiltraci, protože vylučovací metodou například sníží variabilitu pro brute force útok). Tenhle princip souvisí i s tím, že si CPU předzpracovává instrukce ještě, než jsou reálně potřeba (spekulativní exekuce) a i to může vést ke schopnosti jednoho procesu přečíst data jiného (to se stalo se Spectre a Meltdown). Nicméně pokud kód cíle není upraven útočníkem (a to je jiné bezpečnostní téma), je reálná možnost využití otázkou štěstí (kód zkrátka musí dělat operace závislé na vstupu s rozhodovacím stromem, který vede k špatnému rozhodnutí procesoru, kterou část stromu si předpočítat).

Obecně vzato side-channel útoky jsou velmi obtížně využitelné pro něco užitečného (tzn. získání dat), ale taková možnost teoreticky je a podmnožina se může týkat i procesů běžících v enklávě. Tam je ale všechny jakékoli pochybnosti Intel velmi rychle vyřešil a žádné z nálezů nebyly pokud vím prakticky použitelné. Navíc pomůže CPU-pinning což limituje jednu z forem side-channel a další řešení je v kompilátoru, kdy se OpenEnclave postará o obranu před zbytkem (typicky nenechá rozhodovací stromy ve smyčce, kdy true počítá jako blázen a false nedělá skoro nic - kompilátor to zamaskuje).

# Confidential Computing v Azure
Azure dnes nabízí Confidential Computing minimálně ve třech podobách a na dalších se pracuje.
- Infrastruktura - můžete si vytočit VM s podporou Intel SXG a v nich nasadit svoje aplikace s využitím enkláv
- Kontejnery - Azure Kubernetes Service podporuje Confidential Computing a s využitím nástrojů třetích stran můžete konvertovat svoje běžné kontejnery do enklávy nebo ve svých kontejnerech použít kód využívající enklávy
- Azure SQL - v preview lze nasadit Always Encrypted se secure enklávou na straně databázového engine

# Vyzkoušejme si to prakticky
Dnes jsem se pokusil o jednoduchou zkoušku na základě OpenEnclave SDK s využitím základního příkladu a primitivního pokusu o dump paměti. Byl jsem zvědav, jestli tam tajnosti najdu. V tomto případě jde o aplikaci navrženou pro secure enclave, tedy má část nezabezpečenou a ta volá kousek kódu v zabezpečeném prostoru.

Připravil jsem si v Azure VM s podporou confidential computing s SGX instrukcemi Intelu, tedy řadu DCs_v2 podle [návodu](https://docs.microsoft.com/en-us/azure/confidential-computing/quick-create-marketplace).

Dál jsem se pustil do instalace [OpenEnclave SDK](https://github.com/openenclave/openenclave), které obsahuje knihovny pro vývoj zabezpečených aplikací a hlavně příklady, které využiji. Ve VM s Ubuntu 18.04 jsem tedy udělal tohle:

```bash
git clone https://github.com/openenclave/openenclave.git
cd openenclave

echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu bionic main' | sudo tee /etc/apt/sources.list.d/intel-sgx.list
wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | sudo apt-key add -

echo "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-7 main" | sudo tee /etc/apt/sources.list.d/llvm-toolchain-bionic-7.list
wget -qO - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -

echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/18.04/prod bionic main" | sudo tee /etc/apt/sources.list.d/msprod.list
wget -qO - https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

sudo apt update
sudo apt -y install clang-7 libssl-dev gdb libsgx-enclave-common libprotobuf10 libsgx-dcap-ql libsgx-dcap-ql-dev az-dcap-client open-enclave

```

V příkladech je aplikace Hello World, kterou si upravím tak, aby jak hostitelská část tak kód v zabezpečené enklávě obsahovala něco v paměti, co se budu pokoušet hledat. V adresáři samples/helloworld/enclave se nachází zabezpečená část kódu a v souboru enc.c uděláme změnu. Vytvoříme si řetězec (ten pak budeme v paměti hledat) a zacyklíme to, ať nám všechno zůstane pěkně nahoře.

```c
void enclave_helloworld()
{
    char secret[17] = "mysecuredpassword";
    while(1) {}
    ...
```

Něco podobného uděláme v běžné části programu, tedy v souboru samples/helloworld/host/host.c.

```c
int main(int argc, const char* argv[])
{
    char secret[10] = "mypassword";
    ...
```

Zkompilujeme a spustíme.

```bash
source /opt/openenclave/share/openenclave/openenclaverc
cd ~/openenclave/samples/helloworld
make build
make run
```

V druhé session si najdu ID tohoto procesu.

```bash
tomas@conf:~$ ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
...
tomas    10410 99.4  0.1  42688  4720 pts/0    R+   07:14   1:53 host/helloworldhost ./enclave/hellowor
...
```

Stáhnu si skript na jednoduché dumpování paměti do souboru a spustím.

```bash
git clone https://github.com/hajzer/bash-memory-dump.git
chmod +x ./bash-memory-dump/memory-dump.sh 
sudo ./bash-memory-dump/memory-dump.sh -p 10410 -m stack -d gdb
-----------------------------------------
Process of dumping memory was started ...
-----------------------------------------
PROCESS (PID) : 10410
MEMORY_REGION : stack
DUMP_METHOD   : gdb
-----------------------------------------
Dumping ...
-----------------------------------------
MEMORY REGION 'stack' of process with PID='10410' was dumped with DUMP_METHOD='gdb' to directory './MEMDUMPS-of-PID-10410'.
-----------------------------------------
LIST OF DUMPED FILES:
132K    ./MEMDUMPS-of-PID-10410/7ffd6e974000-7ffd6e995000.dump
```

To bychom měli, zlý administrátor nebo útočník s root přístupem nám právě ukradli obsah paměti. Najdeme tam řetězec mypassword z hostitelské části a mysecuredpassword z enklávy?

```bash
tomas@conf:~$ grep mypassword ./MEMDUMPS-of-PID-10410/7ffd6e974000-7ffd6e995000.dump
Binary file ./MEMDUMPS-of-PID-10410/7ffd6e974000-7ffd6e995000.dump matches

tomas@conf:~$ grep mysecuredpassword ./MEMDUMPS-of-PID-10410/7ffd6e974000-7ffd6e995000.dump
tomas@conf:~$
```

Běžný program (hostitelská část) má obsah paměti ve standardní podobě - tedy právě používaná data jsou tam nezašifrovaná. I pokud poctivě kryptujeme veškerou komunikaci a veškerá uložená data, pokud bude možné získat obsah paměti, k datům se dostaneme. Pro mysecuredpassword ale match nenacházíme - přestože kód v enklávě s touto proměnnou normálně pracuje, v paměti je uložena v zašifrované podobě.

Confidential Computing se dost možná za pár let stane naprostým standardem v cloudu, ale začít tuto technologii používat můžete už dnes. Stroje jsou dostupné, confidential kontejnery taky a přichází první PaaS služba s podporou TEE - Azure SQL. Na některé z těchto variant se podívám příště.