---
layout: post
published: true
title: "Dynamický routing v Azure s vašim vlastním zařízením - Azure Route Server"
tags:
- Networking
---
Pokud jdete nativní cestou dokáže Azure VPN a Azure Express Route Gateway synchronizovat směrování s vaší sítí přes BGP a tyto cesty programovat do Azure. Pokud se rozhodnete do cesty ještě přidat další zařízení jako je Azure Firewall, budete muset ve spoke sítích přidat směrování na něj (User Defined Route). Pokud ale chcete tohle všechno automatizovat, podívejte se na Azure Virtual WAN - ale o tom jindy. Co když ale chcete klasickou hub and spoke topologii ale používat vlastní síťové zařízení - tedy nějakou Network Virtual Appliance? Pak vás čeká hodně ruční práce v nastavování směrování ... a nebo už ne. Podívejme se na novinku v podobě Azure Route Server.

# Proč vznikla potřeba Azure Route Server
Azure VNET je vlastně virtuální router. Pokud vytvoříte více VNETů (například v hub and spoke topologii), musíte provést jejich peering, což zajistí něco na způsob dynamického vyměňování směrovacích informací typu directly connected. Pokud ve spoke zapnete Use remote gateway, tak se vám informace z Azure VPN a Azure Express Route Gateway budou propagovat dolu do spoke VNETů - ty budou tedy vědět jak směrovat do on-premises. 

Tohle se ale zkomplikuje když se rozhodnete do hry vložit firewall a to zejména pokud to bude nějaké ne-nativní řešení, tedy NVA třetí strany. A možná nebude mít na starost jen firewalling, ale budete přes tuto NVA řešit i routing domů třeba s VPN tunely. A nebo toto budou dvě různá zařízení - firewall + SD-WAN. Tím se nastavení směrování trochu zkomplikuje:
- NVA běží v Azure jako VM a nemá žádnou interakci s VNETem na úrovni výměny routing informací. Pokud mají spoke sítě posílat data přes NVA, musíte jim to říct statickou cestou (UDR). 
- Pokud má NVA směrovat do sítí v Azure, musíte jí nastavit routovací tabulku sami. 
- Pokud má Azure znát specifické sítě on-premises naučené z VPN NVA (například pro scénář kdy komunikace do on-prem nemá jít přes firewall, ale rovnou do VPNky třetí strany), musíte je také nastavit ručně. 
- Pokud má být NVA redundantní (a to by byl opravdu dobrý nápad):
  - Musí se schovat za Load Balancer, který bude fungovat jako next-hop, což je pro řadu NVA v pořádku pro firewalling uvnitř Azure nebo směrem k Internetu (v obou případech lze při správném nastavení zajistit symetričnost), ale často už ne pro VPN - s potenciálním asymetrickým routingem se nevypořádají a potřebují active/passive přístup (což lze udělat shozením health check probe, ale zatím jsem moc neviděl NVA třetích stran to takhle implementovat).
  - Použije se active/standby režim a to historicky ne přes Load Balancer, ale tak, že UDR směřují na jednu z instancí. Ty si mezi sebou kontrolují jestli je vše v pořádku a v případě výpadku primární se ta sekundární připojí do Azure a přenastaví UDR. To funguje skvěle v PoC, když máte pár spoke sítí, ale pokud jich jsou vyšší desítky nebo stovky, je to docela kostrbaté.

Vše vychází z toho, že NVA se s Azure na úrovni control plane nebaví. Co kdyby to ale uměla? Nenašel by se nějaký standardní protokol jakým by to šlo udělat? A víte, že ano? Co takhle BGP z roku 1989?

# Co je Azure Route Server

Azure Route Server je platformní služba, která vytvoří control plane vrstvu využívající BGP protokol. Komunikuje s Azure networkingem a informace o VNETech předává dál přes BGP a na oplátku se umí naučit informace od vás a v Azure je naprogramovat. Je to tedy čistě control plane záležitost - přes tento router fyzicky nic neteče.

Protože je služba platformní nemusíte se trápit vysokou dostupností ani patchováním. Podobně jako Azure VPN nebo Azure Firewall bude mít dedikovaný subnet a v něm si rozjede dvě aktivní instance a jednu pasivní a to vše rozložené přes zóny dostupnosti. 

Mimochodem z atributů, které show příkazy vrací je dost vidět, že podobná komponenta se využívá v Azure Virtual WAN ve scénáři, kdy chcete aby to routovalo, ale nemusel tam být finančně náročnější firewall. To asi nebude náhoda a technologie pod kapotou bude společná.

