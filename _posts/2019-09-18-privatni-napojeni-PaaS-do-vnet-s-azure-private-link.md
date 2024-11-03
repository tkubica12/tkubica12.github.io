---
layout: post
title: Privátní napojení PaaS služeb do VNETu s Azure Private Link
tags:
- Security
- Networking
- Storage
- SQL
---
Existují platformní služby, které v single-tenant režimu napojíte rovnou do VNETu (tedy na privátní adresy) a můžete je pak využívat z IaaS infrastruktury nebo přes Azure VPN či Express Route. Tyto alternativy ale mohou mít trochu jinou funkčnost a mohou být dražší (což je logické, protože jsou single-tenantní a tím pádem nevyužijete tolik výnosů z rozsahu).

Klasické PaaS služby jako je Azure SQL, Blob Storage, Key Vault a velké množství dalších, jsou provozovány na public endpointu. Nicméně je před nimi firewall, takže můžete přístup k nim omezit jen na zvolené public IP adresy. Další možnost je Service Endpoint, který už funguje na většinu PaaS služeb. Ten vytvoří tunel mezi subnetem vašeho VNETu a PaaS, nicméně ta i nadále zůstává na public endpointu (byť se k ní nedostanete z Internetu, pokud to zakážete). Jenže tato varianta funguje pouze mezi VM v konkrétním subnetu VNETu a PaaS službou, protože tunel vzniká uvnitř Azure z VM napřímo. Nefunguje to pro přístup přes roztaženou privátní síť ať už je to VNET peering nebo on-premises za IPSec VPNku jako je Azure VPN nebo private peering na Express Route.

Novým řešením v preview je Private Link. Ve vašem VNETu vznikne jakási virtuální proxy, která bude mít IP adresu z VNETu a ta bude zprostředkovávat tunelem komunikaci s PaaS službou. Výhodou je, že to funguje přes VPN a nemusíte VM vůbec povolovat outbound spojení do Internetu nebo klidně třeba cesty ven hnát přes on-premises (byť to není výkonnostně dobrá architektura). Další příjemnou vlastností je, že Private Link vás napojuje na konkrétní instanci vaší PaaS služby, zatímco většina Service Endpointů vytváří tunel do PaaS služby genericky (tedy ne na přímo váš storage account, ale na storage službu jako takovou včetně jiných zákazníků). Tím je private link ještě o něco bezpečnější, protože znemožňuje vynést data třeba na jiný storage account. Nevýhodou je, že služba je zatím v preview a bude se na služby přidávat postupně. Druhou nevýhodou je, že s tímto řešením jsou spojeny nějaké náklady (byť ne nějak velké). V ceníku je jednak platba za instanci private endpointu jako takového a také poplatek ze přenášená data. Pojďme se dnes na Private Link podívat.

Zaměřím se na Private Link pro Azure PaaS. V příštím díle se podíváme na další zajímavou možnost a to je Private Link pro vaše vlastní služby (můžete zprovoznit něco svého a poskytnout to kolegům, partnerům či zákazníkům privátně aniž byste museli propojovat svoje VNETy).

# Jak private link funguje
V zásadě si představme Private Link jako virtuální síťový port, který zaklapne do vašeho VNETu a vezme si z něj IP. S touto IP můžete komunikovat uvnitř VNETu, ale i přes VNET peering nebo VPNku. Tento virtuální port má nastavenu konkrétní PaaS instanci, na kterou je schopen provoz odvážet. Tato komunikace nikdy nejde přes Internet, běží na backbone Microsoft sítě v tunelu, do kterého se nikdo zvenku nedostane a míří do konkrétní instance služby - tedy ne genericky do storage služby, ale do vašeho storage accountu.

Kromě nativních PaaS služeb může být na druhé straně Private Linku i vaše vlastní služba (Private Link Service), ale k tomu se dostaneme příště.

