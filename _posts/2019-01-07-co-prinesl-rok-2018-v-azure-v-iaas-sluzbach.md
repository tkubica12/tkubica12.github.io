---
layout: post
status: publish
published: true
title: Co přinesl rok 2018 v Azure v IaaS službách
tags:
- Compute
- Storage
---
Co nového představil Azure v roce 2018 v oblasti compute a storage? Stejně jako loni se pokusím ohlédnout a zjistit, co všechno se dá za jediný rok stihnout. V roce 2017 se to hodně točilo kolem compute, 2018 bylo především ve znamení novinek ve storage.

# Compute
Rok 2017 zaznamenal masivní příval dramatických změn v oblasti virtuálních mašin a první polovina 2018 byla spíše ve znamení dobíhání těchto novinek a uvádění do General Availability. Přesto v druhé polovině roku pár důležitých oznámení přišlo.

## Nové vysoce výkonné H-series mašiny pro HPC a jiné náročné výpočty
Pokud provádíte náročné výpočty a nejzásadnější je pro vás brutální rychlost připojení paměti, použijte novou řadu HB postavenou na procesorech AMD EPYC 7551 (zatím stále v Preview). Ta nabízí 260GB/s přístup do paměti. Pokud vám jde spíš o co největší výkon samotného CPU, koukněte na řadu HC postavenou na Intel Xeon Platinum 8168 s výkonem běžně 3,4 GHz (řada H má vždy vypnutý hyperthreading, dostáváte tedy fyzické core a můžete tak skutečně pro většinu výpočtů počítat s možností burstingu).

## Novinky v grafických řadách
Rok 2017 znamenal příval NC řad a to až do extrémně výkonné NVIDIA V100 v řadě NCv3, která v roce 2018 přešla do General Availability. V roce 2018 přišlo preview vylepšení NV řady (NVv2), tedy varianty pro pracovní stanici, která ponechala kartu M60, ale přidala podporu SSD storage. Další preview je NDv2. Jde o jen jedinou velikost a to monstrózní výpočetní stroj čítající 40 výkonných Skylake core, 672 GB RAM a především 8x V100 karet propojených přes vysokorychlostní NVLINK.

## Confidential Computing s řadou DC
Novinkou je specifická řada DC, která nově nabízí compute zdroje s podporou bezpečných enkláv pro řešení typu Encryption in Use. Procesor podporuje Intel SGX implementaci právě pro tento velmi zajímavý nový typ bezpečnosti. Zatím je DC řada v private preview, tak se těším na 2019 jak se bude rozvíjet. Kromě samotného železa je prvním kandidátem na využití této funkce Azure SQL s Always Encrypted (šifrování na klienstké straně před posláním do DB). Za normálních okolností totiž DB datům nerozumí, takže vám nemůže vyhledávat, počítat agregace a tak podobně. Enkláva by mohl být výborný způsob, jak dát DB možnost s daty pracovat, aniž by se obsah paměti stal čitelným zvenku nebo aniž by superadministrátor mohl provést dump dat.

# Storage
Ve storage byl rok 2017 docela klidný, v compute naopak. 2018 na tom byl obráceně.

## Standard SSD
Točivé disky (HDD) jsou levné, ale méně výkonné. Skok na Premium SSD je ale poměrně velký. Možná vás netrápí IOPS ani přenosová rychlost, ale potřebujete lepší latenci. Na to se Standard SSD perfektně hodí. Není o moc dražší a v latenci přístupu je na tom podstatně lépe.

## Větší a rychlejší disky
Standard HDD se postupně dostalo až na 32TB na jediném disku, takže už nemusíte skládat velké disky v operačním systému, když jdete po kapacitě. Navíc od velikosti 8TB roste i výkonnost (což dříve u Standard HDD nebylo) a to až na 2000 IOPS a přenosy 500 MB/s.

Premium SSD rovněž navýšilo maximální velikosti a s tím spojené rychlosti. Největší P80 s kapacitou 32TB nabízí 20 000 IOPS a 750 MB/s přenosové pásmo.

## Ultra SSD
Největší novinkou (zatím stále v Preview) jsou ale jednoznačně disky typu Ultra SSD. Zcela přepracovaná technologie nabízí extrémně vysoké IOPS až 160 000 na jediný disk. Ještě zajímavější je oddělení kapacity od výkonu, tedy platí se za kapacitu + výkon. Můžete tak mít výkonný, ale relativně malý disk nebo naopak hodně velký disk, ale bez nutnosti mít u něj maximální možný výkon.

