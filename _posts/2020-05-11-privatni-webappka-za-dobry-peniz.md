---
layout: post
published: true
title: Privátní leč cenově dostupná WebApp díky Private Link pro App Service v Azure
tags:
- Networking
- Security
- AppService
---
Azure Applicaiton Services a především její slavná WebApp je jedna z nejstarších a nejpoužívanějších služeb Azure společně s Azure SQL. Původně začala jako platforma pro provoz .NET aplikací, ale už před pěti lety uměla Javu a další jazyky a v posledních letech přišla i podpora kontejnerů a Linux verze včetně bring your own container. Pokud potřebujete provozovat webovou aplikaci jednoduše a bez starostí, tohle je ideální volba. Nemusíte řešit OS, patchování, infrastrukturu, škálování, A/B testing, canary release a tak podobně - na tohle všechno je tam tlačítko. Současně je to velmi jednoduché, takže nemusíte investovat rok práce do dokonalého zvládnutí platforem typu Kubernetes. Zkrátka webová appka s pár komponentama má parádní místo právě v této platformní službě. Komplikovanější mikroslužbová architektura si určitě zaslouží Azure Kubernetes Service a některý legacy kód zase nezbyde, než provozovat IaaS způsobem třeba na farmě z Virtual Machine Scale Set.

Takovou bolístkou ale vždy bylo to, že je to platformní služba a neběží ve VNETu. Jak z ní volat onpremises zdroje, třeba nějaké interní API, které je zastaralé a z bezpečnostních důvodů je nelze vystavit do Internetu - musí to jít přes VPN nebo Express Route. A co přístup uživatelů? To by dnes ideálně mělo být přes veřejný endpoint a soustředit se na identitní perimetr s Azure Active Directory, ale ne vždy je aplikace připravena na takové moderní zacházení a potřeba vystavit aplikaci pouze interně zkrátka existuje. Jak se s tím dnes umí WebApp vypořádat?

# Ultimátní single-tenant varianta - Application Services Environment
Než byly ASE prostředí k dispozici mohli zákazníci jít cestou single-tenant varianty. Jak to funguje? App Service je docela složitý systém s několika komponentami, zdaleka to není jen IIS pro vaší appku. Součástí řešení je reverse proxy pro frontendy, eventové komponenty usnadňující automatické stahování nových verzí kódu aplikace, řídící systémy pro updatování celého clusteru a tak dále. Typicky má cluster přes 1000 VM a je multi-tenantní, takže zákazník z něj dostane konkrétní VMka jen pro sebe (tam je totální izolace na úrovni přidělených zdrojů apod.), ale pomocné komponenty i síťové prvky (reverse proxy) jsou sdílené s logickou izolací. To má dva zásadní efekty. Tím prvním je, že náklady na pomocné komponenty se rozpustí mezi 1000 mašin zákazníků a to výrazně sníží cenu. Druhý efekt je to, že cluster je hodně velký a je tak možné v něm udržovat volnou kapacitu ve formě přednastartovaných strojů, takže velmi rychle jsou zdroje k dispozici pro vaší aplikaci, když potřebuje přidat nody.

ASE umožňuje vystavit tohle celé jen pro vás ve vašem VNETu, takže komunikace na backend i přístup na frontend je součástí vaší sítě. Nicméně má to i tři méně příjemné vlastnosti:
- Platforma je celá jen pro vás, takže realizujete nižší výnosy z rozsahu - pomocné komponenty musíte zaplatit, takže zejména pro použití pro malé aplikace vyjde o dost dráž (nicméně pro velké aplikace už to tak velký rozdíl není).
- Cluster je menší, nové nody se pro vás vyrábějí, nejsou přednastartované - takže rychlost zvýšení kapacity pro potřeby aplikace je nižší, než v případě běžné App Service (např. 1 minuta vs. 5-10 minut).
- Síťaři a bezpečáci jsou sice spokojeni, že je aplikace uvnitř VNETu, ale i tak lze očekávat v tomto směru velké diskuse - přesunutím PaaS do VNETu sice vyřešíte problém komunikaci uživatelů uvnitř VNETu, ale objeví se nový problém, jak do toho bude chodit Microsoft - je to platformní služba, takže chcete aby se vám o ni Microsoft staral, ale ten se tam tudíž musí dostat a je nutné udělat prostupy.

Z těhto tří důvodů není u mých zákazníků používání ASE příliš rozšířené až na situace, kdy dokáží ASE cluster využít pro větší množství aplikací a security tým nemá problém otevřít Microsoftu vrátka pro správu řešení.