Nutno ještě poznamenat, že v rámci preview jsou tu jistá (a typicky dočasná) omezení. Služba je dostupná jen v určitých regionech, nemá zatím SLA a je omezena jen na některé služby jako je Azure SQL nebo Azure Storage. Jsou tam ještě nějaké další dočasné překážky, například nefunguje to pro přístup z některých single-tenant služeb (App Service Isolated, Azure Container Instances ve VNETu), nemůžete na traffic endpointu nasadit NSG a nefunguje dohromady v jednom subnetu se zapnutým Service Endpoint nebo delegovaným subnetem (to se používá u některých služeb jako je Azure NetApp Files, které musíte dát do jiného subnetu, než Private Endpoint).

Jak dále uvidíte, síťařská část z pohledu IP je opravdu jednoduchá a intuitivní. Složitější je situace s DNS. Jde o to, že služby používají TLS šifrování a mají certifkát vystavený na nějaké jméno, například *.blob.core.windows.net (kde * je jméno accountu) a pokud přistupujete třeba rovnou na privátní IP nebo úplně jinou URL, tak se to SDK nebude líbit. Ale to brzy uvidíme.

# Vyzkoušejme Azure Files
Tento příklad je ten nejsnazší, protože mapování SMB protokolem nemá problém s tím, pod jakým jménem nebo adresou se Azure Files ptáme. V zásadě tedy ani nemusíme DNS vůbec použít a jít rovnou na IP - zkusme si to.

Mám VM ve VNETu, storage account a teď v tomto VNETu vytvoříme Private Link. 

![](/images/2019/2019-09-17-21-58-27.png){:class="img-fluid"}

V Private Link Center je i hezký obrázek, který vysvětluje, že na endpoint se dostaneme i přes VPNku.

![](/images/2019/2019-09-17-21-59-12.png){:class="img-fluid"}

Založme nový Private Link.

![](/images/2019/2019-09-17-21-59-51.png){:class="img-fluid"}

V prvním kroku vyberu resource group a zadám název linku. Služba je v preview dostupná jen v některých regionech v US.

![](/images/2019/2019-09-17-22-00-50.png){:class="img-fluid"}

V dalším kroku si vyberu svůj storage account a službu File. Private Link můžete použít i napříč tenanty, takže místo vybírání můžete zadat přímo ID zdroje (a následuje pak nutnost schválit ještě na druhé straně).

![](/images/2019/2019-09-17-22-02-14.png){:class="img-fluid"}

Vyberu si v jakém VNETu a v jakém subnetu chci endpoint vytvořit. V subnetu klidně mohou být i jiné zdroje a dostanete se do něj z jiných subnetů, přes VNET peering i VPNku. Pro případ Files nebude nutné řešit DNS, tak zvolím No.

![](/images/2019/2019-09-17-22-03-39.png){:class="img-fluid"}

To je všechno a musíme minutku počkat. Pak už vidím svůj endpoint. Zajímavé bude kliknout na jeho NIC.

![](/images/2019/2019-09-17-22-05-02.png){:class="img-fluid"}

Obrazovka vám určitě připomíná běžnou NIC pro VM. Tady sice žádné VM nevidíme, ale chová se to jako síťovka v subnetu. Můžeme tedy například nastavit privátní IP staticky.

![](/images/2019/2019-09-17-22-06-20.png){:class="img-fluid"}

Podívám se do svých Azure Files, vytvořím share a na tlačítku Connect mám návod, jak si je namapovat do Windows jako síťový disk:

```
cmdkey /add:mojeprivatnistorage.file.core.windows.net /user:Azure\mojeprivatnistorage /pass:7pFOkooPJPyJ0D2jIBqCGDl/j0Jth61TsFRGHJWxxl6drzHXYm6UXzMbKgpT17ryAhut+FmPf2wC5JBnrCpEPA==
net use Z: \\mojeprivatnistorage.file.core.windows.net\share /persistent:Yes
```

Nicméně to je URL pro public endpoint, tak ji pojďme změnit za privátní adresu, kterou jsme našli na private endpointu.

```
cmdkey /add:10.1.1.5 /user:Azure\mojeprivatnistorage /pass:7pFOkooPJPyJ0D2jIBqCGDl/j0Jth61TsFRGHJWxxl6drzHXYm6UXzMbKgpT17ryAhut+FmPf2wC5JBnrCpEPA==
net use Z: \\10.1.1.5\share /persistent:Yes
```

