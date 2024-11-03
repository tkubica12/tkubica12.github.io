---
layout: post
published: true
title: Testování síťového výkonu v Azure
tags:
- Networking
---
Jak správně testovat síťovou latenci a prostupnost? Jaké jsou parametry sítí v Azure a jaké jsou možnosti z pohledu optimalizací pro potřeby vašich aplikací? Nejprve se podíváme na koncepty Accelerated Networking, Proximity placement group, Availability zóny a regiony. Následně si popíšeme správné testovací nástroje a vyzkoušíme si, co naměříme.

# Datová centra, regiony a síťová topologie na backendu
Základním stavebním blokem je datové centrum nebo sál. Jak je velké záleží na konkrétním regionu a stáří. Může to být technologie malých DC v kontejnerech, obrovská hala, patro či design ala motýl (4 haly se společným středem). Uvnitř DC jsou ToR prvky v každém racku zapojené do CLOS architektury s agregačními prvky. Pokud máte dvě VM ve stejném kontejneru či sálu je mezi nimi malinkatá vzdálenost a očekávejme nejlepší latenci i propustnost. Při vytvoření VM ale Azure rozhodne o umístění do konkrétního sálu podle aktuální kapacity, typu VM apod., takže nemůžete garantovat, že se VM dostanou skutečně do stejného sálu. Aby něco takového bylo možné přichází v preview funkce Proximity placement group, díky které si zajistíte, že vaše VM budou ve stejném sále. Získáte tak optimální latenci, ale doporučuji skutečně pouze tam, kde je síťová latence pro vás to nejdůležitější (takových případů je strašně málo). Ono jak uvidíte síťová latence se pohybuje v desítkách **mikrosekund**, zatímco obvyklá aplikační latence je běžně v řádech milisekund. Jinak řečeno optimalizace software je obvykle to nejdůležitější. Nicméně jsou situace, kde vám pár desítek mikrosekund k dobru pomůže (některé druhy High performance computing, high-frequency trading apod.). Nezapomínejte ale, že proximity group omezuje Azure scheduleru možnosti volby. Pokud například uděláte proximity group s VM typu D a pak do ní chcete přidat VM typu M, může se stát, že se deployment nepodaří jednoduše proto, že exotičtější typy strojů nejsou nutně v každém sále (řešením je začít plnit proximity group právě exotičtějšími servery a pak pokračovat běžnějšími). Zkrátka váš požadavek je velmi přísný a ztěžujete Azure práci, ale pokud je latence pro vás naprosto zásadní, je to pro vás k dispozici.

V regionu není jen jedno datové centrum, ale obvykle několik - třeba 12 obrovských hal nebo desítky/stovky kontejnerů. Ve vybraných regionech jsou k dispozici zóny dostupnosti, tedy datová centra (haly), které mají všechny samostatné napájení, generátory, chlazení, síťovou agregaci apod. Někdy jsou relativně blízko u sebe, ale někdy může být vzdálenost přes kilometr. Obvykle takových jednotek bývá několik. Pro uživatele je to ale zjednodušeno na 3 zóny dostupnosti, s kterými pracuje a ty reprezentují jednu a více budov. Pokud umístíte tři VM každé do jiné zóny, budou výborně odděleny do různých datových center a logicky tak dál od sebe s větší latencí. Nicméně CLOS networking architektura zajišťuje extrémně výkonné propoje, takže na propustnosti to prakticky nepoznáte.

Regiony jsou vždy dostatečně daleko od sebe pro minimalizaci dopadu nějaké místní katastrofy typu zemětřesení. Každý region má (alespoň co do "moderního" Azure, tedy ARM zdrojů) kompletní control plane a nasazování změn řídícího software se provádí tak, aby případná chyba nebyla zanesena najednou do dvou párových regionů jako je třeba West Europe a North Europe. Regiony propojuje globální Microsoft WAN síť s brutální kapacitou. Nicméně logicky musíme očekávat podstatně větší latenci (s rychlostí světla se nic nenadělá) a menší propustnost, než uvnitř datového centra (to určitě znáte z on-premises - servery máte připojeny 10G/40G a celkovou kapacitu DC klidně v řádu desítek TB, ale WAN linku mezi dvěma DC máte třeba jen 10G - v Azure je tohle samozřejmě o řády jinde, ale i tam platí, že výkon uvnitř regionu je logicky větší, než na WAN).