# Přístup z aplikace do VNETu (volání backendu)
První a častější požadavek je na to, aby aplikace mohla přistupovat ke zdrojům ve VNETu. To by typicky bylo nějaké VM v Azure s backendem (které nejde z nějakého důvodu přenést do App Service), nějaké API v on-premises (SAP apod.) a v dnešní době i třeba Private Link nějaké platformní služby typu Azure SQL (tedy snaha zamknout SQL jen na přístupy z konkrétní aplikace). To se dřív dělalo tak, že node platformy vytáčel P2S VPN spojení do Azure VPN. Dnes je ale plně v GA možnost napojit aplikaci do VNETu napřímo. V rámci preview tam ještě byla určitá omezení (například nebyla podpora pro sítě s UDR, což byl zásadní problém v enterprise topologii), ale ta s uvedením do GA padla.

Zapneme si VNET integraci na WebApp.

![](/images/2020/2020-03-18-13-24-23.png){:class="img-fluid"}

![](/images/2020/2020-03-18-13-24-54.png){:class="img-fluid"}

Průvodce pro nás vytvoří nový subnet. Ten musí být prázdný a nastaví se v něm automaticky delegace, tedy dostane se pod správu App Service, která si do něj bude umět napojit vaše nody.

![](/images/2020/2020-03-18-13-26-16.png){:class="img-fluid"}

Vyzkoušíme a skutečně funguje!

![](/images/2020/2020-03-18-13-29-12.png){:class="img-fluid"}

Tuto integraci můžete využít už od plánů Standard (včetně S1).

# Přístup uživatelů k aplikaci z VNETu (frontend)
App Services mají jako součást služby reverse proxy, která běží na public endpointu a na něm provádí směrování, filtrace a další věci, které nastavíte. Podporuje jak IP based řešení (do DNS serveru si zadáváte A záznam) i CNAME based a SNI, nicméně tento endpoint je stále public. Je to podobné jako u platformních služeb typu SQL. Nově jste ale schopni v rámci subnetu VNETu vytvořit Private Link - privátní IP adresu, pod kterou budete ke službě přistupovat. Public endpoint zakážete a jediná povolená komunikace bude přes privátní endpoint Private Linku.

Tato funkce není dostupná u nižších nebo starších clusterů, budete potřebovat použít plán Premium v2. Nicméně ten bych pro produkci stejnak doporučoval - je sice dražší, ale běží pod ním silnější stroje (CPU je víc jak 2x silnější, než u Standard), takže poměr cena/výkon je ve skutečnosti lepší. V každém případě u malé aplikace je to stále výrazně levnější a jednodušší, než použít Application Services Environment (PaaS uvnitř VNETu).

Vytvořme tedy Private Link.

![](/images/2020/2020-05-08-11-16-34.png){:class="img-fluid"}

![](/images/2020/2020-05-08-11-17-07.png){:class="img-fluid"}

![](/images/2020/2020-05-08-11-17-34.png){:class="img-fluid"}

![](/images/2020/2020-05-08-11-18-05.png){:class="img-fluid"}

![](/images/2020/2020-05-08-11-18-23.png){:class="img-fluid"}

To je celé! Moje WebApp teď má privátní IP adresu. Aby fungovala i z pohledu certifikátů a DNS, musíme mít správně DNS záznamy - o to se postaral průvodce alespoň co do výchozího jména. Ověřím si, že DNS vrací privátní adresu a připojím se zevnitř VNETu. Funguje!


```bash
tomas@webapp-test-vm:~$ host mojetestovaciwebapp.azurewebsites.net
mojetestovaciwebapp.azurewebsites.net is an alias for mojetestovaciwebapp.privatelink.azurewebsites.net.
mojetestovaciwebapp.privatelink.azurewebsites.net has address 10.0.1.5

tomas@webapp-test-vm:~$ curl https://mojetestovaciwebapp.azurewebsites.net
<!DOCTYPE html><html lang="en">
...
```

A co když chcete vlastní doménové jméno? V tuto chvíli v rámci preview to lze, ale ověření musí být public - tzn. toto doménové jméno musí být dosažitelné přes veřejné DNS servery, aby mohla platforma ověřit vlastnictví vaší domény. Platforma vám specifikuje TXT record, který musíte zadat a ten musí být dosažitelný zvenku (v rámci General Availability je možné, že budou i jiné metodoy ověření domény). Samotný A záznam pak může být interní (split horizon). Aktuálně tedy domény, které nemáte koupené (např. intranet.local) použít nelze.

Nové možnosti integrace WebApp do sítě jsou myslím velmi zásadní přínos. Dokážete elegentně využít plně platformní službu se všemi výhodami a přitom je začleněna do vaší sítě jak z aplikace ven, tak od uživatelů k aplikaci aniž by bylo nutné používat finančně náročné a méně flexibilní služby typu Application Services Environment.