# Praktické vyzkoušení
Cílem dnešního testu bude vytvořit hub and spoke topologii s využitím NVA, které pro nás bude představovat Linux mašina s Quagga. Budeme chtít dosáhnout toho, že NVA bude dostávat informace z Azure routingu a na oplátku do něj předávat informace o svých cestách například do on-premises.

Vytvořme hub síť.

```bash
export rg=route-server-test-rg
az group create -n $rg -l westeurope
az network vnet create -n hub-net -g $rg --address-prefixes 10.0.0.0/16
az network vnet subnet create -n RouteServerSubnet -g $rg --vnet-name hub-net --address-prefixes 10.0.0.0/24
az network vnet subnet create -n NvaSubnet -g $rg --vnet-name hub-net --address-prefixes 10.0.1.0/24
az network vnet subnet create -n VmSubnet -g $rg --vnet-name hub-net --address-prefixes 10.0.2.0/24
```

Založíme Route Server.

```bash
az network routeserver create -n route-server -g $rg \
    --hosted-subnet $(az network vnet subnet show -n RouteServerSubnet -g $rg --vnet-name hub-net --query id -o tsv)
```

Poznamenáme si jeho BGP ASN a dvě IP adresy.

```bash
az network routeserver show -n route-server -g $rg --query virtualRouterAsn -o tsv
65515

az network routeserver show -n route-server -g $rg --query virtualRouterIps -o tsv
10.0.0.4
10.0.0.5
```

Vytvořme si teď VM s Ubuntu, která bude fungovat jako NVA a dejme ji do zóny dostupnosti 1.

```bash
az vm create -n linux-nva \
    -g $rg \
    --image UbuntuLTS \
    --size Standard_B1ms \
    --zone 1 \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --public-ip-address nva-ip \
    --private-ip-address 10.0.1.4 \
    --subnet NvaSubnet \
    --vnet-name hub-net \
    --storage-sku Standard_LRS
```

Nastavíme teď tuto VM jako BGP peer pro Route Server. Azure bude mít BGP AS číslo 65515 a my ve své NVA zvolíme 65514 (pozor, některá čísla má Azure rezervované jako právě 65515).

```bash
az network routeserver peering create --routeserver route-server -g $rg --peer-ip 10.0.1.4 --peer-asn 65514 -n nva1
```

Připojíme se do VM, nainstalujeme Quaggu a nahodíme konfigurace. Tento prvek bude do Azure posílat prefixy 10.50.0.0/16, 10.60.0.0/16 a 10.70.0.0/16. Obě adresy Route Server nastavíme jako BGP peer (neighbor).

```bash
ssh tomas@$(az network public-ip show -n nva-ip -g $rg --query ipAddress -o tsv)
    sudo -i
    apt update
    apt install quagga quagga-doc -y
    sysctl -w net.ipv4.ip_forward=1
    cat > /etc/quagga/zebra.conf << EOF
hostname Router
password zebra
enable password zebra
interface eth0
interface lo
ip forwarding
line vty
EOF
    cat > /etc/quagga/vtysh.conf << EOF
!service integrated-vtysh-config
hostname quagga-router
username root nopassword
EOF
    cat > /etc/quagga/bgpd.conf << EOF
hostname bgpd
password zebra
enable password zebra
router bgp 65514
network 10.50.0.0/16
network 10.60.0.0/16
network 10.70.0.0/16
neighbor 10.0.0.4 remote-as 65515
neighbor 10.0.0.4 soft-reconfiguration inbound
neighbor 10.0.0.5 remote-as 65515
neighbor 10.0.0.5 soft-reconfiguration inbound
line vty
EOF
    chown quagga:quagga /etc/quagga/*.conf
    chown quagga:quaggavty /etc/quagga/vtysh.conf
    chmod 640 /etc/quagga/*.conf
    echo 'zebra=yes' > /etc/quagga/daemons
    echo 'bgpd=yes' >> /etc/quagga/daemons
    systemctl enable zebra.service
    systemctl enable bgpd.service
    systemctl start zebra 
    systemctl start bgpd  
```

Podívejme se teď jaké prefixy Route Server posílá a jaké přijímá. Podíváme se také na síťovou kartu,