# Accelerated Networking
Virtualizace tradičně znamená, že na hostiteli běží vSwitch, který implementuje věci jako je filtrace paketů (firewallig) aka NSG, routing, load-balancing pravidla nebo IP NAT. To samozřejmě přidává latenci, protože implementace běží v CPU. Nicméně v Azure jsou pro standardní a high-end řady montovány síťové karty s podporou SR-IOV a speciální FPGA čipy, které Microsoft programuje pro hardwarovou akceleraci těchto funkcí. Výsledkem pak je, že díky SR-IOV je virtuální síťová karta namapovaná přímo do guest OS (nemusí tak jít přes host procesy) a navíc je logika zpracování paketů zanesena do vedle sedícího FPGA. To výrazně snižuje latenci, takže pokud vám o ni jde, vyberte si stroje, které ji umožňují a zapněte její podporu. Jde typicky a řady D/E a vyšší (kromě nejmenších VM v řadě). Pozor ale, že pro podporu je potřeba mít speciální síťový driver. Ten je součástí Windows a Linux imagů v Azure, ale pokud si přinášíte svůj vlastní, dejte si na to pozor.

# Propustnostní limity na VM
Řekněme například, že fyzický server v Azure má 100G připojení do sítě. Nebylo by fér, aby zákazník, který si koupí malé VM reprezentující 1/32 fyzického serveru mohl vyčerpat celých 100G. Stejně jako s CPU, RAM, cache nebo storage IO je i propustnost sítě přidělována VM podle jejich velikosti. Tak například Standard D16 v3 dle dokumentace nabízí 8Gbps hrubé propustnosti. D8 méně, D32 více. U některých typů VM, zejména těch levnějších, není jejich propustnost uvedena a je nějakým způsobem agregována (A-series, B-series).

# Nástroje pro testování
Pro testování propustnosti vždy doporučuji použít iperf, který je k dispozici jak pro Linux tak Windows. Má serverovou stranu a klienstkou stranu. Nepoužívejte pro testování něco typu kopírování souborů, protože pak vám do toho promlouvá výkonnost storage a neměříte co potřebujete. U iperf by default pouštíte jako test jednu session. Ve vnitřní sítí obvykle není zásadní rozdíl mezi jednou session a vícero paralelních, protože jsou nízké latence a relativně jednoduché prvky. U WAN linek nebo při průchodu nějakým vaším firewallem už tam ale rozdíl být může, protože třeba firewall může paralelizovat zpracování podle session na jednotlivé core a součet vícero session tak může dávat víc, než session jedna. To prakticky uvidíte právě na spojení mezi dvěma Azure regiony nebo při připojení z on-prem. V takových situacích se snažte paralelizovat přenosy (například ve Windows robocopy vs. copy).

Co se latence týče prosím **nikdy** nepoužívejte ping. Ten má nejnižší možnou prioritu jak v SDN Azure tak v rámci TCP/IP stacku v OS. Dostanete naprosto nesmyslné výsledky. Pro Linux doporučuji qperf, ve Windws můžete použít ntttcp.