## Premium Blob a Files
Další revoluce je v objektové a souborové storage, do které přichází Premium varianta postavená na SSD. Samozřejmě pro zálohování a běžnou práci budete i nadále používat standardní typ služby, ale občas je potřeba mít vyšší výkon. Tak například Azure Files můžete chtít jako share namapovat přímo k aplikaci a v souborech mít třeba databázi nebo zdroje potřebné pro nějaké počítání či grafickou práci. Dobrým příkladem jsou stavové kontejnery v Azure Kubernetes Service nebo zpracování dat náročné na přístup k nim.

## Data Lake Storage gen2
Pro ty co potřebují k datům přistupovat přes HDFS protokol, typicky pro datovou analytiku jako je Hadoop či Spark, nabízel Azure speciální typ takové storage. Nová generace Storage Account dnes dokázala pod jednou storage technologií kromě přístupů diskových, blob, files, table a queue přidat právě i HDFS. Výsledek? Jednodušší a levnější řešení pro váš data lake v Azure.

## Rodina Data Box
Už v roce 2017 bylo možné poslat do Microsoftu disky s daty pro jejich nahrání do storage. V roce 2018 ale přišla celá řada Data Box produktů. Jednak pro offline přenosy, kde si můžete objednat dodávku jak disků, tak krabice i doslova bedny s velkou kapacitou. Kromě toho existují i online produkty jako je Data Box Gateway, virtuální appliance pro synchronizaci dat do Azure, a Data Box Edge, pronajatá bednička pro synchronizaci dat i jejich lokální zpracování před odesláním.

## Statické weby v Azure Blob Storage
Blob storage používá standardní HTTP protokol a v roce 2018 se přidala možnost servírování defaultních souborů a chybových hlášek, což umožňilo hostování statických webů přímo z Azure Storage. Přesně na této technologii je postaven aktuálně tento blog.

## Immutable storage, soft-delete a automatická archivace
Z pohledu práce s Blob storage se v roce 2018 přidala řada zajímavých vylepšení. Je možné nastavit politiky pro automatické přesouvání nepoužívaných souborů mezi tiery (Hot, Cool, Archive) nebo jejich automatické mazání po uplynutí nějaké doby. Dále je tu možnost soft-delete, tedy něco jako odpadkový koš pro vaši Blob storage. Nejvýznamnější novinkou ale určitě byla storage typu WORM neboli immutable storage. Máte možnost zakázat jakékoli změny uložených dat například po nějakou dobu. Soubor se nedá smazat ani změnit a to ani administrátorem. Ideální pro dodržení zákonných a jiných podmínek uchovávání dokumentů po nějakou dobu.

## Zónově redundantní storage nové generace
Klasická storage podporovala kromě lokální redundance (LRS) a globální redundance (GRS) také zónovou (ZRS). Tři kopie dat se zapisovaly do různých datových center typicky ve stejném regionu. S uvedením zón dostupnosti pro compute vznikla potřeba stejné garance a mechanismus přinést i do storage a vznikla ZRS nové generace, která kopíruje zóny dostupnosti pro compute. Durabilita LRS je designována na 11 devítek, GRS cílí na 16 devítek a ZRS přináší 12 devítek. SLA (finanční závazek ze strany Microsoftu) na dostupnost je u LRS i ZRS stejné, ale reálné hodnoty a míra rizika bude pochopitelně u ZRS lepší, protože chrání před odstřižením celé jedné zóny.

## Azure NetApp Files
Řada zákazníků pro své NASky dává přednost NetApp. Podobně jako jiné storage společnosti podporuje NetApp i extenzi do cloudu, ale v případě NetApp je jejich partnerství s Azure o hodně dál. Azure NetApp Files je nativní Azure služba. Je přímo integrovaná do Azure portálu a placená vašimi Azure kredity. Pokud hledáte enterprise NAS řešení s hybridními vlastnostmi, NetApp Files jsou zajímavá volba.

## Avere vFXT
Pro náročné počítání nebo rendering je přístup k datům velmi zásadní. Avere je firma, kterou Microsoft koupil už před nějakým časem, a která se specializovala na v podstatě cachování pro high-end situace. V roce 2018 se tato akvizice projevila ve službě určené pro Azure a hybridní scénáře.

Jak vidíte, rok je v cloudu opravdu dlouhá doba! Tak se nechme překvapit, co nás všechno čeká v roce 2019.