```bash
az network routeserver peering list-advertised-routes -g $rg --routeserver route-server -n nva1
{
  "RouteServiceRole_IN_0": [
    {
      "asPath": "65515",
      "localAddress": "10.0.0.4",
      "network": "10.0.0.0/16",
      "nextHop": "10.0.0.4",
      "origin": "Igp",
      "weight": 0
    },
    {
      "asPath": "65515",
      "localAddress": "10.0.0.4",
      "network": "10.1.0.0/16",
      "nextHop": "10.0.0.4",
      "origin": "Igp",
      "weight": 0
    },
    {
      "asPath": "65515",
      "localAddress": "10.0.0.4",
      "network": "10.2.0.0/16",
      "nextHop": "10.0.0.4",
      "origin": "Igp",
      "weight": 0
    }
  ],
  "RouteServiceRole_IN_1": [
    {
      "asPath": "65515",
      "localAddress": "10.0.0.5",
      "network": "10.0.0.0/16",
      "nextHop": "10.0.0.5",
      "origin": "Igp",
      "weight": 0
    },
    {
      "asPath": "65515",
      "localAddress": "10.0.0.5",
      "network": "10.1.0.0/16",
      "nextHop": "10.0.0.5",
      "origin": "Igp",
      "weight": 0
    },
    {
      "asPath": "65515",
      "localAddress": "10.0.0.5",
      "network": "10.2.0.0/16",
      "nextHop": "10.0.0.5",
      "origin": "Igp",
      "weight": 0
    }
  ],
  "value": null
}

az network routeserver peering list-learned-routes -g $rg --routeserver route-server -n nva1
{
  "RouteServiceRole_IN_0": [
    {
      "asPath": "65514",
      "localAddress": "10.0.0.4",
      "network": "10.50.0.0/16",
      "nextHop": "10.0.1.4",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.4",
      "weight": 32768
    },
    {
      "asPath": "65514",
      "localAddress": "10.0.0.4",
      "network": "10.70.0.0/16",
      "nextHop": "10.0.1.4",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.4",
      "weight": 32768
    },
    {
      "asPath": "65514",
      "localAddress": "10.0.0.4",
      "network": "10.60.0.0/16",
      "nextHop": "10.0.1.4",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.4",
      "weight": 32768
    }
  ],
  "RouteServiceRole_IN_1": [
    {
      "asPath": "65514",
      "localAddress": "10.0.0.5",
      "network": "10.50.0.0/16",
      "nextHop": "10.0.1.4",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.4",
      "weight": 32768
    },
    {
      "asPath": "65514",
      "localAddress": "10.0.0.5",
      "network": "10.70.0.0/16",
      "nextHop": "10.0.1.4",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.4",
      "weight": 32768
    },
    {
      "asPath": "65514",
      "localAddress": "10.0.0.5",
      "network": "10.60.0.0/16",
      "nextHop": "10.0.1.4",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.4",
      "weight": 32768
    }
  ],
  "value": null
}

az network nic show-effective-route-table -g $rg -n linux-nvaVMNic -o table
Source                 State    Address Prefix    Next Hop Type          Next Hop IP
---------------------  -------  ----------------  ---------------------  -------------
Default                Active   10.0.0.0/16       VnetLocal
Default                Active   10.1.0.0/16       VNetPeering
Default                Active   10.2.0.0/16       VNetPeering
VirtualNetworkGateway  Active   10.50.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.70.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.60.0.0/16      VirtualNetworkGateway  10.0.1.4
Default                Active   0.0.0.0/0         Internet
Default                Active   10.0.0.0/8        None
Default                Active   100.64.0.0/10     None
Default                Active   192.168.0.0/16    None
Default                Active   25.33.80.0/20     None
Default                Active   25.41.3.0/25      None
```

Perfektní. Přidejme teď nějaké spoke sítě a zajistěme peering do hubu. Uděláme to tak, že spoke bude využívat "gateway" v hubu, tedy že se bude učit sítě "z on-premises" (v našem případě jsou to prefixy z Route Serveru, ale stejné chování znáte i z Azure VPN nebo Express Route Gateway, které mimochodem lze s Route Serverem kombinovat). Až to bude, vytvoříme si VM ve spoke a podíváme se na routovací tabulku na jeho síťovce.