# Prostředí
Pro jednoduchost jsem připravil ARM šablonu, která pro vás založí testovací stroje o velikosti D16 v3. Více detailů jak to funguje a jak je to udělané najdete na mém [githubu](https://github.com/tkubica12/azure-network-performance-test).

Nasaďte šablonu do Azure:

[![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.png)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ftkubica12%2Fazure-network-performance-test%2Fmaster%2Fazuredeploy.json){:target="_blank"}

Připojte se na první stroj a odtud budeme testovat (username je net a password zadáváte v šabloně).

```bash
export ip=$(az network public-ip show -n r1-z1-pg1-vm01-ip -g netperf --query ipAddress -o tsv)
ssh net@$ip
```

# Testy latence
Nejprve se podívejme latenci.

## Latence v rámci proximity placement group
Proximity placement group nám garantuje, že stroje jsou ve stejném sálu. Podívejme se na výsledky:

```bash
net@r1-z1-pg1-vm01:~$ qperf -t 20 -v r1-z1-pg1-vm02 tcp_lat # same proximity placement group
tcp_lat:
    latency        =  39.4 us
    msg_rate       =  25.3 K/sec
    time           =    20 sec
    loc_cpus_used  =  15.1 % cpus
    rem_cpus_used  =  12.8 % cpus
```

Naměřil jsem cca 40 mikrosekund. Můžeme očekávat latenci velmi velmi stabilní.

## Latence v rámci zóny dostupnosti
Další VM je ve stejné zóně dostupnosti jako to první, ale ne ve stejné proximity group. To může znamenat buď, že máme štěstí a jsme ve stejném sále a nebo taky jsme v sále jiném. Výsledky tedy mohou být úplně stejné jako v předchozím případě, ale také nemusí. Jak už jsem psal zóna dostupnosti je logické členění a nemusí znamenat pouze jediný sál. Nicméně sály budou blízko u sebe, takže očekáváme výbornou latenci. Změřme si to.

```bash
net@r1-z1-pg1-vm01:~$ qperf -t 20 -v r1-z1-vm tcp_lat # same availability zone
tcp_lat:
    latency        =  58.2 us
    msg_rate       =  17.2 K/sec
    time           =    20 sec
    loc_cpus_used  =  10.5 % cpus
    rem_cpus_used  =  10.9 % cpus
```

V mém případě jsem tedy evidentně v jiném sále, ale latence je pořád pod 60 mikrosekund. 

## Latence mezi zónami dostupnosti
Další VM už je v jiné zóně dostupnosti, tedy rozhodně nebude ve stejné budově, jako VM první. To může znamenat, že jsou od sebe stovky metrů, ale v některých regionech mohou být DC od sebe i dál a to už bude znamenat větší latenci. Přesto mezi zónami očekávejte latenci hluboko pod 1 milisekundu. Vyzkoušejme na příkladu West Europe.

```bash
net@r1-z1-pg1-vm01:~$ qperf -t 20 -v r1-z2-vm tcp_lat # different availability zone
tcp_lat:
    latency        =  57.2 us
    msg_rate       =  17.5 K/sec
    time           =    20 sec
    loc_cpus_used  =    10 % cpus
    rem_cpus_used  =    12 % cpus
```

Všimněte si, že latence je u mě stejná, jako v předchozím příkladě. Datová centra jsou tedy v jiných zónách, ale blízko u sebe. U jiných regionů, třeba Paříž, to tak ale být nemusí. V každém případě je latence velmi nízká a umožňuje používání synchronních operací mezi zónami.

## Latence mezi regiony
V tomto případě jsou centra od sebe stovky kilometrů a jdeme přes WAN síť. Tady se fyzikální zákony ošálit nedají. Jakou jsem naměřil latenci mezi West Europe a North Europe?

```bash
net@r1-z1-pg1-vm01:~$ qperf -t 20 -v 10.1.0.4 tcp_lat # secondary region via VNET peering
tcp_lat:
    latency        =   9.9 ms
    msg_rate       =   101 /sec
    time           =    20 sec
    loc_cpus_used  =  0.95 % cpus
    rem_cpus_used  =   0.9 % cpus
```

Výsledek je kolem 10ms. To není vůbec špatné, ale pro věci typu synchronní replikace už je to moc. Z aplikačního hlediska to ale není nic šíleného, nicméně asi nedává smysl mít databázi v jednom regionu a aplikaci, která ji transakčně obsluhuje v jiném regionu.

# Testy propustnosti
Podívejme se teď na jiný aspekt výkonnosti sítě - propustnost. Použiji TCP testy, protože ty nejvíce odpovídají běžnému provozu. VM mojí velikosti má v dokumentaci 8Gbps, ale musíme počítat s nějakým overheadem pro TCP/IP hlavičky.

## Propustnost v rámci proximity placement group
Jakou jsem naměřil propustnosti v rámci proximity skupiny?

```bash
net@r1-z1-pg1-vm01:~$ sudo iperf -c r1-z1-pg1-vm02 -i 1 -t 30 # same proximity placement group
------------------------------------------------------------
Client connecting to r1-z1-pg1-vm02, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.4 port 43002 connected with 10.0.0.5 port 5001
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec   909 MBytes  7.62 Gbits/sec
[  3]  1.0- 2.0 sec   902 MBytes  7.56 Gbits/sec
[  3]  2.0- 3.0 sec   902 MBytes  7.56 Gbits/sec
[  3]  3.0- 4.0 sec   900 MBytes  7.55 Gbits/sec
[  3]  4.0- 5.0 sec   902 MBytes  7.56 Gbits/sec
[  3]  5.0- 6.0 sec   902 MBytes  7.56 Gbits/sec
[  3]  6.0- 7.0 sec   902 MBytes  7.57 Gbits/sec
[  3]  7.0- 8.0 sec   896 MBytes  7.52 Gbits/sec
[  3]  8.0- 9.0 sec   900 MBytes  7.55 Gbits/sec
[  3]  9.0-10.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 10.0-11.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 11.0-12.0 sec   900 MBytes  7.55 Gbits/sec
[  3] 12.0-13.0 sec   892 MBytes  7.48 Gbits/sec
[  3] 13.0-14.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 14.0-15.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 15.0-16.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 16.0-17.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 17.0-18.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 18.0-19.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 19.0-20.0 sec   875 MBytes  7.34 Gbits/sec
[  3] 20.0-21.0 sec   900 MBytes  7.55 Gbits/sec
[  3] 21.0-22.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 22.0-23.0 sec   900 MBytes  7.55 Gbits/sec
[  3] 23.0-24.0 sec   902 MBytes  7.57 Gbits/sec
[  3] 24.0-25.0 sec   900 MBytes  7.55 Gbits/sec
[  3] 25.0-26.0 sec   902 MBytes  7.57 Gbits/sec
[  3] 26.0-27.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 27.0-28.0 sec   898 MBytes  7.53 Gbits/sec
[  3] 28.0-29.0 sec   898 MBytes  7.53 Gbits/sec
[  3] 29.0-30.0 sec   901 MBytes  7.56 Gbits/sec
[  3]  0.0-30.0 sec  26.4 GBytes  7.55 Gbits/sec
```

7,55 Gbps a velmi stabilní.

## Propustnost v rámci zóny dostupnosti
Jak bude vypadat situace v rámci zóny dostupnosti?

```bash
net@r1-z1-pg1-vm01:~$ sudo iperf -c r1-z1-vm -i 1 -t 30 # same availability zone
------------------------------------------------------------
Client connecting to r1-z1-vm, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.4 port 51196 connected with 10.0.0.6 port 5001
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec   909 MBytes  7.62 Gbits/sec
[  3]  1.0- 2.0 sec   902 MBytes  7.57 Gbits/sec
[  3]  2.0- 3.0 sec   902 MBytes  7.57 Gbits/sec
[  3]  3.0- 4.0 sec   902 MBytes  7.56 Gbits/sec
[  3]  4.0- 5.0 sec   901 MBytes  7.56 Gbits/sec
[  3]  5.0- 6.0 sec   898 MBytes  7.53 Gbits/sec
[  3]  6.0- 7.0 sec   895 MBytes  7.51 Gbits/sec
[  3]  7.0- 8.0 sec   901 MBytes  7.56 Gbits/sec
[  3]  8.0- 9.0 sec   902 MBytes  7.56 Gbits/sec
[  3]  9.0-10.0 sec   898 MBytes  7.53 Gbits/sec
[  3] 10.0-11.0 sec   902 MBytes  7.57 Gbits/sec
[  3] 11.0-12.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 12.0-13.0 sec   902 MBytes  7.57 Gbits/sec
[  3] 13.0-14.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 14.0-15.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 15.0-16.0 sec   899 MBytes  7.54 Gbits/sec
[  3] 16.0-17.0 sec   903 MBytes  7.57 Gbits/sec
[  3] 17.0-18.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 18.0-19.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 19.0-20.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 20.0-21.0 sec   898 MBytes  7.53 Gbits/sec
[  3] 21.0-22.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 22.0-23.0 sec   900 MBytes  7.55 Gbits/sec
[  3] 23.0-24.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 24.0-25.0 sec   900 MBytes  7.55 Gbits/sec
[  3] 25.0-26.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 26.0-27.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 27.0-28.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 28.0-29.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 29.0-30.0 sec   902 MBytes  7.56 Gbits/sec
[  3]  0.0-30.0 sec  26.4 GBytes  7.56 Gbits/sec
```

Situace je prakticky stejná. V rámci zóny jsou síťové propoje masivní, takže nepozoruji žádný úbytek propustnosti nebo její vyrovnanosti.

## Latence mezi zónami dostupnosti
Každá zóna dostupnosti má nezávislé agregační prvky z důvodu nesdílení žádných komponent. Teoreticky tak může propustnost mezi zónami vypadat jinak. Vyzkoušejme si to.

```bash
net@r1-z1-pg1-vm01:~$ sudo iperf -c r1-z2-vm -i 1 -t 30 # different availability zone
------------------------------------------------------------
Client connecting to r1-z2-vm, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.4 port 45604 connected with 10.0.0.7 port 5001
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec   904 MBytes  7.58 Gbits/sec
[  3]  1.0- 2.0 sec   901 MBytes  7.56 Gbits/sec
[  3]  2.0- 3.0 sec   901 MBytes  7.56 Gbits/sec
[  3]  3.0- 4.0 sec   899 MBytes  7.54 Gbits/sec
[  3]  4.0- 5.0 sec   900 MBytes  7.55 Gbits/sec
[  3]  5.0- 6.0 sec   901 MBytes  7.56 Gbits/sec
[  3]  6.0- 7.0 sec   892 MBytes  7.48 Gbits/sec
[  3]  7.0- 8.0 sec   901 MBytes  7.56 Gbits/sec
[  3]  8.0- 9.0 sec   897 MBytes  7.52 Gbits/sec
[  3]  9.0-10.0 sec   884 MBytes  7.41 Gbits/sec
[  3] 10.0-11.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 11.0-12.0 sec   895 MBytes  7.51 Gbits/sec
[  3] 12.0-13.0 sec   900 MBytes  7.55 Gbits/sec
[  3] 13.0-14.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 14.0-15.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 15.0-16.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 16.0-17.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 17.0-18.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 18.0-19.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 19.0-20.0 sec   902 MBytes  7.56 Gbits/sec
[  3] 20.0-21.0 sec   899 MBytes  7.54 Gbits/sec
[  3] 21.0-22.0 sec   899 MBytes  7.54 Gbits/sec
[  3] 22.0-23.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 23.0-24.0 sec   901 MBytes  7.56 Gbits/sec
[  3] 24.0-25.0 sec   899 MBytes  7.54 Gbits/sec
[  3] 25.0-26.0 sec   897 MBytes  7.53 Gbits/sec
[  3] 26.0-27.0 sec   899 MBytes  7.54 Gbits/sec
[  3] 27.0-28.0 sec   893 MBytes  7.49 Gbits/sec
[  3] 28.0-29.0 sec   894 MBytes  7.50 Gbits/sec
[  3] 29.0-30.0 sec   899 MBytes  7.54 Gbits/sec
[  3]  0.0-30.0 sec  26.3 GBytes  7.54 Gbits/sec
```

Je vidět, že propoje jsou i mezi zónami nesmírně silné a na celkovou propustnost v mém případě prakticky nemají vliv. Je vidět častější zakolísání, ale v řádu 1%. Z pohledu propustnosti tedy můžeme považovat zóny dostupnost stále za lokální provoz. Pokud máte v on-premises třeba dvě datová centra v rámci Prahy, v Azure tomu odpovídá zóna dostupnosti. Pokud mezi nimi máte 10G linku považte, že v Azure jsme dostali skoro to samé jen pro jedno VMko - a to jsme tam s ohromným množství dalších VM.

## Propustnost mezi regiony
Mezi regiony už je WAN linka. Očekávám tedy složitější síťové prvky, nějaké velké routery a podobná zařízení a slabší propoje, než ve vnitřní síti. Připomínám, že v on-premises se tomu přibližuje třeba DC v Plzni a v Ostravě. Propojení mezi nimi budete mít typicky třeba 1G nebo 10G.

Kolik naměříme v Azure?

```bash
net@r1-z1-pg1-vm01:~$ sudo iperf -c 10.1.0.4 -i 1 -t 30 # secondary region via VNET peering
------------------------------------------------------------
Client connecting to 10.1.0.4, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.4 port 60516 connected with 10.1.0.4 port 5001
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec  23.4 MBytes   196 Mbits/sec
[  3]  1.0- 2.0 sec   124 MBytes  1.04 Gbits/sec
[  3]  2.0- 3.0 sec   116 MBytes   969 Mbits/sec
[  3]  3.0- 4.0 sec   113 MBytes   946 Mbits/sec
[  3]  4.0- 5.0 sec  91.1 MBytes   764 Mbits/sec
[  3]  5.0- 6.0 sec  88.8 MBytes   744 Mbits/sec
[  3]  6.0- 7.0 sec  91.0 MBytes   763 Mbits/sec
[  3]  7.0- 8.0 sec  95.9 MBytes   804 Mbits/sec
[  3]  8.0- 9.0 sec  97.4 MBytes   817 Mbits/sec
[  3]  9.0-10.0 sec  99.6 MBytes   836 Mbits/sec
[  3] 10.0-11.0 sec  97.8 MBytes   820 Mbits/sec
[  3] 11.0-12.0 sec   100 MBytes   843 Mbits/sec
[  3] 12.0-13.0 sec   100 MBytes   842 Mbits/sec
[  3] 13.0-14.0 sec   100 MBytes   843 Mbits/sec
[  3] 14.0-15.0 sec  98.9 MBytes   829 Mbits/sec
[  3] 15.0-16.0 sec   101 MBytes   844 Mbits/sec
[  3] 16.0-17.0 sec   103 MBytes   866 Mbits/sec
[  3] 17.0-18.0 sec  80.5 MBytes   675 Mbits/sec
[  3] 18.0-19.0 sec  81.9 MBytes   687 Mbits/sec
[  3] 19.0-20.0 sec  61.2 MBytes   514 Mbits/sec
[  3] 20.0-21.0 sec  65.8 MBytes   552 Mbits/sec
[  3] 21.0-22.0 sec  68.4 MBytes   574 Mbits/sec
[  3] 22.0-23.0 sec  70.2 MBytes   589 Mbits/sec
[  3] 23.0-24.0 sec  70.0 MBytes   587 Mbits/sec
[  3] 24.0-25.0 sec  72.1 MBytes   605 Mbits/sec
[  3] 25.0-26.0 sec  72.6 MBytes   609 Mbits/sec
[  3] 26.0-27.0 sec  71.2 MBytes   598 Mbits/sec
[  3] 27.0-28.0 sec  73.1 MBytes   613 Mbits/sec
[  3] 28.0-29.0 sec  74.4 MBytes   624 Mbits/sec
[  3] 29.0-30.0 sec  75.0 MBytes   629 Mbits/sec
[  3]  0.0-30.0 sec  2.52 GBytes   721 Mbits/sec
```

Dostal jsem se asi na 700 Mbps. Takže pokud máte mezi Plzní a Ostravou 1G linku, tak mezi Azure regiony jsme to dostali i na jednu z třeba milionu VM tam běžících.

Nicméně je to WAN linka a po cestě tedy budou určitě složitější prvky, které mohou paralelizovat zpracování podle jednotlivých sessions. Možná bychom tedy dosáhli vyšší propustnosti, pokud budeme přenášet paralelně.

```bash
net@r1-z1-pg1-vm01:~$ sudo iperf -c 10.1.0.4 -P16 -t 30 # multiple parallel sessions
------------------------------------------------------------
Client connecting to 10.1.0.4, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[ 18] local 10.0.0.4 port 60988 connected with 10.1.0.4 port 5001
[ 16] local 10.0.0.4 port 60984 connected with 10.1.0.4 port 5001
[ 17] local 10.0.0.4 port 60986 connected with 10.1.0.4 port 5001
[ 15] local 10.0.0.4 port 60982 connected with 10.1.0.4 port 5001
[  3] local 10.0.0.4 port 60958 connected with 10.1.0.4 port 5001
[  6] local 10.0.0.4 port 60964 connected with 10.1.0.4 port 5001
[  5] local 10.0.0.4 port 60962 connected with 10.1.0.4 port 5001
[  4] local 10.0.0.4 port 60960 connected with 10.1.0.4 port 5001
[ 10] local 10.0.0.4 port 60972 connected with 10.1.0.4 port 5001
[  9] local 10.0.0.4 port 60970 connected with 10.1.0.4 port 5001
[  7] local 10.0.0.4 port 60968 connected with 10.1.0.4 port 5001
[ 11] local 10.0.0.4 port 60974 connected with 10.1.0.4 port 5001
[ 14] local 10.0.0.4 port 60978 connected with 10.1.0.4 port 5001
[  8] local 10.0.0.4 port 60966 connected with 10.1.0.4 port 5001
[ 13] local 10.0.0.4 port 60980 connected with 10.1.0.4 port 5001
[ 12] local 10.0.0.4 port 60976 connected with 10.1.0.4 port 5001
[ ID] Interval       Transfer     Bandwidth
[ 10]  0.0-30.0 sec  1.16 GBytes   332 Mbits/sec
[  5]  0.0-30.0 sec   466 MBytes   130 Mbits/sec
[  3]  0.0-30.0 sec   442 MBytes   124 Mbits/sec
[  9]  0.0-30.0 sec   530 MBytes   148 Mbits/sec
[  7]  0.0-30.0 sec   324 MBytes  90.4 Mbits/sec
[ 13]  0.0-30.0 sec   376 MBytes   105 Mbits/sec
[ 16]  0.0-30.0 sec  1.11 GBytes   319 Mbits/sec
[ 17]  0.0-30.0 sec   729 MBytes   204 Mbits/sec
[  8]  0.0-30.0 sec   351 MBytes  98.1 Mbits/sec
[ 12]  0.0-30.1 sec   573 MBytes   160 Mbits/sec
[ 18]  0.0-30.1 sec   582 MBytes   162 Mbits/sec
[ 14]  0.0-30.1 sec   393 MBytes   110 Mbits/sec
[  4]  0.0-30.1 sec   437 MBytes   122 Mbits/sec
[ 15]  0.0-30.1 sec   461 MBytes   129 Mbits/sec
[ 11]  0.0-30.1 sec   561 MBytes   157 Mbits/sec
[  6]  0.0-30.1 sec   620 MBytes   173 Mbits/sec
[SUM]  0.0-30.1 sec  8.96 GBytes  2.55 Gbits/sec
```

Při použití 16 vláken jsme na 2,5 Gbps. Efekt zvýšení počtu sessions je v lokálu prakticky nulový, ale mezi regiony hraje důležitou roli. Opět si představte jak silná asi globální Microsoft síť je, když jedno z obrovského množství VM se může dostat na takovou propustnost.


Síť Microsoftu je myslím extrémně silná. V každém případě doporučuji testovat propustnost správně s použitím vhodných nástrojů. Pokud potřebujete testovat výkon ze svého DC do Azure, použijte stejné techniky. Nevěřte obecným statistikám nebo webovkám, ale jen vlastním očím. Pusťte si VM v Azure a otestujte si to sami, ať se přesvědčíte. Pokud máte pocit, že je aplikace uvnitř regionu pomalá a má dlouhou odezvu, zaměřil bych si primárně na prověření aplikačního a OS stacku, možná na sofistikované virtuální prvky po cestě (NGFW, WAFka). Síťovým fabric to obvykle nebude, protože je o 2 řády jinde, než většina software.