A je to. Přistoupil jsem do Azure Files přes privátní endpoint ve VNETu a všechno funguje. Je čas to zavřít a znemožnit jakýkoli jiný přístup zvenku.

![](/images/2019/2019-09-17-22-10-51.png){:class="img-fluid"}

I přes zamezení prakticky všeho mi komunikace přes private link funguje.

Výborně. Tohle bylo opravdu jednoduché a nemuseli jsme se trápit s DNS.

# Vyzkoušejme Azure SQL
Připravil jsem si Azure SQL DB, na VM nainstaloval Azure Data Studio a vyzkoušíme privátní přístup do této služby. Aby to bylo ještě veselejší, tento Azure SQL je v jiném regionu, než je můj VNET.

![](/images/2019/2019-09-17-22-27-44.png){:class="img-fluid"}

Tentokrát si nechám založit také záznam v Azure Private DNS. Ta mi bude dělat vnitřní překlady jmen v rámci Azure (nicméně on-premises mi neřeší, o tom později).

![](/images/2019/2019-09-17-22-32-04.png){:class="img-fluid"}

Takhle vypadá privátní zóna, kterou průvodce založil.

![](/images/2019/2019-09-17-22-36-14.png){:class="img-fluid"}

Řešení s privátní DNS udělá ještě jednu zajímavost. Kromě A záznamu na doméně privatelink.database.windows.net nám začne vracet i modifikovaný záznam na klasické doméně database.windows.net, takže aplikace nasazené v Azure nemusí měnit svůj connection string.

```bash
dig mujprivatniserver.privatelink.database.windows.net

;; ANSWER SECTION:
mujprivatniserver.privatelink.database.windows.net. 1800 IN A 10.1.1.6



dig mujprivatniserver.database.windows.net

;; ANSWER SECTION:
mujprivatniserver.database.windows.net. 300 IN CNAME mujprivatniserver.privatelink.database.windows.net.
mujprivatniserver.privatelink.database.windows.net. 1799 IN A 10.1.1.6
```

Zkusíme se z VM ve VNETu připojit na privátní endpoint.

![](/images/2019/2019-09-17-22-42-14.png){:class="img-fluid"}

Funguje.

![](/images/2019/2019-09-17-22-42-40.png){:class="img-fluid"}

Musíme ale zmínit, že v případě Azure SQL klient ověřuje certifikát a server opravdu musí být na správném FQDN (pokud nechcete vypnout ověřování certifikátů, což rozhodně nechcete). Pokud zadáte jen IP adresu nebo mujprivatniserver.privatelink.database.windows.net tak se nepřipojíte. Azure internal DNS to řeší elegantně přepsáním odpovědi na public FQDN (jak jsme si ukazovali - CNAME na privátní FQDN a to na A záznam). Pokud potřebujete vyřešit třeba v on-premises na vlastním DNS serveru, budete to muset udělat sami. Tedy přepsat public odpověď na privátní endpoint a to buď tak jak to dělá Azure private DNS krokem přes CNAME nebo natvrdo A záznamem.

A mimochodem - Azure SQL mám opravdu v jiném regionu, než je VNET s VM.

# Vyzkoušejme Blob Storage
Budeme postupovat stejně - připravíme private link a DNS záznamy a pak budeme zkoušet Storage Explorer.

Funguje jako normálně včetně vylistování storage accountů v subskripci stejně jako přímým zápisem connection stringu. Jen nezapomeňte na to, že pokud storage accountu zamezíte jakýkoli přístup jinak než přes private link a vytvoříte link jen na Blob, ale ne na třeba Table, tak kliknutí na Table hodí chybovou hlášku (ale to je logické).


Private Link je funkce, která určitě potěší zejména ty z vás, co máte velmi složitou a přísnou síťovou bezpečnostní politiku a topologii. Doufejme, že se Private Link brzo dostane do GA a rychle se rozšíří na další regiony a služby. Příště se mrkneme na to, jak můžete Private Link namířit nejen na PaaS od Microsoftu, ale od kohokoli jiného, kdo ji vystaví v Azure a bude chtít - váš kolega, váš obchodní partner nebo dodavatel nějakého SaaS řešení.