```bash
az network vnet create -n spoke1-net -g $rg --address-prefixes 10.1.0.0/16 --subnet-name sub1 --subnet-prefixes 10.1.0.0/24
az network vnet create -n spoke2-net -g $rg --address-prefixes 10.2.0.0/16 --subnet-name sub1 --subnet-prefixes 10.2.0.0/24
az network vnet peering create -n hub-to-spoke1 \
    -g $rg \
    --vnet-name hub-net \
    --remote-vnet $(az network vnet show -n spoke1-net -g $rg --query id -o tsv) \
    --allow-forwarded-traffic \
    --allow-vnet-access \
    --allow-gateway-transit
az network vnet peering create -n hub-to-spoke2 \
    -g $rg \
    --vnet-name hub-net \
    --remote-vnet $(az network vnet show -n spoke2-net -g $rg --query id -o tsv) \
    --allow-forwarded-traffic \
    --allow-vnet-access \
    --allow-gateway-transit
az network vnet peering create -n spoke1-to-hub \
    -g $rg \
    --vnet-name spoke1-net \
    --remote-vnet $(az network vnet show -n hub-net -g $rg --query id -o tsv) \
    --allow-forwarded-traffic \
    --allow-vnet-access \
    --use-remote-gateways
az network vnet peering create -n spoke2-to-hub \
    -g $rg \
    --vnet-name spoke2-net \
    --remote-vnet $(az network vnet show -n hub-net -g $rg --query id -o tsv) \
    --allow-forwarded-traffic \
    --allow-vnet-access \
    --use-remote-gateways
az vm create -n linux-vm1 \
    -g $rg \
    --image UbuntuLTS \
    --size Standard_B1s \
    --zone 1 \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --public-ip-address vm1-ip \
    --subnet sub1 \
    --vnet-name spoke1-net \
    --storage-sku Standard_LRS

az network nic show-effective-route-table -g $rg -n linux-vm1VMNic -o table
Source                 State    Address Prefix    Next Hop Type          Next Hop IP
---------------------  -------  ----------------  ---------------------  -------------
Default                Active   10.1.0.0/16       VnetLocal
Default                Active   10.0.0.0/16       VNetPeering
VirtualNetworkGateway  Active   10.60.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.70.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.50.0.0/16      VirtualNetworkGateway  10.0.1.4
Default                Active   0.0.0.0/0         Internet
Default                Active   10.0.0.0/8        None
Default                Active   100.64.0.0/10     None
Default                Active   192.168.0.0/16    None
Default                Active   25.33.80.0/20     None
Default                Active   25.41.3.0/25      None
```

Výborně, jsou tam - informace z Route Server v hubu se propagují do VM ve spoke. Podívejme se, že prefixy Azure dostává na oplátku naše NVA.

```bash
ssh tomas@$(az network public-ip show -n nva-ip -g $rg --query ipAddress -o tsv)
    sudo vtysh
        show ip bgp cidr-only

BGP table version is 0, local router ID is 10.0.1.4
Status codes: s suppressed, d damped, h history, * valid, > best, = multipath,
              i internal, r RIB-failure, S Stale, R Removed
Origin codes: i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
   10.0.0.0/16      10.0.0.5                               0 65515 i
                    10.0.0.4                               0 65515 i
   10.1.0.0/16      10.0.0.5                               0 65515 i
                    10.0.0.4                               0 65515 i
   10.2.0.0/16      10.0.0.5                               0 65515 i
                    10.0.0.4                               0 65515 i
*> 10.50.0.0/16     0.0.0.0                  0         32768 i
*> 10.60.0.0/16     0.0.0.0                  0         32768 i
*> 10.70.0.0/16     0.0.0.0                  0         32768 i
```

Všechno funguje - dalším krokem bude redundance.

# Redundantní NVA a konvergence BGP
Náš scénář teď obohatíme o další NVA. Teď začne být vidět síla dynamického směrovacícho protokolu. Místo nutnosti řešit to jako cluster s balancerem před prvky se můžeme spolehnout na čisté L3 řešení s BGP. Navíc k této dvojici bychom pak klidně mohli přidat další, která by měla jinou roli. Typicky by to například mohla být dvojice NVA zajišťující konektivitu (VPN, SD-WAN) a jiná dvojice NVA fungující jako firewall. Něco co je v klasickém řešení postaveném na UDR poměrně komplikované se stane jednodušším a síťařsky pochopitelnějším.

Přidám druhou NVA v jiné zóně dostupnosti.

```bash
az network routeserver peering create --routeserver route-server -g $rg --peer-ip 10.0.1.5 --peer-asn 65514 -n nva2
az vm create -n linux-nva2 \
    -g $rg \
    --image UbuntuLTS \
    --size Standard_B1ms \
    --zone 2 \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --public-ip-address nva2-ip \
    --private-ip-address 10.0.1.5 \
    --subnet NvaSubnet \
    --vnet-name hub-net \
    --storage-sku Standard_LRS

ssh tomas@$(az network public-ip show -n nva2-ip -g $rg --query ipAddress -o tsv)
    sudo -i
    apt update
    apt install quagga quagga-doc -y
    sysctl -w net.ipv4.ip_forward=1
    cat > /etc/quagga/zebra.conf << EOF
hostname Router
password zebra
enable password zebra
interface eth0
interface lo
ip forwarding
line vty
EOF
    cat > /etc/quagga/vtysh.conf << EOF
!service integrated-vtysh-config
hostname quagga-router
username root nopassword
EOF
    cat > /etc/quagga/bgpd.conf << EOF
hostname bgpd
password zebra
enable password zebra
router bgp 65514
! bgp router-id 10.0.0.1
network 10.50.0.0/16
network 10.60.0.0/16
network 10.70.0.0/16
neighbor 10.0.0.4 remote-as 65515
neighbor 10.0.0.4 soft-reconfiguration inbound
neighbor 10.0.0.5 remote-as 65515
neighbor 10.0.0.5 soft-reconfiguration inbound
line vty
EOF
    chown quagga:quagga /etc/quagga/*.conf
    chown quagga:quaggavty /etc/quagga/vtysh.conf
    chmod 640 /etc/quagga/*.conf
    echo 'zebra=yes' > /etc/quagga/daemons
    echo 'bgpd=yes' >> /etc/quagga/daemons
    systemctl enable zebra.service
    systemctl enable bgpd.service
    systemctl start zebra 
    systemctl start bgpd  
```

Podívejme se jak to ovlivnilo routing v Azure. Všimněte si skvělé zprávy - v tabulce jsou hopy do obou appliance a mezi nimi se balancuje (ECMP).

```bash
az network nic show-effective-route-table -g $rg -n linux-vm1VMNic -o table
Source                 State    Address Prefix    Next Hop Type          Next Hop IP
---------------------  -------  ----------------  ---------------------  -------------
Default                Active   10.1.0.0/16       VnetLocal
Default                Active   10.0.0.0/16       VNetPeering
VirtualNetworkGateway  Active   10.60.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.60.0.0/16      VirtualNetworkGateway  10.0.1.5
VirtualNetworkGateway  Active   10.70.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.70.0.0/16      VirtualNetworkGateway  10.0.1.5
VirtualNetworkGateway  Active   10.50.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.50.0.0/16      VirtualNetworkGateway  10.0.1.5
Default                Active   0.0.0.0/0         Internet
Default                Active   10.0.0.0/8        None
Default                Active   100.64.0.0/10     None
Default                Active   192.168.0.0/16    None
Default                Active   25.33.80.0/20     None
Default                Active   25.41.3.0/25      None
```

Co kdybychom se teď rozhodli, že zatímco u sítí 10.50.0.0/16 a 10.70.0.0/16 nám rozdělení zátěže vyhovuje, ale pro síť 10.60.0.0/16 potřebujeme fungovat active/passive? Stačí použít klasické BGP konstrukty, tedy BGP AS PATH prepending na nva2, čímž cestu prodloužíme a Azure tak bude pro tento prefix preferovat nva1 - nicméně pokud nva1 vypadne, začne to posílat do nva2.

```bash
ssh tomas@$(az network public-ip show -n nva2-ip -g $rg --query ipAddress -o tsv)
    sudo -i
    cat > /etc/quagga/bgpd.conf << EOF
hostname bgpd
password zebra
enable password zebra
router bgp 65514
network 10.50.0.0/16
network 10.60.0.0/16
network 10.70.0.0/16
neighbor 10.0.0.4 remote-as 65515
neighbor 10.0.0.4 soft-reconfiguration inbound
neighbor 10.0.0.4 route-map r60map out
neighbor 10.0.0.5 remote-as 65515
neighbor 10.0.0.5 soft-reconfiguration inbound
neighbor 10.0.0.5 route-map r60map out
line vty
!
ip prefix-list r60 seq 10 permit 10.60.0.0/16
ip prefix-list any seq 10 permit any
route-map r60map permit 10 
match ip address prefix-list r60
set as-path prepend 65514
route-map r60map permit 20 
match ip address prefix-list any
!
EOF
    systemctl restart bgpd
    exit
    exit
    exit

az network routeserver peering list-learned-routes -g $rg --routeserver route-server -n nva2
{
  "RouteServiceRole_IN_0": [
    {
      "asPath": "65514",
      "localAddress": "10.0.0.4",
      "network": "10.70.0.0/16",
      "nextHop": "10.0.1.5",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.5",
      "weight": 32768
    },
    {
      "asPath": "65514",
      "localAddress": "10.0.0.4",
      "network": "10.50.0.0/16",
      "nextHop": "10.0.1.5",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.5",
      "weight": 32768
    },
    {
      "asPath": "65514-65514-65514",
      "localAddress": "10.0.0.4",
      "network": "10.60.0.0/16",
      "nextHop": "10.0.1.5",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.5",
      "weight": 32768
    }
  ],
  "RouteServiceRole_IN_1": [
    {
      "asPath": "65514",
      "localAddress": "10.0.0.5",
      "network": "10.70.0.0/16",
      "nextHop": "10.0.1.5",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.5",
      "weight": 32768
    },
    {
      "asPath": "65514",
      "localAddress": "10.0.0.5",
      "network": "10.50.0.0/16",
      "nextHop": "10.0.1.5",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.5",
      "weight": 32768
    },
    {
      "asPath": "65514-65514",
      "localAddress": "10.0.0.5",
      "network": "10.60.0.0/16",
      "nextHop": "10.0.1.5",
      "origin": "EBgp",
      "sourcePeer": "10.0.1.5",
      "weight": 32768
    }
  ],
  "value": null
}

az network nic show-effective-route-table -g $rg -n linux-vm1VMNic -o table
Source                 State    Address Prefix    Next Hop Type          Next Hop IP
---------------------  -------  ----------------  ---------------------  -------------
Default                Active   10.1.0.0/16       VnetLocal
Default                Active   10.0.0.0/16       VNetPeering
VirtualNetworkGateway  Active   10.60.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.70.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.70.0.0/16      VirtualNetworkGateway  10.0.1.5
VirtualNetworkGateway  Active   10.50.0.0/16      VirtualNetworkGateway  10.0.1.4
VirtualNetworkGateway  Active   10.50.0.0/16      VirtualNetworkGateway  10.0.1.5
Default                Active   0.0.0.0/0         Internet
Default                Active   10.0.0.0/8        None
Default                Active   100.64.0.0/10     None
Default                Active   192.168.0.0/16    None
Default                Active   25.33.80.0/20     None
Default                Active   25.41.3.0/25      None
```

Na závěr důležitá poznámka - Route Server naprogramuje toto směrování i na samotný NVA subnet. Na to dejte pozor, pokud chcete z NVA propagovat default route 0.0.0.0/0, tedy že veškerý provoz má jít přes vaše NVA. Tím ale samotnému NVA odříznete Internet (bude to posílat samo na sebe). Proto v takovém případě na NVA subnetu udělejte UDR se statickým záznamem 0.0.0.0/0 -> Internet (statika v UDR má vždy přednost před dynamickým směrováním). 


# Kdy tedy Route Server použít?

Pokud chcete hub and spoke s vysokou mírou kontroly (tedy postavíte si ho sami), doporučuji použít nativních prvků jako je Azure VPN, Azure Express Route Gateway a Azure Firewall. Je to jednodušší a lépe automatizovatelné.

Pokud chcete ještě jednodušší řešení, kdy vám Azure bude cesty spravovat sám a topologii hub and spoke pro vás postaví, použijte Azure Virtual WAN. Ta podporuje pro bezpečnost Azure Firewall i postupně některé firewally třetích stran. Varianta Virtual WAN je určitě budoucnost. Má dnes nějaká omezení pro veliké zákazníky, ale je to skvělá volba, které se budu v článcích ještě věnovat.

No a pak je tu třetí varianta. Chcete si do cloudu přinést své síťové prvky. Svého oblíbeného poskytovatele VPNky, preferovaný firewall, vlastní SD-WAN appliance. Skládat si hub and spoke klasicky je v takovém případě náročné a některé modely redundance nabízené výrobci NVA jsou řekněme kostrabaté (např. firewall si bude sám přenastavovat UDR ve všech spoke ... představte si dopad toho, že výrobce firewallu udělá chybu nebo že ve firmě nepoužijete least privilege speciální roli jen na změny UDR a dáte do firewallu účet s právem měnit veškerý networking v celé firmě nebo ještě hůř tam z lenosti přistane Contributor a s pravidelnou rotací hesel se nebudete moc obtěžovat ... brrr). V takovém případě je Azure Route Server skvělé řešení. Aktuálně je v preview, ideální čas vyzkoušet a připravit se na případné nasazení jakmile bude plně dostupný.


